"""Tests for data models."""

from decimal import Decimal

import pytest

from ..models.email import EmailContent, StockEmail
from ..models.llm import LLMRequest, LLMResponse
from ..models.market import MacroeconomicNews, MarketConditions
from ..models.stock import Stock, StockAnalysis, StockRecommendation


class TestStockModels:
    """Test stock-related models."""

    def test_stock_analysis_creation(self):
        """Test StockAnalysis model creation."""
        analysis = StockAnalysis(
            fundamental_analysis="Strong balance sheet with low debt",
            technical_analysis="Price above 50-day moving average",
            news_analysis="Positive earnings surprise",
            analyst_recommendations="Buy consensus",
            analyst_price_targets="Target: $150, Current: $120",
            sudden_news="FDA approval for new drug",
        )

        assert analysis.fundamental_analysis == "Strong balance sheet with low debt"
        assert analysis.technical_analysis == "Price above 50-day moving average"
        assert analysis.news_analysis == "Positive earnings surprise"

    def test_stock_recommendation_creation(self):
        """Test StockRecommendation model creation."""
        recommendation = StockRecommendation(
            short_term_reasoning="Technical breakout pattern",
            long_term_reasoning="Strong market position and growth",
            risk_factors=["Market volatility", "Regulatory changes"],
            confidence_score=0.85,
        )

        assert recommendation.short_term_reasoning == "Technical breakout pattern"
        assert recommendation.long_term_reasoning == "Strong market position and growth"
        assert len(recommendation.risk_factors) == 2
        assert recommendation.confidence_score == 0.85

    def test_stock_creation(self):
        """Test Stock model creation."""
        analysis = StockAnalysis(
            fundamental_analysis="Test",
            technical_analysis="Test",
            news_analysis="Test",
            analyst_recommendations="Test",
            analyst_price_targets="Test",
            sudden_news="Test",
        )

        recommendation = StockRecommendation(
            short_term_reasoning="Test",
            long_term_reasoning="Test",
            confidence_score=0.8,
        )

        stock = Stock(
            name="Apple Inc.",
            symbol="AAPL",
            price=Decimal("150.00"),
            change=Decimal("2.50"),
            change_percentage=Decimal("1.67"),
            volume=1000000,
            market_cap=Decimal("2500000000000"),
            industry="Technology",
            analysis=analysis,
            recommendation=recommendation,
        )

        assert stock.name == "Apple Inc."
        assert stock.symbol == "AAPL"
        assert stock.price == Decimal("150.00")
        assert stock.industry == "Technology"

    def test_stock_symbol_validation(self):
        """Test stock symbol validation."""
        analysis = StockAnalysis(
            fundamental_analysis="Test",
            technical_analysis="Test",
            news_analysis="Test",
            analyst_recommendations="Test",
            analyst_price_targets="Test",
            sudden_news="Test",
        )

        recommendation = StockRecommendation(
            short_term_reasoning="Test",
            long_term_reasoning="Test",
            confidence_score=0.8,
        )

        # Test valid symbol
        stock = Stock(
            name="Test",
            symbol="AAPL",
            price=Decimal("100.00"),
            change=Decimal("1.00"),
            change_percentage=Decimal("1.00"),
            volume=1000,
            market_cap=Decimal("1000000000"),
            industry="Test",
            analysis=analysis,
            recommendation=recommendation,
        )
        assert stock.symbol == "AAPL"

        # Test invalid symbol
        with pytest.raises(ValueError, match="Stock symbol must contain only letters"):
            Stock(
                name="Test",
                symbol="AAPL1",
                price=Decimal("100.00"),
                change=Decimal("1.00"),
                change_percentage=Decimal("1.00"),
                volume=1000,
                market_cap=Decimal("1000000000"),
                industry="Test",
                analysis=analysis,
                recommendation=recommendation,
            )


class TestMarketModels:
    """Test market-related models."""

    def test_macroeconomic_news_creation(self):
        """Test MacroeconomicNews model creation."""
        news = MacroeconomicNews(
            headline="Fed Raises Interest Rates",
            summary="Federal Reserve increases rates by 25 basis points",
            impact="negative",
            source="Reuters",
            relevance_score=0.9,
        )

        assert news.headline == "Fed Raises Interest Rates"
        assert news.impact == "negative"
        assert news.relevance_score == 0.9

    def test_market_conditions_creation(self):
        """Test MarketConditions model creation."""
        news = MacroeconomicNews(
            headline="Test",
            summary="Test",
            impact="neutral",
            source="Test",
            relevance_score=0.5,
        )

        conditions = MarketConditions(
            overall_sentiment="bullish",
            volatility_level="medium",
            sector_performance={"tech": "up", "finance": "down"},
            market_movers=["AAPL", "GOOGL"],
            key_events=["Earnings season", "Fed meeting"],
            economic_indicators={"unemployment": "3.5%", "gdp_growth": "2.1%"},
            macro_news=[news],
        )

        assert conditions.overall_sentiment == "bullish"
        assert conditions.volatility_level == "medium"
        assert len(conditions.sector_performance) == 2
        assert len(conditions.macro_news) == 1


