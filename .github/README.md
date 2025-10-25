# GitHub Copilot Configuration for Nutricount

Welcome to the GitHub Copilot configuration directory! This directory contains comprehensive instructions and guidelines for optimal GitHub Copilot coding agent performance in the Nutricount project.

---

## 📚 Documentation Overview

### Main Configuration Files

#### 1. **[copilot-instructions.md](copilot-instructions.md)** ⭐ START HERE
**1,356 lines | Primary configuration file**

This is the main instructions file that GitHub Copilot reads automatically. It contains:
- Complete project overview and architecture
- Technology stack details (Python 3.11, Flask 2.3.3, SQLite, Redis)
- Repository structure and component descriptions
- Build, test, and deploy commands
- Code standards and conventions
- Testing requirements (unit, integration, E2E)
- Security and performance best practices
- Common patterns and troubleshooting

**When to use**: GitHub Copilot reads this automatically, but you should review it before starting work on the project.

#### 2. **[COPILOT_AGENT_GUIDE.md](COPILOT_AGENT_GUIDE.md)** 📖 COMPLETE GUIDE
**888 lines | Comprehensive workflow guide**

Complete guide for using GitHub Copilot coding agent effectively:
- **Part 1**: Issue Management Best Practices
  - Writing issues for Copilot
  - Bug reports and feature requests
  - 7 essential components with examples
  
- **Part 2**: PDCA Workflow (Plan-Do-Check-Act)
  - **PLAN**: Analysis, pattern research, task decomposition
  - **DO**: TDD, incremental development, version control
  - **CHECK**: Testing, code quality, security validation
  - **ACT**: Retrospective, learning documentation
  
- **Part 3**: Quality Metrics and Monitoring
  - Commit quality metrics
  - Code quality metrics (93% coverage)
  - Build and CI metrics
  - Performance targets
  
- **Part 4**: Code Review Guidelines
  - For authors (pre-review checklist)
  - For reviewers (comprehensive checklist)

**When to use**: Read this when planning new features, fixing bugs, or reviewing code.

#### 3. **[CONFIGURATION_SUMMARY.md](CONFIGURATION_SUMMARY.md)** 📊 ANALYSIS & SUMMARY
**570 lines | Complete configuration analysis**

Comprehensive summary of the entire configuration:
- All files created/modified
- Project analysis (tech stack, structure, patterns)
- Dependencies analysis (17 minimal, 103 full)
- CI/CD pipeline details
- Recommendations for improvements
- Main patterns and conventions
- Success metrics

**When to use**: Understanding what was configured and why.

---

## 🎯 Path-Specific Instructions

These files provide specialized guidance for specific code paths:

### [instructions/unit-tests.instructions.md](instructions/unit-tests.instructions.md)
**Applies to**: `**/test_*.py` in `/tests/unit/`

Covers:
- AAA pattern (Arrange-Act-Assert)
- Test naming conventions
- Mocking external dependencies
- Coverage requirements (>80%)

### [instructions/integration-tests.instructions.md](instructions/integration-tests.instructions.md)
**Applies to**: `**/integration/**/*.py`, `**/e2e/**/*.py`

Covers:
- Real test database usage
- Setup/teardown patterns
- E2E testing with stable locators
- Async handling

### [instructions/api-routes.instructions.md](instructions/api-routes.instructions.md)
**Applies to**: `**/routes/**/*.py`, `**/api/**/*.py`

Covers:
- Input validation requirements
- HTTP status code usage
- Error handling patterns
- Security requirements

---

## 🚀 Setup and Workflow

### [copilot-setup-steps.yml](copilot-setup-steps.yml)
**Development environment setup in 14 steps**

Complete setup guide with:
- Step-by-step instructions
- Verification commands
- Troubleshooting section
- Quick start guide (<5 minutes)

**Use this for**: Setting up development environment

---

## 📋 Templates

### Issue Templates

Located in `ISSUE_TEMPLATE/`:

- **[task.md](ISSUE_TEMPLATE/task.md)** - Task template for GitHub Copilot coding agent
  - Structured format with:
    - Objective and context
    - Detailed requirements
    - Acceptance criteria
    - Files to modify
    - Implementation guidance
    - Testing requirements
  
- **bug_report.yml** - Bug reporting (existing)
- **feature_request.yml** - Feature requests (existing)
- **documentation.yml** - Documentation issues (existing)
- **question.yml** - Questions (existing)
- **test_issue.yml** - Test-related issues (existing)

### Pull Request Template

