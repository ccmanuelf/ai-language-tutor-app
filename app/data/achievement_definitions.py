"""
Achievement Definitions for AI Language Tutor App

This module contains all achievement definitions with criteria for unlocking.
Achievements are organized by category: completion, streak, quality, engagement, and learning.
"""

from app.models.gamification_models import AchievementCategory, AchievementRarity

# =====================================================================
# COMPLETION ACHIEVEMENTS
# =====================================================================

COMPLETION_ACHIEVEMENTS = [
    {
        "achievement_id": "first_steps",
        "name": "First Steps",
        "description": "Complete your first scenario",
        "category": AchievementCategory.COMPLETION.value,
        "rarity": AchievementRarity.COMMON.value,
        "icon_url": "🎯",
        "xp_reward": 50,
        "criteria": {"type": "scenario_completions", "count": 1},
        "display_order": 1,
    },
    {
        "achievement_id": "getting_started",
        "name": "Getting Started",
        "description": "Complete 5 scenarios",
        "category": AchievementCategory.COMPLETION.value,
        "rarity": AchievementRarity.COMMON.value,
        "icon_url": "🌱",
        "xp_reward": 100,
        "criteria": {"type": "scenario_completions", "count": 5},
        "display_order": 2,
    },
    {
        "achievement_id": "dedicated_learner",
        "name": "Dedicated Learner",
        "description": "Complete 10 scenarios",
        "category": AchievementCategory.COMPLETION.value,
        "rarity": AchievementRarity.RARE.value,
        "icon_url": "📚",
        "xp_reward": 200,
        "criteria": {"type": "scenario_completions", "count": 10},
        "display_order": 3,
    },
    {
        "achievement_id": "scenario_master",
        "name": "Scenario Master",
        "description": "Complete 25 scenarios",
        "category": AchievementCategory.COMPLETION.value,
        "rarity": AchievementRarity.RARE.value,
        "icon_url": "🏆",
        "xp_reward": 500,
        "criteria": {"type": "scenario_completions", "count": 25},
        "display_order": 4,
    },
    {
        "achievement_id": "century_club",
        "name": "Century Club",
        "description": "Complete 100 scenarios",
        "category": AchievementCategory.COMPLETION.value,
        "rarity": AchievementRarity.EPIC.value,
        "icon_url": "💯",
        "xp_reward": 2000,
        "criteria": {"type": "scenario_completions", "count": 100},
        "display_order": 5,
    },
    {
        "achievement_id": "category_champion_restaurant",
        "name": "Restaurant Champion",
        "description": "Complete all restaurant scenarios",
        "category": AchievementCategory.COMPLETION.value,
        "rarity": AchievementRarity.RARE.value,
        "icon_url": "🍽️",
        "xp_reward": 300,
        "criteria": {
            "type": "category_completions",
            "category": "restaurant",
            "percentage": 100,
        },
        "display_order": 10,
    },
    {
        "achievement_id": "category_champion_travel",
        "name": "Travel Champion",
        "description": "Complete all travel scenarios",
        "category": AchievementCategory.COMPLETION.value,
        "rarity": AchievementRarity.RARE.value,
        "icon_url": "✈️",
        "xp_reward": 300,
        "criteria": {
            "type": "category_completions",
            "category": "travel",
            "percentage": 100,
        },
        "display_order": 11,
    },
]

# =====================================================================
# STREAK ACHIEVEMENTS
# =====================================================================

STREAK_ACHIEVEMENTS = [
    {
        "achievement_id": "streak_starter",
        "name": "Streak Starter",
        "description": "Maintain a 3-day streak",
        "category": AchievementCategory.STREAK.value,
        "rarity": AchievementRarity.COMMON.value,
        "icon_url": "🔥",
        "xp_reward": 75,
        "criteria": {"type": "current_streak", "days": 3},
        "display_order": 20,
    },
    {
        "achievement_id": "week_warrior",
        "name": "Week Warrior",
        "description": "Maintain a 7-day streak",
        "category": AchievementCategory.STREAK.value,
        "rarity": AchievementRarity.RARE.value,
        "icon_url": "🔥🔥",
        "xp_reward": 200,
        "criteria": {"type": "current_streak", "days": 7},
        "display_order": 21,
    },
    {
        "achievement_id": "month_master",
        "name": "Month Master",
        "description": "Maintain a 30-day streak",
        "category": AchievementCategory.STREAK.value,
        "rarity": AchievementRarity.EPIC.value,
        "icon_url": "🔥🔥🔥",
        "xp_reward": 1000,
        "criteria": {"type": "current_streak", "days": 30},
        "display_order": 22,
    },
    {
        "achievement_id": "unstoppable",
        "name": "Unstoppable",
        "description": "Maintain a 100-day streak",
        "category": AchievementCategory.STREAK.value,
        "rarity": AchievementRarity.LEGENDARY.value,
        "icon_url": "⚡",
        "xp_reward": 5000,
        "criteria": {"type": "current_streak", "days": 100},
        "display_order": 23,
    },
    {
        "achievement_id": "comeback_kid",
        "name": "Comeback Kid",
        "description": "Use a streak freeze to save your streak",
        "category": AchievementCategory.STREAK.value,
        "rarity": AchievementRarity.RARE.value,
        "icon_url": "❄️",
        "xp_reward": 150,
        "criteria": {"type": "streak_freeze_used", "count": 1},
        "display_order": 24,
    },
]

