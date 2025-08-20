.PHONY: help install install-dev test test-cov lint format clean run example

# Default target
help:
	@echo "🤖 Morning Stock Screener - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  venv         - Create virtual environment"
	@echo "  activate     - Show activation command"
	@echo "  venv-status  - Check virtual environment status"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test         - Run all tests"
	@echo "  test-cov     - Run tests with coverage report"
	@echo ""
	@echo "🔧 Code Quality:"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo ""
	@echo "🚀 Running:"
	@echo "  run          - Run the chat application"
	@echo "  example      - Run example usage"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean        - Clean build artifacts and cache"
	@echo "  help         - Show this help message"

# Create and activate virtual environment
venv:
	@echo "🔧 Creating virtual environment..."
	uv venv
	@echo "✅ Virtual environment created at .venv/"
	@echo "🔧 Activating virtual environment..."
	@echo "source .venv/bin/activate"
	@echo "💡 Run 'source .venv/bin/activate' in your terminal to activate it"

# Check virtual environment status
venv-status:
	@echo "🔍 Checking virtual environment status..."
	@if [ -d ".venv" ]; then \
		echo "✅ Virtual environment exists at .venv/"; \
		echo "📦 Python version: $$(. .venv/bin/activate && python --version)"; \
		echo "📦 Installed packages:"; \
		. .venv/bin/activate && pip list; \
	else \
		echo "❌ No virtual environment found. Run 'make venv' to create one."; \
	fi

# Activate virtual environment in current shell
activate:
	@echo "🔧 Activating virtual environment in current shell..."
	@if [ -d ".venv" ]; then \
		echo "✅ Virtual environment found. Run this command in your terminal:"; \
		echo "source .venv/bin/activate"; \
		echo ""; \
		echo "Or use: . .venv/bin/activate"; \
	else \
		echo "❌ No virtual environment found. Run 'make venv' first."; \
	fi

# Install production dependencies
install: venv
	@echo "📦 Installing production dependencies..."
	. .venv/bin/activate && uv pip install -e .

# Install development dependencies
install-dev:
	@echo "🔧 Installing development dependencies..."
	. .venv/bin/activate && uv pip install -e ".[dev]"

# Run tests
test:
	@echo "🧪 Running tests..."
	@echo "🔧 Activating virtual environment (.venv)..."
	. .venv/bin/activate && python -m pytest tests/ -v

# Run tests with coverage
test-cov:
	@echo "📊 Running tests with coverage..."
	. .venv/bin/activate && python -m pytest tests/ -v --cov=src --cov-report=html:tests/fixtures/htmlcov --cov-report=term-missing

# Run linting
lint:
	@echo "🔍 Running linting checks..."
	. .venv/bin/activate && ruff check src/
	. .venv/bin/activate && mypy src/
	. .venv/bin/activate && black --check src/
	. .venv/bin/activate && isort --check-only src/

# Format code
format:
	@echo "✨ Formatting code..."
	. .venv/bin/activate && black src/
	. .venv/bin/activate && isort src/

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf tests/fixtures/.coverage
	rm -rf tests/fixtures/htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run the chat application
run:
	@echo "🚀 Starting chat application..."
	@echo "🔧 Activating virtual environment (.venv)..."
	. .venv/bin/activate && python -m src.main

# Run example usage
example:
	@echo "📚 Running example usage..."
	@echo "This will demonstrate the LLM wrapper functionality"
	@echo "Run 'make run' to test the chat interface"

# Development workflow
dev: venv install-dev format lint test
	@echo "✅ Development environment ready!"

# Full build and test
build: clean venv install-dev format lint test-cov
	@echo "🎉 Build completed successfully!"
