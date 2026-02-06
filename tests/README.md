# Tests

This directory contains comprehensive tests for the Quizzer project.

## Test Structure

```
tests/
├── conftest.py              # Shared test configuration
├── test_normalizer.py       # Tests for answer normalization
├── test_quiz_data.py        # Tests for data models
├── test_import_quiz.py      # Tests for CSV import script
└── test_run_quiz.py         # Tests for quiz runner script
```

## Running Tests

### Run all tests
```bash
python -m pytest tests/ -v
```

### Run specific test file
```bash
python -m pytest tests/test_normalizer.py -v
```

### Run with coverage report
```bash
python -m pytest tests/ --cov=quizzer --cov=import_quiz --cov=run_quiz --cov-report=term-missing
```

### Run specific test class or function
```bash
python -m pytest tests/test_normalizer.py::TestNormalizeAnswer -v
python -m pytest tests/test_normalizer.py::TestNormalizeAnswer::test_single_answer -v
```

## Test Coverage

Current test coverage (57 tests total):

| Module | Tests | Coverage |
|--------|-------|----------|
| `normalizer.py` | 22 | 100% |
| `quiz_data.py` | 13 | 100% |
| `import_quiz.py` | 13 | 54%* |
| `run_quiz.py` | 8 | 61%* |

*Lower coverage for main scripts is expected as they include CLI argument parsing and user interaction code that's difficult to test in unit tests.

## Test Categories

### Unit Tests

**`test_normalizer.py`** - Answer normalization logic
- Single and multiple answer normalization
- Case insensitivity
- Whitespace handling
- Sorting and comparison
- Edge cases (empty strings, special characters)

**`test_quiz_data.py`** - Data models and serialization
- Question, Quiz, and QuizResult creation
- Dictionary conversion (to_dict/from_dict)
- JSON file save/load
- Report generation

### Integration Tests

**`test_import_quiz.py`** - CSV import workflow
- CSV reading and validation
- Quiz generation
- Randomization
- Full import workflow

**`test_run_quiz.py`** - Quiz running workflow
- Interactive quiz execution
- Answer validation
- Result calculation
- Display and reporting

## Requirements

```bash
pip install pytest pytest-cov
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

## Continuous Integration

Tests are designed to be run in CI/CD pipelines. Exit code 0 indicates all tests passed.

```bash
# CI-friendly command
python -m pytest tests/ --tb=short --strict-markers
```

## Adding New Tests

When adding new functionality:

1. Create tests in the appropriate test file
2. Use descriptive test names (e.g., `test_normalize_answer_with_commas`)
3. Include docstrings explaining what the test validates
4. Test edge cases and error conditions
5. Run tests locally before committing

Example:
```python
def test_new_feature(self):
    """Test description of what this validates."""
    # Arrange
    input_data = "test"
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```
