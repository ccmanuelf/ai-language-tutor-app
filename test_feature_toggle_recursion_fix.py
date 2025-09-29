#!/usr/bin/env python3
"""
Test to reproduce and fix the Feature Toggle Service recursion issue
Task 3.1.7 - Fix recursion issue to achieve 100% success rate
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_recursion_issue():
    """Test to reproduce and fix the recursion issue"""
    print("🔍 TESTING FEATURE TOGGLE SERVICE RECURSION FIX")
    print("=" * 60)

    try:
        # Import the service
        from app.services.feature_toggle_service import (
            get_feature_toggle_service,
            FeatureToggleService,
        )

        print("✅ Successfully imported FeatureToggleService")

        # Test direct service creation
        print("\n📋 Testing direct service instantiation...")
        service = FeatureToggleService()
        await service.initialize()
        print("✅ Direct service instantiation successful")

        # Test global service getter
        print("\n📋 Testing global service getter...")
        global_service = await get_feature_toggle_service()
        print("✅ Global service getter successful")

        # Test feature creation
        print("\n📋 Testing feature operations...")
        features = await global_service.get_all_features()
        print(f"✅ Retrieved {len(features)} features")

        print("\n🎉 ALL RECURSION TESTS PASSED!")
        return True

    except RecursionError as e:
        print(f"❌ RECURSION ERROR DETECTED: {e}")
        print("\n🔧 ANALYZING RECURSION...")

        # Let's analyze the recursion issue
        import traceback

        traceback.print_exc()

        return False

    except Exception as e:
        print(f"❌ OTHER ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_recursion_issue())
    if result:
        print(
            "\n✅ Feature Toggle Service is working correctly - no recursion issue found!"
        )
    else:
        print("\n❌ Recursion issue confirmed - needs fixing")
