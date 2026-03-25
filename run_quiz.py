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
import json
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from quizzer import Quiz, QuizResult, answers_match, format_answer_display, is_test_data
from quizzer.constants import (
    DATA_DIR_NAME,
    DEFAULT_PASS_THRESHOLD,
    QUIZ_FILE_EXTENSION,
    QUIZZES_DIR_NAME,
    REPORTS_DIR_NAME,
)
from quizzer.template_utils import render_report_template


def select_quiz_folder(base_dir: str = f"{DATA_DIR_NAME}/{QUIZZES_DIR_NAME}") -> Path:
    """
    Interactively select a quiz folder if multiple exist.

    Why this function exists:
    When users have multiple quiz categories (e.g., Python, Azure, AWS),
    this provides a user-friendly way to choose without typing paths.

    Args:
        base_dir: Base directory containing quiz folders (default: data/quizzes)

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
        quiz_count = len(list(folder.glob(f"*{QUIZ_FILE_EXTENSION}")))
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
    Generate an HTML report for quiz results using Jinja2 template.

    This function now uses shared template rendering to eliminate code duplication.
    Previously contained 383 lines of embedded HTML/CSS, now delegates to template_utils.

    Args:
        result: QuizResult object with quiz results
        quiz: Quiz object with quiz metadata

    Returns:
        HTML string with formatted report
    """
    return render_report_template(result, quiz)


def save_html_report(
    result: QuizResult,
    quiz: Quiz,
    output_dir: str = f"{DATA_DIR_NAME}/{REPORTS_DIR_NAME}",
) -> Path:
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

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    return filepath


def clear_screen():
    """Clear the console screen."""
    os.system("cls" if os.name == "nt" else "clear")


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


def run_quiz(quiz: Quiz, pass_threshold: float = DEFAULT_PASS_THRESHOLD) -> QuizResult:
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
    print("\nInstructions:")
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
            failures.append(
                {
                    "question_id": str(question.id),
                    "question": question.question,
                    "user_answer": (
                        format_answer_display(user_answer)
                        if user_answer
                        else "(no answer)"
                    ),
                    "correct_answer": question.original_answer,
                    "explanation": question.original_explanation if question.original_explanation else "",
                }
            )

        # Show detailed answer
        print(
            f"\nYour answer: {format_answer_display(user_answer) if user_answer else '(no answer)'}"
        )
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
        time_spent=time_spent,
    )

    return result


def run_quiz_review_mode(quiz: Quiz) -> QuizResult:
    """
    Run the quiz in review mode with immediate feedback and explanations.

    In review mode:
    - Shows correct answer immediately after each question
    - Displays explanation if available
    - No pass/fail pressure, focus on learning
    - Still tracks statistics for reporting

    Args:
        quiz: Quiz object to run

    Returns:
        QuizResult object with complete results
    """
    clear_screen()
    print_header()
    print(f"Quiz ID: {quiz.quiz_id}")
    print(f"Questions: {len(quiz.questions)}")
    print("Mode: REVIEW (Learning Mode)")
    print("\nInstructions:")
    print("  - For multiple answers, separate with commas (e.g., 'a, b, c')")
    print("  - Answers are case-insensitive")
    print("  - Whitespace is ignored")
    print("  - You'll see the correct answer and explanation immediately")
    print("  - Focus on learning, not scoring!")
    print("\nPress Ctrl+C to quit at any time.\n")

    input("Press Enter to start...")

    start_time = time.time()
    correct_count = 0
    failures: List[Dict[str, str]] = []

    for idx, question in enumerate(quiz.questions, 1):
        # Clear screen and display question
        clear_screen()
        print("=" * 60)
        print(f"Question {idx}/{len(quiz.questions)} (REVIEW MODE)".center(60))
        print("=" * 60 + "\n")
        print(f"{question.question}\n")

        user_answer = get_user_answer()

        # Compare answers
        is_correct = answers_match(user_answer, question.original_answer)

        # Display result with immediate feedback
        print("\n" + "=" * 60)
        if is_correct:
            correct_count += 1
            print("✓ CORRECT!")
        else:
            print("✗ INCORRECT")
            failures.append(
                {
                    "question_id": str(question.id),
                    "question": question.question,
                    "user_answer": (
                        format_answer_display(user_answer)
                        if user_answer
                        else "(no answer)"
                    ),
                    "correct_answer": question.original_answer,
                    "explanation": question.original_explanation if question.original_explanation else "",
                }
            )

        # Always show the correct answer in review mode
        print()
        print(
            f"Your answer:    {format_answer_display(user_answer) if user_answer else '(no answer)'}"
        )
        print(f"Correct answer: {question.original_answer}")

        # Show explanation if available
        if question.explanation and question.explanation.strip():
            print("\n📘 Explanation:")
            print(f"   {question.explanation}")

        # Show running score
        print(f"\nCurrent Score: {correct_count}/{idx} ({(correct_count / idx) * 100:.1f}%)")
        print("=" * 60)

        # Wait for user to press Enter before continuing
        if idx < len(quiz.questions):
            input("\nPress Enter for next question...")

    # Calculate time spent
    end_time = time.time()
    time_spent = end_time - start_time

    # Calculate results (no pass/fail threshold in review mode)
    total_questions = len(quiz.questions)
    score_percentage = (correct_count / total_questions) * 100

    # Create result object (passed=True for review mode to avoid negative messaging)
    result = QuizResult(
        quiz_id=quiz.quiz_id,
        completed_at=datetime.now().isoformat(),
        total_questions=total_questions,
        correct_answers=correct_count,
        score_percentage=score_percentage,
        passed=True,  # Review mode always "passes" - it's for learning
        failures=failures,
        time_spent=time_spent,
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
    print(
        f"\nScore:               {result.correct_answers}/{result.total_questions} ({result.score_percentage:.1f}%)"
    )

    if result.passed:
        print("Result:              ✓ PASS")
    else:
        print("Result:              ✗ FAIL")

    print("\n" + "=" * 60)


def get_quiz_folders(
    base_dir: str = f"{DATA_DIR_NAME}/{QUIZZES_DIR_NAME}", test_mode: bool = False
) -> List[Path]:
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
            f for f in json_files if f.stem not in ["last_import", "README", "metadata"]
        ]
        if quiz_files:
            folders.append(item)

    # Sort folders alphabetically
    return sorted(folders, key=lambda p: p.name.lower())


