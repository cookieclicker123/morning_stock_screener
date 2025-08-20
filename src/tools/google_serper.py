"""Google Serper tool for web search functionality."""

import asyncio
import httpx
from typing import Any, Dict, List, Optional
from pathlib import Path
import logging

from .base import BaseTool
from ..config import get_settings


class GoogleSerperTool(BaseTool):
    """Google Serper tool for performing web searches.
    
    This tool provides web search functionality using the Serper API,
    which offers fast and reliable Google search results.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize the Google Serper tool.
        
        Args:
            output_dir: Directory to save tool outputs
        """
        super().__init__("GoogleSerper", output_dir)
        self.settings = get_settings()
        self.api_key = self.settings.serper_api_key
        self.base_url = "https://google.serper.dev/search"
        
        # Rate limiting settings
        self.max_requests_per_minute = 100  # Serper free tier limit
        self.request_delay = 60.0 / self.max_requests_per_minute  # Delay between requests
        self.last_request_time = 0.0

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate search parameters.
        
        Args:
            params: Search parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        required_fields = ["query"]
        
        # Check required fields
        for field in required_fields:
            if field not in params:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Check query is not empty
        if not params["query"] or not params["query"].strip():
            self.logger.error("Query cannot be empty")
            return False
        
        # Check optional fields
        if "num_results" in params:
            num_results = params["num_results"]
            if not isinstance(num_results, int) or num_results < 1 or num_results > 100:
                self.logger.error("num_results must be an integer between 1 and 100")
                return False
        
        return True

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a web search using Serper API.
        
        Args:
            params: Search parameters containing:
                - query: Search query string
                - num_results: Number of results to return (optional, default 10)
                - search_type: Type of search (optional, default "search")
                - country: Country code for localized results (optional)
                - language: Language code (optional)
                
        Returns:
            Dictionary containing search results and metadata
        """
        # Rate limiting
        await self._rate_limit()
        
        # Extract parameters
        query = params["query"].strip()
        num_results = params.get("num_results", 10)
        search_type = params.get("search_type", "search")
        country = params.get("country", "us")
        language = params.get("language", "en")
        
        # Prepare request payload
        payload = {
            "q": query,
            "num": min(num_results, 100),  # Ensure we don't exceed API limits
            "gl": country,
            "hl": language
        }
        
        # Add search type specific parameters
        if search_type == "news":
            payload["tbm"] = "nws"
        elif search_type == "images":
            payload["tbm"] = "isch"
        elif search_type == "videos":
            payload["tbm"] = "vid"
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers
                )
                
                response.raise_for_status()
                search_results = response.json()
                
                # Log successful search
                self.logger.info(f"Search completed: '{query}' returned {len(search_results.get('organic', []))} results")
                
                return {
                    "query": query,
                    "search_type": search_type,
                    "num_results": num_results,
                    "country": country,
                    "language": language,
                    "raw_results": search_results,
                    "success": True
                }
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            self.logger.error(error_msg)
            return {
                "query": query,
                "error": error_msg,
                "success": False,
                "http_status": e.response.status_code
            }
            
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            self.logger.error(error_msg)
            return {
                "query": query,
                "error": error_msg,
                "success": False
            }
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            return {
                "query": query,
                "error": error_msg,
                "success": False
            }

    def format_output(self, raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """Format and structure the raw search results.
        
        Args:
            raw_output: Raw output from the search execution
            
        Returns:
            Formatted search results with structured data
        """
        if not raw_output.get("success", False):
            return raw_output
        
        raw_results = raw_output.get("raw_results", {})
        
        # Extract and format organic results
        organic_results = []
        for result in raw_results.get("organic", [])[:raw_output.get("num_results", 10)]:
            formatted_result = {
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "position": result.get("position", 0)
            }
            
            # Add additional fields if available
            if "sitelinks" in result:
                formatted_result["sitelinks"] = result["sitelinks"]
            
            organic_results.append(formatted_result)
        
        # Extract knowledge graph if available
        knowledge_graph = None
        if "knowledgeGraph" in raw_results:
            kg = raw_results["knowledgeGraph"]
            knowledge_graph = {
                "title": kg.get("title", ""),
                "type": kg.get("type", ""),
                "description": kg.get("description", ""),
                "attributes": kg.get("attributes", {}),
                "image_url": kg.get("imageUrl", "")
            }
        
        # Extract related questions if available
        related_questions = []
        for q in raw_results.get("relatedQuestions", []):
            related_questions.append({
                "question": q.get("question", ""),
                "answer": q.get("answer", ""),
                "source": q.get("source", "")
            })
        
        # Format final output
        formatted_output = {
            "query": raw_output["query"],
            "search_type": raw_output["search_type"],
            "num_results": raw_output["num_results"],
            "country": raw_output["country"],
            "language": raw_output["language"],
            "total_results": len(organic_results),
            "organic_results": organic_results,
            "knowledge_graph": knowledge_graph,
            "related_questions": related_questions,
            "search_metadata": {
                "search_time": raw_results.get("searchTime", 0),
                "total_results_approx": raw_results.get("searchInformation", {}).get("totalResults", 0)
            },
            "success": True
        }
        
        return formatted_output

    async def _rate_limit(self):
        """Implement rate limiting for API requests."""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            delay_needed = self.request_delay - time_since_last
            self.logger.debug(f"Rate limiting: waiting {delay_needed:.2f}s")
            await asyncio.sleep(delay_needed)
        
        self.last_request_time = asyncio.get_event_loop().time()

    def get_capabilities(self) -> List[str]:
        """Get a list of capabilities this tool provides.
        
        Returns:
            List of capability strings
        """
        return [
            "web_search",
            "news_search", 
            "image_search",
            "video_search",
            "knowledge_graph",
            "related_questions"
        ]

    def get_required_params(self) -> List[str]:
        """Get a list of required parameters for this tool.
        
        Returns:
            List of required parameter names
        """
        return ["query"]

    def get_optional_params(self) -> List[str]:
        """Get a list of optional parameters for this tool.
        
        Returns:
            List of optional parameter names
        """
        return [
            "num_results",
            "search_type", 
            "country",
            "language"
        ]

    def get_example_usage(self) -> Dict[str, Any]:
        """Get an example of how to use this tool.
        
        Returns:
            Dictionary with example parameters and expected output
        """
        return {
            "description": "Perform a web search using Google Serper API",
            "params": {
                "query": "latest stock market news",
                "num_results": 10,
                "search_type": "news",
                "country": "us",
                "language": "en"
            },
            "expected_output": {
                "query": "latest stock market news",
                "search_type": "news",
                "num_results": 10,
                "organic_results": "List of news articles",
                "success": True
            }
        }
