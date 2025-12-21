#!/usr/bin/env python3
"""
Manual Database Migration for Session 129 - Content Organization & Management

This migration adds comprehensive content organization features:
- Content Collections: Group related content
- Content Tags: Tag content for discovery
- Content Favorites: Mark favorite content
- Study Tracking: Track study sessions and mastery

Run this script to migrate your database:
    python manual_migration_session129.py

Created: 2025-12-20
Session: 129
"""

import sqlite3
from datetime import datetime
from pathlib import Path


def get_db_path():
    """Get the database path"""
    # Use the correct database file from .env (ai_language_tutor.db)
    db_path = Path(__file__).parent / "data" / "ai_language_tutor.db"
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")
    return str(db_path)


def backup_database(db_path):
    """Create a backup of the database"""
    backup_path = (
        f"{db_path}.backup_session129_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    import shutil

    shutil.copy2(db_path, backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    return backup_path


def check_table_exists(cursor, table_name):
    """Check if a table already exists"""
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
    )
    return cursor.fetchone() is not None


def migrate_content_collections(cursor):
    """Create content_collections and content_collection_items tables"""
    print("\n📋 Migrating Content Collections...")

    # Check if tables already exist
    if check_table_exists(cursor, "content_collections"):
        print("⚠️  Table 'content_collections' already exists, skipping...")
        return False

    # Create content_collections table
    cursor.execute(
        """
        CREATE TABLE content_collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            collection_id VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            color VARCHAR(20),
            icon VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """
    )

    # Create indexes for content_collections
    cursor.execute("CREATE INDEX idx_collections_user ON content_collections(user_id)")
    cursor.execute(
        "CREATE INDEX idx_collections_id ON content_collections(collection_id)"
    )

    print("✅ Created table: content_collections")

    # Create content_collection_items table
    cursor.execute(
        """
        CREATE TABLE content_collection_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id VARCHAR(100) NOT NULL,
            content_id VARCHAR(100) NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            position INTEGER DEFAULT 0,
            FOREIGN KEY (collection_id) REFERENCES content_collections(collection_id) ON DELETE CASCADE,
            FOREIGN KEY (content_id) REFERENCES processed_content(content_id) ON DELETE CASCADE,
            UNIQUE(collection_id, content_id)
        )
    """
    )

    # Create indexes for content_collection_items
    cursor.execute(
        "CREATE INDEX idx_collection_items_collection ON content_collection_items(collection_id)"
    )
    cursor.execute(
        "CREATE INDEX idx_collection_items_content ON content_collection_items(content_id)"
    )

    print("✅ Created table: content_collection_items")
    return True


def migrate_content_tags(cursor):
    """Create content_tags table"""
    print("\n🏷️  Migrating Content Tags...")

    if check_table_exists(cursor, "content_tags"):
        print("⚠️  Table 'content_tags' already exists, skipping...")
        return False

    # Create content_tags table
    cursor.execute(
        """
        CREATE TABLE content_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content_id VARCHAR(100) NOT NULL,
            tag VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (content_id) REFERENCES processed_content(content_id) ON DELETE CASCADE,
            UNIQUE(user_id, content_id, tag)
        )
    """
    )

    # Create indexes for content_tags
    cursor.execute("CREATE INDEX idx_tags_user ON content_tags(user_id)")
    cursor.execute("CREATE INDEX idx_tags_content ON content_tags(content_id)")
    cursor.execute("CREATE INDEX idx_tags_tag ON content_tags(tag)")

    print("✅ Created table: content_tags")
    return True


def migrate_content_favorites(cursor):
    """Create content_favorites table"""
    print("\n⭐ Migrating Content Favorites...")

    if check_table_exists(cursor, "content_favorites"):
        print("⚠️  Table 'content_favorites' already exists, skipping...")
        return False

    # Create content_favorites table
    cursor.execute(
        """
        CREATE TABLE content_favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content_id VARCHAR(100) NOT NULL,
            favorited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (content_id) REFERENCES processed_content(content_id) ON DELETE CASCADE,
            UNIQUE(user_id, content_id)
        )
    """
    )

    # Create indexes for content_favorites
    cursor.execute("CREATE INDEX idx_favorites_user ON content_favorites(user_id)")
    cursor.execute(
        "CREATE INDEX idx_favorites_content ON content_favorites(content_id)"
    )

    print("✅ Created table: content_favorites")
    return True


def migrate_study_tracking(cursor):
    """Create study tracking tables"""
    print("\n📊 Migrating Study Tracking...")

    # Create content_study_sessions table
    if not check_table_exists(cursor, "content_study_sessions"):
        cursor.execute(
            """
            CREATE TABLE content_study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content_id VARCHAR(100) NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                duration_seconds INTEGER,
                materials_studied JSON,
                items_correct INTEGER DEFAULT 0,
                items_total INTEGER DEFAULT 0,
                completion_percentage DECIMAL(5,2) DEFAULT 0.0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (content_id) REFERENCES processed_content(content_id) ON DELETE CASCADE
            )
        """
        )

        # Create indexes for content_study_sessions
        cursor.execute(
            "CREATE INDEX idx_study_sessions_user ON content_study_sessions(user_id)"
        )
        cursor.execute(
            "CREATE INDEX idx_study_sessions_content ON content_study_sessions(content_id)"
        )
        cursor.execute(
            "CREATE INDEX idx_study_sessions_date ON content_study_sessions(started_at)"
        )

        print("✅ Created table: content_study_sessions")
    else:
        print("⚠️  Table 'content_study_sessions' already exists, skipping...")

    # Create content_mastery_status table
    if not check_table_exists(cursor, "content_mastery_status"):
        cursor.execute(
            """
            CREATE TABLE content_mastery_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content_id VARCHAR(100) NOT NULL,
                mastery_level VARCHAR(20) DEFAULT 'not_started',
                total_study_time_seconds INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                last_studied_at TIMESTAMP,
                items_mastered INTEGER DEFAULT 0,
                items_total INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (content_id) REFERENCES processed_content(content_id) ON DELETE CASCADE,
                UNIQUE(user_id, content_id)
            )
        """
        )

        # Create indexes for content_mastery_status
        cursor.execute(
            "CREATE INDEX idx_mastery_user ON content_mastery_status(user_id)"
        )
        cursor.execute(
            "CREATE INDEX idx_mastery_content ON content_mastery_status(content_id)"
        )
        cursor.execute(
            "CREATE INDEX idx_mastery_level ON content_mastery_status(mastery_level)"
        )

        print("✅ Created table: content_mastery_status")
    else:
        print("⚠️  Table 'content_mastery_status' already exists, skipping...")

    return True


def verify_migration(cursor):
    """Verify all tables were created successfully"""
    print("\n🔍 Verifying Migration...")

    required_tables = [
        "content_collections",
        "content_collection_items",
        "content_tags",
        "content_favorites",
        "content_study_sessions",
        "content_mastery_status",
    ]

    all_exist = True
    for table in required_tables:
        exists = check_table_exists(cursor, table)
        status = "✅" if exists else "❌"
        print(f"{status} {table}: {'EXISTS' if exists else 'MISSING'}")
        if not exists:
            all_exist = False

    return all_exist


def main():
    """Run the migration"""
    print("=" * 70)
    print("SESSION 129 DATABASE MIGRATION - CONTENT ORGANIZATION & MANAGEMENT")
    print("=" * 70)

    try:
        # Get database path
        db_path = get_db_path()
        print(f"\n📍 Database: {db_path}")

        # Backup database
        backup_path = backup_database(db_path)

        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Run migrations
        collections_created = migrate_content_collections(cursor)
        tags_created = migrate_content_tags(cursor)
        favorites_created = migrate_content_favorites(cursor)
        study_created = migrate_study_tracking(cursor)

        # Commit changes
        conn.commit()

        # Verify migration
        success = verify_migration(cursor)

        # Close connection
        conn.close()

        # Summary
        print("\n" + "=" * 70)
        if success:
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("\nNew Tables Created:")
            if collections_created:
                print("  • content_collections")
                print("  • content_collection_items")
            if tags_created:
                print("  • content_tags")
            if favorites_created:
                print("  • content_favorites")
            if study_created:
                print("  • content_study_sessions")
                print("  • content_mastery_status")

            print(f"\n💾 Backup saved at: {backup_path}")
            print("\n🎯 Ready to implement content organization features!")
        else:
            print("❌ MIGRATION FAILED - Some tables are missing")
            print(f"💾 Database backup available at: {backup_path}")
            return 1

        print("=" * 70)
        return 0

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except sqlite3.Error as e:
        print(f"\n❌ Database Error: {e}")
        print("💾 Database backup may be available")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
