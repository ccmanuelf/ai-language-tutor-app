#!/usr/bin/env python3
"""
Add Language Configuration Tables for Admin Management
Task 3.1.3 - Language Configuration Panel

This script adds new tables to support advanced language configuration
including voice model management and admin configuration settings.
"""

import sqlite3
import json
import logging
from pathlib import Path
import sys

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_language_config_tables():
    """Create additional tables for language configuration management"""

    db_path = "data/ai_language_tutor.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create voice_models table for Piper TTS model management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name VARCHAR(100) NOT NULL UNIQUE,
                language_code VARCHAR(10) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                config_path VARCHAR(500) NOT NULL,
                quality_level VARCHAR(20) DEFAULT 'medium',
                sample_rate INTEGER DEFAULT 22050,
                file_size_mb REAL,
                is_active BOOLEAN DEFAULT 1,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON,
                FOREIGN KEY (language_code) REFERENCES languages (code)
            )
        """)

        # Create admin_language_config table for admin-specific language settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_language_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                language_code VARCHAR(10) NOT NULL,
                is_enabled_globally BOOLEAN DEFAULT 1,
                default_voice_model VARCHAR(100),
                speech_recognition_enabled BOOLEAN DEFAULT 1,
                text_to_speech_enabled BOOLEAN DEFAULT 1,
                pronunciation_analysis_enabled BOOLEAN DEFAULT 1,
                conversation_mode_enabled BOOLEAN DEFAULT 1,
                tutor_mode_enabled BOOLEAN DEFAULT 1,
                scenario_mode_enabled BOOLEAN DEFAULT 1,
                realtime_analysis_enabled BOOLEAN DEFAULT 1,
                difficulty_levels JSON DEFAULT '["beginner", "intermediate", "advanced"]',
                voice_settings JSON DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (language_code) REFERENCES languages (code),
                FOREIGN KEY (default_voice_model) REFERENCES voice_models (model_name),
                UNIQUE (language_code)
            )
        """)

        # Create admin_feature_toggles table for system-wide feature management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_feature_toggles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_name VARCHAR(100) NOT NULL UNIQUE,
                is_enabled BOOLEAN DEFAULT 1,
                description TEXT,
                category VARCHAR(50) DEFAULT 'general',
                requires_restart BOOLEAN DEFAULT 0,
                min_role VARCHAR(20) DEFAULT 'CHILD',
                configuration JSON DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        logger.info("✅ Language configuration tables created successfully")

        # Populate voice_models table with detected models
        populate_voice_models(cursor)

        # Populate admin_language_config with current languages
        populate_admin_language_config(cursor)

        # Populate admin_feature_toggles with core features
        populate_admin_feature_toggles(cursor)

        conn.commit()
        conn.close()

        logger.info("✅ Database schema upgrade completed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to create language configuration tables: {e}")
        return False


def populate_voice_models(cursor):
    """Populate voice_models table with available Piper TTS models"""

    voices_dir = Path("app/data/piper_voices")
    if not voices_dir.exists():
        logger.warning("Piper voices directory not found")
        return

    # Clear existing entries
    cursor.execute("DELETE FROM voice_models")

    # Language mapping for voice models
    language_mapping = {
        "en_US": "en",
        "es_AR": "es",
        "es_ES": "es",
        "es_MX": "es",
        "fr_FR": "fr",
        "de_DE": "de",
        "it_IT": "it",
        "pt_BR": "pt",
        "zh_CN": "zh",
    }

    for onnx_file in voices_dir.glob("*.onnx"):
        if onnx_file.stat().st_size < 1000:  # Skip corrupt files
            continue

        model_name = onnx_file.stem
        config_file = onnx_file.with_suffix(".onnx.json")

        # Extract language code from model name
        lang_prefix = model_name.split("-")[0]
        language_code = language_mapping.get(lang_prefix, "en")

        # Extract quality level
        quality_level = "medium"
        if "high" in model_name:
            quality_level = "high"
        elif "low" in model_name:
            quality_level = "low"
        elif "x_low" in model_name:
            quality_level = "x_low"

        # Calculate file size in MB
        file_size_mb = round(onnx_file.stat().st_size / (1024 * 1024), 2)

        # Load config metadata if available
        metadata = {}
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config_data = json.load(f)
                    metadata = {
                        "speaker": config_data.get("speaker", "unknown"),
                        "language_info": config_data.get("language", {}),
                        "audio_info": config_data.get("audio", {}),
                    }
            except Exception as e:
                logger.warning(f"Could not load config for {model_name}: {e}")

        # Determine if this should be the default for this language
        is_default = "medium" in model_name and (
            lang_prefix == "en_US" or lang_prefix == "es_MX" or lang_prefix == "fr_FR"
        )

        cursor.execute(
            """
            INSERT INTO voice_models
            (model_name, language_code, file_path, config_path, quality_level,
             sample_rate, file_size_mb, is_active, is_default, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                model_name,
                language_code,
                str(onnx_file),
                str(config_file) if config_file.exists() else "",
                quality_level,
                metadata.get("audio_info", {}).get("sample_rate", 22050),
                file_size_mb,
                True,
                is_default,
                json.dumps(metadata),
            ),
        )

    logger.info("✅ Voice models populated successfully")


def populate_admin_language_config(cursor):
    """Populate admin_language_config with current languages"""

    # Get current languages
    cursor.execute("SELECT code, name FROM languages WHERE is_active = 1")
    languages = cursor.fetchall()

    # Clear existing config
    cursor.execute("DELETE FROM admin_language_config")

    for code, name in languages:
        # Find default voice model for this language
        cursor.execute(
            """
            SELECT model_name FROM voice_models
            WHERE language_code = ? AND is_default = 1
            LIMIT 1
        """,
            (code,),
        )
        result = cursor.fetchone()
        default_voice = result[0] if result else None

        # Enhanced voice settings per language
        voice_settings = {
            "speaking_rate": 1.0,
            "noise_scale": 0.667,
            "noise_w": 0.8,
            "length_scale": 1.0,
            "voice_variant": "default",
            "audio_format": "wav",
            "sample_rate": 22050,
        }

        cursor.execute(
            """
            INSERT INTO admin_language_config
            (language_code, is_enabled_globally, default_voice_model,
             speech_recognition_enabled, text_to_speech_enabled,
             pronunciation_analysis_enabled, conversation_mode_enabled,
             tutor_mode_enabled, scenario_mode_enabled, realtime_analysis_enabled,
             voice_settings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                code,
                True,  # All languages enabled by default
                default_voice,
                True,  # STT enabled
                True,  # TTS enabled
                True,  # Pronunciation analysis enabled
                True,  # Conversation mode enabled
                True,  # Tutor mode enabled
                True,  # Scenario mode enabled
                True,  # Real-time analysis enabled
                json.dumps(voice_settings),
            ),
        )

    logger.info("✅ Admin language configuration populated successfully")


