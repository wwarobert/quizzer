let quizzes = [];
        let currentQuiz = null;
        let currentQuizPath = null;
        let currentQuestionIndex = 0;
        let correctCount = 0;
        let failures = [];
        let startTime = null;
        let timerInterval = null;
        let quizRuns = JSON.parse(localStorage.getItem('quizRuns') || '[]');
        let sidebarCollapsed = false;

        // Motivational Messages Configuration
        const motivationalMessages = {
            perfect: [
                "🎉 Perfect Score! You're absolutely crushing it!",
                "💯 Flawless! Your expertise is truly impressive!",
                "🌟 Outstanding! A perfect demonstration of mastery!",
                "🏆 Perfect execution! You've reached the pinnacle!"
            ],
            excellent: [ // 90-99%
                "🌟 Excellent work! You're clearly on top of your game!",
                "💪 Nearly perfect! Your dedication shows!",
                "✨ Exceptional performance! Just shy of perfection!",
                "🚀 Impressive! You're reaching for the stars!"
            ],
            good: [ // 80-89%
                "✅ Well done! You've passed with solid knowledge!",
                "👍 Good job! You're demonstrating strong understanding!",
                "💚 Nice work! You've got the fundamentals down!",
                "🎯 Passed! Keep up the good momentum!"
            ],
            close: [ // 70-79%
                "😊 Close! You're almost there! Review and try again!",
                "📚 Not bad! A bit more study and you'll ace it!",
                "💪 Keep pushing! You're on the right track!",
                "🔄 Good effort! One more review should do it!"
            ],
            failed: [ // <70%
                "📖 Don't give up! Learning takes time and practice.",
                "💡 This is a learning opportunity! Review and come back stronger!",
                "🌱 Every expert was once a beginner. Keep studying!",
                "🔍 Take time to review. You'll get there with persistence!",
                "💪 Challenges make you stronger! Don't stop now!"
            ]
        };

        function getMotivationalMessage(scorePercentage) {
            let messages;
            if (scorePercentage === 100) {
                messages = motivationalMessages.perfect;
            } else if (scorePercentage >= 90) {
                messages = motivationalMessages.excellent;
            } else if (scorePercentage >= 80) {
                messages = motivationalMessages.good;
            } else if (scorePercentage >= 70) {
                messages = motivationalMessages.close;
            } else {
                messages = motivationalMessages.failed;
            }
            return messages[Math.floor(Math.random() * messages.length)];
        }

        // Notification System (adds focus trap and Esc-to-close)
        function showNotification(icon, title, message, buttons = [{ text: 'OK', primary: true }]) {
            const overlay = document.getElementById('notificationOverlay');
            const iconEl = document.getElementById('notificationIcon');
            const titleEl = document.getElementById('notificationTitle');
            const messageEl = document.getElementById('notificationMessage');
            const buttonsEl = document.getElementById('notificationButtons');
            const closeBtn = document.getElementById('notificationCloseBtn');

            iconEl.textContent = icon;
            titleEl.textContent = title;
            messageEl.textContent = message;
            buttonsEl.innerHTML = '';

            buttons.forEach(btn => {
                const button = document.createElement('button');
                button.className = `notification-btn ${btn.primary ? 'notification-btn-primary' : 'notification-btn-secondary'}`;
                button.textContent = btn.text;
                button.onclick = () => {
                    overlay.classList.add('hidden');
                    if (btn.onClick) btn.onClick();
                };
                buttonsEl.appendChild(button);
            });

            overlay.classList.remove('hidden');

            // Focus trap and Esc-to-close for dialog
            const focusable = overlay.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            (first || closeBtn)?.focus();

            function onKeyDown(e) {
                if (e.key === 'Escape') {
                    overlay.classList.add('hidden');
                    overlay.removeEventListener('keydown', onKeyDown);
                }
                if (e.key === 'Tab') {
                    if (e.shiftKey && document.activeElement === first) {
                        e.preventDefault();
                        last.focus();
                    } else if (!e.shiftKey && document.activeElement === last) {
                        e.preventDefault();
                        first.focus();
                    }
                }
            }
            overlay.addEventListener('keydown', onKeyDown);
        }

        function showConfirm(icon, title, message, onConfirm, onCancel) {
            showNotification(icon, title, message, [
                { text: 'Cancel', primary: false, onClick: onCancel },
                { text: 'Confirm', primary: true, onClick: onConfirm }
            ]);
        }

        // Sidebar Toggle via Hamburger
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('mainContent');
            const hamburgerCheckbox = document.getElementById('hamburgerCheckbox');
            
            sidebarCollapsed = !sidebarCollapsed;
            
            if (sidebarCollapsed) {
                sidebar.classList.add('collapsed');
                mainContent.classList.add('expanded');
                hamburgerCheckbox.checked = false;
            } else {
                sidebar.classList.remove('collapsed');
                mainContent.classList.remove('expanded');
                hamburgerCheckbox.checked = true;
            }
        }

        // Handle hamburger checkbox change
        function handleHamburgerChange() {
            const checkbox = document.getElementById('hamburgerCheckbox');
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('mainContent');
            
            console.log('Hamburger changed! Checked:', checkbox.checked);
            
            if (checkbox.checked) {
                // Open sidebar
                console.log('Opening sidebar');
                sidebar.classList.remove('collapsed');
                mainContent.classList.remove('expanded');
                sidebarCollapsed = false;
            } else {
                // Close sidebar
                console.log('Closing sidebar');
                sidebar.classList.add('collapsed');
                mainContent.classList.add('expanded');
                sidebarCollapsed = true;
            }
        }

        // Initialize sidebar button on page load
        function initSidebarButton() {
            const hamburgerCheckbox = document.getElementById('hamburgerCheckbox');
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('mainContent');
            const isMobile = window.innerWidth <= 768;
            
            console.log('Initializing hamburger menu. Mobile:', isMobile);
            
            // Add event listener to hamburger checkbox
            hamburgerCheckbox.addEventListener('change', handleHamburgerChange);
            console.log('Event listener attached to hamburger checkbox');
            
            if (isMobile) {
                // On mobile, sidebar starts hidden
                sidebarCollapsed = true;
                sidebar.classList.add('collapsed');
                mainContent.classList.add('expanded');
                hamburgerCheckbox.checked = false; // Shows 3 lines
                console.log('Mobile: Sidebar collapsed, checkbox unchecked');
            } else {
                // On desktop, sidebar starts visible
                sidebarCollapsed = false;
                sidebar.classList.remove('collapsed');
                mainContent.classList.remove('expanded');
                hamburgerCheckbox.checked = true; // Shows X
                console.log('Desktop: Sidebar visible, checkbox checked');
            }
        }

        // Toggle Quiz Menu
        function toggleQuizMenu() {
            const content = document.getElementById('quizMenuContent');
            const chevron = document.getElementById('quizChevron');
            const toggleBtn = document.getElementById('quizMenuToggle');
            
            if (content.classList.contains('expanded')) {
                content.classList.remove('expanded');
                chevron.classList.remove('rotated');
                if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
            } else {
                content.classList.add('expanded');
                chevron.classList.add('rotated');
                if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'true');
                // Load quizzes if not already loaded
                if (quizzes.length === 0) {
                    loadQuizzes();
                }
            }
        }

        // Show View
        function showView(viewName) {
            console.log('Showing view:', viewName);
            
            // Hide all views
            document.querySelectorAll('.view').forEach(view => view.classList.add('hidden'));
            
            // Show selected view
            if (viewName === 'dashboard') {
                document.getElementById('dashboardView').classList.remove('hidden');
                updateDashboard();
            } else if (viewName === 'quizSelection') {
                document.getElementById('quizSelectionView').classList.remove('hidden');
                displayQuizList();
            } else if (viewName === 'quiz') {
                document.getElementById('quizView').classList.remove('hidden');
            }

            // Update active menu item
            document.querySelectorAll('.menu-item').forEach(item => {
                item.classList.remove('active');
                item.removeAttribute('aria-current');
            });
            if (event && event.target) {
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

        // Load quiz list
        async function loadQuizzes() {
            console.log('Loading quizzes...');
            const response = await fetch('/api/quizzes');
            quizzes = await response.json();
            console.log('Loaded quizzes:', quizzes.length);
            
            displayQuizMenuItems();
            displayQuizList();
            updateDashboard();
        }

        function displayQuizMenuItems() {
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
                div.onclick = () => startQuizFromMenu(quiz.path);
                div.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        startQuizFromMenu(quiz.path);
                    }
                });
                menuContent.appendChild(div);
            });
        }

        function displayQuizList() {
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
                li.onclick = () => startQuiz(quiz.path);
                listEl.appendChild(li);
            });
        }

        function startQuizFromMenu(quizPath) {
            console.log('Starting quiz from menu:', quizPath);
            startQuiz(quizPath);
        }

        async function startQuiz(quizPath) {
            console.log('Starting quiz:', quizPath);
            try {
                const response = await fetch(`/api/quiz?path=${encodeURIComponent(quizPath)}`);
                if (!response.ok) {
                    throw new Error('Failed to load quiz');
                }
                currentQuiz = await response.json();
                currentQuizPath = quizPath;
                currentQuestionIndex = 0;
                correctCount = 0;
                failures = [];
                startTime = Date.now();

                // Show quiz view instead of fullpage overlay
                showView('quiz');
                // Move focus to quiz title
                const title = document.getElementById('quizTitle');
                if (title) title.focus();
                const quizName = currentQuiz.quiz_id || 'Quiz';
                document.getElementById('quizBreadcrumb').textContent = quizName;
                startTimer();
                displayQuestion();
            } catch (error) {
                console.error('Error starting quiz:', error);
                showNotification('❌', 'Error', 'Failed to load quiz: ' + error.message);
            }
        }

        function startTimer() {
            timerInterval = setInterval(() => {
                const elapsed = Math.floor((Date.now() - startTime) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                document.getElementById('timer').textContent = `Time: ${minutes}:${seconds.toString().padStart(2, '0')}`;
            }, 1000);
        }

        function stopTimer() {
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
        }

        function displayQuestion() {
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

        async function submitAnswer() {
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
                    correctCount++;
                    feedbackEl.textContent = '✓ Correct!';
                    feedbackEl.classList.add('feedback-correct');
                } else {
                    failures.push({
                        question_id: question.id,
                        question: question.question,
                        user_answer: userAnswer,
                        correct_answer: question.original_answer
                    });
                    feedbackEl.innerHTML = `✗ Incorrect<br>Correct answer: ${question.original_answer}`;
                    feedbackEl.classList.add('feedback-incorrect');
                }

                setTimeout(() => {
                    currentQuestionIndex++;
                    if (currentQuestionIndex < currentQuiz.questions.length) {
                        displayQuestion();
                    } else {
                        showResults();
                    }
                }, 2000);
            } catch (error) {
                console.error('Error submitting answer:', error);
                showNotification('❌', 'Error', 'Failed to submit answer: ' + error.message);
                document.getElementById('submitBtn').disabled = false;
            }
        }

        function showResults() {
            console.log('showResults called');
            stopTimer();
            const totalQuestions = currentQuiz.questions.length;
            const scorePercentage = (correctCount / totalQuestions * 100).toFixed(1);
            const passed = scorePercentage >= 80;
            const timeSpent = Math.floor((Date.now() - startTime) / 1000);

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
            quizRuns.unshift(run);
            if (quizRuns.length > 100) quizRuns = quizRuns.slice(0, 100); // Keep last 100
            localStorage.setItem('quizRuns', JSON.stringify(quizRuns));

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
            
            // No longer generate HTML report automatically - results page IS the report
            console.log('Results displayed - no separate HTML report generated');
        }

        function showScreen(screenId) {
            document.getElementById('selectionScreen').classList.add('hidden');
            document.getElementById('quizScreen').classList.add('hidden');
            document.getElementById('resultsScreen').classList.add('hidden');
            document.getElementById(screenId).classList.remove('hidden');
        }

        function quitQuiz() {
            console.log('quitQuiz called - going directly to results');
            if (!currentQuiz) {
                console.error('No quiz loaded');
                showNotification('⚠️', 'No Active Quiz', 'No quiz is currently active.');
                return;
            }
            
            try {
                // Exit fullscreen mode if active
                document.body.classList.remove('fullscreen-mode');
                showResults();
            } catch (error) {
                console.error('Error showing results:', error);
                showNotification('❌', 'Error', 'Error showing results: ' + error.message);
            }
        }

        function backToSelection() {
            document.getElementById('resultsScreen').classList.add('hidden');
            document.body.classList.remove('fullscreen-mode');
            showView('dashboard');
            updateDashboard();
        }

        async function generateHtmlReport() {
            if (!currentQuiz) return;

            const totalQuestions = currentQuiz.questions.length;
            const scorePercentage = (correctCount / totalQuestions * 100).toFixed(1);
            const passed = scorePercentage >= 80;
            const timeSpent = Math.floor((Date.now() - startTime) / 1000);

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

        function updateDashboard() {
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

        function displayPerformanceTrends() {
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

        function displayQuizBreakdown() {
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

        function displayRecentRuns() {
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

        function displayPassFailAnalysis() {
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

        function displayResultsHistory() {
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

        // Toggle Fullscreen Mode
        function toggleFullscreen() {
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

        // Initialize event listeners when DOM is ready
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
                    submitAnswer();
                });
                console.log('Submit button listener attached');
            }

            if (quitBtn) {
                quitBtn.addEventListener('click', function(e) {
                    console.log('Quit button clicked!');
                    e.preventDefault();
                    e.stopPropagation();
                    quitQuiz();
                });
                console.log('Quit button listener attached');
            } else {
                console.error('Quit button not found!');
            }

            if (backBtn) {
                backBtn.addEventListener('click', function(e) {
                    console.log('Back button clicked');
                    backToSelection();
                });
                console.log('Back button listener attached');
            }

            if (answerInput) {
                answerInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        console.log('Enter key pressed in answer input');
                        submitAnswer();
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
                    e.preventDefault();
                    // Hide results screen before starting quiz
                    document.getElementById('resultsScreen').classList.add('hidden');
                    document.body.classList.remove('fullscreen-mode');
                    // Restart the same quiz
                    if (currentQuizPath) {
                        startQuiz(currentQuizPath);
                    }
                });
                console.log('Retake button listener attached');
            }

            console.log('All event listeners initialized');
        }

        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                console.log('DOMContentLoaded event fired');
                initSidebarButton();
                initEventListeners();
                loadQuizzes();
            });
        } else {
            // DOM is already ready
            console.log('DOM already ready');
            initSidebarButton();
            initEventListeners();
            loadQuizzes();
        }

        // Handle window resize to update sidebar state
        window.addEventListener('resize', function() {
            const isMobile = window.innerWidth <= 768;
            const hamburgerCheckbox = document.getElementById('hamburgerCheckbox');
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('mainContent');
            
            if (isMobile && !sidebarCollapsed) {
                // Switching to mobile view, collapse sidebar
                sidebarCollapsed = true;
                sidebar.classList.add('collapsed');
                mainContent.classList.add('expanded');
                hamburgerCheckbox.checked = false;
            } else if (!isMobile && sidebarCollapsed) {
                // Switching to desktop view, expand sidebar
                sidebarCollapsed = false;
                sidebar.classList.remove('collapsed');
                mainContent.classList.remove('expanded');
                hamburgerCheckbox.checked = true;
            }
        });