"""
Study Session Tracking UI
AI Language Tutor App - Session 129 Frontend

Provides:
- Study session starter and tracker
- Study statistics dashboard
- Mastery level visualization
- Study history display
- Extensible for future study features

User Stories Implemented:
- US-4.1: Start study session
- US-4.2: See progress during session
- US-4.3: Complete session and see mastery update
- US-4.4: See mastery level for content
- US-4.5: See study history
- US-4.6: See overall study statistics

Design: Modular components for easy extension
"""

from fasthtml.common import *


def create_study_routes(app):
    """Create study tracking routes"""

    @app.route("/study-stats")
    def study_stats_dashboard():
        """Study statistics dashboard - US-4.6"""
        return Html(
            Head(
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Title("Study Statistics - AI Language Tutor"),
                Style("""
                    /* Reuse same CSS variables as collections */
                    :root {
                        --primary-color: #6366f1;
                        --success: #22c55e;
                        --warning: #f59e0b;
                        --info: #3b82f6;
                        --text-primary: #0f172a;
                        --text-secondary: #64748b;
                        --text-muted: #94a3b8;
                        --bg-primary: #ffffff;
                        --bg-secondary: #f8fafc;
                        --border-color: #e2e8f0;
                        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                        --radius: 0.5rem;
                        --radius-lg: 1rem;
                    }

                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }

                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, sans-serif;
                        line-height: 1.6;
                        color: var(--text-primary);
                        background: var(--bg-secondary);
                    }

                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 2rem;
                    }

                    .header {
                        margin-bottom: 2rem;
                    }

                    .header h1 {
                        color: var(--primary-color);
                        font-size: 2rem;
                        margin-bottom: 0.5rem;
                    }

                    .stats-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 1.5rem;
                        margin-bottom: 2rem;
                    }

                    .stat-card {
                        background: var(--bg-primary);
                        padding: 1.5rem;
                        border-radius: var(--radius-lg);
                        box-shadow: var(--shadow);
                    }

                    .stat-label {
                        color: var(--text-muted);
                        font-size: 0.875rem;
                        margin-bottom: 0.5rem;
                    }

                    .stat-value {
                        font-size: 2rem;
                        font-weight: 700;
                        color: var(--text-primary);
                    }

                    .stat-icon {
                        font-size: 1.5rem;
                        float: right;
                    }

                    .mastery-breakdown {
                        background: var(--bg-primary);
                        padding: 1.5rem;
                        border-radius: var(--radius-lg);
                        box-shadow: var(--shadow);
                        margin-bottom: 2rem;
                    }

                    .mastery-breakdown h2 {
                        margin-bottom: 1rem;
                    }

                    .mastery-item {
                        display: flex;
                        align-items: center;
                        gap: 1rem;
                        padding: 0.75rem;
                        margin-bottom: 0.5rem;
                        border-radius: var(--radius);
                        background: var(--bg-secondary);
                    }

                    .mastery-badge {
                        display: inline-flex;
                        align-items: center;
                        gap: 0.5rem;
                        padding: 0.375rem 0.75rem;
                        border-radius: var(--radius);
                        font-size: 0.875rem;
                        font-weight: 600;
                    }

                    .mastery-not-started {
                        background: #f1f5f9;
                        color: #64748b;
                    }

                    .mastery-learning {
                        background: #fef3c7;
                        color: #92400e;
                    }

                    .mastery-reviewing {
                        background: #dbeafe;
                        color: #1e40af;
                    }

                    .mastery-mastered {
                        background: #d1fae5;
                        color: #065f46;
                    }

                    .recent-activity {
                        background: var(--bg-primary);
                        padding: 1.5rem;
                        border-radius: var(--radius-lg);
                        box-shadow: var(--shadow);
                    }

                    .recent-activity h2 {
                        margin-bottom: 1rem;
                    }

                    .activity-item {
                        padding: 1rem;
                        border-bottom: 1px solid var(--border-color);
                    }

                    .activity-item:last-child {
                        border-bottom: none;
                    }

                    .activity-title {
                        font-weight: 600;
                        color: var(--text-primary);
                        margin-bottom: 0.25rem;
                    }

                    .activity-meta {
                        color: var(--text-muted);
                        font-size: 0.875rem;
                    }

                    .loading {
                        text-align: center;
                        padding: 2rem;
                        color: var(--text-muted);
                    }

                    @media (max-width: 768px) {
                        .container {
                            padding: 1rem;
                        }

                        .stats-grid {
                            grid-template-columns: 1fr;
                        }
                    }
                """),
            ),
            Body(
                Div(
                    Div(
                        H1("📊 Study Statistics"),
                        P(
                            "Track your learning progress and achievements",
                            style="color: var(--text-muted);",
                        ),
                        cls="header",
                    ),
                    Div(id="loadingState", cls="loading")("Loading your statistics..."),
                    Div(
                        Div(id="statsGrid", cls="stats-grid"),
                        Div(id="masteryBreakdown", cls="mastery-breakdown"),
                        Div(id="recentActivity", cls="recent-activity"),
                        id="statsContent",
                        style="display: none;",
                    ),
                    cls="container",
                ),
                Script("""
                    document.addEventListener('DOMContentLoaded', loadStudyStats);

                    async function loadStudyStats() {
                        try {
                            const response = await fetch('/api/content/study/stats', {
                                credentials: 'include'
                            });

                            if (!response.ok) {
                                throw new Error('Failed to load statistics');
                            }

                            const stats = await response.json();
                            displayStats(stats);

                            // Load recent activity
                            const activityResponse = await fetch('/api/content/study/recent?limit=10', {
                                credentials: 'include'
                            });

                            if (activityResponse.ok) {
                                const activity = await activityResponse.json();
                                displayRecentActivity(activity);
                            }

                        } catch (error) {
                            console.error('Error loading stats:', error);
                            document.getElementById('loadingState').innerHTML =
                                '<div class="error">Failed to load statistics. Please try again.</div>';
                        }
                    }

                    function displayStats(stats) {
                        document.getElementById('loadingState').style.display = 'none';
                        document.getElementById('statsContent').style.display = 'block';

                        const statsGrid = document.getElementById('statsGrid');
                        statsGrid.innerHTML = `
                            <div class="stat-card">
                                <span class="stat-icon">⏱️</span>
                                <div class="stat-label">Total Study Time</div>
                                <div class="stat-value">${formatTime(stats.total_study_time_seconds || 0)}</div>
                            </div>
                            <div class="stat-card">
                                <span class="stat-icon">📚</span>
                                <div class="stat-label">Total Sessions</div>
                                <div class="stat-value">${stats.total_sessions || 0}</div>
                            </div>
                            <div class="stat-card">
                                <span class="stat-icon">🎯</span>
                                <div class="stat-label">Average Accuracy</div>
                                <div class="stat-value">${Math.round((stats.average_correctness || 0) * 100)}%</div>
                            </div>
                            <div class="stat-card">
                                <span class="stat-icon">🏆</span>
                                <div class="stat-label">Content Mastered</div>
                                <div class="stat-value">${stats.mastered_count || 0}</div>
                            </div>
                        `;

                        // Display mastery breakdown
                        const masteryBreakdown = document.getElementById('masteryBreakdown');
                        const breakdown = stats.mastery_breakdown || {
                            not_started: 0,
                            learning: 0,
                            reviewing: 0,
                            mastered: 0
                        };

                        masteryBreakdown.innerHTML = `
                            <h2>Mastery Breakdown</h2>
                            <div class="mastery-item">
                                <span class="mastery-badge mastery-not-started">⚪ Not Started</span>
                                <span>${breakdown.not_started || 0} items</span>
                            </div>
                            <div class="mastery-item">
                                <span class="mastery-badge mastery-learning">🟡 Learning</span>
                                <span>${breakdown.learning || 0} items</span>
                            </div>
                            <div class="mastery-item">
                                <span class="mastery-badge mastery-reviewing">🔵 Reviewing</span>
                                <span>${breakdown.reviewing || 0} items</span>
                            </div>
                            <div class="mastery-item">
                                <span class="mastery-badge mastery-mastered">🟢 Mastered</span>
                                <span>${breakdown.mastered || 0} items</span>
                            </div>
                        `;
                    }

                    function displayRecentActivity(activity) {
                        const recentActivity = document.getElementById('recentActivity');

                        if (!activity || activity.length === 0) {
                            recentActivity.innerHTML = `
                                <h2>Recent Activity</h2>
                                <p style="color: var(--text-muted); text-align: center; padding: 2rem;">
                                    No recent study activity. Start studying to see your progress here!
                                </p>
                            `;
                            return;
                        }

                        const activityHTML = activity.map(item => `
                            <div class="activity-item">
                                <div class="activity-title">${item.content_title || 'Study Session'}</div>
                                <div class="activity-meta">
                                    ${formatTime(item.duration_seconds || 0)} •
                                    ${item.items_correct || 0}/${item.items_total || 0} correct •
                                    ${formatDate(item.started_at)}
                                </div>
                            </div>
                        `).join('');

                        recentActivity.innerHTML = `
                            <h2>Recent Activity</h2>
                            ${activityHTML}
                        `;
                    }

                    function formatTime(seconds) {
                        if (seconds < 60) return `${seconds}s`;
                        const minutes = Math.floor(seconds / 60);
                        if (minutes < 60) return `${minutes}m`;
                        const hours = Math.floor(minutes / 60);
                        const remainingMinutes = minutes % 60;
                        return `${hours}h ${remainingMinutes}m`;
                    }

                    function formatDate(dateString) {
                        const date = new Date(dateString);
                        const now = new Date();
                        const diffMs = now - date;
                        const diffMins = Math.floor(diffMs / 60000);

                        if (diffMins < 60) return `${diffMins} minutes ago`;
                        const diffHours = Math.floor(diffMins / 60);
                        if (diffHours < 24) return `${diffHours} hours ago`;
                        const diffDays = Math.floor(diffHours / 24);
                        if (diffDays < 7) return `${diffDays} days ago`;

                        return date.toLocaleDateString();
                    }
                """),
            ),
        )


