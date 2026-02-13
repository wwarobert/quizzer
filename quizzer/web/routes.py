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

import run_quiz
from quizzer import Quiz, QuizResult, is_test_data, normalize_answer
from quizzer.constants import DATA_DIR_NAME, QUIZZES_DIR_NAME, REPORTS_DIR_NAME

logger = logging.getLogger("quizzer")

# Directory paths
BASE_DIR = Path(__file__).parent.parent.parent
QUIZZES_DIR = BASE_DIR / DATA_DIR_NAME / QUIZZES_DIR_NAME
REPORTS_DIR = BASE_DIR / DATA_DIR_NAME / REPORTS_DIR_NAME


def register_routes(app):
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
            return jsonify({"error": "Failed to fetch quizzes"}), 500

    @app.route("/api/quiz")
    def get_quiz():
        """Get a specific quiz by path."""
        quiz_path = request.args.get("path")
        if not quiz_path:
            logger.warning("Quiz path not provided in request")
            return jsonify({"error": "No quiz path provided"}), 400

        try:
            logger.debug(f"Loading quiz: {quiz_path}")
            quiz = Quiz.load(quiz_path)
            logger.info(f"Quiz loaded successfully: {quiz.quiz_id}")
            return jsonify(quiz.to_dict())
        except FileNotFoundError:
            logger.error(f"Quiz file not found: {quiz_path}")
            return jsonify({"error": "Quiz not found"}), 404
        except Exception as e:
            logger.error(f"Error loading quiz {quiz_path}: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @app.route("/api/check-answer", methods=["POST"])
    def check_answer():
        """Check if user's answer is correct."""
        try:
            data = request.json
            user_answer = data.get("user_answer", "")
            correct_answer = data.get("correct_answer", "")

            # Normalize and compare answers
            user_normalized = normalize_answer(user_answer)
            correct_normalized = normalize_answer(correct_answer)

            is_correct = user_normalized == correct_normalized

            logger.debug(
                f'Answer check: user="{user_answer}" correct="{correct_answer}" result={is_correct}'
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
            return jsonify({"error": "Failed to check answer"}), 500

    @app.route("/api/save-report", methods=["POST"])
    def save_report():
        """Generate and save HTML report for quiz results."""
        try:
            logger.debug("Saving quiz report")
            data = request.json
            result_data = data.get("result", {})
            quiz_data = data.get("quiz", {})

            # Reconstruct Quiz object
            quiz = Quiz(
                quiz_id=quiz_data["quiz_id"],
                created_at=quiz_data.get("created_at", ""),
                source_file=quiz_data.get("source_file", ""),
                questions=[],
            )

            # Reconstruct QuizResult object
            result = QuizResult(
                quiz_id=result_data["quiz_id"],
                total_questions=result_data["total_questions"],
                correct_answers=result_data["correct_count"],
                failures=result_data["failures"],
                score_percentage=result_data["score_percentage"],
                passed=result_data["passed"],
                completed_at=datetime.now().isoformat(),
                time_spent=result_data.get("time_spent", 0),
            )

            # Generate and save HTML report
            report_path = run_quiz.save_html_report(result, quiz)
            logger.info(f"Report saved successfully: {report_path}")

            return jsonify({"success": True, "report_path": str(report_path)})

        except Exception as e:
            logger.error(f"Error saving report: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/report/<quiz_id>")
    def view_report(quiz_id: str):
        """Serve HTML report for a completed quiz."""
        try:
            report_path = REPORTS_DIR / f"{quiz_id}_report.html"
            if report_path.exists():
                return send_file(report_path, mimetype="text/html")
            else:
                logger.warning(f"Report not found: {report_path}")
                return (
                    f"<h1>Report Not Found</h1><p>No report found for quiz ID: {quiz_id}</p>",
                    404,
                )
        except Exception as e:
            logger.error(f"Error viewing report: {e}", exc_info=True)
            return f"<h1>Error</h1><p>Failed to load report: {e}</p>", 500

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 Not Found: {request.url}")
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Internal Server Error: {error}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500