- **[pull_request_template.md](pull_request_template.md)** - Enhanced PR template
  - Type of change
  - Implementation details
  - Testing performed
  - Comprehensive checklists

---

## 🗺️ Quick Navigation

### I want to...

**Start working on the project**
1. Read [copilot-instructions.md](copilot-instructions.md) (main instructions)
2. Follow [copilot-setup-steps.yml](copilot-setup-steps.yml) (setup)
3. Review [COPILOT_AGENT_GUIDE.md](COPILOT_AGENT_GUIDE.md) (workflow)

**Write unit tests**
→ See [instructions/unit-tests.instructions.md](instructions/unit-tests.instructions.md)

**Write integration/E2E tests**
→ See [instructions/integration-tests.instructions.md](instructions/integration-tests.instructions.md)

**Create new API endpoints**
→ See [instructions/api-routes.instructions.md](instructions/api-routes.instructions.md)

**Create a new issue**
→ Use [ISSUE_TEMPLATE/task.md](ISSUE_TEMPLATE/task.md) template

**Submit a pull request**
→ Use [pull_request_template.md](pull_request_template.md) template

**Understand the configuration**
→ Read [CONFIGURATION_SUMMARY.md](CONFIGURATION_SUMMARY.md)

**Learn the PDCA workflow**
→ See Part 2 of [COPILOT_AGENT_GUIDE.md](COPILOT_AGENT_GUIDE.md)

**Check quality metrics**
→ See Part 3 of [COPILOT_AGENT_GUIDE.md](COPILOT_AGENT_GUIDE.md)

---

## 📊 Key Statistics

**Documentation**: 4,000+ lines across 10 files
- Main instructions: 1,356 lines
- Comprehensive guide: 888 lines
- Configuration summary: 570 lines
- Path-specific instructions: 3 files
- Setup steps: 14 steps
- Templates: 1 new + 5 existing

**Project Stats**:
- **Tests**: 567 tests with 93% coverage
- **API Endpoints**: 47 endpoints documented
- **Dependencies**: 17 minimal (CI/CD), 103 full (production)
- **Tech Stack**: Python 3.11, Flask 2.3.3, SQLite, Redis
- **Target**: Raspberry Pi 4 Model B 2018 (ARM64)

---

## 🎯 Project Patterns

### Architecture
- **Style**: Monolithic with modular components (Blueprint-based)
- **Entry Point**: `app.py` (main Flask application)
- **Business Logic**: `src/` modules (9 files)
- **API Routes**: `routes/` blueprints (9 files)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3

### Key Patterns
- **Authentication**: JWT with `@require_auth` decorator
- **Caching**: Redis with fallback to in-memory
- **Background Tasks**: Celery with fallback to synchronous
- **Database**: SQLite with WAL mode
- **Testing**: pytest with AAA pattern
- **Error Handling**: `json_response()` helper
- **Logging**: Structured logging with loguru

### Naming Conventions
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Test files**: `test_*.py`

### Code Style
- **Line length**: 100 characters max
- **Indentation**: 4 spaces
- **Quotes**: Double quotes
- **Linting**: flake8 with specific ignores (E501, W503, E226)
- **Formatting**: black
- **Import sorting**: isort

---

## 🔍 Additional Resources

### In This Repository
- **README.md** (root) - User documentation
- **PROJECT_SETUP.md** - Detailed setup guide
- **ARCHITECTURE.md** - Architecture documentation
- **CODE_QUALITY.md** - Code quality standards
- **CONTRIBUTING.md** - Contributing guidelines

### External Links
- [GitHub Copilot Documentation](https://docs.github.com/copilot)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)

---

## ✅ Status

**Configuration Status**: ✅ Complete and Ready for Use

All files are in place and ready for GitHub Copilot coding agent to use. The configuration follows industry best practices and is tailored specifically to the Nutricount project.

**Last Updated**: October 25, 2024
**Version**: 1.0

---

## 🤝 Contributing

When adding new patterns or updating instructions:
1. Update the relevant file in this directory
2. Keep examples real and project-specific
3. Test that instructions are clear and actionable
4. Update this README if adding new files

---

## 📞 Questions or Issues?

- Review the comprehensive guide: [COPILOT_AGENT_GUIDE.md](COPILOT_AGENT_GUIDE.md)
- Check the main instructions: [copilot-instructions.md](copilot-instructions.md)
- See the configuration summary: [CONFIGURATION_SUMMARY.md](CONFIGURATION_SUMMARY.md)
- Create an issue using the appropriate template

---

**Happy Coding with GitHub Copilot! 🚀**
