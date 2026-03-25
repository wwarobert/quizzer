# Sprint 2: Review Mode + Answer Explanations

## Summary
Add educational learning mode with answer explanations. Support optional 3rd column in CSV for detailed explanations, implement `--review` mode for immediate feedback during quiz, and enhance reports with explanation display.

## Goals

### 1. Answer Explanations (Data Layer)
- **CSV Import**: Support optional 3rd column `Question, Answer, Explanation`
- **Quiz Schema**: Extend JSON to store explanations
- **Backward Compatible**: Works with 2-column CSVs (explanation = None)
- **Validation**: Preserve explanations through normalization

### 2. Review Mode (CLI Experience)
- **New Flag**: `--review` or `-r` for review/practice mode
- **Immediate Feedback**: Show correct answer after each response
- **Display Explanations**: Show explanation (if available) after each question
- **No Pressure**: No pass/fail scoring, focus on learning
- **Progress Tracking**: Show running score and progress
- **Report Generation**: Save review session results with explanations

### 3. Enhanced Reporting
- **Explanation Display**: Show explanations for all questions in report
- **Visual Enhancement**: Clear separation between answer and explanation
- **Web Integration**: Display explanations in web quiz interface

---

## Implementation Plan

### Phase 1: Data Layer (Explanations in CSV/JSON)

#### Step 1: Update CSV Import (`import_quiz.py`)
**Changes:**
- Detect 2 or 3 columns in CSV
- Parse explanation from 3rd column (optional)
- Store in quiz JSON schema
- Handle empty/missing explanations
- Update validation logic

**Files Modified:**
- `import_quiz.py` - Add explanation parsing
- `quizzer/quiz_data.py` - Extend Question model with explanation field

#### Step 2: Update Quiz Data Model
**Changes:**
- Add `explanation` field to Question class
- Add `original_explanation` for display (preserve formatting)
- Update JSON serialization/deserialization
- Backward compatible with old quiz files

**Files Modified:**
- `quizzer/quiz_data.py` - Extend Question dataclass

#### Step 3: Tests for Explanation Parsing
**Test Coverage:**
- Import CSV with 3 columns → explanations stored
- Import CSV with 2 columns → explanations = None
- Mixed: some questions with explanations, some without
- Empty explanation column → treated as None
- Special characters in explanations
- Multi-line explanations

**Files Modified:**
- `tests/test_import_quiz.py` - Add explanation tests
- `tests/test_quiz_data.py` - Add schema tests

---

### Phase 2: Review Mode Implementation

#### Step 4: Add Review Mode to CLI Runner (`run_quiz.py`)
**Features:**
- Parse `--review` or `-r` flag
- Modified question loop:
  - Show question
  - Get user answer
  - Immediately show ✓/✗ result
  - Display correct answer
  - Display explanation (if available)
  - Pause for "Press Enter to continue"
  - Track statistics but don't enforce pass/fail
- Show final summary with running score
- Generate HTML report with review mode indicator

**Flow:**
```
Question 1/50: What is the capital of France?
Your answer: paris
✅ Correct!

Explanation: Paris has been the capital of France since 987 AD...

[Press Enter for next question]

---

Question 2/50: What are primary colors?
Your answer: red, blue, green
❌ Incorrect

Correct Answer: red, blue, yellow

Explanation: Primary colors cannot be created by mixing other colors...

[Press Enter for next question]
```

**Files Modified:**
- `run_quiz.py` - Add review mode logic
- `quizzer/services/answer_service.py` - Add explanation retrieval

#### Step 5: Tests for Review Mode
**Test Coverage:**
- Review mode flag parsing
- Immediate feedback display
- Explanation display (when present)
- Explanation omitted (when None)
- Press Enter to continue behavior
- Report generation in review mode
- Statistics tracking (correct/incorrect counts)

**Files Modified:**
- `tests/test_run_quiz.py` - Add review mode tests

---

### Phase 3: Enhanced Reporting

#### Step 6: Update Report Templates with Explanations
**Features:**
- Show explanations for all failed questions
- Optional: Show explanations for passed questions (collapsible)
- Visual styling for explanation sections
- Review mode indicator in report header

**Files Modified:**
- `templates/reports/report.html` - Add explanation sections
- `static/css/report.css` - Style explanation display
- `quizzer/template_utils.py` - Pass explanations to template

#### Step 7: Tests for Enhanced Reports
**Test Coverage:**
- Report includes explanations for failed questions
- Report handles None explanations gracefully
- Review mode report shows all questions with explanations
- HTML output is well-formed

**Files Modified:**
- `tests/test_report_service.py` - Add explanation tests

---

### Phase 4: Web Interface Integration

#### Step 8: Add Review Mode to Web Interface (Optional)
**Features:**
- Toggle between "Quiz Mode" and "Review Mode"
- Show immediate feedback in web UI
- Display explanations in overlay notifications
- Track review sessions separately

**Files Modified:**
- `templates/index.html` - Add review mode toggle
- `static/js/app.js` - Add review mode logic
- `quizzer/web/routes.py` - Add review mode endpoint

#### Step 9: Tests for Web Review Mode
**Test Coverage:**
- Review mode toggle API
- Explanation display in web UI
- Review session tracking

**Files Modified:**
- `tests/test_web_quiz.py` - Add web review tests

