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
- **Intermittent Fasting**: Complete fasting tracking with goals and statistics
- **High Performance**: Redis caching, async tasks, and optimized database queries
- **Advanced Monitoring**: Prometheus metrics, system monitoring, and performance analytics
- **Enterprise Security**: JWT authentication, rate limiting, HTTPS, audit logging
- **🎯 Demo Version**: Standalone browser-only SPA for public demonstrations ([see demo/](demo/))

## 🏗️ Architecture

```
Frontend:  HTML5, CSS3 (+Bootstrap 5), Vanilla JS
API:       Flask 2.3+, SQLite+WAL, Redis Cache
Infra:     Docker ARM64, docker-compose, Gunicorn, Nginx, Redis
Pi 4:      ARM64 optimized, thermal-aware, conservative settings
Monitoring: Temperature, Prometheus metrics, system monitoring
CI/CD:     GitHub Actions → Tests → Deploy to Pi
Fasting:   Complete intermittent fasting tracking system
Performance: Redis caching, async tasks, optimized queries
Security:  JWT auth, rate limiting, HTTPS, audit logging
```

**Admin Panel:** Ctrl+Alt+A or triple-click on page title!

## 📦 Folder Structure

```
.
├── src/                 # config.py, constants.py, utils.py
├── routes/              # Blueprint modules (auth, products, dishes, etc.)
├── templates/           # index.html, admin-modal.html
├── static/
│   ├── css/final-polish.css
│   └── js/ (app.js, shortcuts.js, notifications.js, admin.js, offline.js)
├── demo/                # 🆕 Standalone SPA demo version (browser-only)
│   ├── index.html       # Single-file demo app
│   ├── manifest.json    # PWA manifest
│   ├── README.md        # Demo documentation
│   └── DEPLOYMENT.md    # Deployment guide
├── tests/               # Comprehensive test suite (679 tests)
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
- **Prometheus Metrics**: `http://<pi-ip>/metrics`
- **Fasting API**: `http://<pi-ip>/api/fasting/`
- **Background Tasks**: `http://<pi-ip>/api/tasks/`

## 🎯 Demo Version (NEW!)

A standalone browser-only version for public demonstrations:

### Features
- ✅ **No Server Required**: All data in browser LocalStorage
- ✅ **Mobile Optimized**: Perfect for smartphones and tablets
- ✅ **Offline Capable**: Works without internet (after first load)
- ✅ **Easy Deployment**: Single HTML file, deploy anywhere
- ✅ **Full Functionality**: Products, logging, and statistics
- ✅ **PWA Support**: Install as app on mobile devices

### Quick Start
```bash
# Option 1: Open directly
cd demo/
open index.html  # or double-click the file

# Option 2: Deploy to web
# See demo/DEPLOYMENT.md for GitHub Pages, Netlify, Vercel, etc.

# Option 3: Local server
cd demo/
python3 -m http.server 8000
# Visit http://localhost:8000/
```

### Documentation
- [Demo README](demo/README.md) - Complete usage guide
- [Deployment Guide](demo/DEPLOYMENT.md) - Deployment instructions
- [Implementation Plan](SPA_DEMO_PLAN.md) - Technical details

### Use Cases
- 📱 Mobile demonstrations
- 🎓 Educational purposes  
- 🚀 Quick prototyping
- 🔒 Privacy-focused usage (no server)
- 🌍 Public sharing without backend

## ⏰ Intermittent Fasting

The application now includes a complete intermittent fasting tracking system:

### Features
- **Multiple Fasting Types**: 16:8, 18:6, 20:4, OMAD, Custom
- **Session Management**: Start, pause, resume, end, cancel sessions
- **Progress Tracking**: Real-time duration and progress percentage
- **Statistics**: Total sessions, average duration, longest session, current streak
- **Goals**: Set daily, weekly, or monthly fasting goals
- **History**: Complete fasting session history with filtering

### Usage
1. Navigate to the **Fasting** tab
2. Select your fasting type and add optional notes
3. Click **Start Fasting** to begin tracking
4. Monitor your progress with real-time updates
5. End your session when complete

### API Endpoints
- `POST /api/fasting/start` - Start a new fasting session
- `POST /api/fasting/end` - End current session
- `POST /api/fasting/pause` - Pause current session
- `POST /api/fasting/resume` - Resume paused session
- `GET /api/fasting/status` - Get current fasting status
- `GET /api/fasting/stats` - Get fasting statistics
- `GET /api/fasting/goals` - Get fasting goals

## ⚡ Performance Features

### Redis Caching
- **Automatic Caching**: Products, dishes, and statistics are cached
- **Smart Invalidation**: Cache is automatically invalidated on data changes
- **Fallback Support**: Falls back to in-memory cache if Redis is unavailable
- **Configurable TTL**: Different cache expiration times for different data types

