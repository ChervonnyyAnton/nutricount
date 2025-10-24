# 🔄 Rollback Runbook

**Document Type**: Operational Runbook  
**Audience**: DevOps Engineers, Site Reliability Engineers, Developers  
**Last Updated**: October 24, 2025  
**Version**: 1.0

---

## 📋 Quick Reference

### When to Use This Runbook
- Production issue discovered after deployment
- E2E tests failing consistently post-deployment
- Critical functionality broken on live demo
- Security vulnerability deployed to production

### Prerequisites
- GitHub repository write access
- Understanding of the issue requiring rollback
- Knowledge of target version (or use automatic selection)

### Average Rollback Time
- **Automated Rollback**: < 2 minutes
- **Manual Rollback**: 3-5 minutes
- **Emergency Rollback**: 5-10 minutes

---

## 🚀 Standard Rollback Procedure

### Step 1: Assess the Situation

**Questions to Answer**:
1. What is the issue? (specific functionality broken, security issue, etc.)
2. How severe is the issue? (Critical/High/Medium/Low)
3. Is the previous version known to work correctly?
4. Are there any data migration concerns?

**Decision Tree**:
```
Is it a critical issue affecting all users?
├─ YES → Proceed with immediate rollback (Step 2)
└─ NO → Can we fix forward instead?
   ├─ YES → Consider hotfix PR instead of rollback
   └─ NO → Proceed with rollback (Step 2)
```

### Step 2: Trigger Rollback Workflow

#### Option A: Rollback to Previous Version (Recommended)

1. **Navigate to GitHub Actions**
   ```
   https://github.com/ChervonnyyAnton/nutricount/actions/workflows/rollback.yml
   ```

2. **Click "Run workflow"**

3. **Fill in the form**:
   - **Branch**: `main` (default)
   - **Reason**: Brief description (e.g., "E2E tests failing after deployment", "Product creation broken", "Security vulnerability in auth")
   - **Target commit**: Leave empty to use previous commit

4. **Click "Run workflow"**

5. **Monitor progress**: Watch the workflow run
   - Validation job should complete in ~30 seconds
   - Rollback job should complete in ~1-2 minutes
   - Smoke tests should complete in ~30 seconds

#### Option B: Rollback to Specific Version

**Use when**: You know exactly which version to restore

1. **Find target commit SHA**:
   ```bash
   # List recent commits
   git log --oneline -10
   
   # Or view on GitHub
   https://github.com/ChervonnyyAnton/nutricount/commits/main
   ```

2. **Follow Option A steps**, but:
   - **Target commit**: Enter specific commit SHA (e.g., `abc1234`)

3. **Verify commit details** in the workflow summary

### Step 3: Verify Rollback Success

#### Automated Checks (Built into Workflow)
- ✅ Deployment completes successfully
- ✅ Demo page is accessible
- ✅ Version file is available

#### Manual Verification (Recommended)

1. **Check Demo Accessibility**
   ```bash
   curl -f https://chervonnyyanton.github.io/nutricount/
   ```

2. **Verify Version**
   ```bash
   curl https://chervonnyyanton.github.io/nutricount/.deployment/VERSION
   ```
   
   Look for:
   - Correct commit SHA
   - "ROLLBACK INFORMATION" section
   - Rollback reason

3. **Test Critical Paths** (Manual smoke tests):
   - [ ] Home page loads
   - [ ] Can add a product
   - [ ] Can log food
   - [ ] Statistics display correctly
   - [ ] Dark/light theme works
   - [ ] Mobile view works

4. **Check Workflow Summary**
   - Review the workflow run summary in GitHub Actions
   - Verify all jobs completed successfully
   - Check smoke test results

### Step 4: Post-Rollback Actions

#### Immediate Actions

1. **Verify Incident Issue Created**
   - Check GitHub issues for new rollback incident
   - Should be tagged: `rollback`, `incident`, `priority-high`
   - Should be assigned to you

2. **Update Team**
   - Post in team chat (Slack/Discord)
   - Include: reason, target version, current status
   - Example:
     ```
     🔄 Rollback executed on nutricount demo
     Reason: E2E tests failing after deployment
     Status: ✅ Completed successfully
     Demo: https://chervonnyyanton.github.io/nutricount/
     Issue: #123
     ```

3. **Monitor for Issues**
   - Watch for user reports
   - Monitor error logs (if available)
   - Check E2E test results

#### Follow-up Actions (Within 24 hours)

1. **Investigate Root Cause**
   - Review commit that caused the issue
   - Identify what broke
   - Document findings in incident issue

2. **Create Fix Plan**
   - Design solution
   - Estimate effort
   - Identify testing needs

3. **Update Incident Issue**
   - Add root cause analysis
   - Add fix plan
   - Set timeline