---

## Success Criteria

### Must Have (MVP)
- ✅ CSV import supports optional 3rd column for explanations
- ✅ Quiz JSON stores explanations
- ✅ `--review` flag works in CLI runner
- ✅ Immediate feedback shows correct answer
- ✅ Explanations displayed in review mode
- ✅ Report templates show explanations
- ✅ All existing tests pass (376+ tests)
- ✅ New tests for explanations and review mode

### Nice to Have (Future)
- [ ] Web interface review mode
- [ ] Collapsible explanations in reports
- [ ] Export review sessions to study guide
- [ ] Multiple review modes (hints, partial answers)

---

## Testing Strategy

### Unit Tests
- CSV parsing with 2 and 3 columns
- Question model with explanation field
- Review mode CLI argument parsing
- Explanation display logic

### Integration Tests
- Full flow: CSV → JSON → Review Mode → Report
- Backward compatibility with old quiz files
- Mixed content (some with explanations, some without)

### Manual Testing
- Import sample CSV with explanations
- Run review mode and verify UX
- Check HTML reports display correctly
- Test on Python 3.10-3.13

---

## Timeline Estimate

**Total**: ~4-6 hours for full implementation

### Phase 1: Data Layer (1-2 hours)
- CSV import: 30 min
- Schema updates: 30 min
- Tests: 30-60 min

### Phase 2: Review Mode (2-3 hours)
- CLI implementation: 1-1.5 hours
- Interactive UX: 30-45 min
- Tests: 45-60 min

### Phase 3: Reports (1 hour)
- Template updates: 30 min
- Styling: 15 min
- Tests: 15 min

### Phase 4: Web (Optional, 1-2 hours)
- Web UI: 45-60 min
- Tests: 30-45 min

---

## Branch Management

**Branch**: `feature/review-mode-explanations`
**Base**: `main`
**Related**: None

**After Sprint 2**:
- **Next Sprint**: Refactoring Sprint (`refactor/split-javascript-modules`)
- **Objective**: Split monolithic app.js into ES6 modules

---

## Open Questions

1. Should explanations be required or optional in 3-column CSVs?
   - **Decision**: Optional, gracefully handle empty strings
   
2. Should review mode generate a different report template?
   - **Decision**: Same template, add review mode indicator
   
3. Should we show explanations for correct answers in review mode?
   - **Decision**: Yes, for learning reinforcement

4. Explanation character limit?
   - **Decision**: No limit, but recommend 200-500 chars for readability

---

## Notes

- Feature requested in ROADMAP.md as high priority
- Builds foundation for future enhancements (difficulty levels, categories)
- Educational focus: learning tool, not just assessment
- Maintain backward compatibility with existing quiz files

---

## ✅ Implementation Complete

**Completed**: March 25, 2026
**Time Spent**: ~4 hours
**Tests Added**: 10 (7 review mode + 3 explanation display)
**Total Tests**: 456 (all passing)

### Changes Summary

#### Files Modified (9)
1. **import_quiz.py** - Added 3rd column parsing for explanations
2. **quizzer/quiz_data.py** - Extended Question model with explanation fields
3. **run_quiz.py** - Implemented review mode with \`--review\` flag
4. **static/css/report.css** - Added explanation styling
5. **templates/reports/inline_styles.html** - Added explanation styling
6. **templates/reports/report.html** - Added explanation display in failures
7. **tests/test_import_quiz.py** - Added 3-column CSV tests
8. **tests/test_quiz_data.py** - Added explanation field tests
9. **tests/test_run_quiz.py** - Added 10 new tests for review mode and explanations

#### Key Features Implemented
- ✅ CSV import with optional 3rd column for explanations
- ✅ Backward compatible with 2-column CSVs
- ✅ \`--review\` CLI flag for learning mode
- ✅ Immediate feedback after each question
- ✅ Explanation display in review mode (when available)
- ✅ Running score display in review mode
- ✅ Explanations in HTML reports (both CLI and web)
- ✅ Review mode always exits with code 0 (no pressure)
- ✅ Beautiful explanation styling (blue accent box)

### Testing Results
\\\
tests/test_import_quiz.py    : 49 tests (3 new for explanations)
tests/test_quiz_data.py      : 43 tests (2 new for explanations)
tests/test_run_quiz.py       : 47 tests (10 new: 7 review + 3 reports)
Total test suite             : 456 tests (all passing)
\\\

### Example Usage

**Import quiz with explanations:**
\\\ash
python import_quiz.py examples/sample_with_explanations.csv
\\\

**Run in review mode:**
\\\ash
python run_quiz.py --review
python run_quiz.py data/quizzes/az-104/quiz_001.json --review
\\\

**Review mode experience:**
\\\
Question 1/50 (REVIEW MODE)
What is the capital of France?

Your answer: paris
✓ CORRECT!

Your answer:    paris
Correct answer: Paris

📘 Explanation:
   Paris has been the capital of France since 987 AD...

Current Score: 1/1 (100.0%)

Press Enter for next question...
\\\

### Ready for Review
- [x] All 456 tests passing
- [x] Code follows project style
- [x] No breaking changes
- [x] Backward compatible with old quizzes
- [x] Documentation updated (help text, examples)
- [x] Commit messages follow convention

