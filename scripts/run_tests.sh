#!/bin/bash
"""
Test runner script for Nutrition Tracker
"""
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing test dependencies..."
    
    if command_exists pip3; then
        pip3 install -r requirements.txt
    elif command_exists pip; then
        pip install -r requirements.txt
    else
        print_error "pip not found. Please install Python and pip first."
        exit 1
    fi
    
    print_success "Dependencies installed successfully"
}

# Function to run linting
run_linting() {
    print_status "Running code linting..."
    
    if command_exists flake8; then
        flake8 src/ --max-line-length=100 --ignore=E501,W503
        print_success "Linting passed"
    else
        print_warning "flake8 not found, skipping linting"
    fi
    
    if command_exists black; then
        black --check src/
        print_success "Code formatting check passed"
    else
        print_warning "black not found, skipping formatting check"
    fi
    
    if command_exists isort; then
        isort --check-only src/
        print_success "Import sorting check passed"
    else
        print_warning "isort not found, skipping import sorting check"
    fi
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    
    if command_exists pytest; then
        pytest tests/unit/ -v --cov=src --cov-report=term-missing --cov-report=html:htmlcov
        print_success "Unit tests completed"
    else
        print_error "pytest not found. Please install it first."
        exit 1
    fi
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    
    if command_exists pytest; then
        pytest tests/integration/ -v --cov=src --cov-report=term-missing
        print_success "Integration tests completed"
    else
        print_error "pytest not found. Please install it first."
        exit 1
    fi
}

# Function to run e2e tests
run_e2e_tests() {
    print_status "Running end-to-end tests..."
    
    if command_exists pytest; then
        pytest tests/e2e/ -v --cov=src --cov-report=term-missing
        print_success "End-to-end tests completed"
    else
        print_error "pytest not found. Please install it first."
        exit 1
    fi
}

# Function to run all tests
run_all_tests() {
    print_status "Running all tests..."
    
    if command_exists pytest; then
        pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml
        print_success "All tests completed"
    else
        print_error "pytest not found. Please install it first."
        exit 1
    fi
}

# Function to run performance tests
run_performance_tests() {
    print_status "Running performance tests..."
    
    if command_exists pytest; then
        pytest tests/ -v -m performance --cov=src --cov-report=term-missing
        print_success "Performance tests completed"
    else
        print_error "pytest not found. Please install it first."
        exit 1
    fi
}

# Function to run security tests
run_security_tests() {
    print_status "Running security tests..."
    
    if command_exists pytest; then
        pytest tests/ -v -m security --cov=src --cov-report=term-missing
        print_success "Security tests completed"
    else
        print_error "pytest not found. Please install it first."
        exit 1
    fi
}

# Function to generate test report
generate_report() {
    print_status "Generating test report..."
    
    if command_exists pytest; then
        pytest tests/ -v --cov=src --cov-report=html:htmlcov --cov-report=xml --junitxml=test-results.xml
        print_success "Test report generated in htmlcov/ and test-results.xml"
    else
        print_error "pytest not found. Please install it first."
        exit 1
    fi
}

# Function to clean test artifacts
clean_artifacts() {
    print_status "Cleaning test artifacts..."
    
    rm -rf htmlcov/
    rm -rf .coverage
    rm -rf test-results.xml
    rm -rf .pytest_cache/
    rm -rf __pycache__/
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} +
    
    print_success "Test artifacts cleaned"
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  install     Install test dependencies"
    echo "  lint        Run code linting"
    echo "  unit        Run unit tests"
    echo "  integration Run integration tests"
    echo "  e2e         Run end-to-end tests"
    echo "  all         Run all tests"
    echo "  performance Run performance tests"
    echo "  security    Run security tests"
    echo "  report      Generate test report"
    echo "  clean       Clean test artifacts"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install    # Install dependencies"
    echo "  $0 all        # Run all tests"
    echo "  $0 unit       # Run only unit tests"
    echo "  $0 report     # Generate test report"
}

# Main script logic
case "${1:-help}" in
    install)
        install_dependencies
        ;;
    lint)
        run_linting
        ;;
    unit)
        run_unit_tests
        ;;
    integration)
        run_integration_tests
        ;;
    e2e)
        run_e2e_tests
        ;;
    all)
        run_linting
        run_all_tests
        ;;
    performance)
        run_performance_tests
        ;;
    security)
        run_security_tests
        ;;
    report)
        generate_report
        ;;
    clean)
        clean_artifacts
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
