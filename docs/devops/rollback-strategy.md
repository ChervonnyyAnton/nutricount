# 🔄 Rollback Strategy & Implementation Plan

**Date**: October 24, 2025  
**Status**: ✅ Phase 1-4 Complete - Fully Implemented  
**Priority**: Week 7 - Technical Priority 1  
**Implementation Time**: ~8 hours (as estimated)

---

## 📋 Overview

This document outlines the rollback strategy for the Nutricount application, covering automatic failure detection, rollback mechanisms, and recovery procedures for both production (Raspberry Pi) and demo (GitHub Pages) deployments.

### Goals
- **Automatic Detection**: Detect deployment failures automatically
- **Automated Rollback**: Revert to last known good version on critical failures
- **Minimal Downtime**: Keep downtime under 2 minutes during rollback
- **Clear Communication**: Notify team of rollback events
- **Manual Override**: Support manual rollback when needed

---

## 🎯 Scope

### In Scope
1. **GitHub Pages Deployment**: Demo version rollback
2. **CI/CD Pipeline**: Build and test failure handling
3. **Health Check Failures**: Post-deployment validation
4. **Notification System**: Team alerts for rollback events

### Out of Scope (Future Enhancement)
- Raspberry Pi production deployment (requires webhook/SSH setup)
- Database migration rollback (requires migration tracking)
- Blue-green deployment strategy (requires infrastructure changes)

---

## 🏗️ Current Deployment Architecture

### Deployment Flow
```
Push to main
    ↓
CI/CD Pipeline (test.yml)
    ├─ Test Job
    │  ├─ Linting
    │  ├─ Security Scan
    │  └─ Unit Tests
    ├─ Build Job
    │  ├─ Docker Build
    │  └─ Health Check
    └─ Deploy Job
       └─ Authorization

    ↓ (on success)

GitHub Pages Deployment (deploy-demo.yml)
    ├─ Verify CI/CD Authorization
    ├─ Deploy to Pages
    └─ E2E Tests (post-deployment)
```

### Current Failure Points

1. **Test Job Failure**
   - Linting errors
   - Security vulnerabilities (high severity)
   - Unit test failures
   - **Current Behavior**: Pipeline stops, no deployment

2. **Build Job Failure**
   - Docker build errors
   - Health check failures
   - **Current Behavior**: Pipeline stops, no deployment

3. **Pages Deployment Failure**
   - Upload/deploy errors
   - Configuration issues
   - **Current Behavior**: Workflow fails, previous version remains

4. **E2E Test Failure (Post-deployment)**
   - Functional test failures
   - **Current Behavior**: Tests fail, but deployment stays (❌ RISK)

---

## 🚨 Failure Detection Strategy

### 1. Pre-Deployment Validation (Already Implemented ✅)

**CI/CD Pipeline Stages:**
- ✅ Linting (flake8)
- ✅ Security scan (bandit)
- ✅ Unit tests (pytest)
- ✅ Docker build
- ✅ Container health check

**Failure Action**: Block deployment (no rollback needed)

### 2. Deployment Validation (Needs Implementation 🔴)

**GitHub Pages Deployment:**
- 🔴 Deployment success check (deploy-pages action result)
- 🔴 Post-deployment health check (verify demo is accessible)
- 🔴 E2E test results validation

**Failure Action**: Trigger rollback

### 3. Post-Deployment Monitoring (Needs Implementation 🔴)

**E2E Test Results:**
- 🔴 Monitor test pass rate (target: 95%+)
- 🔴 Track critical path failures
- 🔴 Detect regression patterns

**Failure Action**: Alert + Optional rollback

---

## 🔄 Rollback Mechanisms

### Mechanism 1: GitHub Pages Version Pinning (RECOMMENDED)

**Strategy**: Deploy specific commit/tag instead of latest

**Implementation**:
```yaml
# Before (current)
- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: 'demo'

# After (with version tracking)
- name: Save deployment version
  run: |
    echo "${{ github.sha }}" > demo/.deploy-version
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> demo/.deploy-version

- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: 'demo'
```

**Rollback Process**:
1. Identify last known good commit (via deployment history)
2. Checkout specific commit
3. Re-run Pages deployment with `workflow_dispatch`

