#!/usr/bin/env python3
"""
Sample Data Initialization for AI Language Tutor App

This script creates sample data for testing and development:
- Default languages
- Test users
- Sample conversations
- Sample documents
- Test vocabulary items
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta, timezone
from app.database.config import db_manager
from app.database.chromadb_config import ChromaDBManager
from sqlalchemy import text
import logging
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Simple password hashing for testing"""
    return hashlib.sha256(password.encode()).hexdigest()


def init_languages():
    """Initialize default languages"""
    logger.info("Initializing default languages...")

    session = db_manager.get_sqlite_session()

    languages = [
        ("en", "English", "English", True, True, True),
        ("es", "Spanish", "Español", True, True, True),
        ("fr", "French", "Français", True, True, True),
        ("zh", "Chinese (Mandarin)", "中文", True, True, True),
        ("ja", "Japanese", "日本語", False, True, True),
        ("de", "German", "Deutsch", False, True, True),
    ]

    try:
        for code, name, native_name, is_active, has_speech, has_tts in languages:
            session.execute(
                text("""
                INSERT OR IGNORE INTO languages
                (code, name, native_name, is_active, has_speech_support, has_tts_support)
                VALUES (:code, :name, :native_name, :active, :speech, :tts)
                """),
                {
                    "code": code,
                    "name": name,
                    "native_name": native_name,
                    "active": is_active,
                    "speech": has_speech,
                    "tts": has_tts,
                },
            )

        session.commit()
        logger.info(f"✅ Initialized {len(languages)} languages")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Failed to initialize languages: {e}")
        raise
    finally:
        session.close()


def init_users():
    """Initialize test users"""
    logger.info("Initializing test users...")

    session = db_manager.get_sqlite_session()

    users = [
        {
            "user_id": "user_001",
            "username": "familia_admin",
            "email": "admin@family.local",
            "first_name": "Family",
            "last_name": "Admin",
            "role": "user",  # No admin roles in family app
            "is_active": True,
            "is_verified": True,
        },
        {
            "user_id": "user_002",
            "username": "estudiante_1",
            "email": "student1@family.local",
            "first_name": "Student",
            "last_name": "One",
            "role": "user",
            "is_active": True,
            "is_verified": True,
        },
        {
            "user_id": "user_003",
            "username": "estudiante_2",
            "email": "student2@family.local",
            "first_name": "Student",
            "last_name": "Two",
            "role": "user",
            "is_active": True,
            "is_verified": True,
        },
    ]

    try:
        for user in users:
            session.execute(
                text("""
                INSERT OR IGNORE INTO users
                (user_id, username, email, password_hash, role, first_name, last_name,
                 is_active, is_verified, created_at, updated_at)
                VALUES (:user_id, :username, :email, :password_hash, :role, :first_name, :last_name,
                        :is_active, :is_verified, :created_at, :updated_at)
                """),
                {
                    **user,
                    "password_hash": hash_password("family_password_123"),
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                },
            )

        session.commit()
        logger.info(f"✅ Initialized {len(users)} test users")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Failed to initialize users: {e}")
        raise
    finally:
        session.close()


def init_sample_conversations():
    """Initialize sample conversations"""
    logger.info("Initializing sample conversations...")

    session = db_manager.get_sqlite_session()

    conversations = [
        {
            "conversation_id": "conv_001",
            "user_id": 2,  # user_002 -> db_id 2
            "title": "Spanish Greetings Practice",
            "language": "es",
            "ai_model": "gpt-3.5-turbo",
            "context_data": '{"practice_type": "greetings", "difficulty": "beginner"}',
            "started_at": datetime.now(timezone.utc) - timedelta(days=2),
            "last_message_at": datetime.now(timezone.utc) - timedelta(days=2),
            "message_count": 8,
            "total_tokens": 150,
            "estimated_cost": 0.02,
            "is_active": False,
        },
        {
            "conversation_id": "conv_002",
            "user_id": 3,  # user_003 -> db_id 3
            "title": "Chinese Numbers and Counting",
            "language": "zh",
            "ai_model": "gpt-4",
            "context_data": '{"practice_type": "numbers", "difficulty": "intermediate"}',
            "started_at": datetime.now(timezone.utc) - timedelta(days=1),
            "last_message_at": datetime.now(timezone.utc) - timedelta(hours=3),
            "message_count": 12,
            "total_tokens": 320,
            "estimated_cost": 0.08,
            "is_active": True,
        },
        {
            "conversation_id": "conv_003",
            "user_id": 1,  # user_001 -> db_id 1
            "title": "French Restaurant Vocabulary",
            "language": "fr",
            "ai_model": "gpt-3.5-turbo",
            "context_data": '{"scenario": "restaurant", "difficulty": "beginner"}',
            "started_at": datetime.now(timezone.utc) - timedelta(hours=6),
            "last_message_at": datetime.now(timezone.utc) - timedelta(minutes=30),
            "message_count": 5,
            "total_tokens": 95,
            "estimated_cost": 0.015,
            "is_active": True,
        },
    ]

    try:
        for conv in conversations:
            session.execute(
                text("""
                INSERT OR IGNORE INTO conversations
                (conversation_id, user_id, title, language, ai_model, context_data,
                 started_at, last_message_at, message_count, total_tokens, estimated_cost, is_active)
                VALUES (:conversation_id, :user_id, :title, :language, :ai_model, :context_data,
                        :started_at, :last_message_at, :message_count, :total_tokens, :estimated_cost, :is_active)
                """),
                conv,
            )

        session.commit()
        logger.info(f"✅ Initialized {len(conversations)} sample conversations")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Failed to initialize conversations: {e}")
        raise
    finally:
        session.close()


