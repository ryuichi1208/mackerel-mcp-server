"""
Mackerel MCP Server module.

This module implements a Model Context Protocol (MCP) server for Mackerel, providing
tools to interact with the Mackerel monitoring service via its API. The module allows
retrieving host information and status data through MCP tools.
"""

import datetime
import json
import logging
import os
import sys
from typing import Dict, List, Optional

from .client import Mackerel
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Tool


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
        return client.Mackerel(api_key=api_key)
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
    cli = get_mackerel_client()
    if not cli:
        logger.error("Failed to get Mackerel client")
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        logger.info("Fetching hosts from Mackerel API")
        hosts = await cli.get_hosts()
        logger.info("Successfully fetched hosts")
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
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        services = await cli.get_services()
        logger.info("Successfully retrieved services")
        return [TextContent(type="text", text=json.dumps(services, indent=2))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error(f"Failed to retrieve services: {e}")
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def get_service(service_name: str):
    """
    Get detailed information about a specific Mackerel service.

    Args:
        service_name (str): The name of the service to retrieve

    Returns:
        list: A list containing a TextContent object with JSON-formatted service data
    """
    logger.info("Calling get_service", extra={"service_name": service_name})
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        service_data = await cli.get_service(service_name)
        logger.info("Successfully fetched service data", extra={"service_name": service_name})
        return [TextContent(type="text", text=json.dumps(service_data, ensure_ascii=False))]
    except Exception as e:
        logger.error(
            "Error in get_service",
            extra={"error": str(e), "service_name": service_name},
        )
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


@mcp.tool()
async def get_host(host_id: str):
    """
    Get information about a specific Mackerel host.

    Args:
        host_id (str): The ID of the host to retrieve

    Returns:
        list: A list containing a TextContent object with JSON-formatted host data
    """
    logger.info("Calling get_host", extra={"host_id": host_id})
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        host = await cli.get_host(host_id)
        logger.info("Successfully fetched host", extra={"host_id": host_id})
        return [TextContent(type="text", text=json.dumps(host, ensure_ascii=False))]
    except Exception as e:
        logger.error("Error in get_host", extra={"error": str(e), "host_id": host_id})
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]


