"""
Integration tests for run_quiz script.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from quizzer.quiz_data import Question, Quiz, QuizResult
import importlib.util

# Import the run_quiz module
spec = importlib.util.spec_from_file_location("run_quiz", "run_quiz.py")
run_quiz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_quiz)


class TestRunQuiz:
    """Tests for run_quiz function."""
    
    def test_run_quiz_all_correct(self):
        """Test quiz with all correct answers."""
        questions = [
            Question(1, "What is 2+2?", ["4"], "4"),
            Question(2, "Capital?", ["paris"], "Paris")
        ]
        quiz = Quiz("test_001", "2026-02-06T10:00:00", questions)
        
        # Mock user inputs (all correct)
        inputs = ["", "4", "paris"]  # First empty for "Press Enter"
        
        with patch('builtins.input', side_effect=inputs):
            result = run_quiz.run_quiz(quiz, 80.0)
            assert result.total_questions == 2
            assert result.correct_answers == 2
            assert result.score_percentage == 100.0
            assert result.passed is True
            assert len(result.failures) == 0
    
    def test_run_quiz_some_incorrect(self):
        """Test quiz with some incorrect answers."""
        questions = [
            Question(1, "What is 2+2?", ["4"], "4"),
            Question(2, "Capital?", ["paris"], "Paris"),
            Question(3, "Color?", ["blue"], "blue")
        ]
        quiz = Quiz("test_002", "2026-02-06T11:00:00", questions)
        
        # Mock user inputs (1 wrong)
        inputs = ["", "4", "london", "blue"]
        
        with patch('builtins.input', side_effect=inputs):
            result = run_quiz.run_quiz(quiz, 80.0)
            assert result.total_questions == 3
            assert result.correct_answers == 2
            assert result.score_percentage == pytest.approx(66.67, rel=0.01)
            assert result.passed is False  # Below 80%
            assert len(result.failures) == 1
            assert result.failures[0]["user_answer"] == "london"
    
    def test_run_quiz_pass_threshold(self):
        """Test quiz pass threshold."""
        questions = [Question(i, f"Q{i}?", [f"a{i}"], f"A{i}") for i in range(1, 11)]
        quiz = Quiz("test_003", "2026-02-06T12:00:00", questions)
        
        # 8 correct out of 10 = 80%
        inputs = ["", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "wrong", "wrong"]
        
        with patch('builtins.input', side_effect=inputs):
            result = run_quiz.run_quiz(quiz, 80.0)
            assert result.score_percentage == 80.0
            assert result.passed is True  # Exactly 80%


class TestPrintQuestion:
    """Tests for print_question function."""
    
    def test_print_question_format(self, capsys):
        """Test question printing format."""
        run_quiz.print_question(1, 10, "What is the capital of France?")
        captured = capsys.readouterr()
        assert "Question 1/10" in captured.out
        assert "What is the capital of France?" in captured.out
    
    def test_print_question_progress(self, capsys):
        """Test progress indicator."""
        run_quiz.print_question(25, 50, "Test question?")
        captured = capsys.readouterr()
        assert "Question 25/50" in captured.out


class TestDisplayResults:
    """Tests for display_results function."""
    
    def test_display_pass_result(self, capsys):
        """Test displaying passing result."""
        result = QuizResult(
            quiz_id="quiz_001",
            completed_at="2026-02-06T13:00:00",
            total_questions=10,
            correct_answers=9,
            score_percentage=90.0,
            passed=True,
            failures=[]
        )
        run_quiz.display_results(result)
        captured = capsys.readouterr()
        assert "9/10" in captured.out
        assert "90.0%" in captured.out
        assert "PASS" in captured.out
        assert "Perfect score" in captured.out
    
    def test_display_fail_result(self, capsys):
        """Test displaying failing result."""
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
        run_quiz.display_results(result)
        captured = capsys.readouterr()
        assert "7/10" in captured.out
        assert "70.0%" in captured.out
        assert "FAIL" in captured.out
        assert "Failed Questions (1)" in captured.out
        assert "What is 2+2?" in captured.out
        assert "5" in captured.out
        assert "4" in captured.out


class TestIntegration:
    """Integration tests for quiz runner."""
    
    def test_full_quiz_workflow(self):
        """Test complete quiz running workflow."""
        # Create quiz
        questions = [
            Question(1, "What is 2+2?", ["4"], "4"),
            Question(2, "Capital of France?", ["paris"], "Paris"),
            Question(3, "Primary colors?", ["blue", "red", "yellow"], "red, blue, yellow")
        ]
        quiz = Quiz("integration_001", "2026-02-06T15:00:00", questions, "test.csv")
        
        # Save quiz to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_quiz_path = f.name
        
        try:
            quiz.save(temp_quiz_path)
            
            # Load quiz
            loaded_quiz = Quiz.load(temp_quiz_path)
            assert loaded_quiz.quiz_id == quiz.quiz_id
            assert len(loaded_quiz.questions) == 3
            
            # Simulate quiz with all correct answers
            inputs = ["", "4", "paris", "red, blue, yellow"]
            
            with patch('builtins.input', side_effect=inputs):
                result = run_quiz.run_quiz(loaded_quiz, 80.0)
                assert result.correct_answers == 3
                assert result.passed is True
                
                # Save result report
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    report_path = f.name
                
                try:
                    result.save_report(report_path)
                    assert Path(report_path).exists()
                    
                    with open(report_path, 'r') as f:
                        content = f.read()
                        assert "integration_001" in content
                        assert "100.0%" in content
                finally:
                    Path(report_path).unlink(missing_ok=True)
                
        finally:
            Path(temp_quiz_path).unlink(missing_ok=True)
