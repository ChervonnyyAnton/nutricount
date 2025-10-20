# 🛠️ Nutricount Scripts

This directory contains utility scripts for development, testing, deployment, and maintenance.

---

## 📜 Available Scripts

### 🧬 Mutation Testing

#### `run_mutation_baseline.sh` (NEW!)
**Purpose:** Run comprehensive mutation testing baseline for Phase 2 refactoring

**Usage:**
```bash
# Show help
./scripts/run_mutation_baseline.sh help

# Quick baseline (simple modules, 2-3 hours)
./scripts/run_mutation_baseline.sh quick

# Critical modules (utils, security, 6-8 hours)
./scripts/run_mutation_baseline.sh critical

# Core modules (cache, monitoring, fasting, 8-10 hours)
./scripts/run_mutation_baseline.sh core

# Specific module
./scripts/run_mutation_baseline.sh utils

# All modules (WARNING: 8-12 hours!)
./scripts/run_mutation_baseline.sh all
```

**Features:**
- Multiple execution modes (quick, critical, core, all)
- Individual module testing
- Automatic report generation
- Detailed time estimates
- Progress logging

**Documentation:** See [PHASE2_EXECUTION_GUIDE.md](../PHASE2_EXECUTION_GUIDE.md)

---

#### `mutation_test.sh`
**Purpose:** Interactive mutation testing script

**Usage:**
```bash
# Run mutation testing
./scripts/mutation_test.sh src/module.py run

# View results
./scripts/mutation_test.sh src/module.py results

# Generate HTML report
./scripts/mutation_test.sh src/module.py html
```

---

### 🧪 Testing

#### `run_tests.sh`
**Purpose:** Run test suite with various options

**Usage:**
```bash
# Install test dependencies
./scripts/run_tests.sh install

# Run all tests
./scripts/run_tests.sh all

# Run specific test type
./scripts/run_tests.sh unit
./scripts/run_tests.sh integration
./scripts/run_tests.sh e2e

# Generate coverage report
./scripts/run_tests.sh report

# Clean test artifacts
./scripts/run_tests.sh clean
```

---

### 📊 Monitoring & Maintenance

#### `monitor.sh`
**Purpose:** Monitor system resources and application health

**Usage:**
```bash
# One-time check
./scripts/monitor.sh

# Continuous monitoring
./scripts/monitor.sh --continuous

# View logs
./scripts/monitor.sh --logs
```

**Monitors:**
- CPU usage
- Memory usage
- Disk space
- Temperature (Raspberry Pi)
- Container status
- Application health

---

#### `backup.sh`
**Purpose:** Create database backups with integrity checks

**Usage:**
```bash
# Manual backup
./scripts/backup.sh

# Backup with compression
./scripts/backup.sh --compress

# Backup to specific location
./scripts/backup.sh --output /path/to/backup
```

**Features:**
- Automatic backup rotation
- Integrity verification
- Compression support
- Timestamp naming

---

#### `healthcheck.sh`
**Purpose:** Application health check for Docker

**Usage:**
```bash
# Check application health
./scripts/healthcheck.sh
```

**Checks:**
- API endpoint availability
- Database connectivity
- Redis connectivity (optional)
- Response time

---

### 🚀 Deployment & Setup

#### `setup.sh`
**Purpose:** Automated setup for Raspberry Pi deployment

**Usage:**
```bash
# Full setup
./scripts/setup.sh

# Specific setup steps
./scripts/setup.sh --docker-only
./scripts/setup.sh --system-only
```

**Features:**
- Docker installation
- System optimization
- Dependency setup
- Configuration templates

---

#### `auto_update.sh`
**Purpose:** Automated application updates

**Usage:**
```bash
# Update application
./scripts/auto_update.sh

# Update with rebuild
./scripts/auto_update.sh --rebuild
```

**Features:**
- Git pull latest changes
- Docker rebuild
- Service restart
- Rollback on failure

---

#### `simple_update.sh`
**Purpose:** Simple update without Docker rebuild

**Usage:**
```bash
# Quick update
./scripts/simple_update.sh
```

---

#### `cron_update.sh`
**Purpose:** Scheduled updates via cron

**Setup:**
```bash
# Add to crontab
# Run daily at 3 AM
0 3 * * * /path/to/nutricount/scripts/cron_update.sh
```

---

## 🎯 Quick Reference

### Phase 2 Execution
```bash
# 1. Setup environment
export PYTHONPATH=/home/runner/work/nutricount/nutricount
cd /home/runner/work/nutricount/nutricount

# 2. Verify tests
./scripts/run_tests.sh all

# 3. Run mutation baseline
./scripts/run_mutation_baseline.sh quick  # Start small

# 4. View results
mutmut results
mutmut html
```

### Regular Testing
```bash
# Run all tests
./scripts/run_tests.sh all

# Run with coverage
./scripts/run_tests.sh report

# Run mutation testing
./scripts/mutation_test.sh src/utils.py run
```

### Monitoring
```bash
# Check system
./scripts/monitor.sh

# Continuous monitoring
./scripts/monitor.sh --continuous

# Create backup
./scripts/backup.sh
```

### Deployment
```bash
# Initial setup
./scripts/setup.sh

# Update application
./scripts/auto_update.sh

# Quick update
./scripts/simple_update.sh
```

---

## 📚 Related Documentation

- [README.md](../README.md) - Main project documentation
- [PROJECT_SETUP.md](../PROJECT_SETUP.md) - Development setup guide
- [PHASE2_EXECUTION_GUIDE.md](../PHASE2_EXECUTION_GUIDE.md) - Mutation testing guide
- [PHASE2_CHECKLIST.md](../PHASE2_CHECKLIST.md) - Execution checklist
- [MUTATION_TESTING.md](../MUTATION_TESTING.md) - Mutation testing documentation
- [TEST_COVERAGE_REPORT.md](../TEST_COVERAGE_REPORT.md) - Coverage report

---

## 🔧 Script Permissions

All scripts should be executable:

```bash
# Make all scripts executable
chmod +x scripts/*.sh

# Or individually
chmod +x scripts/run_mutation_baseline.sh
chmod +x scripts/run_tests.sh
chmod +x scripts/monitor.sh
```

---

## 💡 Tips

### Running Long Tasks
```bash
# Run in background with nohup
nohup ./scripts/run_mutation_baseline.sh all > logs/mutation.log 2>&1 &

# Check progress
tail -f logs/mutation.log

# Find process
ps aux | grep mutation
```

### Scheduling Tasks
```bash
# Edit crontab
crontab -e

# Add scheduled task
# Daily backup at 2 AM
0 2 * * * /path/to/nutricount/scripts/backup.sh

# Weekly mutation testing (Sunday 1 AM)
0 1 * * 0 /path/to/nutricount/scripts/mutation_test.sh src/ run
```

---

**Last Updated:** October 20, 2025  
**Maintained by:** Nutricount Development Team
