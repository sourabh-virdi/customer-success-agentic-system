"""Shared configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mcp_base_url: str = "http://localhost:8000"
    memory_api_url: str = "http://localhost:8001"
    agent_identity: str = "supervisor"
    agent_role: str = "supervisor"
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"
    otel_service_name: str = "cs-agent-system"
    otel_traces_exporter: str = "console"
    token_ttl_minutes: int = 10
    crm_mock_url: str = "http://localhost:8010"
    billing_mock_url: str = "http://localhost:8011"
    diagnostics_mock_url: str = "http://localhost:8012"


settings = Settings()
