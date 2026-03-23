"""
Answer validation and checking service.

This module provides business logic for answer validation, normalization,
and comparison. Extracted from routes.py to improve testability and reusability.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

from dataclasses import dataclass
from typing import List

from quizzer.normalizer import normalize_answer


@dataclass
class AnswerCheckResult:
    """
    Result of an answer check operation.

    Attributes:
        is_correct: Whether the user's answer matches the correct answer
        user_normalized: Normalized version of user's answer
        correct_normalized: Normalized version of correct answer
        user_raw: Original user answer (before normalization)
        correct_raw: Original correct answer (before normalization)
    """

    is_correct: bool
    user_normalized: List[str]
    correct_normalized: List[str]
    user_raw: str
    correct_raw: str

    def to_dict(self) -> dict:
        """
        Convert result to dictionary format for API responses.

        Returns:
            Dict with correct status and normalized answer parts
        """
        return {
            "correct": self.is_correct,
            "normalized_user": self.user_normalized,
            "normalized_correct": self.correct_normalized,
        }


class AnswerService:
    """
    Service for answer validation and checking.

    This service encapsulates the business logic for:
    - Normalizing user and correct answers
    - Comparing normalized answers
    - Providing detailed check results
    """

    @staticmethod
    def check_answer(user_answer: str, correct_answer: str) -> AnswerCheckResult:
        """
        Check if a user's answer matches the correct answer.

        Both answers are normalized before comparison using the
        normalize_answer function, making the check case-insensitive,
        whitespace-tolerant, and order-independent for multi-part answers.

        Args:
            user_answer: The answer provided by the user
            correct_answer: The stored correct answer

        Returns:
            AnswerCheckResult with comparison details

        Examples:
            >>> result = AnswerService.check_answer("Paris", "paris")
            >>> result.is_correct
            True

            >>> result = AnswerService.check_answer("red, blue", "Blue, Red")
            >>> result.is_correct
            True

            >>> result = AnswerService.check_answer("London", "Paris")
            >>> result.is_correct
            False
        """
        # Normalize both answers
        user_normalized = normalize_answer(user_answer)
        correct_normalized = normalize_answer(correct_answer)

        # Compare normalized versions
        is_correct = user_normalized == correct_normalized

        return AnswerCheckResult(
            is_correct=is_correct,
            user_normalized=user_normalized,
            correct_normalized=correct_normalized,
            user_raw=user_answer,
            correct_raw=correct_answer,
        )

    @staticmethod
    def validate_answer_input(answer: str, max_length: int = 10000) -> tuple[bool, str]:
        """
        Validate that an answer input is acceptable.

        Args:
            answer: The answer string to validate
            max_length: Maximum allowed length (default: 10000)

        Returns:
            Tuple of (is_valid, error_message)
            - (True, "") if valid
            - (False, "error message") if invalid

        Examples:
            >>> AnswerService.validate_answer_input("Paris")
            (True, '')

            >>> AnswerService.validate_answer_input("")
            (False, 'Answer cannot be empty')

            >>> AnswerService.validate_answer_input("   ")
            (False, 'Answer cannot be only whitespace')
        """
        if not answer:
            return False, "Answer cannot be empty"

        if not answer.strip():
            return False, "Answer cannot be only whitespace"

        if len(answer) > max_length:
            return False, f"Answer exceeds maximum length of {max_length} characters"

        return True, ""

    @staticmethod
    def format_for_display(answer: str) -> str:
        """
        Format an answer for display purposes.

        Removes excess whitespace and normalizes comma separation
        while preserving the original case.

        Args:
            answer: Raw answer string

        Returns:
            Formatted answer string

        Examples:
            >>> AnswerService.format_for_display("  Paris  ")
            'Paris'

            >>> AnswerService.format_for_display("Red,  Blue  , Yellow")
            'Red, Blue, Yellow'
        """
        if not answer:
            return ""

        # Split by comma and clean each part
        parts = [part.strip() for part in answer.split(",")]

        # Filter empty parts and join with proper spacing
        cleaned_parts = [part for part in parts if part]

        return ", ".join(cleaned_parts)

    @staticmethod
    def get_answer_statistics(user_answer: str) -> dict:
        """
        Get statistics about an answer for analytics.

        Args:
            user_answer: The answer to analyze

        Returns:
            Dictionary containing answer statistics

        Examples:
            >>> stats = AnswerService.get_answer_statistics("red, blue, yellow")
            >>> stats['length']
            18
            >>> stats['has_comma']
            True
            >>> stats['num_parts']
            3
        """
        normalized = normalize_answer(user_answer)

        return {
            "length": len(user_answer),
            "has_comma": "," in user_answer,
            "num_parts": len(normalized),
            "is_multi_part": len(normalized) > 1,
        }
