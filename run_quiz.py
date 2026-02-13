#!/usr/bin/env python3
"""
Run Quiz Script - Interactive Quiz Runner

This script loads a quiz JSON file and presents questions interactively,
validates answers, and generates a pass/fail report.

Usage:
    python run_quiz.py quiz_001.json
    python run_quiz.py data/quizzes/quiz_001.json --pass-threshold 75

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import argparse
import sys
import json
import random
import os
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from quizzer import answers_match, format_answer_display, Quiz, QuizResult, is_test_data


def select_quiz_folder(base_dir: str = "data/quizzes") -> Path:
    """
    Interactively select a quiz folder if multiple exist.

    Args:
        base_dir: Base directory containing quiz folders

    Returns:
        Path to selected folder
    """
    base_path = Path(base_dir)

    if not base_path.exists():
        print(f"Error: Quiz directory not found: {base_path}")
        sys.exit(1)

    # Get all subdirectories
    subdirs = [d for d in base_path.iterdir() if d.is_dir()]

    if len(subdirs) == 0:
        print(f"Error: No quiz folders found in {base_path}")
        sys.exit(1)

    if len(subdirs) == 1:
        return subdirs[0]

    # Multiple folders - ask user to select
    print("\nAvailable quiz folders:")
    for i, folder in enumerate(subdirs, 1):
        quiz_count = len(list(folder.glob("*.json")))
        print(f"  {i}. {folder.name} ({quiz_count} quizzes)")

    while True:
        try:
            choice = input("\nSelect folder (1-{0}): ".format(len(subdirs)))
            idx = int(choice) - 1
            if 0 <= idx < len(subdirs):
                return subdirs[idx]
            else:
                print(f"Please enter a number between 1 and {len(subdirs)}")
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled by user.")
            sys.exit(0)


def select_random_quiz(quiz_dir: str = "data/quizzes") -> Path:
    """
    Select a random quiz from the quiz directory.

    Args:
        quiz_dir: Base directory containing quiz folders

    Returns:
        Path to randomly selected quiz file
    """
    import random

    base_path = Path(quiz_dir)

    # Check if there are subfolders or direct quiz files
    subdirs = [d for d in base_path.iterdir() if d.is_dir()]

    if subdirs:
        # Select folder (interactive if multiple)
        folder = select_quiz_folder(quiz_dir)
        quiz_files = list(folder.glob("*.json"))
    else:
        # Look for quiz files directly in base directory
        quiz_files = list(base_path.glob("*.json"))

    if not quiz_files:
        print(f"Error: No quiz files found in {base_path}")
        sys.exit(1)

    # Select random quiz
    selected = random.choice(quiz_files)
    print(f"Selected random quiz: {selected.name}")
    return selected


def generate_html_report(result: QuizResult, quiz: Quiz) -> str:
    """
    Generate an HTML report for quiz results.

    Args:
        result: QuizResult object with quiz results
        quiz: Quiz object with quiz metadata

    Returns:
        HTML string with formatted report
    """
    pass_status = "PASS" if result.passed else "FAIL"
    status_color = "#28a745" if result.passed else "#dc3545"
    coverage_color = "#28a745" if result.score_percentage >= 80 else "#ffc107" if result.score_percentage >= 60 else "#dc3545"

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


def save_html_report(result: QuizResult, quiz: Quiz, output_dir: str = "data/reports") -> Path:
    """
    Save quiz results as HTML report.

    Args:
        result: QuizResult object
        quiz: Quiz object
        output_dir: Directory to save reports (default: data/reports)

    Returns:
        Path to saved HTML file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Use quiz_id for filename so it gets overwritten on each run
    filename = f"{result.quiz_id}_report.html"
    filepath = output_path / filename

    html_content = generate_html_report(result, quiz)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return filepath


