# 👥 User Personas

## Overview

This document defines the primary user personas for Nutricount, helping Product Owners, Designers, and Developers understand our users' needs, goals, and pain points.

---

## 🎯 Persona Framework

Each persona includes:
- **Demographics:** Age, occupation, location
- **Goals:** What they want to achieve
- **Motivations:** Why they use Nutricount
- **Pain Points:** Challenges they face
- **Tech Savviness:** Comfort level with technology
- **Devices:** Primary devices used
- **Key Features:** Most valued features
- **User Journey:** Typical usage pattern

---

## 👤 Persona 1: Sarah - Keto Enthusiast

### Demographics
- **Age:** 32
- **Occupation:** Marketing Manager
- **Location:** Austin, TX
- **Education:** Bachelor's Degree
- **Income:** $75,000/year
- **Family:** Single, no children

### Photo/Avatar
```
👩‍💼 Professional woman, active lifestyle, health-conscious
```

### Quote
> "I want to lose weight and feel energized, but I need to make sure I stay in ketosis without obsessing over every meal."

### Goals
1. Lose 15 pounds in 3 months
2. Maintain ketosis consistently (GKI < 6)
3. Track macros without spending too much time
4. Find keto-friendly recipes and foods

### Motivations
- Health and fitness improvement
- Looking good for upcoming events
- Increased energy and mental clarity
- Following keto community trends

### Pain Points
- Calculating net carbs is confusing
- Hard to know if foods are keto-friendly
- Time-consuming to track everything
- Uncertain if she's in ketosis
- Limited keto-friendly restaurant options

### Tech Savviness
**Medium** (3/5)
- Comfortable with mobile apps
- Uses social media regularly
- Prefers intuitive interfaces
- Not interested in technical details

### Devices
- **Primary:** iPhone 13 Pro
- **Secondary:** iPad Air, MacBook Pro
- **Usage:** 70% mobile, 30% desktop

### Key Features Used
1. ✅ Keto index for products (most important)
2. ✅ Quick product logging
3. ✅ Daily macro tracking
4. ✅ Net carbs calculation
5. ⭐ Recipe suggestions (desired)
6. ⭐ Restaurant meal database (desired)

### User Journey

**Morning (7 AM):**
- Opens app on iPhone
- Logs breakfast (eggs, bacon, avocado)
- Checks keto index (95 - excellent!)
- Views daily macros progress

**Lunch (12 PM):**
- Searches for "chicken salad"
- Finds saved dish
- Logs with custom portion size
- Checks if still in keto range

**Evening (6 PM):**
- Plans dinner to hit macro targets
- Uses dish builder for new recipe
- Logs meal and snacks
- Reviews daily summary

**Night (10 PM):**
- Checks weekly trends
- Compares to previous weeks
- Adjusts tomorrow's meals

### Frustrations with Other Apps
- MyFitnessPal: Too many non-keto features
- Carb Manager: Expensive subscription
- Generic trackers: No keto-specific calculations

### Why Nutricount Works for Sarah
- ✅ Clear keto index on every food
- ✅ Fast, mobile-first interface
- ✅ Free and privacy-focused
- ✅ Beautiful, modern design
- ✅ Works offline (PWA)

---

## 👨‍💻 Persona 2: Mike - Health Optimizer

### Demographics
- **Age:** 45
- **Occupation:** Software Developer
- **Location:** San Francisco, CA
- **Education:** Master's in Computer Science
- **Income:** $140,000/year
- **Family:** Married, two children

### Photo/Avatar
```
👨‍💻 Tech professional, data-driven, biohacker
```

### Quote
> "I want complete control over my health data and the ability to analyze every metric without privacy concerns."

### Goals
1. Optimize GKI to therapeutic levels (<3)
2. Self-host all health data
3. Track correlations (food → blood metrics)
4. Export data for custom analysis
5. Maintain privacy (no cloud tracking)

### Motivations
- Health optimization and longevity
- Data privacy and ownership
- Scientific approach to health
- Learning and self-experimentation
- Building personal health dashboard

