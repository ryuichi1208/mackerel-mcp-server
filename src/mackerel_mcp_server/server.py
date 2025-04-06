import os
import sys
import logging
import json

from mackerel.client import Client
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)

# シンプルなFastMCPインスタンス
mcp = FastMCP("mackerel server")


def get_mackerel_client():
    """Get Mackerel client"""
    try:
        api_key = os.environ["MACKEREL_API_KEY"]
        return Client(mackerel_api_key=api_key)
    except Exception as e:
        logger.error(f"Error in get_mackerel_client: {e}")
        return None


@mcp.tool()
async def list_hosts():
    """List all hosts in Mackerel"""
    client = get_mackerel_client()
    hosts = client.get_hosts()

    hosts = [
        {
            "id": host.id,
            "name": host.name,
            "status": host.status,
            "roles": host.roles,
            "memo": host.memo,
            "meta": [{"key": k, "value": v} for k, v in host.meta.items() if k in ("agent-version", "kernel")],
        }
        for host in hosts
    ]

    """List all hosts in Mackerel"""
    try:
        return [TextContent(type="text", text=json.dumps(hosts, ensure_ascii=False))]
    except Exception as e:
        logger.error(f"Error in list_hosts: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]


@mcp.tool()
async def get_host(host_id: str):
    """Get host information"""
    client = get_mackerel_client()

    try:
        res = client.get_host(host_id)

        host = {
            "id": res.id,
            "name": res.name,
            "status": res.status,
            "roles": res.roles,
            "memo": res.memo,
        }

        return [TextContent(type="text", text=json.dumps(host, ensure_ascii=False))]
    except Exception as e:
        logger.error(f"Error in get_host: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]


async def main():
    print("Starting Mackerel MCP server...")
    await mcp.run(transport="stdio")


if __name__ == "__main__":
    mcp.run(transport="stdio")
