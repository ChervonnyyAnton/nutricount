# Mutation Testing Guide

## Overview

Mutation testing is a technique to evaluate the quality of test suites by introducing small changes (mutations) to the source code and checking if the tests can detect these changes. This ensures that tests are not only passing but also effectively catching bugs.

## What is Mutation Testing?

Mutation testing works by:
1. **Creating Mutants**: Small changes are made to the source code (e.g., changing `+` to `-`, `==` to `!=`)
2. **Running Tests**: The test suite is run against each mutant
3. **Analyzing Results**: 
   - **Killed**: Test suite detected the mutation (GOOD)
   - **Survived**: Test suite did not detect the mutation (BAD - test quality issue)
   - **Timeout**: Mutant caused infinite loop or took too long
   - **Suspicious**: Unclear result

## Why Mutation Testing?

Traditional code coverage shows which lines are executed during tests, but it doesn't prove that tests actually verify the correct behavior. Mutation testing ensures:

- **Test Effectiveness**: Tests actually catch bugs, not just execute code
- **Edge Cases**: Tests cover boundary conditions and error paths
- **Test Quality**: Tests are meaningful, not just placeholder assertions
- **Confidence**: High mutation score = high confidence in test suite

## Setup

Mutation testing is configured using **mutmut**, a mutation testing framework for Python.

### Installation

Mutmut is already included in `requirements-minimal.txt`:

```bash
pip install -r requirements-minimal.txt
```

### Configuration

Configuration is in `pyproject.toml`:

```toml
[tool.mutmut]
paths_to_mutate = "src/"
backup = false
runner = "python -m pytest --tb=short --disable-warnings -x"
tests_dir = "tests/"
dict_synonyms = "Struct, NamedStruct"
```

## Running Mutation Testing

### Basic Usage

```bash
# Run mutation testing
make mutation-test

# Or directly with mutmut
export PYTHONPATH=/home/runner/work/nutricount/nutricount
mutmut run --paths-to-mutate=src/
```

### View Results

```bash
# Show summary of results
make mutation-results
mutmut results

# Show details of surviving mutants
mutmut show
```

### Generate HTML Report

```bash
# Generate HTML report
make mutation-html
mutmut html

# Open html/index.html in browser
```

## Understanding Results

### Mutation Score

Mutation score = (Killed mutants) / (Total mutants - Timeouts - Suspicious)

**Target Scores:**
- **90-100%**: Excellent test quality
- **80-90%**: Good test quality
- **70-80%**: Acceptable test quality
- **Below 70%**: Needs improvement

### Example Output

```
Mutant #1 - survived
--- src/utils.py
+++ src/utils.py
@@ -15,7 +15,7 @@
     try:
-        if value is None:
+        if value is not None:
             return default
```

This indicates a test gap: the test suite doesn't verify the `None` case properly.

## Fixing Surviving Mutants

When mutants survive, it means tests are missing or inadequate. Here's how to fix:

### 1. Identify the Gap

```bash
# Show specific mutant
mutmut show <mutant_id>
```

### 2. Analyze the Mutation

Understand what the mutation changed and why tests didn't catch it.

### 3. Add/Improve Tests

Write tests that specifically verify the mutated behavior:

```python
# Before: Missing test
def test_safe_float():
    assert safe_float("123.45") == 123.45

# After: Added None case test
def test_safe_float_none():
    assert safe_float(None) == 0.0  # Now will catch the mutation
    assert safe_float(None, 5.0) == 5.0
```

### 4. Re-run Mutation Testing

```bash
# Run for specific mutants
mutmut run --paths-to-mutate=src/utils.py

# Verify the mutant is now killed
mutmut results
```

## Common Mutation Types

### 1. Arithmetic Operators
```python
# Original → Mutant
a + b → a - b
a * b → a / b
a / b → a // b
```

### 2. Comparison Operators
```python
# Original → Mutant
a == b → a != b
a < b → a <= b
a > b → a >= b
```

### 3. Boolean Operators
```python
# Original → Mutant
if condition: → if not condition:
a and b → a or b
True → False
```

### 4. Return Values
```python
# Original → Mutant
return value → return None
return True → return False
return 0 → return 1
```

### 5. Constant Values
```python
# Original → Mutant
"string" → ""
100 → 101
[1, 2, 3] → []
```

## Best Practices

### 1. Start Small

Don't run mutation testing on entire codebase at once:

```bash
# Test specific module first
mutmut run --paths-to-mutate=src/utils.py

# Then expand gradually
mutmut run --paths-to-mutate=src/security.py
mutmut run --paths-to-mutate=src/
```

### 2. Focus on Critical Code

Prioritize mutation testing for:
- Security-critical code (authentication, authorization)
- Business logic (calculations, validations)
- Error handling (exception paths)
- Edge case handling (boundary conditions)

