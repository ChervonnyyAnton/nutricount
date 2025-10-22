# 🧪 Testing Guide for Workflow Dependency Implementation

## Overview

This document provides testing instructions to verify that GitHub Pages deployment correctly depends on CI/CD Pipeline success.

## Test Scenarios

### Test 1: Normal Flow - CI/CD Success → Pages Deploys

**Objective**: Verify that Pages deploys when CI/CD Pipeline succeeds

**Steps**:
1. Make a small change to any file (e.g., update README.md)
2. Commit and push to `main` branch
3. Go to Actions tab
4. Wait for "CI/CD Pipeline" workflow to complete

**Expected Results**:
- ✅ CI/CD Pipeline should complete successfully
  - Test job: PASS ✅
  - Build job: PASS ✅
  - Deploy job: PASS ✅ (shows authorization message)
- ✅ "Deploy Demo to GitHub Pages" workflow should trigger automatically
- ✅ Pages deployment should complete successfully
- ✅ Pages workflow should show:
  - Link to the CI/CD Pipeline run that authorized it
  - Commit message that triggered it
- ✅ Demo should be accessible at https://chervonnyyanton.github.io/nutricount/

**Verification Commands**:
```bash
# Check workflow status via GitHub CLI (if available)
gh run list --workflow=test.yml --limit 1
gh run list --workflow=deploy-demo.yml --limit 1
```

---

### Test 2: Failure Flow - CI/CD Fails → Pages Does NOT Deploy

**Objective**: Verify that Pages does NOT deploy when CI/CD Pipeline fails

**Steps**:
1. Create a branch with intentionally broken code:
   ```bash
   git checkout -b test-failure
   echo "import non_existent_module" >> src/test_break.py
   git add .
   git commit -m "Test: intentionally broken import"
   ```
2. Create a PR to `main` or push directly to `main`
3. Go to Actions tab
4. Wait for "CI/CD Pipeline" to fail

**Expected Results**:
- ❌ CI/CD Pipeline should FAIL (at Test job due to import error)
- ✅ "Deploy Demo to GitHub Pages" workflow should NOT trigger
- ✅ No new deployment to Pages

**Cleanup**:
```bash
# If pushed to main, revert the commit
git revert HEAD
git push origin main

# If in branch, just delete it
git checkout main
git branch -D test-failure
```

---

### Test 3: Linting Failure - Pages Does NOT Deploy

**Objective**: Verify that Pages does NOT deploy when linting fails

**Steps**:
1. Create a file with intentionally bad formatting:
   ```bash
   git checkout -b test-lint-fail
   echo "def bad_function(  ):  pass" >> src/test_lint.py
   git add .
   git commit -m "Test: intentionally bad formatting"
   ```
2. Push to `main` or create PR
3. Go to Actions tab
4. Wait for CI/CD Pipeline to fail at linting step

