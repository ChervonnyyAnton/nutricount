# 🚀 Quick Start: Enable GitHub Pages

## For Repository Owner (ChervonnyyAnton)

To make the demo publicly accessible, you need to enable GitHub Pages **once**. This is a one-time setup.

### Step-by-Step Instructions

1. **Go to Repository Settings**
   - Navigate to https://github.com/ChervonnyyAnton/nutricount
   - Click **Settings** (top right, near "Insights")

2. **Navigate to Pages Section**
   - In the left sidebar, scroll down to find **Pages**
   - Click on **Pages**

3. **Configure Source**
   - Under "Build and deployment"
   - Find "Source" dropdown
   - Select **"GitHub Actions"** (NOT "Deploy from a branch")
   - That's it! No need to click Save (it auto-saves)

4. **Trigger First Deployment**
   - Go to **Actions** tab
   - You should see "Deploy Demo to GitHub Pages" workflow
   - Click on it
   - Click "Run workflow" button (top right)
   - Select `main` branch
   - Click green "Run workflow" button

5. **Wait for Deployment** (~1-2 minutes)
   - Watch the workflow run
   - Green checkmark ✅ means success
   - If it fails, check the error logs

6. **Access Your Demo**
   - After successful deployment, go to:
   - **https://chervonnyyanton.github.io/nutricount/**
   - Share this link with anyone! 🎉

### Troubleshooting

**If you see "Pages is not enabled":**
- Make sure the repository is **public** (GitHub Pages free tier requires this)
- If repository is private, you need GitHub Pro/Team

**If workflow fails:**
- Check Actions tab for error details
- Most common issue: Pages source not set to "GitHub Actions"
- Go back to Settings → Pages and verify source

**If demo shows 404:**
- Wait 1-2 minutes after first deployment
- Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)
- Check that deployment was successful in Actions tab

### What Happens Next?

**Automatic Deployments:**
- Every time you push to `main` branch
- If changes affect `demo/**` files
- Workflow automatically re-deploys the demo
- No manual action needed! 🚀

**URL will always be:**
- https://chervonnyyanton.github.io/nutricount/

### Need Help?

See detailed guide: [docs/GITHUB_PAGES_SETUP.md](GITHUB_PAGES_SETUP.md)

---

**Estimated Time**: 2 minutes for setup + 2 minutes for first deployment = **4 minutes total**

**Status**: ✅ Workflow configured and ready  
**Action Required**: Enable GitHub Pages in Settings (one-time, 1 minute)