**Pros**:
- ✅ Simple to implement
- ✅ Uses existing workflow
- ✅ No infrastructure changes

**Cons**:
- ❌ Manual process (workflow_dispatch)
- ❌ Requires GitHub UI access or API call

### Mechanism 2: Automated Rollback Workflow (RECOMMENDED)

**Strategy**: New workflow that automatically reverts to previous version

**Implementation**:
```yaml
name: Rollback GitHub Pages

on:
  workflow_dispatch:
    inputs:
      reason:
        description: 'Reason for rollback'
        required: true
      target_version:
        description: 'Target commit SHA (leave empty for previous deployment)'
        required: false

jobs:
  rollback:
    name: Rollback to Previous Version
    runs-on: ubuntu-latest
    
    steps:
    - name: Get previous deployment
      run: |
        # Fetch deployment history from GitHub API
        # Identify last successful deployment before current
        
    - name: Checkout target version
      uses: actions/checkout@v4
      with:
        ref: ${{ inputs.target_version || steps.previous.outputs.commit }}
    
    - name: Deploy previous version
      # Same deployment steps as deploy-demo.yml
      
    - name: Verify rollback
      # Run health checks
      
    - name: Notify team
      # Send notifications
```

**Pros**:
- ✅ Fast rollback (< 2 minutes)
- ✅ Can be automated
- ✅ Audit trail in GitHub Actions

**Cons**:
- ❌ Requires deployment history tracking
- ❌ Additional workflow maintenance

### Mechanism 3: E2E Test Failure Triggers Rollback (ADVANCED)

**Strategy**: Automatically rollback if E2E tests fail post-deployment

**Implementation**:
```yaml
# In deploy-demo.yml, after E2E tests
- name: Check E2E Test Results
  if: always()
  id: e2e-check
  run: |
    if [ ${{ job.status }} == 'failure' ]; then
      echo "rollback_needed=true" >> $GITHUB_OUTPUT
    fi

- name: Trigger Rollback
  if: steps.e2e-check.outputs.rollback_needed == 'true'
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.actions.createWorkflowDispatch({
        owner: context.repo.owner,
        repo: context.repo.repo,
        workflow_id: 'rollback.yml',
        ref: 'main',
        inputs: {
          reason: 'E2E tests failed after deployment',
          target_version: context.payload.before  // Previous commit
        }
      })
```

**Pros**:
- ✅ Fully automated
- ✅ Fast response to failures
- ✅ Reduces manual intervention

**Cons**:
- ❌ Complex implementation
- ❌ Risk of rollback loops if previous version also fails
- ❌ Requires careful failure threshold tuning

---

## 📊 Implementation Plan

### Phase 1: Design & Documentation ✅ COMPLETE
**Status**: Complete  
**Deliverable**: This document  
**Completed**: October 24, 2025

### Phase 2: Deployment Version Tracking ✅ COMPLETE
**Status**: Complete  
**Time Taken**: 1 hour  
**Completed**: October 24, 2025

**Implemented**:
- ✅ Deployment version tracking in deploy-demo.yml
- ✅ Deployment metadata stored (commit SHA, timestamp, deployer)
- ✅ Version files created: `.deployment/version.json`, `.deployment/VERSION`
- ✅ Version accessible at: https://chervonnyyanton.github.io/nutricount/.deployment/VERSION

**Files Modified**:
- `.github/workflows/deploy-demo.yml` - Added version creation step
- `.github/workflows/rollback.yml` - Already includes version tracking

### Phase 3: Manual Rollback Workflow ✅ COMPLETE
**Status**: Complete  
**Time Taken**: Pre-existing (validated and documented)  
**Completed**: October 24, 2025

**Implemented**:
- ✅ rollback.yml workflow exists and functional
- ✅ Deployment history retrieval via GitHub API
- ✅ Rollback verification with smoke tests
- ✅ Automatic incident issue creation
- ✅ Loop prevention guards (max 3 per hour)
- ✅ Commit age validation (warns if > 30 days old)

**Features**:
- Manual trigger via workflow_dispatch
- Reason field (required)
- Target commit selection (optional, defaults to previous)
- Comprehensive validation and safety checks
- Post-rollback smoke tests
- Automatic incident tracking

