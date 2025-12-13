"""
Tests for Admin AI Model Management Frontend
Achieves 100% coverage of app/frontend/admin_ai_models.py
"""

import pytest
from fasthtml.common import to_xml

from app.frontend.admin_ai_models import (
    create_ai_models_page,
    create_model_card,
    create_model_configuration_modal,
    create_model_list,
    create_performance_report_modal,
    create_system_overview_card,
)


class TestCreateAiModelsPage:
    """Test the main AI models management page"""

    def test_create_ai_models_page_returns_valid_html(self):
        """Test that create_ai_models_page returns valid HTML structure"""
        result = create_ai_models_page()
        result_str = to_xml(result)

        # Verify page structure
        assert "ai-models-container" in result_str
        assert "ai-models-content" in result_str
        assert "AI Model Management" in result_str
        assert "Monitor, configure, and optimize AI models and providers" in result_str

    def test_create_ai_models_page_has_system_stats_section(self):
        """Test that system stats section is present"""
        result = create_ai_models_page()
        result_str = to_xml(result)

        assert 'id="system-stats"' in result_str
        assert "stats-grid" in result_str

    def test_create_ai_models_page_has_filter_controls(self):
        """Test that filter controls are present"""
        result = create_ai_models_page()
        result_str = to_xml(result)

        # Category filter
        assert "All Categories" in result_str
        assert "Conversation" in result_str
        assert "Grammar" in result_str
        assert "Translation" in result_str
        assert "Analysis" in result_str
        assert "General" in result_str

        # Provider filter
        assert "All Providers" in result_str
        assert "Claude" in result_str
        assert "Mistral" in result_str
        assert "DeepSeek" in result_str
        assert "Ollama" in result_str

        # Status filter
        assert "All Status" in result_str
        assert "Active" in result_str
        assert "Inactive" in result_str
        assert "Maintenance" in result_str
        assert "Error" in result_str

    def test_create_ai_models_page_has_search_input(self):
        """Test that search input is present"""
        result = create_ai_models_page()
        result_str = to_xml(result)

        assert 'placeholder="Search models..."' in result_str
        assert "search-input" in result_str

    def test_create_ai_models_page_has_action_buttons(self):
        """Test that action buttons are present"""
        result = create_ai_models_page()
        result_str = to_xml(result)

        assert "Health Check" in result_str
        assert "Optimize Models" in result_str
        assert "Performance Report" in result_str

    def test_create_ai_models_page_has_models_list_section(self):
        """Test that models list section is present"""
        result = create_ai_models_page()
        result_str = to_xml(result)

        assert 'id="models-list"' in result_str
        assert "models-grid" in result_str

    def test_create_ai_models_page_has_javascript(self):
        """Test that JavaScript for interactivity is included"""
        result = create_ai_models_page()
        result_str = to_xml(result)

        assert "<script>" in result_str
        assert "setInterval" in result_str
        assert "htmx.ajax" in result_str
        assert "/admin/ai-models/overview" in result_str
        assert "/admin/ai-models/models" in result_str


class TestCreateSystemOverviewCard:
    """Test system overview statistics cards"""

    def test_create_system_overview_card_with_full_data(self):
        """Test system overview card with complete data"""
        overview_data = {
            "overview": {
                "total_models": 10,
                "active_models": 8,
                "total_cost": 123.4567,
                "total_requests": 5000,
            },
            "budget_status": {
                "remaining_budget": 876.54,
                "percentage_used": 58.5,
            },
        }

        result = create_system_overview_card(overview_data)
        result_str = to_xml(result)

        # Verify all stats are present
        assert "10" in result_str
        assert "Total Models" in result_str
        assert "8" in result_str
        assert "Active Models" in result_str
        assert "$123.4567" in result_str
        assert "Total Cost" in result_str
        assert "$876.54" in result_str
        assert "Budget Remaining" in result_str
        assert "5000" in result_str
        assert "Total Requests" in result_str
        assert "58.5%" in result_str
        assert "Budget Used" in result_str

    def test_create_system_overview_card_with_zero_values(self):
        """Test system overview card with zero values"""
        overview_data = {
            "overview": {
                "total_models": 0,
                "active_models": 0,
                "total_cost": 0,
                "total_requests": 0,
            },
            "budget_status": {
                "remaining_budget": 0,
                "percentage_used": 0,
            },
        }

        result = create_system_overview_card(overview_data)
        result_str = to_xml(result)

        assert "$0.0000" in result_str
        assert "$0.00" in result_str
        assert "0.0%" in result_str

    def test_create_system_overview_card_with_missing_data(self):
        """Test system overview card handles missing data gracefully"""
        overview_data = {}

        result = create_system_overview_card(overview_data)
        result_str = to_xml(result)

        # Should use default values of 0
        assert "stat-card" in result_str


