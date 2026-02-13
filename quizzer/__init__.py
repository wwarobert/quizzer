"""
Quizzer Package - Quiz generation and validation utilities.

This package provides helper modules for the Quizzer CLI tool:
- normalizer: Answer normalization and validation
- quiz_data: Data models for quizzes, questions, and results
- constants: Application-wide configuration values

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

from pathlib import Path
from typing import Union

__version__ = "1.0.0"
__author__ = "Quizzer Project"

from .constants import TEST_DATA_PATTERNS
from .normalizer import answers_match, format_answer_display, normalize_answer
from .quiz_data import Question, Quiz, QuizResult

# Note: Final __all__ definition is at the end of the file after is_test_data()

# Backward compatibility - keep TEST_DATA_PATTERNS at module level
TEST_DATA_PATTERNS = TEST_DATA_PATTERNS


def is_test_data(path: Union[str, Path]) -> bool:
    """
    Check if path contains test/sample data markers.

    This function identifies test, sample, or demo data by checking if the
    immediate folder name (not the full path) contains any of the predefined
    test data patterns (case-insensitive).

    Args:
        path: File or folder path to check (str or Path object)

    Returns:
        True if the immediate folder name matches test data patterns, False otherwise

    Examples:
        >>> is_test_data(Path('data/quizzes/sample_questions'))
        True
        >>> is_test_data(Path('data/quizzes/az-104'))
        False
        >>> is_test_data('data/test_folder/quiz.json')
        True
        >>> is_test_data('data/my_test_folder/prod/quiz.json')  # Only checks 'prod'
        False
    """
    # Get the immediate folder/file name, not the full path
    path_obj = Path(path) if isinstance(path, str) else path
    name = path_obj.name.lower()
    return any(pattern in name for pattern in TEST_DATA_PATTERNS)


__all__ = [
    "normalize_answer",
    "answers_match",
    "format_answer_display",
    "Question",
    "Quiz",
    "QuizResult",
    "is_test_data",
    "TEST_DATA_PATTERNS",
]
