"""
Answer normalization module for quiz validation.

This module provides utilities for normalizing quiz answers to enable
consistent comparison between user inputs and stored correct answers.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

from typing import List


def normalize_answer(answer: str) -> List[str]:
    """
    Normalize an answer string for comparison.
    
    Normalization steps:
    1. Strip leading/trailing whitespace
    2. Convert to lowercase
    3. Split by comma for multi-part answers
    4. Remove whitespace from each part
    5. Sort parts alphabetically
    6. Filter out empty strings
    
    Args:
        answer: Raw answer string (e.g., "Red, Blue, Yellow" or "Paris")
    
    Returns:
        Sorted list of normalized answer parts (e.g., ["blue", "red", "yellow"])
    
    Examples:
        >>> normalize_answer("Paris")
        ['paris']
        
        >>> normalize_answer("Red, Blue, Yellow")
        ['blue', 'red', 'yellow']
        
        >>> normalize_answer("  washington ,  george  ")
        ['george', 'washington']
        
        >>> normalize_answer("a, b, , c")
        ['a', 'b', 'c']
    """
    if not answer:
        return []
    
    # Split by comma and normalize each part
    parts = [part.strip().lower() for part in answer.split(',')]
    
    # Filter out empty strings and sort
    normalized = sorted([part for part in parts if part])
    
    return normalized


def answers_match(user_answer: str, correct_answer: str) -> bool:
    """
    Check if a user's answer matches the correct answer.
    
    Both answers are normalized before comparison, making the check
    case-insensitive and whitespace-tolerant.
    
    Args:
        user_answer: The answer provided by the user
        correct_answer: The stored correct answer
    
    Returns:
        True if normalized answers match, False otherwise
    
    Examples:
        >>> answers_match("Paris", "paris")
        True
        
        >>> answers_match("red, blue, yellow", "Yellow, Red, Blue")
        True
        
        >>> answers_match("London", "Paris")
        False
    """
    return normalize_answer(user_answer) == normalize_answer(correct_answer)


def format_answer_display(answer: str) -> str:
    """
    Format an answer for display purposes.
    
    Removes extra whitespace but preserves capitalization and comma separation.
    
    Args:
        answer: Raw answer string
    
    Returns:
        Cleaned answer string for display
    
    Examples:
        >>> format_answer_display("  Paris  ")
        'Paris'
        
        >>> format_answer_display("Red,  Blue  , Yellow")
        'Red, Blue, Yellow'
    """
    if not answer:
        return ""
    
    # Split by comma, strip each part, rejoin with consistent formatting
    parts = [part.strip() for part in answer.split(',') if part.strip()]
    return ', '.join(parts)
