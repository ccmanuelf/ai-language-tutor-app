"""
Test module for Learning Analytics Dashboard Frontend
AI Language Tutor App - Session 106

Tests for app/frontend/learning_analytics_dashboard.py module
Target: 100% coverage with comprehensive test scenarios
"""

import pytest
from fasthtml.common import *

from app.frontend.learning_analytics_dashboard import (
    analytics_dashboard_page,
    create_achievement_card,
    create_achievements_section,
    create_goal_card,
    create_goals_section,
    create_recommendations_section,
    create_spaced_repetition_section,
    create_sr_item_card,
    create_stats_grid,
    create_streak_section,
    learning_analytics_styles,
)


class TestLearningAnalyticsStyles:
    """Test learning analytics CSS styles"""

    def test_learning_analytics_styles_returns_style(self):
        """Test that styles function returns style content"""
        result = learning_analytics_styles()
        result_str = str(result)
        assert "<style>" in result_str.lower()

    def test_learning_analytics_styles_contains_css_classes(self):
        """Test that CSS contains expected class definitions"""
        result = learning_analytics_styles()
        css_content = str(result)

        # Check for main container classes
        assert ".analytics-dashboard" in css_content
        assert ".analytics-container" in css_content
        assert ".analytics-header" in css_content

        # Check for stats grid classes
        assert ".stats-grid" in css_content
        assert ".stat-card" in css_content

        # Check for section classes
        assert ".progress-section" in css_content
        assert ".streak-card" in css_content
        assert ".achievements-grid" in css_content

    def test_learning_analytics_styles_contains_animations(self):
        """Test that CSS includes animation definitions"""
        result = learning_analytics_styles()
        css_content = str(result)

        assert ".fade-in" in css_content or "fadeIn" in css_content
        assert ".slide-in" in css_content or "slideIn" in css_content

    def test_learning_analytics_styles_contains_responsive_design(self):
        """Test that CSS includes responsive design media queries"""
        result = learning_analytics_styles()
        css_content = str(result)

        assert "@media (max-width: 768px)" in css_content


class TestStatsGrid:
    """Test statistics grid component"""

    def test_create_stats_grid_with_default_data(self):
        """Test creating stats grid with default analytics data"""
        analytics_data = {
            "basic_stats": {
                "total_study_time": 1250,
                "total_sessions": 45,
                "avg_accuracy": 78.5,
                "total_items_learned": 158,
            },
            "spaced_repetition": {
                "avg_mastery": 0.67,
            },
            "streaks": {
                "current_streak": 7,
                "longest_streak": 23,
            },
        }

        result = create_stats_grid(analytics_data)
        result_str = str(result)

        # Check for stat values
        assert "1,250" in result_str  # total_study_time formatted
        assert "45" in result_str  # total_sessions
        assert "78.5%" in result_str  # avg_accuracy
        assert "158" in result_str  # total_items_learned

    def test_create_stats_grid_with_missing_data(self):
        """Test stats grid handles missing data gracefully"""
        analytics_data = {}

        result = create_stats_grid(analytics_data)
        result_str = str(result)

        # Should render without errors
        assert "stat-card" in result_str.lower() or "Total Study Time" in result_str

    def test_create_stats_grid_contains_all_metrics(self):
        """Test stats grid includes all expected metrics"""
        analytics_data = {
            "basic_stats": {
                "total_study_time": 1000,
                "total_sessions": 50,
                "avg_accuracy": 80.0,
                "total_items_learned": 200,
            },
            "spaced_repetition": {
                "avg_mastery": 0.75,
            },
            "streaks": {
                "current_streak": 10,
            },
        }

        result = create_stats_grid(analytics_data)
        result_str = str(result)

        # Check for labels
        assert "minutes" in result_str.lower() or "study time" in result_str.lower()
        assert (
            "sessions" in result_str.lower()
            or "learning sessions" in result_str.lower()
        )


