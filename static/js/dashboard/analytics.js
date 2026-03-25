/**
 * Dashboard Analytics
 * Performance trends, quiz breakdown, and analytics displays
 */

import { quizRuns } from '../state/quiz-state.js';

/**
 * Display performance trends chart (last 10 runs)
 */
export function displayPerformanceTrends() {
    const trendsEl = document.getElementById('performanceTrends');
    if (quizRuns.length === 0) return;
    
    // Show last 10 runs as a trend
    const recentRuns = quizRuns.slice(0, 10).reverse();
    let html = '<div class="trend-bar">';
    
    recentRuns.forEach((run, index) => {
        const date = new Date(run.timestamp).toLocaleDateString();
        html += `
            <div class="trend-item">
                <div class="trend-label">${date} - ${run.quiz_id.substring(0, 15)}</div>
                <div class="trend-bar-container">
                    <div class="trend-bar-fill" style="width: ${run.score}%">
                        ${run.score.toFixed(0)}%
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    trendsEl.innerHTML = html;
}

/**
 * Display quiz breakdown by quiz_id
 */
export function displayQuizBreakdown() {
    const breakdownEl = document.getElementById('quizBreakdown');
    if (quizRuns.length === 0) return;
    
    // Group runs by quiz_id
    const quizStats = {};
    quizRuns.forEach(run => {
        if (!quizStats[run.quiz_id]) {
            quizStats[run.quiz_id] = {
                attempts: 0,
                totalScore: 0,
                passed: 0,
                bestScore: 0
            };
        }
        quizStats[run.quiz_id].attempts++;
        quizStats[run.quiz_id].totalScore += run.score;
        if (run.passed) quizStats[run.quiz_id].passed++;
        if (run.score > quizStats[run.quiz_id].bestScore) {
            quizStats[run.quiz_id].bestScore = run.score;
        }
    });
    
    let html = '<table class="report-table"><thead><tr>';
    html += '<th>Quiz</th><th>Attempts</th><th>Avg Score</th><th>Best Score</th><th>Pass Rate</th>';
    html += '</tr></thead><tbody>';
    
    Object.entries(quizStats).forEach(([quizId, stats]) => {
        const avgScore = (stats.totalScore / stats.attempts).toFixed(1);
        const passRate = ((stats.passed / stats.attempts) * 100).toFixed(0);
        html += `
            <tr>
                <td><strong>${quizId}</strong></td>
                <td>${stats.attempts}</td>
                <td>${avgScore}%</td>
                <td>${stats.bestScore.toFixed(1)}%</td>
                <td><span class="badge ${stats.passed > 0 ? 'badge-pass' : 'badge-fail'}">${passRate}%</span></td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    breakdownEl.innerHTML = html;
}

/**
 * Display recent quiz runs timeline (last 10)
 */
export function displayRecentRuns() {
    const listEl = document.getElementById('recentRunsList');
    if (quizRuns.length === 0) {
        listEl.innerHTML = '<p style="color: #B0BEC5; text-align: center; padding: 20px;">No quiz runs yet</p>';
        return;
    }
    
    const recentRuns = quizRuns.slice(0, 10);
    let html = '<div class="timeline">';
    
    recentRuns.forEach(run => {
        const date = new Date(run.timestamp);
        const timeStr = date.toLocaleString();
        const badge = run.score >= 90 ? 'excellent' : (run.passed ? 'pass' : 'fail');
        const badgeText = run.score >= 90 ? '🌟 Excellent' : (run.passed ? '✓ Pass' : '✗ Fail');
        
        html += `
            <div class="timeline-item">
                <div class="timeline-content">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <strong>${run.quiz_id}</strong>
                        <span class="badge badge-${badge}">${badgeText}</span>
                    </div>
                    <div style="color: #B0BEC5; font-size: 0.9em;">
                        ${timeStr}<br>
                        Score: <strong>${run.score.toFixed(1)}%</strong> • 
                        ${run.correct}/${run.total_questions} correct •
                        Time: ${Math.floor(run.time_spent / 60)}:${(run.time_spent % 60).toString().padStart(2, '0')}
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    listEl.innerHTML = html;
}

/**
 * Display pass/fail analysis statistics
 */
export function displayPassFailAnalysis() {
    const analysisEl = document.getElementById('passFailAnalysis');
    if (quizRuns.length === 0) return;
    
    const passed = quizRuns.filter(run => run.passed).length;
    const failed = quizRuns.length - passed;
    const excellent = quizRuns.filter(run => run.score >= 90).length;
    const avgPassScore = passed > 0 
        ? quizRuns.filter(run => run.passed).reduce((sum, run) => sum + run.score, 0) / passed 
        : 0;
    const avgFailScore = failed > 0 
        ? quizRuns.filter(run => !run.passed).reduce((sum, run) => sum + run.score, 0) / failed 
        : 0;
    
    let html = '<div class="analysis-grid">';
    html += `
        <div class="analysis-item" style="border-left-color: #455A64;">
            <div class="analysis-value" style="color: #455A64;">${passed}</div>
            <div class="analysis-label">Passed Quizzes</div>
        </div>
        <div class="analysis-item" style="border-left-color: #455A64;">
            <div class="analysis-value" style="color: #455A64;">${failed}</div>
            <div class="analysis-label">Failed Quizzes</div>
        </div>
        <div class="analysis-item" style="border-left-color: #B0BEC5;">
            <div class="analysis-value" style="color: #455A64;">${excellent}</div>
            <div class="analysis-label">Excellent (90%+)</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-value">${avgPassScore.toFixed(1)}%</div>
            <div class="analysis-label">Avg Pass Score</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-value">${avgFailScore.toFixed(1)}%</div>
            <div class="analysis-label">Avg Fail Score</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-value">${((passed / quizRuns.length) * 100).toFixed(0)}%</div>
            <div class="analysis-label">Success Rate</div>
        </div>
    `;
    html += '</div>';
    analysisEl.innerHTML = html;
}

/**
 * Display results history table
 */
export function displayResultsHistory() {
    const historyEl = document.getElementById('resultsHistory');
    if (quizRuns.length === 0) {
        historyEl.innerHTML = '<p style="color: #B0BEC5; text-align: center; padding: 20px;">No quiz results yet</p>';
        return;
    }
    
    let html = '<table class="report-table"><thead><tr>';
    html += '<th>Date & Time</th>';
    html += '<th>Quiz</th>';
    html += '<th>Score</th>';
    html += '<th>Result</th>';
    html += '<th>Time</th>';
    html += '<th>Report</th>';
    html += '</tr></thead><tbody>';
    
    quizRuns.forEach(run => {
        const date = new Date(run.timestamp);
        const dateStr = date.toLocaleDateString();
        const timeStr = date.toLocaleTimeString();
        const badge = run.passed ? 'badge-pass' : 'badge-fail';
        const badgeText = run.passed ? '✓ Pass' : '✗ Fail';
        const minutes = Math.floor(run.time_spent / 60);
        const seconds = run.time_spent % 60;
        const timeSpent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        html += `
            <tr>
                <td style="font-size: 0.9em;">${dateStr}<br><span style="color: #B0BEC5;">${timeStr}</span></td>
                <td><strong>${run.quiz_id}</strong></td>
                <td><strong>${run.score.toFixed(1)}%</strong> (${run.correct}/${run.total_questions})</td>
                <td><span class="badge ${badge}">${badgeText}</span></td>
                <td>${timeSpent}</td>
                <td><a href="/report/${run.quiz_id}" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: 500;">View Report →</a></td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    historyEl.innerHTML = html;
}