### Background Tasks
- **Async Processing**: Database backups, optimization, and exports run in background
- **Task Monitoring**: Track task progress and status via API
- **Celery Integration**: Full Celery support for distributed task processing
- **Fallback Mode**: Synchronous execution if Celery is not available

### Monitoring & Metrics
- **Prometheus Integration**: Complete metrics collection
- **System Monitoring**: CPU, memory, and disk usage tracking
- **Application Metrics**: HTTP requests, database operations, cache performance
- **Custom Metrics**: Fasting sessions, nutrition calculations, user activity

### API Endpoints
- `GET /metrics` - Prometheus metrics endpoint
- `GET /api/metrics/summary` - Metrics summary for API
- `POST /api/tasks` - Create background tasks
- `GET /api/tasks/<task_id>` - Get task status

## 🔒 Security Features

The application includes comprehensive security measures:

### Authentication & Authorization
- **JWT Tokens**: Secure access and refresh tokens
- **Role-based Access**: Admin and user roles
- **Session Management**: Automatic token refresh
- **Password Security**: Bcrypt hashing with strength requirements

### Rate Limiting
- **API Endpoints**: 100 requests per hour
- **Authentication**: 10 attempts per hour
- **Admin Operations**: 200 requests per hour
- **Redis-based**: Distributed rate limiting

### HTTPS & SSL
- **Automatic HTTPS**: HTTP to HTTPS redirect
- **Self-signed Certificates**: For development
- **SSL Security**: TLS 1.2+ with secure ciphers
- **Security Headers**: HSTS, CSP, XSS protection

### Audit Logging
- **Authentication Events**: Login attempts and failures
- **Token Usage**: Access and refresh token tracking
- **Admin Actions**: All administrative operations
- **Rate Limit Hits**: Suspicious activity monitoring

### Input Validation
- **Data Sanitization**: XSS and injection prevention
- **Email Validation**: RFC-compliant email checking
- **Password Strength**: Multi-criteria validation
- **Numeric Validation**: Range and type checking

### API Endpoints
- `POST /api/auth/login` - User authentication
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/verify` - Token verification
- `POST /api/auth/logout` - User logout

### SSL Setup
```bash
# Generate SSL certificates
./scripts/setup_ssl.sh [hostname]

# Default credentials (change in production):
# Username: admin
# Password: admin123
```

## 📊 Advanced Monitoring & Logging

The application includes comprehensive monitoring and logging capabilities:

### Prometheus Metrics
- **System Metrics**: CPU, memory, disk usage, temperature
- **Application Metrics**: Request rates, response times, error rates
- **Database Metrics**: Query performance, connection pool status
- **Custom Metrics**: Business logic metrics, user activity

### Structured Logging
- **Loguru Integration**: High-performance structured logging
- **Structured Logs**: JSON format with context and metadata
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Automatic log file rotation and cleanup

### ELK Stack Integration
- **Elasticsearch**: Centralized log storage and search
- **Logstash**: Log processing and enrichment
- **Kibana**: Log visualization and analysis
- **Real-time Monitoring**: Live log streaming and alerts

### Grafana Dashboards
- **System Dashboards**: Hardware and performance metrics
- **Application Dashboards**: API performance and usage
- **Business Dashboards**: User activity and nutrition trends
- **Custom Dashboards**: Configurable metrics visualization

### API Endpoints
- `GET /metrics` - Prometheus metrics endpoint
- `GET /api/metrics/summary` - Application metrics summary
- `POST /api/tasks` - Create background tasks
- `GET /api/tasks/<task_id>` - Get task status

### Monitoring Features
- **Real-time Alerts**: Temperature, memory, disk space warnings
- **Performance Tracking**: Response times, throughput metrics
- **Error Monitoring**: Exception tracking and analysis
- **Health Checks**: Service availability and status monitoring

## 🧪 Comprehensive Testing

The application includes extensive testing capabilities:

### Test Types
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **End-to-End Tests**: Complete workflow testing
- **Security Tests**: Authentication and authorization testing
- **Performance Tests**: Load and stress testing

### Test Coverage
- **Code Coverage**: 93% overall (567 tests, 28s execution time)
- **API Coverage**: All 47 endpoints tested
- **Business Logic**: Core functionality tested
- **Error Handling**: Exception scenarios tested
- **Edge Cases**: Boundary conditions tested
- **Test Types**: Unit (330+), Integration (125+), E2E (100+)

### Test Tools
- **pytest**: Main testing framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking and patching
- **pytest-xdist**: Parallel test execution
- **mutmut**: Mutation testing for test quality
- **factory-boy**: Test data generation
- **faker**: Fake data generation
- **requests-mock**: HTTP request mocking
- **freezegun**: Time mocking

### Running Tests
```bash
# Install test dependencies
./scripts/run_tests.sh install

