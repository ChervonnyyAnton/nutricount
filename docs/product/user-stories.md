# 📝 User Stories Guide for Product Owners

## Overview

This guide helps Product Owners write effective user stories for Nutricount, a privacy-focused nutrition and keto tracking application. It includes templates, examples, and best practices aligned with our dual mission: educational platform and FOSS health tracker.

---

## 🎯 Understanding Nutricount's Value Proposition

**For End Users:**
- Track nutrition with privacy (browser-only or self-hosted)
- Follow ketogenic diet with keto index calculation
- Practice intermittent fasting with session tracking
- Monitor health metrics (GKI, blood glucose, ketones)
- Accessible on mobile, tablet, and desktop

**For Developers/Learners:**
- Learn modern web development patterns
- Study full-stack architecture (Flask + Vanilla JS)
- Understand test-driven development
- Practice CI/CD and DevOps
- Explore design patterns in real project

---

## 📋 User Story Template

```
As a [user type/persona],
I want to [action/feature],
So that [benefit/value].

Acceptance Criteria:
- [ ] [Specific, measurable criterion 1]
- [ ] [Specific, measurable criterion 2]
- [ ] [Specific, measurable criterion 3]

Definition of Done:
- [ ] Code implemented and reviewed
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] User tested and accepted
```

---

## 👥 User Personas

### 1. Sarah - Keto Enthusiast
- **Age:** 32, Marketing Manager
- **Goal:** Maintain ketosis, lose 15 lbs
- **Tech Savvy:** Medium
- **Devices:** iPhone, iPad, MacBook
- **Pain Points:** Tracking net carbs, staying in ketosis
- **Needs:** Quick logging, keto index, mobile access

### 2. Mike - Health Optimizer
- **Age:** 45, Software Developer
- **Goal:** Optimize health metrics (GKI, fasting)
- **Tech Savvy:** High
- **Devices:** Android, Linux laptop
- **Pain Points:** Data privacy, flexibility
- **Needs:** Self-hosting, data export, API access

### 3. Emma - Intermittent Faster
- **Age:** 28, Nurse
- **Goal:** Practice 16:8 fasting, improve energy
- **Tech Savvy:** Low-Medium
- **Devices:** iPhone
- **Pain Points:** Remembering fasting times, tracking progress
- **Needs:** Simple interface, notifications, statistics

### 4. Alex - Developer Learner
- **Age:** 24, Junior Developer
- **Goal:** Learn full-stack development
- **Tech Savvy:** Medium-High
- **Devices:** Windows laptop, WSL
- **Pain Points:** Finding real-world projects to learn from
- **Needs:** Well-documented code, tests, patterns

---

## 📚 User Story Examples

### Epic 1: Nutrition Tracking

#### Story 1.1: Quick Product Entry
```
As a keto enthusiast (Sarah),
I want to quickly add food products with nutrition info,
So that I can track my daily intake without spending too much time.

Acceptance Criteria:
- [ ] Product form has all nutrition fields (calories, protein, fat, carbs, fiber)
- [ ] Keto index is automatically calculated from macros
- [ ] Products are saved to browser/database immediately
- [ ] Product list updates in real-time after adding
- [ ] Validation prevents invalid nutrition values (negatives, non-numbers)
- [ ] Mobile-friendly input with proper keyboard types (numeric)

Definition of Done:
- [ ] ProductService.createProduct() implemented with validation
- [ ] Unit tests cover validation edge cases
- [ ] Integration tests verify API endpoint
- [ ] Mobile responsive design tested on iOS/Android
- [ ] Documentation updated in user guide
- [ ] Deployed to staging and tested
```

#### Story 1.2: Daily Log Entry
```
As a health optimizer (Mike),
I want to log what I eat throughout the day,
So that I can see my total nutrition and stay on track.

Acceptance Criteria:
- [ ] Can select from existing products or dishes
- [ ] Can specify portion size (grams)
- [ ] Can choose meal time (breakfast, lunch, dinner, snack)
- [ ] Daily totals update automatically
- [ ] Can see progress towards daily goals
- [ ] Can edit or delete log entries

Definition of Done:
- [ ] LogService implemented with CRUD operations
- [ ] Real-time calculation of daily totals
- [ ] Tests verify calculation accuracy
- [ ] UI shows visual progress bars
- [ ] Works offline (PWA)
- [ ] Documented in quick start guide
```

### Epic 2: Ketogenic Diet Support

