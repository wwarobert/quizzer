/**
 * Quiz Runner
 * Handles quiz execution, question display, answer submission, and results
 */

import { 
    currentQuiz, currentQuizPath, currentQuestionIndex, correctCount, failures,
    setCurrentQuiz, setCurrentQuizPath, resetQuizState,
    incrementQuestionIndex, incrementCorrectCount, addFailure, addQuizRun
} from '../state/quiz-state.js';
import { startTimer, stopTimer, getElapsedTime } from './timer.js';
import { showNotification } from '../ui/notifications.js';
import { showView } from '../ui/screens.js';
import { getMotivationalMessage } from '../config/motivational.js';

/**
 * Start a quiz
 * @param {string} quizPath - Path to quiz JSON file
 * @param {Function} updateDashboardCallback - Callback to update dashboard after quiz
 */
export async function startQuiz(quizPath, updateDashboardCallback) {
    console.log('Starting quiz:', quizPath);
    try {
        const response = await fetch(`/api/quiz?path=${encodeURIComponent(quizPath)}`);
        if (!response.ok) {
            throw new Error('Failed to load quiz');
        }
        const quiz = await response.json();
        setCurrentQuiz(quiz);
        setCurrentQuizPath(quizPath);
        resetQuizState();

        // Show quiz view
        showView('quiz', updateDashboardCallback);
        
        // Focus on quiz title
        const title = document.getElementById('quizTitle');
        if (title) title.focus();
        
        const quizName = quiz.quiz_id || 'Quiz';
        document.getElementById('quizBreadcrumb').textContent = quizName;
        
        startTimer();
        displayQuestion();
    } catch (error) {
        console.error('Error starting quiz:', error);
        showNotification('❌', 'Error', 'Failed to load quiz: ' + error.message);
    }
}

/**
 * Display current question
 */
export function displayQuestion() {
    const question = currentQuiz.questions[currentQuestionIndex];
    document.getElementById('questionText').textContent = question.question;
    document.getElementById('answerInput').value = '';
    document.getElementById('answerInput').focus();

    const progress = ((currentQuestionIndex + 1) / currentQuiz.questions.length) * 100;
    document.getElementById('progressFill').style.width = progress + '%';
    document.getElementById('progressText').textContent =
        `Question ${currentQuestionIndex + 1} of ${currentQuiz.questions.length}`;

    document.getElementById('feedback').classList.add('hidden');
    document.getElementById('submitBtn').disabled = false;
}

/**
 * Submit answer for current question
 * @param {Function} showResultsCallback - Callback to show results when quiz ends
 */
export async function submitAnswer(showResultsCallback) {
    const userAnswer = document.getElementById('answerInput').value.trim();
    if (!userAnswer) {
        showNotification('⚠️', 'Empty Answer', 'Please enter an answer before submitting.');
        return;
    }

    document.getElementById('submitBtn').disabled = true;

    try {
        const question = currentQuiz.questions[currentQuestionIndex];
        const response = await fetch('/api/check-answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_answer: userAnswer,
                correct_answer: question.original_answer
            })
        });

        if (!response.ok) {
            throw new Error('Failed to check answer');
        }

        const result = await response.json();
        const feedbackEl = document.getElementById('feedback');
        feedbackEl.classList.remove('hidden', 'feedback-correct', 'feedback-incorrect');

        if (result.correct) {
            incrementCorrectCount();
            feedbackEl.textContent = '✓ Correct!';
            feedbackEl.classList.add('feedback-correct');
        } else {
            addFailure({
                question_id: question.id,
                question: question.question,
                user_answer: userAnswer,
                correct_answer: question.original_answer
            });
            feedbackEl.innerHTML = `✗ Incorrect<br>Correct answer: ${question.original_answer}`;
            feedbackEl.classList.add('feedback-incorrect');
        }

        setTimeout(() => {
            incrementQuestionIndex();
            if (currentQuestionIndex < currentQuiz.questions.length) {
                displayQuestion();
            } else {
                showResultsCallback();
            }
        }, 2000);
    } catch (error) {
        console.error('Error submitting answer:', error);
        showNotification('❌', 'Error', 'Failed to submit answer: ' + error.message);
        document.getElementById('submitBtn').disabled = false;
    }
}

/**
 * Show quiz results
 * @param {Function} updateDashboardCallback - Callback to update dashboard after showing results
 */
