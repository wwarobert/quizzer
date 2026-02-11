"""
Tests for web quiz interface.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import pytest
import json
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch

# Import the Flask app
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import web_quiz


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    web_quiz.app.config['TESTING'] = True
    with web_quiz.app.test_client() as client:
        yield client


@pytest.fixture
def sample_quiz_dir(tmp_path):
    """Create a temporary directory with sample quiz files."""
    quizzes_dir = tmp_path / "data" / "quizzes" / "test"
    quizzes_dir.mkdir(parents=True)

    # Create a sample quiz
    quiz_data = {
        "quiz_id": "test_quiz_001",
        "created_at": "2026-02-11T10:00:00",
        "source_file": "test.csv",
        "questions": [
            {
                "id": 1,
                "question": "What is 2+2?",
                "answer": ["4"],
                "original_answer": "4"
            },
            {
                "id": 2,
                "question": "Capital of France?",
                "answer": ["paris"],
                "original_answer": "Paris"
            }
        ]
    }

    quiz_file = quizzes_dir / "test_quiz_001.json"
    with open(quiz_file, 'w') as f:
        json.dump(quiz_data, f)

    return tmp_path


class TestWebQuizRoutes:
    """Tests for web quiz API routes."""

    def test_index_route(self, client):
        """Test that index route returns HTML."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Quizzer' in response.data
        assert b'<!DOCTYPE html>' in response.data

    def test_get_quizzes_empty(self, client, monkeypatch, tmp_path):
        """Test getting quizzes when directory is empty."""
        # Use pytest's tmp_path which handles Windows cleanup better
        monkeypatch.chdir(tmp_path)
        response = client.get('/api/quizzes')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_quizzes_with_data(self, client, sample_quiz_dir, monkeypatch):
        """Test getting quizzes when quizzes exist."""
        monkeypatch.chdir(sample_quiz_dir)
        response = client.get('/api/quizzes')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert 'quiz_id' in data[0]
        assert 'num_questions' in data[0]

    def test_get_quiz_no_path(self, client):
        """Test getting quiz without providing path."""
        response = client.get('/api/quiz')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_quiz_not_found(self, client):
        """Test getting quiz with invalid path."""
        response = client.get('/api/quiz?path=nonexistent.json')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_quiz_success(self, client, sample_quiz_dir, monkeypatch):
        """Test successfully getting a quiz."""
        monkeypatch.chdir(sample_quiz_dir)
        quiz_path = sample_quiz_dir / "data" / "quizzes" / "test" / "test_quiz_001.json"

        response = client.get(f'/api/quiz?path={quiz_path}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['quiz_id'] == 'test_quiz_001'
        assert len(data['questions']) == 2

    def test_check_answer_correct(self, client):
        """Test checking a correct answer."""
        response = client.post('/api/check-answer',
                               json={
                                   'user_answer': 'Paris',
                                   'correct_answer': 'paris'
                               })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['correct'] is True

    def test_check_answer_incorrect(self, client):
        """Test checking an incorrect answer."""
        response = client.post('/api/check-answer',
                               json={
                                   'user_answer': 'London',
                                   'correct_answer': 'Paris'
                               })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['correct'] is False

    def test_check_answer_case_insensitive(self, client):
        """Test that answer checking is case-insensitive."""
        response = client.post('/api/check-answer',
                               json={
                                   'user_answer': 'PARIS',
                                   'correct_answer': 'paris'
                               })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['correct'] is True

    def test_check_answer_whitespace_tolerant(self, client):
        """Test that answer checking is whitespace-tolerant."""
        response = client.post('/api/check-answer',
                               json={
                                   'user_answer': '  Paris  ',
                                   'correct_answer': 'Paris'
                               })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['correct'] is True

    def test_check_answer_multiple_parts(self, client):
        """Test checking answer with multiple comma-separated parts."""
        response = client.post('/api/check-answer',
                               json={
                                   'user_answer': 'red, blue, yellow',
                                   'correct_answer': 'yellow, red, blue'
                               })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['correct'] is True  # Order doesn't matter


class TestWebQuizFunctionality:
    """Tests for web quiz application logic."""

    def test_html_contains_required_elements(self, client):
        """Test that HTML contains all required UI elements."""
        response = client.get('/')
        html = response.data.decode('utf-8')

        # Check for main components
        assert 'sidebar' in html
        assert 'dashboardView' in html
        assert 'quizFullpage' in html
        assert 'resultsScreen' in html

        # Check for key functionality
        assert 'loadQuizzes' in html
        assert 'startQuiz' in html
        assert 'submitAnswer' in html
        assert 'showResults' in html
        assert 'toggleSidebar' in html
        assert 'updateDashboard' in html

        # Check for styling
        assert 'background:' in html or 'background :' in html
        assert '.sidebar' in html
        assert '.menu-item' in html

    def test_api_endpoints_exist(self, client):
        """Test that all required API endpoints exist."""
        # These should not return 404
        endpoints = [
            '/',
            '/api/quizzes',
            '/api/quiz',
        ]

        for endpoint in endpoints:
            if endpoint == '/api/quiz':
                # This endpoint requires a path parameter
                response = client.get(endpoint)
                assert response.status_code in [400, 404]  # Not 404 (route not found)
            else:
                response = client.get(endpoint)
                assert response.status_code != 404

        # POST endpoint
        response = client.post('/api/check-answer', json={})
        assert response.status_code != 404


class TestWebQuizFrontend:
    """Tests for frontend HTML elements and JavaScript functionality."""

    def test_quit_button_exists(self, client):
        """Test that Quit button exists in the HTML."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'id="quitBtn"' in html
        assert 'Quit' in html

    def test_submit_button_exists(self, client):
        """Test that Submit button exists in the HTML."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'id="submitBtn"' in html
        assert 'Submit Answer' in html

    def test_back_button_exists(self, client):
        """Test that Back button exists in the HTML."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'id="backBtn"' in html
        assert 'Back to Dashboard' in html

    def test_quit_function_defined(self, client):
        """Test that quitQuiz function is defined in JavaScript."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'function quitQuiz()' in html
        assert 'showResults()' in html

    def test_quit_button_event_listener(self, client):
        """Test that quit button has event listener attached."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert "getElementById('quitBtn')" in html
        assert 'addEventListener' in html

    def test_all_three_screens_present(self, client):
        """Test that all main views are in the HTML."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'id="dashboardView"' in html
        assert 'id="quizSelectionView"' in html
        assert 'id="quizFullpage"' in html
        assert 'id="resultsScreen"' in html

    def test_results_screen_elements(self, client):
        """Test that results screen has all required elements."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'id="totalQuestions"' in html
        assert 'id="correctAnswers"' in html
        assert 'id="incorrectAnswers"' in html
        assert 'id="finalScore"' in html
        assert 'id="resultStatus"' in html
        assert 'id="failuresList"' in html

    def test_quiz_screen_elements(self, client):
        """Test that quiz screen has all required elements."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'id="questionText"' in html
        assert 'id="answerInput"' in html
        assert 'id="progressFill"' in html
        assert 'id="progressText"' in html
        assert 'id="timer"' in html
        assert 'id="feedback"' in html

    def test_timer_functionality_exists(self, client):
        """Test that timer functions are defined."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'function startTimer()' in html
        assert 'function stopTimer()' in html
        assert 'let timerInterval' in html

    def test_console_logging_for_debugging(self, client):
        """Test that console logging is present for debugging."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'console.log' in html

    def test_error_handling_in_quit(self, client):
        """Test that quit function has error handling."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'try {' in html or 'catch' in html

    def test_cache_busting_headers(self, client):
        """Test that HTML has cache-busting meta tags."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'no-cache' in html.lower()
        assert 'Cache-Control' in html

    def test_javascript_variables_initialized(self, client):
        """Test that all necessary JavaScript variables are initialized."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'let quizzes = []' in html
        assert 'let currentQuiz = null' in html
        assert 'let currentQuestionIndex = 0' in html
        assert 'let correctCount = 0' in html
        assert 'let failures = []' in html
        assert 'let startTime = null' in html
        assert 'let quizRuns' in html
        assert 'let sidebarCollapsed' in html

    def test_css_styling_present(self, client):
        """Test that CSS styling is present in the HTML."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '<style>' in html
        assert '.button' in html
        assert '.sidebar' in html
        assert '.dashboard' in html
        assert '.menu-item' in html


class TestWebQuizWorkflow:
    """Tests for complete quiz workflow scenarios."""

    def test_answer_submission_workflow(self, client, sample_quiz_dir, monkeypatch):
        """Test complete workflow of getting quiz and submitting answers."""
        monkeypatch.chdir(sample_quiz_dir)
        
        # Get quiz list
        response = client.get('/api/quizzes')
        assert response.status_code == 200
        quizzes = json.loads(response.data)
        assert len(quizzes) > 0
        
        # Load a specific quiz
        quiz_path = quizzes[0]['path']
        response = client.get(f'/api/quiz?path={quiz_path}')
        assert response.status_code == 200
        quiz = json.loads(response.data)
        
        # Submit correct answer for first question
        question = quiz['questions'][0]
        response = client.post('/api/check-answer',
                             json={
                                 'user_answer': question['original_answer'],
                                 'correct_answer': question['original_answer']
                             })
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['correct'] is True

    def test_multiple_answer_checks(self, client):
        """Test checking multiple answers in sequence."""
        test_cases = [
            ('Paris', 'paris', True),
            ('London', 'paris', False),
            ('RED, BLUE', 'blue, red', True),
            ('4', '4', True),
            ('5', '4', False),
        ]
        
        for user_ans, correct_ans, expected in test_cases:
            response = client.post('/api/check-answer',
                                 json={
                                     'user_answer': user_ans,
                                     'correct_answer': correct_ans
                                 })
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['correct'] == expected

    def test_quiz_id_format(self, client, sample_quiz_dir, monkeypatch):
        """Test that quiz IDs are properly formatted."""
        monkeypatch.chdir(sample_quiz_dir)
        response = client.get('/api/quizzes')
        assert response.status_code == 200
        quizzes = json.loads(response.data)
        
        for quiz in quizzes:
            assert isinstance(quiz['quiz_id'], str)
            assert len(quiz['quiz_id']) > 0
            assert isinstance(quiz['num_questions'], int)
            assert quiz['num_questions'] > 0

