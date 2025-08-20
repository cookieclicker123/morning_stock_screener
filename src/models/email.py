"""Email content data models."""

from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field, field_validator

from .market import MarketConditions
from .stock import Stock


class EmailContent(BaseModel):
    """Content structure for the daily stock email."""

    subject: str = Field(..., description="Email subject line")
    market_summary: str = Field(..., description="General market conditions summary")
    market_conditions: MarketConditions = Field(
        ..., description="Detailed market conditions"
    )
    top_stocks: List[Stock] = Field(..., description="Top 10 stock recommendations")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the email was generated",
    )

    @field_validator("top_stocks")
    @classmethod
    def validate_top_stocks(cls, v):
        """Ensure exactly 10 stocks are provided."""
        if len(v) != 10:
            raise ValueError("Must provide exactly 10 top stocks")
        return v


class StockEmail(BaseModel):
    """Complete email structure for sending."""

    to_email: str = Field(..., description="Recipient email address")
    from_email: str = Field(..., description="Sender email address")
    content: EmailContent = Field(..., description="Email content")

    @field_validator("to_email", "from_email")
    @classmethod
    def validate_email_format(cls, v):
        """Basic email format validation."""
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}
