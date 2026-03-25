/**
 * Quiz State Management
 * Centralized state for quiz application
 */

// Quiz data
export let quizzes = [];
export let currentQuiz = null;
export let currentQuizPath = null;
export let currentQuestionIndex = 0;
export let correctCount = 0;
export let failures = [];

// Timer state
export let startTime = null;
export let timerInterval = null;

// UI state
export let sidebarCollapsed = false;

// Local storage state
export let quizRuns = JSON.parse(localStorage.getItem('quizRuns') || '[]');

// State setters
export function setQuizzes(newQuizzes) {
    quizzes = newQuizzes;
}

export function setCurrentQuiz(quiz) {
    currentQuiz = quiz;
}

export function setCurrentQuizPath(path) {
    currentQuizPath = path;
}

export function setCurrentQuestionIndex(index) {
    currentQuestionIndex = index;
}

export function incrementQuestionIndex() {
    currentQuestionIndex++;
}

export function setCorrectCount(count) {
    correctCount = count;
}

export function incrementCorrectCount() {
    correctCount++;
}

export function setFailures(newFailures) {
    failures = newFailures;
}

export function addFailure(failure) {
    failures.push(failure);
}

export function setStartTime(time) {
    startTime = time;
}

export function setTimerInterval(interval) {
    timerInterval = interval;
}

export function setSidebarCollapsed(collapsed) {
    sidebarCollapsed = collapsed;
}

export function setQuizRuns(runs) {
    quizRuns = runs;
}

export function addQuizRun(run) {
    quizRuns.unshift(run);
    if (quizRuns.length > 100) {
        quizRuns = quizRuns.slice(0, 100); // Keep last 100
    }
    localStorage.setItem('quizRuns', JSON.stringify(quizRuns));
}

/**
 * Reset quiz state for a new quiz
 */
export function resetQuizState() {
    currentQuestionIndex = 0;
    correctCount = 0;
    failures = [];
    startTime = Date.now();
}
