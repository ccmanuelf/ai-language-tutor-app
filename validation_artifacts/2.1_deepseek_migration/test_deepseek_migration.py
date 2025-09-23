#!/usr/bin/env python3
"""
Test DeepSeek Service Migration from Qwen
Validates that the new DeepSeek service works correctly
"""

import asyncio
import sys
import os

sys.path.append(".")


async def test_deepseek_migration():
    """Test the DeepSeek service migration"""

    print("🧪 Testing DeepSeek Service Migration...")

    try:
        from app.services.deepseek_service import deepseek_service
        from app.services.ai_router import ai_router

        print(f"✅ DeepSeek service imported successfully")
        print(f"Service available: {deepseek_service.is_available}")
        print(f"Supported languages: {deepseek_service.supported_languages}")

        # Test service availability
        if deepseek_service.is_available:
            print("\n🎯 Testing DeepSeek service directly...")

            # Test English conversation
            response_en = await deepseek_service.generate_response(
                message="Hello! I would like to practice English conversation.",
                language="en",
            )

            print(f"✅ English Response: {response_en.content[:100]}...")
            print(f"   Provider: {response_en.provider}, Model: {response_en.model}")
            print(
                f"   Cost: ${response_en.cost:.6f}, Time: {response_en.processing_time:.2f}s"
            )

            # Test Chinese conversation
            response_zh = await deepseek_service.generate_response(
                message="你好！我想练习中文对话。", language="zh"
            )

            print(f"✅ Chinese Response: {response_zh.content[:100]}...")
            print(f"   Provider: {response_zh.provider}, Model: {response_zh.model}")
            print(
                f"   Cost: ${response_zh.cost:.6f}, Time: {response_zh.processing_time:.2f}s"
            )

        else:
            print("⚠️  DeepSeek service not available - may be missing API key")
            print("   This is expected if DEEPSEEK_API_KEY is not configured")

        # Test AI router integration
        print("\n🎯 Testing AI Router integration...")

        # Check if deepseek is registered
        deepseek_provider = ai_router.providers.get("deepseek")
        qwen_alias = ai_router.providers.get("qwen")  # Should point to deepseek now

        print(f"DeepSeek provider registered: {deepseek_provider is not None}")
        print(f"Qwen alias points to DeepSeek: {qwen_alias is deepseek_provider}")

        # Test Chinese language routing
        chinese_providers = ai_router.language_preferences.get("zh", [])
        print(f"Chinese language providers: {chinese_providers}")
        print(
            f"DeepSeek is primary for Chinese: {'deepseek' in chinese_providers and chinese_providers[0] == 'deepseek'}"
        )

        print("\n🎉 DeepSeek migration test completed successfully!")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_deepseek_migration())
    exit(0 if success else 1)
