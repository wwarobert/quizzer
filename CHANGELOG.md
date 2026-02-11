# Changelog

All notable changes to the Quizzer project will be documented in this file.

## [1.5.0] - 2026-02-11

### Major Release: Web Interface

#### Web Browser Interface (web_quiz.py)
- **Flask-Based Server**: Complete web application for taking quizzes in the browser
- **Beautiful Blue Theme**: Modern design with CSS custom properties (variables)
  - Primary blue (#2563eb) color scheme
  - Gradient backgrounds and smooth transitions
  - Professional styling for all components
- **Automatic Dark Mode**: Detects system preferences via `@media (prefers-color-scheme: dark)`
  - Seamless switching between light and dark themes
  - Optimized colors for both modes
- **Comprehensive Dashboard**: 
  - Performance metrics card (total quizzes, average score, pass rate)
  - Visual pie charts (quiz breakdown, question analysis)
  - Activity timeline with recent quiz attempts
  - Quick statistics (time tracking, quiz counts)
- **Interactive Sidebar** (250px width):
  - Hierarchical quiz browser organized by folder
  - Expandable/collapsible folder structure
  - Quick stats section
  - Smooth hover effects and active highlighting
- **Real-time Quiz Taking**:
  - Live timer tracking duration (MM:SS format)
  - Visual progress bar (0-100%)
  - Auto-focused input fields
  - Instant answer feedback with color coding (✓ green / ✗ red)
  - Keyboard shortcuts (Enter to submit, Escape to quit)
- **Overlay Notification System**:
  - Custom notifications instead of browser `alert()` popups
  - Elegant centered overlays with icons (✓✗ⓘ⚠)
  - Confirmation dialogs with callback support
  - Non-blocking, user-friendly design
- **Comprehensive Error Logging**:
  - Python logging module with `RotatingFileHandler`
  - Log file: `logs/web_quiz.log` (auto-rotates at 10MB, keeps 5 backups)
  - Dual output: DEBUG to file, INFO to console
  - Flask error handlers (404, 500, Exception)
  - All routes wrapped in try-except with detailed logging
  - Stack traces for debugging
- **Fully Responsive Design**:
  - Desktop: Full sidebar + main content
  - Tablet: Collapsible sidebar
  - Mobile: Stacked layout, optimized cards
- **RESTful API Endpoints**:
  - `GET /`: Main HTML page
  - `GET /api/quizzes`: List all quizzes
  - `GET /api/quiz?path=<path>`: Load specific quiz
  - `POST /api/check-answer`: Validate answers
  - `POST /api/save-report`: Generate HTML report
  - `GET /version`: Server version info
- **Command-Line Options**:
  - `--host`: Bind to specific host (default: 127.0.0.1)
  - `--port`: Custom port (default: 5000)
  - `--debug`: Enable debug mode with auto-reload
- **Usage**: `python web_quiz.py` (requires Flask >= 3.0.0)
- **Access**: `http://127.0.0.1:5000` by default

#### Non-Interactive Mode with --force Flag
- **New CLI Flag**: Added `--force` flag to skip interactive prompts
- **Automatic Deletion**: When `--force` is used, existing quizzes are automatically deleted without prompting
- **CI/CD Friendly**: Enables use in automated pipelines like GitHub Actions
- **Usage**: `python import_quiz.py input.csv --force`
- **Backward Compatible**: Existing behavior unchanged when flag is not used

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
