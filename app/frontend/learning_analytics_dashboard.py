"""
Learning Analytics Dashboard UI
Task 3.1.4 - Learning Analytics & Progress Tracking Dashboard

FastHTML components for displaying comprehensive learning analytics,
spaced repetition progress, achievements, and gamification elements.
"""

from fasthtml.common import *
from typing import Dict, List, Optional
from datetime import datetime


def learning_analytics_styles():
    """CSS styles for learning analytics dashboard"""
    return Style("""
        /* Learning Analytics Dashboard Styles */
        .analytics-dashboard {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }

        .analytics-container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }

        .analytics-header {
            text-align: center;
            margin-bottom: 3rem;
        }

        .analytics-title {
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }

        .analytics-subtitle {
            color: #666;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }

        /* Stats Cards Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }

        .stat-card {
            background: linear-gradient(135deg, #ffffff, #f8fafc);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(0, 0, 0, 0.05);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }

        .stat-header {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }

        .stat-icon {
            font-size: 2rem;
            margin-right: 0.75rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stat-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stat-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.5rem;
        }

        .stat-subtitle {
            font-size: 0.85rem;
            color: #64748b;
        }

        .stat-trend {
            display: flex;
            align-items: center;
            margin-top: 0.5rem;
            font-size: 0.8rem;
        }

        .trend-positive {
            color: #10b981;
        }

        .trend-negative {
            color: #ef4444;
        }

        /* Progress Tracking */
        .progress-section {
            background: #ffffff;
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(0, 0, 0, 0.05);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
        }

        .section-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
        }

        .section-icon {
            font-size: 1.5rem;
            margin-right: 0.75rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Spaced Repetition Progress */
        .sr-items-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .sr-item-card {
            background: linear-gradient(135deg, #f8fafc, #e2e8f0);
            border-radius: 12px;
            padding: 1rem;
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
        }

        .sr-item-card:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .sr-item-content {
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 0.5rem;
        }

        .sr-item-translation {
            color: #64748b;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }

        .sr-item-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: #94a3b8;
        }

        .mastery-bar {
            width: 60px;
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            overflow: hidden;
        }

        .mastery-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #22c55e);
            transition: width 0.3s ease;
        }

        /* Achievements Section */
        .achievements-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .achievement-card {
            background: linear-gradient(135deg, #fef3c7, #fed7aa);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            border: 2px solid #f59e0b;
            position: relative;
            overflow: hidden;
        }

        .achievement-badge {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }

        .achievement-title {
            font-weight: 700;
            color: #92400e;
            margin-bottom: 0.25rem;
        }

        .achievement-description {
            font-size: 0.85rem;
            color: #b45309;
            margin-bottom: 0.5rem;
        }

        .achievement-points {
            font-size: 0.8rem;
            font-weight: 600;
            color: #d97706;
        }

        /* Learning Streak */
        .streak-card {
            background: linear-gradient(135deg, #fecaca, #fca5a5);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            border: 2px solid #ef4444;
            margin-bottom: 2rem;
        }

        .streak-emoji {
            font-size: 4rem;
            margin-bottom: 1rem;
        }

        .streak-number {
            font-size: 3rem;
            font-weight: 700;
            color: #dc2626;
            margin-bottom: 0.5rem;
        }

        .streak-label {
            font-size: 1.2rem;
            font-weight: 600;
            color: #991b1b;
            margin-bottom: 1rem;
        }

        .streak-subtitle {
            color: #b91c1c;
            font-size: 0.9rem;
        }

        /* Goals Section */
        .goals-list {
            space-y: 1rem;
        }

        .goal-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #e2e8f0;
            margin-bottom: 1rem;
        }

        .goal-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 1rem;
        }

        .goal-title {
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.25rem;
        }

        .goal-description {
            color: #64748b;
            font-size: 0.9rem;
        }

        .goal-progress {
            text-align: right;
        }

        .goal-percentage {
            font-size: 1.5rem;
            font-weight: 700;
            color: #667eea;
        }

        .goal-target {
            font-size: 0.8rem;
            color: #94a3b8;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 1rem;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }

        /* Recommendations */
        .recommendations-list {
            space-y: 0.75rem;
        }

        .recommendation-item {
            background: linear-gradient(135deg, #e0f2fe, #b3e5fc);
            border-radius: 8px;
            padding: 1rem;
            border-left: 4px solid #0284c7;
            margin-bottom: 0.75rem;
        }

        .recommendation-text {
            color: #0f172a;
            font-weight: 500;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .analytics-dashboard {
                padding: 1rem;
            }

            .analytics-container {
                padding: 1rem;
            }

            .analytics-title {
                font-size: 2rem;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }

            .stat-value {
                font-size: 1.8rem;
            }

            .sr-items-grid {
                grid-template-columns: 1fr;
            }

            .achievements-grid {
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            }
        }

        /* Animation Classes */
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .slide-in {
            animation: slideIn 0.6s ease-out;
        }

        @keyframes slideIn {
            from { transform: translateX(-30px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    """)


