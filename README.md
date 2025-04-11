# Nerve MCP Server

This project implements an [MCP server](https://spec.modelcontextprotocol.io/) for the [Nerve API](https://usenerve.com/).

### Installation

#### 1. Setting up Integration in Nerve:

Go to [https://usenerve.com/](https://usenerve.com/) and create an account.

Continue to your Settings page to create an API key to use for the client.

#### 2. Adding MCP config to your client:

Add the following to your `.cursor/mcp.json` or `claude_desktop_config.json` (MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`)

```javascript
{
  "mcpServers": {
    "nerve": {
      "command": "uv",
      "args": [
        "--directory",
        "/<ABSOLUTE_PATH>/nerve-mcp-server",
        "run",
        "nerve-mcp"
      ],
      "env": {
      	"NERVE_API_KEY": "<API_KEY>",
      	"NERVE_ENVIRONMENT": "prod"
      }
    }
  }
}

```

Don't forget to replace `API_KEY` with your own key. Find it from your Settings tab:

#### 3. Enable third party integrations:

Navigate to your integrations page on Nerve to conenct to the various SaaS tools you use.

### Examples

1. Using the following instruction

```
What emails have I gotten with customer feedback?
```

AI will plan one API calls, `/search`

(more examples coming soon)

### Development

Execute

```
NERVE_API_KEY='<API_KEY>' uv run nerve-mcp
```
