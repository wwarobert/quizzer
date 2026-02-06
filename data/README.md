# Data Directory

This directory stores quiz-related data files with clear separation between inputs and outputs.

## Structure

```
data/
├── input/              # ← Place your CSV question files here
│   ├── README.md
│   └── sample_questions.csv
├── quizzes/            # ← Generated quiz JSON files stored here
│   └── README.md
└── README.md (this file)
```

## Workflow

### 1. Add CSV Files to `input/`

Place your question CSV files in the `input/` directory:
```
data/input/my_questions.csv
data/input/biology_quiz.csv
data/input/history_exam.csv
```

### 2. Generate Quizzes

Run the import script to convert CSV → JSON:
```bash
python import_quiz.py data/input/my_questions.csv
```

### 3. Quizzes Saved to `quizzes/`

Generated quiz JSON files are automatically saved to `quizzes/`:
```
data/quizzes/quiz_20260206_103045.json
```

### 4. Run Quizzes

Take quizzes from the `quizzes/` directory:
```bash
python run_quiz.py data/quizzes/quiz_20260206_103045.json
```

## Separation Benefits

✅ **Input/Output clarity**: CSV sources separate from generated quizzes  
✅ **Version control**: Easier to track source CSVs vs generated files  
✅ **Organization**: Multiple quiz variations from same CSV stay organized  
✅ **Gitignore ready**: Can exclude `quizzes/*.json` while keeping `input/*.csv`
