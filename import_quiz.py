#!/usr/bin/env python3
"""
Import Quiz Script - CSV to JSON Converter

This script reads a CSV file with question-answer pairs and generates
randomized quiz JSON files with up to 50 questions each.

Usage:
    python import_quiz.py input.csv -o output_dir/ -n 3

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import csv
import json
import math
import random
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

from quizzer import normalize_answer, format_answer_display, Question, Quiz


def check_existing_quizzes(output_dir: Path) -> List[Path]:
    """
    Check for existing quiz JSON files in the output directory.
    
    Args:
        output_dir: Path to the output directory
    
    Returns:
        List of existing quiz JSON file paths
    """
    if not output_dir.exists():
        return []
    
    # Find all JSON files (quizzes) in the directory
    quiz_files = list(output_dir.glob("*.json"))
    return quiz_files


def prompt_delete_existing_quizzes(quiz_files: List[Path]) -> bool:
    """
    Prompt the user whether to delete existing quizzes.
    
    Args:
        quiz_files: List of existing quiz file paths
    
    Returns:
        True if user wants to delete, False if user wants to keep
    """
    print(f"\n⚠️  Found {len(quiz_files)} existing quiz(zes) in this folder:")
    for quiz_file in quiz_files:
        print(f"  - {quiz_file.name}")
    
    while True:
        response = input("\nDo you want to DELETE these quizzes before importing? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please answer 'yes' or 'no'")


def delete_quiz_files(quiz_files: List[Path]) -> None:
    """
    Delete quiz files from the directory.
    
    Args:
        quiz_files: List of quiz file paths to delete
    """
    print("\nDeleting existing quizzes...")
    for quiz_file in quiz_files:
        try:
            quiz_file.unlink()
            print(f"  ✓ Deleted: {quiz_file.name}")
        except Exception as e:
            print(f"  ✗ Failed to delete {quiz_file.name}: {e}")
    print("Deletion complete.\n")


def read_csv_questions(filepath: str) -> List[Tuple[str, str]]:
    """
    Read questions and answers from a CSV file.
    
    Expected format: At least 2 columns (Question, Answer).
    Only the first 2 columns are used; additional columns are ignored.
    If a header row is detected (first row contains "question" or "answer"),
    it will be skipped.
    
    Args:
        filepath: Path to the CSV file
    
    Returns:
        List of (question, answer) tuples
    
    Raises:
        ValueError: If CSV doesn't have at least 2 columns
        FileNotFoundError: If CSV file doesn't exist
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    
    questions = []
    
    # Try multiple encodings in order of preference
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    last_error = None
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding, newline='') as f:
                reader = csv.reader(f)
                questions = []  # Reset for each encoding attempt
                
                for i, row in enumerate(reader, 1):
                    # Validate column count - need at least 2 columns
                    if len(row) < 2:
                        raise ValueError(
                            f"Row {i} has {len(row)} column(s), expected at least 2. "
                            f"Each row must have at least Question,Answer format."
                        )
                    
                    # Use only first 2 columns, ignore the rest
                    question, answer = row[0], row[1]
                    question = question.strip()
                    answer = answer.strip()
                    
                    # Skip potential header row
                    if i == 1 and (
                        'question' in question.lower() or 
                        'answer' in answer.lower()
                    ):
                        continue
                    
                    # Skip empty rows
                    if not question or not answer:
                        print(f"Warning: Skipping row {i} with empty question or answer")
                        continue
                    
                    questions.append((question, answer))
            
            # If we got here, encoding worked - break out of loop
            break
            
        except (UnicodeDecodeError, UnicodeError) as e:
            last_error = e
            continue  # Try next encoding
    
    else:
        # All encodings failed
        raise UnicodeDecodeError(
            'multiple',
            b'',
            0,
            1,
            f"Failed to decode file with any of the attempted encodings: {encodings}. "
            f"Last error: {last_error}"
        )
    
    return questions


def create_quiz(
    questions: List[Tuple[str, str]], 
    quiz_id: str,
    source_file: str = ""
) -> Quiz:
    """
    Create a Quiz object from a list of question-answer pairs.
    
    Questions are used as provided (no shuffling or limiting).
    
    Args:
        questions: List of (question, answer) tuples (already shuffled/limited)
        quiz_id: Unique identifier for the quiz
        source_file: Original CSV filename
    
    Returns:
        Quiz object ready to be saved
    """
    # Use questions as provided
    selected = questions
    
    # Create Question objects
    quiz_questions = []
    for idx, (q_text, a_text) in enumerate(selected, 1):
        question = Question(
            id=idx,
            question=q_text,
            answer=normalize_answer(a_text),
            original_answer=format_answer_display(a_text)
        )
        quiz_questions.append(question)
    
    # Create Quiz object
    quiz = Quiz(
        quiz_id=quiz_id,
        created_at=datetime.now().isoformat(),
        questions=quiz_questions,
        source_file=source_file
    )
    
    return quiz


