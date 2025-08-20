# Morning Stock Screener - Implementation Plan

## 🎯 **Project Vision**
Build the ultimate AI-powered stock screener that leaves no stone unturned, delivering top 10 stock recommendations daily at 9:30 AM BST with comprehensive market analysis, news synthesis, and detailed stock research.

## 🏗️ **System Architecture**

### **Multi-Agent Workflow (8 Agents)**
```
Orchestrator Agent
├── Stage 1: Market Analysis
│   ├── Google Serper Market Tool
│   ├── Market Search Registry (30+ searches)
│   └── Market Analysis Agent
├── Stage 2: News Analysis
│   ├── News Query Generator (context-aware)
│   ├── News Search Registry
│   └── News Analysis Agent
├── Stage 3: Stock Analysis
│   ├── Stock Query Generator (context-aware)
│   ├── Stock Search Registry
│   └── Stock Analysis Agent
└── Stage 4: Ranking + Synthesis
    ├── Ranker Agent
    ├── Synthesis Agent
    └── Final 4-Segment Report
```

### **Key Design Principles**
- **True Separation of Concerns** - 8 distinct agents, each with specific responsibilities
- **Stateless Design** - All agents are stateless, receiving context as input
- **Progressive Context Building** - Each stage enhances the next with accumulated intelligence
- **No Stone Unturned** - 30+ market searches, comprehensive coverage
- **Iterative Improvement** - Raw outputs saved to tmp/ for analysis and refinement
- **Test-Driven Development** - Each component tested in isolation before integration
- **Trackable Progress** - Each agent stage can be monitored and improved independently

## 📁 **Project Structure**

```
src/
├── agents/           # Agent implementations (8 agents)
│   ├── __init__.py
│   ├── base.py      # Base agent class
│   ├── orchestrator.py
│   ├── market_analysis.py
│   ├── news_query_generator.py
│   ├── news_analysis.py
│   ├── stock_query_generator.py
│   ├── stock_analysis.py
│   ├── ranker.py
│   └── synthesis.py
├── models/           # Data models (separated by agent)
│   ├── __init__.py
│   ├── market_agent.py
│   ├── news_agent.py
│   ├── stock_agent.py
│   ├── ranking_agent.py
│   └── synthesis_agent.py
├── tools/            # Tool implementations
│   ├── __init__.py
│   ├── base.py      # Base tool class
│   ├── google_serper.py
│   ├── market_registry.py
│   ├── news_registry.py
│   └── stock_registry.py
├── prompts/          # Agent system prompts (Python scripts with constants)
│   ├── __init__.py
│   ├── market_analysis.py
│   ├── news_query_generation.py
│   ├── news_analysis.py
│   ├── stock_query_generation.py
│   ├── stock_analysis.py
│   ├── ranking.py
│   └── synthesis.py
├── utils/            # Helper functions (separated by agent)
│   ├── __init__.py
│   ├── market_utils.py
│   ├── news_utils.py
│   ├── stock_utils.py
│   ├── ranking_utils.py
│   └── synthesis_utils.py
├── workflows/        # Workflow orchestration
│   ├── __init__.py
│   └── main_workflow.py
├── testing/          # Test chat interface
│   ├── __init__.py
│   └── chat_client.py
└── tmp/              # Raw outputs for analysis (git-ignored)
    ├── market_outputs/
    ├── news_outputs/
    ├── stock_outputs/
    └── final_outputs/
```

## 🔄 **Iterative Improvement Process**

### **Raw Output Tracking**
- **Market Stage**: Raw outputs saved to `tmp/market_outputs/` for analysis
- **News Stage**: Raw outputs saved to `tmp/news_outputs/` for analysis  
- **Stock Stage**: Raw outputs saved to `tmp/stock_outputs/` for analysis
- **Final Stage**: Complete reports saved to `tmp/final_outputs/` for analysis

### **Continuous Refinement**
- Each agent stage can be monitored independently
- Weak links identified through output analysis
- Prompts and search strategies refined based on real results
- LLM theory supports: separation leads to better, more focused answers

### **4-Segment Final Report Structure**
1. **Market Summary** - Macroeconomic overview and trends
2. **News Summary** - Key financial news and market-moving events
3. **Stock Rankings** - Top 10 stocks with detailed analysis
4. **Overall Summary** - Executive summary and key insights

## 🚀 **Implementation Phases**

### **Phase 1: Foundation & Testing Infrastructure**
**Goal**: Establish the testing framework and move current main.py to testing folder

#### **Step 1.1: Reorganize Testing Structure**
- [ ] Move `src/main.py` to `src/testing/chat_client.py`
- [ ] Create `src/testing/__init__.py`
- [ ] Update imports and test paths
- [ ] Verify chat interface still works
- [ ] **Test**: Run chat client, verify LLM wrapper functionality

