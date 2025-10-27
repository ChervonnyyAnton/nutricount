# Week 8 Execution Guide - Practical Steps

**Created:** October 27, 2025  
**Status:** Ready for Execution  
**Context:** Continuation of Week 8 Plan (Phase 1 Complete)

---

## 🎯 Current Status Summary

### Completed ✅
- **Phase 1 Mutation Testing:** constants.py + config.py (100%)
- **Test Baseline:** 844 tests passing, 1 skipped
- **Coverage:** 87-94% across modules
- **Code Quality:** 96/100 (Grade A)
- **E2E Test Fixes:** Phase 2 code complete, validation pending

### Progress Metrics
- **Mutation Testing Baseline:** 20% (2/11 modules)
- **E2E Expected Pass Rate:** 96% (115/120 tests)
- **Week 8 Overall:** Phase 1 complete, Phase 2 ready

---

## 🚀 Two Execution Paths

### Path A: E2E Test Validation (Quick Win - 1-2 hours)

**Prerequisites:**
- ✅ GitHub repository access
- ✅ Can view/trigger GitHub Actions
- ✅ Browser access to GitHub UI

**Step-by-Step Execution:**

1. **Navigate to GitHub Actions**
   ```
   https://github.com/ChervonnyyAnton/nutricount/actions
   ```

2. **Select E2E Tests Workflow**
   - Click "E2E Tests" from the left sidebar
   - You'll see the workflow list

3. **Trigger Manual Run**
   - Click "Run workflow" button (top right, gray button)
   - Dropdown appears with branch selection
   - Select branch: `copilot/continue-working-on-plan-please-work`
   - Click green "Run workflow" button

4. **Monitor Execution (10-15 minutes)**
   - Refresh page to see new workflow run appear
   - Click on the running workflow
   - Watch live logs (optional)
   - Wait for completion

5. **Review Results**
   - Check summary: "X of 120 tests passed"
   - Expected: 115-120 tests passing (96%+)
   - Click "Artifacts" if failures exist
   - Download failure reports/screenshots

6. **Document Outcome**
   Create file: `E2E_VALIDATION_RESULTS_OCT27.md`
   ```markdown
   # E2E Validation Results
   **Date:** October 27, 2025
   **Branch:** copilot/continue-working-on-plan-please-work
   
   ## Results
   - Tests Run: 120
   - Passed: X
   - Failed: Y
   - Pass Rate: Z%
   
   ## Analysis
   [Your analysis here]
   
   ## Next Steps
   [Based on results]
   ```

7. **Re-enable on PRs (If Successful >= 96%)**
   Edit `.github/workflows/e2e-tests.yml`:
   ```yaml
   on:
     pull_request:  # ← Uncomment this
       branches: [ main, develop ]  # ← And this
     workflow_dispatch:
   ```
   
   Commit and push:
   ```bash
   git add .github/workflows/e2e-tests.yml
   git commit -m "Re-enable E2E tests on PRs (96%+ pass rate validated)"
   git push origin copilot/continue-working-on-plan-please-work
   ```

**Expected Outcome:**
- ✅ E2E tests validated at 96%+ pass rate
- ✅ Workflow ready for PR checks
- ✅ Quick win for team confidence
- ⏱️ Time: 1-2 hours total

---

### Path B: Mutation Testing Phase 2 (Deep Analysis - 8-12 hours)

**Prerequisites:**
- ✅ Local development machine (not CI/CD)
- ✅ Python 3.11+ installed
- ✅ 2-4 hours available per day
- ✅ Repository cloned locally

**Important:** This CANNOT be run in CI/CD due to:
- 30+ seconds per mutant execution time
- Timeouts in CI environment
- 8-12 hours total execution time
- Requires human monitoring

**Setup (One-time - 5 minutes):**

```bash
# Clone repository (if not already)
git clone https://github.com/ChervonnyyAnton/nutricount.git
cd nutricount
git checkout copilot/continue-working-on-plan-please-work

# Setup environment
export PYTHONPATH=$(pwd)
mkdir -p logs

# Install dependencies
pip install -r requirements-minimal.txt

# Verify baseline
pytest tests/ -v
# Should show: 844 passed, 1 skipped
```

**Day 1: security.py (3-4 hours)**

```bash
# Start mutation testing
mutmut run --paths-to-mutate=src/security.py --no-progress

# This will take 3-4 hours. Progress shown in terminal.
# You can Ctrl+C to pause - cache is saved automatically.

# After completion, check results
mutmut results

# Expected output:
# To apply a mutant on disk:
#     mutmut apply <id>
# To show a mutant:
#     mutmut show <id>

# Generate HTML report
mutmut html

# This creates htmlcov/ directory
# Open htmlcov/index.html in browser to view

# Analyze survivors
mutmut show 1  # Show first surviving mutant
mutmut show 2  # Show second, etc.

# Document results
cat > docs/mutation-testing/baseline-security.md << 'EOF'
# security.py Mutation Testing Results

**Date:** October 27, 2025  
**Duration:** X hours  
**Module:** src/security.py

## Results Summary
- Total Mutants: X
- Killed: Y
- Survived: Z
- Score: A%

## Critical Survivors
[List concerning survivors requiring test improvements]

## Acceptable Survivors
[List survivors that are acceptable]

## Action Items
[Tests to add/improve]
EOF
```

**Day 2: utils.py (2-3 hours)**

```bash
# Same process as Day 1
mutmut run --paths-to-mutate=src/utils.py --no-progress
mutmut results
mutmut html

# Document results
# Create docs/mutation-testing/baseline-utils.md
```