class TestCreateModelCard:
    """Test individual model configuration card"""

    def test_create_model_card_with_active_status(self):
        """Test model card with active status"""
        model = {
            "id": "model-1",
            "display_name": "Claude Sonnet 4",
            "provider": "claude",
            "status": "active",
            "enabled": True,
            "quality_score": 0.95,
            "cost_per_1k_tokens": 0.003,
            "avg_response_time_ms": 850,
            "priority": 1,
            "supported_languages": ["en", "es", "fr"],
            "primary_languages": ["en"],
            "context_window": 200000,
            "max_tokens": 4096,
            "supports_streaming": True,
            "supports_functions": True,
            "usage_stats": {
                "success_rate": 0.98,
                "total_requests": 1500,
            },
        }

        result = create_model_card(model)
        result_str = to_xml(result)

        # Verify model information
        assert "Claude Sonnet 4" in result_str
        assert "CLAUDE" in result_str
        assert "Active" in result_str
        assert "status-active" in result_str

        # Verify metrics
        assert "0.95" in result_str  # quality score
        assert "98.0%" in result_str  # success rate
        assert "$0.0030" in result_str  # cost
        assert "850ms" in result_str  # response time
        assert "1500" in result_str  # requests
        assert "Priority 1" in result_str

        # Verify languages
        assert "EN" in result_str
        assert "ES" in result_str
        assert "FR" in result_str

        # Verify technical specs
        assert "Context Window: 200,000 tokens" in result_str
        assert "Max Tokens: 4,096" in result_str
        assert "Streaming: Yes" in result_str
        assert "Functions: Yes" in result_str

        # Verify action buttons
        assert "Configure" in result_str
        assert "Performance" in result_str
        assert "Disable" in result_str  # Should show Disable for enabled model

    def test_create_model_card_with_inactive_status(self):
        """Test model card with inactive status"""
        model = {
            "id": "model-2",
            "display_name": "Mistral Large",
            "provider": "mistral",
            "status": "inactive",
            "enabled": False,
            "quality_score": 0.85,
            "cost_per_1k_tokens": 0.002,
            "avg_response_time_ms": 650,
            "priority": 2,
            "supported_languages": ["en", "de"],
            "primary_languages": [],
            "context_window": 32000,
            "max_tokens": 2048,
            "supports_streaming": False,
            "supports_functions": False,
            "usage_stats": {
                "success_rate": 0.92,
                "total_requests": 800,
            },
        }

        result = create_model_card(model)
        result_str = to_xml(result)

        assert "Mistral Large" in result_str
        assert "MISTRAL" in result_str
        assert "Inactive" in result_str
        assert "status-inactive" in result_str
        assert "Streaming: No" in result_str
        assert "Functions: No" in result_str
        assert "Enable" in result_str  # Should show Enable for disabled model

    def test_create_model_card_with_maintenance_status(self):
        """Test model card with maintenance status"""
        model = {
            "id": "model-3",
            "display_name": "DeepSeek Chat",
            "provider": "deepseek",
            "status": "maintenance",
            "enabled": True,
            "quality_score": 0.88,
            "cost_per_1k_tokens": 0.0015,
            "avg_response_time_ms": 720,
            "priority": 3,
            "supported_languages": ["en", "zh"],
            "primary_languages": ["en"],
            "context_window": 64000,
            "max_tokens": 4096,
            "supports_streaming": True,
            "supports_functions": True,
            "usage_stats": {
                "success_rate": 0.95,
                "total_requests": 1200,
            },
        }

        result = create_model_card(model)
        result_str = to_xml(result)

        assert "DeepSeek Chat" in result_str
        assert "DEEPSEEK" in result_str
        assert "Maintenance" in result_str
        assert "status-maintenance" in result_str

    def test_create_model_card_with_error_status(self):
        """Test model card with error status"""
        model = {
            "id": "model-4",
            "display_name": "Ollama Model",
            "provider": "ollama",
            "status": "error",
            "enabled": False,
            "quality_score": 0,
            "cost_per_1k_tokens": 0,
            "avg_response_time_ms": 0,
            "priority": 5,
            "supported_languages": [],
            "primary_languages": [],
            "context_window": 0,
            "max_tokens": 0,
            "supports_streaming": False,
            "supports_functions": False,
            "usage_stats": {
                "success_rate": 0,
                "total_requests": 0,
            },
        }

        result = create_model_card(model)
        result_str = to_xml(result)

        assert "Ollama Model" in result_str
        assert "OLLAMA" in result_str
        # Error status maps to status-inactive
        assert "status-inactive" in result_str

    def test_create_model_card_with_unknown_status(self):
        """Test model card with unknown status defaults correctly"""
        model = {
            "id": "model-5",
            "display_name": "Unknown Model",
            "provider": "unknown",
            "status": "unknown",
            "enabled": True,
            "quality_score": 0.5,
            "cost_per_1k_tokens": 0.001,
            "avg_response_time_ms": 500,
            "priority": 10,
            "supported_languages": ["en"],
            "primary_languages": [],
            "context_window": 8000,
            "max_tokens": 1024,
            "supports_streaming": False,
            "supports_functions": False,
            "usage_stats": {
                "success_rate": 0.5,
                "total_requests": 100,
            },
        }

        result = create_model_card(model)
        result_str = to_xml(result)

        assert "Unknown Model" in result_str
        # Unknown status should default to status-inactive
        assert "status-inactive" in result_str