def create_mastery_badge_component(level):
    """
    Reusable mastery badge component - US-4.4

    Can be used in multiple places (home.py, content_view.py, etc.)
    Returns HTML for mastery level badge

    Extensible: Add more levels by updating this function
    """
    level_config = {
        "not_started": {
            "label": "Not Started",
            "icon": "⚪",
            "class": "mastery-not-started",
            "color": "#94a3b8",
        },
        "learning": {
            "label": "Learning",
            "icon": "🟡",
            "class": "mastery-learning",
            "color": "#f59e0b",
        },
        "reviewing": {
            "label": "Reviewing",
            "icon": "🔵",
            "class": "mastery-reviewing",
            "color": "#3b82f6",
        },
        "mastered": {
            "label": "Mastered",
            "icon": "🟢",
            "class": "mastery-mastered",
            "color": "#22c55e",
        },
    }

    config = level_config.get(level, level_config["not_started"])

    return Span(
        f"{config['icon']} {config['label']}", cls=f"mastery-badge {config['class']}"
    )


def create_study_session_modal_html():
    """
    Study session modal HTML - US-4.1, US-4.2, US-4.3

    Returns HTML string for study session tracker modal
    Can be embedded in any page that needs study tracking

    Extensible: Add more tracking fields by updating this template
    """
    return """
        <div id="studySessionModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>📖 Study Session</h2>
                    <button class="close-btn" onclick="cancelStudySession()">✕</button>
                </div>
                <div id="studySessionContent">
                    <div class="session-timer">
                        <div class="timer-display" id="timerDisplay">00:00</div>
                        <div class="timer-label">Elapsed Time</div>
                    </div>
                    <div class="session-stats">
                        <div class="stat-item">
                            <label for="itemsStudied">Items Studied</label>
                            <input type="number" id="itemsStudied" value="0" min="0" class="form-input">
                        </div>
                        <div class="stat-item">
                            <label for="itemsCorrect">Items Correct</label>
                            <input type="number" id="itemsCorrect" value="0" min="0" class="form-input">
                        </div>
                    </div>
                    <div class="progress-section">
                        <div class="progress-label">
                            <span>Progress</span>
                            <span id="progressPercent">0%</span>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar" id="progressBar" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="cancelStudySession()">Cancel</button>
                    <button class="btn" onclick="completeStudySession()">Complete Session</button>
                </div>
            </div>
        </div>

        <style>
            .session-timer {
                text-align: center;
                padding: 2rem;
                background: var(--bg-secondary);
                border-radius: var(--radius);
                margin-bottom: 1.5rem;
            }

            .timer-display {
                font-size: 3rem;
                font-weight: 700;
                color: var(--primary-color);
                font-variant-numeric: tabular-nums;
            }

            .timer-label {
                color: var(--text-muted);
                margin-top: 0.5rem;
            }

            .session-stats {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
                margin-bottom: 1.5rem;
            }

            .stat-item label {
                display: block;
                margin-bottom: 0.5rem;
                color: var(--text-primary);
                font-weight: 600;
            }

            .progress-section {
                margin-bottom: 1.5rem;
            }

            .progress-label {
                display: flex;
                justify-content: space-between;
                margin-bottom: 0.5rem;
                color: var(--text-secondary);
                font-size: 0.875rem;
            }

            .progress-bar-container {
                height: 8px;
                background: var(--bg-tertiary);
                border-radius: 4px;
                overflow: hidden;
            }

            .progress-bar {
                height: 100%;
                background: var(--primary-color);
                transition: width 0.3s ease;
            }
        </style>
    """


