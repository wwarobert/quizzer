"""
Custom exceptions for Quizzer application.

This module defines a hierarchy of exceptions used throughout the application
to provide specific, actionable error handling and better debugging.

Why custom exceptions:
- More specific error handling (catch specific exceptions, not generic Exception)
- Better error messages for users and logs
- Clear separation between different error types
- Easier to map to HTTP status codes in web interface

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""


# ============================================================================
# Base Exception
# ============================================================================


class QuizzerError(Exception):
    """
    Base exception for all Quizzer-specific errors.

    All custom exceptions in the application inherit from this base class,
    making it easy to catch all application-specific errors with:
        except QuizzerError as e:
            # Handle any Quizzer error
    """

    pass


# ============================================================================
# Quiz Data Exceptions
# ============================================================================


class QuizNotFoundError(QuizzerError):
    """
    Raised when a requested quiz file cannot be found.

    HTTP Status: 404 Not Found

    Examples:
        - Quiz file doesn't exist at specified path
        - Quiz ID doesn't match any existing quiz
        - Quiz folder is empty
    """

    pass


class InvalidQuizPathError(QuizzerError):
    """
    Raised when a quiz path is invalid or potentially malicious.

    HTTP Status: 400 Bad Request

    Examples:
        - Path contains '..' (directory traversal attempt)
        - Path is absolute when relative expected
        - Path points outside allowed directory
        - Path doesn't end in .json extension
        - Path contains invalid characters

    Security Note:
        This exception helps prevent path traversal attacks by rejecting
        suspicious paths before they're processed.
    """

    pass


class InvalidQuizFormatError(QuizzerError):
    """
    Raised when a quiz file has invalid structure or missing required fields.

    HTTP Status: 400 Bad Request

    Examples:
        - JSON is malformed (syntax error)
        - Missing required fields (quiz_id, questions)
        - Invalid data types (questions is not a list)
        - Empty questions array
    """

    pass


# ============================================================================
# Import/Export Exceptions
# ============================================================================


class InvalidCSVFormatError(QuizzerError):
    """
    Raised when a CSV file doesn't match expected format.

    Examples:
        - Wrong number of columns (expected 2 or 3)
        - Empty file
        - Invalid encoding
        - Malformed CSV syntax
    """

    pass


class QuizImportError(QuizzerError):
    """
    Raised when quiz import/generation fails.

    Examples:
        - Unable to write quiz file (permissions)
        - Disk full
        - Invalid source file path
    """

    pass


# ============================================================================
# Report Exceptions
# ============================================================================


class ReportGenerationError(QuizzerError):
    """
    Raised when HTML report generation fails.

    Examples:
        - Unable to write report file
        - Template rendering error
        - Invalid result data
    """

    pass


class ReportNotFoundError(QuizzerError):
    """
    Raised when a requested report file cannot be found.

    HTTP Status: 404 Not Found
    """

    pass


# ============================================================================
# Validation Exceptions
# ============================================================================


class InvalidAnswerError(QuizzerError):
    """
    Raised when an answer fails validation.

    Examples:
        - Answer exceeds maximum length
        - Answer contains invalid characters
        - Answer format doesn't match expected pattern
    """

    pass


class ValidationError(QuizzerError):
    """
    Raised when request data fails validation.

    HTTP Status: 400 Bad Request

    Examples:
        - Missing required field
        - Invalid data type
        - Value out of acceptable range
        - Malformed JSON
    """

    pass


# ============================================================================
# Configuration Exceptions
# ============================================================================


class ConfigurationError(QuizzerError):
    """
    Raised when application configuration is invalid or missing.

    Examples:
        - Required environment variable not set
        - Invalid configuration value
        - Missing config file
    """

    pass


# ============================================================================
# Exception Mapping for HTTP Status Codes
# ============================================================================

# Map exception types to HTTP status codes for API error handling
HTTP_STATUS_MAP = {
    QuizNotFoundError: 404,
    ReportNotFoundError: 404,
    InvalidQuizPathError: 400,
    InvalidQuizFormatError: 400,
    InvalidCSVFormatError: 400,
    InvalidAnswerError: 400,
    ValidationError: 400,
    QuizImportError: 500,
    ReportGenerationError: 500,
    ConfigurationError: 500,
    QuizzerError: 500,  # Generic fallback
}


def get_http_status(exception: Exception) -> int:
    """
    Get appropriate HTTP status code for an exception.

    Args:
        exception: The exception to map

    Returns:
        HTTP status code (400, 404, 500, etc.)

    Examples:
        >>> get_http_status(QuizNotFoundError("Quiz not found"))
        404
        >>> get_http_status(InvalidQuizPathError("Invalid path"))
        400
        >>> get_http_status(ValueError("Some error"))
        500
    """
    return HTTP_STATUS_MAP.get(type(exception), 500)