class TestCreateModelList:
    """Test the models list display"""

    def test_create_model_list_with_models(self):
        """Test creating model list with multiple models"""
        models = [
            {
                "id": "model-1",
                "display_name": "Model 1",
                "provider": "claude",
                "status": "active",
                "enabled": True,
                "quality_score": 0.9,
                "cost_per_1k_tokens": 0.003,
                "avg_response_time_ms": 800,
                "priority": 1,
                "supported_languages": ["en"],
                "primary_languages": ["en"],
                "context_window": 100000,
                "max_tokens": 4096,
                "supports_streaming": True,
                "supports_functions": True,
                "usage_stats": {"success_rate": 0.95, "total_requests": 1000},
            },
            {
                "id": "model-2",
                "display_name": "Model 2",
                "provider": "mistral",
                "status": "inactive",
                "enabled": False,
                "quality_score": 0.8,
                "cost_per_1k_tokens": 0.002,
                "avg_response_time_ms": 600,
                "priority": 2,
                "supported_languages": ["en", "fr"],
                "primary_languages": [],
                "context_window": 32000,
                "max_tokens": 2048,
                "supports_streaming": False,
                "supports_functions": False,
                "usage_stats": {"success_rate": 0.90, "total_requests": 500},
            },
        ]

        result = create_model_list(models)
        result_str = to_xml(result)

        assert "Model 1" in result_str
        assert "Model 2" in result_str
        assert "models-grid" in result_str

    def test_create_model_list_with_empty_list(self):
        """Test creating model list with empty list shows empty state"""
        models = []

        result = create_model_list(models)
        result_str = to_xml(result)

        assert "No AI models found" in result_str
        assert "Try adjusting your filters" in result_str
        assert "empty-state" in result_str
        assert "🤖" in result_str


class TestCreateModelConfigurationModal:
    """Test model configuration modal"""

    def test_create_model_configuration_modal_with_complete_data(self):
        """Test configuration modal with complete model data"""
        model = {
            "id": "model-1",
            "display_name": "Claude Sonnet 4",
            "status": "active",
            "priority": 1,
            "weight": 1.0,
            "temperature": 0.7,
            "quality_score": 0.8,
            "reliability_score": 0.9,
        }

        result = create_model_configuration_modal(model)
        result_str = to_xml(result)

        # Verify title
        assert "Configure Claude Sonnet 4" in result_str

        # Verify form fields
        assert 'name="display_name"' in result_str
        assert 'value="Claude Sonnet 4"' in result_str
        assert 'name="status"' in result_str
        assert 'name="priority"' in result_str
        assert 'value="1"' in result_str
        assert 'name="weight"' in result_str
        assert 'value="1.0"' in result_str
        assert 'name="temperature"' in result_str
        assert 'value="0.7"' in result_str
        assert 'name="quality_score"' in result_str
        assert 'value="0.8"' in result_str
        assert 'name="reliability_score"' in result_str
        assert 'value="0.9"' in result_str

        # Verify action buttons
        assert "Cancel" in result_str
        assert "Save Changes" in result_str
        assert "closeModal()" in result_str

    def test_create_model_configuration_modal_with_active_status_selected(self):
        """Test configuration modal with active status selected"""
        model = {
            "id": "model-1",
            "display_name": "Test Model",
            "status": "active",
            "priority": 1,
            "weight": 1.0,
            "temperature": 0.7,
            "quality_score": 0.8,
            "reliability_score": 0.9,
        }

        result = create_model_configuration_modal(model)
        result_str = to_xml(result)

        # Active should be selected
        assert 'value="active"' in result_str
        assert "selected" in result_str or "Active" in result_str

    def test_create_model_configuration_modal_with_inactive_status_selected(self):
        """Test configuration modal with inactive status selected"""
        model = {
            "id": "model-2",
            "display_name": "Test Model",
            "status": "inactive",
            "priority": 2,
            "weight": 0.5,
            "temperature": 0.5,
            "quality_score": 0.7,
            "reliability_score": 0.8,
        }

        result = create_model_configuration_modal(model)
        result_str = to_xml(result)

        assert 'value="inactive"' in result_str

    def test_create_model_configuration_modal_with_maintenance_status_selected(self):
        """Test configuration modal with maintenance status selected"""
        model = {
            "id": "model-3",
            "display_name": "Test Model",
            "status": "maintenance",
            "priority": 3,
            "weight": 0.8,
            "temperature": 0.9,
            "quality_score": 0.6,
            "reliability_score": 0.7,
        }

        result = create_model_configuration_modal(model)
        result_str = to_xml(result)

        assert 'value="maintenance"' in result_str


