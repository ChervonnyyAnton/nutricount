# 🥗 Nutrition Tracker v2.0

**Production-ready, accessible, and modern nutrition tracking application optimized for Raspberry Pi Zero 2W.**

## 🚀 Features

- **WCAG 2.2 AA Compliant** UI: accessible, keyboard-friendly, color-blind safe, and readable for screen readers
- **Nutrition Management:** Products, Dishes, Daily Log
- **Realtime Analytics:** Auto calorie, macro, and keto-index calculations
- **Offline Support:** PWA with Service Worker & IndexedDB; installable as a native app
- **Raspberry Pi Zero 2W Optimized:** Memory-efficient, single-core optimized, perfect for local home server
- **Admin Panel:** quick actions (backup, optimize DB, export/import), stats, and monitoring
- **Docker Native:** Multi-stage Docker builds; compose for local deployment
- **Testing & CI:** Automated testing with pytest, GitHub Actions CI/CD
- **Full documentation:** Setup, usage, troubleshooting, and best practices

## 🏗️ Architecture

```
Frontend:  HTML5, CSS3 (+Bootstrap 5), Vanilla JS (shortcuts, toasts, offline, admin)
API:       Flask 2.3+, SQLite+WAL. Modular.
Infra:     Docker, docker-compose, Gunicorn, Nginx, Service Worker
Pi Zero:   Memory-optimized containers, single-worker Gunicorn, minimal Nginx
Add-ons:   Backups, advanced scripts, security headers
```

**Admin Panel:** Ctrl+Alt+A or triple-click on page title!

## 📦 Folder Structure

```
.
├── src/                 # config.py, constants.py, utils.py
├── templates/           # index.html, admin-modal.html
├── static/
│   ├── css/final-polish.css
│   └── js/ (app.js, shortcuts.js, notifications.js, admin.js, offline.js)
├── dockerfile
├── docker-compose.yml
├── scripts/
├── .env.example
├── README.md
└── schema_v2.sql
```

## 🚦 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed
- `git`, `curl`, and a browser

### 1. Get the code

```sh
git clone https://github.com/your-username/nutrition-tracker.git
cd nutrition-tracker
```

### 2. Configure

```sh
cp .env.example .env
# Edit .env with your database settings
```

- At minimum set: `SECRET_KEY` for production use

### 3. Start (Docker)

```sh
docker-compose up --build -d
```

- Check health:

```sh
curl http://localhost:5000/health
```

### 4. Open the app

Open http://localhost:5000 in your browser

## 🛡️ Raspberry Pi Zero 2W Setup

### System Requirements

- **Raspberry Pi Zero 2W** (512MB RAM)
- **microSD card** Class 10 or better (minimum 8GB)
- **Raspberry Pi OS** (32-bit)
- **Stable WiFi connection**

### Automatic Setup

```sh
# Make script executable
chmod +x scripts/setup.sh

# Run automatic setup
./scripts/setup.sh
```

### Manual Setup

```sh
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo pip3 install docker-compose

# Create .env file
cp env.example .env

# Build and start
docker-compose up -d
```

### Performance Monitoring

```sh
# Run monitoring
chmod +x scripts/monitor.sh
./scripts/monitor.sh

# Continuous monitoring
./scripts/monitor.sh --continuous
```

### Service Management

```sh
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Auto-start on boot
sudo systemctl enable nutrition-tracker
```

## 📊 Performance Expectations

### ✅ What works great:
- Application startup: 30-60 seconds
- API requests: 50-200ms
- Up to 5-10 concurrent users
- Database up to 10,000 records

### ⚠️ Limitations:
- Slow startup (1-2 minutes)
- Delays under high load
- SSD card recommended
- Regular restarts for memory cleanup

## 🔧 Pi Zero 2W Optimizations

### Memory (300MB limit)
- **Gunicorn**: 1 worker instead of 4
- **Nginx**: minimal configuration
- **Docker**: memory limits
- **Logging**: disabled to save space

### CPU (1 core)
- **Workers**: synchronous instead of asynchronous
- **Timeouts**: increased for slow processing
- **Compression**: minimal gzip level

### Disk
- **Logs**: limited size and count
- **Swap**: increased to 1GB
- **Cache**: minimal size

## 🌐 Access

- **Web Interface**: `http://<pi-ip>:80`
- **API**: `http://<pi-ip>:5000`
- **Health Check**: `http://<pi-ip>:5000/health`

## 🛠️ Troubleshooting

### High Memory Usage
```bash
# Restart containers
docker-compose restart

# Clean unused images
docker system prune -f

# Check memory usage
free -h
```

### Slow Performance
```bash
# Check temperature
vcgencmd measure_temp

# Check CPU load
top

# Increase swap
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Network Issues
```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs nutrition-tracker
```

## 🔒 Security & Accessibility

- **Out-of-the-box:** strong passwords, rate limiting, HTTPS, no secrets in VCS
- **Accessibility:** semantic HTML, ARIA, high-contrast, skip links, focus management, reduced motion, print-friendly
- **Security:** application runs under unprivileged user, Nginx configured with basic security headers, rate limiting for DDoS protection

## 📝 Logging

Logs are limited to save space:
- **Log size**: maximum 10MB
- **File count**: 1
- **Log level**: warning and above

## 🔄 Updates

```bash
# Update code
git pull origin main

# Rebuild containers
docker-compose build --no-cache

# Restart service
docker-compose up -d
```

## 🧪 Testing

### Local Testing
```bash
# Run tests locally (requires Python environment)
make test

# Run integration tests only
make test-integration

# Run tests in Docker
make test-docker

# Run linting
make lint
```

### Test Coverage
- **API Endpoints:** Health, products, stats, logging
- **Database Operations:** CRUD operations, constraints
- **Error Handling:** Invalid data, missing fields
- **Integration Tests:** Complete workflow testing (products → dishes → logging → statistics → modifications → cleanup)

### CI/CD Pipeline
- **GitHub Actions:** Automated testing on push/PR
- **Docker Build:** Container testing
- **Health Checks:** Application startup verification
- **Code Quality:** Linting with flake8

## 🛠️ Admin Panel

- **Ctrl+Alt+A** or **Triple-click page title** for admin panel (backups, stats, export)
- **Alt+1,2,3,N,S,B** for keyboard shortcuts

## 💡 Philosophy

- **Simple-first:** every module is removable or replaceable, no bloated code, no unnecessary dependencies
- **Accessible by default:** every user, every device, every place
- **Production-focused:** all features tested for real-world reliability

## 📞 Support & Community

- GitHub issues for bugs/feature requests
- GitHub Discussions for Q&A and best practices
- Email: support@nutrition-tracker.com

## 🎯 Recommendations

- Use **Class 10** or better microSD card
- Ensure **good ventilation** to prevent overheating
- **Regularly restart** application for memory cleanup
- **Monitor logs** for errors
- Use **stable WiFi** connection

---

**Note**: This version is optimized for Pi Zero 2W. For production use with multiple users, Raspberry Pi 4 (4GB+) is recommended.

**Made with ❤️ for healthy living and accessible technology!**