# CI/CD Pipeline Architecture (Week 5)

**Target Audience:** DevOps Engineers, Architects, Technical Leads  
**Status:** ✅ Complete  
**Last Updated:** October 23, 2025  
**Version:** 2.0 (Week 5 Update)

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Workflow Orchestration](#workflow-orchestration)
4. [Pipeline Stages](#pipeline-stages)
5. [Deployment Strategy](#deployment-strategy)
6. [Quality Gates](#quality-gates)
7. [Security Integration](#security-integration)
8. [Testing Pyramid](#testing-pyramid)
9. [Monitoring & Observability](#monitoring--observability)
10. [Future Enhancements](#future-enhancements)

---

## Executive Summary

Nutricount implements a **multi-stage, dependency-based CI/CD pipeline** using GitHub Actions. The pipeline ensures code quality, security, and reliability through automated testing, security scanning, and conditional deployments.

### Key Achievements (Week 5)
- ✅ **3-stage pipeline**: Test → Build → Deploy
- ✅ **GitHub Pages auto-deployment** with CI/CD dependency
- ✅ **E2E testing** post-deployment on live GitHub Pages
- ✅ **Security scanning** with Bandit integration
- ✅ **844 tests** with 87-94% coverage
- ✅ **Zero-downtime** deployments via GitHub Pages
- ✅ **Conditional deployment** gates (only on success)

### Metrics
- **Pipeline Duration**: ~5-8 minutes (full pipeline)
- **Test Suite**: 844 tests, 1 skipped
- **Code Coverage**: 87-94% across modules
- **Security Score**: Grade A (96/100)
- **Deployment Frequency**: On every main branch push
- **Success Rate**: >95% (based on test stability)

---

## Architecture Overview

### High-Level Pipeline Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          GITHUB REPOSITORY                                │
│                                                                           │
│  Trigger Events:                                                          │
│  • Pull Request → main/develop                                            │
│  • Push → main (direct commits only)                                      │
│  • Manual workflow_dispatch                                               │
└────────────────────────────────┬──────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        WORKFLOW 1: CI/CD Pipeline                         │
│                        (.github/workflows/test.yml)                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────┐      ┌──────────────┐      ┌────────────────┐          │
│  │  STAGE 1    │      │   STAGE 2    │      │   STAGE 3      │          │
│  │   TEST      │─────▶│    BUILD     │─────▶│    DEPLOY      │          │
│  │             │      │              │      │  AUTHORIZATION │          │
│  └─────────────┘      └──────────────┘      └────────────────┘          │
│       │                     │                      │                     │
│       ▼                     ▼                      ▼                     │
│  • Lint (flake8)      • Docker build         • Auth gate               │
│  • Security scan      • ARM64 support        • Permission              │
│  • Unit tests         • Health check         • Signal success          │
│  • Coverage           • Image test                                      │
│                                                                           │
│  Exit Code: 0 (Success) / 1 (Failure)                                    │
└────────────────────────────────┬──────────────────────────────────────────┘
                                 │
                                 │ workflow_run trigger
                                 │ (only if conclusion == 'success')
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                  WORKFLOW 2: Deploy Demo to GitHub Pages                 │
│                  (.github/workflows/deploy-demo.yml)                      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Condition: github.event.workflow_run.conclusion == 'success'             │
│                                                                           │
│  ┌─────────────────┐      ┌──────────────────┐                          │
│  │  JOB 1: DEPLOY  │─────▶│  JOB 2: E2E TEST │                          │
│  │  GitHub Pages   │      │  Live Pages URL  │                          │
│  └─────────────────┘      └──────────────────┘                          │
│       │                          │                                       │
│       ▼                          ▼                                       │
│  • Verify CI/CD auth       • Wait for deployment                         │
│  • Upload demo/ artifact   • Run Playwright E2E                          │
│  • Deploy to Pages         • Test on live URL                            │
│  • Generate summary        • Upload test artifacts                       │
│                                                                           │
│  URL: https://chervonnyyanton.github.io/nutricount/                      │
└──────────────────────────────────────────────────────────────────────────┘
```

### Workflow Dependencies

The pipeline uses **workflow_run** triggers to create dependencies:

1. **Primary Workflow** (`test.yml`): Runs on PR/push
2. **Secondary Workflow** (`deploy-demo.yml`): Triggered only after primary succeeds
3. **Tertiary Job** (E2E tests): Runs after Pages deployment completes

This ensures:
- ❌ Failed tests → No build
- ❌ Failed build → No deployment
- ❌ Failed deployment → No E2E tests
- ✅ All pass → Production-ready code on GitHub Pages

---

## Workflow Orchestration

### Workflow 1: CI/CD Pipeline (test.yml)

**Purpose:** Validate code quality, run tests, build Docker image, authorize deployments

**Triggers:**
```yaml
on:
  pull_request:
    branches: [ main, develop ]
  push:
    branches: [ main ]  # Direct pushes only (not PR commits)
  workflow_dispatch:
```

**Key Design Decision:**
- Pull requests trigger the workflow for validation
- Direct pushes to main trigger full pipeline including deployment
- This prevents duplicate runs when PR is merged

**Jobs Sequence:**

```
test job (runs on: ubuntu-latest)
    │
    ├─ Checkout code
    ├─ Setup Python 3.11
    ├─ Install dependencies (requirements-minimal.txt)
    ├─ Lint with flake8 (max-line-length=100)
    ├─ Security scan with Bandit (continue-on-error)
    ├─ Run pytest (844 tests)
    └─ Upload coverage to Codecov
    │
    ▼
build job (needs: test)
    │
    ├─ Setup Docker Buildx
    ├─ Build ARM64 Docker image
    ├─ Start container (port 5000)
    ├─ Health check (curl /health)
    └─ Stop and remove container
    │
    ▼
deploy job (needs: build, if: main branch + push event)
    │
    └─ Deploy authorization message
       "✅ All tests and builds passed"
       "🔐 Authorizing deployment to production and GitHub Pages"
```

### Workflow 2: Deploy Demo to GitHub Pages (deploy-demo.yml)

**Purpose:** Deploy validated code to GitHub Pages and run E2E tests on live deployment

**Triggers:**
```yaml
on:
  workflow_run:
    workflows: ["CI/CD Pipeline"]
    types: [completed]
    branches: [ main ]
  workflow_dispatch:  # Allow manual triggers
```

**Conditional Execution:**
```yaml
if: ${{ github.event.workflow_run.conclusion == 'success' || 
        github.event_name == 'workflow_dispatch' }}
```

**Jobs Sequence:**

```
deploy job (environment: github-pages)
    │
    ├─ Verify CI/CD authorization
    ├─ Checkout code
    ├─ Setup Pages configuration
    ├─ Upload demo/ artifact
    ├─ Deploy to GitHub Pages
    └─ Generate deployment summary
    │
    ▼
e2e-tests-pages job (needs: deploy)
    │
    ├─ Setup Node.js 20
    ├─ Install npm dependencies
    ├─ Install Playwright (chromium)
    ├─ Wait for Pages to be ready (30s + health check)
    ├─ Run E2E tests on https://chervonnyyanton.github.io/nutricount/
    ├─ Upload test reports on failure
    └─ Generate test summary
```

### Workflow 3: E2E Tests (e2e-tests.yml) - DISABLED

**Status:** Currently disabled (manual trigger only)

**Reason:** Infrastructure issues documented in E2E_TEST_ANALYSIS.md

**When Re-enabled:**
- Tests both Local version (Flask backend) and Public version (demo SPA)
- Can run on schedule (daily at 2 AM UTC)
- Provides comprehensive E2E coverage for both deployment modes

---

## Pipeline Stages

### Stage 1: TEST

**Objective:** Validate code quality and correctness

#### 1.1 Linting (flake8)
```bash
flake8 src/ app.py --max-line-length=100 --ignore=E501,W503,E226
```

**Configuration:**
- Max line length: 100 characters
- Ignored rules:
  - E501: Line too long (handled by max-line-length)
  - W503: Line break before binary operator
  - E226: Missing whitespace around arithmetic operator

**Exit Criteria:** Zero linting errors

#### 1.2 Security Scanning (Bandit)
```bash
bandit -r src/ app.py -ll -f json -o bandit-report.json
```

**Configuration:**
- Severity: Low and above (-ll)
- Output: JSON report + console text
- Continue on error: Yes (informational)

**Artifacts:**
- `bandit-report.json`
- `bandit-output.txt`
- Retention: 30 days

**Exit Criteria:** Non-blocking (informational only)

#### 1.3 Unit & Integration Tests (pytest)
```bash
pytest tests/ -v --cov=src --cov-report=xml
```

**Test Categories:**
- Unit tests: `tests/unit/` (isolated function/class tests)
- Integration tests: `tests/integration/` (API endpoint tests)
- E2E tests: `tests/e2e/` (workflow tests)

**Coverage Targets:**
- Overall: 87-94%
- Per module: Varies by complexity

**Exit Criteria:** All tests pass (844 passed, 1 skipped allowed)

#### 1.4 Coverage Reporting (Codecov)
```yaml
- uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
    fail_ci_if_error: false
```

**Exit Criteria:** Non-blocking (informational)

---

### Stage 2: BUILD

**Objective:** Create production-ready Docker image

#### 2.1 Docker Build
```bash
docker build -f dockerfile -t nutrition-tracker:latest .
```

**Key Features:**
- Base image: ARM64-compatible Python 3.11
- Multi-stage build (if applicable)
- Layer caching optimization
- Security: Non-root user, minimal attack surface

**Exit Criteria:** Build succeeds without errors

#### 2.2 Image Testing
```bash
docker run -d --name test-container -p 5000:5000 nutrition-tracker:latest
sleep 10
curl -f http://localhost:5000/health || exit 1
docker stop test-container && docker rm test-container
```

**Validation:**
1. Container starts successfully
2. Health endpoint responds with 200 OK
3. Container stops cleanly

**Exit Criteria:** Health check passes

---

### Stage 3: DEPLOY (Authorization Gate)

**Objective:** Authorize downstream deployments

**Conditional Execution:**
```yaml
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

**Purpose:**
- Signal successful pipeline completion
- Authorize GitHub Pages deployment
- Authorize production deployment (future)
- Create audit trail

**Output:**
```
🚀 Deployment Authorization
✅ All tests and builds passed
🔐 Authorizing deployment to production and GitHub Pages

Tests passed: Unit tests, linting, coverage
Build passed: Docker image built and health-checked
Authorization granted for:
  - Production deployment to Raspberry Pi
  - GitHub Pages demo deployment
📡 GitHub Pages workflow will be triggered automatically
```

**Exit Criteria:** Informational (always succeeds if reached)

---

## Deployment Strategy

### GitHub Pages Deployment

**Environment:** `github-pages`

**URL:** https://chervonnyyanton.github.io/nutricount/

**Deployment Method:** GitHub Actions native Pages deployment

**Process:**
1. ✅ CI/CD Pipeline completes successfully
2. ✅ `workflow_run` trigger fires
3. ✅ Conditional check: `conclusion == 'success'`
4. ✅ Upload `demo/` directory as artifact
5. ✅ Deploy artifact to Pages
6. ✅ Wait 30 seconds for propagation
7. ✅ Run E2E tests on live URL
8. ✅ Generate deployment summary

**Permissions Required:**
```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

**Concurrency Control:**
```yaml
concurrency:
  group: "pages"
  cancel-in-progress: true
```

**Rollback Strategy:**
- Manual: Re-run previous successful deployment
- Automated: Planned for Week 6

**Monitoring:**
- GitHub Pages status dashboard
- E2E test results
- Deployment summary in workflow run

---

### Production Deployment (Raspberry Pi)

**Status:** Planned (not yet automated)

**Target Platform:**
- Raspberry Pi 4 Model B 2018
- ARM64 architecture
- Raspberry Pi OS Lite 64-bit

**Deployment Method:** Docker Compose

**Process (Manual):**
1. SSH to Raspberry Pi
2. Pull latest Docker image
3. Run `docker-compose up -d`
4. Health check
5. Monitor logs

**Future Automation (Week 6+):**
- Webhook-based deployment
- Automated health checks
- Rollback mechanism
- Blue-green deployment

---

## Quality Gates

### Gate 1: Linting
- **Enforced:** Yes
- **Blocking:** Yes
- **Criteria:** Zero flake8 errors

### Gate 2: Security Scanning
- **Enforced:** Yes
- **Blocking:** No (informational)
- **Criteria:** Review findings, document false positives

### Gate 3: Unit Tests
- **Enforced:** Yes
- **Blocking:** Yes
- **Criteria:** 844/844 tests pass (1 skip allowed)

### Gate 4: Code Coverage
- **Enforced:** Yes
- **Blocking:** No (informational)
- **Criteria:** Maintain 87-94% coverage

### Gate 5: Docker Build
- **Enforced:** Yes
- **Blocking:** Yes
- **Criteria:** Build + health check succeed

### Gate 6: Deployment Authorization
- **Enforced:** Yes
- **Blocking:** Yes (blocks downstream deployments)
- **Criteria:** All previous gates pass

### Gate 7: E2E Tests (Post-Deployment)
- **Enforced:** Yes
- **Blocking:** No (informational for now)
- **Criteria:** Playwright tests pass on live URL

---

## Security Integration

### Bandit Security Scanner

**Scan Scope:**
- `src/` directory (all Python modules)
- `app.py` (main application)

**Severity Levels:**
- Low and above (`-ll`)

**Common Findings:**
- Password hashing: ✅ Using bcrypt (secure)
- JWT tokens: ✅ Using PyJWT with HS256 (secure)
- SQL injection: ✅ Using parameterized queries
- XSS: ✅ Using Flask templating (auto-escaping)

**False Positives:**
- Documented in `SECURITY_FIXES_OCT23.md`
- Reviewed by security team

**Artifact Retention:**
- Reports stored for 30 days
- Historical trends tracked

### Dependency Scanning

**Tools:**
- Dependabot (GitHub native)
- pip-audit (planned)

**Coverage:**
- Python dependencies (`requirements.txt`, `requirements-minimal.txt`)
- npm dependencies (`package.json`)

**Update Strategy:**
- Security patches: Immediate
- Minor versions: Weekly review
- Major versions: Quarterly planning

---

## Testing Pyramid

### Level 1: Unit Tests (~70%)

**Location:** `tests/unit/`

**Coverage:**
- `src/config.py`: Configuration loading
- `src/utils.py`: Utility functions
- `src/security.py`: JWT, bcrypt
- `src/nutrition_calculator.py`: Calculations
- `src/fasting_manager.py`: Fasting logic
- `src/cache_manager.py`: Redis caching
- `src/monitoring.py`: Metrics

**Characteristics:**
- Fast execution (<1s per test)
- Isolated (mocked dependencies)
- Deterministic
- High coverage (90%+)

### Level 2: Integration Tests (~20%)

**Location:** `tests/integration/`

**Coverage:**
- API endpoints (products, dishes, logging, fasting)
- Authentication flows
- Database operations
- Multi-module interactions

**Characteristics:**
- Medium execution time (1-5s per test)
- Real database (SQLite in-memory)
- Real Flask test client
- HTTP-level testing

### Level 3: E2E Tests (~10%)

**Location:** `tests/e2e/` (pytest), `tests/e2e-playwright/` (Playwright)

**Coverage:**
- Complete user workflows
- UI interactions
- API + Database + Frontend integration
- Real-world scenarios

**Characteristics:**
- Slow execution (5-30s per test)
- Full stack testing
- Browser automation (Playwright)
- Production-like environment

### E2E Test Categories

1. **UI Workflows** (tests/e2e/test_enhanced_workflows.py)
   - Homepage loading
   - Static assets
   - Service worker registration

2. **API Workflows**
   - Product lifecycle
   - Dish lifecycle
   - Logging workflow
   - Profile workflow
   - GKI workflow

3. **System Workflows**
   - System status
   - Database maintenance
   - Export functionality

4. **Performance Workflows**
   - Bulk operations
   - Concurrent requests
   - Large data handling

5. **Security Workflows**
   - Authentication
   - Input validation
   - Rate limiting

6. **Playwright E2E** (tests/e2e-playwright/)
   - 120 tests (when enabled)
   - Tests both Local and Public versions
   - Full browser automation

---

## Monitoring & Observability

### Pipeline Metrics

**Available via GitHub Actions:**
- Workflow duration
- Job duration (per stage)
- Success/failure rate
- Test execution time
- Coverage trends

**GitHub Step Summary:**
- Deployment authorization
- Security scan results
- E2E test results
- Deployment URL

### Application Metrics

**Prometheus Integration:**
- Endpoint: `/metrics`
- Metrics:
  - Request count
  - Response time
  - Error rate
  - Active sessions
  - Database operations

**Health Endpoint:**
- Endpoint: `/health`
- Response: `{"status": "healthy"}`
- Used in Docker health checks

### Log Aggregation

**Current:**
- GitHub Actions logs (90 days retention)
- Application logs (local files)

**Future:**
- Centralized logging (ELK stack or similar)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Structured logging (JSON format)

---

## Future Enhancements

### Week 6 (Planned)

1. **Rollback Mechanism**
   - Detect deployment failures
   - Automatic rollback to previous version
   - Notification system

2. **Production Deployment Automation**
   - Webhook-based deployment to Raspberry Pi
   - Health checks
   - Zero-downtime deployments

3. **Enhanced Monitoring**
   - Uptime monitoring
   - Performance metrics
   - Alert system (Slack/Email)

### Beyond Week 6

1. **Blue-Green Deployments**
   - Zero-downtime updates
   - Instant rollback capability
   - Traffic routing

2. **Canary Deployments**
   - Gradual rollout
   - Risk mitigation
   - A/B testing capability

3. **Performance Testing**
   - Load testing (Locust)
   - Stress testing
   - Performance budgets

4. **Infrastructure as Code**
   - Terraform for cloud resources
   - Ansible for configuration management
   - GitOps workflow

5. **Multi-Environment Strategy**
   - Development
   - Staging
   - Production
   - Environment parity

---

## Comparison: Before vs After Week 5

| Aspect | Before Week 5 | After Week 5 |
|--------|---------------|--------------|
| **GitHub Pages Deployment** | Independent trigger | Dependent on CI/CD success ✅ |
| **E2E Testing** | Separate workflow | Integrated post-deployment ✅ |
| **Deployment Gate** | None | CI/CD success required ✅ |
| **Pipeline Stages** | 2 (Test, Build) | 3 (Test, Build, Deploy Auth) ✅ |
| **E2E on Live URL** | No | Yes (after Pages deployment) ✅ |
| **Rollback** | Manual only | Manual (Auto planned Week 6) |
| **Security Scanning** | Yes | Yes (enhanced reporting) ✅ |
| **Documentation** | Basic | Comprehensive (this doc) ✅ |

---

## Quick Reference

### Key Files
- `.github/workflows/test.yml` - Main CI/CD pipeline
- `.github/workflows/deploy-demo.yml` - GitHub Pages deployment
- `.github/workflows/e2e-tests.yml` - E2E tests (disabled)
- `requirements-minimal.txt` - CI/CD dependencies
- `pytest.ini` - Test configuration
- `.flake8` or `pyproject.toml` - Linting config

### Key Commands

**Local Testing:**
```bash
# Install dependencies
pip install -r requirements-minimal.txt

# Run linting
flake8 src/ app.py --max-line-length=100 --ignore=E501,W503,E226

# Run security scan
bandit -r src/ app.py -ll

# Run tests
pytest tests/ -v --cov=src --cov-report=xml

# Build Docker image
docker build -f dockerfile -t nutrition-tracker:latest .

# Test Docker image
docker run -d --name test-container -p 5000:5000 nutrition-tracker:latest
curl http://localhost:5000/health
docker stop test-container && docker rm test-container
```

**Manual Deployment:**
```bash
# Trigger CI/CD manually
# Go to Actions → CI/CD Pipeline → Run workflow

# Trigger Pages deployment manually
# Go to Actions → Deploy Demo to GitHub Pages → Run workflow
```

---

## Conclusion

The Week 5 CI/CD architecture represents a mature, production-ready pipeline with:
- ✅ Automated quality gates
- ✅ Security scanning
- ✅ Conditional deployments
- ✅ E2E testing on live deployments
- ✅ Comprehensive documentation

**Next Steps:** Week 6 will focus on automated rollback mechanisms and enhanced monitoring.

---

**Document Version:** 2.0  
**Author:** DevOps Team  
**Review Date:** October 23, 2025  
**Next Review:** Week 6 (Rollback implementation)
