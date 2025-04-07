import os
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
import httpx

from mackerel_mcp_server.client import Mackerel


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
