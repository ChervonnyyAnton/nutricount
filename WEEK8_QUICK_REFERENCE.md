# Week 8 Quick Reference Card

**Purpose:** Quick reference for Week 8 continuation tasks  
**Status:** Ready for Execution  
**Date:** October 27, 2025

---

## 🎯 Two Paths Available

### Path A: E2E Test Validation (1-2 hours)
**Trigger:** GitHub Actions UI  
**Expected:** 96%+ pass rate (115/120 tests)

```
1. Open: https://github.com/ChervonnyyAnton/nutricount/actions
2. Click: "E2E Tests" workflow
3. Click: "Run workflow" button
4. Select: copilot/continue-working-on-plan-please-work
5. Wait: 10-15 minutes
6. Result: Pass rate shown in summary
```

---

### Path B: Mutation Testing Phase 2 (8-12 hours)
**Environment:** Local development machine  
**Modules:** security.py, utils.py, nutrition_calculator.py

```bash
# Day 1: security.py (3-4 hours)
mutmut run --paths-to-mutate=src/security.py --no-progress
mutmut results
mutmut html

# Day 2: utils.py (2-3 hours)
mutmut run --paths-to-mutate=src/utils.py --no-progress
mutmut results
mutmut html

# Day 3: nutrition_calculator.py (3-4 hours)
mutmut run --paths-to-mutate=src/nutrition_calculator.py --no-progress
mutmut results
mutmut html
```

---

## ⚡ Quick Commands

### Validate Repository
```bash
./scripts/week8_validate.sh
```

### Run Tests
```bash
export PYTHONPATH=$(pwd)
pytest tests/ -v
```

### Check Linting
```bash
flake8 src/ --max-line-length=100 --ignore=E501,W503,E226
```

### Check Coverage
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

---

## 📊 Current Status

- **Tests:** 844/845 passing (99.9%) ✅
- **Coverage:** 93% (target: 87%+) ✅
- **Linting:** 0 errors ✅
- **Code Quality:** 96/100 (Grade A) ✅
- **Mutation Baseline:** 20% (2/11 modules) ⏳
- **E2E Pass Rate:** 85.4% → 96% expected ⏳

---

## 📚 Key Documentation

| Document | Purpose |
|----------|---------|
| `WEEK8_EXECUTION_GUIDE.md` | Complete step-by-step instructions |
| `scripts/week8_validate.sh` | Automated health check |
| `SESSION_SUMMARY_OCT27_WEEK8_CONTINUATION.md` | Session details |
| `INTEGRATED_ROADMAP.md` | Overall project roadmap |
| `NEXT_STEPS_WEEK8.md` | Weekly overview |

---

## ✅ Pre-flight Checklist

### Before E2E Validation
- [ ] GitHub repository access
- [ ] Can navigate to Actions tab
- [ ] 1-2 hours available
- [ ] Browser ready

### Before Mutation Testing
- [ ] Local development machine
- [ ] Python 3.11+ installed
- [ ] Repository cloned locally
- [ ] Tests passing (run `./scripts/week8_validate.sh`)
- [ ] 2-4 hours available per module

---

## 🚨 Quick Troubleshooting

**Tests failing?**
```bash
pytest tests/ -v  # Check which tests fail
```

**Dependencies missing?**
```bash
pip install -r requirements-minimal.txt
```

**Validation fails?**
```bash
./scripts/week8_validate.sh  # See specific failure
```

**Need help?**
```bash
# Read full guide
cat WEEK8_EXECUTION_GUIDE.md | less
```

---

## 📞 Support Files

- **Validation Script:** `scripts/week8_validate.sh`
- **Execution Guide:** `WEEK8_EXECUTION_GUIDE.md`
- **Session Summary:** `SESSION_SUMMARY_OCT27_WEEK8_CONTINUATION.md`
- **E2E Validation:** `E2E_VALIDATION_GUIDE.md`
- **Mutation Docs:** `docs/mutation-testing/`

---

## 🎯 Success Criteria

### Path A Success
- ✅ 115+ tests passing (96%+)
- ✅ Workflow re-enabled on PRs
- ✅ Results documented

### Path B Success
- ✅ All 3 modules tested
- ✅ Mutation scores 85%+
- ✅ Survivors analyzed
- ✅ Improvement plan created

---

**Quick Start:** `./scripts/week8_validate.sh`  
**Full Guide:** `WEEK8_EXECUTION_GUIDE.md`  
**Status:** ✅ READY