def analytics_dashboard_page(user_data: Dict = None, analytics_data: Optional[Dict] = None):
    """Main learning analytics dashboard page"""

    # Default data if none provided
    if not user_data:
        user_data = {
            "user_id": 1,
            "username": "demo_user",
            "language_code": "en",
            "language_name": "English",
        }

    if not analytics_data:
        analytics_data = {
            "basic_stats": {
                "total_sessions": 45,
                "total_study_time": 1250,
                "avg_accuracy": 78.5,
                "total_items_studied": 342,
                "total_items_learned": 158,
            },
            "spaced_repetition": {
                "total_items": 158,
                "avg_mastery": 0.67,
                "mastered_items": 89,
                "due_items": 12,
            },
            "streaks": {
                "current_streak": 7,
                "longest_streak": 23,
                "total_active_days": 68,
            },
            "recent_achievements": [
                {
                    "achievement_type": "streak",
                    "title": "Week Warrior",
                    "description": "Studied for 7 consecutive days",
                    "points_awarded": 50,
                    "earned_at": "2025-09-26T15:30:00",
                },
                {
                    "achievement_type": "vocabulary",
                    "title": "Word Master",
                    "description": "Learned 50 new vocabulary words",
                    "points_awarded": 100,
                    "earned_at": "2025-09-25T09:15:00",
                },
            ],
            "active_goals": [
                {
                    "goal_type": "vocabulary",
                    "title": "Learn 100 New Words",
                    "progress_percentage": 73.0,
                    "status": "active",
                },
                {
                    "goal_type": "conversation",
                    "title": "Complete 20 Conversations",
                    "progress_percentage": 45.0,
                    "status": "active",
                },
            ],
            "recommendations": [
                "You have 12 items ready for review!",
                "Study today to maintain your streak!",
                "Great progress! Consider learning new vocabulary.",
            ],
        }

    return Div(
        learning_analytics_styles(),
        # Dashboard Container
        Div(
            # Header Section
            Div(
                H1("Learning Analytics Dashboard", cls="analytics-title fade-in"),
                P(
                    f"Progress tracking for {user_data['username']} in {user_data.get('language_name', 'English')}",
                    cls="analytics-subtitle",
                ),
                P(
                    f"Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                    cls="analytics-subtitle",
                    style="font-size: 0.9rem; color: #94a3b8;",
                ),
                cls="analytics-header",
            ),
            # Main Stats Grid
            create_stats_grid(analytics_data),
            # Learning Streak Section
            create_streak_section(analytics_data.get("streaks", {})),
            # Spaced Repetition Progress
            create_spaced_repetition_section(
                analytics_data.get("spaced_repetition", {})
            ),
            # Active Goals Section
            create_goals_section(analytics_data.get("active_goals", [])),
            # Recent Achievements
            create_achievements_section(analytics_data.get("recent_achievements", [])),
            # Recommendations
            create_recommendations_section(analytics_data.get("recommendations", [])),
            cls="analytics-container",
        ),
        cls="analytics-dashboard",
    )