export function showResults(updateDashboardCallback) {
    console.log('showResults called');
    stopTimer();
    
    const totalQuestions = currentQuiz.questions.length;
    const scorePercentage = (correctCount / totalQuestions * 100).toFixed(1);
    const passed = scorePercentage >= 80;
    const timeSpent = getElapsedTime();

    console.log('Results:', { totalQuestions, correctCount, scorePercentage, passed });

    // Save run to local storage
    const run = {
        quiz_id: currentQuiz.quiz_id,
        quiz_path: currentQuizPath,
        timestamp: new Date().toISOString(),
        score: parseFloat(scorePercentage),
        passed: passed,
        total_questions: totalQuestions,
        correct: correctCount,
        time_spent: timeSpent,
        failures: failures
    };
    addQuizRun(run);

    // Update stats
    document.getElementById('totalQuestions').textContent = totalQuestions;
    document.getElementById('correctAnswers').textContent = correctCount;
    document.getElementById('incorrectAnswers').textContent = failures.length;
    document.getElementById('finalScore').textContent = scorePercentage + '%';

    // Update status badge
    const statusBadge = document.getElementById('resultStatusBadge');
    statusBadge.textContent = passed ? '✓ PASS' : '✗ FAIL';
    statusBadge.className = 'results-status-badge ' + (passed ? 'results-status-pass' : 'results-status-fail');

    // Show motivational message
    const score = parseFloat(scorePercentage);
    const motivationalMsg = getMotivationalMessage(score);
    document.getElementById('motivationalMessage').textContent = motivationalMsg;

    // Handle failures section
    const failuresSection = document.getElementById('failuresSection');
    const failuresListEl = document.getElementById('failuresList');
    
    if (failures.length > 0) {
        failuresSection.classList.remove('hidden');
        failuresListEl.innerHTML = '';
        failures.forEach(failure => {
            const div = document.createElement('div');
            div.className = 'results-failure-item';
            div.innerHTML = `
                <div class="results-failure-question">Q${failure.question_id}: ${failure.question}</div>
                <div class="results-failure-answer">❌ Your answer: ${failure.user_answer}</div>
                <div class="results-failure-correct">✅ Correct answer: ${failure.correct_answer}</div>
            `;
            failuresListEl.appendChild(div);
        });
    } else {
        failuresSection.classList.add('hidden');
    }

    // Hide quiz view, exit fullscreen, show results
    document.querySelectorAll('.view').forEach(view => view.classList.add('hidden'));
    document.body.classList.remove('fullscreen-mode');
    document.getElementById('resultsScreen').classList.remove('hidden');
    
    console.log('Results displayed - no separate HTML report generated');
}

/**
 * Quit quiz and show results immediately
 */
export function quitQuiz(showResultsCallback) {
    console.log('quitQuiz called - going directly to results');
    if (!currentQuiz) {
        console.error('No quiz loaded');
        showNotification('⚠️', 'No Active Quiz', 'No quiz is currently active.');
        return;
    }
    
    try {
        // Exit fullscreen mode if active
        document.body.classList.remove('fullscreen-mode');
        showResultsCallback();
    } catch (error) {
        console.error('Error showing results:', error);
        showNotification('❌', 'Error', 'Error showing results: ' + error.message);
    }
}

/**
 * Return to selection screen from results
 * @param {Function} updateDashboardCallback - Callback to update dashboard
 */
export function backToSelection(updateDashboardCallback) {
    document.getElementById('resultsScreen').classList.add('hidden');
    document.body.classList.remove('fullscreen-mode');
    showView('dashboard', updateDashboardCallback);
}

/**
 * Generate and save HTML report
 */
export async function generateHtmlReport() {
    if (!currentQuiz) return;

    const totalQuestions = currentQuiz.questions.length;
    const scorePercentage = (correctCount / totalQuestions * 100).toFixed(1);
    const passed = scorePercentage >= 80;
    const timeSpent = getElapsedTime();

    const result = {
        quiz_id: currentQuiz.quiz_id,
        total_questions: totalQuestions,
        correct_count: correctCount,
        failures: failures,
        score_percentage: parseFloat(scorePercentage),
        passed: passed,
        time_spent: timeSpent
    };

    try {
        const response = await fetch('/api/save-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ result: result, quiz: currentQuiz })
        });

        if (response.ok) {
            const data = await response.json();
            console.log('Report saved:', data.report_path);
            const msgEl = document.getElementById('reportSavedMessage');
            if (msgEl) {
                msgEl.textContent = `Report saved to: ${data.report_path}`;
                msgEl.classList.remove('hidden');
            }
        } else {
            console.error('Failed to save report');
            const msgEl = document.getElementById('reportSavedMessage');
            if (msgEl) {
                msgEl.textContent = 'Warning: Failed to save report.';
                msgEl.classList.remove('hidden');
            }
        }
    } catch (error) {
        console.error('Error generating report:', error);
        const msgEl = document.getElementById('reportSavedMessage');
        if (msgEl) {
            msgEl.textContent = 'Error generating report: ' + error.message;
            msgEl.classList.remove('hidden');
        }
    }
}