#### Story 2.1: Keto Index Display
```
As a keto enthusiast (Sarah),
I want to see the keto index for each product,
So that I know which foods keep me in ketosis.

Acceptance Criteria:
- [ ] Keto index calculated as: (fat / (protein + carbs)) * 100
- [ ] Color-coded indicators:
  - Green (90-100): Excellent for keto
  - Yellow (70-89): Good for keto
  - Orange (50-69): Moderate
  - Red (<50): Not keto-friendly
- [ ] Displayed on product cards and detail views
- [ ] Helps prioritize keto-friendly foods
- [ ] Net carbs calculated (total carbs - fiber)

Definition of Done:
- [ ] nutrition-calculator.js has calculateKetoIndex()
- [ ] Unit tests verify calculation accuracy
- [ ] Color coding matches design system
- [ ] Documented with formula explanation
- [ ] Works in both Local and Public versions
```

#### Story 2.2: GKI Tracking
```
As a health optimizer (Mike),
I want to track my Glucose Ketone Index (GKI),
So that I can monitor my metabolic state.

Acceptance Criteria:
- [ ] Can input blood glucose (mg/dL) and ketones (mmol/L)
- [ ] GKI calculated as: glucose (mg/dL) / 18 / ketones (mmol/L)
- [ ] Historical GKI data displayed as chart
- [ ] Zones indicated: Therapeutic (<3), Weight Loss (3-6), Maintenance (6-9), Not in ketosis (>9)
- [ ] Can set GKI goals and track progress

Definition of Done:
- [ ] GKI calculation implemented and tested
- [ ] Chart.js integration for visualization
- [ ] Tests verify formula accuracy
- [ ] Mobile-responsive chart
- [ ] User documentation includes GKI guide
```

### Epic 3: Intermittent Fasting

#### Story 3.1: Start Fasting Session
```
As an intermittent faster (Emma),
I want to start a fasting session with one tap,
So that I can easily track my fasting time.

Acceptance Criteria:
- [ ] One-tap "Start Fasting" button
- [ ] Can select fasting type (16:8, 18:6, 20:4, OMAD, Custom)
- [ ] Timer starts immediately
- [ ] Can add optional notes
- [ ] Notification when target time reached
- [ ] Can pause/resume session if needed

Definition of Done:
- [ ] FastingManager.startSession() implemented
- [ ] Unit tests cover all fasting types
- [ ] Integration tests verify API
- [ ] Timer updates every minute
- [ ] Notifications work on mobile (PWA)
- [ ] Documented in fasting guide
```

#### Story 3.2: Fasting Statistics
```
As an intermittent faster (Emma),
I want to see my fasting statistics and streaks,
So that I can stay motivated and track progress.

Acceptance Criteria:
- [ ] Total sessions completed
- [ ] Average fasting duration
- [ ] Longest fasting session
- [ ] Current streak (consecutive days)
- [ ] Weekly/monthly completion rate
- [ ] Visual charts showing trends

Definition of Done:
- [ ] FastingManager.getStatistics() implemented
- [ ] Tests verify calculation accuracy
- [ ] Charts display historical data
- [ ] Mobile-optimized statistics view
- [ ]励志 badges/achievements (optional)
```

### Epic 4: Privacy & Data Control

#### Story 4.1: Browser-Only Mode
```
As a privacy-conscious user (Mike),
I want to use Nutricount without any server,
So that my health data stays 100% private on my device.

Acceptance Criteria:
- [ ] Public version uses only localStorage
- [ ] No network requests (except initial load)
- [ ] All calculations done client-side
- [ ] Works offline after first visit
- [ ] Can export data as JSON
- [ ] Can import data from JSON

Definition of Done:
- [ ] StorageAdapter fully implements offline storage
- [ ] PWA manifest configured
- [ ] Service Worker caches all assets
- [ ] Tests verify no server calls
- [ ] Privacy messaging clear in UI
- [ ] Documented in privacy guide
```

#### Story 4.2: Data Export/Import
```
As a health optimizer (Mike),
I want to export my data at any time,
So that I can backup or migrate to another device.

Acceptance Criteria:
- [ ] Export all data as JSON file
- [ ] Export includes products, dishes, log, fasting sessions
- [ ] Import validates JSON structure
- [ ] Import offers merge or replace options
- [ ] Export filename includes date
- [ ] Works in both Local and Public versions

Definition of Done:
- [ ] Export/import functions implemented
- [ ] Tests verify data integrity
- [ ] UI has clear export/import buttons
- [ ] Error handling for invalid imports
- [ ] Documented in user guide
```

