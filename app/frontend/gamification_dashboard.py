"""
Frontend Gamification Dashboard
AI Language Tutor App - Session 135

Provides comprehensive gamification features:
- XP and leveling system
- Achievement tracking
- Streak management
- Leaderboards
- User progress visualization
"""

from fasthtml.common import *

from app.core.security import require_auth
from app.models.database import get_db_session
from app.models.gamification_models import LeaderboardMetric
from app.services.achievement_service import AchievementService
from app.services.leaderboard_service import LeaderboardService
from app.services.streak_service import StreakService
from app.services.xp_service import XPService

from .layout import create_layout


def create_gamification_icon(icon_name):
    """Create icons for gamification elements"""
    icons = {
        "trophy": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"></path><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"></path><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"></path></svg>',
        "star": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>',
        "flame": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path></svg>',
        "chart": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>',
        "users": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>',
        "gift": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 12 20 22 4 22 4 12"></polyline><rect x="2" y="7" width="20" height="5"></rect><line x1="12" y1="22" x2="12" y2="7"></line><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"></path><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"></path></svg>',
        "zap": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>',
        "award": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline></svg>',
        "target": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>',
    }
    return NotStr(icons.get(icon_name, icons["star"]))


def create_xp_progress_card(level_info, user_xp):
    """Create XP and level progress card"""
    progress_pct = level_info.get("level_progress_percentage", 0)

    return Div(
        # Header
        Div(
            Div(
                Span(
                    create_gamification_icon("zap"),
                    style="margin-right: 0.5rem; color: var(--warning-color);",
                ),
                H3("Level Progress", style="margin: 0; display: inline;"),
                style="display: flex; align-items: center;",
            ),
            Div(
                Span(
                    f"Level {level_info.get('current_level', 1)}",
                    style="font-size: 1.5rem; font-weight: 700; color: var(--primary-color);",
                ),
                style="text-align: right;",
            ),
            style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;",
        ),
        # Title/Rank
        Div(
            Span(
                level_info.get("title", "Novice"),
                style="font-size: 1.2rem; font-weight: 600; color: var(--text-primary);",
            ),
            style="text-align: center; margin-bottom: 1rem;",
        ),
        # XP Stats
        Div(
            Div(
                Div(
                    "Total XP",
                    style="font-size: 0.875rem; color: var(--text-secondary);",
                ),
                Div(
                    f"{level_info.get('total_xp', 0):,}",
                    style="font-size: 1.5rem; font-weight: 700; color: var(--success-color);",
                ),
                style="text-align: center;",
            ),
            Div(
                Div(
                    "To Next Level",
                    style="font-size: 0.875rem; color: var(--text-secondary);",
                ),
                Div(
                    f"{level_info.get('xp_to_next_level', 0):,} XP",
                    style="font-size: 1.5rem; font-weight: 700; color: var(--info-color);",
                ),
                style="text-align: center;",
            ),
            style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;",
        ),
        # Progress Bar
        Div(
            Div(
                style=f"height: 100%; background: linear-gradient(90deg, var(--success-color), var(--info-color)); border-radius: var(--radius); width: {progress_pct}%; transition: width 0.3s ease;",
            ),
            style="width: 100%; height: 24px; background: var(--bg-tertiary); border-radius: var(--radius); overflow: hidden; margin-bottom: 0.5rem;",
        ),
        Div(
            f"{progress_pct:.1f}% to Level {level_info.get('current_level', 1) + 1}",
            style="text-align: center; font-size: 0.875rem; color: var(--text-secondary);",
        ),
        cls="card",
        style="background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);",
    )


def create_streak_card(streak_status):
    """Create streak tracking card"""
    current_streak = streak_status.get("current_streak", 0)
    longest_streak = streak_status.get("longest_streak", 0)
    streak_freezes = streak_status.get("streak_freezes_available", 0)

    # Determine streak color
    if current_streak >= 30:
        streak_color = "#ff6b35"  # Hot orange
    elif current_streak >= 7:
        streak_color = "#ffa500"  # Orange
    else:
        streak_color = "#ffd700"  # Gold

    return Div(
        # Header
        Div(
            Span(
                create_gamification_icon("flame"),
                style=f"margin-right: 0.5rem; color: {streak_color};",
            ),
            H3("Daily Streak", style="margin: 0; display: inline;"),
            style="display: flex; align-items: center; margin-bottom: 1.5rem;",
        ),
        # Current Streak (Large)
        Div(
            Div(
                Span(
                    f"{current_streak}",
                    style=f"font-size: 4rem; font-weight: 700; color: {streak_color}; line-height: 1;",
                ),
                Span(
                    create_gamification_icon("flame"),
                    style=f"color: {streak_color}; margin-left: 0.5rem;",
                ),
                style="display: flex; align-items: center; justify-content: center;",
            ),
            Div(
                "Day Streak",
                style="text-align: center; color: var(--text-secondary); margin-top: 0.5rem;",
            ),
            style="margin-bottom: 2rem;",
        ),
        # Stats Grid
        Div(
            Div(
                Div(
                    "Longest Streak",
                    style="font-size: 0.875rem; color: var(--text-secondary);",
                ),
                Div(
                    f"{longest_streak} days",
                    style="font-size: 1.25rem; font-weight: 600; color: var(--text-primary);",
                ),
                style="text-align: center; padding: 1rem; background: var(--bg-tertiary); border-radius: var(--radius);",
            ),
            Div(
                Div(
                    "Streak Freezes",
                    style="font-size: 0.875rem; color: var(--text-secondary);",
                ),
                Div(
                    f"{streak_freezes} available",
                    style="font-size: 1.25rem; font-weight: 600; color: var(--info-color);",
                ),
                style="text-align: center; padding: 1rem; background: var(--bg-tertiary); border-radius: var(--radius);",
            ),
            style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;",
        ),
        # Motivation message
        Div(
            Span(
                "Keep it up!" if current_streak > 0 else "Start your streak today!",
                style="font-size: 0.875rem; color: var(--text-secondary); font-style: italic;",
            ),
            style="text-align: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-light);",
        ),
        cls="card",
    )