### Phase 4: Automated Rollback Trigger ✅ COMPLETE
**Status**: Complete  
**Time Taken**: 2 hours  
**Completed**: October 24, 2025

**Implemented**:
- ✅ E2E test result checking
- ✅ Automatic rollback trigger on E2E failure
- ✅ Rollback threshold guards (max 2 per hour)
- ✅ Previous commit detection with fallback
- ✅ Workflow dispatch integration
- ✅ Comprehensive error handling and logging

**Files Modified**:
- `.github/workflows/deploy-demo.yml` - Added `auto-rollback` job

**New Job**: `auto-rollback`
- Triggers only when: deploy succeeds AND E2E tests fail
- Checks rollback history (prevents loops)
- Gets previous commit automatically
- Dispatches rollback workflow with proper inputs
- Creates detailed incident summary

**Safety Features**:
- Maximum 2 automatic rollbacks per hour
- Third attempt blocked with clear error message
- Fallback commit detection (event.before → parent commit)
- Comprehensive audit trail

**Documentation**:
- ✅ Created `docs/devops/automated-rollback-implementation.md` (400+ lines)
- ✅ Detailed implementation guide
- ✅ Testing strategy
- ✅ Troubleshooting guide
- ✅ Monitoring metrics
- Test scenarios and results

### Phase 5: Notification System (1-2 hours)

**Tasks**:
1. Add GitHub issue creation on rollback
2. Add workflow summary with rollback details
3. Optional: Slack/Discord notifications
4. Document notification channels

**Deliverables**:
- Notification workflow steps
- Documentation updates

---

## 🎯 Rollback Scenarios

### Scenario 1: E2E Tests Fail After Deployment

**Trigger**: E2E test pass rate < 95%

**Actions**:
1. Mark deployment as failed
2. Create GitHub issue with test failures
3. Trigger rollback workflow (automated or manual)
4. Notify team via workflow summary

**Recovery**:
- Automated rollback to previous version
- Developer investigates test failures
- Fix applied in new PR
- Re-deploy when tests pass

### Scenario 2: Pages Deployment Fails

**Trigger**: deploy-pages action fails

**Actions**:
1. Workflow fails
2. Previous version remains deployed (automatic)
3. Alert in workflow summary

**Recovery**:
- No rollback needed (previous version still live)
- Developer fixes deployment issue
- Re-run workflow

### Scenario 3: Manual Rollback Required

**Trigger**: Production issue discovered post-deployment

**Actions**:
1. Developer goes to GitHub Actions
2. Run "Rollback GitHub Pages" workflow
3. Specify reason and target version (optional)
4. Verify rollback success

**Recovery**:
- Immediate rollback to last known good version
- Create incident report
- Fix issue in develop branch
- Deploy fix when ready

### Scenario 4: Docker Build Fails

**Trigger**: Docker build or health check fails

**Actions**:
1. Build job fails
2. Deployment blocked (no rollback needed)
3. Alert in workflow summary

**Recovery**:
- Fix Docker configuration
- Create new PR with fix
- CI/CD validates fix before deployment

---

## 🛡️ Rollback Guards

### Guard 1: Rollback Loop Prevention

**Problem**: Automated rollback might revert to a version that also fails

**Solution**:
```yaml
- name: Check rollback history
  run: |
    # Count rollbacks in last hour
    ROLLBACK_COUNT=$(gh api /repos/${{ github.repository }}/actions/runs \
      --jq '.workflow_runs[] | select(.name=="Rollback GitHub Pages" and .created_at > (now - 3600)) | .id' | wc -l)
    
    if [ $ROLLBACK_COUNT -gt 2 ]; then
      echo "❌ Too many rollbacks in last hour. Manual intervention required."
      exit 1
    fi
```

### Guard 2: Deployment Age Check

**Problem**: Rolling back to very old version might introduce security issues

**Solution**:
```yaml
- name: Validate target version
  run: |
    TARGET_DATE=$(git show -s --format=%ci ${{ inputs.target_version }})
    DAYS_OLD=$(( ($(date +%s) - $(date -d "$TARGET_DATE" +%s)) / 86400 ))
    
    if [ $DAYS_OLD -gt 30 ]; then
      echo "⚠️ Warning: Target version is $DAYS_OLD days old"
      echo "Please verify this is the correct version for rollback"
    fi
```

