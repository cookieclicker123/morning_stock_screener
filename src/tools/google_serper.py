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
        
        # Check filter_sites parameter
        if "filter_sites" in params:
            if not isinstance(params["filter_sites"], bool):
                self.logger.error("filter_sites must be a boolean")
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
                - filter_sites: Whether to filter results to financial websites (optional, default True)
                
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
        
        # Add intelligent site filtering based on query type and content
        if params.get("filter_sites", True):
            relevant_sites = self._get_relevant_sites_for_query(query, search_type)
            if relevant_sites:
                site_filter = " OR ".join([f"site:{site}" for site in relevant_sites])
                payload["q"] = f"({payload['q']}) ({site_filter})"
        
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

    def _get_relevant_sites_for_query(self, query: str, search_type: str) -> List[str]:
        """Intelligently select the most relevant websites based on query content and search type.
        
        This method analyzes the query and search type to determine which websites are most relevant,
        avoiding the inefficiency of searching all websites for every query.
        
        Args:
            query: The search query string
            search_type: Type of search (search, news, images, videos)
            
        Returns:
            List of relevant website domains to search
        """
        query_lower = query.lower()
        
        # Define website categories for different types of queries
        website_categories = {
            # Core Financial News & Analysis (for general financial queries)
            "core_financial": [
                "yahoo.com/finance", "cnbc.com", "bloomberg.com", "marketwatch.com",
                "reuters.com", "wsj.com", "ft.com", "forbes.com", "thestreet.com",
                "investopedia.com", "google.com/finance"
            ],
            
            # Financial Data & Analysis Platforms (for stock-specific queries)
            "financial_data": [
                "stockanalysis.com", "wallstreetzen.com", "finbox.com", "simplywall.st",
                "investing.com", "tradingview.com", "morningstar.com", "marketbeat.com",
                "fool.com", "seekingalpha.com", "alphaquery.com", "quiverquant.com",
                "finviz.com", "stocktwits.com", "tipranks.com", "zacks.com",
                # Specialized Financial Data & Research
                "factset.com", "refinitiv.com", "bloomberg.com/professional",
                "spratings.com", "fitchratings.com", "moodys.com",
                "capitaliq.com", "snl.com", "thomsonreuters.com",
                "screener.co", "gurufocus.com", "stockrover.com"
            ],
            
            # Government & Economic Data (for macroeconomic queries)
            "government_economic": [
                "federalreserve.gov", "bls.gov", "bea.gov", "census.gov", "treasury.gov",
                "sec.gov", "fdic.gov", "cftc.gov", "irs.gov", "whitehouse.gov/cea",
                "fred.stlouisfed.org", "worldbank.org", "imf.org", "oecd.org",
                # Regional Federal Reserve Banks
                "newyorkfed.org", "frbsf.org", "frbatlanta.org", "frbchicago.org",
                "frbdallas.org", "frbkc.org", "frbphiladelphia.org", "frbminneapolis.org",
                "frbcleveland.org", "frbstlouis.org", "frbboston.org", "frbrichmond.org",
                # Additional Economic Data Sources
                "bea.gov/regional", "usitc.gov", "census.gov/foreign-trade",
                "bls.gov/regions", "dol.gov/agencies", "commerce.gov/data"
            ],
            
            # Index & ETF Providers (for market index queries)
            "index_etf": [
                "spglobal.com", "nasdaq.com", "nyse.com", "cboe.com", "vix.com",
                "ishares.com", "vanguard.com", "spdrs.com", "invesco.com",
                "schwab.com", "fidelity.com", "tdameritrade.com"
            ],
            
            # Credit Rating & Risk Agencies (for credit/risk queries)
            "credit_risk": [
                "standardandpoors.com", "moodys.com", "fitchratings.com",
                "kroll.com", "am-best.com", "dbrs.com"
            ],
            
            # Commodity & Currency Data (for commodity/currency queries)
            "commodities_currencies": [
                "kitco.com", "oilprice.com", "goldprice.org", "copper.org",
                "lme.com", "comex.com", "nymex.com", "ice.com"
            ],
            
            # Real Estate & Housing Data (for real estate queries)
            "real_estate": [
                "realtor.com", "zillow.com", "redfin.com", "huduser.gov",
                "nahb.org", "nar.realtor", "freddiemac.com", "fanniemae.com"
            ],
            
            # Employment & Labor Data (for employment queries)
            "employment_labor": [
                "bls.gov", "dol.gov", "adp.com", "indeed.com", "linkedin.com",
                "glassdoor.com", "salary.com", "payscale.com"
            ],
            
            # Manufacturing & Industrial Data (for manufacturing queries)
            "manufacturing_industrial": [
                "ismworld.org", "chicagofed.org", "philadelphiafed.org",
                "richmondfed.org", "kc.frb.org", "dallasfed.org"
            ],
            
            # Technology & Innovation Data (for tech queries)
            "technology_innovation": [
                "gartner.com", "forrester.com", "idc.com", "statista.com",
                "crunchbase.com", "pitchbook.com", "cbinsights.com",
                # Specialized Tech Research & Data
                "techcrunch.com", "wired.com", "ars-technica.com", "verge.com",
                "recode.net", "protocol.com", "axios.com/technology",
                "techmeme.com", "hackernews.com", "stackoverflow.com",
                "github.com", "gitlab.com", "bitbucket.org"
            ],
            
            # Healthcare & Biotech Data (for healthcare queries)
            "healthcare_biotech": [
                "fda.gov", "nih.gov", "cdc.gov", "who.int", "biospace.com",
                "genomeweb.com", "fiercebiotech.com", "biopharmadive.com",
                # Specialized Healthcare Research & Data
                "clinicaltrials.gov", "drugs.com", "medscape.com", "webmd.com",
                "mayoclinic.org", "hopkinsmedicine.org", "clevelandclinic.org",
                "biocentury.com", "endpts.com", "statnews.com",
                "fiercepharma.com", "pharmalive.com", "pharmaceutical-journal.com"
            ],
            
            # Energy & Environmental Data (for energy queries)
            "energy_environmental": [
                "eia.gov", "epa.gov", "iea.org", "opec.org", "bp.com",
                "shell.com", "exxonmobil.com", "chevron.com",
                # Specialized Energy Research & Data
                "rigzone.com", "oilprice.com", "naturalgasintel.com", "platts.com",
                "argusmedia.com", "s&pglobal.com/platts", "woodmac.com",
                "rbnenergy.com", "energyintel.com", "renewableenergyworld.com",
                "greentechmedia.com", "utilitydive.com", "energynews.com"
            ],
            
            # Academic & Research Institutions (for research queries)
            "academic_research": [
                "harvard.edu", "mit.edu", "stanford.edu", "princeton.edu",
                "chicagobooth.edu", "wharton.upenn.edu", "columbia.edu",
                "nber.org", "brookings.edu", "cepr.org"
            ],
            
            # Alternative Data & Social Sentiment (for sentiment queries)
            "alternative_social": [
                "reddit.com/r/stocks", "reddit.com/r/ValueInvesting", 
                "reddit.com/r/wallstreetbets", "reddit.com/r/investing",
                "stocktwits.com", "twitter.com"
            ],
            
            # Specialized Earnings & M&A Data (for earnings and deal queries)
            "earnings_ma_data": [
                "zacks.com/earnings", "factset.com/earnings", "refinitiv.com/earnings",
                "bloomberg.com/earnings", "s&pglobal.com/earnings", "morningstar.com/earnings",
                "mergermarket.com", "dealogic.com", "pitchbook.com/ma",
                "thomsonreuters.com/ma", "sdcplatinum.com", "preqin.com"
            ],
            
            # Specialized Regulatory & Legal Data (for regulatory queries)
            "regulatory_legal_data": [
                "sec.gov/edgar", "federalregister.gov", "regulations.gov",
                "cfpb.gov", "fdic.gov", "occ.gov", "federalreserve.gov/regulations",
                "bloomberg.com/regulatory", "reuters.com/legal", "law360.com",
                "lexology.com", "mlex.com", "regulatoryfocus.com"
            ],
            
            # Specialized Industry Research (for industry-specific queries)
            "industry_research": [
                "ibisworld.com", "freedoniagroup.com", "frost.com", "technavio.com",
                "marketsandmarkets.com", "grandviewresearch.com", "persistencemarketresearch.com",
                "transparencymarketresearch.com", "alliedmarketresearch.com", "coherentmarketinsights.com"
            ],
            
            # Specialized Commodity & Trading Data (for commodity queries)
            "commodity_trading": [
                "kitco.com", "goldprice.org", "silverprice.org", "copper.org",
                "lme.com", "comex.com", "nymex.com", "ice.com", "cbot.com",
                "platts.com", "argusmedia.com", "s&pglobal.com/commodities",
                "bloomberg.com/commodities", "reuters.com/commodities"
            ],
            
            # Specialized Real Estate Data (for real estate queries)
            "real_estate_data": [
                "realtor.com", "zillow.com", "redfin.com", "trulia.com",
                "huduser.gov", "nahb.org", "nar.realtor", "freddiemac.com",
                "fanniemae.com", "corelogic.com", "blackknight.com",
                "attomdata.com", "realtytrac.com", "rentdata.com"
            ],
            
            # Specialized Employment & Labor Data (for employment queries)
            "employment_labor_data": [
                "bls.gov", "dol.gov", "adp.com", "indeed.com", "linkedin.com",
                "glassdoor.com", "salary.com", "payscale.com", "monster.com",
                "careerbuilder.com", "simplyhired.com", "ziprecruiter.com",
                "manpower.com", "adecco.com", "kellyservices.com"
            ]
        }
        
        # Determine which categories are relevant based on query content
        relevant_categories = []
        
        # Always include core financial for financial queries
        relevant_categories.append("core_financial")
        
        # Macroeconomic indicators and economic data
        macro_keywords = [
            "gdp", "cpi", "inflation", "unemployment", "employment", "fed", "federal reserve",
            "interest rate", "yield", "treasury", "bond", "economic growth", "recession",
            "monetary policy", "fiscal policy", "trade deficit", "current account",
            "manufacturing", "ism", "pmi", "housing", "real estate", "construction"
        ]
        if any(keyword in query_lower for keyword in macro_keywords):
            relevant_categories.extend(["government_economic", "employment_labor", "real_estate", "manufacturing_industrial"])
        
        # Stock-specific queries
        stock_keywords = [
            "stock", "earnings", "revenue", "profit", "margin", "pe ratio", "p/e",
            "market cap", "valuation", "dividend", "balance sheet", "income statement",
            "cash flow", "analyst", "price target", "buy", "sell", "hold", "upgrade",
            "downgrade", "technical", "chart", "support", "resistance", "trend"
        ]
        if any(keyword in query_lower for keyword in stock_keywords):
            relevant_categories.extend(["financial_data", "index_etf", "earnings_ma_data"])
        
        # News and market sentiment
        news_keywords = [
            "news", "announcement", "press release", "ceo", "executive", "merger",
            "acquisition", "ipo", "spac", "bankruptcy", "lawsuit", "regulation",
            "sec", "fda", "approval", "clinical trial", "earnings call", "conference call"
        ]
        if any(keyword in query_lower for keyword in news_keywords):
            relevant_categories.extend(["core_financial", "alternative_social", "earnings_ma_data", "regulatory_legal_data"])
        
        # Sector-specific queries
        if any(sector in query_lower for sector in ["tech", "technology", "software", "ai", "artificial intelligence"]):
            relevant_categories.append("technology_innovation")
        
        if any(sector in query_lower for sector in ["healthcare", "biotech", "pharma", "medical", "drug"]):
            relevant_categories.append("healthcare_biotech")
        
        if any(sector in query_lower for sector in ["energy", "oil", "gas", "renewable", "solar", "wind"]):
            relevant_categories.extend(["energy_environmental", "commodity_trading"])
        
        if any(sector in query_lower for sector in ["commodity", "gold", "silver", "copper", "oil", "gas"]):
            relevant_categories.extend(["commodities_currencies", "commodity_trading"])
        
        if any(sector in query_lower for sector in ["credit", "rating", "risk", "default", "bankruptcy"]):
            relevant_categories.append("credit_risk")
        
        # Industry and competitive analysis queries
        industry_keywords = [
            "industry", "sector", "competitive", "market share", "competition", "peer",
            "industry analysis", "market research", "industry trends", "competitive advantage"
        ]
        if any(keyword in query_lower for keyword in industry_keywords):
            relevant_categories.append("industry_research")
        
        # Real estate specific queries
        real_estate_keywords = [
            "housing", "real estate", "property", "mortgage", "home", "construction",
            "building", "development", "reit", "real estate investment trust"
        ]
        if any(keyword in query_lower for keyword in real_estate_keywords):
            relevant_categories.extend(["real_estate", "real_estate_data"])
        
        # Employment and labor specific queries
        employment_keywords = [
            "employment", "unemployment", "jobs", "labor", "wages", "salary",
            "hiring", "firing", "workforce", "job market", "labor force"
        ]
        if any(keyword in query_lower for keyword in employment_keywords):
            relevant_categories.extend(["employment_labor", "employment_labor_data"])
        
        # Remove duplicates and flatten the list
        unique_categories = list(set(relevant_categories))
        relevant_sites = []
        for category in unique_categories:
            relevant_sites.extend(website_categories[category])
        
        # Limit to reasonable number to avoid query length issues
        return relevant_sites[:25]  # Keep queries manageable

    async def execute_staggered_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a comprehensive search using staggered queries across ALL financial websites.
        
        This method implements the "holding pen" approach by running multiple focused searches
        across all 100+ financial websites and collecting all results before returning them 
        to the LLM for analysis.
        
        Args:
            params: Search parameters containing:
                - query: Base search query string
                - num_results: Number of results per search (optional, default 5)
                - search_type: Type of search (optional, default "search")
                - country: Country code for localized results (optional)
                - language: Language code (optional)
                - max_searches: Maximum number of staggered searches (optional, default 18)
                
        Returns:
            Dictionary containing aggregated search results from all sources
        """
        base_query = params["query"].strip()
        num_results = params.get("num_results", 5)
        search_type = params.get("search_type", "search")
        country = params.get("country", "us")
        language = params.get("language", "en")
        max_searches = params.get("max_searches", 18)
        
        # Define website categories for staggered searching using ALL the comprehensive websites
        website_categories = [
            # Category 1: Core Financial News & Analysis
            {
                "name": "core_financial",
                "sites": ["yahoo.com/finance", "cnbc.com", "bloomberg.com", "marketwatch.com", 
                         "reuters.com", "ft.com", "forbes.com", "wsj.com", "money.cnn.com",
                         "thestreet.com", "investopedia.com", "google.com/finance"]
            },
            # Category 2: Financial Data & Analysis Platforms
            {
                "name": "data_platforms", 
                "sites": ["stockanalysis.com", "wallstreetzen.com", "finbox.com", "simplywall.st",
                         "investing.com", "tradingview.com", "morningstar.com", "marketbeat.com",
                         "fool.com", "seekingalpha.com", "alphaquery.com", "quiverquant.com",
                         "finviz.com", "stocktwits.com", "tipranks.com", "zacks.com"]
            },
            # Category 3: Government & Central Bank Sources (Critical for Macro Data)
            {
                "name": "government_central_banks",
                "sites": ["federalreserve.gov", "bls.gov", "bea.gov", "census.gov", "treasury.gov",
                         "sec.gov", "fdic.gov", "cftc.gov", "irs.gov", "whitehouse.gov/cea"]
            },
            # Category 4: Economic Data & Research
            {
                "name": "economic_research",
                "sites": ["fred.stlouisfed.org", "worldbank.org", "imf.org", "oecd.org",
                         "ecb.europa.eu", "bankofengland.co.uk", "boj.or.jp", "pboc.gov.cn",
                         "bis.org", "nber.org", "brookings.edu", "cepr.org"]
            },
            # Category 5: Index & ETF Providers
            {
                "name": "index_etf_providers",
                "sites": ["spglobal.com", "nasdaq.com", "nyse.com", "cboe.com", "vix.com",
                         "ishares.com", "vanguard.com", "spdrs.com", "invesco.com",
                         "schwab.com", "fidelity.com", "tdameritrade.com"]
            },
            # Category 6: Credit Rating & Risk Agencies
            {
                "name": "credit_ratings_risk",
                "sites": ["standardandpoors.com", "moodys.com", "fitchratings.com",
                         "kroll.com", "am-best.com", "dbrs.com"]
            },
            # Category 7: Commodity & Currency Data
            {
                "name": "commodities_currencies",
                "sites": ["kitco.com", "oilprice.com", "goldprice.org", "copper.org",
                         "lme.com", "comex.com", "nymex.com", "ice.com"]
            },
            # Category 8: Real Estate & Housing Data
            {
                "name": "real_estate_housing",
                "sites": ["realtor.com", "zillow.com", "redfin.com", "huduser.gov",
                         "nahb.org", "nar.realtor", "freddiemac.com", "fanniemae.com"]
            },
            # Category 9: Employment & Labor Data
            {
                "name": "employment_labor",
                "sites": ["bls.gov", "dol.gov", "adp.com", "indeed.com", "linkedin.com",
                         "glassdoor.com", "salary.com", "payscale.com"]
            },
            # Category 10: Manufacturing & Industrial Data
            {
                "name": "manufacturing_industrial",
                "sites": ["ismworld.org", "chicagofed.org", "philadelphiafed.org",
                         "richmondfed.org", "kc.frb.org", "dallasfed.org"]
            },
            # Category 11: Technology & Innovation Data
            {
                "name": "technology_innovation",
                "sites": ["gartner.com", "forrester.com", "idc.com", "statista.com",
                         "crunchbase.com", "pitchbook.com", "cbinsights.com"]
            },
            # Category 12: Healthcare & Biotech Data
            {
                "name": "healthcare_biotech",
                "sites": ["fda.gov", "nih.gov", "cdc.gov", "who.int", "biospace.com",
                         "genomeweb.com", "fiercebiotech.com", "biopharmadive.com"]
            },
            # Category 13: Energy & Environmental Data
            {
                "name": "energy_environmental",
                "sites": ["eia.gov", "epa.gov", "iea.org", "opec.org", "bp.com",
                         "shell.com", "exxonmobil.com", "chevron.com"]
            },
            # Category 14: Academic & Research Institutions
            {
                "name": "academic_research",
                "sites": ["harvard.edu", "mit.edu", "stanford.edu", "princeton.edu",
                         "chicagobooth.edu", "wharton.upenn.edu", "columbia.edu"]
            },
            # Category 15: Professional Associations & Standards
            {
                "name": "professional_associations",
                "sites": ["cfainstitute.org", "garp.org", "prmia.org", "iafe.org",
                         "sifma.org", "icma.org", "isda.org"]
            },
            # Category 16: Alternative Data & Social Sentiment
            {
                "name": "alternative_social_sentiment",
                "sites": ["reddit.com/r/stocks", "reddit.com/r/ValueInvesting", 
                         "reddit.com/r/wallstreetbets", "reddit.com/r/investing", 
                         "twitter.com", "stocktwits.com", "glassdoor.com", "indeed.com", "linkedin.com"]
            },
            # Category 17: Regulatory & Legal Sources
            {
                "name": "regulatory_legal",
                "sites": ["supremecourt.gov", "congress.gov", "gao.gov", "cbo.gov",
                         "federalregister.gov", "regulations.gov"]
            },
            # Category 18: International Financial Centers
            {
                "name": "international_financial_centers",
                "sites": ["londonstockexchange.com", "deutsche-boerse.com", "euronext.com",
                         "tmx.com", "asx.com.au", "sgx.com", "hkex.com.hk",
                         "tse.or.jp", "bseindia.com", "nseindia.com"]
            }
        ]
        
        # Limit to max_searches to avoid overwhelming the API
        website_categories = website_categories[:max_searches]
        
        all_results = []
        search_metadata = {
            "total_searches": len(website_categories),
            "successful_searches": 0,
            "failed_searches": 0,
            "total_results": 0,
            "categories_searched": []
        }
        
        # Execute staggered searches
        for i, category in enumerate(website_categories):
            try:
                # Rate limit between searches
                if i > 0:
                    await self._rate_limit()
                
                # Create category-specific query
                category_sites = " OR ".join([f"site:{site}" for site in category["sites"]])
                category_query = f"({base_query}) ({category_sites})"
                
                # Execute search for this category
                category_params = {
                    "query": category_query,
                    "num_results": num_results,
                    "search_type": search_type,
                    "country": country,
                    "language": language,
                    "filter_sites": False  # Don't apply additional filtering since we're already filtering
                }
                
                # Use the base execute method
                result = await self.execute(category_params)
                
                if result.get("success", False):
                    # Add category metadata to results
                    category_results = result.get("raw_results", {}).get("organic", [])
                    for item in category_results:
                        item["_category"] = category["name"]
                        item["_source_category"] = category["name"]
                    
                    all_results.extend(category_results)
                    search_metadata["successful_searches"] += 1
                    search_metadata["total_results"] += len(category_results)
                    search_metadata["categories_searched"].append(category["name"])
                    
                    self.logger.info(f"Category {category['name']} search successful: {len(category_results)} results")
                else:
                    search_metadata["failed_searches"] += 1
                    self.logger.warning(f"Category {category['name']} search failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                search_metadata["failed_searches"] += 1
                self.logger.error(f"Error in category {category['name']} search: {str(e)}")
        
        # Return aggregated results
        return {
            "query": base_query,
            "search_type": search_type,
            "num_results": num_results,
            "country": country,
            "language": language,
            "staggered_search": True,
            "search_metadata": search_metadata,
            "all_results": all_results,
            "success": search_metadata["successful_searches"] > 0,
            "total_aggregated_results": len(all_results)
        }

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
            "related_questions",
            "staggered_comprehensive_search"
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
            "language",
            "filter_sites"
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
    
    def get_staggered_search_example(self) -> Dict[str, Any]:
        """Get an example of how to use the staggered comprehensive search.
        
        Returns:
            Dictionary with example parameters and expected output
        """
        return {
            "description": "Perform a comprehensive staggered search across all financial websites",
            "method": "execute_staggered_search",
            "params": {
                "query": "Apple stock analysis Q4 2024",
                "num_results": 5,
                "search_type": "search",
                "max_searches": 18,
                "country": "us",
                "language": "en"
            },
            "expected_output": {
                "query": "Apple stock analysis Q4 2024",
                "staggered_search": True,
                "search_metadata": {
                    "total_searches": 18,
                    "successful_searches": "Number of successful category searches",
                    "total_results": "Total aggregated results from all sources"
                },
                "all_results": "Comprehensive results from 100+ financial websites",
                "success": True
            }
        }