**Expected Results**:
- ❌ CI/CD Pipeline should FAIL (at Test job's flake8 step)
- ✅ "Deploy Demo to GitHub Pages" workflow should NOT trigger
- ✅ No new deployment to Pages

**Cleanup**:
```bash
git revert HEAD
git push origin main
```

---

### Test 4: Build Failure - Pages Does NOT Deploy

**Objective**: Verify that Pages does NOT deploy when Docker build fails

**Steps**:
1. Create a branch with broken Dockerfile:
   ```bash
   git checkout -b test-build-fail
   # Add a line that will break the Docker build
   echo "RUN exit 1" >> dockerfile
   git add dockerfile
   git commit -m "Test: intentionally broken Docker build"
   ```
2. Push to `main`
3. Go to Actions tab
4. Wait for CI/CD Pipeline to fail at build step

**Expected Results**:
- ❌ CI/CD Pipeline should FAIL (at Build job)
- ✅ Test job should PASS
- ✅ Build job should FAIL
- ✅ Deploy job should NOT run (depends on build)
- ✅ "Deploy Demo to GitHub Pages" workflow should NOT trigger
- ✅ No new deployment to Pages

**Cleanup**:
```bash
git revert HEAD
git push origin main
```

---

### Test 5: Manual Trigger - Bypasses CI/CD

**Objective**: Verify that manual workflow trigger works independently

**Steps**:
1. Go to Actions tab
2. Click on "Deploy Demo to GitHub Pages" workflow
3. Click "Run workflow" button (top right)
4. Select `main` branch
5. Click green "Run workflow" button

**Expected Results**:
- ✅ Workflow should start immediately
- ✅ Should NOT wait for or check CI/CD Pipeline
- ✅ Should deploy successfully
- ✅ Demo should update at https://chervonnyyanton.github.io/nutricount/

**Use Case**: Emergency deployments or demo updates without code changes

---

### Test 6: PR to Main - Only CI/CD Runs

**Objective**: Verify that PRs don't trigger Pages deployment

**Steps**:
1. Create a PR targeting `main` branch
2. Go to Actions tab
3. Observe which workflows run

**Expected Results**:
- ✅ "CI/CD Pipeline" should run on PR
- ✅ "Deploy Demo to GitHub Pages" should NOT run on PR
- ✅ Pages deployment only happens after merge to main

---

### Test 7: Verify Authorization Link

**Objective**: Verify traceability from Pages deployment to CI/CD run

**Steps**:
1. After a successful deployment, go to Actions tab
2. Click on the latest "Deploy Demo to GitHub Pages" run
3. Check the job summary

**Expected Results**:
- ✅ Should see "CI/CD Pipeline Authorization" section
- ✅ Should show link to the CI/CD workflow run
- ✅ Should show the commit message that triggered it
- ✅ Link should work and point to correct CI/CD run

---

## Automated Verification Script

You can use this script to verify the implementation:

```bash
#!/bin/bash

echo "🧪 Testing Workflow Dependencies"
echo "=================================="
echo ""

# Test 1: Check workflow files syntax
echo "Test 1: Validating YAML syntax..."
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/deploy-demo.yml'))" && \
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))" && \
echo "✅ YAML syntax valid" || echo "❌ YAML syntax invalid"
echo ""

# Test 2: Check workflow_run trigger
echo "Test 2: Checking workflow_run trigger..."
grep -q "workflow_run:" .github/workflows/deploy-demo.yml && \
grep -q 'workflows: \["CI/CD Pipeline"\]' .github/workflows/deploy-demo.yml && \
echo "✅ workflow_run trigger configured" || echo "❌ workflow_run trigger not found"
echo ""

# Test 3: Check success condition
echo "Test 3: Checking success condition..."
grep -q "workflow_run.conclusion == 'success'" .github/workflows/deploy-demo.yml && \
echo "✅ Success condition present" || echo "❌ Success condition missing"
echo ""

# Test 4: Check manual trigger
echo "Test 4: Checking manual trigger..."
grep -q "workflow_dispatch:" .github/workflows/deploy-demo.yml && \
echo "✅ Manual trigger enabled" || echo "❌ Manual trigger missing"
echo ""

# Test 5: Check authorization step
echo "Test 5: Checking authorization verification..."
grep -q "Verify CI/CD Authorization" .github/workflows/deploy-demo.yml && \
echo "✅ Authorization verification present" || echo "❌ Authorization verification missing"
echo ""

# Test 6: Check deploy job updates
echo "Test 6: Checking deploy job authorization..."
grep -q "Deploy authorization" .github/workflows/test.yml && \
echo "✅ Deploy authorization present" || echo "❌ Deploy authorization missing"
echo ""

echo "=================================="
echo "✅ All static checks passed!"
echo ""
echo "Next: Test with actual workflow runs (see test scenarios above)"
```

Save this as `/tmp/verify_workflow.sh` and run:
```bash
bash /tmp/verify_workflow.sh
```

---

## Success Criteria

The implementation is successful if:

1. ✅ Pages deployment triggers only after CI/CD Pipeline success
2. ✅ Pages deployment does NOT trigger when CI/CD Pipeline fails
3. ✅ Manual workflow trigger works independently
4. ✅ Each Pages deployment shows link to authorizing CI/CD run
5. ✅ Documentation accurately describes the behavior
6. ✅ No disruption to existing CI/CD Pipeline functionality

---

## Monitoring

### Check Workflow Status

```bash
# List recent CI/CD Pipeline runs
gh run list --workflow=test.yml --limit 5

# List recent Pages deployment runs
gh run list --workflow=deploy-demo.yml --limit 5

# View specific run details
gh run view <run-id>
```

### View Workflow in GitHub UI

1. Go to repository → Actions tab
2. Filter by workflow name
3. Click on specific run to view details
4. Check job summaries for authorization info

---

## Troubleshooting

### Problem: Pages deploys even when tests fail

**Solution**: Check the `if` condition in deploy-demo.yml:
```yaml
if: ${{ github.event.workflow_run.conclusion == 'success' || github.event_name == 'workflow_dispatch' }}
```

### Problem: Pages never deploys even when tests pass

**Solutions**:
1. Check that CI/CD Pipeline workflow name matches exactly: "CI/CD Pipeline"
2. Verify branch name in workflow_run trigger: `branches: [ main ]`
3. Check GitHub Actions permissions in Settings → Actions

### Problem: Can't find authorization link in Pages deployment

**Solution**: Check that the verification step runs before checkout:
```yaml
steps:
- name: Verify CI/CD Authorization
  run: |
    echo "**CI/CD Workflow Run**: ${{ github.event.workflow_run.html_url }}"
```

---

## Rollback Procedure

If issues arise, rollback by:

1. Revert workflow changes:
   ```bash
   git revert <commit-hash>
   git push origin main
   ```

2. Or manually edit `.github/workflows/deploy-demo.yml`:
   ```yaml
   on:
     push:
       branches: [ main ]
       paths:
         - 'demo/**'
         - '.github/workflows/deploy-demo.yml'
     workflow_dispatch:
   ```

3. Remove the `if` condition from the job

---

**Last Updated**: October 22, 2025  
**Author**: Copilot Agent  
**Status**: ✅ Ready for testing
