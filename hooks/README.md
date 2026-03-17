# Git Hooks

This directory contains git hooks to maintain code quality.

## Available Hooks

### pre-push

Runs flake8 code quality checks before pushing to remote. This ensures that:
- Code follows PEP 8 style guidelines (except E501 - line length)
- No obvious code quality issues are introduced
- CI/CD pipeline won't fail due to flake8 errors

## Installation

### Automatic Installation (Recommended)

Run the installation script from the repository root:

**PowerShell (Windows):**
```powershell
.\hooks\install-hooks.ps1
```

**Bash (Linux/Mac):**
```bash
chmod +x hooks/install-hooks.sh
./hooks/install-hooks.sh
```

### Manual Installation

Copy the hook file to your `.git/hooks/` directory:

**Windows:**
```powershell
Copy-Item hooks\pre-push .git\hooks\pre-push -Force
```

**Linux/Mac:**
```bash
cp hooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

## Usage

Once installed, the pre-push hook runs automatically before every `git push`:

```bash
git push
```

Output example:
```
Running flake8 code quality checks...
✅ All flake8 checks passed!
```

### Bypassing the Hook

If you need to push without running checks (not recommended):

```bash
git push --no-verify
```

**⚠️ Warning:** Bypassing the hook may cause CI/CD pipeline failures.

## What Gets Checked

The pre-push hook runs flake8 on:
- `quizzer/` - Main package directory
- `import_quiz.py` - Import script
- `run_quiz.py` - CLI runner
- `web_quiz.py` - Web server

### Ignored Rules

- `E501` - Line too long (we use longer lines for readability)

## Troubleshooting

### Hook doesn't run

1. Check if the hook file exists: `ls -la .git/hooks/pre-push`
2. On Unix systems, ensure it's executable: `chmod +x .git/hooks/pre-push`
3. Verify flake8 is installed: `python -m flake8 --version`

### Flake8 not found

Install flake8:
```bash
pip install flake8
```

### False positives

If you believe flake8 is incorrectly flagging code, you can:
1. Add inline ignore comment: `# noqa: <error_code>`
2. Update `.flake8` configuration file
3. Discuss with team before modifying rules

## Benefits

✅ **Catch issues early** - Before they reach CI/CD  
✅ **Consistent code style** - Enforced automatically  
✅ **Faster reviews** - No style discussions needed  
✅ **Clean git history** - No "fix linting" commits  
✅ **CI/CD stability** - Fewer pipeline failures  

## Related

- See `.github/workflows/` for CI/CD configuration
- See `requirements.txt` for flake8 version
- See project README for full development setup
