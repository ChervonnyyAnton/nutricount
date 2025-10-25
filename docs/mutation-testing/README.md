# Mutation Testing Documentation

This directory contains all mutation testing related documentation and results for the Nutricount project.

---

## 📁 Directory Structure

```
docs/mutation-testing/
├── README.md                    # This file - overview and navigation
├── BASELINE_RESULTS.md          # Baseline mutation scores for all modules
├── IMPROVEMENT_LOG.md           # Log of test improvements made
└── reviews/                     # Monthly review documents
    └── YYYY-MM.md               # Monthly review (e.g., 2025-11.md)
```

---

## 📚 Documentation Files

### Core Documents (in project root)

#### MUTATION_TESTING_STRATEGY.md ⭐ START HERE
**Purpose:** Comprehensive strategy document defining the mutation testing approach  
**Status:** ✅ Complete  
**Created:** October 25, 2025

**Contents:**
- Goals and objectives
- Module priority matrix
- Phased execution plan
- Scoring interpretation guidelines
- Test improvement patterns
- Risk mitigation strategies

**When to Read:** Before starting mutation testing baseline

#### MUTATION_TESTING_PLAN.md
**Purpose:** Original implementation plan with detailed steps  
**Status:** ✅ Complete  
**Created:** October 20, 2025

**Contents:**
- Executive summary
- Expected baseline results
- Phased implementation plan (Day 1-12)
- Best practices
- Mutation testing metrics

**When to Read:** During baseline execution for detailed steps

#### MUTATION_TESTING.md
**Purpose:** General mutation testing guide and reference  
**Status:** ✅ Complete

**Contents:**
- What is mutation testing
- Setup and configuration
- Running mutation testing
- Understanding results
- Troubleshooting

**When to Read:** When you need to understand mutation testing concepts

---

### Results and Tracking (in this directory)

#### BASELINE_RESULTS.md
**Purpose:** Document baseline mutation scores for all modules  
**Status:** ⏳ Template ready, awaiting execution  
**Updated:** After baseline execution (Week 8)

**Contents:**
- Overall summary (total mutants, killed, survived, score)
- Module-by-module scores
- Critical surviving mutants
- Test improvement actions

**When to Update:** After each mutation testing run

#### IMPROVEMENT_LOG.md
**Purpose:** Track test improvements made in response to surviving mutants  
**Status:** ✅ Ready for use  
**Updated:** Whenever tests are improved

**Contents:**
- Improvement entries (mutant, why it survived, fix made)
- Common patterns
- Statistics by module
- Best practices learned

**When to Update:** Whenever you fix a surviving mutant

#### reviews/YYYY-MM.md
**Purpose:** Monthly mutation testing reviews  
**Status:** ⏳ Will be created monthly  
**Updated:** Monthly (first Monday of each month)

**Contents:**
- Changes since last review
- Score trends
- Action items
- Next review date

**When to Create:** First Monday of each month

---

## 🚀 Quick Start Guide

### For First-Time Baseline Execution

1. **Read Strategy Document**
   ```bash
   cat ../../MUTATION_TESTING_STRATEGY.md
   ```

2. **Follow Phased Plan**
   - Week 8 (Nov 1-8, 2025)
   - Start with constants.py (simplest)
   - Progress through phases 1-4

3. **Document Results**
   - Update BASELINE_RESULTS.md after each module
   - Record scores and surviving mutants

4. **Create Improvement Plan**
   - Analyze surviving mutants
   - Prioritize fixes
   - Log improvements in IMPROVEMENT_LOG.md

### For Monthly Reviews

1. **Run Mutation Tests**
   ```bash
   cd /home/runner/work/nutricount/nutricount
   export PYTHONPATH=$PWD
   mutmut run --paths-to-mutate=src/
   mutmut results
   ```

2. **Create Review Document**
   ```bash
   cp reviews/template.md reviews/2025-11.md
   # Fill in results
   ```

3. **Update Baseline Results**
   - Update scores in BASELINE_RESULTS.md
   - Note any improvements or regressions

4. **Schedule Next Review**
   - Add to calendar
   - Update INTEGRATED_ROADMAP.md

---

## 📊 Current Status

### Project-Wide Status
- **Baseline:** ⏳ Pending (Week 8)
- **Target Score:** 80%+ overall
- **Critical Modules:** 90%+ (security.py, utils.py)
- **Current Score:** _TBD_

### Module Status

