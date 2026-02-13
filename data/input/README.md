# Input CSV Files

Place your quiz question CSV files in this directory.

## CSV Format

Your CSV files must have exactly **2 columns**:
1. **Question** - The question text
2. **Answer** - The correct answer (can be comma-separated for multiple answers)

## Example

```csv
Question,Answer
What is the capital of France?,Paris
List primary colors,"red, blue, yellow"
What is 2 + 2?,4
```

## Example File

An example file is provided: [az-104.csv](az-104.csv) - Microsoft Azure Administrator certification practice questions

## Usage

Generate quizzes from CSV files in this directory:

```bash
# Generate quiz from a CSV in this directory
python import_quiz.py data/input/your_questions.csv

# Or use relative path
python import_quiz.py data/input/biology_quiz.csv -n 3
```

Generated quiz JSON files will be saved to: `data/quizzes/`
