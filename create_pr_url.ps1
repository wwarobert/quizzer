# Create GitHub PR - SIMPLE MANUAL METHOD
# URL pre-filling is unreliable - manual paste is faster and always works

# Get current branch
$currentBranch = git branch --show-current

# Generate simple PR URL (no parameters - GitHub's pre-filling is broken)
$prUrl = "https://github.com/wwarobert/quizzer/compare/main...${currentBranch}"

# SHORT description for manual paste
$description = @"
Split 870-line app.js into 13 ES6 modules (<150 lines each).

**Changes:** 18 files, 456 tests passing ✅

See PR_SPRINT3_REFACTORING.md for details.
"@

# Display instructions
Write-Host ""
Write-Host "=== CREATE PULL REQUEST ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Click this URL:" -ForegroundColor Yellow
Write-Host "   $prUrl" -ForegroundColor Green
Write-Host ""
Write-Host "2️⃣  Copy and paste this description:" -ForegroundColor Yellow
Write-Host $description -ForegroundColor White
Write-Host ""
Write-Host "✅ Simple and reliable - no URL encoding issues!" -ForegroundColor Green
Write-Host ""

# Copy URL to clipboard
$prUrl | Set-Clipboard
Write-Host "📋 PR URL copied to clipboard" -ForegroundColor Cyan
Write-Host ""
