#!/usr/bin/env python3
"""
Watson Deprecation Validation Test Script
Tests that Watson services are properly deprecated and Mistral+Piper are primary

Task: 2A.4 - Watson Deprecation & Cleanup
Date: September 22, 2025
"""

import sys
import os
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_watson_imports_removed():
    """Test that Watson imports are removed from speech processor"""
    print("🧪 Testing Watson imports removal...")

    try:
        # Read speech processor file
        speech_file = project_root / "app" / "services" / "speech_processor.py"
        content = speech_file.read_text()

        # Check for Watson import statements
        watson_imports = [
            "from ibm_watson import",
            "import ibm_watson",
            "from ibm_cloud_sdk_core import",
        ]

        for import_line in watson_imports:
            if (
                import_line in content
                and not "REMOVED" in content.split(import_line)[0].split("\n")[-1]
            ):
                print(f"❌ FAIL: Watson import still present: {import_line}")
                return False

        print("✅ PASS: Watson imports properly removed")
        return True

    except Exception as e:
        print(f"❌ FAIL: Error checking imports: {e}")
        return False


def test_watson_configuration_removed():
    """Test that Watson configuration is removed from config.py"""
    print("🧪 Testing Watson configuration removal...")

    try:
        # Read config file
        config_file = project_root / "app" / "core" / "config.py"
        content = config_file.read_text()

        # Check for Watson configuration fields
        watson_fields = [
            "IBM_WATSON_STT_API_KEY",
            "IBM_WATSON_TTS_API_KEY",
            "IBM_WATSON_STT_URL",
            "IBM_WATSON_TTS_URL",
        ]

        for field in watson_fields:
            # Allow if it's in a comment explaining removal
            lines = content.split("\n")
            for line in lines:
                if field in line and not line.strip().startswith("#"):
                    print(f"❌ FAIL: Watson config field still active: {field}")
                    return False

        print("✅ PASS: Watson configuration properly removed")
        return True

    except Exception as e:
        print(f"❌ FAIL: Error checking config: {e}")
        return False


def test_watson_dependencies_removed():
    """Test that Watson dependencies are removed from requirements.txt"""
    print("🧪 Testing Watson dependencies removal...")

    try:
        # Read requirements file
        req_file = project_root / "requirements.txt"
        content = req_file.read_text()

        # Check for Watson dependencies
        watson_deps = ["ibm-watson==", "ibm-cloud-sdk-core=="]

        for dep in watson_deps:
            lines = content.split("\n")
            for line in lines:
                if dep in line and not line.strip().startswith("#"):
                    print(f"❌ FAIL: Watson dependency still active: {dep}")
                    return False

        print("✅ PASS: Watson dependencies properly removed")
        return True

    except Exception as e:
        print(f"❌ FAIL: Error checking requirements: {e}")
        return False


def test_provider_selection_deprecation():
    """Test that provider selection properly rejects Watson"""
    print("🧪 Testing provider selection deprecation...")

    try:
        # Read speech processor file
        speech_file = project_root / "app" / "services" / "speech_processor.py"
        content = speech_file.read_text()

        # Check for proper Watson deprecation messages
        expected_patterns = [
            "Watson STT deprecated",
            "Watson TTS deprecated",
            "use 'auto' or 'mistral'",
            "use 'auto' or 'piper'",
        ]

        found_patterns = 0
        for pattern in expected_patterns:
            if pattern in content:
                found_patterns += 1

        if found_patterns < 3:  # At least 3 patterns should be present
            print(
                f"❌ FAIL: Insufficient deprecation messages found ({found_patterns}/4)"
            )
            return False

        print("✅ PASS: Provider selection properly rejects Watson")
        return True

    except Exception as e:
        print(f"❌ FAIL: Error checking provider selection: {e}")
        return False


def test_env_example_updated():
    """Test that .env.example is updated to reflect Watson deprecation"""
    print("🧪 Testing .env.example updates...")

    try:
        # Read .env.example file
        env_file = project_root / ".env.example"
        content = env_file.read_text()

        # Check that Watson variables are commented or removed
        watson_vars = [
            "IBM_WATSON_STT_API_KEY=",
            "IBM_WATSON_TTS_API_KEY=",
            "IBM_WATSON_STT_URL=",
            "IBM_WATSON_TTS_URL=",
        ]

        for var in watson_vars:
            lines = content.split("\n")
            for line in lines:
                if var in line and not line.strip().startswith("#"):
                    print(f"❌ FAIL: Watson env var still active: {var}")
                    return False

        # Check for deprecation notice
        if "deprecated" not in content.lower() or "phase 2a" not in content.lower():
            print("❌ FAIL: No deprecation notice found in .env.example")
            return False

        print("✅ PASS: .env.example properly updated")
        return True

    except Exception as e:
        print(f"❌ FAIL: Error checking .env.example: {e}")
        return False


def test_watson_availability_flags():
    """Test that Watson availability flags are set to False"""
    print("🧪 Testing Watson availability flags...")

    try:
        # Read speech processor file
        speech_file = project_root / "app" / "services" / "speech_processor.py"
        content = speech_file.read_text()

        # Check for Watson availability being set to False
        required_flags = [
            "self.watson_stt_available = False",
            "self.watson_tts_available = False",
            "self.watson_sdk_available = False",
        ]

        for flag in required_flags:
            if flag not in content:
                print(f"❌ FAIL: Watson flag not set to False: {flag}")
                return False

        print("✅ PASS: Watson availability flags properly set to False")
        return True

    except Exception as e:
        print(f"❌ FAIL: Error checking availability flags: {e}")
        return False


def main():
    """Run all Watson deprecation validation tests"""
    print("🔒 WATSON DEPRECATION VALIDATION TESTS")
    print("=" * 50)
    print("Task: 2A.4 - Watson Deprecation & Cleanup")
    print("Date: September 22, 2025")
    print("=" * 50)

    tests = [
        test_watson_imports_removed,
        test_watson_configuration_removed,
        test_watson_dependencies_removed,
        test_provider_selection_deprecation,
        test_env_example_updated,
        test_watson_availability_flags,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ FAIL: Test {test.__name__} crashed: {e}")
            print(traceback.format_exc())
            print()

    print("=" * 50)
    print(f"🎯 WATSON DEPRECATION TEST RESULTS")
    print(f"Passed: {passed}/{total} tests")

    if passed == total:
        print("✅ ALL TESTS PASSED: Watson deprecation complete!")
        print("🎉 Task 2A.4 validation successful")
        return True
    else:
        print("❌ SOME TESTS FAILED: Watson deprecation incomplete")
        print("🚨 Fix failing tests before completing Task 2A.4")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
