"""
Comprehensive tests for app/api/ai_models.py
Testing all 15 API endpoints with FastAPI TestClient

Coverage Target: TRUE 100% (293 statements, 112 branches)
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.ai_models import (
    ModelOptimizationRequest,
    ModelUpdateRequest,
    PerformanceReportRequest,
    _apply_all_filters,
    _build_statistics_response,
    _calculate_provider_breakdown,
    _calculate_summary_stats,
    _filter_by_provider,
    _filter_by_search,
    _filter_by_status,
    _filter_models,
    _set_default_date_range,
    router,
)
from app.services.ai_model_manager import ModelCategory, ModelStatus


# Test fixtures
@pytest.fixture
def mock_admin_user():
    """Mock admin user for authentication"""
    return {"user_id": "admin123", "role": "admin"}


@pytest.fixture
def sample_model():
    """Sample model data"""
    return {
        "id": "claude-3-sonnet",
        "provider": "claude",
        "model_name": "claude-3-sonnet-20240229",
        "display_name": "Claude 3 Sonnet",
        "category": "conversation",
        "status": "active",
        "enabled": True,
        "priority": 1,
        "usage_stats": {
            "total_requests": 100,
            "total_cost": 1.25,
            "success_rate": 0.98,
        },
    }


@pytest.fixture
def sample_models():
    """List of sample models"""
    return [
        {
            "id": "claude-3-sonnet",
            "provider": "claude",
            "model_name": "claude-3-sonnet-20240229",
            "display_name": "Claude 3 Sonnet",
            "category": "conversation",
            "status": "active",
            "enabled": True,
            "priority": 1,
            "usage_stats": {
                "total_requests": 100,
                "total_cost": 1.25,
                "success_rate": 0.98,
            },
        },
        {
            "id": "mistral-large",
            "provider": "mistral",
            "model_name": "mistral-large-latest",
            "display_name": "Mistral Large",
            "category": "conversation",
            "status": "active",
            "enabled": True,
            "priority": 2,
            "usage_stats": {
                "total_requests": 50,
                "total_cost": 0.75,
                "success_rate": 0.95,
            },
        },
        {
            "id": "deepseek-coder",
            "provider": "deepseek",
            "model_name": "deepseek-coder",
            "display_name": "DeepSeek Coder",
            "category": "code",
            "status": "inactive",
            "enabled": False,
            "priority": 5,
            "usage_stats": {
                "total_requests": 10,
                "total_cost": 0.10,
                "success_rate": 0.90,
            },
        },
    ]


@pytest.fixture
def sample_performance_report():
    """Sample performance report"""

    # Create a simple object with __dict__ attribute
    class PerformanceReport:
        def __init__(self):
            self.model_id = "claude-3-sonnet"
            self.period_days = 30
            self.total_requests = 100
            self.success_rate = 0.98
            self.avg_response_time = 1.2
            self.total_cost = 1.25
            self.recommendations = ["Increase priority for high success rate"]

    return PerformanceReport()


# ============================================================================
# TEST CLASS 1: Pydantic Request Models
# ============================================================================


class TestPydanticModels:
    """Test Pydantic request model validation"""

    def test_model_update_request_valid(self):
        """Test ModelUpdateRequest with valid data"""
        data = {
            "display_name": "Updated Model",
            "status": "active",
            "priority": 5,
            "weight": 1.5,
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5,
            "quality_score": 0.95,
            "reliability_score": 0.98,
            "enabled": True,
        }
        request = ModelUpdateRequest(**data)
        assert request.display_name == "Updated Model"
        assert request.priority == 5
        assert request.temperature == 0.7

    def test_model_update_request_partial(self):
        """Test ModelUpdateRequest with partial data"""
        data = {"display_name": "Updated", "priority": 3}
        request = ModelUpdateRequest(**data)
        assert request.display_name == "Updated"
        assert request.priority == 3
        assert request.status is None

    def test_model_update_request_priority_validation(self):
        """Test priority validation (1-10)"""
        with pytest.raises(Exception):  # Pydantic validation error
            ModelUpdateRequest(priority=0)
        with pytest.raises(Exception):
            ModelUpdateRequest(priority=11)

    def test_model_optimization_request_valid(self):
        """Test ModelOptimizationRequest with valid data"""
        request = ModelOptimizationRequest(
            language="fr",
            use_case="translation",
            budget_limit=10.0,
            max_response_time=2.0,
            min_quality_score=0.9,
        )
        assert request.language == "fr"
        assert request.use_case == "translation"
        assert request.budget_limit == 10.0

    def test_model_optimization_request_defaults(self):
        """Test ModelOptimizationRequest default values"""
        request = ModelOptimizationRequest()
        assert request.language == "en"
        assert request.use_case == "conversation"
        assert request.budget_limit is None

    def test_performance_report_request_valid(self):
        """Test PerformanceReportRequest with valid data"""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)
        request = PerformanceReportRequest(
            model_id="claude-3-sonnet",
            start_date=start,
            end_date=end,
            include_comparisons=False,
            include_recommendations=False,
        )
        assert request.model_id == "claude-3-sonnet"
        assert request.start_date == start
        assert request.include_comparisons is False

    def test_performance_report_request_defaults(self):
        """Test PerformanceReportRequest default values"""
        request = PerformanceReportRequest()
        assert request.model_id is None
        assert request.include_comparisons is True
        assert request.include_recommendations is True


# ============================================================================
# TEST CLASS 2: Helper Functions - Filter Functions
# ============================================================================


class TestFilterFunctions:
    """Test helper filter functions"""

    def test_filter_by_provider_with_provider(self, sample_models):
        """Test filtering by provider"""
        result = _filter_by_provider(sample_models, "claude")
        assert len(result) == 1
        assert result[0]["provider"] == "claude"

    def test_filter_by_provider_no_provider(self, sample_models):
        """Test filter with no provider returns all"""
        result = _filter_by_provider(sample_models, None)
        assert len(result) == 3
        assert result == sample_models

    def test_filter_by_provider_case_insensitive(self, sample_models):
        """Test provider filter is case-insensitive"""
        result = _filter_by_provider(sample_models, "MISTRAL")
        assert len(result) == 1
        assert result[0]["provider"] == "mistral"

    def test_filter_by_status_with_status(self, sample_models):
        """Test filtering by status"""
        result = _filter_by_status(sample_models, "active")
        assert len(result) == 2
        assert all(m["status"] == "active" for m in result)

    def test_filter_by_status_no_status(self, sample_models):
        """Test filter with no status returns all"""
        result = _filter_by_status(sample_models, None)
        assert len(result) == 3

    def test_filter_by_status_case_insensitive(self, sample_models):
        """Test status filter is case-insensitive"""
        result = _filter_by_status(sample_models, "INACTIVE")
        assert len(result) == 1
        assert result[0]["status"] == "inactive"

    def test_filter_by_search_display_name(self, sample_models):
        """Test search in display name"""
        result = _filter_by_search(sample_models, "claude")
        assert len(result) == 1
        assert "Claude" in result[0]["display_name"]

    def test_filter_by_search_model_name(self, sample_models):
        """Test search in model name"""
        result = _filter_by_search(sample_models, "coder")
        assert len(result) == 1
        assert "coder" in result[0]["model_name"]

    def test_filter_by_search_provider(self, sample_models):
        """Test search in provider"""
        result = _filter_by_search(sample_models, "mistral")
        assert len(result) == 1
        assert result[0]["provider"] == "mistral"

    def test_filter_by_search_no_search(self, sample_models):
        """Test filter with no search returns all"""
        result = _filter_by_search(sample_models, None)
        assert len(result) == 3

    def test_filter_by_search_case_insensitive(self, sample_models):
        """Test search is case-insensitive"""
        result = _filter_by_search(sample_models, "DEEPSEEK")
        assert len(result) == 1

    def test_filter_by_search_no_matches(self, sample_models):
        """Test search with no matches returns empty"""
        result = _filter_by_search(sample_models, "nonexistent")
        assert len(result) == 0

    def test_apply_all_filters_combined(self, sample_models):
        """Test applying all filters together"""
        result = _apply_all_filters(sample_models, "claude", "active", None)
        assert len(result) == 1
        assert result[0]["id"] == "claude-3-sonnet"

    def test_apply_all_filters_no_filters(self, sample_models):
        """Test apply_all_filters with no filters"""
        result = _apply_all_filters(sample_models, None, None, None)
        assert len(result) == 3


# ============================================================================
# TEST CLASS 3: Helper Functions - Statistics Functions
# ============================================================================


class TestStatisticsFunctions:
    """Test helper statistics calculation functions"""

    def test_set_default_date_range_both_provided(self):
        """Test date range when both dates provided"""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)
        result_start, result_end = _set_default_date_range(start, end)
        assert result_start == start
        assert result_end == end

    def test_set_default_date_range_no_dates(self):
        """Test date range with no dates (defaults to last 30 days)"""
        result_start, result_end = _set_default_date_range(None, None)
        assert isinstance(result_start, datetime)
        assert isinstance(result_end, datetime)
        assert (result_end - result_start).days == 30

    def test_set_default_date_range_only_end(self):
        """Test date range with only end date"""
        end = datetime(2024, 1, 31)
        result_start, result_end = _set_default_date_range(None, end)
        assert result_end == end
        assert (result_end - result_start).days == 30

    def test_filter_models_by_provider(self, sample_models):
        """Test filtering models by provider"""
        result = _filter_models(sample_models, "claude", None)
        assert len(result) == 1
        assert result[0]["provider"] == "claude"

    def test_filter_models_by_model_id(self, sample_models):
        """Test filtering models by model_id"""
        result = _filter_models(sample_models, None, "mistral-large")
        assert len(result) == 1
        assert result[0]["id"] == "mistral-large"

    def test_filter_models_both_filters(self, sample_models):
        """Test filtering with both provider and model_id"""
        result = _filter_models(sample_models, "claude", "claude-3-sonnet")
        assert len(result) == 1
        assert result[0]["id"] == "claude-3-sonnet"

    def test_filter_models_no_filters(self, sample_models):
        """Test filtering with no filters"""
        result = _filter_models(sample_models, None, None)
        assert len(result) == 3

    def test_calculate_summary_stats(self, sample_models):
        """Test summary statistics calculation"""
        result = _calculate_summary_stats(sample_models)
        assert result["total_models"] == 3
        assert result["total_requests"] == 160  # 100 + 50 + 10
        assert result["total_cost"] == 2.1  # 1.25 + 0.75 + 0.10
        assert result["avg_success_rate"] > 0.9

    def test_calculate_summary_stats_empty_models(self):
        """Test summary stats with empty model list"""
        result = _calculate_summary_stats([])
        assert result["total_models"] == 0
        assert result["total_requests"] == 0
        assert result["total_cost"] == 0.0

    def test_calculate_provider_breakdown(self, sample_models):
        """Test provider breakdown calculation"""
        result = _calculate_provider_breakdown(sample_models)
        assert "claude" in result
        assert "mistral" in result
        assert "deepseek" in result
        assert result["claude"]["models"] == 1
        assert result["claude"]["total_requests"] == 100

    def test_calculate_provider_breakdown_averages(self, sample_models):
        """Test provider breakdown calculates averages correctly"""
        result = _calculate_provider_breakdown(sample_models)
        # Each provider has 1 model, so avg_success_rate equals success_rate
        assert result["claude"]["avg_success_rate"] == 0.98
        assert result["mistral"]["avg_success_rate"] == 0.95

    def test_build_statistics_response(self, sample_models):
        """Test building statistics response"""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)
        summary = {"total_models": 3}
        provider_stats = {"claude": {"models": 1}}

        response = _build_statistics_response(
            start, end, summary, provider_stats, sample_models
        )

        assert response.status_code == 200
        # Parse JSON content
        import json

        content = json.loads(response.body.decode())
        assert "period" in content
        assert "summary" in content
        assert "provider_breakdown" in content
        assert content["period"]["days"] == 30


# ============================================================================
# TEST CLASS 4: GET /overview Endpoint
# ============================================================================


class TestGetSystemOverview:
    """Test GET /overview endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_system_overview_success(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test successful system overview retrieval"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_system_overview = AsyncMock(
            return_value={
                "total_models": 10,
                "active_models": 8,
                "total_requests": 1000,
                "total_cost": 25.50,
            }
        )

        from app.api.ai_models import get_system_overview

        result = await get_system_overview(mock_admin_user)

        assert result.status_code == 200
        mock_manager.get_system_overview.assert_called_once()

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_system_overview_error(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test system overview with service error"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_system_overview = AsyncMock(
            side_effect=Exception("Service error")
        )

        from app.api.ai_models import get_system_overview

        with pytest.raises(HTTPException) as exc:
            await get_system_overview(mock_admin_user)

        assert exc.value.status_code == 500
        assert "Failed to get system overview" in exc.value.detail


