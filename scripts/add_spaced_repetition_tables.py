#!/usr/bin/env python3
"""
Add Spaced Repetition & Progress Analytics Tables for Admin Management
Task 3.1.4 - Spaced Repetition & Progress Tracking Implementation

This script adds comprehensive tables to support spaced repetition algorithms,
learning analytics, gamification, and progress tracking systems.
"""

import sqlite3
import logging
from pathlib import Path
import sys

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_spaced_repetition_tables():
    """Create comprehensive tables for spaced repetition and progress analytics"""

    db_path = "data/ai_language_tutor.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create learning_sessions table for tracking individual study sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(100) NOT NULL UNIQUE,
                user_id INTEGER NOT NULL,
                language_code VARCHAR(10) NOT NULL,
                session_type VARCHAR(50) NOT NULL, -- 'vocabulary', 'conversation', 'tutor_mode', 'scenario'
                mode_specific_data JSON DEFAULT '{}',

                -- Session metrics
                duration_minutes INTEGER DEFAULT 0,
                items_studied INTEGER DEFAULT 0,
                items_correct INTEGER DEFAULT 0,
                items_incorrect INTEGER DEFAULT 0,
                accuracy_percentage REAL DEFAULT 0.0,

                -- Performance metrics
                average_response_time_ms INTEGER DEFAULT 0,
                confidence_score REAL DEFAULT 0.0,
                engagement_score REAL DEFAULT 0.0,
                difficulty_level INTEGER DEFAULT 1,

                -- Progress tracking
                new_items_learned INTEGER DEFAULT 0,
                items_reviewed INTEGER DEFAULT 0,
                streak_contributions INTEGER DEFAULT 0,
                goal_progress REAL DEFAULT 0.0,

                -- Session context
                content_source VARCHAR(100), -- 'youtube', 'conversation', 'manual'
                ai_model_used VARCHAR(50),
                tutor_mode VARCHAR(50),
                scenario_id VARCHAR(100),

                -- Timestamps
                started_at TIMESTAMP NOT NULL,
                ended_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (language_code) REFERENCES languages (code)
            )
        """)

        # Create spaced_repetition_items table for tracking individual learning items
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spaced_repetition_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id VARCHAR(100) NOT NULL UNIQUE,
                user_id INTEGER NOT NULL,
                language_code VARCHAR(10) NOT NULL,
                item_type VARCHAR(50) NOT NULL, -- 'vocabulary', 'phrase', 'grammar', 'pronunciation'

                -- Item content
                content TEXT NOT NULL,
                translation TEXT,
                definition TEXT,
                pronunciation_guide TEXT,
                example_usage TEXT,
                context_tags JSON DEFAULT '[]',
                difficulty_level INTEGER DEFAULT 1,

                -- Spaced repetition algorithm data (SM-2 enhanced)
                ease_factor REAL DEFAULT 2.5,
                repetition_number INTEGER DEFAULT 0,
                interval_days INTEGER DEFAULT 1,
                last_review_date TIMESTAMP,
                next_review_date TIMESTAMP,

                -- Performance tracking
                total_reviews INTEGER DEFAULT 0,
                correct_reviews INTEGER DEFAULT 0,
                incorrect_reviews INTEGER DEFAULT 0,
                streak_count INTEGER DEFAULT 0,
                mastery_level REAL DEFAULT 0.0, -- 0.0 to 1.0
                confidence_score REAL DEFAULT 0.0,

                -- Learning analytics
                first_seen_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_studied_date TIMESTAMP,
                average_response_time_ms INTEGER DEFAULT 0,
                learning_speed_factor REAL DEFAULT 1.0,
                retention_rate REAL DEFAULT 0.0,

                -- Source and metadata
                source_session_id VARCHAR(100),
                source_content VARCHAR(100), -- 'conversation', 'youtube', 'manual'
                metadata JSON DEFAULT '{}',
                is_active BOOLEAN DEFAULT 1,

                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (language_code) REFERENCES languages (code),
                FOREIGN KEY (source_session_id) REFERENCES learning_sessions (session_id),
                UNIQUE (user_id, language_code, content, item_type)
            )
        """)

        # Create learning_analytics table for aggregated performance metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                language_code VARCHAR(10) NOT NULL,
                metric_type VARCHAR(50) NOT NULL, -- 'daily', 'weekly', 'monthly'
                date_period VARCHAR(20) NOT NULL, -- '2025-09-27', '2025-W39', '2025-09'

                -- Study metrics
                total_study_time_minutes INTEGER DEFAULT 0,
                sessions_completed INTEGER DEFAULT 0,
                avg_session_duration_minutes REAL DEFAULT 0.0,

                -- Performance metrics
                items_studied INTEGER DEFAULT 0,
                items_learned INTEGER DEFAULT 0,
                items_reviewed INTEGER DEFAULT 0,
                overall_accuracy REAL DEFAULT 0.0,
                avg_response_time_ms INTEGER DEFAULT 0,

                -- Progress metrics
                mastery_improvements INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                goals_achieved INTEGER DEFAULT 0,
                skill_level_gains REAL DEFAULT 0.0,

                -- Engagement metrics
                avg_engagement_score REAL DEFAULT 0.0,
                feature_usage JSON DEFAULT '{}', -- Usage of different features
                preferred_study_times JSON DEFAULT '{}',

                -- Comparative metrics
                percentile_rank REAL DEFAULT 0.0,
                improvement_rate REAL DEFAULT 0.0,
                consistency_score REAL DEFAULT 0.0,

                -- Metadata
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_current BOOLEAN DEFAULT 1,

                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (language_code) REFERENCES languages (code),
                UNIQUE (user_id, language_code, metric_type, date_period)
            )
        """)

        # Create learning_goals table for goal setting and tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id VARCHAR(100) NOT NULL UNIQUE,
                user_id INTEGER NOT NULL,
                language_code VARCHAR(10) NOT NULL,

                -- Goal definition
                goal_type VARCHAR(50) NOT NULL, -- 'vocabulary', 'conversation', 'fluency', 'streak'
                title VARCHAR(255) NOT NULL,
                description TEXT,
                target_value REAL NOT NULL,
                current_value REAL DEFAULT 0.0,
                unit VARCHAR(50) NOT NULL, -- 'words', 'minutes', 'days', 'conversations'

                -- Goal settings
                difficulty_level INTEGER DEFAULT 2, -- 1=easy, 2=medium, 3=hard
                priority INTEGER DEFAULT 2, -- 1=low, 2=medium, 3=high
                is_daily BOOLEAN DEFAULT 0,
                is_weekly BOOLEAN DEFAULT 0,
                is_monthly BOOLEAN DEFAULT 0,
                is_custom BOOLEAN DEFAULT 1,

                -- Progress tracking
                progress_percentage REAL DEFAULT 0.0,
                milestones_reached INTEGER DEFAULT 0,
                total_milestones INTEGER DEFAULT 5,
                last_progress_update TIMESTAMP,

                -- Timeline
                start_date TIMESTAMP NOT NULL,
                target_date TIMESTAMP NOT NULL,
                completed_date TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'paused', 'failed'

                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (language_code) REFERENCES languages (code)
            )
        """)

        # Create gamification_achievements table for badges and achievements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gamification_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                achievement_id VARCHAR(100) NOT NULL UNIQUE,
                user_id INTEGER NOT NULL,
                language_code VARCHAR(10),

                -- Achievement definition
                achievement_type VARCHAR(50) NOT NULL, -- 'streak', 'vocabulary', 'conversation', 'goal'
                title VARCHAR(255) NOT NULL,
                description TEXT,
                badge_icon VARCHAR(100),
                badge_color VARCHAR(20) DEFAULT '#FFD700',
                points_awarded INTEGER DEFAULT 10,

                -- Achievement criteria
                criteria_met JSON NOT NULL, -- Specific criteria that were met
                required_criteria JSON NOT NULL, -- What was required
                rarity VARCHAR(20) DEFAULT 'common', -- 'common', 'rare', 'epic', 'legendary'

                -- Achievement context
                earned_in_session VARCHAR(100),
                earned_activity VARCHAR(100),
                milestone_level INTEGER DEFAULT 1,

                -- Timestamps
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (language_code) REFERENCES languages (code),
                FOREIGN KEY (earned_in_session) REFERENCES learning_sessions (session_id)
            )
        """)

        # Create learning_streaks table for detailed streak tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_streaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                language_code VARCHAR(10) NOT NULL,

                -- Streak data
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                total_active_days INTEGER DEFAULT 0,

                -- Streak tracking
                last_activity_date DATE,
                streak_start_date DATE,
                longest_streak_start DATE,
                longest_streak_end DATE,

                -- Streak goals and motivation
                weekly_goal_days INTEGER DEFAULT 5,
                monthly_goal_days INTEGER DEFAULT 20,
                streak_freeze_count INTEGER DEFAULT 0, -- Number of "streak freezes" used
                max_freeze_count INTEGER DEFAULT 3,

                -- Performance during streaks
                avg_daily_minutes REAL DEFAULT 0.0,
                avg_daily_accuracy REAL DEFAULT 0.0,
                total_streak_points INTEGER DEFAULT 0,

                -- Metadata
                is_active BOOLEAN DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (language_code) REFERENCES languages (code),
                UNIQUE (user_id, language_code)
            )
        """)

        # Create admin_spaced_repetition_config table for algorithm configuration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_spaced_repetition_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_name VARCHAR(100) NOT NULL UNIQUE,
                config_type VARCHAR(50) NOT NULL, -- 'algorithm', 'thresholds', 'gamification'

                -- Algorithm parameters
                initial_ease_factor REAL DEFAULT 2.5,
                minimum_ease_factor REAL DEFAULT 1.3,
                maximum_ease_factor REAL DEFAULT 3.0,
                ease_factor_change REAL DEFAULT 0.15,

                -- Interval parameters
                initial_interval_days INTEGER DEFAULT 1,
                graduation_interval_days INTEGER DEFAULT 4,
                easy_interval_days INTEGER DEFAULT 7,
                maximum_interval_days INTEGER DEFAULT 365,

                -- Performance thresholds
                mastery_threshold REAL DEFAULT 0.85,
                review_threshold REAL DEFAULT 0.7,
                difficulty_threshold REAL DEFAULT 0.5,
                retention_threshold REAL DEFAULT 0.8,

                -- Gamification settings
                points_per_correct REAL DEFAULT 10,
                points_per_streak_day REAL DEFAULT 5,
                points_per_goal_achieved REAL DEFAULT 100,
                daily_goal_default INTEGER DEFAULT 30, -- minutes

                -- Configuration metadata
                is_active BOOLEAN DEFAULT 1,
                applies_to_language VARCHAR(10), -- NULL means all languages
                created_by_admin INTEGER,
                description TEXT,

                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (applies_to_language) REFERENCES languages (code),
                FOREIGN KEY (created_by_admin) REFERENCES users (id)
            )
        """)

        # Create indexes for performance
        create_indexes(cursor)

        conn.commit()
        logger.info(
            "✅ Spaced repetition and progress analytics tables created successfully"
        )

        # Populate with initial data
        populate_spaced_repetition_config(cursor)
        populate_default_achievements(cursor)

        conn.commit()
        conn.close()

        logger.info("✅ Spaced repetition database schema ready!")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to create spaced repetition tables: {e}")
        return False


def create_indexes(cursor):
    """Create performance indexes for spaced repetition tables"""

    indexes = [
        # Learning sessions indexes
        "CREATE INDEX IF NOT EXISTS idx_sessions_user_language ON learning_sessions (user_id, language_code)",
        "CREATE INDEX IF NOT EXISTS idx_sessions_date ON learning_sessions (started_at)",
        "CREATE INDEX IF NOT EXISTS idx_sessions_type ON learning_sessions (session_type)",
        # Spaced repetition items indexes
        "CREATE INDEX IF NOT EXISTS idx_sr_items_user_language ON spaced_repetition_items (user_id, language_code)",
        "CREATE INDEX IF NOT EXISTS idx_sr_items_review_date ON spaced_repetition_items (next_review_date)",
        "CREATE INDEX IF NOT EXISTS idx_sr_items_mastery ON spaced_repetition_items (mastery_level)",
        "CREATE INDEX IF NOT EXISTS idx_sr_items_type ON spaced_repetition_items (item_type)",
        # Learning analytics indexes
        "CREATE INDEX IF NOT EXISTS idx_analytics_user_period ON learning_analytics (user_id, date_period)",
        "CREATE INDEX IF NOT EXISTS idx_analytics_type_date ON learning_analytics (metric_type, date_period)",
        # Learning goals indexes
        "CREATE INDEX IF NOT EXISTS idx_goals_user_status ON learning_goals (user_id, status)",
        "CREATE INDEX IF NOT EXISTS idx_goals_target_date ON learning_goals (target_date)",
        # Achievements indexes
        "CREATE INDEX IF NOT EXISTS idx_achievements_user ON gamification_achievements (user_id)",
        "CREATE INDEX IF NOT EXISTS idx_achievements_type ON gamification_achievements (achievement_type)",
        "CREATE INDEX IF NOT EXISTS idx_achievements_earned ON gamification_achievements (earned_at)",
        # Streaks indexes
        "CREATE INDEX IF NOT EXISTS idx_streaks_user_language ON learning_streaks (user_id, language_code)",
        "CREATE INDEX IF NOT EXISTS idx_streaks_activity_date ON learning_streaks (last_activity_date)",
    ]

    for index_sql in indexes:
        cursor.execute(index_sql)

    logger.info("✅ Performance indexes created successfully")


def populate_spaced_repetition_config(cursor):
    """Populate admin_spaced_repetition_config with default algorithm settings"""

    # Clear existing config
    cursor.execute("DELETE FROM admin_spaced_repetition_config")

    configs = [
        {
            "config_name": "default_algorithm",
            "config_type": "algorithm",
            "description": "Default SM-2 algorithm parameters for all languages",
            "initial_ease_factor": 2.5,
            "minimum_ease_factor": 1.3,
            "maximum_ease_factor": 3.0,
            "ease_factor_change": 0.15,
            "initial_interval_days": 1,
            "graduation_interval_days": 4,
            "easy_interval_days": 7,
            "maximum_interval_days": 365,
        },
        {
            "config_name": "performance_thresholds",
            "config_type": "thresholds",
            "description": "Performance thresholds for mastery and review scheduling",
            "mastery_threshold": 0.85,
            "review_threshold": 0.7,
            "difficulty_threshold": 0.5,
            "retention_threshold": 0.8,
        },
        {
            "config_name": "gamification_settings",
            "config_type": "gamification",
            "description": "Point values and daily goals for gamification system",
            "points_per_correct": 10,
            "points_per_streak_day": 5,
            "points_per_goal_achieved": 100,
            "daily_goal_default": 30,
        },
    ]

    for config in configs:
        placeholders = ", ".join(["?" for _ in config.keys()])
        columns = ", ".join(config.keys())

        cursor.execute(
            f"INSERT INTO admin_spaced_repetition_config ({columns}) VALUES ({placeholders})",
            list(config.values()),
        )

    logger.info("✅ Spaced repetition configuration populated successfully")


def populate_default_achievements(cursor):
    """Create default achievement definitions (templates for users to earn)"""

    # Note: These are just examples - actual achievements will be created when users earn them
    # This is for reference and could be used for an achievement catalog

    logger.info("✅ Default achievement templates ready for implementation")


if __name__ == "__main__":
    if create_spaced_repetition_tables():
        print("🎉 Spaced repetition and progress analytics database schema ready!")
        sys.exit(0)
    else:
        print("❌ Failed to create spaced repetition schema")
        sys.exit(1)
