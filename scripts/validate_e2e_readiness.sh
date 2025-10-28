#!/bin/bash
# E2E Validation Readiness Check
# Validates that the repository is ready for E2E testing
# October 27, 2025

set -e

echo "🔍 E2E Validation Readiness Check"
echo "=================================="
echo ""

ERRORS=0
WARNINGS=0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print success
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
error() {
    echo -e "${RED}❌ $1${NC}"
    ((ERRORS++))
}

# Function to print warning
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

# 1. Check Python version
echo "1️⃣  Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    success "Python $PYTHON_VERSION installed"
else
    error "Python 3 not found"
fi
echo ""

# 2. Check Node.js version
echo "2️⃣  Checking Node.js version..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    success "Node.js $NODE_VERSION installed"
else
    error "Node.js not found"
fi
echo ""

# 3. Check npm dependencies
echo "3️⃣  Checking npm dependencies..."
if [ -f "package.json" ]; then
    success "package.json found"
    if [ -d "node_modules" ]; then
        success "node_modules directory exists"
        if [ -d "node_modules/@playwright/test" ]; then
            success "Playwright installed"
        else
            warning "Playwright not installed (run: npm install)"
        fi
    else
        warning "node_modules not found (run: npm install)"
    fi
else
    error "package.json not found"
fi
echo ""

# 4. Check Python dependencies
echo "4️⃣  Checking Python dependencies..."
if [ -f "requirements-minimal.txt" ]; then
    success "requirements-minimal.txt found"
    # Check if Flask is installed
    if python3 -c "import flask" 2>/dev/null; then
        success "Flask installed"
    else
        warning "Flask not installed (run: pip install -r requirements-minimal.txt)"
    fi
else
    error "requirements-minimal.txt not found"
fi
echo ""

# 5. Check E2E workflow configuration
echo "5️⃣  Checking E2E workflow configuration..."
if [ -f ".github/workflows/e2e-tests.yml" ]; then
    success "E2E workflow file found"
    if grep -q "workflow_dispatch" ".github/workflows/e2e-tests.yml"; then
        success "Manual trigger enabled"
    else
        warning "workflow_dispatch not found in E2E workflow"
    fi
else
    error "E2E workflow file not found"
fi
echo ""

# 6. Check E2E test files
echo "6️⃣  Checking E2E test files..."
if [ -d "tests/e2e-playwright" ]; then
    success "E2E test directory found"
    TEST_COUNT=$(ls -1 tests/e2e-playwright/*.spec.js 2>/dev/null | wc -l)
    if [ "$TEST_COUNT" -gt 0 ]; then
        success "Found $TEST_COUNT E2E test files"
    else
        error "No E2E test files found"
    fi
else
    error "E2E test directory not found"
fi
echo ""

# 7. Check Playwright configuration
echo "7️⃣  Checking Playwright configuration..."
if [ -f "playwright.config.js" ]; then
    success "Playwright config found"
else
    error "playwright.config.js not found"
fi
echo ""

# 8. Check test helpers
echo "8️⃣  Checking test helpers..."
if [ -f "tests/e2e-playwright/helpers/page-helpers.js" ]; then
    success "Page helpers found"
else
    warning "Page helpers not found (tests might fail)"
fi
echo ""

# 9. Check logs directory
echo "9️⃣  Checking logs directory..."
if [ -d "logs" ]; then
    success "logs directory exists"
else
    warning "logs directory not found (will be created on test run)"
fi
echo ""

# 10. Check database schema
echo "🔟 Checking database schema..."
if [ -f "schema_v2.sql" ]; then
    success "Database schema found"
else
    error "schema_v2.sql not found"
fi
echo ""

# 11. Check init_db script
echo "1️⃣1️⃣  Checking database initialization..."
if [ -f "init_db.py" ]; then
    success "init_db.py found"
else
    error "init_db.py not found"
fi
echo ""

# 12. Check app.py
echo "1️⃣2️⃣  Checking Flask application..."
if [ -f "app.py" ]; then
    success "app.py found"
else
    error "app.py not found"
fi
echo ""

# 13. Run unit tests to verify repository health
echo "1️⃣3️⃣  Running unit tests (quick verification)..."
if command -v pytest &> /dev/null; then
    export PYTHONPATH=$(pwd)
    mkdir -p logs  # Ensure logs directory exists
    if pytest tests/ -q --tb=no -x 2>&1 | tail -1 | grep -q "passed"; then
        success "Unit tests passing"
    else
        warning "Some unit tests failing (but E2E can still be validated)"
    fi
else
    warning "pytest not found (cannot verify unit tests)"
fi
echo ""

# 14. Check git status
echo "1️⃣4️⃣  Checking git status..."
if git rev-parse --is-inside-work-tree &> /dev/null; then
    success "Git repository detected"
    BRANCH=$(git branch --show-current)
    success "Current branch: $BRANCH"
    if git status --porcelain | grep -q .; then
        warning "Working directory has uncommitted changes"
    else
        success "Working directory clean"
    fi
else
    error "Not a git repository"
fi
echo ""

# Summary
echo "=================================="
echo "📊 Summary"
echo "=================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Repository is ready for E2E validation.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Navigate to: https://github.com/ChervonnyyAnton/nutricount/actions"
    echo "2. Select 'E2E Tests' workflow"
    echo "3. Click 'Run workflow'"
    echo "4. Monitor results (~15 minutes)"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS warnings found, but repository is mostly ready.${NC}"
    echo ""
    echo "Recommended actions:"
    if [ ! -d "node_modules" ]; then
        echo "- Run: npm install"
    fi
    if ! python3 -c "import flask" 2>/dev/null; then
        echo "- Run: pip install -r requirements-minimal.txt"
    fi
    echo ""
    echo "You can proceed with E2E validation, but address warnings for best results."
    echo ""
    exit 0
else
    echo -e "${RED}❌ $ERRORS errors found. Please fix before proceeding with E2E validation.${NC}"
    echo ""
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Also found $WARNINGS warnings.${NC}"
        echo ""
    fi
    exit 1
fi
