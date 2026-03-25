/**
 * Dashboard Management
 * Main dashboard update and coordination
 */

import { quizzes, quizRuns } from '../state/quiz-state.js';
import {
    displayPerformanceTrends,
    displayQuizBreakdown,
    displayRecentRuns,
    displayPassFailAnalysis,
    displayResultsHistory
} from './analytics.js';

/**
 * Update all dashboard statistics and charts
 */
export function updateDashboard() {
    console.log('Updating dashboard');
    
    // Update quiz count
    document.getElementById('totalQuizzes').textContent = quizzes.length;
    
    // Update run statistics
    document.getElementById('totalRuns').textContent = quizRuns.length;
    
    if (quizRuns.length > 0) {
        // Calculate statistics
        const avgScore = quizRuns.reduce((sum, run) => sum + run.score, 0) / quizRuns.length;
        const bestScore = Math.max(...quizRuns.map(run => run.score));
        const totalQuestions = quizRuns.reduce((sum, run) => sum + run.total_questions, 0);
        const passCount = quizRuns.filter(run => run.passed).length;
        const passRate = (passCount / quizRuns.length * 100).toFixed(1);
        
        document.getElementById('avgScore').textContent = avgScore.toFixed(1) + '%';
        document.getElementById('passRate').textContent = passRate + '%';
        document.getElementById('bestScore').textContent = bestScore.toFixed(1) + '%';
        document.getElementById('totalQuestions').textContent = totalQuestions;
        
        // Update all report sections
        displayPerformanceTrends();
        displayQuizBreakdown();
        displayRecentRuns();
        displayPassFailAnalysis();
        displayResultsHistory();
    } else {
        document.getElementById('avgScore').textContent = '0%';
        document.getElementById('passRate').textContent = '0%';
        document.getElementById('bestScore').textContent = '0%';
        document.getElementById('totalQuestions').textContent = '0';
    }
}
