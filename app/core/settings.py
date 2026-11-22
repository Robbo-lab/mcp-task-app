from pydantic import BaseModel, ConfigDict, NonNegativeInt


class Settings(BaseModel):
    model_config = ConfigDict(validate_default=True)
    server_host: str = "localhost"
    server_port: NonNegativeInt = 8003
    mcp_base_url: str = "http://localhost:8003"
    mcp_protocol_version: str = "2026-07-28"


settings = Settings()