# =====================================================================
# QUALITY ACHIEVEMENTS
# =====================================================================

QUALITY_ACHIEVEMENTS = [
    {
        "achievement_id": "perfectionist",
        "name": "Perfectionist",
        "description": "Complete a scenario with a perfect 5-star rating",
        "category": AchievementCategory.QUALITY.value,
        "rarity": AchievementRarity.RARE.value,
        "icon_url": "⭐",
        "xp_reward": 200,
        "criteria": {"type": "perfect_rating", "count": 1},
        "display_order": 30,
    },
    {
        "achievement_id": "excellence_streak",
        "name": "Excellence Streak",
        "description": "Complete 5 scenarios in a row with 5-star ratings",
        "category": AchievementCategory.QUALITY.value,
        "rarity": AchievementRarity.EPIC.value,
        "icon_url": "⭐⭐",
        "xp_reward": 750,
        "criteria": {"type": "perfect_rating_streak", "count": 5},
        "display_order": 31,
    },
    {
        "achievement_id": "cultural_expert",
        "name": "Cultural Expert",
        "description": "Achieve 90%+ cultural accuracy on 10 scenarios",
        "category": AchievementCategory.QUALITY.value,
        "rarity": AchievementRarity.RARE.value,
        "icon_url": "🌍",
        "xp_reward": 400,
        "criteria": {"type": "high_cultural_accuracy", "threshold": 90, "count": 10},
        "display_order": 32,
    },
    {
        "achievement_id": "speed_demon",
        "name": "Speed Demon",
        "description": "Complete a scenario 50% faster than estimated time",
        "category": AchievementCategory.QUALITY.value,
        "rarity": AchievementRarity.RARE.value,
        "icon_url": "⚡",
        "xp_reward": 250,
        "criteria": {"type": "fast_completion", "speed_multiplier": 0.5},
        "display_order": 33,
    },
]

# =====================================================================
# ENGAGEMENT ACHIEVEMENTS
# =====================================================================

ENGAGEMENT_ACHIEVEMENTS = [
    {
        "achievement_id": "helpful_reviewer",
        "name": "Helpful Reviewer",
        "description": "Rate 10 scenarios",
        "category": AchievementCategory.ENGAGEMENT.value,
        "rarity": AchievementRarity.COMMON.value,
        "icon_url": "📝",
        "xp_reward": 100,
        "criteria": {"type": "ratings_given", "count": 10},
        "display_order": 40,
    },
    {
        "achievement_id": "super_reviewer",
        "name": "Super Reviewer",
        "description": "Rate 50 scenarios",
        "category": AchievementCategory.ENGAGEMENT.value,
        "rarity": AchievementRarity.RARE.value,
        "icon_url": "📝📝",
        "xp_reward": 500,
        "criteria": {"type": "ratings_given", "count": 50},
        "display_order": 41,
    },
    {
        "achievement_id": "curator",
        "name": "Curator",
        "description": "Create 5 scenario collections",
        "category": AchievementCategory.ENGAGEMENT.value,
        "rarity": AchievementRarity.RARE.value,
        "icon_url": "📂",
        "xp_reward": 300,
        "criteria": {"type": "collections_created", "count": 5},
        "display_order": 42,
    },
    {
        "achievement_id": "bookworm",
        "name": "Bookworm",
        "description": "Bookmark 20 scenarios",
        "category": AchievementCategory.ENGAGEMENT.value,
        "rarity": AchievementRarity.COMMON.value,
        "icon_url": "🔖",
        "xp_reward": 150,
        "criteria": {"type": "bookmarks_created", "count": 20},
        "display_order": 43,
    },
    {
        "achievement_id": "social_butterfly",
        "name": "Social Butterfly",
        "description": "Share 10 scenarios with others",
        "category": AchievementCategory.ENGAGEMENT.value,
        "rarity": AchievementRarity.RARE.value,
        "icon_url": "🦋",
        "xp_reward": 250,
        "criteria": {"type": "scenarios_shared", "count": 10},
        "display_order": 44,
    },
]

