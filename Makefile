# BSV Address Generator - Development Tools

.PHONY: help install format lint check test clean all run start-gui build appimage release

# Get App Version from config.py to use in filenames
APP_VERSION := $(shell grep -oP 'APP_VERSION = "\K[^"]+' config.py)

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
	@echo "  build     - Build a single-file executable for the GUI"
	@echo "  appimage  - Build a distributable AppImage for Linux"
	@echo "  release   - Build the release AppImage"
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

# Build the application
build:
	@echo "📦 Building single-file executable..."
	./venv/bin/pyinstaller --name "BSV_Address_Generator" \
	--onefile \
	--windowed \
	--additional-hooks-dir=./hooks \
	--hidden-import="coincurve._cffi_backend" \
	--icon="assets/app_icon.png" \
	--add-data="assets:assets" \
	gui.py
	@echo "✅ Build complete! Executable is in the 'dist' directory."

# Build the Linux AppImage
appimage:
	@echo "📦 Building Linux AppImage v$(APP_VERSION)..."
	@# 1. Ensure appimagetool exists
	@[ -f .bin/appimagetool ] || (mkdir -p .bin && \
	echo "Downloading appimagetool..." && \
	wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" -O .bin/appimagetool && \
	chmod +x .bin/appimagetool)
	
	@# 2. Build the app as a one-dir bundle
	./venv/bin/pyinstaller --name "BSV_Address_Generator" \
	--onedir \
	--windowed \
	--noconfirm \
	--additional-hooks-dir=./hooks \
	--hidden-import="coincurve._cffi_backend" \
	--add-data="assets:assets" \
	gui.py
	
	@# 3. Prepare the AppDir structure
	@mv dist/BSV_Address_Generator dist/AppDir
	@cp assets/app_icon.png dist/AppDir/
	
	@# 4. Create the .desktop file
	@printf "[Desktop Entry]\nName=BSV Address Generator\nExec=AppRun\nIcon=app_icon\nType=Application\nCategories=Utility;\n" > dist/AppDir/bsv-address-generator.desktop
	@chmod +x dist/AppDir/bsv-address-generator.desktop
	
	@# 5. Create the AppRun entrypoint script
	@printf '#!/bin/sh\nHERE=$$(dirname "$$(readlink -f "$$0")")\nexport PATH="$$HERE/usr/bin:$$PATH"\ncd $$HERE\n./BSV_Address_Generator "$$@"\n' > dist/AppDir/AppRun
	@chmod +x dist/AppDir/AppRun

	@# 6. Build the AppImage
	@./.bin/appimagetool dist/AppDir/ dist/BSV_Address_Generator-v$(APP_VERSION)-x86_64.AppImage
	
	@# 7. Clean up
	@rm -rf dist/AppDir build/ BSV_Address_Generator.spec
	
	@echo "✅ AppImage complete! Find it in the 'dist' directory."

# Release command
release: appimage

# Run everything
all: format lint
	@echo "🎉 All checks passed!" 