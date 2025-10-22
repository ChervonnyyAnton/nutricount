# 📊 KPIs & Metrics Guide for Product Managers

## Overview

This guide helps Product Managers define, track, and optimize key performance indicators (KPIs) for Nutricount, balancing our dual mission as an educational platform and FOSS health tracker.

---

## 🎯 Strategic Objectives

### Primary Objectives
1. **User Success:** Help users achieve their health goals
2. **Developer Learning:** Provide valuable learning experiences
3. **Privacy Leadership:** Set the standard for privacy in health apps
4. **Community Growth:** Build a sustainable FOSS community
5. **Technical Excellence:** Maintain high code and product quality

### Success Metrics Framework
```
Acquisition → Activation → Retention → Referral → Revenue (FOSS = Contribution)
```

---

## 📈 Product Metrics Dashboard

### 1. User Metrics

#### Active Users
**Definition:** Users who perform meaningful actions

**Metrics:**
- **DAU (Daily Active Users):** Unique users per day
- **WAU (Weekly Active Users):** Unique users per week
- **MAU (Monthly Active Users):** Unique users per month
- **Stickiness:** DAU/MAU ratio (target: >20%)

**Tracking:**
```javascript
// Example: LocalStorage tracking (privacy-preserving)
const trackUsage = () => {
  const lastVisit = localStorage.getItem('lastVisit');
  const today = new Date().toISOString().split('T')[0];
  
  if (lastVisit !== today) {
    localStorage.setItem('lastVisit', today);
    // Increment visit counter (local only)
  }
};
```

**Target KPIs:**
- DAU: 100+ (by Q1 2026)
- WAU: 500+ (by Q1 2026)
- MAU: 1,500+ (by Q1 2026)
- Stickiness: 20%+

#### User Acquisition
**Definition:** New users joining the platform

**Metrics:**
- **Sign-ups per day:** New user registrations
- **Installation rate:** PWA installs / visits
- **Conversion rate:** Visitors → active users
- **Acquisition channels:** Organic, referral, social, etc.

**Target KPIs:**
- Growth rate: 10% month-over-month
- Conversion rate: 5%+ (visitor → user)
- PWA install rate: 15%+ (mobile)

#### User Retention
**Definition:** Users returning to the platform

**Metrics:**
- **Day 1 retention:** Users returning next day
- **Week 1 retention:** Users active in week 1
- **Month 1 retention:** Users active in month 1
- **Cohort analysis:** Retention by sign-up date

**Calculation:**
```
Day 1 Retention = (Users active on Day 1) / (Users signed up on Day 0)
```

**Target KPIs:**
- Day 1: 40%+
- Week 1: 25%+
- Month 1: 15%+
- Month 3: 10%+

### 2. Engagement Metrics

#### Feature Usage
**Definition:** How users interact with features

**Metrics:**
- **Products logged per user:** Average daily entries
- **Fasting sessions per user:** Average weekly sessions
- **Dishes created per user:** Average total dishes
- **Feature adoption rate:** % users using each feature

**Tracking Example:**
```python
# Backend analytics (aggregated, anonymized)
metrics = {
    'products_per_user': db.query(
        "SELECT AVG(product_count) FROM user_stats"
    ),
    'fasting_sessions_per_week': db.query(
        "SELECT AVG(sessions) FROM fasting_stats WHERE week = current_week"
    ),
    'feature_adoption': {
        'fasting': percentage_using_fasting,
        'gki': percentage_using_gki,
        'dishes': percentage_using_dishes,
    }
}
```

**Target KPIs:**
- Products logged/day: 5+ per active user
- Fasting sessions/week: 4+ for fasting users
- Dishes created: 3+ per user
- Feature adoption (fasting): 30%+
- Feature adoption (GKI): 15%+

#### Session Metrics
**Definition:** User behavior during sessions

**Metrics:**
- **Session duration:** Average time per visit
- **Sessions per day:** How often users return
- **Bounce rate:** Single-page sessions
- **Pages per session:** Depth of engagement

**Target KPIs:**
- Session duration: 5+ minutes
- Sessions per day: 2+ for active users
- Bounce rate: <30%
- Pages per session: 4+

