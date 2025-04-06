"""
Mackerel MCP Server module.

This module implements a Model Context Protocol (MCP) server for Mackerel, providing
tools to interact with the Mackerel monitoring service via its API. The module allows
retrieving host information and status data through MCP tools.
"""

import os
import sys
import logging
import json
import datetime
import asyncio
import httpx
import anyio

from mackerel.client import Client
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent


# Configure JSON logging
class JsonFormatter(logging.Formatter):
    """
    Custom formatter to output logs in JSON format.
    """

    def format(self, record):
        log_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Add any extra attributes
        if hasattr(record, "extra"):
            log_record.update(record.extra)

        return json.dumps(log_record, ensure_ascii=False)


# Configure root logger with JSON formatter
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])

logger = logging.getLogger(__name__)

# FastMCP instance
mcp = FastMCP("mackerel server")

# Constants
MACKEREL_API_BASE_URL = "https://api.mackerelio.com/api/v0"


def get_mackerel_client():
    """
    Create and return a Mackerel API client.

    Attempts to retrieve the API key from the MACKEREL_API_KEY environment variable
    and initializes a Mackerel client with this key.

    Returns:
        Client: An initialized Mackerel client if successful
        None: If initialization fails

    Raises:
        KeyError: If MACKEREL_API_KEY environment variable is not set
    """
    try:
        api_key = os.environ["MACKEREL_API_KEY"]
        logger.info("Creating Mackerel client", extra={"api_key_length": len(api_key)})
        return Client(mackerel_api_key=api_key)
    except KeyError as e:
        logger.error("Missing MACKEREL_API_KEY environment variable", extra={"error": str(e)})
        return None
    except Exception as e:
        logger.error("Error creating Mackerel client", extra={"error": str(e)})
        return None


@mcp.tool()
async def list_hosts():
    """
    List all hosts registered in Mackerel.

    Retrieves a list of all hosts from the Mackerel API and formats them into
    a structured JSON response. The response includes host information such as
    ID, name, status, roles, and metadata.

    Returns:
        list: A list containing a TextContent object with JSON-formatted host data
    """
    logger.info("Calling list_hosts")
    client = get_mackerel_client()
    if not client:
        logger.error("Failed to get Mackerel client")
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        logger.info("Fetching hosts from Mackerel API")
        hosts = client.get_hosts()
        logger.info("Successfully fetched hosts", extra={"host_count": len(hosts)})

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

        return [TextContent(type="text", text=json.dumps(hosts, ensure_ascii=False))]
    except Exception as e:
        logger.error("Error in list_hosts", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]


@mcp.tool()
async def list_services() -> list[TextContent]:
    """
    List all services registered in Mackerel.

    Returns:
        list: A list containing a TextContent object with JSON-formatted service data
    """
    logger.info("Retrieving list of services")
    try:
        api_key = os.getenv("MACKEREL_API_KEY") or os.getenv("MACKEREL_APIKEY")
        if not api_key:
            raise ValueError("Mackerel API key not found in environment variables")

        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.mackerelio.com/api/v0/services", headers={"X-Api-Key": api_key})
            response.raise_for_status()
            services = response.json()
            logger.info(f"Successfully retrieved {len(services['services'])} services")
            return [TextContent(type="text", text=json.dumps(services, indent=2))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error(f"Failed to retrieve services: {e}")
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def get_service(service_name: str):
    """
    Get detailed information about a specific Mackerel service.

    This tool directly calls the Mackerel API to retrieve detailed information
    about a service identified by its name, including roles, metrics configuration,
    and other service-specific details.

    Args:
        service_name (str): The name of the service to retrieve

    Returns:
        list: A list containing a TextContent object with JSON-formatted service data
    """
    logger.info("Calling get_service", extra={"service_name": service_name})

    # Get API key
    try:
        api_key = os.environ.get("MACKEREL_API_KEY") or os.environ.get("MACKEREL_APIKEY")
        if not api_key:
            error_msg = "MACKEREL_API_KEY not found in environment variables"
            logger.error(error_msg)
            return [TextContent(type="text", text=json.dumps({"error": error_msg}))]
    except Exception as e:
        logger.error("Error retrieving API key", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    # Directly call Mackerel API
    try:
        logger.info("Fetching service from Mackerel API", extra={"service_name": service_name})

        # Construct API URL and headers
        url = f"{MACKEREL_API_BASE_URL}/services/{service_name}"
        headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

            # Check for successful response
            if response.status_code == 200:
                service_data = response.json()
                logger.info(
                    "Successfully fetched service data",
                    extra={"service_name": service_name, "status_code": response.status_code},
                )
                return [TextContent(type="text", text=json.dumps(service_data, ensure_ascii=False))]
            else:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                logger.error(
                    "Service API request failed",
                    extra={
                        "service_name": service_name,
                        "status_code": response.status_code,
                        "response": response.text,
                    },
                )
                return [TextContent(type="text", text=json.dumps({"error": error_msg}))]

    except Exception as e:
        logger.error("Error in get_service", extra={"error": str(e), "service_name": service_name})
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


@mcp.tool()
async def get_host(host_id: str):
    """
    Get information about a specific Mackerel host.

    Retrieves detailed information about a specific host identified by its ID.

    Args:
        host_id (str): The ID of the host to retrieve

    Returns:
        list: A list containing a TextContent object with JSON-formatted host data

    Raises:
        Exception: If the host cannot be found or other API errors occur
    """
    logger.info("Calling get_host", extra={"host_id": host_id})
    client = get_mackerel_client()
    if not client:
        logger.error("Failed to get Mackerel client")
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        logger.info("Fetching host from Mackerel API", extra={"host_id": host_id})
        res = client.get_host(host_id)
        logger.info("Successfully fetched host", extra={"host_id": host_id, "host_name": res.name})

        host = {
            "id": res.id,
            "name": res.name,
            "status": res.status,
            "roles": res.roles,
            "memo": res.memo,
        }

        return [TextContent(type="text", text=json.dumps(host, ensure_ascii=False))]
    except Exception as e:
        logger.error("Error in get_host", extra={"error": str(e), "host_id": host_id})
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]


async def main():
    """
    Main entry point for the Mackerel MCP server.

    Initializes and runs the MCP server using stdio as the transport mechanism.
    """
    logger.info("Starting Mackerel MCP server")
    await mcp.run(transport="stdio")


if __name__ == "__main__":
    try:
        anyio.run(main)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
