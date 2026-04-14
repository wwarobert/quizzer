"""
Tests for quiz management features (delete, grouping, metadata).

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from quizzer.web import create_app


@pytest.fixture
def app_with_quizzes(tmp_path):
    """Create app with temp quiz directory containing test quizzes."""
    quizzes_dir = tmp_path / "data" / "quizzes"

    # Create az-104 group with 3 quizzes
    az_dir = quizzes_dir / "az-104"
    az_dir.mkdir(parents=True)
    for i in range(1, 4):
        quiz = {
            "quiz_id": f"az-104_20260209_164742_{i}",
            "created_at": f"2026-02-09T16:47:42.{i:06d}",
            "source_file": "az-104.csv",
            "questions": [
                {
                    "id": 1,
                    "question": f"Q{i}?",
                    "answer": ["a"],
                    "original_answer": "A",
                }
            ],
        }
        path = az_dir / f"az-104_20260209_164742_{i}.json"
        path.write_text(json.dumps(quiz), encoding="utf-8")

    # Create sample group with 1 quiz
    sample_dir = quizzes_dir / "sample_questions"
    sample_dir.mkdir(parents=True)
    sample_quiz = {
        "quiz_id": "sample_20260209_165453_1",
        "created_at": "2026-02-09T16:54:53.000001",
        "source_file": "sample_questions.csv",
        "questions": [
            {
                "id": 1,
                "question": "What is 2+2?",
                "answer": ["4"],
                "original_answer": "4",
            }
        ],
    }
    sample_path = sample_dir / "sample_20260209_165453_1.json"
    sample_path.write_text(
        json.dumps(sample_quiz), encoding="utf-8"
    )

    return tmp_path


@pytest.fixture
def client(app_with_quizzes, monkeypatch):
    """Test client with quiz data (test mode to see all quizzes)."""
    monkeypatch.chdir(app_with_quizzes)
    app = create_app(test_mode=True)
    app.config["TESTING"] = True

    import quizzer.web.routes as routes_module
    test_quizzes_dir = app_with_quizzes / "data" / "quizzes"
    monkeypatch.setattr(
        routes_module, "QUIZZES_DIR", test_quizzes_dir
    )

    with app.test_client() as client:
        yield client


@pytest.fixture
def prod_client(app_with_quizzes, monkeypatch):
    """Test client in production mode."""
    monkeypatch.chdir(app_with_quizzes)
    app = create_app(test_mode=False)
    app.config["TESTING"] = True

    import quizzer.web.routes as routes_module
    test_quizzes_dir = app_with_quizzes / "data" / "quizzes"
    monkeypatch.setattr(
        routes_module, "QUIZZES_DIR", test_quizzes_dir
    )

    with app.test_client() as client:
        yield client


class TestDeleteQuiz:
    """Tests for DELETE /api/quiz endpoint."""

    def test_delete_quiz_success(self, client, app_with_quizzes):
        """Delete a quiz file and verify it's removed."""
        quiz_path = "az-104/az-104_20260209_164742_1.json"
        resp = client.delete(f"/api/quiz?path={quiz_path}")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["success"] is True
        full_path = (
            app_with_quizzes / "data" / "quizzes" /
            "az-104" / "az-104_20260209_164742_1.json"
        )
        assert not full_path.exists()

    def test_delete_quiz_no_path(self, client):
        """Missing path parameter returns 400."""
        resp = client.delete("/api/quiz")
        assert resp.status_code == 400

    def test_delete_quiz_not_found(self, client):
        """Non-existent file returns 404."""
        resp = client.delete(
            "/api/quiz?path=az-104/nonexistent.json"
        )
        assert resp.status_code == 404

    def test_delete_quiz_path_traversal(self, client):
        """Path traversal attempt returns 400."""
        resp = client.delete(
            "/api/quiz?path=../../../etc/passwd"
        )
        assert resp.status_code == 400

    def test_delete_quiz_updates_list(self, client):
        """After deletion, quiz list is smaller."""
        # Get initial count
        resp = client.get("/api/quizzes")
        initial = json.loads(resp.data)
        initial_count = len(initial)

        # Delete one using relative path
        quiz_path = "az-104/az-104_20260209_164742_2.json"
        del_resp = client.delete(f"/api/quiz?path={quiz_path}")
        assert del_resp.status_code == 200

        # Verify count decreased
        resp = client.get("/api/quizzes")
        after = json.loads(resp.data)
        assert len(after) == initial_count - 1


class TestQuizListMetadata:
    """Tests for quiz list response metadata."""

    def test_quiz_list_has_source_file(self, client):
        """Each quiz in list includes source_file field."""
        resp = client.get("/api/quizzes")
        data = json.loads(resp.data)
        assert len(data) > 0
        for quiz in data:
            assert "source_file" in quiz

    def test_quiz_list_has_question_count(self, client):
        """Each quiz includes num_questions field."""
        resp = client.get("/api/quizzes")
        data = json.loads(resp.data)
        for quiz in data:
            assert "num_questions" in quiz
            assert quiz["num_questions"] >= 1

    def test_quiz_list_has_created_at(self, client):
        """Each quiz includes created_at timestamp."""
        resp = client.get("/api/quizzes")
        data = json.loads(resp.data)
        for quiz in data:
            assert "created_at" in quiz
            assert len(quiz["created_at"]) > 0

    def test_quiz_list_sorted_newest_first(self, client):
        """Quizzes are sorted by created_at descending."""
        resp = client.get("/api/quizzes")
        data = json.loads(resp.data)
        dates = [q["created_at"] for q in data]
        assert dates == sorted(dates, reverse=True)

    def test_production_mode_filters_samples(
        self, prod_client
    ):
        """Production mode excludes sample_questions folder."""
        resp = prod_client.get("/api/quizzes")
        data = json.loads(resp.data)
        ids = [q["quiz_id"] for q in data]
        assert not any("sample" in qid for qid in ids)

    def test_test_mode_includes_all(self, client):
        """Test mode returns both az-104 and sample quizzes."""
        resp = client.get("/api/quizzes")
        data = json.loads(resp.data)
        sources = {q["source_file"] for q in data}
        assert "az-104.csv" in sources
        assert "sample_questions.csv" in sources
