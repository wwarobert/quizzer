#!/usr/bin/env pwsh
# Pre-push hook to run flake8 before pushing (PowerShell version)
# This ensures code quality checks pass before creating a PR

Write-Host "Running flake8 code quality checks..." -ForegroundColor Cyan

# Run flake8 on the quizzer package
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

# Also check main scripts
$result = python -m flake8 --ignore E501 import_quiz.py run_quiz.py web_quiz.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Flake8 checks failed on main scripts!" -ForegroundColor Red
    Write-Host "Please fix the code quality issues before pushing." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ All flake8 checks passed!" -ForegroundColor Green
exit 0