#### **Step 1.2: Create Base Agent Framework**
- [ ] Create `src/agents/base.py` with abstract base agent class
- [ ] Define common agent interface (execute, validate_input, process_output)
- [ ] **Test**: Unit tests for base agent class

#### **Step 1.3: Create Base Tool Framework**
- [ ] Create `src/tools/base.py` with abstract base tool class
- [ ] Define common tool interface (execute, validate_params, format_output)
- [ ] **Test**: Unit tests for base tool class

### **Phase 2: Core Tools Implementation**
**Goal**: Build the foundational tools that agents will use

#### **Step 2.1: Google Serper Tool**
- [ ] Create `src/tools/google_serper.py`
- [ ] Implement search functionality with Serper API
- [ ] Add error handling and rate limiting
- [ ] **Test**: Unit tests with mocked API responses
- [ ] **Integration Test**: Real API calls (with test queries)

#### **Step 2.2: Search Registry System**
- [ ] Create `src/tools/registry.py`
- [ ] Implement search query management (add, remove, categorize)
- [ ] Support for context-aware query augmentation
- [ ] **Test**: Unit tests for registry operations

### **Phase 3: Agent Implementation (Sequential)**
**Goal**: Build each agent one by one, testing thoroughly before moving to the next

#### **Step 3.1: Market Analysis Agent**
- [ ] Create `src/agents/market_analysis.py`
- [ ] Implement market context gathering using Market data models
- [ ] Use Google Serper tool with market search registry (30+ searches)
- [ ] Generate comprehensive market analysis report
- [ ] Save raw output to `tmp/market_outputs/`
- [ ] **Test**: Unit tests with mocked search results
- [ ] **Integration Test**: Real market analysis workflow

#### **Step 3.2: News Query Generator Agent**
- [ ] Create `src/agents/news_query_generator.py`
- [ ] Implement context-aware news query augmentation
- [ ] Take market analysis and enhance news search registry
- [ ] Generate targeted news search queries
- [ ] **Test**: Unit tests with sample market context
- [ ] **Integration Test**: News query generation with real market analysis

#### **Step 3.3: News Analysis Agent**
- [ ] Create `src/agents/news_analysis.py`
- [ ] Implement news gathering and analysis using News data models
- [ ] Use enhanced search queries from news query generator
- [ ] Generate comprehensive news analysis report
- [ ] Save raw output to `tmp/news_outputs/`
- [ ] **Test**: Unit tests with mocked news data
- [ ] **Integration Test**: News analysis with real search results

#### **Step 3.4: Stock Query Generator Agent**
- [ ] Create `src/agents/stock_query_generator.py`
- [ ] Implement context-aware stock query augmentation
- [ ] Take market + news analysis and enhance stock search registry
- [ ] Generate targeted stock search queries
- [ ] **Test**: Unit tests with sample market + news context
- [ ] **Integration Test**: Stock query generation with real context

#### **Step 3.5: Stock Analysis Agent**
- [ ] Create `src/agents/stock_analysis.py`
- [ ] Implement stock research using Stock data models
- [ ] Use enhanced search queries from stock query generator
- [ ] Generate comprehensive stock analysis report
- [ ] Save raw output to `tmp/stock_outputs/`
- [ ] **Test**: Unit tests with mocked stock data
- [ ] **Integration Test**: Stock analysis with real search results

#### **Step 3.6: Ranker Agent**
- [ ] Create `src/agents/ranker.py`
- [ ] Implement stock ranking algorithm considering all factors
- [ ] Support for additional searches if needed for clarification
- [ ] Generate top 10 ranked list
- [ ] **Test**: Unit tests with sample analysis data
- [ ] **Integration Test**: Ranking with real analysis results

#### **Step 3.7: Synthesis Agent**
- [ ] Create `src/agents/synthesis.py`
- [ ] Implement final 4-segment report generation:
  - Market Summary
  - News Summary  
  - Stock Rankings
  - Overall Summary
- [ ] Combine all agent outputs into cohesive report
- [ ] Save final output to `tmp/final_outputs/`
- [ ] **Test**: Unit tests with sample synthesis data
- [ ] **Integration Test**: Report generation with real data

### **Phase 4: Orchestration & Workflow**
**Goal**: Connect all agents into a cohesive workflow

#### **Step 4.1: Orchestrator Agent**
- [ ] Create `src/agents/orchestrator.py`
- [ ] Implement workflow coordination logic
- [ ] Manage data flow between agents
- [ ] Handle errors and retries
- [ ] **Test**: Unit tests for workflow logic
- [ ] **Integration Test**: Full workflow execution

