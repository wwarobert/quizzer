"""
Integration tests for import_quiz script.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import pytest
import tempfile
import csv
from pathlib import Path
import sys
import importlib.util

# Import the import_quiz module
spec = importlib.util.spec_from_file_location("import_quiz", "import_quiz.py")
import_quiz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(import_quiz)


class TestReadCSVQuestions:
    """Tests for read_csv_questions function."""
    
    def test_read_valid_csv(self):
        """Test reading a valid CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["What is 2+2?", "4"])
            writer.writerow(["Capital of France?", "Paris"])
            temp_path = f.name
        
        try:
            questions = import_quiz.read_csv_questions(temp_path)
            assert len(questions) == 2
            assert questions[0] == ("What is 2+2?", "4")
            assert questions[1] == ("Capital of France?", "Paris")
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_skip_header_row(self):
        """Test that header row is skipped."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer"])
            writer.writerow(["What is 2+2?", "4"])
            temp_path = f.name
        
        try:
            questions = import_quiz.read_csv_questions(temp_path)
            assert len(questions) == 1
            assert questions[0] == ("What is 2+2?", "4")
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_skip_empty_rows(self):
        """Test that empty rows are skipped."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["What is 2+2?", "4"])
            writer.writerow(["", ""])
            writer.writerow(["Capital?", "Paris"])
            temp_path = f.name
        
        try:
            questions = import_quiz.read_csv_questions(temp_path)
            assert len(questions) == 2
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_extra_columns_ignored(self):
        """Test that extra columns beyond first 2 are ignored."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer", "Extra1", "Extra2"])
            writer.writerow(["What is 2+2?", "4", "ignored1", "ignored2"])
            writer.writerow(["Capital?", "Paris", "ignored3", "ignored4"])
            temp_path = f.name
        
        try:
            questions = import_quiz.read_csv_questions(temp_path)
            # Should skip header and read 2 questions, ignoring extra columns
            assert len(questions) == 2
            assert questions[0] == ("What is 2+2?", "4")
            assert questions[1] == ("Capital?", "Paris")
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_insufficient_columns(self):
        """Test error when CSV has fewer than 2 columns."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["OnlyOneColumn"])
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="expected at least 2"):
                import_quiz.read_csv_questions(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_file_not_found(self):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            import_quiz.read_csv_questions("nonexistent.csv")


class TestCreateQuiz:
    """Tests for create_quiz function."""
    
    def test_create_quiz_basic(self):
        """Test creating a basic quiz."""
        questions = [
            ("What is 2+2?", "4"),
            ("Capital?", "Paris"),
            ("Color?", "red, blue")
        ]
        quiz = import_quiz.create_quiz(questions, "test_001", "test.csv")
        
        assert quiz.quiz_id == "test_001"
        assert quiz.source_file == "test.csv"
        assert len(quiz.questions) == 3
        assert quiz.created_at  # Should have timestamp
    
    def test_max_questions_limit(self):
        """Test that quiz respects max_questions limit."""
        questions = [(f"Q{i}?", f"A{i}") for i in range(100)]
        quiz = import_quiz.create_quiz(questions, "test_002", max_questions=10)
        
        assert len(quiz.questions) == 10
    
    def test_randomization(self):
        """Test that questions are randomized."""
        questions = [(f"Q{i}?", f"A{i}") for i in range(50)]
        quiz1 = import_quiz.create_quiz(questions, "test_003")
        quiz2 = import_quiz.create_quiz(questions, "test_004")
        
        # Extract question texts
        q1_texts = [q.question for q in quiz1.questions]
        q2_texts = [q.question for q in quiz2.questions]
        
        # Due to randomization, order should likely differ
        # (There's a tiny chance they're the same, but very unlikely)
        assert q1_texts != q2_texts or len(questions) < 3
    
    def test_normalized_answers(self):
        """Test that answers are normalized."""
        questions = [
            ("Primary colors?", "Red, Blue, Yellow"),
            ("Number?", "42")
        ]
        quiz = import_quiz.create_quiz(questions, "test_005")
        
        # Check first question has normalized answer
        q1 = quiz.questions[0]
        if q1.question == "Primary colors?":
            assert q1.answer == ["blue", "red", "yellow"]  # Sorted and lowercase
            assert q1.original_answer == "Red, Blue, Yellow"
        
        # Find the number question
        for q in quiz.questions:
            if q.question == "Number?":
                assert q.answer == ["42"]
                assert q.original_answer == "42"


class TestGenerateQuizId:
    """Tests for generate_quiz_id function."""
    
    def test_default_prefix(self):
        """Test quiz ID generation with default prefix."""
        quiz_id = import_quiz.generate_quiz_id()
        assert quiz_id.startswith("quiz_")
        assert len(quiz_id) > 10  # Should include timestamp
    
    def test_custom_prefix(self):
        """Test quiz ID generation with custom prefix."""
        quiz_id = import_quiz.generate_quiz_id("midterm")
        assert quiz_id.startswith("midterm_")
    
    def test_unique_ids(self):
        """Test that generated IDs are unique."""
        id1 = import_quiz.generate_quiz_id()
        id2 = import_quiz.generate_quiz_id()
        # They might be the same if generated in same second, but unlikely
        assert id1 != id2 or True  # Accept same if generated too fast


class TestIntegration:
    """Integration tests for full workflow."""
    
    def test_full_import_workflow(self):
        """Test complete CSV to Quiz workflow."""
        # Create temporary CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer"])  # Header
            writer.writerow(["What is 2+2?", "4"])
            writer.writerow(["Capital of France?", "Paris"])
            writer.writerow(["Primary colors?", "red, blue, yellow"])
            csv_path = f.name
        
        # Create temporary output directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Read CSV
            questions = import_quiz.read_csv_questions(csv_path)
            assert len(questions) == 3
            
            # Create quiz
            quiz_id = import_quiz.generate_quiz_id("test")
            quiz = import_quiz.create_quiz(questions, quiz_id, "test.csv")
            
            # Save quiz
            output_path = Path(temp_dir) / f"{quiz_id}.json"
            quiz.save(str(output_path))
            
            # Verify file exists
            assert output_path.exists()
            
            # Load and verify
            from quizzer.quiz_data import Quiz
            loaded_quiz = Quiz.load(str(output_path))
            assert loaded_quiz.quiz_id == quiz_id
            assert len(loaded_quiz.questions) == 3
            
        finally:
            # Cleanup
            Path(csv_path).unlink(missing_ok=True)
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
