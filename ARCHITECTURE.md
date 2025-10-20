# 🏗️ Nutricount Architecture Guide
**Last Updated:** October 20, 2025

---

## 📋 Quick Navigation

This document provides a consolidated view of the Nutricount architecture. For detailed diagrams, see:
- 📊 [NUTRICOUNT_ARCHITECTURE_DIAGRAM.md](NUTRICOUNT_ARCHITECTURE_DIAGRAM.md) - Visual architecture diagrams
- 🧠 [NUTRICOUNT_MINDMAP_AND_TEST_COVERAGE.md](NUTRICOUNT_MINDMAP_AND_TEST_COVERAGE.md) - Mindmap and coverage details

---

## 🎯 Architecture Overview

### System Type
**Modern Web Application** with Progressive Web App (PWA) capabilities

### Deployment Target
**Raspberry Pi 4 Model B 2018** (ARM64, Raspberry Pi OS Lite 64-bit)

### Architecture Style
**Monolithic with Modular Components** (transitioning to microservices-ready)

---

## 📐 Architecture Layers

### 1. Presentation Layer (Frontend)

```
┌─────────────────────────────────────────────────────┐
│  📱 User Interface                                  │
├─────────────────────────────────────────────────────┤
│  HTML Templates:                                    │
│  - index.html (main application)                    │
│  - admin-modal.html (admin panel)                   │
│                                                     │
│  CSS Stylesheets:                                   │
│  - final-polish.css (main styles)                   │
│  - responsive.css (mobile-first)                    │
│                                                     │
│  JavaScript:                                        │
│  - app.js (main logic)                              │
│  - admin.js (admin features)                        │
│  - fasting.js (fasting tracking)                    │
│  - notifications.js (toast messages)                │
│  - shortcuts.js (keyboard shortcuts)                │
│  - offline.js (PWA support)                         │
│                                                     │
│  PWA:                                               │
│  - sw.js (service worker)                           │
│  - manifest.json (app manifest)                     │
└─────────────────────────────────────────────────────┘
```

**Key Features:**
- Responsive design (mobile-first)
- WCAG 2.2 AA accessibility compliance
- Offline support via Service Worker
- Multiple theme support
- Keyboard shortcuts for power users

---

### 2. API Layer (REST Endpoints)

```
┌─────────────────────────────────────────────────────┐
│  🌐 REST API (47 endpoints)                        │
├─────────────────────────────────────────────────────┤
│  Products API:                                      │
│  - GET/POST/PUT/DELETE /api/products                │
│  - GET /api/products/<id>                           │
│                                                     │
│  Dishes API:                                        │
│  - GET/POST/PUT/DELETE /api/dishes                  │
│  - GET /api/dishes/<id>                             │
│                                                     │
│  Logging API:                                       │
│  - GET/POST/PUT/DELETE /api/log                     │
│  - GET /api/log/<date>                              │
│                                                     │
│  Statistics API:                                    │
│  - GET /api/stats/<date>                            │
│  - GET /api/stats/weekly                            │
│  - POST /api/gki                                    │
│                                                     │
│  Fasting API:                                       │
│  - POST /api/fasting/start                          │
│  - POST /api/fasting/end                            │
│  - POST /api/fasting/pause                          │
│  - POST /api/fasting/resume                         │
│  - GET /api/fasting/status                          │
│  - GET /api/fasting/sessions                        │
│  - GET /api/fasting/stats                           │
│                                                     │
│  Authentication API:                                │
│  - POST /api/auth/login                             │
│  - POST /api/auth/logout                            │
│  - POST /api/auth/refresh                           │
│  - GET /api/auth/verify                             │
│                                                     │
│  System API:                                        │
│  - GET /api/system/status                           │
│  - POST /api/backup                                 │
│  - POST /api/restore                                │
│  - POST /api/optimize                               │
│                                                     │
│  Monitoring API:                                    │
│  - GET /metrics (Prometheus format)                 │
│  - GET /api/metrics/summary                         │
│  - GET /health                                      │
└─────────────────────────────────────────────────────┘
```

**Key Features:**
- RESTful design principles
- Consistent JSON responses
- CORS support for cross-origin requests
- Rate limiting (100 req/hour)
- JWT authentication on protected endpoints

---

### 3. Business Logic Layer

