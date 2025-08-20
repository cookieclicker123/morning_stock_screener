"""Unit tests for SearchRegistry class."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from datetime import datetime

from src.tools.search_registry import SearchRegistry


class TestSearchRegistry:
    """Test SearchRegistry functionality."""

    def test_initialization(self):
        """Test registry initialization."""
        registry = SearchRegistry()
        
        assert registry.name == "SearchRegistry"
        assert len(registry.market_registry) >= 45  # Increased from 30
        assert len(registry.news_registry) >= 40   # Increased from 30
        assert len(registry.stock_registry) >= 50  # Allow for expansion

    def test_market_registry_content(self):
        """Test market registry contains expected queries."""
        registry = SearchRegistry()
        
        # Check we have the right categories (expanded)
        categories = set(query["category"] for query in registry.market_registry)
        expected_categories = {
            "monetary_policy", "inflation", "gdp", "employment", "consumer_sentiment",
            "manufacturing", "services", "housing", "trade",
            "global_economy", "technical_analysis", "market_sentiment", "sector_analysis",
            "commodities", "currencies", "bonds", "political", "geopolitical", 
            "technology", "climate_esg"
        }
        
        assert categories == expected_categories
        
        # Check specific important queries exist
        queries = [query["query"] for query in registry.market_registry]
        assert any("Federal Reserve interest rate" in q for q in queries)
        assert any("S&P 500 technical analysis" in q for q in queries)
        assert any("VIX volatility index" in q for q in queries)
        assert any("artificial intelligence" in q for q in queries)
        assert any("climate change" in q for q in queries)

    def test_news_registry_content(self):
        """Test news registry contains expected general news queries."""
        registry = SearchRegistry()
        
        # Check we have the right categories (expanded)
        categories = set(query["category"] for query in registry.news_registry)
        expected_categories = {
            "earnings", "analyst_ratings", "m_a", "regulatory", "corporate_actions",
            "insider_activity", "ownership", "industry_trends", "operations", "global_operations",
            "technology", "healthcare", "energy", "financial", "consumer"
        }
        
        assert categories == expected_categories
        
        # Check general news topics exist (no company placeholders)
        queries = [query["query"] for query in registry.news_registry]
        assert any("earnings season" in q for q in queries)
        assert any("artificial intelligence" in q for q in queries)
        assert any("biotech breakthrough" in q for q in queries)
        assert any("fintech disruption" in q for q in queries)

    def test_stock_registry_content(self):
        """Test stock registry contains expected query templates."""
        registry = SearchRegistry()
        
        # Check we have the right categories
        categories = set(query["category"] for query in registry.stock_registry)
        expected_categories = {
            "valuation", "cash_flow", "financial_health", "profitability",
            "growth", "technical", "risk", "competitive", "governance"
        }
        
        assert categories == expected_categories
        
        # Check template placeholders exist
        queries = [query["query"] for query in registry.stock_registry]
        assert any("{company}" in q for q in queries)
        assert any("{sector}" in q for q in queries)
        assert any("{industry}" in q for q in queries)

    def test_validate_params_valid_operations(self):
        """Test parameter validation with valid operations."""
        registry = SearchRegistry()
        
        valid_operations = ["get_market", "get_news", "get_stock", "augment_news", "augment_stock"]
        
        for operation in valid_operations:
            params = {"operation": operation}
            if operation in ["augment_news", "augment_stock"]:
                params["context"] = {"test": "data"}
            
            assert registry.validate_params(params) is True

    def test_validate_params_missing_operation(self):
        """Test parameter validation with missing operation."""
        registry = SearchRegistry()
        
        params = {"query_limit": 10}
        assert registry.validate_params(params) is False

    def test_validate_params_invalid_operation(self):
        """Test parameter validation with invalid operation."""
        registry = SearchRegistry()
        
        params = {"operation": "invalid_operation"}
        assert registry.validate_params(params) is False

    def test_validate_params_missing_context_for_augmentation(self):
        """Test parameter validation for augmentation operations."""
        registry = SearchRegistry()
        
        params = {"operation": "augment_news"}
        assert registry.validate_params(params) is False
        
        params = {"operation": "augment_stock"}
        assert registry.validate_params(params) is False

    def test_get_market_queries_no_limit(self):
        """Test getting all market queries."""
        registry = SearchRegistry()
        
        result = registry._get_market_queries()
        
        assert result["operation"] == "get_market"
        assert result["registry_type"] == "market"
        assert result["query_count"] >= 45  # Increased from 30
        assert len(result["queries"]) >= 45  # Increased from 30
        assert result["metadata"]["augmentation_required"] is False
        assert result["timestamp"]

    def test_get_market_queries_with_limit(self):
        """Test getting limited market queries."""
        registry = SearchRegistry()
        
        result = registry._get_market_queries(query_limit=10)
        
        assert result["query_count"] == 10
        assert len(result["queries"]) == 10

    def test_get_news_queries_no_limit(self):
        """Test getting all news queries."""
        registry = SearchRegistry()
        
        result = registry._get_news_queries()
        
        assert result["operation"] == "get_news"
        assert result["registry_type"] == "news"
        assert result["query_count"] >= 40  # Increased from 30
        assert len(result["queries"]) >= 40  # Increased from 30
        assert result["metadata"]["augmentation_required"] is True
        assert result["timestamp"]

    def test_get_stock_queries_no_limit(self):
        """Test getting all stock queries."""
        registry = SearchRegistry()
        
        result = registry._get_stock_queries()
        
        assert result["operation"] == "get_stock"
        assert result["registry_type"] == "stock"
        assert result["query_count"] >= 50  # Allow for expansion
        assert len(result["queries"]) >= 50  # Allow for expansion
        assert result["metadata"]["augmentation_required"] is True
        assert "50-200+ queries" in result["metadata"]["expected_augmented_count"]

    def test_augment_news_queries_basic(self):
        """Test basic news query augmentation."""
        registry = SearchRegistry()
        
        context = {"market_sentiment": "bullish"}
        result = registry._augment_news_queries(context)
        
        assert result["operation"] == "augment_news"
        assert result["registry_type"] == "news_augmented"
        assert result["query_count"] > 40  # Should have augmented queries (increased from 30)
        assert result["metadata"]["context_used"] == ["market_sentiment"]
        assert result["metadata"]["augmentation_required"] is False

    def test_augment_stock_queries_basic(self):
        """Test basic stock query augmentation."""
        registry = SearchRegistry()
        
        context = {"mentioned_stocks": ["AAPL", "MSFT", "GOOGL"]}
        result = registry._augment_stock_queries(context)
        
        assert result["operation"] == "augment_stock"
        assert result["registry_type"] == "stock_augmented"
        assert result["query_count"] > 50  # Should have augmented queries
        assert result["metadata"]["context_used"] == ["mentioned_stocks"]
        assert result["metadata"]["augmentation_required"] is False

    def test_augment_news_queries_with_limit(self):
        """Test news query augmentation with limit."""
        registry = SearchRegistry()
        
        context = {"market_sentiment": "bearish"}
        result = registry._augment_news_queries(context, query_limit=20)
        
        assert result["query_count"] == 20
        assert len(result["queries"]) == 20

    def test_augment_stock_queries_with_limit(self):
        """Test stock query augmentation with limit."""
        registry = SearchRegistry()
        
        context = {"mentioned_stocks": ["TSLA"]}
        result = registry._augment_stock_queries(context, query_limit=25)
        
        assert result["query_count"] == 25
        assert len(result["queries"]) == 25

    def test_augment_news_queries_empty_context(self):
        """Test news query augmentation with empty context."""
        registry = SearchRegistry()
        
        context = {}
        result = registry._augment_news_queries(context)
        
        assert result["query_count"] >= 40  # Should return base queries only (increased from 30)
        assert result["metadata"]["context_used"] == []

    def test_augment_stock_queries_empty_context(self):
        """Test stock query augmentation with empty context."""
        registry = SearchRegistry()
        
        context = {}
        result = registry._augment_stock_queries(context)
        
        assert result["query_count"] >= 50  # Should return base queries only (allow for expansion)
        assert result["metadata"]["context_used"] == []

    @pytest.mark.asyncio
    async def test_execute_get_market(self):
        """Test executing get_market operation."""
        registry = SearchRegistry()
        
        params = {"operation": "get_market"}
        result = await registry.execute(params)
        
        assert result["operation"] == "get_market"
        assert result["registry_type"] == "market"
        assert result["query_count"] >= 45  # Increased from 30

    @pytest.mark.asyncio
    async def test_execute_get_news(self):
        """Test executing get_news operation."""
        registry = SearchRegistry()
        
        params = {"operation": "get_news"}
        result = await registry.execute(params)
        
        assert result["operation"] == "get_news"
        assert result["registry_type"] == "news"
        assert result["query_count"] >= 40  # Increased from 30

    @pytest.mark.asyncio
    async def test_execute_get_stock(self):
        """Test executing get_stock operation."""
        registry = SearchRegistry()
        
        params = {"operation": "get_stock"}
        result = await registry.execute(params)
        
        assert result["operation"] == "get_stock"
        assert result["registry_type"] == "stock"
        assert result["query_count"] >= 50  # Allow for expansion

    @pytest.mark.asyncio
    async def test_execute_augment_news(self):
        """Test executing augment_news operation."""
        registry = SearchRegistry()
        
        params = {
            "operation": "augment_news",
            "context": {"market_sentiment": "neutral"}
        }
        result = await registry.execute(params)
        
        assert result["operation"] == "augment_news"
        assert result["registry_type"] == "news_augmented"

    @pytest.mark.asyncio
    async def test_execute_augment_stock(self):
        """Test executing augment_stock operation."""
        registry = SearchRegistry()
        
        params = {
            "operation": "augment_stock",
            "context": {"mentioned_stocks": ["NVDA"]}
        }
        result = await registry.execute(params)
        
        assert result["operation"] == "augment_stock"
        assert result["registry_type"] == "stock_augmented"

    @pytest.mark.asyncio
    async def test_execute_unknown_operation(self):
        """Test executing unknown operation."""
        registry = SearchRegistry()
        
        params = {"operation": "unknown_operation"}
        
        with pytest.raises(ValueError, match="Unknown operation: unknown_operation"):
            await registry.execute(params)

    def test_format_output(self):
        """Test output formatting."""
        registry = SearchRegistry()
        
        raw_output = {
            "operation": "get_market",
            "registry_type": "market",
            "query_count": 45,
            "queries": [{"query": "test", "category": "test"}],
            "metadata": {"test": "data"},
            "timestamp": "2023-01-01T00:00:00"
        }
        
        formatted = registry.format_output(raw_output)
        
        assert formatted["operation"] == "get_market"
        assert formatted["registry_type"] == "market"
        assert formatted["query_count"] == 45
        assert formatted["queries"] == [{"query": "test", "category": "test"}]
        assert formatted["metadata"] == {"test": "data"}
        assert formatted["timestamp"] == "2023-01-01T00:00:00"
        assert formatted["success"] is True

    def test_get_capabilities(self):
        """Test getting tool capabilities."""
        registry = SearchRegistry()
        
        capabilities = registry.get_capabilities()
        
        expected_capabilities = [
            "market_query_management",
            "news_query_management", 
            "stock_query_management",
            "query_augmentation",
            "context_aware_search"
        ]
        
        assert capabilities == expected_capabilities

    def test_get_required_params(self):
        """Test getting required parameters."""
        registry = SearchRegistry()
        
        required_params = registry.get_required_params()
        
        assert required_params == ["operation"]

    def test_get_optional_params(self):
        """Test getting optional parameters."""
        registry = SearchRegistry()
        
        optional_params = registry.get_optional_params()
        
        expected_params = [
            "context",
            "query_limit"
        ]
        
        assert optional_params == expected_params

    def test_get_example_usage(self):
        """Test getting example usage."""
        registry = SearchRegistry()
        
        example = registry.get_example_usage()
        
        assert example["description"] == "Manage and augment search queries for market, news, and stock analysis"
        assert "operation" in example["params"]
        assert "expected_output" in example

    def test_market_registry_fixed_queries(self):
        """Test that market registry queries are fixed and comprehensive."""
        registry = SearchRegistry()
        
        # Check we have queries for all major market aspects
        queries = [query["query"].lower() for query in registry.market_registry]
        
        # Macroeconomic indicators
        assert any("federal reserve" in q for q in queries)
        assert any("inflation" in q for q in queries)
        assert any("gdp" in q for q in queries)
        assert any("unemployment" in q for q in queries)
        
        # Technical analysis
        assert any("s&p 500" in q for q in queries)
        assert any("nasdaq" in q for q in queries)
        assert any("dow jones" in q for q in queries)
        assert any("vix" in q for q in queries)
        
        # Global markets (US-focused impact)
        assert any("china" in q for q in queries)
        assert any("eurozone" in q for q in queries)
        assert any("uk" in q for q in queries)
        
        # New comprehensive coverage areas
        assert any("artificial intelligence" in q for q in queries)
        assert any("climate change" in q for q in queries)
        assert any("election impact" in q for q in queries)  # Political content
        assert any("china relations" in q for q in queries)  # Geopolitical content
        assert any("technology" in q for q in queries)

    def test_news_registry_template_queries(self):
        """Test that news registry contains proper general news queries."""
        registry = SearchRegistry()
        
        # Check for general news queries (no company placeholders)
        queries = [query["query"] for query in registry.news_registry]
        
        # Should NOT have company placeholders - these are general queries
        company_queries = [q for q in queries if "{company}" in q]
        assert len(company_queries) == 0
        
        # Should have general news topics
        assert any("earnings season" in q for q in queries)
        assert any("merger acquisition deals" in q for q in queries)
        assert any("artificial intelligence" in q for q in queries)
        assert any("technology disruption" in q for q in queries)

    def test_stock_registry_comprehensive_coverage(self):
        """Test that stock registry covers all aspects of stock analysis."""
        registry = SearchRegistry()
        
        # Check we have queries for all major stock analysis areas
        queries = [query["query"].lower() for query in registry.stock_registry]
        
        # Fundamental analysis
        assert any("p/e ratio" in q for q in queries)
        assert any("price to book" in q for q in queries)
        assert any("ev/ebitda" in q for q in queries)
        assert any("dividend yield" in q for q in queries)
        
        # Technical analysis
        assert any("moving averages" in q for q in queries)
        assert any("support resistance" in q for q in queries)
        assert any("volume analysis" in q for q in queries)
        
        # Risk assessment
        assert any("beta coefficient" in q for q in queries)
        assert any("volatility analysis" in q for q in queries)
        assert any("credit rating" in q for q in queries)
        
        # Competitive analysis
        assert any("competitive advantage" in q for q in queries)
        assert any("market positioning" in q for q in queries)
        assert any("pricing power" in q for q in queries)
