"""Nerve MCP Server with Stytch Connected Apps OAuth."""

import json
import logging
from contextvars import ContextVar
from functools import wraps

import jwt
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from nerve_mcp.auth import (
    AuthContext,
    get_protected_resource_metadata,
    get_www_authenticate_header,
    validate_token,
)
from nerve_mcp.client import nerve_client
from nerve_mcp.settings import settings

# Context variable to store the current request's access token
current_access_token: ContextVar[str | None] = ContextVar("current_access_token", default=None)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create the MCP server
mcp = FastMCP(
    "nerve-mcp",
    instructions="""
    Nerve is a search engine for business information. It connects to all sorts of third parties,
    like Google Drive (docs, sheets, slides, etc.), Email, Slack, Jira, etc.
    Use this to gather information about work, search for deeper context, or in general browse
    company information.
    """,
)


def handle_errors(func):
    """Decorator to handle errors in MCP tools."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in {func.__name__}: {e}")
            return f"Error: {str(e)}. Please try again or modify your query."
    return wrapper


@handle_errors
@mcp.tool(
    name="search",
    description="Search for information across connected business applications (Google Drive, Email, Slack, Jira, etc.)"
)
async def search(query: str) -> str:
    """Search for information in the user's connected services."""
    # Get the access token from context variable
    access_token = current_access_token.get()
    if not access_token:
        return "Error: Not authenticated. Please connect your Nerve account."

    logger.info(f"Searching for: {query}")
    results = await nerve_client.search(query, access_token)

    if not results:
        return "No results found for your query."

    # Format results for the LLM
    formatted = []
    for r in results:
        formatted.append(f"- **{r.get('name', 'Untitled')}**\n  {r.get('content', '')[:500]}")

    return f"Found {len(results)} results:\n\n" + "\n\n".join(formatted)


@handle_errors
@mcp.tool(
    name="get_file",
    description="Get the full content of a specific file by its ID"
)
async def get_file(file_id: str) -> str:
    """Get the content of a specific file."""
    access_token = current_access_token.get()
    if not access_token:
        return "Error: Not authenticated. Please connect your Nerve account."

    logger.info(f"Getting file: {file_id}")
    file_data = await nerve_client.get_file(file_id, access_token)

    return file_data.get("content", "No content available.")


# OAuth endpoints
async def oauth_protected_resource_metadata(_request: Request) -> JSONResponse:
    """Serve the OAuth Protected Resource Metadata document."""
    metadata = get_protected_resource_metadata()
    return JSONResponse(metadata)


class StytchAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate Stytch OAuth tokens on MCP requests."""

    # Paths that don't require authentication
    PUBLIC_PATHS = {
        "/.well-known/oauth-protected-resource",
        "/health",
        "/",
    }

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Allow public paths without auth
        if path in self.PUBLIC_PATHS:
            return await call_next(request)

        # Check for Authorization header
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            # Return 401 with WWW-Authenticate header for OAuth discovery
            return Response(
                content=json.dumps({"error": "unauthorized", "message": "Access token required"}),
                status_code=401,
                headers={
                    "WWW-Authenticate": get_www_authenticate_header(),
                    "Content-Type": "application/json",
                },
            )

        token = auth_header.replace("Bearer ", "")

        try:
            # Validate the token
            claims = validate_token(token)
            auth_context = AuthContext(claims)
            logger.info(f"Authenticated request from {auth_context}")

            # Store auth context in request state and set context variable for tools
            request.state.auth_context = auth_context
            request.state.access_token = token
            current_access_token.set(token)

        except jwt.ExpiredSignatureError:
            return Response(
                content=json.dumps({"error": "token_expired", "message": "Access token has expired"}),
                status_code=401,
                headers={
                    "WWW-Authenticate": get_www_authenticate_header(),
                    "Content-Type": "application/json",
                },
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return Response(
                content=json.dumps({"error": "invalid_token", "message": str(e)}),
                status_code=401,
                headers={
                    "WWW-Authenticate": get_www_authenticate_header(),
                    "Content-Type": "application/json",
                },
            )

        return await call_next(request)


async def health_check(_request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({"status": "healthy", "service": "nerve-mcp"})


def create_app() -> Starlette:
    """Create the Starlette application with MCP and OAuth support."""

    # Get the MCP ASGI app
    mcp_app = mcp.http_app()

    # Create routes for non-MCP endpoints
    routes = [
        Route("/.well-known/oauth-protected-resource", oauth_protected_resource_metadata),
        Route("/health", health_check),
    ]

    # Create Starlette app with middleware and MCP lifespan
    app = Starlette(
        routes=routes,
        middleware=[
            Middleware(StytchAuthMiddleware),
        ],
        lifespan=mcp_app.lifespan,
    )

    # Mount the MCP app at root (must be last since it catches all paths)
    app.mount("/", mcp_app)

    return app


def main():
    """Run the MCP server."""
    import uvicorn

    logger.info(f"Starting Nerve MCP server on {settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Nerve API: {settings.nerve_api_url}")
    logger.info(f"Stytch Project: {settings.stytch_project_id}")

    app = create_app()

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
