"""
Tests for QuizService.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import json
from pathlib import Path

import pytest

from quizzer.exceptions import InvalidQuizPathError
from quizzer.services import QuizMetadata, QuizService


class TestQuizMetadata:
    """Tests for QuizMetadata dataclass."""

    def test_metadata_creation(self):
        """Test creating QuizMetadata."""
        metadata = QuizMetadata(
            path="data/quizzes/quiz_001.json",
            quiz_id="quiz_001",
            num_questions=50,
            source_file="sample.csv",
            created_at="2026-03-23T10:00:00",
        )

        assert metadata.path == "data/quizzes/quiz_001.json"
        assert metadata.quiz_id == "quiz_001"
        assert metadata.num_questions == 50
        assert metadata.source_file == "sample.csv"
        assert metadata.created_at == "2026-03-23T10:00:00"

    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = QuizMetadata(
            path="data/quizzes/quiz_001.json",
            quiz_id="quiz_001",
            num_questions=50,
            source_file="sample.csv",
            created_at="2026-03-23T10:00:00",
        )

        result = metadata.to_dict()

        assert result == {
            "path": "data/quizzes/quiz_001.json",
            "quiz_id": "quiz_001",
            "num_questions": 50,
            "source_file": "sample.csv",
            "created_at": "2026-03-23T10:00:00",
        }


class TestQuizServiceInit:
    """Tests for QuizService initialization."""

    def test_init_with_path(self):
        """Test initializing service with path."""
        service = QuizService(Path("data/quizzes"))
        assert service.quizzes_dir == Path("data/quizzes")

    def test_init_with_string(self):
        """Test initializing service with string path."""
        service = QuizService("data/quizzes")
        assert service.quizzes_dir == Path("data/quizzes")


class TestQuizServiceLoadMetadata:
    """Tests for QuizService.load_metadata() method."""

    def test_load_metadata_success(self, tmp_path):
        """Test successfully loading quiz metadata."""
        # Create test quiz file
        quiz_file = tmp_path / "quiz_001.json"
        quiz_data = {
            "quiz_id": "quiz_001",
            "created_at": "2026-03-23T10:00:00",
            "questions": [{"id": 1}] * 25,
            "source_file": "test.csv",
        }
        quiz_file.write_text(json.dumps(quiz_data))

        service = QuizService(tmp_path)
        metadata = service.load_metadata(quiz_file)

        assert metadata is not None
        assert metadata.quiz_id == "quiz_001"
        assert metadata.num_questions == 25
        assert metadata.source_file == "test.csv"
        assert metadata.created_at == "2026-03-23T10:00:00"

    def test_load_metadata_missing_fields(self, tmp_path):
        """Test loading metadata with missing optional fields."""
        quiz_file = tmp_path / "quiz_002.json"
        quiz_data = {"questions": [{"id": 1}] * 10}
        quiz_file.write_text(json.dumps(quiz_data))

        service = QuizService(tmp_path)
        metadata = service.load_metadata(quiz_file)

        assert metadata is not None
        assert metadata.quiz_id == "quiz_002"  # Falls back to filename
        assert metadata.num_questions == 10
        assert metadata.source_file == ""
        assert metadata.created_at == ""

    def test_load_metadata_invalid_json(self, tmp_path):
        """Test loading metadata from invalid JSON."""
        quiz_file = tmp_path / "invalid.json"
        quiz_file.write_text("{ invalid json")

        service = QuizService(tmp_path)
        metadata = service.load_metadata(quiz_file)

        assert metadata is None

    def test_load_metadata_file_not_found(self, tmp_path):
        """Test loading metadata from nonexistent file."""
        quiz_file = tmp_path / "nonexistent.json"

        service = QuizService(tmp_path)
        metadata = service.load_metadata(quiz_file)

        assert metadata is None

    def test_load_metadata_preserves_path(self, tmp_path):
        """Test that metadata preserves full file path."""
        quiz_file = tmp_path / "subfolder" / "quiz.json"
        quiz_file.parent.mkdir(parents=True)
        quiz_data = {"questions": []}
        quiz_file.write_text(json.dumps(quiz_data))

        service = QuizService(tmp_path)
        metadata = service.load_metadata(quiz_file)

        assert str(quiz_file) in metadata.path


class TestQuizServiceListQuizzes:
    """Tests for QuizService.list_quizzes() method."""

    def test_list_quizzes_empty_directory(self, tmp_path):
        """Test listing quizzes from empty directory."""
        service = QuizService(tmp_path)
        quizzes = service.list_quizzes()

        assert quizzes == []

    def test_list_quizzes_nonexistent_directory(self, tmp_path):
        """Test listing quizzes from nonexistent directory."""
        service = QuizService(tmp_path / "nonexistent")
        quizzes = service.list_quizzes()

        assert quizzes == []

    def test_list_quizzes_with_files(self, tmp_path):
        """Test listing quizzes from directory with quiz files."""
        for i in range(3):
            quiz_file = tmp_path / f"quiz_{i}.json"
            quiz_data = {
                "quiz_id": f"quiz_{i}",
                "created_at": f"2026-03-{20+i}T10:00:00",
                "questions": [{"id": 1}] * (i + 1),
                "source_file": f"source_{i}.csv",
            }
            quiz_file.write_text(json.dumps(quiz_data))

        service = QuizService(tmp_path)
        quizzes = service.list_quizzes()

        assert len(quizzes) == 3
        assert all(isinstance(q, QuizMetadata) for q in quizzes)

    def test_list_quizzes_sorted_by_date(self, tmp_path):
        """Test quizzes are sorted by creation date (newest first)."""
        dates = ["2026-03-20", "2026-03-22", "2026-03-21"]
        for i, date in enumerate(dates):
            quiz_file = tmp_path / f"quiz_{i}.json"
            quiz_data = {
                "quiz_id": f"quiz_{i}",
                "created_at": f"{date}T10:00:00",
                "questions": [],
                "source_file": f"source_{i}.csv",
            }
            quiz_file.write_text(json.dumps(quiz_data))

        service = QuizService(tmp_path)
        quizzes = service.list_quizzes()

        assert quizzes[0].quiz_id == "quiz_1"  # 2026-03-22
        assert quizzes[1].quiz_id == "quiz_2"  # 2026-03-21
        assert quizzes[2].quiz_id == "quiz_0"  # 2026-03-20

    def test_list_quizzes_skips_last_import(self, tmp_path):
        """Test that last_import.json is skipped."""
        (tmp_path / "last_import.json").write_text("{}")

        quiz_file = tmp_path / "quiz_001.json"
        quiz_data = {
            "quiz_id": "quiz_001",
            "created_at": "2026-03-23T10:00:00",
            "questions": [],
            "source_file": "test.csv",
        }
        quiz_file.write_text(json.dumps(quiz_data))

        service = QuizService(tmp_path)
        quizzes = service.list_quizzes()

        assert len(quizzes) == 1
        assert quizzes[0].quiz_id == "quiz_001"

    def test_list_quizzes_skips_test_data(self, tmp_path):
        """Test that test data is skipped in production mode."""
        sample_dir = tmp_path / "sample_questions"
        sample_dir.mkdir()
        (sample_dir / "sample.json").write_text(json.dumps({
            "quiz_id": "sample",
            "created_at": "2026-03-23T10:00:00",
            "questions": [],
            "source_file": "sample.csv",
        }))

        (tmp_path / "quiz_001.json").write_text(json.dumps({
            "quiz_id": "quiz_001",
            "created_at": "2026-03-23T10:00:00",
            "questions": [],
            "source_file": "test.csv",
        }))

        service = QuizService(tmp_path)

        quizzes = service.list_quizzes(include_test_data=False)
        assert len(quizzes) == 1
        assert quizzes[0].quiz_id == "quiz_001"

        quizzes = service.list_quizzes(include_test_data=True)
        assert len(quizzes) == 2

    def test_list_quizzes_recursive(self, tmp_path):
        """Test listing quizzes from nested directories."""
        (tmp_path / "folder1" / "folder2").mkdir(parents=True)

        quiz_template = {
            "created_at": "2026-03-23T10:00:00",
            "questions": [],
            "source_file": "test.csv",
        }

        paths = [
            (tmp_path / "quiz1.json", "quiz1"),
            (tmp_path / "folder1" / "quiz2.json", "quiz2"),
            (tmp_path / "folder1" / "folder2" / "quiz3.json", "quiz3"),
        ]

        for path, quiz_id in paths:
            data = {**quiz_template, "quiz_id": quiz_id}
            path.write_text(json.dumps(data))

        service = QuizService(tmp_path)
        quizzes = service.list_quizzes()

        assert len(quizzes) == 3

    def test_list_quizzes_ignores_invalid_files(self, tmp_path):
        """Test that invalid JSON files are skipped."""
        (tmp_path / "invalid.json").write_text("{ bad json")

        (tmp_path / "valid.json").write_text(json.dumps({
            "quiz_id": "valid",
            "created_at": "2026-03-23T10:00:00",
            "questions": [],
            "source_file": "test.csv",
        }))

        service = QuizService(tmp_path)
        quizzes = service.list_quizzes()

        assert len(quizzes) == 1
        assert quizzes[0].quiz_id == "valid"


class TestQuizServiceLoadQuiz:
    """Tests for QuizService.load_quiz() method."""

    def test_load_quiz_success(self, tmp_path):
        """Test successfully loading a quiz."""
        quiz_file = tmp_path / "quiz_001.json"
        quiz_data = {
            "quiz_id": "quiz_001",
            "created_at": "2026-03-23T10:00:00",
            "questions": [
                {"id": 1, "question": "Test?", "answer": "test", "original_answer": "Test"}
            ],
            "source_file": "test.csv",
        }
        quiz_file.write_text(json.dumps(quiz_data))

        service = QuizService(tmp_path)
        quiz = service.load_quiz(str(quiz_file))

        assert quiz.quiz_id == "quiz_001"
        assert len(quiz.questions) == 1
        assert quiz.questions[0].question == "Test?"

    def test_load_quiz_with_relative_path(self, tmp_path):
        """Test loading quiz with relative path."""
        quiz_file = tmp_path / "quiz_001.json"
        quiz_data = {
            "quiz_id": "quiz_001",
            "created_at": "2026-03-23T10:00:00",
            "questions": [],
            "source_file": "test.csv",
        }
        quiz_file.write_text(json.dumps(quiz_data))

        service = QuizService(tmp_path)
        quiz = service.load_quiz("quiz_001.json")

        assert quiz.quiz_id == "quiz_001"

    def test_load_quiz_file_not_found(self, tmp_path):
        """Test loading nonexistent quiz raises FileNotFoundError."""
        service = QuizService(tmp_path)

        with pytest.raises(FileNotFoundError):
            service.load_quiz("nonexistent.json")

    def test_load_quiz_invalid_path(self, tmp_path):
        """Test loading quiz with path traversal raises InvalidQuizPathError."""
        service = QuizService(tmp_path)

        with pytest.raises(InvalidQuizPathError):
            service.load_quiz("../../../etc/passwd")

    def test_load_quiz_absolute_path_outside_dir(self, tmp_path):
        """Test loading quiz from outside quizzes_dir raises error."""
        service = QuizService(tmp_path)

        with pytest.raises(InvalidQuizPathError):
            service.load_quiz("/etc/passwd")


class TestQuizServiceQuizExists:
    """Tests for QuizService.quiz_exists() method."""

    def test_quiz_exists_true(self, tmp_path):
        """Test quiz_exists returns True for existing file."""
        quiz_file = tmp_path / "quiz_001.json"
        quiz_file.write_text(json.dumps({
            "quiz_id": "quiz_001",
            "created_at": "2026-03-23T10:00:00",
            "questions": [],
            "source_file": "test.csv",
        }))

        service = QuizService(tmp_path)
        assert service.quiz_exists(str(quiz_file)) is True

    def test_quiz_exists_false(self, tmp_path):
        """Test quiz_exists returns False for nonexistent file."""
        service = QuizService(tmp_path)
        assert service.quiz_exists("nonexistent.json") is False

    def test_quiz_exists_invalid_path(self, tmp_path):
        """Test quiz_exists returns False for invalid path."""
        service = QuizService(tmp_path)
        assert service.quiz_exists("../../../etc/passwd") is False


class TestQuizServiceGetQuizCount:
    """Tests for QuizService.get_quiz_count() method."""

    def test_get_quiz_count_empty(self, tmp_path):
        """Test quiz count for empty directory."""
        service = QuizService(tmp_path)
        assert service.get_quiz_count() == 0

    def test_get_quiz_count_with_quizzes(self, tmp_path):
        """Test quiz count with multiple quizzes."""
        quiz_template = {
            "created_at": "2026-03-23T10:00:00",
            "questions": [],
            "source_file": "test.csv",
        }
        for i in range(5):
            quiz_file = tmp_path / f"quiz_{i}.json"
            data = {**quiz_template, "quiz_id": f"quiz_{i}"}
            quiz_file.write_text(json.dumps(data))

        service = QuizService(tmp_path)
        assert service.get_quiz_count() == 5

    def test_get_quiz_count_exclude_test_data(self, tmp_path):
        """Test quiz count excludes test data by default."""
        sample_dir = tmp_path / "sample"
        sample_dir.mkdir()
        (sample_dir / "sample.json").write_text(json.dumps({
            "quiz_id": "sample",
            "created_at": "2026-03-23T10:00:00",
            "questions": [],
            "source_file": "sample.csv",
        }))

        (tmp_path / "quiz.json").write_text(json.dumps({
            "quiz_id": "quiz",
            "created_at": "2026-03-23T10:00:00",
            "questions": [],
            "source_file": "test.csv",
        }))

        service = QuizService(tmp_path)

        assert service.get_quiz_count(include_test_data=False) == 1
        assert service.get_quiz_count(include_test_data=True) == 2


class TestQuizServiceIntegration:
    """Integration tests for QuizService."""

    def test_full_workflow(self, tmp_path):
        """Test complete workflow: list, check, load."""
        for i in range(3):
            quiz_file = tmp_path / f"quiz_{i}.json"
            quiz_data = {
                "quiz_id": f"quiz_{i}",
                "created_at": f"2026-03-{20+i}T10:00:00",
                "questions": [
                    {
                        "id": 1,
                        "question": f"Question {i}?",
                        "answer": f"answer{i}",
                        "original_answer": f"Answer{i}",
                    }
                ],
                "source_file": f"source_{i}.csv",
            }
            quiz_file.write_text(json.dumps(quiz_data))

        service = QuizService(tmp_path)

        quizzes = service.list_quizzes()
        assert len(quizzes) == 3

        assert service.quiz_exists(quizzes[0].path)

        quiz = service.load_quiz(quizzes[0].path)
        assert quiz.quiz_id == quizzes[0].quiz_id
        assert len(quiz.questions) == quizzes[0].num_questions

        assert service.get_quiz_count() == 3
