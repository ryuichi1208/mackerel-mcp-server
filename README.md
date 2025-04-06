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

## Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
    "mcp-mackerel": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/app/mackerel_mcp_server",
        "server.py"
      ],
      "env": {
        "MACKEREL_API_KEY": "XXXXXXXXXXXXXX"
      }
    }
  }
}
```

## Requirements

- Python >= 3.12
- Mackerel API key
