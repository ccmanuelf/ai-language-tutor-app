"""
Manual migration for Session 127
Adds scenario_progress_history and updates learning_sessions table
"""
import sqlite3
from datetime import datetime

DB_PATH = "data/ai_language_tutor.db"

def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Starting Session 127 manual migration...")
    
    try:
        # 1. Create scenario_progress_history table
        print("Creating scenario_progress_history table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scenario_progress_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                scenario_id VARCHAR(100) NOT NULL,
                progress_id VARCHAR(100) NOT NULL,
                started_at DATETIME NOT NULL,
                completed_at DATETIME NOT NULL,
                duration_minutes INTEGER NOT NULL,
                phases_completed INTEGER NOT NULL,
                total_phases INTEGER NOT NULL,
                vocabulary_mastered TEXT,
                objectives_completed TEXT,
                success_rate REAL DEFAULT 0.0,
                completion_score REAL DEFAULT 0.0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scenario_history_user 
            ON scenario_progress_history(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scenario_history_scenario 
            ON scenario_progress_history(scenario_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scenario_history_completed 
            ON scenario_progress_history(completed_at)
        """)
        
        print("✓ scenario_progress_history table created")
        
        # 2. Add source_type to vocabulary_items
        print("Adding source_type to vocabulary_items...")
        try:
            cursor.execute("""
                ALTER TABLE vocabulary_items 
                ADD COLUMN source_type VARCHAR(50)
            """)
            print("✓ source_type column added to vocabulary_items")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("  source_type column already exists, skipping...")
            else:
                raise
        
        # 3. Rename old learning_sessions to learning_sessions_old
        print("Backing up old learning_sessions table...")
        cursor.execute("""
            ALTER TABLE learning_sessions 
            RENAME TO learning_sessions_old
        """)
        
        # 4. Create new learning_sessions table
        print("Creating new learning_sessions table...")
        cursor.execute("""
            CREATE TABLE learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_type VARCHAR(50) NOT NULL,
                source_id VARCHAR(100),
                language VARCHAR(10) NOT NULL,
                started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                duration_seconds INTEGER DEFAULT 0,
                items_studied INTEGER DEFAULT 0,
                items_correct INTEGER DEFAULT 0,
                items_incorrect INTEGER DEFAULT 0,
                accuracy_rate REAL DEFAULT 0.0,
                session_metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_learning_session_user 
            ON learning_sessions(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_learning_session_type 
            ON learning_sessions(session_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_learning_session_date 
            ON learning_sessions(started_at)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_learning_session_source 
            ON learning_sessions(source_id)
        """)
        
        print("✓ New learning_sessions table created")
        
        # 5. Migrate data from old learning_sessions to new (with compatibility mapping)
        print("Migrating data from old learning_sessions...")
        cursor.execute("""
            INSERT INTO learning_sessions (
                user_id, session_type, source_id, language, started_at, ended_at,
                duration_seconds, items_studied, items_correct, items_incorrect,
                accuracy_rate, session_metadata
            )
            SELECT 
                user_id,
                session_type,
                scenario_id as source_id,
                language_code as language,
                started_at,
                ended_at,
                duration_minutes * 60 as duration_seconds,
                items_studied,
                items_correct,
                items_incorrect,
                accuracy_percentage / 100.0 as accuracy_rate,
                mode_specific_data as session_metadata
            FROM learning_sessions_old
        """)
        
        migrated_count = cursor.rowcount
        print(f"✓ Migrated {migrated_count} learning sessions")
        
        # 6. Update Alembic version
        print("Updating Alembic version...")
        cursor.execute("""
            UPDATE alembic_version SET version_num = '103bff5401ca'
        """)
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print(f"   - scenario_progress_history table created")
        print(f"   - source_type added to vocabulary_items")
        print(f"   - learning_sessions table restructured")
        print(f"   - {migrated_count} learning sessions migrated")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