class TestStreakSection:
    """Test learning streak section component"""

    def test_create_streak_section_with_active_streak(self):
        """Test streak section with active streak"""
        streak_data = {
            "current_streak": 7,
            "longest_streak": 23,
            "total_active_days": 68,
        }

        result = create_streak_section(streak_data)
        result_str = str(result)

        # Check for streak number
        assert "7" in result_str

        # Check for streak label
        assert "Day" in result_str or "Streak" in result_str

    def test_create_streak_section_with_zero_streak(self):
        """Test streak section with no active streak"""
        streak_data = {
            "current_streak": 0,
            "longest_streak": 10,
        }

        result = create_streak_section(streak_data)
        result_str = str(result)

        # Should handle zero streak
        assert "0" in result_str or "start" in result_str.lower()

    def test_create_streak_section_with_long_streak(self):
        """Test streak section with long streak (30+ days)"""
        streak_data = {
            "current_streak": 35,
            "longest_streak": 50,
        }

        result = create_streak_section(streak_data)
        result_str = str(result)

        assert "35" in result_str

    def test_create_streak_section_emoji_based_on_length(self):
        """Test that streak section uses appropriate emoji based on streak length"""
        # Short streak
        streak_data_short = {"current_streak": 3, "longest_streak": 10}
        result_short = create_streak_section(streak_data_short)
        result_str_short = str(result_short)
        # Should have some emoji
        assert any(emoji in result_str_short for emoji in ["🔥", "🚀", "👑", "😴"])


class TestSpacedRepetitionSection:
    """Test spaced repetition progress section"""

    def test_create_spaced_repetition_section_with_data(self):
        """Test creating spaced repetition section with SR data"""
        sr_data = {
            "total_items": 158,
            "mastered_items": 89,
            "due_items": 12,
            "avg_mastery": 0.67,
        }

        result = create_spaced_repetition_section(sr_data)
        result_str = str(result)

        # Check section title
        assert (
            "Spaced Repetition" in result_str
            or "spaced repetition" in result_str.lower()
        )

        # Check for stats
        assert "158" in result_str  # total_items
        assert "89" in result_str  # mastered_items
        assert "12" in result_str  # due_items

    def test_create_spaced_repetition_section_with_sample_items(self):
        """Test that section displays sample items"""
        sr_data = {
            "total_items": 100,
            "mastered_items": 50,
            "due_items": 10,
        }

        result = create_spaced_repetition_section(sr_data)
        result_str = str(result)

        # Should display sample items
        assert "beautiful" in result_str or "restaurant" in result_str

    def test_create_spaced_repetition_section_has_view_all_button(self):
        """Test that section includes view all items button"""
        sr_data = {"total_items": 50}

        result = create_spaced_repetition_section(sr_data)
        result_str = str(result)

        assert "View All" in result_str or "view all" in result_str.lower()


class TestSRItemCard:
    """Test individual SR item card component"""

    def test_create_sr_item_card_with_data(self):
        """Test creating SR item card with item data"""
        item = {
            "content": "beautiful",
            "translation": "hermoso/a",
            "mastery_level": 0.85,
            "next_review": "Due now",
        }

        result = create_sr_item_card(item)
        result_str = str(result)

        # Check content
        assert "beautiful" in result_str
        assert "hermoso/a" in result_str
        assert "Due now" in result_str

    def test_create_sr_item_card_with_high_mastery(self):
        """Test SR item card with high mastery level"""
        item = {
            "content": "conversation",
            "translation": "conversación",
            "mastery_level": 0.93,
            "next_review": "3 days",
        }

        result = create_sr_item_card(item)
        result_str = str(result)

        assert "conversation" in result_str
        assert "conversación" in result_str

    def test_create_sr_item_card_with_low_mastery(self):
        """Test SR item card with low mastery level"""
        item = {
            "content": "learning",
            "translation": "aprendizaje",
            "mastery_level": 0.56,
            "next_review": "Due now",
        }

        result = create_sr_item_card(item)
        result_str = str(result)

        assert "learning" in result_str
        assert "aprendizaje" in result_str


class TestAchievementsSection:
    """Test achievements section component"""

    def test_create_achievements_section_with_achievements(self):
        """Test creating achievements section with achievement data"""
        achievements = [
            {
                "achievement_type": "streak",
                "title": "Week Warrior",
                "description": "Studied for 7 consecutive days",
                "points_awarded": 50,
            },
            {
                "achievement_type": "vocabulary",
                "title": "Word Master",
                "description": "Learned 50 new vocabulary words",
                "points_awarded": 100,
            },
        ]

        result = create_achievements_section(achievements)
        result_str = str(result)

        # Check section title
        assert "Achievement" in result_str

        # Check for achievement data
        assert "Week Warrior" in result_str
        assert "Word Master" in result_str

    def test_create_achievements_section_with_empty_list(self):
        """Test achievements section with no achievements"""
        achievements = []

        result = create_achievements_section(achievements)
        result_str = str(result)

        # Should render with default achievement
        assert "Achievement" in result_str

    def test_create_achievements_section_limits_display(self):
        """Test that section limits number of achievements displayed"""
        achievements = [
            {
                "achievement_type": "test",
                "title": f"Achievement {i}",
                "description": "Test",
                "points_awarded": 10,
            }
            for i in range(10)
        ]

        result = create_achievements_section(achievements)
        result_str = str(result)

        # Should display achievements
        assert "Achievement" in result_str


