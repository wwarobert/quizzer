# GitHub PR URL Generator with Auto-Fill
# Keeps description EXTREMELY short to avoid GitHub URL length limits

# Get current branch
$currentBranch = git branch --show-current

# ULTRA SHORT description (under 100 chars to guarantee it works)
$title = "refactor(js): Modularize JavaScript (Sprint 3)"

$body = @"
Split 870 lines into 13 ES6 modules. All tests passing.

See PR_SPRINT3_REFACTORING.md
"@

# URL encode
Add-Type -AssemblyName System.Web
$encodedTitle = [System.Web.HttpUtility]::UrlEncode($title)
$encodedBody = [System.Web.HttpUtility]::UrlEncode($body)

# Build URL with parameters
$url = "https://github.com/wwarobert/quizzer/compare/main...${currentBranch}?expand=1&title=${encodedTitle}&body=${encodedBody}"

# Display
Write-Host ""
Write-Host "🔗 CLICK THIS LINK (description will auto-fill):" -ForegroundColor Green
Write-Host ""
Write-Host $url -ForegroundColor Cyan
Write-Host ""

# Copy to clipboard
$url | Set-Clipboard
Write-Host "✅ URL copied to clipboard - paste in browser!" -ForegroundColor Yellow
Write-Host ""
