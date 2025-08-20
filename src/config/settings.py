"""Application settings and configuration."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5", env="OPENAI_MODEL")

    # Serper Configuration (for future use)
    serper_api_key: Optional[str] = Field(default=None, env="SERPER_API_KEY")

    # Email Configuration (for future use)
    smtp_server: Optional[str] = Field(default=None, env="SMTP_SERVER")
    smtp_port: Optional[int] = Field(default=None, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")

    # Application Configuration
    app_name: str = Field(default="Morning Stock Screener", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Email Schedule (for future cron job)
    email_schedule_hour: int = Field(default=9, env="EMAIL_SCHEDULE_HOUR")
    email_schedule_minute: int = Field(default=30, env="EMAIL_SCHEDULE_MINUTE")
    email_timezone: str = Field(default="Europe/London", env="EMAIL_TIMEZONE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Application settings
    """
    return Settings()