def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print quiz header banner."""
    print("\n" + "=" * 60)
    print("QUIZ RUNNER".center(60))
    print("=" * 60 + "\n")


def print_question(question_num: int, total: int, question_text: str):
    """
    Print a formatted question.

    Args:
        question_num: Current question number (1-indexed)
        total: Total number of questions
        question_text: The question text to display
    """
    print(f"\nQuestion {question_num}/{total}: {question_text}")


def get_user_answer() -> str:
    """
    Get answer input from the user.

    Returns:
        User's answer string (may be empty if they skip)
    """
    try:
        answer = input("Your answer: ").strip()
        return answer
    except (KeyboardInterrupt, EOFError):
        print("\n\nQuiz interrupted by user.")
        sys.exit(0)


def run_quiz(quiz: Quiz, pass_threshold: float = 80.0) -> QuizResult:
    """
    Run the quiz interactively and collect results.

    Args:
        quiz: Quiz object to run
        pass_threshold: Minimum percentage to pass (default: 80.0)

    Returns:
        QuizResult object with complete results
    """
    clear_screen()
    print_header()
    print(f"Quiz ID: {quiz.quiz_id}")
    print(f"Questions: {len(quiz.questions)}")
    print(f"Pass threshold: {pass_threshold}%")
    print(f"\nInstructions:")
    print("  - For multiple answers, separate with commas (e.g., 'a, b, c')")
    print("  - Answers are case-insensitive")
    print("  - Whitespace is ignored")
    print("  - After each answer, press Enter to continue")
    print("\nPress Ctrl+C to quit at any time.\n")

    input("Press Enter to start...")

    start_time = time.time()
    correct_count = 0
    failures: List[Dict[str, str]] = []

    for idx, question in enumerate(quiz.questions, 1):
        # Clear screen and display question
        clear_screen()
        print("=" * 60)
        print(f"Question {idx}/{len(quiz.questions)}".center(60))
        print("=" * 60 + "\n")
        print(f"{question.question}\n")

        user_answer = get_user_answer()

        # Compare answers
        is_correct = answers_match(user_answer, question.original_answer)

        # Display result
        print("\n" + "-" * 60)
        if is_correct:
            correct_count += 1
            print("✓ CORRECT!")
        else:
            print("✗ INCORRECT")
            failures.append({
                'question_id': str(question.id),
                'question': question.question,
                'user_answer': format_answer_display(user_answer) if user_answer else "(no answer)",
                'correct_answer': question.original_answer
            })

        # Show detailed answer
        print(f"\nYour answer: {format_answer_display(user_answer) if user_answer else '(no answer)'}")
        print(f"Correct answer: {question.original_answer}")
        print("-" * 60)

        # Wait for user to press Enter before continuing
        if idx < len(quiz.questions):
            input("\nPress Enter to continue to the next question...")

    # Calculate time spent
    end_time = time.time()
    time_spent = end_time - start_time

    # Calculate results
    total_questions = len(quiz.questions)
    score_percentage = (correct_count / total_questions) * 100
    passed = score_percentage >= pass_threshold

    # Create result object
    result = QuizResult(
        quiz_id=quiz.quiz_id,
        completed_at=datetime.now().isoformat(),
        total_questions=total_questions,
        correct_answers=correct_count,
        score_percentage=score_percentage,
        passed=passed,
        failures=failures,
        time_spent=time_spent
    )

    return result


def display_results(result: QuizResult):
    """
    Display quiz results to the console.

    Args:
        result: QuizResult object to display
    """
    clear_screen()
    print("\n" + "=" * 60)
    print("QUIZ COMPLETE".center(60))
    print("=" * 60 + "\n")

    # Summary statistics
    incorrect_count = result.total_questions - result.correct_answers
    mins, secs = divmod(int(result.time_spent), 60)
    time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

    print(f"Total Questions:     {result.total_questions}")
    print(f"Correct Answers:     {result.correct_answers}")
    print(f"Incorrect Answers:   {incorrect_count}")
    print(f"Time Spent:          {time_str}")
    print(f"\nScore:               {result.correct_answers}/{result.total_questions} ({result.score_percentage:.1f}%)")

    if result.passed:
        print("Result:              ✓ PASS")
    else:
        print("Result:              ✗ FAIL")

    print("\n" + "=" * 60)


def get_quiz_folders(base_dir: str = "data/quizzes", test_mode: bool = False) -> List[Path]:
    """
    Get list of subdirectories containing quiz files.

    Args:
        base_dir: Base directory where quizzes are stored
        test_mode: If False (default), exclude sample quizzes for production

    Returns:
        List of Path objects for subdirectories containing quiz files
        
    Examples:
        >>> # Production mode - hide test data
        >>> folders = get_quiz_folders(test_mode=False)
        >>> assert not any(is_test_data(f) for f in folders)
        
        >>> # Test mode - show all
        >>> folders = get_quiz_folders(test_mode=True)
        >>> assert len(folders) >= 0
    """
    base_path = Path(base_dir)
    if not base_path.exists():
        return []

    # Find all subdirectories that contain .json files
    folders = []
    for item in base_path.iterdir():
        if not item.is_dir():
            continue
            
        # Skip test data folders in production mode
        if not test_mode and is_test_data(item):
            continue
            
        # Check if directory contains any JSON files (quiz files have timestamp pattern)
        json_files = list(item.glob("*.json"))
        # Filter out non-quiz files (like metadata)
        quiz_files = [
            f for f in json_files
            if f.stem not in ['last_import', 'README', 'metadata']
        ]
        if quiz_files:
            folders.append(item)

    # Sort folders alphabetically
    return sorted(folders, key=lambda p: p.name.lower())


def select_quiz_folder(folders: List[Path]) -> Path:
    """
    Display folder selection menu and get user choice.

    Args:
        folders: List of folder paths to choose from

    Returns:
        Selected folder path

    Raises:
        SystemExit: If user cancels or provides invalid input
    """
    print("\n" + "=" * 60)
    print("SELECT QUIZ FOLDER".center(60))
    print("=" * 60 + "\n")

    if not folders:
        print("No quiz folders found in data/quizzes/")
        print("\nPlease create quizzes first using import_quiz.py")
        sys.exit(1)

    print("Available quiz folders:\n")
    for idx, folder in enumerate(folders, 1):
        # Count quiz files in folder (all JSON files except metadata)
        json_files = list(folder.glob("*.json"))
        quiz_files = [
            f for f in json_files
            if f.stem not in ['last_import', 'README', 'metadata']
        ]
        quiz_count = len(quiz_files)
        print(f"  {idx}. {folder.name} ({quiz_count} quiz{'zes' if quiz_count != 1 else ''})")

    print("\n  0. Exit\n")

    try:
        choice = input("Select folder number: ").strip()

        if choice == "0":
            print("Cancelled by user.")
            sys.exit(0)

        choice_idx = int(choice) - 1

        if 0 <= choice_idx < len(folders):
            return folders[choice_idx]
        else:
            print(f"\nError: Invalid selection. Please choose 1-{len(folders)} or 0 to exit.")
            sys.exit(1)

    except ValueError:
        print("\nError: Please enter a valid number.")
        sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print("\n\nCancelled by user.")
        sys.exit(0)


def get_random_quiz_from_folder(folder: Path) -> Path:
    """
    Select a random quiz file from the specified folder.

    Args:
        folder: Path to folder containing quiz files

    Returns:
        Path to randomly selected quiz file

    Raises:
        FileNotFoundError: If no quiz files found in folder
    """
    # Get all JSON files, excluding known metadata files
    json_files = list(folder.glob("*.json"))
    quiz_files = [
        f for f in json_files
        if f.stem not in ['last_import', 'README', 'metadata']
    ]

    if not quiz_files:
        raise FileNotFoundError(f"No quiz files found in {folder}")

    return random.choice(quiz_files)


def find_latest_quiz(base_dir: str = "data/quizzes") -> Path:
    """
    Find the most recent quiz file from the last import.

    Args:
        base_dir: Base directory where quizzes are stored

    Returns:
        Path to the most recent quiz file

    Raises:
        FileNotFoundError: If no quizzes found or metadata missing
    """
    base_path = Path(base_dir)
    metadata_file = base_path / "last_import.json"

    if metadata_file.exists():
        # Use metadata from last import
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        quiz_files = metadata.get('quiz_files', [])
        if not quiz_files:
            raise FileNotFoundError("No quiz files found in last import metadata")

        # Pick a random quiz from the last import batch
        selected_quiz = random.choice(quiz_files)
        return Path(selected_quiz)

    # Fallback: find most recent quiz file by modification time
    quiz_files = list(base_path.rglob("quiz_*.json"))
    if not quiz_files:
        raise FileNotFoundError(f"No quiz files found in {base_path}")

    # Sort by modification time, newest first
    latest_quiz = max(quiz_files, key=lambda p: p.stat().st_mtime)
    return latest_quiz


def main():
    """Main entry point for the quiz runner script."""
    parser = argparse.ArgumentParser(
        prog='run_quiz.py',
        description='Interactive quiz runner with automatic grading and reporting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive folder selection (recommended):
    python run_quiz.py

  Run a specific quiz file:
    python run_quiz.py data/quizzes/az-104/quiz_001.json

  Run with custom pass threshold:
    python run_quiz.py data/quizzes/az-104/quiz_001.json --pass-threshold 75

  Run with additional text report:
    python run_quiz.py --report-output custom_reports/

Notes:
  - HTML reports are automatically generated in data/reports/
  - Pass threshold determines if the quiz is passed (default: 80%)
  - Use Ctrl+C at any time to exit the quiz
  - Answers are case-insensitive and whitespace-tolerant

For more information, see README.md
        """
    )

    parser.add_argument(
        'quiz_file',
        nargs='?',
        metavar='FILE',
        help='path to quiz JSON file (if omitted, interactive folder selection is shown)'
    )

    parser.add_argument(
        '-t', '--pass-threshold',
        type=float,
        default=80.0,
        metavar='PERCENT',
        help='minimum score percentage required to pass (default: 80.0)'
    )

    parser.add_argument(
        '-r', '--report-output',
        metavar='DIR',
        help='directory to save additional text report (HTML report always generated)'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='minimal output mode without decorative elements'
    )

    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='enable test mode (show sample quizzes, hidden by default in production)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    try:
        # Auto-select quiz if not provided
        if args.quiz_file:
            quiz_file = Path(args.quiz_file)
        else:
            # Show folder selection menu
            test_mode: bool = args.test_mode
            folders = get_quiz_folders(test_mode=test_mode)
            
            if not args.quiet and test_mode:
                print("\n⚠️  TEST MODE: Sample quizzes are visible\n", file=sys.stderr)
            
            selected_folder = select_quiz_folder(folders)
            quiz_file = get_random_quiz_from_folder(selected_folder)

            if not args.quiet:
                print(f"\nSelected folder: {selected_folder.name}")
                print(f"Selected quiz: {quiz_file.name}\n")

        # Validate quiz file
        if not quiz_file.exists():
            print(f"Error: Quiz file not found: {quiz_file}")
            sys.exit(1)

        # Load quiz
        if not args.quiet:
            print(f"Loading quiz from: {quiz_file}")

        quiz = Quiz.load(str(quiz_file))

        # Run quiz
        result = run_quiz(quiz, args.pass_threshold)

        # Display results
        if not args.quiet:
            display_results(result)
        else:
            print(f"Score: {result.score_percentage:.1f}% - {'PASS' if result.passed else 'FAIL'}")

        # Always save HTML report
        html_path = save_html_report(result, quiz)
        if not args.quiet:
            print(f"\n📄 HTML report saved to: {html_path}")

        # Save text report if requested
        if args.report_output:
            report_dir = Path(args.report_output)
            report_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = report_dir / f"report_{quiz.quiz_id}_{timestamp}.txt"

            result.save_report(str(report_file))
            print(f"\nText report saved to: {report_file}")

        # Exit with code based on pass/fail
        sys.exit(0 if result.passed else 1)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Invalid quiz file format - missing key: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
