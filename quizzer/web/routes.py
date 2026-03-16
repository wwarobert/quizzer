"""
Flask routes for web quiz interface.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from flask import jsonify, render_template, request, send_file
from flask_limiter.errors import RateLimitExceeded
from pydantic import ValidationError

import run_quiz
from quizzer import Quiz, QuizResult, is_test_data, normalize_answer
from quizzer.constants import DATA_DIR_NAME, QUIZZES_DIR_NAME, REPORTS_DIR_NAME
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
from quizzer.exceptions import InvalidQuizPathError
from quizzer.security import validate_quiz_path, validate_report_path
from quizzer.web.schemas import CheckAnswerRequest, SaveReportRequest

logger = logging.getLogger("quizzer")

# Directory paths
BASE_DIR = Path(__file__).parent.parent.parent
QUIZZES_DIR = BASE_DIR / DATA_DIR_NAME / QUIZZES_DIR_NAME
REPORTS_DIR = BASE_DIR / DATA_DIR_NAME / REPORTS_DIR_NAME


def register_routes(app, limiter):
    """Register all Flask routes."""

    @app.after_request
    def add_header(response):
        """Add headers to prevent caching during development"""
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
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

                    try:
                        with open(quiz_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            quiz_files.append(
                                {
                                    "path": str(quiz_file),
                                    "quiz_id": data.get("quiz_id", quiz_file.stem),
                                    "num_questions": len(data.get("questions", [])),
                                    "source_file": data.get("source_file", ""),
                                    "created_at": data.get("created_at", ""),
                                }
                            )
                    except (json.JSONDecodeError, IOError) as e:
                        logger.warning(f"Error loading quiz file {quiz_file}: {e}")
                        continue
            else:
                logger.warning(f"Quizzes directory does not exist: {quizzes_dir}")

            # Sort by creation date (newest first)
            quiz_files.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            logger.info(f"Found {len(quiz_files)} quizzes (test_mode={test_mode})")
            return jsonify(quiz_files)
        except Exception as e:
            logger.error(f"Error fetching quizzes: {e}", exc_info=True)
            return jsonify({"error": QUIZ_LIST_FAILED}), 500

    @app.route("/api/quiz")
    @limiter.limit("100 per hour")
    def get_quiz():
        """Get a specific quiz by path."""
        quiz_path = request.args.get("path")
        if not quiz_path:
            logger.warning("Quiz path not provided in request")
            return jsonify({"error": QUIZ_NOT_PROVIDED}), 400

        try:
            logger.debug(f"Loading quiz: {quiz_path}")

            # Validate and sanitize path (prevents path traversal attacks)
            validated_path = validate_quiz_path(quiz_path, QUIZZES_DIR)

            quiz = Quiz.load(validated_path)
            logger.info(f"Quiz loaded successfully: {quiz.quiz_id}")
            return jsonify(quiz.to_dict())
        except InvalidQuizPathError as e:
            logger.warning(f"Invalid quiz path: {quiz_path} - {e}")
            return jsonify({"error": QUIZ_INVALID_PATH}), 400
        except FileNotFoundError:
            logger.error(f"Quiz file not found: {quiz_path}")
            return jsonify({"error": QUIZ_NOT_FOUND}), 404
        except Exception as e:
            logger.error(f"Error loading quiz {quiz_path}: {e}", exc_info=True)
            # Don't expose internal error details to client
            return jsonify({"error": QUIZ_LOAD_FAILED}), 500

    @app.route("/api/check-answer", methods=["POST"])
    @limiter.limit("10 per minute")
    def check_answer():
        """Check if user's answer is correct."""
        try:
            # Validate request payload
            try:
                validated_data = CheckAnswerRequest(**request.json)
            except ValidationError as e:
                logger.warning(f"Invalid check-answer payload: {e}")
                return jsonify({"error": "Invalid request data"}), 400

            # Normalize and compare answers
            user_normalized = normalize_answer(validated_data.user_answer)
            correct_normalized = normalize_answer(validated_data.correct_answer)

            is_correct = user_normalized == correct_normalized

            logger.debug(
                f'Answer check: user="{validated_data.user_answer}" '
                f'correct="{validated_data.correct_answer}" result={is_correct}'
            )

            return jsonify(
                {
                    "correct": is_correct,
                    "normalized_user": user_normalized,
                    "normalized_correct": correct_normalized,
                }
            )
        except Exception as e:
            logger.error(f"Error checking answer: {e}", exc_info=True)
            return jsonify({"error": ANSWER_CHECK_FAILED}), 500

    @app.route("/api/save-report", methods=["POST"])
    @limiter.limit("20 per hour")
    def save_report():
        """Generate and save HTML report for quiz results."""
        try:
            logger.debug("Saving quiz report")

            # Validate request payload
            try:
                validated_data = SaveReportRequest(**request.json)
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

            return jsonify({"success": True, "report_path": str(report_path)})

        except Exception as e:
            logger.error(f"Error saving report: {e}", exc_info=True)
            # Don't expose internal error details to client
            return jsonify({"success": False, "error": REPORT_SAVE_FAILED}), 500

    @app.route("/report/<quiz_id>")
    @limiter.limit("50 per hour")
    def view_report(quiz_id: str):
        """Serve HTML report for a completed quiz."""
        try:
            # Validate quiz_id to prevent path traversal in file name
            validated_id = validate_report_path(quiz_id)

            report_path = REPORTS_DIR / f"{validated_id}_report.html"
            if report_path.exists():
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
        logger.warning(f"Rate limit exceeded: {request.url} - {error}")
        return jsonify({
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later."
        }), 429

    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 Not Found: {request.url}")
        return jsonify({"error": RESOURCE_NOT_FOUND}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Internal Server Error: {error}", exc_info=True)
        return jsonify({"error": INTERNAL_ERROR}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        # Don't catch RateLimitExceeded as a generic exception
        if isinstance(error, RateLimitExceeded):
            raise error
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        return jsonify({"error": UNEXPECTED_ERROR}), 500