def create_study_session_js():
    """
    JavaScript for study session functionality - US-4.1, US-4.2, US-4.3

    Returns JavaScript code for study session management

    Extensible: Add more session tracking features here
    """
    return """
        let activeSessionId = null;
        let sessionStartTime = null;
        let timerInterval = null;
        let currentContentId = null;

        function startStudySession(contentId) {
            currentContentId = contentId;

            fetch(`/api/content/${contentId}/study/start`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(response => {
                if (!response.ok) throw new Error('Failed to start session');
                return response.json();
            })
            .then(session => {
                activeSessionId = session.id;
                sessionStartTime = new Date();
                showStudySessionModal();
                startTimer();
            })
            .catch(error => {
                console.error('Error starting session:', error);
                alert('Failed to start study session');
            });
        }

        function showStudySessionModal() {
            document.getElementById('studySessionModal').classList.add('active');
            resetSessionUI();
        }

        function hideStudySessionModal() {
            document.getElementById('studySessionModal').classList.remove('active');
            stopTimer();
        }

        function resetSessionUI() {
            document.getElementById('timerDisplay').textContent = '00:00';
            document.getElementById('itemsStudied').value = '0';
            document.getElementById('itemsCorrect').value = '0';
            document.getElementById('progressBar').style.width = '0%';
            document.getElementById('progressPercent').textContent = '0%';
        }

        function startTimer() {
            timerInterval = setInterval(updateTimer, 1000);
        }

        function stopTimer() {
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
        }

        function updateTimer() {
            if (!sessionStartTime) return;

            const elapsed = Math.floor((new Date() - sessionStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;

            document.getElementById('timerDisplay').textContent =
                `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }

        function updateProgress() {
            const studied = parseInt(document.getElementById('itemsStudied').value) || 0;
            const correct = parseInt(document.getElementById('itemsCorrect').value) || 0;

            if (studied > 0) {
                const percent = Math.round((correct / studied) * 100);
                document.getElementById('progressBar').style.width = percent + '%';
                document.getElementById('progressPercent').textContent = percent + '%';
            }
        }

        // Update progress when stats change
        document.addEventListener('DOMContentLoaded', () => {
            const studiedInput = document.getElementById('itemsStudied');
            const correctInput = document.getElementById('itemsCorrect');

            if (studiedInput) studiedInput.addEventListener('input', updateProgress);
            if (correctInput) correctInput.addEventListener('input', updateProgress);
        });

        function cancelStudySession() {
            if (confirm('Are you sure you want to cancel this session? Progress will not be saved.')) {
                hideStudySessionModal();
                activeSessionId = null;
                sessionStartTime = null;
            }
        }

        function completeStudySession() {
            if (!activeSessionId) {
                alert('No active session');
                return;
            }

            const duration = Math.floor((new Date() - sessionStartTime) / 1000);
            const studied = parseInt(document.getElementById('itemsStudied').value) || 0;
            const correct = parseInt(document.getElementById('itemsCorrect').value) || 0;

            fetch(`/api/content/${currentContentId}/study/${activeSessionId}/complete`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    duration_seconds: duration,
                    items_total: studied,
                    items_correct: correct
                })
            })
            .then(response => {
                if (!response.ok) throw new Error('Failed to complete session');
                return response.json();
            })
            .then(result => {
                alert(`Session completed! Mastery level: ${result.mastery_level}`);
                hideStudySessionModal();
                activeSessionId = null;
                sessionStartTime = null;
                // Reload page to show updated mastery
                window.location.reload();
            })
            .catch(error => {
                console.error('Error completing session:', error);
                alert('Failed to complete session');
            });
        }
    """
