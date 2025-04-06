import httpx


class Mackerel:
    """
    Mackerel API client.
    """

    BASE_URL = "https://api.mackerelio.com/api/v0"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_services(self):
        url = f"{self.BASE_URL}/services"
        headers = {"X-Api-Key": self.api_key}
        response = await httpx.AsyncClient().get(url, headers=headers)
        return response.json()

    async def get_service(self, service_name: str):
        url = f"{self.BASE_URL}/services/{service_name}"
        headers = {"X-Api-Key": self.api_key}
        response = await httpx.AsyncClient().get(url, headers=headers)
        return response.json()
