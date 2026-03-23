"""
Template rendering utilities for quiz reports.

This module provides shared template rendering logic used by both CLI (run_quiz.py)
and web (report_service.py) to eliminate HTML duplication and maintain consistency.
"""

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from quizzer.constants import COLOR_DANGER, COLOR_SUCCESS
from quizzer.quiz_data import Quiz, QuizResult


def _get_score_color(score_percentage: float) -> str:
    """
    Get color code based on score percentage.

    Args:
        score_percentage: Score as percentage (0-100)

    Returns:
        Hex color code for visual feedback
    """
    if score_percentage >= 80:
        return "#28a745"  # Green
    elif score_percentage >= 60:
        return "#ffc107"  # Yellow
    else:
        return "#dc3545"  # Red


def render_report_template(result: QuizResult, quiz: Quiz) -> str:
    """
    Render HTML report using Jinja2 template.

    This function provides shared rendering logic for both CLI and web report generation,
    eliminating the 800+ lines of HTML duplication between run_quiz.py and report_service.py.

    Args:
        result: QuizResult object with quiz results
        quiz: Quiz object with quiz metadata

    Returns:
        Rendered HTML string

    Examples:
        >>> from quizzer.quiz_data import QuizResult, Quiz
        >>> result = QuizResult(
        ...     quiz_id="test_001",
        ...     completed_at="2026-03-23T10:00:00",
        ...     total_questions=10,
        ...     correct_answers=8,
        ...     score_percentage=80.0,
        ...     passed=True,
        ...     failures=[],
        ...     time_spent=120.0
        ... )
        >>> quiz = Quiz(
        ...     quiz_id="test_001",
        ...     created_at="2026-03-23T09:00:00",
        ...     source_file="test.csv",
        ...     questions=[]
        ... )
        >>> html = render_report_template(result, quiz)
        >>> "Quiz Report" in html
        True
        >>> "80.0%" in html
        True
    """
    # Get templates directory (project_root/templates)
    # Resolve to absolute path to ensure it works in all contexts (tests, CI, etc.)
    template_dir = Path(__file__).parent.parent / "templates"
    template_dir = template_dir.resolve()

    if not template_dir.exists():
        raise FileNotFoundError(
            f"Templates directory not found: {template_dir}. "
            f"Expected structure: project_root/templates/reports/"
        )

    # Create Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Load template
    template = env.get_template("reports/report.html")

    # Prepare template context
    status_color = COLOR_SUCCESS if result.passed else COLOR_DANGER
    coverage_color = _get_score_color(result.score_percentage)

    # Format datetime and time spent for display
    completed_at_formatted = datetime.fromisoformat(result.completed_at).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    time_spent_minutes = int(result.time_spent // 60)
    time_spent_seconds = int(result.time_spent % 60)
    time_spent_formatted = f"{time_spent_minutes}m {time_spent_seconds}s"

    generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Render template (use_flask_assets=False for standalone CLI reports)
    return template.render(
        result=result,
        quiz=quiz,
        status_color=status_color,
        coverage_color=coverage_color,
        completed_at_formatted=completed_at_formatted,
        time_spent_formatted=time_spent_formatted,
        generation_time=generation_time,
        use_flask_assets=False,  # Don't use url_for in standalone reports
    )
