"""
Comprehensive tests for models/feature_toggle.py
Achieves TRUE 100% coverage (statement + branch)
"""

from datetime import datetime
from typing import Any, Dict

import pytest
from pydantic import ValidationError

from app.models.feature_toggle import (
    # Models
    FeatureCondition,
    FeatureToggle,
    FeatureToggleCategory,
    FeatureToggleEvent,
    FeatureToggleListResponse,
    FeatureToggleRequest,
    FeatureToggleResponse,
    # Enums
    FeatureToggleScope,
    FeatureToggleStatsResponse,
    FeatureToggleStatus,
    FeatureToggleUpdateRequest,
    UserFeatureAccess,
    UserFeatureStatusResponse,
)


class TestEnums:
    """Test all enum classes"""

    def test_feature_toggle_scope_values(self):
        """Test FeatureToggleScope enum values"""
        assert FeatureToggleScope.GLOBAL == "global"
        assert FeatureToggleScope.USER_SPECIFIC == "user_specific"
        assert FeatureToggleScope.ROLE_BASED == "role_based"
        assert FeatureToggleScope.EXPERIMENTAL == "experimental"

    def test_feature_toggle_status_values(self):
        """Test FeatureToggleStatus enum values"""
        assert FeatureToggleStatus.ENABLED == "enabled"
        assert FeatureToggleStatus.DISABLED == "disabled"
        assert FeatureToggleStatus.EXPERIMENTAL == "experimental"
        assert FeatureToggleStatus.DEPRECATED == "deprecated"
        assert FeatureToggleStatus.MAINTENANCE == "maintenance"

    def test_feature_toggle_category_values(self):
        """Test FeatureToggleCategory enum values"""
        assert FeatureToggleCategory.TUTOR_MODES == "tutor_modes"
        assert FeatureToggleCategory.SCENARIOS == "scenarios"
        assert FeatureToggleCategory.ANALYSIS == "analysis"
        assert FeatureToggleCategory.SPEECH == "speech"
        assert FeatureToggleCategory.UI_COMPONENTS == "ui_components"
        assert FeatureToggleCategory.API_ENDPOINTS == "api_endpoints"
        assert FeatureToggleCategory.INTEGRATIONS == "integrations"
        assert FeatureToggleCategory.EXPERIMENTAL == "experimental"


class TestFeatureCondition:
    """Test FeatureCondition model"""

    def test_feature_condition_creation(self):
        """Test basic FeatureCondition creation"""
        condition = FeatureCondition(type="user_role", operator="equals", value="admin")
        assert condition.type == "user_role"
        assert condition.operator == "equals"
        assert condition.value == "admin"
        assert condition.description is None

    def test_feature_condition_with_list_value(self):
        """Test FeatureCondition with list value"""
        condition = FeatureCondition(
            type="user_role",
            operator="in",
            value=["admin", "moderator"],
            description="Admin or moderator roles",
        )
        assert condition.value == ["admin", "moderator"]
        assert condition.description == "Admin or moderator roles"

    def test_feature_condition_with_numeric_value(self):
        """Test FeatureCondition with numeric values"""
        condition_int = FeatureCondition(type="age", operator="greater_than", value=18)
        assert condition_int.value == 18

        condition_float = FeatureCondition(
            type="percentage", operator="less_than", value=50.5
        )
        assert condition_float.value == 50.5


