# 📖 README.md

## 🥗 Nutrition Tracker v2.0

**Production-ready, accessible, and modern nutrition tracking for web and Telegram.**

***

### 🚀 Features

- **WCAG 2.2 AA Compliant** UI: accessible, keyboard-friendly, color-blind safe, and readable for screen readers.
- **Nutrition Management:** Products, Dishes, Daily Log.
- **Realtime Analytics:** Auto calorie, macro, and keto-index calculations.
- **Offline Support:** PWA with Service Worker \& IndexedDB; installable as a native app.
- **Telegram WebApp ready:** Optimized for Telegram, includes webhook endpoints and automation.
- **Admin Panel:** quick actions (backup, optimize DB, export/import), stats, and monitoring.
- **CI/CD:** GitHub Actions pipeline automates linting, tests, security checks, builds, and deploy.
- **Docker Native:** Multi-stage Docker builds; compose for local, staging, prod.
- **Full documentation:** Setup, usage, troubleshooting, and best developer practices.

***

### 🏗️ Architecture

```
Frontend:  HTML5, CSS3 (+Bootstrap 5), Vanilla JS (shortcuts, toasts, offline, admin)
API:       Flask 2.3+, SQLite+WAL. Modular.
Infra:     Docker, docker-compose, Gunicorn, Nginx, GitHub Actions, Service Worker
Add-ons:   Prometheus & Grafana, backups, advanced scripts, security headers
```

Admin Panel: Ctrl+Alt+A or triple-click on page title!

***

### 📦 Folder Structure

```
.
├── src/                 # config.py, constants.py, utils.py
├── templates/           # index.html, admin-modal.html
├── static/
│   ├── css/final-polish.css
│   └── js/ (app.js, shortcuts.js, notifications.js, admin.js, offline.js)
├── Dockerfile.production
├── docker-compose.telegram.yml
├── scripts/
├── .env.example
├── README.md
└── ... (see QUICKSTART.md for details)
```


***

### 🛡️ Security \& Accessibility

- **Out-of-the-box:** strong passwords, rate limiting, HTTPS, no secrets in VCS.
- **Accessibility:** semantic HTML, ARIA, high-contrast, skip links, focus management, reduced motion, print-friendly.
- **Dev best-practices:** auto-format with Black, linting (`flake8`), strict isort, mypy type checks, bandit (security), Snyk, Trivy integration.

***

### 📓 Documentation Links

- [QUICKSTART.md](./QUICKSTART.md): 5-min setup, Docker \& manual, troubleshooting
- [CONTRIBUTING.md](./CONTRIBUTING.md): PRs, issues, style-guide, pre-commits
- [docs/SECURITY.md](./docs/SECURITY.md): security checklist prior to release
- [docs/PERFORMANCE.md](./docs/PERFORMANCE.md): optimization tips
- [docs/DEV_TIPS.md](./docs/DEV_TIPS.md): productivity for devs

***

### 💡 Philosophy

- **Simple-first:** every module is removable or replaceable, no bloated code, no unnecessary dependencies.
- **Accessible by default:** every user, every device, every place.
- **Production-focused:** all features tested for real-world reliability.

***

### 📬 Support \& Community

- GitHub issues for bugs/feature requests
- GitHub Discussions for Q\&A and best practices
- Email: support@nutrition-tracker.com

***

**Made with ❤️ for healthy living and accessible technology!**

***