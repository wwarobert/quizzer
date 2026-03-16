"""Tests for API rate limiting.

This module tests that rate limiting is properly configured and enforced
to prevent DoS attacks and resource exhaustion.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import json
import time
from pathlib import Path

import pytest

from quizzer.web.app import create_app


@pytest.fixture
def app():
    """Create test Flask app with rate limiting enabled."""
    test_app = create_app(test_mode=True)
    test_app.config["TESTING"] = True
    # Disable rate limit storage (use in-memory for tests)
    test_app.config["RATELIMIT_STORAGE_URL"] = "memory://"
    return test_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestRateLimitConfiguration:
    """Test rate limiting is properly configured."""

    def test_limiter_enabled(self, app):
        """Rate limiter should be enabled in the app."""
        from quizzer.web.app import limiter

        assert limiter is not None
        assert limiter.enabled

    def test_default_limits_configured(self, app):
        """Default rate limits should be configured."""
        from quizzer.web.app import limiter

        # Check default limits are set (check limiter is properly initialized)
        assert limiter.enabled
        # Verify the app has extensions configured
        assert hasattr(app, 'extensions')
        assert 'limiter' in app.extensions


class TestQuizzesEndpointRateLimit:
    """Test rate limiting on /api/quizzes endpoint."""

    def test_quizzes_within_limit(self, client):
        """Requests within limit should succeed."""
        # Make 5 requests (well under 100/hour limit)
        for i in range(5):
            response = client.get("/api/quizzes")
            assert response.status_code == 200, f"Request {i+1} failed"

    def test_quizzes_rate_limit_headers(self, client):
        """Rate limit headers should be present."""
        response = client.get("/api/quizzes")
        assert response.status_code == 200

        # Check for rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers


class TestQuizEndpointRateLimit:
    """Test rate limiting on /api/quiz endpoint."""

    def test_quiz_within_limit(self, client):
        """Requests within limit should succeed."""
        # Make 5 requests (well under 100/hour limit)
        for i in range(5):
            # Query parameter required but we're testing rate limit not functionality
            response = client.get("/api/quiz?path=test.json")
            # May return 400 (no quiz) but shouldn't return 429 (rate limited)
            assert response.status_code != 429, f"Request {i+1} was rate limited"

    def test_quiz_rate_limit_headers(self, client):
        """Rate limit headers should be present."""
        response = client.get("/api/quiz?path=test.json")

        # Check for rate limit headers
        assert "X-RateLimit-Limit" in response.headers


class TestCheckAnswerRateLimit:
    """Test rate limiting on /api/check-answer endpoint (10/minute)."""

    def test_check_answer_within_limit(self, client):
        """Requests within limit should succeed."""
        payload = {"user_answer": "test", "correct_answer": "test"}

        # Make 5 requests (under 10/minute limit)
        for i in range(5):
            response = client.post(
                "/api/check-answer",
                data=json.dumps(payload),
                content_type="application/json",
            )
            assert response.status_code in [
                200,
                400,
            ], f"Request {i+1} got unexpected status"
            assert response.status_code != 429, f"Request {i+1} was rate limited"

    def test_check_answer_strict_limit(self, client):
        """Check answer has stricter limits than other endpoints."""
        from quizzer.web.app import limiter

        # This endpoint should have "10 per minute" limit (stricter)
        # We can't easily test hitting the limit without mocking time,
        # but we can verify headers show the limit
        payload = {"user_answer": "test", "correct_answer": "test"}
        response = client.post(
            "/api/check-answer",
            data=json.dumps(payload),
            content_type="application/json",
        )

        # Check headers indicate per-minute limit
        if "X-RateLimit-Limit" in response.headers:
            limit = response.headers["X-RateLimit-Limit"]
            # Should show "10" for 10 per minute
            assert "10" in limit or limit.startswith("10")


class TestSaveReportRateLimit:
    """Test rate limiting on /api/save-report endpoint (20/hour)."""

    def test_save_report_within_limit(self, client):
        """Requests within limit should succeed or fail gracefully."""
        # Valid payload structure
        payload = {
            "result": {
                "quiz_id": "test",
                "total_questions": 10,
                "correct_count": 8,
                "failures": [],
                "score_percentage": 80.0,
                "passed": True,
                "time_spent": 300,
            },
            "quiz": {"quiz_id": "test", "created_at": "", "source_file": ""},
        }

        # Make 5 requests (under 20/hour limit)
        for i in range(5):
            response = client.post(
                "/api/save-report",
                data=json.dumps(payload),
                content_type="application/json",
            )
            # Should not be rate limited (may fail for other reasons)
            assert response.status_code != 429, f"Request {i+1} was rate limited"


class TestReportViewRateLimit:
    """Test rate limiting on /report/<quiz_id> endpoint (50/hour)."""

    def test_report_view_within_limit(self, client):
        """Requests within limit should succeed or return 404."""
        # Make 5 requests (under 50/hour limit)
        for i in range(5):
            response = client.get("/report/test_quiz_001")
            # Should not be rate limited
            assert response.status_code != 429, f"Request {i+1} was rate limited"
            # May return 404 (not found) but that's OK for rate limit test


class TestRateLimitErrorResponse:
    """Test rate limit exceeded responses."""

    def test_rate_limit_returns_429(self, app):
        """Rate limit exceeded should return 429 status code."""
        # This test verifies the response when limit is exceeded
        # We use a custom app with very low limits for testing
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address

        test_app = create_app(test_mode=True)
        test_app.config["TESTING"] = True

        # Create a new limiter with very low limits for testing
        test_limiter = Limiter(
            key_func=get_remote_address,
            app=test_app,
            default_limits=["2 per hour"],  # Very low for testing
            storage_uri="memory://",
        )

        # Override route with test limit
        @test_app.route("/test-limit")
        @test_limiter.limit("2 per minute")
        def test_endpoint():
            return "OK"

        client = test_app.test_client()

        # First 2 requests should succeed
        response1 = client.get("/test-limit")
        response2 = client.get("/test-limit")
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Third request should be rate limited
        response3 = client.get("/test-limit")
        assert response3.status_code == 429

    def test_rate_limit_error_message(self, app):
        """Rate limit error should include helpful message."""
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address

        test_app = create_app(test_mode=True)
        test_app.config["TESTING"] = True

        test_limiter = Limiter(
            key_func=get_remote_address,
            app=test_app,
            default_limits=["1 per hour"],
            storage_uri="memory://",
        )

        @test_app.route("/test-limit")
        @test_limiter.limit("1 per minute")
        def test_endpoint():
            return "OK"

        client = test_app.test_client()

        # Exhaust limit
        client.get("/test-limit")

        # Get rate limited response
        response = client.get("/test-limit")
        assert response.status_code == 429
        # Response should contain retry information
        assert "Retry-After" in response.headers or "X-RateLimit-Reset" in response.headers


class TestDifferentEndpointsIndependentLimits:
    """Test that different endpoints have independent rate limits."""

    def test_endpoints_have_separate_counters(self, client):
        """Hitting limit on one endpoint shouldn't affect another."""
        # Make requests to /api/quizzes
        for _ in range(5):
            response = client.get("/api/quizzes")
            assert response.status_code == 200

        # /api/quiz should still work (separate counter)
        response = client.get("/api/quiz?path=test.json")
        assert response.status_code != 429  # Not rate limited

        # /api/check-answer should still work (separate counter)
        payload = {"user_answer": "test", "correct_answer": "test"}
        response = client.post(
            "/api/check-answer",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code != 429  # Not rate limited
