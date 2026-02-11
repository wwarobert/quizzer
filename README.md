# Quizzer

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-57%20passing-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-71%25-yellow.svg)](tests/)

A command-line tool that generates randomized quizzes from CSV files and provides interactive testing with automatic grading.

## Features

- Simple CSV input format (Question, Answer)
- Randomized question selection and ordering
- Interactive command-line interface
- Smart answer validation (case-insensitive, whitespace-tolerant, multi-answer support)
- Detailed pass/fail reports with incorrect answer breakdown
- Automatic HTML report generation
- Built entirely with Python standard library (zero external dependencies)
- Time tracking for quiz completion

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
- No external dependencies required

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

3. Verify installation:
   ```bash
   python import_quiz.py --help
   python run_quiz.py --help
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

Or use the provided sample:
```bash
# Sample CSV is already in data/input/sample_questions.csv
```

### 2. Generate a quiz

```bash
python import_quiz.py data/input/my_questions.csv
```

Output: `data/quizzes/quiz_YYYYMMDD_HHMMSS.json`

### 3. Take the quiz

```bash
python run_quiz.py data/quizzes/quiz_YYYYMMDD_HHMMSS.json
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
python import_quiz.py data/input/sample_questions.csv
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

#### Managing Existing Quizzes

When importing quizzes into an existing folder (e.g., re-importing the same CSV file), the tool will detect existing quiz files and prompt you to decide whether to keep or delete them:

```
Reading questions from: data/input/az-104.csv
Loaded 200 questions

⚠️  Found 5 existing quiz(zes) in this folder:
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
| `-q, --quiet` | Minimal output mode | `false` |

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
- Professional styling with gradients and responsive design

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

### Sample File

See [data/input/sample_questions.csv](data/input/sample_questions.csv) for a complete example with 25 questions.

## Quiz Format

Quizzes are stored as JSON files with the following structure:

```json
{
  "quiz_id": "quiz_20260206_103045",
  "created_at": "2026-02-06T10:30:45.123456",
  "source_file": "sample_questions.csv",
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
python import_quiz.py data/input/sample_questions.csv

# Output shows: Created quiz 1/1: data\quizzes\quiz_20260206_103045.json

# Take the quiz
python run_quiz.py data/quizzes/quiz_20260206_103045.json
```

### Example 2: Create Multiple Variations

```bash
# Generate 3 different quiz variations from input CSV
python import_quiz.py data/input/sample_questions.csv -n 3

# Take any variation
python run_quiz.py data/quizzes/quiz_20260206_103045.json
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

### Project Structure

```
quizzer/
├── import_quiz.py          # Main script: CSV → JSON converter
├── run_quiz.py             # Main script: Interactive quiz runner
├── quizzer/                # Helper package
│   ├── __init__.py
│   ├── normalizer.py       # Answer normalization logic
│   └── quiz_data.py        # Data models (Quiz, Question, QuizResult)
├── tests/
│   └── (test files)
├── data/
│   ├── input/              # ← CSV source files go here
│   │   ├── README.md
│   │   └── sample_questions.csv
│   ├── quizzes/            # ← Generated quiz JSON files
│   │   └── README.md
│   └── README.md
├── examples/
│   └── sample_questions.csv  # Demo file (also copied to data/input/)
├── .github/
│   ├── workflows/          # CI/CD pipelines
│   │   ├── ci.yml          # Main CI pipeline
│   │   ├── pr-comment.yml  # PR test result comments
│   │   └── README.md
│   └── copilot-instructions.md  # AI agent guidelines
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
Interactive quiz runner:
- Loads quiz JSON
- Presents questions
- Validates answers
- Generates reports

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

Contributions are welcome! Areas for enhancement:

- [ ] Unit tests for all modules
- [ ] Question categories/tags
- [ ] Time tracking per question
- [ ] Historical performance statistics
- [ ] Web-based UI
- [ ] Multiple quiz modes (practice vs. exam)
- [ ] Answer variants (accept synonyms)
- [ ] Spaced repetition algorithm

## License

Copyright 2026 Quizzer Project

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

## Support

For issues, questions, or contributions:
- File an issue on GitHub
- Review [.github/copilot-instructions.md](.github/copilot-instructions.md) for development guidelines
