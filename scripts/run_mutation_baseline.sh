#!/bin/bash
# Mutation Testing Baseline Script for Nutricount
# This script runs mutation testing on all modules and generates a comprehensive report
#
# Usage:
#   ./scripts/run_mutation_baseline.sh [module|all]
#
# Examples:
#   ./scripts/run_mutation_baseline.sh all           # Run all modules (SLOW!)
#   ./scripts/run_mutation_baseline.sh utils         # Run only utils.py
#   ./scripts/run_mutation_baseline.sh quick         # Run quick baseline (simple modules only)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Setup environment
export PYTHONPATH=/home/runner/work/nutricount/nutricount
cd /home/runner/work/nutricount/nutricount

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}  Mutation Testing Baseline for Nutricount${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# Check if mutmut is installed
if ! command -v mutmut &> /dev/null; then
    echo -e "${RED}Error: mutmut is not installed${NC}"
    echo "Run: pip install -r requirements-minimal.txt"
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p reports/mutation

# Parse arguments
TARGET="${1:-help}"

# Function to run mutation testing on a module
run_mutation() {
    local module=$1
    local module_name=$(basename $module .py)
    
    echo -e "${YELLOW}Running mutation testing on: $module${NC}"
    echo "This may take 30 minutes to several hours..."
    echo ""
    
    # Clean previous cache
    rm -f .mutmut-cache
    
    # Run mutation testing with coverage optimization
    echo -e "${BLUE}[$(date '+%H:%M:%S')] Starting mutation testing...${NC}"
    mutmut run --paths-to-mutate="$module" --use-coverage 2>&1 | tee "logs/mutation-${module_name}.log"
    
    # Generate results
    echo ""
    echo -e "${BLUE}[$(date '+%H:%M:%S')] Generating results...${NC}"
    mutmut results | tee "logs/mutation-${module_name}-results.txt"
    
    # Generate HTML report
    mutmut html
    echo -e "${GREEN}HTML report generated in: html/index.html${NC}"
    
    echo ""
    echo -e "${GREEN}==================================================${NC}"
    echo -e "${GREEN}  Mutation testing completed for $module_name!${NC}"
    echo -e "${GREEN}==================================================${NC}"
}

# Function to show help
show_help() {
    echo "Mutation Testing Baseline Script"
    echo ""
    echo "Usage:"
    echo "  $0 [option]"
    echo ""
    echo "Options:"
    echo "  all             Run all modules (WARNING: Takes 8-12 hours!)"
    echo "  quick           Run quick baseline (constants, config, utils)"
    echo "  critical        Run critical modules (security, utils)"
    echo "  core            Run core modules (cache, monitoring, fasting)"
    echo "  utils           Run utils.py only"
    echo "  security        Run security.py only"
    echo "  [module]        Run specific module (e.g., cache_manager)"
    echo ""
    echo "Module Priority Order:"
    echo "  1. Critical: constants, config, utils, security"
    echo "  2. Core: cache_manager, monitoring, fasting_manager"
    echo "  3. Support: nutrition_calculator, task_manager, advanced_logging, ssl_config"
    echo ""
    echo "Estimated Times:"
    echo "  constants.py:           30-60 minutes"
    echo "  config.py:              1-2 hours"
    echo "  utils.py:               3-4 hours"
    echo "  security.py:            3-4 hours"
    echo "  nutrition_calculator:   4-6 hours"
    echo "  All modules:            8-12 hours"
    echo ""
}

# Main execution
case "$TARGET" in
    help)
        show_help
        ;;
        
    all)
        echo -e "${YELLOW}WARNING: This will run mutation testing on ALL modules!${NC}"
        echo -e "${YELLOW}Estimated time: 8-12 hours${NC}"
        echo ""
        read -p "Continue? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Aborted."
            exit 0
        fi
        
        # Run all modules in priority order
        modules=(
            "src/constants.py"
            "src/config.py"
            "src/utils.py"
            "src/security.py"
            "src/cache_manager.py"
            "src/monitoring.py"
            "src/fasting_manager.py"
            "src/nutrition_calculator.py"
            "src/task_manager.py"
            "src/advanced_logging.py"
            "src/ssl_config.py"
        )
        
        for module in "${modules[@]}"; do
            echo ""
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            run_mutation "$module"
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
        done
        
        echo -e "${GREEN}All modules completed!${NC}"
        ;;
        
    quick)
        echo -e "${BLUE}Running quick baseline (simple modules only)${NC}"
        echo -e "${YELLOW}Estimated time: 2-3 hours${NC}"
        echo ""
        
        modules=(
            "src/constants.py"
            "src/config.py"
        )
        
        for module in "${modules[@]}"; do
            run_mutation "$module"
            echo ""
        done
        ;;
        
    critical)
        echo -e "${BLUE}Running critical modules${NC}"
        echo -e "${YELLOW}Estimated time: 6-8 hours${NC}"
        echo ""
        
        modules=(
            "src/utils.py"
            "src/security.py"
        )
        
        for module in "${modules[@]}"; do
            run_mutation "$module"
            echo ""
        done
        ;;
        
    core)
        echo -e "${BLUE}Running core modules${NC}"
        echo -e "${YELLOW}Estimated time: 8-10 hours${NC}"
        echo ""
        
        modules=(
            "src/cache_manager.py"
            "src/monitoring.py"
            "src/fasting_manager.py"
        )
        
        for module in "${modules[@]}"; do
            run_mutation "$module"
            echo ""
        done
        ;;
        
    utils|security|cache_manager|monitoring|fasting_manager|nutrition_calculator|task_manager|advanced_logging|ssl_config|constants|config)
        run_mutation "src/${TARGET}.py"
        ;;
        
    *)
        echo -e "${RED}Unknown option: $TARGET${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}  Mutation testing baseline complete!${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Review results in logs/ directory"
echo "  2. Check HTML report in html/index.html"
echo "  3. Analyze surviving mutants"
echo "  4. Update MUTATION_TESTING.md with results"
echo "  5. Create test improvement plan"
echo ""
