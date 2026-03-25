/**
 * Quiz Timer
 * Manages quiz timer display and control
 */

import { startTime, timerInterval, setStartTime, setTimerInterval } from '../state/quiz-state.js';

/**
 * Start the quiz timer
 */
export function startTimer() {
    setStartTime(Date.now());
    const interval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        document.getElementById('timer').textContent = `Time: ${minutes}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
    setTimerInterval(interval);
}

/**
 * Stop the quiz timer
 */
export function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        setTimerInterval(null);
    }
}

/**
 * Get elapsed time in seconds
 * @returns {number} Elapsed time in seconds
 */
export function getElapsedTime() {
    return startTime ? Math.floor((Date.now() - startTime) / 1000) : 0;
}
