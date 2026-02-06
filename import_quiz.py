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
import random
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

from quizzer import normalize_answer, format_answer_display, Question, Quiz


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
    source_file: str = "",
    max_questions: int = 50
) -> Quiz:
    """
    Create a Quiz object from a list of question-answer pairs.
    
    Questions are randomized and limited to max_questions.
    
    Args:
        questions: List of (question, answer) tuples
        quiz_id: Unique identifier for the quiz
        source_file: Original CSV filename
        max_questions: Maximum number of questions per quiz (default: 50)
    
    Returns:
        Quiz object ready to be saved
    """
    # Randomize question order
    shuffled = questions.copy()
    random.shuffle(shuffled)
    
    # Limit to max questions
    selected = shuffled[:max_questions]
    
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
        description="Convert CSV question files to randomized quiz JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate one quiz from questions.csv
  python import_quiz.py data/input/questions.csv
  
  # Generate 3 quizzes to specific output directory
  python import_quiz.py questions.csv -o data/quizzes/ -n 3
  
  # Generate quiz with custom max questions
  python import_quiz.py questions.csv -m 25
        """
    )
    
    parser.add_argument(
        'csv_file',
        help='Path to CSV file with questions (first 2 columns: Question, Answer; additional columns ignored)'
    )
    parser.add_argument(
        '-o', '--output',
        default='data/quizzes/',
        help='Output directory for quiz JSON files (default: data/quizzes/)'
    )
    parser.add_argument(
        '-n', '--number',
        type=int,
        default=1,
        help='Number of quiz variations to generate (default: 1)'
    )
    parser.add_argument(
        '-m', '--max-questions',
        type=int,
        default=50,
        help='Maximum questions per quiz (default: 50)'
    )
    parser.add_argument(
        '--prefix',
        default='quiz',
        help='Prefix for quiz IDs (default: quiz)'
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
        
        if len(questions) < args.max_questions:
            print(
                f"Warning: CSV has {len(questions)} questions, "
                f"less than max {args.max_questions}"
            )
        
        # Create output directory with subfolder based on CSV filename
        base_output_dir = Path(args.output)
        csv_basename = Path(args.csv_file).stem  # filename without extension
        output_dir = base_output_dir / csv_basename
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate quizzes
        source_filename = Path(args.csv_file).name
        created_files = []
        
        for i in range(args.number):
            # Generate unique quiz ID with sequence number for multiple quizzes
            quiz_id = generate_quiz_id(args.prefix, i + 1 if args.number > 1 else None)
            quiz = create_quiz(
                questions, 
                quiz_id,
                source_file=source_filename,
                max_questions=args.max_questions
            )
            
            output_file = output_dir / f"{quiz_id}.json"
            quiz.save(str(output_file))
            created_files.append(str(output_file))
            
            print(
                f"Created quiz {i+1}/{args.number}: {output_file} "
                f"({len(quiz.questions)} questions)"
            )
        
        # Save metadata about last import
        metadata = {
            "last_import": datetime.now().isoformat(),
            "source_csv": args.csv_file,
            "csv_basename": csv_basename,
            "output_dir": str(output_dir.absolute()),
            "quiz_files": created_files,
            "num_quizzes": args.number,
            "total_questions": len(questions)
        }
        metadata_file = base_output_dir / "last_import.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✓ Successfully generated {args.number} quiz(zes)")
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
