"""Tests for API request payload validation.

This module tests that malformed or malicious request payloads are rejected
with appropriate 400 Bad Request errors.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import pytest
from pydantic import ValidationError

from quizzer.web.schemas import (
    CheckAnswerRequest,
    FailureSchema,
    QuizDataSchema,
    ResultDataSchema,
    SaveReportRequest,
)


class TestCheckAnswerRequestValidation:
    """Test validation of /api/check-answer requests."""

    def test_valid_request(self):
        """Valid request should pass validation."""
        data = {"user_answer": "paris", "correct_answer": "Paris"}
        request = CheckAnswerRequest(**data)
        assert request.user_answer == "paris"
        assert request.correct_answer == "Paris"

    def test_missing_user_answer(self):
        """Request without user_answer should fail."""
        data = {"correct_answer": "Paris"}
        with pytest.raises(ValidationError) as exc_info:
            CheckAnswerRequest(**data)
        assert "user_answer" in str(exc_info.value)

    def test_missing_correct_answer(self):
        """Request without correct_answer should fail."""
        data = {"user_answer": "paris"}
        with pytest.raises(ValidationError) as exc_info:
            CheckAnswerRequest(**data)
        assert "correct_answer" in str(exc_info.value)

    def test_empty_user_answer(self):
        """Empty user_answer should fail."""
        data = {"user_answer": "", "correct_answer": "Paris"}
        with pytest.raises(ValidationError):
            CheckAnswerRequest(**data)

    def test_whitespace_only_user_answer(self):
        """Whitespace-only user_answer should fail."""
        data = {"user_answer": "   ", "correct_answer": "Paris"}
        with pytest.raises(ValidationError) as exc_info:
            CheckAnswerRequest(**data)
        assert "whitespace" in str(exc_info.value).lower()

    def test_whitespace_only_correct_answer(self):
        """Whitespace-only correct_answer should fail."""
        data = {"user_answer": "paris", "correct_answer": "   "}
        with pytest.raises(ValidationError) as exc_info:
            CheckAnswerRequest(**data)
        assert "whitespace" in str(exc_info.value).lower()

    def test_answer_too_long(self):
        """Answer exceeding max_length should fail."""
        data = {
            "user_answer": "a" * 10001,  # Exceeds 10000 char limit
            "correct_answer": "Paris",
        }
        with pytest.raises(ValidationError):
            CheckAnswerRequest(**data)

    def test_non_string_answer(self):
        """Non-string answer should fail."""
        data = {"user_answer": 123, "correct_answer": "Paris"}
        with pytest.raises(ValidationError):
            CheckAnswerRequest(**data)

    def test_null_answer(self):
        """Null answer should fail."""
        data = {"user_answer": None, "correct_answer": "Paris"}
        with pytest.raises(ValidationError):
            CheckAnswerRequest(**data)

    def test_extra_fields_allowed(self):
        """Extra fields should be ignored (for forward compatibility)."""
        data = {
            "user_answer": "paris",
            "correct_answer": "Paris",
            "extra_field": "ignored",
        }
        # Should not raise - Pydantic allows extra fields by default
        request = CheckAnswerRequest(**data)
        assert request.user_answer == "paris"


class TestSaveReportRequestValidation:
    """Test validation of /api/save-report requests."""

    def test_valid_request(self):
        """Valid request should pass validation."""
        data = {
            "result": {
                "quiz_id": "test_001",
                "total_questions": 10,
                "correct_count": 8,
                "failures": [],
                "score_percentage": 80.0,
                "passed": True,
                "time_spent": 300,
            },
            "quiz": {
                "quiz_id": "test_001",
                "created_at": "2026-03-13T10:00:00",
                "source_file": "test.csv",
            },
        }
        request = SaveReportRequest(**data)
        assert request.result.quiz_id == "test_001"
        assert request.quiz.quiz_id == "test_001"

    def test_missing_result_field(self):
        """Request without result field should fail."""
        data = {
            "quiz": {
                "quiz_id": "test_001",
                "created_at": "2026-03-13T10:00:00",
            }
        }
        with pytest.raises(ValidationError) as exc_info:
            SaveReportRequest(**data)
        assert "result" in str(exc_info.value)

    def test_missing_quiz_field(self):
        """Request without quiz field should fail."""
        data = {
            "result": {
                "quiz_id": "test_001",
                "total_questions": 10,
                "correct_count": 8,
                "failures": [],
                "score_percentage": 80.0,
                "passed": True,
            }
        }
        with pytest.raises(ValidationError) as exc_info:
            SaveReportRequest(**data)
        assert "quiz" in str(exc_info.value)

    def test_negative_total_questions(self):
        """Negative total_questions should fail."""
        data = {
            "result": {
                "quiz_id": "test_001",
                "total_questions": -1,
                "correct_count": 0,
                "failures": [],
                "score_percentage": 0.0,
                "passed": False,
            },
            "quiz": {"quiz_id": "test_001"},
        }
        with pytest.raises(ValidationError):
            SaveReportRequest(**data)

    def test_zero_total_questions(self):
        """Zero total_questions should fail (must be >= 1)."""
        data = {
            "result": {
                "quiz_id": "test_001",
                "total_questions": 0,
                "correct_count": 0,
                "failures": [],
                "score_percentage": 0.0,
                "passed": False,
            },
            "quiz": {"quiz_id": "test_001"},
        }
        with pytest.raises(ValidationError):
            SaveReportRequest(**data)

    def test_correct_count_exceeds_total(self):
        """correct_count exceeding total_questions should fail."""
        data = {
            "result": {
                "quiz_id": "test_001",
                "total_questions": 10,
                "correct_count": 15,  # More than total!
                "failures": [],
                "score_percentage": 150.0,
                "passed": True,
            },
            "quiz": {"quiz_id": "test_001"},
        }
        with pytest.raises(ValidationError) as exc_info:
            SaveReportRequest(**data)
        assert "correct_count" in str(exc_info.value).lower()

    def test_score_percentage_over_100(self):
        """Score percentage > 100 should fail."""
        data = {
            "result": {
                "quiz_id": "test_001",
                "total_questions": 10,
                "correct_count": 8,
                "failures": [],
                "score_percentage": 120.0,  # Invalid!
                "passed": True,
            },
            "quiz": {"quiz_id": "test_001"},
        }
        with pytest.raises(ValidationError):
            SaveReportRequest(**data)

    def test_negative_score_percentage(self):
        """Negative score percentage should fail."""
        data = {
            "result": {
                "quiz_id": "test_001",
                "total_questions": 10,
                "correct_count": 0,
                "failures": [],
                "score_percentage": -10.0,  # Invalid!
                "passed": False,
            },
            "quiz": {"quiz_id": "test_001"},
        }
        with pytest.raises(ValidationError):
            SaveReportRequest(**data)

    def test_negative_time_spent(self):
        """Negative time_spent should fail."""
        data = {
            "result": {
                "quiz_id": "test_001",
                "total_questions": 10,
                "correct_count": 8,
                "failures": [],
                "score_percentage": 80.0,
                "passed": True,
                "time_spent": -100,  # Invalid!
            },
            "quiz": {"quiz_id": "test_001"},
        }
        with pytest.raises(ValidationError):
            SaveReportRequest(**data)

    def test_empty_quiz_id(self):
        """Empty quiz_id should fail."""
        data = {
            "result": {
                "quiz_id": "",  # Empty!
                "total_questions": 10,
                "correct_count": 8,
                "failures": [],
                "score_percentage": 80.0,
                "passed": True,
            },
            "quiz": {"quiz_id": "test_001"},
        }
        with pytest.raises(ValidationError):
            SaveReportRequest(**data)

    def test_quiz_id_too_long(self):
        """Quiz ID exceeding 255 chars should fail."""
        data = {
            "result": {
                "quiz_id": "a" * 256,  # Too long!
                "total_questions": 10,
                "correct_count": 8,
                "failures": [],
                "score_percentage": 80.0,
                "passed": True,
            },
            "quiz": {"quiz_id": "test_001"},
        }
        with pytest.raises(ValidationError):
            SaveReportRequest(**data)

    def test_extra_fields_rejected(self):
        """Extra fields in SaveReportRequest should be rejected."""
        data = {
            "result": {
                "quiz_id": "test_001",
                "total_questions": 10,
                "correct_count": 8,
                "failures": [],
                "score_percentage": 80.0,
                "passed": True,
            },
            "quiz": {"quiz_id": "test_001"},
            "malicious_field": "should be rejected",  # Not allowed!
        }
        with pytest.raises(ValidationError) as exc_info:
            SaveReportRequest(**data)
        assert "extra" in str(exc_info.value).lower() or "malicious" in str(
            exc_info.value
        )

    def test_valid_failure_schema(self):
        """Valid failure object should pass validation."""
        failure_data = {
            "question": "What is 2+2?",
            "user_answer": "5",
            "correct_answer": "4",
            "question_number": 1,
        }
        failure = FailureSchema(**failure_data)
        assert failure.question == "What is 2+2?"
        assert failure.question_number == 1

    def test_failure_with_negative_question_number(self):
        """Failure with negative question_number should fail."""
        failure_data = {
            "question": "What is 2+2?",
            "user_answer": "5",
            "correct_answer": "4",
            "question_number": -1,  # Invalid!
        }
        with pytest.raises(ValidationError):
            FailureSchema(**failure_data)

    def test_failure_with_zero_question_number(self):
        """Failure with zero question_number should fail (must be >= 1)."""
        failure_data = {
            "question": "What is 2+2?",
            "user_answer": "5",
            "correct_answer": "4",
            "question_number": 0,  # Invalid!
        }
        with pytest.raises(ValidationError):
            FailureSchema(**failure_data)

    def test_failure_with_empty_question(self):
        """Failure with empty question should fail."""
        failure_data = {
            "question": "",  # Empty!
            "user_answer": "5",
            "correct_answer": "4",
            "question_number": 1,
        }
        with pytest.raises(ValidationError):
            FailureSchema(**failure_data)


class TestQuizDataSchema:
    """Test QuizDataSchema validation."""

    def test_valid_quiz_data(self):
        """Valid quiz data should pass."""
        data = {
            "quiz_id": "test_001",
            "created_at": "2026-03-13T10:00:00",
            "source_file": "test.csv",
        }
        quiz_data = QuizDataSchema(**data)
        assert quiz_data.quiz_id == "test_001"

    def test_empty_quiz_id(self):
        """Empty quiz_id should fail."""
        data = {"quiz_id": ""}
        with pytest.raises(ValidationError):
            QuizDataSchema(**data)

    def test_missing_quiz_id(self):
        """Missing quiz_id should fail."""
        data = {"created_at": "2026-03-13T10:00:00"}
        with pytest.raises(ValidationError):
            QuizDataSchema(**data)

    def test_extra_fields_allowed_in_quiz_data(self):
        """Extra fields should be allowed in QuizDataSchema."""
        data = {
            "quiz_id": "test_001",
            "extra_field": "should be allowed",
        }
        # Should not raise - extra='allow' in config
        quiz_data = QuizDataSchema(**data)
        assert quiz_data.quiz_id == "test_001"


class TestResultDataSchema:
    """Test ResultDataSchema validation."""

    def test_valid_result_data(self):
        """Valid result data should pass."""
        data = {
            "quiz_id": "test_001",
            "total_questions": 50,
            "correct_count": 40,
            "failures": [],
            "score_percentage": 80.0,
            "passed": True,
        }
        result = ResultDataSchema(**data)
        assert result.total_questions == 50
        assert result.correct_count == 40

    def test_total_questions_too_large(self):
        """Total questions > 10000 should fail."""
        data = {
            "quiz_id": "test_001",
            "total_questions": 10001,  # Too many!
            "correct_count": 40,
            "failures": [],
            "score_percentage": 80.0,
            "passed": True,
        }
        with pytest.raises(ValidationError):
            ResultDataSchema(**data)
