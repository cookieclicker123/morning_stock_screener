# 🤖 Morning Stock Screener

An AI-powered morning stock screener system that delivers comprehensive market analysis by 9:30 AM BST daily. Built with Python, GPT-5, and a custom multi-agent framework using Google Serper for data collection.

## 🎯 **Project Status: Phase 2 Complete - Ready for Phase 3**

### ✅ **Completed Components:**
- **GPT-5 Integration**: Working independently with content filtering resolved
- **Google Serper Tool**: Comprehensive website coverage (100+ financial sources)
- **Data Models**: Pydantic v2 models for stocks, markets, emails, and LLM requests
- **Base Architecture**: BaseAgent and BaseTool classes with comprehensive testing
- **Search Registry**: 118+ market queries, 82+ news queries, 60+ stock queries
- **Intelligent Website Filtering**: Dynamic query-to-website mapping
- **Staggered Search**: Comprehensive coverage without API limits

### 🚀 **Next Phase: Phase 3 - Agent Implementation**
- Market Analysis Agent
- News Query Generator Agent  
- News Analysis Agent
- Stock Query Generator Agent
- Stock Analysis Agent
- Ranker Agent
- Synthesis Agent
- Orchestrator Agent

## 🏗️ **Architecture Overview**

The system uses an 8-agent, 4-stage workflow:

1. **Stage 1: Market Analysis** - Orchestrator uses Google Serper with Market Search Registry (118+ queries)
2. **Stage 2: News Analysis** - Market output feeds News Query Generator, then News Analysis Agent
3. **Stage 3: Stock Analysis** - Market and News outputs feed Stock Query Generator, then Stock Analysis Agent
4. **Stage 4: Ranking + Synthesis** - Ranker Agent → Synthesis Agent → Final 4-segment report

## 🛠️ **Technology Stack**

- **Python 3.11+** with async/await support
- **GPT-5** via OpenAI API for AI analysis
- **Google Serper API** for comprehensive web search
- **Pydantic v2** for robust data validation
- **uv** for fast Python package management
- **pytest** for comprehensive testing
- **httpx** for async HTTP requests

## 📦 **Installation & Setup**

### Prerequisites
- Python 3.11+
- uv package manager
- OpenAI API key
- Google Serper API key

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd morning_stock_screener

# Create virtual environment and install dependencies
make venv
make install-dev

# Set up environment variables
cp env.example .env
# Edit .env with your API keys
```

### Environment Variables
Create a `.env` file with:
```bash
OPENAI_API_KEY=your_openai_key_here
SERPER_API_KEY=your_serper_key_here
OPENAI_MODEL=gpt-5
```

## 🚀 **Available Commands**

### **Setup & Installation**
```bash
make venv              # Create virtual environment
make activate          # Show activation command
make venv-status       # Check virtual environment status
make install           # Install production dependencies
make install-dev       # Install development dependencies
```

### **Testing & Development**
```bash
make test              # Run all tests
make test-cov          # Run tests with coverage report
make lint              # Run linting checks
make format            # Format code with black and isort
```

### **Running the System**
```bash
make run               # Run the main stock screener application
make chat              # Run LLM test interface
```

### **Maintenance**
```bash
make clean             # Clean build artifacts and cache
make help              # Show this help message
```

## 🧪 **Testing the System**

### **1. Verify Basic Setup**
```bash
# Check virtual environment
make venv-status

# Run unit tests
make test

# Run with coverage
make test-cov
```

### **2. Test LLM Integration**
```bash
# Test GPT-5 integration
make chat
```

### **3. Test Google Serper (Use Sparingly - Uses API Credits)**
```bash
# Direct command to avoid accidental usage
python -m src.testing.serper_test_client
```

**⚠️ Note**: The Serper test uses significant API credits. Only run when you need to validate the system is working.

### **4. Verify All Components**
```bash
# Run integration tests
python -m pytest tests/integration/ -v

# Check specific components
python -m pytest tests/unit/test_google_serper.py -v
python -m pytest tests/unit/test_search_registry.py -v
```

## 📊 **Current Test Coverage**

- **Total Tests**: 113+ (unit + integration)
- **Coverage**: Comprehensive across all core components
- **All Tests Passing**: ✅ 100% success rate
- **Integration Tests**: Real API calls to OpenAI and Serper

## 🔍 **System Validation Checklist**

Before proceeding to Phase 3, verify:

- [ ] **Virtual Environment**: `make venv-status` shows active environment
- [ ] **Dependencies**: `make install-dev` completes without errors
- [ ] **Unit Tests**: `make test` shows all tests passing
- [ ] **LLM Integration**: `make chat` allows conversation with GPT-5
- [ ] **Google Serper**: `python -m src.testing.serper_test_client` runs successfully (when needed)
- [ ] **Data Models**: All Pydantic models validate correctly
- [ ] **Search Registry**: 118+ market queries, 82+ news queries, 60+ stock queries available

## 🏗️ **Project Structure**

```
morning_stock_screener/
├── src/
│   ├── agents/           # Multi-agent framework
│   ├── config/           # Configuration and settings
│   ├── llm/              # LLM wrappers (OpenAI)
│   ├── models/           # Pydantic data models
│   ├── tools/            # Tools (Google Serper, Search Registry)
│   └── testing/          # Test clients and utilities
├── tests/                # Comprehensive test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Test data and coverage reports
├── specs/               # Project specifications and plans
├── tmp/                 # Temporary outputs (gitignored)
└── Makefile             # Development automation
```

## 📈 **Performance & Quality**

- **Response Time**: GPT-5 responses typically under 10 seconds
- **Search Coverage**: 100+ financial websites with intelligent filtering
- **Data Quality**: Real-time market data, news, and analysis
- **Error Handling**: Comprehensive error handling and logging
- **Rate Limiting**: Built-in API rate limiting and retry logic

## 🚀 **Ready for Phase 3**

The system foundation is complete and robust:

1. **✅ GPT-5 Integration**: Working independently
2. **✅ Google Serper**: Comprehensive data collection
3. **✅ Data Models**: Robust validation and structure
4. **✅ Base Architecture**: Extensible agent and tool framework
5. **✅ Testing**: Comprehensive test coverage
6. **✅ Documentation**: Clear setup and usage instructions

**Next Step**: Implement the 8-agent workflow to create the ultimate stock screener!

## 🤝 **Contributing**

This is a development project. All contributions should follow the established patterns:
- Test-driven development
- Comprehensive error handling
- Async/await patterns
- Pydantic v2 data models
- Extensive logging and monitoring

## 📄 **License**

[Your License Here]
