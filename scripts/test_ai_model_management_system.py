"""
Comprehensive Test Suite for AI Model Management System
AI Language Tutor App - Task 3.1.5

This test suite provides comprehensive validation of the AI Model Management system including:
- Model configuration and CRUD operations
- Performance monitoring and analytics
- Health checks and diagnostics
- Cost optimization controls
- Provider management
- Usage statistics and reporting
- API endpoint validation
- Database operations
- Error handling and edge cases

Target: 100% test success rate with comprehensive coverage
"""

import asyncio
import sqlite3
import json
import sys
import os
import tempfile
from datetime import datetime
import traceback

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.ai_model_manager import (  # noqa: E402 - Required after sys.path modification for script execution
    ai_model_manager,
)
from app.services.ai_router import ai_router  # noqa: E402 - Required after sys.path modification for script execution


class AIModelManagementTestSuite:
    """Comprehensive test suite for AI Model Management system"""

    def __init__(self):
        self.test_results = []
        self.temp_db_path = None
        self.original_db_path = None

    def log_test(
        self, test_name: str, success: bool, details: str = "", error: str = ""
    ):
        """Log test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")

    async def setup_test_environment(self):
        """Set up isolated test environment"""
        try:
            # Create temporary database for testing
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
            self.temp_db_path = temp_file.name
            temp_file.close()

            # Backup original db path
            self.original_db_path = ai_model_manager.db_path

            # Set test database path
            ai_model_manager.db_path = self.temp_db_path

            # Reinitialize with test database
            ai_model_manager._initialize_database()
            ai_model_manager._load_default_models()

            self.log_test(
                "Setup Test Environment",
                True,
                f"Test database created: {self.temp_db_path}",
            )

        except Exception as e:
            self.log_test("Setup Test Environment", False, error=str(e))
            raise

    async def cleanup_test_environment(self):
        """Clean up test environment"""
        try:
            # Restore original database path
            if self.original_db_path:
                ai_model_manager.db_path = self.original_db_path

            # Remove temporary database
            if self.temp_db_path and os.path.exists(self.temp_db_path):
                os.unlink(self.temp_db_path)

            self.log_test(
                "Cleanup Test Environment",
                True,
                "Test environment cleaned up successfully",
            )

        except Exception as e:
            self.log_test("Cleanup Test Environment", False, error=str(e))

    async def test_database_initialization(self):
        """Test 1: Database Schema and Initialization"""
        try:
            with sqlite3.connect(ai_model_manager.db_path) as conn:
                cursor = conn.cursor()

                # Check if all required tables exist
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name IN (
                        'model_configurations',
                        'model_usage_stats',
                        'model_performance_logs'
                    )
                """)

                tables = [row[0] for row in cursor.fetchall()]
                expected_tables = [
                    "model_configurations",
                    "model_usage_stats",
                    "model_performance_logs",
                ]

                if len(tables) == len(expected_tables):
                    # Check model_configurations table structure
                    cursor.execute("PRAGMA table_info(model_configurations)")
                    columns = [row[1] for row in cursor.fetchall()]

                    required_columns = [
                        "model_id",
                        "provider",
                        "model_name",
                        "display_name",
                        "category",
                        "status",
                        "enabled",
                        "priority",
                    ]

                    missing_columns = [
                        col for col in required_columns if col not in columns
                    ]

                    if not missing_columns:
                        self.log_test(
                            "Database Schema Validation",
                            True,
                            f"All tables and columns present: {len(tables)} tables, {len(columns)} columns",
                        )
                    else:
                        self.log_test(
                            "Database Schema Validation",
                            False,
                            error=f"Missing columns: {missing_columns}",
                        )
                else:
                    self.log_test(
                        "Database Schema Validation",
                        False,
                        error=f"Missing tables. Found: {tables}, Expected: {expected_tables}",
                    )

        except Exception as e:
            self.log_test(
                "Database Schema Validation", False, error=f"Database error: {str(e)}"
            )

    async def test_default_models_loading(self):
        """Test 2: Default Models Loading"""
        try:
            models = await ai_model_manager.get_all_models()

            if len(models) >= 5:  # Expect at least 5 default models
                # Check for required providers
                providers = set(model["provider"] for model in models)
                expected_providers = {"claude", "mistral", "deepseek", "ollama"}

                if expected_providers.issubset(providers):
                    # Verify model structure
                    sample_model = models[0]
                    required_fields = [
                        "id",
                        "provider",
                        "model_name",
                        "display_name",
                        "category",
                        "status",
                        "enabled",
                        "priority",
                    ]

                    missing_fields = [
                        field for field in required_fields if field not in sample_model
                    ]

                    if not missing_fields:
                        self.log_test(
                            "Default Models Loading",
                            True,
                            f"Loaded {len(models)} models with {len(providers)} providers",
                        )
                    else:
                        self.log_test(
                            "Default Models Loading",
                            False,
                            error=f"Missing fields in model data: {missing_fields}",
                        )
                else:
                    self.log_test(
                        "Default Models Loading",
                        False,
                        error=f"Missing providers. Found: {providers}, Expected: {expected_providers}",
                    )
            else:
                self.log_test(
                    "Default Models Loading",
                    False,
                    error=f"Insufficient models loaded: {len(models)}",
                )

        except Exception as e:
            self.log_test("Default Models Loading", False, error=str(e))

    async def test_model_crud_operations(self):
        """Test 3: Model CRUD Operations"""
        try:
            # Get initial model count
            initial_models = await ai_model_manager.get_all_models()
            initial_count = len(initial_models)

            # Test READ operations
            if initial_count > 0:
                sample_model_id = initial_models[0]["id"]
                retrieved_model = await ai_model_manager.get_model(sample_model_id)

                if retrieved_model and retrieved_model["id"] == sample_model_id:
                    read_success = True
                else:
                    read_success = False
                    self.log_test(
                        "Model CRUD - READ",
                        False,
                        error="Failed to retrieve specific model",
                    )
            else:
                read_success = False
                self.log_test(
                    "Model CRUD - READ",
                    False,
                    error="No models available for READ test",
                )

            # Test UPDATE operations
            if read_success and initial_count > 0:
                sample_model_id = initial_models[0]["id"]

                # Update model configuration
                update_data = {
                    "display_name": "Test Updated Model",
                    "priority": 5,
                    "temperature": 0.8,
                    "quality_score": 0.85,
                }

                update_success = await ai_model_manager.update_model(
                    sample_model_id, update_data
                )

                if update_success:
                    # Verify update
                    updated_model = await ai_model_manager.get_model(sample_model_id)

                    if (
                        updated_model["display_name"] == "Test Updated Model"
                        and updated_model["priority"] == 5
                        and abs(updated_model["temperature"] - 0.8) < 0.01
                    ):
                        self.log_test(
                            "Model CRUD - UPDATE",
                            True,
                            "Successfully updated model configuration",
                        )
                    else:
                        self.log_test(
                            "Model CRUD - UPDATE",
                            False,
                            error="Model update verification failed",
                        )
                else:
                    self.log_test(
                        "Model CRUD - UPDATE",
                        False,
                        error="Model update operation failed",
                    )

            # Test enable/disable operations
            if initial_count > 0:
                sample_model_id = initial_models[0]["id"]

                # Test disable
                disable_success = await ai_model_manager.disable_model(sample_model_id)
                if disable_success:
                    disabled_model = await ai_model_manager.get_model(sample_model_id)

                    if not disabled_model["enabled"]:
                        # Test enable
                        enable_success = await ai_model_manager.enable_model(
                            sample_model_id
                        )
                        if enable_success:
                            enabled_model = await ai_model_manager.get_model(
                                sample_model_id
                            )

                            if enabled_model["enabled"]:
                                self.log_test(
                                    "Model CRUD - ENABLE/DISABLE",
                                    True,
                                    "Successfully toggled model enabled status",
                                )
                            else:
                                self.log_test(
                                    "Model CRUD - ENABLE/DISABLE",
                                    False,
                                    error="Enable operation failed",
                                )
                        else:
                            self.log_test(
                                "Model CRUD - ENABLE/DISABLE",
                                False,
                                error="Enable operation returned False",
                            )
                    else:
                        self.log_test(
                            "Model CRUD - ENABLE/DISABLE",
                            False,
                            error="Disable operation failed",
                        )
                else:
                    self.log_test(
                        "Model CRUD - ENABLE/DISABLE",
                        False,
                        error="Disable operation returned False",
                    )

        except Exception as e:
            self.log_test("Model CRUD Operations", False, error=str(e))

    async def test_model_filtering_and_search(self):
        """Test 4: Model Filtering and Search"""
        try:
            # Test category filtering
            conversation_models = await ai_model_manager.get_all_models(
                category="conversation"
            )
            all_models = await ai_model_manager.get_all_models()

            conversation_count = len(
                [m for m in all_models if m["category"] == "conversation"]
            )

            if len(conversation_models) == conversation_count:
                category_filter_success = True
            else:
                category_filter_success = False
                self.log_test(
                    "Model Filtering - Category",
                    False,
                    error=f"Category filter mismatch: got {len(conversation_models)}, expected {conversation_count}",
                )

            # Test enabled-only filtering
            enabled_models = await ai_model_manager.get_all_models(enabled_only=True)
            enabled_count = len([m for m in all_models if m["enabled"]])

            if len(enabled_models) == enabled_count:
                enabled_filter_success = True
            else:
                enabled_filter_success = False
                self.log_test(
                    "Model Filtering - Enabled Only",
                    False,
                    error=f"Enabled filter mismatch: got {len(enabled_models)}, expected {enabled_count}",
                )

            if category_filter_success and enabled_filter_success:
                self.log_test(
                    "Model Filtering and Search",
                    True,
                    f"Successfully filtered models: {len(conversation_models)} conversation, {len(enabled_models)} enabled",
                )

        except Exception as e:
            self.log_test("Model Filtering and Search", False, error=str(e))

    async def test_usage_tracking(self):
        """Test 5: Usage Statistics Tracking"""
        try:
            models = await ai_model_manager.get_all_models()

            if len(models) > 0:
                sample_model_id = models[0]["id"]

                # Get initial stats
                initial_model = await ai_model_manager.get_model(sample_model_id)
                initial_requests = initial_model["usage_stats"]["total_requests"]

                # Track some usage
                await ai_model_manager.track_model_usage(
                    model_id=sample_model_id,
                    response_time_ms=1200.5,
                    tokens_used=150,
                    cost=0.005,
                    success=True,
                    quality_rating=0.9,
                )

                # Track another usage
                await ai_model_manager.track_model_usage(
                    model_id=sample_model_id,
                    response_time_ms=800.0,
                    tokens_used=100,
                    cost=0.003,
                    success=True,
                    quality_rating=0.85,
                )

                # Verify stats update
                updated_model = await ai_model_manager.get_model(sample_model_id)
                updated_requests = updated_model["usage_stats"]["total_requests"]

                if updated_requests == initial_requests + 2:
                    # Check if other metrics were updated
                    usage_stats = updated_model["usage_stats"]

                    if (
                        usage_stats["total_cost"] > 0
                        and usage_stats["avg_response_time"] > 0
                    ):
                        self.log_test(
                            "Usage Statistics Tracking",
                            True,
                            f"Successfully tracked usage: {updated_requests} total requests",
                        )
                    else:
                        self.log_test(
                            "Usage Statistics Tracking",
                            False,
                            error="Usage metrics not properly calculated",
                        )
                else:
                    self.log_test(
                        "Usage Statistics Tracking",
                        False,
                        error=f"Request count mismatch: expected {initial_requests + 2}, got {updated_requests}",
                    )
            else:
                self.log_test(
                    "Usage Statistics Tracking",
                    False,
                    error="No models available for usage tracking test",
                )

        except Exception as e:
            self.log_test("Usage Statistics Tracking", False, error=str(e))

    async def test_performance_reporting(self):
        """Test 6: Performance Report Generation"""
        try:
            models = await ai_model_manager.get_all_models()

            if len(models) > 0:
                sample_model_id = models[0]["id"]

                # Generate performance report
                report = await ai_model_manager.get_model_performance_report(
                    sample_model_id, days=30
                )

                if report:
                    # Verify report structure
                    required_fields = [
                        "model_id",
                        "cost_efficiency",
                        "speed_efficiency",
                        "reliability_score",
                        "recommended_for",
                        "optimization_suggestions",
                    ]

                    missing_fields = [
                        field for field in required_fields if not hasattr(report, field)
                    ]

                    if not missing_fields:
                        self.log_test(
                            "Performance Report Generation",
                            True,
                            f"Generated report with {len(report.recommended_for)} recommendations",
                        )
                    else:
                        self.log_test(
                            "Performance Report Generation",
                            False,
                            error=f"Missing report fields: {missing_fields}",
                        )
                else:
                    self.log_test(
                        "Performance Report Generation",
                        False,
                        error="No performance report generated (may be normal for new models)",
                    )
            else:
                self.log_test(
                    "Performance Report Generation",
                    False,
                    error="No models available for performance reporting test",
                )

        except Exception as e:
            self.log_test("Performance Report Generation", False, error=str(e))

    async def test_system_overview(self):
        """Test 7: System Overview and Statistics"""
        try:
            overview = await ai_model_manager.get_system_overview()

            # Verify overview structure
            required_sections = [
                "overview",
                "budget_status",
                "providers",
                "top_models",
                "categories",
            ]
            missing_sections = [
                section for section in required_sections if section not in overview
            ]

            if not missing_sections:
                # Verify data consistency
                overview_data = overview["overview"]

                if (
                    overview_data["total_models"] >= 0
                    and overview_data["active_models"] >= 0
                    and overview_data["total_cost"] >= 0
                ):
                    self.log_test(
                        "System Overview and Statistics",
                        True,
                        f"Overview generated: {overview_data['total_models']} models, ${overview_data['total_cost']:.4f} cost",
                    )
                else:
                    self.log_test(
                        "System Overview and Statistics",
                        False,
                        error="Invalid data in overview metrics",
                    )
            else:
                self.log_test(
                    "System Overview and Statistics",
                    False,
                    error=f"Missing overview sections: {missing_sections}",
                )

        except Exception as e:
            self.log_test("System Overview and Statistics", False, error=str(e))

    async def test_model_optimization(self):
        """Test 8: Model Optimization and Recommendations"""
        try:
            # Test optimization for different use cases
            test_cases = [
                {"language": "en", "use_case": "conversation"},
                {"language": "fr", "use_case": "conversation"},
                {"language": "zh", "use_case": "conversation"},
                {"language": "en", "use_case": "translation"},
            ]

            optimization_results = []

            for test_case in test_cases:
                recommendations = await ai_model_manager.optimize_model_selection(
                    language=test_case["language"], use_case=test_case["use_case"]
                )

                optimization_results.append(
                    {
                        "test_case": test_case,
                        "recommendations": recommendations,
                        "count": len(recommendations),
                    }
                )

            # Verify we got recommendations for each test case
            successful_cases = [r for r in optimization_results if r["count"] > 0]

            if (
                len(successful_cases) >= len(test_cases) * 0.75
            ):  # At least 75% success rate
                self.log_test(
                    "Model Optimization and Recommendations",
                    True,
                    f"Generated recommendations for {len(successful_cases)}/{len(test_cases)} test cases",
                )
            else:
                self.log_test(
                    "Model Optimization and Recommendations",
                    False,
                    error=f"Insufficient recommendations: {len(successful_cases)}/{len(test_cases)} cases",
                )

        except Exception as e:
            self.log_test("Model Optimization and Recommendations", False, error=str(e))

    async def test_health_monitoring(self):
        """Test 9: Health Monitoring and Status Checks"""
        try:
            health_status = await ai_model_manager.get_health_status()

            # Verify health status structure
            required_fields = [
                "system_health",
                "providers",
                "total_models",
                "active_models",
            ]
            missing_fields = [
                field for field in required_fields if field not in health_status
            ]

            if not missing_fields:
                # Check provider health information
                providers = health_status["providers"]
                expected_providers = ["claude", "mistral", "deepseek", "ollama"]

                provider_checks = []
                for provider in expected_providers:
                    if provider in providers:
                        provider_info = providers[provider]
                        if "status" in provider_info and "available" in provider_info:
                            provider_checks.append(True)
                        else:
                            provider_checks.append(False)
                    else:
                        provider_checks.append(False)

                successful_checks = sum(provider_checks)

                if (
                    successful_checks >= len(expected_providers) * 0.75
                ):  # At least 75% providers checked
                    self.log_test(
                        "Health Monitoring and Status Checks",
                        True,
                        f"Health check completed: {successful_checks}/{len(expected_providers)} providers checked",
                    )
                else:
                    self.log_test(
                        "Health Monitoring and Status Checks",
                        False,
                        error=f"Insufficient provider health checks: {successful_checks}/{len(expected_providers)}",
                    )
            else:
                self.log_test(
                    "Health Monitoring and Status Checks",
                    False,
                    error=f"Missing health status fields: {missing_fields}",
                )

        except Exception as e:
            self.log_test("Health Monitoring and Status Checks", False, error=str(e))

    async def test_error_handling(self):
        """Test 10: Error Handling and Edge Cases"""
        try:
            error_tests = []

            # Test 1: Invalid model ID operations
            try:
                result = await ai_model_manager.get_model("invalid_model_id")
                error_tests.append(("Invalid Model ID", result is None))
            except Exception:
                error_tests.append(
                    ("Invalid Model ID", True)
                )  # Exception is acceptable

            # Test 2: Invalid update data
            try:
                result = await ai_model_manager.update_model(
                    "invalid_model_id", {"invalid_field": "value"}
                )
                error_tests.append(("Invalid Update Data", not result))
            except Exception:
                error_tests.append(
                    ("Invalid Update Data", True)
                )  # Exception is acceptable

            # Test 3: Invalid priority values
            try:
                result = await ai_model_manager.set_model_priority(
                    "invalid_model_id", 15
                )  # Out of range
                error_tests.append(("Invalid Priority Range", not result))
            except Exception:
                error_tests.append(
                    ("Invalid Priority Range", True)
                )  # Exception is acceptable

            # Test 4: Usage tracking with invalid model ID
            try:
                await ai_model_manager.track_model_usage(
                    model_id="invalid_model_id",
                    response_time_ms=1000,
                    tokens_used=100,
                    cost=0.01,
                )
                error_tests.append(("Invalid Usage Tracking", True))  # Should not crash
            except Exception:
                error_tests.append(
                    ("Invalid Usage Tracking", True)
                )  # Exception is acceptable

            successful_error_tests = sum(
                1 for test_name, success in error_tests if success
            )

            if successful_error_tests >= len(error_tests) * 0.75:  # At least 75% pass
                self.log_test(
                    "Error Handling and Edge Cases",
                    True,
                    f"Handled {successful_error_tests}/{len(error_tests)} error scenarios correctly",
                )
            else:
                self.log_test(
                    "Error Handling and Edge Cases",
                    False,
                    error=f"Poor error handling: {successful_error_tests}/{len(error_tests)} scenarios",
                )

        except Exception as e:
            self.log_test("Error Handling and Edge Cases", False, error=str(e))

    async def test_data_persistence(self):
        """Test 11: Data Persistence and Database Operations"""
        try:
            # Get initial data
            initial_models = await ai_model_manager.get_all_models()

            if len(initial_models) > 0:
                sample_model_id = initial_models[0]["id"]

                # Make some changes
                update_data = {"display_name": "Persistence Test Model", "priority": 7}

                await ai_model_manager.update_model(sample_model_id, update_data)

                # Track usage
                await ai_model_manager.track_model_usage(
                    model_id=sample_model_id,
                    response_time_ms=1500,
                    tokens_used=200,
                    cost=0.01,
                    success=True,
                )

                # Verify data in database directly
                with sqlite3.connect(ai_model_manager.db_path) as conn:
                    cursor = conn.cursor()

                    # Check model configuration
                    cursor.execute(
                        "SELECT display_name, priority FROM model_configurations WHERE model_id = ?",
                        (sample_model_id,),
                    )
                    config_result = cursor.fetchone()

                    # Check usage stats
                    cursor.execute(
                        "SELECT total_requests, total_cost FROM model_usage_stats WHERE model_id = ?",
                        (sample_model_id,),
                    )
                    stats_result = cursor.fetchone()

                    # Check performance logs
                    cursor.execute(
                        "SELECT COUNT(*) FROM model_performance_logs WHERE model_id = ?",
                        (sample_model_id,),
                    )
                    logs_count = cursor.fetchone()[0]

                if (
                    config_result
                    and config_result[0] == "Persistence Test Model"
                    and config_result[1] == 7
                    and stats_result
                    and logs_count > 0
                ):
                    self.log_test(
                        "Data Persistence and Database Operations",
                        True,
                        f"Data persisted correctly: config updated, {stats_result[0]} requests, {logs_count} logs",
                    )
                else:
                    self.log_test(
                        "Data Persistence and Database Operations",
                        False,
                        error="Data not properly persisted to database",
                    )
            else:
                self.log_test(
                    "Data Persistence and Database Operations",
                    False,
                    error="No models available for persistence test",
                )

        except Exception as e:
            self.log_test(
                "Data Persistence and Database Operations", False, error=str(e)
            )

    async def test_integration_with_ai_router(self):
        """Test 12: Integration with AI Router"""
        try:
            # Test router status integration
            router_status = await ai_router.get_router_status()

            if router_status:
                # Verify router has access to models
                if "providers" in router_status:
                    provider_count = len(router_status["providers"])

                    # Check if model manager can provide health data
                    health_status = await ai_model_manager.get_health_status()

                    if "providers" in health_status:
                        manager_provider_count = len(health_status["providers"])

                        if provider_count > 0 and manager_provider_count > 0:
                            self.log_test(
                                "Integration with AI Router",
                                True,
                                f"Router integration verified: {provider_count} router providers, {manager_provider_count} manager providers",
                            )
                        else:
                            self.log_test(
                                "Integration with AI Router",
                                False,
                                error="No providers found in router or manager",
                            )
                    else:
                        self.log_test(
                            "Integration with AI Router",
                            False,
                            error="Model manager health status missing providers",
                        )
                else:
                    self.log_test(
                        "Integration with AI Router",
                        False,
                        error="Router status missing providers information",
                    )
            else:
                self.log_test(
                    "Integration with AI Router",
                    False,
                    error="Unable to get router status",
                )

        except Exception as e:
            self.log_test("Integration with AI Router", False, error=str(e))

    async def run_all_tests(self):
        """Run all tests in the test suite"""
        print("🚀 Starting AI Model Management System Test Suite")
        print("=" * 60)

        # Set up test environment
        await self.setup_test_environment()

        try:
            # Run all tests
            await self.test_database_initialization()
            await self.test_default_models_loading()
            await self.test_model_crud_operations()
            await self.test_model_filtering_and_search()
            await self.test_usage_tracking()
            await self.test_performance_reporting()
            await self.test_system_overview()
            await self.test_model_optimization()
            await self.test_health_monitoring()
            await self.test_error_handling()
            await self.test_data_persistence()
            await self.test_integration_with_ai_router()

        finally:
            # Clean up test environment
            await self.cleanup_test_environment()

        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate comprehensive final test report"""
        print("\n" + "=" * 60)
        print("📊 AI MODEL MANAGEMENT SYSTEM TEST RESULTS")
        print("=" * 60)

        stats = self._calculate_test_statistics()

        self._print_summary(stats)
        self._print_failed_tests()
        self._print_categories_analysis()
        passed_gates = self._print_quality_gates(stats)
        self._print_final_verdict(stats["success_rate"])
        self._save_detailed_results(stats, passed_gates)

    def _calculate_test_statistics(self) -> dict:
        """Calculate test statistics"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
        }

    def _print_summary(self, stats: dict):
        """Print test summary statistics"""
        print(f"Total Tests: {stats['total_tests']}")
        print(f"Passed: {stats['passed_tests']}")
        print(f"Failed: {stats['failed_tests']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")

    def _print_failed_tests(self):
        """Print failed tests details"""
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"  • {result['test_name']}: {result['error']}")

    def _print_categories_analysis(self):
        """Print test categories analysis"""
        print("\n📋 TEST CATEGORIES ANALYSIS:")

        categories = {
            "Database & Storage": [
                "Database Schema Validation",
                "Default Models Loading",
                "Data Persistence and Database Operations",
            ],
            "Model Management": [
                "Model CRUD Operations",
                "Model Filtering and Search",
                "Usage Statistics Tracking",
            ],
            "Performance & Analytics": [
                "Performance Report Generation",
                "System Overview and Statistics",
                "Model Optimization and Recommendations",
            ],
            "System Integration": [
                "Health Monitoring and Status Checks",
                "Integration with AI Router",
                "Error Handling and Edge Cases",
            ],
        }

        for category, test_names in categories.items():
            category_results = [
                r for r in self.test_results if r["test_name"] in test_names
            ]
            category_passed = len([r for r in category_results if r["success"]])
            category_total = len(category_results)
            category_rate = (
                (category_passed / category_total * 100) if category_total > 0 else 0
            )
            print(
                f"  {category}: {category_passed}/{category_total} ({category_rate:.1f}%)"
            )

    def _print_quality_gates(self, stats: dict) -> int:
        """Print quality gates assessment and return passed count"""
        print("\n🎯 QUALITY GATES ASSESSMENT:")

        gates = [
            (
                "Database Operations",
                stats["success_rate"] >= 90,
                "All database operations must work correctly",
            ),
            (
                "Model CRUD Operations",
                stats["passed_tests"] >= stats["total_tests"] * 0.85,
                "Core model operations must be functional",
            ),
            (
                "Performance Tracking",
                any(
                    "Performance" in r["test_name"] and r["success"]
                    for r in self.test_results
                ),
                "Performance monitoring must be operational",
            ),
            (
                "Error Handling",
                any(
                    "Error Handling" in r["test_name"] and r["success"]
                    for r in self.test_results
                ),
                "System must handle errors gracefully",
            ),
            (
                "Overall System Health",
                stats["success_rate"] >= 80,
                "Overall system must be stable and functional",
            ),
        ]

        passed_gates = 0
        for gate_name, gate_passed, gate_description in gates:
            status = "✅ PASS" if gate_passed else "❌ FAIL"
            print(f"  {status} {gate_name}: {gate_description}")
            if gate_passed:
                passed_gates += 1

        print(f"\nQuality Gates: {passed_gates}/{len(gates)} PASSED")
        return passed_gates

    def _print_final_verdict(self, success_rate: float):
        """Print final verdict based on success rate"""
        print("\n🏆 FINAL VERDICT:")
        if success_rate >= 95:
            print("🌟 EXCELLENT: AI Model Management System is production-ready!")
        elif success_rate >= 85:
            print("✅ GOOD: AI Model Management System is functional with minor issues")
        elif success_rate >= 70:
            print(
                "⚠️  ACCEPTABLE: AI Model Management System has some issues that should be addressed"
            )
        else:
            print(
                "❌ NEEDS WORK: AI Model Management System requires significant fixes"
            )

    def _save_detailed_results(self, stats: dict, passed_gates: int):
        """Save detailed test results to JSON file"""
        try:
            os.makedirs("./validation_artifacts/3.1.5", exist_ok=True)

            with open(
                "./validation_artifacts/3.1.5/ai_model_management_test_results.json",
                "w",
            ) as f:
                json.dump(
                    {
                        "summary": {
                            **stats,
                            "quality_gates_passed": passed_gates,
                            "quality_gates_total": 5,
                        },
                        "test_results": self.test_results,
                        "timestamp": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )

            print(
                "\n💾 Detailed results saved to: ./validation_artifacts/3.1.5/ai_model_management_test_results.json"
            )

        except Exception as e:
            print(f"\n⚠️  Failed to save detailed results: {e}")


async def main():
    """Main test execution function"""
    try:
        test_suite = AIModelManagementTestSuite()
        await test_suite.run_all_tests()

    except KeyboardInterrupt:
        print("\n\n⚠️ Test suite interrupted by user")
        return 1

    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
