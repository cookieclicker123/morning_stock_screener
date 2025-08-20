"""Market and macroeconomic data models."""

from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field


class MacroeconomicNews(BaseModel):
    """Macroeconomic news and events."""

    headline: str = Field(..., description="News headline")
    summary: str = Field(..., description="Brief summary of the news")
    impact: str = Field(
        ..., description="Expected market impact (positive/negative/neutral)"
    )
    source: str = Field(..., description="News source")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the news was published",
    )
    relevance_score: float = Field(
        ..., ge=0.0, le=1.0, description="Relevance to traders (0-1)"
    )


class MarketConditions(BaseModel):
    """Current market conditions and sentiment."""

    overall_sentiment: str = Field(
        ..., description="Overall market sentiment (bullish/bearish/neutral)"
    )
    volatility_level: str = Field(
        ..., description="Current volatility level (low/medium/high)"
    )
    sector_performance: dict = Field(..., description="Performance by sector")
    market_movers: List[str] = Field(
        default_factory=list, description="Stocks moving the market"
    )
    key_events: List[str] = Field(
        default_factory=list, description="Key events affecting the market"
    )
    economic_indicators: dict = Field(
        ..., description="Key economic indicators and their values"
    )
    macro_news: List[MacroeconomicNews] = Field(
        default_factory=list, description="Relevant macroeconomic news"
    )
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
    )

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}
