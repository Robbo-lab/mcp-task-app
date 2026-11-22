"""Centralised storage for configuration settings used throughout the application."""

from pydantic import BaseModel, ConfigDict, NonNegativeInt


class Settings(BaseModel):
    """
    Application configuration settings.

    It is expected that most code will access these defaults through the
    module-level instance (settings).
    """

    model_config = ConfigDict(validate_default=True)
    server_host: str = "localhost"
    server_port: NonNegativeInt = 8003
    mcp_base_url: str = "http://localhost:8003"
    mcp_protocol_version: str = "2026-07-28"


# Create the instance for import by other modules.
settings = Settings()