def select_folder_from_list(folders: List[Path]) -> Path:
    """
    Display folder selection menu and get user choice.

    Why this exists separately from select_quiz_folder:
    This function handles the UI for choosing from a pre-filtered list,
    while select_quiz_folder finds folders from a directory path.

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
            f for f in json_files if f.stem not in ["last_import", "README", "metadata"]
        ]
        quiz_count = len(quiz_files)
        print(
            f"  {idx}. {folder.name} ({quiz_count} quiz{'zes' if quiz_count != 1 else ''})"
        )

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
            print(
                f"\nError: Invalid selection. Please choose 1-{len(folders)} or 0 to exit."
            )
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
        f for f in json_files if f.stem not in ["last_import", "README", "metadata"]
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
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        quiz_files = metadata.get("quiz_files", [])
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
        prog="run_quiz.py",
        description="Interactive quiz runner with automatic grading and reporting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive folder selection (recommended):
    python run_quiz.py

  Run a specific quiz file:
    python run_quiz.py data/quizzes/az-104/quiz_001.json

  Run in review mode (learning with immediate feedback):
    python run_quiz.py --review

  Run with custom pass threshold:
    python run_quiz.py data/quizzes/az-104/quiz_001.json --pass-threshold 75

  Run with additional text report:
    python run_quiz.py --report-output custom_reports/

Notes:
  - HTML reports are automatically generated in data/reports/
  - Pass threshold determines if the quiz is passed (default: 80%)
  - Review mode shows answers and explanations immediately (great for learning!)
  - Use Ctrl+C at any time to exit the quiz
  - Answers are case-insensitive and whitespace-tolerant

For more information, see README.md
        """,
    )

    parser.add_argument(
        "quiz_file",
        nargs="?",
        metavar="FILE",
        help="path to quiz JSON file (if omitted, interactive folder selection is shown)",
    )

    parser.add_argument(
        "-t",
        "--pass-threshold",
        type=float,
        default=80.0,
        metavar="PERCENT",
        help="minimum score percentage required to pass (default: 80.0)",
    )

    parser.add_argument(
        "--review",
        action="store_true",
        help="review mode: show correct answers and explanations immediately after each question",
    )

    parser.add_argument(
        "-o",
        "--report-output",
        metavar="DIR",
        help="directory to save additional text report (HTML report always generated)",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="minimal output mode without decorative elements",
    )

    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="enable test mode (show sample quizzes, hidden by default in production)",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

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

            selected_folder = select_folder_from_list(folders)
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

        # Run quiz in appropriate mode
        if args.review:
            result = run_quiz_review_mode(quiz)
        else:
            result = run_quiz(quiz, args.pass_threshold)

        # Display results
        if not args.quiet:
            display_results(result)
        else:
            print(
                f"Score: {result.score_percentage:.1f}% - {'PASS' if result.passed else 'FAIL'}"
            )

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
