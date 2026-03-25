/**
 * Quiz Manager
 * Handles loading quizzes and displaying quiz lists
 */

import { quizzes, setQuizzes } from '../state/quiz-state.js';

/**
 * Load quiz list from API
 * @param {Function} displayMenuCallback - Callback to display quiz menu items
 * @param {Function} displayListCallback - Callback to display quiz list
 * @param {Function} updateDashboardCallback - Callback to update dashboard
 */
export async function loadQuizzes(displayMenuCallback, displayListCallback, updateDashboardCallback) {
    console.log('Loading quizzes...');
    const response = await fetch('/api/quizzes');
    const loadedQuizzes = await response.json();
    setQuizzes(loadedQuizzes);
    console.log('Loaded quizzes:', loadedQuizzes.length);
    
    if (displayMenuCallback) displayMenuCallback();
    if (displayListCallback) displayListCallback();
    if (updateDashboardCallback) updateDashboardCallback();
}

/**
 * Display quiz menu items in sidebar
 * @param {Function} startQuizCallback - Callback to start quiz when clicked
 */
export function displayQuizMenuItems(startQuizCallback) {
    const menuContent = document.getElementById('quizMenuContent');
    menuContent.innerHTML = '';

    if (quizzes.length === 0) {
        menuContent.innerHTML = '<div style="padding: 10px; color: rgba(255,255,255,0.7); font-size: 0.85em;">No quizzes available</div>';
        return;
    }

    quizzes.forEach(quiz => {
        const div = document.createElement('div');
        div.className = 'quiz-menu-item';
        div.setAttribute('role', 'button');
        div.setAttribute('tabindex', '0');
        div.textContent = quiz.quiz_id;
        div.onclick = () => startQuizCallback(quiz.path);
        div.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                startQuizCallback(quiz.path);
            }
        });
        menuContent.appendChild(div);
    });
}

/**
 * Display quiz list in quiz selection view
 * @param {Function} startQuizCallback - Callback to start quiz when clicked
 */
export function displayQuizList(startQuizCallback) {
    const listEl = document.getElementById('quizList');
    listEl.innerHTML = '';

    if (quizzes.length === 0) {
        listEl.innerHTML = '<p style="color: #B0BEC5; text-align: center; padding: 20px;">No quizzes available. Import some CSV files first!</p>';
        return;
    }

    quizzes.forEach(quiz => {
        const li = document.createElement('li');
        li.className = 'quiz-item';
        li.innerHTML = `
            <div class="quiz-item-title">${quiz.quiz_id}</div>
            <div class="quiz-item-details">
                ${quiz.num_questions} questions
                ${quiz.source_file ? '• ' + quiz.source_file : ''}
            </div>
        `;
        li.onclick = () => startQuizCallback(quiz.path);
        listEl.appendChild(li);
    });
}
