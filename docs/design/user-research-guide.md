# 🔍 User Research Guide

**Status:** ✅ Week 6 Complete  
**Target Audience:** UX/UI Designers, Product Managers, Product Owners  
**Last Updated:** October 23, 2025

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [User Research Fundamentals](#user-research-fundamentals)
3. [Research Methodologies](#research-methodologies)
4. [Persona Development](#persona-development)
5. [User Interviews](#user-interviews)
6. [Usability Testing](#usability-testing)
7. [A/B Testing](#ab-testing)
8. [Analytics & Metrics](#analytics--metrics)
9. [Tools & Resources](#tools--resources)
10. [Research Process](#research-process)
11. [Best Practices](#best-practices)

---

## 🎯 Introduction

User research is the foundation of user-centered design. It helps us understand our users' needs, behaviors, motivations, and pain points to build products that truly serve them.

### Why User Research Matters

- **Reduces Risk:** Validates assumptions before investing in development
- **Saves Time & Money:** Identifies issues early when they're cheaper to fix
- **Improves User Satisfaction:** Creates products that users actually want and need
- **Drives Business Value:** Aligns product features with user needs and business goals
- **Informs Design Decisions:** Provides data-driven insights for better decision-making

### Our User Research Philosophy

At Nutricount, we believe in:
- **Continuous Research:** Research is ongoing, not a one-time event
- **Inclusive Design:** Research with diverse user groups
- **Data-Driven Decisions:** Base design choices on evidence, not opinions
- **User Empowerment:** Give users a voice in the product development process
- **Privacy First:** Respect user privacy and data protection

---

## 📚 User Research Fundamentals

### Types of Research

#### 1. Exploratory Research
**Purpose:** Understand the problem space  
**When:** Early stages, before defining requirements  
**Methods:** User interviews, field studies, diary studies  
**Output:** Problem statements, opportunity areas

#### 2. Generative Research
**Purpose:** Generate ideas and solutions  
**When:** During ideation phase  
**Methods:** Design workshops, card sorting, co-creation sessions  
**Output:** Design concepts, feature ideas

#### 3. Evaluative Research
**Purpose:** Test and validate designs  
**When:** During and after design phase  
**Methods:** Usability testing, A/B testing, surveys  
**Output:** Usability issues, performance metrics

### Quantitative vs. Qualitative Research

#### Quantitative Research
- **What it measures:** Numbers, patterns, trends
- **Methods:** Surveys, analytics, A/B tests
- **Strengths:** Large sample sizes, statistical significance
- **Weaknesses:** Doesn't explain "why"
- **Example:** "80% of users complete the onboarding flow"

#### Qualitative Research
- **What it measures:** Behaviors, motivations, attitudes
- **Methods:** Interviews, observations, usability tests
- **Strengths:** Deep insights, context, understanding "why"
- **Weaknesses:** Smaller sample sizes, harder to generalize
- **Example:** "Users struggle with onboarding because terminology is unclear"

### Research Questions Framework

Good research questions are:
- **Specific:** Focus on a particular aspect
- **Actionable:** Can inform design decisions
- **Measurable:** Can be answered with data
- **Relevant:** Align with business and user goals

**Example Research Questions for Nutricount:**
- How do users currently track their nutrition?
- What motivates users to start and maintain a keto diet?
- What are the biggest challenges in meal planning?
- How do users decide what to eat on a keto diet?
- What information do users need to feel confident about their food choices?

---

## 🔬 Research Methodologies

### 1. User Interviews

**Purpose:** Understand user needs, behaviors, and pain points  
**When:** Early stages, exploratory research  
**Duration:** 30-60 minutes per interview  
**Sample Size:** 5-8 users per user group

#### Interview Structure

1. **Introduction (5 minutes)**
   - Build rapport
   - Explain purpose
   - Get consent
   - Set expectations

2. **Warm-up (5 minutes)**
   - Easy, open-ended questions
   - Build comfort
   - Establish context

3. **Main Questions (40 minutes)**
   - Focus on behaviors, not opinions
   - Ask "why" and "how"
   - Use follow-up probes
   - Listen actively

4. **Wrap-up (10 minutes)**
   - Final thoughts
   - Anything missed?
   - Thank participant
   - Next steps

#### Interview Question Types

**Good Questions:**
- "Walk me through your typical day of meal planning."
- "Tell me about the last time you tracked your nutrition."
- "What challenges do you face when trying to eat healthy?"
- "How do you decide what to eat for dinner?"

**Avoid:**
- Leading questions: "Don't you think tracking is useful?"
- Closed questions: "Do you track your food?"
- Hypothetical questions: "Would you use feature X?"
- Multiple questions at once

#### Interview Best Practices

✅ **Do:**
- Record (with permission) for later review
- Take notes on key quotes and observations
- Ask open-ended questions
- Listen more than you talk (80/20 rule)
- Be curious and empathetic
- Follow interesting threads
- Stay neutral and non-judgmental

❌ **Don't:**
- Lead the participant
- Interrupt
- Fill every silence
- Pitch your product
- Ask about features ("Would you like X?")
- Make assumptions

### 2. Usability Testing

**Purpose:** Identify usability issues and validate design decisions  
**When:** During and after design phase  
**Duration:** 30-60 minutes per session  
**Sample Size:** 5 users for qualitative insights, 20+ for quantitative metrics

#### Usability Testing Methods

##### Think-Aloud Protocol
- Participants verbalize thoughts while completing tasks
- Reveals mental models and confusion points
- Most common usability testing method

##### Task-Based Testing
- Give participants specific tasks to complete
- Measure success rates, time, errors
- Compare against benchmarks

##### Remote Unmoderated Testing
- Participants complete tasks on their own
- Use tools like UserTesting, Maze
- Scale to larger sample sizes
- Less control but more realistic context

#### Usability Test Plan Template

\`\`\`markdown
## Test Objectives
What we want to learn

## Test Participants
Who we're testing with (personas, screening criteria)

## Test Tasks
1. Task 1: [Description]
   - Success criteria: [Criteria]
   - Time estimate: [Time]
2. Task 2: [Description]
   ...

## Success Metrics
- Task completion rate
- Time on task
- Error rate
- Satisfaction rating (1-5)

## Test Environment
- Device/browser
- Test location
- Tools needed

## Test Script
Step-by-step moderator script
\`\`\`

#### Analyzing Usability Test Results

1. **Severity Rating** (for each issue):
   - **Critical (P0):** Prevents task completion
   - **High (P1):** Causes significant frustration, workarounds exist
   - **Medium (P2):** Minor inconvenience
   - **Low (P3):** Cosmetic issue

2. **Frequency:**
   - How many users experienced the issue?
   - Pattern across different user types?

3. **Impact:**
   - How does it affect user goals?
   - Business impact?

4. **Recommendations:**
   - Specific design changes
   - Prioritized by severity × frequency

### 3. Surveys

**Purpose:** Collect quantitative data from large samples  
**When:** After launch, periodic check-ins  
**Sample Size:** 100+ responses for statistical significance

#### Survey Best Practices

**Question Types:**
- Multiple choice (for easy analysis)
- Rating scales (Likert scales: 1-5, 1-7)
- Open-ended (for qualitative insights)
- Ranking (to prioritize features)

**Survey Structure:**
1. **Introduction:** Purpose, time estimate, privacy
2. **Screening questions:** Ensure right participants
3. **Main questions:** Core research questions
4. **Demographics:** Age, location, experience level
5. **Open feedback:** Catch anything missed
6. **Thank you:** Appreciation and next steps

**Tips:**
- Keep it short (5-10 minutes max)
- One question per screen (mobile-friendly)
- Avoid jargon and technical terms
- Use consistent rating scales
- Pilot test with 5 people first
- Offer incentive for completion

### 4. Card Sorting

**Purpose:** Understand how users organize information  
**When:** Planning information architecture  
**Sample Size:** 15-30 participants

#### Card Sorting Types

**Open Card Sort:**
- Users create their own categories
- Reveals mental models
- Use early in design process

**Closed Card Sort:**
- Users sort into predefined categories
- Validates existing structure
- Use to test navigation

**Hybrid Card Sort:**
- Predefined categories + option to create new ones
- Balance between structure and flexibility

**Tools:** OptimalSort, Optimal Workshop, Miro

### 5. Diary Studies

**Purpose:** Understand behavior over time in natural context  
**When:** Exploring long-term behaviors  
**Duration:** 1-4 weeks  
**Sample Size:** 10-20 participants

**Methods:**
- Daily logs (text, photos, videos)
- Prompted entries (specific times or triggers)
- Weekly check-ins

**Use Cases for Nutricount:**
- How users plan meals over a week
- Challenges in maintaining keto diet
- Patterns in food logging behavior
- Factors affecting diet adherence

### 6. Field Studies

**Purpose:** Observe users in their natural environment  
**When:** Early research, understanding context  
**Duration:** 2-4 hours per visit

**Methods:**
- Contextual inquiry: Interview + observation
- Ethnographic research: Immerse in user's environment
- Shadowing: Follow user through their day

**Example:** Visit users' homes to observe:
- How they plan meals
- Use of existing nutrition apps
- Kitchen organization
- Food shopping habits

### 7. A/B Testing (See dedicated section)

**Purpose:** Compare two versions to determine which performs better  
**When:** After launch, continuous optimization

---

## 👥 Persona Development

### What Are Personas?

Personas are fictional characters that represent key user segments. They help teams:
- Understand user needs and goals
- Make design decisions from user perspective
- Prioritize features
- Communicate user research findings

### Creating Research-Based Personas

#### Step 1: Collect Data
Sources:
- User interviews (primary source)
- Surveys
- Analytics
- Customer support tickets
- Sales team insights

#### Step 2: Identify Patterns
Look for patterns in:
- Demographics (age, location, occupation)
- Goals and motivations
- Behaviors and habits
- Pain points and frustrations
- Technology usage
- Attitudes and values

#### Step 3: Group Users
Create 3-5 distinct user segments based on:
- Behavioral patterns (most important)
- Goals and needs
- Context of use
- NOT just demographics

#### Step 4: Create Persona Profiles

**Persona Template:**

\`\`\`markdown
## [Persona Name] - [Tagline]

### Demographics
- Age: [Age range]
- Occupation: [Job title]
- Location: [City type]
- Income: [Range]
- Education: [Level]

### Background
[Short narrative about their life]

### Goals
1. [Primary goal]
2. [Secondary goal]
3. [Tertiary goal]

### Needs
- [Need 1]
- [Need 2]
- [Need 3]

### Pain Points
- [Pain point 1]
- [Pain point 2]
- [Pain point 3]

### Behaviors
- [Behavior pattern 1]
- [Behavior pattern 2]
- [Behavior pattern 3]

### Technology
- Devices: [Devices used]
- Apps: [Commonly used apps]
- Tech Comfort: [Low/Medium/High]

### Motivations
- [What drives them]

### Frustrations
- [What blocks them]

### Quote
"[Representative quote from research]"
\`\`\`

### Example: Nutricount Persona

**See [docs/product/user-personas.md](../product/user-personas.md)** for our detailed personas:
- Sarah - The Keto Beginner
- Mike - The Fitness Enthusiast
- Lisa - The Busy Professional

### Using Personas in Design

**During Ideation:**
- "Would Sarah find this useful?"
- "Does this solve Mike's pain point?"

**During Prioritization:**
- "Which persona does this serve?"
- "How many personas need this?"

**During Design Reviews:**
- "Does this fit Lisa's mental model?"
- "Is this simple enough for Sarah?"

**In User Stories:**
- "As Sarah (Keto Beginner), I want to..."
- "As Mike (Fitness Enthusiast), I need to..."

---

## 💬 User Interviews

### Interview Planning

#### 1. Define Research Goals
- What do we want to learn?
- What decisions will this inform?
- What are the key research questions?

#### 2. Recruit Participants
**Screening criteria:**
- Demographics (age, location)
- Behaviors (uses nutrition tracking apps)
- Experience (new to keto vs. experienced)
- Technology (smartphone usage)

**Recruitment channels:**
- User base (existing users)
- Social media (Facebook groups, Reddit)
- User testing platforms (UserTesting, Respondent)
- Personal network (for early research)

**Incentives:**
- $50-100 for 60-minute interview
- Gift cards (Amazon, Starbucks)
- Early access to features
- Free subscription

#### 3. Prepare Interview Guide

**Introduction Script:**
\`\`\`
"Hi [Name], thanks for joining me today. I'm [Your Name] from Nutricount.

We're working on improving our nutrition tracking app, and I'd love to hear 
about your experience with tracking food and managing your diet.

This will take about 45 minutes. There are no right or wrong answers - I'm 
just interested in your honest thoughts and experiences.

With your permission, I'd like to record this call so I can focus on our 
conversation rather than taking notes. The recording is just for my team 
and won't be shared publicly. Is that okay with you?

Do you have any questions before we start?"
\`\`\`

**Main Questions (Example for Nutricount):**

**Current Behavior:**
1. Tell me about how you currently track what you eat.
2. Walk me through the last time you logged your food.
3. What apps or tools do you use for nutrition tracking?

**Pain Points:**
4. What's the most frustrating part of tracking your nutrition?
5. Tell me about a time when tracking felt like too much work.
6. What causes you to stop tracking?

**Goals & Motivations:**
7. What are you hoping to achieve with nutrition tracking?
8. What would make tracking easier for you?
9. How do you know if you're making progress?

**Specific Features:**
10. Tell me about how you plan your meals.
11. How do you decide what to eat when you're hungry?
12. What information do you need to feel confident about food choices?

**Wrap-up:**
13. If you could change one thing about nutrition tracking, what would it be?
14. Is there anything else you think I should know?

### Conducting the Interview

#### Before the Session
- Test recording equipment
- Review participant background
- Prepare interview guide
- Clear your schedule (no interruptions)

#### During the Session

**Build Rapport:**
- Be warm and friendly
- Share a bit about yourself
- Use their name
- Show genuine interest

**Active Listening:**
- Give full attention
- Don't interrupt
- Use verbal cues ("mm-hmm", "I see")
- Take notes on key points and quotes

**Probe Deeper:**
- "Can you tell me more about that?"
- "Why did you do that?"
- "How did that make you feel?"
- "What were you thinking at that moment?"
- "Can you give me a specific example?"

**Handle Silence:**
- Don't rush to fill pauses
- Give participants time to think
- Silence often leads to deeper insights

**Stay Neutral:**
- Don't show approval/disapproval
- Avoid leading questions
- Don't pitch your product
- Stay curious, not defensive

#### After the Session

**Immediate Notes (within 1 hour):**
- Key insights
- Surprising findings
- Memorable quotes
- Questions for next interview

**Thank You:**
- Send thank you email within 24 hours
- Deliver incentive promptly
- Share how their input will be used (if appropriate)

### Analyzing Interview Data

#### 1. Transcribe & Review
- Transcribe recordings (manual or automated)
- Read through all transcripts
- Highlight key quotes

#### 2. Affinity Mapping
- Write each insight on a sticky note
- Group related insights together
- Label each group with a theme
- Look for patterns across participants

**Tools:** Miro, Mural, FigJam, physical sticky notes

#### 3. Synthesize Findings
- **Themes:** What patterns emerged?
- **Insights:** What did we learn?
- **Quotes:** What memorable statements support each theme?
- **Recommendations:** What should we do based on this?

#### 4. Share Results

**Research Report Template:**

\`\`\`markdown
## Research Study: [Title]

### Executive Summary
- Key findings (3-5 bullets)
- Main recommendations (3-5 bullets)

### Methodology
- Participants: [Number, criteria]
- Method: [Interviews, duration]
- Dates: [When conducted]

### Key Findings

#### Finding 1: [Theme]
[Description of the pattern]

**Evidence:**
- "[Quote from Participant A]"
- "[Quote from Participant B]"
- [Additional evidence]

**Recommendation:**
[What we should do]

#### Finding 2: [Theme]
...

### Next Steps
- [Action item 1]
- [Action item 2]
- [Action item 3]

### Appendix
- Interview guide
- Participant details
- Full quotes
\`\`\`

---

## 🧪 Usability Testing

### Planning Usability Tests

#### 1. Define Test Objectives

**Good Objectives:**
- "Evaluate if users can successfully add a new food to their log"
- "Identify pain points in the meal planning flow"
- "Measure time to complete first nutrition log entry"

**Poor Objectives:**
- "See if users like the new design" (too vague)
- "Test everything" (too broad)

#### 2. Create Test Tasks

**Task Characteristics:**
- **Realistic:** Match real-world use cases
- **Specific:** Clear start and end point
- **Measurable:** Can determine success/failure
- **Scenario-based:** Provide context

**Example Tasks for Nutricount:**

**Task 1: Log Breakfast**
\`\`\`
Scenario: It's 8 AM and you just finished eating 2 scrambled eggs 
and 1 cup of coffee with heavy cream.

Task: Log this breakfast in the app.

Success criteria: User successfully adds both items to today's food log.
\`\`\`

**Task 2: Find Keto-Friendly Lunch**
\`\`\`
Scenario: It's lunchtime and you're hungry. You want to find something 
keto-friendly to eat that's quick to prepare.

Task: Find a keto-friendly lunch option in the app.

Success criteria: User navigates to dishes/recipes and identifies a 
keto-friendly option.
\`\`\`

**Task 3: Check Macros**
\`\`\`
Scenario: You want to know if you're staying within your keto macro goals 
for today.

Task: Check your current macro breakdown for today.

Success criteria: User finds and views today's nutrition summary.
\`\`\`

#### 3. Prepare Test Materials

**Moderator Script:**
- Introduction
- Consent and recording
- Think-aloud instructions
- Tasks (read exactly as written)
- Post-task questions
- Closing

**Think-Aloud Instructions:**
\`\`\`
"As you use the app, please think aloud - tell me what you're looking at, 
what you're trying to do, and what you're thinking. Imagine I'm sitting 
next to you and can't see the screen. Say everything that comes to mind, 
even if it seems obvious.

For example, instead of silently clicking a button, you might say: 
'I see a button that says Add Food, so I'm going to click that because 
I want to log my breakfast.'

There are no right or wrong actions. We're testing the app, not you. 
If something is confusing, that's valuable feedback - it means we need 
to improve the design.

Do you have any questions?"
\`\`\`

### Conducting Usability Tests

#### Test Environment Setup

**Remote Testing:**
- Video conferencing tool (Zoom, Google Meet)
- Screen sharing
- Recording (with permission)
- Backup recording method

**In-Person Testing:**
- Quiet, private room
- Camera to record screen and participant
- Note-taker (in addition to moderator)
- Test device

#### During the Test

**1. Introduction (5 minutes)**
- Welcome and build rapport
- Explain purpose of test
- Get consent for recording
- Explain think-aloud protocol

**2. Background Questions (5 minutes)**
- Current nutrition tracking habits
- Experience level with similar apps
- Device usage patterns

**3. Tasks (30-40 minutes)**

**For Each Task:**

a) **Read the task scenario** exactly as written

b) **Observe and take notes:**
   - Where do they look first?
   - What do they click?
   - Do they hesitate?
   - Do they express confusion?
   - Do they complete the task?
   - How long does it take?

c) **Post-task questions:**
   - "On a scale of 1-5, how difficult was that?"
   - "What did you expect to happen?"
   - "Was anything confusing?"

d) **Don't help** unless they're completely stuck (>2 minutes)

**4. Post-Test Questions (10 minutes)**
- Overall impressions (1-5 rating)
- Favorite feature
- Biggest frustration
- Suggested improvements
- Comparison to other apps

**5. Thank You**
- Appreciation
- Incentive delivery
- Next steps

#### Moderator Best Practices

✅ **Do:**
- Stay neutral (don't react to success/failure)
- Encourage thinking aloud
- Ask probing questions ("What are you looking for?")
- Give participants time to struggle (valuable insights!)
- Take notes on specific quotes
- Note body language and facial expressions

❌ **Don't:**
- Lead them to the answer
- Interrupt while they're working
- Defend the design
- Fill every silence
- Answer questions (reflect them back: "What do you think?")

### Analyzing Usability Test Results

#### 1. Review Sessions
- Watch recordings
- Take detailed notes
- Mark timestamps for key moments
- Track task completion and time

#### 2. Identify Issues

**Issue Template:**
\`\`\`markdown
## Issue #[Number]: [Short Title]

**Description:** What happened?

**Task:** Which task(s) affected?

**Frequency:** [X] out of [Y] participants

**Severity:** [Critical/High/Medium/Low]
- Critical: Prevents task completion
- High: Major frustration, workaround exists  
- Medium: Minor inconvenience
- Low: Cosmetic issue

**Evidence:**
- Participant 1: "[Quote or description]"
- Participant 2: "[Quote or description]"
- [Video timestamp: 12:34]

**Impact:**
- User impact: [How it affects users]
- Business impact: [How it affects metrics]

**Recommendation:** [Specific design change]

**Priority:** [P0/P1/P2/P3]
\`\`\`

#### 3. Calculate Metrics

**Task Success Rate:**
\`\`\`
Success Rate = (Successful completions / Total attempts) × 100%

Example: 4 out of 5 users completed the task = 80% success rate
\`\`\`

**Time on Task:**
\`\`\`
Average Time = Sum of all completion times / Number of completions

Example: (45s + 60s + 50s + 55s + 40s) / 5 = 50s average
\`\`\`

**Error Rate:**
\`\`\`
Error Rate = (Number of errors / Total tasks) × 100%
\`\`\`

**System Usability Scale (SUS):**
- Post-test questionnaire (10 questions)
- Scores range from 0-100
- Above 68 is average
- Above 80 is excellent

#### 4. Prioritize Issues

**Priority Matrix:**
\`\`\`
          High Impact
         ┌───────────────┐
High     │ P0 - Fix Now  │ P1 - Fix Soon
Freq     ├───────────────┤
         │ P1 - Fix Soon │ P2 - Fix Later
Low      └───────────────┘
          Low Impact
\`\`\`

#### 5. Create Usability Report

**Report Structure:**
1. **Executive Summary**
   - Key findings (3-5 bullets)
   - Critical issues (P0)
   - Overall usability score

2. **Methodology**
   - Participants
   - Tasks
   - Test setup

3. **Results by Task**
   - Task 1: Success rate, average time, issues
   - Task 2: ...

4. **Key Issues**
   - Issue #1 with priority, evidence, recommendation
   - Issue #2: ...

5. **Recommendations**
   - Prioritized list of improvements
   - Estimated effort
   - Expected impact

6. **Next Steps**
   - Design iterations
   - Follow-up testing

---

## 📊 A/B Testing

### What is A/B Testing?

A/B testing (split testing) compares two versions of something to determine which performs better. It's the gold standard for making data-driven design decisions.

### When to Use A/B Testing

**Good for:**
- Testing specific design changes
- Optimizing conversion rates
- Validating assumptions
- Incremental improvements
- High-traffic features

**Not good for:**
- Major redesigns (too many variables)
- Low-traffic features (not enough data)
- Exploratory research (use qualitative methods)
- When qualitative feedback is more important

### A/B Test Process

#### 1. Formulate Hypothesis

**Good Hypothesis Template:**
\`\`\`
If we [change], then [metric] will [increase/decrease] 
because [reasoning based on user research].
\`\`\`

**Examples:**
- "If we add nutrition previews to the food search results, then 
  users will add foods to their log 20% faster because they won't 
  need to click through to see macros."

- "If we simplify the onboarding flow from 5 steps to 3 steps, 
  then completion rate will increase from 65% to 80% because 
  users told us the current flow is too long."

#### 2. Define Metrics

**Primary Metric:**
- The main success metric (e.g., task completion rate)
- Directly related to hypothesis

**Secondary Metrics:**
- Support primary metric
- Check for unintended consequences

**Example Metrics for Nutricount:**
- Task completion rate (% who complete food logging)
- Time to complete task
- Error rate
- Daily active users (DAU)
- Feature adoption rate
- User satisfaction score

#### 3. Determine Sample Size

**Factors:**
- Current conversion rate
- Minimum detectable effect (MDE)
- Statistical significance (typically 95%)
- Statistical power (typically 80%)

**Use Sample Size Calculator:**
- Optimizely Calculator
- Evan Miller's Calculator
- VWO Calculator

**Example:**
\`\`\`
Current rate: 60%
Target rate: 70%
Significance: 95%
Power: 80%

Required sample: ~350 users per variation
\`\`\`

#### 4. Create Variations

**Control (A):** Current version  
**Treatment (B):** New version

**Only change one thing at a time!**

Bad: Change button color, text, and position  
Good: Change only button color

#### 5. Run the Test

**Duration:**
- Run until you reach required sample size
- Run at least 1-2 weeks (captures weekly patterns)
- Don't stop early even if results look good (false positives!)

**Implementation:**
- Use A/B testing tools: Optimizely, Google Optimize, VWO
- Or feature flags: LaunchDarkly, Split.io
- Ensure random assignment (50/50 split)
- Track users consistently (same variation throughout)

#### 6. Analyze Results

**Statistical Significance:**
- P-value < 0.05 (95% confidence)
- Don't stop early
- Look at confidence intervals

**Check for:**
- Novelty effect (users react to change itself)
- Selection bias (non-random assignment)
- Sample ratio mismatch (50/50 not maintained)

**Winner Criteria:**
\`\`\`
B is winner if:
1. Primary metric improved
2. Statistically significant (p < 0.05)
3. Practical significance (worth the effort)
4. No negative impact on secondary metrics
\`\`\`

#### 7. Make Decision

**Possible Outcomes:**

**Clear Winner:**
- Roll out to 100%
- Document learnings
- Plan next test

**No Significant Difference:**
- Keep control (simpler is better)
- Investigate why hypothesis was wrong
- Plan follow-up research

**Negative Result:**
- Roll back to control
- Understand what went wrong
- Update hypothesis

### A/B Testing Best Practices

✅ **Do:**
- Test one change at a time
- Run tests long enough
- Have a clear hypothesis
- Track secondary metrics
- Document all tests (winners and losers)
- Share learnings with team

❌ **Don't:**
- Test without a hypothesis
- Stop tests early
- Test multiple changes at once
- Ignore negative results
- Run tests on low-traffic features
- Make decisions on inconclusive results

### Example: A/B Test Plan for Nutricount

\`\`\`markdown
## A/B Test: Food Search Results Preview

### Hypothesis
If we show macro previews directly in search results (without requiring 
a click), then users will add foods to their log 25% faster because they 
can make decisions without leaving the search page.

### Metrics

**Primary:**
- Time to add food (from search to log saved)

**Secondary:**
- Search result clicks
- Task completion rate  
- User satisfaction rating

### Variations

**Control (A):**
- Current design: search results show only food name
- Users must click to see nutrition info

**Treatment (B):**
- New design: search results show food name + macro preview
  (Calories, Protein, Fat, Carbs)

### Sample Size
- Current avg time: 45 seconds
- Target time: 34 seconds (25% faster)
- Required sample: 400 users per variation
- Expected duration: 2 weeks

### Success Criteria
- Primary metric improves by ≥20%
- Statistical significance (p < 0.05)
- No degradation in secondary metrics

### Implementation
- Feature flag: food_search_macro_preview
- 50/50 split
- Track: user_id, variation, time_to_add, completion

### Timeline
- Week 1-2: Run test
- Week 3: Analyze results
- Week 3: Make decision & roll out

### Owner: [Name]
### Status: [Planning/Running/Complete]
\`\`\`

---

## 📈 Analytics & Metrics

### Product Analytics Fundamentals

#### Event Tracking

**Event Structure:**
\`\`\`javascript
{
  event_name: "food_added",
  timestamp: "2025-10-23T14:30:00Z",
  user_id: "user123",
  properties: {
    food_type: "product",
    food_id: 456,
    quantity: 100,
    meal_time: "lunch",
    source: "search"
  }
}
\`\`\`

**Key Events for Nutricount:**
- \`app_opened\`
- \`food_searched\`
- \`food_added\`
- \`nutrition_viewed\`
- \`goal_set\`
- \`meal_logged\`
- \`feature_used\`

#### User Properties

Track characteristics:
- \`user_type\`: free, premium
- \`signup_date\`: 2025-10-01
- \`diet_type\`: keto, general
- \`activity_level\`: high, medium, low
- \`goal\`: weight_loss, muscle_gain, maintenance

### Key Metrics to Track

#### 1. Activation Metrics
- **First-time user experience:**
  - Onboarding completion rate
  - Time to first value (e.g., first food logged)
  - Feature discovery rate

#### 2. Engagement Metrics
- **Daily/Weekly/Monthly Active Users (DAU/WAU/MAU)**
- **Session duration**
- **Session frequency**
- **Features used per session**
- **Stickiness:** DAU/MAU ratio (higher = more engaged)

#### 3. Retention Metrics
- **Day 1, Day 7, Day 30 retention**
- **Cohort retention curves**
- **Churn rate**

#### 4. Task Completion Metrics
- **Success rate:** % who complete key tasks
- **Time to complete:** How long tasks take
- **Error rate:** How often users make mistakes
- **Abandonment rate:** % who start but don't finish

#### 5. Feature Adoption
- **% of users who've tried feature**
- **Frequency of feature usage**
- **Time to first use**

### Analytics Tools

**Product Analytics:**
- **Google Analytics 4:** Free, comprehensive
- **Mixpanel:** Event-based, user-focused
- **Amplitude:** Powerful, product analytics
- **Heap:** Auto-tracking, retroactive analysis

**Heatmaps & Session Recording:**
- **Hotjar:** Heatmaps, recordings, feedback
- **FullStory:** Session replay, frustration signals
- **Clarity:** Free from Microsoft

**Specialized:**
- **Prometheus + Grafana:** Performance metrics (currently used!)
- **Sentry:** Error tracking
- **LogRocket:** Session replay for bugs

### Creating Analytics Dashboard

**Dashboard Structure:**

1. **Overview (Executive View)**
   - Total users (MAU)
   - Active today (DAU)
   - Key metric trend (e.g., foods logged)
   - Health score (red/yellow/green)

2. **Acquisition**
   - New signups
   - Signup source
   - Conversion funnel

3. **Activation**
   - Onboarding completion
   - Time to first log
   - Feature discovery

4. **Engagement**
   - DAU, WAU, MAU trends
   - Session duration
   - Features used

5. **Retention**
   - Retention curves by cohort
   - Churn analysis

6. **Feature Performance**
   - Feature X adoption rate
   - Feature X usage frequency
   - Feature X satisfaction

### Analyzing User Behavior

#### Funnel Analysis

**Example: Food Logging Funnel**
\`\`\`
1. Open app               100% (500 users)
2. Navigate to log         80% (400 users) - 20% drop
3. Search for food         70% (350 users) - 10% drop
4. Select food             60% (300 users) - 10% drop
5. Confirm and save        50% (250 users) - 10% drop
\`\`\`

**Analysis Questions:**
- Where is the biggest drop-off?
- Why are users dropping?
- How can we improve each step?

#### Cohort Analysis

**Track retention by signup cohort:**
\`\`\`
            Day 0  Day 1  Day 7  Day 30
Oct Week 1  100%    60%    40%    25%
Oct Week 2  100%    65%    42%    28%  (improving!)
Oct Week 3  100%    68%    45%    30%  (continuing improvement)
\`\`\`

**Insights:**
- Is retention improving over time?
- Which cohorts have better retention?
- What changed that caused improvement?

#### User Segmentation

**Segment by behavior:**
- **Power users:** >5 days/week active
- **Regular users:** 2-4 days/week active
- **Occasional users:** <2 days/week active
- **Dormant users:** Haven't used in 30 days

**Analyze each segment:**
- What do they have in common?
- What features do they use?
- How can we move users to higher engagement?

### Metrics Best Practices

✅ **Do:**
- Track key metrics consistently
- Review metrics regularly (weekly)
- Set targets and track progress
- Use metrics to validate hypotheses
- Share metrics with team

❌ **Don't:**
- Track everything (focus on what matters)
- Look at metrics without context
- Make decisions on single data points
- Ignore qualitative feedback
- Optimize for vanity metrics

---

## 🛠️ Tools & Resources

### Research Tools

#### User Interview Tools
- **Zoom / Google Meet:** Video conferencing
- **Calendly:** Scheduling
- **Otter.ai:** Transcription
- **Dovetail:** Research repository
- **EnjoyHQ:** Insights management
- **Miro / Mural:** Affinity mapping

#### Usability Testing Tools
- **UserTesting:** Remote unmoderated testing
- **Maze:** Rapid usability testing
- **Lookback:** Moderated remote testing
- **UsabilityHub:** Quick 5-second tests

#### Survey Tools
- **Typeform:** Beautiful surveys
- **Google Forms:** Free, simple
- **SurveyMonkey:** Professional surveys
- **Qualtrics:** Enterprise solution

#### Card Sorting Tools
- **OptimalSort:** Online card sorting
- **UserZoom:** Card sorting + tree testing
- **Miro:** Virtual card sorting

#### A/B Testing Tools
- **Optimizely:** Enterprise A/B testing
- **Google Optimize:** Free (sunsets 2023)
- **VWO:** Visual editor
- **LaunchDarkly:** Feature flags

#### Analytics Tools
- **Google Analytics 4:** Free web analytics
- **Mixpanel:** Product analytics
- **Amplitude:** Behavioral analytics
- **Hotjar:** Heatmaps + recordings

### Design Tools

#### Prototyping
- **Figma:** Collaborative design tool
- **Sketch:** Mac design tool
- **Adobe XD:** Adobe's design tool
- **Framer:** Interactive prototypes

#### Accessibility Testing
- **WAVE:** Browser extension
- **axe DevTools:** Accessibility checker
- **Lighthouse:** Chrome DevTools audit
- **WebAIM Contrast Checker:** Color contrast

### Learning Resources

#### UX Research
- **Nielsen Norman Group:** UX research articles
- **IDEO Design Thinking:** Design thinking methods
- **Google Design Sprint:** Sprint methodology
- **18F Methods:** Government design methods

#### Books
- **"The User Experience Team of One"** by Leah Buley
- **"Just Enough Research"** by Erika Hall
- **"Observing the User Experience"** by Mike Kuniavsky
- **"Don't Make Me Think"** by Steve Krug
- **"The Mom Test"** by Rob Fitzpatrick

#### Courses
- **Interaction Design Foundation:** UX courses
- **Coursera:** UX Research & Design Specialization
- **Nielsen Norman Group:** Professional training
- **General Assembly:** UX Design Bootcamp

#### Communities
- **UXPA:** UX Professionals Association
- **r/userexperience:** Reddit community
- **UX Research Collective:** Slack community
- **Designer Hangout:** Slack community

---

## 🔄 Research Process

### Research Project Flow

#### 1. Define (Week 1)
- **Identify problem or question**
- **Align with stakeholders**
- **Set research objectives**
- **Choose methods**
- **Define success criteria**

**Deliverable:** Research plan

#### 2. Prepare (Week 2)
- **Recruit participants**
- **Prepare materials** (guides, prototypes)
- **Pilot test** (1-2 sessions)
- **Refine based on pilot**

**Deliverable:** Ready to launch

#### 3. Conduct (Week 3-4)
- **Run research sessions**
- **Take detailed notes**
- **Record sessions** (with permission)
- **Debrief after each session**

**Deliverable:** Raw data

#### 4. Analyze (Week 5)
- **Review all data**
- **Identify patterns**
- **Create affinity map**
- **Extract insights**

**Deliverable:** Synthesized findings

#### 5. Share (Week 6)
- **Create research report**
- **Present to stakeholders**
- **Workshops with design team**
- **Document in research repository**

**Deliverable:** Research report + recommendations

#### 6. Implement (Ongoing)
- **Design based on insights**
- **Track impact**
- **Follow-up research**

**Deliverable:** Improved product

### Continuous Research

**Build research into your workflow:**

**Weekly:**
- Review customer support tickets
- Check analytics dashboard
- Read user feedback

**Monthly:**
- Conduct 3-5 user interviews
- Run usability test on new features
- Analyze cohort retention

**Quarterly:**
- Large research project
- Update personas
- Validate product roadmap

**Annually:**
- Comprehensive user needs study
- Competitive analysis
- Market research

---

## ✨ Best Practices

### Research Ethics

**Always:**
- ✅ Get informed consent
- ✅ Protect participant privacy
- ✅ Store data securely
- ✅ Be transparent about purpose
- ✅ Compensate fairly
- ✅ Allow participants to withdraw

**Never:**
- ❌ Deceive participants
- ❌ Share identifying information
- ❌ Coerce participation
- ❌ Use data without consent

### Research Quality

**Ensure quality by:**
- **Diverse participants:** Different demographics, behaviors
- **Multiple methods:** Triangulate findings
- **Sufficient sample:** 5+ for qualitative, 100+ for quantitative
- **Pilot testing:** Test materials before launch
- **Peer review:** Have teammate review findings

### Common Pitfalls

#### ❌ Confirmation Bias
**Problem:** Looking for evidence that supports what you already believe

**Solution:**
- State hypotheses upfront
- Ask neutral questions
- Look for disconfirming evidence
- Have teammate review

#### ❌ Leading Questions
**Problem:** Questions that suggest a preferred answer

**Bad:** "Don't you think this feature is useful?"  
**Good:** "How useful is this feature to you?"

#### ❌ Small Sample Sizes
**Problem:** Drawing conclusions from too few users

**Solution:**
- 5+ for qualitative insights
- 100+ for quantitative metrics
- Consider statistical significance

#### ❌ Not Recruiting Right Users
**Problem:** Testing with people who aren't your target users

**Solution:**
- Create screening criteria
- Recruit from actual user base
- Verify participants match criteria

#### ❌ Not Following Up
**Problem:** Research sits on shelf, not used

**Solution:**
- Share findings quickly
- Make actionable recommendations
- Track which insights get implemented
- Show impact of research

### Research Checklist

**Before Research:**
- [ ] Clear research objectives
- [ ] Stakeholder alignment
- [ ] Method selected
- [ ] Materials prepared
- [ ] Participants recruited
- [ ] Pilot test complete
- [ ] Recording setup tested
- [ ] Consent forms ready

**During Research:**
- [ ] Informed consent obtained
- [ ] Recording started
- [ ] Notes taken
- [ ] Follow-up questions asked
- [ ] Thank you sent

**After Research:**
- [ ] Data analyzed
- [ ] Patterns identified
- [ ] Insights extracted
- [ ] Report created
- [ ] Findings presented
- [ ] Recommendations made
- [ ] Repository updated

---

## 📞 Next Steps

### For UX/UI Designers

1. **Review existing user personas:** [docs/product/user-personas.md](../product/user-personas.md)
2. **Check analytics:** What features are most/least used?
3. **Plan research:** What do we need to learn next?
4. **Conduct usability tests:** Test new features before launch
5. **Stay close to users:** Regular interviews (monthly)

### For Product Managers

1. **Use research for roadmap:** Prioritize based on user needs
2. **Set up analytics:** Track key metrics
3. **Run A/B tests:** Validate product hypotheses
4. **Review metrics:** Weekly metrics review
5. **Share insights:** Keep team informed

### For Product Owners

1. **Validate user stories:** Base stories on research
2. **Use personas:** Write stories from persona perspective
3. **Include acceptance criteria:** Based on success metrics
4. **Review research:** Before sprint planning
5. **Prioritize with data:** Use research + metrics

### Getting Started

**Your First Research Project:**

1. **Week 1:** Define research question
2. **Week 2:** Recruit 5 users, prepare interview guide
3. **Week 3:** Conduct 5 interviews
4. **Week 4:** Analyze and present findings

**Questions?**
- Review this guide
- Check [CONTRIBUTING.md](../../CONTRIBUTING.md)
- Ask in team meetings

---

## 📚 Additional Resources

### Internal Documentation
- [User Personas](../product/user-personas.md)
- [User Stories](../product/user-stories.md)
- [Product Metrics](../product-management/metrics.md)
- [QA Testing Strategy](../qa/testing-strategy.md)

### External Resources
- [Nielsen Norman Group](https://www.nngroup.com/)
- [IDEO Design Kit](https://www.designkit.org/)
- [18F Methods](https://methods.18f.gov/)
- [User Interviews Blog](https://www.userinterviews.com/blog)

---

**Maintained by:** Nutricount UX Team  
**Last Updated:** October 23, 2025  
**Next Review:** November 2025

**Contributors:**
- UX Researchers
- Product Designers
- Product Managers

**Version:** 1.0.0

---

*This guide is a living document. Have suggestions? See [CONTRIBUTING.md](../../CONTRIBUTING.md) for how to contribute.*