def create_achievements_grid(user_achievements, all_achievements):
    """Create achievements display grid"""
    # Create set of unlocked achievement IDs
    unlocked_ids = {ua.achievement_id for ua in user_achievements}

    achievement_cards = []
    for achievement in all_achievements[:12]:  # Show first 12
        is_unlocked = achievement.achievement_id in unlocked_ids

        # Find user achievement for unlock date
        user_achievement = next(
            (
                ua
                for ua in user_achievements
                if ua.achievement_id == achievement.achievement_id
            ),
            None,
        )

        card = Div(
            # Icon
            Div(
                Span(
                    create_gamification_icon("award" if is_unlocked else "target"),
                    style=f"color: {'var(--success-color)' if is_unlocked else 'var(--text-secondary)'}; opacity: {'1' if is_unlocked else '0.3'};",
                ),
                style="text-align: center; margin-bottom: 0.75rem;",
            ),
            # Title
            Div(
                achievement.name,
                style=f"font-weight: 600; font-size: 0.875rem; text-align: center; margin-bottom: 0.5rem; color: {'var(--text-primary)' if is_unlocked else 'var(--text-secondary)'};",
            ),
            # Description
            Div(
                achievement.description,
                style="font-size: 0.75rem; color: var(--text-secondary); text-align: center; margin-bottom: 0.5rem;",
            ),
            # XP Reward
            Div(
                f"+{achievement.xp_reward} XP",
                style=f"font-size: 0.75rem; font-weight: 600; text-align: center; color: {'var(--success-color)' if is_unlocked else 'var(--text-secondary)'};",
            ),
            # Unlocked badge
            *(
                [
                    Div(
                        "✓ Unlocked",
                        style="margin-top: 0.5rem; padding: 0.25rem 0.5rem; background: var(--success-color); color: white; font-size: 0.75rem; border-radius: var(--radius); text-align: center;",
                    )
                ]
                if is_unlocked
                else []
            ),
            style=f"padding: 1rem; background: var(--bg-secondary); border-radius: var(--radius); border: 2px solid {'var(--success-color)' if is_unlocked else 'var(--border-light)'}; transition: all 0.2s; opacity: {'1' if is_unlocked else '0.6'};",
        )
        achievement_cards.append(card)

    return Div(
        Div(
            Span(
                create_gamification_icon("trophy"),
                style="margin-right: 0.5rem; color: var(--warning-color);",
            ),
            H3("Achievements", style="margin: 0; display: inline;"),
            Span(
                f"{len(unlocked_ids)}/{len(all_achievements)}",
                style="margin-left: 1rem; color: var(--text-secondary);",
            ),
            style="display: flex; align-items: center; margin-bottom: 1.5rem;",
        ),
        Div(
            *achievement_cards,
            style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem;",
        ),
        cls="card",
    )