### 3. Health Outcome Metrics

#### Goal Achievement
**Definition:** Users reaching their health goals

**Metrics:**
- **Users with goals set:** % setting nutrition goals
- **Goal achievement rate:** % reaching daily goals
- **Keto users in ketosis:** % maintaining keto (index >70)
- **Fasting completion rate:** % completing fasting sessions

**Target KPIs:**
- Users with goals: 60%+
- Goal achievement (daily): 40%+
- Keto users in ketosis: 70%+
- Fasting completion: 80%+

#### Tracking Consistency
**Definition:** Regular usage indicating commitment

**Metrics:**
- **Streak length:** Consecutive days logging
- **Weekly logging rate:** Days logged per week
- **Data completeness:** % of meals logged

**Target KPIs:**
- Average streak: 7+ days
- Weekly logging: 5+ days
- Data completeness: 70%+

### 4. Developer/Learning Metrics

#### Code Quality
**Definition:** Technical health of the codebase

**Metrics:**
- **Test coverage:** Backend 94%, Frontend 85%
- **Build success rate:** % of CI/CD builds passing
- **Code review time:** Average PR review time
- **Tech debt ratio:** Estimated tech debt / codebase

**Target KPIs:**
- Backend coverage: >90%
- Frontend coverage: >80%
- Build success: >95%
- PR review time: <24 hours
- Tech debt: <10%

#### Developer Engagement
**Definition:** Developer community participation

**Metrics:**
- **GitHub stars:** Public interest indicator
- **Forks:** Developers experimenting
- **Contributors:** Active contributors
- **PR acceptance rate:** % PRs merged
- **Issue resolution time:** Average time to close

**Target KPIs:**
- GitHub stars: 500+ (by Q2 2026)
- Contributors: 20+ (by Q2 2026)
- PR acceptance: 70%+
- Issue resolution: <7 days

#### Documentation Usage
**Definition:** Learning resource effectiveness

**Metrics:**
- **Documentation views:** Page views on docs
- **Time on documentation:** Engagement time
- **Documentation completeness:** % of features documented
- **Feedback score:** User ratings of docs

**Target KPIs:**
- Documentation completeness: 100%
- User satisfaction: 4.5/5 stars
- Search success rate: 80%+

### 5. Privacy & Trust Metrics

#### Data Control
**Definition:** User control over their data

**Metrics:**
- **Browser-only adoption:** % using Public version
- **Self-hosted adoption:** % deploying locally
- **Export usage:** % users exporting data
- **Privacy awareness:** Survey responses

**Target KPIs:**
- Browser-only: 40%+
- Self-hosted: 30%+
- Export usage: 20%+
- Privacy trust score: 4.8/5

#### Security & Reliability
**Definition:** Platform trustworthiness

**Metrics:**
- **Uptime:** Service availability
- **Security incidents:** Zero-tolerance
- **Data breaches:** Zero-tolerance
- **Bug severity:** Critical bugs per release

**Target KPIs:**
- Uptime: 99.9%
- Security incidents: 0
- Data breaches: 0
- Critical bugs: <1 per release

---

## 📊 Metrics Collection Strategy

### Privacy-Preserving Analytics

#### Principle: Respect Privacy First
- ✅ Local-only tracking when possible
- ✅ Aggregated, anonymized server metrics
- ✅ Opt-in for detailed analytics
- ✅ Transparent about data collection
- ❌ No third-party analytics (Google, etc.)
- ❌ No user tracking across sessions
- ❌ No selling or sharing data

#### Implementation Example

**Browser-Only Version (Public):**
```javascript
// Fully local, no server calls
class LocalMetrics {
  constructor() {
    this.metrics = JSON.parse(localStorage.getItem('metrics') || '{}');
  }
  
  trackEvent(category, action) {
    const key = `${category}_${action}`;
    this.metrics[key] = (this.metrics[key] || 0) + 1;
    localStorage.setItem('metrics', JSON.stringify(this.metrics));
  }
  
  getMetrics() {
    return this.metrics; // User can view their own metrics
  }
}
```

