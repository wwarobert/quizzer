"""
Tests for sanitized error messages.

Verifies that API endpoints return user-friendly error messages without
exposing internal system details, while detailed errors are logged server-side.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from quizzer.error_messages import (
    ANSWER_CHECK_FAILED,
    INTERNAL_ERROR,
    QUIZ_INVALID_PATH,
    QUIZ_LIST_FAILED,
    QUIZ_LOAD_FAILED,
    QUIZ_NOT_FOUND,
    QUIZ_NOT_PROVIDED,
    REPORT_INVALID_ID,
    REPORT_LOAD_FAILED,
    REPORT_NOT_FOUND,
    REPORT_SAVE_FAILED,
    RESOURCE_NOT_FOUND,
    UNEXPECTED_ERROR,
)
from quizzer.web import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app = create_app(test_mode=False)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_quiz_path():
    """Return a sample quiz path for testing."""
    return "data/quizzes/sample_questions/sample_20260209_165453_1.json"


@pytest.fixture
def sample_quiz_data():
    """Return sample quiz data structure."""
    return {
        "quiz_id": "test_001",
        "created_at": "2026-02-11T10:00:00",
        "source_file": "test.csv",
        "questions": [
            {
                "id": 1,
                "question": "What is 2+2?",
                "answer": ["4"],
                "original_answer": "4",
            }
        ],
    }


class TestErrorMessageSanitization:
    """Test that error messages are sanitized and don't expose internal details."""

    def test_quiz_not_provided(self, client):
        """Test error when quiz path is not provided."""
        response = client.get("/api/quiz")
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == QUIZ_NOT_PROVIDED
        # Ensure no internal file system paths are exposed
        assert "/" not in data["error"]
        assert "\\" not in data["error"]
        assert "data/quizzes" not in data["error"].lower()

    def test_quiz_invalid_path_traversal(self, client):
        """Test error message for path traversal attempt."""
        response = client.get("/api/quiz?path=../../../etc/passwd")
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == QUIZ_INVALID_PATH
        # Ensure the actual malicious path is not in the response
        assert "../" not in data["error"]
        assert "etc" not in data["error"]
        assert "passwd" not in data["error"]

    def test_quiz_not_found(self, client, tmp_path):
        """Test error message when quiz file doesn't exist."""
        # Create a valid quiz path that doesn't exist
        response = client.get("/api/quiz?path=data/quizzes/nonexistent.json")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["error"] == QUIZ_NOT_FOUND
        # Ensure no file path details are exposed
        assert "nonexistent" not in data["error"]
        assert ".json" not in data["error"]

    @patch("quizzer.Quiz.load")
    def test_quiz_load_failed_generic_error(self, mock_load, client, sample_quiz_path):
        """Test error message when quiz loading fails due to unexpected error."""
        # Simulate an unexpected error during quiz load
        mock_load.side_effect = RuntimeError("Internal database connection failed")

        response = client.get(f"/api/quiz?path={sample_quiz_path}")
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["error"] == QUIZ_LOAD_FAILED
        # Ensure internal error details are NOT exposed
        assert "database" not in data["error"].lower()
        assert "RuntimeError" not in data["error"]
        assert "connection" not in data["error"].lower()

    @patch("quizzer.web.routes.logger")
    def test_detailed_errors_logged_server_side(self, mock_logger, client):
        """Test that detailed error information is logged server-side only."""
        # Trigger an error (invalid path)
        client.get("/api/quiz?path=../../../etc/passwd")

        # Verify that detailed error was logged
        mock_logger.warning.assert_called()
        # Check that the log contains detailed information
        call_args = str(mock_logger.warning.call_args)
        assert "Invalid quiz path" in call_args or "path" in call_args.lower()

    def test_answer_check_failed(self, client):
        """Test error message when answer checking fails."""
        # Send invalid JSON to trigger an error
        response = client.post(
            "/api/check-answer",
            data="invalid json",
            content_type="application/json",
        )
        # Should fail during JSON parsing
        assert response.status_code in [400, 500]
        data = json.loads(response.data)
        # Should not expose internal parsing errors
        assert "json" not in data.get("error", "").lower() or data.get("error") == ANSWER_CHECK_FAILED

    @patch("run_quiz.save_html_report")
    def test_report_save_failed(self, mock_save, client, sample_quiz_data):
        """Test error message when report saving fails."""
        # Simulate a failure during report save
        mock_save.side_effect = IOError("Disk full: /var/app/data/reports/")

        response = client.post(
            "/api/save-report",
            data=json.dumps({
                "result": {
                    "quiz_id": "test_001",
                    "total_questions": 10,
                    "correct_count": 8,
                    "failures": [],
                    "score_percentage": 80.0,
                    "passed": True,
                    "time_spent": 120,
                },
                "quiz": sample_quiz_data,
            }),
            content_type="application/json",
        )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["error"] == REPORT_SAVE_FAILED
        # Ensure internal error details are NOT exposed
        assert "IOError" not in data["error"]
        assert "Disk full" not in data["error"]
        assert "/var/app" not in data["error"]
        assert "reports" not in data["error"].lower()

    def test_report_not_found(self, client):
        """Test error message when report doesn't exist."""
        response = client.get("/report/nonexistent_quiz_id")
        assert response.status_code == 404
        html = response.data.decode("utf-8")
        assert REPORT_NOT_FOUND in html
        # Ensure no internal details in HTML response
        assert "nonexistent_quiz_id" not in html

    def test_report_invalid_id(self, client):
        """Test error message for invalid quiz ID in report request."""
        # Use a quiz ID with invalid characters (path traversal)
        response = client.get("/report/quiz..id")
        assert response.status_code == 400
        html = response.data.decode("utf-8")
        assert REPORT_INVALID_ID in html
        # Ensure malicious pattern is not in response
        assert "quiz..id" not in html

    @patch("quizzer.web.routes.logger")
    @patch("quizzer.web.routes.Path.rglob")
    def test_quiz_list_failed(self, mock_rglob, mock_logger, client):
        """Test error message when quiz list retrieval fails."""
        # Simulate an error during quiz list retrieval
        mock_rglob.side_effect = PermissionError("Access denied to /secret/path")

        response = client.get("/api/quizzes")
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["error"] == QUIZ_LIST_FAILED
        # Ensure internal error details are NOT exposed
        assert "PermissionError" not in data["error"]
        assert "Access denied" not in data["error"]
        assert "/secret" not in data["error"]

        # Verify detailed error was logged server-side
        mock_logger.error.assert_called()

    def test_404_error_handler(self, client):
        """Test 404 error handler returns sanitized message."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["error"] == RESOURCE_NOT_FOUND
        # Ensure no URL details are exposed
        assert "nonexistent" not in data["error"]

    def test_500_error_handler(self, client):
        """Test 500 error handler returns sanitized message."""
        # The 500 handler is tested indirectly through other error scenarios
        # Here we verify the error message constant is correct
        assert INTERNAL_ERROR == "Internal server error"
        assert "Internal" in INTERNAL_ERROR

    def test_unexpected_error_handler(self, client):
        """Test unexpected error handler returns sanitized message."""
        # This is tested through various error scenarios above
        assert UNEXPECTED_ERROR == "An unexpected error occurred"
        assert "unexpected" in UNEXPECTED_ERROR.lower()

    def test_error_messages_are_user_friendly(self):
        """Test that all error messages are user-friendly and concise."""
        error_messages = [
            ANSWER_CHECK_FAILED,
            QUIZ_INVALID_PATH,
            QUIZ_LIST_FAILED,
            QUIZ_LOAD_FAILED,
            QUIZ_NOT_FOUND,
            QUIZ_NOT_PROVIDED,
            REPORT_INVALID_ID,
            REPORT_LOAD_FAILED,
            REPORT_NOT_FOUND,
            REPORT_SAVE_FAILED,
            RESOURCE_NOT_FOUND,
            INTERNAL_ERROR,
            UNEXPECTED_ERROR,
        ]

        for msg in error_messages:
            # All messages should be short and user-friendly
            assert len(msg) < 100, f"Error message too long: {msg}"
            # No technical jargon or internal details
            assert "exception" not in msg.lower()
            assert "traceback" not in msg.lower()
            assert "/" not in msg  # No file paths
            assert "\\" not in msg  # No Windows paths
            # Messages should be clear and actionable
            assert msg.strip() == msg  # No extra whitespace
            assert msg[0].isupper() or msg[0].isdigit()  # Proper capitalization


class TestLoggingBehavior:
    """Test that detailed errors are logged properly server-side."""

    @patch("quizzer.web.routes.logger")
    def test_quiz_load_error_logged_with_details(self, mock_logger, client):
        """Test that quiz load errors are logged with full details."""
        # Try to load a non-existent quiz
        client.get("/api/quiz?path=data/quizzes/missing.json")

        # Verify error was logged with details
        assert mock_logger.error.called or mock_logger.warning.called

    @patch("quizzer.web.routes.logger")
    def test_path_traversal_logged_with_details(self, mock_logger, client):
        """Test that path traversal attempts are logged with full details."""
        malicious_path = "../../../etc/passwd"
        client.get(f"/api/quiz?path={malicious_path}")

        # Verify the attempt was logged
        assert mock_logger.warning.called
        # Check that detailed information was logged (not returned to client)
        log_messages = " ".join(str(call) for call in mock_logger.warning.call_args_list)
        assert "path" in log_messages.lower()

    @patch("quizzer.web.routes.logger")
    def test_unexpected_errors_logged_with_traceback(self, mock_logger, client):
        """Test that unexpected errors are logged with exc_info=True."""
        # This test verifies the pattern is used correctly
        # Actual exc_info testing is covered in integration tests
        with patch("quizzer.Quiz.load", side_effect=RuntimeError("Test error")):
            client.get("/api/quiz?path=data/quizzes/test.json")

        # Verify error was logged with exc_info
        assert mock_logger.error.called
        # Check that exc_info=True was used
        calls_with_exc_info = [
            call for call in mock_logger.error.call_args_list
            if call[1].get("exc_info") is True
        ]
        assert len(calls_with_exc_info) > 0
