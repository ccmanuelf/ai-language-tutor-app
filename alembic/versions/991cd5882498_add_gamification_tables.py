"""add_gamification_tables

Revision ID: 991cd5882498
Revises: 9e145591946b
Create Date: 2025-12-22 21:52:29.782624

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "991cd5882498"
down_revision: Union[str, Sequence[str], None] = "9e145591946b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add gamification tables for achievements, streaks, XP, and leaderboards."""

    # =====================================================================
    # ACHIEVEMENT SYSTEM TABLES
    # =====================================================================

    # 1. Achievements table - Achievement definitions (master data)
    op.create_table(
        "achievements",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "achievement_id", sa.String(100), unique=True, nullable=False, index=True
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "category", sa.String(50), nullable=False, index=True
        ),  # completion, streak, quality, engagement, learning
        sa.Column(
            "rarity", sa.String(20), nullable=False, index=True
        ),  # common, rare, epic, legendary
        sa.Column("icon_url", sa.String(500), nullable=True),
        sa.Column("xp_reward", sa.Integer(), nullable=False, default=0),
        sa.Column(
            "criteria", sa.JSON(), nullable=False
        ),  # Unlock conditions (flexible JSON)
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("display_order", sa.Integer(), default=0),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # 2. User Achievements table - Track user achievement unlocks
    op.create_table(
        "user_achievements",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "achievement_id",
            sa.Integer(),
            sa.ForeignKey("achievements.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "unlocked_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "progress", sa.Integer(), default=100, nullable=False
        ),  # 0-100, 100 = completed
        sa.Column(
            "unlock_metadata", sa.JSON(), default=dict
        ),  # Additional context (e.g., which scenario completed)
        sa.UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    # =====================================================================
    # STREAK TRACKING TABLES
    # =====================================================================

    # 3. User Streaks table - Daily streak tracking
    op.create_table(
        "user_streaks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
            index=True,
        ),
        sa.Column("current_streak", sa.Integer(), default=0, nullable=False),
        sa.Column("longest_streak", sa.Integer(), default=0, nullable=False),
        sa.Column("last_activity_date", sa.Date(), nullable=True),
        sa.Column("streak_freezes_available", sa.Integer(), default=0, nullable=False),
        sa.Column("total_freezes_earned", sa.Integer(), default=0, nullable=False),
        sa.Column("total_freezes_used", sa.Integer(), default=0, nullable=False),
        sa.Column("last_freeze_earned_at", sa.DateTime(), nullable=True),
        sa.Column("last_freeze_used_at", sa.DateTime(), nullable=True),
        sa.Column(
            "timezone", sa.String(50), default="UTC", nullable=False
        ),  # User's timezone for streak calculation
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # 4. Streak History table - Historical streak data
    op.create_table(
        "streak_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("activity_date", sa.Date(), nullable=False),
        sa.Column("streak_value", sa.Integer(), nullable=False),
        sa.Column("freeze_used", sa.Boolean(), default=False, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("user_id", "activity_date", name="uq_user_activity_date"),
    )

    # =====================================================================
    # XP AND LEVELING TABLES
    # =====================================================================

    # 5. User XP table - Track user experience points and levels
    op.create_table(
        "user_xp",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
            index=True,
        ),
        sa.Column(
            "total_xp", sa.Integer(), default=0, nullable=False, index=True
        ),  # All-time XP
        sa.Column("current_level", sa.Integer(), default=1, nullable=False, index=True),
        sa.Column("xp_to_next_level", sa.Integer(), default=100, nullable=False),
        sa.Column(
            "level_progress_percentage", sa.Float(), default=0.0, nullable=False
        ),  # 0.0 - 100.0
        sa.Column(
            "title", sa.String(50), default="Novice", nullable=False
        ),  # Novice, Learner, Expert, Master, etc.
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # 6. XP Transactions table - Audit log of all XP awards
    op.create_table(
        "xp_transactions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "xp_amount", sa.Integer(), nullable=False
        ),  # Can be positive or negative
        sa.Column(
            "reason", sa.String(100), nullable=False, index=True
        ),  # scenario_completion, achievement_unlock, etc.
        sa.Column(
            "reference_id", sa.String(255), nullable=True
        ),  # scenario_id, achievement_id, etc.
        sa.Column(
            "transaction_metadata", sa.JSON(), default=dict
        ),  # Additional context
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
    )

    # =====================================================================
    # LEADERBOARD TABLES
    # =====================================================================

    # 7. Leaderboard Cache table - Materialized rankings for performance
    op.create_table(
        "leaderboard_cache",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "metric", sa.String(50), nullable=False, index=True
        ),  # xp_all_time, xp_weekly, streak_current, etc.
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("previous_rank", sa.Integer(), nullable=True),
        sa.Column(
            "rank_change", sa.Integer(), default=0
        ),  # Positive = moved up, negative = moved down
        sa.Column("percentile", sa.Float(), nullable=True),  # Top X% of users
        sa.Column(
            "cached_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
        sa.UniqueConstraint("user_id", "metric", name="uq_user_metric"),
    )

    # 8. Leaderboard Snapshots table - Historical leaderboard archives
    op.create_table(
        "leaderboard_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("metric", sa.String(50), nullable=False, index=True),
        sa.Column("period", sa.String(20), nullable=False),  # daily, weekly, monthly
        sa.Column("snapshot_date", sa.Date(), nullable=False, index=True),
        sa.Column("data", sa.JSON(), nullable=False),  # Top 100 users
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("metric", "period", "snapshot_date", name="uq_snapshot"),
    )

    # =====================================================================
    # INDEXES FOR PERFORMANCE
    # =====================================================================

    # Achievement queries
    op.create_index(
        "idx_achievements_category_rarity", "achievements", ["category", "rarity"]
    )
    op.create_index(
        "idx_user_achievements_unlocked",
        "user_achievements",
        ["user_id", "unlocked_at"],
    )

    # Streak queries
    op.create_index(
        "idx_streak_history_user_date", "streak_history", ["user_id", "activity_date"]
    )

    # XP queries
    op.create_index(
        "idx_xp_transactions_user_created", "xp_transactions", ["user_id", "created_at"]
    )
    op.create_index("idx_xp_transactions_reason", "xp_transactions", ["reason"])

    # Leaderboard queries
    op.create_index(
        "idx_leaderboard_metric_rank", "leaderboard_cache", ["metric", "rank"]
    )
    op.create_index(
        "idx_leaderboard_metric_score", "leaderboard_cache", ["metric", "score"]
    )


def downgrade() -> None:
    """Downgrade schema - Remove gamification tables."""

    # Drop in reverse order (children first, then parents)
    op.drop_index("idx_leaderboard_metric_score", "leaderboard_cache")
    op.drop_index("idx_leaderboard_metric_rank", "leaderboard_cache")
    op.drop_index("idx_xp_transactions_reason", "xp_transactions")
    op.drop_index("idx_xp_transactions_user_created", "xp_transactions")
    op.drop_index("idx_streak_history_user_date", "streak_history")
    op.drop_index("idx_user_achievements_unlocked", "user_achievements")
    op.drop_index("idx_achievements_category_rarity", "achievements")

    op.drop_table("leaderboard_snapshots")
    op.drop_table("leaderboard_cache")
    op.drop_table("xp_transactions")
    op.drop_table("user_xp")
    op.drop_table("streak_history")
    op.drop_table("user_streaks")
    op.drop_table("user_achievements")
    op.drop_table("achievements")
