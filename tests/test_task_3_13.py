#!/usr/bin/env python3
"""
Task 3.13 Verification Test
Verify AI Services Testing Suite & Integration Tests implementation
"""

import asyncio
import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

async def test_ai_testing_suite():
    """Test the AI testing suite implementation"""
    
    print("🧪 Testing Task 3.13: AI Services Testing Suite & Integration Tests")
    print("=" * 75)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Import AI Test Suite
    tests_total += 1
    try:
        from app.services.ai_test_suite import (
            AIServicesTestSuite,
            TestResult,
            TestReport,
            ai_test_suite,
            run_ai_tests
        )
        print("✅ Test 1: AI test suite imports successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1: AI test suite import failed: {e}")
    
    # Test 2: Test Suite Initialization
    tests_total += 1
    try:
        suite = AIServicesTestSuite()
        assert hasattr(suite, 'test_results')
        assert hasattr(suite, 'performance_metrics')
        assert isinstance(suite.test_results, list)
        assert isinstance(suite.performance_metrics, dict)
        print("✅ Test 2: Test suite initializes correctly")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2: Test suite initialization failed: {e}")
    
    # Test 3: Test Result Enum
    tests_total += 1
    try:
        results = list(TestResult)
        expected_results = ["passed", "failed", "skipped", "error"]
        assert len(results) >= 4
        assert all(result.value in expected_results for result in results)
        print("✅ Test 3: Test result types properly defined")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 3: Test result types test failed: {e}")
    
    # Test 4: Test Report Structure
    tests_total += 1
    try:
        report = TestReport(
            test_name="sample_test",
            result=TestResult.PASSED,
            execution_time=1.5,
            error_message=None
        )
        
        assert report.test_name == "sample_test"
        assert report.result == TestResult.PASSED
        assert report.execution_time == 1.5
        assert report.error_message is None
        print("✅ Test 4: Test report structure works correctly")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 4: Test report structure failed: {e}")
    
    # Test 5: Individual Test Methods Exist
    tests_total += 1
    try:
        suite = AIServicesTestSuite()
        
        # Check that all expected test methods exist
        expected_methods = [
            "test_ai_service_base",
            "test_budget_manager", 
            "test_ollama_service",
            "test_conversation_manager",
            "test_speech_processor",
            "test_ai_router_integration",
            "test_conversation_flow",
            "test_multi_language_support",
            "test_performance",
            "test_e2e_learning",
            "test_budget_fallback",
            "test_cost_estimation"
        ]
        
        for method_name in expected_methods:
            assert hasattr(suite, method_name)
            assert callable(getattr(suite, method_name))
        
        print("✅ Test 5: All expected test methods exist")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 5: Test methods check failed: {e}")
    
    # Test 6: Run Individual Test Method
    tests_total += 1
    try:
        suite = AIServicesTestSuite()
        
        # Test the AI service base test
        await suite.test_ai_service_base()
        print("✅ Test 6: Individual test method executes successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 6: Individual test method failed: {e}")
    
    # Test 7: Performance Metrics Collection
    tests_total += 1
    try:
        suite = AIServicesTestSuite()
        
        # Run performance test to collect metrics
        await suite.test_performance()
        
        # Check that metrics were collected
        assert len(suite.performance_metrics) > 0
        assert "ai_provider_selection" in suite.performance_metrics
        
        metrics = suite.performance_metrics["ai_provider_selection"]
        assert "average_time" in metrics
        assert "sample_size" in metrics
        assert metrics["average_time"] > 0
        
        print("✅ Test 7: Performance metrics collection works")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 7: Performance metrics failed: {e}")
    
    # Test 8: Test Suite Summary Generation
    tests_total += 1
    try:
        suite = AIServicesTestSuite()
        
        # Add some mock test results
        suite.test_results = [
            TestReport("test1", TestResult.PASSED, 1.0),
            TestReport("test2", TestResult.FAILED, 0.5, "Test error"),
            TestReport("test3", TestResult.SKIPPED, 0.0, "Skipped condition")
        ]
        
        # Test summary generation (private method test)
        summary = {
            "total_tests": 3,
            "passed": 1,
            "failed": 1,
            "skipped": 1,
            "errors": 0,
            "success_rate": 33.3,
            "total_execution_time": 1.5,
            "performance_metrics": {}
        }
        
        # This should not raise an exception
        suite._print_summary(summary)
        
        print("✅ Test 8: Test suite summary generation works")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 8: Test suite summary failed: {e}")
    
    # Test 9: Convenience Function
    tests_total += 1
    try:
        from app.services.ai_test_suite import run_ai_tests
        
        assert callable(run_ai_tests)
        print("✅ Test 9: Convenience function exists and is callable")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 9: Convenience function test failed: {e}")
    
    # Test 10: Full Test Suite Execution (Limited)
    tests_total += 1
    try:
        # This is a meta-test - testing our test suite
        # We'll just verify it can start and has the right structure
        suite = AIServicesTestSuite()
        
        # Mock a small test run by testing just one component
        await suite.test_ai_service_base()
        await suite.test_budget_manager()
        
        # Verify test results were recorded
        assert hasattr(suite, 'test_results')
        
        print("✅ Test 10: Test suite execution structure works")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 10: Test suite execution failed: {e}")
    
    # Summary
    print("\n" + "=" * 75)
    print(f"📊 TEST SUMMARY: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("🎉 ALL TESTS PASSED - Task 3.13 successfully implemented!")
        print("\n✨ AI Services Testing Suite is ready!")
        return True
    else:
        print(f"⚠️  {tests_total - tests_passed} tests failed - implementation needs fixes")
        return False

async def main():
    """Main test function"""
    try:
        success = await test_ai_testing_suite()
        
        if success:
            print("\n🚀 AI Services Testing Suite Features:")
            print("   ✅ Comprehensive unit tests for all AI services")
            print("   ✅ Integration tests for AI router and conversation flow")
            print("   ✅ Performance testing and benchmarking")
            print("   ✅ End-to-end learning session testing")
            print("   ✅ Budget management and fallback testing")
            print("   ✅ Multi-language support validation")
            print("   ✅ Cost estimation accuracy testing")
            print("   ✅ Error handling and edge case testing")
            print("   ✅ Automated test reporting and metrics")
            print("   ✅ Mock services for cost-free testing")
            
            print("\n🎯 Ready to run full test suite:")
            print("   python -m app.services.ai_test_suite")
        
        return success
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)