class TestFeatureToggle:
    """Test FeatureToggle model"""

    def test_feature_toggle_minimal(self):
        """Test FeatureToggle with minimal required fields"""
        toggle = FeatureToggle(
            id="test_feature",
            name="Test Feature",
            description="A test feature",
            category=FeatureToggleCategory.EXPERIMENTAL,
        )
        assert toggle.id == "test_feature"
        assert toggle.name == "Test Feature"
        assert toggle.scope == FeatureToggleScope.GLOBAL
        assert toggle.status == FeatureToggleStatus.DISABLED
        assert toggle.enabled_by_default is False
        assert toggle.requires_admin is False
        assert toggle.experimental is False
        assert toggle.conditions == []
        assert toggle.target_users == []
        assert toggle.target_roles == []
        assert toggle.rollout_percentage == 100.0
        assert toggle.dependencies == []
        assert toggle.conflicts == []
        assert toggle.environments == {
            "development": True,
            "staging": False,
            "production": False,
        }
        assert toggle.usage_tracking is True
        assert toggle.metrics == {}

    def test_feature_toggle_complete(self):
        """Test FeatureToggle with all fields"""
        now = datetime.now()
        conditions = [
            FeatureCondition(type="user_role", operator="equals", value="admin")
        ]

        toggle = FeatureToggle(
            id="advanced_feature",
            name="Advanced Feature",
            description="An advanced feature with all options",
            category=FeatureToggleCategory.TUTOR_MODES,
            scope=FeatureToggleScope.ROLE_BASED,
            status=FeatureToggleStatus.ENABLED,
            enabled_by_default=True,
            requires_admin=True,
            experimental=True,
            conditions=conditions,
            target_users=["user1", "user2"],
            target_roles=["admin", "moderator"],
            rollout_percentage=75.0,
            created_at=now,
            updated_at=now,
            created_by="admin_user",
            updated_by="admin_user",
            dependencies=["feature1", "feature2"],
            conflicts=["old_feature"],
            environments={"development": True, "staging": True, "production": True},
            usage_tracking=True,
            metrics={"usage_count": 100},
        )

        assert toggle.scope == FeatureToggleScope.ROLE_BASED
        assert toggle.status == FeatureToggleStatus.ENABLED
        assert toggle.enabled_by_default is True
        assert toggle.requires_admin is True
        assert toggle.experimental is True
        assert len(toggle.conditions) == 1
        assert toggle.target_users == ["user1", "user2"]
        assert toggle.target_roles == ["admin", "moderator"]
        assert toggle.rollout_percentage == 75.0
        assert toggle.created_by == "admin_user"
        assert toggle.dependencies == ["feature1", "feature2"]
        assert toggle.conflicts == ["old_feature"]
        assert toggle.environments["production"] is True
        assert toggle.metrics["usage_count"] == 100

    def test_feature_toggle_datetime_serialization_with_values(self):
        """Test FeatureToggle datetime serialization when datetime exists"""
        now = datetime.now()
        toggle = FeatureToggle(
            id="test",
            name="Test",
            description="Test",
            category=FeatureToggleCategory.EXPERIMENTAL,
            created_at=now,
            updated_at=now,
        )

        # Trigger serialization by converting to JSON
        json_data = toggle.model_dump_json()
        assert now.isoformat() in json_data

    def test_feature_toggle_datetime_serialization_with_none(self):
        """Test FeatureToggle datetime serialization when datetime is None - BRANCH COVERAGE"""
        toggle = FeatureToggle(
            id="test",
            name="Test",
            description="Test",
            category=FeatureToggleCategory.EXPERIMENTAL,
            created_by=None,  # Optional field
            updated_by=None,  # Optional field
        )

        # Manually call serializer with None to test else branch
        serialized = toggle.serialize_datetime(None)
        assert serialized is None


class TestUserFeatureAccess:
    """Test UserFeatureAccess model"""

    def test_user_feature_access_minimal(self):
        """Test UserFeatureAccess with minimal fields"""
        access = UserFeatureAccess(
            user_id="user123", feature_id="feature_abc", enabled=True
        )
        assert access.user_id == "user123"
        assert access.feature_id == "feature_abc"
        assert access.enabled is True
        assert access.override_global is False
        assert access.override_reason is None
        assert access.override_expires is None
        assert access.granted_by is None
        assert access.last_used is None
        assert access.usage_count == 0

    def test_user_feature_access_complete(self):
        """Test UserFeatureAccess with all fields"""
        now = datetime.now()

        access = UserFeatureAccess(
            user_id="user123",
            feature_id="feature_abc",
            enabled=True,
            override_global=True,
            override_reason="Special permissions for testing",
            override_expires=now,
            granted_at=now,
            granted_by="admin_user",
            last_used=now,
            usage_count=42,
        )

        assert access.override_global is True
        assert access.override_reason == "Special permissions for testing"
        assert access.override_expires == now
        assert access.granted_by == "admin_user"
        assert access.last_used == now
        assert access.usage_count == 42

    def test_user_feature_access_datetime_serialization_with_values(self):
        """Test UserFeatureAccess datetime serialization when datetimes exist"""
        now = datetime.now()
        access = UserFeatureAccess(
            user_id="user123",
            feature_id="feature_abc",
            enabled=True,
            granted_at=now,
            last_used=now,
            override_expires=now,
        )

        # Trigger serialization
        json_data = access.model_dump_json()
        assert now.isoformat() in json_data

    def test_user_feature_access_datetime_serialization_with_none(self):
        """Test UserFeatureAccess datetime serialization when datetime is None - BRANCH COVERAGE"""
        access = UserFeatureAccess(
            user_id="user123",
            feature_id="feature_abc",
            enabled=True,
            granted_by=None,  # Optional
            last_used=None,  # Optional
            override_expires=None,  # Optional
        )

        # Manually call serializer with None to test else branch
        serialized = access.serialize_datetime(None)
        assert serialized is None


