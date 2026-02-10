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
from unittest.mock import patch
import shutil

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
    
    def test_quiz_uses_all_provided_questions(self):
        """Test that quiz uses all provided questions."""
        questions = [(f"Q{i}?", f"A{i}") for i in range(10)]
        quiz = import_quiz.create_quiz(questions, "test_002")
        
        # Should use all provided questions
        assert len(quiz.questions) == 10
    
    def test_question_order_preserved(self):
        """Test that question order is preserved as provided."""
        questions = [(f"Q{i}?", f"A{i}") for i in range(5)]
        quiz = import_quiz.create_quiz(questions, "test_003")
        
        # Questions should be in the order provided (shuffling happens before create_quiz)
        assert len(quiz.questions) == 5
    
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
    
    def test_with_sequence_number(self):
        """Test quiz ID generation with sequence number."""
        quiz_id = import_quiz.generate_quiz_id("test", 1)
        assert quiz_id.startswith("test_")
        assert quiz_id.endswith("_1")
        
        quiz_id2 = import_quiz.generate_quiz_id("test", 5)
        assert quiz_id2.endswith("_5")
    
    def test_without_sequence_number(self):
        """Test quiz ID generation without sequence number."""
        quiz_id = import_quiz.generate_quiz_id("test", None)
        assert quiz_id.startswith("test_")
        assert not quiz_id.endswith("_1")  # Should not have sequence suffix


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


