#!/usr/bin/env python3
"""
Functional Verification Test
Verify that the core AI Language Tutor functionality actually works end-to-end.
"""

import asyncio
import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent))


async def test_ai_router_functionality():
    """Test that AI router can actually generate responses"""

    print("🤖 Testing AI Router Actual Functionality")
    print("=" * 60)

    tests_passed = 0
    tests_total = 0

    # Test 1: AI Router Provider Selection
    tests_total += 1
    try:
        from app.services.ai_router import ai_router

        # Test provider selection
        selection = await ai_router.select_provider(language="en")
        assert selection is not None
        assert hasattr(selection, "provider_name")
        assert hasattr(selection, "model_name")

        print(
            f"✅ Test 1: AI router selected provider: {selection.provider_name} with model: {selection.model_name}"
        )
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1: AI router provider selection failed: {e}")

    # Test 2: Generate AI Response (Mock Mode)
    tests_total += 1
    try:
        from app.services.ai_router import generate_ai_response

        test_messages = [
            {"role": "user", "content": "Hello, can you help me learn English?"}
        ]

        # This should work even in mock mode
        response = await generate_ai_response(messages=test_messages, language="en")

        assert response is not None
        assert hasattr(response, "content")
        assert hasattr(response, "provider")
        assert len(response.content) > 0

        print(
            f"✅ Test 2: Generated response from {response.provider}: '{response.content[:50]}...'"
        )
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2: AI response generation failed: {e}")

    # Test 3: Budget Management Integration
    tests_total += 1
    try:
        from app.services.budget_manager import budget_manager

        # Check budget status
        status = budget_manager.get_current_budget_status()
        assert status is not None
        assert hasattr(status, "current_spend")
        assert hasattr(status, "remaining_budget")

        print(
            f"✅ Test 3: Budget status - Spend: ${status.current_spend:.2f}, Remaining: ${status.remaining_budget:.2f}"
        )
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 3: Budget management failed: {e}")

    # Test 4: Fallback System
    tests_total += 1
    try:
        # Force fallback to Ollama
        selection = await ai_router.select_provider(language="en", force_local=True)
        assert selection.provider_name == "ollama"
        assert selection.is_fallback == True

        print("✅ Test 4: Fallback system working - will use Ollama when needed")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 4: Fallback system failed: {e}")

    return tests_passed, tests_total


async def test_conversation_functionality():
    """Test actual conversation management functionality"""

    print("\n💬 Testing Conversation Management Actual Functionality")
    print("=" * 60)

    tests_passed = 0
    tests_total = 0

    # Test 1: Start Real Conversation
    tests_total += 1
    try:
        from app.services.conversation_manager import conversation_manager
        from app.services.conversation_models import LearningFocus

        conversation_id = await conversation_manager.start_conversation(
            user_id="test-user-123",
            language="en",
            learning_focus=LearningFocus.CONVERSATION,
            topic="Daily Life",
        )

        assert conversation_id is not None
        assert len(conversation_id) > 0

        print(f"✅ Test 1: Started conversation: {conversation_id}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1: Conversation start failed: {e}")
        conversation_id = None

    # Test 2: Send Message and Get Response
    tests_total += 1
    try:
        if conversation_id:
            from app.services.conversation_manager import send_learning_message

            response = await send_learning_message(
                conversation_id=conversation_id,
                user_message="Hello! I want to practice English conversation.",
                user_id="test-user-123",
            )

            assert response is not None
            assert hasattr(response, "content")
            assert len(response.content) > 0

            print(f"✅ Test 2: Got conversation response: '{response.content[:50]}...'")
            tests_passed += 1
        else:
            print("⏭️  Test 2: Skipped - no conversation ID")
    except Exception as e:
        print(f"❌ Test 2: Conversation messaging failed: {e}")

    # Test 3: Conversation History
    tests_total += 1
    try:
        if conversation_id:
            history = await conversation_manager.get_conversation_history(
                conversation_id
            )
            assert isinstance(history, list)
            assert len(history) > 0

            print(
                f"✅ Test 3: Retrieved conversation history with {len(history)} messages"
            )
            tests_passed += 1
        else:
            print("⏭️  Test 3: Skipped - no conversation ID")
    except Exception as e:
        print(f"❌ Test 3: Conversation history failed: {e}")

    # Test 4: Learning Insights
    tests_total += 1
    try:
        if conversation_id:
            insights = await conversation_manager.generate_learning_insights(
                conversation_id
            )
            assert insights is not None
            assert "vocabulary_used" in insights
            assert "learning_progress" in insights

            print("✅ Test 4: Generated learning insights successfully")
            tests_passed += 1
        else:
            print("⏭️  Test 4: Skipped - no conversation ID")
    except Exception as e:
        print(f"❌ Test 4: Learning insights failed: {e}")

    return tests_passed, tests_total