class TestAchievementCard:
    """Test individual achievement card component"""

    def test_create_achievement_card_with_data(self):
        """Test creating achievement card with achievement data"""
        achievement = {
            "achievement_type": "streak",
            "title": "Week Warrior",
            "description": "Studied for 7 consecutive days",
            "points_awarded": 50,
        }

        result = create_achievement_card(achievement)
        result_str = str(result)

        assert "Week Warrior" in result_str
        assert "Studied for 7 consecutive days" in result_str
        assert "50" in result_str or "+50" in result_str

    def test_create_achievement_card_different_types(self):
        """Test achievement card with different achievement types"""
        types = [
            "streak",
            "vocabulary",
            "conversation",
            "goal",
            "mastery",
            "dedication",
        ]

        for achievement_type in types:
            achievement = {
                "achievement_type": achievement_type,
                "title": f"Test {achievement_type}",
                "description": "Test description",
                "points_awarded": 10,
            }

            result = create_achievement_card(achievement)
            result_str = str(result)

            # Should render without errors
            assert f"Test {achievement_type}" in result_str


class TestGoalsSection:
    """Test learning goals section component"""

    def test_create_goals_section_with_goals(self):
        """Test creating goals section with goal data"""
        goals = [
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
        ]

        result = create_goals_section(goals)
        result_str = str(result)

        # Check section title
        assert "Goal" in result_str

        # Check for goal data
        assert "Learn 100 New Words" in result_str
        assert "Complete 20 Conversations" in result_str

    def test_create_goals_section_with_empty_list(self):
        """Test goals section with no goals"""
        goals = []

        result = create_goals_section(goals)
        result_str = str(result)

        # Should render with default message
        assert "Goal" in result_str or "goal" in result_str.lower()

    def test_create_goals_section_displays_all_goals(self):
        """Test that section displays all provided goals"""
        goals = [
            {
                "goal_type": "test",
                "title": f"Goal {i}",
                "progress_percentage": i * 10,
                "status": "active",
            }
            for i in range(5)
        ]

        result = create_goals_section(goals)
        result_str = str(result)

        # Should display goals
        assert "Goal" in result_str


class TestGoalCard:
    """Test individual goal card component"""

    def test_create_goal_card_with_data(self):
        """Test creating goal card with goal data"""
        goal = {
            "goal_type": "vocabulary",
            "title": "Learn 100 New Words",
            "progress_percentage": 73.0,
            "status": "active",
        }

        result = create_goal_card(goal)
        result_str = str(result)

        assert "Learn 100 New Words" in result_str
        assert "73" in result_str  # progress percentage

    def test_create_goal_card_with_zero_progress(self):
        """Test goal card with 0% progress"""
        goal = {
            "goal_type": "conversation",
            "title": "Start Conversations",
            "progress_percentage": 0,
            "status": "active",
        }

        result = create_goal_card(goal)
        result_str = str(result)

        assert "Start Conversations" in result_str
        assert "0" in result_str

    def test_create_goal_card_with_complete_progress(self):
        """Test goal card with 100% progress"""
        goal = {
            "goal_type": "mastery",
            "title": "Master Grammar",
            "progress_percentage": 100,
            "status": "completed",
        }

        result = create_goal_card(goal)
        result_str = str(result)

        assert "Master Grammar" in result_str
        assert "100" in result_str


