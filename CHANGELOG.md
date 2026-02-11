# Changelog

All notable changes to the Quizzer project will be documented in this file.

## [Unreleased]

### Added - 2026-02-11

#### Interactive Quiz Management on Import
- **Existing Quiz Detection**: Import script now detects existing quiz files in the target folder before importing
- **User Prompt**: Interactive prompt asks users whether to delete or keep existing quizzes
  - Accepts `yes`/`y`/`no`/`n` (case-insensitive)
  - Repeats prompt until valid input is received
- **Safe Deletion**: If user chooses to delete, all old quizzes are removed **before** new ones are created
- **Keep Option**: If user chooses to keep, old quizzes remain and new quizzes are added alongside them

#### Test Coverage
- Added 10 unit tests in `TestExistingQuizManagement` class:
  - Directory scanning and file detection
  - User prompt handling with various inputs
  - File deletion operations
  - Error handling for missing files
- Added 2 integration tests in `TestMainFunction` class:
  - Full workflow with deletion (`test_main_with_existing_quizzes_delete_yes`)
  - Full workflow keeping old quizzes (`test_main_with_existing_quizzes_delete_no`)
- **Total Tests**: 45 (previously 33, now 45)
- **All Tests Passing**: ✓

#### Documentation Updates
- **README.md**: Added "Managing Existing Quizzes" subsection with example interaction
- **IMPLEMENTATION.md**: Added detailed section documenting the new feature
- **copilot-instructions.md**: Updated Import Script Features section

### Benefits
- Prevents accidental accumulation of outdated quiz versions
- Gives users explicit control over quiz file management
- Clear visual feedback with ⚠️ warning icons and deletion confirmations
- Non-destructive by default (requires explicit user action to delete)
- Ensures clean state before import when desired

---

## Previous Features

### HTML Report Generation - 2026-02-06
- Automatic HTML report generation after each quiz completion
- Professional styling with responsive design
- Pass/fail status with color-coded indicators
- Detailed failure breakdown with correct answers

### Core Functionality - Project Start
- CSV to JSON quiz conversion
- Randomized question ordering
- Interactive quiz runner with CLI
- Smart answer validation (case-insensitive, multi-answer support)
- 80% pass threshold with detailed scoring
- Time tracking for quiz completion
