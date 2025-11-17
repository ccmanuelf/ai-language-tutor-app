"""
Comprehensive tests for Feature Toggle Manager
AI Language Tutor App - Feature flag system testing

Tests cover:
- Enum definitions (FeatureCategory, UserRole)
- Dataclass (FeatureToggle)
- Manager initialization and database setup
- Cache management (refresh, TTL)
- Feature checking (enabled/disabled, role permissions)
- Feature retrieval (single, all, by category)
- CRUD operations (create, update, delete)
- Statistics and analytics
- Bulk operations
- Import/Export functionality
- Global instance and convenience functions
"""

import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.feature_toggle_manager import (
    FeatureCategory,
    FeatureToggle,
    FeatureToggleManager,
    UserRole,
    feature_toggle_manager,
    get_feature,
    get_features_by_category,
    is_feature_enabled,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    # Create feature toggles table
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE admin_feature_toggles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_name TEXT UNIQUE NOT NULL,
            is_enabled INTEGER DEFAULT 1,
            description TEXT,
            category TEXT DEFAULT 'general',
            requires_restart INTEGER DEFAULT 0,
            min_role TEXT DEFAULT 'CHILD',
            configuration TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def manager(temp_db):
    """Create a FeatureToggleManager instance with temp database"""
    return FeatureToggleManager(db_path=temp_db)


@pytest.fixture
def sample_feature():
    """Create a sample feature toggle"""
    return FeatureToggle(
        feature_name="test_feature",
        is_enabled=True,
        description="Test feature",
        category="general",
        requires_restart=False,
        min_role="CHILD",
        configuration={"key": "value"},
    )


# ============================================================================
# Test Enums
# ============================================================================


class TestEnums:
    """Test enum definitions"""

    def test_feature_category_enum(self):
        """Test FeatureCategory enum values"""
        assert FeatureCategory.LEARNING.value == "learning"
        assert FeatureCategory.SPEECH.value == "speech"
        assert FeatureCategory.ADMIN.value == "admin"
        assert FeatureCategory.ACCESS.value == "access"
        assert FeatureCategory.PERFORMANCE.value == "performance"
        assert FeatureCategory.GENERAL.value == "general"

    def test_user_role_enum(self):
        """Test UserRole enum values"""
        assert UserRole.CHILD.value == "CHILD"
        assert UserRole.PARENT.value == "PARENT"
        assert UserRole.ADMIN.value == "ADMIN"


# ============================================================================
# Test FeatureToggle Dataclass
# ============================================================================


class TestFeatureToggleDataclass:
    """Test FeatureToggle dataclass"""

    def test_feature_toggle_with_all_fields(self):
        """Test creating FeatureToggle with all fields"""
        feature = FeatureToggle(
            id=1,
            feature_name="test_feature",
            is_enabled=True,
            description="Test description",
            category="learning",
            requires_restart=True,
            min_role="PARENT",
            configuration={"setting": "value"},
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-02T00:00:00",
        )

        assert feature.id == 1
        assert feature.feature_name == "test_feature"
        assert feature.is_enabled is True
        assert feature.description == "Test description"
        assert feature.category == "learning"
        assert feature.requires_restart is True
        assert feature.min_role == "PARENT"
        assert feature.configuration == {"setting": "value"}
        assert feature.created_at == "2025-01-01T00:00:00"
        assert feature.updated_at == "2025-01-02T00:00:00"

    def test_feature_toggle_with_defaults(self):
        """Test FeatureToggle with default values"""
        feature = FeatureToggle()

        assert feature.id is None
        assert feature.feature_name == ""
        assert feature.is_enabled is True
        assert feature.description == ""
        assert feature.category == "general"
        assert feature.requires_restart is False
        assert feature.min_role == "CHILD"
        assert feature.configuration == {}
        assert feature.created_at is None
        assert feature.updated_at is None

    def test_feature_toggle_configuration_none_initialization(self):
        """Test that None configuration is initialized to empty dict"""
        feature = FeatureToggle(
            feature_name="test",
            configuration=None,
        )

        assert feature.configuration == {}


# ============================================================================
# Test Manager Initialization
# ============================================================================


class TestManagerInitialization:
    """Test FeatureToggleManager initialization"""

    def test_manager_initialization_success(self, temp_db):
        """Test successful manager initialization"""
        manager = FeatureToggleManager(db_path=temp_db)

        assert manager.db_path == temp_db
        assert isinstance(manager._cache, dict)
        assert manager.cache_ttl == 300
        assert manager._last_cache_update is not None

    def test_manager_initialization_with_existing_features(self, temp_db):
        """Test initialization loads existing features into cache"""
        # Add a feature to the database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO admin_feature_toggles
            (feature_name, is_enabled, description, category, min_role, configuration)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            ("test_feature", 1, "Test", "general", "CHILD", "{}"),
        )
        conn.commit()
        conn.close()

        manager = FeatureToggleManager(db_path=temp_db)

        assert len(manager._cache) == 1
        assert "test_feature" in manager._cache

    def test_manager_get_connection(self, manager):
        """Test database connection creation"""
        conn = manager._get_connection()

        assert isinstance(conn, sqlite3.Connection)
        assert conn.row_factory == sqlite3.Row

        conn.close()


