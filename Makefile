# Nutrition Tracker Makefile
# Simple commands for development and testing

.PHONY: help test lint format clean install mutation-test mutation-results mutation-html mutation-clean

help:
	@echo "Available commands:"
	@echo "  install           - Install dependencies"
	@echo "  test              - Run all tests"
	@echo "  test-integration  - Run integration tests only"
	@echo "  test-docker       - Run tests in Docker"
	@echo "  lint              - Run linting"
	@echo "  format            - Format code with black and isort"
	@echo "  mutation-test     - Run mutation testing with mutmut"
	@echo "  mutation-results  - Show mutation testing results"
	@echo "  mutation-html     - Generate mutation testing HTML report"
	@echo "  mutation-clean    - Clean mutation testing cache"
	@echo "  clean             - Clean up temporary files"

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
	flake8 app.py src/ routes/ services/ repositories/ --max-line-length=100 --ignore=E501,W503,E226 --statistics
	black --check app.py src/ routes/ services/ repositories/
	isort --check-only app.py src/ routes/ services/ repositories/

format:
	black app.py src/ routes/ services/ repositories/
	isort app.py src/ routes/ services/ repositories/

mutation-test:
	@chmod +x scripts/mutation_test.sh
	@./scripts/mutation_test.sh src/ run

mutation-results:
	@./scripts/mutation_test.sh src/ results

mutation-html:
	@./scripts/mutation_test.sh src/ html

mutation-clean:
	@./scripts/mutation_test.sh src/ clean

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name "htmlcov" -delete
	rm -rf .mutmut-cache html/ logs/mutation-test.log