```
┌─────────────────────────────────────────────────────┐
│  🧠 Core Business Logic                            │
├─────────────────────────────────────────────────────┤
│  Modules (src/):                                    │
│                                                     │
│  nutrition_calculator.py (416 statements, 86%)     │
│  - BMR/TDEE calculations                            │
│  - Macro calculations                               │
│  - Net carbs calculation                            │
│  - Calorie adjustments                              │
│                                                     │
│  fasting_manager.py (203 statements, 100%)         │
│  - Session management                               │
│  - Progress tracking                                │
│  - Statistics calculation                           │
│  - Goal management                                  │
│                                                     │
│  security.py (224 statements, 88%)                 │
│  - JWT token generation/validation                  │
│  - Password hashing (bcrypt)                        │
│  - Rate limiting                                    │
│  - Input validation                                 │
│                                                     │
│  cache_manager.py (172 statements, 94%)            │
│  - Redis caching                                    │
│  - In-memory fallback                               │
│  - Cache invalidation                               │
│  - TTL management                                   │
│                                                     │
│  task_manager.py (197 statements, 92%)             │
│  - Celery task management                           │
│  - Background job processing                        │
│  - Task status tracking                             │
│  - Synchronous fallback                             │
│                                                     │
│  monitoring.py (174 statements, 90%)               │
│  - Prometheus metrics                               │
│  - System monitoring                                │
│  - Application metrics                              │
│  - Custom metrics                                   │
│                                                     │
│  advanced_logging.py (189 statements, 93%)         │
│  - Structured logging                               │
│  - Log levels and rotation                          │
│  - ELK stack integration                            │
│  - Performance logging                              │
│                                                     │
│  utils.py (223 statements, 92%)                    │
│  - Validation functions                             │
│  - Database utilities                               │
│  - Helper functions                                 │
│  - Context managers                                 │
│                                                     │
│  ssl_config.py (138 statements, 91%)               │
│  - SSL/TLS configuration                            │
│  - Certificate management                           │
│  - Security headers                                 │
│  - HTTPS redirect                                   │
│                                                     │
│  config.py (25 statements, 92%)                    │
│  - Configuration management                         │
│  - Environment variables                            │
│  - Default settings                                 │
│                                                     │
│  constants.py (19 statements, 100%)                │
│  - Application constants                            │
│  - Configuration values                             │
│  - Fixed values                                     │
└─────────────────────────────────────────────────────┘
```

**Key Features:**
- High cohesion, low coupling
- Clear separation of concerns
- Extensive test coverage (91% overall)
- Type hints for critical functions
- Comprehensive error handling

---

### 4. Data Access Layer

```
┌─────────────────────────────────────────────────────┐
│  🗄️ Database Layer                                 │
├─────────────────────────────────────────────────────┤
│  SQLite Database (WAL mode):                        │
│                                                     │
│  Tables:                                            │
│  - products (nutrition data)                        │
│  - dishes (recipes)                                 │
│  - dish_ingredients (many-to-many)                  │
│  - daily_log (food logging)                         │
│  - user_profile (user settings)                     │
│  - fasting_sessions (fasting tracking)              │
│  - fasting_goals (goals)                            │
│  - auth_users (authentication)                      │
│  - auth_tokens (JWT tokens)                         │
│  - audit_logs (security audit)                      │
│                                                     │
│  Features:                                          │
│  - WAL mode (concurrent reads/writes)               │
│  - Foreign key constraints                          │
│  - Automatic backups                                │
│  - Connection pooling                               │
│  - Transaction support                              │
└─────────────────────────────────────────────────────┘
```

**Key Features:**
- SQLite with WAL mode for concurrency
- Automatic backups with integrity checks
- Foreign key constraints enforced
- Optimized indexes for queries
- Regular VACUUM operations

---

### 5. Infrastructure Layer

```
┌─────────────────────────────────────────────────────┐
│  🏗️ Infrastructure                                 │
├─────────────────────────────────────────────────────┤
│  Container Orchestration:                           │
│  - Docker (multi-stage builds)                      │
│  - docker-compose (service orchestration)           │
│  - ARM64 optimization                               │
│                                                     │
│  Web Server:                                        │
│  - Flask (application server)                       │
│  - Gunicorn (WSGI server, 4 workers)                │
│  - Nginx (reverse proxy)                            │
│  - SSL/TLS termination                              │
│                                                     │
│  Caching:                                           │
│  - Redis (primary cache)                            │
│  - In-memory fallback                               │
│                                                     │
│  Task Queue:                                        │
│  - Celery (background tasks)                        │
│  - Redis (broker)                                   │
│  - Synchronous fallback                             │
│                                                     │
│  Monitoring:                                        │
│  - Prometheus (metrics collection)                  │
│  - Grafana (visualization) [optional]               │
│  - Structured logging                               │
│                                                     │
│  CI/CD:                                             │
│  - GitHub Actions (test → build → deploy)           │
│  - Automated testing (545 tests)                    │
│  - Docker image building                            │
│  - Webhook deployment                               │
└─────────────────────────────────────────────────────┘
```

**Key Features:**
- Docker-based deployment
- ARM64 optimized images
- Multi-stage builds (small image size)
- Health checks and monitoring
- Automatic restarts on failure

---

## 🔄 Data Flow

### Read Operation Flow
```
User Request
    ↓
Nginx (reverse proxy)
    ↓
Gunicorn (WSGI)
    ↓
Flask Route Handler
    ↓
Cache Manager (check cache)
    ↓ (cache miss)
Business Logic Layer
    ↓
Database Query
    ↓
Cache Manager (store result)
    ↓
JSON Response
    ↓
User
```

