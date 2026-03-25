# Create GitHub PR URL with pre-filled description
# This solves the issue of empty PR descriptions

$title = "refactor(js): Modularize JavaScript into ES6 modules (Sprint 3)"

$body = @"
## Summary
Split 870-line monolithic app.js into 13 focused ES6 modules for better maintainability. Created modular directory structure with separated concerns, documented CSS organization plan.

## Changes
**18 files changed** (3 modified, 15 new) | **456 tests passing** (all 456 ✅)

**JavaScript Modules Created:**
- ``config/motivational.js`` - Message configuration (55 lines)
- ``state/quiz-state.js`` - Centralized state (85 lines)
- ``ui/notifications.js``, ``ui/sidebar.js``, ``ui/screens.js`` - UI layer
- ``quiz/quiz-manager.js``, ``quiz/timer.js``, ``quiz/runner.js`` - Quiz logic
- ``dashboard/dashboard.js``, ``dashboard/analytics.js`` - Analytics
- ``app.js`` - Main orchestration with ES6 imports

**CSS Organization:**
- Documented comprehensive CSS refactoring plan
- Created directory structure (base/, layout/, components/, pages/, utilities/)
- Extracted ``base/variables.css`` and ``base/reset.css``
- Strategy: Keep existing ``style.css`` intact, migrate incrementally

**Benefits:**
- Each module <150 lines (was 870 lines)
- Clear dependencies via ES6 imports
- No global scope pollution
- Better testability and maintainability

## Validation
✅ All 456 tests passing | ✅ Flake8 checks passed | ✅ No regressions

See ``static/css/README.md`` for CSS organization plan.
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