# ============================================================================
# Test Cache Management
# ============================================================================


class TestCacheManagement:
    """Test cache refresh and TTL logic"""

    def test_refresh_cache_loads_features(self, manager, temp_db):
        """Test that refresh_cache loads features from database"""
        # Add features to database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO admin_feature_toggles
            (feature_name, is_enabled, description, configuration)
            VALUES (?, ?, ?, ?)
        """,
            ("feature1", 1, "Feature 1", '{"key": "value"}'),
        )
        conn.commit()
        conn.close()

        manager._refresh_cache()

        assert len(manager._cache) == 1
        assert "feature1" in manager._cache
        assert manager._cache["feature1"].is_enabled is True

    def test_refresh_cache_parses_json_configuration(self, manager, temp_db):
        """Test that JSON configuration is properly parsed"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO admin_feature_toggles
            (feature_name, configuration)
            VALUES (?, ?)
        """,
            ("feature1", '{"setting1": "value1", "setting2": 123}'),
        )
        conn.commit()
        conn.close()

        manager._refresh_cache()

        feature = manager._cache["feature1"]
        assert feature.configuration == {"setting1": "value1", "setting2": 123}

    def test_refresh_cache_handles_invalid_json(self, manager, temp_db):
        """Test that invalid JSON configuration defaults to empty dict"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO admin_feature_toggles
            (feature_name, configuration)
            VALUES (?, ?)
        """,
            ("feature1", "invalid json"),
        )
        conn.commit()
        conn.close()

        manager._refresh_cache()

        feature = manager._cache["feature1"]
        assert feature.configuration == {}

    def test_should_refresh_cache_when_never_updated(self, manager):
        """Test that cache should refresh when never updated"""
        manager._last_cache_update = None

        assert manager._should_refresh_cache() is True

    def test_should_refresh_cache_when_expired(self, manager):
        """Test that cache should refresh when TTL expired"""
        manager._last_cache_update = datetime.now() - timedelta(seconds=400)
        manager.cache_ttl = 300

        assert manager._should_refresh_cache() is True

    def test_should_not_refresh_cache_when_fresh(self, manager):
        """Test that cache should not refresh when still fresh"""
        manager._last_cache_update = datetime.now()
        manager.cache_ttl = 300

        assert manager._should_refresh_cache() is False


# ============================================================================
# Test Feature Checking
# ============================================================================


class TestFeatureChecking:
    """Test feature enabled/disabled checking"""

    def test_is_feature_enabled_returns_true_for_enabled_feature(
        self, manager, sample_feature
    ):
        """Test that enabled feature returns True"""
        manager.create_feature(sample_feature)

        assert manager.is_feature_enabled("test_feature", "CHILD") is True

    def test_is_feature_enabled_returns_false_for_disabled_feature(
        self, manager, sample_feature
    ):
        """Test that disabled feature returns False"""
        sample_feature.is_enabled = False
        manager.create_feature(sample_feature)

        assert manager.is_feature_enabled("test_feature", "CHILD") is False

    def test_is_feature_enabled_returns_false_for_nonexistent_feature(self, manager):
        """Test that nonexistent feature returns False"""
        assert manager.is_feature_enabled("nonexistent_feature", "CHILD") is False

    def test_is_feature_enabled_checks_role_permission(self, manager, sample_feature):
        """Test that role permission is checked"""
        sample_feature.min_role = "PARENT"
        manager.create_feature(sample_feature)

        # CHILD should not have access
        assert manager.is_feature_enabled("test_feature", "CHILD") is False

        # PARENT should have access
        assert manager.is_feature_enabled("test_feature", "PARENT") is True

        # ADMIN should have access
        assert manager.is_feature_enabled("test_feature", "ADMIN") is True

    def test_is_feature_enabled_refreshes_cache_when_stale(self, manager):
        """Test that stale cache is refreshed"""
        manager._last_cache_update = datetime.now() - timedelta(seconds=400)
        manager.cache_ttl = 300

        with patch.object(manager, "_refresh_cache") as mock_refresh:
            manager.is_feature_enabled("test_feature")
            mock_refresh.assert_called_once()


# ============================================================================
# Test Role Permission Checking
# ============================================================================


class TestRolePermissionChecking:
    """Test role hierarchy permission checking"""

    def test_check_role_permission_child_can_access_child_features(self, manager):
        """Test CHILD can access CHILD-level features"""
        assert manager._check_role_permission("CHILD", "CHILD") is True

    def test_check_role_permission_child_cannot_access_parent_features(self, manager):
        """Test CHILD cannot access PARENT-level features"""
        assert manager._check_role_permission("CHILD", "PARENT") is False

    def test_check_role_permission_parent_can_access_child_features(self, manager):
        """Test PARENT can access CHILD-level features"""
        assert manager._check_role_permission("PARENT", "CHILD") is True

    def test_check_role_permission_parent_can_access_parent_features(self, manager):
        """Test PARENT can access PARENT-level features"""
        assert manager._check_role_permission("PARENT", "PARENT") is True

    def test_check_role_permission_admin_can_access_all_features(self, manager):
        """Test ADMIN can access all features"""
        assert manager._check_role_permission("ADMIN", "CHILD") is True
        assert manager._check_role_permission("ADMIN", "PARENT") is True
        assert manager._check_role_permission("ADMIN", "ADMIN") is True

    def test_check_role_permission_case_insensitive(self, manager):
        """Test role permission check is case-insensitive"""
        assert manager._check_role_permission("child", "CHILD") is True
        assert manager._check_role_permission("PARENT", "parent") is True


# ============================================================================
# Test Feature Retrieval
# ============================================================================


class TestFeatureRetrieval:
    """Test getting feature information"""

    def test_get_feature_returns_feature(self, manager, sample_feature):
        """Test get_feature returns the correct feature"""
        manager.create_feature(sample_feature)

        feature = manager.get_feature("test_feature")

        assert feature is not None
        assert feature.feature_name == "test_feature"
        assert feature.description == "Test feature"

    def test_get_feature_returns_none_for_nonexistent(self, manager):
        """Test get_feature returns None for nonexistent feature"""
        feature = manager.get_feature("nonexistent")

        assert feature is None

    def test_get_all_features_returns_all_features(self, manager):
        """Test get_all_features returns all features"""
        manager.create_feature(
            FeatureToggle(feature_name="feature1", category="learning")
        )
        manager.create_feature(
            FeatureToggle(feature_name="feature2", category="speech")
        )

        features = manager.get_all_features(user_role="ADMIN")

        assert len(features) == 2
        assert "feature1" in features
        assert "feature2" in features

    def test_get_all_features_filters_by_category(self, manager):
        """Test get_all_features filters by category"""
        manager.create_feature(
            FeatureToggle(feature_name="feature1", category="learning")
        )
        manager.create_feature(
            FeatureToggle(feature_name="feature2", category="speech")
        )

        features = manager.get_all_features(category="learning", user_role="ADMIN")

        assert len(features) == 1
        assert "feature1" in features

    def test_get_all_features_filters_by_role(self, manager):
        """Test get_all_features filters by role permission"""
        manager.create_feature(
            FeatureToggle(feature_name="child_feature", min_role="CHILD")
        )
        manager.create_feature(
            FeatureToggle(feature_name="parent_feature", min_role="PARENT")
        )
        manager.create_feature(
            FeatureToggle(feature_name="admin_feature", min_role="ADMIN")
        )

        # CHILD should only see child_feature
        child_features = manager.get_all_features(user_role="CHILD")
        assert len(child_features) == 1
        assert "child_feature" in child_features

        # PARENT should see child and parent features
        parent_features = manager.get_all_features(user_role="PARENT")
        assert len(parent_features) == 2

        # ADMIN should see all features
        admin_features = manager.get_all_features(user_role="ADMIN")
        assert len(admin_features) == 3

    def test_get_features_by_category_organizes_by_category(self, manager):
        """Test get_features_by_category groups features correctly"""
        manager.create_feature(
            FeatureToggle(feature_name="learn1", category="learning")
        )
        manager.create_feature(
            FeatureToggle(feature_name="learn2", category="learning")
        )
        manager.create_feature(FeatureToggle(feature_name="speech1", category="speech"))

        categories = manager.get_features_by_category(user_role="ADMIN")

        assert "learning" in categories
        assert "speech" in categories
        assert len(categories["learning"]) == 2
        assert len(categories["speech"]) == 1

    def test_get_features_by_category_sorts_within_category(self, manager):
        """Test features are sorted within each category"""
        manager.create_feature(
            FeatureToggle(feature_name="zzz_feature", category="learning")
        )
        manager.create_feature(
            FeatureToggle(feature_name="aaa_feature", category="learning")
        )

        categories = manager.get_features_by_category(user_role="ADMIN")

        features = categories["learning"]
        assert features[0].feature_name == "aaa_feature"
        assert features[1].feature_name == "zzz_feature"


# ============================================================================
# Test CRUD Operations
# ============================================================================


class TestCRUDOperations:
    """Test create, update, delete operations"""

    def test_create_feature_success(self, manager, sample_feature):
        """Test successful feature creation"""
        result = manager.create_feature(sample_feature)

        assert result is True
        assert "test_feature" in manager._cache

    def test_create_feature_stores_in_database(self, manager, sample_feature, temp_db):
        """Test feature is stored in database"""
        manager.create_feature(sample_feature)

        # Verify in database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM admin_feature_toggles WHERE feature_name = ?",
            ("test_feature",),
        )
        row = cursor.fetchone()
        conn.close()

        assert row is not None

    def test_update_feature_enabled_state(self, manager, sample_feature):
        """Test updating feature enabled state"""
        manager.create_feature(sample_feature)

        result = manager.update_feature("test_feature", is_enabled=False)

        assert result is True
        feature = manager.get_feature("test_feature")
        assert feature.is_enabled is False

    def test_update_feature_description(self, manager, sample_feature):
        """Test updating feature description"""
        manager.create_feature(sample_feature)

        result = manager.update_feature("test_feature", description="New description")

        assert result is True
        feature = manager.get_feature("test_feature")
        assert feature.description == "New description"

    def test_update_feature_configuration(self, manager, sample_feature):
        """Test updating feature configuration"""
        manager.create_feature(sample_feature)

        new_config = {"new_key": "new_value"}
        result = manager.update_feature("test_feature", configuration=new_config)

        assert result is True
        feature = manager.get_feature("test_feature")
        assert feature.configuration == new_config

    def test_update_feature_nonexistent_returns_false(self, manager):
        """Test updating nonexistent feature returns False"""
        result = manager.update_feature("nonexistent", is_enabled=False)

        assert result is False

    def test_delete_feature_success(self, manager, sample_feature):
        """Test successful feature deletion"""
        manager.create_feature(sample_feature)

        result = manager.delete_feature("test_feature")

        assert result is True
        assert "test_feature" not in manager._cache

    def test_delete_feature_nonexistent_returns_false(self, manager):
        """Test deleting nonexistent feature returns False"""
        result = manager.delete_feature("nonexistent")

        assert result is False


# ============================================================================
# Test Statistics
# ============================================================================


class TestStatistics:
    """Test feature statistics generation"""

    def test_calculate_basic_stats(self, manager):
        """Test basic statistics calculation"""
        features = {
            "f1": FeatureToggle(feature_name="f1", is_enabled=True),
            "f2": FeatureToggle(feature_name="f2", is_enabled=False),
            "f3": FeatureToggle(feature_name="f3", is_enabled=True),
        }

        stats = manager._calculate_basic_stats(features)

        assert stats["total_features"] == 3
        assert stats["enabled_features"] == 2
        assert stats["disabled_features"] == 1

    def test_build_category_breakdown(self, manager):
        """Test category breakdown statistics"""
        features = {
            "f1": FeatureToggle(
                feature_name="f1", category="learning", is_enabled=True
            ),
            "f2": FeatureToggle(
                feature_name="f2", category="learning", is_enabled=False
            ),
            "f3": FeatureToggle(feature_name="f3", category="speech", is_enabled=True),
        }

        breakdown = manager._build_category_breakdown(features)

        assert "learning" in breakdown
        assert "speech" in breakdown
        assert breakdown["learning"]["total"] == 2
        assert breakdown["learning"]["enabled"] == 1
        assert breakdown["speech"]["total"] == 1
        assert breakdown["speech"]["enabled"] == 1

    def test_build_role_breakdown(self, manager):
        """Test role breakdown statistics"""
        features = {
            "f1": FeatureToggle(feature_name="f1", min_role="CHILD", is_enabled=True),
            "f2": FeatureToggle(feature_name="f2", min_role="PARENT", is_enabled=False),
            "f3": FeatureToggle(feature_name="f3", min_role="ADMIN", is_enabled=True),
        }

        breakdown = manager._build_role_breakdown(features)

        assert "CHILD" in breakdown
        assert "PARENT" in breakdown
        assert "ADMIN" in breakdown
        assert breakdown["CHILD"]["total"] == 1
        assert breakdown["PARENT"]["enabled"] == 0
        assert breakdown["ADMIN"]["enabled"] == 1

    def test_build_role_breakdown_multiple_features_same_role(self, manager):
        """Test role breakdown with multiple features sharing the same role (branch 432->435)"""
        # Pattern: Dictionary key already exists (similar to Sessions 38, 41)
        # When processing second feature with same role, hits else branch at line 432->435
        features = {
            "f1": FeatureToggle(feature_name="f1", min_role="CHILD", is_enabled=True),
            "f2": FeatureToggle(feature_name="f2", min_role="CHILD", is_enabled=False),
            "f3": FeatureToggle(feature_name="f3", min_role="CHILD", is_enabled=True),
            "f4": FeatureToggle(feature_name="f4", min_role="PARENT", is_enabled=True),
            "f5": FeatureToggle(feature_name="f5", min_role="PARENT", is_enabled=False),
        }

        breakdown = manager._build_role_breakdown(features)

        # Verify CHILD role aggregated correctly (3 features, 2 enabled)
        assert "CHILD" in breakdown
        assert breakdown["CHILD"]["total"] == 3
        assert breakdown["CHILD"]["enabled"] == 2

        # Verify PARENT role aggregated correctly (2 features, 1 enabled)
        assert "PARENT" in breakdown
        assert breakdown["PARENT"]["total"] == 2
        assert breakdown["PARENT"]["enabled"] == 1

    def test_get_feature_statistics_complete(self, manager):
        """Test complete feature statistics"""
        manager.create_feature(
            FeatureToggle(
                feature_name="f1",
                category="learning",
                min_role="CHILD",
                is_enabled=True,
            )
        )
        manager.create_feature(
            FeatureToggle(
                feature_name="f2",
                category="speech",
                min_role="PARENT",
                is_enabled=False,
            )
        )

        stats = manager.get_feature_statistics()

        assert "total_features" in stats
        assert "enabled_features" in stats
        assert "disabled_features" in stats
        assert "categories" in stats
        assert "roles" in stats


# ============================================================================
# Test Bulk Operations
# ============================================================================


class TestBulkOperations:
    """Test bulk update operations"""

    def test_bulk_update_features_success(self, manager):
        """Test bulk updating multiple features"""
        manager.create_feature(FeatureToggle(feature_name="f1", is_enabled=True))
        manager.create_feature(FeatureToggle(feature_name="f2", is_enabled=True))
        manager.create_feature(FeatureToggle(feature_name="f3", is_enabled=True))

        updates = {"f1": False, "f2": False}
        results = manager.bulk_update_features(updates)

        assert results["f1"] is True
        assert results["f2"] is True
        assert manager.get_feature("f1").is_enabled is False
        assert manager.get_feature("f2").is_enabled is False
        assert manager.get_feature("f3").is_enabled is True  # Unchanged

    def test_bulk_update_handles_nonexistent_features(self, manager):
        """Test bulk update handles nonexistent features"""
        manager.create_feature(FeatureToggle(feature_name="f1", is_enabled=True))

        updates = {"f1": False, "nonexistent": False}
        results = manager.bulk_update_features(updates)

        assert results["f1"] is True
        assert results["nonexistent"] is False


# ============================================================================
# Test Import/Export
# ============================================================================


class TestImportExport:
    """Test configuration import/export"""

    def test_export_configuration(self, manager):
        """Test exporting feature configuration"""
        manager.create_feature(
            FeatureToggle(
                feature_name="f1",
                is_enabled=True,
                description="Feature 1",
                category="learning",
                configuration={"key": "value"},
            )
        )

        export_data = manager.export_configuration()

        assert "export_timestamp" in export_data
        assert "total_features" in export_data
        assert "features" in export_data
        assert "f1" in export_data["features"]
        assert export_data["features"]["f1"]["is_enabled"] is True
        assert export_data["features"]["f1"]["description"] == "Feature 1"
        assert export_data["features"]["f1"]["configuration"] == {"key": "value"}

    def test_import_configuration(self, manager):
        """Test importing feature configuration"""
        # Create initial features
        manager.create_feature(FeatureToggle(feature_name="f1", is_enabled=True))
        manager.create_feature(FeatureToggle(feature_name="f2", is_enabled=True))

        # Import configuration
        import_data = {
            "features": {
                "f1": {
                    "is_enabled": False,
                    "description": "Updated feature 1",
                    "configuration": {"new": "config"},
                },
                "f2": {"is_enabled": False},
            }
        }

        results = manager.import_configuration(import_data)

        assert results["f1"] is True
        assert results["f2"] is True

        # Verify updates
        f1 = manager.get_feature("f1")
        assert f1.is_enabled is False
        assert f1.description == "Updated feature 1"
        assert f1.configuration == {"new": "config"}

    def test_export_includes_timestamp(self, manager):
        """Test export includes valid timestamp"""
        export_data = manager.export_configuration()

        assert "export_timestamp" in export_data
        # Verify it's a valid ISO format timestamp
        timestamp = datetime.fromisoformat(export_data["export_timestamp"])
        assert isinstance(timestamp, datetime)


# ============================================================================
# Test Global Instance
# ============================================================================


class TestGlobalInstance:
    """Test global instance and convenience functions"""

    def test_global_instance_exists(self):
        """Test that global feature_toggle_manager exists"""
        assert feature_toggle_manager is not None
        assert isinstance(feature_toggle_manager, FeatureToggleManager)

    def test_convenience_is_feature_enabled(self):
        """Test convenience function is_feature_enabled"""
        with patch.object(
            feature_toggle_manager, "is_feature_enabled", return_value=True
        ) as mock:
            result = is_feature_enabled("test_feature", "CHILD")

            assert result is True
            mock.assert_called_once_with("test_feature", "CHILD")

    def test_convenience_get_feature(self):
        """Test convenience function get_feature"""
        mock_feature = FeatureToggle(feature_name="test")

        with patch.object(
            feature_toggle_manager, "get_feature", return_value=mock_feature
        ) as mock:
            result = get_feature("test_feature")

            assert result == mock_feature
            mock.assert_called_once_with("test_feature")

    def test_convenience_get_features_by_category(self):
        """Test convenience function get_features_by_category"""
        mock_categories = {"learning": [], "speech": []}

        with patch.object(
            feature_toggle_manager,
            "get_features_by_category",
            return_value=mock_categories,
        ) as mock:
            result = get_features_by_category("PARENT")

            assert result == mock_categories
            mock.assert_called_once_with("PARENT")


# ============================================================================
# Test Error Handling
# ============================================================================


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_is_feature_enabled_handles_exceptions(self, manager):
        """Test is_feature_enabled handles exceptions gracefully"""
        with patch.object(
            manager, "_should_refresh_cache", side_effect=Exception("Cache error")
        ):
            result = manager.is_feature_enabled("test_feature")

            assert result is False

    def test_get_feature_handles_exceptions(self, manager):
        """Test get_feature handles exceptions gracefully"""
        with patch.object(
            manager, "_should_refresh_cache", side_effect=Exception("Cache error")
        ):
            result = manager.get_feature("test_feature")

            assert result is None

    def test_get_all_features_handles_exceptions(self, manager, sample_feature):
        """Test get_all_features handles exceptions gracefully"""
        manager.create_feature(sample_feature)

        # Make cache stale to trigger refresh, then cause error during iteration
        manager._last_cache_update = datetime.now() - timedelta(seconds=400)
        manager.cache_ttl = 300

        # Mock _check_role_permission to raise exception during iteration
        with patch.object(
            manager, "_check_role_permission", side_effect=Exception("Permission error")
        ):
            result = manager.get_all_features()

            assert result == {}

    def test_update_feature_handles_database_errors(self, manager):
        """Test update_feature handles database errors"""
        with patch.object(
            manager, "_get_connection", side_effect=Exception("DB error")
        ):
            result = manager.update_feature("test", is_enabled=False)

            assert result is False

    def test_create_feature_handles_database_errors(self, manager, sample_feature):
        """Test create_feature handles database errors"""
        with patch.object(
            manager, "_get_connection", side_effect=Exception("DB error")
        ):
            result = manager.create_feature(sample_feature)

            assert result is False

    def test_delete_feature_handles_database_errors(self, manager):
        """Test delete_feature handles database errors"""
        with patch.object(
            manager, "_get_connection", side_effect=Exception("DB error")
        ):
            result = manager.delete_feature("test")

            assert result is False

    def test_refresh_cache_handles_database_errors(self, manager):
        """Test _refresh_cache handles database connection errors"""
        with patch.object(
            manager, "_get_connection", side_effect=Exception("Connection failed")
        ):
            # Should not raise, just logs error
            manager._refresh_cache()

            # Cache should remain empty or unchanged
            assert isinstance(manager._cache, dict)

    def test_get_features_by_category_handles_exceptions(self, manager):
        """Test get_features_by_category handles exceptions gracefully"""
        with patch.object(
            manager, "get_all_features", side_effect=Exception("Unexpected error")
        ):
            result = manager.get_features_by_category("ADMIN")

            assert result == {}

    def test_get_feature_statistics_handles_exceptions(self, manager):
        """Test get_feature_statistics handles exceptions gracefully"""
        with patch.object(
            manager, "get_all_features", side_effect=Exception("Stats error")
        ):
            result = manager.get_feature_statistics()

            assert result == {}

    def test_export_configuration_handles_exceptions(self, manager):
        """Test export_configuration handles exceptions gracefully"""
        with patch.object(
            manager, "get_all_features", side_effect=Exception("Export error")
        ):
            result = manager.export_configuration()

            assert result == {}

    def test_import_configuration_handles_exceptions(self, manager):
        """Test import_configuration handles exceptions gracefully"""
        # Create malformed config that will cause exception
        bad_config = {"features": {"f1": "not a dict"}}

        with patch.object(
            manager, "update_feature", side_effect=Exception("Import error")
        ):
            result = manager.import_configuration(bad_config)

            # Should return empty dict on error
            assert result == {}

    def test_update_feature_with_no_changes_returns_true(self, manager, sample_feature):
        """Test update_feature returns True when no updates provided"""
        manager.create_feature(sample_feature)

        # Call update with no parameters (all None)
        result = manager.update_feature("test_feature")

        assert result is True

    def test_is_feature_enabled_cache_refresh_on_stale(self, manager, sample_feature):
        """Test is_feature_enabled triggers cache refresh when stale"""
        manager.create_feature(sample_feature)

        # Make cache stale
        manager._last_cache_update = datetime.now() - timedelta(seconds=400)
        manager.cache_ttl = 300

        # Track if refresh was called
        with patch.object(
            manager, "_refresh_cache", wraps=manager._refresh_cache
        ) as mock_refresh:
            result = manager.is_feature_enabled("test_feature")

            assert result is True
            mock_refresh.assert_called_once()

    def test_get_feature_cache_refresh_on_stale(self, manager, sample_feature):
        """Test get_feature triggers cache refresh when stale"""
        manager.create_feature(sample_feature)

        # Make cache stale
        manager._last_cache_update = datetime.now() - timedelta(seconds=400)
        manager.cache_ttl = 300

        # Track if refresh was called
        with patch.object(
            manager, "_refresh_cache", wraps=manager._refresh_cache
        ) as mock_refresh:
            result = manager.get_feature("test_feature")

            assert result is not None
            mock_refresh.assert_called_once()
