"""
Integration tests for run_quiz script.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import pytest
import tempfile
import json
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from quizzer.quiz_data import Question, Quiz, QuizResult
import importlib.util
import sys

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
        
        # Mock user inputs: start prompt, answer1, continue, answer2
        inputs = ["", "4", "", "paris"]  # Empty strings for "Press Enter" prompts
        
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
        
        # Mock user inputs: start, answer1, continue, answer2, continue, answer3
        inputs = ["", "4", "", "london", "", "blue"]
        
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
        # Need: start + (answer + continue) * 10 questions, minus last continue
        inputs = [""] + [item for i in range(1, 11) for item in ([f"a{i}" if i <= 8 else "wrong", ""] if i < 10 else [f"a{i}" if i <= 8 else "wrong"])]
        
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
        # Note: display_results doesn't show "Perfect score" - that's only in the report
    
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
        # Note: display_results shows summary stats, not detailed failures


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
            # Need: start + (answer + continue) for each question, minus last continue
            inputs = ["", "4", "", "paris", "", "red, blue, yellow"]
            
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


class TestRunQuizEdgeCases:
    """Additional edge case tests for run_quiz function."""
    
    def test_run_quiz_empty_answers(self):
        """Test quiz handling empty/skipped answers."""
        questions = [
            Question(1, "What is 2+2?", ["4"], "4"),
            Question(2, "Capital?", ["paris"], "Paris")
        ]
        quiz = Quiz("test_empty", "2026-02-06T10:00:00", questions)
        
        # Mock user inputs: start, empty answer (skip Q1), continue, answer Q2
        inputs = ["", "", "", "paris"]
        
        with patch('builtins.input', side_effect=inputs):
            result = run_quiz.run_quiz(quiz, 80.0)
            assert result.total_questions == 2
            assert result.correct_answers == 1
            assert len(result.failures) == 1
            assert result.failures[0]["user_answer"] == "(no answer)"
    
    def test_run_quiz_case_insensitive(self):
        """Test case-insensitive answer matching."""
        questions = [
            Question(1, "Capital?", ["paris"], "Paris"),
            Question(2, "Color?", ["blue"], "blue")
        ]
        quiz = Quiz("test_case", "2026-02-06T10:00:00", questions)
        
        inputs = ["", "PARIS", "", "BLUE"]
        
        with patch('builtins.input', side_effect=inputs):
            result = run_quiz.run_quiz(quiz, 80.0)
            assert result.correct_answers == 2
    
    def test_run_quiz_multiple_answers_order_independent(self):
        """Test that order doesn't matter for multiple answers."""
        questions = [
            Question(1, "Colors?", ["blue", "red", "yellow"], "red, blue, yellow")
        ]
        quiz = Quiz("test_order", "2026-02-06T10:00:00", questions)
        
        # Answer in different order
        inputs = ["", "yellow, blue, red"]
        
        with patch('builtins.input', side_effect=inputs):
            result = run_quiz.run_quiz(quiz, 80.0)
            assert result.correct_answers == 1
    
    def test_run_quiz_whitespace_tolerance(self):
        """Test whitespace tolerance in answers."""
        questions = [
            Question(1, "Number?", ["42"], "42")
        ]
        quiz = Quiz("test_whitespace", "2026-02-06T10:00:00", questions)
        
        inputs = ["", "  42  "]
        
        with patch('builtins.input', side_effect=inputs):
            result = run_quiz.run_quiz(quiz, 80.0)
            assert result.correct_answers == 1
    
    def test_run_quiz_time_tracking(self):
        """Test that time is tracked during quiz."""
        questions = [Question(1, "Q?", ["a"], "A")]
        quiz = Quiz("test_time", "2026-02-06T10:00:00", questions)
        
        inputs = ["", "a"]
        
        with patch('builtins.input', side_effect=inputs):
            result = run_quiz.run_quiz(quiz, 80.0)
            assert result.time_spent >= 0  # Should have some time recorded
    
    def test_run_quiz_custom_pass_threshold(self):
        """Test quiz with custom pass threshold."""
        questions = [Question(i, f"Q{i}?", [f"a{i}"], f"A{i}") for i in range(1, 11)]
        quiz = Quiz("test_threshold", "2026-02-06T10:00:00", questions)
        
        # 7 correct out of 10 = 70%
        # Create input list: start + (answer + continue) for 10 questions, minus last continue
        answers = [f"a{i}" if i <= 7 else "wrong" for i in range(1, 11)]
        inputs = [""]
        for i, ans in enumerate(answers, 1):
            inputs.append(ans)
            if i < len(answers):
                inputs.append("")  # continue prompt
        
        with patch('builtins.input', side_effect=inputs):
            # With 60% threshold, should pass (70% > 60%)
            result = run_quiz.run_quiz(quiz, 60.0)
            assert result.score_percentage == 70.0
            assert result.passed is True
        
        # Test with higher threshold separately with new input mock
        with patch('builtins.input', side_effect=inputs):
            # With 75% threshold, should fail (70% < 75%)
            result2 = run_quiz.run_quiz(quiz, 75.0)
            assert result2.score_percentage == 70.0
            assert result2.passed is False