### Epic 5: Developer Learning Experience

#### Story 5.1: Well-Documented Code
```
As a developer learner (Alex),
I want to read clear code comments and documentation,
So that I can understand how the system works.

Acceptance Criteria:
- [ ] All modules have JSDoc/docstring comments
- [ ] Complex algorithms explained with comments
- [ ] README.md has setup instructions
- [ ] Architecture documented with diagrams
- [ ] API endpoints documented
- [ ] Design patterns explained

Definition of Done:
- [ ] 100% of public functions documented
- [ ] ARCHITECTURE.md updated
- [ ] API documentation complete
- [ ] Code examples in documentation
- [ ] Reviewed by developer community
```

#### Story 5.2: Comprehensive Tests
```
As a developer learner (Alex),
I want to see comprehensive test suites,
So that I can learn TDD best practices.

Acceptance Criteria:
- [ ] >90% backend test coverage
- [ ] >80% frontend test coverage
- [ ] Unit, integration, and E2E tests
- [ ] Tests follow AAA pattern
- [ ] Clear test naming conventions
- [ ] Test documentation explains patterns

Definition of Done:
- [ ] Coverage targets met
- [ ] All tests passing
- [ ] tests/README.md explains testing strategy
- [ ] Examples of mocking, fixtures, parametrization
- [ ] CI/CD runs all tests automatically
```

---

## 🎯 INVEST Criteria

Good user stories are **INVEST**:

### Independent
✅ Stories can be developed in any order
❌ Avoid dependencies between stories in same sprint

### Negotiable
✅ Details can be discussed during development
❌ Not a rigid contract, allows collaboration

### Valuable
✅ Delivers value to end users or learners
❌ Not just technical tasks

### Estimable
✅ Team can estimate effort (S/M/L or story points)
❌ If not estimable, split or research more

### Small
✅ Can be completed in 1-3 days
❌ Epics should be broken into smaller stories

### Testable
✅ Clear acceptance criteria
❌ Vague success measures

---

## 📊 Story Sizing Guide

### XS (1 point) - 2-4 hours
- Simple UI text change
- Add validation to existing field
- Minor bug fix

### S (2 points) - 4-8 hours
- New form field with validation
- Simple CRUD endpoint
- Basic unit tests

### M (3 points) - 1-2 days
- New API endpoint with tests
- New page with components
- Integration test suite

### L (5 points) - 2-3 days
- Complex feature with multiple endpoints
- Major UI refactoring
- E2E test coverage

### XL (8 points) - 3-5 days
- Epic-level work (should be split)
- Major architectural change
- New system integration

---

## 🏃 Story Lifecycle

```
Backlog → Ready → In Progress → In Review → Testing → Done
```

### Backlog
- Story written and prioritized
- Not yet ready for development
- May need refinement

### Ready
- Acceptance criteria defined
- Design mockups available (if UI)
- Technical approach discussed
- Dependencies identified

### In Progress
- Developer assigned
- Code being written
- Tests being created

### In Review
- Pull request created
- Code review in progress
- CI/CD checks running

### Testing
- Deployed to staging
- QA testing
- User acceptance testing

### Done
- All acceptance criteria met
- All DoD items checked
- Deployed to production
- Documented

---

## 🛠️ Tools & Templates

### Story Template (Markdown)
```markdown
## [STORY-123] Title

**As a** [persona],
**I want** [action],
**So that** [benefit].

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### Definition of Done
- [ ] Code implemented
- [ ] Tests written (>90%)
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] User tested

### Technical Notes
[Optional implementation details]

### Design Mockups
[Links to Figma/screenshots]

### Related Stories
- Depends on: [STORY-122]
- Blocks: [STORY-124]
```

---

## 📖 Resources

### Internal Documentation
- [User Quick Start Guide](../users/quick-start.md)
- [Architecture Overview](../../ARCHITECTURE.md)
- [Testing Strategy](../qa/testing-strategy.md)
- [CI/CD Pipeline](../devops/ci-cd-pipeline.md)

### External Resources
- [User Story Mapping (Jeff Patton)](https://www.jpattonassociates.com/user-story-mapping/)
- [INVEST Criteria](https://en.wikipedia.org/wiki/INVEST_(mnemonic))
- [Agile Alliance - User Stories](https://www.agilealliance.org/glossary/user-stories/)

---

**Last Updated:** October 22, 2025  
**Version:** 1.0  
**Status:** ✅ Complete