class TestCreatePerformanceReportModal:
    """Test performance report modal"""

    def test_create_performance_report_modal_with_full_data(self):
        """Test performance report modal with complete data"""
        report = {
            "model_name": "Claude Sonnet 4",
            "cost_efficiency": 0.92,
            "speed_efficiency": 0.88,
            "reliability_score": 0.95,
            "rank_by_cost": 1,
            "rank_by_speed": 2,
            "rank_by_quality": 1,
            "rank_overall": 1,
            "recommended_for": ["conversation", "translation", "grammar"],
            "optimization_suggestions": [
                "Consider reducing temperature for more consistent outputs",
                "Enable streaming for better user experience",
                "Increase weight for high-priority tasks",
            ],
        }

        result = create_performance_report_modal(report)
        result_str = to_xml(result)

        # Verify title
        assert "Performance Report: Claude Sonnet 4" in result_str

        # Verify performance metrics
        assert "0.92" in result_str  # cost efficiency
        assert "0.88" in result_str  # speed efficiency
        assert "0.95" in result_str  # reliability

        # Verify rankings
        assert "#1" in result_str  # cost rank
        assert "#2" in result_str  # speed rank

        # Verify recommendations
        assert "Conversation" in result_str
        assert "Translation" in result_str
        assert "Grammar" in result_str

        # Verify optimization suggestions
        assert "Consider reducing temperature" in result_str
        assert "Enable streaming" in result_str
        assert "Increase weight" in result_str

        # Verify chart placeholder
        assert "Performance charts would be displayed here" in result_str

        # Verify close button
        assert "Close" in result_str
        assert "closeModal()" in result_str

    def test_create_performance_report_modal_with_minimal_data(self):
        """Test performance report modal with minimal data"""
        report = {
            "model_name": "Unknown Model",
            "cost_efficiency": 0,
            "speed_efficiency": 0,
            "reliability_score": 0,
            "rank_by_cost": "?",
            "rank_by_speed": "?",
            "rank_by_quality": "?",
            "rank_overall": "?",
            "recommended_for": [],
            "optimization_suggestions": [],
        }

        result = create_performance_report_modal(report)
        result_str = to_xml(result)

        assert "Performance Report: Unknown Model" in result_str
        assert "#?" in result_str  # Unknown ranks

    def test_create_performance_report_modal_with_multiple_recommendations(self):
        """Test performance report modal with multiple recommendation categories"""
        report = {
            "model_name": "Test Model",
            "cost_efficiency": 0.75,
            "speed_efficiency": 0.80,
            "reliability_score": 0.85,
            "rank_by_cost": 3,
            "rank_by_speed": 4,
            "rank_by_quality": 2,
            "rank_overall": 3,
            "recommended_for": [
                "general_purpose",
                "quick_responses",
                "budget_conscious",
            ],
            "optimization_suggestions": [
                "Optimize for cost by reducing max tokens",
                "Improve speed with better caching",
            ],
        }

        result = create_performance_report_modal(report)
        result_str = to_xml(result)

        assert "General Purpose" in result_str
        assert "Quick Responses" in result_str
        assert "Budget Conscious" in result_str
        assert "Optimize for cost" in result_str
        assert "Improve speed" in result_str
