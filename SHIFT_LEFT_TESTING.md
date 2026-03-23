# Shift-Left Testing: Catch Errors Before CI

## Problem
Tests were passing locally but failing in CI due to:
1. Template path resolution issues in different environments
2. Pre-push hooks only ran flake8, not tests
3. Changes pushed without full validation

## Solution: Enhanced Pre-Push Validation

### 1. Install Enhanced Git Hooks

**Windows (PowerShell):**
```powershell
cd hooks
.\install-hooks.ps1
```

**Linux/Mac (Bash):**
```bash
cd hooks
./install-hooks.sh
```

This installs hooks that run **before every push**:
1. ✅ Flake8 code quality checks (quizzer package)
2. ✅ Flake8 on main scripts (import_quiz.py, run_quiz.py, web_quiz.py)
3. ✅ **Full test suite** (all 440 tests)

### 2. Manual Pre-Push Checklist

Before pushing any branch:

```bash
# 1. Run tests locally
python -m pytest tests/ -v

# 2. Check code quality
python -m flake8 --ignore E501 quizzer/

# 3. Verify no uncommitted changes
git status

# 4. Review your commit messages
git log --oneline -5
```

### 3. Quick Validation Command

Run this before every push:

```bash
# One command to rule them all
python -m flake8 --ignore E501 quizzer/ && python -m pytest tests/ -q
```

If both pass (exit code 0), you're safe to push.

### 4. CI Environment Parity

**Issue:** Tests passed locally but failed in CI because:
- Different Python versions (3.10 vs 3.13)
- Different path resolution
- Missing dependencies

**Solution:**
```bash
# Test with multiple Python versions locally
python3.10 -m pytest tests/
python3.11 -m pytest tests/
python3.13 -m pytest tests/

# Or use tox for matrix testing
pip install tox
tox
```

### 5. Path Resolution Best Practices

**Bad (fragile):**
```python
template_dir = Path(__file__).parent.parent / "templates"
```

**Good (robust):**
```python
template_dir = Path(__file__).parent.parent / "templates"
template_dir = template_dir.resolve()  # Absolute path

if not template_dir.exists():
    raise FileNotFoundError(f"Templates not found: {template_dir}")
```

### 6. GitHub Actions Workflow Tips

**.github/workflows/test.yml** should match your local env:
- Same Python versions
- Same dependencies (requirements.txt)
- Same test command (`pytest tests/`)

### 7. Skip Hooks (Emergency Only)

If you **absolutely must** push without validation:

```bash
git push --no-verify
```

⚠️ **Warning:** Only use this if:
- CI is broken and you're fixing it
- You're pushing documentation changes only
- You know what you're doing

### 8. Local CI Simulation (Advanced)

Install `act` to run GitHub Actions locally:

```bash
# Install act (requires Docker)
winget install nektos.act  # Windows
# or
brew install act  # macOS

# Run CI workflow locally
act -j test
```

This runs the **exact same** tests that GitHub Actions will run.

## What Changed in This PR

### Fixed: Template Path Resolution
```python
# Added explicit path resolution and validation
template_dir = template_dir.resolve()  # Make absolute

if not template_dir.exists():
    raise FileNotFoundError(...)  # Clear error message
```

### Enhanced: Pre-Push Hooks
**Before:**
- ❌ Only ran flake8
- ❌ Tests could fail in CI

**After:**
- ✅ Runs flake8 on package
- ✅ Runs flake8 on scripts
- ✅ Runs full test suite
- ✅ Clear step-by-step output

**Output example:**
```
🔍 Running pre-push validation...

1️⃣  Running flake8 on quizzer package...
   ✅ Package checks passed
2️⃣  Running flake8 on main scripts...
   ✅ Script checks passed
3️⃣  Running test suite...
   ✅ All tests passed (440/440)

✅ All pre-push checks passed! Safe to push.
```

## Quick Reference

| Action | Command |
|--------|---------|
| Install hooks | `cd hooks && ./install-hooks.sh` |
| Run tests | `pytest tests/ -v` |
| Run quality checks | `flake8 --ignore E501 quizzer/` |
| Run everything | `flake8 --ignore E501 quizzer/ && pytest tests/ -q` |
| Skip hooks (emergency) | `git push --no-verify` |
| Test specific file | `pytest tests/test_report_service.py -v` |
| Test with coverage | `pytest tests/ --cov=quizzer` |

## Best Practices

1. **Always run tests before pushing** — Saves CI time and embarrassment
2. **Use hooks** — Automation prevents human error
3. **Match CI environment** — Same Python version, dependencies
4. **Use absolute paths** — `Path.resolve()` for cross-platform compatibility
5. **Test edge cases** — Different OS, Python versions
6. **Commit frequently** — Small commits are easier to debug
7. **Review your own PR** — Catch issues before reviewers do

## Troubleshooting

### Hook not running?
```bash
# Verify hook is installed
ls -la .git/hooks/pre-push

# Should show link to hooks/pre-push.ps1 or hooks/pre-push
```

### Tests passing locally but failing in CI?
1. Check Python version difference
2. Check for absolute vs relative paths
3. Check for OS-specific code (Windows vs Linux)
4. Check for timezone or locale differences
5. Check for missing files in git (use `git ls-files`)

### Path issues?
```python
# Debug path resolution
from pathlib import Path
print(f"__file__: {__file__}")
print(f"parent: {Path(__file__).parent}")
print(f"parent.parent: {Path(__file__).parent.parent}")
print(f"resolved: {Path(__file__).parent.parent.resolve()}")
```

### Files ignored by .gitignore?
```bash
# Check if files are being ignored
git check-ignore -v templates/reports/report.html

# List all ignored files
git status --ignored

# Force add a file that's being ignored
git add -f path/to/file

# Verify files are tracked
git ls-files templates/
```

**Common .gitignore mistakes:**
- ❌ `report.html` — Ignores report.html EVERYWHERE (including templates/)
- ✅ `/report.html` — Only ignores report.html in ROOT directory
- ✅ `data/reports/*.html` — Only ignores HTML in specific folder

**This PR lesson:** The pattern `report.html` in .gitignore was blocking `templates/reports/report.html` from being committed!

## Resources

- [Pre-commit hooks](https://pre-commit.com/)
- [pytest documentation](https://docs.pytest.org/)
- [GitHub Actions `act`](https://github.com/nektos/act)
- [flake8 documentation](https://flake8.pycqa.org/)
