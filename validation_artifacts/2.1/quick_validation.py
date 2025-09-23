#!/usr/bin/env python3
"""
Quick Task 2.1 Validation - Essential Components Check
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_essential_components():
    """Test that essential components exist and can be imported"""
    results = []

    # Test 1: Content Processor Service
    try:
        from app.services.content_processor import (
            content_processor,
            ContentType,
            LearningMaterialType,
        )

        results.append(("✅", "Content processor service imported"))
    except Exception as e:
        results.append(("❌", f"Content processor import failed: {e}"))

    # Test 2: API Endpoints
    try:
        from app.api.content import router

        results.append(("✅", "Content API router imported"))
    except Exception as e:
        results.append(("❌", f"Content API import failed: {e}"))

    # Test 3: Frontend Integration
    try:
        home_file = Path("app/frontend/home.py")
        if home_file.exists():
            content = home_file.read_text()
            if "showContentProcessingModal" in content:
                results.append(("✅", "Frontend processing modals integrated"))
            else:
                results.append(("❌", "Frontend missing processing modals"))
        else:
            results.append(("❌", "Home frontend file not found"))
    except Exception as e:
        results.append(("❌", f"Frontend check failed: {e}"))

    # Test 4: Content View Page
    try:
        content_view_file = Path("app/frontend/content_view.py")
        if content_view_file.exists():
            results.append(("✅", "Content view page exists"))
        else:
            results.append(("❌", "Content view page missing"))
    except Exception as e:
        results.append(("❌", f"Content view check failed: {e}"))

    return results


def main():
    print("🚀 QUICK TASK 2.1 VALIDATION")
    print("=" * 50)

    results = test_essential_components()

    passed = 0
    total = len(results)

    for status, message in results:
        print(f"{status} {message}")
        if status == "✅":
            passed += 1

    print(f"\n📊 Results: {passed}/{total} tests passed ({passed / total * 100:.1f}%)")

    if passed == total:
        print("🎉 Essential components are working!")
        return True
    else:
        print("⚠️ Some components need attention")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
