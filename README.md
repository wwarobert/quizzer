# Quizzer

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-241%20passing-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)](tests/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting](https://img.shields.io/badge/linting-ruff-orange.svg)](https://github.com/astral-sh/ruff)

A quiz platform that generates randomized quizzes from CSV files with both command-line and web browser interfaces.

## Features

### Core Functionality
- Simple CSV input format (Question, Answer)
- Randomized question selection and ordering
- Smart answer validation (case-insensitive, whitespace-tolerant, multi-answer support)
- Automatic HTML report generation
- Time tracking for quiz completion
- Zero external dependencies for CLI (Python standard library only)

### Two Ways to Take Quizzes

**Command-Line Interface:**
- Traditional terminal-based quiz runner
- No external dependencies required
- Perfect for automation and scripting
- Lightweight and fast

**Web Interface:**
- Modern minimalistic Scandinavian design
- Clean, light interface with centered elements
- White sidebar with compact menu structure
- Dashboard with performance metrics and analytics
- Breadcrumb navigation for easy orientation
- Real-time progress tracking and timer
- Instant feedback after each answer
- Fullscreen mode for distraction-free quizzing
- Overlay notifications (no browser popups)
- Responsive design (desktop, tablet, mobile)
- Charts for quiz performance and question breakdown
- Activity timeline with recent quiz attempts
- HTML report generation
- Error logging with automatic rotation

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Creating Quizzes](#creating-quizzes)
  - [Taking Quizzes](#taking-quizzes)
- [CSV Format](#csv-format)
- [Quiz Format](#quiz-format)
- [Examples](#examples)
- [Development](#development)
- [License](#license)

## Installation

### Prerequisites

- Python 3.10 or higher
- Flask 3.0+ (only required for web interface)
- No other external dependencies required

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd quizzer
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. (Optional for web interface) Install Flask:
   ```bash
   pip install Flask>=3.0.0
   ```

4. Verify installation:
   ```bash
   python import_quiz.py --help
   python run_quiz.py --help
   python web_quiz.py --help  # If Flask installed
   ```

## Quick Start

### 1. Create a CSV file with your questions

Create `data/input/my_questions.csv`:
```csv
Question,Answer
What is the capital of France?,Paris
List primary colors,"red, blue, yellow"
What is 2 + 2?,4
```

Or use the provided example:
```bash
# Example CSV is already in data/input/az-104.csv
```

### 2. Generate a quiz

```bash
python import_quiz.py data/input/my_questions.csv
```

Output: `data/quizzes/quiz_YYYYMMDD_HHMMSS.json`

### 3. Take the quiz

**Option A: Command Line**
```bash
python run_quiz.py data/quizzes/quiz_YYYYMMDD_HHMMSS.json
```

**Option B: Web Browser** (recommended)
```bash
# Easy way (auto-installs dependencies):
python start_server.py

# Or direct:
python web_quiz.py

# Windows: Double-click start_server.bat

# Open http://127.0.0.1:5000 in your browser
```

## Usage

### Creating Quizzes

The `import_quiz.py` script converts CSV files into randomized quiz JSON files.

#### Basic Usage

```bash
python import_quiz.py <csv_file>
```

#### Advanced Options

```bash
python import_quiz.py questions.csv \
  --output data/quizzes/ \
  --number 3 \
  --max-questions 25 \
  --prefix midterm
```

**Parameters:**

| Option | Description | Default |
|--------|-------------|---------|
| `csv_file` | Path to input CSV file | *required* |
| `-o, --output` | Output directory for quiz JSON files | `data/quizzes/` |
| `-n, --number` | Number of quiz variations to generate | `1` |
| `-m, --max-questions` | Maximum questions per quiz | `50` |
| `--prefix` | Prefix for quiz IDs | `quiz` |
| `--force` | Automatically delete existing quizzes without prompting | `false` |

#### Examples

Generate one quiz:
```bash
python import_quiz.py data/input/az-104.csv
```

Generate 5 quiz variations:
```bash
python import_quiz.py data/input/biology.csv -n 5
```

Generate quiz with only 20 questions:
```bash
python import_quiz.py data/input/history.csv -m 20
```

Generate in non-interactive environment (CI/CD):
```bash
python import_quiz.py data/input/questions.csv --force
```

### Using the Web Interface

The web interface provides a browser-based way to take quizzes with real-time feedback and progress tracking.

#### Starting the Web Server

**Recommended: Use the startup script** (auto-checks dependencies)
```bash
# Automatically creates virtual environment and installs requirements if needed
python start_server.py

# Windows: Simply double-click start_server.bat
```

**Alternative: Direct start**
```bash
# Install Flask (required for web interface)
pip install Flask>=3.0.0

# Optional: Install cryptography for HTTPS support
pip install cryptography>=41.0.0

# Start the web server (HTTPS if cryptography installed, HTTP otherwise)
python web_quiz.py
```

**HTTPS Support**:
- If `cryptography` is installed: Server runs on `https://127.0.0.1:5000` with auto-generated self-signed certificates
- If `cryptography` is not installed: Server automatically falls back to HTTP on `http://127.0.0.1:5000`

**Browser Security Warning**: 
When using self-signed certificates for local development, your browser will show a security warning. This is normal and safe for local development:
1. Click "Advanced" or "Show Details"
2. Click "Proceed to localhost" or "Accept the Risk and Continue"
3. The warning only appears once per browser session

#### Advanced Options

```bash
# Run on custom port
python web_quiz.py --port 8443

# Disable HTTPS (force HTTP only)
python web_quiz.py --no-https

# Make accessible from other devices on network (HTTPS)
python web_quiz.py --host 0.0.0.0 --port 8443

# Use custom SSL certificates (for production)
python web_quiz.py --cert /path/to/cert.pem --key /path/to/key.pem

# Enable debug mode with auto-reload
python web_quiz.py --debug

# Configure logging levels (default: ALL - logs everything)
# Options: ALL, DEBUG, INFO, WARNING, ERROR, CRITICAL
python web_quiz.py --log-level INFO                    # Set both file and console to INFO
python web_quiz.py --log-file-level DEBUG --log-console-level WARNING  # Different levels
python web_quiz.py --log-level ERROR                   # Only errors and above

# Examples of logging combinations
python web_quiz.py --log-console-level WARNING         # Console: warnings only, File: ALL (DEBUG)
python web_quiz.py --log-file-level INFO               # File: INFO only, Console: ALL (DEBUG)

# Enable test mode to show sample quizzes (hidden by default)
python web_quiz.py --test-mode
```

#### Production vs Test Mode

**Production Mode (Default)**
- Sample quizzes are automatically hidden
- Only production data (e.g., az-104, biology) is visible
- Ideal for real quiz-taking sessions

**Test Mode**
- Show all quizzes including samples from `examples/`
- Useful for development and testing
- Enabled with `--test-mode` flag

```bash
# Production mode (default) - sample quizzes hidden
python web_quiz.py

# Test mode - sample quizzes visible
python web_quiz.py --test-mode
```

**Logging Configuration**:
- **Default**: ALL (DEBUG) - Logs all messages to both file and console
- **`--log-level`**: Set level for both file and console simultaneously
  - `ALL`: Everything (DEBUG level)
  - `DEBUG`: Debug messages and above
  - `INFO`: Information messages and above
  - `WARNING`: Warnings and errors only
  - `ERROR`: Errors and critical messages only
  - `CRITICAL`: Critical messages only
- **`--log-file-level`**: Override level for file logging only
- **`--log-console-level`**: Override level for console logging only
- **Log File**: `logs/web_quiz.log` (rotates at 10MB, keeps 5 backups)
- **Combinations**: You can use `--log-file-level` and `--log-console-level` together for fine-grained control

**Command-Line Options**:
| Option | Description | Default |
|--------|-------------|---------|
| `--host` | Host to bind to | `127.0.0.1` |
| `--port` | Port number | `5000` |
| `--debug` | Enable debug mode | `False` |
| `--no-https` | Disable HTTPS (use HTTP only) | `False` |
| `--cert` | Path to SSL certificate | `certs/cert.pem` |
| `--key` | Path to SSL private key | `certs/key.pem` |

#### Web Interface Features

**Quiz Taking:**
- **Smart Quiz Selection**: Browse all quizzes by folder with automatic organization
- **Real-time Timer**: Track time spent with live countdown
- **Visual Progress Bar**: See completion percentage at a glance
- **Instant Feedback**: Immediate correct/incorrect indication with visual cues
- **Keyboard Shortcuts**: Press Enter to submit, Escape to quit
- **Auto-focus Input**: Seamless typing experience without clicking

**Dashboard & Analytics:**
- **Performance Metrics**: Total quizzes taken, average score, pass rate
- **Quiz Breakdown Chart**: Visual pie chart of passed vs failed quizzes
- **Question Analysis**: See your correct/incorrect answer distribution
- **Activity Timeline**: Chronological list of recent quiz attempts with scores
- **Quick Stats**: Average time per quiz, total questions answered

**Design & UX:**
- **Custom Theme**: White sidebar (#ffffff), blue main (#77a6f7), teal/black text (#00887a/#000000), light blue/peach accents (#d3e3fc/#ffccbc)
- **Automatic Dark Mode**: Respects system preferences with transitions
- **Responsive Layout**: Adapts to screen size (desktop/tablet/mobile)
- **Overlay Notifications**: Non-blocking notifications with icons
- **Navigation**: 300px sidebar with collapsible sections
- **Animations**: Transitions and hover effects

**Reports & Logging:**
- **Automatic HTML Reports**: Styled reports with pass/fail status
- **Detailed Failure Breakdown**: See exactly which questions you missed
- **Report History**: All reports saved to `data/reports/` directory
- **Error Logging**: Comprehensive logging to `logs/web_quiz.log`
- **Log Rotation**: Automatic 10MB rotation keeping 5 backup files

#### Error Logging

The web server automatically logs all errors and important events to help with debugging:

**Log File Location**: `logs/web_quiz.log`

**Log Features**:
- Automatic log rotation (max 10MB per file, keeps 5 backups)
- Detailed error messages with stack traces
- Request logging for debugging
- Separate DEBUG level for file (detailed) and INFO level for console
- Timestamps and line numbers for easy debugging

**Log Levels**:
- `DEBUG`: Detailed information (file only)
- `INFO`: General informational messages
- `WARNING`: Warning messages for non-critical issues
- `ERROR`: Error messages with stack traces
- `CRITICAL`: Critical errors that may cause server failure

**Viewing Logs**:
```bash
# View the current log file
cat logs/web_quiz.log

# View in real-time (Linux/Mac)
tail -f logs/web_quiz.log

# View in real-time (Windows PowerShell)
Get-Content logs/web_quiz.log -Wait

# View last 50 lines
tail -n 50 logs/web_quiz.log
```

#### Managing Existing Quizzes

When importing quizzes into an existing folder (e.g., re-importing the same CSV file), the tool will detect existing quiz files and prompt you to decide whether to keep or delete them:

```
Reading questions from: data/input/az-104.csv
Loaded 200 questions

WARNING: Found 5 existing quiz(zes) in this folder:
  - az-104_20260209_164742_1.json
  - az-104_20260209_164742_2.json
  - az-104_20260209_164742_3.json
  - az-104_20260209_164742_4.json
  - az-104_20260209_164742_5.json

Do you want to DELETE these quizzes before importing? (yes/no): 
```

**Behavior:**
- Choose `yes`/`y`: Old quizzes are deleted **before** new quizzes are created
- Choose `no`/`n`: Old quizzes are kept and new quizzes are added alongside them
- Use `--force` flag: Automatically deletes old quizzes without prompting (useful for CI/CD)
- This ensures you can refresh quiz sets without accidentally accumulating old versions
- Only JSON files in the target folder are affected

### Taking Quizzes

The `run_quiz.py` script provides an interactive CLI for taking quizzes.

#### Basic Usage

```bash
python run_quiz.py <quiz_file>
```

#### Advanced Options

```bash
python run_quiz.py data/quizzes/quiz_001.json \
  --pass-threshold 75 \
  --report-output reports/
```

**Parameters:**

| Option | Description | Default |
|--------|-------------|---------|
| `quiz_file` | Path to quiz JSON file | *required* |
| `-t, --pass-threshold` | Pass threshold percentage | `80.0` |
| `-r, --report-output` | Directory to save report | *(disabled)* |
| `-q, --quiet` | Minimal output mode | `false` || `--test-mode` | Show sample quizzes (hidden by default) | `false` |

#### Production vs Test Mode

By default, the CLI runs in **production mode** which hides sample quizzes. Use `--test-mode` to show all quizzes including samples.

```bash
# Production mode (default) - sample quizzes hidden
python run_quiz.py

# Test mode - sample quizzes visible
python run_quiz.py --test-mode

# Direct quiz file (bypasses folder selection, works in both modes)
python run_quiz.py data/quizzes/az-104/quiz_001.json
```
#### Interactive Features

- Progress tracking: Shows `Question X/Y` for each question
- Multi-answer support: Separate answers with commas (e.g., `red, blue, yellow`)
- Instant feedback: Shows result after each answer
- HTML Report Generation: Automatically creates a styled HTML report in `data/reports/`
- Final report: Displays score, pass/fail, time spent, and all incorrect answers
- Keyboard interrupt: Press Ctrl+C to exit anytime

#### HTML Reports

Each quiz automatically generates an HTML report with the following features:
- Visual pass/fail status banner
- Score percentage with color coding
- Complete statistics (total/correct/failed questions)
- Detailed breakdown of all failed questions
- Responsive design with gradients

Reports are saved to: `data/reports/{quiz_id}_report.html`

Note: Each quiz run overwrites its previous report, ensuring the latest results are retained.

To view reports:
- Open the HTML file directly in a web browser
- On Windows: `start data/reports/quiz_xxx_report.html`
- On macOS: `open data/reports/quiz_xxx_report.html`
- On Linux: `xdg-open data/reports/quiz_xxx_report.html`

#### Examples

Run quiz with default 80% threshold:
```bash
python run_quiz.py data/quizzes/quiz_001.json
```

Run with 75% threshold and save report:
```bash
python run_quiz.py quiz.json -t 75 -r reports/
```

## CSV Format

### Structure

CSV files must have exactly 2 columns:

1. Column 1: Question text
2. Column 2: Answer text

### Rules

- Header row: Optional (auto-detected if first row contains "question"/"answer")
- Encoding: UTF-8
- Quotes: Use quotes for answers containing commas
- Multi-answers: Separate with commas (e.g., `"red, blue, yellow"`)
- Empty rows: Skipped automatically

### Example

```csv
Question,Answer
What is the capital of France?,Paris
"List primary colors","red, blue, yellow"
Who wrote Hamlet?,William Shakespeare
```

### Example File

See [data/input/az-104.csv](data/input/az-104.csv) for a complete example with 445 Azure certification questions.

## Quiz Format

Quizzes are stored as JSON files with the following structure:

```json
{
  "quiz_id": "az-104_20260209_164742_1",
  "created_at": "2026-02-09T16:47:42.123456",
  "source_file": "az-104.csv",
  "questions": [
    {
      "id": 1,
      "question": "What is the capital of France?",
      "answer": ["paris"],
      "original_answer": "Paris"
    },
    {
      "id": 2,
      "question": "List primary colors",
      "answer": ["blue", "red", "yellow"],
      "original_answer": "red, blue, yellow"
    }
  ]
}
```

### Key Points

- `answer`: Normalized for comparison (lowercase, sorted, no whitespace)
- `original_answer`: Preserved for display in reports
- `questions`: Limited to 50 per quiz
- `order`: Randomized during import

## Examples

### Example 1: Generate and Take Quiz

```bash
# Generate quiz from CSV in data/input/
python import_quiz.py data/input/az-104.csv

# Output shows: Created quiz 1/1: data\quizzes\az-104\az-104_20260209_164742_1.json

# Take the quiz
python run_quiz.py data/quizzes/az-104/az-104_20260209_164742_1.json
```

### Example 2: Create Multiple Variations

```bash
# Generate 3 different quiz variations from input CSV
python import_quiz.py data/input/az-104.csv -n 3

# Take any variation
python run_quiz.py data/quizzes/az-104/az-104_20260209_164742_1.json
```

### Example 3: Custom Configuration

```bash
# Generate shorter quiz (15 questions) with custom ID
python import_quiz.py data/input/chapter1.csv -m 15 --prefix chapter1

# Run with 70% pass threshold and save report
python run_quiz.py data/quizzes/chapter1_*.json -t 70 -r reports/
```

### Example Session

```
$ python run_quiz.py data/quizzes/quiz_001.json

============================================================
                        QUIZ RUNNER
============================================================

Quiz ID: quiz_001
Questions: 25
Pass threshold: 80.0%

Instructions:
  - For multiple answers, separate with commas (e.g., 'a, b, c')
  - Answers are case-insensitive
  - Whitespace is ignored

Press Ctrl+C to quit at any time.

Press Enter to start...

Question 1/25: What is the capital of France?
Your answer: paris
Correct!

Question 2/25: List primary colors
Your answer: red, blue, yellow
Correct!

[... continues for all questions ...]

============================================================
                      QUIZ COMPLETE
============================================================

Total Questions:     25
Correct Answers:     21
Incorrect Answers:   4
Time Spent:          3m 45s

Score:               21/25 (84.0%)
Result:              PASS

Failed Questions (4):
------------------------------------------------------------

Q5: Who wrote Romeo and Juliet?
  Your answer: Shakespeare
  Correct answer: William Shakespeare

[... other failures ...]

============================================================
```

## Development

### Code Quality

This project follows **Clean Code Principles** with:
- ✅ **Centralized constants** - No magic numbers or strings
- ✅ **Type hints** - Complete type safety throughout
- ✅ **Short, focused functions** - Single responsibility principle
- ✅ **Automated formatting** - Black, isort for consistency
- ✅ **Comprehensive linting** - Ruff for code quality
- ✅ **241 passing tests** - High test coverage
- ✅ **Clear documentation** - "Why" not "what" comments

See [REFACTORING.md](REFACTORING.md) for detailed explanation of refactoring changes.

**Run Quality Checks:**
```bash
# Format code
black .
isort . --profile black

# Lint code
ruff check . --fix

# Run tests
pytest tests/ -v

# Type check (if mypy installed)
mypy .
```

### Project Structure

```
quizzer/
├── import_quiz.py          # Main script: CSV → JSON converter
├── run_quiz.py             # Main script: CLI quiz runner
├── web_quiz.py             # Main script: Web interface server (Flask)
├── quizzer/                # Helper package
│   ├── __init__.py         # Public API exports
│   ├── constants.py        # Centralized configuration (NEW!)
│   ├── normalizer.py       # Answer normalization logic
│   └── quiz_data.py        # Data models (Quiz, Question, QuizResult)
├── tests/                  # Test suite (241 tests)
│   └── (test files)
├── data/
│   ├── input/              # CSV source files go here
│   │   ├── README.md
│   │   └── az-104.csv
│   ├── quizzes/            # Generated quiz JSON files
│   │   ├── az-104/         # Quiz variations by source
│   │   └── README.md
│   ├── reports/            # Auto-generated HTML reports
│   │   └── README.md
│   └── README.md
├── logs/                   # Web server logs (auto-created)
│   └── README.md
├── examples/
│   └── sample_questions.csv  # Demo file with 25 basic questions
├── .github/
│   ├── workflows/          # CI/CD pipelines
│   │   ├── ci.yml          # Main CI pipeline
│   │   ├── pr-comment.yml  # PR test result comments
│   │   └── README.md
│   └── copilot-instructions.md  # AI agent guidelines
├── REFACTORING.md          # Clean code principles documentation
├── requirements.txt
├── LICENSE
└── README.md
```

### CI/CD Pipeline

This project uses GitHub Actions for continuous integration:

Automated checks on pull requests:
- Test suite across Python 3.10-3.13
- Code coverage reporting
- Code formatting (Black, isort)
- Static analysis (Flake8, Pylint, MyPy)
- Security scanning (Bandit)
- Automated PR comments with results

See [.github/workflows/README.md](.github/workflows/README.md) for details.

### Key Modules

#### `normalizer.py`
Handles answer normalization for comparison:
- Removes whitespace
- Converts to lowercase
- Splits multi-part answers
- Sorts alphabetically

#### `quiz_data.py`
Defines data structures:
- `Question`: Individual quiz question
- `Quiz`: Complete quiz with metadata
- `QuizResult`: Quiz attempt results

#### `import_quiz.py`
CSV import and quiz generation:
- Parses CSV files
- Validates format
- Randomizes questions
- Generates JSON files

#### `run_quiz.py`
Interactive CLI quiz runner:
- Loads quiz JSON
- Presents questions
- Validates answers
- Generates reports

#### `web_quiz.py`
Web interface server:
- Flask-based REST API
- Serves embedded HTML/CSS/JavaScript
- Real-time quiz taking
- Dashboard with analytics
- Error logging
- HTML report generation

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=quizzer --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_normalizer.py -v
```

Test Results: 57 tests passing with 100% coverage on core modules.

See [tests/README.md](tests/README.md) for detailed testing documentation.

### Contributing

Contributions are welcome! Priority areas for enhancement:

- [ ] Question explanations (3rd CSV column)
- [ ] Review mode with immediate feedback
- [ ] Question categories/tags
- [ ] Per-question time tracking
- [ ] Historical performance graphs
- [ ] Multiple quiz modes (practice vs. exam)
- [ ] Answer variants (accept synonyms)
- [ ] Spaced repetition algorithm
- [ ] Progressive Web App (PWA)
- [ ] Multi-user authentication

**Completed:**
- [x] Web-based UI with Flask
- [x] Dashboard with analytics
- [x] Dark mode support
- [x] Comprehensive error logging
- [x] Responsive design

## License

Copyright 2026 Quizzer Project

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

## Support

For issues, questions, or contributions:
- File an issue on GitHub
- Review [.github/copilot-instructions.md](.github/copilot-instructions.md) for development guidelines
