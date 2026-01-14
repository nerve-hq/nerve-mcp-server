import os
from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


def load_environment():
    """Load environment variables from .env file based on NERVE_MCP_ENV."""
    if os.environ.get("NERVE_MCP_ENV") == "prod":
        load_dotenv(".env.prod")
    else:
        load_dotenv(".env.dev")


# Load environment on module import
load_environment()


class Settings(BaseSettings):
    """Settings for the Nerve MCP server."""

    model_config = SettingsConfigDict(
        env_prefix="NERVE_MCP_",
        env_file=".env",
        extra="ignore",
    )

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    environment: Literal["dev", "prod"] = "dev"
    server_url: str = "http://localhost:8000"

    # Stytch settings (no prefix - shared with server)
    stytch_project_id: str = ""
    stytch_secret: str = ""
    stytch_public_token: str = ""
    stytch_domain: str = "https://test.stytch.com"
    stytch_custom_base_url: str = ""

    # Stytch Connected App credentials (for this MCP server)
    stytch_connected_app_client_id: str = ""
    stytch_connected_app_secret: str = ""

    # Nerve API
    nerve_api_base_url: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load Stytch values from non-prefixed env vars
        self.stytch_project_id = os.getenv("STYTCH_PROJECT_ID", self.stytch_project_id)
        self.stytch_secret = os.getenv("STYTCH_SECRET", self.stytch_secret)
        self.stytch_public_token = os.getenv("STYTCH_PUBLIC_TOKEN", self.stytch_public_token)
        self.stytch_domain = os.getenv("STYTCH_DOMAIN", self.stytch_domain)
        self.stytch_custom_base_url = os.getenv("STYTCH_CUSTOM_BASE_URL", self.stytch_custom_base_url)
        self.stytch_connected_app_client_id = os.getenv("STYTCH_CONNECTED_APP_CLIENT_ID", self.stytch_connected_app_client_id)
        self.stytch_connected_app_secret = os.getenv("STYTCH_CONNECTED_APP_SECRET", self.stytch_connected_app_secret)
        self.nerve_api_base_url = os.getenv("NERVE_API_BASE_URL", self.nerve_api_base_url)

    @property
    def nerve_api_url(self) -> str:
        """Get the Nerve API URL based on environment."""
        if self.nerve_api_base_url:
            return self.nerve_api_base_url
        if self.environment == "prod":
            return "https://api.usenerve.com/api/v1"
        return "http://localhost:5000/api/v1"

    @property
    def stytch_jwks_url(self) -> str:
        """Get the Stytch JWKS URL for Connected Apps JWT validation."""
        # Connected Apps uses the standard OIDC JWKS endpoint
        base = self.stytch_custom_base_url or self.stytch_domain
        return f"{base}/.well-known/jwks.json"

    @property
    def mcp_server_url(self) -> str:
        """Get the public URL of this MCP server."""
        if self.server_url:
            return self.server_url
        if self.environment == "prod":
            return "https://mcp.usenerve.com"
        return f"http://localhost:{self.port}"


settings = Settings()
