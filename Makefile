# BSV Address Generator - Development Tools

.PHONY: help format lint check test clean all

# Default target
help:
	@echo "Available commands:"
	@echo "  format    - Format code with black and isort"
	@echo "  lint      - Run all linters (flake8, pylint, mypy)"
	@echo "  check     - Run format check without making changes"
	@echo "  test      - Run the test script"
	@echo "  clean     - Clean up cache files"
	@echo "  all       - Run format, lint, and test"

# Format code
format:
	@echo "🎨 Formatting code with black..."
	./venv/bin/black *.py
	@echo "📦 Sorting imports with isort..."
	./venv/bin/isort *.py
	@echo "✅ Formatting complete!"

# Check formatting without making changes
check:
	@echo "🔍 Checking code format..."
	./venv/bin/black --check --diff *.py
	./venv/bin/isort --check-only --diff *.py

# Run linters
lint:
	@echo "🔎 Running flake8..."
	./venv/bin/flake8 *.py
	@echo "🔍 Running pylint..."
	./venv/bin/pylint *.py
	@echo "🎯 Running mypy..."
	./venv/bin/mypy *.py
	@echo "✅ Linting complete!"

# Run tests
test:
	@echo "🧪 Running test script..."
	./venv/bin/python test_script.py

# Clean cache files
clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Run everything
all: format lint test
	@echo "🎉 All checks passed!"

# Run the main application
run:
	@echo "🚀 Running BSV Address Generator..."
	./venv/bin/python main.py 