def create_stats_grid(analytics_data: Dict):
    """Create the main statistics grid"""

    basic_stats = analytics_data.get("basic_stats", {})
    sr_stats = analytics_data.get("spaced_repetition", {})
    streak_stats = analytics_data.get("streaks", {})

    return Div(
        # Total Study Time
        Div(
            Div(
                Span("🕒", cls="stat-icon"),
                Span("Total Study Time", cls="stat-title"),
                cls="stat-header",
            ),
            Div(f"{basic_stats.get('total_study_time', 0):,}", cls="stat-value"),
            Div("minutes", cls="stat-subtitle"),
            Div(Span("▲ +15% this week", cls="trend-positive"), cls="stat-trend"),
            cls="stat-card slide-in",
        ),
        # Learning Sessions
        Div(
            Div(
                Span("📚", cls="stat-icon"),
                Span("Learning Sessions", cls="stat-title"),
                cls="stat-header",
            ),
            Div(f"{basic_stats.get('total_sessions', 0):,}", cls="stat-value"),
            Div("completed", cls="stat-subtitle"),
            Div(Span("▲ +8 this week", cls="trend-positive"), cls="stat-trend"),
            cls="stat-card slide-in",
        ),
        # Average Accuracy
        Div(
            Div(
                Span("🎯", cls="stat-icon"),
                Span("Average Accuracy", cls="stat-title"),
                cls="stat-header",
            ),
            Div(f"{basic_stats.get('avg_accuracy', 0):.1f}%", cls="stat-value"),
            Div("success rate", cls="stat-subtitle"),
            Div(Span("▲ +2.3% improvement", cls="trend-positive"), cls="stat-trend"),
            cls="stat-card slide-in",
        ),
        # Items Learned
        Div(
            Div(
                Span("🧠", cls="stat-icon"),
                Span("Items Learned", cls="stat-title"),
                cls="stat-header",
            ),
            Div(f"{basic_stats.get('total_items_learned', 0):,}", cls="stat-value"),
            Div("vocabulary & phrases", cls="stat-subtitle"),
            Div(Span("▲ +12 this week", cls="trend-positive"), cls="stat-trend"),
            cls="stat-card slide-in",
        ),
        # Mastery Level
        Div(
            Div(
                Span("⭐", cls="stat-icon"),
                Span("Mastery Level", cls="stat-title"),
                cls="stat-header",
            ),
            Div(f"{sr_stats.get('avg_mastery', 0) * 100:.0f}%", cls="stat-value"),
            Div("average proficiency", cls="stat-subtitle"),
            Div(Span("▲ Improving steadily", cls="trend-positive"), cls="stat-trend"),
            cls="stat-card slide-in",
        ),
        # Current Streak
        Div(
            Div(
                Span("🔥", cls="stat-icon"),
                Span("Current Streak", cls="stat-title"),
                cls="stat-header",
            ),
            Div(f"{streak_stats.get('current_streak', 0)}", cls="stat-value"),
            Div("consecutive days", cls="stat-subtitle"),
            Div(
                Span(
                    f"Best: {streak_stats.get('longest_streak', 0)} days",
                    cls="trend-positive",
                ),
                cls="stat-trend",
            ),
            cls="stat-card slide-in",
        ),
        cls="stats-grid",
    )


def create_streak_section(streak_data: Dict):
    """Create the learning streak section"""

    current_streak = streak_data.get("current_streak", 0)
    streak_data.get("longest_streak", 0)

    # Determine streak emoji based on length
    if current_streak == 0:
        streak_emoji = "😴"
        streak_message = "Ready to start a new streak?"
    elif current_streak < 7:
        streak_emoji = "🔥"
        streak_message = "Building momentum!"
    elif current_streak < 30:
        streak_emoji = "🚀"
        streak_message = "Amazing dedication!"
    else:
        streak_emoji = "👑"
        streak_message = "Legendary learning!"

    return Div(
        Span(streak_emoji, cls="streak-emoji"),
        Div(f"{current_streak}", cls="streak-number"),
        Div("Day Learning Streak", cls="streak-label"),
        Div(streak_message, cls="streak-subtitle"),
        cls="streak-card fade-in",
    )


def create_spaced_repetition_section(sr_data: Dict):
    """Create the spaced repetition progress section"""

    total_items = sr_data.get("total_items", 0)
    mastered_items = sr_data.get("mastered_items", 0)
    due_items = sr_data.get("due_items", 0)
    sr_data.get("avg_mastery", 0)

    # Sample items for demonstration
    sample_items = [
        {
            "content": "beautiful",
            "translation": "hermoso/a",
            "mastery_level": 0.85,
            "next_review": "Due now",
        },
        {
            "content": "restaurant",
            "translation": "restaurante",
            "mastery_level": 0.72,
            "next_review": "2 hours",
        },
        {
            "content": "conversation",
            "translation": "conversación",
            "mastery_level": 0.93,
            "next_review": "3 days",
        },
        {
            "content": "learning",
            "translation": "aprendizaje",
            "mastery_level": 0.56,
            "next_review": "Due now",
        },
    ]

    return Div(
        Div(
            Span("🧠", cls="section-icon"),
            "Spaced Repetition Progress",
            cls="section-title",
        ),
        # Summary stats
        Div(
            Div(
                Div("📊", style="font-size: 1.2rem; margin-right: 0.5rem;"),
                f"{total_items} total items | {mastered_items} mastered | {due_items} due for review",
                style="display: flex; align-items: center; color: #64748b; margin-bottom: 1rem;",
            ),
            # Sample items grid
            Div(
                *[create_sr_item_card(item) for item in sample_items[:4]],
                cls="sr-items-grid",
            ),
            # View all button
            Div(
                Button(
                    "View All Items →",
                    onclick="window.location.href='/spaced-repetition'",
                    style="""
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        border: none;
                        padding: 0.75rem 1.5rem;
                        border-radius: 8px;
                        font-weight: 600;
                        cursor: pointer;
                        margin-top: 1rem;
                        transition: all 0.3s ease;
                    """,
                    onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 5px 15px rgba(0,0,0,0.2)'",
                    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'",
                ),
                style="text-align: center; margin-top: 1.5rem;",
            ),
        ),
        cls="progress-section fade-in",
    )


