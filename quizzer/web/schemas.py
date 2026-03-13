"""Request/Response validation schemas for web API endpoints.

This module uses Pydantic for runtime validation of API request payloads,
preventing malformed or malicious data from reaching the application logic.

Copyright 2026 - Apache License 2.0
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CheckAnswerRequest(BaseModel):
    """Request model for /api/check-answer endpoint.

    Validates that both user_answer and correct_answer are provided
    as non-empty strings.
    """

    user_answer: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The user's submitted answer",
    )
    correct_answer: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The correct answer to compare against",
    )

    @field_validator("user_answer", "correct_answer")
    @classmethod
    def validate_not_whitespace_only(cls, v: str) -> str:
        """Ensure answer is not just whitespace."""
        if not v.strip():
            raise ValueError("Answer cannot be empty or whitespace-only")
        return v


class QuizDataSchema(BaseModel):
    """Nested schema for quiz data in SaveReportRequest."""

    quiz_id: str = Field(..., min_length=1, max_length=255)
    created_at: str = Field(default="")
    source_file: str = Field(default="")

    model_config = ConfigDict(
        extra="allow"  # Allow additional fields for forward compatibility
    )


class FailureSchema(BaseModel):
    """Schema for individual quiz failures."""

    question: str = Field(..., min_length=1)
    user_answer: str = Field(...)
    correct_answer: str = Field(..., min_length=1)
    question_number: int = Field(..., ge=1)

    model_config = ConfigDict(extra="allow")


class ResultDataSchema(BaseModel):
    """Nested schema for result data in SaveReportRequest."""

    quiz_id: str = Field(..., min_length=1, max_length=255)
    total_questions: int = Field(..., ge=1, le=10000)
    correct_count: int = Field(..., ge=0)
    failures: list[FailureSchema] = Field(default_factory=list)
    score_percentage: float = Field(..., ge=0.0, le=100.0)
    passed: bool = Field(...)
    time_spent: int = Field(default=0, ge=0)

    @field_validator("correct_count")
    @classmethod
    def validate_correct_count(cls, v: int, info: Any) -> int:
        """Ensure correct_count doesn't exceed total_questions."""
        if "total_questions" in info.data and v > info.data["total_questions"]:
            raise ValueError("correct_count cannot exceed total_questions")
        return v

    model_config = ConfigDict(extra="allow")


class SaveReportRequest(BaseModel):
    """Request model for /api/save-report endpoint.

    Validates the structure of quiz results before generating reports.
    """

    result: ResultDataSchema = Field(..., description="Quiz result data")
    quiz: QuizDataSchema = Field(..., description="Quiz metadata")

    model_config = ConfigDict(
        extra="forbid"  # Reject unexpected fields for security
    )
