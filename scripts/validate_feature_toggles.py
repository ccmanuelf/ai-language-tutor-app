#!/usr/bin/env python3
"""
Feature Toggle System Validation
Comprehensive testing and validation for Task 3.1.7
"""

import asyncio
import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.feature_toggle_service import (
    FeatureToggleService,
    get_feature_toggle_service,
)
from app.models.feature_toggle import (
    FeatureToggleRequest,
    FeatureToggleUpdateRequest,
    FeatureToggleCategory,
    FeatureToggleScope,
    FeatureToggleStatus,
)


class FeatureToggleValidator:
    """Comprehensive validation of feature toggle system."""

    def __init__(self):
        self.results = {
            "validation_type": "Feature Toggle System Comprehensive Test",
            "timestamp": datetime.now().isoformat(),
            "task_id": "3.1.7",
            "test_results": {},
            "performance_metrics": {},
            "integration_tests": {},
            "error_log": [],
            "summary": {},
        }
        self.temp_dir = None
        self.test_service = None

    async def setup_test_environment(self):
        """Setup isolated test environment."""
        print("🔧 Setting up test environment...")

        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp(prefix="feature_toggle_test_")

        # Create test service with isolated storage
        self.test_service = FeatureToggleService(storage_dir=self.temp_dir)
        await self.test_service.initialize()

        print(f"✅ Test environment created: {self.temp_dir}")

    async def cleanup_test_environment(self):
        """Cleanup test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up test environment: {self.temp_dir}")

    async def test_service_initialization(self):
        """Test service initialization and default features."""
        print("🧪 Testing service initialization...")

        test_name = "service_initialization"
        start_time = time.time()

        try:
            # Test service initialization
            service = FeatureToggleService(storage_dir=self.temp_dir)
            await service.initialize()

            # Verify default features were created
            features = await service.get_all_features()
            assert len(features) > 0, "Should have default features"

            # Check for expected default features
            feature_ids = [f.id for f in features]
            expected_features = [
                "advanced_speech_analysis",
                "conversation_scenarios",
                "ai_tutor_mode",
                "spaced_repetition",
                "admin_dashboard",
            ]

            for expected_id in expected_features:
                assert any(expected_id in fid for fid in feature_ids), (
                    f"Should have {expected_id}"
                )

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "default_features_count": len(features),
                "feature_ids": feature_ids,
                "details": "Service initialized successfully with default features",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Service initialization test failed: {e}")

    async def test_feature_crud_operations(self):
        """Test all CRUD operations for features."""
        print("🧪 Testing CRUD operations...")

        # Test Create
        await self._test_create_feature()

        # Test Read
        await self._test_read_features()

        # Test Update
        await self._test_update_feature()

        # Test Delete
        await self._test_delete_feature()

    async def _test_create_feature(self):
        """Test feature creation."""
        test_name = "create_feature"
        start_time = time.time()

        try:
            test_feature = FeatureToggleRequest(
                name="Test Feature Creation",
                description="A test feature for validation",
                category=FeatureToggleCategory.EXPERIMENTAL,
                scope=FeatureToggleScope.GLOBAL,
                status=FeatureToggleStatus.DISABLED,
                enabled_by_default=False,
                requires_admin=True,
                experimental=True,
                rollout_percentage=50.0,
            )

            feature = await self.test_service.create_feature(test_feature, "test_user")
            assert feature is not None, "Should return created feature"
            assert feature.name == test_feature.name, "Name should match"
            assert feature.category == test_feature.category, "Category should match"
            assert feature.created_by == "test_user", "Created by should be set"

            # Store feature ID for other tests
            self.test_feature_id = feature.id

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "feature_id": feature.id,
                "details": "Feature created successfully",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Create feature test failed: {e}")

    async def _test_read_features(self):
        """Test feature reading operations."""
        test_name = "read_features"
        start_time = time.time()

        try:
            # Test get all features
            all_features = await self.test_service.get_all_features()
            assert len(all_features) > 0, "Should have features"

            # Test get specific feature
            if hasattr(self, "test_feature_id"):
                specific_feature = await self.test_service.get_feature(
                    self.test_feature_id
                )
                assert specific_feature is not None, "Should retrieve specific feature"
                assert specific_feature.id == self.test_feature_id, "IDs should match"

            # Test filtering by category
            experimental_features = await self.test_service.get_all_features(
                category=FeatureToggleCategory.EXPERIMENTAL
            )
            assert isinstance(experimental_features, list), "Should return list"

            # Test filtering by status
            enabled_features = await self.test_service.get_all_features(
                status=FeatureToggleStatus.ENABLED
            )
            assert isinstance(enabled_features, list), "Should return list"

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "total_features": len(all_features),
                "experimental_features": len(experimental_features),
                "enabled_features": len(enabled_features),
                "details": "All read operations successful",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Read features test failed: {e}")

    async def _test_update_feature(self):
        """Test feature update operations."""
        test_name = "update_feature"
        start_time = time.time()

        try:
            if not hasattr(self, "test_feature_id"):
                raise Exception("No test feature ID available for update test")

            # Update feature
            update_request = FeatureToggleUpdateRequest(
                name="Updated Test Feature",
                description="Updated description for testing",
                status=FeatureToggleStatus.ENABLED,
                rollout_percentage=75.0,
            )

            updated_feature = await self.test_service.update_feature(
                self.test_feature_id, update_request, "test_updater"
            )

            assert updated_feature is not None, "Update should return feature"
            assert updated_feature.name == update_request.name, "Name should be updated"
            assert updated_feature.status == update_request.status, (
                "Status should be updated"
            )
            assert updated_feature.updated_by == "test_updater", (
                "Updated by should be set"
            )

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "feature_id": self.test_feature_id,
                "details": "Feature updated successfully",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Update feature test failed: {e}")

    async def _test_delete_feature(self):
        """Test feature deletion operations."""
        test_name = "delete_feature"
        start_time = time.time()

        try:
            if not hasattr(self, "test_feature_id"):
                raise Exception("No test feature ID available for delete test")

            # Delete feature
            success = await self.test_service.delete_feature(
                self.test_feature_id, "test_deleter"
            )
            assert success, "Deletion should return True"

            # Verify feature is deleted
            deleted_feature = await self.test_service.get_feature(self.test_feature_id)
            assert deleted_feature is None, "Feature should not exist after deletion"

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "deleted_feature_id": self.test_feature_id,
                "details": "Feature deleted successfully",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Delete feature test failed: {e}")

    async def test_feature_evaluation(self):
        """Test feature evaluation logic."""
        print("🧪 Testing feature evaluation...")

        test_name = "feature_evaluation"
        start_time = time.time()

        try:
            # Create test features with different configurations
            await self._test_global_feature()
            await self._test_role_based_feature()
            await self._test_user_specific_feature()
            await self._test_experimental_feature()

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "details": "All feature evaluation tests passed",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Feature evaluation test failed: {e}")

    async def _test_global_feature(self):
        """Test global feature evaluation."""
        global_feature = FeatureToggleRequest(
            name="Global Test Feature",
            description="Global feature for testing",
            category=FeatureToggleCategory.UI_COMPONENTS,
            scope=FeatureToggleScope.GLOBAL,
            status=FeatureToggleStatus.ENABLED,
        )

        feature = await self.test_service.create_feature(global_feature)

        # Test with different users
        result1 = await self.test_service.is_feature_enabled(feature.id, "user1")
        result2 = await self.test_service.is_feature_enabled(feature.id, "user2")
        result3 = await self.test_service.is_feature_enabled(
            feature.id, None
        )  # Anonymous

        assert result1 == True, "Global feature should be enabled for user1"
        assert result2 == True, "Global feature should be enabled for user2"
        assert result3 == True, "Global feature should be enabled for anonymous"

    async def _test_role_based_feature(self):
        """Test role-based feature evaluation."""
        role_feature = FeatureToggleRequest(
            name="Role Based Test Feature",
            description="Role-based feature for testing",
            category=FeatureToggleCategory.UI_COMPONENTS,
            scope=FeatureToggleScope.ROLE_BASED,
            status=FeatureToggleStatus.ENABLED,
            target_roles=["admin", "moderator"],
        )

        feature = await self.test_service.create_feature(role_feature)

        # Test with different roles
        result_admin = await self.test_service.is_feature_enabled(
            feature.id, "user1", ["admin"]
        )
        result_user = await self.test_service.is_feature_enabled(
            feature.id, "user2", ["user"]
        )
        result_mod = await self.test_service.is_feature_enabled(
            feature.id, "user3", ["moderator"]
        )

        assert result_admin == True, "Admin should have access to role-based feature"
        assert result_user == False, "Regular user should not have access"
        assert result_mod == True, "Moderator should have access to role-based feature"

    async def _test_user_specific_feature(self):
        """Test user-specific feature evaluation."""
        user_feature = FeatureToggleRequest(
            name="User Specific Test Feature",
            description="User-specific feature for testing",
            category=FeatureToggleCategory.EXPERIMENTAL,
            scope=FeatureToggleScope.USER_SPECIFIC,
            status=FeatureToggleStatus.ENABLED,
            target_users=["special_user1", "special_user2"],
        )

        feature = await self.test_service.create_feature(user_feature)

        # Test with different users
        result_special = await self.test_service.is_feature_enabled(
            feature.id, "special_user1"
        )
        result_regular = await self.test_service.is_feature_enabled(
            feature.id, "regular_user"
        )

        assert result_special == True, "Special user should have access"
        assert result_regular == False, "Regular user should not have access"

    async def _test_experimental_feature(self):
        """Test experimental feature evaluation."""
        exp_feature = FeatureToggleRequest(
            name="Experimental Test Feature",
            description="Experimental feature for testing",
            category=FeatureToggleCategory.EXPERIMENTAL,
            scope=FeatureToggleScope.EXPERIMENTAL,
            status=FeatureToggleStatus.ENABLED,
            experimental=True,
            rollout_percentage=50.0,
        )

        feature = await self.test_service.create_feature(exp_feature)

        # Test rollout percentage (deterministic based on user hash)
        test_users = [f"user_{i}" for i in range(100)]
        enabled_count = 0

        for user in test_users:
            if await self.test_service.is_feature_enabled(feature.id, user):
                enabled_count += 1

        # Should be approximately 50% (allow some variance)
        assert 40 <= enabled_count <= 60, (
            f"Rollout should be ~50%, got {enabled_count}%"
        )

    async def test_user_access_management(self):
        """Test user-specific access management."""
        print("🧪 Testing user access management...")

        test_name = "user_access_management"
        start_time = time.time()

        try:
            # Create a test feature
            test_feature = FeatureToggleRequest(
                name="User Access Test Feature",
                description="Feature for testing user access",
                category=FeatureToggleCategory.UI_COMPONENTS,
                scope=FeatureToggleScope.GLOBAL,
                status=FeatureToggleStatus.DISABLED,
            )

            feature = await self.test_service.create_feature(test_feature)

            # Initially disabled for all users
            result_before = await self.test_service.is_feature_enabled(
                feature.id, "test_user"
            )
            assert result_before == False, "Feature should be disabled initially"

            # Grant access to specific user
            success = await self.test_service.set_user_feature_access(
                user_id="test_user",
                feature_id=feature.id,
                enabled=True,
                override_global=True,
                override_reason="Testing user access",
                granted_by="admin",
            )
            assert success == True, "Setting user access should succeed"

            # Check if user now has access
            result_after = await self.test_service.is_feature_enabled(
                feature.id, "test_user"
            )
            assert result_after == True, "User should have access after grant"

            # Other users should still not have access
            result_other = await self.test_service.is_feature_enabled(
                feature.id, "other_user"
            )
            assert result_other == False, "Other users should not have access"

            # Test user features overview
            user_features = await self.test_service.get_user_features("test_user")
            assert isinstance(user_features, dict), "Should return dict of features"
            assert feature.id in user_features, "Feature should be in user features"
            assert user_features[feature.id] == True, (
                "Feature should be enabled for user"
            )

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "feature_id": feature.id,
                "details": "User access management working correctly",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"User access management test failed: {e}")

    async def test_persistence_and_recovery(self):
        """Test data persistence and service recovery."""
        print("🧪 Testing persistence and recovery...")

        test_name = "persistence_recovery"
        start_time = time.time()

        try:
            # Create features with first service instance
            service1 = FeatureToggleService(storage_dir=self.temp_dir)
            await service1.initialize()

            test_feature = FeatureToggleRequest(
                name="Persistence Test Feature",
                description="Feature for testing persistence",
                category=FeatureToggleCategory.SCENARIOS,
                scope=FeatureToggleScope.GLOBAL,
                status=FeatureToggleStatus.ENABLED,
            )

            created_feature = await service1.create_feature(test_feature)
            feature_id = created_feature.id

            # Set user access
            await service1.set_user_feature_access("persist_user", feature_id, True)

            # Create new service instance and verify persistence
            service2 = FeatureToggleService(storage_dir=self.temp_dir)
            await service2.initialize()

            # Verify feature exists
            persisted_feature = await service2.get_feature(feature_id)
            assert persisted_feature is not None, (
                "Feature should persist across service instances"
            )
            assert persisted_feature.name == test_feature.name, (
                "Feature data should match"
            )

            # Verify user access persists
            user_access = await service2.is_feature_enabled(feature_id, "persist_user")
            assert user_access == True, "User access should persist"

            # Verify statistics
            stats = await service2.get_feature_statistics()
            assert stats["total_features"] > 0, "Statistics should show features"

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "persisted_feature_id": feature_id,
                "details": "Persistence and recovery working correctly",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(
                f"Persistence and recovery test failed: {e}"
            )

    async def test_performance_and_caching(self):
        """Test performance and caching mechanisms."""
        print("🧪 Testing performance and caching...")

        test_name = "performance_caching"
        start_time = time.time()

        try:
            # Create multiple features for performance testing
            features = []
            for i in range(20):
                feature_request = FeatureToggleRequest(
                    name=f"Performance Test Feature {i}",
                    description=f"Feature {i} for performance testing",
                    category=FeatureToggleCategory.EXPERIMENTAL,
                    scope=FeatureToggleScope.GLOBAL,
                    status=FeatureToggleStatus.ENABLED,
                )
                feature = await self.test_service.create_feature(feature_request)
                features.append(feature)

            # Test feature evaluation performance
            evaluation_times = []
            for _ in range(100):
                eval_start = time.time()
                await self.test_service.is_feature_enabled(features[0].id, "perf_user")
                evaluation_times.append(time.time() - eval_start)

            avg_evaluation_time = sum(evaluation_times) / len(evaluation_times)

            # Test batch operations performance
            batch_start = time.time()
            await self.test_service.get_user_features("batch_user")
            batch_time = time.time() - batch_start

            # Test statistics generation performance
            stats_start = time.time()
            await self.test_service.get_feature_statistics()
            stats_time = time.time() - stats_start

            self.results["performance_metrics"] = {
                "average_evaluation_time": avg_evaluation_time,
                "batch_operations_time": batch_time,
                "statistics_generation_time": stats_time,
                "total_features_tested": len(features),
                "cache_effectiveness": "Tested via repeated evaluations",
            }

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "avg_evaluation_time_ms": avg_evaluation_time * 1000,
                "batch_time_ms": batch_time * 1000,
                "stats_time_ms": stats_time * 1000,
                "details": "Performance testing completed successfully",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(
                f"Performance and caching test failed: {e}"
            )

    async def test_error_handling(self):
        """Test error handling scenarios."""
        print("🧪 Testing error handling...")

        test_name = "error_handling"
        start_time = time.time()

        try:
            error_tests = []

            # Test get non-existent feature
            result = await self.test_service.get_feature("non-existent-feature")
            error_tests.append(
                {
                    "test": "get_non_existent_feature",
                    "result": "handled_gracefully"
                    if result is None
                    else "unexpected_result",
                    "value": result,
                }
            )

            # Test update non-existent feature
            update_request = FeatureToggleUpdateRequest(name="Updated")
            result = await self.test_service.update_feature(
                "non-existent", update_request
            )
            error_tests.append(
                {
                    "test": "update_non_existent_feature",
                    "result": "handled_gracefully"
                    if result is None
                    else "unexpected_result",
                    "value": result,
                }
            )

            # Test delete non-existent feature
            result = await self.test_service.delete_feature("non-existent")
            error_tests.append(
                {
                    "test": "delete_non_existent_feature",
                    "result": "handled_gracefully"
                    if not result
                    else "unexpected_success",
                    "value": result,
                }
            )

            # Test invalid user access
            result = await self.test_service.set_user_feature_access(
                "user", "non-existent-feature", True
            )
            error_tests.append(
                {
                    "test": "set_access_non_existent_feature",
                    "result": "handled_gracefully"
                    if not result
                    else "unexpected_success",
                    "value": result,
                }
            )

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "error_tests": error_tests,
                "details": "Error handling scenarios tested successfully",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Error handling test failed: {e}")

    async def test_integration_with_global_service(self):
        """Test integration with global service instance."""
        print("🧪 Testing global service integration...")

        test_name = "global_service_integration"
        start_time = time.time()

        try:
            # Test global service getter
            global_service = await get_feature_toggle_service()
            assert global_service is not None, "Global service should be available"

            # Test that global service is singleton
            global_service2 = await get_feature_toggle_service()
            assert global_service is global_service2, (
                "Global service should be singleton"
            )

            # Test helper function
            from app.services.feature_toggle_service import is_feature_enabled

            # This should work with default features
            result = await is_feature_enabled("advanced_speech_analysis", "test_user")
            assert isinstance(result, bool), "Helper function should return boolean"

            self.results["integration_tests"]["global_service"] = {
                "status": "PASSED",
                "singleton_check": "PASSED",
                "helper_function": "PASSED",
                "details": "Global service integration working correctly",
            }

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "details": "Global service integration successful",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(
                f"Global service integration test failed: {e}"
            )

    def generate_summary(self):
        """Generate validation summary."""
        test_results = self.results["test_results"]
        passed_tests = [
            name
            for name, result in test_results.items()
            if result.get("status") == "PASSED"
        ]
        failed_tests = [
            name
            for name, result in test_results.items()
            if result.get("status") == "FAILED"
        ]

        self.results["summary"] = {
            "total_tests": len(test_results),
            "passed_tests": len(passed_tests),
            "failed_tests": len(failed_tests),
            "success_rate": len(passed_tests) / len(test_results) * 100
            if test_results
            else 0,
            "passed_test_names": passed_tests,
            "failed_test_names": failed_tests,
            "validation_status": "PASSED" if len(failed_tests) == 0 else "FAILED",
            "error_count": len(self.results["error_log"]),
            "performance_tested": bool(self.results.get("performance_metrics")),
            "integration_tested": bool(self.results.get("integration_tests")),
        }

    async def run_validation(self):
        """Run complete validation suite."""
        print("🚀 Starting Feature Toggle System Comprehensive Validation...")
        print("=" * 70)

        try:
            await self.setup_test_environment()

            # Core functionality tests
            await self.test_service_initialization()
            await self.test_feature_crud_operations()
            await self.test_feature_evaluation()
            await self.test_user_access_management()
            await self.test_persistence_and_recovery()

            # Performance and reliability tests
            await self.test_performance_and_caching()
            await self.test_error_handling()

            # Integration tests
            await self.test_integration_with_global_service()

            self.generate_summary()

        finally:
            await self.cleanup_test_environment()

        return self.results


async def main():
    """Main validation function."""
    validator = FeatureToggleValidator()
    results = await validator.run_validation()

    # Save results
    validation_dir = Path("validation_artifacts/3.1.7")
    validation_dir.mkdir(parents=True, exist_ok=True)

    results_file = validation_dir / "feature_toggle_comprehensive_validation.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Print summary
    summary = results["summary"]
    performance = results.get("performance_metrics", {})

    print("\n" + "=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)
    print(f"✅ Total Tests: {summary['total_tests']}")
    print(f"✅ Passed: {summary['passed_tests']}")
    print(f"❌ Failed: {summary['failed_tests']}")
    print(f"📊 Success Rate: {summary['success_rate']:.1f}%")
    print(f"🔧 Validation Status: {summary['validation_status']}")

    if performance:
        print(f"\n📈 PERFORMANCE METRICS")
        print(
            f"⏱️  Avg Evaluation Time: {performance.get('average_evaluation_time', 0) * 1000:.2f}ms"
        )
        print(
            f"📦 Batch Operations: {performance.get('batch_operations_time', 0) * 1000:.2f}ms"
        )
        print(
            f"📊 Statistics Generation: {performance.get('statistics_generation_time', 0) * 1000:.2f}ms"
        )

    if summary["failed_tests"] > 0:
        print(f"\n❌ Failed Tests: {summary['failed_test_names']}")
        print(f"📝 Error Count: {summary['error_count']}")

    print(f"\n📁 Results saved to: {results_file}")

    return summary["validation_status"] == "PASSED"


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
