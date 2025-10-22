# DevOps Documentation

**Target Audience:** DevOps Engineers, Site Reliability Engineers, Platform Engineers  
**Status:** ✅ Complete (Week 3)  
**Last Updated:** October 22, 2025

## Overview

This section provides comprehensive guides for DevOps engineers working on the Nutricount project, covering CI/CD, deployment, monitoring, and infrastructure management.

## Documentation

### CI/CD Pipeline
📄 **[CI/CD Pipeline Guide](ci-cd-pipeline.md)** - Complete CI/CD methodology
- GitHub Actions workflows
- Deployment automation
- Docker configuration
- Monitoring & alerts
- Rollback procedures
- Environment management

## Quick Start for DevOps Engineers

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/ChervonnyyAnton/nutricount.git
cd nutricount

# Copy environment variables
cp .env.example .env

# Start with Docker Compose
docker-compose up -d

# Verify deployment
curl http://localhost/health
```

### CI/CD Pipeline Overview

```
Pull Request → Lint & Test → Security Scan → Build Docker → Deploy (main only)
     ↓              ↓             ↓              ↓              ↓
  3 min         1 min         1 min         5 min         2 min
```

**Total Pipeline Time:** ~12 minutes

## Infrastructure Components

### Production Stack

```
┌─────────────────────────────────────────────┐
│         Raspberry Pi 4 Model B 2018         │
│              ARM64, 4GB RAM                 │
├─────────────────────────────────────────────┤
│                                             │
│  ┌────────────┐  ┌────────────┐           │
│  │   Nginx    │  │   Redis    │           │
│  │  (Proxy)   │  │  (Cache)   │           │
│  └─────┬──────┘  └─────┬──────┘           │
│        │                │                   │
│  ┌─────▼────────────────▼──────┐           │
│  │    Flask Application        │           │
│  │    (Gunicorn + Workers)     │           │
│  └─────────────┬─────────────┘            │
│                │                            │
│  ┌─────────────▼─────────────┐             │
│  │      SQLite (WAL)         │             │
│  └───────────────────────────┘             │
│                                             │
└─────────────────────────────────────────────┘
```

### Docker Services

| Service | Image | Purpose | Port |
|---------|-------|---------|------|
| nutricount | custom:latest | Flask app | 5000 |
| redis | redis:7-alpine | Cache | 6379 |
| nginx | nginx:alpine | Reverse proxy | 80, 443 |

## Deployment Strategies

### 1. Rolling Deployment (Current)

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose up -d --build
```

**Downtime:** 5-10 seconds

### 2. Blue-Green Deployment (Week 5 - Planned)

```bash
# Deploy to blue environment
docker-compose -f docker-compose.blue.yml up -d

# Switch traffic
nginx reload

# Teardown green environment
docker-compose -f docker-compose.green.yml down
```

**Downtime:** Zero

## Monitoring & Observability

### Key Metrics

**Application Metrics (Prometheus):**
- HTTP request rate and latency
- Error rates by endpoint
- Active users and sessions
- Database query performance

**System Metrics:**
- CPU usage and temperature
- Memory usage
- Disk I/O
- Network traffic

**Raspberry Pi Specific:**
- Temperature (critical: >80°C)
- Throttling status
- Power supply voltage
- SD card health

### Health Checks

```bash
# Application health
curl http://localhost/health

# Prometheus metrics
curl http://localhost/metrics

# Temperature check
./scripts/temp_monitor.sh --check

# Complete system check
./scripts/monitor.sh
```

## Performance Optimization

### Raspberry Pi Tuning

**CPU Frequency:**
```bash
# /boot/config.txt
arm_freq=1500
over_voltage=1
temp_limit=75
```

**Swap Memory:**
```bash
# Increase swap for builds
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

**Docker Optimization:**
```yaml
# docker-compose.yml
services:
  nutricount:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

## Backup & Recovery

### Automated Backups

```bash
# Database backup (daily cron job)
0 3 * * * /opt/nutricount/scripts/backup.sh

# Backup script creates:
# - Database dump
# - Configuration files
# - Uploaded files
# - Stored in /backups with 7-day retention
```

### Restore Procedure

```bash
# Stop application
docker-compose down

# Restore database
cp /backups/latest/nutricount.db /data/

# Restart application
docker-compose up -d

# Verify
curl http://localhost/health
```

## Security Hardening

### SSL/TLS Configuration

```bash
# Generate certificates
./scripts/setup_ssl.sh raspberry-pi.local

# Nginx SSL config
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
```

### Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny all other incoming
sudo ufw default deny incoming
```

### Rate Limiting

```python
# Application-level (Redis-based)
RATE_LIMIT_API = "100/hour"
RATE_LIMIT_AUTH = "10/hour"
RATE_LIMIT_ADMIN = "200/hour"
```

## Troubleshooting

### Common Issues

#### High Memory Usage

```bash
# Check memory
free -h

# Restart services
docker-compose restart

# Clean up images
docker system prune -a
```

#### High Temperature

```bash
# Check temperature
vcgencmd measure_temp

# Check throttling
vcgencmd get_throttled

# Solutions:
# 1. Improve cooling
# 2. Reduce CPU frequency
# 3. Limit Docker resources
```

#### Slow Performance

```bash
# Check CPU load
htop

# Check disk I/O
iostat -x 1

# Check database
sqlite3 /data/nutricount.db "PRAGMA integrity_check;"
```

## CI/CD Best Practices

### Pipeline Configuration

✅ **Do:**
- Run tests in parallel where possible
- Use Docker layer caching
- Fail fast on critical errors
- Monitor pipeline performance
- Keep workflows DRY

❌ **Don't:**
- Run full test suite on every commit
- Build for unnecessary platforms
- Skip security scans
- Ignore flaky tests
- Deploy without health checks

### Deployment Checklist

- [ ] All tests pass
- [ ] Security scan clean
- [ ] Docker image built successfully
- [ ] Backup created
- [ ] Rollback plan ready
- [ ] Health checks configured
- [ ] Monitoring alerts active

## Resources

- [CI/CD Pipeline Guide](ci-cd-pipeline.md) - Detailed CI/CD setup
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Raspberry Pi Optimization](../../PROJECT_SETUP.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Prometheus Monitoring](https://prometheus.io/docs/)

## Infrastructure as Code

### Terraform (Planned - Week 6)

```hcl
# main.tf
resource "aws_instance" "nutricount" {
  ami           = "ami-raspberry-pi"
  instance_type = "arm64.small"
  
  tags = {
    Name = "nutricount-production"
  }
}
```

### Ansible (Planned - Week 6)

```yaml
# playbook.yml
- name: Deploy Nutricount
  hosts: raspberry-pi
  tasks:
    - name: Pull latest code
      git:
        repo: https://github.com/ChervonnyyAnton/nutricount.git
        dest: /opt/nutricount
    
    - name: Start services
      community.docker.docker_compose:
        project_src: /opt/nutricount
        state: present
```

## Support

For DevOps questions or issues:
1. Check the [CI/CD Pipeline Guide](ci-cd-pipeline.md)
2. Review GitHub Actions logs
3. Check system logs: `docker-compose logs -f`
4. Contact the development team

---

**Educational Expansion:** See [EDUCATIONAL_EXPANSION_PLAN.md](../../EDUCATIONAL_EXPANSION_PLAN.md) for the complete DevOps learning path.

**Status:** ✅ Complete (Week 3 - DevOps CI/CD)

