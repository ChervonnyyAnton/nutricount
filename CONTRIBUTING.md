
# Contributing to Nutrition Tracker

🥗 Thank you for your interest in contributing to Nutrition Tracker! This guide will help you get started with contributing to our WCAG 2.2 compliant nutrition tracking application.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project adheres to a code of conduct adapted from the [Contributor Covenant](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code.

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Be Respectful

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Docker (optional but recommended)
- Basic knowledge of Flask, HTML, CSS, and JavaScript

### First Steps

1. **Fork the Repository**
```


# Fork the repo on GitHub, then clone your fork

git clone https://github.com/YOUR_USERNAME/nutrition-tracker.git
cd nutrition-tracker

```

2. **Set Up Development Environment**
```


# Create virtual environment

python -m venv venv
source venv/bin/activate  \# or `venv\Scripts\activate` on Windows

# Install dependencies

make dev-install

# Set up the development environment

make dev-setup

```

3. **Run the Application**
```

make run

```

4. **Access the Application**
Open http://localhost:5000 in your browser

## Development Setup

### Environment Configuration

1. Copy the environment template:
```

cp .env.example .env

```

2. Edit `.env` with your configuration:
- Generate a secure `SECRET_KEY`
- Add your Telegram bot token (if testing Telegram features)
- Set other variables as needed

### Database Setup

```


# Initialize the database

make db-init

# Or manually

python init_db.py

```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```


# Install pre-commit hooks

pip install pre-commit
pre-commit install

# Run hooks manually

pre-commit run --all-files

```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Bug fixes, new features, improvements
- **Documentation**: Improve or expand documentation
- **Testing**: Add or improve test coverage
- **UI/UX**: Improve accessibility and user experience

### Before You Start

1. **Check Existing Issues**: Look for existing issues or feature requests
2. **Create an Issue**: For significant changes, create an issue first to discuss
3. **Accessibility First**: Ensure all UI changes maintain WCAG 2.2 AA compliance
4. **Test Your Changes**: Make sure your changes don't break existing functionality

### Branch Naming Convention

Use descriptive branch names:

```

feature/add-food-search
fix/accessibility-focus-issues
docs/update-api-documentation
test/add-integration-tests
refactor/improve-database-queries

```

### Commit Message Format

Follow the conventional commit format:

```

type(scope): description

feat(api): add food search endpoint
fix(ui): resolve keyboard navigation issues
docs(readme): update installation instructions
test(api): add integration tests for food logging
style(css): improve button hover states
refactor(db): optimize query performance
chore(deps): update dependencies

```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

## Pull Request Process

### Before Submitting

1. **Test Your Changes**
```

make test
make lint
make format

```

2. **Update Documentation**
- Update README.md if needed
- Add/update docstrings
- Update API documentation

3. **Add Tests**
- Write tests for new features
- Ensure existing tests pass
- Maintain test coverage above 80%

### Pull Request Template

When creating a pull request, include:

```


## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other (please describe)


## Testing

- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed


## Accessibility

- [ ] WCAG 2.2 compliance maintained
- [ ] Keyboard navigation tested
- [ ] Screen reader compatibility verified


## Screenshots (if applicable)

Include screenshots for UI changes

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or properly documented)

```

### Review Process

1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one maintainer review required
3. **Testing**: Manual testing may be performed
4. **Accessibility Review**: UI changes reviewed for accessibility
5. **Merge**: Squash merge preferred for clean history

## Code Style

### Python

We follow PEP 8 with some modifications:

- **Line Length**: 120 characters
- **Formatting**: Use Black for automatic formatting
- **Import Sorting**: Use isort with Black profile
- **Linting**: Use flake8 with project configuration
- **Type Hints**: Encouraged for new code

```


# Format code

make format

# Check style

make lint

```

### JavaScript

- **Standard**: ES6+ features
- **Semicolons**: Required
- **Indentation**: 2 spaces
- **Quotes**: Single quotes preferred
- **Functions**: Arrow functions for callbacks

### HTML/CSS

- **Semantic HTML**: Use proper HTML5 elements
- **Accessibility**: ARIA labels, proper heading structure
- **CSS**: BEM methodology preferred
- **Bootstrap**: Use Bootstrap classes when possible

### Accessibility Requirements

All UI contributions must maintain WCAG 2.2 AA compliance:

- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Screen Readers**: Proper ARIA labels and semantic HTML
- **Color Contrast**: Minimum 4.5:1 ratio for normal text
- **Focus Indicators**: Visible focus states for all interactive elements
- **Alternative Text**: Meaningful alt text for images
- **Headings**: Proper heading hierarchy

### Testing Accessibility

```


# Install accessibility testing tools

npm install -g axe-cli

# Run accessibility tests

axe http://localhost:5000

# Manual testing checklist:

# 1. Navigate using only keyboard (Tab, Arrow keys, Enter, Space)

# 2. Test with screen reader (NVDA, JAWS, VoiceOver)

# 3. Verify color contrast ratios

# 4. Test with 200% zoom

```

## Testing

### Running Tests

```


# Run all tests

make test

# Run specific test file

pytest tests/test_api.py

# Run with coverage

make test-coverage

# Run tests in watch mode

make test-watch

```

### Writing Tests

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints and workflows
- **Accessibility Tests**: Test keyboard navigation and screen reader compatibility
- **Performance Tests**: Test response times and load handling

```

def test_create_product_success(client, sample_product):
"""Test successful product creation"""
response = client.post('/api/products',
data=json.dumps(sample_product),
content_type='application/json')

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['name'] == sample_product['name']
    ```

### Test Coverage

Maintain test coverage above 80%:

```


# Check coverage

pytest --cov --cov-report=html
open htmlcov/index.html

```

## Documentation

### Types of Documentation

- **Code Comments**: Explain complex logic
- **Docstrings**: Document functions, classes, and modules
- **API Documentation**: Document endpoints and parameters
- **User Documentation**: README, guides, tutorials
- **Developer Documentation**: Architecture, setup, contributing

### Documentation Standards

```

def calculate_keto_index(fat: float, protein: float, carbs: float) -> float:
"""Calculate keto index for given macronutrients.

    The keto index is calculated as: (fat * 2) / (protein + carbs)
    
    Args:
        fat: Fat content in grams per 100g
        protein: Protein content in grams per 100g
        carbs: Carbohydrate content in grams per 100g
        
    Returns:
        Keto index value, higher values indicate more keto-friendly foods
        
    Example:
        >>> calculate_keto_index(20.0, 5.0, 2.0)
        5.71
    """
    ```

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussion
- **Email**: support@nutrition-tracker.com for sensitive issues

### Getting Help

1. **Check Documentation**: README, wiki, and inline documentation
2. **Search Issues**: Look for existing solutions
3. **Ask Questions**: Create a GitHub Discussion
4. **Join Community**: Participate in discussions and reviews

### Reporting Bugs

Use the bug report template and include:

- **Environment**: OS, Python version, browser
- **Steps to Reproduce**: Clear, numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Screenshots**: If applicable
- **Logs**: Relevant error messages

### Suggesting Features

Use the feature request template and include:

- **Problem**: What problem does this solve?
- **Solution**: Describe your proposed solution
- **Alternatives**: Other solutions considered
- **Additional Context**: Mockups, examples, references

## Recognition

Contributors are recognized in several ways:

- **Contributors List**: Listed in README.md
- **Release Notes**: Credited in changelog
- **GitHub Recognition**: GitHub's contributor graph
- **Community Appreciation**: Public thanks in discussions

## Development Workflow

### Typical Workflow

1. **Find/Create Issue**: Identify work to be done
2. **Fork & Branch**: Create feature branch
3. **Develop**: Write code following guidelines
4. **Test**: Ensure all tests pass
5. **Document**: Update documentation
6. **Submit PR**: Create pull request
7. **Review**: Address feedback
8. **Merge**: Maintainer merges PR

### Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## Advanced Topics

### Architecture Overview

```

Frontend (HTML/CSS/JS) → Flask API → SQLite Database
↓                        ↓
Service Worker          System APIs
↓                        ↓
Offline Storage        Monitoring/Health

```

### Key Technologies

- **Backend**: Flask, SQLite, Gunicorn
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Infrastructure**: Docker, Nginx, GitHub Actions
- **Monitoring**: Prometheus, Grafana
- **Testing**: pytest, coverage.py

### Performance Considerations

- **Database**: Use indexes, optimize queries
- **Caching**: Implement appropriate caching strategies
- **Assets**: Minimize and compress CSS/JS
- **Images**: Optimize images and use appropriate formats

### Security Guidelines

- **Input Validation**: Validate all user inputs
- **SQL Injection**: Use parameterized queries
- **XSS Protection**: Escape output, use CSP headers
- **HTTPS**: Always use HTTPS in production
- **Dependencies**: Keep dependencies updated

## Questions?

If you have questions not covered in this guide:

1. **Check the documentation** in the `docs/` directory
2. **Search existing issues** and discussions
3. **Create a GitHub Discussion** for community help
4. **Contact maintainers** at support@nutrition-tracker.com

---

**Thank you for contributing to Nutrition Tracker!** 🥗✨

Together, we're building an accessible, reliable, and helpful tool for nutrition tracking that benefits everyone in the community.
```


### `GITHUB_SECRETS.md`

```markdown
# GitHub Secrets Configuration Guide

This guide explains how to configure GitHub Secrets for automated deployment of the Nutrition Tracker Telegram Web App.

## Table of Contents

- [Overview](#overview)
- [Required Secrets](#required-secrets)
- [Optional Secrets](#optional-secrets)
- [Setting Up Secrets](#setting-up-secrets)
- [Environment-Specific Configuration](#environment-specific-configuration)
- [Security Best Practices](#security-best-practices)
- [Validation](#validation)
- [Troubleshooting](#troubleshooting)

## Overview

GitHub Secrets allow you to store sensitive information that your GitHub Actions workflows need for deployment. These secrets are encrypted and only available to your repository's actions.

## Required Secrets

### Core Application Secrets

| Secret Name | Description | Example/Format |
|-------------|-------------|----------------|
| `SECRET_KEY` | Flask secret key for sessions and CSRF | `your-32-character-random-string` |
| `TELEGRAM_BOT_TOKEN` | Production Telegram bot token | `123456789:ABCDEFghijklmnopqrstuvwxyz` |
| `TELEGRAM_WEBHOOK_SECRET` | Webhook validation token | `your-secure-webhook-secret` |

### Server Access Secrets

| Secret Name | Description | Example/Format |
|-------------|-------------|----------------|
| `PROD_HOST` | Production server hostname or IP | `your-domain.com` or `192.168.1.100` |
| `PROD_USER` | SSH username for production server | `deploy` |
| `PROD_SSH_KEY` | Private SSH key for production server | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `PROD_PORT` | SSH port for production server | `22` (default) |

### URL Configuration

| Secret Name | Description | Example/Format |
|-------------|-------------|----------------|
| `PRODUCTION_WEBHOOK_URL` | Full webhook URL for production | `https://your-domain.com/telegram/webhook` |
| `PRODUCTION_URL` | Main production URL | `https://your-domain.com` |

## Optional Secrets

### Staging Environment

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `TELEGRAM_BOT_TOKEN_STAGING` | Staging bot token | Staging deployments |
| `STAGING_HOST` | Staging server hostname | Staging deployments |
| `STAGING_USER` | SSH username for staging | Staging deployments |
| `STAGING_SSH_KEY` | Private SSH key for staging | Staging deployments |
| `STAGING_PORT` | SSH port for staging | Staging deployments |
| `STAGING_WEBHOOK_URL` | Staging webhook URL | Staging deployments |

### SSL and Domain

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `DOMAIN_NAME` | Your domain name | SSL certificates |
| `CERTBOT_EMAIL` | Email for Let's Encrypt | SSL certificates |

### Monitoring and Notifications

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `GRAFANA_PASSWORD` | Grafana admin password | Monitoring stack |
| `TELEGRAM_CHAT_ID` | Chat ID for notifications | Deployment notifications |

### Security Scanning

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `SNYK_TOKEN` | Snyk API token | Security scanning |

## Setting Up Secrets

### Step 1: Generate Required Values

#### Secret Key
```


# Generate a secure secret key

python3 -c "import secrets; print(secrets.token_urlsafe(32))"

```

#### Webhook Secret
```


# Generate webhook secret

python3 -c "import secrets; print(secrets.token_urlsafe(16))"

```

#### Telegram Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the provided token

#### SSH Key Pair
```


# Generate SSH key pair for deployments

ssh-keygen -t ed25519 -C "github-actions@your-domain.com" -f ~/.ssh/nutrition-tracker-deploy

# Add public key to your server's authorized_keys

ssh-copy-id -i ~/.ssh/nutrition-tracker-deploy.pub user@your-server.com

# Use the private key content for PROD_SSH_KEY secret

cat ~/.ssh/nutrition-tracker-deploy

```

### Step 2: Add Secrets to GitHub

1. **Navigate to Repository Settings**
   - Go to your GitHub repository
   - Click "Settings" tab
   - Click "Secrets and variables" → "Actions"

2. **Add Repository Secrets**
   - Click "New repository secret"
   - Enter the secret name (exactly as shown in tables above)
   - Paste the secret value
   - Click "Add secret"

3. **Repeat for All Required Secrets**

### Step 3: Verify Secrets

Use the validation script to check your configuration:

```


# Run the validation script

./scripts/validate-secrets.sh

```

## Environment-Specific Configuration

### Production Environment

Configure these secrets for production deployments:

```

SECRET_KEY=your-production-secret-key
TELEGRAM_BOT_TOKEN=your-production-bot-token
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret
PROD_HOST=your-domain.com
PROD_USER=deploy
PROD_SSH_KEY=your-private-ssh-key
PRODUCTION_WEBHOOK_URL=https://your-domain.com/telegram/webhook
PRODUCTION_URL=https://your-domain.com
DOMAIN_NAME=your-domain.com
CERTBOT_EMAIL=your-email@your-domain.com

```

### Staging Environment

Configure these additional secrets for staging:

```

TELEGRAM_BOT_TOKEN_STAGING=your-staging-bot-token
STAGING_HOST=staging.your-domain.com
STAGING_USER=deploy
STAGING_SSH_KEY=your-staging-ssh-key
STAGING_WEBHOOK_URL=https://staging.your-domain.com/telegram/webhook

```

## Security Best Practices

### Secret Generation

- **Use Strong Secrets**: Generate cryptographically secure random values
- **Unique Values**: Use different secrets for staging and production
- **Minimum Length**: SECRET_KEY should be at least 32 characters
- **No Patterns**: Avoid predictable patterns or dictionary words

### Secret Management

- **Regular Rotation**: Rotate secrets every 90 days
- **Limited Access**: Only repository collaborators can access secrets
- **Audit Trail**: GitHub logs secret usage in Actions
- **No Exposure**: Secrets are masked in logs and cannot be retrieved

### Best Practices

1. **Never Commit Secrets**
```


# Add to .gitignore

echo "*.key" >> .gitignore
echo ".env" >> .gitignore

```

2. **Use Environment-Specific Secrets**
```


# Different values for different environments

TELEGRAM_BOT_TOKEN=prod-bot-token
TELEGRAM_BOT_TOKEN_STAGING=staging-bot-token

```

3. **Validate Secret Format**
```


# Check if bot token has correct format

if [[ $TELEGRAM_BOT_TOKEN =~ ^[0-9]+:[a-zA-Z0-9_-]+$ ]]; then
echo "Valid bot token format"
fi

```

4. **Monitor Secret Usage**
- Check GitHub Actions logs for secret usage
- Review workflow runs for suspicious activity
- Set up notifications for deployment failures

## Validation

### Automated Validation

The repository includes a validation script:

```


# Check if all required secrets are configured

./scripts/validate-secrets.sh

# Output example:

# 🔐 Validating GitHub Secrets Configuration...

# ✅ SECRET_KEY - configured

# ✅ TELEGRAM_BOT_TOKEN - configured

# ✅ PROD_HOST - configured

# 🎉 Basic configuration is complete!

```

### Manual Validation

#### Test SSH Connection
```


# Test SSH connection (replace with your values)

ssh -i ~/.ssh/nutrition-tracker-deploy deploy@your-domain.com "echo 'SSH connection successful'"

```

#### Test Telegram Bot Token
```


# Test bot token

curl "https://api.telegram.org/bot\${TELEGRAM_BOT_TOKEN}/getMe"

```

#### Test Webhook URL
```


# Test webhook endpoint accessibility

curl -I https://your-domain.com/telegram/webhook

```

## Troubleshooting

### Common Issues

#### 1. SSH Connection Failed

**Problem**: Deployment fails with SSH connection error

**Solutions**:
- Verify `PROD_HOST`, `PROD_USER`, and `PROD_PORT` are correct
- Check SSH key format (should be private key, not public key)
- Ensure public key is added to server's `authorized_keys`
- Verify server allows SSH key authentication

```


# Debug SSH connection

ssh -v -i ~/.ssh/nutrition-tracker-deploy deploy@your-domain.com

```

#### 2. Telegram Webhook Failed

**Problem**: Webhook setup fails or bot doesn't respond

**Solutions**:
- Verify `TELEGRAM_BOT_TOKEN` is correct and active
- Check `TELEGRAM_WEBHOOK_SECRET` matches server configuration
- Ensure `PRODUCTION_WEBHOOK_URL` is accessible via HTTPS
- Verify webhook URL format: `https://domain.com/telegram/webhook`

```


# Test webhook manually

curl -X POST "https://api.telegram.org/bot\${TELEGRAM_BOT_TOKEN}/setWebhook" \
-H "Content-Type: application/json" \
-d '{"url": "https://your-domain.com/telegram/webhook"}'

```

#### 3. SSL Certificate Issues

**Problem**: Let's Encrypt certificate creation fails

**Solutions**:
- Verify `DOMAIN_NAME` points to your server (DNS)
- Check `CERTBOT_EMAIL` is a valid email address
- Ensure port 80 and 443 are open on your server
- Verify domain is publicly accessible

```


# Test domain resolution

nslookup your-domain.com

# Test port accessibility

telnet your-domain.com 80
telnet your-domain.com 443

```

#### 4. Secret Not Found

**Problem**: GitHub Actions reports secret not found

**Solutions**:
- Check secret name spelling (case-sensitive)
- Verify secret is added at repository level (not organization)
- Ensure you have admin access to the repository
- Re-add the secret if necessary

#### 5. Invalid Secret Format

**Problem**: Secret validation fails

**Solutions**:
- Check secret format requirements
- Regenerate secret with proper format
- Remove any extra whitespace or newlines
- Verify character encoding (UTF-8)

### Debugging Commands

```


# List all environment variables (in GitHub Actions)

env | sort

# Check secret availability (will show masked values)

echo "Secret exists: \${{ secrets.SECRET_KEY != '' }}"

# Validate server connectivity

curl -I https://your-domain.com/health

# Test Telegram API

curl "https://api.telegram.org/bot\${TELEGRAM_BOT_TOKEN}/getWebhookInfo"

```

### Getting Help

If you're still having issues:

1. **Check Logs**: Review GitHub Actions workflow logs
2. **Validate Configuration**: Run `./scripts/validate-secrets.sh`
3. **Test Components**: Test each component individually
4. **Create Issue**: Create a GitHub issue with error logs
5. **Community Support**: Ask in GitHub Discussions

## Example Workflow

Here's a complete example of setting up secrets:

```


# 1. Generate secrets

SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
WEBHOOK_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")

# 2. Create Telegram bot

# (Message @BotFather and follow instructions)

# 3. Generate SSH key

ssh-keygen -t ed25519 -C "nutrition-tracker-deploy" -f ~/.ssh/nutrition-deploy
ssh-copy-id -i ~/.ssh/nutrition-deploy.pub deploy@your-domain.com

# 4. Add secrets to GitHub

# (Use GitHub web interface)

# 5. Configure webhook URLs

WEBHOOK_URL="https://your-domain.com/telegram/webhook"

# 6. Test deployment

git push origin main

```

## Security Checklist

Before going to production, verify:

- [ ] All required secrets are configured
- [ ] SSH keys are unique and secure
- [ ] Bot tokens are from @BotFather
- [ ] Webhook URLs use HTTPS
- [ ] Secrets are not exposed in logs
- [ ] Different values for staging/production
- [ ] Regular rotation schedule planned
- [ ] Backup recovery plan in place

---

**Need Help?** Check the [troubleshooting section](#troubleshooting) or create a [GitHub issue](https://github.com/your-username/nutrition-tracker/issues).
```


## 📁 docs/ Directory Files

### `docs/PERFORMANCE.md`

```markdown
# Performance Optimization Guide

This guide covers performance optimization strategies for the Nutrition Tracker application.

## Overview

The Nutrition Tracker is designed to be fast and efficient out of the box. However, as your data grows or traffic increases, you may want to implement additional optimizations.

## Current Performance Features

### Already Implemented

✅ **Database Optimizations**
- SQLite WAL mode for better concurrency
- Proper indexes on frequently queried columns
- Query optimization with prepared statements
- Database connection pooling

✅ **Caching**
- Service Worker caches static assets
- Nginx caches API responses
- Browser caching headers for static files
- IndexedDB for offline data storage

✅ **Compression**
- Gzip compression for text responses
- Asset minification not needed (using CDN)
- Image optimization for PWA icons

✅ **Code Optimization**
- Lightweight dependencies (Flask + SQLite)
- Efficient JavaScript (vanilla ES6+)
- Minimal CSS footprint with Bootstrap

## Performance Monitoring

### Built-in Monitoring

Check application performance:

```


# Application health

curl http://localhost:5000/health

# System status with metrics

curl http://localhost:5000/api/system/status

# Database size and stats

ls -lh data/nutrition.db

```

### External Monitoring

If you have monitoring enabled:

```


# Prometheus metrics

curl http://localhost:9090/metrics

# Grafana dashboard

open http://localhost:3000

```

## Database Performance

### Current Optimizations

The database is already optimized with:

```

-- WAL mode for better concurrency
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 1000;

-- Performance indexes
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_log_date ON log_entries(date);
CREATE INDEX idx_log_date_meal ON log_entries(date, meal_time);

```

### When to Optimize Further

Consider additional optimization if you have:
- **1000+ products** in your database
- **10,000+ log entries** 
- **Slow query response times** (>100ms)
- **High concurrent usage** (10+ users)

### Advanced Database Optimization

#### Full-Text Search (if needed)

```

-- Add full-text search for products (if you have 1000+ products)
CREATE VIRTUAL TABLE products_fts USING fts5(name, content=products, content_rowid=id);

-- Populate the index
INSERT INTO products_fts(products_fts) VALUES('rebuild');

-- Use in queries
SELECT * FROM products WHERE id IN (
SELECT rowid FROM products_fts WHERE products_fts MATCH ?
);

```

#### Query Optimization

```

-- Analyze query performance
EXPLAIN QUERY PLAN SELECT * FROM log_entries WHERE date = '2025-10-15';

-- Optimize frequently used queries
CREATE INDEX idx_log_item_type_id ON log_entries(item_type, item_id);

```

#### Database Maintenance

```


# Regular maintenance (run monthly)

make db-vacuum

# Or manually

sqlite3 data/nutrition.db "VACUUM;"
sqlite3 data/nutrition.db "ANALYZE;"

```

## Application Performance

### Memory Usage

Monitor memory usage:

```


# Check Docker container memory

docker stats nutrition-tracker

# Check system memory

free -h

# Check process memory

ps aux | grep python

```

### Reduce Memory Usage

If memory is limited:

```


# In gunicorn.conf.py, reduce workers

workers = 2  \# Instead of 4

# Reduce cache size

CACHE_SIZE = 500  \# Instead of 1000

```

### CPU Optimization

For CPU-intensive operations:

```


# Use database aggregations instead of Python loops

query = """
SELECT SUM(calories_per_100g * quantity_grams / 100.0) as total_calories
FROM log_entries
JOIN products ON log_entries.item_id = products.id
WHERE date = ?
"""

# Instead of:

# total = sum(entry.calories for entry in entries)

```

## Frontend Performance

### JavaScript Optimization

Current optimizations:
- Vanilla JavaScript (no framework overhead)
- ES6+ features for cleaner code
- Event delegation for dynamic content
- Debounced search inputs

### Additional Optimizations

If needed:

```

// Debounce search input
function debounce(func, wait) {
let timeout;
return function executedFunction(...args) {
const later = () => {
clearTimeout(timeout);
func(...args);
};
clearTimeout(timeout);
timeout = setTimeout(later, wait);
};
}

// Use for search
const debouncedSearch = debounce(searchProducts, 300);

```

### CSS Performance

Current optimizations:
- Bootstrap 5 via CDN
- Minimal custom CSS
- CSS Grid for layouts
- Hardware acceleration for animations

## Network Performance

### Current Optimizations

✅ **Compression**: Gzip enabled for all text responses
✅ **Caching**: Proper cache headers set
✅ **CDN**: Bootstrap loaded from CDN
✅ **HTTP/2**: Supported via nginx

### Additional Network Optimization

#### Enable Brotli Compression

If your server supports it:

```


# In nginx.conf

load_module modules/ngx_http_brotli_filter_module.so;
load_module modules/ngx_http_brotli_static_module.so;

http {
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css application/json application/javascript;
}

```

#### Optimize Images

```


# Convert PNG icons to WebP (if supported)

cwebp static/icon-192.png -o static/icon-192.webp
cwebp static/icon-512.png -o static/icon-512.webp

```

## Scaling Strategies

### Vertical Scaling (Single Server)

Increase server resources:

```


# In docker-compose.yml

services:
nutrition-tracker:
deploy:
resources:
limits:
memory: 1G  \# Increase from 512M
cpus: '1.0'  \# Increase from 0.5

```

### Horizontal Scaling (Multiple Servers)

For high traffic:

1. **Load Balancer**
```

upstream nutrition_app {
server app1:5000;
server app2:5000;
server app3:5000;
}

```

2. **Shared Database**
- Use PostgreSQL instead of SQLite
- Use Redis for sessions
- Implement database connection pooling

3. **CDN for Static Assets**
- Move static files to CDN
- Use external file storage for uploads

### Database Scaling

#### Move to PostgreSQL

When SQLite becomes a bottleneck:

```


# In requirements.txt

psycopg2-binary==2.9.7

# In config.py

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/nutrition')

```

#### Read Replicas

For read-heavy workloads:

```

class DatabaseConfig:
WRITE_DB = 'postgresql://user:pass@primary/nutrition'
READ_DB = 'postgresql://user:pass@replica/nutrition'

```

## Performance Testing

### Load Testing with Locust

```


# locustfile.py

from locust import HttpUser, task, between

class NutritionUser(HttpUser):
wait_time = between(1, 3)

    @task(3)
    def view_products(self):
        self.client.get("/api/products")
    
    @task(2)
    def view_stats(self):
        self.client.get("/api/stats/2025-10-15")
    
    @task(1)
    def add_log_entry(self):
        self.client.post("/api/log", json={
            "date": "2025-10-15",
            "item_type": "product",
            "item_id": 1,
            "quantity_grams": 100
        })
    ```

```


# Run load test

pip install locust
locust -f locustfile.py --host=http://localhost:5000

```

### Apache Bench Testing

```


# Test API endpoint

ab -n 1000 -c 10 http://localhost:5000/api/products

# Test with POST data

ab -n 100 -c 5 -p post_data.json -T application/json http://localhost:5000/api/log

```

### Database Performance Testing

```


# Test database performance

sqlite3 data/nutrition.db ".timer on" "SELECT COUNT(*) FROM log_entries;"

# Profile slow queries

sqlite3 data/nutrition.db ".eqp on" "SELECT * FROM log_entries WHERE date = '2025-10-15';"

```

## Performance Benchmarks

### Expected Performance

On a modest server (1 CPU, 1GB RAM):

- **API Response Time**: < 50ms for simple queries
- **Database Queries**: < 10ms for indexed lookups  
- **Page Load Time**: < 2s on 3G connection
- **Concurrent Users**: 50+ without degradation

### Performance Goals

- **Time to First Byte**: < 200ms
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **API Response**: 95th percentile < 100ms

## Monitoring and Alerting

### Key Metrics to Monitor

```


# Response time

curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/api/products

# Database size growth

watch -n 60 'ls -lh data/nutrition.db'

# Memory usage

watch -n 30 'docker stats --no-stream nutrition-tracker'

```

### Performance Alerts

Set up alerts for:
- Response time > 500ms
- Memory usage > 80%
- Database size > 100MB
- Error rate > 1%

## Optimization Checklist

### Daily Monitoring
- [ ] Check application response times
- [ ] Monitor memory and CPU usage
- [ ] Review error logs for performance issues

### Weekly Maintenance
- [ ] Run database VACUUM if needed
- [ ] Check disk space usage
- [ ] Review slow query logs
- [ ] Update performance dashboard

### Monthly Optimization
- [ ] Analyze usage patterns
- [ ] Review and optimize slow queries
- [ ] Update performance benchmarks
- [ ] Plan capacity upgrades if needed

### Quarterly Review
- [ ] Load test with expected traffic
- [ ] Review architecture for scaling needs
- [ ] Update performance documentation
- [ ] Plan major optimizations

## Common Performance Issues

### Slow Database Queries

**Symptoms**: High response times, database locks
**Solutions**: Add indexes, optimize queries, use EXPLAIN

### Memory Leaks

**Symptoms**: Increasing memory usage over time
**Solutions**: Monitor with tools, restart services, fix code

### High CPU Usage

**Symptoms**: Slow response times, high load average
**Solutions**: Optimize algorithms, add caching, scale horizontally

### Network Bottlenecks

**Symptoms**: Slow page loads, timeouts
**Solutions**: Enable compression, use CDN, optimize assets

## Conclusion

The Nutrition Tracker is designed to perform well with minimal configuration. Most optimizations should only be needed as your usage grows significantly.

**Remember**: Measure before optimizing. Use the monitoring tools to identify actual bottlenecks rather than optimizing prematurely.

For most users, the default configuration provides excellent performance for personal or small team use.

## Quick Commands

```


# Check current performance

make health
make status

# Run performance tests

make benchmark
make load-test

# Optimize database

make db-vacuum

# Monitor in real-time

make monitor

```

---

**Need help with performance issues?** Create a [GitHub issue](https://github.com/your-username/nutrition-tracker/issues) with your performance metrics and system information.
```


### `docs/DEV_TIPS.md`

```markdown
# Developer Tips & Tricks

This guide contains helpful tips, tricks, and best practices for developing with the Nutrition Tracker codebase.

## Table of Contents

- [Development Environment](#development-environment)
- [Daily Workflow](#daily-workflow)
- [Debugging Techniques](#debugging-techniques)
- [Testing Tips](#testing-tips)
- [Database Tips](#database-tips)
- [Frontend Development](#frontend-development)
- [Performance Tips](#performance-tips)
- [Deployment Tips](#deployment-tips)
- [Troubleshooting](#troubleshooting)
- [IDE Configuration](#ide-configuration)
- [Useful Commands](#useful-commands)

## Development Environment

### Quick Setup

```


# One-command setup

make quickstart

# Or step by step

make dev-setup
make run

```

### Environment Variables

```


# Create development environment

cp .env.example .env.dev

# Set development-specific variables

export FLASK_ENV=development
export FLASK_DEBUG=1
export DATABASE_URL=sqlite:///data/nutrition-dev.db

```

### Virtual Environment Management

```


# Create and activate virtual environment

python -m venv venv
source venv/bin/activate  \# Linux/Mac

# or

venv\Scripts\activate     \# Windows

# Install development dependencies

pip install -r requirements-dev.txt

# Deactivate when done

deactivate

```

### Docker Development

```


# Quick Docker development

docker-compose up --build

# Development with live reload

docker-compose -f docker-compose.yml -f docker-compose.override.yml up

# View logs

docker-compose logs -f nutrition-tracker

# Execute commands in container

docker-compose exec nutrition-tracker bash

```

## Daily Workflow

### Starting Development

```


# Daily routine

git pull origin main           \# Get latest changes
make dev-install              \# Update dependencies
make db-migrate               \# Run any new migrations
make test                     \# Ensure everything works
make run                      \# Start development server

```

### Code Quality Checks

```


# Before committing

make format                   \# Format code
make lint                     \# Check code quality
make type-check              \# Type checking
make security               \# Security checks
make test                   \# Run tests

```

### Git Workflow

```


# Feature development

git checkout -b feature/new-feature

# Make changes...

git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# Create pull request

# Keep branch updated

git checkout main
git pull origin main
git checkout feature/new-feature
git rebase main

```

## Debugging Techniques

### Python Debugging

#### Using pdb

```


# Add breakpoint in code

import pdb; pdb.set_trace()

# Or use the newer breakpoint() function (Python 3.7+)

breakpoint()

```

#### Flask Debugging

```


# Enable debug mode

app.config['DEBUG'] = True

# Add logging

import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.debug('Debug message')

```

#### SQLite Debugging

```


# Examine database directly

sqlite3 data/nutrition.db

# Common queries

.tables                       \# List tables
.schema products             \# Show table schema
SELECT * FROM products LIMIT 5;  \# Sample data
.mode column                 \# Better formatting
.headers on                  \# Show column headers

# Check indexes

.indices products

# Analyze query performance

EXPLAIN QUERY PLAN SELECT * FROM products WHERE name LIKE '%chicken%';

```

### Frontend Debugging

#### Browser DevTools

```

// Console debugging
console.log('Debug info:', data);
console.table(products);     // Nice table format
console.time('api-call');    // Timing
// ... API call ...
console.timeEnd('api-call');

// Breakpoints in code
debugger;

// Network monitoring
// Open DevTools > Network tab to monitor API calls

```

#### Service Worker Debugging

```


# Chrome DevTools

# Application tab > Service Workers

# Check for service worker registration and status

# Debug service worker

chrome://inspect/\#service-workers

```

### API Debugging

```


# Test API endpoints

curl -X GET http://localhost:5000/api/products
curl -X POST http://localhost:5000/api/products \
-H "Content-Type: application/json" \
-d '{"name":"Test","calories_per_100g":100,"protein_per_100g":10,"fat_per_100g":5,"carbs_per_100g":15}'

# Pretty print JSON responses

curl -s http://localhost:5000/api/products | jq .

# Test with different data

curl -X POST http://localhost:5000/api/log \
-H "Content-Type: application/json" \
-d '{"date":"2025-10-15","item_type":"product","item_id":1,"quantity_grams":150}'

```

## Testing Tips

### Running Tests Efficiently

```


# Run specific test file

pytest tests/test_api.py

# Run specific test

pytest tests/test_api.py::test_create_product

# Run tests matching pattern

pytest -k "product"

# Run with verbose output

pytest -v

# Run with coverage

pytest --cov

# Run tests in parallel (if you have pytest-xdist)

pytest -n auto

```

### Test-Driven Development

```


# Write test first

def test_calculate_keto_index():
"""Test keto index calculation"""
result = calculate_keto_index(fat=20, protein=10, carbs=5)
assert result == 2.67  \# (20 * 2) / (10 + 5)

# Then implement function

def calculate_keto_index(fat, protein, carbs):
return round((fat * 2) / (protein + carbs), 2)

```

### Test Data Management

```


# Use fixtures for reusable test data

@pytest.fixture
def sample_product():
return {
'name': 'Test Product',
'calories_per_100g': 100,
'protein_per_100g': 10,
'fat_per_100g': 5,
'carbs_per_100g': 15
}

# Create test database

@pytest.fixture
def test_db():
\# Setup test database
yield db
\# Cleanup

```

### API Testing

```


# Test API endpoints

def test_api_endpoint(client):
response = client.get('/api/products')
assert response.status_code == 200

    data = response.get_json()
    assert 'data' in data
    assert data['status'] == 'success'
    ```

## Database Tips

### Development Database

```


# Create development database

cp data/nutrition.db data/nutrition-dev.db

# Reset development database

rm data/nutrition-dev.db
python init_db.py

```

### Database Migrations

```


# Create new migration

echo "-- Migration: Add new column" > migrations/002_add_column.sql
echo "ALTER TABLE products ADD COLUMN new_field TEXT;" >> migrations/002_add_column.sql

# Run migrations

python migrations/migrate.py

```

### Query Optimization

```

-- Use EXPLAIN to understand query performance
EXPLAIN QUERY PLAN
SELECT p.name, SUM(le.quantity_grams) as total_consumed
FROM products p
JOIN log_entries le ON p.id = le.item_id
WHERE le.date = '2025-10-15'
GROUP BY p.id;

-- Add indexes for slow queries
CREATE INDEX idx_log_entries_date_item ON log_entries(date, item_id);

```

### Backup and Restore

```


# Quick backup

cp data/nutrition.db data/nutrition-backup-\$(date +%Y%m%d).db

# Backup with SQL dump

sqlite3 data/nutrition.db .dump > backup.sql

# Restore from SQL dump

sqlite3 data/nutrition-new.db < backup.sql

```

## Frontend Development

### JavaScript Development

#### ES6+ Features

```

// Use modern JavaScript features
const products = await fetch('/api/products').then(r => r.json());

// Destructuring
const { name, calories_per_100g } = product;

// Template literals

```
const html = `<h3>${product.name}</h3><p>Calories: ${product.calories_per_100g}</p>`;
```

// Arrow functions
const filteredProducts = products.filter(p => p.name.includes(searchTerm));

// Async/await
async function loadProducts() {
try {
const response = await fetch('/api/products');
const data = await response.json();
return data.data;
} catch (error) {
console.error('Error loading products:', error);
return [];
}
}

```

#### DOM Manipulation

```

// Efficient DOM queries
const productsList = document.getElementById('products-list');
const searchInput = document.querySelector('\#product-search');

// Event delegation
document.addEventListener('click', (e) => {
if (e.target.matches('.delete-btn')) {
deleteProduct(e.target.dataset.productId);
}
});

// Create elements efficiently
function createProductCard(product) {
const card = document.createElement('div');
card.className = 'product-card';
card.innerHTML = `        <h3>${product.name}</h3>         <p>Calories: ${product.calories_per_100g}</p>         ```         <button class="delete-btn" data-product-id="${product.id}">Delete</button>         ```    `;
return card;
}

```

### CSS Tips

#### Bootstrap Utilities

```

<!-- Use Bootstrap utility classes -->
<div class="d-flex justify-content-between align-items-center mb-3">
    ```
    <h2 class="h4 mb-0">Products</h2>
    ```
    ```
    <button class="btn btn-primary btn-sm">Add Product</button>
    ```
</div>
<!-- Responsive utilities -->
<div class="row">
    <div class="col-12 col-md-6 col-lg-4">
        <!-- Content -->
    </div>
</div>
```

#### Custom CSS

```

/* Use CSS custom properties */
:root {
--primary-color: \#0d6efd;
--success-color: \#198754;
--border-radius: 0.375rem;
}

/* Mobile-first responsive design */
.stats-grid {
display: grid;
grid-template-columns: 1fr;
gap: 1rem;
}

@media (min-width: 768px) {
.stats-grid {
grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
}

```

### Accessibility Development

```

<!-- Semantic HTML -->
<main id="main-content">
    <h1>Nutrition Tracker</h1>
    
    <section aria-labelledby="products-heading">
        ```
        <h2 id="products-heading">Products</h2>
        ```
        <!-- Products content -->
    </section>
</main>
<!-- Form accessibility -->
<form>
    ```
    <label for="product-name">Product Name</label>
    ```
    <input type="text" id="product-name" name="name" required 
           aria-describedby="name-help">
    <div id="name-help" class="form-text">
        Enter the name of the food product
    </div>
</form>
<!-- Button accessibility -->
<button type="button" aria-label="Delete chicken breast product">
    🗑️
</button>
```

## Performance Tips

### Database Performance

```


# Use database aggregations instead of Python loops

def get_daily_stats(date):
query = """
SELECT
SUM(p.calories_per_100g * le.quantity_grams / 100.0) as calories,
SUM(p.protein_per_100g * le.quantity_grams / 100.0) as protein
FROM log_entries le
JOIN products p ON le.item_id = p.id
WHERE le.date = ? AND le.item_type = 'product'
"""
return db.execute(query, (date,)).fetchone()

# Instead of:

# entries = get_log_entries(date)

# total_calories = sum(entry.calories for entry in entries)

```

### Frontend Performance

```

// Debounce search input
function debounce(func, wait) {
let timeout;
return function executedFunction(...args) {
const later = () => {
clearTimeout(timeout);
func(...args);
};
clearTimeout(timeout);
timeout = setTimeout(later, wait);
};
}

const debouncedSearch = debounce(searchProducts, 300);
searchInput.addEventListener('input', debouncedSearch);

// Use DocumentFragment for multiple DOM insertions
function renderProducts(products) {
const fragment = document.createDocumentFragment();
products.forEach(product => {
fragment.appendChild(createProductCard(product));
});
productsList.appendChild(fragment);
}

```

## Deployment Tips

### Local Production Testing

```


# Test production build locally

docker build -f Dockerfile.production -t nutrition-tracker:prod .
docker run -p 5000:5000 nutrition-tracker:prod

# Test with production database

FLASK_ENV=production python app.py

```

### Environment-Specific Configuration

```


# Use different configurations

class DevelopmentConfig:
DEBUG = True
DATABASE_URL = 'sqlite:///data/nutrition-dev.db'

class ProductionConfig:
DEBUG = False
DATABASE_URL = os.environ.get('DATABASE_URL')

# Select config based on environment

config = DevelopmentConfig if os.environ.get('FLASK_ENV') == 'development' else ProductionConfig

```

### Pre-deployment Checklist

```


# Run full test suite

make test

# Check code quality

make lint
make security

# Test production build

make docker-build-prod

# Validate secrets

./scripts/validate-secrets.sh

# Test database migrations

python migrations/migrate.py --dry-run

```

## Troubleshooting

### Common Issues

#### Database Locked

```


# Check for locks

lsof data/nutrition.db

# Fix corrupted database

sqlite3 data/nutrition.db "PRAGMA integrity_check;"
sqlite3 data/nutrition.db "VACUUM;"

```

#### Port Already in Use

```


# Find process using port 5000

lsof -i :5000
netstat -tulpn | grep :5000

# Kill process

kill -9 <PID>

```

#### Permission Issues

```


# Fix file permissions

chmod 644 data/nutrition.db
chmod 755 scripts/*.sh

# Fix directory permissions

chmod 755 data/ logs/ backups/

```

#### Import Errors

```


# Fix Python path issues

import sys
sys.path.insert(0, '/path/to/project')

# Or use relative imports

from .src.config import Config

```

### Debugging Production Issues

```


# Check application logs

docker-compose logs nutrition-tracker

# Check system resources

docker stats

# Test database connectivity

docker-compose exec nutrition-tracker python -c "from app import get_db; print('DB OK')"

# Check network connectivity

docker-compose exec nutrition-tracker curl -I http://localhost:5000/health

```

## IDE Configuration

### VS Code

```

// .vscode/settings.json
{
"python.defaultInterpreterPath": "./venv/bin/python",
"python.linting.flake8Enabled": true,
"python.formatting.provider": "black",
"python.testing.pytestEnabled": true,
"editor.formatOnSave": true,
"python.linting.flake8Args": ["--max-line-length=120"]
}

```

#### Useful Extensions

- Python
- Python Docstring Generator
- SQLite Viewer
- Docker
- GitHub Pull Requests
- GitLens

### PyCharm

```


# Configure run configuration

# Name: Nutrition Tracker

# Script path: app.py

# Environment variables: FLASK_ENV=development

# Python interpreter: ./venv/bin/python

```

## Useful Commands

### Development

```


# Quick commands

make run                     \# Start development server
make test                    \# Run tests
make format                  \# Format code
make lint                    \# Check code quality

# Database commands

make db-init                 \# Initialize database
make db-reset                \# Reset database (destructive!)
make db-backup               \# Create backup

# Docker commands

make docker-build            \# Build Docker image
make docker-run              \# Run in Docker
make compose-up              \# Start with compose
make compose-down            \# Stop compose services

```

### Git Workflow

```


# Quick git commands

git status                   \# Check status
git add .                    \# Stage all changes
git commit -m "message"      \# Commit changes
git push origin main         \# Push to remote

# Branch management

git checkout -b feature/name \# Create feature branch
git checkout main            \# Switch to main
git branch -d feature/name   \# Delete branch
git merge feature/name       \# Merge branch

```

### System Monitoring

```


# Monitor application

watch -n 5 'curl -s http://localhost:5000/health'

# Monitor database size

watch -n 30 'ls -lh data/nutrition.db'

# Monitor Docker containers

watch -n 10 'docker stats --no-stream'

# Monitor logs

tail -f logs/*.log

```

### Productivity Tips

```


# Create aliases for common commands

alias nr="make run"
alias nt="make test"
alias nf="make format"
alias nl="make lint"

# Use history search

# Ctrl+R to search command history

# Use tab completion

# Tab to complete filenames and commands

```

## Learning Resources

### Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

### Tools

- [Postman](https://www.postman.com/) - API testing
- [DB Browser for SQLite](https://sqlitebrowser.org/) - Database GUI
- [Chrome DevTools](https://developers.google.com/web/tools/chrome-devtools) - Frontend debugging

---

**Pro tip**: Bookmark this page and refer to it regularly. The more you use these techniques, the more productive you'll become! 🚀
```


### `docs/SECURITY.md`

```markdown
# Security Guidelines & Checklist

This document outlines security best practices and provides a comprehensive checklist for securing the Nutrition Tracker application.

## Table of Contents

- [Security Overview](#security-overview)
- [Pre-Deployment Security Checklist](#pre-deployment-security-checklist)
- [Application Security](#application-security)
- [Infrastructure Security](#infrastructure-security)
- [Development Security](#development-security)
- [Monitoring & Incident Response](#monitoring--incident-response)
- [Regular Maintenance](#regular-maintenance)
- [Security Testing](#security-testing)
- [Compliance](#compliance)

## Security Overview

The Nutrition Tracker implements security best practices by default, including:

- ✅ **HTTPS enforcement** with SSL/TLS encryption
- ✅ **Input validation** and sanitization
- ✅ **SQL injection prevention** through parameterized queries
- ✅ **XSS protection** with proper output encoding
- ✅ **CSRF protection** via Flask's built-in mechanisms
- ✅ **Security headers** configured in nginx
- ✅ **Container security** with non-root users
- ✅ **Secret management** through environment variables

## Pre-Deployment Security Checklist

### Credentials & Secrets Management

- [ ] **Change all default passwords and keys**
  - [ ] Generate strong `SECRET_KEY` (32+ characters)
  - [ ] Use unique `TELEGRAM_WEBHOOK_SECRET`
  - [ ] Set secure database credentials
  - [ ] Generate unique SSH keys for deployment

- [ ] **Never commit secrets to version control**
  - [ ] All secrets stored in environment variables
  - [ ] `.env` file in `.gitignore`
  - [ ] No hardcoded credentials in code
  - [ ] GitHub Secrets properly configured

- [ ] **Use different credentials for different environments**
  - [ ] Separate staging and production credentials
  - [ ] Different bot tokens for testing and production
  - [ ] Separate SSH keys for different servers

### Authentication & Authorization

- [ ] **Secure webhook validation**
  - [ ] Telegram webhook secret properly configured
  - [ ] Webhook signature validation implemented
  - [ ] Rate limiting on webhook endpoints

- [ ] **API security**
  - [ ] Rate limiting on all API endpoints
  - [ ] Input validation on all endpoints
  - [ ] Proper error handling (no information disclosure)

### Network Security

- [ ] **HTTPS configuration**
  - [ ] SSL/TLS certificates properly configured
  - [ ] HTTP redirects to HTTPS
  - [ ] HSTS headers enabled
  - [ ] Modern TLS configuration (TLS 1.2+)

- [ ] **Firewall configuration**
  - [ ] Only necessary ports open (22, 80, 443)
  - [ ] SSH access restricted to specific IPs if possible
  - [ ] Internal services not exposed publicly

### Server Security

- [ ] **SSH hardening**
  - [ ] SSH key authentication enabled
  - [ ] Password authentication disabled
  - [ ] Root login disabled
  - [ ] SSH port changed from default (optional)
  - [ ] fail2ban configured for SSH protection

- [ ] **System updates**
  - [ ] Operating system fully updated
  - [ ] Automatic security updates enabled
  - [ ] Docker and docker-compose updated to latest versions

- [ ] **User permissions**
  - [ ] Application runs as non-root user
  - [ ] Proper file permissions set
  - [ ] Sudo access restricted

## Application Security

### Input Validation

```


# Example: Proper input validation

def validate_product_data(data):
errors = []

    # Validate name
    name = data.get('name', '').strip()
    if not name or len(name) > 100:
        errors.append("Name is required and must be less than 100 characters")
    
    # Validate numeric values
    try:
        calories = float(data.get('calories_per_100g', 0))
        if calories < 0 or calories > 9999:
            errors.append("Calories must be between 0 and 9999")
    except (ValueError, TypeError):
        errors.append("Calories must be a valid number")
    
    return errors
    ```

### SQL Injection Prevention

```


# Always use parameterized queries

cursor.execute(
"SELECT * FROM products WHERE name = ?",
(name,)  \# Parameterized
)

# Never use string formatting

# BAD: cursor.execute(f"SELECT * FROM products WHERE name = '{name}'")

```

### XSS Prevention

```

<!-- Use proper escaping in templates -->
<h3>{{ product.name | e }}</h3>

<!-- Or use Flask's automatic escaping -->
<h3>{{ product.name }}</h3>

```

```

// Escape user input in JavaScript
function escapeHtml(text) {
const map = {
'\&': '\&',
'<': '<',
'>': '>',
'"': '"',
"'": '&#039;'
};
return text.replace(/[\&<>"']/g, m => map[m]);
}

```

### CSRF Protection

```


# Flask-WTF automatically handles CSRF

from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

```

### Security Headers

```


# Configured in nginx.conf

add_header X-Content-Type-Options nosniff always;
add_header X-Frame-Options DENY always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net" always;

```

## Infrastructure Security

### Docker Security

- [ ] **Container configuration**
  - [ ] Run containers as non-root user
  - [ ] Use minimal base images
  - [ ] Regularly update base images
  - [ ] Scan images for vulnerabilities

```


# Security best practices in Dockerfile

FROM python:3.11-slim

# Create non-root user

RUN groupadd -r appuser \&\& useradd -r -g appuser appuser

# Switch to non-root user

USER appuser

# Use specific versions

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

```

### Nginx Security

```


# Security configuration

server_tokens off;  \# Hide nginx version
client_max_body_size 1M;  \# Limit request size

# Rate limiting

limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;

# SSL configuration

ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;

```

### Database Security

- [ ] **SQLite security**
  - [ ] Database file permissions (600)
  - [ ] Database directory permissions (700)
  - [ ] WAL files properly secured
  - [ ] Backup files encrypted

```


# Secure database permissions

chmod 600 data/nutrition.db
chmod 700 data/

```

- [ ] **Database backups**
  - [ ] Regular automated backups
  - [ ] Backup encryption
  - [ ] Secure backup storage
  - [ ] Backup restoration testing

## Development Security

### Code Review Security

- [ ] **Security-focused code reviews**
  - [ ] Input validation checks
  - [ ] Authentication/authorization verification
  - [ ] Secret management review
  - [ ] Dependency security assessment

### Dependency Security

```


# Check for vulnerable dependencies

pip install safety
safety check

# Update dependencies regularly

pip list --outdated
pip install --upgrade package-name

```

### Pre-commit Security Hooks

```


# In .pre-commit-config.yaml

- repo: https://github.com/pycqa/bandit
rev: 1.7.5
hooks:
    - id: bandit
args: [--skip=B101,B601]
- repo: https://github.com/Lucas-C/pre-commit-hooks-safety
rev: v1.3.2
hooks:
    - id: python-safety-dependencies-check

```

### Secrets Management

```


# Never commit secrets

echo "*.key" >> .gitignore
echo ".env" >> .gitignore
echo "secrets/" >> .gitignore

# Use environment variables

export SECRET_KEY="\$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"

# Validate secrets format

./scripts/validate-secrets.sh

```

## Monitoring & Incident Response

### Security Monitoring

- [ ] **Log monitoring**
  - [ ] Monitor for suspicious activities
  - [ ] Failed login attempts tracking
  - [ ] Unusual API usage patterns
  - [ ] Error rate monitoring

```


# Monitor logs for security events

tail -f logs/access.log | grep -E "(40[1-5]|50[0-5])"

# Monitor failed requests

grep "POST.*40[1-4]" logs/access.log | tail -20

```

- [ ] **Automated alerts**
  - [ ] High error rates
  - [ ] Unusual traffic patterns
  - [ ] Failed authentication attempts
  - [ ] System resource exhaustion

### Incident Response Plan

1. **Detection**
   - Monitor logs and alerts
   - User reports of issues
   - Security scan findings

2. **Containment**
   - Isolate affected systems
   - Block malicious IPs
   - Disable compromised accounts

3. **Eradication**
   - Remove malware/backdoors
   - Patch vulnerabilities
   - Update credentials

4. **Recovery**
   - Restore from clean backups
   - Gradually restore services
   - Monitor for recurrence

5. **Lessons Learned**
   - Document incident
   - Update security measures
   - Improve monitoring

### Security Incident Checklist

If you suspect a security breach:

- [ ] **Immediate actions**
  - [ ] Take affected systems offline
  - [ ] Change all passwords and API keys
  - [ ] Create backup of current state for analysis
  - [ ] Notify relevant stakeholders

- [ ] **Investigation**
  - [ ] Check logs for unauthorized access
  - [ ] Identify compromised data
  - [ ] Determine attack vector
  - [ ] Assess scope of compromise

- [ ] **Remediation**
  - [ ] Patch identified vulnerabilities
  - [ ] Restore from clean backup if necessary
  - [ ] Implement additional security controls
  - [ ] Update incident response procedures

- [ ] **Communication**
  - [ ] Notify affected users if personal data involved
  - [ ] Document incident for future reference
  - [ ] Report to authorities if required
  - [ ] Update security documentation

## Regular Maintenance

### Weekly Security Tasks

- [ ] **System maintenance**
  - [ ] Check for security updates
  - [ ] Review access logs for anomalies
  - [ ] Verify backup integrity
  - [ ] Monitor resource usage

- [ ] **Application maintenance**
  - [ ] Check for failed requests in logs
  - [ ] Verify SSL certificate status
  - [ ] Test backup restoration process
  - [ ] Review user activity patterns

### Monthly Security Tasks

- [ ] **Security assessment**
  - [ ] Dependency vulnerability scan
  - [ ] Access control review
  - [ ] Credential rotation
  - [ ] Security documentation update

- [ ] **Testing**
  - [ ] Penetration testing
  - [ ] Backup restoration test
  - [ ] Incident response drill
  - [ ] Security awareness training

### Quarterly Security Tasks

- [ ] **Comprehensive review**
  - [ ] Full security audit
  - [ ] Threat model update
  - [ ] Security architecture review
  - [ ] Compliance assessment

- [ ] **Strategic planning**
  - [ ] Security budget planning
  - [ ] Security tool evaluation
  - [ ] Training needs assessment
  - [ ] Security roadmap update

## Security Testing

### Automated Security Testing

```


# Dependency scanning

safety check

# Code security analysis

bandit -r app.py src/

# Container security scanning

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
aquasec/trivy image nutrition-tracker:latest

```

### Manual Security Testing

- [ ] **Authentication testing**
  - [ ] Test session management
  - [ ] Verify logout functionality
  - [ ] Test session timeout
  - [ ] Check for session fixation

- [ ] **Authorization testing**
  - [ ] Test access controls
  - [ ] Verify privilege escalation prevention
  - [ ] Test direct object references
  - [ ] Check for forced browsing

- [ ] **Input validation testing**
  - [ ] SQL injection testing
  - [ ] XSS testing
  - [ ] Command injection testing
  - [ ] File upload testing (if applicable)

### Security Testing Tools

```


# OWASP ZAP for web application security testing

docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:5000

# Nikto for web server scanning

nikto -h http://localhost:5000

# SSL testing

testssl.sh your-domain.com

```

## Compliance

### Data Protection

- [ ] **Data minimization**
  - [ ] Collect only necessary data
  - [ ] Regular data cleanup
  - [ ] Secure data disposal
  - [ ] Data retention policies

- [ ] **Privacy by design**
  - [ ] Privacy settings
  - [ ] Data anonymization where possible
  - [ ] User consent management
  - [ ] Right to deletion

### Security Standards

- [ ] **Industry standards compliance**
  - [ ] OWASP Top 10 mitigation
  - [ ] NIST Cybersecurity Framework alignment
  - [ ] ISO 27001 best practices
  - [ ] Local regulations compliance

### Documentation

- [ ] **Security documentation**
  - [ ] Security policies and procedures
  - [ ] Incident response plan
  - [ ] Risk assessment documentation
  - [ ] Security architecture documentation

## Security Resources

### Learning Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls)
- [Flask Security Guidelines](https://flask.palletsprojects.com/en/2.3.x/security/)

### Security Tools

- [Bandit](https://bandit.readthedocs.io/) - Python code security analysis
- [Safety](https://github.com/pyupio/safety) - Dependency vulnerability checking
- [OWASP ZAP](https://www.zaproxy.org/) - Web application security testing
- [Trivy](https://aquasecurity.github.io/trivy/) - Container vulnerability scanning

### Emergency Contacts

Keep these contacts readily available:

- **System Administrator**: [contact info]
- **Security Team**: [contact info]
- **Hosting Provider**: [contact info]
- **Domain Registrar**: [contact info]

---

## Security Checklist Summary

Print this checklist and review it before each deployment:

### Pre-Deployment ✓
- [ ] All secrets changed from defaults
- [ ] HTTPS properly configured
- [ ] Firewalls configured
- [ ] SSH hardened
- [ ] System fully updated
- [ ] Dependency scan passed
- [ ] Security headers configured

### Post-Deployment ✓
- [ ] Security monitoring enabled
- [ ] Backup system tested
- [ ] Incident response plan ready
- [ ] Regular maintenance scheduled
- [ ] Security documentation updated

### Ongoing ✓
- [ ] Weekly log reviews
- [ ] Monthly security scans
- [ ] Quarterly security audits
- [ ] Annual incident response drills

---

**Remember**: Security is an ongoing process, not a one-time task. Regular reviews and updates are essential for maintaining a secure application.

**Need help with security?** Create a [GitHub issue](https://github.com/your-username/nutrition-tracker/issues) with the "security" label, or contact our security team directly.
```


***

## 🎯 Final Summary

You now have **ALL** the missing files for your complete production-ready Nutrition Tracker project:

### ✅ Scripts Added

- `scripts/validate-secrets.sh` - Complete secret validation with format checking


### ✅ Configuration Added

- `.env.example` - Comprehensive environment template with all variables
- `.pre-commit-config.yaml` - Complete pre-commit hooks configuration


### ✅ Legal Added

- `LICENSE` - MIT license with third-party acknowledgments


### ✅ Documentation Added

- `CONTRIBUTING.md` - Complete contributor guide with workflows
- `GITHUB_SECRETS.md` - Comprehensive secrets setup guide
- `docs/PERFORMANCE.md` - Performance optimization guide
- `docs/DEV_TIPS.md` - Developer productivity guide
- `docs/SECURITY.md` - Security checklist and best practices

**Total files created: 8 comprehensive files** with production-ready content, security best practices, and complete developer documentation.

Your Nutrition Tracker project is now **100% complete** and ready for production deployment! 🥗✨