**Self-Hosted Version (Local):**
```python
# Optional server-side aggregated metrics
class MetricsCollector:
    def track_event(self, category: str, action: str):
        """Aggregate event counts only, no user identification"""
        metric_key = f"{category}:{action}"
        redis.incr(metric_key)
        redis.incr(f"{metric_key}:daily:{today}")
        # No user_id, no session_id, no IP address stored
```

### Measurement Framework

#### 1. Product Analytics (Local)
- User counts (localStorage)
- Feature usage (localStorage)
- Session metrics (localStorage)
- User can export their own data

#### 2. Aggregated Server Metrics (Optional)
- Total users (count only)
- Popular features (percentages)
- Performance metrics (response times)
- Error rates (anonymized)

#### 3. Community Metrics (Public)
- GitHub stars, forks, contributors
- Issue/PR counts and resolution times
- Documentation page views
- Public community feedback

#### 4. Health Outcome Surveys (Opt-in)
- Anonymous surveys about success
- Goal achievement self-reports
- Feature satisfaction ratings
- Privacy satisfaction ratings

---

## 📈 Reporting Cadence

### Daily Metrics (Automated)
- Active users (DAU)
- New sign-ups
- Critical errors
- System performance

### Weekly Review (Team Meeting)
- Engagement trends
- Feature adoption
- Bug/issue status
- Developer activity

### Monthly Business Review
- All KPIs vs. targets
- User retention cohorts
- Growth trends
- Strategic adjustments

### Quarterly Planning
- OKR review
- Roadmap adjustments
- Resource allocation
- Long-term strategy

---

## 🎯 OKR Framework

### Q4 2025 OKRs

#### Objective 1: Achieve Testing Excellence
**Key Results:**
- ✅ Backend coverage >90% (Current: 94%)
- ✅ Frontend coverage >80% (Current: 85%)
- ⏳ E2E critical paths 100% covered (Target: Week 4)
- ⏳ Zero flaky tests (Current: 0)

#### Objective 2: Complete Educational Materials
**Key Results:**
- ✅ QA guide published (Done)
- ✅ DevOps guide published (Done)
- ⏳ PO guide published (This PR)
- ⏳ PM guide published (This PR)
- [ ] UX/UI guide published (Week 5)

#### Objective 3: Grow Developer Community
**Key Results:**
- GitHub stars: 100+ (Current: tracking)
- Contributors: 5+ (Current: tracking)
- Documentation satisfaction: 4.5/5
- Issue response time: <48 hours

### Q1 2026 OKRs (Draft)

#### Objective 1: Scale User Adoption
**Key Results:**
- MAU: 1,500+ active users
- Retention D1: 40%+
- Feature adoption (fasting): 30%+
- Privacy satisfaction: 4.8/5

#### Objective 2: Enhance Mobile Experience
**Key Results:**
- Mobile users: 60%+ of total
- PWA install rate: 15%+
- Mobile session duration: 7+ minutes
- Touch UI satisfaction: 4.7/5

#### Objective 3: Community Growth
**Key Results:**
- GitHub stars: 500+
- Contributors: 20+
- Community recipes: 100+
- Forum activity: 50+ posts/month

---

## 🔧 Tools & Dashboards

### Recommended Tools

#### Free/Open Source
- **Plausible Analytics:** Privacy-first web analytics
- **Matomo:** Self-hosted analytics
- **GitHub Insights:** Built-in metrics
- **Grafana:** System monitoring dashboards
- **Prometheus:** Metrics collection

#### Custom Solutions
- **Local Dashboard:** Show users their own metrics
- **Admin Panel:** Aggregated, anonymized metrics
- **GitHub Actions:** CI/CD metrics
- **Automated Reports:** Weekly summary emails

### Dashboard Layout

