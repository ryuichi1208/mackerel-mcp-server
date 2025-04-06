import os
import sys
import logging
import json
from mackerel.client import Client

logger = logging.getLogger(__name__)


def get_mackerel_client():
    """Get Mackerel client"""
    try:
        api_key = os.environ["MACKEREL_API_KEY"]
        return Client(mackerel_api_key=api_key)
    except Exception as e:
        logger.error(f"Error in get_mackerel_client: {e}")
    return None


def get_hosts():
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
    print(json.dumps(hosts, ensure_ascii=False))


def get_services():
    client = get_mackerel_client()
    services = client.
    print(json.dumps(services, ensure_ascii=False))


if __name__ == "__main__":
    get_services()
