"""
Security tests for path validation and sanitization.

Tests to ensure path traversal attacks and other security vulnerabilities
are properly prevented.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import pytest
from pathlib import Path

from quizzer.exceptions import InvalidQuizPathError
from quizzer.security import validate_quiz_path, validate_report_path


class TestValidateQuizPath:
    """Test suite for validate_quiz_path() function."""

    @pytest.fixture
    def allowed_dir(self, tmp_path):
        """Create a temporary allowed directory for testing."""
        quiz_dir = tmp_path / "quizzes"
        quiz_dir.mkdir()
        return quiz_dir

    def test_valid_relative_path(self, allowed_dir):
        """Test that valid relative paths are accepted."""
        result = validate_quiz_path("quiz.json", allowed_dir)
        assert result == allowed_dir / "quiz.json"
        assert result.is_absolute()

    def test_valid_path_with_subdirectory(self, allowed_dir):
        """Test that valid paths with subdirectories are accepted."""
        result = validate_quiz_path("subfolder/quiz.json", allowed_dir)
        assert result == allowed_dir / "subfolder" / "quiz.json"
        assert result.is_absolute()

    def test_valid_absolute_path_within_allowed(self, allowed_dir):
        """Test that absolute paths within allowed directory are accepted."""
        abs_path = allowed_dir / "quiz.json"
        result = validate_quiz_path(str(abs_path), allowed_dir)
        assert result == abs_path

    def test_path_traversal_double_dot(self, allowed_dir):
        """Test that paths with '..' are rejected (directory traversal)."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_quiz_path("../quiz.json", allowed_dir)
        assert "path traversal" in str(exc_info.value).lower()

    def test_path_traversal_in_middle(self, allowed_dir):
        """Test that '..' in the middle of path is rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_quiz_path("folder/../quiz.json", allowed_dir)
        assert "path traversal" in str(exc_info.value).lower()

    def test_path_traversal_multiple_levels(self, allowed_dir):
        """Test that multiple '..' components are rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_quiz_path("../../etc/passwd", allowed_dir)
        assert "path traversal" in str(exc_info.value).lower()

    def test_absolute_path_outside_allowed(self, allowed_dir, tmp_path):
        """Test that absolute paths outside allowed directory are rejected."""
        outside_path = tmp_path / "outside" / "quiz.json"
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_quiz_path(str(outside_path), allowed_dir)
        assert "outside allowed directory" in str(exc_info.value).lower()

    def test_invalid_extension(self, allowed_dir):
        """Test that non-JSON files are rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_quiz_path("quiz.txt", allowed_dir)
        assert "invalid file extension" in str(exc_info.value).lower()

    def test_no_extension(self, allowed_dir):
        """Test that files without extension are rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_quiz_path("quiz", allowed_dir)
        assert "invalid file extension" in str(exc_info.value).lower()

    def test_empty_path(self, allowed_dir):
        """Test that empty path is rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_quiz_path("", allowed_dir)
        assert "cannot be empty" in str(exc_info.value).lower()

    def test_none_path(self, allowed_dir):
        """Test that None path is rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_quiz_path(None, allowed_dir)
        assert "cannot be empty" in str(exc_info.value).lower()

    def test_path_object_input(self, allowed_dir):
        """Test that Path objects are accepted as input."""
        result = validate_quiz_path(Path("quiz.json"), allowed_dir)
        assert result == allowed_dir / "quiz.json"

    def test_case_insensitive_extension(self, allowed_dir):
        """Test that .JSON extension (uppercase) is accepted."""
        result = validate_quiz_path("quiz.JSON", allowed_dir)
        assert result == allowed_dir / "quiz.JSON"

    def test_deep_subdirectory_path(self, allowed_dir):
        """Test that deeply nested valid paths are accepted."""
        result = validate_quiz_path("a/b/c/d/quiz.json", allowed_dir)
        assert result == allowed_dir / "a" / "b" / "c" / "d" / "quiz.json"

    def test_path_with_spaces(self, allowed_dir):
        """Test that paths with spaces are handled correctly."""
        result = validate_quiz_path("my quiz.json", allowed_dir)
        assert result == allowed_dir / "my quiz.json"

    def test_path_with_special_chars(self, allowed_dir):
        """Test that paths with allowed special characters work."""
        result = validate_quiz_path("quiz-001_v2.json", allowed_dir)
        assert result == allowed_dir / "quiz-001_v2.json"