#### **Step 4.2: Main Workflow**
- [ ] Create `src/workflows/main_workflow.py`
- [ ] Implement the complete 3-stage workflow
- [ ] Add logging and monitoring
- [ ] **Test**: Integration tests for complete workflow
- [ ] **End-to-End Test**: Full system execution

### **Phase 5: Prompt Engineering & Optimization**
**Goal**: Refine system prompts and search strategies

#### **Step 5.1: Prompt Development**
- [ ] Create all prompt Python scripts in `src/prompts/`
- [ ] Define system prompt constants (e.g., `MARKET_SYSTEM_PROMPT = """..."""`)
- [ ] Develop system prompts for each agent
- [ ] Test prompts with sample inputs
- [ ] **Test**: Prompt effectiveness with real LLM calls

#### **Step 5.2: Search Strategy Optimization**
- [ ] Refine search registries based on testing results
- [ ] Optimize query augmentation strategies
- [ ] **Test**: Search result quality and coverage

### **Phase 6: Production Readiness**
**Goal**: Prepare for production deployment

#### **Step 6.1: Error Handling & Resilience**
- [ ] Add comprehensive error handling
- [ ] Implement retry mechanisms
- [ ] Add circuit breakers for external APIs
- [ ] **Test**: Error scenarios and recovery

#### **Step 6.2: Performance Optimization**
- [ ] Optimize search strategies
- [ ] Implement caching where appropriate
- [ ] **Test**: Performance benchmarks

#### **Step 6.3: Monitoring & Logging**
- [ ] Add comprehensive logging
- [ ] Implement metrics collection
- [ ] **Test**: Logging and monitoring functionality

## 🧪 **Testing Strategy**

### **Unit Tests**
- Each agent tested in isolation with mocked dependencies
- Each tool tested with mocked external APIs
- All data models validated thoroughly

### **Integration Tests**
- Agent-to-agent communication tested
- Tool integration verified
- Data flow between stages validated

### **End-to-End Tests**
- Complete workflow execution tested
- Real API calls (with test data)
- Full system validation

## 📊 **Success Metrics**

### **Quality Metrics**
- **Recall**: No important opportunities missed
- **Precision**: High-quality recommendations
- **Consistency**: Reliable daily output
- **Speed**: Complete analysis within time constraints

### **Technical Metrics**
- **Test Coverage**: >90% for all new code
- **Performance**: Analysis completes within 30 minutes
- **Reliability**: 99%+ uptime for daily runs
- **Maintainability**: Clean, documented, testable code

## 🚨 **Risk Mitigation**

### **Technical Risks**
- **API Rate Limits**: Implement proper rate limiting and retry logic
- **LLM Response Quality**: Extensive prompt testing and validation
- **Data Consistency**: Robust validation and error handling

### **Business Risks**
- **Market Coverage**: Comprehensive search strategies
- **Timing**: Ensure daily delivery by 9:30 AM BST
- **Quality**: Continuous testing and refinement

## 📅 **Timeline Estimate**

- **Phase 1**: 1-2 days (Foundation)
- **Phase 2**: 2-3 days (Core Tools)
- **Phase 3**: 5-7 days (Agent Implementation)
- **Phase 4**: 2-3 days (Orchestration)
- **Phase 5**: 2-3 days (Optimization)
- **Phase 6**: 2-3 days (Production Readiness)

**Total Estimated Time**: 14-21 days

## 🔄 **Refined Workflow Flow**

```
Market Agent → News Query Generator → News Agent → Stock Query Generator → Stock Agent → Ranking Agent → Synthesis Agent
     ↓              ↓                    ↓              ↓                    ↓            ↓            ↓
Market Analysis → Enhanced News → News Analysis → Enhanced Stock → Stock Analysis → Top 10 → 4-Segment Report
                Queries                Queries                Rankings
```

### **Stage Progression**
1. **Market Stage**: 30+ comprehensive market searches → Market analysis report
2. **News Stage**: Market context → Enhanced news queries → News analysis report  
3. **Stock Stage**: Market + News context → Enhanced stock queries → Stock analysis report
4. **Final Stage**: All context → Ranking → Synthesis → Final 4-segment report

## 🎯 **Next Immediate Steps**

1. **Review this updated plan** - Ensure it captures your refined vision correctly
2. **Approve Phase 1** - Begin with foundation and testing infrastructure
3. **Start Step 1.1** - Move main.py to testing folder and verify functionality

This plan ensures we build systematically, test thoroughly, and create a robust foundation for the ultimate stock screener. Each phase builds on the previous one, allowing us to validate our approach before moving forward.
