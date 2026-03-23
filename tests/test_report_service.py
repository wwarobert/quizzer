"""
Tests for ReportService.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

from pathlib import Path

import pytest

from quizzer import Quiz, QuizResult
from quizzer.services import ReportMetadata, ReportService
from quizzer.template_utils import _get_score_color


class TestReportMetadata:
    """Tests for ReportMetadata dataclass."""

    def test_metadata_creation(self):
        """Test ReportMetadata creation."""
        metadata = ReportMetadata(
            path="/data/reports/test_001_report.html",
            quiz_id="test_001",
            created_at="2026-03-23T10:00:00",
            size_bytes=5120,
        )

        assert metadata.path == "/data/reports/test_001_report.html"
        assert metadata.quiz_id == "test_001"
        assert metadata.created_at == "2026-03-23T10:00:00"
        assert metadata.size_bytes == 5120

    def test_metadata_to_dict(self):
        """Test ReportMetadata to_dict conversion."""
        metadata = ReportMetadata(
            path="/tmp/report.html",
            quiz_id="test",
            created_at="2026-03-23T10:00:00",
            size_bytes=1024,
        )

        data = metadata.to_dict()
        assert data["path"] == "/tmp/report.html"
        assert data["quiz_id"] == "test"
        assert data["created_at"] == "2026-03-23T10:00:00"
        assert data["size_bytes"] == 1024


class TestReportServiceInit:
    """Tests for ReportService initialization."""

    def test_init_with_path(self, tmp_path):
        """Test service initialization with Path object."""
        service = ReportService(tmp_path)
        assert service.reports_dir == tmp_path

    def test_init_with_string(self, tmp_path):
        """Test service initialization with string path."""
        service = ReportService(str(tmp_path))
        assert service.reports_dir == Path(tmp_path)


class TestReportServiceGetScoreColor:
    """Tests for _get_score_color function from template_utils."""

    def test_excellent_score_90(self):
        """Test color for 90% score (excellent)."""
        color = _get_score_color(90.0)
        assert color == "#28a745"  # COLOR_SUCCESS (green)

    def test_excellent_score_80(self):
        """Test color for 80% score (excellent threshold)."""
        color = _get_score_color(80.0)
        assert color == "#28a745"  # COLOR_SUCCESS (green)

    def test_warning_score_70(self):
        """Test color for 70% score (warning)."""
        color = _get_score_color(70.0)
        assert color == "#ffc107"  # COLOR_WARNING (yellow)

    def test_warning_score_60(self):
        """Test color for 60% score (warning threshold)."""
        color = _get_score_color(60.0)
        assert color == "#ffc107"  # COLOR_WARNING (yellow)

    def test_danger_score_50(self):
        """Test color for 50% score (danger)."""
        color = _get_score_color(50.0)
        assert color == "#dc3545"  # COLOR_DANGER (red)

    def test_danger_score_0(self):
        """Test color for 0% score (danger)."""
        color = _get_score_color(0.0)
        assert color == "#dc3545"  # COLOR_DANGER (red)

    def test_perfect_score_100(self):
        """Test color for 100% score (perfect)."""
        color = _get_score_color(100.0)
        assert color == "#28a745"  # COLOR_SUCCESS (green)


class TestReportServiceGenerateHtmlReport:
    """Tests for generate_html_report method."""

    def test_generate_report_pass_status(self):
        """Test HTML report generation for passing quiz."""
        service = ReportService(Path("/tmp"))
        result = QuizResult(
            quiz_id="test_001",
            completed_at="2026-03-23T10:00:00",
            total_questions=10,
            correct_answers=8,
            score_percentage=80.0,
            passed=True,
            failures=[],
            time_spent=120.0,
        )
        quiz = Quiz(
            quiz_id="test_001",
            created_at="2026-03-23T09:00:00",
            source_file="test.csv",
            questions=[],
        )

        html = service.generate_html_report(result, quiz)

        assert "Quiz Report" in html
        assert "test_001" in html
        assert "PASS" in html
        assert "80.0%" in html
        assert "Perfect Score" in html  # No failures

    def test_generate_report_fail_status(self):
        """Test HTML report generation for failing quiz."""
        service = ReportService(Path("/tmp"))
        result = QuizResult(
            quiz_id="test_002",
            completed_at="2026-03-23T10:00:00",
            total_questions=10,
            correct_answers=5,
            score_percentage=50.0,
            passed=False,
            failures=[
                {
                    "question_id": 1,
                    "question": "What is 2+2?",
                    "user_answer": "5",
                    "correct_answer": "4",
                }
            ],
            time_spent=120.0,
        )
        quiz = Quiz(
            quiz_id="test_002",
            created_at="2026-03-23T09:00:00",
            source_file="test.csv",
            questions=[],
        )

        html = service.generate_html_report(result, quiz)

        assert "FAIL" in html
        assert "50.0%" in html
        assert "Failed Questions" in html
        assert "What is 2+2?" in html
        assert "Your Answer:" in html
        assert "Correct Answer:" in html

    def test_generate_report_with_multiple_failures(self):
        """Test HTML report with multiple failed questions."""
        service = ReportService(Path("/tmp"))
        result = QuizResult(
            quiz_id="test_003",
            completed_at="2026-03-23T10:00:00",
            total_questions=10,
            correct_answers=7,
            score_percentage=70.0,
            passed=False,
            failures=[
                {
                    "question_id": 1,
                    "question": "Question 1?",
                    "user_answer": "Wrong 1",
                    "correct_answer": "Right 1",
                },
                {
                    "question_id": 5,
                    "question": "Question 5?",
                    "user_answer": "Wrong 5",
                    "correct_answer": "Right 5",
                },
                {
                    "question_id": 8,
                    "question": "Question 8?",
                    "user_answer": "Wrong 8",
                    "correct_answer": "Right 8",
                },
            ],
            time_spent=180.0,
        )
        quiz = Quiz(
            quiz_id="test_003",
            created_at="2026-03-23T09:00:00",
            source_file="test.csv",
            questions=[],
        )

        html = service.generate_html_report(result, quiz)

        assert "Failed Questions (3)" in html
        assert "Question 1?" in html
        assert "Question 5?" in html
        assert "Question 8?" in html

    def test_generate_report_contains_metadata(self):
        """Test HTML report contains all metadata."""
        service = ReportService(Path("/tmp"))
        result = QuizResult(
            quiz_id="metadata_test",
            completed_at="2026-03-23T15:30:00",
            total_questions=20,
            correct_answers=18,
            score_percentage=90.0,
            passed=True,
            failures=[],
            time_spent=300.0,  # 5 minutes
        )
        quiz = Quiz(
            quiz_id="metadata_test",
            created_at="2026-03-23T15:00:00",
            source_file="metadata.csv",
            questions=[],
        )

        html = service.generate_html_report(result, quiz)

        assert "metadata_test" in html
        assert "2026-03-23" in html
        assert "5m 0s" in html  # Time spent formatting
        assert "metadata.csv" in html

    def test_generate_report_valid_html_structure(self):
        """Test generated HTML has valid structure."""
        service = ReportService(Path("/tmp"))
        result = QuizResult(
            quiz_id="structure_test",
            completed_at="2026-03-23T10:00:00",
            total_questions=5,
            correct_answers=5,
            score_percentage=100.0,
            passed=True,
            failures=[],
            time_spent=60.0,
        )
        quiz = Quiz(
            quiz_id="structure_test",
            created_at="2026-03-23T09:00:00",
            source_file="test.csv",
            questions=[],
        )

        html = service.generate_html_report(result, quiz)

        assert html.startswith("<!DOCTYPE html>")
        assert "<html lang=\"en\">" in html
        assert "<head>" in html
        assert "<title>" in html
        assert "<body>" in html
        assert "</html>" in html


class TestReportServiceSaveReport:
    """Tests for save_report method."""

    def test_save_report_creates_file(self, tmp_path):
        """Test saving report creates HTML file."""
        service = ReportService(tmp_path)
        result = QuizResult(
            quiz_id="save_test_001",
            completed_at="2026-03-23T10:00:00",
            total_questions=10,
            correct_answers=8,
            score_percentage=80.0,
            passed=True,
            failures=[],
            time_spent=120.0,
        )
        quiz = Quiz(
            quiz_id="save_test_001",
            created_at="2026-03-23T09:00:00",
            source_file="test.csv",
            questions=[],
        )

        report_path = service.save_report(result, quiz)

        assert report_path.exists()
        assert report_path.name == "save_test_001_report.html"
        assert report_path.parent == tmp_path

    def test_save_report_creates_directory(self, tmp_path):
        """Test saving report creates directory if needed."""
        reports_dir = tmp_path / "reports"
        service = ReportService(reports_dir)
        result = QuizResult(
            quiz_id="dir_test",
            completed_at="2026-03-23T10:00:00",
            total_questions=5,
            correct_answers=5,
            score_percentage=100.0,
            passed=True,
            failures=[],
            time_spent=60.0,
        )
        quiz = Quiz(
            quiz_id="dir_test",
            created_at="2026-03-23T09:00:00",
            source_file="test.csv",
            questions=[],
        )

        report_path = service.save_report(result, quiz, create_dirs=True)

        assert reports_dir.exists()
        assert report_path.exists()

    def test_save_report_without_create_dirs_fails(self, tmp_path):
        """Test saving report without create_dirs raises error."""
        reports_dir = tmp_path / "nonexistent"
        service = ReportService(reports_dir)
        result = QuizResult(
            quiz_id="fail_test",
            completed_at="2026-03-23T10:00:00",
            total_questions=5,
            correct_answers=5,
            score_percentage=100.0,
            passed=True,
            failures=[],
            time_spent=60.0,
        )
        quiz = Quiz(
            quiz_id="fail_test",
            created_at="2026-03-23T09:00:00",
            source_file="test.csv",
            questions=[],
        )

        with pytest.raises(FileNotFoundError):
            service.save_report(result, quiz, create_dirs=False)

    def test_save_report_overwrites_existing(self, tmp_path):
        """Test saving report overwrites existing file."""
        service = ReportService(tmp_path)

        # Create first result (failing)
        result1 = QuizResult(
            quiz_id="overwrite_test",
            completed_at="2026-03-23T10:00:00",
            total_questions=10,
            correct_answers=5,
            score_percentage=50.0,
            passed=False,
            failures=[
                {
                    "question_id": 1,
                    "question": "Test question?",
                    "user_answer": "Wrong",
                    "correct_answer": "Right",
                }
            ],
            time_spent=120.0,
        )
        quiz = Quiz(
            quiz_id="overwrite_test",
            created_at="2026-03-23T09:00:00",
            source_file="test.csv",
            questions=[],
        )

        # Save first time
        report_path1 = service.save_report(result1, quiz)
        with open(report_path1, "r", encoding="utf-8") as f:
            content1 = f.read()

        # Create second result (passing, different data)
        result2 = QuizResult(
            quiz_id="overwrite_test",
            completed_at="2026-03-23T11:00:00",
            total_questions=10,
            correct_answers=10,
            score_percentage=100.0,
            passed=True,
            failures=[],
            time_spent=180.0,
        )

        # Save again with different result
        report_path2 = service.save_report(result2, quiz)
        with open(report_path2, "r", encoding="utf-8") as f:
            content2 = f.read()

        assert report_path1 == report_path2  # Same file
        assert content1 != content2  # Content changed
        assert "FAIL" in content1
        assert "PASS" in content2
        assert "50.0%" in content1
        assert "100.0%" in content2

    def test_save_report_content_readable(self, tmp_path):
        """Test saved report content is readable."""
        service = ReportService(tmp_path)
        result = QuizResult(
            quiz_id="readable_test",
            completed_at="2026-03-23T10:00:00",
            total_questions=10,
            correct_answers=10,
            score_percentage=100.0,
            passed=True,
            failures=[],
            time_spent=120.0,
        )
        quiz = Quiz(
            quiz_id="readable_test",
            created_at="2026-03-23T09:00:00",
            source_file="test.csv",
            questions=[],
        )

        report_path = service.save_report(result, quiz)

        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Quiz Report" in content
        assert "readable_test" in content
        assert "100.0%" in content


class TestReportServiceListReports:
    """Tests for list_reports method."""

    def test_list_reports_empty_directory(self, tmp_path):
        """Test listing reports from empty directory."""
        service = ReportService(tmp_path)
        reports = service.list_reports()

        assert reports == []

    def test_list_reports_nonexistent_directory(self, tmp_path):
        """Test listing reports from nonexistent directory."""
        service = ReportService(tmp_path / "nonexistent")
        reports = service.list_reports()

        assert reports == []

    def test_list_reports_with_files(self, tmp_path):
        """Test listing reports from directory with report files."""
        service = ReportService(tmp_path)

        # Create three reports
        for i in range(3):
            result = QuizResult(
                quiz_id=f"quiz_{i}",
                completed_at=f"2026-03-{20 + i}T10:00:00",
                total_questions=10,
                correct_answers=8,
                score_percentage=80.0,
                passed=True,
                failures=[],
                time_spent=120.0,
            )
            quiz = Quiz(
                quiz_id=f"quiz_{i}",
                created_at=f"2026-03-{20 + i}T09:00:00",
                source_file=f"test_{i}.csv",
                questions=[],
            )
            service.save_report(result, quiz)

        reports = service.list_reports()

        assert len(reports) == 3
        assert all(isinstance(r, ReportMetadata) for r in reports)
        assert all(r.quiz_id.startswith("quiz_") for r in reports)

    def test_list_reports_ignores_non_report_files(self, tmp_path):
        """Test listing ignores non-report files."""
        service = ReportService(tmp_path)

        # Create a report
        result = QuizResult(
            quiz_id="real_quiz",
            completed_at="2026-03-23T10:00:00",
            total_questions=10,
            correct_answers=8,
            score_percentage=80.0,
            passed=True,
            failures=[],
            time_spent=120.0,
        )
        quiz = Quiz(
            quiz_id="real_quiz",
            created_at="2026-03-23T09:00:00",
            source_file="test.csv",
            questions=[],
        )
        service.save_report(result, quiz)

        # Create non-report files
        (tmp_path / "random.txt").write_text("not a report")
        (tmp_path / "data.json").write_text("{}")
        (tmp_path / "other.html").write_text("<html></html>")

        reports = service.list_reports()

        assert len(reports) == 1
        assert reports[0].quiz_id == "real_quiz"

    def test_list_reports_sorted_by_date(self, tmp_path):
        """Test reports are sorted by creation date (newest first)."""
        service = ReportService(tmp_path)
        import time

        # Create reports with slight delay to ensure different timestamps
        quiz_ids = ["first", "second", "third"]
        for quiz_id in quiz_ids:
            result = QuizResult(
                quiz_id=quiz_id,
                completed_at="2026-03-23T10:00:00",
                total_questions=5,
                correct_answers=5,
                score_percentage=100.0,
                passed=True,
                failures=[],
                time_spent=60.0,
            )
            quiz = Quiz(
                quiz_id=quiz_id,
                created_at="2026-03-23T09:00:00",
                source_file="test.csv",
                questions=[],
            )
            service.save_report(result, quiz)
            time.sleep(0.01)  # Small delay to ensure different timestamps

        reports = service.list_reports()

        # Should be sorted newest first (reverse chronological)
        assert reports[0].quiz_id == "third"
        assert reports[-1].quiz_id == "first"


class TestReportServiceReportExists:
    """Tests for report_exists method."""

    def test_report_exists_true(self, tmp_path):
        """Test report_exists returns True for existing report."""
        service = ReportService(tmp_path)
        result = QuizResult(
            quiz_id="exists_test",
            completed_at="2026-03-23T10:00:00",
            total_questions=5,
            correct_answers=5,
            score_percentage=100.0,
            passed=True,
            failures=[],
            time_spent=60.0,
        )
        quiz = Quiz(
            quiz_id="exists_test",
            created_at="2026-03-23T09:00:00",
            source_file="test.csv",
            questions=[],
        )
        service.save_report(result, quiz)

        assert service.report_exists("exists_test") is True

    def test_report_exists_false(self, tmp_path):
        """Test report_exists returns False for nonexistent report."""
        service = ReportService(tmp_path)
        assert service.report_exists("nonexistent") is False


class TestReportServiceGetReportPath:
    """Tests for get_report_path method."""

    def test_get_report_path_exists(self, tmp_path):
        """Test get_report_path returns path for existing report."""
        service = ReportService(tmp_path)
        result = QuizResult(
            quiz_id="path_test",
            completed_at="2026-03-23T10:00:00",
            total_questions=5,
            correct_answers=5,
            score_percentage=100.0,
            passed=True,
            failures=[],
            time_spent=60.0,
        )
        quiz = Quiz(
            quiz_id="path_test",
            created_at="2026-03-23T09:00:00",
            source_file="test.csv",
            questions=[],
        )
        service.save_report(result, quiz)

        path = service.get_report_path("path_test")

        assert path is not None
        assert path.exists()
        assert path.name == "path_test_report.html"

    def test_get_report_path_nonexistent(self, tmp_path):
        """Test get_report_path returns None for nonexistent report."""
        service = ReportService(tmp_path)
        path = service.get_report_path("nonexistent")

        assert path is None


class TestReportServiceGetReportCount:
    """Tests for get_report_count method."""

    def test_get_report_count_empty(self, tmp_path):
        """Test count of reports in empty directory."""
        service = ReportService(tmp_path)
        count = service.get_report_count()

        assert count == 0

    def test_get_report_count_with_reports(self, tmp_path):
        """Test count of reports with multiple files."""
        service = ReportService(tmp_path)

        # Create 5 reports
        for i in range(5):
            result = QuizResult(
                quiz_id=f"count_test_{i}",
                completed_at="2026-03-23T10:00:00",
                total_questions=5,
                correct_answers=5,
                score_percentage=100.0,
                passed=True,
                failures=[],
                time_spent=60.0,
            )
            quiz = Quiz(
                quiz_id=f"count_test_{i}",
                created_at="2026-03-23T09:00:00",
                source_file="test.csv",
                questions=[],
            )
            service.save_report(result, quiz)

        count = service.get_report_count()

        assert count == 5


class TestReportServiceDeleteReport:
    """Tests for delete_report method."""

    def test_delete_report_success(self, tmp_path):
        """Test deleting existing report."""
        service = ReportService(tmp_path)
        result = QuizResult(
            quiz_id="delete_test",
            completed_at="2026-03-23T10:00:00",
            total_questions=5,
            correct_answers=5,
            score_percentage=100.0,
            passed=True,
            failures=[],
            time_spent=60.0,
        )
        quiz = Quiz(
            quiz_id="delete_test",
            created_at="2026-03-23T09:00:00",
            source_file="test.csv",
            questions=[],
        )
        service.save_report(result, quiz)

        assert service.report_exists("delete_test") is True

        deleted = service.delete_report("delete_test")

        assert deleted is True
        assert service.report_exists("delete_test") is False

    def test_delete_report_nonexistent(self, tmp_path):
        """Test deleting nonexistent report returns False."""
        service = ReportService(tmp_path)

        deleted = service.delete_report("nonexistent")

        assert deleted is False


class TestReportServiceIntegration:
    """Integration tests for ReportService."""

    def test_full_workflow(self, tmp_path):
        """Test complete workflow: generate, save, list, verify, delete."""
        service = ReportService(tmp_path)

        # Create and save 3 reports
        quiz_ids = ["workflow_1", "workflow_2", "workflow_3"]
        for quiz_id in quiz_ids:
            result = QuizResult(
                quiz_id=quiz_id,
                completed_at="2026-03-23T10:00:00",
                total_questions=10,
                correct_answers=8,
                score_percentage=80.0,
                passed=True,
                failures=[],
                time_spent=120.0,
            )
            quiz = Quiz(
                quiz_id=quiz_id,
                created_at="2026-03-23T09:00:00",
                source_file="test.csv",
                questions=[],
            )
            service.save_report(result, quiz)

        # List reports
        reports = service.list_reports()
        assert len(reports) == 3

        # Verify each report exists
        for quiz_id in quiz_ids:
            assert service.report_exists(quiz_id) is True
            path = service.get_report_path(quiz_id)
            assert path is not None
            assert path.exists()

        # Count reports
        assert service.get_report_count() == 3

        # Delete one report
        service.delete_report("workflow_2")
        assert service.get_report_count() == 2
        assert service.report_exists("workflow_1") is True
        assert service.report_exists("workflow_2") is False
        assert service.report_exists("workflow_3") is True
