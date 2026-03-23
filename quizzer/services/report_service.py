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
from quizzer.template_utils import render_report_template

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

    def generate_html_report(self, result: QuizResult, quiz: Quiz) -> str:
        """
        Generate an HTML report for quiz results using Jinja2 template.

        This method now uses shared template rendering to eliminate code duplication.
        Previously contained 423 lines of embedded HTML/CSS, now delegates to template_utils.

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
        return render_report_template(result, quiz)

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
