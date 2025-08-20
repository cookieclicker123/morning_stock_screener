#!/usr/bin/env python3
"""
Google Serper Test Client

This client tests 10 broad queries across different categories to validate
the Google Serper tool's functionality and see real results in action.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from src.tools.google_serper import GoogleSerperTool
from src.config.settings import get_settings


class SerperTestClient:
    """Test client for Google Serper tool with comprehensive query testing."""
    
    def __init__(self):
        """Initialize the test client."""
        self.settings = get_settings()
        self.serper_tool = GoogleSerperTool()
        self.output_dir = Path("tmp/google_serper_test_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def test_broad_queries(self) -> Dict[str, Any]:
        """Test 10 broad queries across different categories."""
        
        # Define 10 broad test queries covering different aspects
        test_queries = [
            {
                "name": "macroeconomic_overview",
                "query": "Federal Reserve interest rate decision latest meeting minutes economic outlook",
                "category": "monetary_policy",
                "expected_sources": ["government_economic", "core_financial", "academic_research"]
            },
            {
                "name": "market_sentiment_analysis",
                "query": "S&P 500 technical analysis support resistance levels market sentiment VIX",
                "category": "technical_analysis",
                "expected_sources": ["core_financial", "financial_data", "index_etf"]
            },
            {
                "name": "earnings_performance",
                "query": "earnings season Q4 2024 results beat miss revenue growth top performers",
                "category": "earnings",
                "expected_sources": ["core_financial", "earnings_ma_data", "financial_data"]
            },
            {
                "name": "technology_innovation",
                "query": "artificial intelligence AI breakthrough companies quantum computing development",
                "category": "technology",
                "expected_sources": ["technology_innovation", "core_financial", "academic_research"]
            },
            {
                "name": "healthcare_biotech",
                "query": "biotech breakthrough drug development pipeline FDA approval clinical trials",
                "category": "healthcare",
                "expected_sources": ["healthcare_biotech", "regulatory_legal_data", "core_financial"]
            },
            {
                "name": "energy_commodities",
                "query": "oil price volatility energy market trends renewable energy transition",
                "category": "energy",
                "expected_sources": ["energy_environmental", "commodity_trading", "core_financial"]
            },
            {
                "name": "real_estate_housing",
                "query": "US housing market data home sales existing new construction mortgage rates",
                "category": "real_estate",
                "expected_sources": ["real_estate", "real_estate_data", "government_economic"]
            },
            {
                "name": "employment_labor",
                "query": "US unemployment rate jobs report nonfarm payrolls labor market trends",
                "category": "employment",
                "expected_sources": ["employment_labor", "employment_labor_data", "government_economic"]
            },
            {
                "name": "regulatory_legal",
                "query": "SEC investigation corporate fraud accounting issues regulatory changes",
                "category": "regulatory",
                "expected_sources": ["regulatory_legal_data", "core_financial", "government_economic"]
            },
            {
                "name": "global_economic_impact",
                "query": "China economic growth GDP slowdown US impact global supply chain",
                "category": "global_economy",
                "expected_sources": ["core_financial", "government_economic", "academic_research"]
            }
        ]
        
        print(f"🚀 Starting Google Serper Test Client")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🔍 Testing {len(test_queries)} broad queries...")
        print("=" * 80)
        
        results = {}
        successful_queries = 0
        failed_queries = 0
        
        for i, query_info in enumerate(test_queries, 1):
            print(f"\n📊 Query {i}/{len(test_queries)}: {query_info['name']}")
            print(f"🔍 Query: {query_info['query']}")
            print(f"📂 Category: {query_info['category']}")
            print(f"🎯 Expected Sources: {', '.join(query_info['expected_sources'])}")
            
            try:
                # Test both single query and staggered search
                single_result = await self._test_single_query(query_info)
                staggered_result = await self._test_staggered_search(query_info)
                
                # Combine results
                query_results = {
                    "query_info": query_info,
                    "single_search": single_result,
                    "staggered_search": staggered_result,
                    "timestamp": datetime.now().isoformat(),
                    "success": single_result.get("success", False) or staggered_result.get("success", False)
                }
                
                # Save individual query results
                self._save_query_results(query_info["name"], query_results)
                
                results[query_info["name"]] = query_results
                
                if query_results["success"]:
                    successful_queries += 1
                    print(f"✅ SUCCESS: {single_result.get('total_results', 0)} single results, {staggered_result.get('total_aggregated_results', 0)} staggered results")
                else:
                    failed_queries += 1
                    print(f"❌ FAILED: {single_result.get('error', 'Unknown error')}")
                
            except Exception as e:
                error_result = {
                    "query_info": query_info,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "success": False
                }
                results[query_info["name"]] = error_result
                failed_queries += 1
                print(f"❌ EXCEPTION: {str(e)}")
            
            # Rate limiting between queries
            if i < len(test_queries):
                print("⏳ Waiting 2 seconds before next query...")
                await asyncio.sleep(2)
        
        # Generate summary report
        summary = {
            "test_summary": {
                "total_queries": len(test_queries),
                "successful_queries": successful_queries,
                "failed_queries": failed_queries,
                "success_rate": f"{(successful_queries/len(test_queries)*100):.1f}%",
                "timestamp": datetime.now().isoformat(),
                "test_duration_seconds": None  # Will be calculated
            },
            "query_results": results
        }
        
        # Save summary report
        self._save_summary_report(summary)
        
        print("\n" + "=" * 80)
        print(f"🎯 TEST COMPLETE!")
        print(f"📊 Results: {successful_queries}/{len(test_queries)} successful ({summary['test_summary']['success_rate']})")
        print(f"📁 All results saved to: {self.output_dir}")
        print(f"📋 Summary report: {self.output_dir}/test_summary.json")
        
        return summary
    
    async def _test_single_query(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single query execution."""
        try:
            params = {
                "query": query_info["query"],
                "num_results": 5,
                "search_type": "search",
                "country": "us",
                "language": "en",
                "filter_sites": True  # Test intelligent site filtering
            }
            
            result = await self.serper_tool.execute(params)
            return result
            
        except Exception as e:
            return {
                "query": query_info["query"],
                "error": str(e),
                "success": False
            }
    
    async def _test_staggered_search(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test staggered search execution."""
        try:
            params = {
                "query": query_info["query"],
                "num_results": 3,  # Lower for staggered to avoid rate limits
                "search_type": "search",
                "country": "us",
                "language": "en",
                "max_searches": 5  # Limit for testing
            }
            
            result = await self.serper_tool.execute_staggered_search(params)
            return result
            
        except Exception as e:
            return {
                "query": query_info["query"],
                "error": str(e),
                "success": False
            }
    
    def _save_query_results(self, query_name: str, results: Dict[str, Any]) -> None:
        """Save individual query results to JSON file."""
        filename = f"{query_name}_results.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Saved: {filename}")
    
    def _save_summary_report(self, summary: Dict[str, Any]) -> None:
        """Save comprehensive summary report."""
        filepath = self.output_dir / "test_summary.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Saved: test_summary.json")


async def main():
    """Main function to run the test client."""
    client = SerperTestClient()
    
    try:
        await client.test_broad_queries()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
