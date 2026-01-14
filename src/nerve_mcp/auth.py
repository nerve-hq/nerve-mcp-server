"""Authentication module for Nerve MCP server using Stytch Connected Apps."""

import logging
from functools import wraps
from typing import Any

import httpx
import jwt
from jwt import PyJWKClient

from nerve_mcp.settings import settings

logger = logging.getLogger(__name__)

# Cache for JWKS client
_jwks_client: PyJWKClient | None = None


def get_jwks_client() -> PyJWKClient:
    """Get or create JWKS client for Stytch JWT validation."""
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(settings.stytch_jwks_url)
    return _jwks_client


def validate_token(token: str) -> dict[str, Any]:
    """Validate a Stytch OAuth access token (JWT).

    Args:
        token: The JWT access token from the Authorization header

    Returns:
        The decoded token claims

    Raises:
        jwt.InvalidTokenError: If the token is invalid
    """
    jwks_client = get_jwks_client()

    # Get the signing key from JWKS
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    # Decode and validate the token
    decoded = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        # Stytch uses the project domain as issuer
        issuer=settings.stytch_custom_base_url or settings.stytch_domain,
        options={
            "verify_aud": False,  # Stytch Connected Apps may not set aud
            "verify_exp": True,
            "verify_iss": True,
        },
    )

    return decoded


def get_protected_resource_metadata() -> dict[str, Any]:
    """Get the OAuth Protected Resource Metadata document.

    This is served at /.well-known/oauth-protected-resource
    per RFC 8707 and MCP spec requirements.
    """
    return {
        "resource": settings.mcp_server_url,
        "authorization_servers": [
            settings.stytch_custom_base_url or settings.stytch_domain
        ],
        "scopes_supported": ["openid", "profile", "email"],
        "bearer_methods_supported": ["header"],
    }


def get_www_authenticate_header() -> str:
    """Get the WWW-Authenticate header value for 401 responses.

    This header tells MCP clients where to find the authorization server
    metadata so they can initiate the OAuth flow.
    """
    resource_metadata_url = f"{settings.mcp_server_url}/.well-known/oauth-protected-resource"
    return (
        f'Bearer error="Unauthorized", '
        f'error_description="Access token required", '
        f'resource_metadata="{resource_metadata_url}"'
    )


class AuthContext:
    """Context object containing authenticated user information."""

    def __init__(self, token_claims: dict[str, Any]):
        self.claims = token_claims
        self.member_id = token_claims.get("sub")
        self.organization_id = token_claims.get("https://stytch.com/organization", {}).get(
            "organization_id"
        )
        self.email = token_claims.get("email")
        self.scopes = token_claims.get("scope", "").split()

    def __repr__(self) -> str:
        return f"AuthContext(member_id={self.member_id}, org_id={self.organization_id})"
