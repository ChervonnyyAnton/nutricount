# 🤝 Contributing to Nutricount

First off, thank you for considering contributing to Nutricount! It's people like you that make Nutricount such a great tool for health-conscious individuals and developers learning best practices.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Expected Behavior

- ✅ Be respectful and inclusive
- ✅ Welcome newcomers and help them learn
- ✅ Focus on what is best for the community
- ✅ Show empathy towards other community members
- ✅ Give and receive constructive feedback gracefully

### Unacceptable Behavior

- ❌ Harassment, discrimination, or personal attacks
- ❌ Trolling, insulting/derogatory comments
- ❌ Publishing others' private information
- ❌ Other conduct which could reasonably be considered inappropriate

**Enforcement**: Violations may result in temporary or permanent ban from the project.

---

## 🎯 How Can I Contribute?

### Reporting Bugs 🐛

Found a bug? Help us fix it!

**Before Submitting**:
1. Check [existing issues](https://github.com/ChervonnyyAnton/nutricount/issues)
2. Try latest version to see if bug still exists
3. Collect relevant information (OS, browser, version)

**Bug Report Template**:
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment**:
- OS: [e.g., Ubuntu 22.04, Windows 11]
- Browser: [e.g., Chrome 120, Firefox 121]
- Version: [e.g., 2.0.0]

**Additional context**
Any other relevant information.
```

### Suggesting Features 💡

Have an idea? We'd love to hear it!

**Feature Request Template**:
```markdown
**Problem Statement**
What problem does this solve?

**Proposed Solution**
How would this feature work?

**Alternatives Considered**
What other solutions did you consider?

**Additional Context**
Mockups, examples, or related features.
```

### Improving Documentation 📚

Documentation improvements are always welcome:
- Fix typos or clarify explanations
- Add examples or use cases
- Translate documentation
- Write tutorials or guides

**Simple Process**:
1. Fork repository
2. Edit documentation files
3. Submit Pull Request
4. No tests required for docs-only changes

### Contributing Code 💻

Ready to write code? Awesome!

**Good First Issues**:
- Look for `good first issue` label
- Small, self-contained tasks
- Great for learning the codebase

**Areas for Contribution**:
- 🐛 Bug fixes
- ✨ New features
- 🎨 UI/UX improvements
- ⚡ Performance optimizations
- 🧪 Test coverage improvements
- 📝 Code documentation

---

## 🛠️ Development Setup

### Prerequisites

**Required**:
- Python 3.11+
- Node.js 18+ and npm
- Git

**Optional** (for full stack):
- Docker & docker-compose
- Redis (for caching)
- Raspberry Pi (for testing Pi deployment)

### Quick Setup

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/nutricount.git
cd nutricount

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-minimal.txt

# 3. Set up frontend
cd frontend
npm install
cd ..

# 4. Set up environment
cp .env.example .env
nano .env  # Configure as needed

# 5. Initialize database
python init_db.py

# 6. Run tests
export PYTHONPATH=$PWD
pytest tests/ -v
npm --prefix frontend test

# 7. Start development server
python app.py
# Backend runs on http://localhost:5000
```

### Project Structure

```
nutricount/
├── app.py                    # Main Flask application
├── src/                      # Core backend modules
│   ├── config.py            # Configuration
│   ├── security.py          # Authentication
│   └── utils.py             # Utilities
├── routes/                   # API endpoints (Blueprints)
├── repositories/             # Data access layer
├── services/                 # Business logic layer
├── frontend/                 # Frontend code
│   ├── src/                 # Source files
│   │   ├── adapters/        # Backend adapters
│   │   └── business-logic/  # Business logic
│   └── tests/               # Frontend tests
├── tests/                    # Backend tests
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
└── docs/                     # Documentation
```

---

## 📏 Coding Standards

### Python Style

**Follow PEP 8** with exceptions defined in `.flake8`:
- Max line length: 100 characters
- Ignore: E501, W503, E226

**Example**:
```python
def calculate_nutrition(
    protein: float,
    fats: float,
    carbs: float
) -> dict:
    """
    Calculate total calories and macros distribution.
    
    Args:
        protein: Protein in grams
        fats: Fats in grams  
        carbs: Carbohydrates in grams
    
    Returns:
        Dictionary with calories and percentages
    """
    calories = protein * 4 + fats * 9 + carbs * 4
    return {
        'calories': calories,
        'protein_pct': (protein * 4 / calories * 100) if calories > 0 else 0,
        'fats_pct': (fats * 9 / calories * 100) if calories > 0 else 0,
        'carbs_pct': (carbs * 4 / calories * 100) if calories > 0 else 0
    }
```

**Run Linter**:
```bash
flake8 src/ routes/ repositories/ services/ --max-line-length=100 --ignore=E501,W503,E226
```

### JavaScript Style

**Modern ES6+ with consistent formatting**:

**Example**:
```javascript
/**
 * Calculate nutrition totals from log entries
 * @param {Array} entries - Array of log entries
 * @param {Object} products - Products lookup
 * @returns {Object} Nutrition totals
 */
function calculateTotals(entries, products) {
    return entries.reduce((totals, entry) => {
        const product = products[entry.product_id];
        const factor = entry.quantity / 100;
        
        return {
            calories: totals.calories + (product.calories * factor),
            protein: totals.protein + (product.protein * factor),
            fats: totals.fats + (product.fats * factor),
            carbs: totals.carbs + (product.carbs * factor)
        };
    }, { calories: 0, protein: 0, fats: 0, carbs: 0 });
}
```

**Run Linter** (if configured):
```bash
cd frontend
npm run lint
```

### General Principles

✅ **SOLID Principles**: Follow all 5 principles
✅ **DRY**: Don't Repeat Yourself
✅ **KISS**: Keep It Simple, Stupid  
✅ **YAGNI**: You Aren't Gonna Need It
✅ **Type Hints**: Use type hints in Python
✅ **Docstrings**: Document public functions
✅ **Comments**: Explain "why", not "what"

---

## 📝 Commit Guidelines

### Commit Message Format

```
<type>: <short summary>

<optional body>

<optional footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Build process, dependencies, etc.

### Examples

**Good Commits**:
```
feat: Add intermittent fasting timer

Implement real-time countdown timer for fasting sessions.
Includes pause/resume functionality and session history.

Closes #123
```

```
fix: Correct keto index calculation for high-protein foods

Previous formula underestimated keto-friendliness of high-protein,
low-carb foods. Adjusted protein multiplier from 0.3 to 0.5.

Fixes #456
```

```
docs: Update quick start guide with mobile PWA instructions

Added section on installing Nutricount as Progressive Web App
on iOS and Android devices.
```

**Bad Commits** (avoid these):
```
Update stuff
Fixed things
WIP
asdfasdf
```

### Commit Best Practices

- ✅ Atomic commits (one logical change per commit)
- ✅ Present tense ("Add feature" not "Added feature")
- ✅ Imperative mood ("Fix bug" not "Fixes bug")
- ✅ Reference issues (#123) or PRs
- ✅ Keep subject line under 72 characters
- ❌ Don't commit commented-out code
- ❌ Don't commit secrets or credentials
- ❌ Don't commit generated files (node_modules, __pycache__)

---

## 🔄 Pull Request Process

### Before Submitting

1. **Create Branch**:
   ```bash
   git checkout -b feat/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make Changes**: Follow coding standards

3. **Add Tests**: Write tests for new code

4. **Run Tests**:
   ```bash
   # Backend tests
   pytest tests/ -v
   
   # Frontend tests
   npm --prefix frontend test
   
   # Linting
   flake8 src/ routes/ --max-line-length=100 --ignore=E501,W503,E226
   ```

5. **Update Documentation**: If needed

6. **Commit Changes**: Follow commit guidelines

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review performed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
- [ ] Dependent changes merged

## Screenshots (if applicable)
Add screenshots for UI changes.

## Related Issues
Closes #123
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs automatically
   - Linting
   - Tests
   - Security scan
   - Build verification

2. **Code Review**: Maintainers review your code
   - Usually within 2-3 business days
   - May request changes
   - Constructive feedback provided

3. **Iterate**: Address feedback
   - Push new commits to same branch
   - No need to create new PR

4. **Merge**: Once approved
   - Maintainer merges PR
   - Your changes go live!

---

## 🧪 Testing Requirements

### Test Coverage Goals

- **Backend**: 90%+ overall, 85%+ per module
- **Frontend**: 80%+ overall
- **Critical Modules**: 95%+ (security, utils, repositories)

### Writing Tests

**Backend (pytest)**:
```python
def test_calculate_keto_index():
    """Test keto index calculation for high-fat food."""
    # Arrange
    nutrition = {
        'protein': 10,
        'fats': 40,
        'carbs': 5
    }
    
    # Act
    result = calculate_keto_index(nutrition)
    
    # Assert
    assert result >= 70, "Should be keto-friendly"
    assert result <= 100, "Should not exceed maximum"
```

**Frontend (Jest)**:
```javascript
test('calculates daily totals correctly', () => {
    // Arrange
    const entries = [
        { product_id: 1, quantity: 100, calories: 200 },
        { product_id: 2, quantity: 150, calories: 300 }
    ];
    
    // Act
    const totals = calculateDailyTotals(entries);
    
    // Assert
    expect(totals.calories).toBe(500);
});
```

### Running Tests

```bash
# All backend tests
pytest tests/ -v

# Specific test file
pytest tests/unit/test_utils.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# All frontend tests
npm --prefix frontend test

# Watch mode (for development)
npm --prefix frontend test -- --watch
```

---

## 📖 Documentation

### What to Document

- **New Features**: How to use them
- **API Changes**: Breaking changes, new endpoints
- **Setup Changes**: New dependencies, configuration
- **Complex Logic**: Why decisions were made
- **Design Patterns**: Patterns used and why

### Documentation Locations

- **User Docs**: `docs/users/`
- **Developer Docs**: `docs/`
- **API Docs**: Inline docstrings
- **Architecture**: `ARCHITECTURE.md`
- **Patterns**: `DESIGN_PATTERNS_GUIDE.md`

### Documentation Style

**Clear, Concise, Helpful**:

```markdown
## Feature Name

### Overview
Brief description of what this feature does and why it's useful.

### Usage
```python
# Example code
result = do_something(param)
```

### Parameters
- `param` (str): Description of parameter

### Returns
- `result` (dict): Description of return value

### Examples
```python
# Common use case
result = do_something("example")
print(result)  # {'key': 'value'}
```

### Notes
- Important considerations
- Edge cases
- Limitations
```

---

## 🏆 Recognition

### Contributors

All contributors are recognized in:
- `CONTRIBUTORS.md` file
- GitHub contributors page
- Release notes (for significant contributions)

### Top Contributors

Exceptional contributors may be invited to:
- Join core team
- Participate in roadmap planning
- Review pull requests

---

## ❓ Questions?

**Need Help?**
- 💬 [GitHub Discussions](https://github.com/ChervonnyyAnton/nutricount/discussions)
- 📧 Email: [TBD]
- 📚 [Documentation](docs/)

**Found an Issue with This Guide?**
- Open an issue or PR to improve it!

---

## 🙏 Thank You!

Your contributions make Nutricount better for everyone. Whether it's a bug report, documentation fix, or major feature, every contribution matters.

**Happy coding!** 🚀

---

**Last Updated**: October 22, 2025  
**Version**: 1.0  
**Maintainers**: [@ChervonnyyAnton](https://github.com/ChervonnyyAnton)
