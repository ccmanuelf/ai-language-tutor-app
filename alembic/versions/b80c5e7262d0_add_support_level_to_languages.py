"""add_support_level_to_languages

Revision ID: b80c5e7262d0
Revises: cbb0c3ec84ad
Create Date: 2025-12-16 12:57:02.203304

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b80c5e7262d0"
down_revision: Union[str, Sequence[str], None] = "cbb0c3ec84ad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add support_level column to languages table."""
    # Create enum type for support_level
    support_level_enum = sa.Enum("FULL", "STT_ONLY", "FUTURE", name="supportlevel")
    support_level_enum.create(op.get_bind(), checkfirst=True)

    # Add support_level column with default value 'FULL'
    op.add_column(
        "languages",
        sa.Column(
            "support_level", support_level_enum, nullable=False, server_default="FULL"
        ),
    )

    # Update existing languages based on has_tts_support flag
    # Languages with has_tts_support=False should be STT_ONLY
    op.execute("""
        UPDATE languages
        SET support_level = 'STT_ONLY'
        WHERE has_tts_support = 0
    """)


def downgrade() -> None:
    """Downgrade schema - Remove support_level column from languages table."""
    # Remove the column
    op.drop_column("languages", "support_level")

    # Drop the enum type
    support_level_enum = sa.Enum("FULL", "STT_ONLY", "FUTURE", name="supportlevel")
    support_level_enum.drop(op.get_bind(), checkfirst=True)
