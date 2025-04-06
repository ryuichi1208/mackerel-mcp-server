# mackerel-mcp-server

An MCP server project for Mackerel server monitoring

## Overview

This MCP server provides tools to retrieve and manage server monitoring information using the [Mackerel](https://mackerel.io/) API. It integrates with Claude AI assistant, allowing you to interactively check Mackerel host information through direct conversation.

## Components

### Tools

The server implements the following tools:

- **list_hosts**: Lists all hosts registered in Mackerel

  - Returns host ID, name, status, roles, memo, and meta information (agent version, kernel information)
  - No arguments required

- **get_host**: Retrieves information about a specific host
  - Argument: `host_id` (required) - The ID of the host to retrieve
  - Returns host ID, name, status, roles, and memo

## Configuration

### Environment Variables

- **MACKEREL_API_KEY** or **MACKEREL_APIKEY**: Set your Mackerel API key (required)
  ```bash
  export MACKEREL_API_KEY=your_api_key_here
  ```

## Quick Start

### Installation

```bash
pip install mackerel-mcp-server
```

Or install from source:

```bash
git clone https://github.com/ryuichi1208/mackerel-mcp-server.git
cd mackerel-mcp-server
pip install -e .
```

### Using with Claude Desktop

#### Configuration File Location

- MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Server Configuration</summary>

```json
"mcpServers": {
  "mackerel-mcp-server": {
    "command": "uv",
    "args": [
      "--directory",
      "/Users/ryuichi/ghq/github.com/ryuichi1208/mackerel-mcp-server",
      "run",
      "mackerel-mcp-server"
    ]
  }
}
```

</details>

<details>
  <summary>Published Server Configuration</summary>

```json
"mcpServers": {
  "mackerel-mcp-server": {
    "command": "uvx",
    "args": [
      "mackerel-mcp-server"
    ]
  }
}
```

</details>

### Usage Examples

You can use the following commands in conversation with Claude:

1. Get host list:

   ```
   Call the list_hosts MCP tool
   ```

2. Get specific host information:
   ```
   Call the get_host MCP tool with host_id=your_host_id
   ```

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:

```bash
uv sync
```

2. Build package distributions:

```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:

```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:

- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/ryuichi/ghq/github.com/ryuichi1208/mackerel-mcp-server run mackerel-mcp-server
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