class TestHTMLReport:
    """Tests for HTML report generation."""
    
    def test_generate_html_report_pass(self):
        """Test HTML report generation for passing result."""
        result = QuizResult(
            quiz_id="html_test_001",
            completed_at="2026-02-06T10:00:00",
            total_questions=10,
            correct_answers=9,
            score_percentage=90.0,
            passed=True,
            failures=[],
            time_spent=120.5
        )
        quiz = Quiz("html_test_001", "2026-02-06T09:00:00", 
                   [Question(i, f"Q{i}?", [f"a{i}"], f"A{i}") for i in range(1, 11)],
                   "test.csv")
        
        html = run_quiz.generate_html_report(result, quiz)
        
        assert "html" in html.lower()
        assert "PASS" in html
        assert "90.0%" in html
        assert "html_test_001" in html
        assert "9" in html  # Correct answers
    
    def test_generate_html_report_fail(self):
        """Test HTML report generation for failing result."""
        failures = [
            {
                "question_id": "5",
                "question": "What is 2+2?",
                "user_answer": "5",
                "correct_answer": "4"
            }
        ]
        result = QuizResult(
            quiz_id="html_test_002",
            completed_at="2026-02-06T10:00:00",
            total_questions=10,
            correct_answers=6,
            score_percentage=60.0,
            passed=False,
            failures=failures,
            time_spent=180.0
        )
        quiz = Quiz("html_test_002", "2026-02-06T09:00:00",
                   [Question(i, f"Q{i}?", [f"a{i}"], f"A{i}") for i in range(1, 11)])
        
        html = run_quiz.generate_html_report(result, quiz)
        
        assert "FAIL" in html
        assert "60.0%" in html
        assert "What is 2+2?" in html
        assert "5" in html  # User's wrong answer
        assert "4" in html  # Correct answer
    
    def test_generate_html_report_perfect_score(self):
        """Test HTML report for perfect score."""
        result = QuizResult(
            quiz_id="html_test_003",
            completed_at="2026-02-06T10:00:00",
            total_questions=50,
            correct_answers=50,
            score_percentage=100.0,
            passed=True,
            failures=[],
            time_spent=300.0
        )
        quiz = Quiz("html_test_003", "2026-02-06T09:00:00",
                   [Question(i, f"Q{i}?", [f"a{i}"], f"A{i}") for i in range(1, 51)])
        
        html = run_quiz.generate_html_report(result, quiz)
        
        assert "Perfect Score" in html or "perfect" in html.lower()
        assert "100.0%" in html
        assert "PASS" in html
    
    def test_save_html_report(self):
        """Test saving HTML report to file."""
        result = QuizResult(
            quiz_id="save_test_001",
            completed_at="2026-02-06T10:00:00",
            total_questions=10,
            correct_answers=8,
            score_percentage=80.0,
            passed=True,
            failures=[],
            time_spent=150.0
        )
        quiz = Quiz("save_test_001", "2026-02-06T09:00:00",
                   [Question(i, f"Q{i}?", [f"a{i}"], f"A{i}") for i in range(1, 11)])
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            filepath = run_quiz.save_html_report(result, quiz, temp_dir)
            
            assert filepath.exists()
            assert filepath.suffix == ".html"
            assert "save_test_001" in filepath.name
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "html" in content.lower()
                assert "80.0%" in content
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_save_html_report_overwrites(self):
        """Test that HTML report overwrites previous report."""
        result = QuizResult(
            quiz_id="overwrite_test",
            completed_at="2026-02-06T10:00:00",
            total_questions=10,
            correct_answers=8,
            score_percentage=80.0,
            passed=True,
            failures=[],
            time_spent=100.0
        )
        quiz = Quiz("overwrite_test", "2026-02-06T09:00:00",
                   [Question(1, "Q?", ["a"], "A")])
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Save report first time
            filepath1 = run_quiz.save_html_report(result, quiz, temp_dir)
            mtime1 = filepath1.stat().st_mtime
            
            # Save again with different score
            result.score_percentage = 90.0
            filepath2 = run_quiz.save_html_report(result, quiz, temp_dir)
            
            # Same file should be overwritten
            assert filepath1 == filepath2
            
            # Content should be updated
            with open(filepath2, 'r') as f:
                content = f.read()
                assert "90.0%" in content
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestQuizFolderSelection:
    """Tests for quiz folder selection functions."""
    
    def test_get_quiz_folders(self):
        """Test getting list of quiz folders."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create folder structure
            folder1 = Path(temp_dir) / "quiz_folder_1"
            folder2 = Path(temp_dir) / "quiz_folder_2"
            folder3 = Path(temp_dir) / "empty_folder"
            
            folder1.mkdir()
            folder2.mkdir()
            folder3.mkdir()
            
            # Add quiz files
            (folder1 / "quiz_001.json").write_text("{}")
            (folder2 / "quiz_002.json").write_text("{}")
            # folder3 has no quiz files
            
            folders = run_quiz.get_quiz_folders(temp_dir)
            
            assert len(folders) == 2
            assert folder1 in folders
            assert folder2 in folders
            assert folder3 not in folders  # Empty folder excluded
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_quiz_folders_empty(self):
        """Test getting folders when none exist."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            folders = run_quiz.get_quiz_folders(temp_dir)
            assert len(folders) == 0
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_quiz_folders_sorts_alphabetically(self):
        """Test that folders are sorted alphabetically."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create folders in non-alphabetical order
            for name in ["zebra", "alpha", "beta"]:
                folder = Path(temp_dir) / name
                folder.mkdir()
                (folder / "quiz.json").write_text("{}")
            
            folders = run_quiz.get_quiz_folders(temp_dir)
            folder_names = [f.name for f in folders]
            
            assert folder_names == ["alpha", "beta", "zebra"]
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_random_quiz_from_folder(self):
        """Test getting random quiz from folder."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            folder = Path(temp_dir) / "test_folder"
            folder.mkdir()
            
            # Create multiple quiz files
            quiz1 = folder / "quiz_001.json"
            quiz2 = folder / "quiz_002.json"
            quiz1.write_text("{}")
            quiz2.write_text("{}")
            
            selected = run_quiz.get_random_quiz_from_folder(folder)
            
            assert selected in [quiz1, quiz2]
            assert selected.exists()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_random_quiz_from_empty_folder(self):
        """Test error when folder has no quizzes."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            folder = Path(temp_dir) / "empty"
            folder.mkdir()
            
            with pytest.raises(FileNotFoundError):
                run_quiz.get_random_quiz_from_folder(folder)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_find_latest_quiz_with_metadata(self):
        """Test finding latest quiz using metadata file."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create metadata file
            metadata = {
                "last_import": "2026-02-06T10:00:00",
                "quiz_files": [
                    str(Path(temp_dir) / "quiz_001.json"),
                    str(Path(temp_dir) / "quiz_002.json")
                ]
            }
            metadata_path = Path(temp_dir) / "last_import.json"
            metadata_path.write_text(json.dumps(metadata))
            
            # Create the quiz files
            (Path(temp_dir) / "quiz_001.json").write_text("{}")
            (Path(temp_dir) / "quiz_002.json").write_text("{}")
            
            latest = run_quiz.find_latest_quiz(temp_dir)
            
            assert latest.exists()
            assert latest.name in ["quiz_001.json", "quiz_002.json"]
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_find_latest_quiz_without_metadata(self):
        """Test finding latest quiz without metadata (fallback)."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create quiz files without metadata
            import time
            
            quiz1 = Path(temp_dir) / "quiz_001.json"
            quiz1.write_text("{}")
            time.sleep(0.01)  # Ensure different timestamps
            
            quiz2 = Path(temp_dir) / "quiz_002.json"
            quiz2.write_text("{}")
            
            latest = run_quiz.find_latest_quiz(temp_dir)
            
            # Should find the most recently created file
            assert latest == quiz2
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_find_latest_quiz_no_quizzes(self):
        """Test error when no quizzes exist."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            with pytest.raises(FileNotFoundError):
                run_quiz.find_latest_quiz(temp_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestUserInputHelpers:
    """Tests for user input helper functions."""
    
    def test_get_user_answer_normal(self):
        """Test getting normal user answer."""
        with patch('builtins.input', return_value="Paris"):
            answer = run_quiz.get_user_answer()
            assert answer == "Paris"
    
    def test_get_user_answer_with_whitespace(self):
        """Test that whitespace is stripped."""
        with patch('builtins.input', return_value="  Paris  "):
            answer = run_quiz.get_user_answer()
            assert answer == "Paris"
    
    def test_get_user_answer_keyboard_interrupt(self):
        """Test handling of Ctrl+C during input."""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit):
                run_quiz.get_user_answer()
    
    def test_get_user_answer_eof(self):
        """Test handling of EOF during input."""
        with patch('builtins.input', side_effect=EOFError):
            with pytest.raises(SystemExit):
                run_quiz.get_user_answer()
    
    def test_print_header(self, capsys):
        """Test printing quiz header."""
        run_quiz.print_header()
        captured = capsys.readouterr()
        assert "QUIZ" in captured.out.upper()
        assert "=" in captured.out


