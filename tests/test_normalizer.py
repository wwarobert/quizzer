"""
Unit tests for normalizer module.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import pytest
from quizzer.normalizer import normalize_answer, answers_match, format_answer_display


class TestNormalizeAnswer:
    """Tests for normalize_answer function."""
    
    def test_single_answer(self):
        """Test normalization of single answer."""
        assert normalize_answer("Paris") == ["paris"]
        assert normalize_answer("LONDON") == ["london"]
        assert normalize_answer("New York") == ["new york"]
    
    def test_multiple_answers(self):
        """Test normalization of comma-separated answers."""
        result = normalize_answer("red, blue, yellow")
        assert result == ["blue", "red", "yellow"]  # Sorted alphabetically
    
    def test_whitespace_removal(self):
        """Test that whitespace is properly removed."""
        assert normalize_answer("  Paris  ") == ["paris"]
        assert normalize_answer("red,  blue  , yellow") == ["blue", "red", "yellow"]
    
    def test_case_insensitive(self):
        """Test that answers are converted to lowercase."""
        assert normalize_answer("PARIS") == ["paris"]
        assert normalize_answer("PaRiS") == ["paris"]
    
    def test_sorting(self):
        """Test that multiple answers are sorted alphabetically."""
        assert normalize_answer("zebra, apple, banana") == ["apple", "banana", "zebra"]
        assert normalize_answer("3, 1, 2") == ["1", "2", "3"]
    
    def test_empty_string(self):
        """Test handling of empty strings."""
        assert normalize_answer("") == []
        assert normalize_answer("   ") == []
    
    def test_empty_parts_filtered(self):
        """Test that empty parts from multiple commas are filtered out."""
        assert normalize_answer("red,, blue") == ["blue", "red"]
        assert normalize_answer("red, , blue") == ["blue", "red"]
    
    def test_special_characters(self):
        """Test handling of special characters."""
        assert normalize_answer("O'Brien") == ["o'brien"]
        assert normalize_answer("file.txt") == ["file.txt"]
    
    def test_numbers(self):
        """Test normalization of numeric answers."""
        assert normalize_answer("42") == ["42"]
        assert normalize_answer("3.14") == ["3.14"]


class TestAnswersMatch:
    """Tests for answers_match function."""
    
    def test_exact_match(self):
        """Test exact matches."""
        assert answers_match("Paris", "Paris") is True
        assert answers_match("London", "London") is True
    
    def test_case_insensitive_match(self):
        """Test case-insensitive matching."""
        assert answers_match("paris", "Paris") is True
        assert answers_match("PARIS", "paris") is True
        assert answers_match("PaRiS", "pArIs") is True
    
    def test_whitespace_tolerant(self):
        """Test whitespace tolerance."""
        assert answers_match("  Paris  ", "Paris") is True
        assert answers_match("Paris", "  Paris  ") is True
    
    def test_multiple_answers_order_independent(self):
        """Test that order doesn't matter for multiple answers."""
        assert answers_match("red, blue, yellow", "yellow, red, blue") is True
        assert answers_match("a, b, c", "c, b, a") is True
    
    def test_multiple_answers_with_whitespace(self):
        """Test multiple answers with various whitespace."""
        assert answers_match("red,blue,yellow", "red, blue, yellow") is True
        assert answers_match("red , blue , yellow", "red,blue,yellow") is True
    
    def test_no_match(self):
        """Test non-matching answers."""
        assert answers_match("Paris", "London") is False
        assert answers_match("red", "blue") is False
    
    def test_partial_match_fails(self):
        """Test that partial matches fail."""
        assert answers_match("red, blue", "red, blue, yellow") is False
        assert answers_match("red", "red, blue") is False
    
    def test_empty_answers(self):
        """Test handling of empty answers."""
        assert answers_match("", "") is True
        assert answers_match("Paris", "") is False
        assert answers_match("", "Paris") is False


class TestFormatAnswerDisplay:
    """Tests for format_answer_display function."""
    
    def test_single_answer(self):
        """Test formatting of single answer."""
        assert format_answer_display("Paris") == "Paris"
        assert format_answer_display("  Paris  ") == "Paris"
    
    def test_multiple_answers(self):
        """Test formatting of multiple answers."""
        assert format_answer_display("red,blue,yellow") == "red, blue, yellow"
        assert format_answer_display("red, blue, yellow") == "red, blue, yellow"
    
    def test_preserves_capitalization(self):
        """Test that capitalization is preserved."""
        assert format_answer_display("Paris") == "Paris"
        assert format_answer_display("LONDON") == "LONDON"
    
    def test_normalizes_spacing(self):
        """Test that spacing is normalized."""
        assert format_answer_display("red,  blue  , yellow") == "red, blue, yellow"
        assert format_answer_display("red ,blue, yellow") == "red, blue, yellow"
    
    def test_empty_string(self):
        """Test handling of empty strings."""
        assert format_answer_display("") == ""
        assert format_answer_display("   ") == ""
    
    def test_removes_empty_parts(self):
        """Test that empty parts are removed."""
        assert format_answer_display("red,, blue") == "red, blue"
        assert format_answer_display("red, , blue") == "red, blue"
