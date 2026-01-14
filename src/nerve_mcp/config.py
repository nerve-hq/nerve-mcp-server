from fastmcp import FastMCP

from nerve_mcp.client import NerveAsyncClient

server = FastMCP(
    "nerve-mcp",
    instructions="""
    Nerve is a search engine for business information. It connects to all sorts of third parties,
    like Google Drive (docs, sheets, slides, etc.), Email, Slack, Jira, etc.
    Use this to gather information about work, search for deeper context, or in general users browse
    their company information.
    """,
    dependencies=[
        "httpx",
    ],
)

# Create and export the client instance
nerve_client = NerveAsyncClient() 