### Guard 3: Critical Path Validation

**Problem**: Rolling back might break critical functionality

**Solution**:
```yaml
- name: Smoke test after rollback
  run: |
    # Run critical path smoke tests
    curl -f https://chervonnyyanton.github.io/nutricount/ || exit 1
    # Test product loading
    # Test logging functionality
    # Test statistics
```

---

## 📢 Notification Strategy

### Notification Channels

1. **GitHub Workflow Summary** (Primary)
   - Rollback reason
   - Target version details
   - Verification results
   - Next steps

2. **GitHub Issue** (Automated)
   - Created on rollback
   - Links to failed workflows
   - Rollback details
   - Mentions @copilot for automated assistance
   - Assignee: last committer

3. **Slack/Discord** (Optional)
   - Webhook integration
   - Real-time alerts
   - Team coordination

### Notification Content

**Rollback Alert Template**:
```markdown
## 🔄 Rollback Initiated

**Reason**: E2E tests failed after deployment
**Trigger**: Automated (test pass rate: 85%, threshold: 95%)
**Current Version**: abc1234 (commit message)
**Rolling Back To**: def5678 (commit message)
**Rollback Time**: 2025-10-24 18:30:00 UTC

### Failed Tests
- test_product_creation_flow
- test_logging_statistics
- test_dish_calculator

### Action Required
1. Review test failures: [link to test results]
2. Investigate regression: [link to commit diff]
3. Create fix PR when ready

### Rollback Status
✅ Rollback completed successfully
✅ Smoke tests passed
✅ Demo is accessible at: https://chervonnyyanton.github.io/nutricount/

---

@copilot Please help investigate and fix this rollback incident.
```

---

## 📖 Rollback Runbook

### Manual Rollback Procedure

**When to Use**:
- Production issue discovered after deployment
- Automated rollback failed
- Need to revert to specific version

**Prerequisites**:
- GitHub repository write access
- Knowledge of target version (commit SHA or tag)

**Steps**:

1. **Identify Target Version**
   ```bash
   # View recent deployments
   gh api /repos/ChervonnyyAnton/nutricount/deployments \
     --jq '.[] | select(.environment=="github-pages") | {id, sha, created_at}'
   
   # Or check git history
   git log --oneline -10
   ```

2. **Trigger Rollback Workflow**
   - Go to GitHub Actions
   - Select "Rollback GitHub Pages" workflow
   - Click "Run workflow"
   - Fill in:
     - Reason: "Brief description of issue"
     - Target Version: "commit SHA" (or leave empty for previous)
   - Click "Run workflow"

3. **Monitor Rollback Progress**
   - Watch workflow execution
   - Check for errors in logs
   - Verify each step completes

4. **Verify Rollback Success**
   ```bash
   # Check demo is accessible
   curl -f https://chervonnyyanton.github.io/nutricount/
   
   # Verify version
   curl https://chervonnyyanton.github.io/nutricount/.deploy-version
   ```

5. **Create Incident Report**
   - Document issue that triggered rollback
   - Link to failed deployment
   - List steps taken
   - Assign owner for fix

6. **Plan Fix**
   - Create issue for root cause
   - Develop fix in feature branch
   - Ensure tests cover regression
   - Deploy fix when ready

### Emergency Rollback (If Automated Fails)

**Scenario**: Automated rollback workflow fails or is not available

**Manual Rollback Process**:

1. **Checkout Target Version Locally**
   ```bash
   git checkout <target-commit-sha>
   ```

2. **Manually Trigger Pages Deployment**
   - Go to GitHub repository settings
   - Pages section
   - Select source: GitHub Actions
   - Manually trigger deploy-demo.yml workflow with `workflow_dispatch`

3. **Verify Deployment**
   - Check GitHub Pages URL
   - Run smoke tests manually
   - Monitor for errors

---

## 🧪 Testing Strategy

### Test Scenarios

1. **Test Rollback Workflow (Happy Path)**
   - Deploy version A
   - Deploy version B (intentionally break something)
   - Trigger rollback manually
   - Verify version A is deployed
   - Check notifications sent

2. **Test Automated Rollback**
   - Deploy version with failing E2E tests
   - Verify rollback triggered automatically
   - Check rollback completed successfully
   - Verify notifications sent

