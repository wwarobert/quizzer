# GitHub Actions CI/CD

This directory contains GitHub Actions workflows for continuous integration and deployment.

## Workflows

### 🔄 `ci.yml` - Main CI Pipeline

**Triggers:** Pull requests and pushes to `main`/`develop`

**Jobs:**

1. **Test** - Run test suite across Python versions
   - Matrix: Python 3.10, 3.11, 3.12, 3.13
   - Runs all 57 tests with pytest
   - Generates coverage reports
   - Uploads to Codecov
   - Publishes test results as PR checks

2. **Code Quality** - Static analysis
   - **Black**: Code formatting check
   - **isort**: Import sorting validation
   - **Flake8**: Linting and style guide enforcement
   - **Pylint**: Advanced code analysis
   - **MyPy**: Type checking
   - **Bandit**: Security vulnerability scanning
   - **Safety**: Dependency vulnerability check

3. **Integration** - End-to-end tests
   - Tests import_quiz.py script
   - Validates quiz JSON structure
   - Ensures full workflow functionality

4. **Status Check** - Overall CI status
   - Aggregates all job results
   - Provides summary for PR

### 💬 `pr-comment.yml` - PR Test Results

**Triggers:** Pull request opened/updated

**Features:**
- Posts/updates test results as PR comment
- Shows pass/fail status with emojis
- Displays coverage percentage
- Provides detailed test output in collapsible section
- Uploads coverage HTML report as artifact

## Setup Requirements

### Repository Secrets

No secrets required for basic functionality.

**Optional Integrations:**
- `CODECOV_TOKEN` - For Codecov integration (recommended)

### Branch Protection Rules

Recommended settings for `main` branch:

```yaml
Require status checks to pass:
  ✅ Test (Python 3.10, 3.11, 3.12, 3.13)
  ✅ Code Quality Analysis
  ✅ Integration Tests
  ✅ CI Status

Require branches to be up to date: ✅
```

## Viewing Results

### In Pull Requests

1. **Checks Tab** - View all workflow runs
2. **Files Changed** - See inline annotations from flake8
3. **Conversation** - Automated comment with test summary
4. **Actions Tab** - Detailed logs and artifacts

### Artifacts

Available for 30 days after workflow run:
- `coverage-report` - HTML coverage report
- `test-report` - HTML test results

Download from: Actions → Workflow Run → Artifacts

## Local Testing

Run the same checks locally before pushing:

```bash
# Run tests
python -m pytest tests/ -v --cov=quizzer --cov-report=html

# Code formatting
black --check quizzer/ *.py
isort --check-only quizzer/ *.py

# Linting
flake8 quizzer/ *.py
pylint quizzer/ *.py

# Type checking
mypy quizzer/ *.py --ignore-missing-imports

# Security
bandit -r quizzer/ *.py
```

Or install pre-commit hooks (see below).

## Pre-commit Hooks (Recommended)

Install pre-commit to run checks automatically:

```bash
pip install pre-commit
pre-commit install
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
  
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

## Workflow Status Badges

Add to README.md:

```markdown
![CI](https://github.com/<owner>/<repo>/workflows/CI%20-%20Tests%20and%20Code%20Quality/badge.svg)
```

## Troubleshooting

### Tests Fail in CI but Pass Locally

- Check Python version (CI uses 3.10-3.13)
- Verify all dependencies in requirements.txt
- Check for OS-specific issues (CI uses Ubuntu)

### Code Quality Failures

- Run `black quizzer/ *.py` to auto-format
- Run `isort quizzer/ *.py` to sort imports
- Fix linting issues reported by flake8

### Coverage Below Threshold

- Add tests for uncovered code
- Check coverage report: `htmlcov/index.html`

## Continuous Deployment

Future enhancements:
- Auto-publish to PyPI on release
- Build and publish documentation
- Create GitHub releases with changelogs
