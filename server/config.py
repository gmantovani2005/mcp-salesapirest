"""Configurações carregadas do ambiente / arquivo .env."""
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    sales_api_base_url: str = Field(
        default="http://localhost:8000",
        description="URL base da Sales Dataset API REST.",
    )
    sales_api_timeout: float = Field(
        default=30.0,
        description="Timeout (segundos) para chamadas HTTP à Sales API.",
    )

    mcp_transport: str = Field(
        default="stdio",
        description='Transporte do MCP: "stdio" (dev) ou "sse" (container).',
    )
    mcp_host: str = Field(default="0.0.0.0")
    mcp_port: int = Field(default=8080)


settings = Settings()
