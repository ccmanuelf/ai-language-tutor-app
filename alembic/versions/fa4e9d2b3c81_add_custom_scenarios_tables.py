"""Add custom scenarios tables

Revision ID: fa4e9d2b3c81
Revises: a358c11bb177
Create Date: 2025-12-21 00:00:00.000000

"""

import json
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fa4e9d2b3c81"
down_revision: Union[str, Sequence[str], None] = "a358c11bb177"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create scenarios table
    op.create_table(
        "scenarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scenario_id", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("estimated_duration", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=True),
        sa.Column("user_role", sa.String(length=50), nullable=True),
        sa.Column("ai_role", sa.String(length=50), nullable=True),
        sa.Column("setting", sa.Text(), nullable=True),
        # Ownership
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column(
            "is_system_scenario", sa.Boolean(), nullable=False, server_default="0"
        ),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="0"),
        # JSON columns for complex data
        sa.Column("prerequisites", sa.JSON(), nullable=True),
        sa.Column("learning_outcomes", sa.JSON(), nullable=True),
        sa.Column("vocabulary_focus", sa.JSON(), nullable=True),
        sa.Column("cultural_context", sa.JSON(), nullable=True),
        # Metadata
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
        sa.UniqueConstraint("scenario_id"),
    )

    # Create indexes for scenarios
    op.create_index("idx_scenario_user", "scenarios", ["created_by"])
    op.create_index("idx_scenario_category", "scenarios", ["category"])
    op.create_index(
        "idx_scenario_public", "scenarios", ["is_public", "is_system_scenario"]
    )

    # Create scenario_phases table
    op.create_table(
        "scenario_phases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scenario_id", sa.Integer(), nullable=False),
        sa.Column("phase_number", sa.Integer(), nullable=False),
        sa.Column("phase_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("expected_duration_minutes", sa.Integer(), nullable=True),
        # JSON columns for arrays
        sa.Column("key_vocabulary", sa.JSON(), nullable=True),
        sa.Column("essential_phrases", sa.JSON(), nullable=True),
        sa.Column("learning_objectives", sa.JSON(), nullable=True),
        sa.Column("success_criteria", sa.JSON(), nullable=True),
        sa.Column("cultural_notes", sa.Text(), nullable=True),
        # Metadata
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "scenario_id", "phase_number", name="uq_scenario_phase_number"
        ),
    )

    # Create index for scenario_phases
    op.create_index("idx_phase_scenario", "scenario_phases", ["scenario_id"])

    # Migrate existing scenarios from JSON to database
    _migrate_scenarios_from_json()


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_index("idx_phase_scenario", table_name="scenario_phases")
    op.drop_table("scenario_phases")

    op.drop_index("idx_scenario_public", table_name="scenarios")
    op.drop_index("idx_scenario_category", table_name="scenarios")
    op.drop_index("idx_scenario_user", table_name="scenarios")
    op.drop_table("scenarios")


def _migrate_scenarios_from_json():
    """Migrate existing scenarios from JSON file to database."""
    import os
    from pathlib import Path

    # Path to scenarios JSON
    json_path = (
        Path(__file__).parent.parent.parent / "data" / "scenarios" / "scenarios.json"
    )

    if not json_path.exists():
        print(f"⚠️  Scenarios JSON not found at {json_path}, skipping migration")
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            scenarios_data = json.load(f)

        # Get database connection
        connection = op.get_bind()

        # System user ID for system scenarios
        SYSTEM_USER_ID = 0

        migrated_count = 0

        # scenarios_data is a dict with scenario_id as keys
        for scenario_key, scenario in scenarios_data.items():
            # Insert scenario
            scenario_result = connection.execute(
                sa.text("""
                    INSERT INTO scenarios (
                        scenario_id, title, description, category, difficulty,
                        estimated_duration, language, user_role, ai_role, setting,
                        created_by, is_system_scenario, is_public,
                        prerequisites, learning_outcomes, vocabulary_focus, cultural_context
                    ) VALUES (
                        :scenario_id, :title, :description, :category, :difficulty,
                        :estimated_duration, :language, :user_role, :ai_role, :setting,
                        :created_by, :is_system_scenario, :is_public,
                        :prerequisites, :learning_outcomes, :vocabulary_focus, :cultural_context
                    )
                """),
                {
                    "scenario_id": scenario.get("scenario_id", scenario_key),
                    "title": scenario.get("name", scenario_key),
                    "description": scenario.get("description", ""),
                    "category": scenario["category"],
                    "difficulty": scenario["difficulty"],
                    "estimated_duration": scenario.get(
                        "duration_minutes", scenario.get("estimated_duration", 20)
                    ),
                    "language": scenario.get("language", "en"),
                    "user_role": scenario.get("user_role"),
                    "ai_role": scenario.get("ai_role"),
                    "setting": scenario.get("setting"),
                    "created_by": SYSTEM_USER_ID,
                    "is_system_scenario": 1,
                    "is_public": 1,
                    "prerequisites": json.dumps(scenario.get("prerequisites", [])),
                    "learning_outcomes": json.dumps(
                        scenario.get("learning_outcomes", [])
                    ),
                    "vocabulary_focus": json.dumps(
                        scenario.get("vocabulary_focus", [])
                    ),
                    "cultural_context": json.dumps(
                        scenario.get("cultural_context", {})
                    ),
                },
            )

            # Get the inserted scenario ID
            db_scenario_id = scenario_result.lastrowid

            # Insert phases
            phases = scenario.get("phases", [])
            for idx, phase in enumerate(phases):
                connection.execute(
                    sa.text("""
                        INSERT INTO scenario_phases (
                            scenario_id, phase_number, phase_id, name, description,
                            expected_duration_minutes, key_vocabulary, essential_phrases,
                            learning_objectives, success_criteria, cultural_notes
                        ) VALUES (
                            :scenario_id, :phase_number, :phase_id, :name, :description,
                            :expected_duration_minutes, :key_vocabulary, :essential_phrases,
                            :learning_objectives, :success_criteria, :cultural_notes
                        )
                    """),
                    {
                        "scenario_id": db_scenario_id,
                        "phase_number": idx + 1,
                        "phase_id": phase["phase_id"],
                        "name": phase["name"],
                        "description": phase.get("description", ""),
                        "expected_duration_minutes": phase.get(
                            "expected_duration_minutes", 5
                        ),
                        "key_vocabulary": json.dumps(phase.get("key_vocabulary", [])),
                        "essential_phrases": json.dumps(
                            phase.get("essential_phrases", [])
                        ),
                        "learning_objectives": json.dumps(
                            phase.get("learning_objectives", [])
                        ),
                        "success_criteria": json.dumps(
                            phase.get("success_criteria", [])
                        ),
                        "cultural_notes": phase.get("cultural_notes"),
                    },
                )

            migrated_count += 1

        print(
            f"✅ Successfully migrated {migrated_count} scenarios from JSON to database"
        )

        # Create backup of JSON file
        backup_path = json_path.with_suffix(".json.backup")
        import shutil

        shutil.copy2(json_path, backup_path)
        print(f"✅ Created backup at {backup_path}")

    except Exception as e:
        print(f"❌ Error migrating scenarios: {e}")
        raise
