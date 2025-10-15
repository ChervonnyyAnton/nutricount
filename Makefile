# Nutrition Tracker Makefile
# Simple commands for development and testing

.PHONY: help test lint format clean install

help:
	@echo "Available commands:"
	@echo "  install         - Install dependencies"
	@echo "  test            - Run all tests"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-docker     - Run tests in Docker"
	@echo "  lint            - Run linting"
	@echo "  format          - Format code"
	@echo "  clean           - Clean up temporary files"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

test-integration:
	pytest tests/test_integration.py -v

test-docker:
	docker build -t nutrition-tracker-test .
	docker run --rm nutrition-tracker-test pytest tests/ -v

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	@echo "Code formatting not configured (using flake8 only)"

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name "htmlcov" -delete
