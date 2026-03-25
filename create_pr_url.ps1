# Create GitHub PR URL with pre-filled description
# IMPORTANT: Keep description SHORT (<500 chars) due to GitHub URL limits

$title = "refactor(js): Modularize JavaScript into ES6 modules (Sprint 3)"

$body = @"
## Summary
Split 870-line app.js into 13 ES6 modules (<150 lines each). Documented CSS refactoring plan.

## Changes
- 18 files (3 modified, 15 new)
- Created: config/, state/, ui/, quiz/, dashboard/ modules
- Tests: 456 passing ✅
- No regressions

See PR_SPRINT3_REFACTORING.md for full details.
"@

# Get current branch name
$currentBranch = git branch --show-current

# URL encode the title and body
$encodedTitle = [System.Web.HttpUtility]::UrlEncode($title)
$encodedBody = [System.Web.HttpUtility]::UrlEncode($body)

# Construct the full URL
$baseUrl = "https://github.com/wwarobert/quizzer/compare/main...${currentBranch}"
$fullUrl = "${baseUrl}?expand=1&title=${encodedTitle}&body=${encodedBody}"

# Output the URL
Write-Host ""
Write-Host "🔗 GitHub PR URL with Pre-filled Description:" -ForegroundColor Green
Write-Host ""
Write-Host $fullUrl -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Click the link above to create PR with description automatically filled!" -ForegroundColor Green
Write-Host ""

# Copy to clipboard
$fullUrl | Set-Clipboard
Write-Host "📋 URL copied to clipboard - just paste in browser!" -ForegroundColor Yellow
Write-Host ""
