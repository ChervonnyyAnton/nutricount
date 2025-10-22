# 📋 GitHub Pages Setup Instructions

This guide explains how to enable GitHub Pages for the Nutrition Tracker demo.

## Prerequisites

- Repository must be public (GitHub Pages free tier requirement)
- Admin access to the repository
- Demo workflow file already exists (`.github/workflows/deploy-demo.yml`)

## Setup Steps

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under "Build and deployment":
   - **Source**: Select "GitHub Actions"
   - Save the configuration

That's it! The workflow will automatically deploy on the next push to `main` branch.

### 2. Trigger Deployment

The demo will automatically deploy when:
- You push changes to `main` branch **AND** the CI/CD Pipeline (tests + build) passes successfully
- The deployment is authorized by the successful completion of all CI/CD checks
- You manually trigger the workflow (bypasses CI/CD requirement)

#### Manual Trigger (Optional)
1. Go to **Actions** tab
2. Select "Deploy Demo to GitHub Pages" workflow
3. Click "Run workflow"
4. Select `main` branch
5. Click "Run workflow"

### 3. Access Your Demo

After successful deployment (takes ~1-2 minutes):
- Demo URL: `https://[username].github.io/[repo]/`
- For this repo: `https://chervonnyyanton.github.io/nutricount/`

The demo will be accessible at the root because we upload only the `demo` directory content.

## Deployment Status

### CI/CD Pipeline Integration

**Important**: GitHub Pages deployment now requires successful CI/CD Pipeline completion.

The deployment workflow:
1. **Test job** runs (linting + pytest)
2. **Build job** runs (Docker build + health check)
3. **Deploy job** runs (authorization gate)
4. **Pages deployment** triggers automatically if all above succeed

This ensures that only validated code is deployed to GitHub Pages.

### Check Deployment Status

1. Go to **Actions** tab
2. Look for "Deploy Demo to GitHub Pages" workflow runs
3. Green checkmark ✅ = successful deployment
4. Red X ❌ = deployment failed (check logs)

### Workflow Badge

Add this badge to your README to show deployment status:

```markdown
[![Deploy Demo](https://github.com/ChervonnyyAnton/nutricount/actions/workflows/deploy-demo.yml/badge.svg)](https://github.com/ChervonnyyAnton/nutricount/actions/workflows/deploy-demo.yml)
```

## Troubleshooting

### "Pages is not enabled for this repository"

**Solution**: 
1. Go to Settings → Pages
2. Ensure "Source" is set to "GitHub Actions"
3. If option is not available, repository might be private (upgrade to public)

### Workflow fails with "pages build and deployment" error

**Solution**:
1. Check that Pages is enabled in Settings
2. Verify repository has Pages permissions
3. Ensure branch is `main` (not `master` or other)

### Pages deployment doesn't trigger

**Solution**:
1. Check that the CI/CD Pipeline completed successfully
2. Go to Actions tab and verify "CI/CD Pipeline" workflow passed
3. Pages deployment only triggers after CI/CD success
4. For manual deployment without CI/CD, use "Run workflow" button

### Demo shows 404

**Possible causes**:
1. Deployment is still in progress (wait 1-2 minutes)
2. Wrong URL - should be `https://username.github.io/repo/`
3. Workflow failed - check Actions tab for errors

**Solution**:
1. Check Actions tab for successful deployment
2. Verify URL format
3. Check browser console for errors
4. Try hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

### Bootstrap/CSS not loading

**Solution**:
1. Check browser console for CDN errors
2. Verify internet connection
3. Try different browser
4. Check if CDN URLs are correct in `demo/index.html`

## Custom Domain (Optional)

To use a custom domain (e.g., `demo.yoursite.com`):

1. Go to Settings → Pages
2. Under "Custom domain", enter your domain
3. Add DNS records at your domain provider:
   - For apex domain: A records to GitHub Pages IPs
   - For subdomain: CNAME record to `username.github.io`
4. Wait for DNS propagation (can take 24-48 hours)
5. Enable "Enforce HTTPS" (recommended)

## Monitoring

### Check Deployment Logs

1. Go to Actions tab
2. Click on latest "Deploy Demo to GitHub Pages" workflow
3. Click on "Deploy Demo to GitHub Pages" job
4. Review each step's output

### Test Demo Features

After deployment, verify:
- ✅ Page loads correctly
- ✅ Product management works
- ✅ Daily logging works
- ✅ Statistics display correctly
- ✅ Theme switching works
- ✅ Mobile responsiveness
- ✅ PWA features (manifest, icons)

## Rollback

If you need to rollback to a previous version:

1. Go to Actions tab
2. Find the previous successful deployment
3. Click "Re-run all jobs"
4. Wait for re-deployment

Or revert the commit:
```bash
git revert HEAD
git push origin main
```

## Security Notes

- Demo stores all data in browser LocalStorage (no server)
- No sensitive data should be included in demo
- All demo code is public (repository is public)
- HTTPS is automatically enabled by GitHub Pages

## Performance

Expected metrics:
- **Deploy time**: 1-2 minutes
- **Page load**: <2 seconds (first load)
- **Page load**: <0.5 seconds (cached)
- **Demo size**: ~120KB (with Bootstrap CDN)

## Support

If you encounter issues:
1. Check this troubleshooting guide
2. Review Actions workflow logs
3. Check [GitHub Pages documentation](https://docs.github.com/en/pages)
4. Create an issue in the repository

---

**Last Updated**: October 22, 2025  
**Workflow**: `.github/workflows/deploy-demo.yml`  
**Status**: ✅ Ready for deployment
