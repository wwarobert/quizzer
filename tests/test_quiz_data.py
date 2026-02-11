"""
Unit tests for quiz_data module.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from quizzer.quiz_data import Question, Quiz, QuizResult


class TestQuestion:
    """Tests for Question class."""

    def test_create_question(self):
        """Test creating a Question object."""
        q = Question(
            id=1,
            question="What is the capital of France?",
            answer=["paris"],
            original_answer="Paris"
        )
        assert q.id == 1
        assert q.question == "What is the capital of France?"
        assert q.answer == ["paris"]
        assert q.original_answer == "Paris"

    def test_to_dict(self):
        """Test converting Question to dictionary."""
        q = Question(
            id=1,
            question="Test question?",
            answer=["test"],
            original_answer="Test"
        )
        d = q.to_dict()
        assert d["id"] == 1
        assert d["question"] == "Test question?"
        assert d["answer"] == ["test"]
        assert d["original_answer"] == "Test"

    def test_from_dict(self):
        """Test creating Question from dictionary."""
        data = {
            "id": 2,
            "question": "Test?",
            "answer": ["blue", "red"],
            "original_answer": "red, blue"
        }
        q = Question.from_dict(data)
        assert q.id == 2
        assert q.question == "Test?"
        assert q.answer == ["blue", "red"]
        assert q.original_answer == "red, blue"


class TestQuiz:
    """Tests for Quiz class."""

    def test_create_quiz(self):
        """Test creating a Quiz object."""
        questions = [
            Question(1, "Q1?", ["a"], "A"),
            Question(2, "Q2?", ["b"], "B")
        ]
        quiz = Quiz(
            quiz_id="test_001",
            created_at="2026-02-06T10:00:00",
            questions=questions,
            source_file="test.csv"
        )
        assert quiz.quiz_id == "test_001"
        assert quiz.created_at == "2026-02-06T10:00:00"
        assert len(quiz.questions) == 2
        assert quiz.source_file == "test.csv"

    def test_to_dict(self):
        """Test converting Quiz to dictionary."""
        questions = [Question(1, "Q?", ["a"], "A")]
        quiz = Quiz("quiz_001", "2026-02-06T10:00:00", questions, "test.csv")
        d = quiz.to_dict()
        assert d["quiz_id"] == "quiz_001"
        assert d["created_at"] == "2026-02-06T10:00:00"
        assert d["source_file"] == "test.csv"
        assert len(d["questions"]) == 1
        assert d["questions"][0]["id"] == 1

    def test_from_dict(self):
        """Test creating Quiz from dictionary."""
        data = {
            "quiz_id": "quiz_002",
            "created_at": "2026-02-06T11:00:00",
            "source_file": "sample.csv",
            "questions": [
                {"id": 1, "question": "Q?", "answer": ["a"], "original_answer": "A"}
            ]
        }
        quiz = Quiz.from_dict(data)
        assert quiz.quiz_id == "quiz_002"
        assert len(quiz.questions) == 1
        assert quiz.questions[0].question == "Q?"

    def test_save_and_load(self):
        """Test saving and loading quiz from JSON file."""
        questions = [
            Question(1, "What is 2+2?", ["4"], "4"),
            Question(2, "Capital of France?", ["paris"], "Paris")
        ]
        quiz = Quiz("quiz_003", "2026-02-06T12:00:00", questions, "test.csv")

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            quiz.save(temp_path)

            # Verify file exists and is valid JSON
            assert Path(temp_path).exists()
            with open(temp_path, 'r') as f:
                data = json.load(f)
                assert data["quiz_id"] == "quiz_003"

            # Load quiz back
            loaded_quiz = Quiz.load(temp_path)
            assert loaded_quiz.quiz_id == quiz.quiz_id
            assert len(loaded_quiz.questions) == len(quiz.questions)
            assert loaded_quiz.questions[0].question == questions[0].question
        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)


class TestQuizResult:
    """Tests for QuizResult class."""

    def test_create_result_pass(self):
        """Test creating a passing QuizResult."""
        result = QuizResult(
            quiz_id="quiz_001",
            completed_at="2026-02-06T13:00:00",
            total_questions=10,
            correct_answers=9,
            score_percentage=90.0,
            passed=True,
            failures=[]
        )
        assert result.quiz_id == "quiz_001"
        assert result.total_questions == 10
        assert result.correct_answers == 9
        assert result.score_percentage == 90.0
        assert result.passed is True
        assert len(result.failures) == 0

    def test_create_result_fail(self):
        """Test creating a failing QuizResult."""
        failures = [
            {
                "question_id": "5",
                "question": "What is 2+2?",
                "user_answer": "5",
                "correct_answer": "4"
            }
        ]
        result = QuizResult(
            quiz_id="quiz_002",
            completed_at="2026-02-06T14:00:00",
            total_questions=10,
            correct_answers=7,
            score_percentage=70.0,
            passed=False,
            failures=failures
        )
        assert result.passed is False
        assert len(result.failures) == 1
        assert result.failures[0]["user_answer"] == "5"

    def test_generate_report_pass(self):
        """Test generating report for passing result."""
        result = QuizResult(
            quiz_id="quiz_003",
            completed_at="2026-02-06T15:00:00",
            total_questions=50,
            correct_answers=50,
            score_percentage=100.0,
            passed=True,
            failures=[]
        )
        report = result.generate_report()
        assert "quiz_003" in report
        assert "50" in report
        assert "100.0%" in report
        assert "PASS" in report
        assert "Perfect score" in report

    def test_generate_report_fail(self):
        """Test generating report for failing result."""
        failures = [
            {
                "question_id": "5",
                "question": "What is the capital of France?",
                "user_answer": "London",
                "correct_answer": "Paris"
            },
            {
                "question_id": "10",
                "question": "What is 2+2?",
                "user_answer": "5",
                "correct_answer": "4"
            }
        ]
        result = QuizResult(
            quiz_id="quiz_004",
            completed_at="2026-02-06T16:00:00",
            total_questions=50,
            correct_answers=40,
            score_percentage=80.0,
            passed=True,
            failures=failures
        )
        report = result.generate_report()
        assert "quiz_004" in report
        assert "40" in report
        assert "80.0%" in report
        assert "PASS" in report
        assert "Failures (2)" in report
        assert "London" in report
        assert "Paris" in report

    def test_save_report(self):
        """Test saving report to file."""
        result = QuizResult(
            quiz_id="quiz_005",
            completed_at="2026-02-06T17:00:00",
            total_questions=25,
            correct_answers=20,
            score_percentage=80.0,
            passed=True,
            failures=[]
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name

        try:
            result.save_report(temp_path)
            assert Path(temp_path).exists()

            with open(temp_path, 'r') as f:
                content = f.read()
                assert "quiz_005" in content
                assert "80.0%" in content
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_to_dict(self):
        """Test converting QuizResult to dictionary."""
        result = QuizResult(
            quiz_id="quiz_006",
            completed_at="2026-02-06T18:00:00",
            total_questions=10,
            correct_answers=8,
            score_percentage=80.0,
            passed=True,
            failures=[]
        )
        d = result.to_dict()
        assert d["quiz_id"] == "quiz_006"
        assert d["total_questions"] == 10
        assert d["correct_answers"] == 8
        assert d["passed"] is True


class TestQuestionEdgeCases:
    """Additional edge case tests for Question class."""

    def test_question_with_unicode(self):
        """Test Question with Unicode characters."""
        q = Question(1, "What is café?", ["coffee shop"], "Coffee shop")
        assert "café" in q.question
        assert q.to_dict()["question"] == "What is café?"

    def test_question_with_empty_answer_list(self):
        """Test Question with empty answer list."""
        q = Question(1, "Empty?", [], "")
        assert len(q.answer) == 0
        assert q.original_answer == ""

    def test_question_with_large_id(self):
        """Test Question with large ID number."""
        q = Question(1000000, "Large ID?", ["yes"], "Yes")
        assert q.id == 1000000

    def test_question_with_multiline_text(self):
        """Test Question with multiline question text."""
        q = Question(1, "What is\na multiline\nquestion?", ["answer"], "Answer")
        assert "\n" in q.question
        d = q.to_dict()
        assert "\n" in d["question"]

    def test_question_with_long_answer_list(self):
        """Test Question with very long answer list."""
        long_list = [f"item{i}" for i in range(200)]
        q = Question(1, "List items?", long_list, ", ".join(long_list))
        assert len(q.answer) == 200
        d = q.to_dict()
        assert len(d["answer"]) == 200

    def test_question_serialization_deserialization(self):
        """Test that Question survives serialization round-trip."""
        q1 = Question(42, "Test question?", ["a", "b", "c"], "A, B, C")
        d = q1.to_dict()
        q2 = Question.from_dict(d)

        assert q1.id == q2.id
        assert q1.question == q2.question
        assert q1.answer == q2.answer
        assert q1.original_answer == q2.original_answer


class TestQuizEdgeCases:
    """Additional edge case tests for Quiz class."""

    def test_quiz_with_no_questions(self):
        """Test Quiz with empty question list."""
        quiz = Quiz("empty_quiz", "2026-02-06T10:00:00", [])
        assert len(quiz.questions) == 0
        d = quiz.to_dict()
        assert len(d["questions"]) == 0

    def test_quiz_with_single_question(self):
        """Test Quiz with exactly one question."""
        q = Question(1, "Only one?", ["yes"], "Yes")
        quiz = Quiz("single_q", "2026-02-06T10:00:00", [q])
        assert len(quiz.questions) == 1

    def test_quiz_with_max_questions(self):
        """Test Quiz with 50 questions (max)."""
        questions = [Question(i, f"Q{i}?", [f"a{i}"], f"A{i}") for i in range(1, 51)]
        quiz = Quiz("max_quiz", "2026-02-06T10:00:00", questions)
        assert len(quiz.questions) == 50

    def test_quiz_with_empty_source_file(self):
        """Test Quiz with empty source_file field."""
        q = Question(1, "Q?", ["a"], "A")
        quiz = Quiz("test", "2026-02-06T10:00:00", [q], "")
        assert quiz.source_file == ""
        d = quiz.to_dict()
        assert d["source_file"] == ""

    def test_quiz_with_missing_source_file_in_dict(self):
        """Test Quiz.from_dict with missing source_file key."""
        data = {
            "quiz_id": "test",
            "created_at": "2026-02-06T10:00:00",
            "questions": [
                {"id": 1, "question": "Q?", "answer": ["a"], "original_answer": "A"}
            ]
            # No source_file key
        }
        quiz = Quiz.from_dict(data)
        assert quiz.source_file == ""  # Should default to empty string

    def test_quiz_save_creates_valid_json(self):
        """Test that saved quiz is valid JSON."""
        questions = [Question(1, "Test?", ["test"], "Test")]
        quiz = Quiz("json_test", "2026-02-06T10:00:00", questions, "test.csv")

        temp_dir = tempfile.mkdtemp()
        try:
            filepath = Path(temp_dir) / "test.json"
            quiz.save(str(filepath))

            # Verify it's valid JSON
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data["quiz_id"] == "json_test"
                assert len(data["questions"]) == 1
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_quiz_load_handles_missing_file(self):
        """Test that Quiz.load raises error for missing file."""
        with pytest.raises(FileNotFoundError):
            Quiz.load("nonexistent_file.json")

    def test_quiz_load_handles_invalid_json(self):
        """Test that Quiz.load raises error for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("not valid json {{{")
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                Quiz.load(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_quiz_serialization_preserves_order(self):
        """Test that question order is preserved through serialization."""
        questions = [Question(i, f"Q{i}?", [f"a{i}"], f"A{i}") for i in range(1, 11)]
        quiz = Quiz("order_test", "2026-02-06T10:00:00", questions)

        temp_dir = tempfile.mkdtemp()
        try:
            filepath = Path(temp_dir) / "test.json"
            quiz.save(str(filepath))
            loaded = Quiz.load(str(filepath))

            for i, q in enumerate(loaded.questions):
                assert q.id == questions[i].id
                assert q.question == questions[i].question
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_quiz_with_unicode_in_metadata(self):
        """Test Quiz with Unicode in quiz_id and source_file."""
        q = Question(1, "Test?", ["test"], "Test")
        quiz = Quiz("café_quiz", "2026-02-06T10:00:00", [q], "café.csv")

        d = quiz.to_dict()
        assert d["quiz_id"] == "café_quiz"
        assert d["source_file"] == "café.csv"


class TestQuizResultEdgeCases:
    """Additional edge case tests for QuizResult class."""

    def test_result_with_zero_questions(self):
        """Test QuizResult with zero questions."""
        result = QuizResult(
            quiz_id="empty",
            completed_at="2026-02-06T10:00:00",
            total_questions=0,
            correct_answers=0,
            score_percentage=0.0,
            passed=False,
            failures=[]
        )
        assert result.total_questions == 0
        report = result.generate_report()
        assert "0" in report

    def test_result_with_default_time_spent(self):
        """Test QuizResult with default time_spent value."""
        result = QuizResult(
            quiz_id="test",
            completed_at="2026-02-06T10:00:00",
            total_questions=10,
            correct_answers=8,
            score_percentage=80.0,
            passed=True,
            failures=[]
            # time_spent not provided, should default to 0.0
        )
        assert result.time_spent == 0.0

    def test_result_with_long_time_spent(self):
        """Test QuizResult with time over an hour."""
        result = QuizResult(
            quiz_id="long_test",
            completed_at="2026-02-06T10:00:00",
            total_questions=50,
            correct_answers=45,
            score_percentage=90.0,
            passed=True,
            failures=[],
            time_spent=3725.5  # 1 hour, 2 minutes, 5.5 seconds
        )
        report = result.generate_report()
        assert "62m" in report  # 3725 / 60 = 62 minutes

    def test_result_with_fractional_percentage(self):
        """Test QuizResult with fractional score percentage."""
        result = QuizResult(
            quiz_id="fraction",
            completed_at="2026-02-06T10:00:00",
            total_questions=3,
            correct_answers=2,
            score_percentage=66.66666666666667,
            passed=False,
            failures=[]
        )
        report = result.generate_report()
        assert "66.7%" in report  # Should be formatted to 1 decimal

    def test_result_with_many_failures(self):
        """Test QuizResult with many failed questions."""
        failures = [
            {
                "question_id": str(i),
                "question": f"Question {i}?",
                "user_answer": "wrong",
                "correct_answer": "correct"
            }
            for i in range(1, 26)  # 25 failures
        ]
        result = QuizResult(
            quiz_id="many_fails",
            completed_at="2026-02-06T10:00:00",
            total_questions=50,
            correct_answers=25,
            score_percentage=50.0,
            passed=False,
            failures=failures
        )
        report = result.generate_report()
        assert "Failures (25)" in report
        assert "Question 1?" in report
        assert "Question 25?" in report

    def test_result_report_time_formatting_seconds_only(self):
        """Test time formatting with only seconds."""
        result = QuizResult(
            quiz_id="quick",
            completed_at="2026-02-06T10:00:00",
            total_questions=5,
            correct_answers=5,
            score_percentage=100.0,
            passed=True,
            failures=[],
            time_spent=45.0
        )
        report = result.generate_report()
        assert "45s" in report
        # Should not show minutes format (like "0m 45s")
        assert "m " not in report  # More specific check

    def test_result_report_time_formatting_with_minutes(self):
        """Test time formatting with minutes and seconds."""
        result = QuizResult(
            quiz_id="normal",
            completed_at="2026-02-06T10:00:00",
            total_questions=10,
            correct_answers=8,
            score_percentage=80.0,
            passed=True,
            failures=[],
            time_spent=125.0  # 2m 5s
        )
        report = result.generate_report()
        assert "2m 5s" in report

    def test_result_with_unicode_in_failures(self):
        """Test QuizResult with Unicode in failure details."""
        failures = [
            {
                "question_id": "1",
                "question": "What is café?",
                "user_answer": "coffee",
                "correct_answer": "café"
            }
        ]
        result = QuizResult(
            quiz_id="unicode_fail",
            completed_at="2026-02-06T10:00:00",
            total_questions=1,
            correct_answers=0,
            score_percentage=0.0,
            passed=False,
            failures=failures
        )
        report = result.generate_report()
        assert "café" in report

    def test_result_with_very_long_quiz_id(self):
        """Test QuizResult with very long quiz_id."""
        long_id = "quiz_" + "x" * 200
        result = QuizResult(
            quiz_id=long_id,
            completed_at="2026-02-06T10:00:00",
            total_questions=10,
            correct_answers=10,
            score_percentage=100.0,
            passed=True,
            failures=[]
        )
        assert result.quiz_id == long_id
        report = result.generate_report()
        assert long_id in report

    def test_result_save_overwrites_existing_file(self):
        """Test that save_report overwrites existing file."""
        result = QuizResult(
            quiz_id="overwrite",
            completed_at="2026-02-06T10:00:00",
            total_questions=10,
            correct_answers=8,
            score_percentage=80.0,
            passed=True,
            failures=[]
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Old content")
            temp_path = f.name

        try:
            result.save_report(temp_path)

            with open(temp_path, 'r') as f:
                content = f.read()
                assert "Old content" not in content
                assert "overwrite" in content
        finally:
            Path(temp_path).unlink(missing_ok=True)
