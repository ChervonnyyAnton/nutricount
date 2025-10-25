# Week 8: Mutation Testing Execution Guide
**Created:** October 25, 2025  
**Status:** Ready for Local Execution  
**Estimated Time:** 18-28 hours over 2 weeks

---

## 📋 Overview

This guide provides step-by-step instructions for executing the mutation testing baseline as defined in MUTATION_TESTING_STRATEGY.md. This work is scheduled for **Week 8 (Nov 1-8, 2025)** of the INTEGRATED_ROADMAP.

**IMPORTANT:** Mutation testing should be run **locally** on a developer machine, NOT in CI/CD, due to the time requirements (18-28 hours total).

---

## ⚙️ Prerequisites

### 1. Environment Setup
```bash
cd /path/to/nutricount
export PYTHONPATH=$(pwd)
mkdir -p logs
```

### 2. Install Dependencies
```bash
# If not already installed
pip install -r requirements-minimal.txt

# Verify mutmut is installed
mutmut --help
```

### 3. Verify Tests Pass
```bash
# Make sure all tests pass before starting
pytest tests/ -v

# Expected: 844 passed, 1 skipped
```

---

## 📅 Week 8 Execution Schedule

### Day 1-2: Warm-up Phase (2-3 hours)
**Goal:** Build confidence, understand the process

#### Step 1: constants.py (30-60 minutes)
```bash
mutmut run --paths-to-mutate=src/constants.py
mutmut results
mutmut html
```

**Expected:**
- ~106 mutants generated
- ~90%+ mutation score (constants are simple)
- Most survivors will be acceptable (message strings, emojis)

**Document Results:**
```bash
mutmut results > docs/mutation-testing/constants_results.txt
```

#### Step 2: config.py (1-2 hours)
```bash
mutmut run --paths-to-mutate=src/config.py
mutmut results
mutmut html
```

**Expected:**
- ~20-40 mutants
- 85-90% mutation score
- Some survivors in error handling

**Document Results:**
```bash
mutmut results > docs/mutation-testing/config_results.txt
```

---

### Day 3-4: Critical Module - security.py (3-4 hours)
**Goal:** Ensure security logic is well-tested

```bash
mutmut run --paths-to-mutate=src/security.py
mutmut results
mutmut show
```

**Expected Challenges:**
- JWT token validation edge cases
- Password hashing boundary conditions
- Rate limiting threshold tests

**Target:** 90%+ mutation score

**Review Survivors:**
1. Check each surviving mutant with `mutmut show <id>`
2. Categorize as "acceptable" or "needs test"
3. For "needs test" survivors, add test cases

**Document:**
```bash
mutmut results > docs/mutation-testing/security_results.txt
# Note: Document which survivors are acceptable vs needing fixes
```

---

### Day 4-5: Critical Module - utils.py (2-3 hours)
**Goal:** Ensure utility functions are robust

```bash
mutmut run --paths-to-mutate=src/utils.py
mutmut results
```

**Expected Challenges:**
- Data validation edge cases
- String parsing boundaries
- Numeric conversion errors

**Target:** 90%+ mutation score

---

### Day 6-7: Business Logic - nutrition_calculator.py (3-4 hours)
**Goal:** Ensure calculation accuracy

```bash
mutmut run --paths-to-mutate=src/nutrition_calculator.py
mutmut results
```

**Expected Challenges:**
- Keto index calculation edge cases
- Macro ratio boundaries
- Division by zero scenarios

**Target:** 85%+ mutation score

---

### Day 8: Core Feature - cache_manager.py (2-3 hours)
```bash
mutmut run --paths-to-mutate=src/cache_manager.py
mutmut results
```

**Target:** 85%+ mutation score

---

### Day 9: Core Feature - fasting_manager.py (2-3 hours)
```bash
mutmut run --paths-to-mutate=src/fasting_manager.py
mutmut results
```

**Target:** 85%+ mutation score

---

### Day 10: Monitoring - monitoring.py (2-3 hours)
```bash
mutmut run --paths-to-mutate=src/monitoring.py
mutmut results
```

**Target:** 80%+ mutation score

---

### Day 11: Infrastructure Modules (3-4 hours)
```bash
mutmut run --paths-to-mutate=src/task_manager.py
mutmut results

mutmut run --paths-to-mutate=src/advanced_logging.py
mutmut results

mutmut run --paths-to-mutate=src/ssl_config.py
mutmut results
```

**Target:** 75-80% mutation score each

---

### Day 12: Consolidation (2-3 hours)
1. Generate comprehensive HTML report
2. Document all baseline scores
3. Create improvement roadmap
4. Update INTEGRATED_ROADMAP.md

---

## 📊 Results Documentation

### Create BASELINE_RESULTS.md

