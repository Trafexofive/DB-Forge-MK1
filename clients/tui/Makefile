# DB-Forge TUI Makefile

.PHONY: help install dev test lint format clean build

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	python -m venv venv
	source venv/bin/activate && pip install -e .
	@echo "✅ TUI installed. Run: source venv/bin/activate && dbforge-tui"

dev: ## Install development dependencies
	source venv/bin/activate && pip install -e ".[dev]"
	@echo "✅ Development environment ready"

run: ## Run the TUI application
	source venv/bin/activate && dbforge-tui

run-dev: ## Run TUI in development mode with debug
	source venv/bin/activate && dbforge-tui --dev --debug

test: ## Run tests
	source venv/bin/activate && pytest tests/ -v

lint: ## Run linting
	source venv/bin/activate && mypy src/
	source venv/bin/activate && black --check src/ tests/
	source venv/bin/activate && isort --check-only src/ tests/

format: ## Format code
	source venv/bin/activate && black src/ tests/
	source venv/bin/activate && isort src/ tests/
	@echo "✅ Code formatted"

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf venv/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned up"

build: ## Build distribution packages
	source venv/bin/activate && python -m build
	@echo "✅ Built packages in dist/"

demo: ## Show TUI demo
	@echo "🎬 DB-Forge TUI Demo"
	@echo ""
	@echo "1. Start DB-Forge server:"
	@echo "   cd ../../ && make up"
	@echo ""
	@echo "2. Run TUI:"
	@echo "   make run"
	@echo ""
	@echo "3. Navigate with keyboard:"
	@echo "   - Tab: Switch panels"
	@echo "   - Enter: Select database"
	@echo "   - Ctrl+Q: Quit"
	@echo "   - F1: Help"

# Examples
example-basic: ## Run basic usage example
	source venv/bin/activate && python examples/basic_usage.py

# Quality checks
check: lint test ## Run all quality checks

# Development workflow
setup: install dev ## Complete development setup
	@echo "🚀 Development environment ready!"
	@echo "Run 'make run' to start the TUI"