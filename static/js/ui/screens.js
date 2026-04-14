/**
 * Screen/View Management
 * Handles switching between different views (dashboard, quiz selection, quiz, results)
 */

import { setActiveQuizPath } from '../state/quiz-state.js';

/**
 * Show a specific view and hide others
 * @param {string} viewName - Name of the view to show (dashboard, quizSelection, quiz)
 * @param {Function} updateDashboardCallback - Callback to update dashboard if needed
 */
export function showView(viewName, updateDashboardCallback) {
    console.log('Showing view:', viewName);
    
    // Hide all views
    document.querySelectorAll('.view').forEach(view => view.classList.add('hidden'));
    
    // Show selected view
    if (viewName === 'dashboard') {
        document.getElementById('dashboardView').classList.remove('hidden');
        if (updateDashboardCallback) {
            updateDashboardCallback();
        }
    } else if (viewName === 'quizSelection') {
        document.getElementById('quizSelectionView').classList.remove('hidden');
    } else if (viewName === 'quiz') {
        document.getElementById('quizView').classList.remove('hidden');
    }

    // Update active menu items
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
        item.removeAttribute('aria-current');
    });
    document.querySelectorAll('.expandable-header').forEach(h => h.classList.remove('active'));

    if (viewName === 'dashboard') {
        // Mark the Dashboard button active, clear active quiz item
        setActiveQuizPath(null);
        document.querySelectorAll('.quiz-menu-item').forEach(el => el.classList.remove('active'));
        const dashboardBtn = document.querySelector('.menu-item[onclick*="dashboard"]');
        if (dashboardBtn) {
            dashboardBtn.classList.add('active');
            dashboardBtn.setAttribute('aria-current', 'page');
        }
    } else if (viewName === 'quiz') {
        // Mark the Available Quizzes header active while quiz is running
        const quizMenuToggle = document.getElementById('quizMenuToggle');
        if (quizMenuToggle) {
            quizMenuToggle.classList.add('active');
        }
    } else if (event && event.target) {
        const active = event.target.closest('.menu-item');
        if (active) {
            active.classList.add('active');
            active.setAttribute('aria-current', 'page');
        }
    }

    // Move focus to the view title for screen readers
    const title = document.querySelector(`#${viewName}View .view-title`);
    if (title) {
        title.focus();
    }
}

/**
 * Show a specific screen (legacy function for results screen)
 * @param {string} screenId - Screen element ID to show
 */
export function showScreen(screenId) {
    document.getElementById('selectionScreen').classList.add('hidden');
    document.getElementById('quizScreen').classList.add('hidden');
    document.getElementById('resultsScreen').classList.add('hidden');
    document.getElementById(screenId).classList.remove('hidden');
}

/**
 * Toggle fullscreen mode
 */
export function toggleFullscreen() {
    document.body.classList.toggle('fullscreen-mode');
    const btn = document.getElementById('fullscreenToggle');
    if (document.body.classList.contains('fullscreen-mode')) {
        btn.textContent = '✕'; // X symbol for exit
        btn.title = 'Exit Fullscreen';
    } else {
        btn.textContent = '⛶'; // Fullscreen symbol
        btn.title = 'Toggle Fullscreen';
    }
}
