import os
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
import httpx

from mackerel_mcp_server.client import Mackerel, MackerelError


@pytest.fixture
def api_key():
    return "dummy-api-key"


@pytest.fixture
def client(api_key):
    return Mackerel(api_key)


def test_init_with_api_key():
    """Test initialization with API key."""
    api_key = "test-api-key"
    client = Mackerel(api_key)
    assert client.api_key == api_key


def test_init_with_env_var():
    """Test initialization with environment variable."""
    api_key = "test-api-key"
    with patch.dict(os.environ, {"MACKEREL_APIKEY": api_key}):
        client = Mackerel()
        assert client.api_key == api_key


def test_init_without_api_key():
    """Test initialization without API key."""
    with pytest.raises(MackerelError):
        Mackerel()


def test_validate_host_status():
    """Test host status validation."""
    client = Mackerel("dummy-key")
    assert client._validate_host_status("working") is None
    assert client._validate_host_status("standby") is None
    assert client._validate_host_status("maintenance") is None
    assert client._validate_host_status("poweroff") is None
    with pytest.raises(MackerelError):
        client._validate_host_status("invalid")


@pytest.mark.asyncio
async def test_get_hosts(client):
    """Test getting host list."""
    mock_response = {
        "hosts": [
            {
                "id": "host123",
                "name": "test-host",
                "status": "working",
            }
        ]
    }

    mock_client = AsyncMock()
    mock_response_obj = AsyncMock()
    mock_response_obj.json.return_value = mock_response
    mock_client.request.return_value = mock_response_obj

    async with patch("httpx.AsyncClient", return_value=mock_client):
        response = await client.get_hosts()
        assert response == mock_response


@pytest.mark.asyncio
async def test_update_host_status(client):
    """Test updating host status."""
    host_id = "host123"
    status = "maintenance"
    mock_response = {"success": True}

    mock_client = AsyncMock()
    mock_response_obj = AsyncMock()
    mock_response_obj.json.return_value = mock_response
    mock_client.post.return_value = mock_response_obj

    async with patch("httpx.AsyncClient", return_value=mock_client):
        response = await client.update_host_status(host_id, status)
        assert response == mock_response


def test_update_host_status_invalid(client):
    """Test updating host status with invalid status."""
    with pytest.raises(MackerelError):
        client.update_host_status("host123", "invalid")


@pytest.mark.asyncio
async def test_get_service_metrics(client):
    """Test getting service metrics."""
    service_name = "test-service"
    metric_name = "cpu.user"
    from_time = 1600000000
    to_time = 1600001000
    mock_response = {
        "metrics": [
            {"time": 1600000000, "value": 50},
            {"time": 1600000060, "value": 55},
        ]
    }

    mock_client = AsyncMock()
    mock_response_obj = AsyncMock()
    mock_response_obj.json.return_value = mock_response
    mock_client.request.return_value = mock_response_obj

    async with patch("httpx.AsyncClient", return_value=mock_client):
        response = await client.get_service_metrics(service_name, metric_name, from_time, to_time)
        assert response == mock_response