class TestFeatureToggleEvent:
    """Test FeatureToggleEvent model"""

    def test_feature_toggle_event_minimal(self):
        """Test FeatureToggleEvent with minimal fields"""
        event = FeatureToggleEvent(
            id="event_123",
            feature_id="feature_abc",
            event_type="enabled",
            new_state={"status": "enabled"},
        )
        assert event.id == "event_123"
        assert event.feature_id == "feature_abc"
        assert event.event_type == "enabled"
        assert event.previous_state is None
        assert event.new_state == {"status": "enabled"}
        assert event.change_reason is None
        assert event.user_id is None
        assert event.environment == "development"
        assert event.ip_address is None
        assert event.user_agent is None

    def test_feature_toggle_event_complete(self):
        """Test FeatureToggleEvent with all fields"""
        now = datetime.now()

        event = FeatureToggleEvent(
            id="event_123",
            feature_id="feature_abc",
            event_type="status_changed",
            previous_state={"status": "disabled"},
            new_state={"status": "enabled"},
            change_reason="Production rollout",
            user_id="admin_user",
            environment="production",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            timestamp=now,
        )

        assert event.previous_state == {"status": "disabled"}
        assert event.change_reason == "Production rollout"
        assert event.user_id == "admin_user"
        assert event.environment == "production"
        assert event.ip_address == "192.168.1.1"
        assert event.user_agent == "Mozilla/5.0"
        assert event.timestamp == now

    def test_feature_toggle_event_datetime_serialization_with_value(self):
        """Test FeatureToggleEvent datetime serialization when datetime exists"""
        now = datetime.now()
        event = FeatureToggleEvent(
            id="event_123",
            feature_id="feature_abc",
            event_type="enabled",
            new_state={"status": "enabled"},
            timestamp=now,
        )

        # Trigger serialization
        json_data = event.model_dump_json()
        assert now.isoformat() in json_data

    def test_feature_toggle_event_datetime_serialization_with_none(self):
        """Test FeatureToggleEvent datetime serialization when datetime is None - BRANCH COVERAGE"""
        event = FeatureToggleEvent(
            id="event_123",
            feature_id="feature_abc",
            event_type="enabled",
            new_state={"status": "enabled"},
            user_id=None,  # Optional field
        )

        # Manually call serializer with None to test else branch
        serialized = event.serialize_datetime(None)
        assert serialized is None


