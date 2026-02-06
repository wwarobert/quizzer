# Generated Quiz JSON Files

This directory contains quiz JSON files generated from CSV inputs, organized in timestamped subfolders.

## Structure

Each import batch creates a subfolder with timestamp:
```
data/quizzes/
├── 20260206_120000/
│   ├── quiz_20260206_120001.json
│   ├── quiz_20260206_120002.json
│   └── quiz_20260206_120003.json
├── 20260206_150000/
│   ├── quiz_20260206_150001.json
│   └── quiz_20260206_150002.json
└── README.md
```

**Subfolder naming:** `YYYYMMDD_HHMMSS` (timestamp of import)

## Format

Each quiz JSON contains:
- Unique quiz ID
- Creation timestamp
- Source CSV filename
- Up to 50 randomized questions with normalized answers

## Usage

### Run a Random Quiz (Recommended)

```bash
# Automatically selects a random quiz
python run_quiz.py
```

If multiple subfolders exist, you'll be prompted to choose one.

### Run a Specific Quiz

```bash
# Run from specific folder
python run_quiz.py data/quizzes/20260206_120000/quiz_20260206_120001.json

# Run with wildcards (latest quiz)
python run_quiz.py data/quizzes/20260206_*/quiz_*.json

# Run with custom options
python run_quiz.py data/quizzes/20260206_120000/quiz_*.json --pass-threshold 75
```

## Automatic Generation

Quiz subfolders are created automatically by:
```bash
python import_quiz.py data/input/your_questions.csv
```

Each import creates a new timestamped subfolder containing all generated quizzes from that batch.

## Benefits of Subfolder Organization

- **Batch tracking**: Easily identify which quizzes were generated together
- **Version control**: Keep different versions of quizzes from the same source
- **Easy cleanup**: Delete entire batches without affecting others
- **Better organization**: No clutter in the main directory
