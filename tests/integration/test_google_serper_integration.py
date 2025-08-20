"""Integration tests for GoogleSerperTool with real API calls."""

import pytest
import os
from src.tools.google_serper import GoogleSerperTool


class TestGoogleSerperIntegration:
    """Integration tests for GoogleSerperTool with real Serper API."""

    def setup_method(self):
        """Set up test fixtures."""
        # Skip tests if no API key is available
        if not os.getenv('SERPER_API_KEY'):
            pytest.skip("SERPER_API_KEY not found - skipping integration tests")

    @pytest.mark.asyncio
    async def test_real_web_search(self):
        """Test real web search with Serper API."""
        tool = GoogleSerperTool()
        
        params = {
            "query": "stock market news today",
            "num_results": 3,
            "search_type": "search",
            "country": "us",
            "language": "en"
        }
        
        result = await tool.run(params)
        
        # Verify successful response
        assert result["success"] is True
        assert result["query"] == "stock market news today"
        assert result["search_type"] == "search"
        assert result["total_results"] >= 1
        assert len(result["organic_results"]) >= 1
        
        # Verify result structure
        first_result = result["organic_results"][0]
        assert "title" in first_result
        assert "link" in first_result
        assert "snippet" in first_result
        assert first_result["title"] != ""
        assert first_result["link"].startswith("http")

    @pytest.mark.asyncio
    async def test_real_news_search(self):
        """Test real news search with Serper API."""
        tool = GoogleSerperTool()
        
        params = {
            "query": "Apple stock earnings",
            "num_results": 5,
            "search_type": "news",
            "country": "us",
            "language": "en"
        }
        
        result = await tool.run(params)
        
        # Verify successful response
        assert result["success"] is True
        assert result["search_type"] == "news"
        assert result["total_results"] >= 1
        assert len(result["organic_results"]) >= 1
        
        # Verify news-specific content
        first_result = result["organic_results"][0]
        assert "title" in first_result
        assert "link" in first_result
        assert "snippet" in first_result

    @pytest.mark.asyncio
    async def test_real_financial_search(self):
        """Test real financial search with Serper API."""
        tool = GoogleSerperTool()
        
        params = {
            "query": "S&P 500 performance 2024",
            "num_results": 3,
            "search_type": "search"
        }
        
        result = await tool.run(params)
        
        # Verify successful response
        assert result["success"] is True
        assert result["total_results"] >= 1
        
        # Check if we got financial data
        found_financial_content = False
        for organic_result in result["organic_results"]:
            if any(term in organic_result["snippet"].lower() 
                   for term in ["s&p", "stock", "market", "index", "performance"]):
                found_financial_content = True
                break
        
        assert found_financial_content, "Expected financial content in search results"

    @pytest.mark.asyncio
    async def test_search_modalities(self):
        """Test different search modalities as required by the plan."""
        tool = GoogleSerperTool()
        
        # Test 1: General web search
        web_result = await tool.run({
            "query": "Tesla stock analysis",
            "search_type": "search",
            "num_results": 2
        })
        assert web_result["success"] is True
        assert web_result["search_type"] == "search"
        
        # Test 2: News search
        news_result = await tool.run({
            "query": "Tesla earnings report",
            "search_type": "news",
            "num_results": 2
        })
        assert news_result["success"] is True
        assert news_result["search_type"] == "news"
        
        # Test 3: Different countries/languages
        uk_result = await tool.run({
            "query": "FTSE 100 index",
            "search_type": "search",
            "country": "uk",
            "language": "en",
            "num_results": 2
        })
        assert uk_result["success"] is True
        assert uk_result["country"] == "uk"
        
        print("✅ All search modalities working correctly!")

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test that rate limiting works in practice."""
        tool = GoogleSerperTool()
        
        # Make multiple rapid requests
        results = []
        for i in range(3):
            result = await tool.run({
                "query": f"test query {i}",
                "num_results": 1
            })
            results.append(result)
        
        # All should succeed (rate limiting should handle the delays)
        for result in results:
            assert result["success"] is True
        
        print("✅ Rate limiting working correctly!")

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling with invalid queries."""
        tool = GoogleSerperTool()
        
        # Test empty query (should fail validation and raise exception)
        with pytest.raises(RuntimeError, match="Tool GoogleSerper execution failed: Invalid parameters for GoogleSerper"):
            await tool.run({"query": ""})
        
        print("✅ Error handling working correctly!")
