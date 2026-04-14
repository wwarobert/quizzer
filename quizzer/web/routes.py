"""
Flask routes for web quiz interface.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import json
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path

from flask import g, jsonify, render_template, request, send_file
from flask_limiter.errors import RateLimitExceeded
from pydantic import ValidationError

import run_quiz
from quizzer import Quiz, QuizResult, is_test_data
from quizzer.constants import DATA_DIR_NAME, QUIZZES_DIR_NAME, REPORTS_DIR_NAME
from quizzer.services import AnswerService
from quizzer.error_messages import (
    ANSWER_CHECK_FAILED,
    INTERNAL_ERROR,
    QUIZ_DELETE_FAILED,
    QUIZ_DELETE_NOT_ALLOWED,
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
from quizzer.exceptions import InvalidQuizPathError
from quizzer.security import validate_quiz_path, validate_report_path
from quizzer.web.schemas import CheckAnswerRequest, SaveReportRequest

logger = logging.getLogger("quizzer")

# Directory paths
BASE_DIR = Path(__file__).parent.parent.parent
QUIZZES_DIR = BASE_DIR / DATA_DIR_NAME / QUIZZES_DIR_NAME
REPORTS_DIR = BASE_DIR / DATA_DIR_NAME / REPORTS_DIR_NAME


def _get_request_id() -> str:
    """Get current request ID for logging."""
    return getattr(g, 'request_id', 'no-request-id')


def _log_user_action(action: str, **kwargs):
    """
    Log user action with structured format.

    Args:
        action: Action name (e.g., 'quiz_loaded', 'answer_checked')
        **kwargs: Additional context to log
    """
    context = {
        "request_id": _get_request_id(),
        "action": action,
        "path": request.path,
        "method": request.method,
        "ip": request.remote_addr,
        **kwargs
    }
    logger.info(f"USER_ACTION: {json.dumps(context)}")


def _log_and_return_error(
    message: str,
    status_code: int,
    error_details: str = "",
    exc_info: bool = False
) -> tuple:
    """
    Log error and return JSON error response.

    Args:
        message: User-facing error message
        status_code: HTTP status code
        error_details: Additional details for logging (not exposed to client)
        exc_info: Whether to include exception info in logs

    Returns:
        Tuple of (jsonify response, status_code)
    """
    log_msg = f"[{_get_request_id()}] {message}"
    if error_details:
        log_msg += f" - {error_details}"

    if status_code >= 500:
        logger.error(log_msg, exc_info=exc_info)
    elif status_code >= 400:
        logger.warning(log_msg)

    return jsonify({"error": message}), status_code


def _load_quiz_metadata(quiz_file: Path) -> dict | None:
    """
    Load quiz metadata from JSON file.

    Args:
        quiz_file: Path to quiz JSON file

    Returns:
        Dict with quiz metadata or None if loading fails
    """
    try:
        with open(quiz_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "path": str(quiz_file),
                "quiz_id": data.get("quiz_id", quiz_file.stem),
                "num_questions": len(data.get("questions", [])),
                "source_file": data.get("source_file", ""),
                "created_at": data.get("created_at", ""),
            }
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Error loading quiz file {quiz_file}: {e}")
        return None


def _validate_payload(schema_class, data: dict):
    """
    Validate request payload against Pydantic schema.

    Args:
        schema_class: Pydantic model class
        data: Request data to validate

    Returns:
        Validated data instance

    Raises:
        ValidationError: If validation fails
    """
    return schema_class(**data)


def register_routes(app, limiter):
    """Register all Flask routes."""

    @app.before_request
    def generate_request_id():
        """Generate unique request ID for tracing and start request timer."""
        g.request_id = str(uuid.uuid4())
        g.request_start_time = time.time()
        # Log incoming request
        logger.debug(
            f"[{g.request_id}] INCOMING: {request.method} {request.path} "
            f"from {request.remote_addr}"
        )

    @app.after_request
    def add_header(response):
        """Add headers, include request ID, and log performance metrics."""
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        # Add request ID for tracing
        response.headers["X-Request-ID"] = getattr(g, 'request_id', 'unknown')

        # Log performance metrics
        if hasattr(g, 'request_start_time'):
            duration_ms = (time.time() - g.request_start_time) * 1000
            logger.info(
                f"[{_get_request_id()}] RESPONSE: {request.method} {request.path} "
                f"→ {response.status_code} ({duration_ms:.2f}ms)"
            )

        return response

    @app.route("/")
    def index():
        """Serve the main quiz interface."""
        try:
            logger.debug("Serving main page")
            # Use timestamp for cache busting
            cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
            return render_template("index.html", timestamp=cache_buster)
        except Exception as e:
            logger.error(f"Error serving main page: {e}", exc_info=True)
            raise

    @app.route("/version")
    def version():
        """Return version info to verify what's being served."""
        return jsonify(
            {
                "version": "5.0",
                "layout": "Two-Column: Custom Theme Sidebar (300px) + Comprehensive Dashboard",
                "sidebar_width": "300px",
                "main_content_margin": "300px from left",
                "theme": "Modern Minimalist (#FFFFFF, #F7F7F7, #B0BEC5, #455A64, #263238) with dark mode support",
                "dashboard_features": [
                    "Overall Statistics (6 stat cards)",
                    "Performance Trends (visual bars)",
                    "Quiz Performance Breakdown (detailed table)",
                    "Recent Activity (timeline view)",
                    "Pass/Fail Analysis (comprehensive stats)",
                ],
                "timestamp": datetime.now().isoformat(),
            }
        )

    @app.route("/api/quizzes")
    @limiter.limit("100 per hour")
    def get_quizzes():
        """Get list of available quizzes."""
        try:
            logger.debug("Fetching quiz list")
            quizzes_dir = Path("data/quizzes")
            quiz_files = []
            test_mode: bool = app.config.get("TEST_MODE", False)

            if quizzes_dir.exists():
                # Search recursively for all quiz JSON files
                for quiz_file in quizzes_dir.rglob("*.json"):
                    # Skip last_import.json metadata file
                    if quiz_file.name == "last_import.json":
                        continue

                    # Skip test data quizzes in production mode
                    if not test_mode and is_test_data(quiz_file.parent):
                        logger.debug(
                            f"Skipping test data quiz in production mode: {quiz_file}"
                        )
                        continue

                    # Load quiz metadata using helper
                    metadata = _load_quiz_metadata(quiz_file)
                    if metadata:
                        quiz_files.append(metadata)
            else:
                logger.warning(f"Quizzes directory does not exist: {quizzes_dir}")

            # Sort by creation date (newest first)
            quiz_files.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            logger.info(f"[{_get_request_id()}] Found {len(quiz_files)} quizzes (test_mode={test_mode})")
            _log_user_action("quizzes_listed", count=len(quiz_files), test_mode=test_mode)
            return jsonify(quiz_files)
        except Exception as e:
            return _log_and_return_error(
                QUIZ_LIST_FAILED,
                500,
                error_details=f"Error fetching quizzes: {e}",
                exc_info=True
            )

    @app.route("/api/quiz")
    @limiter.limit("100 per hour")
    def get_quiz():
        """Get a specific quiz by path."""
        quiz_path = request.args.get("path")
        if not quiz_path:
            logger.warning(f"[{_get_request_id()}] Quiz path not provided in request")
            return jsonify({"error": QUIZ_NOT_PROVIDED}), 400

        try:
            logger.debug(f"[{_get_request_id()}] Loading quiz: {quiz_path}")

            # Validate and sanitize path (prevents path traversal attacks)
            validated_path = validate_quiz_path(quiz_path, QUIZZES_DIR)

            quiz = Quiz.load(validated_path)
            logger.info(f"[{_get_request_id()}] Quiz loaded successfully: {quiz.quiz_id}")
            _log_user_action(
                "quiz_loaded",
                quiz_id=quiz.quiz_id,
                num_questions=len(quiz.questions),
                path=quiz_path
            )
            return jsonify(quiz.to_dict())
        except InvalidQuizPathError as e:
            return _log_and_return_error(
                QUIZ_INVALID_PATH,
                400,
                error_details=f"Invalid quiz path: {quiz_path} - {e}"
            )
        except FileNotFoundError:
            return _log_and_return_error(
                QUIZ_NOT_FOUND,
                404,
                error_details=f"Quiz file not found: {quiz_path}"
            )
        except Exception as e:
            return _log_and_return_error(
                QUIZ_LOAD_FAILED,
                500,
                error_details=f"Error loading quiz {quiz_path}: {e}",
                exc_info=True
            )

    @app.route("/api/check-answer", methods=["POST"])
    @limiter.limit("10 per minute")
    def check_answer():
        """Check if user's answer is correct."""
        try:
            # Validate request payload using helper
            try:
                validated_data = _validate_payload(CheckAnswerRequest, request.json)
            except ValidationError as e:
                return _log_and_return_error(
                    "Invalid request data",
                    400,
                    error_details=f"Invalid check-answer payload: {e}"
                )

            # Use AnswerService to check answer
            result = AnswerService.check_answer(
                validated_data.user_answer,
                validated_data.correct_answer
            )

            logger.debug(
                f'Answer check: user="{result.user_raw}" '
                f'correct="{result.correct_raw}" result={result.is_correct}'
            )

            _log_user_action(
                "answer_checked",
                correct=result.is_correct,
                user_answer_length=len(validated_data.user_answer),
                has_comma=("," in validated_data.user_answer)
            )

            return jsonify(result.to_dict())
        except Exception as e:
            return _log_and_return_error(
                ANSWER_CHECK_FAILED,
                500,
                error_details=f"Error checking answer: {e}",
                exc_info=True
            )

    @app.route("/api/save-report", methods=["POST"])
    @limiter.limit("20 per hour")
    def save_report():
        """Generate and save HTML report for quiz results."""
        try:
            logger.debug("Saving quiz report")

            # Validate request payload using helper
            try:
                validated_data = _validate_payload(SaveReportRequest, request.json)
            except ValidationError as e:
                logger.warning(f"Invalid save-report payload: {e}")
                return jsonify({"success": False, "error": "Invalid request data"}), 400

            # Reconstruct Quiz object
            quiz = Quiz(
                quiz_id=validated_data.quiz.quiz_id,
                created_at=validated_data.quiz.created_at,
                source_file=validated_data.quiz.source_file,
                questions=[],
            )

            # Reconstruct QuizResult object
            result = QuizResult(
                quiz_id=validated_data.result.quiz_id,
                total_questions=validated_data.result.total_questions,
                correct_answers=validated_data.result.correct_count,
                failures=validated_data.result.failures,
                score_percentage=validated_data.result.score_percentage,
                passed=validated_data.result.passed,
                completed_at=datetime.now().isoformat(),
                time_spent=validated_data.result.time_spent,
            )

            # Generate and save HTML report
            report_path = run_quiz.save_html_report(result, quiz)
            logger.info(f"Report saved successfully: {report_path}")

            _log_user_action(
                "report_saved",
                quiz_id=result.quiz_id,
                score=result.score_percentage,
                passed=result.passed,
                total_questions=result.total_questions,
                correct=result.correct_answers,
                time_spent=result.time_spent
            )

            return jsonify({"success": True, "report_path": str(report_path)})

        except Exception as e:
            logger.error(f"Error saving report: {e}", exc_info=True)
            # Don't expose internal error details to client
            return jsonify({"success": False, "error": REPORT_SAVE_FAILED}), 500

    @app.route("/api/quiz", methods=["DELETE"])
    @limiter.limit("20 per hour")
    def delete_quiz():
        """Delete a quiz JSON file.

        Validates the path to prevent directory traversal, then
        removes the quiz file from disk.

        Returns:
            JSON with success status and updated quiz count.
        """
        quiz_path = request.args.get("path")
        if not quiz_path:
            return jsonify({"error": QUIZ_NOT_PROVIDED}), 400

        try:
            # Validate path (prevents traversal attacks)
            validated_path = validate_quiz_path(quiz_path, QUIZZES_DIR)

            if not validated_path.exists():
                return _log_and_return_error(
                    QUIZ_NOT_FOUND, 404,
                    error_details=f"Quiz file not found: {quiz_path}"
                )

            # Delete the file
            validated_path.unlink()

            _log_user_action(
                "quiz_deleted",
                quiz_path=str(validated_path)
            )

            logger.info(
                f"[{_get_request_id()}] Quiz deleted: "
                f"{validated_path}"
            )

            return jsonify({"success": True})

        except InvalidQuizPathError as e:
            return _log_and_return_error(
                QUIZ_DELETE_NOT_ALLOWED, 400,
                error_details=f"Invalid path for deletion: "
                f"{quiz_path} - {e}"
            )
        except Exception as e:
            return _log_and_return_error(
                QUIZ_DELETE_FAILED, 500,
                error_details=f"Error deleting quiz: {e}",
                exc_info=True
            )

    @app.route("/report/<quiz_id>")
    @limiter.limit("50 per hour")
    def view_report(quiz_id: str):
        """Serve HTML report for a completed quiz."""
        try:
            # Validate quiz_id to prevent path traversal in file name
            validated_id = validate_report_path(quiz_id)

            report_path = REPORTS_DIR / f"{validated_id}_report.html"
            if report_path.exists():
                _log_user_action("report_viewed", quiz_id=validated_id)
                return send_file(report_path, mimetype="text/html")
            else:
                logger.warning(f"Report not found: {report_path}")
                return (
                    f"<h1>{REPORT_NOT_FOUND}</h1><p>No report found for the requested quiz.</p>",
                    404,
                )
        except InvalidQuizPathError as e:
            logger.warning(f"Invalid quiz ID in report request: {quiz_id} - {e}")
            return f"<h1>{REPORT_INVALID_ID}</h1><p>The provided quiz ID is invalid.</p>", 400
        except Exception as e:
            logger.error(f"Error viewing report: {e}", exc_info=True)
            # Don't expose internal error details
            return f"<h1>Error</h1><p>{REPORT_LOAD_FAILED}</p>", 500

    # Error handlers
    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(error):
        """Handle rate limit exceeded errors."""
        logger.warning(f"[{_get_request_id()}] Rate limit exceeded: {request.url} - {error}")
        return jsonify({
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later."
        }), 429

    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"[{_get_request_id()}] 404 Not Found: {request.url}")
        return jsonify({"error": RESOURCE_NOT_FOUND}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"[{_get_request_id()}] 500 Internal Server Error: {error}", exc_info=True)
        return jsonify({"error": INTERNAL_ERROR}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        # Don't catch RateLimitExceeded as a generic exception
        if isinstance(error, RateLimitExceeded):
            raise error
        logger.error(f"[{_get_request_id()}] Unhandled exception: {error}", exc_info=True)
        return jsonify({"error": UNEXPECTED_ERROR}), 500
