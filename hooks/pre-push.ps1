#!/usr/bin/env pwsh
# Pre-push hook to run code quality checks and tests before pushing
# This ensures both code quality and functionality checks pass before creating a PR

Write-Host ""
Write-Host "🔍 Running pre-push validation..." -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
} elseif (Test-Path ".venv/bin/activate") {
    . ".venv/bin/activate"
}

# Step 1: Run flake8 on the quizzer package
Write-Host "1️⃣  Running flake8 on quizzer package..." -ForegroundColor Yellow
$result = python -m flake8 --ignore E501 quizzer/
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Flake8 checks failed!" -ForegroundColor Red
    Write-Host "Please fix the code quality issues before pushing." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To see details, run:" -ForegroundColor Yellow
    Write-Host "  python -m flake8 --ignore E501 quizzer/" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To skip this check (not recommended), use: git push --no-verify" -ForegroundColor Gray
    exit 1
}
Write-Host "   ✅ Package checks passed" -ForegroundColor Green

# Step 2: Check main scripts
Write-Host "2️⃣  Running flake8 on main scripts..." -ForegroundColor Yellow
$result = python -m flake8 --ignore E501 import_quiz.py run_quiz.py web_quiz.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Flake8 checks failed on main scripts!" -ForegroundColor Red
    Write-Host "Please fix the code quality issues before pushing." -ForegroundColor Yellow
    exit 1
}
Write-Host "   ✅ Script checks passed" -ForegroundColor Green

# Step 3: Run test suite
Write-Host "3️⃣  Running test suite..." -ForegroundColor Yellow
$result = python -m pytest tests/ -q --tb=line
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Tests failed!" -ForegroundColor Red
    Write-Host "Please fix the failing tests before pushing." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To see details, run:" -ForegroundColor Yellow
    Write-Host "  python -m pytest tests/ -v" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To skip this check (not recommended), use: git push --no-verify" -ForegroundColor Gray
    exit 1
}
Write-Host "   ✅ All tests passed" -ForegroundColor Green

Write-Host ""
Write-Host "✅ All pre-push checks passed! Safe to push." -ForegroundColor Green
Write-Host ""
exit 0
