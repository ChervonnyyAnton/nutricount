# 🥗 Nutrition Tracker

**Production-ready nutrition tracking application optimized for Raspberry Pi 4 Model B 2018 with Raspberry Pi OS Lite 64-bit.**

## 🚀 Features

- **Modern UI**: Clean, responsive design with dark theme support
- **Nutrition Management**: Products, Dishes, Daily Log with real-time calculations
- **Offline Support**: PWA with Service Worker & IndexedDB
- **Raspberry Pi Optimized**: ARM64 optimized, memory-efficient, thermal-aware
- **Admin Panel**: Quick actions (backup, optimize DB, export/import), stats, monitoring
- **Docker Native**: Multi-stage Docker builds optimized for ARM64
- **Temperature Monitoring**: Specialized monitoring for Pi 4 Model B 2018
- **Auto Backup**: Automated database backups with integrity checks
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

## 🏗️ Architecture

```
Frontend:  HTML5, CSS3 (+Bootstrap 5), Vanilla JS
API:       Flask 2.3+, SQLite+WAL
Infra:     Docker ARM64, docker-compose, Gunicorn, Nginx
Pi 4:      ARM64 optimized, thermal-aware, conservative settings
Monitoring: Temperature, performance, automated backups
CI/CD:     GitHub Actions → Tests → Deploy to Pi
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

- **Raspberry Pi 4 Model B 2018** (4GB+ RAM recommended)
- **Raspberry Pi OS Lite 64-bit** (NOT 32-bit!)
- **Active cooling** (fan) - REQUIRED for Pi 4 Model B 2018
- **Stable power supply** (5.1V/3A official adapter)
- **Fast microSD card** (Class 10, A2, or better)

### Automatic Setup (Recommended)

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Run automatic setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. Clone repository
git clone <your-repository-url> nutricount
cd nutricount

# 4. Configure environment
cp env.example .env
nano .env  # Edit settings

# 5. Start application
docker-compose up -d
```

### Manual Setup

```bash
# Install Docker for ARM64
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo apt install -y docker-compose
sudo reboot

# Configure Pi 4 Model B 2018
sudo nano /boot/config.txt
# Add:
# gpu_mem=128
# arm_freq=1500
# over_voltage=1
# temp_limit=75
# avoid_warnings=1
# dtparam=thermal

# Setup swap
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Clone and start
git clone <your-repository-url> nutricount
cd nutricount
cp env.example .env
docker-compose up -d
```

## 🌡️ Temperature Monitoring

**CRITICAL for Pi 4 Model B 2018**: This model is prone to overheating!

```bash
# Check temperature
./scripts/temp_monitor.sh --check

# Continuous monitoring
./scripts/temp_monitor.sh --continuous

# Temperature thresholds:
# 70°C - Warning
# 80°C - Critical (throttling starts)
# 85°C - Maximum safe temperature
```

## 📊 Performance Monitoring

```bash
# Main monitoring dashboard
./scripts/monitor.sh

# Continuous monitoring
./scripts/monitor.sh --continuous

# Manual backup
./scripts/backup.sh
```

## 🌐 Access

- **Web Interface**: `http://<pi-ip>/`
- **API**: `http://<pi-ip>/api/`
- **Health Check**: `http://<pi-ip>/health`

## 🛠️ Troubleshooting

### High Temperature (CRITICAL!)
```bash
# Check temperature
vcgencmd measure_temp

# If > 70°C - check cooling immediately!
# If > 80°C - throttling is active!

# Check throttling status
vcgencmd get_throttled

# Solutions:
# 1. Ensure fan is working
# 2. Check thermal paste
# 3. Improve ventilation
# 4. Reduce CPU frequency in /boot/config.txt
```

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
# Check CPU load
htop

# Check temperature
./scripts/temp_monitor.sh --check

# Check container status
docker-compose ps
```

### Network Issues
```bash
# Check container logs
docker-compose logs nutrition-tracker

# Check nginx logs
docker-compose logs nutrition-nginx

# Restart services
docker-compose restart
```

## 🔒 Security & Maintenance

- **Firewall**: UFW configured with fail2ban
- **Rate Limiting**: DDoS protection via nginx
- **Auto Backup**: Daily database backups with integrity checks
- **Log Rotation**: Automatic log cleanup to save space
- **Service Management**: Auto-start on boot

## 📝 Service Management

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Auto-start on boot
sudo systemctl enable nutrition-tracker.service
```

## 🔄 Updates

```bash
# Update code
git pull origin main

# Rebuild containers
docker-compose build --no-cache

# Restart service
docker-compose up -d
```

## ⚠️ Important Notes for Pi 4 Model B 2018

1. **ACTIVE COOLING REQUIRED** - This model overheats easily
2. **Monitor temperature constantly** - Use `./scripts/temp_monitor.sh`
3. **Use 64-bit OS** - 32-bit will not work optimally
4. **Stable power supply** - Use official 5.1V/3A adapter
5. **Fast microSD card** - Class 10 or A2 recommended
6. **Thermal paste** - Apply between CPU and heatsink
7. **Good ventilation** - Ensure airflow around the Pi

## 🎯 Performance Expectations

- **Startup time**: 30-60 seconds
- **API response**: 50-200ms
- **Concurrent users**: 5-10
- **Database**: Up to 10,000 records
- **Memory usage**: ~400-800MB
- **Temperature**: Keep below 70°C