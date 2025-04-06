from datetime import datetime
from typing import Dict, List, Optional, Union

import httpx


class Mackerel:
    """
    A client for interacting with the Mackerel API.

    This class provides methods to interact with various Mackerel API endpoints,
    including hosts, services, metrics, monitors, alerts, downtimes, and notification channels.

    Attributes:
        BASE_URL (str): The base URL for the Mackerel API
        api_key (str): The API key for authentication
        headers (Dict): Common headers used in API requests
    """

    BASE_URL = "https://api.mackerelio.com/api/v0"

    def __init__(self, api_key: str):
        """
        Initialize the Mackerel API client.

        Args:
            api_key (str): The API key for authentication with Mackerel
        """
        self.api_key = api_key
        self.headers = {"X-Api-Key": self.api_key, "Content-Type": "application/json"}

    async def _request(
        self, method: str, path: str, data: Optional[Dict] = None
    ) -> Dict:
        """
        Make a request to the Mackerel API.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            path (str): API endpoint path
            data (Optional[Dict]): Request data/parameters

        Returns:
            Dict: JSON response from the API

        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.BASE_URL}{path}"
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method, url, headers=self.headers, json=data
            )
            response.raise_for_status()
            return response.json()

    # Host-related APIs
    async def get_hosts(
        self, service: Optional[str] = None, role: Optional[str] = None
    ) -> Dict:
        """
        Get a list of registered hosts.

        Args:
            service (Optional[str]): Filter hosts by service name
            role (Optional[str]): Filter hosts by role name

        Returns:
            Dict: List of hosts and their details
        """
        params = {}
        if service:
            params["service"] = service
        if role:
            params["role"] = role
        return await self._request("GET", "/hosts", params)

    async def get_host(self, host_id: str) -> Dict:
        """
        Get details of a specific host.

        Args:
            host_id (str): The ID of the host to retrieve

        Returns:
            Dict: Host details including status, roles, and metadata
        """
        return await self._request("GET", f"/hosts/{host_id}")

    async def update_host_status(self, host_id: str, status: str) -> Dict:
        """
        Update the status of a host.

        Args:
            host_id (str): The ID of the host to update
            status (str): New status ('working', 'standby', 'maintenance', 'poweroff')

        Returns:
            Dict: Response indicating success or failure
        """
        return await self._request(
            "POST", f"/hosts/{host_id}/status", {"status": status}
        )

    async def retire_host(self, host_id: str) -> Dict:
        """
        Retire (remove) a host from Mackerel.

        Args:
            host_id (str): The ID of the host to retire

        Returns:
            Dict: Response indicating success or failure
        """
        return await self._request("POST", f"/hosts/{host_id}/retire")

    # Service-related APIs
    async def get_services(self) -> Dict:
        """
        Get a list of registered services.

        Returns:
            Dict: List of services and their basic information
        """
        return await self._request("GET", "/services")

    async def get_service(self, service_name: str) -> Dict:
        """
        Get details of a specific service.

        Args:
            service_name (str): Name of the service to retrieve

        Returns:
            Dict: Service details including roles and metadata
        """
        return await self._request("GET", f"/services/{service_name}")

    async def get_service_roles(self, service_name: str) -> Dict:
        """
        Get roles defined for a service.

        Args:
            service_name (str): Name of the service

        Returns:
            Dict: List of roles associated with the service
        """
        return await self._request("GET", f"/services/{service_name}/roles")

    # Metrics-related APIs
    async def post_metrics(self, metrics: List[Dict]) -> Dict:
        """
        Post metrics to Mackerel.

        Args:
            metrics (List[Dict]): List of metric data points to post
                Each metric should contain:
                - name: Metric name
                - value: Metric value
                - time: Unix timestamp
                - host_id: Host ID (optional)
                - service_name: Service name (optional)

        Returns:
            Dict: Response indicating success or failure
        """
        return await self._request("POST", "/metrics", {"metrics": metrics})

    async def get_host_metrics(
        self, host_id: str, name: str, from_time: int, to_time: int
    ) -> Dict:
        """
        Get metric values for a specific host.

        Args:
            host_id (str): The ID of the host
            name (str): Name of the metric to retrieve
            from_time (int): Start time in Unix timestamp
            to_time (int): End time in Unix timestamp

        Returns:
            Dict: Metric values within the specified time range
        """
        params = {"name": name, "from": from_time, "to": to_time}
        return await self._request("GET", f"/hosts/{host_id}/metrics", params)

    async def get_service_metrics(
        self, service_name: str, name: str, from_time: int, to_time: int
    ) -> Dict:
        """
        Get metric values for a specific service.

        Args:
            service_name (str): Name of the service
            name (str): Name of the metric to retrieve
            from_time (int): Start time in Unix timestamp
            to_time (int): End time in Unix timestamp

        Returns:
            Dict: Metric values within the specified time range
        """
        params = {"name": name, "from": from_time, "to": to_time}
        return await self._request("GET", f"/services/{service_name}/metrics", params)

    # Monitoring-related APIs
    async def get_monitors(self) -> Dict:
        """
        Get a list of all monitors.

        Returns:
            Dict: List of monitors and their configurations
        """
        return await self._request("GET", "/monitors")

    async def create_monitor(self, monitor_config: Dict) -> Dict:
        """
        Create a new monitor.

        Args:
            monitor_config (Dict): Monitor configuration including:
                - type: Monitor type (host, service, external, expression)
                - name: Monitor name
                - memo: Monitor description
                - duration: Duration to wait before alerting
                - metric: Metric name to monitor
                - operator: Comparison operator
                - warning: Warning threshold
                - critical: Critical threshold

        Returns:
            Dict: Created monitor details
        """
        return await self._request("POST", "/monitors", monitor_config)

    async def update_monitor(self, monitor_id: str, monitor_config: Dict) -> Dict:
        """
        Update an existing monitor.

        Args:
            monitor_id (str): ID of the monitor to update
            monitor_config (Dict): New monitor configuration

        Returns:
            Dict: Updated monitor details
        """
        return await self._request("PUT", f"/monitors/{monitor_id}", monitor_config)

    async def delete_monitor(self, monitor_id: str) -> Dict:
        """
        Delete a monitor.

        Args:
            monitor_id (str): ID of the monitor to delete

        Returns:
            Dict: Response indicating success or failure
        """
        return await self._request("DELETE", f"/monitors/{monitor_id}")

    # Alert-related APIs
    async def get_alerts(
        self, from_time: Optional[int] = None, to_time: Optional[int] = None
    ) -> Dict:
        """
        Get a list of alerts.

        Args:
            from_time (Optional[int]): Start time in Unix timestamp
            to_time (Optional[int]): End time in Unix timestamp

        Returns:
            Dict: List of alerts within the specified time range
        """
        params = {}
        if from_time:
            params["from"] = from_time
        if to_time:
            params["to"] = to_time
        return await self._request("GET", "/alerts", params)

    async def close_alert(self, alert_id: str, reason: str) -> Dict:
        """
        Close (resolve) an alert.

        Args:
            alert_id (str): ID of the alert to close
            reason (str): Reason for closing the alert

        Returns:
            Dict: Response indicating success or failure
        """
        return await self._request(
            "POST", f"/alerts/{alert_id}/close", {"reason": reason}
        )

    # Downtime-related APIs
    async def get_downtimes(self) -> Dict:
        """
        Get a list of scheduled downtimes.

        Returns:
            Dict: List of downtimes and their configurations
        """
        return await self._request("GET", "/downtimes")

    async def create_downtime(self, downtime_config: Dict) -> Dict:
        """
        Create a new downtime schedule.

        Args:
            downtime_config (Dict): Downtime configuration including:
                - name: Downtime name
                - start: Start time
                - duration: Duration in minutes
                - recurrence: Recurrence settings (optional)
                - service_names: List of services
                - monitor_ids: List of monitor IDs

        Returns:
            Dict: Created downtime details
        """
        return await self._request("POST", "/downtimes", downtime_config)

    async def update_downtime(self, downtime_id: str, downtime_config: Dict) -> Dict:
        """
        Update an existing downtime schedule.

        Args:
            downtime_id (str): ID of the downtime to update
            downtime_config (Dict): New downtime configuration

        Returns:
            Dict: Updated downtime details
        """
        return await self._request("PUT", f"/downtimes/{downtime_id}", downtime_config)

    async def delete_downtime(self, downtime_id: str) -> Dict:
        """
        Delete a downtime schedule.

        Args:
            downtime_id (str): ID of the downtime to delete

        Returns:
            Dict: Response indicating success or failure
        """
        return await self._request("DELETE", f"/downtimes/{downtime_id}")

    # Notification channel-related APIs
    async def get_channels(self) -> Dict:
        """
        Get a list of notification channels.

        Returns:
            Dict: List of notification channels and their configurations
        """
        return await self._request("GET", "/channels")

    async def create_channel(self, channel_config: Dict) -> Dict:
        """
        Create a new notification channel.

        Args:
            channel_config (Dict): Channel configuration including:
                - type: Channel type (email, slack, webhook, etc.)
                - name: Channel name
                - emails: List of email addresses (for email type)
                - url: Webhook URL (for webhook type)
                - mentions: Mention settings (for slack type)

        Returns:
            Dict: Created channel details
        """
        return await self._request("POST", "/channels", channel_config)

    async def delete_channel(self, channel_id: str) -> Dict:
        """
        Delete a notification channel.

        Args:
            channel_id (str): ID of the channel to delete

        Returns:
            Dict: Response indicating success or failure
        """
        return await self._request("DELETE", f"/channels/{channel_id}")
