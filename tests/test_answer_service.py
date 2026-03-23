"""
Tests for AnswerService.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import pytest

from quizzer.services import AnswerCheckResult, AnswerService


class TestAnswerServiceCheckAnswer:
    """Tests for AnswerService.check_answer() method."""

    def test_exact_match_same_case(self):
        """Test exact match with same case."""
        result = AnswerService.check_answer("Paris", "Paris")
        assert result.is_correct is True
        assert result.user_normalized == ["paris"]
        assert result.correct_normalized == ["paris"]
        assert result.user_raw == "Paris"
        assert result.correct_raw == "Paris"

    def test_exact_match_different_case(self):
        """Test exact match with different case."""
        result = AnswerService.check_answer("PARIS", "paris")
        assert result.is_correct is True
        assert result.user_normalized == ["paris"]
        assert result.correct_normalized == ["paris"]

    def test_match_with_whitespace(self):
        """Test match with leading/trailing whitespace."""
        result = AnswerService.check_answer("  Paris  ", "Paris")
        assert result.is_correct is True

    def test_multi_part_answer_same_order(self):
        """Test multi-part answer with same order."""
        result = AnswerService.check_answer("red, blue, yellow", "red, blue, yellow")
        assert result.is_correct is True
        assert result.user_normalized == ["blue", "red", "yellow"]

    def test_multi_part_answer_different_order(self):
        """Test multi-part answer with different order."""
        result = AnswerService.check_answer("yellow, red, blue", "red, blue, yellow")
        assert result.is_correct is True
        assert result.user_normalized == ["blue", "red", "yellow"]

    def test_multi_part_answer_mixed_case(self):
        """Test multi-part answer with mixed case."""
        result = AnswerService.check_answer("RED, Blue, YELLOW", "red, blue, yellow")
        assert result.is_correct is True

    def test_multi_part_answer_extra_spaces(self):
        """Test multi-part answer with extra spaces."""
        result = AnswerService.check_answer("red ,  blue  , yellow", "red, blue, yellow")
        assert result.is_correct is True

    def test_incorrect_answer(self):
        """Test incorrect single answer."""
        result = AnswerService.check_answer("London", "Paris")
        assert result.is_correct is False
        assert result.user_normalized == ["london"]
        assert result.correct_normalized == ["paris"]

    def test_incorrect_multi_part_answer(self):
        """Test incorrect multi-part answer."""
        result = AnswerService.check_answer("red, green, yellow", "red, blue, yellow")
        assert result.is_correct is False
        assert "green" in result.user_normalized
        assert "blue" in result.correct_normalized

    def test_partial_match_multi_part(self):
        """Test partial match in multi-part answer."""
        result = AnswerService.check_answer("red, blue", "red, blue, yellow")
        assert result.is_correct is False
        assert len(result.user_normalized) == 2
        assert len(result.correct_normalized) == 3

    def test_empty_answer(self):
        """Test empty answer."""
        result = AnswerService.check_answer("", "Paris")
        assert result.is_correct is False
        assert result.user_normalized == []

    def test_both_empty(self):
        """Test both answers empty (edge case)."""
        result = AnswerService.check_answer("", "")
        assert result.is_correct is True
        assert result.user_normalized == []
        assert result.correct_normalized == []

    def test_answer_with_numbers(self):
        """Test answer containing numbers."""
        result = AnswerService.check_answer("42", "42")
        assert result.is_correct is True

    def test_answer_with_special_characters(self):
        """Test answer containing special characters."""
        result = AnswerService.check_answer("C++", "c++")
        assert result.is_correct is True

    def test_result_dataclass_structure(self):
        """Test that result is proper dataclass instance."""
        result = AnswerService.check_answer("Paris", "Paris")
        assert isinstance(result, AnswerCheckResult)
        assert hasattr(result, "is_correct")
        assert hasattr(result, "user_normalized")
        assert hasattr(result, "correct_normalized")
        assert hasattr(result, "user_raw")
        assert hasattr(result, "correct_raw")


class TestAnswerServiceValidateInput:
    """Tests for AnswerService.validate_answer_input() method."""

    def test_valid_simple_answer(self):
        """Test valid simple answer."""
        is_valid, error = AnswerService.validate_answer_input("Paris")
        assert is_valid is True
        assert error == ""

    def test_valid_multi_part_answer(self):
        """Test valid multi-part answer."""
        is_valid, error = AnswerService.validate_answer_input("red, blue, yellow")
        assert is_valid is True
        assert error == ""

    def test_valid_answer_with_spaces(self):
        """Test valid answer with spaces."""
        is_valid, error = AnswerService.validate_answer_input("  Paris  ")
        assert is_valid is True

    def test_empty_answer(self):
        """Test empty answer is invalid."""
        is_valid, error = AnswerService.validate_answer_input("")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_whitespace_only_answer(self):
        """Test whitespace-only answer is invalid."""
        is_valid, error = AnswerService.validate_answer_input("   ")
        assert is_valid is False
        assert "whitespace" in error.lower()

    def test_answer_exceeds_max_length(self):
        """Test answer exceeding max length."""
        long_answer = "a" * 10001
        is_valid, error = AnswerService.validate_answer_input(long_answer, max_length=10000)
        assert is_valid is False
        assert "maximum length" in error.lower()

    def test_answer_at_max_length(self):
        """Test answer exactly at max length."""
        answer = "a" * 100
        is_valid, error = AnswerService.validate_answer_input(answer, max_length=100)
        assert is_valid is True

    def test_custom_max_length(self):
        """Test custom max length parameter."""
        is_valid, error = AnswerService.validate_answer_input("hello", max_length=3)
        assert is_valid is False
        assert "3" in error


class TestAnswerServiceFormatForDisplay:
    """Tests for AnswerService.format_for_display() method."""

    def test_format_simple_answer(self):
        """Test format simple answer."""
        formatted = AnswerService.format_for_display("Paris")
        assert formatted == "Paris"

    def test_format_with_leading_trailing_spaces(self):
        """Test format with leading/trailing spaces."""
        formatted = AnswerService.format_for_display("  Paris  ")
        assert formatted == "Paris"

    def test_format_multi_part_proper_spacing(self):
        """Test format multi-part with proper comma spacing."""
        formatted = AnswerService.format_for_display("red,blue,yellow")
        assert formatted == "red, blue, yellow"

    def test_format_multi_part_extra_spaces(self):
        """Test format multi-part with extra spaces."""
        formatted = AnswerService.format_for_display("red ,  blue  , yellow")
        assert formatted == "red, blue, yellow"

    def test_format_preserves_case(self):
        """Test format preserves original case."""
        formatted = AnswerService.format_for_display("Red, BLUE, Yellow")
        assert formatted == "Red, BLUE, Yellow"

    def test_format_empty_string(self):
        """Test format empty string."""
        formatted = AnswerService.format_for_display("")
        assert formatted == ""

    def test_format_removes_empty_parts(self):
        """Test format removes empty parts between commas."""
        formatted = AnswerService.format_for_display("red, , blue, , yellow")
        assert formatted == "red, blue, yellow"

    def test_format_with_only_commas(self):
        """Test format with only commas."""
        formatted = AnswerService.format_for_display(", , ,")
        assert formatted == ""


class TestAnswerServiceGetStatistics:
    """Tests for AnswerService.get_answer_statistics() method."""

    def test_statistics_simple_answer(self):
        """Test statistics for simple answer."""
        stats = AnswerService.get_answer_statistics("Paris")
        assert stats["length"] == 5
        assert stats["has_comma"] is False
        assert stats["num_parts"] == 1
        assert stats["is_multi_part"] is False

    def test_statistics_multi_part_answer(self):
        """Test statistics for multi-part answer."""
        stats = AnswerService.get_answer_statistics("red, blue, yellow")
        assert stats["length"] == 17
        assert stats["has_comma"] is True
        assert stats["num_parts"] == 3
        assert stats["is_multi_part"] is True

    def test_statistics_two_part_answer(self):
        """Test statistics for two-part answer."""
        stats = AnswerService.get_answer_statistics("red, blue")
        assert stats["num_parts"] == 2
        assert stats["is_multi_part"] is True

    def test_statistics_empty_answer(self):
        """Test statistics for empty answer."""
        stats = AnswerService.get_answer_statistics("")
        assert stats["length"] == 0
        assert stats["has_comma"] is False
        assert stats["num_parts"] == 0
        assert stats["is_multi_part"] is False

    def test_statistics_answer_with_spaces(self):
        """Test statistics includes spaces in length."""
        stats = AnswerService.get_answer_statistics("  Paris  ")
        assert stats["length"] == 9  # Includes leading/trailing spaces

    def test_statistics_comma_without_parts(self):
        """Test statistics for comma but empty parts."""
        stats = AnswerService.get_answer_statistics(", ,")
        assert stats["has_comma"] is True
        assert stats["num_parts"] == 0  # No valid parts after normalization
        assert stats["is_multi_part"] is False


class TestAnswerServiceIntegration:
    """Integration tests for AnswerService."""

    def test_check_then_format_correct_answer(self):
        """Test checking answer then formatting for display."""
        result = AnswerService.check_answer("red, blue, yellow", "Red, Blue, Yellow")
        assert result.is_correct is True

        formatted = AnswerService.format_for_display(result.user_raw)
        assert formatted == "red, blue, yellow"

    def test_check_then_statistics(self):
        """Test checking answer then getting statistics."""
        result = AnswerService.check_answer("red, blue", "red, blue, yellow")
        assert result.is_correct is False

        stats = AnswerService.get_answer_statistics(result.user_raw)
        assert stats["num_parts"] == 2

    def test_validate_then_check(self):
        """Test validating input before checking answer."""
        user_input = "Paris"
        is_valid, _ = AnswerService.validate_answer_input(user_input)
        assert is_valid is True

        result = AnswerService.check_answer(user_input, "Paris")
        assert result.is_correct is True

    def test_workflow_invalid_input(self):
        """Test workflow with invalid input."""
        user_input = ""
        is_valid, error = AnswerService.validate_answer_input(user_input)
        assert is_valid is False
        assert error  # Should have error message

    def test_workflow_incorrect_answer_formatting(self):
        """Test workflow with incorrect answer and formatting."""
        result = AnswerService.check_answer("London", "Paris")
        assert result.is_correct is False

        # Format both for display
        user_display = AnswerService.format_for_display(result.user_raw)
        correct_display = AnswerService.format_for_display(result.correct_raw)

        assert user_display == "London"
        assert correct_display == "Paris"
