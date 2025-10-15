# 🤖 CLAUDE.md — AI Agent Developer Doc

## Integration Guidelines for AI/Automation Agents (Claude, Copilot etc.)


***

### Overview

Claude/AI agents can autonomously interact with project source, run workflows, perform code reviews, write issues/docs, or suggest upgrades.

***

#### Principles

- **Non-Intrusive**: All actions must be verifiable and explainable by human reviewers.
- **Respect .env/.gitignore/.dockerignore**: Never suggest committing secrets or locally-ignored files.
- **Accessibility First**: All UI/UX changes should preserve or enhance WCAG 2.2 compliance and keyboard accessibility.
- **Idempotence**: CLI scripts and Makefile targets MUST be idempotent.
- **Minimal Dependencies**: Suggest additions only if they are lightweight and as peer-reviewed, production-grade packages.

***

### How To Use

- **Testing:** Use `pytest` for test generation. New modules must be covered by unit/integration tests in `tests/`.
- **Linting/Formatting:** Enforce auto-format before commit. Use `black`, `flake8`, `isort` (see Makefile).
- **Deployment:** Run or modify only `docker-compose` or GitHub Actions workflows for deployment pipelines. Respect the difference between staging and production.
- **Secrets:** All sensitive settings must be read from `.env` or GitHub Secrets only.
- **Accessibility:** If generating HTML or JS, ensure labels, ARIA, tab-index, visible focus indicators, and semantic roles.
- **Documentation:** Auto-generate or update `README.md` and `QUICKSTART.md` as new features are added. Include inline code comments!
- **Migrations:** For DB changes, add or edit helper scripts in a new `migrations/` folder, and document usage.

***

#### Example: To Add a Feature

1. Generate a clean module in `src/` with docstrings and type hints.
2. Create unit/integration tests in `tests/`.
3. Add a Makefile target if relevant.
4. Document the feature in `README.md` (summary + code sample).
5. Summarize semantic and accessibility impact if UI-related.

***

#### Example: To Submit a PR

- Bundle only necessary files; keep PRs minimal and focused.
- Add a summary of your reasoning, expected impact, and testing instructions.
- Reference relevant discussion/issues.

***

### AI-Specific Commit Tag

- Use `commit:ai` in commit messages added by Claude or other agents.

***

### Final Note

> All AI actions should be **safe**, **auditable**, **well-documented**, and **WCAG/Production-compliant**.

Humans/maintainers should always preview, test, and approve significant changes.

***

**When in doubt: STOP and ask for human confirmation.**

---