### Write Operation Flow
```
User Request
    ↓
Nginx (reverse proxy)
    ↓
Gunicorn (WSGI)
    ↓
Flask Route Handler
    ↓
Security Layer (validate, authorize)
    ↓
Business Logic Layer (validate, process)
    ↓
Database Write
    ↓
Cache Manager (invalidate)
    ↓
Background Task (async processing) [optional]
    ↓
JSON Response
    ↓
User
```

---

## 🎯 Design Patterns

### Current Patterns

1. **MVC Pattern** (Modified)
   - Model: Database layer + business logic
   - View: HTML templates + JavaScript
   - Controller: Flask routes

2. **Repository Pattern** (Partial)
   - Database operations abstracted in modules
   - Not fully implemented (future improvement)

3. **Facade Pattern**
   - Simplified interfaces for complex subsystems
   - Example: cache_manager, task_manager

4. **Decorator Pattern**
   - Route decorators
   - Authentication decorators (planned)
   - Error handling decorators (planned)

5. **Singleton Pattern**
   - Configuration objects
   - Cache manager instance
   - Database connections (pooled)

---

## 🔐 Security Architecture

### Defense in Depth

```
Layer 1: Network
- Firewall (UFW)
- Fail2ban (brute force protection)
- Rate limiting (nginx + application)

Layer 2: Transport
- HTTPS/TLS 1.2+ (SSL certificates)
- Security headers (HSTS, CSP, XSS)
- Secure cookies

Layer 3: Application
- JWT authentication
- Password hashing (bcrypt)
- Input validation and sanitization
- SQL injection prevention
- XSS protection

Layer 4: Data
- Database encryption at rest [planned]
- Sensitive data hashing
- Regular backups
- Audit logging
```

### Authentication Flow
```
Login Request
    ↓
Validate credentials (bcrypt)
    ↓
Generate JWT tokens (access + refresh)
    ↓
Store tokens in database
    ↓
Return tokens to client
    ↓
Client stores in memory (not localStorage)
    ↓
Subsequent requests include JWT
    ↓
Validate JWT on server
    ↓
Check rate limits
    ↓
Process request
```

---

## 📊 Performance Optimizations

### Caching Strategy
- **L1 Cache:** In-memory (fastest)
- **L2 Cache:** Redis (persistent)
- **Cache Keys:** Structured with TTL
- **Invalidation:** On data changes

### Database Optimizations
- **WAL Mode:** Concurrent reads during writes
- **Indexes:** On frequently queried columns
- **Connection Pooling:** Reuse connections
- **VACUUM:** Regular database maintenance

### Resource Management
- **Memory Limit:** 800MB (Pi 4 optimized)
- **Worker Count:** 4 Gunicorn workers
- **Connection Pool:** Limited connections
- **Temperature Monitoring:** Prevent throttling

---

## 🚀 Deployment Architecture

### Docker Compose Services

```yaml
services:
  nutrition-app:
    - Flask application
    - Gunicorn WSGI server
    - Health checks
    - Auto-restart
  
  nutrition-nginx:
    - Reverse proxy
    - SSL termination
    - Static file serving
    - Gzip compression
  
  redis:
    - Cache server
    - Session storage
    - Celery broker
    - Persistence enabled
  
  celery:
    - Background workers
    - Task processing
    - Monitoring
    - Auto-scaling
```

### Resource Allocation
```
Total RAM: 4GB (Pi 4 Model B 2018)
- System: ~500MB
- nutrition-app: ~600MB
- nginx: ~50MB
- redis: ~100MB
- celery: ~200MB
- Other: ~550MB (buffer)
```

---

## 🔮 Future Architecture Plans

### Phase 1: Service Extraction (Month 1-2)
- Extract API blueprints
- Create service layer
- Repository pattern

### Phase 2: Microservices Preparation (Month 3-4)
- Modular architecture
- Independent deployment units
- API gateway pattern

### Phase 3: Scalability (Month 5-6)
- Horizontal scaling readiness
- Load balancing
- Distributed caching

---

## 📚 Architecture Documentation

### Related Documents
- 📊 [NUTRICOUNT_ARCHITECTURE_DIAGRAM.md](NUTRICOUNT_ARCHITECTURE_DIAGRAM.md) - Visual diagrams
- 🧠 [NUTRICOUNT_MINDMAP_AND_TEST_COVERAGE.md](NUTRICOUNT_MINDMAP_AND_TEST_COVERAGE.md) - Mindmap
- 🔍 [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md) - Detailed analysis
- 🧪 [TEST_COVERAGE_REPORT.md](TEST_COVERAGE_REPORT.md) - Coverage details
- 🔧 [REFACTORING.md](REFACTORING.md) - Refactoring history
- 📖 [PROJECT_SETUP.md](PROJECT_SETUP.md) - Setup guide

---

**Last Updated:** October 20, 2025  
**Next Review:** November 2025  
**Status:** ✅ Current and Accurate
