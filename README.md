# mackerel-mcp-server

MCP server implementation for Mackerel monitoring service.

## Features

- Host management (list, get, update status, retire)
- Service management (list, get, roles)
- Metrics (post, get host/service metrics)
- Monitors (list, create, update, delete)
- Alerts (list, close)
- Downtimes (list, create, update, delete)
- Notification channels (list, create, delete)

## Setup

```bash
# Install
pip install mackerel-mcp-server

# Set API key
export MACKEREL_API_KEY=your_api_key_here

# Run
mackerel-mcp-server
```

## Development

```bash
# Install from source
git clone https://github.com/ryuichi1208/mackerel-mcp-server.git
cd mackerel-mcp-server
pip install -e .

# Debug with MCP Inspector
npx @modelcontextprotocol/inspector uv run mackerel-mcp-server
```

## Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mackerel-mcp-server": {
      "command": "uvx",
      "args": ["mackerel-mcp-server"]
    }
  }
}
```

## Requirements

- Python >= 3.12
- Mackerel API key
