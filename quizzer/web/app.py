"""
Flask application factory.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

from pathlib import Path

from flask import Flask

from quizzer.web.routes import register_routes


def create_app(test_mode=False):
    """
    Create and configure Flask application.

    Args:
        test_mode: Enable test mode (show sample quizzes)

    Returns:
        app: Configured Flask application
    """
    # Calculate paths relative to project root
    base_dir = Path(__file__).parent.parent.parent
    template_dir = base_dir / "templates"
    static_dir = base_dir / "static"

    # Initialize Flask app with proper paths
    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
    )

    # App configuration
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0  # Disable caching for development
    app.config["TEST_MODE"] = test_mode  # Production mode by default

    # Register routes
    register_routes(app)

    return app