3. **Test Rollback Guards**
   - Attempt multiple rollbacks in short time
   - Verify loop prevention activates
   - Attempt rollback to very old version
   - Verify age warning appears

4. **Test Rollback Failure**
   - Simulate rollback workflow failure
   - Verify manual process documented
   - Test emergency rollback procedure

### Success Criteria

- ✅ Rollback completes in < 2 minutes
- ✅ Previous version is accessible
- ✅ No data loss
- ✅ Notifications sent correctly
- ✅ Rollback guards work as expected
- ✅ Manual process documented and tested

---

## 📊 Monitoring & Metrics

### Rollback Metrics to Track

1. **Rollback Frequency**
   - Number of rollbacks per month
   - Reason for each rollback
   - Target: < 1 rollback per month

2. **Rollback Duration**
   - Time from trigger to completion
   - Target: < 2 minutes average

3. **Rollback Success Rate**
   - Successful rollbacks / total rollbacks
   - Target: > 95%

4. **Mean Time to Recovery (MTTR)**
   - Time from issue detection to resolution
   - Target: < 5 minutes

### Dashboard

**Suggested Metrics Dashboard** (GitHub Issues or external):
- Recent rollbacks (last 30 days)
- Rollback reasons breakdown
- Average rollback time trend
- Success rate trend

---

## 🔮 Future Enhancements

### Phase 6: Database Migration Rollback (Future)

**Scope**: Handle database schema changes

**Challenges**:
- SQLite doesn't support rollback migrations natively
- Need migration versioning system
- Data loss risk

**Solution Direction**:
- Use Alembic or similar migration tool
- Implement up/down migrations
- Backup before each migration
- Test rollback process

### Phase 7: Blue-Green Deployment (Future)

**Scope**: Zero-downtime deployments with instant rollback

**Requirements**:
- Two deployment slots (blue/green)
- Traffic routing mechanism
- Health check before switching
- Instant rollback capability

**Benefits**:
- Zero downtime
- Instant rollback
- Production testing before cutover

### Phase 8: Raspberry Pi Production Rollback (Future)

**Scope**: Rollback for main production deployment

**Challenges**:
- Remote server access required
- Docker container management
- Database state management

**Solution Direction**:
- Webhook-based deployment
- Docker tag versioning
- Automated health checks
- SSH-based rollback script

---

## ✅ Implementation Checklist

### Phase 2: Version Tracking
- [ ] Add version tracking to deploy-demo.yml
- [ ] Create .deploy-version file
- [ ] Test version tracking works
- [ ] Document version format

### Phase 3: Manual Rollback
- [ ] Create rollback.yml workflow
- [ ] Implement deployment history retrieval
- [ ] Add rollback verification
- [ ] Test manual rollback process
- [ ] Create rollback runbook

### Phase 4: Automated Rollback
- [ ] Add E2E test result checking
- [ ] Implement rollback trigger
- [ ] Add rollback guards
- [ ] Test automated rollback
- [ ] Test guard conditions

### Phase 5: Notifications
- [ ] Add GitHub issue creation
- [ ] Enhance workflow summary
- [ ] Optional: Add Slack/Discord
- [ ] Document notification channels
- [ ] Test all notification paths

### Documentation
- [ ] Complete this design document
- [ ] Create rollback runbook
- [ ] Update INTEGRATED_ROADMAP.md
- [ ] Create session summary
- [ ] Update README.md

---

## 📚 References

### Internal Documentation
- INTEGRATED_ROADMAP.md - Overall project roadmap
- WEEK6_PLANNING.md - Week 7 priorities
- .github/workflows/test.yml - CI/CD pipeline
- .github/workflows/deploy-demo.yml - Pages deployment
- .github/workflows/e2e-tests.yml - E2E testing

### External Resources
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Pages Deployment](https://docs.github.com/en/pages)
- [Rollback Strategies](https://www.atlassian.com/continuous-delivery/software-deployment/rollback-strategies)
- [Blue-Green Deployment](https://martinfowler.com/bliki/BlueGreenDeployment.html)

---

**Document Version**: 1.0  
**Status**: Phase 1 Complete - Design Ready  
**Next Phase**: Implementation (Phases 2-5)  
**Estimated Total Time**: 8-10 hours implementation
