# Quizzer - AI Coding Agent Instructions

## Project Overview
Quiz platform with both CLI and web interfaces that generates randomized quizzes from CSV files with interactive testing and automatic grading.

**Current Status**: Production-ready v1.5 with complete web interface, testing suite (57 tests), and documentation.

## Core Functionality

### Three-Component Architecture
1. **Import Script** (`import_quiz.py`)
   - Input: CSV with 2 columns (Question, Answer)
   - Output: JSON file(s) with randomized question sets in organized subfolders
   - Each quiz contains up to 50 questions randomly selected from the pool
   - Creates subfolder `data/quizzes/<source_name>/` for each CSV file
   - Interactive management of existing quizzes (delete or keep)
   - `--force` flag for non-interactive CI/CD pipelines
   
2. **CLI Quiz Runner** (`run_quiz.py`)
   - Traditional terminal-based quiz interface
   - Interactive CLI that loads a quiz JSON
   - Presents questions one-by-one
   - Collects and validates user answers
   - Generates pass/fail report (80% threshold)
   - Automatically creates HTML report after completion
   - Zero external dependencies (Python standard library only)

3. **Web Interface** (`web_quiz.py`) ✨ NEW
   - Flask-based web server for browser-based quizzes
   - Blue theme (#2563eb) with automatic dark mode
   - Dashboard with performance analytics
   - Interactive 250px sidebar with quiz browser
   - Real-time progress tracking and timer
   - Instant answer feedback with visual cues
   - Overlay notification system (no alert popups)
   - Error logging with rotation
   - Fully responsive design (desktop/tablet/mobile)
   - RESTful API endpoints
   - Requires: Flask >= 3.0.0

### Input Format Specification
**CSV Structure:**
```csv
Question,Answer
"What is the capital of France?","Paris"
"List primary colors","red,blue,yellow"
"Name of first president","George Washington"
```

**Key Requirements:**
- Exactly 2 columns: Question | Answer
- No header row required (or auto-detect)
- Answers may contain multiple values (comma-separated)
- Preserve question order in source for reference

### Data Storage Format
**Use JSON for quiz data:**
```json
{
  "quiz_id": "quiz_001",
  "created_at": "2026-02-06T10:30:00",
  "questions": [
    {
      "id": 1,
      "question": "What is the capital of France?",
      "answer": "paris",
      "original_answer": "Paris"
    }
  ]
}
```

**Normalization Strategy:**
- Store normalized answers (lowercase, no whitespace) for comparison
- Retain original answer for display in failure reports
- Sort multi-part answers alphabetically for consistent comparison

### Answer Validation Logic
**Critical Implementation Details:**
1. Normalize both stored and user answers:
   - Remove ALL whitespace (leading, trailing, internal)
   - Convert to lowercase
   - Split by comma for multi-part answers
   - Sort parts alphabetically
2. Example: "Red, Blue, Yellow" → `["blue", "red", "yellow"]`
3. Compare normalized arrays for equality

### Quiz Runner Behavior
**Interactive Flow:**
```
Question 1/50: What is the capital of France?
Your answer: paris
✓ Correct!

Question 2/50: List primary colors
Your answer: red, blue, yellow
✓ Correct!

--- Quiz Complete ---
Score: 42/50 (84%)
Result: PASS

Failed Questions:
Q15: What is 2+2?
  Your answer: 5
  Correct answer: 4
```

**Requirements:**
- Max 50 questions per quiz
- Clear progress indicator (current/total)
- Accept comma-separated answers with auto-normalization
- Generate detailed failure report with original questions
- **Automatically generate HTML report** after each quiz completion

### Report Generation
**Pass Criteria:** 80% or higher (40/50 questions correct)

**Console Report Format:**
```
Quiz Report - quiz_001
Date: 2026-02-06 10:45:00
Questions: 50
Correct: 42
Score: 84.0%
Result: PASS

Failures (8):
---
Q5: Name the first president
Your answer: washington
Correct answer: George Washington
---
```

**HTML Report Format:**
- **Location**: `data/reports/{quiz_id}_report.html`
- **Features**:
  - Responsive design with gradient backgrounds
  - Color-coded pass/fail status banner
  - Statistics cards (total, correct, failed, percentage)
  - Detailed failure breakdown with question numbers
  - Styling (print-friendly, mobile-responsive)
- **Behavior**: Automatically overwrites previous report for same quiz_id
- **Generation**: Happens after every quiz completion (no flag needed)

**Implementation**:
- `generate_html_report(result, quiz)` in [run_quiz.py](../run_quiz.py) creates HTML string
- `save_html_report(result, quiz)` writes to `data/reports/{quiz_id}_report.html`
- Called automatically in `main()` after quiz completion
- Uses inline CSS for standalone HTML files

## Development Setup

### Technology Stack
- **Language**: Python 3.10+
- **License**: Apache License 2.0
- **Data Format**: JSON for quiz storage
- **Version Control**: Git

### Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Suggested Project Structure
```
quizzer/
├── import_quiz.py          # Main script: CSV → JSON converter
├── run_quiz.py             # Main script: Interactive quiz runner
├── web_quiz.py             # Main script: Web interface server
├── quizzer/                # Helper package
│   ├── __init__.py
│   ├── normalizer.py       # Answer normalization logic
│   └── quiz_data.py        # Data models & validation
├── tests/
│   ├── test_import.py
│   ├── test_runner.py
│   ├── test_normalizer.py
│   ├── test_web_quiz.py
│   └── test_sidebar_dashboard.py
├── data/
│   ├── input/              # Source CSV files
│   ├── quizzes/            # Generated JSON quizzes
│   └── reports/            # Auto-generated HTML reports
├── logs/                   # Web server logs (auto-created)
│   └── README.md
├── examples/
│   └── sample_questions.csv
└── requirements.txt
```

### Key Dependencies
- **Standard library**: `csv`, `json`, `argparse`, `datetime`, `re`
- **Web server**: `Flask >= 3.0.0` (for web interface)
- **Testing**: `pytest` for unit tests
- **Optional**: `rich` or `colorama` for enhanced CLI output
- **Type checking**: `mypy` for type safety

## Implementation Guidelines

### Import Script Features
- Validate CSV has exactly 2 columns
- Randomize question order (use `random.shuffle`)
- Generate unique quiz IDs (timestamp or UUID)
- Support batch generation (multiple quizzes from one CSV)
- **Prompt user to delete existing quizzes before importing to same folder**
  - Detect existing quiz JSON files in output directory
  - Ask user: "Do you want to DELETE these quizzes before importing? (yes/no)"
  - If yes: delete all old quizzes BEFORE creating new ones
  - If no: keep old quizzes and add new ones alongside them
- Handle edge cases: empty answers, special characters

### Quiz Runner Features
- Load quiz from JSON file path
- Track answered questions to prevent duplicates
- Save progress (optional: resume interrupted quizzes)
- Export report as text file
- Support quiet mode (no emoji/color for automation)

### Answer Normalization Module
**Critical function:**
```python
def normalize_answer(answer: str) -> list[str]:
    """Normalize answer for comparison.
    
    Steps:
    1. Strip whitespace
    2. Lowercase
    3. Split by comma
    4. Remove whitespace from each part
    5. Sort alphabetically
    6. Return list
    """
    parts = [p.strip().lower() for p in answer.split(',')]
    return sorted(parts)
```

### Testing Strategy
- Unit test normalization with edge cases:
  - Single answers
  - Multiple comma-separated answers
  - Trailing/leading whitespace
  - Mixed case
  - Empty strings
- Integration test full import → quiz → report flow
- Validate 80% threshold calculation accuracy

## Enhancement Opportunities

### Immediate Improvements
1. **Configurable scoring**: Allow pass threshold other than 80%
2. **Question categories**: Add optional 3rd column for topics
3. **Time limits**: Track time per question or total quiz time
4. **Hint system**: Provide hints after wrong attempts
5. **Multiple quiz modes**: Practice (show correct answer) vs. Exam (no feedback until end)

### Enhancement Opportunities
1. **Statistics tracking**: Historical performance across multiple attempts
2. **Spaced repetition**: Prioritize questions previously answered incorrectly
3. **Export formats**: Markdown, PDF reports (HTML already implemented)
4. **~~Web UI~~**: ✅ **IMPLEMENTED** - Flask web interface with dashboard and analytics
5. **Multi-user support**: Track performance by user ID (web interface ready for this)
6. **Question pools**: Generate unique quizzes from large question banks (>50 questions)
7. **Answer variants**: Accept multiple correct answer phrasings
8. **Partial credit**: Award points for partially correct multi-part answers
9. **Progressive Web App**: Offline mode with service workers
10. **Cloud storage integration**: Multi-device sync

### Data Enhancements
1. **Question metadata**: Difficulty level, source, tags
2. **Answer explanations**: 3rd column with rationale for correct answer
3. **Reference links**: Additional column for further reading
4. **Media support**: Link to images/diagrams for questions

## Development Workflow

### Running the Tool
```bash
# Generate quiz from CSV
pythonCLI quiz
python run_quiz.py data/quizzes/quiz_001.json

# Run with options
python run_quiz.py quiz.json --max-questions 25 --pass-threshold 75

# Start web server (requires Flask)
python web_quiz.py

# Web server with options
python web_quiz.py --port 8080 --debug
python web_quiz.py --host 0.0.0.0  # Network access
# Run with options
python run_quiz.py quiz.json --max-questions 25 --pass-threshold 75
```

### Testing
```bash
pytest tests/ -v
pytest tests/test_normalizer.py  # Test specific module
```

### CI/CD Pipeline

GitHub Actions workflows automatically run on pull requests:
- **Tests**: 57 tests across Python 3.10-3.13
- **Coverage**: Reports coverage with 71% overall (100% on core modules)
- **Code Quality**: Black, isort, flake8, pylint, mypy
- **Security**: Bandit security scanning
- **PR Comments**: Automated test result summaries

See `.github/workflows/` for pipeline configuration.

## Notes for AI Agents
- Focus on robust answer normalization (primary complexity point)
- Keep scripts simple and CLI-focused initially
- Preserve original answers for reporting even after normalization
- Use type hints consistently (`str`, `list[str]`, `dict`)
- Handle file I/O errors gracefully (missing CSV, invalid JSON)
- Apache 2.0 license requires preserving copyright notices in new files
- Main scripts at root level, helpers in `quizzer/` package
