# 🤖 Morning Stock Screener

An AI-powered morning stock screener that provides top 10 stocks daily via email, designed for options traders who want to focus on execution rather than research.

## 🎯 Project Overview

Every morning at 9:30 AM BST, receive a curated list of the top 10 stocks most likely to go up in the day and near-to-medium term future. The system analyzes:

- **Market Conditions**: Overall sentiment, volatility, sector performance
- **Macroeconomic News**: Fed decisions, economic indicators, global events
- **Stock Analysis**: Fundamental, technical, news, analyst recommendations
- **AI Synthesis**: GPT-5 powered analysis and ranking

## 🏗️ Architecture

The system uses a multi-agent framework:

1. **Orchestrator**: Coordinates all other agents
2. **Market Analysis Agent**: Analyzes market conditions and macro news
3. **Stock Analysis Agent**: Deep-dive analysis of individual stocks
4. **News Analysis Agent**: Processes financial news and sentiment
5. **Ranker Agent**: Ranks stocks based on multiple factors
6. **Synthesis Agent**: Creates final top 10 list
7. **Email Sender Agent**: Delivers daily report via SMTP

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd morning_stock_screener
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Create and activate virtual environment**
   ```bash
   make venv                    # Create virtual environment
   make activate                # Show activation command
   source .venv/bin/activate   # Activate in your terminal
   ```

4. **Install dependencies**
   ```bash
   make install-dev
   ```

5. **Run tests**
   ```bash
   make test
   ```

6. **Start the chat application**
   ```bash
   make run
   ```

## Available Commands

```bash
# Setup & Installation
make venv          # Create virtual environment
make activate      # Show activation command
make venv-status   # Check virtual environment status
make install       # Install production dependencies
make install-dev   # Install development dependencies

# Testing & Development
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting checks
make format        # Format code
make clean         # Clean build artifacts

# Running the Application
make run           # Run the chat application
make example       # Run example usage

# Development Workflows
make dev           # Full development setup
make build         # Complete build and test
```

## 🧪 Testing

The project uses pytest with comprehensive test coverage:

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test file
pytest src/tests/test_models.py -v
```

## 🔧 Configuration

Create a `.env` file with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5
SERPER_API_KEY=your_serper_api_key_here  # For future use
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the full test suite: `make build`
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Always do your own due diligence before making investment decisions. The authors are not responsible for any financial losses.