# =====================================================================
# LEARNING ACHIEVEMENTS
# =====================================================================

LEARNING_ACHIEVEMENTS = [
    {
        "achievement_id": "vocabulary_builder",
        "name": "Vocabulary Builder",
        "description": "Learn 100 new words",
        "category": AchievementCategory.LEARNING.value,
        "rarity": AchievementRarity.COMMON.value,
        "icon_url": "📖",
        "xp_reward": 200,
        "criteria": {"type": "words_learned", "count": 100},
        "display_order": 50,
    },
    {
        "achievement_id": "word_wizard",
        "name": "Word Wizard",
        "description": "Learn 500 new words",
        "category": AchievementCategory.LEARNING.value,
        "rarity": AchievementRarity.EPIC.value,
        "icon_url": "🧙",
        "xp_reward": 1000,
        "criteria": {"type": "words_learned", "count": 500},
        "display_order": 51,
    },
    {
        "achievement_id": "beginner_graduate",
        "name": "Beginner Graduate",
        "description": "Complete all beginner-level scenarios",
        "category": AchievementCategory.LEARNING.value,
        "rarity": AchievementRarity.RARE.value,
        "icon_url": "🎓",
        "xp_reward": 400,
        "criteria": {
            "type": "difficulty_completions",
            "difficulty": "beginner",
            "percentage": 100,
        },
        "display_order": 52,
    },
    {
        "achievement_id": "intermediate_achiever",
        "name": "Intermediate Achiever",
        "description": "Complete all intermediate-level scenarios",
        "category": AchievementCategory.LEARNING.value,
        "rarity": AchievementRarity.EPIC.value,
        "icon_url": "🎓🎓",
        "xp_reward": 800,
        "criteria": {
            "type": "difficulty_completions",
            "difficulty": "intermediate",
            "percentage": 100,
        },
        "display_order": 53,
    },
    {
        "achievement_id": "advanced_master",
        "name": "Advanced Master",
        "description": "Complete all advanced-level scenarios",
        "category": AchievementCategory.LEARNING.value,
        "rarity": AchievementRarity.LEGENDARY.value,
        "icon_url": "🏅",
        "xp_reward": 2000,
        "criteria": {
            "type": "difficulty_completions",
            "difficulty": "advanced",
            "percentage": 100,
        },
        "display_order": 54,
    },
    {
        "achievement_id": "polyglot",
        "name": "Polyglot",
        "description": "Practice scenarios in 3 different languages",
        "category": AchievementCategory.LEARNING.value,
        "rarity": AchievementRarity.EPIC.value,
        "icon_url": "🌐",
        "xp_reward": 1500,
        "criteria": {"type": "languages_practiced", "count": 3},
        "display_order": 55,
    },
]

# =====================================================================
# ALL ACHIEVEMENTS COMBINED
# =====================================================================

ALL_ACHIEVEMENTS = (
    COMPLETION_ACHIEVEMENTS
    + STREAK_ACHIEVEMENTS
    + QUALITY_ACHIEVEMENTS
    + ENGAGEMENT_ACHIEVEMENTS
    + LEARNING_ACHIEVEMENTS
)


def get_all_achievements():
    """Get all achievement definitions"""
    return ALL_ACHIEVEMENTS


def get_achievements_by_category(category: str):
    """Get achievements filtered by category"""
    return [ach for ach in ALL_ACHIEVEMENTS if ach["category"] == category]


def get_achievements_by_rarity(rarity: str):
    """Get achievements filtered by rarity"""
    return [ach for ach in ALL_ACHIEVEMENTS if ach["rarity"] == rarity]


def get_achievement_by_id(achievement_id: str):
    """Get a specific achievement by ID"""
    for ach in ALL_ACHIEVEMENTS:
        if ach["achievement_id"] == achievement_id:
            return ach
    return None


# Achievement count by category (for documentation)
ACHIEVEMENT_STATS = {
    "total": len(ALL_ACHIEVEMENTS),
    "by_category": {
        "completion": len(COMPLETION_ACHIEVEMENTS),
        "streak": len(STREAK_ACHIEVEMENTS),
        "quality": len(QUALITY_ACHIEVEMENTS),
        "engagement": len(ENGAGEMENT_ACHIEVEMENTS),
        "learning": len(LEARNING_ACHIEVEMENTS),
    },
    "by_rarity": {
        "common": len([a for a in ALL_ACHIEVEMENTS if a["rarity"] == "common"]),
        "rare": len([a for a in ALL_ACHIEVEMENTS if a["rarity"] == "rare"]),
        "epic": len([a for a in ALL_ACHIEVEMENTS if a["rarity"] == "epic"]),
        "legendary": len([a for a in ALL_ACHIEVEMENTS if a["rarity"] == "legendary"]),
    },
}
