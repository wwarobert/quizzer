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


class TestNormalizeAnswerEdgeCases:
    """Additional edge case tests for normalize_answer."""
    
    def test_unicode_characters(self):
        """Test normalization with Unicode characters."""
        assert normalize_answer("café") == ["café"]
        assert normalize_answer("naïve") == ["naïve"]
        assert normalize_answer("Zürich") == ["zürich"]
        assert normalize_answer("北京") == ["北京"]
    
    def test_numbers_with_decimals(self):
        """Test normalization of decimal numbers."""
        assert normalize_answer("3.14159") == ["3.14159"]
        assert normalize_answer("1.5, 2.5, 3.5") == ["1.5", "2.5", "3.5"]
    
    def test_negative_numbers(self):
        """Test normalization of negative numbers."""
        assert normalize_answer("-5") == ["-5"]
        assert normalize_answer("-1, -2, -3") == ["-1", "-2", "-3"]
    
    def test_answers_with_apostrophes(self):
        """Test normalization with apostrophes."""
        assert normalize_answer("O'Brien") == ["o'brien"]
        assert normalize_answer("don't, can't") == ["can't", "don't"]
    
    def test_answers_with_hyphens(self):
        """Test normalization with hyphens."""
        assert normalize_answer("forty-two") == ["forty-two"]
        assert normalize_answer("well-known, up-to-date") == ["up-to-date", "well-known"]
    
    def test_answers_with_parentheses(self):
        """Test normalization with parentheses."""
        assert normalize_answer("(optional)") == ["(optional)"]
        assert normalize_answer("test (1), test (2)") == ["test (1)", "test (2)"]
    
    def test_very_long_answer_list(self):
        """Test normalization with many items."""
        items = ", ".join([f"item{i}" for i in range(100)])
        result = normalize_answer(items)
        assert len(result) == 100
        assert result == sorted([f"item{i}" for i in range(100)])
    
    def test_mixed_case_sorting(self):
        """Test that sorting is case-insensitive."""
        # After lowercasing, should sort properly
        result = normalize_answer("Zebra, apple, Banana")
        assert result == ["apple", "banana", "zebra"]
    
    def test_numeric_string_sorting(self):
        """Test sorting of numeric strings."""
        result = normalize_answer("10, 2, 30, 1")
        # String sorting, not numeric
        assert result == ["1", "10", "2", "30"]
    
    def test_empty_commas_consecutive(self):
        """Test multiple consecutive commas."""
        assert normalize_answer("a,,,,,b") == ["a", "b"]
        assert normalize_answer("a, , , , b") == ["a", "b"]
    
    def test_commas_at_edges(self):
        """Test commas at start and end."""
        assert normalize_answer(",a,b,") == ["a", "b"]
        assert normalize_answer("  ,  a  ,  b  ,  ") == ["a", "b"]
    
    def test_only_commas(self):
        """Test input with only commas."""
        assert normalize_answer(",,,") == []
        assert normalize_answer(", , ,") == []
    
    def test_tabs_and_newlines(self):
        """Test normalization handles tabs and newlines."""
        assert normalize_answer("a\tb") == ["a\tb"]  # Tab preserved within
        assert normalize_answer("  a\t  ") == ["a"]  # Outer whitespace stripped
        assert normalize_answer("a\nb") == ["a\nb"]  # Newline preserved within


class TestAnswersMatchEdgeCases:
    """Additional edge case tests for answers_match."""
    
    def test_match_with_unicode(self):
        """Test matching with Unicode characters."""
        assert answers_match("café", "CAFÉ") is True
        assert answers_match("Zürich", "zürich") is True
    
    def test_match_with_numbers(self):
        """Test matching with numeric answers."""
        assert answers_match("42", "42") is True
        assert answers_match("3.14", "3.14") is True
        assert answers_match("42", "43") is False
    
    def test_match_preserves_punctuation(self):
        """Test that punctuation is significant."""
        assert answers_match("don't", "dont") is False
        assert answers_match("O'Brien", "obrien") is False
        assert answers_match("don't", "don't") is True
    
    def test_match_extra_commas(self):
        """Test matching ignores extra commas."""
        assert answers_match("a,,,b", "a,b") is True
        assert answers_match("a, , b", "a,b") is True
    
    def test_match_subset_fails(self):
        """Test that subset of answers doesn't match."""
        assert answers_match("a, b", "a, b, c") is False
        assert answers_match("a, b, c", "a, b") is False
    
    def test_match_duplicate_items(self):
        """Test matching with duplicate items in answer."""
        # Duplicates are NOT deduplicated - they remain as separate items
        assert answers_match("a, a, b", "a, b") is False
        assert answers_match("a, a, b", "a, a, b") is True
        assert answers_match("red, red, blue", "red, blue") is False
    
    def test_match_with_very_long_lists(self):
        """Test matching with very long answer lists."""
        items1 = ", ".join([f"item{i}" for i in range(50)])
        items2 = ", ".join([f"item{i}" for i in range(49, -1, -1)])  # Reverse order
        assert answers_match(items1, items2) is True


class TestFormatAnswerDisplayEdgeCases:
    """Additional edge case tests for format_answer_display."""
    
    def test_format_with_unicode(self):
        """Test formatting preserves Unicode."""
        assert format_answer_display("café") == "café"
        assert format_answer_display("北京, 上海") == "北京, 上海"
    
    def test_format_with_numbers(self):
        """Test formatting with numbers."""
        assert format_answer_display("1, 2, 3") == "1, 2, 3"
        assert format_answer_display("3.14") == "3.14"
    
    def test_format_preserves_special_chars(self):
        """Test formatting preserves special characters."""
        assert format_answer_display("O'Brien") == "O'Brien"
        assert format_answer_display("test-case") == "test-case"
        assert format_answer_display("(optional)") == "(optional)"
    
    def test_format_with_mixed_spacing(self):
        """Test formatting normalizes various spacing."""
        assert format_answer_display("a,b,c") == "a, b, c"
        assert format_answer_display("a ,b ,c") == "a, b, c"
        assert format_answer_display("a,  b  ,  c") == "a, b, c"
    
    def test_format_empty_parts(self):
        """Test formatting removes empty parts."""
        assert format_answer_display("a, , b") == "a, b"
        assert format_answer_display("a,,,b") == "a, b"
        assert format_answer_display(",a,b,") == "a, b"
    
    def test_format_only_whitespace(self):
        """Test formatting with only whitespace."""
        assert format_answer_display("   ") == ""
        assert format_answer_display("\t\n") == ""
    
    def test_format_tabs_treated_as_whitespace(self):
        """Test that tabs are treated as whitespace."""
        assert format_answer_display("\ta\t") == "a"
        assert format_answer_display("a\t,\tb") == "a, b"
