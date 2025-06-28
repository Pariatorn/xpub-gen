# BSV Address Generator - Development Tools

.PHONY: help install format lint check test clean all run start-gui

# Default target
help:
	@echo "Available commands:"
	@echo "  install   - Install dependencies in virtual environment"
	@echo "  format    - Format code with black and isort"
	@echo "  lint      - Run all linters (flake8, pylint, mypy)"
	@echo "  check     - Run format check without making changes"
	@echo "  test      - Run the test script"
	@echo "  clean     - Clean up cache files"
	@echo "  run       - Run the CLI application"
	@echo "  start-gui - Start the GUI application"
	@echo "  all       - Run format and lint"

# Install dependencies
install:
	@echo "🔧 Setting up virtual environment and installing dependencies..."
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "✅ Installation complete! Use 'make run' for CLI or 'make start-gui' for GUI"

# Format code
format:
	@echo "🎨 Formatting code with black..."
	./venv/bin/black . --exclude venv
	@echo "📦 Sorting imports with isort..."
	./venv/bin/isort . --skip venv
	@echo "✅ Formatting complete!"

# Check formatting without making changes
check:
	@echo "🔍 Checking code format..."
	./venv/bin/black --check --diff . --exclude venv
	./venv/bin/isort --check-only --diff . --skip venv

# Run linters
lint:
	@echo "🔎 Running flake8..."
	./venv/bin/flake8 . --exclude=venv
	@echo "🔍 Running pylint..."
	./venv/bin/pylint **/*.py --ignore=venv
	@echo "🎯 Running mypy..."
	./venv/bin/mypy . --exclude venv
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
all: format lint
	@echo "🎉 All checks passed!"

# Run the main CLI application
run:
	@echo "🚀 Running BSV Address Generator (CLI)..."
	./venv/bin/python main.py

# Start the GUI application
start-gui:
	@echo "🖥️ Starting BSV Address Generator GUI..."
	./venv/bin/python gui.py 