class TestEmailModels:
    """Test email-related models."""

    def test_email_content_creation(self):
        """Test EmailContent model creation."""
        # Create mock data
        analysis = StockAnalysis(
            fundamental_analysis="Test",
            technical_analysis="Test",
            news_analysis="Test",
            analyst_recommendations="Test",
            analyst_price_targets="Test",
            sudden_news="Test",
        )

        recommendation = StockRecommendation(
            short_term_reasoning="Test",
            long_term_reasoning="Test",
            confidence_score=0.8,
        )

        stock = Stock(
            name="Test",
            symbol="TEST",
            price=Decimal("100.00"),
            change=Decimal("1.00"),
            change_percentage=Decimal("1.00"),
            volume=1000,
            market_cap=Decimal("1000000000"),
            industry="Test",
            analysis=analysis,
            recommendation=recommendation,
        )

        conditions = MarketConditions(
            overall_sentiment="neutral",
            volatility_level="low",
            sector_performance={},
            market_movers=[],
            key_events=[],
            economic_indicators={},
            macro_news=[],
        )

        content = EmailContent(
            subject="Daily Stock Picks",
            market_summary="Market is stable today",
            market_conditions=conditions,
            top_stocks=[stock] * 10,  # Create 10 identical stocks for testing
        )

        assert content.subject == "Daily Stock Picks"
        assert content.market_summary == "Market is stable today"
        assert len(content.top_stocks) == 10

    def test_email_content_validation(self):
        """Test EmailContent validation."""
        # Test with less than 10 stocks
        analysis = StockAnalysis(
            fundamental_analysis="Test",
            technical_analysis="Test",
            news_analysis="Test",
            analyst_recommendations="Test",
            analyst_price_targets="Test",
            sudden_news="Test",
        )

        recommendation = StockRecommendation(
            short_term_reasoning="Test",
            long_term_reasoning="Test",
            confidence_score=0.8,
        )

        stock = Stock(
            name="Test",
            symbol="TEST",
            price=Decimal("100.00"),
            change=Decimal("1.00"),
            change_percentage=Decimal("1.00"),
            volume=1000,
            market_cap=Decimal("1000000000"),
            industry="Test",
            analysis=analysis,
            recommendation=recommendation,
        )

        conditions = MarketConditions(
            overall_sentiment="neutral",
            volatility_level="low",
            sector_performance={},
            market_movers=[],
            key_events=[],
            economic_indicators={},
            macro_news=[],
        )

        with pytest.raises(ValueError, match="Must provide exactly 10 top stocks"):
            EmailContent(
                subject="Test",
                market_summary="Test",
                market_conditions=conditions,
                top_stocks=[stock] * 5,  # Only 5 stocks
            )

    def test_stock_email_creation(self):
        """Test StockEmail model creation."""
        # Create mock content
        analysis = StockAnalysis(
            fundamental_analysis="Test",
            technical_analysis="Test",
            news_analysis="Test",
            analyst_recommendations="Test",
            analyst_price_targets="Test",
            sudden_news="Test",
        )

        recommendation = StockRecommendation(
            short_term_reasoning="Test",
            long_term_reasoning="Test",
            confidence_score=0.8,
        )

        stock = Stock(
            name="Test",
            symbol="TEST",
            price=Decimal("100.00"),
            change=Decimal("1.00"),
            change_percentage=Decimal("1.00"),
            volume=1000,
            market_cap=Decimal("1000000000"),
            industry="Test",
            analysis=analysis,
            recommendation=recommendation,
        )

        conditions = MarketConditions(
            overall_sentiment="neutral",
            volatility_level="low",
            sector_performance={},
            market_movers=[],
            key_events=[],
            economic_indicators={},
            macro_news=[],
        )

        content = EmailContent(
            subject="Test",
            market_summary="Test",
            market_conditions=conditions,
            top_stocks=[stock] * 10,
        )

        email = StockEmail(
            to_email="user@example.com",
            from_email="screener@example.com",
            content=content,
        )

        assert email.to_email == "user@example.com"
        assert email.from_email == "screener@example.com"
        assert email.content == content


class TestLLMModels:
    """Test LLM-related models."""

    def test_llm_request_creation(self):
        """Test LLMRequest model creation."""
        request = LLMRequest(
            system_prompt="You are a helpful assistant",
            user_prompt="Tell me about stocks",
            temperature=0.8,
            max_tokens=2000,
            model="gpt-5",
            additional_params={"top_p": 0.9},
        )

        assert request.system_prompt == "You are a helpful assistant"
        assert request.user_prompt == "Tell me about stocks"
        assert request.temperature == 0.8
        assert request.max_tokens == 2000
        assert request.model == "gpt-5"
        assert request.additional_params["top_p"] == 0.9

    def test_llm_response_creation(self):
        """Test LLMResponse model creation."""
        response = LLMResponse(
            content="Here's information about stocks...",
            model_used="gpt-5",
            tokens_used=150,
            finish_reason="stop",
            response_time_ms=2500.5,
            success=True,
        )

        assert response.content == "Here's information about stocks..."
        assert response.model_used == "gpt-5"
        assert response.tokens_used == 150
        assert response.finish_reason == "stop"
        assert response.response_time_ms == 2500.5
        assert response.success is True
        assert response.error_message is None

    def test_llm_response_with_error(self):
        """Test LLMResponse with error."""
        response = LLMResponse(
            content="",
            model_used="gpt-5",
            tokens_used=0,
            finish_reason="error",
            response_time_ms=100.0,
            success=False,
            error_message="API rate limit exceeded",
        )

        assert response.success is False
        assert response.error_message == "API rate limit exceeded"
        assert response.content == ""
