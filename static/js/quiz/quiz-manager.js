/**
 * Quiz Manager
 * Handles loading quizzes and displaying quiz lists
 */

import { quizzes, setQuizzes, quizRuns, activeQuizPath, setActiveQuizPath } from '../state/quiz-state.js';
import { showNotification } from '../ui/notifications.js';

/**
 * Parse a quiz object into a friendly display name and metadata.
 * @param {Object} quiz - Quiz metadata from API
 * @returns {Object} Parsed quiz info with group, label, questionCount
 */
function parseQuizInfo(quiz) {
    const sourceFile = quiz.source_file || '';
    const group = sourceFile
        ? sourceFile.replace(/\.csv$/i, '').replace(/[_-]/g, ' ')
        : 'Other';

    // Extract sequence number from quiz_id (e.g. "az-104_20260209_164742_3" -> 3)
    const parts = quiz.quiz_id.split('_');
    const seq = parts.length > 1 ? parts[parts.length - 1] : '1';
    const label = `Quiz #${seq}`;

    // Parse created_at into a readable date
    let createdDate = '';
    if (quiz.created_at) {
        try {
            const d = new Date(quiz.created_at);
            createdDate = d.toLocaleDateString(undefined, {
                year: 'numeric', month: 'short', day: 'numeric'
            });
        } catch (_) {
            createdDate = '';
        }
    }

    // Find best score and last run from localStorage
    const runs = quizRuns.filter(r => r.quiz_id === quiz.quiz_id);
    const bestScore = runs.length > 0
        ? Math.max(...runs.map(r => r.score)).toFixed(0) + '%'
        : null;
    const lastRun = runs.length > 0
        ? new Date(runs[0].date).toLocaleDateString()
        : null;

    return {
        group: group.charAt(0).toUpperCase() + group.slice(1),
        label,
        questionCount: quiz.num_questions || 0,
        createdDate,
        bestScore,
        lastRun,
        path: quiz.path,
        quiz_id: quiz.quiz_id,
    };
}

/**
 * Group quizzes by their source file.
 * @param {Array} quizList - Array of quiz metadata objects
 * @returns {Object} Map of group name -> array of parsed quiz info
 */
function groupQuizzes(quizList) {
    const groups = {};
    for (const quiz of quizList) {
        const info = parseQuizInfo(quiz);
        if (!groups[info.group]) {
            groups[info.group] = [];
        }
        groups[info.group].push(info);
    }
    // Sort quizzes within each group by sequence
    for (const group of Object.values(groups)) {
        group.sort((a, b) => a.label.localeCompare(
            b.label, undefined, { numeric: true }
        ));
    }
    return groups;
}

/**
 * Delete a quiz via the API and refresh the list.
 * @param {string} quizPath - Path to quiz JSON file
 * @param {Function} startQuizCallback - Callback for starting quizzes
 * @param {Function} updateDashboardCallback - Callback to refresh dashboard
 */
async function deleteQuiz(
    quizPath, startQuizCallback, updateDashboardCallback
) {
    try {
        const resp = await fetch(
            `/api/quiz?path=${encodeURIComponent(quizPath)}`,
            { method: 'DELETE' }
        );
        if (!resp.ok) {
            const data = await resp.json();
            throw new Error(data.error || 'Delete failed');
        }

        showNotification(
            '✅', 'Deleted',
            'Quiz deleted successfully.'
        );

        // Reload quiz list
        await loadQuizzes(
            () => displayQuizMenuItems(
                startQuizCallback, updateDashboardCallback
            ),
            () => displayQuizList(
                startQuizCallback, updateDashboardCallback
            ),
            updateDashboardCallback
        );
    } catch (error) {
        console.error('Error deleting quiz:', error);
        showNotification(
            '❌', 'Error',
            'Failed to delete quiz: ' + error.message
        );
    }
}

