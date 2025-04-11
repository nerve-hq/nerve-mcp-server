import os

import httpx

ENV_TO_BASE_URL = {
    "dev": "http://localhost:5000/api/v1",
    "prod": "https://api.usenerve.com/api/v1",
}


class NerveAsyncClient:
    def __init__(self):
        env = os.getenv("NERVE_ENVIRONMNET", "dev")
        
        if env not in ENV_TO_BASE_URL:
            raise ValueError(f"Environment '{env}' not supported. Choose from: {', '.join(ENV_TO_BASE_URL.keys())}")
        self._base_url = ENV_TO_BASE_URL[env]
        
        self._api_key = os.getenv("NERVE_API_KEY")
        if not self._api_key:
            raise ValueError("NERVE_API_KEY is not set")
        
        self.client = None

    def connect(self):
        self.client = httpx.AsyncClient(
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Nerve-MCP/0.0.1",
            },
        )

    async def search(self, query: str) -> list[dict]:
        results = []
        response = await self.client.get(
            f"{self._base_url}/search",
            params={"query": query},
        )
        response.raise_for_status()
        results = response.json()
        return results["data"]
    
    