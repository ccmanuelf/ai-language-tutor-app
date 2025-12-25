#!/usr/bin/env python3
"""Test DeepSeek API with correct model name"""

import sys
import asyncio
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_deepseek_only():
    try:
        from app.services.ai_router import ai_router

        print("🧪 TESTING DEEPSEEK WITH CORRECT MODEL NAME")
        print("=" * 50)

        # Get qwen service (which now supports DeepSeek)
        qwen_service = ai_router.providers.get("qwen")
        if not qwen_service:
            print("❌ Qwen service not found")
            return False

        print(f"Service available: {qwen_service.is_available}")

        # Test JSON request
        test_prompt = """
        Analyze this content: "Python is a programming language"

        Return ONLY a valid JSON object with this structure:
        {
            "topics": ["topic1", "topic2"],
            "difficulty_level": "beginner",
            "key_concepts": ["concept1", "concept2"],
            "detected_language": "en"
        }
        """

        messages = [{"role": "user", "content": test_prompt}]

        print("Making DeepSeek API call...")
        response = await asyncio.wait_for(
            qwen_service.generate_response(
                messages=messages, language="en", max_tokens=200, temperature=0.1
            ),
            timeout=30,
        )

        print(f"Status: {response.status}")
        print(f"Model: {response.model}")
        print(f"Cost: ${response.cost}")
        print(f"Content preview: {repr(response.content[:200])}")

        # Try JSON parsing
        try:
            parsed = json.loads(response.content)
            print(f"✅ JSON VALID: {parsed}")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ JSON INVALID: {e}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_deepseek_only())
    print(f"\n🎯 DeepSeek test result: {'SUCCESS' if result else 'FAILED'}")
