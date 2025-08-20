"""Search registry system for managing search queries across different domains."""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime

from .base import BaseTool


class SearchRegistry(BaseTool):
    """Search registry system for managing and augmenting search queries.
    
    This tool manages three types of search registries:
    1. Market Registry: Fixed queries for market analysis (30 queries)
    2. News Registry: Placeholder queries for news analysis (30 queries) 
    3. Stock Registry: Placeholder queries for stock analysis (50-70 queries)
    
    Market queries are used directly, while news and stock queries are
    augmented by their respective query generator agents.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize the search registry.
        
        Args:
            output_dir: Directory to save registry outputs
        """
        super().__init__("SearchRegistry", output_dir)
        
        # Initialize the three registries
        self.market_registry = self._initialize_market_registry()
        self.news_registry = self._initialize_news_registry()
        self.stock_registry = self._initialize_stock_registry()

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate registry operation parameters.
        
        Args:
            params: Parameters for registry operations
            
        Returns:
            True if parameters are valid, False otherwise
        """
        required_fields = ["operation"]
        
        # Check required fields
        for field in required_fields:
            if field not in params:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Validate operation types
        valid_operations = ["get_market", "get_news", "get_stock", "augment_news", "augment_stock"]
        if params["operation"] not in valid_operations:
            self.logger.error(f"Invalid operation: {params['operation']}")
            return False
        
        # Validate augmentation parameters
        if params["operation"] in ["augment_news", "augment_stock"]:
            if "context" not in params:
                self.logger.error(f"Context required for {params['operation']}")
                return False
        
        return True

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute registry operations.
        
        Args:
            params: Operation parameters containing:
                - operation: Type of operation to perform
                - context: Context data for augmentation (optional)
                - query_limit: Limit number of queries returned (optional)
                
        Returns:
            Dictionary containing registry data and operation results
        """
        operation = params["operation"]
        context = params.get("context", {})
        query_limit = params.get("query_limit", None)
        
        if operation == "get_market":
            return self._get_market_queries(query_limit)
        elif operation == "get_news":
            return self._get_news_queries(query_limit)
        elif operation == "get_stock":
            return self._get_stock_queries(query_limit)
        elif operation == "augment_news":
            return self._augment_news_queries(context, query_limit)
        elif operation == "augment_stock":
            return self._augment_stock_queries(context, query_limit)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def format_output(self, raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """Format registry output.
        
        Args:
            raw_output: Raw registry output
            
        Returns:
            Formatted registry output
        """
        return {
            "operation": raw_output.get("operation", ""),
            "registry_type": raw_output.get("registry_type", ""),
            "query_count": raw_output.get("query_count", 0),
            "queries": raw_output.get("queries", []),
            "metadata": raw_output.get("metadata", {}),
            "timestamp": raw_output.get("timestamp", ""),
            "success": True
        }

    def _initialize_market_registry(self) -> List[Dict[str, str]]:
        """Initialize the market registry with 45+ comprehensive fixed queries.
        
        These queries are comprehensive and cover all aspects of market analysis.
        They are used directly without augmentation. No stone left unturned.
        
        Returns:
            List of market search queries
        """
        return [
            # Macroeconomic Indicators & Federal Reserve
            {"query": "Federal Reserve interest rate decision latest meeting minutes", "category": "monetary_policy"},
            {"query": "Federal Reserve balance sheet tapering quantitative easing", "category": "monetary_policy"},
            {"query": "Federal Reserve dot plot interest rate projections", "category": "monetary_policy"},
            {"query": "Federal Reserve inflation target 2% PCE core inflation", "category": "monetary_policy"},
            {"query": "Federal Reserve employment mandate maximum employment", "category": "monetary_policy"},
            {"query": "Federal Reserve forward guidance economic outlook", "category": "monetary_policy"},
            {"query": "Federal Reserve stress test bank capital requirements", "category": "monetary_policy"},
            
            # Inflation & Price Pressures
            {"query": "US inflation rate CPI data latest month over month", "category": "inflation"},
            {"query": "US core inflation excluding food energy PCE price index", "category": "inflation"},
            {"query": "US producer price index PPI wholesale inflation", "category": "inflation"},
            {"query": "US wage growth average hourly earnings inflation pressure", "category": "inflation"},
            {"query": "US shelter costs housing inflation rent prices", "category": "inflation"},
            {"query": "US energy prices gasoline oil inflation impact", "category": "inflation"},
            {"query": "US food prices grocery inflation supply chain", "category": "inflation"},
            
            # Economic Growth & GDP
            {"query": "US GDP growth rate quarterly report real GDP", "category": "gdp"},
            {"query": "US GDP components consumption investment government", "category": "gdp"},
            {"query": "US productivity growth labor productivity trends", "category": "gdp"},
            {"query": "US capacity utilization manufacturing capacity", "category": "gdp"},
            {"query": "US business investment capex spending trends", "category": "gdp"},
            {"query": "US consumer spending retail sales personal consumption", "category": "gdp"},
            
            # Employment & Labor Market
            {"query": "US unemployment rate jobs report nonfarm payrolls", "category": "employment"},
            {"query": "US job openings JOLTS quit rate labor market", "category": "employment"},
            {"query": "US labor force participation rate employment ratio", "category": "employment"},
            {"query": "US average hourly earnings wage growth inflation", "category": "employment"},
            {"query": "US initial jobless claims continuing claims", "category": "employment"},
            {"query": "US underemployment rate U6 unemployment", "category": "employment"},
            
            # Consumer & Business Sentiment
            {"query": "US consumer confidence index Conference Board", "category": "consumer_sentiment"},
            {"query": "US consumer sentiment University of Michigan", "category": "consumer_sentiment"},
            {"query": "US business confidence NFIB small business optimism", "category": "consumer_sentiment"},
            {"query": "US CEO confidence Business Roundtable survey", "category": "consumer_sentiment"},
            {"query": "US purchasing managers index PMI manufacturing services", "category": "consumer_sentiment"},
            
            # Manufacturing & Industrial Activity
            {"query": "US manufacturing PMI index ISM manufacturing", "category": "manufacturing"},
            {"query": "US industrial production manufacturing output", "category": "manufacturing"},
            {"query": "US factory orders durable goods orders", "category": "manufacturing"},
            {"query": "US capacity utilization manufacturing capacity", "category": "manufacturing"},
            {"query": "US new orders manufacturing backlog orders", "category": "manufacturing"},
            
            # Services & Consumer Activity
            {"query": "US services PMI index ISM services non-manufacturing", "category": "services"},
            {"query": "US retail sales data monthly consumer spending", "category": "services"},
            {"query": "US personal income personal consumption expenditures", "category": "services"},
            {"query": "US consumer credit outstanding debt levels", "category": "services"},
            {"query": "US restaurant performance index dining out", "category": "services"},
            
            # Housing Market & Real Estate
            {"query": "US housing market data home sales existing new", "category": "housing"},
            {"query": "US housing starts building permits construction", "category": "housing"},
            {"query": "US home prices Case Shiller index median prices", "category": "housing"},
            {"query": "US mortgage rates 30 year fixed rate trends", "category": "housing"},
            {"query": "US housing inventory months supply market", "category": "housing"},
            {"query": "US homebuilder confidence NAHB housing market index", "category": "housing"},
            
            # Trade & International
            {"query": "US trade balance import export data deficit", "category": "trade"},
            {"query": "US trade war China tariffs import duties", "category": "trade"},
            {"query": "US dollar strength DXY index currency impact", "category": "trade"},
            {"query": "US export growth manufacturing exports", "category": "trade"},
            {"query": "US import prices import inflation impact", "category": "trade"},
            
            # Global Economic Conditions (US-focused impact)
            {"query": "China economic growth GDP slowdown US impact", "category": "global_economy"},
            {"query": "Eurozone economic data ECB policy US markets", "category": "global_economy"},
            {"query": "UK economic data Bank of England Brexit impact", "category": "global_economy"},
            {"query": "emerging markets economic outlook US exports", "category": "global_economy"},
            {"query": "global supply chain disruptions US inflation", "category": "global_economy"},
            
            # Market Sentiment & Technical Analysis
            {"query": "S&P 500 technical analysis support resistance levels", "category": "technical_analysis"},
            {"query": "NASDAQ composite index technical levels chart patterns", "category": "technical_analysis"},
            {"query": "Dow Jones Industrial Average chart analysis trends", "category": "technical_analysis"},
            {"query": "Russell 2000 small cap index performance", "category": "technical_analysis"},
            {"query": "VIX volatility index fear greed gauge market sentiment", "category": "market_sentiment"},
            {"query": "market breadth advance decline ratio NYSE", "category": "market_sentiment"},
            {"query": "put call ratio options sentiment fear index", "category": "market_sentiment"},
            {"query": "AAII investor sentiment survey bullish bearish", "category": "market_sentiment"},
            {"query": "CNN fear greed index market sentiment", "category": "market_sentiment"},
            
            # Sector Performance & Rotation
            {"query": "sector performance technology vs financials rotation", "category": "sector_analysis"},
            {"query": "energy sector oil prices performance XLE ETF", "category": "sector_analysis"},
            {"query": "healthcare sector biotech performance XLV ETF", "category": "sector_analysis"},
            {"query": "real estate sector REIT performance XLRE ETF", "category": "sector_analysis"},
            {"query": "consumer discretionary vs staples performance XLY XLP", "category": "sector_analysis"},
            {"query": "industrial sector manufacturing performance XLI ETF", "category": "sector_analysis"},
            {"query": "materials sector commodity prices performance XLB ETF", "category": "sector_analysis"},
            {"query": "utilities sector defensive performance XLU ETF", "category": "sector_analysis"},
            {"query": "communication services sector performance XLC ETF", "category": "sector_analysis"},
            
            # Commodities & Natural Resources
            {"query": "gold price analysis dollar correlation safe haven", "category": "commodities"},
            {"query": "silver price analysis industrial demand", "category": "commodities"},
            {"query": "oil price WTI Brent crude analysis energy demand", "category": "commodities"},
            {"query": "natural gas prices energy market analysis", "category": "commodities"},
            {"query": "copper price analysis industrial demand indicator", "category": "commodities"},
            {"query": "lithium prices electric vehicle battery demand", "category": "commodities"},
            {"query": "rare earth metals supply chain China dominance", "category": "commodities"},
            
            # Currencies & Forex
            {"query": "US dollar index DXY forex analysis strength", "category": "currencies"},
            {"query": "euro USD exchange rate analysis ECB policy", "category": "currencies"},
            {"query": "British pound USD exchange rate Brexit impact", "category": "currencies"},
            {"query": "Chinese yuan USD exchange rate trade war", "category": "currencies"},
            {"query": "Japanese yen USD exchange rate carry trade", "category": "currencies"},
            {"query": "Swiss franc USD exchange rate safe haven", "category": "currencies"},
            
            # Bond Market & Fixed Income
            {"query": "US Treasury yield curve analysis 2s10s spread", "category": "bonds"},
            {"query": "US Treasury yields 10 year 30 year rates", "category": "bonds"},
            {"query": "corporate bond spreads credit risk BBB investment grade", "category": "bonds"},
            {"query": "high yield bond market performance junk bonds", "category": "bonds"},
            {"query": "municipal bond market analysis tax exempt", "category": "bonds"},
            {"query": "TIPS Treasury inflation protected securities", "category": "bonds"},
            {"query": "bond market liquidity trading volume", "category": "bonds"},
            
            # Political & Regulatory Impact
            {"query": "US election impact markets presidential cycle", "category": "political"},
            {"query": "Congress fiscal policy spending debt ceiling", "category": "political"},
            {"query": "SEC regulations market structure changes", "category": "political"},
            {"query": "CFTC regulations derivatives trading rules", "category": "political"},
            {"query": "tax policy changes corporate tax rates", "category": "political"},
            {"query": "infrastructure spending bill market impact", "category": "political"},
            
            # Geopolitical & International Relations
            {"query": "US China relations trade war technology ban", "category": "geopolitical"},
            {"query": "Russia Ukraine conflict energy market impact", "category": "geopolitical"},
            {"query": "Middle East tensions oil supply disruption", "category": "geopolitical"},
            {"query": "Taiwan China tensions semiconductor supply", "category": "geopolitical"},
            {"query": "North Korea nuclear threat Asian markets", "category": "geopolitical"},
            
            # Technology & Innovation Trends
            {"query": "artificial intelligence AI market impact stocks", "category": "technology"},
            {"query": "quantum computing development market applications", "category": "technology"},
            {"query": "blockchain cryptocurrency regulation market", "category": "technology"},
            {"query": "5G network deployment telecom infrastructure", "category": "technology"},
            {"query": "electric vehicle market growth battery technology", "category": "technology"},
            {"query": "renewable energy solar wind market growth", "category": "technology"},
            {"query": "space exploration commercial space market", "category": "technology"},
            
            # Climate & ESG Factors
            {"query": "climate change impact business operations", "category": "climate_esg"},
            {"query": "ESG investing environmental social governance", "category": "climate_esg"},
            {"query": "carbon pricing carbon tax market impact", "category": "climate_esg"},
            {"query": "sustainable investing green bonds market", "category": "climate_esg"},
            {"query": "climate risk disclosure SEC requirements", "category": "climate_esg"}
        ]

    def _initialize_news_registry(self) -> List[Dict[str, str]]:
        """Initialize the news registry with 40+ general news queries.
        
        These queries are designed to surface companies and events naturally
        through general news searches. They will be augmented by the News Query 
        Generator Agent based on market context to find the top 20-30 companies.
        
        Returns:
            List of news search query templates
        """
        return [
            # Earnings & Financial Performance
            {"query": "earnings season Q4 2024 results beat miss", "category": "earnings"},
            {"query": "revenue growth top performers S&P 500 companies", "category": "earnings"},
            {"query": "profit margins expansion contraction corporate earnings", "category": "earnings"},
            {"query": "guidance outlook corporate earnings forecasts", "category": "earnings"},
            {"query": "analyst estimates consensus earnings revisions", "category": "analyst_ratings"},
            {"query": "earnings surprise positive negative corporate results", "category": "earnings"},
            {"query": "forward guidance corporate outlook statements", "category": "earnings"},
            
            # Merger & Acquisition Activity
            {"query": "merger acquisition deals 2024 corporate consolidation", "category": "m_a"},
            {"query": "takeover bids hostile acquisitions corporate battles", "category": "m_a"},
            {"query": "deal value billion dollar acquisitions 2024", "category": "m_a"},
            {"query": "regulatory approval merger deals antitrust concerns", "category": "m_a"},
            {"query": "synergies cost savings post merger integration", "category": "m_a"},
            {"query": "private equity buyouts corporate takeovers", "category": "m_a"},
            {"query": "cross border acquisitions international deals", "category": "m_a"},
            
            # Regulatory & Legal News
            {"query": "SEC investigation corporate fraud accounting issues", "category": "regulatory"},
            {"query": "FDA approval new drugs medical devices breakthrough", "category": "regulatory"},
            {"query": "antitrust lawsuit monopoly competition concerns", "category": "regulatory"},
            {"query": "compliance violation corporate governance issues", "category": "regulatory"},
            {"query": "government contract defense aerospace contracts", "category": "regulatory"},
            {"query": "regulatory changes impact business operations", "category": "regulatory"},
            {"query": "legal settlements corporate litigation outcomes", "category": "regulatory"},
            
            # Market Moving Events
            {"query": "stock split announcements corporate actions", "category": "corporate_actions"},
            {"query": "dividend increase dividend cuts corporate payouts", "category": "corporate_actions"},
            {"query": "share buyback programs corporate repurchases", "category": "corporate_actions"},
            {"query": "insider trading corporate executives stock sales", "category": "insider_activity"},
            {"query": "institutional ownership hedge fund positions", "category": "ownership"},
            {"query": "activist investor campaigns corporate changes", "category": "ownership"},
            {"query": "short interest high short squeeze candidates", "category": "ownership"},
            
            # Technology & Innovation News
            {"query": "artificial intelligence AI breakthrough companies", "category": "technology"},
            {"query": "quantum computing development commercial applications", "category": "technology"},
            {"query": "blockchain cryptocurrency regulation market impact", "category": "technology"},
            {"query": "5G network deployment telecom infrastructure", "category": "technology"},
            {"query": "electric vehicle market growth battery technology", "category": "technology"},
            {"query": "renewable energy solar wind market growth", "category": "technology"},
            {"query": "space exploration commercial space market", "category": "technology"},
            {"query": "semiconductor shortage supply chain disruption", "category": "technology"},
            {"query": "cybersecurity breach corporate data security", "category": "technology"},
            {"query": "cloud computing market share AWS Azure Google", "category": "technology"},
            
            # Industry Trends & Disruption
            {"query": "technology disruption traditional industries", "category": "industry_trends"},
            {"query": "market share shifts industry consolidation", "category": "industry_trends"},
            {"query": "innovation breakthrough disruptive technologies", "category": "industry_trends"},
            {"query": "supply chain disruption global logistics", "category": "operations"},
            {"query": "cost inflation input prices corporate margins", "category": "operations"},
            {"query": "labor shortage workforce challenges companies", "category": "operations"},
            {"query": "digital transformation corporate technology adoption", "category": "industry_trends"},
            {"query": "ESG sustainability corporate responsibility", "category": "industry_trends"},
            
            # Healthcare & Biotech
            {"query": "biotech breakthrough drug development pipeline", "category": "healthcare"},
            {"query": "FDA drug approval process clinical trials", "category": "healthcare"},
            {"query": "healthcare innovation telemedicine digital health", "category": "healthcare"},
            {"query": "pharmaceutical mergers acquisitions consolidation", "category": "healthcare"},
            {"query": "medical device innovation FDA approval", "category": "healthcare"},
            {"query": "healthcare costs insurance market changes", "category": "healthcare"},
            
            # Energy & Commodities
            {"query": "oil price volatility energy market trends", "category": "energy"},
            {"query": "renewable energy transition fossil fuel decline", "category": "energy"},
            {"query": "lithium battery demand electric vehicle growth", "category": "energy"},
            {"query": "natural gas prices energy market analysis", "category": "energy"},
            {"query": "rare earth metals supply chain critical minerals", "category": "energy"},
            {"query": "nuclear energy development small modular reactors", "category": "energy"},
            
            # Financial Services & Banking
            {"query": "bank earnings interest rate impact net interest margin", "category": "financial"},
            {"query": "fintech disruption traditional banking services", "category": "financial"},
            {"query": "credit card spending consumer debt levels", "category": "financial"},
            {"query": "mortgage rates housing market impact", "category": "financial"},
            {"query": "investment banking deal flow M&A advisory", "category": "financial"},
            {"query": "insurance market climate risk pricing", "category": "financial"},
            
            # Consumer & Retail
            {"query": "retail sales data consumer spending trends", "category": "consumer"},
            {"query": "e-commerce growth online shopping market share", "category": "consumer"},
            {"query": "restaurant performance dining out recovery", "category": "consumer"},
            {"query": "luxury goods demand high end consumer spending", "category": "consumer"},
            {"query": "fast food restaurant chains performance", "category": "consumer"},
            {"query": "apparel retail fashion industry trends", "category": "consumer"},
            
            # Global Market Impact
            {"query": "international expansion US companies global markets", "category": "global_operations"},
            {"query": "currency impact multinational corporate earnings", "category": "global_operations"},
            {"query": "trade war impact tariffs corporate supply chains", "category": "global_operations"},
            {"query": "geopolitical risk corporate operations regions", "category": "global_operations"},
            {"query": "emerging market growth US company expansion", "category": "global_operations"},
            {"query": "China market access US companies restrictions", "category": "global_operations"},
            
            # Market Sentiment & Analyst Activity
            {"query": "analyst upgrades downgrades stock recommendations", "category": "analyst_ratings"},
            {"query": "price target changes analyst forecasts", "category": "analyst_ratings"},
            {"query": "institutional investor moves hedge fund positions", "category": "analyst_ratings"},
            {"query": "retail investor sentiment meme stock movement", "category": "analyst_ratings"},
            {"query": "options flow unusual options activity stocks", "category": "analyst_ratings"},
            {"query": "short squeeze candidates high short interest", "category": "analyst_ratings"}
        ]

    def _initialize_stock_registry(self) -> List[Dict[str, str]]:
        """Initialize the stock registry with 50-70 placeholder queries.
        
        These queries serve as comprehensive guidelines for stock analysis.
        They will be extensively augmented by the Stock Query Generator Agent
        based on market and news context, potentially generating 10+ queries per stock.
        
        Returns:
            List of stock search query templates
        """
        return [
            # Fundamental Analysis
            {"query": "P/E ratio {company} {sector} comparison", "category": "valuation"},
            {"query": "price to book ratio {company} {industry}", "category": "valuation"},
            {"query": "EV/EBITDA {company} {peer_group}", "category": "valuation"},
            {"query": "dividend yield {company} {sector}", "category": "valuation"},
            {"query": "free cash flow {company} {timeframe}", "category": "cash_flow"},
            {"query": "debt to equity ratio {company} {industry}", "category": "financial_health"},
            {"query": "current ratio {company} {sector}", "category": "financial_health"},
            {"query": "return on equity {company} {peer_comparison}", "category": "profitability"},
            {"query": "return on assets {company} {industry}", "category": "profitability"},
            {"query": "gross margin {company} {trend_analysis}", "category": "profitability"},
            
            # Growth Metrics
            {"query": "revenue growth rate {company} {period}", "category": "growth"},
            {"query": "earnings growth {company} {forecast}", "category": "growth"},
            {"query": "market share growth {company} {competitor}", "category": "growth"},
            {"query": "customer acquisition {company} {metric}", "category": "growth"},
            {"query": "geographic expansion {company} {region}", "category": "growth"},
            {"query": "product pipeline {company} {development_stage}", "category": "growth"},
            {"query": "R&D investment {company} {percentage_revenue}", "category": "growth"},
            {"query": "capital expenditure {company} {project_type}", "category": "growth"},
            {"query": "acquisition strategy {company} {target_criteria}", "category": "growth"},
            {"query": "partnership deals {company} {partner}", "category": "growth"},
            
            # Technical Analysis
            {"query": "moving averages {company} {timeframe}", "category": "technical"},
            {"query": "support resistance levels {company} {chart_pattern}", "category": "technical"},
            {"query": "volume analysis {company} {trend}", "category": "technical"},
            {"query": "relative strength {company} {index_comparison}", "category": "technical"},
            {"query": "momentum indicators {company} {rsi_macd}", "category": "technical"},
            {"query": "breakout patterns {company} {pattern_type}", "category": "technical"},
            {"query": "fibonacci retracement {company} {swing_points}", "category": "technical"},
            {"query": "option flow {company} {strike_price}", "category": "technical"},
            {"query": "short interest {company} {days_to_cover}", "category": "technical"},
            {"query": "institutional buying {company} {fund_type}", "category": "technical"},
            
            # Risk Assessment
            {"query": "beta coefficient {company} {market_volatility}", "category": "risk"},
            {"query": "volatility analysis {company} {timeframe}", "category": "risk"},
            {"query": "correlation analysis {company} {market_index}", "category": "risk"},
            {"query": "liquidity risk {company} {bid_ask_spread}", "category": "risk"},
            {"query": "credit rating {company} {agency}", "category": "risk"},
            {"query": "default risk {company} {bond_analysis}", "category": "risk"},
            {"query": "regulatory risk {company} {pending_issues}", "category": "risk"},
            {"query": "litigation risk {company} {pending_cases}", "category": "risk"},
            {"query": "environmental risk {company} {compliance_issues}", "category": "risk"},
            {"query": "cybersecurity risk {company} {breach_history}", "category": "risk"},
            
            # Industry & Competitive Analysis
            {"query": "competitive advantage {company} {moat_type}", "category": "competitive"},
            {"query": "market positioning {company} {target_demographic}", "category": "competitive"},
            {"query": "pricing power {company} {industry_dynamics}", "category": "competitive"},
            {"query": "supplier relationships {company} {dependency_analysis}", "category": "competitive"},
            {"query": "customer concentration {company} {top_customers}", "category": "competitive"},
            {"query": "barriers to entry {company} {industry}", "category": "competitive"},
            {"query": "disruption potential {company} {threat_source}", "category": "competitive"},
            {"query": "innovation pipeline {company} {patent_analysis}", "category": "competitive"},
            {"query": "brand value {company} {recognition_metrics}", "category": "competitive"},
            {"query": "intellectual property {company} {patent_portfolio}", "category": "competitive"},
            
            # Management & Governance
            {"query": "executive compensation {company} {peer_comparison}", "category": "governance"},
            {"query": "board composition {company} {independence_ratio}", "category": "governance"},
            {"query": "shareholder activism {company} {activist_funds}", "category": "governance"},
            {"query": "ESG performance {company} {rating_agency}", "category": "governance"},
            {"query": "executive track record {company} {ceo_history}", "category": "governance"},
            {"query": "succession planning {company} {leadership_pipeline}", "category": "governance"},
            {"query": "corporate culture {company} {employee_satisfaction}", "category": "governance"},
            {"query": "diversity metrics {company} {representation_data}", "category": "governance"},
            {"query": "transparency score {company} {disclosure_quality}", "category": "governance"},
            {"query": "stakeholder relations {company} {community_impact}", "category": "governance"}
        ]

    def _get_market_queries(self, query_limit: Optional[int] = None) -> Dict[str, Any]:
        """Get market queries (fixed, no augmentation needed).
        
        Args:
            query_limit: Optional limit on number of queries returned
            
        Returns:
            Dictionary containing market queries
        """
        queries = self.market_registry
        if query_limit:
            queries = queries[:query_limit]
        
        return {
            "operation": "get_market",
            "registry_type": "market",
            "query_count": len(queries),
            "queries": queries,
            "metadata": {
                "description": "Fixed market analysis queries - used directly with Serper",
                "augmentation_required": False,
                "total_available": len(self.market_registry)
            },
            "timestamp": datetime.now().isoformat()
        }

    def _get_news_queries(self, query_limit: Optional[int] = None) -> Dict[str, Any]:
        """Get news queries (placeholders for augmentation).
        
        Args:
            query_limit: Optional limit on number of queries returned
            
        Returns:
            Dictionary containing news query templates
        """
        queries = self.news_registry
        if query_limit:
            queries = queries[:query_limit]
        
        return {
            "operation": "get_news",
            "registry_type": "news",
            "query_count": len(queries),
            "queries": queries,
            "metadata": {
                "description": "News query templates - require augmentation by News Query Generator Agent",
                "augmentation_required": True,
                "total_available": len(self.news_registry)
            },
            "timestamp": datetime.now().isoformat()
        }

    def _get_stock_queries(self, query_limit: Optional[int] = None) -> Dict[str, Any]:
        """Get stock queries (placeholders for extensive augmentation).
        
        Args:
            query_limit: Optional limit on number of queries returned
            
        Returns:
            Dictionary containing stock query templates
        """
        queries = self.stock_registry
        if query_limit:
            queries = queries[:query_limit]
        
        return {
            "operation": "get_stock",
            "registry_type": "stock",
            "query_count": len(queries),
            "queries": queries,
            "metadata": {
                "description": "Stock query templates - require extensive augmentation by Stock Query Generator Agent",
                "augmentation_required": True,
                "total_available": len(self.stock_registry),
                "expected_augmented_count": "50-200+ queries depending on context"
            },
            "timestamp": datetime.now().isoformat()
        }

    def _augment_news_queries(self, context: Dict[str, Any], query_limit: Optional[int] = None) -> Dict[str, Any]:
        """Augment news queries based on market context.
        
        This simulates what the News Query Generator Agent will do.
        In practice, this will be handled by the agent with LLM augmentation.
        
        Args:
            context: Market analysis context
            query_limit: Optional limit on number of queries returned
            
        Returns:
            Dictionary containing augmented news queries
        """
        # This is a placeholder - actual augmentation will be done by the News Query Generator Agent
        base_queries = self.news_registry
        
        # Simulate some basic augmentation based on context
        augmented_queries = []
        for query in base_queries:
            # Add context-specific variations
            if "market_sentiment" in context:
                augmented_queries.append({
                    "query": f"{query['query']} {context['market_sentiment']}",
                    "category": query['category'],
                    "augmentation_type": "market_sentiment"
                })
            
            augmented_queries.append(query)
        
        if query_limit:
            augmented_queries = augmented_queries[:query_limit]
        
        return {
            "operation": "augment_news",
            "registry_type": "news_augmented",
            "query_count": len(augmented_queries),
            "queries": augmented_queries,
            "metadata": {
                "description": "Augmented news queries based on market context",
                "augmentation_required": False,
                "context_used": list(context.keys()),
                "total_available": len(augmented_queries)
            },
            "timestamp": datetime.now().isoformat()
        }

    def _augment_stock_queries(self, context: Dict[str, Any], query_limit: Optional[int] = None) -> Dict[str, Any]:
        """Augment stock queries based on market and news context.
        
        This simulates what the Stock Query Generator Agent will do.
        In practice, this will be handled by the agent with extensive LLM augmentation.
        
        Args:
            context: Market and news analysis context
            query_limit: Optional limit on number of queries returned
            
        Returns:
            Dictionary containing extensively augmented stock queries
        """
        # This is a placeholder - actual augmentation will be done by the Stock Query Generator Agent
        base_queries = self.stock_registry
        
        # Simulate extensive augmentation based on context
        augmented_queries = []
        
        # Add context-specific stock queries
        if "mentioned_stocks" in context:
            for stock in context["mentioned_stocks"][:5]:  # Limit to 5 stocks for demo
                for query in base_queries[:10]:  # Use first 10 base queries for each stock
                    augmented_queries.append({
                        "query": query["query"].replace("{company}", stock),
                        "category": query["category"],
                        "augmentation_type": "stock_specific",
                        "target_stock": stock
                    })
        
        # Add base queries
        augmented_queries.extend(base_queries)
        
        if query_limit:
            augmented_queries = augmented_queries[:query_limit]
        
        return {
            "operation": "augment_stock",
            "registry_type": "stock_augmented",
            "query_count": len(augmented_queries),
            "queries": augmented_queries,
            "metadata": {
                "description": "Extensively augmented stock queries based on market and news context",
                "augmentation_required": False,
                "context_used": list(context.keys()),
                "total_available": len(augmented_queries),
                "note": "In practice, this will generate 50-200+ queries with extensive LLM augmentation"
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_capabilities(self) -> List[str]:
        """Get a list of capabilities this tool provides.
        
        Returns:
            List of capability strings
        """
        return [
            "market_query_management",
            "news_query_management", 
            "stock_query_management",
            "query_augmentation",
            "context_aware_search"
        ]

    def get_required_params(self) -> List[str]:
        """Get a list of required parameters for this tool.
        
        Returns:
            List of required parameter names
        """
        return ["operation"]

    def get_optional_params(self) -> List[str]:
        """Get a list of optional parameters for this tool.
        
        Returns:
            List of optional parameter names
        """
        return [
            "context",
            "query_limit"
        ]

    def get_example_usage(self) -> Dict[str, Any]:
        """Get an example of how to use this tool.
        
        Returns:
            Dictionary with example parameters and expected output
        """
        return {
            "description": "Manage and augment search queries for market, news, and stock analysis",
            "params": {
                "operation": "get_market",
                "query_limit": 10
            },
            "expected_output": {
                "operation": "get_market",
                "registry_type": "market",
                "query_count": 10,
                "queries": "List of market search queries",
                "success": True
            }
        }