```markdown
# Mutation Testing Baseline Results
**Date:** [YYYY-MM-DD]
**mutmut Version:** 2.4.5
**Python Version:** 3.11

## Overall Summary
- **Total Mutants:** [NUMBER]
- **Killed:** [NUMBER] ([PERCENTAGE]%)
- **Survived:** [NUMBER] ([PERCENTAGE]%)
- **Timeouts:** [NUMBER]
- **Suspicious:** [NUMBER]
- **Overall Score:** [PERCENTAGE]%

## Module Scores

| Module | Total | Killed | Survived | Timeout | Score | Status |
|--------|-------|--------|----------|---------|-------|--------|
| constants.py | - | - | - | - | -% | ⏳ Pending |
| config.py | - | - | - | - | -% | ⏳ Pending |
| security.py | - | - | - | - | -% | ⏳ Pending |
| utils.py | - | - | - | - | -% | ⏳ Pending |
| nutrition_calculator.py | - | - | - | - | -% | ⏳ Pending |
| cache_manager.py | - | - | - | - | -% | ⏳ Pending |
| fasting_manager.py | - | - | - | - | -% | ⏳ Pending |
| monitoring.py | - | - | - | - | -% | ⏳ Pending |
| task_manager.py | - | - | - | - | -% | ⏳ Pending |
| advanced_logging.py | - | - | - | - | -% | ⏳ Pending |
| ssl_config.py | - | - | - | - | -% | ⏳ Pending |

## Critical Surviving Mutants

### security.py
- [ ] Mutant #X: [Description]
- [ ] Mutant #Y: [Description]

### utils.py
- [ ] Mutant #X: [Description]
- [ ] Mutant #Y: [Description]

## Next Steps
1. Review surviving mutants
2. Categorize survivors (acceptable vs needs fix)
3. Create improvement plan for low-scoring modules
4. Schedule test improvements
```

---

## 🔧 Troubleshooting

### Issue: Mutation Testing Too Slow
**Problem:** Each mutant takes 30+ seconds to test

**Solution:**
```bash
# Use multiple processes (if you have cores available)
mutmut run --paths-to-mutate=src/module.py --processes=4
```

### Issue: Too Many Mutants
**Problem:** Module has 500+ mutants, taking hours

**Solution:**
- Take breaks between batches
- Run overnight
- Focus on critical functions first

### Issue: All Mutants Survive
**Problem:** 0% mutation score

**Solution:**
- Check if tests are actually running: `pytest tests/ -k "module_name"`
- Verify PYTHONPATH is set correctly
- Check if module is imported in tests

### Issue: Cannot Generate HTML Report
**Problem:** `mutmut html` fails

**Solution:**
```bash
# Make sure you have run mutation tests first
mutmut results

# If cache is corrupted, clear and rerun
rm .mutmut-cache
mutmut run --paths-to-mutate=src/module.py
```

---

## 📝 Best Practices

### 1. Start Small
- Begin with simplest modules (constants, config)
- Build confidence before tackling complex modules

### 2. Take Breaks
- Don't try to complete all in one session
- Each module is independent, can be done separately

### 3. Document as You Go
- Save results after each module
- Note patterns in surviving mutants
- Track time spent per module

### 4. Review Survivors
- Not all survivors indicate test quality issues
- Categorize survivors: acceptable vs needs fix
- Focus on "needs fix" survivors first

### 5. Commit Results
- Commit mutation results to repo
- Update docs/mutation-testing/ with findings
- Share insights with team

---

## ✅ Success Criteria

### Phase 1: Warm-up Complete
- [ ] constants.py baseline documented
- [ ] config.py baseline documented
- [ ] Comfortable with mutmut workflow
- [ ] First HTML report generated

### Phase 2: Critical Modules Complete
- [ ] security.py baseline documented (target: 90%+)
- [ ] utils.py baseline documented (target: 90%+)
- [ ] Surviving mutants categorized
- [ ] Improvement plan drafted

### Phase 3: All Modules Complete
- [ ] All 11 modules have baseline scores
- [ ] At least 7 modules meet target scores
- [ ] Comprehensive HTML report generated
- [ ] BASELINE_RESULTS.md created

### Phase 4: Documentation Updated
- [ ] INTEGRATED_ROADMAP.md updated
- [ ] Results committed to repo
- [ ] Team notified of findings
- [ ] First improvement tasks created

---

## 🔗 Related Documentation

- **MUTATION_TESTING_STRATEGY.md** - Overall strategy and targets
- **MUTATION_TESTING.md** - Comprehensive mutation testing guide
- **INTEGRATED_ROADMAP.md** - Project roadmap
- **PROJECT_ANALYSIS.md** - Current project health

---

## 📞 Getting Help

If you encounter issues:
1. Check troubleshooting section above
2. Review MUTATION_TESTING_STRATEGY.md for context
3. Check mutmut documentation: https://mutmut.readthedocs.io/
4. Ask team for help (don't struggle alone!)

---

**Remember:** Mutation testing is a marathon, not a sprint. Take your time, document thoroughly, and focus on learning and improving test quality.

**Good luck with Week 8 execution!** 🎉
