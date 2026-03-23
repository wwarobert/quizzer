"""
Quiz loading and management service.

This module provides business logic for quiz loading, listing, and validation.
Extracted from routes.py to improve testability and reusability.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from quizzer import Quiz, is_test_data
from quizzer.exceptions import InvalidQuizPathError
from quizzer.security import validate_quiz_path

logger = logging.getLogger("quizzer")


@dataclass
class QuizMetadata:
    """
    Metadata for a quiz file.

    Attributes:
        path: Full path to quiz JSON file
        quiz_id: Unique identifier for the quiz
        num_questions: Number of questions in the quiz
        source_file: Original CSV source filename
        created_at: ISO timestamp of quiz creation
    """

    path: str
    quiz_id: str
    num_questions: int
    source_file: str
    created_at: str

    def to_dict(self) -> dict:
        """Convert metadata to dictionary format for API responses."""
        return {
            "path": self.path,
            "quiz_id": self.quiz_id,
            "num_questions": self.num_questions,
            "source_file": self.source_file,
            "created_at": self.created_at,
        }


class QuizService:
    """
    Service for quiz loading and management.

    This service encapsulates the business logic for:
    - Loading quiz metadata from files
    - Listing available quizzes
    - Loading full quiz data
    - Quiz path validation
    """

    def __init__(self, quizzes_dir: Path):
        """
        Initialize QuizService.

        Args:
            quizzes_dir: Path to directory containing quiz JSON files
        """
        self.quizzes_dir = Path(quizzes_dir)

    def load_metadata(self, quiz_file: Path) -> Optional[QuizMetadata]:
        """
        Load quiz metadata from JSON file.

        Args:
            quiz_file: Path to quiz JSON file

        Returns:
            QuizMetadata object or None if loading fails

        Examples:
            >>> service = QuizService(Path("data/quizzes"))
            >>> metadata = service.load_metadata(Path("data/quizzes/quiz_001.json"))
            >>> metadata.quiz_id
            'quiz_001'
        """
        try:
            with open(quiz_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return QuizMetadata(
                    path=str(quiz_file),
                    quiz_id=data.get("quiz_id", quiz_file.stem),
                    num_questions=len(data.get("questions", [])),
                    source_file=data.get("source_file", ""),
                    created_at=data.get("created_at", ""),
                )
        except (json.JSONDecodeError, IOError, KeyError) as e:
            logger.warning(f"Error loading quiz file {quiz_file}: {e}")
            return None

    def list_quizzes(self, include_test_data: bool = False) -> List[QuizMetadata]:
        """
        List all available quizzes.

        Args:
            include_test_data: Whether to include test/sample quizzes (default: False)

        Returns:
            List of QuizMetadata objects, sorted by creation date (newest first)

        Examples:
            >>> service = QuizService(Path("data/quizzes"))
            >>> quizzes = service.list_quizzes()
            >>> len(quizzes) > 0
            True

            >>> quizzes = service.list_quizzes(include_test_data=True)
            >>> # Includes sample quizzes
        """
        quiz_files = []

        if not self.quizzes_dir.exists():
            logger.warning(f"Quizzes directory does not exist: {self.quizzes_dir}")
            return []

        # Search recursively for all quiz JSON files
        for quiz_file in self.quizzes_dir.rglob("*.json"):
            # Skip metadata files
            if quiz_file.name == "last_import.json":
                continue

            # Skip test data in production mode
            if not include_test_data and is_test_data(quiz_file.parent):
                logger.debug(f"Skipping test data quiz: {quiz_file}")
                continue

            # Load metadata
            metadata = self.load_metadata(quiz_file)
            if metadata:
                quiz_files.append(metadata)

        # Sort by creation date (newest first)
        quiz_files.sort(key=lambda x: x.created_at, reverse=True)

        logger.info(
            f"Found {len(quiz_files)} quizzes (include_test_data={include_test_data})"
        )
        return quiz_files

    def load_quiz(self, quiz_path: str) -> Quiz:
        """
        Load a full quiz from file path.

        Validates the path for security (prevents path traversal),
        then loads and returns the complete quiz data.

        Args:
            quiz_path: Relative or absolute path to quiz JSON file

        Returns:
            Quiz object with questions and metadata

        Raises:
            InvalidQuizPathError: If path is invalid or unsafe
            FileNotFoundError: If quiz file doesn't exist
            ValueError: If quiz file is malformed

        Examples:
            >>> service = QuizService(Path("data/quizzes"))
            >>> quiz = service.load_quiz("data/quizzes/quiz_001.json")
            >>> quiz.quiz_id
            'quiz_001'
            >>> len(quiz.questions) > 0
            True
        """
        # Validate and sanitize path (prevents path traversal attacks)
        validated_path = validate_quiz_path(quiz_path, self.quizzes_dir)

        logger.debug(f"Loading quiz from validated path: {validated_path}")

        # Load quiz using Quiz model
        quiz = Quiz.load(validated_path)

        logger.info(
            f"Quiz loaded successfully: {quiz.quiz_id} "
            f"({len(quiz.questions)} questions)"
        )

        return quiz

    def quiz_exists(self, quiz_path: str) -> bool:
        """
        Check if a quiz file exists.

        Args:
            quiz_path: Path to quiz file

        Returns:
            True if file exists, False otherwise

        Examples:
            >>> service = QuizService(Path("data/quizzes"))
            >>> service.quiz_exists("data/quizzes/quiz_001.json")
            True
            >>> service.quiz_exists("data/quizzes/nonexistent.json")
            False
        """
        try:
            validated_path = validate_quiz_path(quiz_path, self.quizzes_dir)
            return Path(validated_path).exists()
        except InvalidQuizPathError:
            return False

    def get_quiz_count(self, include_test_data: bool = False) -> int:
        """
        Get total count of available quizzes.

        Args:
            include_test_data: Whether to include test/sample quizzes

        Returns:
            Number of quizzes

        Examples:
            >>> service = QuizService(Path("data/quizzes"))
            >>> count = service.get_quiz_count()
            >>> count >= 0
            True
        """
        return len(self.list_quizzes(include_test_data=include_test_data))
