from mcp.server.fastmcp import FastMCP

from .tools import internal_search, nerve_client

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

def main():
    print("Starting Nerve MCP server...")
    server.add_tool(internal_search, name="internal_search", description="Search helper for internal corporate information. Use this to search for information that may appear in Google Drive, Email, Slack, etc.")
    
    nerve_client.connect()
    server.run()

if __name__ == "__main__":
    main()

__all__ = ["main", "server"]