@mcp.tool()
async def update_host_status(host_id: str, status: str):
    """
    Update the status of a specific host.

    Args:
        host_id (str): The ID of the host to update
        status (str): The new status to set ('standby', 'working', 'maintenance', 'poweroff')

    Returns:
        list: A list containing a TextContent object with JSON-formatted response
    """
    logger.info("Calling update_host_status", extra={"host_id": host_id, "status": status})
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        result = await cli.update_host_status(host_id, status)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to update host status", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def retire_host(host_id: str):
    """
    Retire a specific host.

    Args:
        host_id (str): The ID of the host to retire

    Returns:
        list: A list containing a TextContent object with JSON-formatted response
    """
    logger.info("Calling retire_host", extra={"host_id": host_id})
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        result = await cli.retire_host(host_id)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to retire host", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def post_metrics(metrics: List[Dict]):
    """
    Post metrics to Mackerel.

    Args:
        metrics (List[Dict]): List of metric data to post

    Returns:
        list: A list containing a TextContent object with JSON-formatted response
    """
    logger.info("Calling post_metrics", extra={"metrics_count": len(metrics)})
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        result = await cli.post_metrics(metrics)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to post metrics", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def get_monitors():
    """
    Get list of all monitors.

    Returns:
        list: A list containing a TextContent object with JSON-formatted monitor data
    """
    logger.info("Calling get_monitors")
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        monitors = await cli.get_monitors()
        return [TextContent(type="text", text=json.dumps(monitors, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to get monitors", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def create_monitor(monitor_config: Dict):
    """
    Create a new monitor.

    Args:
        monitor_config (Dict): Monitor configuration

    Returns:
        list: A list containing a TextContent object with JSON-formatted response
    """
    logger.info("Calling create_monitor")
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        result = await cli.create_monitor(monitor_config)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to create monitor", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def update_monitor(monitor_id: str, monitor_config: Dict):
    """
    Update an existing monitor.

    Args:
        monitor_id (str): ID of the monitor to update
        monitor_config (Dict): New monitor configuration

    Returns:
        list: A list containing a TextContent object with JSON-formatted response
    """
    logger.info("Calling update_monitor", extra={"monitor_id": monitor_id})
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        result = await cli.update_monitor(monitor_id, monitor_config)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to update monitor", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def delete_monitor(monitor_id: str):
    """
    Delete a monitor.

    Args:
        monitor_id (str): ID of the monitor to delete

    Returns:
        list: A list containing a TextContent object with JSON-formatted response
    """
    logger.info("Calling delete_monitor", extra={"monitor_id": monitor_id})
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        result = await cli.delete_monitor(monitor_id)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to delete monitor", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def get_alerts(from_time: Optional[int] = None, to_time: Optional[int] = None):
    """
    Get list of alerts.

    Args:
        from_time (Optional[int]): Start time in epoch seconds
        to_time (Optional[int]): End time in epoch seconds

    Returns:
        list: A list containing a TextContent object with JSON-formatted alert data
    """
    logger.info("Calling get_alerts", extra={"from": from_time, "to": to_time})
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        alerts = await cli.get_alerts(from_time, to_time)
        return [TextContent(type="text", text=json.dumps(alerts, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to get alerts", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def close_alert(alert_id: str, reason: str):
    """
    Close an alert.

    Args:
        alert_id (str): ID of the alert to close
        reason (str): Reason for closing the alert

    Returns:
        list: A list containing a TextContent object with JSON-formatted response
    """
    logger.info("Calling close_alert", extra={"alert_id": alert_id})
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        result = await cli.close_alert(alert_id, reason)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to close alert", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def get_downtimes():
    """
    Get list of downtimes.

    Returns:
        list: A list containing a TextContent object with JSON-formatted downtime data
    """
    logger.info("Calling get_downtimes")
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        downtimes = await cli.get_downtimes()
        return [TextContent(type="text", text=json.dumps(downtimes, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to get downtimes", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def create_downtime(downtime_config: Dict):
    """
    Create a new downtime.

    Args:
        downtime_config (Dict): Downtime configuration

    Returns:
        list: A list containing a TextContent object with JSON-formatted response
    """
    logger.info("Calling create_downtime")
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        result = await cli.create_downtime(downtime_config)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to create downtime", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def update_downtime(downtime_id: str, downtime_config: Dict):
    """
    Update an existing downtime.

    Args:
        downtime_id (str): ID of the downtime to update
        downtime_config (Dict): New downtime configuration

    Returns:
        list: A list containing a TextContent object with JSON-formatted response
    """
    logger.info("Calling update_downtime", extra={"downtime_id": downtime_id})
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        result = await cli.update_downtime(downtime_id, downtime_config)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to update downtime", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def delete_downtime(downtime_id: str):
    """
    Delete a downtime.

    Args:
        downtime_id (str): ID of the downtime to delete

    Returns:
        list: A list containing a TextContent object with JSON-formatted response
    """
    logger.info("Calling delete_downtime", extra={"downtime_id": downtime_id})
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        result = await cli.delete_downtime(downtime_id)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to delete downtime", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def get_channels():
    """
    Get list of notification channels.

    Returns:
        list: A list containing a TextContent object with JSON-formatted channel data
    """
    logger.info("Calling get_channels")
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        channels = await cli.get_channels()
        return [TextContent(type="text", text=json.dumps(channels, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to get channels", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def create_channel(channel_config: Dict):
    """
    Create a new notification channel.

    Args:
        channel_config (Dict): Channel configuration

    Returns:
        list: A list containing a TextContent object with JSON-formatted response
    """
    logger.info("Calling create_channel")
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        result = await cli.create_channel(channel_config)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to create channel", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


@mcp.tool()
async def delete_channel(channel_id: str):
    """
    Delete a notification channel.

    Args:
        channel_id (str): ID of the channel to delete

    Returns:
        list: A list containing a TextContent object with JSON-formatted response
    """
    logger.info("Calling delete_channel", extra={"channel_id": channel_id})
    cli = get_mackerel_client()
    if not cli:
        return [TextContent(type="text", text=json.dumps({"error": "Failed to get Mackerel client"}))]

    try:
        result = await cli.delete_channel(channel_id)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        error_msg = {"error": str(e)}
        logger.error("Failed to delete channel", extra={"error": str(e)})
        return [TextContent(type="text", text=json.dumps(error_msg))]


async def main():
    """
    Main entry point for the Mackerel MCP server.

    Initializes and runs the MCP server using stdio as the transport mechanism.
    """
    logger.info("Starting Mackerel MCP server")
    await mcp.run(transport="stdio")


if __name__ == "__main__":
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