class TestMainFunction:
    """Tests for main() function."""
    
    def test_main_with_specific_file(self):
        """Test main with specific quiz file."""
        # Create a test quiz
        questions = [Question(1, "Test?", ["test"], "Test")]
        quiz = Quiz("main_test_001", "2026-02-06T10:00:00", questions)
        
        temp_dir = tempfile.mkdtemp()
        quiz_file = Path(temp_dir) / "quiz.json"
        
        try:
            quiz.save(str(quiz_file))
            
            test_args = ['run_quiz.py', str(quiz_file), '--pass-threshold', '80', '--quiet']
            inputs = ["", "test"]
            
            with patch.object(sys, 'argv', test_args):
                with patch('builtins.input', side_effect=inputs):
                    with pytest.raises(SystemExit) as exc_info:
                        run_quiz.main()
                    # Should exit with 0 (pass)
                    assert exc_info.value.code == 0
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_main_with_failing_score(self):
        """Test main exits with code 1 for failing score."""
        questions = [
            Question(1, "Q1?", ["a"], "A"),
            Question(2, "Q2?", ["b"], "B")
        ]
        quiz = Quiz("main_test_002", "2026-02-06T10:00:00", questions)
        
        temp_dir = tempfile.mkdtemp()
        quiz_file = Path(temp_dir) / "quiz.json"
        
        try:
            quiz.save(str(quiz_file))
            
            test_args = ['run_quiz.py', str(quiz_file), '--quiet']
            inputs = ["", "a", "wrong"]  # 1 correct, 1 wrong = 50%
            
            with patch.object(sys, 'argv', test_args):
                with patch('builtins.input', side_effect=inputs):
                    with pytest.raises(SystemExit) as exc_info:
                        run_quiz.main()
                    # Should exit with 1 (fail)
                    assert exc_info.value.code == 1
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_main_missing_file_error(self):
        """Test main with non-existent file."""
        test_args = ['run_quiz.py', 'nonexistent.json']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                run_quiz.main()
            assert exc_info.value.code == 1
    
    def test_main_html_report_generated(self):
        """Test that HTML report is always generated."""
        questions = [Question(1, "Test?", ["test"], "Test")]
        quiz = Quiz("main_test_003", "2026-02-06T10:00:00", questions)
        
        temp_dir = tempfile.mkdtemp()
        quiz_file = Path(temp_dir) / "quiz.json"
        report_dir = Path(temp_dir) / "reports"
        
        try:
            quiz.save(str(quiz_file))
            report_dir.mkdir()
            
            test_args = ['run_quiz.py', str(quiz_file), '--quiet']
            inputs = ["", "test"]
            
            # Patch save_html_report to save to our temp directory
            original_save = run_quiz.save_html_report
            
            def mock_save(result, quiz, output_dir="data/reports"):
                return original_save(result, quiz, str(report_dir))
            
            with patch.object(sys, 'argv', test_args):
                with patch('builtins.input', side_effect=inputs):
                    with patch.object(run_quiz, 'save_html_report', side_effect=mock_save):
                        try:
                            run_quiz.main()
                        except SystemExit:
                            pass
            
            # Check that HTML report was created
            html_files = list(report_dir.glob("*.html"))
            assert len(html_files) >= 1
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_main_with_text_report_output(self):
        """Test main with additional text report output."""
        questions = [Question(1, "Test?", ["test"], "Test")]
        quiz = Quiz("main_test_004", "2026-02-06T10:00:00", questions)
        
        temp_dir = tempfile.mkdtemp()
        quiz_file = Path(temp_dir) / "quiz.json"
        report_dir = Path(temp_dir) / "text_reports"
        
        try:
            quiz.save(str(quiz_file))
            
            test_args = ['run_quiz.py', str(quiz_file), 
                        '--report-output', str(report_dir), '--quiet']
            inputs = ["", "test"]
            
            with patch.object(sys, 'argv', test_args):
                with patch('builtins.input', side_effect=inputs):
                    # Mock HTML report to avoid file creation issues
                    with patch.object(run_quiz, 'save_html_report', return_value=Path("dummy.html")):
                        try:
                            run_quiz.main()
                        except SystemExit:
                            pass
            
            # Check that text report was created
            txt_files = list(report_dir.glob("*.txt"))
            assert len(txt_files) >= 1
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
