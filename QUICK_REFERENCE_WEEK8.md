# Week 8 Quick Reference Card

**⏱️ 2-Minute Overview** | **Status: Ready for Execution**

---

## 🎯 What to Do Next

### Option 1: E2E Tests (1-2 hours) ⚡ RECOMMENDED FIRST

**Why:** Quick win, validates all October fixes

**How:**
1. Go to: https://github.com/ChervonnyyAnton/nutricount/actions
2. Click "E2E Tests" → "Run workflow"
3. Branch: `copilot/continue-working-on-plan-please-work`
4. Wait 10-15 minutes
5. Check: Should see 115-120 tests passing (96%+)

**If successful (>= 96%):**
- Edit `.github/workflows/e2e-tests.yml`
- Uncomment `pull_request:` lines
- Commit: "Re-enable E2E tests on PRs"

---

### Option 2: Mutation Testing (8-12 hours) 🔬 AFTER OPTION 1

**Why:** Deep test quality validation

**How:**
```bash
cd /path/to/nutricount
./scripts/week8_validate.sh  # Health check

# Day 1 (3-4 hours)
mutmut run --paths-to-mutate=src/security.py --no-progress

# Day 2 (2-3 hours)  
mutmut run --paths-to-mutate=src/utils.py --no-progress

# Day 3 (3-4 hours)
mutmut run --paths-to-mutate=src/nutrition_calculator.py --no-progress
```

---

## 📊 Current Status

| Metric | Value | Status |
|--------|-------|--------|
| Tests Passing | 844/845 | ✅ |
| Coverage | 93% | ✅ |
| Linting | 0 errors | ✅ |
| Quality | 96/100 (A) | ✅ |
| Phase 1 | 100% | ✅ |
| E2E Expected | 96%+ | ⏳ |
| Mutation Baseline | 20% → 50% | ⏳ |

---

## 🚨 Key Commands

```bash
# Health check
./scripts/week8_validate.sh

# Run tests
export PYTHONPATH=$(pwd)
pytest tests/ -v

# Check linting
flake8 src/ --max-line-length=100 --ignore=E501,W503,E226

# Check coverage
pytest tests/ --cov=src --cov-report=term
```

---

## 📚 Documentation

| Doc | Purpose |
|-----|---------|
| [WEEK8_ACTION_ITEMS.md](WEEK8_ACTION_ITEMS.md) | Complete guide with all steps |
| [WEEK8_EXECUTION_GUIDE.md](WEEK8_EXECUTION_GUIDE.md) | Detailed reference |
| [scripts/week8_validate.sh](scripts/week8_validate.sh) | Automated health check |
| [INTEGRATED_ROADMAP.md](INTEGRATED_ROADMAP.md) | Overall progress |

---

## ⏰ Timeline

| Day | Task | Time |
|-----|------|------|
| Oct 27 | E2E validation | 1-2h |
| Oct 28 | Review & re-enable | 1h |
| Oct 29 | security.py | 3-4h |
| Oct 30 | utils.py | 2-3h |
| Oct 31 | nutrition_calculator.py | 3-4h |
| Nov 1 | Documentation | 1-2h |

---

## ✅ Success = Done

- [ ] E2E at 96%+ (115/120 tests)
- [ ] E2E workflow enabled on PRs
- [ ] Mutation baseline at 50% (5/11 modules)
- [ ] Results documented

---

## 🔥 Quick Start (Copy-Paste)

### For E2E Validation:
```
1. Open: https://github.com/ChervonnyyAnton/nutricount/actions
2. Click: "E2E Tests" workflow
3. Click: "Run workflow" button
4. Select: copilot/continue-working-on-plan-please-work
5. Click: Green "Run workflow" button
6. Wait: 10-15 minutes
7. Check: Results summary
```

### For Mutation Testing:
```bash
cd /path/to/nutricount
export PYTHONPATH=$(pwd)
./scripts/week8_validate.sh
mutmut run --paths-to-mutate=src/security.py --no-progress
```

---

## 🆘 Help

**E2E < 96%?** → Download artifacts, review failures  
**Mutation too slow?** → Check system resources, run one module at a time  
**Tests failing?** → Run `pytest tests/ -v`, fix, then resume  

---

**Status:** ✅ All docs ready, tools tested, ready to execute  
**Next:** Choose Option 1 (E2E) or Option 2 (Mutation)  
**Tip:** Do Option 1 first for quick win!

---

*Week 8 Phase 2 | Oct 27, 2025*
