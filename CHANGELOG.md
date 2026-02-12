# Changelog

All notable changes to the Quizzer project will be documented in this file.

## [Unreleased]

### Added - 2026-02-12

#### UX Research Documentation
- **Jobs-to-be-Done Analysis**: Created JTBD document for certification candidate user persona in `docs/ux/web-quiz-jtbd.md`
- **User Journey Map**: Documented 5-stage journey from planning to progress tracking in `docs/ux/web-quiz-journey.md`
- **Flow Specification**: Added Figma-ready flow spec with accessibility checklist in `docs/ux/web-quiz-flow.md`
- **User Persona**: Certification candidates preparing for high-stakes exams with daily practice sessions

### Changed - 2026-02-12

#### UI/UX Improvements - Minimalistic Redesign
- **Modal Dialog Improvements**:
  - Increased width to 720px (from 520px) for better content layout and reduced vertical stacking
  - Added max-height (70vh) with scrolling to prevent overly tall dialogs
  - Reduced icon size to 2em for better visual proportions
  - Lightened overlay opacity to 35% (from 50%)
  - Removed heavy box-shadows and borders for cleaner appearance
  - Text alignment changed to left for better readability
  - Buttons right-aligned with minimal hover effects (no layout shifts)
  - Message text now preserves line breaks with `white-space: pre-line`

- **Results Screen Enhancements**:
  - Stat cards: Replaced heavy 2px borders with subtle 1px borders (#EEEEEE)
  - Removed box-shadows for flatter, cleaner design
  - Improved spacing and typography hierarchy
  - Failure items: Removed background boxes, using only left accent border
  - Compact failure list with better scanability
  - Added inline "Report saved" message instead of modal popup

- **Streamlined Quiz Completion Flow**:
  - **Removed confirmation dialog** when clicking "Finish Quiz" button
  - Users now go **directly to results page** with one click
  - Eliminated intermediate popups between quiz finish and results display
  - Results page shows inline status message for saved reports (no modal)
  - Faster, more efficient workflow for certification exam preparation

### Added - 2026-02-11

#### Configurable Logging System
- **Flexible Log Levels**: Control logging verbosity via command-line arguments
- **Default Behavior**: ALL (DEBUG) level - logs everything for comprehensive troubleshooting
- **Command-Line Options**:
  - `--log-level`: Set level for both file and console (ALL, DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - `--log-file-level`: Override level for file logging only
  - `--log-console-level`: Override level for console logging only
- **Independent Control**: Configure file and console logging separately for optimal debugging
- **Level Hierarchy**: CRITICAL → ERROR → WARNING → INFO → DEBUG (ALL)
- **Examples**:
  - `--log-level INFO`: Only INFO and above to both destinations
  - `--log-file-level DEBUG --log-console-level WARNING`: Detailed file logs, minimal console output
  - `--log-level ERROR`: Only errors for quiet operation
- **Smart Defaults**: 'ALL' alias for DEBUG makes maximum logging intuitive
- **Runtime Feedback**: Server startup shows active log level configuration

**Use Cases**:
- **Development**: ALL (DEBUG) for complete visibility
- **Production**: WARNING or ERROR for cleaner logs
- **Debugging**: DEBUG for files, WARNING for console (reduces noise)
- **CI/CD**: ERROR or CRITICAL for minimal output

### Fixed - 2026-02-11

#### CI/CD Pipeline
- **Test Failures**: Fixed Flask import errors in GitHub Actions CI pipeline
  - Root cause: CI workflow only installed pytest/pytest-cov, not project dependencies
  - Solution: Updated workflow to install all requirements from `requirements.txt`
  - Impact: test_web_quiz.py, test_sidebar_dashboard.py, test_two_column_layout.py now run successfully
- **Code Quality**: Updated code-quality job to install project dependencies
  - Ensures linting tools (pylint, mypy, bandit) can properly analyze web_quiz.py
  - Safety tool now checks actual project dependencies for vulnerabilities

#### HTTPS Support for Web Interface
- **Automatic HTTPS**: Web server now runs on HTTPS by default with auto-generated self-signed certificates
- **SSL Certificate Generation**: Automatically creates SSL certificates on first run using `cryptography` library
- **Self-Signed Certificates**: Development-ready certificates valid for `localhost` and `127.0.0.1`
- **Graceful Fallback**: If `cryptography` is not installed, server automatically falls back to HTTP
- **Command-Line Options**:
  - `--no-https`: Disable HTTPS and force HTTP mode
  - `--cert <path>`: Use custom SSL certificate file
  - `--key <path>`: Use custom SSL private key file
- **Certificate Management**: Certificates stored in `certs/` directory (excluded from git)
- **Production-Ready**: Support for custom SSL certificates from trusted CAs
- **Documentation**: Comprehensive README in `certs/` directory with usage instructions

**Security Benefits**:
- Encrypted communications between browser and server
- Protection against man-in-the-middle attacks
- Best practice for web applications (even in development)

**Browser Compatibility**: 
- All modern browsers supported
- Self-signed certificate warnings are normal for local development
- Clear instructions provided for bypassing browser warnings

---

## [1.5.0] - 2026-02-11

### Major Release: Web Interface

#### Web Browser Interface (web_quiz.py)
- **Flask-Based Server**: Web application for taking quizzes in the browser
- **Blue Theme**: CSS custom properties (variables)
  - Primary blue (#2563eb) color scheme
  - Gradient backgrounds and transitions
- **Automatic Dark Mode**: Detects system preferences via `@media (prefers-color-scheme: dark)`
  - Switching between light and dark themes
  - Optimized colors for both modes
- **Dashboard**: 
  - Performance metrics card (total quizzes, average score, pass rate)
  - Pie charts (quiz breakdown, question analysis)
  - Activity timeline with recent quiz attempts
  - Statistics (time tracking, quiz counts)
- **Sidebar** (250px width):
  - Hierarchical quiz browser organized by folder
  - Expandable/collapsible folder structure
  - Stats section
  - Hover effects and active highlighting
- **Real-time Quiz Taking**:
  - Timer tracking duration (MM:SS format)
  - Progress bar (0-100%)
  - Auto-focused input fields
  - Answer feedback with color coding (✓ green / ✗ red)
  - Keyboard shortcuts (Enter to submit, Escape to quit)
- **Overlay Notification System**:
  - Custom notifications instead of browser `alert()` popups
  - Centered overlays with icons (✓✗ⓘ⚠)
  - Confirmation dialogs with callback support
  - Non-blocking design
- **Error Logging**:
  - Python logging module with `RotatingFileHandler`
  - Log file: `logs/web_quiz.log` (auto-rotates at 10MB, keeps 5 backups)
  - Dual output: DEBUG to file, INFO to console
  - Flask error handlers (404, 500, Exception)
  - All routes wrapped in try-except with detailed logging
  - Stack traces for debugging
- **Responsive Design**:
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