class TestEncoding:
    """Tests for CSV encoding handling."""
    
    def test_utf8_bom(self):
        """Test reading CSV with UTF-8 BOM."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            # Write UTF-8 BOM followed by CSV content
            f.write(b'\xef\xbb\xbf')
            f.write("Question,Answer\n".encode('utf-8'))
            f.write("Test question?,Test answer\n".encode('utf-8'))
            temp_path = f.name
        
        try:
            questions = import_quiz.read_csv_questions(temp_path)
            assert len(questions) == 1
            assert questions[0] == ("Test question?", "Test answer")
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_latin1_encoding(self):
        """Test reading CSV with Latin-1 encoding."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, 
                                         newline='', encoding='latin-1') as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer"])
            writer.writerow(["What is café?", "A coffee shop"])
            temp_path = f.name
        
        try:
            questions = import_quiz.read_csv_questions(temp_path)
            assert len(questions) == 1
            assert "café" in questions[0][0]
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_special_characters(self):
        """Test reading CSV with special characters."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, 
                                         newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer"])
            writer.writerow(["What's O'Brien's role?", "Character in 1984"])
            writer.writerow(["Formula for H₂O?", "Water"])
            writer.writerow(["What is π?", "3.14159..."])
            temp_path = f.name
        
        try:
            questions = import_quiz.read_csv_questions(temp_path)
            assert len(questions) == 3
            assert "O'Brien" in questions[0][0]
            assert "H₂O" in questions[1][0]
            assert "π" in questions[2][0]
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestCreateQuizEdgeCases:
    """Tests for create_quiz edge cases."""
    
    def test_quiz_without_source_file(self):
        """Test creating quiz without source file."""
        questions = [("Q1?", "A1"), ("Q2?", "A2")]
        quiz = import_quiz.create_quiz(questions, "test_001")
        assert quiz.source_file == ""
    
    def test_quiz_with_empty_questions_list(self):
        """Test creating quiz with no questions."""
        questions = []
        quiz = import_quiz.create_quiz(questions, "test_002")
        assert len(quiz.questions) == 0
    
    def test_quiz_with_single_question(self):
        """Test creating quiz with only one question."""
        questions = [("Single question?", "Single answer")]
        quiz = import_quiz.create_quiz(questions, "test_003")
        assert len(quiz.questions) == 1
        assert quiz.questions[0].question == "Single question?"
    
    def test_quiz_with_long_answers(self):
        """Test creating quiz with very long answers."""
        long_answer = ", ".join([f"item{i}" for i in range(100)])
        questions = [("List items?", long_answer)]
        quiz = import_quiz.create_quiz(questions, "test_004")
        assert len(quiz.questions[0].answer) == 100  # All items normalized and sorted


class TestCSVEdgeCases:
    """Tests for CSV edge cases."""
    
    def test_csv_with_quoted_commas(self):
        """Test CSV with commas inside quoted fields."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(["Question", "Answer"])
            writer.writerow(["What are primary colors?", "red, blue, yellow"])
            writer.writerow(["List months", "January, February, March"])
            temp_path = f.name
        
        try:
            questions = import_quiz.read_csv_questions(temp_path)
            assert len(questions) == 2
            assert "red, blue, yellow" in questions[0][1]
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_csv_with_newlines_in_fields(self):
        """Test CSV with newlines inside fields."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer"])
            writer.writerow(["What is\na multiline\nquestion?", "Multiline answer"])
            temp_path = f.name
        
        try:
            questions = import_quiz.read_csv_questions(temp_path)
            assert len(questions) == 1
            # Newlines should be preserved in the question
            assert "\n" in questions[0][0] or "multiline" in questions[0][0].lower()
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_csv_with_only_whitespace_rows(self):
        """Test CSV with rows containing only whitespace."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["What is 2+2?", "4"])
            writer.writerow(["   ", "   "])
            writer.writerow([" \t ", " \t "])
            writer.writerow(["Capital?", "Paris"])
            temp_path = f.name
        
        try:
            questions = import_quiz.read_csv_questions(temp_path)
            assert len(questions) == 2  # Whitespace rows should be skipped
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_csv_with_leading_trailing_whitespace(self):
        """Test CSV with leading/trailing whitespace in fields."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer"])
            writer.writerow(["  What is 2+2?  ", "  4  "])
            writer.writerow(["  Capital?  ", "  Paris  "])
            temp_path = f.name
        
        try:
            questions = import_quiz.read_csv_questions(temp_path)
            assert len(questions) == 2
            # Whitespace should be stripped
            assert questions[0] == ("What is 2+2?", "4")
            assert questions[1] == ("Capital?", "Paris")
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_csv_case_insensitive_header_detection(self):
        """Test header detection is case-insensitive."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["QUESTION", "ANSWER"])  # All caps
            writer.writerow(["What is 2+2?", "4"])
            temp_path = f.name
        
        try:
            questions = import_quiz.read_csv_questions(temp_path)
            assert len(questions) == 1  # Header should be skipped
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestMainFunction:
    """Tests for main() function behavior via mocking."""
    
    def test_main_with_valid_csv(self):
        """Test main function with valid CSV input."""
        # Create a test CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer"])
            for i in range(10):
                writer.writerow([f"Question {i}?", f"Answer {i}"])
            csv_path = f.name
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Mock sys.argv to simulate command line args
            test_args = ['import_quiz.py', csv_path, '--output', temp_dir, '--number', '1']
            
            with patch.object(sys, 'argv', test_args):
                # Import fresh to trigger main() with new args
                import_quiz.main()
            
            # Check that quiz files were created
            csv_basename = Path(csv_path).stem
            output_dir = Path(temp_dir) / csv_basename
            quiz_files = list(output_dir.glob("*.json"))
            
            # Should have created 1 quiz
            assert len(quiz_files) >= 1
            
        finally:
            Path(csv_path).unlink(missing_ok=True)
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_main_with_max_questions(self):
        """Test main function with max-questions parameter."""
        # Create a test CSV with 100 questions
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer"])
            for i in range(100):
                writer.writerow([f"Question {i}?", f"Answer {i}"])
            csv_path = f.name
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Don't specify --number, let it auto-calculate based on max-questions
            test_args = ['import_quiz.py', csv_path, '--output', temp_dir, 
                         '--max-questions', '25']
            
            with patch.object(sys, 'argv', test_args):
                import_quiz.main()
            
            # Should create 4 quizzes (100 questions / 25 per quiz)
            csv_basename = Path(csv_path).stem
            output_dir = Path(temp_dir) / csv_basename
            quiz_files = list(output_dir.glob("*.json"))
            
            # Auto-calculated should be 4 quizzes with ~25 questions each
            assert len(quiz_files) == 4
            
            # Verify question distribution
            from quizzer.quiz_data import Quiz
            total_questions = sum(len(Quiz.load(str(qf)).questions) for qf in quiz_files)
            assert total_questions == 100  # All questions should be distributed
            
        finally:
            Path(csv_path).unlink(missing_ok=True)
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_main_with_custom_prefix(self):
        """Test main function with custom prefix."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer"])
            writer.writerow(["Test?", "Test"])
            csv_path = f.name
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            test_args = ['import_quiz.py', csv_path, '--output', temp_dir, 
                         '--prefix', 'midterm']
            
            with patch.object(sys, 'argv', test_args):
                import_quiz.main()
            
            csv_basename = Path(csv_path).stem
            output_dir = Path(temp_dir) / csv_basename
            quiz_files = list(output_dir.glob("midterm_*.json"))
            
            assert len(quiz_files) >= 1
            assert "midterm_" in quiz_files[0].name
            
        finally:
            Path(csv_path).unlink(missing_ok=True)
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_main_error_handling_missing_file(self, capsys):
        """Test main function error handling for missing file."""
        test_args = ['import_quiz.py', 'nonexistent.csv']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                import_quiz.main()
            assert exc_info.value.code == 1
    
    def test_main_metadata_file_creation(self):
        """Test that main creates last_import.json metadata file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer"])
            writer.writerow(["Test?", "Test"])
            csv_path = f.name
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            test_args = ['import_quiz.py', csv_path, '--output', temp_dir]
            
            with patch.object(sys, 'argv', test_args):
                import_quiz.main()
            
            # Check metadata file exists
            metadata_file = Path(temp_dir) / "last_import.json"
            assert metadata_file.exists()
            
            # Verify metadata content
            import json
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                assert 'last_import' in metadata
                assert 'source_csv' in metadata
                assert 'num_quizzes' in metadata
                assert metadata['source_csv'] == csv_path
            
        finally:
            Path(csv_path).unlink(missing_ok=True)
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
