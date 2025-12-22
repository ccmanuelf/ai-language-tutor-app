"""add_scenario_organization_tables

Revision ID: 9e145591946b
Revises: fa4e9d2b3c81
Create Date: 2025-12-22 11:31:32.252538

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9e145591946b"
down_revision: Union[str, Sequence[str], None] = "fa4e9d2b3c81"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add scenario organization tables."""

    # ====================================================================
    # TABLE 1: scenario_collections - Playlists and learning paths
    # ====================================================================
    op.create_table(
        "scenario_collections",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("collection_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("is_learning_path", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("difficulty_level", sa.String(length=20), nullable=True),
        sa.Column("estimated_total_duration", sa.Integer(), nullable=True),  # minutes
        sa.Column("item_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("subscriber_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("collection_id"),
    )

    # Indexes for scenario_collections
    op.create_index("idx_collection_user", "scenario_collections", ["created_by"])
    op.create_index("idx_collection_public", "scenario_collections", ["is_public"])
    op.create_index("idx_collection_category", "scenario_collections", ["category"])

    # ====================================================================
    # TABLE 2: scenario_collection_items - Items in collections
    # ====================================================================
    op.create_table(
        "scenario_collection_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("scenario_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),  # Order in collection
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "added_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["collection_id"], ["scenario_collections.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "collection_id", "scenario_id", name="uq_collection_scenario"
        ),
    )

    # Indexes for scenario_collection_items
    op.create_index(
        "idx_collection_item_collection", "scenario_collection_items", ["collection_id"]
    )
    op.create_index(
        "idx_collection_item_scenario", "scenario_collection_items", ["scenario_id"]
    )

    # ====================================================================
    # TABLE 3: scenario_tags - User and AI-generated tags
    # ====================================================================
    op.create_table(
        "scenario_tags",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scenario_id", sa.Integer(), nullable=False),
        sa.Column("tag", sa.String(length=50), nullable=False),
        sa.Column("tag_type", sa.String(length=20), nullable=False),  # 'user' or 'ai'
        sa.Column("created_by", sa.Integer(), nullable=True),  # NULL for AI tags
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scenario_id", "tag", "tag_type", name="uq_scenario_tag"),
    )

    # Indexes for scenario_tags
    op.create_index("idx_tag_scenario", "scenario_tags", ["scenario_id"])
    op.create_index("idx_tag_value", "scenario_tags", ["tag"])
    op.create_index("idx_tag_type", "scenario_tags", ["tag_type"])

    # ====================================================================
    # TABLE 4: scenario_bookmarks - User favorites with folders
    # ====================================================================
    op.create_table(
        "scenario_bookmarks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("scenario_id", sa.Integer(), nullable=False),
        sa.Column("folder", sa.String(length=100), nullable=True),  # Optional folder
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "scenario_id", name="uq_user_bookmark"),
    )

    # Indexes for scenario_bookmarks
    op.create_index("idx_bookmark_user", "scenario_bookmarks", ["user_id"])
    op.create_index("idx_bookmark_scenario", "scenario_bookmarks", ["scenario_id"])
    op.create_index("idx_bookmark_folder", "scenario_bookmarks", ["folder"])

    # ====================================================================
    # TABLE 5: scenario_ratings - 5-star ratings and reviews
    # ====================================================================
    op.create_table(
        "scenario_ratings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scenario_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),  # 1-5 stars
        sa.Column("review", sa.Text(), nullable=True),
        sa.Column("difficulty_rating", sa.Integer(), nullable=True),  # 1-5
        sa.Column("usefulness_rating", sa.Integer(), nullable=True),  # 1-5
        sa.Column("cultural_accuracy_rating", sa.Integer(), nullable=True),  # 1-5
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("helpful_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scenario_id", "user_id", name="uq_scenario_user_rating"),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    # Indexes for scenario_ratings
    op.create_index("idx_rating_scenario", "scenario_ratings", ["scenario_id"])
    op.create_index("idx_rating_user", "scenario_ratings", ["user_id"])
    op.create_index("idx_rating_value", "scenario_ratings", ["rating"])

    # ====================================================================
    # TABLE 6: scenario_analytics - Aggregated metrics for discovery
    # ====================================================================
    op.create_table(
        "scenario_analytics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scenario_id", sa.Integer(), nullable=False),
        # Usage metrics
        sa.Column(
            "total_completions", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("total_starts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unique_users", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_rate", sa.Float(), nullable=True),  # Percentage
        # Rating metrics
        sa.Column("average_rating", sa.Float(), nullable=True),
        sa.Column("rating_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "rating_distribution", sa.JSON(), nullable=True
        ),  # {1: count, 2: count, ...}
        # Engagement metrics
        sa.Column("bookmark_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("collection_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tag_count", sa.Integer(), nullable=False, server_default="0"),
        # Trending score (computed)
        sa.Column("trending_score", sa.Float(), nullable=True),
        sa.Column("popularity_score", sa.Float(), nullable=True),
        # Time windows
        sa.Column(
            "last_7_days_completions", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "last_30_days_completions", sa.Integer(), nullable=False, server_default="0"
        ),
        # Metadata
        sa.Column(
            "last_updated",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scenario_id"),
    )

    # Indexes for scenario_analytics
    op.create_index("idx_analytics_trending", "scenario_analytics", ["trending_score"])
    op.create_index(
        "idx_analytics_popularity", "scenario_analytics", ["popularity_score"]
    )
    op.create_index("idx_analytics_rating", "scenario_analytics", ["average_rating"])
    op.create_index(
        "idx_analytics_completions", "scenario_analytics", ["total_completions"]
    )


def downgrade() -> None:
    """Downgrade schema - Remove scenario organization tables."""

    # Drop tables in reverse order (respecting foreign key dependencies)

    # Drop scenario_analytics
    op.drop_index("idx_analytics_completions", table_name="scenario_analytics")
    op.drop_index("idx_analytics_rating", table_name="scenario_analytics")
    op.drop_index("idx_analytics_popularity", table_name="scenario_analytics")
    op.drop_index("idx_analytics_trending", table_name="scenario_analytics")
    op.drop_table("scenario_analytics")

    # Drop scenario_ratings
    op.drop_index("idx_rating_value", table_name="scenario_ratings")
    op.drop_index("idx_rating_user", table_name="scenario_ratings")
    op.drop_index("idx_rating_scenario", table_name="scenario_ratings")
    op.drop_table("scenario_ratings")

    # Drop scenario_bookmarks
    op.drop_index("idx_bookmark_folder", table_name="scenario_bookmarks")
    op.drop_index("idx_bookmark_scenario", table_name="scenario_bookmarks")
    op.drop_index("idx_bookmark_user", table_name="scenario_bookmarks")
    op.drop_table("scenario_bookmarks")

    # Drop scenario_tags
    op.drop_index("idx_tag_type", table_name="scenario_tags")
    op.drop_index("idx_tag_value", table_name="scenario_tags")
    op.drop_index("idx_tag_scenario", table_name="scenario_tags")
    op.drop_table("scenario_tags")

    # Drop scenario_collection_items
    op.drop_index(
        "idx_collection_item_scenario", table_name="scenario_collection_items"
    )
    op.drop_index(
        "idx_collection_item_collection", table_name="scenario_collection_items"
    )
    op.drop_table("scenario_collection_items")

    # Drop scenario_collections
    op.drop_index("idx_collection_category", table_name="scenario_collections")
    op.drop_index("idx_collection_public", table_name="scenario_collections")
    op.drop_index("idx_collection_user", table_name="scenario_collections")
    op.drop_table("scenario_collections")