### Pain Points
- Commercial apps sell user data
- Limited export/analysis options
- Can't self-host or customize
- Vendor lock-in concerns
- Need API access for integrations

### Tech Savviness
**Very High** (5/5)
- Runs own servers (Docker, Linux)
- Comfortable with APIs and databases
- Writes custom scripts and tools
- Values open source software

### Devices
- **Primary:** Linux laptop (Arch, i3wm)
- **Secondary:** Android phone (LineageOS)
- **Self-Hosted:** Raspberry Pi 4, NAS

### Key Features Used
1. ✅ Self-hosted deployment (critical)
2. ✅ Complete data export (JSON)
3. ✅ GKI tracking
4. ✅ API access for automation
5. ✅ No telemetry or tracking
6. ⭐ Custom integrations (desired)
7. ⭐ Advanced analytics (desired)

### User Journey

**Morning (6 AM):**
- Blood glucose test: 85 mg/dL
- Ketone test: 2.1 mmol/L
- Logs in self-hosted Nutricount
- GKI calculated: 2.2 (therapeutic!)
- Exports data to personal dashboard

**Throughout Day:**
- Automated logging via API
- Scripts auto-calculate macros
- Receives alerts for GKI changes
- Tracks trends in Grafana

**Evening:**
- Reviews correlation analysis
- Food → blood glucose patterns
- Adjusts diet based on data
- Backs up database to NAS

**Weekly:**
- Exports CSV for R analysis
- Creates custom visualizations
- Shares findings in r/ketoscience
- Contributes code improvements

### Frustrations with Other Apps
- Cronometer: Can't self-host
- MyFitnessPal: Sells data, ads
- Most apps: Closed source, no API
- Mobile-only: Need desktop access

### Why Nutricount Works for Mike
- ✅ 100% open source (can audit code)
- ✅ Self-hostable (Docker + Pi 4)
- ✅ Complete data ownership
- ✅ API for automation
- ✅ No tracking or telemetry
- ✅ Active development (can contribute)

---

## 👩‍⚕️ Persona 3: Emma - Intermittent Faster

### Demographics
- **Age:** 28
- **Occupation:** Registered Nurse
- **Location:** Seattle, WA
- **Education:** BSN (Nursing)
- **Income:** $68,000/year
- **Family:** Single, cat owner

### Photo/Avatar
```
👩‍⚕️ Healthcare professional, busy schedule, wellness-focused
```

### Quote
> "I need a simple way to track my fasting that reminds me when to eat and shows my progress over time."

### Goals
1. Practice 16:8 intermittent fasting consistently
2. Lose 10 pounds gradually (health, not vanity)
3. Improve energy during 12-hour nursing shifts
4. Build a fasting habit (30-day streak)

### Motivations
- Health benefits (autophagy, longevity)
- Better energy and focus at work
- Weight management without dieting
- Scientific evidence for fasting
- Community support and accountability

### Pain Points
- Irregular work schedule (day/night shifts)
- Forgets fasting start/end times
- Hard to track progress over time
- Needs motivation on hard days
- Wants notifications but not spam

### Tech Savviness
**Low-Medium** (2/5)
- Basic smartphone use
- Prefers simple, clear interfaces
- Not interested in complex features
- Values reliability over features

### Devices
- **Primary:** iPhone 12
- **Usage:** 95% mobile, 5% iPad

### Key Features Used
1. ✅ One-tap fasting start/stop (critical)
2. ✅ Timer with notifications
3. ✅ Fasting type presets (16:8, 18:6)
4. ✅ Streak tracking
5. ✅ Simple statistics
6. ⭐ Motivational quotes (desired)
7. ⭐ Community challenges (desired)

### User Journey

**Evening Shift (6 PM):**
- Last meal at 6 PM
- Opens Nutricount
- Taps "Start 16:8 Fasting"
- Timer begins

**Night (10 PM):**
- Working night shift
- Notification: "Halfway through fast!"
- Feels motivated to continue

