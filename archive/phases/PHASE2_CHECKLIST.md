# ✅ Phase 2 Execution Checklist

**Task:** Mutation Testing Baseline  
**Status:** Infrastructure Complete - Strategy Decision Needed  
**Estimated Time:** 18-50 hours (depending on strategy chosen)

> **📌 STRATEGY DECISION REQUIRED**  
> Before executing this checklist, choose an execution strategy:
> - **Option A (Recommended):** Focused approach - 5 critical modules, 18-24 hours
> - **Option B:** Comprehensive approach - All 11 modules, 35-50 hours  
> - **Option C:** Sampling approach - 2 modules, 7-10 hours
> 
> See [PHASE2_PROGRESS_NOTES.md](PHASE2_PROGRESS_NOTES.md) for detailed analysis and recommendations.

---

## 📋 Pre-Execution Checklist

- [x] mutmut installed (`pip install mutmut`)
- [x] Environment configured (`export PYTHONPATH=...`)
- [x] All tests passing (545/545) ✅
- [x] Linting clean (0 errors) ✅
- [x] Execution scripts created
- [x] Documentation complete
- [x] Initial testing completed (constants.py partial)
- [x] Time estimates validated and updated
- [x] Execution strategy options documented
- [ ] Execution strategy chosen (A, B, or C)
- [ ] Ready to start full Phase 2 execution

---

## 🗓️ Week 1: Baseline Establishment

### Day 1: Setup & Simple Modules (2-3 hours)
**Date:** _________  
**Time:** _________

**Morning: Environment Verification**
- [ ] Clone/pull latest code
- [ ] Install dependencies: `pip install -r requirements-minimal.txt`
- [ ] Verify tests pass: `pytest tests/ -v`
- [ ] Verify linting: `flake8 src/ --max-line-length=100 --ignore=E501,W503,E226`

**Afternoon: Quick Baseline**
- [ ] Run: `./scripts/run_mutation_baseline.sh quick`
- [ ] Duration: _______ minutes
- [ ] constants.py score: _______%
- [ ] config.py score: _______%
- [ ] Notes: _________________________________________________

---

### Day 2: Critical Module 1 - utils.py (3-4 hours)
**Date:** _________  
**Time:** _________

**Execution**
- [ ] Run: `./scripts/run_mutation_baseline.sh utils`
- [ ] Start time: _________
- [ ] End time: _________
- [ ] Duration: _______ hours

**Results**
- [ ] Total mutants: _________
- [ ] Killed: _________
- [ ] Survived: _________
- [ ] Mutation score: _______%

**Analysis**
- [ ] View results: `mutmut results`
- [ ] Generate HTML: `mutmut html`
- [ ] Review surviving mutants: `mutmut show`
- [ ] Document top 10 survivors in notes

**Top Survivors:**
1. Line _____: _________________________________________________
2. Line _____: _________________________________________________
3. Line _____: _________________________________________________

---

### Day 3: Critical Module 2 - security.py (3-4 hours)
**Date:** _________  
**Time:** _________

**Execution**
- [ ] Run: `./scripts/run_mutation_baseline.sh security`
- [ ] Start time: _________
- [ ] End time: _________
- [ ] Duration: _______ hours

**Results**
- [ ] Total mutants: _________
- [ ] Killed: _________
- [ ] Survived: _________
- [ ] Mutation score: _______%

**Security Analysis**
- [ ] Review authentication survivors
- [ ] Check authorization survivors
- [ ] Verify rate limiting tests
- [ ] Document critical gaps

**Critical Survivors:**
1. Line _____: _________________________________________________ [Priority: High/Medium/Low]
2. Line _____: _________________________________________________ [Priority: High/Medium/Low]
3. Line _____: _________________________________________________ [Priority: High/Medium/Low]

---

### Day 4: Core Modules (8-10 hours - Run Overnight)
**Date:** _________  
**Start Time:** _________

**Setup for Overnight Run**
- [ ] Clear disk space
- [ ] Ensure stable power
- [ ] Run: `nohup ./scripts/run_mutation_baseline.sh core > logs/core-modules.log 2>&1 &`
- [ ] Note process ID: _________

**Next Morning: Review Results**
- [ ] Check completion: `tail -50 logs/core-modules.log`
- [ ] cache_manager.py score: _______%
- [ ] monitoring.py score: _______%
- [ ] fasting_manager.py score: _______%

---

### Day 5: Documentation & Analysis
**Date:** _________  
**Time:** _________

**Compile Results**
- [ ] Create summary spreadsheet
- [ ] Calculate overall mutation score: _______%
- [ ] Identify patterns in survivors
- [ ] Categorize survivors (critical/important/acceptable)

**Generate Reports**
- [ ] Generate master HTML report: `mutmut html`
- [ ] Copy to reports/: `cp -r html/ reports/mutation-baseline-$(date +%Y%m%d)/`
- [ ] Create summary document