def generate_quiz_id(prefix: str = "quiz", sequence: int = None) -> str:
    """
    Generate a unique quiz ID using timestamp and optional sequence number.
    
    Args:
        prefix: Prefix for the quiz ID (default: "quiz")
        sequence: Optional sequence number for uniqueness (1-based)
    
    Returns:
        Unique quiz ID string (e.g., "quiz_20260206_103045" or "quiz_20260206_103045_1")
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if sequence is not None:
        return f"{prefix}_{timestamp}_{sequence}"
    return f"{prefix}_{timestamp}"


def main():
    """Main entry point for the import script."""
    parser = argparse.ArgumentParser(
        prog='import_quiz.py',
        description='Convert CSV question files into randomized quiz JSON files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate one quiz from CSV:
    python import_quiz.py data/input/questions.csv
  
  Generate multiple quizzes to specific directory:
    python import_quiz.py questions.csv --output data/quizzes/az-104/ --number 5
  
  Generate quiz with custom question limit:
    python import_quiz.py questions.csv --max-questions 25
  
  Generate with custom prefix:
    python import_quiz.py questions.csv --prefix midterm

CSV Format:
  - Must have exactly 2 columns: Question, Answer
  - Header row is optional (auto-detected)
  - Use quotes for answers containing commas
  - Multiple answers separated by commas: "red, blue, yellow"

For more information, see README.md
        """
    )
    
    parser.add_argument(
        'csv_file',
        metavar='FILE',
        help='path to CSV file with questions (columns: Question, Answer)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='data/quizzes/',
        metavar='DIR',
        help='output directory for quiz JSON files (default: data/quizzes/)'
    )
    
    parser.add_argument(
        '-n', '--number',
        type=int,
        default=None,
        metavar='N',
        help='number of quizzes to generate (default: auto-calculate from questions)'
    )
    
    parser.add_argument(
        '-m', '--max-questions',
        type=int,
        default=50,
        metavar='N',
        help='maximum questions per quiz (default: 50)'
    )
    
    parser.add_argument(
        '--prefix',
        default='quiz',
        metavar='TEXT',
        help='prefix for quiz IDs (default: quiz)'
    )
    
    parser.add_argument(
        '--allow-duplicates',
        action='store_true',
        help='allow duplicate questions across quizzes (enables random selection mode)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        # Read CSV questions
        print(f"Reading questions from: {args.csv_file}")
        questions = read_csv_questions(args.csv_file)
        print(f"Loaded {len(questions)} questions")
        
        if len(questions) == 0:
            print("Error: No valid questions found in CSV file")
            sys.exit(1)
        
        # Shuffle all questions once
        shuffled_questions = questions.copy()
        random.shuffle(shuffled_questions)
        
        # Calculate number of quizzes needed
        if args.allow_duplicates:
            # Old behavior: random selection with possible duplicates
            num_quizzes = args.number if args.number else 1
            quiz_sizes = [args.max_questions] * num_quizzes
            if len(questions) < args.max_questions:
                print(
                    f"Warning: CSV has {len(questions)} questions, "
                    f"less than max {args.max_questions}"
                )
                quiz_sizes = [len(questions)] * num_quizzes
        else:
            # New behavior: split all questions evenly across quizzes
            # Use rounding to stay close to max_questions per quiz
            calculated_quizzes = max(1, round(len(questions) / args.max_questions))
            
            if args.number is None:
                num_quizzes = calculated_quizzes
            else:
                num_quizzes = args.number
                if num_quizzes < calculated_quizzes:
                    print(
                        f"Warning: {len(questions)} questions need {calculated_quizzes} quizzes "
                        f"(max {args.max_questions} each), but only generating {num_quizzes}. "
                        f"Some questions will not be used."
                    )
            
            # Distribute questions evenly across quizzes
            base_size = len(questions) // num_quizzes
            remainder = len(questions) % num_quizzes
            
            # First 'remainder' quizzes get base_size + 1, rest get base_size
            quiz_sizes = [base_size + 1] * remainder + [base_size] * (num_quizzes - remainder)
        
        print(f"Generating {num_quizzes} quiz(zes) from {len(questions)} questions")
        print(f"  Quiz sizes: {', '.join(str(s) for s in quiz_sizes)}")
        
        # Create output directory with subfolder based on CSV filename
        base_output_dir = Path(args.output)
        csv_basename = Path(args.csv_file).stem  # filename without extension
        output_dir = base_output_dir / csv_basename
        
        # Check for existing quizzes before creating new ones
        existing_quizzes = check_existing_quizzes(output_dir)
        if existing_quizzes:
            should_delete = prompt_delete_existing_quizzes(existing_quizzes)
            if should_delete:
                delete_quiz_files(existing_quizzes)
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate quizzes
        source_filename = Path(args.csv_file).name
        created_files = []
        question_index = 0  # Track position in questions list
        
        for i in range(num_quizzes):
            # Generate unique quiz ID with sequence number for multiple quizzes
            quiz_id = generate_quiz_id(args.prefix, i + 1 if num_quizzes > 1 else None)
            
            # Get questions for this quiz
            if args.allow_duplicates:
                # Old behavior: random selection with possible duplicates
                quiz_questions = shuffled_questions.copy()
                random.shuffle(quiz_questions)
                quiz_questions = quiz_questions[:quiz_sizes[i]]
            else:
                # New behavior: split questions evenly (no duplicates)
                quiz_size = quiz_sizes[i]
                quiz_questions = shuffled_questions[question_index:question_index + quiz_size]
                question_index += quiz_size
            
            quiz = create_quiz(
                quiz_questions,
                quiz_id,
                source_file=source_filename
            )
            
            output_file = output_dir / f"{quiz_id}.json"
            quiz.save(str(output_file))
            created_files.append(str(output_file))
            
            print(
                f"Created quiz {i+1}/{num_quizzes}: {output_file} "
                f"({len(quiz.questions)} questions)"
            )
        
        # Save metadata about last import
        metadata = {
            "last_import": datetime.now().isoformat(),
            "source_csv": args.csv_file,
            "csv_basename": csv_basename,
            "output_dir": str(output_dir.absolute()),
            "quiz_files": created_files,
            "num_quizzes": num_quizzes,
            "total_questions": len(questions)
        }
        metadata_file = base_output_dir / "last_import.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✓ Successfully generated {num_quizzes} quiz(zes)")
        print(f"  Output directory: {output_dir.absolute()}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