class TestFeatureToggleRequest:
    """Test FeatureToggleRequest model"""

    def test_feature_toggle_request_minimal(self):
        """Test FeatureToggleRequest with minimal fields"""
        request = FeatureToggleRequest(
            name="New Feature",
            description="A new feature",
            category=FeatureToggleCategory.EXPERIMENTAL,
        )
        assert request.name == "New Feature"
        assert request.description == "A new feature"
        assert request.category == FeatureToggleCategory.EXPERIMENTAL
        assert request.scope == FeatureToggleScope.GLOBAL
        assert request.status == FeatureToggleStatus.DISABLED
        assert request.enabled_by_default is False
        assert request.requires_admin is False
        assert request.experimental is False
        assert request.conditions == []
        assert request.target_users == []
        assert request.target_roles == []
        assert request.rollout_percentage == 100.0
        assert request.dependencies == []
        assert request.conflicts == []
        assert request.usage_tracking is True

    def test_feature_toggle_request_complete(self):
        """Test FeatureToggleRequest with all fields"""
        conditions = [
            FeatureCondition(type="user_role", operator="equals", value="admin")
        ]

        request = FeatureToggleRequest(
            name="Advanced Feature",
            description="Advanced feature with all options",
            category=FeatureToggleCategory.TUTOR_MODES,
            scope=FeatureToggleScope.ROLE_BASED,
            status=FeatureToggleStatus.EXPERIMENTAL,
            enabled_by_default=True,
            requires_admin=True,
            experimental=True,
            conditions=conditions,
            target_users=["user1"],
            target_roles=["admin"],
            rollout_percentage=50.0,
            dependencies=["dep1"],
            conflicts=["conflict1"],
            environments={"production": True},
            usage_tracking=False,
        )

        assert request.scope == FeatureToggleScope.ROLE_BASED
        assert request.status == FeatureToggleStatus.EXPERIMENTAL
        assert request.enabled_by_default is True
        assert request.requires_admin is True
        assert request.experimental is True
        assert len(request.conditions) == 1
        assert request.rollout_percentage == 50.0
        assert request.usage_tracking is False

    def test_feature_toggle_request_validation_name_too_short(self):
        """Test FeatureToggleRequest name min_length validation"""
        with pytest.raises(ValidationError) as exc_info:
            FeatureToggleRequest(
                name="",  # Empty string, violates min_length=1
                description="Test",
                category=FeatureToggleCategory.EXPERIMENTAL,
            )
        assert "name" in str(exc_info.value).lower()

    def test_feature_toggle_request_validation_name_too_long(self):
        """Test FeatureToggleRequest name max_length validation"""
        with pytest.raises(ValidationError) as exc_info:
            FeatureToggleRequest(
                name="x" * 101,  # Exceeds max_length=100
                description="Test",
                category=FeatureToggleCategory.EXPERIMENTAL,
            )
        assert "name" in str(exc_info.value).lower()

    def test_feature_toggle_request_validation_description_too_long(self):
        """Test FeatureToggleRequest description max_length validation"""
        with pytest.raises(ValidationError) as exc_info:
            FeatureToggleRequest(
                name="Test",
                description="x" * 501,  # Exceeds max_length=500
                category=FeatureToggleCategory.EXPERIMENTAL,
            )
        assert "description" in str(exc_info.value).lower()

    def test_feature_toggle_request_validation_rollout_percentage_min(self):
        """Test FeatureToggleRequest rollout_percentage ge validation"""
        with pytest.raises(ValidationError) as exc_info:
            FeatureToggleRequest(
                name="Test",
                description="Test",
                category=FeatureToggleCategory.EXPERIMENTAL,
                rollout_percentage=-1.0,  # Below ge=0.0
            )
        assert "rollout_percentage" in str(exc_info.value).lower()

    def test_feature_toggle_request_validation_rollout_percentage_max(self):
        """Test FeatureToggleRequest rollout_percentage le validation"""
        with pytest.raises(ValidationError) as exc_info:
            FeatureToggleRequest(
                name="Test",
                description="Test",
                category=FeatureToggleCategory.EXPERIMENTAL,
                rollout_percentage=101.0,  # Exceeds le=100.0
            )
        assert "rollout_percentage" in str(exc_info.value).lower()


class TestFeatureToggleUpdateRequest:
    """Test FeatureToggleUpdateRequest model"""

    def test_feature_toggle_update_request_all_none(self):
        """Test FeatureToggleUpdateRequest with all fields None"""
        request = FeatureToggleUpdateRequest()
        assert request.name is None
        assert request.description is None
        assert request.category is None
        assert request.scope is None
        assert request.status is None
        assert request.enabled_by_default is None
        assert request.requires_admin is None
        assert request.experimental is None
        assert request.conditions is None
        assert request.target_users is None
        assert request.target_roles is None
        assert request.rollout_percentage is None
        assert request.dependencies is None
        assert request.conflicts is None
        assert request.environments is None
        assert request.usage_tracking is None

    def test_feature_toggle_update_request_partial(self):
        """Test FeatureToggleUpdateRequest with partial fields"""
        request = FeatureToggleUpdateRequest(
            name="Updated Name",
            status=FeatureToggleStatus.ENABLED,
            rollout_percentage=75.0,
        )
        assert request.name == "Updated Name"
        assert request.status == FeatureToggleStatus.ENABLED
        assert request.rollout_percentage == 75.0
        assert request.description is None  # Not provided

    def test_feature_toggle_update_request_validation_rollout_percentage(self):
        """Test FeatureToggleUpdateRequest rollout_percentage validation"""
        with pytest.raises(ValidationError) as exc_info:
            FeatureToggleUpdateRequest(
                rollout_percentage=150.0  # Exceeds le=100.0
            )
        assert "rollout_percentage" in str(exc_info.value).lower()