# Run all tests
./scripts/run_tests.sh all
make test

# Run specific test types
./scripts/run_tests.sh unit
./scripts/run_tests.sh integration
./scripts/run_tests.sh e2e

# Run with coverage
./scripts/run_tests.sh report
pytest tests/ --cov=src --cov-report=html

# Clean test artifacts
./scripts/run_tests.sh clean
make clean
```

### Mutation Testing
Mutation testing verifies test quality by introducing code mutations and checking if tests catch them.

```bash
# Run mutation testing
make mutation-test
./scripts/mutation_test.sh src/ run

# View results
make mutation-results
./scripts/mutation_test.sh src/ results

# Generate HTML report
make mutation-html
./scripts/mutation_test.sh src/ html

# Test specific module
./scripts/mutation_test.sh src/utils.py run
```

**Current Status:**
- **Mutation Testing:** Configured and ready
- **Target Score:** 80%+ for critical modules (security, utils)
- **Baseline:** In progress (see [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md))

See [MUTATION_TESTING.md](MUTATION_TESTING.md) for complete guide.

### Test Structure
```
tests/
├── conftest.py          # Test configuration and fixtures
├── unit/                # Unit tests
│   ├── test_fasting_manager.py
│   ├── test_cache_manager.py
│   ├── test_security.py
│   └── test_monitoring.py
├── integration/         # Integration tests
│   ├── test_api.py
│   ├── test_database.py
│   └── test_redis.py
├── e2e/                # End-to-end tests
│   ├── test_workflows.py
│   └── test_user_journeys.py
└── fixtures/           # Test data fixtures
    ├── products.json
    ├── dishes.json
    └── users.json
```

### CI/CD Testing
- **GitHub Actions**: Automated testing on push/PR
- **Multi-Python**: Tests on Python 3.9, 3.10, 3.11
- **Security Scanning**: Bandit, Safety, Semgrep
- **Performance Testing**: Locust load testing
- **Docker Testing**: Container and compose testing
- **Coverage Reporting**: Codecov integration
- **Mutation Testing**: Weekly mutation testing runs (optional)

## 🎨 Advanced UX/UI Features

The application includes comprehensive user experience and interface enhancements:

### Theme System
- **Multiple Themes**: Light, Dark, Blue, Green, Purple
- **Custom Colors**: Primary, secondary, accent colors
- **Theme Persistence**: User preferences saved locally
- **Theme Preview**: Visual theme selection
- **Keyboard Shortcuts**: Ctrl+Shift+T for theme toggle

### Personalization
- **Dashboard Layout**: Grid, list, or compact view
- **Display Preferences**: Font size, compact mode, icons
- **Nutrition Settings**: Unit system, field visibility
- **Fasting Preferences**: Default type, notifications
- **Accessibility Options**: High contrast, reduced motion

### Responsive Design
- **Mobile-First**: Optimized for all screen sizes
- **Breakpoint System**: 576px, 768px, 992px, 1200px
- **Adaptive Layout**: Cards, tables, forms adapt to screen
- **Touch-Friendly**: Large buttons and touch targets
- **Orientation Support**: Portrait and landscape modes

### Accessibility Features
- **WCAG 2.2 Compliance**: AA level accessibility
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: ARIA labels and roles
- **High Contrast**: Enhanced visibility mode
- **Reduced Motion**: Respects user preferences
- **Focus Indicators**: Clear focus management

### User Experience
- **Intuitive Interface**: Clean, modern design
- **Quick Actions**: Fast access to common tasks
- **Recent Items**: Quick access to recent data
- **Statistics Dashboard**: Visual data representation
- **Fasting Status**: Real-time fasting information
- **Tooltips**: Contextual help and information

### Customization Options
- **Layout Control**: Choose your preferred layout
- **Field Visibility**: Show/hide nutrition fields
- **Notification Settings**: Customize alerts
- **Export/Import**: Backup and restore preferences
- **Keyboard Shortcuts**: Power user features

### Visual Enhancements
- **Smooth Animations**: Subtle transitions and effects
- **Hover Effects**: Interactive feedback
- **Loading States**: Clear loading indicators
- **Error Handling**: User-friendly error messages
- **Success Feedback**: Confirmation of actions
- **Progress Indicators**: Visual progress tracking

### Theme Customization
```javascript
// Access theme manager
window.themeManager.applyTheme('dark');

// Get current theme
const currentTheme = window.themeManager.getCurrentTheme();

// Get theme colors
const colors = window.themeManager.getThemeColors();
```

### Personalization API
```javascript
// Access personalization manager
window.personalizationManager.setPreference('dashboard', 'layout', 'grid');

// Get preference
const layout = window.personalizationManager.getPreference('dashboard', 'layout');

// Reset preferences
window.personalizationManager.resetPreferences();
```

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