def init_sample_vocabulary():
    """Initialize sample vocabulary items"""
    logger.info("Initializing sample vocabulary...")

    session = db_manager.get_sqlite_session()

    # First, get user IDs from the database
    user_map = {}
    result = session.execute(text("SELECT id, user_id FROM users"))
    for db_id, user_id in result.fetchall():
        user_map[user_id] = db_id

    vocab_items = [
        # Spanish vocabulary
        (
            user_map.get("user_002", 1),
            "hola",
            "hello",
            "es",
            3,
            datetime.now(timezone.utc) + timedelta(days=1),
        ),
        (
            user_map.get("user_002", 1),
            "gracias",
            "thank you",
            "es",
            5,
            datetime.now(timezone.utc) + timedelta(days=2),
        ),
        (
            user_map.get("user_002", 1),
            "comida",
            "food",
            "es",
            2,
            datetime.now(timezone.utc),
        ),
        # Chinese vocabulary
        (
            user_map.get("user_003", 1),
            "你好",
            "hello",
            "zh",
            4,
            datetime.now(timezone.utc) + timedelta(days=1),
        ),
        (
            user_map.get("user_003", 1),
            "谢谢",
            "thank you",
            "zh",
            3,
            datetime.now(timezone.utc) + timedelta(hours=12),
        ),
        (
            user_map.get("user_003", 1),
            "一",
            "one",
            "zh",
            6,
            datetime.now(timezone.utc) + timedelta(days=3),
        ),
        # French vocabulary
        (
            user_map.get("user_001", 1),
            "bonjour",
            "hello",
            "fr",
            4,
            datetime.now(timezone.utc) + timedelta(days=1),
        ),
        (
            user_map.get("user_001", 1),
            "restaurant",
            "restaurant",
            "fr",
            2,
            datetime.now(timezone.utc),
        ),
        (
            user_map.get("user_001", 1),
            "menu",
            "menu",
            "fr",
            1,
            datetime.now(timezone.utc) - timedelta(hours=1),
        ),
    ]

    try:
        for vocab in vocab_items:
            user_id, word, translation, language, times_studied, next_review = vocab
            session.execute(
                text("""
                INSERT OR IGNORE INTO vocabulary_items
                (user_id, word, translation, language, times_studied, next_review_date, updated_at)
                VALUES (:user_id, :word, :translation, :language, :times_studied, :next_review, :updated_at)
                """),
                {
                    "user_id": user_id,
                    "word": word,
                    "translation": translation,
                    "language": language,
                    "times_studied": times_studied,
                    "next_review": next_review,
                    "updated_at": datetime.now(timezone.utc),
                },
            )

        session.commit()
        logger.info(f"✅ Initialized {len(vocab_items)} vocabulary items")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Failed to initialize vocabulary: {e}")
        raise
    finally:
        session.close()


def init_chromadb_samples():
    """Initialize sample ChromaDB embeddings"""
    logger.info("Initializing sample ChromaDB embeddings...")

    try:
        chroma_manager = ChromaDBManager()

        # Sample documents
        documents = [
            {
                "user_id": "user_002",
                "document_id": "doc_001",
                "content": "Hola, mi nombre es estudiante. Me gusta aprender español. Es muy interesante.",
                "metadata": {
                    "language": "es",
                    "content_type": "text",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "title": "Spanish Introduction Practice",
                },
            },
            {
                "user_id": "user_003",
                "document_id": "doc_002",
                "content": "你好，我是学生。我学习中文。中文很有意思。",
                "metadata": {
                    "language": "zh",
                    "content_type": "text",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "title": "Chinese Introduction Practice",
                },
            },
        ]

        for doc in documents:
            chroma_manager.add_document_embedding(
                user_id=doc["user_id"],
                document_id=doc["document_id"],
                content=doc["content"],
                metadata=doc["metadata"],
            )

        logger.info(f"✅ Initialized {len(documents)} ChromaDB document embeddings")

    except Exception as e:
        logger.error(f"❌ Failed to initialize ChromaDB samples: {e}")
        raise


def verify_sample_data():
    """Verify that sample data was created successfully"""
    logger.info("Verifying sample data...")

    session = db_manager.get_sqlite_session()

    try:
        # Check languages
        result = session.execute(text("SELECT COUNT(*) FROM languages"))
        language_count = result.scalar()
        logger.info(f"Languages: {language_count} records")

        # Check users
        result = session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        logger.info(f"Users: {user_count} records")

        # Check conversations
        result = session.execute(text("SELECT COUNT(*) FROM conversations"))
        conv_count = result.scalar()
        logger.info(f"Conversations: {conv_count} records")

        # Check vocabulary
        result = session.execute(text("SELECT COUNT(*) FROM vocabulary_items"))
        vocab_count = result.scalar()
        logger.info(f"Vocabulary: {vocab_count} records")

        # Check ChromaDB
        chroma_manager = ChromaDBManager()
        collections = chroma_manager.client.list_collections()
        total_embeddings = sum(c.count() for c in collections)
        logger.info(
            f"ChromaDB embeddings: {total_embeddings} records across {len(collections)} collections"
        )

        logger.info("✅ Sample data verification completed!")

    except Exception as e:
        logger.error(f"❌ Sample data verification failed: {e}")
        raise
    finally:
        session.close()


def main():
    """Initialize all sample data"""
    print("🚀 AI Language Tutor - Sample Data Initialization")
    print("=" * 50)

    try:
        init_languages()
        init_users()
        init_sample_conversations()
        init_sample_vocabulary()
        init_chromadb_samples()
        verify_sample_data()

        print("\n🎉 Sample data initialization completed successfully!")
        print("The database is now ready for testing and development.")

    except Exception as e:
        print(f"\n💥 Sample data initialization failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
