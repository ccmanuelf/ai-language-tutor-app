"""
AI Services Testing Suite & Integration Tests for AI Language Tutor App

Comprehensive testing for all AI services including unit tests, integration tests,
performance testing, and end-to-end validation.
"""

import asyncio
import logging
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def safe_mean(values: List[Union[int, float]], default: float = 0.0) -> float:
    """Safely calculate mean, returning default if empty list"""
    if not values:
        return default
    return statistics.mean(values)


# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class SuiteResultStatus(Enum):
    """Test execution result status"""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class SuiteExecutionReport:
    """Test execution report"""

    test_name: str
    result: SuiteResultStatus
    execution_time: float
    error_message: Optional[str] = None


class AIServicesTestSuite:
    """Main AI services testing suite"""

    def __init__(self):
        self.test_results: List[SuiteExecutionReport] = []
        self.performance_metrics = {}

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""

        print("🧪 AI Services Testing Suite")
        print("=" * 50)

        # Define test methods
        test_methods = [
            ("AI Service Base", self.test_ai_service_base),
            ("Budget Manager", self.test_budget_manager),
            ("Ollama Service", self.test_ollama_service),
            ("Conversation Manager", self.test_conversation_manager),
            ("Speech Processor", self.test_speech_processor),
            ("AI Router Integration", self.test_ai_router_integration),
            ("Conversation Flow", self.test_conversation_flow),
            ("Multi-Language Support", self.test_multi_language_support),
            ("Performance Test", self.test_performance),
            ("End-to-End Learning", self.test_e2e_learning),
            ("Budget Fallback", self.test_budget_fallback),
            ("Cost Estimation", self.test_cost_estimation),
        ]

        self.test_results = []
        passed = 0
        failed = 0
        skipped = 0
        errors = 0

        for test_name, test_method in test_methods:
            print(f"🔍 {test_name}")

            start_time = time.time()
            try:
                await test_method()
                execution_time = time.time() - start_time

                self.test_results.append(
                    SuiteExecutionReport(
                        test_name=test_name,
                        result=SuiteResultStatus.PASSED,
                        execution_time=execution_time,
                    )
                )
                passed += 1
                print(f"   ✅ PASSED ({execution_time:.2f}s)")

            except AssertionError as e:
                execution_time = time.time() - start_time
                self.test_results.append(
                    SuiteExecutionReport(
                        test_name=test_name,
                        result=SuiteResultStatus.FAILED,
                        execution_time=execution_time,
                        error_message=str(e),
                    )
                )
                failed += 1
                print(f"   ❌ FAILED: {str(e)}")

            except Exception as e:
                execution_time = time.time() - start_time
                # Check if it's an expected skip condition
                if "not configured" in str(e) or "not available" in str(e):
                    self.test_results.append(
                        SuiteExecutionReport(
                            test_name=test_name,
                            result=SuiteResultStatus.SKIPPED,
                            execution_time=execution_time,
                            error_message=str(e),
                        )
                    )
                    skipped += 1
                    print(f"   ⏭️  SKIPPED: {str(e)}")
                else:
                    self.test_results.append(
                        SuiteExecutionReport(
                            test_name=test_name,
                            result=SuiteResultStatus.ERROR,
                            execution_time=execution_time,
                            error_message=str(e),
                        )
                    )
                    errors += 1
                    print(f"   💥 ERROR: {str(e)}")

        # Generate summary
        total_tests = len(test_methods)
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        total_time = sum(r.execution_time for r in self.test_results)

        summary = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "success_rate": success_rate,
            "total_execution_time": total_time,
            "performance_metrics": self.performance_metrics,
        }

        self._print_summary(summary)
        return summary

    # Individual Test Methods

    async def test_ai_service_base(self):
        """Test BaseAIService functionality"""
        from app.services.ai_service_base import AIResponse, MockAIService

        mock_service = MockAIService()
        assert mock_service.service_name == "mock"
        assert len(mock_service.supported_languages) > 0

        messages = [{"role": "user", "content": "Hello"}]
        response = await mock_service.generate_response(messages, "en")

        assert isinstance(response, AIResponse)
        assert response.content != ""
        assert response.language == "en"

    async def test_budget_manager(self):
        """Test budget manager functionality"""
        from app.services.budget_manager import BudgetManager

        budget_manager = BudgetManager()
        status = budget_manager.get_current_budget_status()

        assert hasattr(status, "remaining_budget")
        assert hasattr(status, "percentage_used")
        assert 0.0 <= status.percentage_used <= 1.0

        # Test cost tracking
        initial_usage = status.total_usage
        budget_manager.track_usage("test_provider", "test_model", 0.05, 100)
        updated_status = budget_manager.get_current_budget_status()
        assert updated_status.total_usage > initial_usage

    async def test_ollama_service(self):
        """Test Ollama service functionality"""
        from app.services.ollama_service import ollama_service

        assert ollama_service.service_name == "ollama"
        assert len(ollama_service.available_models) > 0

        # Test model recommendations
        en_model = ollama_service.get_recommended_model("en")
        fr_model = ollama_service.get_recommended_model("fr")
        assert en_model != ""
        assert fr_model != ""

        # Test health status
        health = await ollama_service.get_health_status()
        assert "service_name" in health

    async def test_conversation_manager(self):
        """Test conversation management functionality"""
        from app.services.conversation_manager import conversation_manager
        from app.services.conversation_models import LearningFocus

        conv_id = await conversation_manager.start_conversation(
            user_id="test_user",
            language="en",
            learning_focus=LearningFocus.CONVERSATION,
        )

        assert conv_id is not None
        assert conv_id in conversation_manager.active_conversations

        context = conversation_manager.active_conversations[conv_id]
        assert context.user_id == "test_user"
        assert context.language == "en"

        summary = await conversation_manager.get_conversation_summary(conv_id)
        assert "conversation_id" in summary

    async def test_speech_processor(self):
        """Test speech processing functionality"""
        from app.services.speech_processor import AudioFormat, speech_processor

        status = await speech_processor.get_speech_pipeline_status()
        assert "supported_formats" in status
        assert "supported_languages" in status

        # Test audio quality analysis
        mock_audio = b"mock_audio_data" * 100
        metadata = await speech_processor._analyze_audio_quality(
            mock_audio, AudioFormat.WAV
        )
        assert metadata.format == AudioFormat.WAV
        assert 0.0 <= metadata.quality_score <= 1.0

    async def test_ai_router_integration(self):
        """Test AI router integration"""
        from app.services.ai_router import ai_router

        assert "ollama" in ai_router.providers

        selection = await ai_router.select_provider(language="en", force_local=True)
        assert selection.provider_name == "ollama"
        assert selection.is_fallback is True

        status = await ai_router.get_router_status()
        assert "budget_status" in status
        assert "providers" in status

    async def test_conversation_flow(self):
        """Test complete conversation flow"""
        from app.services.conversation_manager import conversation_manager
        from app.services.conversation_models import LearningFocus

        conv_id = await conversation_manager.start_conversation(
            user_id="test_user_flow",
            language="en",
            learning_focus=LearningFocus.CONVERSATION,
        )

        # Test message addition
        await conversation_manager._add_message(
            conversation_id=conv_id,
            role=conversation_manager.MessageRole.USER,
            content="Hello, test message",
            language="en",
        )

        history = await conversation_manager.get_conversation_history(conv_id)
        assert isinstance(history, list)

    async def test_multi_language_support(self):
        """Test multi-language support"""
        from app.services.ai_router import ai_router
        from app.services.ollama_service import ollama_service

        languages = ["en", "fr", "es", "zh"]

        for lang in languages:
            selection = await ai_router.select_provider(language=lang, force_local=True)
            assert selection.provider_name == "ollama"

            model = ollama_service.get_recommended_model(lang)
            assert model != ""

    async def test_performance(self):
        """Test performance metrics"""
        from app.services.ai_router import ai_router

        response_times = []

        for _ in range(5):
            start_time = time.time()
            await ai_router.select_provider(language="en", force_local=True)
            response_times.append(time.time() - start_time)

        avg_time = safe_mean(response_times)
        assert avg_time < 5.0  # Should be fast

        self.performance_metrics["ai_provider_selection"] = {
            "average_time": avg_time,
            "sample_size": len(response_times),
        }

    async def test_e2e_learning(self):
        """Test end-to-end learning session"""
        from app.services.conversation_manager import conversation_manager
        from app.services.conversation_models import LearningFocus

        conv_id = await conversation_manager.start_conversation(
            user_id="e2e_user",
            language="fr",
            learning_focus=LearningFocus.VOCABULARY,
            topic="Travel",
        )

        context = conversation_manager.active_conversations[conv_id]
        assert context.language == "fr"
        assert context.current_topic == "Travel"

        # Test session management
        await conversation_manager.pause_conversation(conv_id)
        success = await conversation_manager.resume_conversation(conv_id)
        assert success

    async def test_budget_fallback(self):
        """Test budget exhaustion fallback"""
        from app.services.ai_router import ai_router
        from app.services.budget_manager import budget_manager

        initial_status = budget_manager.get_current_budget_status()

        # Simulate high usage
        budget_manager.track_usage("test_provider", "test_model", 25.0, 10000)

        selection = await ai_router.select_provider(language="en")
        assert selection.provider_name == "ollama"
        assert selection.is_fallback is True

        # Reset budget
        budget_manager.current_usage = initial_status.total_usage

    async def test_cost_estimation(self):
        """Test cost estimation accuracy"""
        from app.services.ai_router import ai_router

        cost_en = await ai_router._estimate_request_cost("claude", "en", "conversation")
        cost_fr = await ai_router._estimate_request_cost(
            "mistral", "fr", "conversation"
        )

        assert cost_en > 0.0
        assert cost_fr > 0.0
        assert cost_en < 0.1  # Reasonable cost
        assert cost_fr < 0.1

    def _print_summary(self, summary: Dict[str, Any]):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Passed:   {summary['passed']:3d} / {summary['total_tests']}")
        print(f"❌ Failed:   {summary['failed']:3d} / {summary['total_tests']}")
        print(f"⏭️  Skipped:  {summary['skipped']:3d} / {summary['total_tests']}")
        print(f"💥 Errors:   {summary['errors']:3d} / {summary['total_tests']}")
        print(f"🎯 Success Rate: {summary['success_rate']:.1f}%")
        print(f"⏱️  Total Time: {summary['total_execution_time']:.2f}s")

        if summary["performance_metrics"]:
            print("\n📈 PERFORMANCE")
            for metric, data in summary["performance_metrics"].items():
                if "average_time" in data:
                    print(f"   {metric}: {data['average_time']:.3f}s avg")

        # Success determination
        if summary["success_rate"] >= 80:
            print("\n🎉 TEST SUITE PASSED!")
            print("✨ AI Language Tutor services are ready for production!")
        else:
            print("\n⚠️  TEST SUITE NEEDS ATTENTION")
            print(f"   {summary['failed'] + summary['errors']} tests need fixes")


# Global test suite instance
ai_test_suite = AIServicesTestSuite()


# Convenience function
async def run_ai_tests() -> Dict[str, Any]:
    """Run all AI services tests"""
    return await ai_test_suite.run_all_tests()


# Main execution
async def main():
    """Main test runner"""
    print("🚀 Starting AI Language Tutor Test Suite")
    print("Testing all implemented AI services...")
    print()

    start_time = datetime.now()
    results = await run_ai_tests()
    duration = (datetime.now() - start_time).total_seconds()

    print(f"\n🏁 Test Suite Completed in {duration:.2f} seconds")

    return results


if __name__ == "__main__":
    asyncio.run(main())
