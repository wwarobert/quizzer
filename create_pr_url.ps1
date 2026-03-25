# Create GitHub PR URL with pre-filled description
# This solves the issue of empty PR descriptions

$title = "feat(quiz): Add review mode with answer explanations (Sprint 2)"

$body = @"
## Summary
Add review mode with answer explanations for educational learning. CSV import now supports optional 3rd column for explanations, new ``--review`` flag provides immediate feedback, and HTML reports display explanations.

## Changes
**11 files changed** (9 modified, 2 new) | **456 tests passing** (10 new)

**Key Features:**
- CSV import supports ``Question, Answer, Explanation`` format (backward compatible)
- ``--review`` CLI flag for learning mode with immediate feedback
- Explanations displayed in reports with blue accent styling
- Running score tracker in review mode
- Review mode always passes (exit code 0) - no pressure learning

**Modified:**
- ``import_quiz.py`` - 3rd column parsing
- ``quizzer/quiz_data.py`` - Question model with explanation fields  
- ``run_quiz.py`` - Review mode implementation
- Report templates + CSS - Explanation display

**Tests:** 49 import + 43 quiz_data + 47 run_quiz = 456 total ✅

## Usage
``````bash
# Import with explanations
python import_quiz.py examples/sample_with_explanations.csv

# Run review mode  
python run_quiz.py --review
``````

## Validation
✅ All 456 tests passing | ✅ Flake8 checks passed | ✅ Backward compatible

See ``PR_SPRINT2_REVIEW_MODE.md`` for full details.
"@

# URL encode the title and body
$encodedTitle = [System.Web.HttpUtility]::UrlEncode($title)
$encodedBody = [System.Web.HttpUtility]::UrlEncode($body)

# Construct the full URL
$baseUrl = "https://github.com/wwarobert/quizzer/compare/main...feature/review-mode-explanations"
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