class TestFeatureToggleResponse:
    """Test FeatureToggleResponse model"""

    def test_feature_toggle_response_success_with_feature(self):
        """Test FeatureToggleResponse for successful operation"""
        toggle = FeatureToggle(
            id="test",
            name="Test",
            description="Test",
            category=FeatureToggleCategory.EXPERIMENTAL,
        )

        response = FeatureToggleResponse(
            success=True, message="Feature created successfully", feature=toggle
        )
        assert response.success is True
        assert response.message == "Feature created successfully"
        assert response.feature is not None
        assert response.errors == []

    def test_feature_toggle_response_failure_with_errors(self):
        """Test FeatureToggleResponse for failed operation"""
        response = FeatureToggleResponse(
            success=False,
            message="Failed to create feature",
            errors=["Validation error", "Database error"],
        )
        assert response.success is False
        assert response.feature is None
        assert len(response.errors) == 2


class TestFeatureToggleListResponse:
    """Test FeatureToggleListResponse model"""

    def test_feature_toggle_list_response(self):
        """Test FeatureToggleListResponse"""
        toggle1 = FeatureToggle(
            id="feature1",
            name="Feature 1",
            description="First feature",
            category=FeatureToggleCategory.EXPERIMENTAL,
        )
        toggle2 = FeatureToggle(
            id="feature2",
            name="Feature 2",
            description="Second feature",
            category=FeatureToggleCategory.TUTOR_MODES,
        )

        response = FeatureToggleListResponse(
            features=[toggle1, toggle2], total=2, page=1, per_page=50, has_next=False
        )
        assert len(response.features) == 2
        assert response.total == 2
        assert response.page == 1
        assert response.per_page == 50
        assert response.has_next is False


class TestUserFeatureStatusResponse:
    """Test UserFeatureStatusResponse model"""

    def test_user_feature_status_response(self):
        """Test UserFeatureStatusResponse"""
        response = UserFeatureStatusResponse(
            user_id="user123",
            feature_id="feature_abc",
            enabled=True,
            reason="User has admin role",
            metadata={"role": "admin", "granted_at": "2024-01-01"},
        )
        assert response.user_id == "user123"
        assert response.feature_id == "feature_abc"
        assert response.enabled is True
        assert response.reason == "User has admin role"
        assert response.metadata["role"] == "admin"


class TestFeatureToggleStatsResponse:
    """Test FeatureToggleStatsResponse model"""

    def test_feature_toggle_stats_response(self):
        """Test FeatureToggleStatsResponse"""
        event = FeatureToggleEvent(
            id="event1",
            feature_id="feature1",
            event_type="enabled",
            new_state={"status": "enabled"},
        )

        response = FeatureToggleStatsResponse(
            total_features=100,
            enabled_features=75,
            disabled_features=20,
            experimental_features=5,
            features_by_category={"tutor_modes": 30, "scenarios": 25},
            features_by_scope={"global": 80, "user_specific": 20},
            features_by_environment={
                "development": {"enabled": 90, "disabled": 10},
                "production": {"enabled": 50, "disabled": 50},
            },
            recent_changes=[event],
            usage_metrics={"total_usage": 10000},
        )

        assert response.total_features == 100
        assert response.enabled_features == 75
        assert response.disabled_features == 20
        assert response.experimental_features == 5
        assert response.features_by_category["tutor_modes"] == 30
        assert response.features_by_scope["global"] == 80
        assert len(response.recent_changes) == 1
        assert response.usage_metrics["total_usage"] == 10000
