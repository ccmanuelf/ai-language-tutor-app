#!/usr/bin/env python3
"""
Manual Migration for Session 128 - Content Persistence Tables

Creates:
- processed_content table
- learning_materials table

This is a safe migration that only creates tables if they don't exist.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database.config import db_manager
from app.models.database import Base, LearningMaterialDB, ProcessedContent


def run_migration():
    """Run the migration to create content persistence tables"""
    print("🔄 Starting Session 128 Migration - Content Persistence Tables")
    print("=" * 70)

    try:
        # Get SQLite engine from db_manager
        engine = db_manager.sqlite_engine

        print("\n📋 Tables to create:")
        print("  1. processed_content")
        print("  2. learning_materials")

        # Create only these specific tables (safe - only creates if not exists)
        print("\n🔨 Creating tables...")
        Base.metadata.create_all(
            engine,
            tables=[ProcessedContent.__table__, LearningMaterialDB.__table__],
            checkfirst=True,  # Only create if table doesn't exist
        )

        print("\n✅ Migration completed successfully!")
        print("\n📊 Tables created:")
        print("  ✓ processed_content (stores YouTube videos, documents, etc.)")
        print("  ✓ learning_materials (stores generated flashcards, quizzes, etc.)")

        # Verify tables were created
        print("\n🔍 Verifying tables exist...")
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if "processed_content" in tables and "learning_materials" in tables:
            print("  ✓ Both tables verified in database")
        else:
            print("  ⚠️  Warning: Tables may not have been created")
            print(f"  Found tables: {tables}")

        print("\n" + "=" * 70)
        print("✅ Session 128 Migration Complete!")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_migration()