/**
 * Load quiz list from API.
 * @param {Function} displayMenuCallback - Callback to display menu
 * @param {Function} displayListCallback - Callback to display list
 * @param {Function} updateDashboardCallback - Callback for dashboard
 */
export async function loadQuizzes(
    displayMenuCallback, displayListCallback, updateDashboardCallback
) {
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
 * Display quiz menu items in sidebar, grouped by source.
 * @param {Function} startQuizCallback - Callback to start a quiz
 * @param {Function} updateDashboardCallback - Callback for dashboard
 */
export function displayQuizMenuItems(
    startQuizCallback, updateDashboardCallback
) {
    const menuContent = document.getElementById('quizMenuContent');
    menuContent.innerHTML = '';

    if (quizzes.length === 0) {
        menuContent.innerHTML =
            '<div style="padding: 10px; color: #B0BEC5;'
            + ' font-size: 0.85em;">No quizzes available</div>';
        return;
    }

    const groups = groupQuizzes(quizzes);

    for (const [groupName, items] of Object.entries(groups)) {
        // Group header
        const groupDiv = document.createElement('div');
        groupDiv.className = 'quiz-group';

        const header = document.createElement('div');
        header.className = 'quiz-group-header';
        header.setAttribute('role', 'button');
        header.setAttribute('tabindex', '0');
        header.innerHTML =
            `<span class="quiz-group-icon">📁</span>`
            + `<span class="quiz-group-name">${groupName}</span>`
            + `<span class="quiz-group-count">`
            + `${items.length}</span>`;

        header.onclick = () => {
            const list = groupDiv.querySelector(
                '.quiz-group-items'
            );
            list.classList.toggle('expanded');
            header.classList.toggle('expanded');
        };
        header.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                header.click();
            }
        });
        groupDiv.appendChild(header);

        // Group items
        const itemList = document.createElement('div');
        itemList.className = 'quiz-group-items';

        for (const info of items) {
            const div = document.createElement('div');
            div.className = 'quiz-menu-item';
            div.setAttribute('role', 'button');
            div.setAttribute('tabindex', '0');

            const nameSpan = document.createElement('span');
            nameSpan.className = 'quiz-menu-item-name';
            nameSpan.textContent =
                `${info.label} (${info.questionCount}q)`;
            div.appendChild(nameSpan);

            // Score badge if attempted
            if (info.bestScore) {
                const badge = document.createElement('span');
                badge.className = 'quiz-menu-badge';
                badge.textContent = info.bestScore;
                div.appendChild(badge);
            }

            div.title = [
                `${groupName} - ${info.label}`,
                `${info.questionCount} questions`,
                info.createdDate
                    ? `Created: ${info.createdDate}` : '',
                info.bestScore
                    ? `Best: ${info.bestScore}` : 'Not attempted',
            ].filter(Boolean).join('\n');

            div.setAttribute('data-quiz-path', info.path);
            div.onclick = () => startQuizCallback(info.path);
            div.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    startQuizCallback(info.path);
                }
            });
            itemList.appendChild(div);
        }

        groupDiv.appendChild(itemList);
        menuContent.appendChild(groupDiv);
    }

    // Auto-expand if only one group
    if (Object.keys(groups).length === 1) {
        const firstItems = menuContent.querySelector(
            '.quiz-group-items'
        );
        const firstHeader = menuContent.querySelector(
            '.quiz-group-header'
        );
        if (firstItems) firstItems.classList.add('expanded');
        if (firstHeader) firstHeader.classList.add('expanded');
    }

    // Re-apply active state if a quiz is currently selected
    if (activeQuizPath) {
        _applyActiveQuizMenuItem(activeQuizPath);
    }
}

/**
 * Apply active CSS class to the quiz menu item matching the given path.
 * @param {string} path - Quiz file path
 */
function _applyActiveQuizMenuItem(path) {
    const menuContent = document.getElementById('quizMenuContent');
    if (!menuContent) return;
    menuContent.querySelectorAll('.quiz-menu-item').forEach(el => {
        el.classList.toggle('active', el.dataset.quizPath === path);
    });
}