4. **Implement Fix**
   - Create feature branch
   - Implement fix
   - Add tests to prevent regression
   - Submit PR

5. **Deploy Fix**
   - Wait for PR approval
   - Merge to main
   - Monitor deployment
   - Verify fix works

6. **Close Incident**
   - Document resolution
   - Close incident issue
   - Post-mortem if needed (for critical incidents)

---

## ⚠️ Rollback Guard Scenarios

### Scenario 1: Too Many Rollbacks (Loop Prevention)

**Symptom**: Rollback workflow fails with "Rollback Loop Detected"

**Cause**: More than 3 rollbacks in the last hour

**What This Means**:
- There's likely a systemic issue
- Automated rollback is blocked to prevent loop
- Manual investigation required

**Action**:
1. **STOP** - Don't attempt more rollbacks
2. **Investigate**:
   - What's causing repeated failures?
   - Is there a configuration issue?
   - Is the rollback target also broken?
3. **Fix Root Cause**:
   - Identify the actual problem
   - Fix it properly (don't just keep rolling back)
4. **Manual Verification**:
   - Test thoroughly before deploying
   - Consider deploying to a test environment first

**Override** (Use with extreme caution):
- Wait 1 hour for guard to reset
- Or manually edit workflow to adjust threshold
- Only if you're certain the next rollback will succeed

### Scenario 2: Old Target Version Warning

**Symptom**: Rollback workflow shows age warning

**Message**: "Warning: Target version is X days old"

**Threshold**: 30+ days

**What This Means**:
- Rolling back more than 30 days
- May lose recent features
- May introduce old bugs
- May have security vulnerabilities

**Action**:
1. **Verify Target Version**:
   - Is this really the version you want?
   - Check what changes will be lost
   - Review commit history

2. **Consider Alternatives**:
   - Can you rollback to a more recent version?
   - Can you fix forward instead?

3. **If Proceeding**:
   - Document why you're rolling back so far
   - Plan to restore lost features
   - Schedule security review

---

## 🚨 Emergency Rollback (When Automated Fails)

### When to Use
- Rollback workflow is failing
- GitHub Actions is unavailable
- Need immediate rollback

### Prerequisites
- GitHub CLI (`gh`) installed
- Git installed
- Repository cloned locally

### Procedure

#### Step 1: Identify Target Version
```bash
# Clone repository if not already done
git clone https://github.com/ChervonnyyAnton/nutricount.git
cd nutricount

# Find target commit
git log --oneline -10

# Or check deployment history
gh api /repos/ChervonnyyAnton/nutricount/deployments \
  --jq '.[] | select(.environment=="github-pages") | {sha, created_at, description}'
```

#### Step 2: Checkout Target Version
```bash
# Checkout target commit
git checkout <target-commit-sha>

# Verify this is the correct version
git log --oneline -1
git show HEAD:demo/index.html | head -20  # Check demo content
```

#### Step 3: Manual Deployment Trigger

**Option A: Via GitHub CLI**
```bash
# Trigger deployment workflow manually
gh workflow run deploy-demo.yml --ref <target-commit-sha>

# Monitor workflow
gh run watch
```

**Option B: Via GitHub Web UI**
1. Go to: https://github.com/ChervonnyyAnton/nutricount/actions/workflows/deploy-demo.yml
2. Click "Run workflow"
3. Select branch/tag with target commit
4. Click "Run workflow"

**Option C: Direct Pages Deployment** (Last resort)
1. Go to repository Settings → Pages
2. Change source to `main` branch (temporarily)
3. Wait for deployment
4. Change back to GitHub Actions

#### Step 4: Verify Emergency Rollback
```bash
# Wait for deployment (2-3 minutes)
sleep 180

# Test demo
curl -f https://chervonnyyanton.github.io/nutricount/

# Check version
curl https://chervonnyyanton.github.io/nutricount/.deployment/VERSION
```

#### Step 5: Create Manual Incident Report
```bash
# Create issue via CLI
gh issue create \
  --title "🚨 Emergency Rollback: <reason>" \
  --body "Emergency rollback performed manually due to: <reason>

**Details**:
- Date: $(date -u)
- Rolled back from: $PREVIOUS_COMMIT
- Rolled back to: $TARGET_COMMIT
- Performed by: $(git config user.name)

**Root Cause**: <to be investigated>

**Next Steps**:
- [ ] Investigate root cause
- [ ] Fix issue
- [ ] Deploy fix
- [ ] Close incident" \
  --label "rollback,incident,priority-critical,manual"
```

---

## 📊 Rollback Metrics & Monitoring

### Key Metrics to Track

1. **Rollback Frequency**
   - Target: < 1 rollback per month
   - Alert if: > 3 rollbacks per month

2. **Mean Time to Rollback (MTTR)**
   - Target: < 2 minutes (automated)
   - Target: < 5 minutes (manual)

3. **Rollback Success Rate**
   - Target: > 95%
   - Alert if: < 90%

4. **Time to Resolution**
   - Target: < 24 hours (incident to fix deployed)
   - Alert if: > 48 hours

### How to Check Metrics

**View Rollback History**:
```bash
# List all rollback workflow runs
gh run list --workflow=rollback.yml --limit 50

# Get detailed run information
gh run view <run-id>

# Export to CSV for analysis
gh run list --workflow=rollback.yml --json conclusion,createdAt,displayTitle \
  --jq '.[] | [.createdAt, .displayTitle, .conclusion] | @csv'
```

**View Incident Issues**:
```bash
# List rollback incidents
gh issue list --label rollback --state all

# Get incident statistics
gh issue list --label rollback --state all --json number,title,createdAt,closedAt \
  --jq '.[] | {number, title, created: .createdAt, closed: .closedAt, duration: ((.closedAt | fromdate) - (.createdAt | fromdate))}'
```

---

## 🔍 Troubleshooting Common Issues

### Issue 1: Rollback Workflow Fails to Start

**Symptoms**:
- Workflow dispatch doesn't trigger
- No workflow run appears

**Possible Causes**:
- Insufficient permissions
- Workflow file syntax error
- Branch protection rules

**Solutions**:
1. Check GitHub permissions
2. Validate workflow YAML: https://www.yamllint.com/
3. Try manual deployment via CLI
4. Check GitHub Status: https://www.githubstatus.com/

### Issue 2: Deployment Step Fails

**Symptoms**:
- Validation passes but deployment fails
- Error: "deploy-pages failed"

**Possible Causes**:
- GitHub Pages service issues
- Artifact too large
- Invalid artifact contents

**Solutions**:
1. Check artifact size (should be < 100MB)
2. Verify demo folder contents
3. Retry workflow
4. Check GitHub Pages status
5. Try emergency rollback procedure

### Issue 3: Smoke Tests Fail After Rollback

**Symptoms**:
- Deployment succeeds but smoke tests fail
- Demo not accessible

**Possible Causes**:
- Deployment not propagated yet
- CDN cache not updated
- Target version also broken

**Solutions**:
1. Wait 2-3 minutes for CDN propagation
2. Clear browser cache and retry
3. Try accessing from different location/device
4. If persistent, rollback to earlier version
5. Create incident issue for investigation

### Issue 4: Version File Not Accessible

**Symptoms**:
- Demo works but .deployment/VERSION 404

**Possible Causes**:
- Artifact creation step failed silently
- GitHub Pages configuration issue

**Impact**: **Low** - Demo still works, just no version info

**Solutions**:
1. Check workflow logs for artifact creation
2. Verify demo/.deployment folder created
3. Re-run deployment if critical
4. Create issue to fix in next deployment

---

## 📞 Escalation Path

### When to Escalate

1. **Critical Outage** (>30 minutes)
   - Demo completely unavailable
   - Multiple rollback attempts failed
   - GitHub Pages service down

2. **Data Loss Risk**
   - Database corruption suspected
   - User data at risk
   - Security breach

3. **Repeated Failures**
   - Same issue after 2+ rollbacks
   - Unable to identify root cause
   - Need architectural changes

### Escalation Contacts

**Level 1: Team Lead**
- @ChervonnyyAnton (GitHub)
- Contact via: GitHub issues, team chat

**Level 2: Repository Owner**
- Contact via: GitHub direct message
- For: Permission issues, critical decisions

**Level 3: GitHub Support**
- https://support.github.com/
- For: Platform issues, service outages

---

## 📚 Related Documentation

### Internal Docs
- [Rollback Strategy](rollback-strategy.md) - Design document
- [INTEGRATED_ROADMAP.md](../../INTEGRATED_ROADMAP.md) - Project roadmap
- [WEEK6_PLANNING.md](../../WEEK6_PLANNING.md) - Current sprint planning

### Workflows
- [.github/workflows/rollback.yml](../../.github/workflows/rollback.yml) - Rollback workflow
- [.github/workflows/deploy-demo.yml](../../.github/workflows/deploy-demo.yml) - Deployment workflow
- [.github/workflows/test.yml](../../.github/workflows/test.yml) - CI/CD pipeline

### External Resources
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Incident Response Best Practices](https://www.atlassian.com/incident-management/incident-response)

---

## 🔄 Runbook Maintenance

### Update Frequency
- Review quarterly
- Update after each rollback incident
- Update when workflows change

### Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-24 | 1.0 | Initial version | @ChervonnyyAnton |

### Feedback
Found an issue or have suggestions? Create an issue with label `runbook-feedback`

---

**Last Reviewed**: October 24, 2025  
**Next Review**: January 24, 2026  
**Status**: Active
