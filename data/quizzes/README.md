# Generated Quiz JSON Files

This directory contains quiz JSON files generated from CSV inputs.

## Structure

Quiz files are automatically named with timestamps:
```
quiz_YYYYMMDD_HHMMSS.json
```

Example:
```
quiz_20260206_213833.json
```

## Format

Each quiz JSON contains:
- Unique quiz ID
- Creation timestamp
- Source CSV filename
- Up to 50 randomized questions with normalized answers

## Usage

Run quizzes from this directory:

```bash
# Run a specific quiz
python run_quiz.py data/quizzes/quiz_20260206_213833.json

# Run with wildcards (latest quiz)
python run_quiz.py data/quizzes/quiz_*.json

# Run with custom options
python run_quiz.py data/quizzes/quiz_*.json --pass-threshold 75 --report-output reports/
```

## Automatic Generation

These files are created by:
```bash
python import_quiz.py data/input/your_questions.csv
```

The output directory can be customized:
```bash
python import_quiz.py input.csv -o custom/output/path/
```