/**
 * Mark a quiz menu item as active and store the selection in state.
 * Call this when a quiz is started from the sidebar.
 * @param {string} path - Quiz file path
 */
export function markActiveQuizMenuItem(path) {
    setActiveQuizPath(path);
    _applyActiveQuizMenuItem(path);
}

/**
 * Display quiz list in main quiz selection view with preview
 * cards.
 * @param {Function} startQuizCallback - Callback to start a quiz
 * @param {Function} updateDashboardCallback - Callback for dashboard
 */
export function displayQuizList(
    startQuizCallback, updateDashboardCallback
) {
    const listEl = document.getElementById('quizList');
    listEl.innerHTML = '';

    if (quizzes.length === 0) {
        listEl.innerHTML =
            '<p style="color: #B0BEC5; text-align: center;'
            + ' padding: 20px;">No quizzes available.'
            + ' Import some CSV files first!</p>';
        return;
    }

    const groups = groupQuizzes(quizzes);

    for (const [groupName, items] of Object.entries(groups)) {
        // Group section
        const section = document.createElement('li');
        section.className = 'quiz-list-group';

        const groupTitle = document.createElement('h3');
        groupTitle.className = 'quiz-list-group-title';
        groupTitle.textContent =
            `${groupName} (${items.length} `
            + `quiz${items.length !== 1 ? 'zes' : ''})`;
        section.appendChild(groupTitle);

        const grid = document.createElement('div');
        grid.className = 'quiz-card-grid';

        for (const info of items) {
            const card = document.createElement('div');
            card.className = 'quiz-card';

            card.innerHTML = `
                <div class="quiz-card-header">
                    <h4 class="quiz-card-title">
                        ${groupName} - ${info.label}
                    </h4>
                </div>
                <div class="quiz-card-body">
                    <div class="quiz-card-stat">
                        <span class="quiz-card-stat-label">
                            Questions</span>
                        <span class="quiz-card-stat-value">
                            ${info.questionCount}</span>
                    </div>
                    <div class="quiz-card-stat">
                        <span class="quiz-card-stat-label">
                            Created</span>
                        <span class="quiz-card-stat-value">
                            ${info.createdDate || 'Unknown'}</span>
                    </div>
                    <div class="quiz-card-stat">
                        <span class="quiz-card-stat-label">
                            Best Score</span>
                        <span class="quiz-card-stat-value">
                            ${info.bestScore || '—'}</span>
                    </div>
                    <div class="quiz-card-stat">
                        <span class="quiz-card-stat-label">
                            Last Run</span>
                        <span class="quiz-card-stat-value">
                            ${info.lastRun || 'Never'}</span>
                    </div>
                </div>
                <div class="quiz-card-actions">
                    <button class="quiz-card-btn quiz-card-btn-start"
                        >Start Quiz</button>
                    <button class="quiz-card-btn quiz-card-btn-delete"
                        >Delete</button>
                </div>
            `;

            // Wire up buttons
            const startBtn = card.querySelector(
                '.quiz-card-btn-start'
            );
            startBtn.onclick = (e) => {
                e.stopPropagation();
                startQuizCallback(info.path);
            };

            const deleteBtn = card.querySelector(
                '.quiz-card-btn-delete'
            );
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                showNotification(
                    '⚠️',
                    'Delete Quiz',
                    `Delete "${groupName} - ${info.label}"?`
                    + ' This cannot be undone.',
                    [
                        {
                            text: 'Cancel',
                            primary: false,
                        },
                        {
                            text: 'Delete',
                            primary: true,
                            action: () => deleteQuiz(
                                info.path,
                                startQuizCallback,
                                updateDashboardCallback
                            ),
                        },
                    ]
                );
            };

            grid.appendChild(card);
        }

        section.appendChild(grid);
        listEl.appendChild(section);
    }
}
