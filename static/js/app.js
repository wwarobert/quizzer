/**
 * Quizzer Web Application - Main Entry Point
 * Modular ES6 architecture with separated concerns
 */

// Import state management
import { quizzes } from './state/quiz-state.js';

// Import UI modules
import { showNotification } from './ui/notifications.js';
import { initSidebarButton, toggleQuizMenu } from './ui/sidebar.js';
import { showView, toggleFullscreen } from './ui/screens.js';

// Import quiz modules
import { loadQuizzes, displayQuizMenuItems, displayQuizList } from './quiz/quiz-manager.js';
import { 
    startQuiz, displayQuestion, submitAnswer, showResults, 
    quitQuiz, backToSelection, generateHtmlReport 
} from './quiz/quiz-runner.js';

// Import dashboard
import { updateDashboard } from './dashboard/dashboard.js';

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Initializing Quizzer application...');
    
    // Initialize sidebar
    initSidebarButton();
    
    // Initialize event listeners
    initEventListeners();
    
    // Load quizzes on startup
    loadQuizzes(
        () => displayQuizMenuItems(startQuizFromMenu, updateDashboard),
        () => displayQuizList(handleStartQuiz, updateDashboard),
        updateDashboard
    );
    
    // Show dashboard by default
    showView('dashboard', updateDashboard);
    
    console.log('Application initialized successfully');
}

/**
 * Start quiz from sidebar menu
 * @param {string} quizPath - Path to quiz file
 */
function startQuizFromMenu(quizPath) {
    console.log('Starting quiz from menu:', quizPath);
    handleStartQuiz(quizPath);
}

/**
 * Handle starting a quiz (wrapper for callback passing)
 * @param {string} quizPath - Path to quiz file
 */
function handleStartQuiz(quizPath) {
    startQuiz(quizPath, updateDashboard);
}

/**
 * Handle submit answer (wrapper for callback passing)
 */
function handleSubmitAnswer() {
    submitAnswer(() => showResults(updateDashboard));
}

/**
 * Handle quit quiz (wrapper for callback passing)
 */
function handleQuitQuiz() {
    quitQuiz(() => showResults(updateDashboard));
}

/**
 * Handle back to selection (wrapper for callback passing)
 */
function handleBackToSelection() {
    backToSelection(updateDashboard);
}

/**
 * Handle toggle quiz menu (wrapper for callback passing)
 */
function handleToggleQuizMenu() {
    toggleQuizMenu(() => {
        if (quizzes.length === 0) {
            loadQuizzes(
                () => displayQuizMenuItems(startQuizFromMenu, updateDashboard),
                () => displayQuizList(handleStartQuiz, updateDashboard),
                updateDashboard
            );
        }
    });
}

/**
 * Handle showing dashboard view
 */
function handleShowDashboard() {
    showView('dashboard', updateDashboard);
}

/**
 * Handle showing quiz selection view
 */
function handleShowQuizSelection() {
    showView('quizSelection', updateDashboard);
    displayQuizList(handleStartQuiz, updateDashboard);
}

/**
 * Initialize all event listeners
 */
function initEventListeners() {
    console.log('Initializing event listeners...');
    
    const submitBtn = document.getElementById('submitBtn');
    const quitBtn = document.getElementById('quitBtn');
    const backBtn = document.getElementById('backBtn');
    const answerInput = document.getElementById('answerInput');
    const fullscreenToggle = document.getElementById('fullscreenToggle');
    const retakeBtn = document.getElementById('retakeBtn');

    console.log('Elements found:', {
        submitBtn: !!submitBtn,
        quitBtn: !!quitBtn,
        backBtn: !!backBtn,
        answerInput: !!answerInput,
        fullscreenToggle: !!fullscreenToggle,
        retakeBtn: !!retakeBtn
    });

    if (submitBtn) {
        submitBtn.addEventListener('click', function(e) {
            console.log('Submit button clicked');
            handleSubmitAnswer();
        });
        console.log('Submit button listener attached');
    }

    if (quitBtn) {
        quitBtn.addEventListener('click', function(e) {
            console.log('Quit button clicked!');
            e.preventDefault();
            e.stopPropagation();
            handleQuitQuiz();
        });
        console.log('Quit button listener attached');
    }

    if (backBtn) {
        backBtn.addEventListener('click', function(e) {
            console.log('Back button clicked');
            handleBackToSelection();
        });
        console.log('Back button listener attached');
    }

    if (answerInput) {
        answerInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                console.log('Enter key pressed in answer input');
                handleSubmitAnswer();
            }
        });
        console.log('Answer input listener attached');
    }

    if (fullscreenToggle) {
        fullscreenToggle.addEventListener('click', function(e) {
            console.log('Fullscreen toggle clicked');
            toggleFullscreen();
        });
        console.log('Fullscreen toggle listener attached');
    }

    if (retakeBtn) {
        retakeBtn.addEventListener('click', function(e) {
            console.log('Retake button clicked');
            const quizPath = document.getElementById('resultsScreen').dataset.quizPath;
            if (quizPath) {
                handleStartQuiz(quizPath);
            }
        });
        console.log('Retake button listener attached');
    }
    
    console.log('Event listeners initialized successfully');
}

// Make functions globally available for inline event handlers
window.showView = (viewName) => {
    if (viewName === 'dashboard') {
        handleShowDashboard();
    } else if (viewName === 'quizSelection') {
        handleShowQuizSelection();
    } else {
        showView(viewName, updateDashboard);
    }
};
window.toggleQuizMenu = handleToggleQuizMenu;
window.loadQuizzes = () => loadQuizzes(
    () => displayQuizMenuItems(startQuizFromMenu, updateDashboard),
    () => displayQuizList(handleStartQuiz, updateDashboard),
    updateDashboard
);
window.startQuiz = handleStartQuiz;
window.submitAnswer = handleSubmitAnswer;
window.quitQuiz = handleQuitQuiz;
window.backToSelection = handleBackToSelection;
window.toggleFullscreen = toggleFullscreen;
window.generateHtmlReport = generateHtmlReport;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