def create_leaderboard_card(leaderboard, user_rank, current_user_id):
    """Create leaderboard display"""
    leaderboard_rows = []

    for entry in leaderboard[:10]:  # Top 10
        is_current_user = entry.get("user_id") == current_user_id
        rank = entry.get("rank", 0)

        # Rank medal for top 3
        rank_display = ""
        if rank == 1:
            rank_display = "🥇"
        elif rank == 2:
            rank_display = "🥈"
        elif rank == 3:
            rank_display = "🥉"
        else:
            rank_display = str(rank)

        row = Div(
            # Rank
            Div(
                rank_display,
                style="font-weight: 700; font-size: 1.25rem; text-align: center; min-width: 50px;",
            ),
            # Username
            Div(
                entry.get("username", "Unknown"),
                style=f"flex: 1; font-weight: {'700' if is_current_user else '400'}; color: {'var(--primary-color)' if is_current_user else 'var(--text-primary)'};",
            ),
            # Level
            Div(
                f"Lvl {entry.get('level', 1)}",
                style="color: var(--text-secondary); margin-right: 1rem; font-size: 0.875rem;",
            ),
            # Score
            Div(
                f"{entry.get('score', 0):,} XP",
                style="font-weight: 600; color: var(--success-color); min-width: 100px; text-align: right;",
            ),
            style=f"display: flex; align-items: center; padding: 0.75rem 1rem; background: {'var(--bg-tertiary)' if is_current_user else 'transparent'}; border-radius: var(--radius); margin-bottom: 0.5rem; border-left: {'4px solid var(--primary-color)' if is_current_user else '4px solid transparent'};",
        )
        leaderboard_rows.append(row)

    # User's rank if not in top 10
    user_rank_display = None
    if user_rank and user_rank.get("rank", 0) > 10:
        user_rank_display = Div(
            Div(
                "...",
                style="text-align: center; color: var(--text-secondary); padding: 0.5rem;",
            ),
            Div(
                Div(
                    f"#{user_rank.get('rank', 0)}",
                    style="font-weight: 700; font-size: 1.25rem; text-align: center; min-width: 50px;",
                ),
                Div(
                    "You",
                    style="flex: 1; font-weight: 700; color: var(--primary-color);",
                ),
                Div(
                    f"Lvl {user_rank.get('level', 1)}",
                    style="color: var(--text-secondary); margin-right: 1rem; font-size: 0.875rem;",
                ),
                Div(
                    f"{user_rank.get('score', 0):,} XP",
                    style="font-weight: 600; color: var(--success-color); min-width: 100px; text-align: right;",
                ),
                style="display: flex; align-items: center; padding: 0.75rem 1rem; background: var(--bg-tertiary); border-radius: var(--radius); border-left: 4px solid var(--primary-color);",
            ),
        )

    return Div(
        Div(
            Span(
                create_gamification_icon("users"),
                style="margin-right: 0.5rem; color: var(--info-color);",
            ),
            H3("Global Leaderboard", style="margin: 0; display: inline;"),
            style="display: flex; align-items: center; margin-bottom: 1.5rem;",
        ),
        Div(
            *leaderboard_rows,
            *(user_rank_display,) if user_rank_display else (),
        ),
        cls="card",
    )


def create_gamification_routes(app):
    """Register gamification dashboard routes"""

    @app.route("/gamification")
    async def gamification_dashboard():
        """Main gamification dashboard"""

        # TODO: Add proper authentication when session management is implemented
        # For now, use demo user ID
        class DemoUser:
            id = 1

        current_user = DemoUser()

        # Get database session
        db = next(get_db_session())

        try:
            # Initialize services
            achievement_service = AchievementService(db)
            streak_service = StreakService(db)
            xp_service = XPService(db)
            leaderboard_service = LeaderboardService(db)

            # Fetch all gamification data with fallback to demo data
            level_info = await xp_service.get_user_level(current_user.id)
            if not level_info:
                # Provide demo data for new users
                level_info = {
                    "current_level": 1,
                    "total_xp": 0,
                    "level_xp": 0,
                    "xp_for_next_level": 100,
                    "level_progress_percentage": 0,
                }

            streak_status = await streak_service.get_streak_status(current_user.id)
            if not streak_status:
                streak_status = {
                    "current_streak": 0,
                    "longest_streak": 0,
                    "last_activity": None,
                }

            user_achievements = await achievement_service.get_user_achievements(
                current_user.id
            )
            if not user_achievements:
                user_achievements = []

            all_achievements = await achievement_service.get_all_achievements()
            if not all_achievements:
                all_achievements = []

            leaderboard = await leaderboard_service.get_global_leaderboard(
                metric=LeaderboardMetric.XP_ALL_TIME.value,
                limit=10,
            )
            if not leaderboard:
                leaderboard = []

            user_rank = await leaderboard_service.get_user_rank(
                current_user.id,
                LeaderboardMetric.XP_ALL_TIME.value,
            )
            if not user_rank:
                user_rank = {"rank": None, "total_users": 0}

            # Build dashboard
            content = Div(
                # Page Header
                Div(
                    H1(
                        "Gamification Dashboard",
                        style="margin: 0; color: var(--text-primary);",
                    ),
                    P(
                        "Track your progress, unlock achievements, and compete with others!",
                        style="color: var(--text-secondary); margin-top: 0.5rem;",
                    ),
                    style="margin-bottom: 2rem;",
                ),
                # Top Row: XP and Streak
                Div(
                    Div(
                        create_xp_progress_card(level_info, None),
                        style="grid-column: span 2;",
                    ),
                    create_streak_card(streak_status),
                    style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 1.5rem;",
                ),
                # Middle Row: Achievements
                create_achievements_grid(user_achievements, all_achievements),
                # Bottom Row: Leaderboard
                Div(
                    create_leaderboard_card(leaderboard, user_rank, current_user.id),
                    style="margin-top: 1.5rem;",
                ),
                style="max-width: 1400px; margin: 0 auto; padding: 2rem;",
            )

            return create_layout(content)

        finally:
            db.close()
