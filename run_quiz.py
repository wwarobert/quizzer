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
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from quizzer import answers_match, format_answer_display, Quiz, QuizResult


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
    print_header()
    print(f"Quiz ID: {quiz.quiz_id}")
    print(f"Questions: {len(quiz.questions)}")
    print(f"Pass threshold: {pass_threshold}%")
    print(f"\nInstructions:")
    print("  - For multiple answers, separate with commas (e.g., 'a, b, c')")
    print("  - Answers are case-insensitive")
    print("  - Whitespace is ignored")
    print("\nPress Ctrl+C to quit at any time.\n")
    
    input("Press Enter to start...")
    
    correct_count = 0
    failures: List[Dict[str, str]] = []
    
    for idx, question in enumerate(quiz.questions, 1):
        print_question(idx, len(quiz.questions), question.question)
        user_answer = get_user_answer()
        
        # Compare answers
        is_correct = answers_match(user_answer, question.original_answer)
        
        if is_correct:
            correct_count += 1
            print("✓ Correct!")
        else:
            print("✗ Incorrect")
            failures.append({
                'question_id': str(question.id),
                'question': question.question,
                'user_answer': format_answer_display(user_answer) if user_answer else "(no answer)",
                'correct_answer': question.original_answer
            })
    
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
        failures=failures
    )
    
    return result


def display_results(result: QuizResult):
    """
    Display quiz results to the console.
    
    Args:
        result: QuizResult object to display
    """
    print("\n" + "=" * 60)
    print("QUIZ COMPLETE".center(60))
    print("=" * 60 + "\n")
    
    print(f"Score: {result.correct_answers}/{result.total_questions} ({result.score_percentage:.1f}%)")
    
    if result.passed:
        print("Result: ✓ PASS")
    else:
        print("Result: ✗ FAIL")
    
    if result.failures:
        print(f"\nFailed Questions ({len(result.failures)}):")
        print("-" * 60)
        for failure in result.failures:
            print(f"\nQ{failure['question_id']}: {failure['question']}")
            print(f"  Your answer: {failure['user_answer']}")
            print(f"  Correct answer: {failure['correct_answer']}")
    else:
        print("\n🎉 Perfect score! All answers correct!")
    
    print("\n" + "=" * 60)


def main():
    """Main entry point for the quiz runner script."""
    parser = argparse.ArgumentParser(
        description="Run an interactive quiz from a JSON file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a quiz with default 80% pass threshold
  python run_quiz.py data/quizzes/quiz_001.json
  
  # Run with custom pass threshold
  python run_quiz.py quiz.json --pass-threshold 75
  
  # Save report to custom location
  python run_quiz.py quiz.json --report-output reports/
        """
    )
    
    parser.add_argument(
        'quiz_file',
        help='Path to quiz JSON file'
    )
    parser.add_argument(
        '-t', '--pass-threshold',
        type=float,
        default=80.0,
        help='Pass threshold percentage (default: 80.0)'
    )
    parser.add_argument(
        '-r', '--report-output',
        help='Directory to save report (optional, default: data/reports/)'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal output (no decorative elements)'
    )
    
    args = parser.parse_args()
    
    try:
        # Validate quiz file
        quiz_file = Path(args.quiz_file)
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
