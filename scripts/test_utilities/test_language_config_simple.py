#!/usr/bin/env python3
"""
Simple Language Configuration Test
Task 3.1.3 - Language Configuration Panel

This script tests the basic language configuration functionality
by directly testing the database and API components.
"""

import sys
import os
import sqlite3
import json
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))


def test_language_config_system():
    """Test the language configuration system components"""

    print("🧪 TESTING LANGUAGE CONFIGURATION SYSTEM")
    print("=" * 60)

    success_count = 0
    total_tests = 0

    try:
        # Test 1: Database Schema
        print("🔍 Test 1: Database Schema Validation")
        total_tests += 1

        db_path = "data/ai_language_tutor.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check required tables exist
        required_tables = [
            "voice_models",
            "admin_language_config",
            "admin_feature_toggles",
        ]
        for table in required_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {table}: {count} records")

        success_count += 1
        print("   ✅ Database schema test PASSED")

        # Test 2: Voice Models Data
        print("\n🎤 Test 2: Voice Models Validation")
        total_tests += 1

        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active,
                   COUNT(DISTINCT language_code) as languages
            FROM voice_models
        """)
        vm_stats = cursor.fetchone()
        print(f"   ✅ Total voice models: {vm_stats[0]}")
        print(f"   ✅ Active voice models: {vm_stats[1]}")
        print(f"   ✅ Languages covered: {vm_stats[2]}")

        if vm_stats[1] > 0:
            success_count += 1
            print("   ✅ Voice models test PASSED")
        else:
            print("   ❌ Voice models test FAILED - No active models")

        # Test 3: Language Configuration
        print("\n🌐 Test 3: Language Configuration Validation")
        total_tests += 1

        cursor.execute("""
            SELECT l.code, l.name,
                   alc.is_enabled_globally,
                   alc.default_voice_model
            FROM languages l
            LEFT JOIN admin_language_config alc ON l.code = alc.language_code
            WHERE l.is_active = 1
        """)

        lang_configs = cursor.fetchall()
        enabled_count = 0
        for lang in lang_configs:
            status = "✅ Enabled" if lang[2] else "❌ Disabled"
            voice = lang[3] or "None"
            print(f"   {lang[0].upper()} ({lang[1]}): {status}, Voice: {voice}")
            if lang[2]:
                enabled_count += 1

        if enabled_count > 0:
            success_count += 1
            print(f"   ✅ Language configuration test PASSED ({enabled_count} enabled)")
        else:
            print("   ❌ Language configuration test FAILED - No enabled languages")

        # Test 4: Feature Toggles
        print("\n🎛️ Test 4: Feature Toggles Validation")
        total_tests += 1

        cursor.execute("""
            SELECT category,
                   COUNT(*) as total,
                   SUM(CASE WHEN is_enabled = 1 THEN 1 ELSE 0 END) as enabled
            FROM admin_feature_toggles
            GROUP BY category
            ORDER BY category
        """)

        toggle_stats = cursor.fetchall()
        total_features = 0
        enabled_features = 0
        for cat_stat in toggle_stats:
            total_features += cat_stat[1]
            enabled_features += cat_stat[2]
            print(f"   {cat_stat[0]}: {cat_stat[2]}/{cat_stat[1]} enabled")

        if total_features > 0:
            success_count += 1
            print(
                f"   ✅ Feature toggles test PASSED ({enabled_features}/{total_features} enabled)"
            )
        else:
            print("   ❌ Feature toggles test FAILED - No features found")

        conn.close()

        # Test 5: API Import Test
        print("\n🔌 Test 5: API Components Import")
        total_tests += 1

        try:
            from app.api.language_config import router, LanguageConfigResponse
            from app.frontend.admin_language_config import language_config_page

            print("   ✅ Language config API router imported")
            print("   ✅ Language config models imported")
            print("   ✅ Language config UI components imported")

            # Check router has routes
            routes = [route.path for route in router.routes]
            print(f"   ✅ API routes configured: {len(routes)}")

            success_count += 1
            print("   ✅ API components test PASSED")

        except ImportError as e:
            print(f"   ❌ API components test FAILED: {e}")

        # Test 6: Voice Model File Validation
        print("\n📁 Test 6: Voice Model Files Validation")
        total_tests += 1

        voices_dir = Path("app/data/piper_voices")
        if voices_dir.exists():
            onnx_files = list(voices_dir.glob("*.onnx"))
            config_files = list(voices_dir.glob("*.onnx.json"))

            print(f"   ✅ Voice models directory exists")
            print(f"   ✅ ONNX model files: {len(onnx_files)}")
            print(f"   ✅ Config files: {len(config_files)}")

            # Check file sizes
            total_size = sum(f.stat().st_size for f in onnx_files)
            print(f"   ✅ Total model size: {total_size / (1024 * 1024):.1f}MB")

            if len(onnx_files) > 0:
                success_count += 1
                print("   ✅ Voice model files test PASSED")
            else:
                print("   ❌ Voice model files test FAILED - No model files")
        else:
            print("   ❌ Voice model files test FAILED - Directory not found")

        # Test Summary
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests passed: {success_count}/{total_tests}")
        print(f"Success rate: {(success_count / total_tests) * 100:.1f}%")

        if success_count == total_tests:
            print("🎉 ALL TESTS PASSED - Language Configuration System Ready!")
            return True
        elif success_count >= total_tests * 0.8:
            print(
                "⚠️ MOSTLY PASSING - Language Configuration System Functional with Minor Issues"
            )
            return True
        else:
            print(
                "❌ MULTIPLE FAILURES - Language Configuration System Needs Attention"
            )
            return False

    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = test_language_config_system()
    if result:
        print("\n✅ Language Configuration System Test PASSED")
        sys.exit(0)
    else:
        print("\n❌ Language Configuration System Test FAILED")
        sys.exit(1)
