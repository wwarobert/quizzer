#!/usr/bin/env pwsh
# Setup script to install git hooks

Write-Host "Installing git hooks..." -ForegroundColor Cyan

$hooksDir = ".git\hooks"
$sourceDir = "hooks"

# Check if .git directory exists
if (-not (Test-Path ".git")) {
    Write-Host "❌ Error: Not in a git repository root" -ForegroundColor Red
    exit 1
}

# Copy pre-push hook
$sourcePath = Join-Path $sourceDir "pre-push"
$destPath = Join-Path $hooksDir "pre-push"

if (Test-Path $sourcePath) {
    Copy-Item $sourcePath $destPath -Force
    Write-Host "✅ Installed pre-push hook" -ForegroundColor Green
} else {
    Write-Host "❌ Error: pre-push hook not found at $sourcePath" -ForegroundColor Red
    exit 1
}

# Make hook executable (on Unix-like systems)
if ($IsLinux -or $IsMacOS) {
    chmod +x $destPath
}

Write-Host ""
Write-Host "Git hooks installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "The pre-push hook will now run flake8 checks before every push." -ForegroundColor Yellow
Write-Host "To bypass the hook (not recommended), use: git push --no-verify" -ForegroundColor Gray
