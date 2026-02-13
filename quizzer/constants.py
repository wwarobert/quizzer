"""
Application Constants - Centralized configuration values.

This module defines all magic numbers and strings used across the application.
By centralizing constants, we make the code more maintainable and reduce errors.

Why we use constants:
- Type safety and IDE autocomplete
- Single source of truth
- Easy to modify configuration
- Self-documenting code

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

from enum import Enum

# ============================================================================
# Quiz Scoring Configuration
# ============================================================================

# Default passing percentage - chosen based on educational standards
# where 80% represents strong comprehension of material
DEFAULT_PASS_THRESHOLD = 80.0

# Score tier thresholds for feedback and analytics
SCORE_PERFECT = 100.0
SCORE_EXCELLENT_MIN = 90.0
SCORE_GOOD_MIN = 80.0
SCORE_CLOSE_MIN = 70.0
SCORE_FAIL_MAX = 69.9

# Color codes for score visualization in HTML reports
COLOR_SUCCESS = "#28a745"  # Green for passing scores
COLOR_WARNING = "#ffc107"  # Yellow for marginal scores
COLOR_DANGER = "#dc3545"  # Red for failing scores

# Score threshold for color assignment in reports
# - Green: >= 80% (passing)
# - Yellow: 60-79% (marginal)
# - Red: < 60% (failing)
REPORT_EXCELLENT_THRESHOLD = 80.0
REPORT_WARNING_THRESHOLD = 60.0


# ============================================================================
# File System Configuration
# ============================================================================

# File extensions - defined as constants to prevent typos
QUIZ_FILE_EXTENSION = ".json"
CSV_FILE_EXTENSION = ".csv"
HTML_REPORT_EXTENSION = ".html"

# Special filenames used by the application
METADATA_FILENAME = "last_import.json"
QUIZ_FILE_PATTERN = f"*{QUIZ_FILE_EXTENSION}"

# Directory structure - base paths for different data types
# These are relative to the workspace root
DATA_DIR_NAME = "data"
INPUT_DIR_NAME = "input"
QUIZZES_DIR_NAME = "quizzes"
REPORTS_DIR_NAME = "reports"
LOGS_DIR_NAME = "logs"


# ============================================================================
# Quiz Generation Configuration
# ============================================================================

# Maximum questions per quiz - balances depth vs. time commitment
# 50 questions typically takes 10-15 minutes to complete
DEFAULT_MAX_QUESTIONS = 50

# Default number of quizzes to generate from a single source file
DEFAULT_QUIZ_COUNT = 1


# ============================================================================
# Web Server Configuration
# ============================================================================

# Default server settings
DEFAULT_HOST = "127.0.0.1"  # Localhost only for security
DEFAULT_PORT = 5000  # Standard Flask development port

# HTTPS configuration
HTTPS_ENABLED = True
CERT_DIR_NAME = "certs"
CERT_FILENAME = "cert.pem"
KEY_FILENAME = "key.pem"

# Certificate validity period (days)
# Self-signed certs expire after 1 year
CERT_VALIDITY_DAYS = 365


# ============================================================================
# Data Storage Limits
# ============================================================================

# Maximum quiz history to store in browser localStorage
# Balances history depth with storage limits and performance
MAX_QUIZ_RUNS_STORED = 100

# Number of recent runs to display in dashboard trends
MAX_TREND_DISPLAY = 10

# Number of recent activities to show
MAX_RECENT_ACTIVITIES = 10


# ============================================================================
# Test Data Identification
# ============================================================================

# Folder name patterns that indicate test/sample data
# Used to filter out examples in production mode
TEST_DATA_PATTERNS = ["sample", "test", "demo", "example"]


# ============================================================================
# Logging Configuration
# ============================================================================

# Log file settings for web server
LOG_FILENAME = "web_quiz.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB per file
LOG_BACKUP_COUNT = 5  # Keep 5 backup files
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"


# ============================================================================
# UI Configuration
# ============================================================================


class QuizTheme(Enum):
    """Color theme for the web interface."""

    PRIMARY = "#455A64"  # Dark blue-gray
    PRIMARY_DARK = "#263238"  # Darker variant
    PRIMARY_LIGHT = "#B0BEC5"  # Lighter variant
    ACCENT = "#2563eb"  # Blue accent
    SUCCESS = "#10b981"  # Green
    WARNING = "#f59e0b"  # Orange
    DANGER = "#ef4444"  # Red


class ScoreTier(Enum):
    """Score tier categories for messaging and analytics."""

    PERFECT = "perfect"  # 100%
    EXCELLENT = "excellent"  # 90-99%
    GOOD = "good"  # 80-89%
    CLOSE = "close"  # 70-79%
    FAILED = "failed"  # <70%


# ============================================================================
# API Configuration
# ============================================================================

# HTTP timeout settings (in seconds)
API_TIMEOUT = 30
API_RETRY_COUNT = 3


# ============================================================================
# Validation Rules
# ============================================================================

# Minimum questions required in a CSV file
MIN_QUESTIONS_REQUIRED = 1

# Maximum reasonable question length (characters)
MAX_QUESTION_LENGTH = 500

# Maximum reasonable answer length (characters)
MAX_ANSWER_LENGTH = 200