**Document Baseline**
- [ ] Update MUTATION_TESTING.md with baseline results
- [ ] Create test improvement plan for Phase 5
- [ ] Update REFACTORING_STATUS.md with Phase 2 completion

---

## 🗓️ Week 2: Supporting Modules & Final Analysis

### Days 1-3: Supporting Modules (12-15 hours)
**Dates:** _________ to _________

**Module Execution Plan**

#### nutrition_calculator.py (4-6 hours)
- [ ] Run: `./scripts/run_mutation_baseline.sh nutrition_calculator`
- [ ] Duration: _______ hours
- [ ] Score: _______%
- [ ] Notes: _________________________________________________

#### task_manager.py (3 hours)
- [ ] Run: `./scripts/run_mutation_baseline.sh task_manager`
- [ ] Duration: _______ hours
- [ ] Score: _______%

#### advanced_logging.py (3 hours)
- [ ] Run: `./scripts/run_mutation_baseline.sh advanced_logging`
- [ ] Duration: _______ hours
- [ ] Score: _______%

#### ssl_config.py (2-3 hours)
- [ ] Run: `./scripts/run_mutation_baseline.sh ssl_config`
- [ ] Duration: _______ hours
- [ ] Score: _______%

---

### Days 4-5: Final Analysis & Documentation

**Complete Baseline Summary**
- [ ] All 11 modules tested
- [ ] Overall mutation score: _______%
- [ ] Total mutants: _________
- [ ] Total killed: _________
- [ ] Total survived: _________

**Top Priority Improvements (For Phase 5)**
1. __________________________________________________________________
2. __________________________________________________________________
3. __________________________________________________________________
4. __________________________________________________________________
5. __________________________________________________________________

**Documentation Updates**
- [ ] MUTATION_TESTING.md updated with complete baseline
- [ ] REFACTORING_STATUS.md Phase 2 marked complete
- [ ] PROJECT_ANALYSIS.md updated with mutation scores
- [ ] Test improvement plan created for Phase 5
- [ ] Git commit with results

---

## 📊 Results Summary Table

Fill in as you complete each module:

| Module | Statements | Code Cov | Mutants | Killed | Survived | Timeouts | Score | Notes |
|--------|-----------|----------|---------|--------|----------|----------|-------|-------|
| constants.py | 19 | 100% | | | | | | |
| config.py | 25 | 92% | | | | | | |
| utils.py | 223 | 92% | | | | | | |
| security.py | 224 | 88% | | | | | | |
| cache_manager.py | 172 | 94% | | | | | | |
| monitoring.py | 174 | 90% | | | | | | |
| fasting_manager.py | 203 | 100% | | | | | | |
| nutrition_calculator.py | 416 | 86% | | | | | | |
| task_manager.py | 197 | 92% | | | | | | |
| advanced_logging.py | 189 | 93% | | | | | | |
| ssl_config.py | 138 | 91% | | | | | | |
| **TOTAL** | **1980** | **91%** | | | | | **____%** | |

---

## 🎯 Success Criteria

### Phase 2 Complete When:
- [ ] All 11 modules tested
- [ ] Baseline scores documented (table above filled)
- [ ] Surviving mutants analyzed and categorized
- [ ] Test improvement plan created
- [ ] HTML reports generated and saved
- [ ] MUTATION_TESTING.md updated
- [ ] REFACTORING_STATUS.md updated
- [ ] Phase 3 ready to begin

### Quality Gates:
- [ ] Overall mutation score: 75-80%+ ✅
- [ ] Critical modules: 75%+ ✅
- [ ] No critical security survivors unaddressed ✅
- [ ] Documentation complete ✅

---

## 🔧 Troubleshooting Notes

**Issue Log:**

Issue #1:
- **Date:** _________
- **Module:** _________
- **Problem:** _________________________________________________
- **Solution:** _________________________________________________

Issue #2:
- **Date:** _________
- **Module:** _________
- **Problem:** _________________________________________________
- **Solution:** _________________________________________________

---

## 📝 Additional Notes

**Learnings:**
- _________________________________________________________________
- _________________________________________________________________
- _________________________________________________________________

**Observations:**
- _________________________________________________________________
- _________________________________________________________________
- _________________________________________________________________

**Recommendations for Phase 3+:**
- _________________________________________________________________
- _________________________________________________________________
- _________________________________________________________________

---

## ✅ Final Sign-off

**Phase 2 Completion:**
- **Completed by:** _________________________
- **Date:** _________________________
- **Overall Score:** _______%
- **Status:** ☐ Complete ☐ Incomplete
- **Ready for Phase 3:** ☐ Yes ☐ No

**Signature:** _________________________

---

**Resources:**
- [PHASE2_EXECUTION_GUIDE.md](PHASE2_EXECUTION_GUIDE.md) - Detailed guide
- [MUTATION_TESTING.md](MUTATION_TESTING.md) - Mutation testing documentation
- [MUTATION_TESTING_PLAN.md](MUTATION_TESTING_PLAN.md) - Implementation plan
- `scripts/run_mutation_baseline.sh` - Execution script
