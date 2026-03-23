"""
Report generation and management service.

This module provides business logic for report generation, saving, and listing.
Extracted from run_quiz.py and routes.py to improve testability and reusability.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from quizzer import Quiz, QuizResult
from quizzer.constants import (
    COLOR_DANGER,
    COLOR_SUCCESS,
    COLOR_WARNING,
    REPORT_EXCELLENT_THRESHOLD,
    REPORT_WARNING_THRESHOLD,
)

logger = logging.getLogger("quizzer")


@dataclass
class ReportMetadata:
    """
    Metadata for a report file.

    Attributes:
        path: Full path to report HTML file
        quiz_id: Unique identifier for the quiz
        created_at: ISO timestamp of report creation
        size_bytes: File size in bytes
    """

    path: str
    quiz_id: str
    created_at: str
    size_bytes: int

    def to_dict(self) -> dict:
        """Convert metadata to dictionary format for API responses."""
        return {
            "path": self.path,
            "quiz_id": self.quiz_id,
            "created_at": self.created_at,
            "size_bytes": self.size_bytes,
        }


class ReportService:
    """
    Service for report generation and management.

    This service encapsulates the business logic for:
    - Generating HTML reports from quiz results
    - Saving reports to disk
    - Listing available reports
    - Report path validation
    """

    def __init__(self, reports_dir: Path):
        """
        Initialize ReportService.

        Args:
            reports_dir: Path to directory containing report HTML files
        """
        self.reports_dir = Path(reports_dir)

    def _get_score_color(self, score_percentage: float) -> str:
        """
        Get color code based on score percentage.

        Args:
            score_percentage: Score as percentage (0-100)

        Returns:
            Hex color code for score display

        Examples:
            >>> service = ReportService(Path("data/reports"))
            >>> service._get_score_color(90)
            '#28a745'
            >>> service._get_score_color(70)
            '#ffc107'
            >>> service._get_score_color(50)
            '#dc3545'
        """
        if score_percentage >= REPORT_EXCELLENT_THRESHOLD:
            return COLOR_SUCCESS  # Green
        elif score_percentage >= REPORT_WARNING_THRESHOLD:
            return COLOR_WARNING  # Yellow
        else:
            return COLOR_DANGER  # Red

    def generate_html_report(self, result: QuizResult, quiz: Quiz) -> str:
        """
        Generate an HTML report for quiz results.

        Args:
            result: QuizResult object with quiz results
            quiz: Quiz object with quiz metadata

        Returns:
            HTML string with formatted report

        Examples:
            >>> service = ReportService(Path("data/reports"))
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
            >>> quiz = Quiz(quiz_id="test_001", created_at="2026-03-23T09:00:00",
            ...             source_file="test.csv", questions=[])
            >>> html = service.generate_html_report(result, quiz)
            >>> "Quiz Report" in html
            True
            >>> "80.0%" in html
            True
        """
        # Color coding based on pass/fail status
        pass_status = "PASS" if result.passed else "FAIL"
        status_color = COLOR_SUCCESS if result.passed else COLOR_DANGER

        # Color coding based on score percentage for visual feedback
        coverage_color = self._get_score_color(result.score_percentage)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz Report - {result.quiz_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .quiz-id {{
            opacity: 0.9;
            font-size: 1.1em;
        }}

        .status-banner {{
            background: {status_color};
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 1.5em;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}

        .summary {{
            padding: 40px;
            background: #f8f9fa;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}

        .stat-label {{
            color: #6c757d;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
        }}

        .score-circle {{
            position: relative;
            width: 150px;
            height: 150px;
            margin: 20px auto;
        }}

        .score-text {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 2em;
            font-weight: bold;
            color: {coverage_color};
        }}

        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            padding: 20px;
            background: #e9ecef;
            border-radius: 8px;
        }}

        .metadata-item {{
            display: flex;
            flex-direction: column;
        }}

        .metadata-label {{
            font-size: 0.8em;
            color: #6c757d;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}

        .metadata-value {{
            font-weight: 600;
            color: #212529;
        }}

        .failures {{
            padding: 40px;
        }}

        .failures h2 {{
            color: #212529;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}

        .failure-card {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 4px;
        }}

        .failure-card.incorrect {{
            background: #f8d7da;
            border-left-color: #dc3545;
        }}

        .question-number {{
            background: #6c757d;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            display: inline-block;
            margin-bottom: 10px;
        }}

        .question-text {{
            font-size: 1.2em;
            font-weight: 600;
            margin: 10px 0;
            color: #212529;
        }}

        .answer-row {{
            display: grid;
            grid-template-columns: 120px 1fr;
            gap: 10px;
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 4px;
        }}

        .answer-label {{
            font-weight: 600;
            color: #6c757d;
        }}

        .answer-value {{
            font-family: 'Courier New', monospace;
        }}

        .answer-value.incorrect {{
            color: #dc3545;
        }}

        .answer-value.correct {{
            color: #28a745;
        }}

        .perfect-score {{
            text-align: center;
            padding: 60px 40px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}

        .perfect-score h2 {{
            font-size: 3em;
            margin-bottom: 20px;
        }}

        .perfect-score p {{
            font-size: 1.3em;
            opacity: 0.95;
        }}

        .footer {{
            padding: 20px;
            text-align: center;
            background: #212529;
            color: white;
            font-size: 0.9em;
        }}

        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Quiz Report</h1>
            <p class="quiz-id">{result.quiz_id}</p>
        </div>

        <div class="status-banner">
            {pass_status}
        </div>

        <div class="summary">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-label">Total Questions</div>
                    <div class="stat-value">{result.total_questions}</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">Correct Answers</div>
                    <div class="stat-value" style="color: #28a745;">{result.correct_answers}</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">Failed Questions</div>
                    <div class="stat-value" style="color: #dc3545;">{len(result.failures)}</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">Score</div>
                    <div class="stat-value" style="color: {coverage_color};">{result.score_percentage:.1f}%</div>
                </div>
            </div>

            <div class="metadata">
                <div class="metadata-item">
                    <span class="metadata-label">Quiz ID</span>
                    <span class="metadata-value">{result.quiz_id}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Completed</span>
                    <span class="metadata-value">{datetime.fromisoformat(result.completed_at).strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Time Spent</span>
                    <span class="metadata-value">{int(result.time_spent // 60)}m {int(result.time_spent % 60)}s</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Source</span>
                    <span class="metadata-value">{quiz.source_file or 'N/A'}</span>
                </div>
            </div>
        </div>
"""

        if result.failures:
            html += f"""
        <div class="failures">
            <h2>❌ Failed Questions ({len(result.failures)})</h2>
"""
            for failure in result.failures:
                html += f"""
            <div class="failure-card incorrect">
                <span class="question-number">Question #{failure['question_id']}</span>
                <div class="question-text">{failure['question']}</div>
                <div class="answer-row">
                    <span class="answer-label">Your Answer:</span>
                    <span class="answer-value incorrect">{failure['user_answer']}</span>
                </div>
                <div class="answer-row">
                    <span class="answer-label">Correct Answer:</span>
                    <span class="answer-value correct">{failure['correct_answer']}</span>
                </div>
            </div>
"""
            html += """
        </div>
"""
        else:
            html += """
        <div class="perfect-score">
            <h2>🎉 Perfect Score!</h2>
            <p>Congratulations! You answered all questions correctly.</p>
        </div>
"""

        html += f"""
        <div class="footer">
            <p>Generated by Quizzer • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def save_report(
        self, result: QuizResult, quiz: Quiz, create_dirs: bool = True
    ) -> Path:
        """
        Save quiz results as HTML report.

        Args:
            result: QuizResult object
            quiz: Quiz object
            create_dirs: Whether to create output directory if it doesn't exist (default: True)

        Returns:
            Path to saved HTML file

        Raises:
            FileNotFoundError: If reports directory doesn't exist and create_dirs is False
            PermissionError: If lacking write permissions

        Examples:
            >>> service = ReportService(Path("data/reports"))
            >>> result = QuizResult(quiz_id="test_001", completed_at="2026-03-23T10:00:00",
            ...                     total_questions=10, correct_answers=8,
            ...                     score_percentage=80.0, passed=True, failures=[],
            ...                     time_spent=120.0)
            >>> quiz = Quiz(quiz_id="test_001", created_at="2026-03-23T09:00:00",
            ...             source_file="test.csv", questions=[])
            >>> path = service.save_report(result, quiz)
            >>> path.name
            'test_001_report.html'
        """
        if create_dirs:
            self.reports_dir.mkdir(parents=True, exist_ok=True)
        elif not self.reports_dir.exists():
            raise FileNotFoundError(
                f"Reports directory does not exist: {self.reports_dir}"
            )

        # Use quiz_id for filename so it gets overwritten on each run
        filename = f"{result.quiz_id}_report.html"
        filepath = self.reports_dir / filename

        html_content = self.generate_html_report(result, quiz)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Report saved: {filepath}")
        return filepath

    def list_reports(self) -> List[ReportMetadata]:
        """
        List all available reports.

        Returns:
            List of ReportMetadata objects, sorted by creation date (newest first)

        Examples:
            >>> service = ReportService(Path("data/reports"))
            >>> reports = service.list_reports()
            >>> all(isinstance(r, ReportMetadata) for r in reports)
            True
        """
        reports = []

        if not self.reports_dir.exists():
            logger.warning(f"Reports directory does not exist: {self.reports_dir}")
            return []

        # Find all HTML report files
        for report_file in self.reports_dir.glob("*_report.html"):
            # Extract quiz_id from filename (format: {quiz_id}_report.html)
            quiz_id = report_file.stem.replace("_report", "")

            # Get file stats
            stat = report_file.stat()

            reports.append(
                ReportMetadata(
                    path=str(report_file),
                    quiz_id=quiz_id,
                    created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    size_bytes=stat.st_size,
                )
            )

        # Sort by creation date (newest first)
        reports.sort(key=lambda x: x.created_at, reverse=True)

        logger.info(f"Found {len(reports)} reports")
        return reports

    def report_exists(self, quiz_id: str) -> bool:
        """
        Check if report exists for given quiz_id.

        Args:
            quiz_id: Quiz identifier

        Returns:
            True if report file exists, False otherwise

        Examples:
            >>> service = ReportService(Path("data/reports"))
            >>> service.report_exists("nonexistent_quiz")
            False
        """
        filepath = self.reports_dir / f"{quiz_id}_report.html"
        return filepath.exists()

    def get_report_path(self, quiz_id: str) -> Optional[Path]:
        """
        Get path to report file for given quiz_id.

        Args:
            quiz_id: Quiz identifier

        Returns:
            Path to report file if exists, None otherwise

        Examples:
            >>> service = ReportService(Path("data/reports"))
            >>> path = service.get_report_path("test_001")
            >>> path is None or isinstance(path, Path)
            True
        """
        filepath = self.reports_dir / f"{quiz_id}_report.html"
        return filepath if filepath.exists() else None

    def get_report_count(self) -> int:
        """
        Get count of available reports.

        Returns:
            Number of report files

        Examples:
            >>> service = ReportService(Path("data/reports"))
            >>> count = service.get_report_count()
            >>> count >= 0
            True
        """
        return len(self.list_reports())

    def delete_report(self, quiz_id: str) -> bool:
        """
        Delete report for given quiz_id.

        Args:
            quiz_id: Quiz identifier

        Returns:
            True if report was deleted, False if it didn't exist

        Examples:
            >>> service = ReportService(Path("/tmp/test_reports"))
            >>> service.delete_report("nonexistent")
            False
        """
        filepath = self.reports_dir / f"{quiz_id}_report.html"
        if filepath.exists():
            filepath.unlink()
            logger.info(f"Report deleted: {filepath}")
            return True
        return False
