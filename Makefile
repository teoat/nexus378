# Nexus Forensic Reconciliation Platform - Development Makefile

.PHONY: help install format lint quality test clean docs

# Default target
help:
	@echo "🚀 Nexus Forensic Platform - Development Commands"
	@echo "================================================"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  install          Install all dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo ""
	@echo "🎨 Code Quality:"
	@echo "  format           Format code with Black and isort"
	@echo "  lint             Run flake8 and pylint"
	@echo "  quality          Run comprehensive quality check"
	@echo "  quality-fix      Auto-fix quality issues"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test             Run all tests"
	@echo "  test-syntax      Check Python syntax"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs             Generate documentation"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean            Clean up temporary files"
	@echo "  pre-commit       Install pre-commit hooks"
	@echo ""

# Installation
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "🔧 Installing development dependencies..."
	pip install black isort flake8 pylint pre-commit
	@echo "✅ Development dependencies installed"

# Code formatting
format:
	@echo "🎨 Formatting code with Black..."
	black --line-length=88 forensic_reconciliation_app/
	@echo "📦 Organizing imports with isort..."
	isort --profile=black --line-length=88 forensic_reconciliation_app/
	@echo "✅ Code formatting complete"

# Linting
lint:
	@echo "🔍 Running flake8..."
	flake8 --max-line-length=88 --extend-ignore=E203,W503 forensic_reconciliation_app/
	@echo "🔬 Running pylint on key files..."
	pylint --max-line-length=88 --disable=C0114,C0115,C0116,R0903,R0913,R0914,W0621,W0622,W0703,W0612,W0611 \
		forensic_reconciliation_app/ai_service/agents/pattern_detector.py \
		forensic_reconciliation_app/ai_service/taskmaster/core/collective_worker_processor.py \
		forensic_reconciliation_app/ai_service/auth/mfa/mfa_manager.py
	@echo "✅ Linting complete"

# Quality check
quality:
	@echo "🚀 Running comprehensive quality check..."
	python code_quality_manager.py

quality-fix:
	@echo "🔧 Auto-fixing quality issues..."
	black --line-length=88 forensic_reconciliation_app/
	isort --profile=black --line-length=88 forensic_reconciliation_app/
	@echo "✅ Quality fixes applied"

# Testing
test:
	@echo "🧪 Running all tests..."
	python -m pytest forensic_reconciliation_app/ -v

test-syntax:
	@echo "🐍 Checking Python syntax..."
	find forensic_reconciliation_app/ -name "*.py" -exec python -m py_compile {} \;
	@echo "✅ All Python files compile successfully"

# Documentation
docs:
	@echo "📚 Generating documentation..."
	pydoc -w forensic_reconciliation_app/
	@echo "✅ Documentation generated"

# Pre-commit hooks
pre-commit:
	@echo "🔗 Installing pre-commit hooks..."
	pre-commit install
	@echo "✅ Pre-commit hooks installed"

# Cleanup
clean:
	@echo "🧹 Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Development workflow
dev-setup: install-dev pre-commit
	@echo "🚀 Development environment setup complete!"
	@echo "Run 'make quality' to check code quality"
	@echo "Run 'make format' to format code before committing"

# Quick quality check
quick-check: format lint test-syntax
	@echo "✅ Quick quality check complete"

# Full development cycle
dev-cycle: clean format lint quality test-syntax
	@echo "🎉 Full development cycle complete!"
