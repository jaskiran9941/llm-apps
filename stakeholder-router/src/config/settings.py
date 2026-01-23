"""Configuration settings using Pydantic."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AnthropicSettings(BaseSettings):
    """Anthropic API configuration."""

    api_key: str = Field(..., alias="ANTHROPIC_API_KEY")
    model: str = Field(default="claude-sonnet-4-20250514", alias="DEFAULT_MODEL")
    max_tokens: int = Field(default=4096, alias="MAX_TOKENS")
    temperature: float = Field(default=0.7, alias="TEMPERATURE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class RouterSettings(BaseSettings):
    """Router configuration."""

    default_strategy: str = Field(
        default="ask_clarifying",
        alias="DEFAULT_ROUTING_STRATEGY"
    )
    confidence_threshold_high: float = Field(
        default=0.8,
        alias="CONFIDENCE_THRESHOLD_HIGH"
    )
    confidence_threshold_low: float = Field(
        default=0.5,
        alias="CONFIDENCE_THRESHOLD_LOW"
    )
    enable_ood_detection: bool = Field(
        default=True,
        alias="ENABLE_OOD_DETECTION"
    )
    allow_multi_expert: bool = Field(
        default=True,
        alias="ALLOW_MULTI_EXPERT"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class AppSettings(BaseSettings):
    """Application-wide settings."""

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Singleton instances
anthropic_settings = AnthropicSettings()
router_settings = RouterSettings()
app_settings = AppSettings()