**Day 3: nutrition_calculator.py (3-4 hours)**

```bash
# Same process
mutmut run --paths-to-mutate=src/nutrition_calculator.py --no-progress
mutmut results
mutmut html

# Document results
# Create docs/mutation-testing/baseline-nutrition_calculator.md
```

**After Phase 2 Complete:**

```bash
# Update baseline results
# Edit docs/mutation-testing/BASELINE_RESULTS.md

# Update roadmap
# Edit INTEGRATED_ROADMAP.md
# Change "Mutation Testing Baseline: 20%" to "50%" (5/11 modules)

# Commit all results
git add docs/mutation-testing/
git add INTEGRATED_ROADMAP.md
git commit -m "Complete mutation testing Phase 2 (security, utils, nutrition_calculator)"
git push origin copilot/continue-working-on-plan-please-work
```

**Expected Outcome:**
- ✅ 3 critical modules validated (security, utils, nutrition_calculator)
- ✅ Mutation scores: 85-90%+ expected
- ✅ Test improvement plan created
- ✅ 50% baseline complete (5/11 modules)
- ⏱️ Time: 8-12 hours over 3 days

---

## 📋 Decision Matrix

### Choose Path A if:
- ✅ Want immediate validation
- ✅ Need to unblock PR workflow
- ✅ Have GitHub Actions access
- ✅ Limited time available (1-2 hours)
- ✅ Team needs quick win

### Choose Path B if:
- ✅ Have local dev environment
- ✅ Can dedicate 2-4 hours/day for 3 days
- ✅ Want deep test quality analysis
- ✅ Following original Week 8 plan
- ✅ Ready for systematic approach

### Recommended: Both (Sequential)
1. **Today:** Path A - E2E validation (1-2 hours)
2. **Next 3 days:** Path B - Mutation testing (8-12 hours)
3. **Day 5:** Documentation and consolidation

---

## 🔍 Validation Commands

### Quick Health Check
```bash
# Run from repository root
cd /path/to/nutricount
export PYTHONPATH=$(pwd)

# Check tests
pytest tests/ -v --tb=short | tail -5
# Expected: "844 passed, 1 skipped"

# Check linting
flake8 src/ --max-line-length=100 --ignore=E501,W503,E226
# Expected: No output (0 errors)

# Check coverage
pytest tests/ --cov=src --cov-report=term-missing | grep "^TOTAL"
# Expected: 87-94%
```

### Mutation Testing Cache Check
```bash
# Check if cache exists (allows resume)
ls -lh .mutmut-cache 2>/dev/null

# If exists, you can resume with same command
# If not, you're starting fresh
```

### E2E Test Local Run (Optional)
```bash
# If you want to run E2E tests locally first
npm install
npx playwright install
npx playwright test

# This runs all 120 E2E tests locally
# Takes ~5-10 minutes
```

---

## 📊 Success Criteria

### Path A Success:
- ✅ E2E workflow triggered successfully
- ✅ 115+ tests passing (96%+)
- ✅ Workflow re-enabled on PRs
- ✅ Results documented

### Path B Success:
- ✅ All 3 modules tested (security, utils, nutrition_calculator)
- ✅ Mutation scores 85%+
- ✅ Survivors analyzed and documented
- ✅ Test improvement plan created
- ✅ Baseline results updated

### Overall Week 8 Success:
- ✅ E2E tests stable (96%+)
- ✅ 50% mutation baseline complete (5/11 modules)
- ✅ Test quality validated
- ✅ Clear path to completion

---

## 🚨 Troubleshooting

### E2E Tests Failing
```bash
# If pass rate < 96%:
1. Download failure artifacts from GitHub Actions
2. Review screenshots and traces
3. Check if failures are new or existing
4. Review error messages
5. Document patterns
6. Create issues for investigation
```

### Mutation Testing Too Slow
```bash
# If taking longer than expected:
1. Check system resources (CPU, memory)
2. Close other applications
3. Use --no-progress flag (already recommended)
4. Run one module at a time
5. Cache allows pause/resume (Ctrl+C is safe)
```

### Tests Failing During Mutation Testing
```bash
# If baseline tests fail:
1. Stop mutation testing (Ctrl+C)
2. Run: pytest tests/ -v
3. Fix any failing tests
4. Verify: pytest tests/ -v (all pass)
5. Resume mutation testing (same command)
```

---

## 📚 Reference Documentation

- **Overall Plan:** `INTEGRATED_ROADMAP.md`
- **Week 8 Overview:** `NEXT_STEPS_WEEK8.md`
- **Strategy:** `MUTATION_TESTING_STRATEGY.md`
- **Baseline Results:** `docs/mutation-testing/BASELINE_RESULTS.md`
- **Russian Report:** `ОТЧЕТ_ПРОДОЛЖЕНИЕ_ПЛАНА.md`

---

## ✅ Pre-flight Checklist

### Before E2E Validation:
- [ ] GitHub account has repository access
- [ ] Can navigate to Actions tab
- [ ] Browser available
- [ ] 1-2 hours available
- [ ] Ready to document results

### Before Mutation Testing:
- [ ] Local development machine ready
- [ ] Python 3.11+ installed
- [ ] Repository cloned locally
- [ ] Tests passing (844 passed, 1 skipped)
- [ ] 2-4 hours available for first module
- [ ] Ready for multi-day commitment

---

**Status:** Ready for Execution  
**Next Action:** Choose Path A or Path B (or both)  
**Support:** Refer to reference documentation for details

---

*Created: October 27, 2025*  
*Version: 1.0*  
*For: Week 8 Continuation*