def create_sr_item_card(item: Dict):
    """Create a single spaced repetition item card"""

    mastery_percentage = item["mastery_level"] * 100

    return Div(
        Div(item["content"], cls="sr-item-content"),
        Div(item["translation"], cls="sr-item-translation"),
        Div(
            Div(f"Next: {item['next_review']}", style="font-size: 0.8rem;"),
            Div(
                Div(cls="mastery-fill", style=f"width: {mastery_percentage}%"),
                cls="mastery-bar",
                title=f"Mastery: {mastery_percentage:.0f}%",
            ),
            cls="sr-item-meta",
        ),
        cls="sr-item-card",
    )


def create_achievements_section(achievements: List[Dict]):
    """Create the achievements section"""

    if not achievements:
        achievements = [
            {
                "achievement_type": "streak",
                "title": "Getting Started",
                "description": "Complete your first learning session",
                "points_awarded": 10,
            }
        ]

    return Div(
        Div(Span("🏆", cls="section-icon"), "Recent Achievements", cls="section-title"),
        Div(
            *[create_achievement_card(achievement) for achievement in achievements[:6]],
            cls="achievements-grid",
        ),
        cls="progress-section fade-in",
    )


def create_achievement_card(achievement: Dict):
    """Create a single achievement card"""

    # Map achievement types to emojis
    type_emojis = {
        "streak": "🔥",
        "vocabulary": "📚",
        "conversation": "💬",
        "goal": "🎯",
        "mastery": "⭐",
        "dedication": "👑",
    }

    emoji = type_emojis.get(achievement.get("achievement_type", ""), "🏆")

    return Div(
        Div(emoji, cls="achievement-badge"),
        Div(achievement.get("title", "Achievement"), cls="achievement-title"),
        Div(
            achievement.get("description", "Great work!"), cls="achievement-description"
        ),
        Div(
            f"+{achievement.get('points_awarded', 0)} points", cls="achievement-points"
        ),
        cls="achievement-card",
    )


def create_goals_section(goals: List[Dict]):
    """Create the learning goals section"""

    if not goals:
        goals = [
            {
                "goal_type": "vocabulary",
                "title": "No active goals",
                "progress_percentage": 0,
                "status": "none",
            }
        ]

    return Div(
        Div(Span("🎯", cls="section-icon"), "Learning Goals", cls="section-title"),
        Div(*[create_goal_card(goal) for goal in goals], cls="goals-list"),
        cls="progress-section fade-in",
    )


def create_goal_card(goal: Dict):
    """Create a single goal card"""

    progress = goal.get("progress_percentage", 0)

    return Div(
        Div(
            Div(
                Div(goal.get("title", "Goal"), cls="goal-title"),
                Div(
                    f"{goal.get('goal_type', 'general').title()} Goal",
                    cls="goal-description",
                ),
                cls="goal-info",
            ),
            Div(
                Div(f"{progress:.0f}%", cls="goal-percentage"),
                Div("Complete", cls="goal-target"),
                cls="goal-progress",
            ),
            cls="goal-header",
        ),
        Div(Div(cls="progress-fill", style=f"width: {progress}%"), cls="progress-bar"),
        cls="goal-card",
    )


def create_recommendations_section(recommendations: List[str]):
    """Create the recommendations section"""

    if not recommendations:
        recommendations = ["Keep up the great work!"]

    return Div(
        Div(
            Span("💡", cls="section-icon"),
            "Personalized Recommendations",
            cls="section-title",
        ),
        Div(
            *[
                Div(Div(rec, cls="recommendation-text"), cls="recommendation-item")
                for rec in recommendations
            ],
            cls="recommendations-list",
        ),
        cls="progress-section fade-in",
    )


# Export main function
__all__ = ["analytics_dashboard_page", "learning_analytics_styles"]
