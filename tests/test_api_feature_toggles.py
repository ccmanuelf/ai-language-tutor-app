"""
Comprehensive tests for app/api/feature_toggles.py
Session 90: TRUE 100% Coverage (statements + branches + zero warnings)

Tests cover:
- 12 API endpoints (all success, error, and edge cases)
- 9 helper functions (all code paths)
- HTTPException re-raising patterns (Session 87)
- Admin permission checks
- Pagination logic
- All enum values and edge cases
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

# Direct imports for coverage measurement (Session 84 pattern)
from app.api.feature_toggles import (
    _build_status_response,
    _check_admin_required,
    _check_global_disabled,
    _check_role_based_access,
    _check_user_specific_access,
    _determine_status_reason,
    _get_default_status,
    _get_feature_or_404,
    _parse_user_roles,
    bulk_update_features,
    check_user_feature_status,
    create_feature,
    delete_feature,
    disable_feature,
    enable_feature,
    get_feature,
    get_feature_statistics,
    get_user_features,
    list_features,
    public_check_feature,
    set_user_feature_access,
    update_feature,
)
from app.models.database import User
from app.models.feature_toggle import (
    FeatureToggle,
    FeatureToggleCategory,
    FeatureToggleListResponse,
    FeatureToggleRequest,
    FeatureToggleResponse,
    FeatureToggleScope,
    FeatureToggleStatsResponse,
    FeatureToggleStatus,
    FeatureToggleUpdateRequest,
    UserFeatureStatusResponse,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_admin_user():
    """Mock admin user for authentication."""
    user = MagicMock(spec=User)
    user.id = "admin123"
    user.username = "admin_user"
    user.roles = ["admin"]
    user.is_guest = False
    return user


@pytest.fixture
def sample_feature_toggle():
    """Sample feature toggle matching production model."""
    return FeatureToggle(
        id="feature_test_1",
        name="Test Feature",
        description="A test feature for coverage",
        category=FeatureToggleCategory.TUTOR_MODES,
        scope=FeatureToggleScope.GLOBAL,
        status=FeatureToggleStatus.ENABLED,
        enabled_by_default=True,
        requires_admin=False,
        experimental=False,
        conditions=[],
        target_users=["user1", "user2"],
        target_roles=["admin", "parent"],
        rollout_percentage=100.0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="admin_user",
        updated_by="admin_user",
        dependencies=[],
        conflicts=[],
        environments={"development": True, "staging": False, "production": False},
        usage_tracking=True,
        metrics={},
    )


@pytest.fixture
def sample_feature_request():
    """Sample feature toggle request."""
    return FeatureToggleRequest(
        name="New Feature",
        description="A new feature request",
        category=FeatureToggleCategory.SCENARIOS,
        scope=FeatureToggleScope.USER_SPECIFIC,
        status=FeatureToggleStatus.DISABLED,
        enabled_by_default=False,
        requires_admin=True,
        experimental=True,
        conditions=[],
        target_users=["user1"],
        target_roles=["admin"],
        rollout_percentage=50.0,
        dependencies=[],
        conflicts=[],
        environments={"development": True, "staging": False, "production": False},
        usage_tracking=True,
    )


@pytest.fixture
def sample_update_request():
    """Sample feature toggle update request."""
    return FeatureToggleUpdateRequest(
        status=FeatureToggleStatus.ENABLED,
        description="Updated description",
    )


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================


class TestHelperFunctions:
    """Test all helper functions with complete coverage."""

    def test_parse_user_roles_with_roles(self):
        """Test parsing comma-separated user roles."""
        result = _parse_user_roles("admin,parent,child")
        assert result == ["admin", "parent", "child"]

    def test_parse_user_roles_single_role(self):
        """Test parsing single role."""
        result = _parse_user_roles("admin")
        assert result == ["admin"]

    def test_parse_user_roles_none(self):
        """Test parsing None returns None."""
        result = _parse_user_roles(None)
        assert result is None

    def test_parse_user_roles_empty_string(self):
        """Test parsing empty string (falsy, returns None)."""
        result = _parse_user_roles("")
        # Empty string is falsy in Python, so the function returns None
        assert result is None

    @pytest.mark.asyncio
    async def test_get_feature_or_404_success(self, sample_feature_toggle):
        """Test getting feature successfully."""
        mock_service = AsyncMock()
        mock_service.get_feature.return_value = sample_feature_toggle

        result = await _get_feature_or_404(mock_service, "feature_test_1")
        assert result == sample_feature_toggle
        mock_service.get_feature.assert_called_once_with("feature_test_1")

    @pytest.mark.asyncio
    async def test_get_feature_or_404_not_found(self):
        """Test getting non-existent feature raises 404."""
        mock_service = AsyncMock()
        mock_service.get_feature.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await _get_feature_or_404(mock_service, "nonexistent")

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail

    def test_check_global_disabled_true(self, sample_feature_toggle):
        """Test check when feature is globally disabled."""
        sample_feature_toggle.status = FeatureToggleStatus.DISABLED
        result = _check_global_disabled(sample_feature_toggle)
        assert result == "globally disabled"

    def test_check_global_disabled_false(self, sample_feature_toggle):
        """Test check when feature is not disabled."""
        sample_feature_toggle.status = FeatureToggleStatus.ENABLED
        result = _check_global_disabled(sample_feature_toggle)
        assert result is None

    def test_check_global_disabled_experimental_status(self, sample_feature_toggle):
        """Test check with experimental status."""
        sample_feature_toggle.status = FeatureToggleStatus.EXPERIMENTAL
        result = _check_global_disabled(sample_feature_toggle)
        assert result is None

    def test_check_admin_required_with_admin_role(self, sample_feature_toggle):
        """Test admin check when user has admin role."""
        sample_feature_toggle.requires_admin = True
        result = _check_admin_required(sample_feature_toggle, ["admin", "user"])
        assert result is None

    def test_check_admin_required_without_admin_role(self, sample_feature_toggle):
        """Test admin check when user lacks admin role."""
        sample_feature_toggle.requires_admin = True
        result = _check_admin_required(sample_feature_toggle, ["user", "parent"])
        assert result == "requires admin role"

    def test_check_admin_required_no_roles(self, sample_feature_toggle):
        """Test admin check when no roles provided."""
        sample_feature_toggle.requires_admin = True
        result = _check_admin_required(sample_feature_toggle, None)
        assert result == "requires admin role"

    def test_check_admin_required_not_required(self, sample_feature_toggle):
        """Test admin check when admin not required."""
        sample_feature_toggle.requires_admin = False
        result = _check_admin_required(sample_feature_toggle, None)
        assert result is None

    def test_check_user_specific_access_user_in_list(self, sample_feature_toggle):
        """Test user-specific access when user is in target list."""
        sample_feature_toggle.scope = FeatureToggleScope.USER_SPECIFIC
        sample_feature_toggle.target_users = ["user1", "user2"]
        result = _check_user_specific_access(sample_feature_toggle, "user1")
        assert result is None

    def test_check_user_specific_access_user_not_in_list(self, sample_feature_toggle):
        """Test user-specific access when user not in target list."""
        sample_feature_toggle.scope = FeatureToggleScope.USER_SPECIFIC
        sample_feature_toggle.target_users = ["user1", "user2"]
        result = _check_user_specific_access(sample_feature_toggle, "user3")
        assert result == "not in target users"

    def test_check_user_specific_access_non_user_specific_scope(
        self, sample_feature_toggle
    ):
        """Test user-specific check with different scope."""
        sample_feature_toggle.scope = FeatureToggleScope.GLOBAL
        result = _check_user_specific_access(sample_feature_toggle, "user3")
        assert result is None

    def test_check_role_based_access_role_targeted(self, sample_feature_toggle):
        """Test role-based access when user has target role."""
        sample_feature_toggle.scope = FeatureToggleScope.ROLE_BASED
        sample_feature_toggle.target_roles = ["admin", "parent"]
        result = _check_role_based_access(sample_feature_toggle, ["admin", "user"])
        assert result is None

    def test_check_role_based_access_role_not_targeted(self, sample_feature_toggle):
        """Test role-based access when user lacks target role."""
        sample_feature_toggle.scope = FeatureToggleScope.ROLE_BASED
        sample_feature_toggle.target_roles = ["admin", "parent"]
        result = _check_role_based_access(sample_feature_toggle, ["child", "user"])
        assert result == "role not targeted"

    def test_check_role_based_access_no_roles(self, sample_feature_toggle):
        """Test role-based access when no roles provided."""
        sample_feature_toggle.scope = FeatureToggleScope.ROLE_BASED
        sample_feature_toggle.target_roles = ["admin"]
        result = _check_role_based_access(sample_feature_toggle, None)
        assert result == "role not targeted"

    def test_check_role_based_access_non_role_based_scope(self, sample_feature_toggle):
        """Test role-based check with different scope."""
        sample_feature_toggle.scope = FeatureToggleScope.GLOBAL
        result = _check_role_based_access(sample_feature_toggle, None)
        assert result is None

    def test_get_default_status_enabled(self):
        """Test default status for enabled feature."""
        result = _get_default_status(True)
        assert result == "enabled"

    def test_get_default_status_disabled(self):
        """Test default status for disabled feature."""
        result = _get_default_status(False)
        assert result == "disabled"

    def test_determine_status_reason_globally_disabled(self, sample_feature_toggle):
        """Test status reason when globally disabled (highest priority)."""
        sample_feature_toggle.status = FeatureToggleStatus.DISABLED
        sample_feature_toggle.requires_admin = True
        result = _determine_status_reason(
            sample_feature_toggle, False, "user1", ["user"]
        )
        assert result == "globally disabled"

    def test_determine_status_reason_admin_required(self, sample_feature_toggle):
        """Test status reason when admin required."""
        sample_feature_toggle.status = FeatureToggleStatus.ENABLED
        sample_feature_toggle.requires_admin = True
        result = _determine_status_reason(
            sample_feature_toggle, False, "user1", ["user"]
        )
        assert result == "requires admin role"

    def test_determine_status_reason_not_in_target_users(self, sample_feature_toggle):
        """Test status reason when user not in target users."""
        sample_feature_toggle.status = FeatureToggleStatus.ENABLED
        sample_feature_toggle.requires_admin = False
        sample_feature_toggle.scope = FeatureToggleScope.USER_SPECIFIC
        sample_feature_toggle.target_users = ["user2"]
        result = _determine_status_reason(
            sample_feature_toggle, False, "user1", ["admin"]
        )
        assert result == "not in target users"

    def test_determine_status_reason_role_not_targeted(self, sample_feature_toggle):
        """Test status reason when role not targeted."""
        sample_feature_toggle.status = FeatureToggleStatus.ENABLED
        sample_feature_toggle.requires_admin = False
        sample_feature_toggle.scope = FeatureToggleScope.ROLE_BASED
        sample_feature_toggle.target_roles = ["admin"]
        result = _determine_status_reason(
            sample_feature_toggle, False, "user1", ["user"]
        )
        assert result == "role not targeted"

    def test_determine_status_reason_default_enabled(self, sample_feature_toggle):
        """Test status reason defaults to enabled."""
        sample_feature_toggle.status = FeatureToggleStatus.ENABLED
        sample_feature_toggle.requires_admin = False
        sample_feature_toggle.scope = FeatureToggleScope.GLOBAL
        result = _determine_status_reason(
            sample_feature_toggle, True, "user1", ["user"]
        )
        assert result == "enabled"

    def test_determine_status_reason_default_disabled(self, sample_feature_toggle):
        """Test status reason defaults to disabled."""
        sample_feature_toggle.status = FeatureToggleStatus.ENABLED
        sample_feature_toggle.requires_admin = False
        sample_feature_toggle.scope = FeatureToggleScope.GLOBAL
        result = _determine_status_reason(
            sample_feature_toggle, False, "user1", ["user"]
        )
        assert result == "disabled"

    def test_build_status_response(self, sample_feature_toggle):
        """Test building status response."""
        result = _build_status_response(
            user_id="user123",
            feature_id="feature_test_1",
            enabled=True,
            reason="enabled",
            feature=sample_feature_toggle,
        )

        assert isinstance(result, UserFeatureStatusResponse)
        assert result.user_id == "user123"
        assert result.feature_id == "feature_test_1"
        assert result.enabled is True
        assert result.reason == "enabled"
        assert result.metadata["feature_name"] == "Test Feature"
        assert result.metadata["feature_category"] == "tutor_modes"
        assert result.metadata["feature_scope"] == "global"
        assert result.metadata["feature_status"] == "enabled"
        assert result.metadata["requires_admin"] is False
        assert result.metadata["experimental"] is False


# ============================================================================
# API ENDPOINT TESTS - GET OPERATIONS
# ============================================================================


class TestListFeaturesEndpoint:
    """Test list_features endpoint with all scenarios."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_list_features_success_no_filters(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_toggle
    ):
        """Test listing all features without filters."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.get_all_features.return_value = [sample_feature_toggle]
        mock_get_service.return_value = mock_service

        result = await list_features(
            category=None,
            scope=None,
            status=None,
            page=1,
            per_page=50,
            current_user=mock_admin_user,
        )

        assert isinstance(result, FeatureToggleListResponse)
        assert result.total == 1
        assert result.page == 1
        assert result.per_page == 50
        assert result.has_next is False
        assert len(result.features) == 1
        mock_service.get_all_features.assert_called_once_with(None, None, None)

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_list_features_with_filters(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_toggle
    ):
        """Test listing features with category, scope, and status filters."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.get_all_features.return_value = [sample_feature_toggle]
        mock_get_service.return_value = mock_service

        result = await list_features(
            category=FeatureToggleCategory.TUTOR_MODES,
            scope=FeatureToggleScope.GLOBAL,
            status=FeatureToggleStatus.ENABLED,
            page=1,
            per_page=50,
            current_user=mock_admin_user,
        )

        assert result.total == 1
        mock_service.get_all_features.assert_called_once_with(
            FeatureToggleCategory.TUTOR_MODES,
            FeatureToggleScope.GLOBAL,
            FeatureToggleStatus.ENABLED,
        )

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_list_features_pagination(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_toggle
    ):
        """Test pagination logic."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        # Create 100 features for pagination test
        features = [sample_feature_toggle] * 100
        mock_service.get_all_features.return_value = features
        mock_get_service.return_value = mock_service

        # Test first page
        result = await list_features(page=1, per_page=10, current_user=mock_admin_user)
        assert result.total == 100
        assert result.page == 1
        assert result.per_page == 10
        assert result.has_next is True
        assert len(result.features) == 10

        # Test middle page
        result = await list_features(page=5, per_page=10, current_user=mock_admin_user)
        assert result.page == 5
        assert result.has_next is True
        assert len(result.features) == 10

        # Test last page
        result = await list_features(page=10, per_page=10, current_user=mock_admin_user)
        assert result.page == 10
        assert result.has_next is False
        assert len(result.features) == 10

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_list_features_empty_result(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test listing features with empty result."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.get_all_features.return_value = []
        mock_get_service.return_value = mock_service

        result = await list_features(
            category=None,
            scope=None,
            status=None,
            page=1,
            per_page=50,
            current_user=mock_admin_user,
        )
        assert result.total == 0
        assert len(result.features) == 0
        assert result.has_next is False

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_list_features_service_exception(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test handling service exception."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.get_all_features.side_effect = Exception("Database error")
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await list_features(current_user=mock_admin_user)

        assert exc_info.value.status_code == 500
        assert "Failed to retrieve features" in exc_info.value.detail


class TestGetFeatureEndpoint:
    """Test get_feature endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_get_feature_success(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_toggle
    ):
        """Test getting a specific feature successfully."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.get_feature.return_value = sample_feature_toggle
        mock_get_service.return_value = mock_service

        result = await get_feature(
            feature_id="feature_test_1", current_user=mock_admin_user
        )

        assert result == sample_feature_toggle
        mock_service.get_feature.assert_called_once_with("feature_test_1")

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_get_feature_not_found(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test getting non-existent feature."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.get_feature.return_value = None
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await get_feature(feature_id="nonexistent", current_user=mock_admin_user)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_get_feature_service_exception(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test handling service exception (Session 87 pattern: HTTPException re-raising)."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.get_feature.side_effect = Exception("Database error")
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await get_feature(feature_id="feature_test_1", current_user=mock_admin_user)

        assert exc_info.value.status_code == 500
        assert "Failed to retrieve feature" in exc_info.value.detail


class TestGetUserFeaturesEndpoint:
    """Test get_user_features endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_get_user_features_success(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test getting user features successfully."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.get_user_features.return_value = {
            "feature1": True,
            "feature2": False,
        }
        mock_get_service.return_value = mock_service

        result = await get_user_features(
            user_id="user123", user_roles="admin,parent", current_user=mock_admin_user
        )

        assert result == {"feature1": True, "feature2": False}
        mock_service.get_user_features.assert_called_once_with(
            "user123", ["admin", "parent"]
        )

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_get_user_features_no_roles(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test getting user features without roles."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.get_user_features.return_value = {}
        mock_get_service.return_value = mock_service

        result = await get_user_features(
            user_id="user123", user_roles=None, current_user=mock_admin_user
        )

        mock_service.get_user_features.assert_called_once_with("user123", None)

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_get_user_features_exception(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test handling exception."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.get_user_features.side_effect = Exception("Service error")
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await get_user_features(user_id="user123", current_user=mock_admin_user)

        assert exc_info.value.status_code == 500
        assert "Failed to get user features" in exc_info.value.detail


class TestGetFeatureStatisticsEndpoint:
    """Test get_feature_statistics endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_get_feature_statistics_success(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test getting feature statistics successfully."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.get_feature_statistics.return_value = {
            "total_features": 10,
            "enabled_features": 7,
            "disabled_features": 3,
            "experimental_features": 2,
            "features_by_category": {"tutor_modes": 5, "scenarios": 5},
            "features_by_scope": {"global": 8, "user_specific": 2},
            "features_by_environment": {"development": {"enabled": 7, "disabled": 3}},
            "cache_size": 100,
            "total_users_with_overrides": 15,
            "total_events": 50,
        }
        mock_get_service.return_value = mock_service

        result = await get_feature_statistics(current_user=mock_admin_user)

        assert isinstance(result, FeatureToggleStatsResponse)
        assert result.total_features == 10
        assert result.enabled_features == 7
        assert result.disabled_features == 3
        assert result.experimental_features == 2
        assert result.usage_metrics["cache_size"] == 100

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_get_feature_statistics_exception(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test handling exception."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.get_feature_statistics.side_effect = Exception("Stats error")
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await get_feature_statistics(current_user=mock_admin_user)

        assert exc_info.value.status_code == 500
        assert "Failed to get feature statistics" in exc_info.value.detail


class TestCheckUserFeatureStatusEndpoint:
    """Test check_user_feature_status endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_check_user_feature_status_enabled(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_toggle
    ):
        """Test checking feature status when enabled."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.is_feature_enabled.return_value = True
        mock_service.get_feature.return_value = sample_feature_toggle
        mock_get_service.return_value = mock_service

        result = await check_user_feature_status(
            feature_id="feature_test_1",
            user_id="user123",
            user_roles="admin,parent",
            current_user=mock_admin_user,
        )

        assert isinstance(result, UserFeatureStatusResponse)
        assert result.enabled is True
        assert result.user_id == "user123"
        assert result.feature_id == "feature_test_1"

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_check_user_feature_status_disabled(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_toggle
    ):
        """Test checking feature status when disabled."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.is_feature_enabled.return_value = False
        sample_feature_toggle.status = FeatureToggleStatus.DISABLED
        mock_service.get_feature.return_value = sample_feature_toggle
        mock_get_service.return_value = mock_service

        result = await check_user_feature_status(
            feature_id="feature_test_1",
            user_id="user123",
            user_roles=None,
            current_user=mock_admin_user,
        )

        assert result.enabled is False
        assert result.reason == "globally disabled"

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_check_user_feature_status_not_found(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test checking status for non-existent feature (Session 87: HTTPException re-raising)."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.is_feature_enabled.return_value = False
        mock_service.get_feature.return_value = None
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await check_user_feature_status(
                feature_id="nonexistent",
                user_id="user123",
                user_roles=None,
                current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_check_user_feature_status_exception(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test handling exception."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.is_feature_enabled.side_effect = Exception("Check error")
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await check_user_feature_status(
                feature_id="feature_test_1",
                user_id="user123",
                current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == 500


class TestPublicCheckFeatureEndpoint:
    """Test public_check_feature endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_public_check_feature_authenticated_user(
        self, mock_get_service, mock_admin_user
    ):
        """Test public check with authenticated user."""
        mock_service = AsyncMock()
        mock_service.is_feature_enabled.return_value = True
        mock_get_service.return_value = mock_service

        result = await public_check_feature(
            feature_id="feature_test_1", current_user=mock_admin_user
        )

        assert result["feature_id"] == "feature_test_1"
        assert result["enabled"] is True
        assert result["user_authenticated"] is True

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_public_check_feature_unauthenticated_user(self, mock_get_service):
        """Test public check without authenticated user."""
        mock_service = AsyncMock()
        mock_service.is_feature_enabled.return_value = False
        mock_get_service.return_value = mock_service

        result = await public_check_feature(
            feature_id="feature_test_1", current_user=None
        )

        assert result["feature_id"] == "feature_test_1"
        assert result["enabled"] is False
        assert result["user_authenticated"] is False

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_public_check_feature_exception(self, mock_get_service):
        """Test handling exception."""
        mock_service = AsyncMock()
        mock_service.is_feature_enabled.side_effect = Exception("Check error")
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await public_check_feature(feature_id="feature_test_1", current_user=None)

        assert exc_info.value.status_code == 500


# ============================================================================
# API ENDPOINT TESTS - POST/PUT/DELETE OPERATIONS
# ============================================================================


class TestCreateFeatureEndpoint:
    """Test create_feature endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_create_feature_success(
        self,
        mock_get_service,
        mock_check_perm,
        mock_admin_user,
        sample_feature_request,
        sample_feature_toggle,
    ):
        """Test creating feature successfully."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.create_feature.return_value = sample_feature_toggle
        mock_get_service.return_value = mock_service

        result = await create_feature(
            feature_request=sample_feature_request, current_user=mock_admin_user
        )

        assert isinstance(result, FeatureToggleResponse)
        assert result.success is True
        assert "created successfully" in result.message
        assert result.feature == sample_feature_toggle

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_create_feature_validation_error(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_request
    ):
        """Test handling validation error."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        # Create a proper Pydantic ValidationError
        try:
            # Force a validation error by creating invalid model
            FeatureToggleRequest(name="", description="", category="invalid")
        except ValidationError as ve:
            mock_service.create_feature.side_effect = ve
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await create_feature(
                feature_request=sample_feature_request, current_user=mock_admin_user
            )

        assert exc_info.value.status_code == 422
        assert "Validation error" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_create_feature_service_exception(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_request
    ):
        """Test handling service exception."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.create_feature.side_effect = Exception("Database error")
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await create_feature(
                feature_request=sample_feature_request, current_user=mock_admin_user
            )

        assert exc_info.value.status_code == 500
        assert "Failed to create feature toggle" in exc_info.value.detail


class TestUpdateFeatureEndpoint:
    """Test update_feature endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_update_feature_success(
        self,
        mock_get_service,
        mock_check_perm,
        mock_admin_user,
        sample_update_request,
        sample_feature_toggle,
    ):
        """Test updating feature successfully."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.update_feature.return_value = sample_feature_toggle
        mock_get_service.return_value = mock_service

        result = await update_feature(
            feature_id="feature_test_1",
            update_request=sample_update_request,
            current_user=mock_admin_user,
        )

        assert isinstance(result, FeatureToggleResponse)
        assert result.success is True
        assert "updated successfully" in result.message

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_update_feature_not_found(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_update_request
    ):
        """Test updating non-existent feature (Session 87: HTTPException re-raising)."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.update_feature.return_value = None
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await update_feature(
                feature_id="nonexistent",
                update_request=sample_update_request,
                current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_update_feature_validation_error(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_update_request
    ):
        """Test handling validation error."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        # Create a proper Pydantic ValidationError
        try:
            # Force a validation error by creating invalid model
            FeatureToggleUpdateRequest(rollout_percentage=150.0)  # Invalid, > 100
        except ValidationError as ve:
            mock_service.update_feature.side_effect = ve
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await update_feature(
                feature_id="feature_test_1",
                update_request=sample_update_request,
                current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_update_feature_service_exception(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_update_request
    ):
        """Test handling service exception."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.update_feature.side_effect = Exception("Update error")
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await update_feature(
                feature_id="feature_test_1",
                update_request=sample_update_request,
                current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == 500


class TestDeleteFeatureEndpoint:
    """Test delete_feature endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_delete_feature_success(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test deleting feature successfully."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.delete_feature.return_value = True
        mock_get_service.return_value = mock_service

        result = await delete_feature(
            feature_id="feature_test_1", current_user=mock_admin_user
        )

        assert isinstance(result, FeatureToggleResponse)
        assert result.success is True
        assert "deleted successfully" in result.message

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_delete_feature_not_found(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test deleting non-existent feature (Session 87: HTTPException re-raising)."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.delete_feature.return_value = False
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await delete_feature(feature_id="nonexistent", current_user=mock_admin_user)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_delete_feature_service_exception(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test handling service exception."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.delete_feature.side_effect = Exception("Delete error")
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await delete_feature(
                feature_id="feature_test_1", current_user=mock_admin_user
            )

        assert exc_info.value.status_code == 500


class TestEnableFeatureEndpoint:
    """Test enable_feature endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_enable_feature_success(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_toggle
    ):
        """Test enabling feature successfully."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.update_feature.return_value = sample_feature_toggle
        mock_get_service.return_value = mock_service

        result = await enable_feature(
            feature_id="feature_test_1", current_user=mock_admin_user
        )

        assert isinstance(result, FeatureToggleResponse)
        assert result.success is True
        assert "enabled successfully" in result.message
        # Verify the update request has correct status
        call_args = mock_service.update_feature.call_args
        assert call_args[0][1].status == FeatureToggleStatus.ENABLED

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_enable_feature_not_found(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test enabling non-existent feature (Session 87: HTTPException re-raising)."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.update_feature.return_value = None
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await enable_feature(feature_id="nonexistent", current_user=mock_admin_user)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_enable_feature_service_exception(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test handling service exception."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.update_feature.side_effect = Exception("Enable error")
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await enable_feature(
                feature_id="feature_test_1", current_user=mock_admin_user
            )

        assert exc_info.value.status_code == 500


class TestDisableFeatureEndpoint:
    """Test disable_feature endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_disable_feature_success(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_toggle
    ):
        """Test disabling feature successfully."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.update_feature.return_value = sample_feature_toggle
        mock_get_service.return_value = mock_service

        result = await disable_feature(
            feature_id="feature_test_1", current_user=mock_admin_user
        )

        assert isinstance(result, FeatureToggleResponse)
        assert result.success is True
        assert "disabled successfully" in result.message
        # Verify the update request has correct status
        call_args = mock_service.update_feature.call_args
        assert call_args[0][1].status == FeatureToggleStatus.DISABLED

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_disable_feature_not_found(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test disabling non-existent feature (Session 87: HTTPException re-raising)."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.update_feature.return_value = None
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await disable_feature(
                feature_id="nonexistent", current_user=mock_admin_user
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_disable_feature_service_exception(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test handling service exception."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.update_feature.side_effect = Exception("Disable error")
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await disable_feature(
                feature_id="feature_test_1", current_user=mock_admin_user
            )

        assert exc_info.value.status_code == 500


class TestSetUserFeatureAccessEndpoint:
    """Test set_user_feature_access endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_set_user_feature_access_grant(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test granting user feature access."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.set_user_feature_access.return_value = True
        mock_get_service.return_value = mock_service

        result = await set_user_feature_access(
            user_id="user123",
            feature_id="feature_test_1",
            enabled=True,
            override_global=False,
            override_reason=None,
            expires_hours=None,
            current_user=mock_admin_user,
        )

        assert isinstance(result, FeatureToggleResponse)
        assert result.success is True
        assert "granted" in result.message

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_set_user_feature_access_revoke(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test revoking user feature access."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.set_user_feature_access.return_value = True
        mock_get_service.return_value = mock_service

        result = await set_user_feature_access(
            user_id="user123",
            feature_id="feature_test_1",
            enabled=False,
            override_global=False,
            override_reason=None,
            expires_hours=None,
            current_user=mock_admin_user,
        )

        assert result.success is True
        assert "revoked" in result.message

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_set_user_feature_access_with_expiry(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test setting user feature access with expiry."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.set_user_feature_access.return_value = True
        mock_get_service.return_value = mock_service

        result = await set_user_feature_access(
            user_id="user123",
            feature_id="feature_test_1",
            enabled=True,
            override_global=True,
            override_reason="Testing",
            expires_hours=24,
            current_user=mock_admin_user,
        )

        assert result.success is True
        # Verify expiry was calculated
        call_args = mock_service.set_user_feature_access.call_args[1]
        assert call_args["override_expires"] is not None

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_set_user_feature_access_not_found(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test setting access for non-existent feature (Session 87: HTTPException re-raising)."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.set_user_feature_access.return_value = False
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await set_user_feature_access(
                user_id="user123",
                feature_id="nonexistent",
                enabled=True,
                override_global=False,
                override_reason=None,
                expires_hours=None,
                current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_set_user_feature_access_service_exception(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test handling service exception."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.set_user_feature_access.side_effect = Exception("Access error")
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await set_user_feature_access(
                user_id="user123",
                feature_id="feature_test_1",
                enabled=True,
                current_user=mock_admin_user,
            )

        assert exc_info.value.status_code == 500


class TestBulkUpdateFeaturesEndpoint:
    """Test bulk_update_features endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_bulk_update_features_all_success(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_toggle
    ):
        """Test bulk updating all features successfully."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_service.update_feature.return_value = sample_feature_toggle
        mock_get_service.return_value = mock_service

        updates = {
            "feature1": FeatureToggleUpdateRequest(status=FeatureToggleStatus.ENABLED),
            "feature2": FeatureToggleUpdateRequest(status=FeatureToggleStatus.DISABLED),
        }

        result = await bulk_update_features(
            updates=updates, current_user=mock_admin_user
        )

        assert isinstance(result, FeatureToggleResponse)
        assert result.success is True
        assert "Updated 2 features successfully" in result.message
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_bulk_update_features_partial_success(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_toggle
    ):
        """Test bulk updating with some failures."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        # First update succeeds, second returns None (not found)
        mock_service.update_feature.side_effect = [sample_feature_toggle, None]
        mock_get_service.return_value = mock_service

        updates = {
            "feature1": FeatureToggleUpdateRequest(status=FeatureToggleStatus.ENABLED),
            "feature2": FeatureToggleUpdateRequest(status=FeatureToggleStatus.DISABLED),
        }

        result = await bulk_update_features(
            updates=updates, current_user=mock_admin_user
        )

        assert result.success is False
        assert "Updated 1 features successfully, 1 errors" in result.message
        assert len(result.errors) == 1
        assert "not found" in result.errors[0]

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_bulk_update_features_with_exceptions(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_toggle
    ):
        """Test bulk updating with update exceptions."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        # First succeeds, second raises exception
        mock_service.update_feature.side_effect = [
            sample_feature_toggle,
            Exception("Update failed"),
        ]
        mock_get_service.return_value = mock_service

        updates = {
            "feature1": FeatureToggleUpdateRequest(status=FeatureToggleStatus.ENABLED),
            "feature2": FeatureToggleUpdateRequest(status=FeatureToggleStatus.DISABLED),
        }

        result = await bulk_update_features(
            updates=updates, current_user=mock_admin_user
        )

        assert result.success is False
        assert len(result.errors) == 1
        assert "Error updating" in result.errors[0]

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_bulk_update_features_service_exception(
        self, mock_get_service, mock_check_perm, mock_admin_user
    ):
        """Test handling service exception."""
        mock_check_perm.return_value = None
        mock_get_service.side_effect = Exception("Service error")

        updates = {
            "feature1": FeatureToggleUpdateRequest(status=FeatureToggleStatus.ENABLED)
        }

        with pytest.raises(HTTPException) as exc_info:
            await bulk_update_features(updates=updates, current_user=mock_admin_user)

        assert exc_info.value.status_code == 500


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestFeatureToggleWorkflows:
    """Test complete feature toggle workflows."""

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_complete_feature_lifecycle(
        self,
        mock_get_service,
        mock_check_perm,
        mock_admin_user,
        sample_feature_request,
        sample_feature_toggle,
    ):
        """Test complete lifecycle: create, update, check, delete."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service

        # Create
        mock_service.create_feature.return_value = sample_feature_toggle
        create_result = await create_feature(
            feature_request=sample_feature_request, current_user=mock_admin_user
        )
        assert create_result.success is True

        # Update
        mock_service.update_feature.return_value = sample_feature_toggle
        update_result = await update_feature(
            feature_id="feature_test_1",
            update_request=FeatureToggleUpdateRequest(
                status=FeatureToggleStatus.ENABLED
            ),
            current_user=mock_admin_user,
        )
        assert update_result.success is True

        # Check status
        mock_service.is_feature_enabled.return_value = True
        mock_service.get_feature.return_value = sample_feature_toggle
        check_result = await check_user_feature_status(
            feature_id="feature_test_1",
            user_id="user123",
            user_roles=None,
            current_user=mock_admin_user,
        )
        assert check_result.enabled is True

        # Delete
        mock_service.delete_feature.return_value = True
        delete_result = await delete_feature(
            feature_id="feature_test_1", current_user=mock_admin_user
        )
        assert delete_result.success is True

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_feature_access_management_workflow(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_toggle
    ):
        """Test user access management workflow."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service

        # Grant access
        mock_service.set_user_feature_access.return_value = True
        grant_result = await set_user_feature_access(
            user_id="user123",
            feature_id="feature_test_1",
            enabled=True,
            override_global=True,
            override_reason="Beta testing",
            expires_hours=48,
            current_user=mock_admin_user,
        )
        assert grant_result.success is True

        # Check user features
        mock_service.get_user_features.return_value = {"feature_test_1": True}
        features_result = await get_user_features(
            user_id="user123", user_roles=None, current_user=mock_admin_user
        )
        assert features_result["feature_test_1"] is True

        # Revoke access
        revoke_result = await set_user_feature_access(
            user_id="user123",
            feature_id="feature_test_1",
            enabled=False,
            override_global=False,
            override_reason=None,
            expires_hours=None,
            current_user=mock_admin_user,
        )
        assert revoke_result.success is True

    @pytest.mark.asyncio
    @patch("app.api.feature_toggles.check_admin_permission", new_callable=AsyncMock)
    @patch("app.api.feature_toggles.get_feature_toggle_service")
    async def test_feature_statistics_workflow(
        self, mock_get_service, mock_check_perm, mock_admin_user, sample_feature_toggle
    ):
        """Test feature statistics and monitoring workflow."""
        mock_check_perm.return_value = None
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service

        # List all features
        mock_service.get_all_features.return_value = [sample_feature_toggle] * 5
        list_result = await list_features(
            category=None,
            scope=None,
            status=None,
            page=1,
            per_page=50,
            current_user=mock_admin_user,
        )
        assert list_result.total == 5

        # Get statistics
        mock_service.get_feature_statistics.return_value = {
            "total_features": 5,
            "enabled_features": 3,
            "disabled_features": 2,
            "experimental_features": 1,
            "features_by_category": {"tutor_modes": 5},
            "features_by_scope": {"global": 5},
            "features_by_environment": {"development": {"enabled": 3, "disabled": 2}},
            "cache_size": 100,
            "total_users_with_overrides": 10,
            "total_events": 25,
        }
        stats_result = await get_feature_statistics(current_user=mock_admin_user)
        assert stats_result.total_features == 5
        assert stats_result.enabled_features == 3
