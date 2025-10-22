# 🚀 Demo Deployment Guide

## 🌐 Current Live Demo

**Live at**: [https://chervonnyyanton.github.io/nutricount/](https://chervonnyyanton.github.io/nutricount/)

This demo is automatically deployed via GitHub Actions. See [GitHub Pages Setup Guide](../docs/GITHUB_PAGES_SETUP.md) for details.

---

## Quick Deployment Options

### Option 1: GitHub Pages (Recommended) ⭐

**Best for**: Free hosting, automatic HTTPS, easy updates

**This repository is already configured!** The demo automatically deploys on every push to `main` branch.

#### Manual Setup (if forking)
```bash
# 1. Fork this repository

# 2. Enable GitHub Pages
# - Go to repository Settings → Pages
# - Source: Select "GitHub Actions"
# - Save

# 3. Workflow will auto-deploy to:
# https://[username].github.io/[repo]/
```

**Detailed Instructions**: See [docs/GITHUB_PAGES_SETUP.md](../docs/GITHUB_PAGES_SETUP.md)

**Pros**: 
- ✅ Free hosting
- ✅ Automatic HTTPS
- ✅ CDN distribution
- ✅ Easy updates (auto-deploy on push)
- ✅ No manual deployment needed

**Cons**:
- ❌ Must be public repository
- ❌ Build time ~1-2 minutes

---

### Option 2: Netlify Drop

**Best for**: Instant deployment, no git required

```bash
# 1. Go to https://app.netlify.com/drop
# 2. Drag and drop the demo/ folder
# 3. Done! Get instant URL like: https://[random].netlify.app
```

**Pros**:
- ✅ Instant deployment
- ✅ Free HTTPS
- ✅ Custom domains
- ✅ Easy updates (drag & drop)

**Cons**:
- ❌ Requires Netlify account
- ❌ Random URL (can be changed)

---

### Option 3: Vercel

**Best for**: Professional deployments, best performance

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy
cd demo/
vercel

# 3. Follow prompts
# Get URL like: https://[project].vercel.app
```

**Pros**:
- ✅ Excellent performance
- ✅ Free tier
- ✅ Custom domains
- ✅ Analytics

**Cons**:
- ❌ Requires account
- ❌ CLI installation

---

### Option 4: Cloudflare Pages

**Best for**: Global CDN, best availability

```bash
# 1. Go to pages.cloudflare.com
# 2. Create new project
# 3. Upload demo/ folder
# 4. Deploy!

# Get URL like: https://[project].pages.dev
```

**Pros**:
- ✅ Global CDN
- ✅ Unlimited bandwidth
- ✅ Free tier
- ✅ Great speed

**Cons**:
- ❌ Requires account
- ❌ UI-based only

---

### Option 5: Self-Hosted

**Best for**: Full control, custom domain

#### Using Docker (Nginx)

```dockerfile
# Create Dockerfile
FROM nginx:alpine
COPY demo/ /usr/share/nginx/html/demo/
EXPOSE 80
```

```bash
# Build and run
docker build -t nutricount-demo .
docker run -d -p 80:80 nutricount-demo

# Access at http://localhost/demo/
```

#### Using Python Simple Server

```bash
cd demo/
python3 -m http.server 8000

# Access at http://localhost:8000/
```

#### Using Node.js

```bash
cd demo/
npx serve -p 8000

# Access at http://localhost:8000/
```

---

## Mobile-Specific Deployment

### For Testing on Mobile Devices

#### Method 1: ngrok (Easiest)

```bash
# 1. Start local server
cd demo/
python3 -m http.server 8000

# 2. In another terminal
ngrok http 8000

# 3. Use the https URL on your phone
# Example: https://abc123.ngrok.io
```

#### Method 2: Local Network

```bash
# 1. Get your computer's IP
# Windows: ipconfig
# Mac/Linux: ifconfig

# 2. Start server
python3 -m http.server 8000

# 3. On phone, visit:
# http://[YOUR_IP]:8000/

# Example: http://192.168.1.100:8000/
```

---

## Custom Domain Setup

### After deploying to any platform:

#### 1. GitHub Pages

```bash
# Add CNAME file
echo "demo.yourdomain.com" > demo/CNAME
git add demo/CNAME
git commit -m "Add custom domain"
git push

# Then configure DNS:
# Type: CNAME
# Name: demo
# Value: [username].github.io
```

#### 2. Netlify/Vercel

```bash
# In dashboard:
# 1. Go to Domain Settings
# 2. Add custom domain
# 3. Follow DNS instructions
```

---

## Security Best Practices

### 1. HTTPS Only

Ensure your demo is served over HTTPS:
- ✅ GitHub Pages: Automatic
- ✅ Netlify: Automatic
- ✅ Vercel: Automatic
- ⚠️ Self-hosted: Use Let's Encrypt

### 2. Content Security Policy

Add to your HTML (in `<head>`):

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self' https://cdn.jsdelivr.net; 
               script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; 
               style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;">
```

### 3. Disable Directory Listing

For self-hosted setups, ensure directory listing is disabled in your web server config.

---

## Performance Optimization

### 1. Enable Compression

#### Nginx

```nginx
gzip on;
gzip_types text/html text/css application/javascript;
```

#### Apache

```apache
AddOutputFilterByType DEFLATE text/html text/css application/javascript
```

### 2. Cache Headers

```nginx
location ~ \.(html|json)$ {
    add_header Cache-Control "no-cache, must-revalidate";
}

location ~ \.(js|css)$ {
    add_header Cache-Control "public, max-age=31536000";
}
```

### 3. CDN Optimization

If using Bootstrap CDN, it's already optimized. For self-hosting:

```bash
# Download Bootstrap locally
wget https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css
wget https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js

# Update HTML to use local files
```

---

## Monitoring & Analytics

### Google Analytics (Optional)

Add before `</head>`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Simple Analytics (Privacy-focused)

```html
<script async defer src="https://scripts.simpleanalyticscdn.com/latest.js"></script>
<noscript><img src="https://queue.simpleanalyticscdn.com/noscript.gif" alt=""/></noscript>
```

---

## Troubleshooting

### Issue: Bootstrap not loading

**Solution**: Check CDN is accessible, or use local copy:

```bash
cd demo/
mkdir -p vendor
wget -P vendor/ https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css
wget -P vendor/ https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js

# Update HTML links to: vendor/bootstrap.min.css
```

### Issue: LocalStorage not working

**Possible causes**:
- Private/incognito mode
- Browser settings blocking storage
- Disk quota exceeded

**Solution**: Check browser console for errors

### Issue: Mobile viewport issues

**Solution**: Verify meta tag:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
```

---

## Testing Checklist

Before deploying, test:

- [ ] Loads on desktop browser
- [ ] Loads on mobile browser  
- [ ] Theme toggle works
- [ ] Products can be added/deleted
- [ ] Log entries work
- [ ] Statistics calculate correctly
- [ ] Sample data loads
- [ ] Clear data works
- [ ] LocalStorage persists
- [ ] Works offline (after first load)
- [ ] No console errors
- [ ] HTTPS enabled (production)

---

## Update Process

### For Git-based deployments (GitHub Pages, Vercel)

```bash
# 1. Make changes to demo/index.html
# 2. Test locally
cd demo/
python3 -m http.server 8000

# 3. Commit and push
git add demo/
git commit -m "Update demo"
git push

# 4. Automatic deployment (1-2 minutes)
```

### For manual deployments (Netlify Drop, Cloudflare)

```bash
# 1. Make changes
# 2. Test locally
# 3. Upload new version via dashboard
```

---

## Recommended Setup

For best results:

1. **Development**: Local server with ngrok for mobile testing
2. **Staging**: Netlify or Vercel (free tier)
3. **Production**: GitHub Pages with custom domain

---

## Support

For deployment issues:
- GitHub Pages: https://docs.github.com/pages
- Netlify: https://docs.netlify.com
- Vercel: https://vercel.com/docs
- General: Create issue in repository

---

**Last Updated**: October 21, 2025  
**Version**: 1.0