# ============================================================================
# TEST CLASS 5: GET /models Endpoint
# ============================================================================


class TestGetModels:
    """Test GET /models endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_models_no_filters(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test getting all models without filters"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import get_models

        result = await get_models(
            category=None,
            provider=None,
            status=None,
            enabled_only=False,
            search=None,
            admin_user=mock_admin_user,
        )

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert content["total"] == 3
        assert len(content["models"]) == 3

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_models_with_category(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test getting models filtered by category"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=sample_models[:2])

        from app.api.ai_models import get_models

        result = await get_models(
            category="conversation",
            provider=None,
            status=None,
            enabled_only=False,
            search=None,
            admin_user=mock_admin_user,
        )

        mock_manager.get_all_models.assert_called_once_with(
            category="conversation", enabled_only=False
        )

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_models_enabled_only(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test getting only enabled models"""
        enabled_models = [m for m in sample_models if m["enabled"]]
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=enabled_models)

        from app.api.ai_models import get_models

        result = await get_models(
            category=None,
            provider=None,
            status=None,
            enabled_only=True,
            search=None,
            admin_user=mock_admin_user,
        )

        import json

        content = json.loads(result.body.decode())
        assert content["total"] == 2

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_models_with_provider_filter(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test filtering models by provider"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import get_models

        result = await get_models(
            category=None,
            provider="claude",
            status=None,
            enabled_only=False,
            search=None,
            admin_user=mock_admin_user,
        )

        import json

        content = json.loads(result.body.decode())
        assert content["total"] == 1
        assert content["models"][0]["provider"] == "claude"

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_models_with_search(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test searching models"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import get_models

        result = await get_models(
            category=None,
            provider=None,
            status=None,
            enabled_only=False,
            search="Sonnet",
            admin_user=mock_admin_user,
        )

        import json

        content = json.loads(result.body.decode())
        assert content["total"] == 1

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_models_error(self, mock_manager, mock_auth, mock_admin_user):
        """Test get models with service error"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(side_effect=Exception("DB error"))

        from app.api.ai_models import get_models

        with pytest.raises(HTTPException) as exc:
            await get_models(
                category=None,
                provider=None,
                status=None,
                enabled_only=False,
                search=None,
                admin_user=mock_admin_user,
            )

        assert exc.value.status_code == 500
        assert "Failed to retrieve models" in exc.value.detail


# ============================================================================
# TEST CLASS 6: GET /models/{model_id} Endpoint
# ============================================================================


class TestGetModel:
    """Test GET /models/{model_id} endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_model_success(
        self,
        mock_manager,
        mock_auth,
        mock_admin_user,
        sample_model,
        sample_performance_report,
    ):
        """Test successful model retrieval"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(return_value=sample_model)
        mock_manager.get_model_performance_report = AsyncMock(
            return_value=sample_performance_report
        )

        from app.api.ai_models import get_model

        result = await get_model("claude-3-sonnet", mock_admin_user)

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert content["model"]["id"] == "claude-3-sonnet"
        assert "performance_report" in content

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_model_not_found(self, mock_manager, mock_auth, mock_admin_user):
        """Test getting non-existent model"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(return_value=None)

        from app.api.ai_models import get_model

        with pytest.raises(HTTPException) as exc:
            await get_model("nonexistent", mock_admin_user)

        assert exc.value.status_code == 404
        assert "Model not found" in exc.value.detail

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_model_with_no_performance_report(
        self, mock_manager, mock_auth, mock_admin_user, sample_model
    ):
        """Test model retrieval when no performance report available"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(return_value=sample_model)
        mock_manager.get_model_performance_report = AsyncMock(return_value=None)

        from app.api.ai_models import get_model

        result = await get_model("claude-3-sonnet", mock_admin_user)

        import json

        content = json.loads(result.body.decode())
        assert content["performance_report"] is None

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_model_service_error(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test get model with service error"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(side_effect=Exception("Service error"))

        from app.api.ai_models import get_model

        with pytest.raises(HTTPException) as exc:
            await get_model("claude-3-sonnet", mock_admin_user)

        assert exc.value.status_code == 500
        assert "Failed to retrieve model" in exc.value.detail


# ============================================================================
# TEST CLASS 7: PUT /models/{model_id} Endpoint
# ============================================================================


class TestUpdateModel:
    """Test PUT /models/{model_id} endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_update_model_success(
        self, mock_manager, mock_auth, mock_admin_user, sample_model
    ):
        """Test successful model update"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(return_value=sample_model)
        mock_manager.update_model = AsyncMock(return_value=True)

        updated_model = sample_model.copy()
        updated_model["display_name"] = "Updated Name"
        mock_manager.get_model = AsyncMock(side_effect=[sample_model, updated_model])

        from app.api.ai_models import update_model

        update_data = ModelUpdateRequest(display_name="Updated Name", priority=5)
        result = await update_model("claude-3-sonnet", update_data, mock_admin_user)

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert "model" in content
        assert content["message"] == "Model updated successfully"

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_update_model_not_found(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test updating non-existent model"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(return_value=None)

        from app.api.ai_models import update_model

        update_data = ModelUpdateRequest(display_name="Updated")
        with pytest.raises(HTTPException) as exc:
            await update_model("nonexistent", update_data, mock_admin_user)

        assert exc.value.status_code == 404
        assert "Model not found" in exc.value.detail

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_update_model_invalid_status(
        self, mock_manager, mock_auth, mock_admin_user, sample_model
    ):
        """Test update with invalid status value"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(return_value=sample_model)

        from app.api.ai_models import update_model

        update_data = ModelUpdateRequest(status="invalid_status")
        with pytest.raises(HTTPException) as exc:
            await update_model("claude-3-sonnet", update_data, mock_admin_user)

        assert exc.value.status_code == 400
        assert "Invalid status value" in exc.value.detail

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_update_model_valid_status(
        self, mock_manager, mock_auth, mock_admin_user, sample_model
    ):
        """Test update with valid status value"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(return_value=sample_model)
        mock_manager.update_model = AsyncMock(return_value=True)

        from app.api.ai_models import update_model

        update_data = ModelUpdateRequest(status="active")
        result = await update_model("claude-3-sonnet", update_data, mock_admin_user)

        assert result.status_code == 200

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_update_model_update_fails(
        self, mock_manager, mock_auth, mock_admin_user, sample_model
    ):
        """Test when update operation fails"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(return_value=sample_model)
        mock_manager.update_model = AsyncMock(return_value=False)

        from app.api.ai_models import update_model

        update_data = ModelUpdateRequest(priority=5)
        with pytest.raises(HTTPException) as exc:
            await update_model("claude-3-sonnet", update_data, mock_admin_user)

        assert exc.value.status_code == 400
        assert "Failed to update model" in exc.value.detail

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_update_model_service_error(
        self, mock_manager, mock_auth, mock_admin_user, sample_model
    ):
        """Test update with service error"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(return_value=sample_model)
        mock_manager.update_model = AsyncMock(side_effect=Exception("Service error"))

        from app.api.ai_models import update_model

        update_data = ModelUpdateRequest(priority=5)
        with pytest.raises(HTTPException) as exc:
            await update_model("claude-3-sonnet", update_data, mock_admin_user)

        assert exc.value.status_code == 500
        assert "Failed to update model" in exc.value.detail


# ============================================================================
# TEST CLASS 8: POST /models/{model_id}/toggle Endpoint
# ============================================================================


class TestToggleModel:
    """Test POST /models/{model_id}/toggle endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_toggle_model_enable(
        self, mock_manager, mock_auth, mock_admin_user, sample_model
    ):
        """Test enabling a disabled model"""
        mock_auth.return_value = mock_admin_user
        disabled_model = sample_model.copy()
        disabled_model["enabled"] = False

        enabled_model = sample_model.copy()
        enabled_model["enabled"] = True

        mock_manager.get_model = AsyncMock(side_effect=[disabled_model, enabled_model])
        mock_manager.enable_model = AsyncMock(return_value=True)

        from app.api.ai_models import toggle_model

        result = await toggle_model("claude-3-sonnet", mock_admin_user)

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert "enabled successfully" in content["message"]

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_toggle_model_disable(
        self, mock_manager, mock_auth, mock_admin_user, sample_model
    ):
        """Test disabling an enabled model"""
        mock_auth.return_value = mock_admin_user
        enabled_model = sample_model.copy()
        enabled_model["enabled"] = True

        disabled_model = sample_model.copy()
        disabled_model["enabled"] = False

        mock_manager.get_model = AsyncMock(side_effect=[enabled_model, disabled_model])
        mock_manager.disable_model = AsyncMock(return_value=True)

        from app.api.ai_models import toggle_model

        result = await toggle_model("claude-3-sonnet", mock_admin_user)

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert "disabled successfully" in content["message"]

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_toggle_model_not_found(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test toggling non-existent model"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(return_value=None)

        from app.api.ai_models import toggle_model

        with pytest.raises(HTTPException) as exc:
            await toggle_model("nonexistent", mock_admin_user)

        assert exc.value.status_code == 404
        assert "Model not found" in exc.value.detail

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_toggle_model_fails(
        self, mock_manager, mock_auth, mock_admin_user, sample_model
    ):
        """Test when toggle operation fails"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(return_value=sample_model)
        mock_manager.disable_model = AsyncMock(return_value=False)

        from app.api.ai_models import toggle_model

        with pytest.raises(HTTPException) as exc:
            await toggle_model("claude-3-sonnet", mock_admin_user)

        assert exc.value.status_code == 400
        assert "Failed to toggle model status" in exc.value.detail

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_toggle_model_service_error(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test toggle with service error"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(side_effect=Exception("Service error"))

        from app.api.ai_models import toggle_model

        with pytest.raises(HTTPException) as exc:
            await toggle_model("claude-3-sonnet", mock_admin_user)

        assert exc.value.status_code == 500
        assert "Failed to toggle model" in exc.value.detail


# ============================================================================
# TEST CLASS 9: POST /models/{model_id}/priority Endpoint
# ============================================================================


class TestSetModelPriority:
    """Test POST /models/{model_id}/priority endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_set_priority_success(
        self, mock_manager, mock_auth, mock_admin_user, sample_model
    ):
        """Test successfully setting model priority"""
        mock_auth.return_value = mock_admin_user
        mock_manager.set_model_priority = AsyncMock(return_value=True)
        mock_manager.get_model = AsyncMock(return_value=sample_model)

        from app.api.ai_models import set_model_priority

        result = await set_model_priority("claude-3-sonnet", 3, mock_admin_user)

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert "priority set to 3" in content["message"]

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_set_priority_fails(self, mock_manager, mock_auth, mock_admin_user):
        """Test when priority setting fails"""
        mock_auth.return_value = mock_admin_user
        mock_manager.set_model_priority = AsyncMock(return_value=False)

        from app.api.ai_models import set_model_priority

        with pytest.raises(HTTPException) as exc:
            await set_model_priority("claude-3-sonnet", 5, mock_admin_user)

        assert exc.value.status_code == 400
        assert "Failed to set model priority" in exc.value.detail

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_set_priority_service_error(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test set priority with service error"""
        mock_auth.return_value = mock_admin_user
        mock_manager.set_model_priority = AsyncMock(
            side_effect=Exception("Service error")
        )

        from app.api.ai_models import set_model_priority

        with pytest.raises(HTTPException) as exc:
            await set_model_priority("claude-3-sonnet", 5, mock_admin_user)

        assert exc.value.status_code == 500
        assert "Failed to set model priority" in exc.value.detail


# ============================================================================
# TEST CLASS 10: GET /performance/{model_id} Endpoint
# ============================================================================


class TestGetPerformanceReport:
    """Test GET /performance/{model_id} endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_performance_report_success(
        self, mock_manager, mock_auth, mock_admin_user, sample_performance_report
    ):
        """Test successful performance report retrieval"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model_performance_report = AsyncMock(
            return_value=sample_performance_report
        )

        from app.api.ai_models import get_performance_report

        result = await get_performance_report("claude-3-sonnet", 30, mock_admin_user)

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert "report" in content
        assert content["report"]["model_id"] == "claude-3-sonnet"

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_performance_report_not_found(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test performance report when no data available"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model_performance_report = AsyncMock(return_value=None)

        from app.api.ai_models import get_performance_report

        with pytest.raises(HTTPException) as exc:
            await get_performance_report("claude-3-sonnet", 30, mock_admin_user)

        assert exc.value.status_code == 404
        assert "No performance data available" in exc.value.detail

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_performance_report_service_error(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test performance report with service error"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model_performance_report = AsyncMock(
            side_effect=Exception("Service error")
        )

        from app.api.ai_models import get_performance_report

        with pytest.raises(HTTPException) as exc:
            await get_performance_report("claude-3-sonnet", 30, mock_admin_user)

        assert exc.value.status_code == 500
        assert "Failed to generate performance report" in exc.value.detail


# ============================================================================
# TEST CLASS 11: POST /optimize Endpoint
# ============================================================================


class TestOptimizeModelSelection:
    """Test POST /optimize endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_optimize_success(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test successful model optimization"""
        mock_auth.return_value = mock_admin_user
        mock_manager.optimize_model_selection = AsyncMock(
            return_value=["claude-3-sonnet", "mistral-large"]
        )
        mock_manager.get_model = AsyncMock(side_effect=sample_models[:2])

        from app.api.ai_models import optimize_model_selection

        request = ModelOptimizationRequest(
            language="fr", use_case="translation", budget_limit=10.0
        )
        result = await optimize_model_selection(request, mock_admin_user)

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert len(content["recommendations"]) == 2
        assert "translation" in content["message"]

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_optimize_no_recommendations(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test optimization with no model recommendations"""
        mock_auth.return_value = mock_admin_user
        mock_manager.optimize_model_selection = AsyncMock(return_value=[])

        from app.api.ai_models import optimize_model_selection

        request = ModelOptimizationRequest()
        result = await optimize_model_selection(request, mock_admin_user)

        import json

        content = json.loads(result.body.decode())
        assert len(content["recommendations"]) == 0

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_optimize_service_error(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test optimize with service error"""
        mock_auth.return_value = mock_admin_user
        mock_manager.optimize_model_selection = AsyncMock(
            side_effect=Exception("Service error")
        )

        from app.api.ai_models import optimize_model_selection

        request = ModelOptimizationRequest()
        with pytest.raises(HTTPException) as exc:
            await optimize_model_selection(request, mock_admin_user)

        assert exc.value.status_code == 500
        assert "Failed to optimize model selection" in exc.value.detail


# ============================================================================
# TEST CLASS 12: GET /health Endpoint
# ============================================================================


class TestGetHealthStatus:
    """Test GET /health endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_health_status_success(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test successful health status retrieval"""
        mock_auth.return_value = mock_admin_user
        health_data = {
            "overall_status": "healthy",
            "providers": {
                "claude": {"status": "healthy", "available": True},
                "mistral": {"status": "healthy", "available": True},
            },
        }
        mock_manager.get_health_status = AsyncMock(return_value=health_data)

        from app.api.ai_models import get_health_status

        result = await get_health_status(mock_admin_user)

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert content["overall_status"] == "healthy"

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_health_status_error(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test health status with service error"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_health_status = AsyncMock(
            side_effect=Exception("Service error")
        )

        from app.api.ai_models import get_health_status

        with pytest.raises(HTTPException) as exc:
            await get_health_status(mock_admin_user)

        assert exc.value.status_code == 500
        assert "Failed to get health status" in exc.value.detail


# ============================================================================
# TEST CLASS 13: POST /health-check Endpoint
# ============================================================================


class TestRunHealthCheck:
    """Test POST /health-check endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @patch("app.api.ai_models.ai_router")
    @pytest.mark.asyncio
    async def test_run_health_check_success(
        self, mock_router, mock_manager, mock_auth, mock_admin_user
    ):
        """Test successful health check execution"""
        mock_auth.return_value = mock_admin_user
        mock_router.check_provider_health = AsyncMock(
            return_value={"status": "healthy", "available": True}
        )
        mock_manager.get_system_overview = AsyncMock(return_value={"total_models": 10})

        from app.api.ai_models import run_health_check

        result = await run_health_check(mock_admin_user)

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert "health_check_results" in content
        assert "system_overview" in content
        assert content["message"] == "Health check completed"

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @patch("app.api.ai_models.ai_router")
    @pytest.mark.asyncio
    async def test_run_health_check_provider_error(
        self, mock_router, mock_manager, mock_auth, mock_admin_user
    ):
        """Test health check with provider error"""
        mock_auth.return_value = mock_admin_user
        mock_router.check_provider_health = AsyncMock(
            side_effect=Exception("Provider unavailable")
        )
        mock_manager.get_system_overview = AsyncMock(return_value={"total_models": 10})

        from app.api.ai_models import run_health_check

        result = await run_health_check(mock_admin_user)

        import json

        content = json.loads(result.body.decode())
        # Should still return successfully, with error status for failed providers
        assert "health_check_results" in content

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @patch("app.api.ai_models.ai_router")
    @pytest.mark.asyncio
    async def test_run_health_check_service_error(
        self, mock_router, mock_manager, mock_auth, mock_admin_user
    ):
        """Test health check with service error"""
        mock_auth.return_value = mock_admin_user
        mock_router.check_provider_health = AsyncMock(
            return_value={"status": "healthy"}
        )
        mock_manager.get_system_overview = AsyncMock(
            side_effect=Exception("Service error")
        )

        from app.api.ai_models import run_health_check

        with pytest.raises(HTTPException) as exc:
            await run_health_check(mock_admin_user)

        assert exc.value.status_code == 500
        assert "Failed to run health check" in exc.value.detail


# ============================================================================
# TEST CLASS 14: GET /usage-stats Endpoint
# ============================================================================


class TestGetUsageStatistics:
    """Test GET /usage-stats endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_usage_stats_default_dates(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test usage statistics with default date range"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import get_usage_statistics

        result = await get_usage_statistics(
            start_date=None,
            end_date=None,
            provider=None,
            model_id=None,
            admin_user=mock_admin_user,
        )

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert "period" in content
        assert "summary" in content
        assert "provider_breakdown" in content

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_usage_stats_with_dates(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test usage statistics with specific date range"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import get_usage_statistics

        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)

        result = await get_usage_statistics(
            start_date=start,
            end_date=end,
            provider=None,
            model_id=None,
            admin_user=mock_admin_user,
        )

        import json

        content = json.loads(result.body.decode())
        assert content["period"]["days"] == 30

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_usage_stats_with_provider_filter(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test usage statistics filtered by provider"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import get_usage_statistics

        result = await get_usage_statistics(
            start_date=None,
            end_date=None,
            provider="claude",
            model_id=None,
            admin_user=mock_admin_user,
        )

        import json

        content = json.loads(result.body.decode())
        assert content["summary"]["total_models"] == 1

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_usage_stats_with_model_filter(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test usage statistics filtered by model_id"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import get_usage_statistics

        result = await get_usage_statistics(
            start_date=None,
            end_date=None,
            provider=None,
            model_id="claude-3-sonnet",
            admin_user=mock_admin_user,
        )

        import json

        content = json.loads(result.body.decode())
        assert content["summary"]["total_models"] == 1

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_get_usage_stats_error(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test usage statistics with service error"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(side_effect=Exception("Service error"))

        from app.api.ai_models import get_usage_statistics

        with pytest.raises(HTTPException) as exc:
            await get_usage_statistics(
                start_date=None,
                end_date=None,
                provider=None,
                model_id=None,
                admin_user=mock_admin_user,
            )

        assert exc.value.status_code == 500
        assert "Failed to get usage statistics" in exc.value.detail


# ============================================================================
# TEST CLASS 15: POST /reset-stats Endpoint
# ============================================================================


class TestResetUsageStatistics:
    """Test POST /reset-stats endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_reset_stats_without_confirmation(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test reset stats without confirmation flag"""
        mock_auth.return_value = mock_admin_user

        from app.api.ai_models import reset_usage_statistics

        with pytest.raises(HTTPException) as exc:
            await reset_usage_statistics(
                model_id=None, confirm=False, admin_user=mock_admin_user
            )

        assert exc.value.status_code == 400
        assert "Confirmation required" in exc.value.detail

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_reset_stats_specific_model(
        self, mock_manager, mock_auth, mock_admin_user, sample_model
    ):
        """Test resetting stats for specific model"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(return_value=sample_model)

        from app.api.ai_models import reset_usage_statistics

        result = await reset_usage_statistics(
            model_id="claude-3-sonnet", confirm=True, admin_user=mock_admin_user
        )

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert "claude-3-sonnet" in content["message"]

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_reset_stats_all_models(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test resetting stats for all models"""
        mock_auth.return_value = mock_admin_user

        from app.api.ai_models import reset_usage_statistics

        result = await reset_usage_statistics(
            model_id=None, confirm=True, admin_user=mock_admin_user
        )

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert "all models" in content["message"]

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_reset_stats_model_not_found(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test resetting stats for non-existent model"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(return_value=None)

        from app.api.ai_models import reset_usage_statistics

        with pytest.raises(HTTPException) as exc:
            await reset_usage_statistics(
                model_id="nonexistent", confirm=True, admin_user=mock_admin_user
            )

        assert exc.value.status_code == 404
        assert "Model not found" in exc.value.detail

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_reset_stats_service_error(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test reset stats with service error"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_model = AsyncMock(side_effect=Exception("Service error"))

        from app.api.ai_models import reset_usage_statistics

        with pytest.raises(HTTPException) as exc:
            await reset_usage_statistics(
                model_id="claude-3-sonnet", confirm=True, admin_user=mock_admin_user
            )

        assert exc.value.status_code == 500
        assert "Failed to reset statistics" in exc.value.detail


# ============================================================================
# TEST CLASS 16: GET /export Endpoint
# ============================================================================


class TestExportModelData:
    """Test GET /export endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_export_json_with_stats(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test JSON export with usage statistics"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import export_model_data

        result = await export_model_data(
            format="json", include_stats=True, admin_user=mock_admin_user
        )

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert "export_timestamp" in content
        assert "models" in content
        assert len(content["models"]) == 3
        assert "usage_stats" in content["models"][0]

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_export_json_without_stats(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test JSON export without usage statistics"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import export_model_data

        result = await export_model_data(
            format="json", include_stats=False, admin_user=mock_admin_user
        )

        import json

        content = json.loads(result.body.decode())
        assert "usage_stats" not in content["models"][0]

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_export_csv_format(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test CSV export format"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import export_model_data

        result = await export_model_data(
            format="csv", include_stats=True, admin_user=mock_admin_user
        )

        assert result.status_code == 200
        assert result.media_type == "text/csv"
        # Check CSV header
        csv_content = result.body.decode()
        assert "id,provider,model_name" in csv_content

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_export_service_error(self, mock_manager, mock_auth, mock_admin_user):
        """Test export with service error"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(side_effect=Exception("Service error"))

        from app.api.ai_models import export_model_data

        with pytest.raises(HTTPException) as exc:
            await export_model_data(
                format="json", include_stats=True, admin_user=mock_admin_user
            )

        assert exc.value.status_code == 500
        assert "Failed to export model data" in exc.value.detail


# ============================================================================
# TEST CLASS 17: GET /categories Endpoint
# ============================================================================


class TestGetModelCategories:
    """Test GET /categories endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @pytest.mark.asyncio
    async def test_get_categories_success(self, mock_auth, mock_admin_user):
        """Test successful categories retrieval"""
        mock_auth.return_value = mock_admin_user

        from app.api.ai_models import get_model_categories

        result = await get_model_categories(mock_admin_user)

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert "categories" in content
        assert len(content["categories"]) > 0
        # Check structure of category objects
        assert "value" in content["categories"][0]
        assert "label" in content["categories"][0]
        assert "description" in content["categories"][0]

    @patch("app.api.ai_models.require_admin_access")
    @pytest.mark.asyncio
    async def test_get_categories_error(self, mock_auth, mock_admin_user):
        """Test categories with error - patch ModelCategory to raise exception"""
        mock_auth.return_value = mock_admin_user

        # Mock ModelCategory to raise an exception during iteration
        with patch("app.api.ai_models.ModelCategory") as mock_category:
            # Make it raise when trying to iterate
            mock_category.__iter__ = MagicMock(side_effect=Exception("Enum error"))

            from app.api.ai_models import get_model_categories

            with pytest.raises(HTTPException) as exc:
                await get_model_categories(mock_admin_user)

            assert exc.value.status_code == 500
            assert "Failed to get categories" in exc.value.detail


# ============================================================================
# TEST CLASS 18: GET /providers Endpoint
# ============================================================================


class TestGetProviders:
    """Test GET /providers endpoint"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @patch("app.api.ai_models.ai_router")
    @pytest.mark.asyncio
    async def test_get_providers_success(
        self, mock_router, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test successful providers retrieval"""
        mock_auth.return_value = mock_admin_user
        mock_router.check_provider_health = AsyncMock(
            return_value={"status": "healthy", "available": True}
        )
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import get_providers

        result = await get_providers(mock_admin_user)

        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert "providers" in content
        assert len(content["providers"]) == 4  # claude, mistral, deepseek, ollama

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @patch("app.api.ai_models.ai_router")
    @pytest.mark.asyncio
    async def test_get_providers_with_counts(
        self, mock_router, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test providers includes model counts"""
        mock_auth.return_value = mock_admin_user
        mock_router.check_provider_health = AsyncMock(
            return_value={"status": "healthy", "available": True}
        )
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import get_providers

        result = await get_providers(mock_admin_user)

        import json

        content = json.loads(result.body.decode())
        # Find claude provider
        claude_provider = next(p for p in content["providers"] if p["name"] == "claude")
        assert claude_provider["models_count"] == 1
        assert claude_provider["active_models"] == 1

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @patch("app.api.ai_models.ai_router")
    @pytest.mark.asyncio
    async def test_get_providers_service_error(
        self, mock_router, mock_manager, mock_auth, mock_admin_user
    ):
        """Test providers with service error"""
        mock_auth.return_value = mock_admin_user
        mock_router.check_provider_health = AsyncMock(
            side_effect=Exception("Service error")
        )

        from app.api.ai_models import get_providers

        with pytest.raises(HTTPException) as exc:
            await get_providers(mock_admin_user)

        assert exc.value.status_code == 500
        assert "Failed to get providers" in exc.value.detail


# ============================================================================
# TEST CLASS 19: Edge Cases for Missing Branch Coverage
# ============================================================================


class TestMissingBranchCoverage:
    """Test edge cases to achieve 100% branch coverage"""

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_optimize_model_not_found(
        self, mock_manager, mock_auth, mock_admin_user
    ):
        """Test optimize when recommended model is not found (line 414 branch)"""
        mock_auth.return_value = mock_admin_user
        # Return model IDs where one doesn't exist
        mock_manager.optimize_model_selection = AsyncMock(
            return_value=["claude-3-sonnet", "nonexistent-model"]
        )
        # First call returns model, second returns None
        mock_manager.get_model = AsyncMock(
            side_effect=[
                {"id": "claude-3-sonnet", "name": "Claude"},
                None,  # This model doesn't exist
            ]
        )

        from app.api.ai_models import optimize_model_selection

        request = ModelOptimizationRequest()
        result = await optimize_model_selection(request, mock_admin_user)

        import json

        content = json.loads(result.body.decode())
        # Should only include the found model
        assert len(content["recommendations"]) == 1
        assert content["recommendations"][0]["id"] == "claude-3-sonnet"

    def test_calculate_provider_breakdown_existing_provider(self, sample_models):
        """Test provider breakdown when provider already exists in stats (line 567 branch)"""
        # Create models with same provider to test the "already exists" branch
        models_same_provider = [
            {
                "provider": "claude",
                "usage_stats": {
                    "total_requests": 100,
                    "total_cost": 1.0,
                    "success_rate": 0.95,
                },
            },
            {
                "provider": "claude",  # Same provider again
                "usage_stats": {
                    "total_requests": 50,
                    "total_cost": 0.5,
                    "success_rate": 0.90,
                },
            },
        ]

        from app.api.ai_models import _calculate_provider_breakdown

        result = _calculate_provider_breakdown(models_same_provider)

        # Should aggregate both models under same provider
        assert result["claude"]["models"] == 2
        assert result["claude"]["total_requests"] == 150
        assert result["claude"]["total_cost"] == 1.5

    def test_calculate_provider_breakdown_zero_models(self):
        """Test provider breakdown with zero models to test division edge case (line 587 branch)"""
        # This tests the "if stats['models'] > 0" branch
        from app.api.ai_models import _calculate_provider_breakdown

        result = _calculate_provider_breakdown([])

        # Empty input should return empty stats
        assert result == {}

    def test_calculate_provider_breakdown_multiple_providers(self):
        """Test provider breakdown with multiple providers to test loop branches"""
        # Create models from different providers to test loop iterations
        models = [
            {
                "provider": "claude",
                "usage_stats": {
                    "total_requests": 100,
                    "total_cost": 1.0,
                    "success_rate": 0.95,
                },
            },
            {
                "provider": "mistral",
                "usage_stats": {
                    "total_requests": 50,
                    "total_cost": 0.5,
                    "success_rate": 0.90,
                },
            },
            {
                "provider": "deepseek",
                "usage_stats": {
                    "total_requests": 25,
                    "total_cost": 0.25,
                    "success_rate": 0.85,
                },
            },
        ]

        from app.api.ai_models import _calculate_provider_breakdown

        result = _calculate_provider_breakdown(models)

        # All three providers should be present
        assert "claude" in result
        assert "mistral" in result
        assert "deepseek" in result

        # Each should have correct averages
        assert result["claude"]["avg_success_rate"] == 0.95
        assert result["mistral"]["avg_success_rate"] == 0.90
        assert result["deepseek"]["avg_success_rate"] == 0.85

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_export_csv_complete_flow(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test complete CSV export flow to ensure branch coverage (line 702)"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import export_model_data

        # Test CSV format explicitly
        result = await export_model_data(
            format="csv", include_stats=False, admin_user=mock_admin_user
        )

        assert result.status_code == 200
        assert result.media_type == "text/csv"

        # Verify CSV content
        csv_content = result.body.decode()
        lines = csv_content.split("\n")

        # Should have header + 3 data rows
        assert len(lines) >= 4
        assert "id,provider,model_name" in lines[0]

        # Check that data rows are present
        assert "claude-3-sonnet" in csv_content
        assert "mistral-large" in csv_content
        assert "deepseek-coder" in csv_content

    @patch("app.api.ai_models.require_admin_access")
    @patch("app.api.ai_models.ai_model_manager")
    @pytest.mark.asyncio
    async def test_export_invalid_format_fallback(
        self, mock_manager, mock_auth, mock_admin_user, sample_models
    ):
        """Test export with invalid format falls back to JSON (else clause)"""
        mock_auth.return_value = mock_admin_user
        mock_manager.get_all_models = AsyncMock(return_value=sample_models)

        from app.api.ai_models import export_model_data

        # Call the function directly with an invalid format to test else clause
        # This bypasses FastAPI's Query validation
        result = await export_model_data(
            format="invalid", include_stats=True, admin_user=mock_admin_user
        )

        # Should fall back to JSON
        assert result.status_code == 200
        import json

        content = json.loads(result.body.decode())
        assert "models" in content
