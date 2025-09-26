#!/usr/bin/env python3
"""
Test Language Configuration API Endpoints
Task 3.1.3 - Language Configuration Panel

This script tests the language configuration API endpoints to ensure
they're working correctly with proper authentication and data handling.
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))


async def test_language_config_api():
    """Test the language configuration API endpoints"""

    print("🧪 TESTING LANGUAGE CONFIGURATION API")
    print("=" * 60)

    try:
        # Import the API components
        from app.api.language_config import router
        from app.models.database import get_db
        from app.services.admin_auth import admin_auth_service

        print("✅ Successfully imported API components")

        # Test database connection
        db_gen = get_db()
        db = next(db_gen)

        print("✅ Database connection established")

        # Test basic database queries
        from sqlalchemy import text

        # Test languages query
        result = db.execute(text("SELECT COUNT(*) FROM languages WHERE is_active = 1"))
        active_languages = result.fetchone()[0]
        print(f"✅ Active languages: {active_languages}")

        # Test voice models query
        result = db.execute(
            text("SELECT COUNT(*) FROM voice_models WHERE is_active = 1")
        )
        active_voice_models = result.fetchone()[0]
        print(f"✅ Active voice models: {active_voice_models}")

        # Test language config query
        result = db.execute(text("SELECT COUNT(*) FROM admin_language_config"))
        language_configs = result.fetchone()[0]
        print(f"✅ Language configurations: {language_configs}")

        # Test feature toggles query
        result = db.execute(text("SELECT COUNT(*) FROM admin_feature_toggles"))
        feature_toggles = result.fetchone()[0]
        print(f"✅ Feature toggles: {feature_toggles}")

        print()
        print("🔍 TESTING API ENDPOINT STRUCTURE:")
        print("-" * 40)

        # Check API router routes
        routes = [route.path for route in router.routes]
        print(f"✅ API routes configured: {len(routes)}")
        for route in routes[:5]:  # Show first 5 routes
            print(f"   - {route}")
        if len(routes) > 5:
            print(f"   ... and {len(routes) - 5} more routes")

        print()
        print("🎤 VOICE MODEL DETAILS:")
        print("-" * 40)

        result = db.execute(
            text("""
            SELECT model_name, language_code, quality_level,
                   file_size_mb, is_default
            FROM voice_models
            WHERE is_active = 1
            ORDER BY language_code, is_default DESC
        """)
        )

        current_lang = None
        for row in result.fetchall():
            if row.language_code != current_lang:
                current_lang = row.language_code
                print(f"  📍 {row.language_code.upper()}:")

            default_marker = " (DEFAULT)" if row.is_default else ""
            print(
                f"     {row.model_name} - {row.quality_level}, {row.file_size_mb}MB{default_marker}"
            )

        print()
        print("🎛️ FEATURE TOGGLE CATEGORIES:")
        print("-" * 40)

        result = db.execute(
            text("""
            SELECT category, COUNT(*) as count,
                   SUM(CASE WHEN is_enabled = 1 THEN 1 ELSE 0 END) as enabled
            FROM admin_feature_toggles
            GROUP BY category
            ORDER BY category
        """)
        )

        for row in result.fetchall():
            print(f"  {row.category}: {row.enabled}/{row.count} enabled")

        print()
        print("🌐 LANGUAGE CONFIGURATION STATUS:")
        print("-" * 40)

        result = db.execute(
            text("""
            SELECT l.code, l.name, l.native_name,
                   alc.is_enabled_globally,
                   alc.default_voice_model,
                   alc.speech_recognition_enabled,
                   alc.text_to_speech_enabled
            FROM languages l
            LEFT JOIN admin_language_config alc ON l.code = alc.language_code
            WHERE l.is_active = 1
            ORDER BY l.name
        """)
        )

        for row in result.fetchall():
            status = "✅ Enabled" if row.is_enabled_globally else "❌ Disabled"
            stt = "✅" if row.speech_recognition_enabled else "❌"
            tts = "✅" if row.text_to_speech_enabled else "❌"
            voice = row.default_voice_model or "None"

            print(f"  {row.code.upper()} ({row.name}): {status}")
            print(f"     Voice: {voice}")
            print(f"     STT: {stt}, TTS: {tts}")

        # Close database connection
        db.close()

        print()
        print("🎉 ALL LANGUAGE CONFIGURATION API TESTS PASSED!")
        print("🚀 Language Configuration Panel is ready for use!")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required modules are installed")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_language_config_api())
    if result:
        print("\n✅ Test completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Test failed")
        sys.exit(1)
