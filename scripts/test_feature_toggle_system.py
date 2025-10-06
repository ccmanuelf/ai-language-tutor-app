#!/usr/bin/env python3
"""
Comprehensive Feature Toggle System Test Suite
AI Language Tutor App - Task 3.1.4 Validation

Tests all components of the feature toggle system:
- Feature Toggle Manager service
- Database operations
- API endpoints
- Admin interface integration
- Service decorators and utilities

Author: AI Assistant
Date: 2025-09-27
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any
import logging

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.feature_toggle_manager import (
    FeatureToggleManager,
    FeatureToggle,
    feature_toggle_manager,
    is_feature_enabled,
    get_feature,
    get_features_by_category,
)
from app.decorators.feature_toggle import (
    feature_gate,
    FeatureToggleService,
    check_content_processing,
    check_real_time_analysis,
    FeatureContext,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureToggleSystemTests:
    """Comprehensive test suite for feature toggle system"""

    def __init__(self):
        """Initialize test environment"""
        self.db_path = "data/ai_language_tutor.db"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_categories": {},
            "detailed_results": [],
        }

        # Test feature for temporary operations
        self.test_feature_name = "test_feature_toggle_validation"

        logger.info("Feature Toggle System Test Suite initialized")

    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""

        logger.info("🚀 Starting Feature Toggle System Comprehensive Tests")
        print("=" * 60)

        test_categories = [
            ("Database Operations", self.test_database_operations),
            ("Feature Toggle Manager", self.test_feature_toggle_manager),
            ("Service Integration", self.test_service_integration),
            ("Permission System", self.test_permission_system),
            ("Configuration Management", self.test_configuration_management),
            ("Decorators and Utilities", self.test_decorators_utilities),
            ("Caching System", self.test_caching_system),
            ("Error Handling", self.test_error_handling),
            ("Performance Tests", self.test_performance),
            ("Integration Tests", self.test_integration),
        ]

        for category_name, test_function in test_categories:
            logger.info(f"\n📋 Running {category_name} Tests...")
            print(f"\n📋 {category_name} Tests:")
            print("-" * 40)

            try:
                category_results = test_function()
                self.test_results["test_categories"][category_name] = category_results

                # Update totals
                self.test_results["total_tests"] += category_results["total"]
                self.test_results["passed_tests"] += category_results["passed"]
                self.test_results["failed_tests"] += category_results["failed"]

                print(
                    f"✅ {category_name}: {category_results['passed']}/{category_results['total']} passed"
                )

            except Exception as e:
                logger.error(f"❌ {category_name} failed with error: {e}")
                self.test_results["test_categories"][category_name] = {
                    "total": 1,
                    "passed": 0,
                    "failed": 1,
                    "error": str(e),
                }
                self.test_results["total_tests"] += 1
                self.test_results["failed_tests"] += 1

        return self.test_results

    def test_database_operations(self) -> Dict[str, Any]:
        """Test database connectivity and operations"""
        results = {"total": 0, "passed": 0, "failed": 0, "tests": []}

        def run_test(test_name: str, test_func):
            results["total"] += 1
            try:
                test_func()
                results["passed"] += 1
                results["tests"].append({"name": test_name, "status": "PASSED"})
                print(f"  ✅ {test_name}")
            except Exception as e:
                results["failed"] += 1
                results["tests"].append(
                    {"name": test_name, "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {test_name}: {e}")

        # Test 1: Database connection
        def test_db_connection():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='admin_feature_toggles'"
            )
            result = cursor.fetchone()
            conn.close()
            assert result is not None, "admin_feature_toggles table not found"

        run_test("Database Connection", test_db_connection)

        # Test 2: Table schema validation
        def test_table_schema():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(admin_feature_toggles)")
            columns = cursor.fetchall()
            conn.close()

            expected_columns = [
                "id",
                "feature_name",
                "is_enabled",
                "description",
                "category",
                "requires_restart",
                "min_role",
                "configuration",
                "created_at",
                "updated_at",
            ]
            actual_columns = [col[1] for col in columns]

            for expected_col in expected_columns:
                assert expected_col in actual_columns, f"Missing column: {expected_col}"

        run_test("Table Schema Validation", test_table_schema)

        # Test 3: Data integrity check
        def test_data_integrity():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM admin_feature_toggles")
            count = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM admin_feature_toggles WHERE feature_name IS NOT NULL"
            )
            valid_count = cursor.fetchone()[0]
            conn.close()

            assert count > 0, "No features found in database"
            assert count == valid_count, "Found features with NULL names"

        run_test("Data Integrity Check", test_data_integrity)

        # Test 4: Required features exist
        def test_required_features():
            required_features = [
                "content_processing",
                "conversation_chat",
                "real_time_analysis",
                "tutor_modes",
                "scenario_modes",
                "speech_recognition",
                "text_to_speech",
            ]

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for feature in required_features:
                cursor.execute(
                    "SELECT COUNT(*) FROM admin_feature_toggles WHERE feature_name = ?",
                    (feature,),
                )
                count = cursor.fetchone()[0]
                assert count > 0, f"Required feature '{feature}' not found"

            conn.close()

        run_test("Required Features Exist", test_required_features)

        return results

    def test_feature_toggle_manager(self) -> Dict[str, Any]:
        """Test Feature Toggle Manager service"""
        results = {"total": 0, "passed": 0, "failed": 0, "tests": []}

        def run_test(test_name: str, test_func):
            results["total"] += 1
            try:
                test_func()
                results["passed"] += 1
                results["tests"].append({"name": test_name, "status": "PASSED"})
                print(f"  ✅ {test_name}")
            except Exception as e:
                results["failed"] += 1
                results["tests"].append(
                    {"name": test_name, "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {test_name}: {e}")

        # Test 1: Manager initialization
        def test_manager_init():
            manager = FeatureToggleManager()
            assert hasattr(manager, "_cache"), "Manager cache not initialized"
            assert len(manager._cache) > 0, "Cache is empty after initialization"

        run_test("Manager Initialization", test_manager_init)

        # Test 2: Feature existence check
        def test_feature_check():
            enabled = feature_toggle_manager.is_feature_enabled("content_processing")
            assert isinstance(enabled, bool), "Feature check should return boolean"

            # Test with invalid feature
            invalid_enabled = feature_toggle_manager.is_feature_enabled(
                "nonexistent_feature"
            )
            assert not invalid_enabled, "Invalid features should return False"

        run_test("Feature Existence Check", test_feature_check)

        # Test 3: Role permission system
        def test_role_permissions():
            # Test admin access
            admin_enabled = feature_toggle_manager.is_feature_enabled(
                "user_management", "ADMIN"
            )
            assert admin_enabled, "Admin should have access to user_management"

            # Test child access to admin feature
            child_enabled = feature_toggle_manager.is_feature_enabled(
                "user_management", "CHILD"
            )
            assert not child_enabled, (
                "Child should not have access to admin features"
            )

        run_test("Role Permission System", test_role_permissions)

        # Test 4: Get all features
        def test_get_all_features():
            features = feature_toggle_manager.get_all_features(user_role="ADMIN")
            assert isinstance(features, dict), "get_all_features should return dict"
            assert len(features) > 0, "Should return some features"

            # Check feature object structure
            first_feature = next(iter(features.values()))
            assert hasattr(first_feature, "feature_name"), (
                "Feature should have feature_name"
            )
            assert hasattr(first_feature, "is_enabled"), (
                "Feature should have is_enabled"
            )

        run_test("Get All Features", test_get_all_features)

        # Test 5: Features by category
        def test_features_by_category():
            categories = feature_toggle_manager.get_features_by_category("ADMIN")
            assert isinstance(categories, dict), "Should return dict of categories"
            assert len(categories) > 0, "Should have some categories"

            # Check category structure
            for category, features in categories.items():
                assert isinstance(features, list), (
                    f"Category {category} should contain list"
                )
                if features:
                    assert hasattr(features[0], "category"), (
                        "Feature should have category"
                    )

        run_test("Features by Category", test_features_by_category)

        # Test 6: Feature configuration
        def test_feature_configuration():
            feature = feature_toggle_manager.get_feature("content_processing")
            assert feature is not None, "content_processing feature should exist"
            assert hasattr(feature, "configuration"), (
                "Feature should have configuration"
            )
            assert isinstance(feature.configuration, dict), (
                "Configuration should be dict"
            )

        run_test("Feature Configuration", test_feature_configuration)

        return results

    def test_service_integration(self) -> Dict[str, Any]:
        """Test integration with core services"""
        results = {"total": 0, "passed": 0, "failed": 0, "tests": []}

        def run_test(test_name: str, test_func):
            results["total"] += 1
            try:
                test_func()
                results["passed"] += 1
                results["tests"].append({"name": test_name, "status": "PASSED"})
                print(f"  ✅ {test_name}")
            except Exception as e:
                results["failed"] += 1
                results["tests"].append(
                    {"name": test_name, "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {test_name}: {e}")

        # Test 1: Global functions work
        def test_global_functions():
            # Test convenience functions
            result1 = is_feature_enabled("content_processing")
            assert isinstance(result1, bool), "is_feature_enabled should return boolean"

            result2 = get_feature("content_processing")
            assert not result2 is not None or result1, (
                "get_feature should return feature or None"
            )

            result3 = get_features_by_category()
            assert isinstance(result3, dict), (
                "get_features_by_category should return dict"
            )

        run_test("Global Functions", test_global_functions)

        # Test 2: Service integration functions
        def test_service_functions():
            # Test convenience check functions
            cp_enabled = check_content_processing()
            assert isinstance(cp_enabled, bool), (
                "check_content_processing should return boolean"
            )

            rta_enabled = check_real_time_analysis()
            assert isinstance(rta_enabled, bool), (
                "check_real_time_analysis should return boolean"
            )

        run_test("Service Integration Functions", test_service_functions)

        # Test 3: Feature context manager
        def test_feature_context():
            with FeatureContext("content_processing", silent=True) as enabled:
                assert isinstance(enabled, bool), "Context should return boolean"

            # Test with invalid feature
            with FeatureContext("invalid_feature", silent=True) as enabled:
                assert not enabled, "Invalid feature should return False"

        run_test("Feature Context Manager", test_feature_context)

        return results

    def test_permission_system(self) -> Dict[str, Any]:
        """Test role-based permission system"""
        results = {"total": 0, "passed": 0, "failed": 0, "tests": []}

        def run_test(test_name: str, test_func):
            results["total"] += 1
            try:
                test_func()
                results["passed"] += 1
                results["tests"].append({"name": test_name, "status": "PASSED"})
                print(f"  ✅ {test_name}")
            except Exception as e:
                results["failed"] += 1
                results["tests"].append(
                    {"name": test_name, "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {test_name}: {e}")

        # Test 1: Role hierarchy
        def test_role_hierarchy():
            # Admin should access everything
            admin_features = feature_toggle_manager.get_all_features(user_role="ADMIN")

            # Child should access fewer features
            child_features = feature_toggle_manager.get_all_features(user_role="CHILD")

            # Parent should be between admin and child
            parent_features = feature_toggle_manager.get_all_features(
                user_role="PARENT"
            )

            assert len(admin_features) >= len(parent_features), (
                "Admin should have at least as many features as parent"
            )
            assert len(parent_features) >= len(child_features), (
                "Parent should have at least as many features as child"
            )

        run_test("Role Hierarchy", test_role_hierarchy)

        # Test 2: Admin-only features
        def test_admin_only_features():
            admin_only_features = [
                "user_management",
                "feature_toggles",
                "system_monitoring",
            ]

            for feature in admin_only_features:
                admin_access = feature_toggle_manager.is_feature_enabled(
                    feature, "ADMIN"
                )
                child_access = feature_toggle_manager.is_feature_enabled(
                    feature, "CHILD"
                )

                assert admin_access, f"Admin should have access to {feature}"
                assert not child_access, (
                    f"Child should not have access to {feature}"
                )

        run_test("Admin-Only Features", test_admin_only_features)

        # Test 3: Child accessible features
        def test_child_accessible_features():
            child_features = [
                "content_processing",
                "conversation_chat",
                "speech_recognition",
            ]

            for feature in child_features:
                child_access = feature_toggle_manager.is_feature_enabled(
                    feature, "CHILD"
                )
                assert child_access, f"Child should have access to {feature}"

        run_test("Child Accessible Features", test_child_accessible_features)

        return results

    def test_configuration_management(self) -> Dict[str, Any]:
        """Test configuration and update operations"""
        results = {"total": 0, "passed": 0, "failed": 0, "tests": []}

        def run_test(test_name: str, test_func):
            results["total"] += 1
            try:
                test_func()
                results["passed"] += 1
                results["tests"].append({"name": test_name, "status": "PASSED"})
                print(f"  ✅ {test_name}")
            except Exception as e:
                results["failed"] += 1
                results["tests"].append(
                    {"name": test_name, "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {test_name}: {e}")

        # Test 1: Feature update
        def test_feature_update():
            # Create a test feature first
            test_feature = FeatureToggle(
                feature_name=self.test_feature_name,
                is_enabled=True,
                description="Test feature for validation",
                category="testing",
            )

            # Create the feature
            created = feature_toggle_manager.create_feature(test_feature)
            assert created, "Should be able to create test feature"

            # Update the feature
            updated = feature_toggle_manager.update_feature(
                self.test_feature_name,
                is_enabled=False,
                description="Updated test feature",
            )
            assert updated, "Should be able to update feature"

            # Verify update
            feature = feature_toggle_manager.get_feature(self.test_feature_name)
            assert feature is not None, "Feature should exist after update"
            assert not feature.is_enabled, (
                "Feature should be disabled after update"
            )
            assert "Updated" in feature.description, "Description should be updated"

            # Clean up - delete test feature
            deleted = feature_toggle_manager.delete_feature(self.test_feature_name)
            assert deleted, "Should be able to delete test feature"

        run_test("Feature Update Operations", test_feature_update)

        # Test 2: Bulk operations
        def test_bulk_operations():
            # Get some features for bulk test
            features = feature_toggle_manager.get_all_features(user_role="ADMIN")
            if len(features) < 2:
                raise Exception("Need at least 2 features for bulk test")

            # Take first 2 features
            feature_names = list(features.keys())[:2]
            original_states = {
                name: features[name].is_enabled for name in feature_names
            }

            # Bulk update
            updates = {name: not original_states[name] for name in feature_names}
            results = feature_toggle_manager.bulk_update_features(updates)

            assert all(results.values()), "All bulk updates should succeed"

            # Verify changes
            for name in feature_names:
                feature = feature_toggle_manager.get_feature(name)
                assert feature.is_enabled == updates[name], (
                    f"Feature {name} should be updated"
                )

            # Restore original states
            restore_updates = original_states
            feature_toggle_manager.bulk_update_features(restore_updates)

        run_test("Bulk Operations", test_bulk_operations)

        # Test 3: Configuration export/import
        def test_export_import():
            # Export configuration
            config = feature_toggle_manager.export_configuration()
            assert isinstance(config, dict), "Export should return dict"
            assert "features" in config, "Export should contain features"
            assert "export_timestamp" in config, "Export should contain timestamp"

            # Test import (dry run)
            sample_config = {
                "features": {
                    "content_processing": {
                        "is_enabled": True,
                        "description": "Test import",
                        "configuration": {"test": True},
                    }
                }
            }

            import_results = feature_toggle_manager.import_configuration(sample_config)
            assert isinstance(import_results, dict), "Import should return results dict"

        run_test("Export/Import Configuration", test_export_import)

        return results

    def test_decorators_utilities(self) -> Dict[str, Any]:
        """Test decorator and utility functions"""
        results = {"total": 0, "passed": 0, "failed": 0, "tests": []}

        def run_test(test_name: str, test_func):
            results["total"] += 1
            try:
                test_func()
                results["passed"] += 1
                results["tests"].append({"name": test_name, "status": "PASSED"})
                print(f"  ✅ {test_name}")
            except Exception as e:
                results["failed"] += 1
                results["tests"].append(
                    {"name": test_name, "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {test_name}: {e}")

        # Test 1: Feature gate decorator
        def test_feature_gate_decorator():
            @feature_gate("content_processing")
            def test_function():
                return "function executed"

            # Check that decorator adds enabled property
            assert hasattr(test_function, "enabled"), (
                "Decorator should add enabled property"
            )
            assert hasattr(test_function, "feature_name"), (
                "Decorator should add feature_name property"
            )
            assert test_function.feature_name == "content_processing", (
                "Feature name should be correct"
            )

            # Function should still work
            result = test_function()
            assert result == "function executed", "Function should execute normally"

        run_test("Feature Gate Decorator", test_feature_gate_decorator)

        # Test 2: FeatureToggleService class
        def test_feature_toggle_service():
            service = FeatureToggleService("CHILD")

            # Test basic check
            enabled = service.is_enabled("content_processing")
            assert isinstance(enabled, bool), "Service check should return boolean"

            # Test enabled features filter
            test_features = [
                "content_processing",
                "nonexistent_feature",
                "conversation_chat",
            ]
            enabled_features = service.get_enabled_features(test_features)
            assert isinstance(enabled_features, list), "Should return list"
            assert "nonexistent_feature" not in enabled_features, (
                "Disabled features should be filtered out"
            )

            # Test conditional execute
            def test_func():
                return "executed"

            result = service.conditional_execute(
                "content_processing", test_func, "fallback"
            )
            assert result in ["executed", "fallback"], (
                "Should return function result or fallback"
            )

        run_test("FeatureToggleService Class", test_feature_toggle_service)

        return results

    def test_caching_system(self) -> Dict[str, Any]:
        """Test caching functionality"""
        results = {"total": 0, "passed": 0, "failed": 0, "tests": []}

        def run_test(test_name: str, test_func):
            results["total"] += 1
            try:
                test_func()
                results["passed"] += 1
                results["tests"].append({"name": test_name, "status": "PASSED"})
                print(f"  ✅ {test_name}")
            except Exception as e:
                results["failed"] += 1
                results["tests"].append(
                    {"name": test_name, "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {test_name}: {e}")

        # Test 1: Cache initialization
        def test_cache_init():
            manager = FeatureToggleManager()
            assert hasattr(manager, "_cache"), "Manager should have cache"
            assert hasattr(manager, "_last_cache_update"), (
                "Manager should track cache update time"
            )
            assert len(manager._cache) > 0, "Cache should be populated"

        run_test("Cache Initialization", test_cache_init)

        # Test 2: Cache refresh
        def test_cache_refresh():
            manager = FeatureToggleManager()
            original_time = manager._last_cache_update

            # Force cache refresh
            manager._refresh_cache()

            new_time = manager._last_cache_update
            assert new_time != original_time, "Cache timestamp should update"

        run_test("Cache Refresh", test_cache_refresh)

        return results

    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and edge cases"""
        results = {"total": 0, "passed": 0, "failed": 0, "tests": []}

        def run_test(test_name: str, test_func):
            results["total"] += 1
            try:
                test_func()
                results["passed"] += 1
                results["tests"].append({"name": test_name, "status": "PASSED"})
                print(f"  ✅ {test_name}")
            except Exception as e:
                results["failed"] += 1
                results["tests"].append(
                    {"name": test_name, "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {test_name}: {e}")

        # Test 1: Invalid feature names
        def test_invalid_features():
            # Should return False for non-existent features
            enabled = feature_toggle_manager.is_feature_enabled("nonexistent_feature")
            assert not enabled, "Non-existent features should return False"

            feature = feature_toggle_manager.get_feature("nonexistent_feature")
            assert feature is None, "Non-existent features should return None"

        run_test("Invalid Feature Names", test_invalid_features)

        # Test 2: Invalid roles
        def test_invalid_roles():
            # Should handle invalid roles gracefully
            enabled = feature_toggle_manager.is_feature_enabled(
                "content_processing", "INVALID_ROLE"
            )
            assert not enabled, "Invalid roles should return False"

        run_test("Invalid Roles", test_invalid_roles)

        # Test 3: Empty inputs
        def test_empty_inputs():
            enabled = feature_toggle_manager.is_feature_enabled("")
            assert not enabled, "Empty feature name should return False"

            feature = feature_toggle_manager.get_feature("")
            assert feature is None, "Empty feature name should return None"

        run_test("Empty Inputs", test_empty_inputs)

        return results

    def test_performance(self) -> Dict[str, Any]:
        """Test performance of feature toggle operations"""
        results = {"total": 0, "passed": 0, "failed": 0, "tests": []}

        def run_test(test_name: str, test_func):
            results["total"] += 1
            try:
                test_func()
                results["passed"] += 1
                results["tests"].append({"name": test_name, "status": "PASSED"})
                print(f"  ✅ {test_name}")
            except Exception as e:
                results["failed"] += 1
                results["tests"].append(
                    {"name": test_name, "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {test_name}: {e}")

        # Test 1: Bulk feature checks
        def test_bulk_checks():
            import time

            start_time = time.time()

            # Perform many feature checks
            for _ in range(100):
                feature_toggle_manager.is_feature_enabled("content_processing")
                feature_toggle_manager.is_feature_enabled("conversation_chat")
                feature_toggle_manager.is_feature_enabled("real_time_analysis")

            end_time = time.time()
            duration = end_time - start_time

            # Should complete 300 checks in under 1 second (caching effect)
            assert duration < 1.0, (
                f"300 feature checks took {duration:.3f}s, should be under 1s"
            )

        run_test("Bulk Feature Checks Performance", test_bulk_checks)

        # Test 2: Memory usage
        def test_memory_usage():
            import sys

            # Check cache size is reasonable
            manager = FeatureToggleManager()
            cache_size = sys.getsizeof(manager._cache)

            # Cache should be under 100KB for typical usage
            assert cache_size < 100 * 1024, (
                f"Cache size {cache_size} bytes is too large"
            )

        run_test("Memory Usage", test_memory_usage)

        return results

    def test_integration(self) -> Dict[str, Any]:
        """Test integration with other system components"""
        results = {"total": 0, "passed": 0, "failed": 0, "tests": []}

        def run_test(test_name: str, test_func):
            results["total"] += 1
            try:
                test_func()
                results["passed"] += 1
                results["tests"].append({"name": test_name, "status": "PASSED"})
                print(f"  ✅ {test_name}")
            except Exception as e:
                results["failed"] += 1
                results["tests"].append(
                    {"name": test_name, "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {test_name}: {e}")

        # Test 1: Statistics generation
        def test_statistics():
            stats = feature_toggle_manager.get_feature_statistics()
            assert isinstance(stats, dict), "Statistics should return dict"
            assert "total_features" in stats, "Should include total_features"
            assert "enabled_features" in stats, "Should include enabled_features"
            assert "categories" in stats, "Should include categories breakdown"
            assert stats["total_features"] > 0, "Should have some features"

        run_test("Statistics Generation", test_statistics)

        # Test 2: Feature categories validation
        def test_categories_validation():
            categories = feature_toggle_manager.get_features_by_category("ADMIN")

            expected_categories = [
                "learning",
                "speech",
                "admin",
                "access",
                "performance",
            ]

            for category in expected_categories:
                assert category in categories, f"Category {category} should exist"

        run_test("Feature Categories Validation", test_categories_validation)

        return results

    def generate_report(self) -> None:
        """Generate comprehensive test report"""
        results = self.test_results

        print("\n" + "=" * 60)
        print("🎯 FEATURE TOGGLE SYSTEM TEST RESULTS")
        print("=" * 60)

        print("📊 Overall Results:")
        print(f"   Total Tests: {results['total_tests']}")
        print(f"   Passed: {results['passed_tests']} ✅")
        print(f"   Failed: {results['failed_tests']} ❌")
        print(
            f"   Success Rate: {(results['passed_tests'] / results['total_tests'] * 100):.1f}%"
        )

        print("\n📋 Category Breakdown:")
        for category, category_results in results["test_categories"].items():
            status = "✅" if category_results["failed"] == 0 else "❌"
            print(
                f"   {status} {category}: {category_results['passed']}/{category_results['total']}"
            )

        print(f"\n⏰ Test completed at: {results['timestamp']}")

        # Save detailed results
        output_file = "validation_artifacts/3.1.4/feature_toggle_tests.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"📁 Detailed results saved to: {output_file}")

        # Determine overall status
        if results["failed_tests"] == 0:
            print(
                "\n🎉 ALL TESTS PASSED! Feature Toggle System is ready for production."
            )
            return True
        else:
            print(
                f"\n⚠️  {results['failed_tests']} tests failed. Review results before proceeding."
            )
            return False


def main():
    """Main test execution function"""
    print("🚀 Feature Toggle System Comprehensive Test Suite")
    print("=" * 60)

    # Initialize test suite
    test_suite = FeatureToggleSystemTests()

    try:
        # Run all tests
        test_suite.run_all_tests()

        # Generate report
        success = test_suite.generate_report()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"Test suite failed with error: {e}")
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