```
┌─────────────────────────────────────────┐
│         NUTRICOUNT METRICS DASHBOARD     │
├─────────────────────────────────────────┤
│ USERS                                   │
│ ├─ DAU: 250 (↑5%)                      │
│ ├─ WAU: 900 (↑8%)                      │
│ └─ MAU: 2,100 (↑12%)                   │
├─────────────────────────────────────────┤
│ ENGAGEMENT                              │
│ ├─ Products/day: 6.2 (↑0.3)            │
│ ├─ Session time: 7.5 min (↑1.2)        │
│ └─ Fasting completion: 82% (↑2%)       │
├─────────────────────────────────────────┤
│ QUALITY                                 │
│ ├─ Test coverage: 93% (→)              │
│ ├─ Uptime: 99.95% (↑0.05%)             │
│ └─ Error rate: 0.02% (↓0.01%)          │
├─────────────────────────────────────────┤
│ COMMUNITY                               │
│ ├─ GitHub stars: 145 (↑12)             │
│ ├─ Contributors: 8 (↑2)                │
│ └─ Open issues: 15 (↓3)                │
└─────────────────────────────────────────┘
```

---

## 📋 Metric Definitions Reference

### Calculation Formulas

#### Retention Rate
```
Retention Rate = (Users Active on Day N / Users Signed Up on Day 0) × 100%
```

#### Engagement Score
```
Engagement Score = (
  (Sessions per Day × 0.3) +
  (Features Used × 0.3) +
  (Time on Site × 0.2) +
  (Actions per Session × 0.2)
) / 4
```

#### Churn Rate
```
Monthly Churn = (Users Lost in Month / Users at Start of Month) × 100%
```

#### Viral Coefficient (K-factor)
```
K = (Invites Sent per User) × (Conversion Rate of Invites)
```

#### North Star Metric
```
North Star = Weekly Active Users × Avg Sessions per User × Avg Actions per Session
```

---

## 🎓 Learning & Iteration

### A/B Testing Framework

When considering feature changes:

1. **Hypothesis:** "Adding quick-add button will increase logging frequency"
2. **Metric:** Products logged per day
3. **Segments:** 50% with button, 50% without
4. **Duration:** 2 weeks
5. **Success Criteria:** >10% improvement
6. **Analysis:** Statistical significance (p<0.05)

### User Feedback Loop

```
Metrics → Insights → Hypotheses → Experiments → Analysis → Action
```

**Example:**
1. **Metric:** Low fasting completion (60%)
2. **Insight:** Users forget to end sessions
3. **Hypothesis:** Notifications will improve completion
4. **Experiment:** Add notification feature
5. **Analysis:** Completion rises to 82%
6. **Action:** Make notifications default

---

## 📖 Resources

### Internal Documentation
- [User Stories Guide](../product/user-stories.md)
- [Product Backlog](../product/product-backlog.md)
- [Testing Strategy](../qa/testing-strategy.md)
- [CI/CD Pipeline](../devops/ci-cd-pipeline.md)

### External Resources
- [Lean Analytics (Alistair Croll)](https://leananalyticsbook.com/)
- [Amplitude Guide to Product Metrics](https://amplitude.com/blog/product-metrics)
- [Mixpanel Product Metrics](https://mixpanel.com/topics/product-metrics/)
- [Plausible Analytics](https://plausible.io/) - Privacy-first analytics

### Privacy & Ethics
- [Privacy by Design](https://www.ipc.on.ca/wp-content/uploads/Resources/7foundationalprinciples.pdf)
- [GDPR Compliance](https://gdpr.eu/)
- [Mozilla's Lean Data Practices](https://www.mozilla.org/en-US/about/policy/lean-data/)

---

## 🚀 Action Items for Product Managers

### Week 1: Setup
- [ ] Define North Star Metric
- [ ] Set up metrics dashboard (Grafana)
- [ ] Establish baseline metrics
- [ ] Document measurement plan

### Week 2-4: Measurement
- [ ] Implement local analytics
- [ ] Configure server metrics (optional, aggregated)
- [ ] Set up automated reports
- [ ] Create stakeholder dashboards

### Monthly: Review & Optimize
- [ ] Review all KPIs against targets
- [ ] Analyze cohort retention
- [ ] Identify improvement opportunities
- [ ] Run experiments (A/B tests)

### Quarterly: Strategic Planning
- [ ] OKR review and planning
- [ ] Roadmap adjustments
- [ ] Resource allocation
- [ ] Community engagement initiatives

---

**Last Updated:** October 22, 2025  
**Version:** 1.0  
**Status:** ✅ Complete