| Module | Priority | Target | Status |
|--------|----------|--------|--------|
| constants.py | 🔵 LOW | 90%+ | ⏳ Pending |
| config.py | 🔵 LOW | 85%+ | ⏳ Pending |
| security.py | 🔴 CRITICAL | 90%+ | ⏳ Pending |
| utils.py | 🔴 CRITICAL | 90%+ | ⏳ Pending |
| nutrition_calculator.py | 🟡 HIGH | 85%+ | ⏳ Pending |
| cache_manager.py | 🟡 HIGH | 85%+ | ⏳ Pending |
| fasting_manager.py | 🟡 HIGH | 85%+ | ⏳ Pending |
| monitoring.py | 🟢 MEDIUM | 80%+ | ⏳ Pending |
| task_manager.py | 🟢 MEDIUM | 80%+ | ⏳ Pending |
| advanced_logging.py | 🟢 MEDIUM | 75%+ | ⏳ Pending |
| ssl_config.py | 🟢 MEDIUM | 75%+ | ⏳ Pending |

---

## 🔗 Related Documentation

### In Project Root
- `MUTATION_TESTING_STRATEGY.md` - Comprehensive strategy ⭐
- `MUTATION_TESTING_PLAN.md` - Implementation plan
- `MUTATION_TESTING.md` - General guide
- `INTEGRATED_ROADMAP.md` - Project roadmap (includes mutation testing timeline)
- `PROJECT_ANALYSIS.md` - Project health analysis

### In Tests Directory
- `tests/unit/` - Unit tests (will be improved based on mutation results)
- `tests/integration/` - Integration tests
- `pytest.ini` - pytest configuration
- `conftest.py` - Test fixtures

---

## 📝 Contribution Guidelines

### Adding New Mutation Testing Results

1. **Run Tests**
   ```bash
   mutmut run --paths-to-mutate=src/[module].py
   ```

2. **Document Results**
   - Update BASELINE_RESULTS.md with scores
   - Note surviving mutants
   - Add to IMPROVEMENT_LOG.md if fixing

3. **Commit**
   ```bash
   git add docs/mutation-testing/
   git commit -m "docs: update mutation testing results for [module]"
   ```

### Adding Monthly Reviews

1. **Create Review File**
   ```bash
   cp reviews/template.md reviews/YYYY-MM.md
   ```

2. **Fill in Results**
   - Run mutation tests
   - Compare with previous month
   - Document changes

3. **Update Index**
   - Add link to this README
   - Update INTEGRATED_ROADMAP.md

---

## ❓ FAQ

### When should I run mutation testing?
- **Baseline:** Once during Week 8 (Nov 1-8, 2025)
- **Monthly:** First Monday of each month
- **Ad-hoc:** When adding new features or refactoring

### How long does mutation testing take?
- **Per module:** 30 minutes to 4 hours (varies by module size)
- **Full baseline:** 18-28 hours total (spread over 2 weeks)
- **Monthly reviews:** 2-4 hours (only changed modules)

### What if mutation scores are low?
- **Expected:** First baseline often has lower scores
- **Don't panic:** Focus on improvement trend, not absolute numbers
- **Prioritize:** Fix critical modules first
- **Iterate:** Improve gradually over time

### How do I improve mutation scores?
1. Review surviving mutants in HTML report
2. Identify what tests are missing
3. Add tests following patterns in MUTATION_TESTING_STRATEGY.md
4. Re-run mutation testing to verify
5. Document in IMPROVEMENT_LOG.md

### Can I skip mutation testing?
- **Not recommended:** Mutation testing is valuable for test quality
- **Alternative:** At minimum, run baseline once and document
- **Compromise:** Focus on critical modules only (security, utils)

---

## 📅 Timeline

### Week 7 (Oct 25, 2025) ✅
- [x] Strategy definition (MUTATION_TESTING_STRATEGY.md)
- [x] Documentation structure created
- [x] Templates ready

### Week 8 (Nov 1-8, 2025) ⏳
- [ ] Execute baseline mutation testing
- [ ] Document results
- [ ] Create improvement plan

### Week 9 (Nov 9-15, 2025) ⏳
- [ ] Review baseline results
- [ ] Begin critical improvements
- [ ] Update INTEGRATED_ROADMAP.md

### Monthly (Ongoing) ⏳
- [ ] First Monday: Run mutation tests
- [ ] Document results and trends
- [ ] Identify improvements needed

---

## 🎯 Success Criteria

- [x] Strategy defined ✅
- [x] Documentation structure created ✅
- [ ] Baseline executed ⏳
- [ ] Overall score ≥ 80% ⏳
- [ ] Critical modules ≥ 90% ⏳
- [ ] Monthly reviews established ⏳

---

**Created:** October 25, 2025  
**Last Updated:** October 25, 2025  
**Status:** ✅ Ready for Week 8 execution  
**Next Update:** After baseline execution (Week 8)
