#!/bin/bash
# Mutation Testing Script for Nutricount

set -e

# Setup environment
export PYTHONPATH=/home/runner/work/nutricount/nutricount
cd /home/runner/work/nutricount/nutricount

echo "==================================================="
echo "Mutation Testing for Nutricount"
echo "==================================================="
echo ""

# Check if mutmut is installed
if ! command -v mutmut &> /dev/null; then
    echo "Error: mutmut is not installed"
    echo "Run: pip install -r requirements-minimal.txt"
    exit 1
fi

# Parse arguments
TARGET="${1:-src/}"
ACTION="${2:-run}"

case "$ACTION" in
    run)
        echo "Running mutation testing on: $TARGET"
        echo "This may take several minutes..."
        echo ""
        
        # Create logs directory
        mkdir -p logs
        
        # Run mutation testing
        mutmut run --paths-to-mutate="$TARGET" 2>&1 | tee logs/mutation-test.log
        
        echo ""
        echo "==================================================="
        echo "Mutation testing completed!"
        echo "==================================================="
        echo ""
        
        # Show results
        mutmut results
        ;;
        
    results)
        echo "Mutation Testing Results:"
        echo ""
        mutmut results
        ;;
        
    show)
        echo "Showing surviving mutants:"
        echo ""
        mutmut show
        ;;
        
    html)
        echo "Generating HTML report..."
        mutmut html
        echo ""
        echo "HTML report generated at: html/index.html"
        ;;
        
    clean)
        echo "Cleaning mutation testing cache..."
        rm -rf .mutmut-cache html/
        echo "Cache cleared!"
        ;;
        
    *)
        echo "Usage: $0 [target] [action]"
        echo ""
        echo "Targets:"
        echo "  src/              - All source files (default)"
        echo "  src/utils.py      - Specific file"
        echo ""
        echo "Actions:"
        echo "  run               - Run mutation testing (default)"
        echo "  results           - Show results summary"
        echo "  show              - Show surviving mutants"
        echo "  html              - Generate HTML report"
        echo "  clean             - Clean cache"
        echo ""
        echo "Examples:"
        echo "  $0                        # Run on all src/"
        echo "  $0 src/utils.py run       # Run on specific file"
        echo "  $0 src/ results           # Show results"
        echo "  $0 src/ html              # Generate HTML report"
        exit 1
        ;;
esac
