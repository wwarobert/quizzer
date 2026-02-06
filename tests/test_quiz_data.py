"""
Unit tests for quiz_data module.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import pytest
import json
import tempfile
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