**Morning (8 AM):**
- End of shift
- Notification: "Fast complete! 14 hours"
- Feels accomplished
- Decides to extend to 16 hours

**Day (10 AM):**
- "End Fasting" button
- Logs completion (16 hours)
- Streak: 7 days! 🎉
- Views weekly statistics

**Weekly Review:**
- Average fasting: 15.5 hours
- Completion rate: 6/7 days
- Longest fast: 18 hours
- Feeling: More energized!

### Frustrations with Other Apps
- Zero: Too complex, many features
- Life Fasting: Confusing UI
- Most apps: Require account creation
- Some apps: Constant notifications

### Why Nutricount Works for Emma
- ✅ Dead simple interface
- ✅ Works offline (hospital WiFi is bad)
- ✅ Smart notifications (not annoying)
- ✅ Visual progress tracking
- ✅ No account required (browser-only)
- ✅ Free forever

---

## 👨‍🎓 Persona 4: Alex - Developer Learner

### Demographics
- **Age:** 24
- **Occupation:** Junior Developer
- **Location:** Remote (originally from Poland)
- **Education:** Self-taught (bootcamp)
- **Income:** $55,000/year
- **Family:** Single, living with roommates

### Photo/Avatar
```
👨‍🎓 Young developer, eager to learn, portfolio builder
```

### Quote
> "I want to learn modern web development by studying a real, production-quality codebase with excellent tests and documentation."

### Goals
1. Learn full-stack development (Flask + JavaScript)
2. Understand TDD and testing best practices
3. Study design patterns in real code
4. Build portfolio project based on Nutricount
5. Contribute to open source

### Motivations
- Career advancement to mid-level
- Portfolio building for job interviews
- Learning by doing (not tutorials)
- Community contribution
- Skill development (testing, architecture)

### Pain Points
- Tutorials are too simple (to-do apps)
- Production code is often messy
- Hard to find well-documented projects
- Need examples of testing patterns
- Unclear how to contribute to OSS

### Tech Savviness
**Medium-High** (4/5)
- Comfortable with Git, GitHub
- Knows Python and JavaScript basics
- Learning Docker, CI/CD
- Wants to understand advanced patterns

### Devices
- **Primary:** Windows laptop (WSL2)
- **Learning:** Linux VPS for deployment

### Key Features Used
1. ✅ Well-documented code (critical)
2. ✅ Comprehensive test suite (critical)
3. ✅ Design pattern examples
4. ✅ CI/CD pipeline as learning tool
5. ✅ Contribution guidelines
6. ⭐ Video tutorials (desired)
7. ⭐ Interactive learning modules (desired)

### User Journey

**Week 1: Discovery**
- Finds Nutricount on GitHub
- Reads README and documentation
- Impressed by test coverage (94%!)
- Clones repository

**Week 2: Setup & Exploration**
- Follows PROJECT_SETUP.md
- Runs local development server
- Explores codebase structure
- Runs test suite (all passing!)

**Week 3: Learning**
- Studies Repository pattern
- Reads Service layer code
- Understands separation of concerns
- Writes first test

**Week 4: Contributing**
- Fixes a "good first issue"
- Writes tests for new feature
- Submits pull request
- Gets code review feedback
- Improves and merges PR

**Month 2: Deep Dive**
- Studies design patterns guide
- Implements own feature
- Learns E2E testing with Playwright
- Improves documentation

**Month 3: Portfolio**
- Forks Nutricount
- Builds custom version
- Adds to portfolio
- References in job applications
- Gets mid-level position!

### Frustrations with Other Projects
- Most OSS: Poor documentation
- Many repos: No tests or few tests
- Beginner projects: Too simple
- Enterprise code: Too complex, proprietary

### Why Nutricount Works for Alex
- ✅ Production-quality code
- ✅ 94% test coverage with examples
- ✅ Clear documentation for all roles
- ✅ Design patterns explained
- ✅ Welcoming to contributors
- ✅ Active development and support
- ✅ Real-world complexity, learnable

