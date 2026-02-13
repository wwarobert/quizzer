"""
Quiz data models and validation.

This module defines the data structures used for storing and validating
quiz questions and results.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class Question:
    """
    Represents a single quiz question.

    Attributes:
        id: Unique identifier for the question within the quiz
        question: The question text
        answer: Normalized answer for comparison (lowercase, sorted)
        original_answer: Original answer text for display purposes
    """

    id: int
    question: str
    answer: List[str]
    original_answer: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary format."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Question":
        """Create Question from dictionary."""
        return cls(**data)


@dataclass
class Quiz:
    """
    Represents a complete quiz with metadata.

    Attributes:
        quiz_id: Unique identifier for the quiz
        created_at: ISO format timestamp of quiz creation
        questions: List of Question objects (max 50)
        source_file: Original CSV filename (optional)
    """

    quiz_id: str
    created_at: str
    questions: List[Question]
    source_file: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert quiz to dictionary format."""
        return {
            "quiz_id": self.quiz_id,
            "created_at": self.created_at,
            "source_file": self.source_file,
            "questions": [q.to_dict() for q in self.questions],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quiz":
        """Create Quiz from dictionary."""
        questions = [Question.from_dict(q) for q in data["questions"]]
        return cls(
            quiz_id=data["quiz_id"],
            created_at=data["created_at"],
            questions=questions,
            source_file=data.get("source_file", ""),
        )

    def save(self, filepath: str) -> None:
        """
        Save quiz to JSON file.

        Args:
            filepath: Path where the quiz JSON should be saved
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: str) -> "Quiz":
        """
        Load quiz from JSON file.

        Args:
            filepath: Path to the quiz JSON file

        Returns:
            Quiz object loaded from file
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class QuizResult:
    """
    Stores the results of a completed quiz attempt.

    Attributes:
        quiz_id: ID of the quiz that was taken
        completed_at: ISO format timestamp of completion
        total_questions: Total number of questions in the quiz
        correct_answers: Number of correct answers
        score_percentage: Percentage score (0-100)
        passed: Whether the quiz was passed (score >= 80%)
        failures: List of failed questions with user answers
        time_spent: Time spent on quiz in seconds
    """

    quiz_id: str
    completed_at: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    passed: bool
    failures: List[Dict[str, str]]
    time_spent: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return asdict(self)

    def generate_report(self) -> str:
        """
        Generate a formatted text report of quiz results.

        Returns:
            Multi-line string containing the full quiz report
        """
        mins, secs = divmod(int(self.time_spent), 60)
        time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

        lines = [
            f"Quiz Report - {self.quiz_id}",
            f"Date: {self.completed_at}",
            f"Questions: {self.total_questions}",
            f"Correct: {self.correct_answers}",
            f"Score: {self.score_percentage:.1f}%",
            f"Time Spent: {time_str}",
            f"Result: {'PASS' if self.passed else 'FAIL'}",
            "",
        ]

        if self.failures:
            lines.append(f"Failures ({len(self.failures)}):")
            lines.append("=" * 60)
            for failure in self.failures:
                lines.extend(
                    [
                        f"Q{failure['question_id']}: {failure['question']}",
                        f"  Your answer: {failure['user_answer']}",
                        f"  Correct answer: {failure['correct_answer']}",
                        "-" * 60,
                    ]
                )
        else:
            lines.append("Perfect score! All answers correct.")

        return "\n".join(lines)

    def save_report(self, filepath: str) -> None:
        """
        Save the quiz report to a text file.

        Args:
            filepath: Path where the report should be saved
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.generate_report())
