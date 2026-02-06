"""
Quizzer Package - Quiz generation and validation utilities.

This package provides helper modules for the Quizzer CLI tool:
- normalizer: Answer normalization and validation
- quiz_data: Data models for quizzes, questions, and results

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

__version__ = "1.0.0"
__author__ = "Quizzer Project"

from .normalizer import normalize_answer, answers_match, format_answer_display
from .quiz_data import Question, Quiz, QuizResult

__all__ = [
    'normalize_answer',
    'answers_match', 
    'format_answer_display',
    'Question',
    'Quiz',
    'QuizResult'
]