async def test_speech_pipeline_functionality():
    """Test actual speech processing functionality"""

    print("\n🎤 Testing Speech Processing Actual Functionality")
    print("=" * 60)

    tests_passed = 0
    tests_total = 0

    # Test 1: Speech Pipeline Status
    tests_total += 1
    try:
        from app.services.speech_processor import speech_processor

        status = await speech_processor.get_speech_pipeline_status()
        assert status is not None
        assert "status" in status

        print("✅ Test 1: Speech pipeline status retrieved successfully")
        print(f"   Overall status: {status.get('status', 'unknown')}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1: Speech pipeline status failed: {e}")

    # Test 2: Text-to-Speech Processing
    tests_total += 1
    try:
        result = await speech_processor.process_text_to_speech(
            text="Hello, this is a test of text to speech functionality.", language="en"
        )

        assert result is not None
        assert hasattr(result, "audio_data")
        assert hasattr(result, "language")
        assert result.language == "en"

        print("✅ Test 2: Text-to-speech processing completed")
        print(
            f"   Audio duration: {getattr(result, 'duration_seconds', 'unknown')} seconds"
        )
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2: Text-to-speech failed: {e}")

    # Test 3: Speech-to-Text Processing
    tests_total += 1
    try:
        # Use mock audio data for testing
        mock_audio = b"mock_audio_data" * 100

        (
            recognition_result,
            pronunciation_analysis,
        ) = await speech_processor.process_speech_to_text(
            audio_data=mock_audio, language="en", enable_pronunciation_analysis=True
        )

        assert recognition_result is not None
        assert hasattr(recognition_result, "transcript")
        assert hasattr(recognition_result, "confidence")

        print("✅ Test 3: Speech-to-text processing completed")
        print(f"   Transcript: '{recognition_result.transcript}'")
        print(f"   Confidence: {recognition_result.confidence}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 3: Speech-to-text failed: {e}")

    # Test 4: Pronunciation Analysis
    tests_total += 1
    try:
        mock_audio = b"test_pronunciation_audio" * 50

        analysis = await speech_processor.analyze_pronunciation_quality(
            user_audio=mock_audio, reference_text="Hello world", language="en"
        )

        assert analysis is not None
        assert hasattr(analysis, "overall_score")
        assert hasattr(analysis, "pronunciation_level")

        print("✅ Test 4: Pronunciation analysis completed")
        print(f"   Overall score: {analysis.overall_score}")
        print(f"   Level: {analysis.pronunciation_level}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 4: Pronunciation analysis failed: {e}")

    return tests_passed, tests_total


async def test_integration_end_to_end():
    """Test end-to-end integration"""

    print("\n🔗 Testing End-to-End Integration")
    print("=" * 60)

    tests_passed = 0
    tests_total = 0

    # Test 1: Complete Learning Session Simulation
    tests_total += 1
    try:
        from app.services.conversation_manager import conversation_manager
        from app.services.conversation_models import LearningFocus
        from app.services.ai_router import generate_ai_response

        # Start learning session
        conversation_id = await conversation_manager.start_conversation(
            user_id="integration-test-user",
            language="en",
            learning_focus=LearningFocus.CONVERSATION,
            topic="Travel",
        )

        # Simulate user interaction
        user_message = "I want to learn how to ask for directions when traveling."

        # Get AI response
        messages = [{"role": "user", "content": user_message}]
        ai_response = await generate_ai_response(messages, language="en")

        # Add to conversation history
        await conversation_manager._add_message(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            language="en",
        )

        await conversation_manager._add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response.content,
            language="en",
        )

        # Generate learning summary
        summary = await conversation_manager.get_conversation_summary(conversation_id)

        assert summary is not None
        assert "learning_progress" in summary

        print("✅ Test 1: Complete learning session simulation successful")
        print(
            f"   Conversation: {len(summary.get('session_stats', {}).get('total_messages', 0))} messages"
        )
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1: End-to-end integration failed: {e}")

    # Test 2: Multi-Component Integration
    tests_total += 1
    try:
        from app.services.budget_manager import budget_manager
        from app.services.speech_processor import speech_processor

        # Check all components can work together
        budget_status = budget_manager.get_current_budget_status()
        speech_status = await speech_processor.get_speech_pipeline_status()

        assert budget_status is not None
        assert speech_status is not None

        print("✅ Test 2: Multi-component integration working")
        print(f"   Budget remaining: ${budget_status.remaining_budget:.2f}")
        print(f"   Speech pipeline: {speech_status.get('status', 'unknown')}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2: Multi-component integration failed: {e}")

    return tests_passed, tests_total


async def main():
    """Main functional verification test"""

    print("🧪 FUNCTIONAL VERIFICATION TEST")
    print("Testing actual functionality beyond structural validation")
    print("=" * 70)

    total_passed = 0
    total_tests = 0

    # Run all functional tests
    ai_passed, ai_total = await test_ai_router_functionality()
    total_passed += ai_passed
    total_tests += ai_total

    conv_passed, conv_total = await test_conversation_functionality()
    total_passed += conv_passed
    total_tests += conv_total

    speech_passed, speech_total = await test_speech_pipeline_functionality()
    total_passed += speech_passed
    total_tests += speech_total

    int_passed, int_total = await test_integration_end_to_end()
    total_passed += int_passed
    total_tests += int_total

    # Final Summary
    print("\n" + "=" * 70)
    print("🎯 FUNCTIONAL VERIFICATION SUMMARY")
    print("=" * 70)

    success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0

    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_tests - total_passed}")
    print(f"🎯 Success Rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print("\n🎉 FUNCTIONAL VERIFICATION PASSED!")
        print("✨ Core functionality is working correctly")
        return True
    else:
        print("\n⚠️  FUNCTIONAL VERIFICATION NEEDS ATTENTION")
        print("💡 Some core functionality requires fixes")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
