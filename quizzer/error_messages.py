"""
Error message constants for API responses.

This module provides sanitized, user-friendly error messages that don't expose
internal system details. Detailed error information is logged server-side only.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

# Quiz-related errors
QUIZ_NOT_PROVIDED = "No quiz path provided"
QUIZ_INVALID_PATH = "Invalid quiz path"
QUIZ_NOT_FOUND = "Quiz not found"
QUIZ_LOAD_FAILED = "Failed to load quiz"

# Answer checking errors
ANSWER_CHECK_FAILED = "Failed to check answer"

# Report-related errors
REPORT_SAVE_FAILED = "Failed to save report"
REPORT_NOT_FOUND = "Report not found"
REPORT_INVALID_ID = "Invalid quiz ID"
REPORT_LOAD_FAILED = "Failed to load report"

# Quiz list errors
QUIZ_LIST_FAILED = "Failed to fetch quizzes"

# Generic errors
RESOURCE_NOT_FOUND = "Resource not found"
INTERNAL_ERROR = "Internal server error"
UNEXPECTED_ERROR = "An unexpected error occurred"