class TestValidateReportPath:
    """Test suite for validate_report_path() function."""

    def test_valid_quiz_id(self):
        """Test that valid quiz IDs are accepted."""
        result = validate_report_path("quiz_001")
        assert result == "quiz_001"

    def test_valid_quiz_id_with_numbers(self):
        """Test quiz IDs with numbers and underscores."""
        result = validate_report_path("quiz_2026_001")
        assert result == "quiz_2026_001"

    def test_valid_quiz_id_with_hyphens(self):
        """Test quiz IDs with hyphens."""
        result = validate_report_path("quiz-001-test")
        assert result == "quiz-001-test"

    def test_path_separator_forward_slash(self):
        """Test that forward slashes are rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_report_path("../quiz")
        assert "cannot contain" in str(exc_info.value).lower()

    def test_path_separator_backslash(self):
        """Test that backslashes are rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_report_path("folder\\quiz")
        assert "cannot contain" in str(exc_info.value).lower()

    def test_parent_directory_reference(self):
        """Test that '..' is rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_report_path("..")
        assert "cannot contain '..'" in str(exc_info.value).lower()

    def test_empty_quiz_id(self):
        """Test that empty quiz ID is rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_report_path("")
        assert "cannot be empty" in str(exc_info.value).lower()

    def test_none_quiz_id(self):
        """Test that None quiz ID is rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_report_path(None)
        assert "cannot be empty" in str(exc_info.value).lower()

    def test_suspicious_char_less_than(self):
        """Test that '<' character is rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_report_path("quiz<001")
        assert "invalid characters" in str(exc_info.value).lower()

    def test_suspicious_char_greater_than(self):
        """Test that '>' character is rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_report_path("quiz>001")
        assert "invalid characters" in str(exc_info.value).lower()

    def test_suspicious_char_pipe(self):
        """Test that '|' character is rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_report_path("quiz|001")
        assert "invalid characters" in str(exc_info.value).lower()

    def test_suspicious_char_asterisk(self):
        """Test that '*' character is rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_report_path("quiz*001")
        assert "invalid characters" in str(exc_info.value).lower()

    def test_suspicious_char_question_mark(self):
        """Test that '?' character is rejected."""
        with pytest.raises(InvalidQuizPathError) as exc_info:
            validate_report_path("quiz?001")
        assert "invalid characters" in str(exc_info.value).lower()


class TestSecurityIntegration:
    """Integration tests for security features."""

    def test_common_attack_vectors(self, tmp_path):
        """Test common path traversal attack patterns."""
        allowed_dir = tmp_path / "quizzes"
        allowed_dir.mkdir()

        attack_vectors = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/passwd",
            "C:\\Windows\\System32",
            "quiz/../../../etc/passwd",
            "./../../quiz.json",
        ]

        for attack in attack_vectors:
            with pytest.raises(InvalidQuizPathError):
                validate_quiz_path(attack, allowed_dir)

    def test_url_encoded_traversal(self, tmp_path):
        """Test that URL-encoded path traversal attempts are handled."""
        allowed_dir = tmp_path / "quizzes"
        allowed_dir.mkdir()

        # Even if someone tries to URL-encode .., the Path object will decode it
        # But the '..' check will still catch it
        with pytest.raises(InvalidQuizPathError):
            validate_quiz_path("..%2F..%2Fetc%2Fpasswd", allowed_dir)