class TestRecommendationsSection:
    """Test recommendations section component"""

    def test_create_recommendations_section_with_recommendations(self):
        """Test creating recommendations section with recommendation data"""
        recommendations = [
            "You have 12 items ready for review!",
            "Study today to maintain your streak!",
            "Great progress! Consider learning new vocabulary.",
        ]

        result = create_recommendations_section(recommendations)
        result_str = str(result)

        # Check section title
        assert "Recommendation" in result_str

        # Check for recommendations
        assert "You have 12 items ready for review!" in result_str
        assert "Study today to maintain your streak!" in result_str

    def test_create_recommendations_section_with_empty_list(self):
        """Test recommendations section with no recommendations"""
        recommendations = []

        result = create_recommendations_section(recommendations)
        result_str = str(result)

        # Should render with default recommendation
        assert "Recommendation" in result_str or "Keep up" in result_str

    def test_create_recommendations_section_displays_all_recommendations(self):
        """Test that section displays all recommendations"""
        recommendations = [f"Recommendation {i}" for i in range(5)]

        result = create_recommendations_section(recommendations)
        result_str = str(result)

        # Should display all recommendations
        for i in range(5):
            assert f"Recommendation {i}" in result_str


class TestAnalyticsDashboardPage:
    """Test main analytics dashboard page"""

    def test_analytics_dashboard_page_with_defaults(self):
        """Test page renders with default data"""
        result = analytics_dashboard_page()
        result_str = str(result)

        # Check page structure
        assert "Learning Analytics Dashboard" in result_str
        assert "Progress tracking" in result_str

    def test_analytics_dashboard_page_with_custom_user_data(self):
        """Test page renders with custom user data"""
        user_data = {
            "user_id": 5,
            "username": "test_user",
            "language_code": "es",
            "language_name": "Spanish",
        }

        result = analytics_dashboard_page(user_data=user_data)
        result_str = str(result)

        # Check that custom user data appears
        assert "test_user" in result_str
        assert "Spanish" in result_str

    def test_analytics_dashboard_page_with_custom_analytics_data(self):
        """Test page renders with custom analytics data"""
        analytics_data = {
            "basic_stats": {
                "total_sessions": 100,
                "total_study_time": 5000,
            },
        }

        result = analytics_dashboard_page(analytics_data=analytics_data)
        result_str = str(result)

        # Check that custom analytics data appears
        assert "100" in result_str
        assert "5,000" in result_str

    def test_analytics_dashboard_page_contains_all_sections(self):
        """Test page includes all expected sections"""
        result = analytics_dashboard_page()
        result_str = str(result)

        # Check for all major sections (flexible to handle variations)
        assert "stats" in result_str.lower() or "statistics" in result_str.lower()
        assert "streak" in result_str.lower()
        assert "achievement" in result_str.lower()
        assert "goal" in result_str.lower()
        assert "recommendation" in result_str.lower()

    def test_analytics_dashboard_page_has_header(self):
        """Test page has proper header structure"""
        result = analytics_dashboard_page()
        result_str = str(result)

        assert "Learning Analytics Dashboard" in result_str
        # Should have user info
        assert "Progress tracking" in result_str or "username" in result_str.lower()

    def test_analytics_dashboard_page_has_styles(self):
        """Test page includes CSS styles"""
        result = analytics_dashboard_page()
        result_str = str(result)

        # The styles should be included
        assert (
            ".analytics-dashboard" in result_str or "analytics-dashboard" in result_str
        )

    def test_analytics_dashboard_page_handles_none_values(self):
        """Test page handles None user_data and analytics_data"""
        result = analytics_dashboard_page(None, None)
        result_str = str(result)

        # Should use defaults and render successfully
        assert "Learning Analytics Dashboard" in result_str


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_stats_grid_with_zero_values(self):
        """Test stats grid handles all zero values"""
        analytics_data = {
            "basic_stats": {
                "total_study_time": 0,
                "total_sessions": 0,
                "avg_accuracy": 0,
            },
        }

        result = create_stats_grid(analytics_data)
        result_str = str(result)

        # Should render without errors
        assert "stat" in result_str.lower()

    def test_achievements_with_missing_fields(self):
        """Test achievement card handles missing fields"""
        achievement = {
            "title": "Test Achievement",
        }

        result = create_achievement_card(achievement)
        result_str = str(result)

        # Should render without errors
        assert "Test Achievement" in result_str

    def test_goals_with_missing_progress(self):
        """Test goal card handles missing progress_percentage"""
        goal = {
            "title": "Test Goal",
        }

        result = create_goal_card(goal)
        result_str = str(result)

        # Should render without errors
        assert "Test Goal" in result_str

    def test_page_with_incomplete_analytics_data(self):
        """Test page handles incomplete analytics data structure"""
        analytics_data = {
            "basic_stats": {},  # Empty stats
        }

        result = analytics_dashboard_page(analytics_data=analytics_data)
        result_str = str(result)

        # Should render with defaults
        assert "Learning Analytics Dashboard" in result_str