def populate_admin_feature_toggles(cursor):
    """Populate admin_feature_toggles with core system features"""

    # Clear existing toggles
    cursor.execute("DELETE FROM admin_feature_toggles")

    features = [
        # Core Learning Features
        (
            "content_processing",
            True,
            "YouTube content processing and analysis",
            "learning",
            False,
            "CHILD",
        ),
        (
            "conversation_chat",
            True,
            "AI conversation and chat functionality",
            "learning",
            False,
            "CHILD",
        ),
        (
            "real_time_analysis",
            True,
            "Real-time pronunciation and grammar analysis",
            "learning",
            False,
            "CHILD",
        ),
        (
            "tutor_modes",
            True,
            "Fluently-style tutor modes (chit-chat, interview, etc.)",
            "learning",
            False,
            "CHILD",
        ),
        (
            "scenario_modes",
            True,
            "Pingo-style scenario-based conversations",
            "learning",
            False,
            "CHILD",
        ),
        (
            "speech_recognition",
            True,
            "Speech-to-text functionality",
            "speech",
            False,
            "CHILD",
        ),
        ("text_to_speech", True, "Text-to-speech synthesis", "speech", False, "CHILD"),
        # Admin Features
        (
            "user_management",
            True,
            "User account creation and management",
            "admin",
            False,
            "ADMIN",
        ),
        (
            "language_management",
            True,
            "Language configuration and voice model management",
            "admin",
            False,
            "ADMIN",
        ),
        (
            "feature_toggles",
            True,
            "System feature toggle management",
            "admin",
            False,
            "ADMIN",
        ),
        (
            "system_monitoring",
            True,
            "System status and performance monitoring",
            "admin",
            False,
            "ADMIN",
        ),
        (
            "data_export",
            True,
            "User data and progress export functionality",
            "admin",
            False,
            "ADMIN",
        ),
        # Guest Features
        ("guest_access", True, "Allow guest user sessions", "access", False, "ADMIN"),
        (
            "guest_learning_features",
            True,
            "Allow guests to use learning features",
            "access",
            False,
            "ADMIN",
        ),
        # Performance Features
        (
            "ai_cost_optimization",
            True,
            "Smart AI provider routing for cost efficiency",
            "performance",
            False,
            "ADMIN",
        ),
        (
            "response_caching",
            True,
            "Cache AI responses to reduce API calls",
            "performance",
            False,
            "ADMIN",
        ),
        (
            "offline_mode",
            True,
            "Offline learning capabilities",
            "performance",
            False,
            "CHILD",
        ),
    ]

    for (
        feature_name,
        is_enabled,
        description,
        category,
        requires_restart,
        min_role,
    ) in features:
        cursor.execute(
            """
            INSERT INTO admin_feature_toggles
            (feature_name, is_enabled, description, category, requires_restart, min_role)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                feature_name,
                is_enabled,
                description,
                category,
                requires_restart,
                min_role,
            ),
        )

    logger.info("✅ Admin feature toggles populated successfully")


if __name__ == "__main__":
    if create_language_config_tables():
        print("🎉 Language configuration database schema ready!")
        sys.exit(0)
    else:
        print("❌ Failed to create language configuration schema")
        sys.exit(1)
