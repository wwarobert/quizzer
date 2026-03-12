"""
Security utilities for path validation and sanitization.

This module provides security functions to prevent path traversal attacks
and ensure all file system operations are safe.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

from pathlib import Path
from typing import Union

from quizzer.exceptions import InvalidQuizPathError


def validate_quiz_path(quiz_path: Union[str, Path], allowed_dir: Path) -> Path:
    """
    Validate and sanitize a quiz file path to prevent path traversal attacks.
    
    This function ensures the quiz path:
    - Is within the allowed directory (no directory traversal)
    - Uses .json extension
    - Doesn't contain suspicious characters
    - Can be safely resolved to an absolute path
    
    Args:
        quiz_path: User-provided path to quiz file (relative or absolute)
        allowed_dir: Directory that quiz files must be within
        
    Returns:
        Validated absolute Path object
        
    Raises:
        InvalidQuizPathError: If path is invalid or potentially malicious
        
    Security Considerations:
        - Prevents directory traversal (.., ../, symbolic links)
        - Ensures path stays within allowed_dir
        - Rejects absolute paths that don't start with allowed_dir
        - Validates file extension
        
    Examples:
        >>> allowed = Path("/data/quizzes")
        >>> validate_quiz_path("quiz.json", allowed)
        Path("/data/quizzes/quiz.json")
        
        >>> validate_quiz_path("../etc/passwd", allowed)
        InvalidQuizPathError: Path traversal detected
        
        >>> validate_quiz_path("folder/quiz.json", allowed)
        Path("/data/quizzes/folder/quiz.json")
    """
    if not quiz_path:
        raise InvalidQuizPathError("Quiz path cannot be empty")
    
    # Convert to Path object
    path = Path(quiz_path)
    
    # Reject paths with parent directory components (path traversal attempt)
    if ".." in path.parts:
        raise InvalidQuizPathError(
            "Path traversal detected: path cannot contain '..'"
        )
    
    # Check file extension
    if path.suffix.lower() != ".json":
        raise InvalidQuizPathError(
            f"Invalid file extension: expected '.json', got '{path.suffix}'"
        )
    
    # Resolve to absolute path
    # If path is already absolute, resolve() will keep it absolute
    # If path is relative, we need to make it relative to allowed_dir
    try:
        if path.is_absolute():
            # Absolute path - must be within allowed_dir
            resolved = path.resolve(strict=False)
        else:
            # Relative path - resolve relative to allowed_dir
            resolved = (allowed_dir / path).resolve(strict=False)
    except (ValueError, OSError) as e:
        raise InvalidQuizPathError(f"Cannot resolve path: {e}")
    
    # Ensure resolved path is within allowed_dir
    # resolve() follows symlinks, so this check prevents symlink attacks too
    try:
        resolved.relative_to(allowed_dir.resolve(strict=False))
    except ValueError:
        raise InvalidQuizPathError(
            f"Path is outside allowed directory: {resolved} not in {allowed_dir}"
        )
    
    return resolved


def validate_report_path(quiz_id: str) -> str:
    """
    Validate and sanitize a quiz ID for report file names.
    
    Ensures quiz_id doesn't contain path separators or special characters
    that could cause security issues when used in file names.
    
    Args:
        quiz_id: Quiz identifier to validate
        
    Returns:
        Validated quiz_id
        
    Raises:
        InvalidQuizPathError: If quiz_id contains invalid characters
        
    Examples:
        >>> validate_report_path("quiz_001")
        "quiz_001"
        
        >>> validate_report_path("../etc/passwd")
        InvalidQuizPathError: Invalid quiz ID
    """
    if not quiz_id:
        raise InvalidQuizPathError("Quiz ID cannot be empty")
    
    # Check for path separators (both Unix and Windows)
    if "/" in quiz_id or "\\" in quiz_id:
        raise InvalidQuizPathError(
            "Quiz ID cannot contain path separators (/ or \\)"
        )
    
    # Check for parent directory reference
    if ".." in quiz_id:
        raise InvalidQuizPathError("Quiz ID cannot contain '..'")
    
    # Check for other suspicious characters
    suspicious_chars = ["<", ">", ":", '"', "|", "?", "*"]
    if any(char in quiz_id for char in suspicious_chars):
        raise InvalidQuizPathError(
            f"Quiz ID contains invalid characters: {suspicious_chars}"
        )
    
    return quiz_id
