"""Stock-related data models."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field, field_validator


class StockAnalysis(BaseModel):
    """Detailed analysis of a stock."""

    fundamental_analysis: str = Field(..., description="Detailed fundamental analysis")
    technical_analysis: str = Field(..., description="Detailed technical analysis")
    news_analysis: str = Field(..., description="Detailed news analysis")
    analyst_recommendations: str = Field(
        ..., description="Analyst recommendations summary"
    )
    analyst_price_targets: str = Field(
        ..., description="Analyst price targets and consensus"
    )
    sudden_news: str = Field(
        ..., description="Sudden news, innovative products, regulatory approvals"
    )

    class Config:
        json_encoders = {Decimal: str}


class StockRecommendation(BaseModel):
    """Stock recommendation with reasoning."""

    short_term_reasoning: str = Field(
        ..., description="Why this is a good short-term play"
    )
    long_term_reasoning: str = Field(
        ..., description="Why this is a good long-term investment"
    )
    risk_factors: List[str] = Field(
        default_factory=list, description="Key risk factors to consider"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score from 0-1"
    )


class Stock(BaseModel):
    """Stock information and analysis."""

    name: str = Field(..., description="Company name")
    symbol: str = Field(..., description="Stock ticker symbol")
    price: Decimal = Field(..., description="Current stock price")
    change: Decimal = Field(..., description="Price change from previous close")
    change_percentage: Decimal = Field(
        ..., description="Percentage change from previous close"
    )
    volume: int = Field(..., description="Trading volume")
    market_cap: Decimal = Field(..., description="Market capitalization")
    industry: str = Field(..., description="Industry sector")
    analysis: StockAnalysis = Field(..., description="Detailed stock analysis")
    recommendation: StockRecommendation = Field(
        ..., description="Investment recommendation"
    )
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
    )

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v):
        """Validate stock symbol format."""
        if not v.isalpha():
            raise ValueError("Stock symbol must contain only letters")
        return v.upper()

    @field_validator("price", "change", "change_percentage", "market_cap")
    @classmethod
    def validate_decimal_fields(cls, v):
        """Ensure decimal fields are positive where appropriate."""
        if v < 0 and cls.__name__ in ["price", "market_cap"]:
            raise ValueError(f"{cls.__name__} cannot be negative")
        return v

    model_config = {"json_encoders": {Decimal: str, datetime: lambda v: v.isoformat()}}