### 3. Acceptable Survivors

Some mutants are acceptable to survive:
- **Logging statements**: Changing log messages rarely affects functionality
- **Performance optimizations**: Minor algorithm changes
- **Equivalent mutants**: Changes that don't affect behavior (e.g., `x + 0` → `x - 0`)

### 4. CI/CD Integration

Add mutation testing to CI/CD pipeline:

```yaml
# .github/workflows/mutation-test.yml
name: Mutation Testing

on:
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  mutation-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements-minimal.txt
      - name: Run mutation testing
        run: |
          export PYTHONPATH=$PWD
          mutmut run --paths-to-mutate=src/
      - name: Check mutation score
        run: |
          mutmut results
          # Fail if mutation score < 80%
          mutmut junitxml > mutation-results.xml
```

### 5. Iterative Improvement

- Run mutation testing regularly (weekly/monthly)
- Set incremental goals (increase score by 5% each sprint)
- Focus on new code first (easier to fix)
- Don't let perfect be the enemy of good (80%+ is excellent)

## Troubleshooting

### Slow Execution

Mutation testing can be slow. Optimize with:

```bash
# Run in parallel (if supported)
mutmut run --paths-to-mutate=src/ --use-coverage

# Test specific functions
mutmut run --paths-to-mutate=src/utils.py

# Use faster test runner
# Configure in pyproject.toml:
# runner = "python -m pytest --tb=short --disable-warnings -x"
```

### Timeouts

If mutants timeout:

```bash
# Increase timeout (default 10s)
mutmut run --timeout-multiplier 2.0
```

### Cache Issues

If results seem incorrect:

```bash
# Clear cache
rm -rf .mutmut-cache

# Re-run from scratch
mutmut run --paths-to-mutate=src/
```

## Example Workflow

Here's a complete workflow for improving test quality:

### Step 1: Baseline

```bash
# Run mutation testing
make mutation-test

# Check current score
make mutation-results
# Output: Mutation score: 65%
```

### Step 2: Identify Gaps

```bash
# View surviving mutants
mutmut show

# Or generate HTML report
make mutation-html
# Open html/index.html
```

### Step 3: Fix Tests

```python
# Example: Surviving mutant in src/utils.py
# Mutation: changed `if value is None:` to `if value is not None:`

# Add test in tests/unit/test_utils.py
def test_safe_float_none_value():
    """Test safe_float handles None correctly"""
    assert safe_float(None) == 0.0
    assert safe_float(None, default=5.0) == 5.0
```

### Step 4: Verify

```bash
# Re-run mutation testing
make mutation-test

# Check improvement
make mutation-results
# Output: Mutation score: 72% (improved!)
```

### Step 5: Repeat

Continue until target score (80%+) is reached.

## Metrics and Goals

### Current Status

| Module | Mutation Score | Status | Target |
|--------|---------------|--------|--------|
| src/utils.py | TBD | 🔄 Pending | 85%+ |
| src/security.py | TBD | 🔄 Pending | 90%+ |
| src/cache_manager.py | TBD | 🔄 Pending | 80%+ |
| src/monitoring.py | TBD | 🔄 Pending | 80%+ |
| Overall | TBD | 🔄 Pending | 80%+ |

### Improvement Roadmap

**Phase 1: Critical Modules (Week 1-2)**
- [ ] Run baseline mutation testing
- [ ] Fix security.py (target: 90%+)
- [ ] Fix utils.py (target: 85%+)

**Phase 2: Core Modules (Week 3-4)**
- [ ] Fix cache_manager.py (target: 80%+)
- [ ] Fix monitoring.py (target: 80%+)
- [ ] Fix fasting_manager.py (target: 80%+)

**Phase 3: Remaining Modules (Week 5-6)**
- [ ] Fix task_manager.py (target: 80%+)
- [ ] Fix nutrition_calculator.py (target: 80%+)
- [ ] Achieve 80%+ overall score

## Resources

- [Mutmut Documentation](https://mutmut.readthedocs.io/)
- [Mutation Testing Overview](https://en.wikipedia.org/wiki/Mutation_testing)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)

## Commands Quick Reference

```bash
# Installation
pip install -r requirements-minimal.txt

# Run mutation testing
make mutation-test
mutmut run --paths-to-mutate=src/

# View results
make mutation-results
mutmut results
mutmut show

# Generate HTML report
make mutation-html
mutmut html

# Clean up
make clean
rm -rf .mutmut-cache html/

# Run for specific file
mutmut run --paths-to-mutate=src/utils.py

# Re-run specific mutant
mutmut run <mutant_id>
```

---

**Status:** Mutation testing configured and ready to use  
**Tool:** mutmut 2.4.5  
**Target Score:** 80%+ overall  
**Next Steps:** Run baseline and fix surviving mutants
