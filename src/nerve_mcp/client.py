"""Nerve API client for MCP server."""

import logging
from typing import Any

import httpx

from nerve_mcp.settings import settings

logger = logging.getLogger(__name__)


class NerveClient:
    """Async client for the Nerve API.

    This client makes requests to the Nerve backend on behalf of authenticated users.
    Each request uses the OAuth access token from the MCP session.
    """

    def __init__(self):
        self._base_url = settings.nerve_api_url
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "Nerve-MCP/0.0.1",
                },
            )
        return self._client

    async def search(self, query: str, access_token: str) -> list[dict[str, Any]]:
        """Search for information in the user's connected services.

        Args:
            query: The search query
            access_token: The user's OAuth access token (Stytch session JWT)

        Returns:
            List of search results
        """
        client = await self._get_client()
        response = await client.get(
            f"{self._base_url}/search",
            params={"query": query},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])

    async def get_file(self, file_id: str, access_token: str) -> dict[str, Any]:
        """Get the content of a specific file.

        Args:
            file_id: The ID of the file to retrieve
            access_token: The user's OAuth access token

        Returns:
            File data including content
        """
        client = await self._get_client()
        response = await client.get(
            f"{self._base_url}/files/{file_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", {})

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# Singleton client instance
nerve_client = NerveClient()