---

## 📊 Persona Comparison Matrix

| Attribute | Sarah | Mike | Emma | Alex |
|-----------|-------|------|------|------|
| **Tech Level** | Medium | Very High | Low-Med | Med-High |
| **Primary Device** | iPhone | Linux | iPhone | Windows |
| **Top Feature** | Keto Index | Self-Host | Fasting | Tests |
| **Motivation** | Weight Loss | Privacy | Health | Learning |
| **Usage Time** | 5 min/day | 30 min/day | 2 min/day | 2 hours/day |
| **Payment** | Free | Self-host | Free | Contribute |
| **Privacy Concern** | Medium | Very High | Low | Medium |

---

## 🎯 Design Implications

### For Sarah (Keto Enthusiast)
- **Mobile-first design:** Large touch targets
- **Quick actions:** One-tap logging
- **Visual indicators:** Color-coded keto index
- **Minimal complexity:** Hide advanced features
- **Social proof:** Success stories, community

### For Mike (Health Optimizer)
- **Data export:** JSON, CSV formats
- **API documentation:** Complete endpoint docs
- **Self-hosting guides:** Docker, deployment
- **Privacy transparency:** No tracking statement
- **Extensibility:** Plugin system, webhooks

### For Emma (Intermittent Faster)
- **Simple interface:** Big buttons, clear labels
- **Smart notifications:** Timely, not annoying
- **Progress visualization:** Streaks, achievements
- **Offline support:** PWA functionality
- **Reliability:** Never lose data

### For Alex (Developer Learner)
- **Code quality:** Linting, formatting, tests
- **Documentation:** Comprehensive guides
- **Patterns:** Real-world examples
- **Contribution:** Clear process, welcoming
- **Learning resources:** Tutorials, videos

---

## 📈 Usage Scenarios

### Scenario 1: Morning Routine (Sarah)
```
1. Wake up → Weigh self
2. Open Nutricount on phone
3. Log breakfast (saved dish)
4. Check keto index (still good!)
5. Close app (30 seconds total)
```

### Scenario 2: Data Export (Mike)
```
1. SSH into Raspberry Pi
2. Run backup script
3. Export data as JSON
4. Import to R for analysis
5. Visualize trends in custom dashboard
```

### Scenario 3: Night Shift (Emma)
```
1. End dinner at 6 PM
2. Start 16:8 fast
3. Receive notification at midnight
4. Continue fast through shift
5. End fast at 10 AM
6. Log completion, view streak
```

### Scenario 4: Learning Session (Alex)
```
1. Read design patterns guide
2. Study Repository pattern code
3. Run test suite to understand
4. Write own test following examples
5. Commit and create PR
```

---

## 🔄 Persona Evolution

### Sarah → Advanced User (6 months)
- Creates custom keto recipes
- Shares with keto community
- Tracks additional biomarkers (GKI)
- Becomes advocate for Nutricount

### Mike → Contributor (3 months)
- Submits bug fixes
- Adds new features (integrations)
- Mentors new developers
- Maintains fork with custom features

### Emma → Habit Master (2 months)
- 60-day fasting streak
- Experiments with 18:6, OMAD
- Tracks additional health metrics
- Recommends to nurse colleagues

### Alex → Mid-Level Dev (6 months)
- Learned TDD thoroughly
- Understands design patterns
- Got new job (references Nutricount)
- Continues contributing

---

## 📖 Resources

### Internal Documentation
- [User Stories Guide](user-stories.md)
- [Product Backlog](product-backlog.md)
- [Quick Start Guide](../users/quick-start.md)
- [Architecture](../../ARCHITECTURE.md)

### Research Methods
- User interviews (qualitative)
- Analytics data (quantitative)
- Community feedback (Reddit, GitHub)
- Competitor analysis
- Academic research (keto, fasting)

---

**Last Updated:** October 22, 2025  
**Version:** 1.0  
**Status:** ✅ Complete
