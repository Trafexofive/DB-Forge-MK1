# Makefile for DB-Forge Client Libraries

.PHONY: help install-python install-cpp test-python test-cpp clean examples lint

# Default target
help:
	@echo "DB-Forge Client Libraries"
	@echo "========================"
	@echo ""
	@echo "Available targets:"
	@echo "  install-python    Install Python client library"
	@echo "  install-cpp       Build C++ client library"
	@echo "  test-python       Run Python tests"
	@echo "  test-cpp          Run C++ tests"
	@echo "  examples-python   Run Python examples"
	@echo "  examples-cpp      Run C++ examples"
	@echo "  lint-python       Lint Python code"
	@echo "  clean-python      Clean Python build artifacts"
	@echo "  clean-cpp         Clean C++ build artifacts"
	@echo "  clean             Clean all build artifacts"
	@echo "  install           Install both client libraries"
	@echo "  test              Run all tests"
	@echo "  examples          Run all examples"

# Installation targets
install: install-python install-cpp

install-python:
	@echo "Installing Python client library..."
	cd python && pip install -e .

install-cpp:
	@echo "Building C++ client library..."
	cd cpp && mkdir -p build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release && make -j$$(nproc)

# Test targets
test: test-python test-cpp

test-python:
	@echo "Running Python tests..."
	cd python && python -m pytest tests/ -v

test-cpp: install-cpp
	@echo "Running C++ tests..."
	cd cpp/build && make test

# Example targets
examples: examples-python examples-cpp

examples-python: install-python
	@echo "Running Python basic example..."
	cd python && python examples/basic_usage.py
	@echo ""
	@echo "Running Python async example..."
	cd python && python examples/async_usage.py

examples-cpp: install-cpp
	@echo "Running C++ basic example..."
	cd cpp/build && ./examples/basic_example
	@echo ""
	@echo "Running C++ advanced example..."
	cd cpp/build && ./examples/advanced_example

# Linting targets
lint: lint-python

lint-python:
	@echo "Linting Python code..."
	cd python && python -m black --check .
	cd python && python -m isort --check-only .
	cd python && python -m mypy dbforge_client

# Format code
format: format-python

format-python:
	@echo "Formatting Python code..."
	cd python && python -m black .
	cd python && python -m isort .

# Clean targets
clean: clean-python clean-cpp

clean-python:
	@echo "Cleaning Python artifacts..."
	cd python && rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/
	find python -name "*.pyc" -delete
	find python -name "__pycache__" -type d -exec rm -rf {} +

clean-cpp:
	@echo "Cleaning C++ artifacts..."
	cd cpp && rm -rf build/

# Development targets
dev-setup: dev-setup-python

dev-setup-python:
	@echo "Setting up Python development environment..."
	cd python && pip install -e .[dev]

# Package targets
package: package-python

package-python:
	@echo "Building Python package..."
	cd python && python setup.py sdist bdist_wheel

# CLI tests
cli-test: install-python
	@echo "Testing Python CLI..."
	cd python && dbforge --help
	@echo "CLI test completed successfully"

# Integration tests (require running DB-Forge server)
integration-test: install-python install-cpp
	@echo "Running integration tests..."
	@echo "Note: Requires DB-Forge server to be running (make up from project root)"
	cd python && python -m pytest tests/ -v -m integration
	cd cpp/build && ctest --verbose

# Documentation targets
docs:
	@echo "Client library documentation:"
	@echo "- Python: clients/python/README.md"
	@echo "- C++: clients/cpp/README.md"  
	@echo "- Examples in respective examples/ directories"

# Check dependencies
check-deps:
	@echo "Checking Python dependencies..."
	python --version
	pip --version
	@echo ""
	@echo "Checking C++ dependencies..."
	gcc --version || clang --version
	cmake --version
	pkg-config --version
	pkg-config --exists libcurl && echo "libcurl: OK" || echo "libcurl: MISSING"
	pkg-config --exists jsoncpp && echo "jsoncpp: OK" || echo "jsoncpp: MISSING"

# Install system dependencies (Ubuntu/Debian)
install-deps-ubuntu:
	sudo apt-get update
	sudo apt-get install -y \
		python3-dev python3-pip \
		build-essential cmake \
		libcurl4-openssl-dev libjsoncpp-dev \
		libgtest-dev

# Install system dependencies (macOS)
install-deps-macos:
	brew install python cmake curl jsoncpp googletest