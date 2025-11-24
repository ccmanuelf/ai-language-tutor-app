"""
Comprehensive tests for AI Model Manager Service
Tests for model configuration, usage tracking, performance analytics, and optimization
"""

import json
import shutil
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.services.ai_model_manager import (
    AIModelManager,
    ModelCategory,
    ModelConfiguration,
    ModelPerformanceReport,
    ModelSize,
    ModelStatus,
    ModelUsageStats,
    ai_model_manager,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def temp_db_dir():
    """Create temporary directory for test database"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    settings = Mock()
    settings.DATABASE_PATH = "./data/test.db"
    return settings


@pytest.fixture
def model_manager(temp_db_dir, mock_settings):
    """Create fresh AIModelManager instance for testing"""
    with patch(
        "app.services.ai_model_manager.get_settings", return_value=mock_settings
    ):
        manager = AIModelManager()
        manager.db_path = f"{temp_db_dir}/test_ai_models.db"
        manager._initialize_database()
        manager.models = {}
        manager.usage_stats = {}
        manager.performance_cache = {}
        yield manager


@pytest.fixture
def sample_model_config():
    """Sample model configuration for testing"""
    return ModelConfiguration(
        provider="test_provider",
        model_name="test-model-v1",
        display_name="Test Model V1",
        category=ModelCategory.CONVERSATION,
        size=ModelSize.MEDIUM,
        status=ModelStatus.ACTIVE,
        cost_per_1k_tokens=0.01,
        avg_response_time_ms=1000,
        quality_score=0.85,
        reliability_score=0.90,
        supported_languages=["en", "es", "fr"],
        primary_languages=["en"],
        max_tokens=2048,
        context_window=8192,
        supports_streaming=True,
        supports_functions=True,
        temperature=0.7,
        top_p=0.9,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        enabled=True,
        priority=1,
        weight=1.0,
    )


@pytest.fixture
def sample_usage_stats():
    """Sample usage statistics for testing"""
    return ModelUsageStats(
        model_id="test_provider_test-model-v1",
        provider="test_provider",
        model_name="test-model-v1",
        total_requests=100,
        successful_requests=95,
        failed_requests=5,
        total_tokens=50000,
        total_cost=5.0,
        avg_response_time=1200.0,
        min_response_time=800.0,
        max_response_time=2000.0,
        avg_quality_rating=0.85,
        user_satisfaction=0.9,
        last_24h_requests=10,
        last_7d_requests=50,
        last_30d_requests=100,
        first_used=datetime.now() - timedelta(days=30),
        last_used=datetime.now(),
    )


# ============================================================================
# ENUM TESTS
# ============================================================================


class TestEnums:
    """Test enum definitions"""

    def test_model_status_values(self):
        """Test ModelStatus enum values"""
        assert ModelStatus.ACTIVE.value == "active"
        assert ModelStatus.INACTIVE.value == "inactive"
        assert ModelStatus.DEPRECATED.value == "deprecated"
        assert ModelStatus.MAINTENANCE.value == "maintenance"
        assert ModelStatus.ERROR.value == "error"

    def test_model_category_values(self):
        """Test ModelCategory enum values"""
        assert ModelCategory.CONVERSATION.value == "conversation"
        assert ModelCategory.GRAMMAR.value == "grammar"
        assert ModelCategory.TRANSLATION.value == "translation"
        assert ModelCategory.PRONUNCIATION.value == "pronunciation"
        assert ModelCategory.ANALYSIS.value == "analysis"
        assert ModelCategory.GENERAL.value == "general"

    def test_model_size_values(self):
        """Test ModelSize enum values"""
        assert ModelSize.SMALL.value == "small"
        assert ModelSize.MEDIUM.value == "medium"
        assert ModelSize.LARGE.value == "large"
        assert ModelSize.EXTRA_LARGE.value == "extra_large"


# ============================================================================
# DATACLASS TESTS
# ============================================================================


class TestModelConfiguration:
    """Test ModelConfiguration dataclass"""

    def test_model_configuration_creation(self, sample_model_config):
        """Test creating model configuration"""
        assert sample_model_config.provider == "test_provider"
        assert sample_model_config.model_name == "test-model-v1"
        assert sample_model_config.category == ModelCategory.CONVERSATION
        assert sample_model_config.enabled is True

    def test_model_configuration_post_init_timestamps(self):
        """Test __post_init__ creates timestamps"""
        config = ModelConfiguration(
            provider="test",
            model_name="test",
            display_name="Test",
            category=ModelCategory.GENERAL,
            size=ModelSize.SMALL,
            status=ModelStatus.ACTIVE,
            cost_per_1k_tokens=0.01,
            avg_response_time_ms=1000,
            quality_score=0.8,
            reliability_score=0.9,
            supported_languages=["en"],
            primary_languages=["en"],
            max_tokens=2048,
            context_window=4096,
            supports_streaming=False,
            supports_functions=False,
        )
        assert config.created_at is not None
        assert config.updated_at is not None
        assert isinstance(config.created_at, datetime)
        assert isinstance(config.updated_at, datetime)

    def test_model_configuration_with_explicit_timestamps(self):
        """Test model configuration with explicit timestamps"""
        now = datetime.now()
        config = ModelConfiguration(
            provider="test",
            model_name="test",
            display_name="Test",
            category=ModelCategory.GENERAL,
            size=ModelSize.SMALL,
            status=ModelStatus.ACTIVE,
            cost_per_1k_tokens=0.01,
            avg_response_time_ms=1000,
            quality_score=0.8,
            reliability_score=0.9,
            supported_languages=["en"],
            primary_languages=["en"],
            max_tokens=2048,
            context_window=4096,
            supports_streaming=False,
            supports_functions=False,
            created_at=now,
            updated_at=now,
        )
        assert config.created_at == now
        assert config.updated_at == now


class TestModelUsageStats:
    """Test ModelUsageStats dataclass"""

    def test_usage_stats_creation(self, sample_usage_stats):
        """Test creating usage statistics"""
        assert sample_usage_stats.model_id == "test_provider_test-model-v1"
        assert sample_usage_stats.total_requests == 100
        assert sample_usage_stats.successful_requests == 95
        assert sample_usage_stats.failed_requests == 5

    def test_usage_stats_defaults(self):
        """Test usage statistics with default values"""
        stats = ModelUsageStats(
            model_id="test_id",
            provider="test",
            model_name="test",
        )
        assert stats.total_requests == 0
        assert stats.successful_requests == 0
        assert stats.total_cost == 0.0
        assert stats.avg_response_time == 0.0


class TestModelPerformanceReport:
    """Test ModelPerformanceReport dataclass"""

    def test_performance_report_creation(self):
        """Test creating performance report"""
        report = ModelPerformanceReport(
            model_id="test_id",
            report_date=datetime.now(),
            cost_efficiency=100.0,
            speed_efficiency=50.0,
            reliability_score=0.95,
            rank_by_cost=1,
            rank_by_speed=2,
            rank_by_quality=1,
            rank_overall=1,
            recommended_for=["conversation", "high_volume"],
            optimization_suggestions=["Great for cost-sensitive workloads"],
            performance_trend="improving",
            usage_trend="stable",
        )
        assert report.model_id == "test_id"
        assert report.cost_efficiency == 100.0
        assert len(report.recommended_for) == 2
        assert report.performance_trend == "improving"


# ============================================================================
# DATABASE INITIALIZATION TESTS
# ============================================================================


class TestDatabaseInitialization:
    """Test database initialization"""

    def test_initialize_database_creates_tables(self, model_manager):
        """Test database initialization creates all required tables"""
        with sqlite3.connect(model_manager.db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}

        assert "model_configurations" in tables
        assert "model_usage_stats" in tables
        assert "model_performance_logs" in tables

    def test_initialize_database_creates_indexes(self, model_manager):
        """Test database initialization creates indexes"""
        with sqlite3.connect(model_manager.db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = {row[0] for row in cursor.fetchall()}

        assert "idx_performance_logs_model_timestamp" in indexes
        assert "idx_performance_logs_language" in indexes

    def test_initialize_database_model_configurations_schema(self, model_manager):
        """Test model_configurations table has correct schema"""
        with sqlite3.connect(model_manager.db_path) as conn:
            cursor = conn.execute("PRAGMA table_info(model_configurations)")
            columns = {row[1] for row in cursor.fetchall()}

        required_columns = {
            "model_id",
            "provider",
            "model_name",
            "display_name",
            "category",
            "size",
            "status",
            "cost_per_1k_tokens",
            "enabled",
            "priority",
            "weight",
            "created_at",
            "updated_at",
        }
        assert required_columns.issubset(columns)

    def test_initialize_database_model_usage_stats_schema(self, model_manager):
        """Test model_usage_stats table has correct schema"""
        with sqlite3.connect(model_manager.db_path) as conn:
            cursor = conn.execute("PRAGMA table_info(model_usage_stats)")
            columns = {row[1] for row in cursor.fetchall()}

        required_columns = {
            "model_id",
            "provider",
            "model_name",
            "total_requests",
            "successful_requests",
            "failed_requests",
            "total_tokens",
            "total_cost",
            "avg_response_time",
        }
        assert required_columns.issubset(columns)


# ============================================================================
# DEFAULT MODELS LOADING TESTS
# ============================================================================


class TestDefaultModelsLoading:
    """Test loading default model configurations"""

    def test_load_default_models_creates_models(self, model_manager):
        """Test loading default models creates model configurations"""
        model_manager._load_default_models()

        assert len(model_manager.models) > 0
        assert "claude_claude-3-haiku-20240307" in model_manager.models

    def test_load_default_models_creates_usage_stats(self, model_manager):
        """Test loading default models creates usage statistics"""
        model_manager._load_default_models()

        assert len(model_manager.usage_stats) > 0
        for model_id in model_manager.models:
            assert model_id in model_manager.usage_stats

    def test_load_default_models_saves_to_database(self, model_manager):
        """Test loading default models saves to database"""
        model_manager._load_default_models()

        with sqlite3.connect(model_manager.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM model_configurations")
            count = cursor.fetchone()[0]

        assert count > 0

    def test_load_default_models_claude_configuration(self, model_manager):
        """Test Claude model configuration"""
        model_manager._load_default_models()

        claude_model = model_manager.models["claude_claude-3-haiku-20240307"]
        assert claude_model.provider == "claude"
        assert claude_model.category == ModelCategory.CONVERSATION
        assert claude_model.status == ModelStatus.ACTIVE
        assert claude_model.supports_streaming is True
        assert "en" in claude_model.supported_languages

    def test_load_default_models_mistral_configuration(self, model_manager):
        """Test Mistral model configuration"""
        model_manager._load_default_models()

        mistral_model = model_manager.models["mistral_mistral-small-latest"]
        assert mistral_model.provider == "mistral"
        assert mistral_model.category == ModelCategory.CONVERSATION
        assert "fr" in mistral_model.primary_languages

    def test_load_default_models_deepseek_configuration(self, model_manager):
        """Test DeepSeek model configuration"""
        model_manager._load_default_models()

        deepseek_model = model_manager.models["deepseek_deepseek-chat"]
        assert deepseek_model.provider == "deepseek"
        assert "zh" in deepseek_model.primary_languages

    def test_load_default_models_ollama_configurations(self, model_manager):
        """Test Ollama local model configurations"""
        model_manager._load_default_models()

        llama_model = model_manager.models["ollama_llama2:7b"]
        assert llama_model.provider == "ollama"
        assert llama_model.cost_per_1k_tokens == 0.0  # Free local model

        mistral_local = model_manager.models["ollama_mistral:7b"]
        assert mistral_local.provider == "ollama"
        assert mistral_local.cost_per_1k_tokens == 0.0


# ============================================================================
# DATABASE OPERATION TESTS
# ============================================================================


class TestDatabaseOperations:
    """Test database save and load operations"""

    def test_save_model_to_db(self, model_manager, sample_model_config):
        """Test saving model configuration to database"""
        model_id = "test_provider_test-model-v1"
        model_manager._save_model_to_db(model_id, sample_model_config)

        with sqlite3.connect(model_manager.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM model_configurations WHERE model_id = ?", (model_id,)
            )
            row = cursor.fetchone()

        assert row is not None
        assert row[1] == "test_provider"  # provider
        assert row[2] == "test-model-v1"  # model_name

    def test_save_model_to_db_replaces_existing(
        self, model_manager, sample_model_config
    ):
        """Test saving model configuration replaces existing"""
        model_id = "test_provider_test-model-v1"

        # Save first time
        model_manager._save_model_to_db(model_id, sample_model_config)

        # Modify and save again
        sample_model_config.quality_score = 0.95
        model_manager._save_model_to_db(model_id, sample_model_config)

        with sqlite3.connect(model_manager.db_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM model_configurations WHERE model_id = ?",
                (model_id,),
            )
            count = cursor.fetchone()[0]

        assert count == 1  # Should still be only one row

    def test_save_usage_stats_to_db(self, model_manager, sample_usage_stats):
        """Test saving usage statistics to database"""
        model_id = "test_provider_test-model-v1"
        model_manager._save_usage_stats_to_db(model_id, sample_usage_stats)

        with sqlite3.connect(model_manager.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM model_usage_stats WHERE model_id = ?", (model_id,)
            )
            row = cursor.fetchone()

        assert row is not None
        assert row[3] == 100  # total_requests
        assert row[4] == 95  # successful_requests

    def test_log_performance(self, model_manager):
        """Test logging performance data"""
        model_id = "test_model"
        model_manager._log_performance(
            model_id=model_id,
            response_time_ms=1500.0,
            tokens_used=500,
            cost=0.05,
            quality_rating=0.85,
        )

        with sqlite3.connect(model_manager.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM model_performance_logs WHERE model_id = ?", (model_id,)
            )
            row = cursor.fetchone()

        assert row is not None
        # Schema: id, model_id, timestamp, request_type, language, response_time_ms, tokens_used, cost, quality_rating, error_count
        assert row[5] == 1500.0  # response_time_ms (column index 5)
        assert row[6] == 500  # tokens_used (column index 6)
        assert row[7] == 0.05  # cost (column index 7)
        assert row[8] == 0.85  # quality_rating (column index 8)


# ============================================================================
# MODEL CRUD OPERATION TESTS
# ============================================================================


class TestModelCRUDOperations:
    """Test model configuration CRUD operations"""

    @pytest.mark.asyncio
    async def test_get_all_models_empty(self, model_manager):
        """Test getting all models when none exist"""
        models = await model_manager.get_all_models()
        assert models == []

    @pytest.mark.asyncio
    async def test_get_all_models_with_data(self, model_manager):
        """Test getting all models with data"""
        model_manager._load_default_models()
        models = await model_manager.get_all_models()

        assert len(models) > 0
        assert all("id" in m for m in models)
        assert all("provider" in m for m in models)
        assert all("usage_stats" in m for m in models)

    @pytest.mark.asyncio
    async def test_get_all_models_filter_by_category(self, model_manager):
        """Test filtering models by category"""
        model_manager._load_default_models()

        conversation_models = await model_manager.get_all_models(
            category="conversation"
        )

        assert all(m["category"] == "conversation" for m in conversation_models)

    @pytest.mark.asyncio
    async def test_get_all_models_enabled_only(
        self, model_manager, sample_model_config
    ):
        """Test filtering enabled models only"""
        model_manager._load_default_models()

        # Add a disabled model
        disabled_config = sample_model_config
        disabled_config.enabled = False
        model_manager.models["disabled_model"] = disabled_config

        enabled_models = await model_manager.get_all_models(enabled_only=True)

        assert all(m["enabled"] for m in enabled_models)
        assert not any(m["id"] == "disabled_model" for m in enabled_models)

    @pytest.mark.asyncio
    async def test_get_all_models_sorted_by_priority(self, model_manager):
        """Test models are sorted by priority and quality"""
        model_manager._load_default_models()
        models = await model_manager.get_all_models()

        # Check priority ordering (lower number = higher priority)
        for i in range(len(models) - 1):
            if models[i]["priority"] == models[i + 1]["priority"]:
                # Same priority, should be sorted by quality (descending)
                assert models[i]["quality_score"] >= models[i + 1]["quality_score"]
            else:
                # Different priority, check priority order
                assert models[i]["priority"] <= models[i + 1]["priority"]

    @pytest.mark.asyncio
    async def test_get_model_exists(self, model_manager):
        """Test getting specific model that exists"""
        model_manager._load_default_models()

        model = await model_manager.get_model("claude_claude-3-haiku-20240307")

        assert model is not None
        assert model["id"] == "claude_claude-3-haiku-20240307"
        assert model["provider"] == "claude"

    @pytest.mark.asyncio
    async def test_get_model_not_exists(self, model_manager):
        """Test getting specific model that doesn't exist"""
        model_manager._load_default_models()

        model = await model_manager.get_model("nonexistent_model")

        assert model is None

    @pytest.mark.asyncio
    async def test_update_model_success(self, model_manager, sample_model_config):
        """Test updating model configuration"""
        model_id = "test_model"
        model_manager.models[model_id] = sample_model_config

        result = await model_manager.update_model(
            model_id, {"quality_score": 0.95, "priority": 2}
        )

        assert result is True
        assert model_manager.models[model_id].quality_score == 0.95
        assert model_manager.models[model_id].priority == 2

    @pytest.mark.asyncio
    async def test_update_model_not_found(self, model_manager):
        """Test updating nonexistent model"""
        result = await model_manager.update_model(
            "nonexistent", {"quality_score": 0.95}
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_update_model_status(self, model_manager, sample_model_config):
        """Test updating model status"""
        model_id = "test_model"
        model_manager.models[model_id] = sample_model_config

        result = await model_manager.update_model(model_id, {"status": "maintenance"})

        assert result is True
        assert model_manager.models[model_id].status == ModelStatus.MAINTENANCE

    @pytest.mark.asyncio
    async def test_update_model_clears_cache(self, model_manager, sample_model_config):
        """Test updating model clears performance cache"""
        model_id = "test_model"
        model_manager.models[model_id] = sample_model_config
        model_manager.performance_cache = {"some": "data"}

        await model_manager.update_model(model_id, {"priority": 3})

        assert model_manager.performance_cache == {}

    @pytest.mark.asyncio
    async def test_update_model_only_updateable_fields(
        self, model_manager, sample_model_config
    ):
        """Test only updateable fields can be changed"""
        model_id = "test_model"
        original_provider = sample_model_config.provider
        model_manager.models[model_id] = sample_model_config

        # Try to update non-updateable field
        await model_manager.update_model(
            model_id, {"provider": "new_provider", "priority": 5}
        )

        # Provider should not change, but priority should
        assert model_manager.models[model_id].provider == original_provider
        assert model_manager.models[model_id].priority == 5

    @pytest.mark.asyncio
    async def test_enable_model(self, model_manager, sample_model_config):
        """Test enabling a model"""
        model_id = "test_model"
        sample_model_config.enabled = False
        model_manager.models[model_id] = sample_model_config

        result = await model_manager.enable_model(model_id)

        assert result is True
        assert model_manager.models[model_id].enabled is True

    @pytest.mark.asyncio
    async def test_disable_model(self, model_manager, sample_model_config):
        """Test disabling a model"""
        model_id = "test_model"
        model_manager.models[model_id] = sample_model_config

        result = await model_manager.disable_model(model_id)

        assert result is True
        assert model_manager.models[model_id].enabled is False

    @pytest.mark.asyncio
    async def test_set_model_priority_valid(self, model_manager, sample_model_config):
        """Test setting valid model priority"""
        model_id = "test_model"
        model_manager.models[model_id] = sample_model_config

        result = await model_manager.set_model_priority(model_id, 5)

        assert result is True
        assert model_manager.models[model_id].priority == 5

    @pytest.mark.asyncio
    async def test_set_model_priority_invalid_too_low(
        self, model_manager, sample_model_config
    ):
        """Test setting invalid priority (too low)"""
        model_id = "test_model"
        model_manager.models[model_id] = sample_model_config

        result = await model_manager.set_model_priority(model_id, 0)

        assert result is False

    @pytest.mark.asyncio
    async def test_set_model_priority_invalid_too_high(
        self, model_manager, sample_model_config
    ):
        """Test setting invalid priority (too high)"""
        model_id = "test_model"
        model_manager.models[model_id] = sample_model_config

        result = await model_manager.set_model_priority(model_id, 11)

        assert result is False


# ============================================================================
# USAGE TRACKING TESTS
# ============================================================================


class TestUsageTracking:
    """Test model usage tracking and performance logging"""

    @pytest.mark.asyncio
    async def test_track_model_usage_first_request(self, model_manager):
        """Test tracking usage for first request"""
        model_id = "test_model"
        model_manager.usage_stats[model_id] = ModelUsageStats(
            model_id=model_id,
            provider="test",
            model_name="test",
        )

        await model_manager.track_model_usage(
            model_id=model_id,
            response_time_ms=1500.0,
            tokens_used=500,
            cost=0.05,
            success=True,
            quality_rating=0.85,
        )

        stats = model_manager.usage_stats[model_id]
        assert stats.total_requests == 1
        assert stats.successful_requests == 1
        assert stats.avg_response_time == 1500.0
        assert stats.min_response_time == 1500.0
        assert stats.max_response_time == 1500.0

    @pytest.mark.asyncio
    async def test_track_model_usage_multiple_requests(self, model_manager):
        """Test tracking usage across multiple requests"""
        model_id = "test_model"
        model_manager.usage_stats[model_id] = ModelUsageStats(
            model_id=model_id,
            provider="test",
            model_name="test",
        )

        # First request
        await model_manager.track_model_usage(
            model_id=model_id,
            response_time_ms=1000.0,
            tokens_used=500,
            cost=0.05,
            success=True,
        )

        # Second request
        await model_manager.track_model_usage(
            model_id=model_id,
            response_time_ms=2000.0,
            tokens_used=600,
            cost=0.06,
            success=True,
        )

        stats = model_manager.usage_stats[model_id]
        assert stats.total_requests == 2
        assert stats.successful_requests == 2
        assert stats.total_tokens == 1100
        assert stats.total_cost == 0.11
        assert stats.avg_response_time == 1500.0
        assert stats.min_response_time == 1000.0
        assert stats.max_response_time == 2000.0

    @pytest.mark.asyncio
    async def test_track_model_usage_failed_request(self, model_manager):
        """Test tracking failed request"""
        model_id = "test_model"
        model_manager.usage_stats[model_id] = ModelUsageStats(
            model_id=model_id,
            provider="test",
            model_name="test",
        )

        await model_manager.track_model_usage(
            model_id=model_id,
            response_time_ms=1000.0,
            tokens_used=0,
            cost=0.0,
            success=False,
        )

        stats = model_manager.usage_stats[model_id]
        assert stats.total_requests == 1
        assert stats.successful_requests == 0
        assert stats.failed_requests == 1

    @pytest.mark.asyncio
    async def test_track_model_usage_quality_rating_first(self, model_manager):
        """Test quality rating tracking for first request"""
        model_id = "test_model"
        model_manager.usage_stats[model_id] = ModelUsageStats(
            model_id=model_id,
            provider="test",
            model_name="test",
        )

        await model_manager.track_model_usage(
            model_id=model_id,
            response_time_ms=1000.0,
            tokens_used=500,
            cost=0.05,
            success=True,
            quality_rating=0.9,
        )

        stats = model_manager.usage_stats[model_id]
        assert stats.avg_quality_rating == 0.9

    @pytest.mark.asyncio
    async def test_track_model_usage_quality_rating_weighted_average(
        self, model_manager
    ):
        """Test quality rating uses weighted average"""
        model_id = "test_model"
        model_manager.usage_stats[model_id] = ModelUsageStats(
            model_id=model_id,
            provider="test",
            model_name="test",
        )

        # First request
        await model_manager.track_model_usage(
            model_id=model_id,
            response_time_ms=1000.0,
            tokens_used=500,
            cost=0.05,
            success=True,
            quality_rating=0.8,
        )

        # Second request
        await model_manager.track_model_usage(
            model_id=model_id,
            response_time_ms=1000.0,
            tokens_used=500,
            cost=0.05,
            success=True,
            quality_rating=1.0,
        )

        stats = model_manager.usage_stats[model_id]
        # Should be weighted: 0.8 * 0.8 + 1.0 * 0.2 = 0.84
        assert abs(stats.avg_quality_rating - 0.84) < 0.01

    @pytest.mark.asyncio
    async def test_track_model_usage_no_quality_rating(self, model_manager):
        """Test tracking without quality rating"""
        model_id = "test_model"
        model_manager.usage_stats[model_id] = ModelUsageStats(
            model_id=model_id,
            provider="test",
            model_name="test",
        )

        await model_manager.track_model_usage(
            model_id=model_id,
            response_time_ms=1000.0,
            tokens_used=500,
            cost=0.05,
            success=True,
            quality_rating=None,
        )

        stats = model_manager.usage_stats[model_id]
        assert stats.avg_quality_rating == 0.0

    @pytest.mark.asyncio
    async def test_track_model_usage_nonexistent_model(self, model_manager):
        """Test tracking usage for nonexistent model (should not crash)"""
        await model_manager.track_model_usage(
            model_id="nonexistent",
            response_time_ms=1000.0,
            tokens_used=500,
            cost=0.05,
            success=True,
        )
        # Should not crash, just return early


# ============================================================================
# PERFORMANCE REPORT TESTS
# ============================================================================


class TestPerformanceReports:
    """Test performance report generation and analytics"""

    @pytest.mark.asyncio
    async def test_get_model_performance_report_nonexistent_model(self, model_manager):
        """Test getting report for nonexistent model"""
        report = await model_manager.get_model_performance_report("nonexistent")
        assert report is None

    @pytest.mark.asyncio
    async def test_get_model_performance_report_no_data(
        self, model_manager, sample_model_config
    ):
        """Test getting report with no performance data"""
        model_id = "test_model"
        model_manager.models[model_id] = sample_model_config

        report = await model_manager.get_model_performance_report(model_id)
        assert report is None

    @pytest.mark.asyncio
    async def test_get_model_performance_report_with_data(
        self, model_manager, sample_model_config
    ):
        """Test getting performance report with data"""
        model_id = "test_model"
        model_manager.models[model_id] = sample_model_config
        model_manager.usage_stats[model_id] = ModelUsageStats(
            model_id=model_id,
            provider="test",
            model_name="test",
            total_requests=100,
            successful_requests=95,
        )

        # Add performance logs
        for i in range(10):
            model_manager._log_performance(
                model_id=model_id,
                response_time_ms=1000.0 + i * 100,
                tokens_used=500,
                cost=0.05,
                quality_rating=0.85,
            )

        # Add another enabled model for ranking
        model_manager.models["other_model"] = ModelConfiguration(
            provider="other",
            model_name="other",
            display_name="Other",
            category=ModelCategory.GENERAL,
            size=ModelSize.SMALL,
            status=ModelStatus.ACTIVE,
            cost_per_1k_tokens=0.02,
            avg_response_time_ms=2000,
            quality_score=0.7,
            reliability_score=0.8,
            supported_languages=["en"],
            primary_languages=["en"],
            max_tokens=2048,
            context_window=4096,
            supports_streaming=False,
            supports_functions=False,
            enabled=True,
        )

        report = await model_manager.get_model_performance_report(model_id, days=30)

        assert report is not None
        assert report.model_id == model_id
        assert report.cost_efficiency > 0
        assert report.speed_efficiency > 0
        assert report.reliability_score == sample_model_config.reliability_score

    def test_fetch_performance_data_exists(self, model_manager):
        """Test fetching performance data that exists"""
        model_id = "test_model"

        # Add some performance logs
        for i in range(5):
            model_manager._log_performance(
                model_id=model_id,
                response_time_ms=1000.0,
                tokens_used=500,
                cost=0.05,
                quality_rating=0.85,
            )

        data = model_manager._fetch_performance_data(model_id, days=30)
        assert data is not None
        assert data[0] == 5  # total_requests

    def test_fetch_performance_data_not_exists(self, model_manager):
        """Test fetching performance data that doesn't exist"""
        data = model_manager._fetch_performance_data("nonexistent", days=30)
        assert data is None

    def test_calculate_efficiency_metrics(self, model_manager, sample_model_config):
        """Test calculating efficiency metrics"""
        perf_data = (
            10,
            1000.0,
            0.85,
            0.01,
            5000,
        )  # requests, time, quality, cost, tokens

        efficiency = model_manager._calculate_efficiency_metrics(
            sample_model_config, perf_data
        )

        assert "cost" in efficiency
        assert "speed" in efficiency
        assert efficiency["cost"] > 0
        assert efficiency["speed"] > 0

    def test_generate_model_recommendations_conversation(self, model_manager):
        """Test generating recommendations for conversation model"""
        model = ModelConfiguration(
            provider="test",
            model_name="test",
            display_name="Test",
            category=ModelCategory.CONVERSATION,
            size=ModelSize.MEDIUM,
            status=ModelStatus.ACTIVE,
            cost_per_1k_tokens=0.0005,
            avg_response_time_ms=1000,
            quality_score=0.85,
            reliability_score=0.9,
            supported_languages=["en", "zh"],
            primary_languages=["zh"],
            max_tokens=2048,
            context_window=4096,
            supports_streaming=True,
            supports_functions=False,
        )

        recommendations = model_manager._generate_model_recommendations(model)

        assert "conversation" in recommendations
        assert "chat" in recommendations
        assert "high_volume" in recommendations
        assert "chinese_language" in recommendations

    def test_generate_model_recommendations_high_quality(self, model_manager):
        """Test recommendations include complex tasks for high quality"""
        model = ModelConfiguration(
            provider="test",
            model_name="test",
            display_name="Test",
            category=ModelCategory.GRAMMAR,
            size=ModelSize.LARGE,
            status=ModelStatus.ACTIVE,
            cost_per_1k_tokens=0.02,
            avg_response_time_ms=1000,
            quality_score=0.92,
            reliability_score=0.95,
            supported_languages=["en", "fr"],
            primary_languages=["fr"],
            max_tokens=4096,
            context_window=8192,
            supports_streaming=True,
            supports_functions=True,
        )

        recommendations = model_manager._generate_model_recommendations(model)

        assert "complex_tasks" in recommendations
        assert "french_language" in recommendations

    def test_generate_optimization_suggestions_high_cost(
        self, model_manager, sample_model_config
    ):
        """Test suggestions for high-cost model"""
        sample_model_config.cost_per_1k_tokens = 0.015
        stats = ModelUsageStats(
            model_id="test",
            provider="test",
            model_name="test",
            total_requests=200,
            successful_requests=200,
        )

        suggestions = model_manager._generate_optimization_suggestions(
            sample_model_config, stats
        )

        assert any("cost-sensitive" in s for s in suggestions)

    def test_generate_optimization_suggestions_slow_response(
        self, model_manager, sample_model_config
    ):
        """Test suggestions for slow response time"""
        sample_model_config.avg_response_time_ms = 3000
        stats = ModelUsageStats(
            model_id="test",
            provider="test",
            model_name="test",
        )

        suggestions = model_manager._generate_optimization_suggestions(
            sample_model_config, stats
        )

        assert any("response time" in s for s in suggestions)

    def test_generate_optimization_suggestions_low_reliability(
        self, model_manager, sample_model_config
    ):
        """Test suggestions for low reliability"""
        stats = ModelUsageStats(
            model_id="test",
            provider="test",
            model_name="test",
            total_requests=200,
            successful_requests=180,  # 90% success rate
        )

        suggestions = model_manager._generate_optimization_suggestions(
            sample_model_config, stats
        )

        assert any("reliability" in s for s in suggestions)


# ============================================================================
# SYSTEM OVERVIEW TESTS
# ============================================================================


class TestSystemOverview:
    """Test system overview and statistics"""

    @pytest.mark.asyncio
    async def test_get_system_overview_structure(self, model_manager):
        """Test system overview returns correct structure"""
        model_manager._load_default_models()

        with patch("app.services.ai_model_manager.budget_manager") as mock_budget:
            mock_budget.get_current_budget_status.return_value = Mock(
                remaining_budget=100.0,
                percentage_used=50.0,
                alert_level=Mock(value="green"),
            )

            overview = await model_manager.get_system_overview()

        assert "overview" in overview
        assert "budget_status" in overview
        assert "providers" in overview
        assert "top_models" in overview
        assert "categories" in overview

    @pytest.mark.asyncio
    async def test_get_system_overview_overview_stats(self, model_manager):
        """Test overview statistics calculation"""
        model_manager._load_default_models()

        with patch("app.services.ai_model_manager.budget_manager") as mock_budget:
            mock_budget.get_current_budget_status.return_value = Mock(
                remaining_budget=100.0,
                percentage_used=50.0,
                alert_level=Mock(value="green"),
            )

            overview = await model_manager.get_system_overview()

        stats = overview["overview"]
        assert "total_models" in stats
        assert "active_models" in stats
        assert "total_requests" in stats
        assert "total_cost" in stats
        assert stats["total_models"] > 0

    def test_calculate_overview_stats(self, model_manager):
        """Test calculating overview statistics"""
        models = [
            {
                "status": "active",
                "enabled": True,
                "usage_stats": {"total_requests": 100, "total_cost": 5.0},
            },
            {
                "status": "active",
                "enabled": False,
                "usage_stats": {"total_requests": 50, "total_cost": 2.0},
            },
            {
                "status": "inactive",
                "enabled": True,
                "usage_stats": {"total_requests": 0, "total_cost": 0.0},
            },
        ]

        stats = model_manager._calculate_overview_stats(models)

        assert stats["total_models"] == 3
        assert stats["active_models"] == 1
        assert stats["total_requests"] == 150
        assert stats["total_cost"] == 7.0
        # Code rounds to 6 decimal places
        assert stats["avg_cost_per_request"] == round(7.0 / 150, 6)

    def test_calculate_overview_stats_no_requests(self, model_manager):
        """Test overview stats with no requests (avoid division by zero)"""
        models = [
            {
                "status": "active",
                "enabled": True,
                "usage_stats": {"total_requests": 0, "total_cost": 0.0},
            },
        ]

        stats = model_manager._calculate_overview_stats(models)

        assert stats["avg_cost_per_request"] == 0.0

    def test_get_budget_status_dict(self, model_manager):
        """Test getting budget status dictionary"""
        with patch("app.services.ai_model_manager.budget_manager") as mock_budget:
            mock_budget.get_current_budget_status.return_value = Mock(
                remaining_budget=75.5,
                percentage_used=24.5,
                alert_level=Mock(value="green"),
            )

            budget_status = model_manager._get_budget_status_dict()

        assert budget_status["remaining_budget"] == 75.5
        assert budget_status["percentage_used"] == 24.5
        assert budget_status["alert_level"] == "green"

    def test_get_budget_status_dict_no_alert_level(self, model_manager):
        """Test budget status with no alert level"""
        with patch("app.services.ai_model_manager.budget_manager") as mock_budget:
            mock_budget.get_current_budget_status.return_value = Mock(
                remaining_budget=100.0,
                percentage_used=0.0,
                alert_level=None,
            )

            budget_status = model_manager._get_budget_status_dict()

        assert budget_status["alert_level"] == "green"

    def test_calculate_provider_breakdown(self, model_manager):
        """Test calculating provider breakdown"""
        models = [
            {
                "provider": "claude",
                "status": "active",
                "enabled": True,
                "usage_stats": {"total_requests": 100, "total_cost": 10.0},
            },
            {
                "provider": "claude",
                "status": "active",
                "enabled": True,
                "usage_stats": {"total_requests": 50, "total_cost": 5.0},
            },
            {
                "provider": "ollama",
                "status": "active",
                "enabled": True,
                "usage_stats": {"total_requests": 200, "total_cost": 0.0},
            },
        ]

        breakdown = model_manager._calculate_provider_breakdown(models)

        assert "claude" in breakdown
        assert "ollama" in breakdown
        assert breakdown["claude"]["models"] == 2
        assert breakdown["claude"]["active_models"] == 2
        assert breakdown["claude"]["total_requests"] == 150
        assert breakdown["claude"]["total_cost"] == 15.0

    def test_get_top_performing_models(self, model_manager):
        """Test getting top performing models"""
        models = [
            {
                "id": "model1",
                "display_name": "Model 1",
                "provider": "test",
                "usage_stats": {"total_requests": 100},
                "quality_score": 0.9,
            },
            {
                "id": "model2",
                "display_name": "Model 2",
                "provider": "test",
                "usage_stats": {"total_requests": 200},
                "quality_score": 0.8,
            },
            {
                "id": "model3",
                "display_name": "Model 3",
                "provider": "test",
                "usage_stats": {"total_requests": 50},
                "quality_score": 0.95,
            },
        ]

        top_models = model_manager._get_top_performing_models(models, limit=2)

        assert len(top_models) == 2
        assert top_models[0]["id"] == "model2"  # Most requests
        assert top_models[1]["id"] == "model1"

    def test_calculate_category_breakdown(self, model_manager):
        """Test calculating category breakdown"""
        models = [
            {"category": "conversation"},
            {"category": "conversation"},
            {"category": "grammar"},
            {"category": "translation"},
        ]

        breakdown = model_manager._calculate_category_breakdown(models)

        assert breakdown["conversation"] == 2
        assert breakdown["grammar"] == 1
        assert breakdown["translation"] == 1


# ============================================================================
# MODEL OPTIMIZATION TESTS
# ============================================================================


class TestModelOptimization:
    """Test model selection optimization"""

    @pytest.mark.asyncio
    async def test_optimize_model_selection_basic(self, model_manager):
        """Test basic model optimization"""
        model_manager._load_default_models()

        recommended = await model_manager.optimize_model_selection(
            language="en",
            use_case="conversation",
        )

        assert len(recommended) > 0
        assert all(isinstance(model_id, str) for model_id in recommended)

    @pytest.mark.asyncio
    async def test_optimize_model_selection_with_budget(self, model_manager):
        """Test optimization with budget limit"""
        model_manager._load_default_models()

        recommended = await model_manager.optimize_model_selection(
            language="en",
            use_case="conversation",
            budget_limit=0.005,
        )

        # Should only include models within budget
        for model_id in recommended:
            model = model_manager.models[model_id]
            assert model.cost_per_1k_tokens <= 0.005

    @pytest.mark.asyncio
    async def test_optimize_model_selection_language_specific(self, model_manager):
        """Test optimization for specific language"""
        model_manager._load_default_models()

        zh_recommended = await model_manager.optimize_model_selection(
            language="zh",
            use_case="conversation",
        )

        # DeepSeek should be highly ranked for Chinese
        assert any("deepseek" in model_id for model_id in zh_recommended[:3])

    def test_filter_suitable_models_by_language(self, model_manager):
        """Test filtering models by language support"""
        models = [
            {
                "supported_languages": ["en", "es"],
                "primary_languages": ["en"],
                "cost_per_1k_tokens": 0.01,
            },
            {
                "supported_languages": ["zh", "en"],
                "primary_languages": ["zh"],
                "cost_per_1k_tokens": 0.01,
            },
        ]

        suitable = model_manager._filter_suitable_models(models, "zh", None)

        assert len(suitable) == 1
        assert "zh" in suitable[0]["supported_languages"]

    def test_filter_suitable_models_by_budget(self, model_manager):
        """Test filtering models by budget limit"""
        models = [
            {
                "supported_languages": ["en"],
                "primary_languages": ["en"],
                "cost_per_1k_tokens": 0.001,
            },
            {
                "supported_languages": ["en"],
                "primary_languages": ["en"],
                "cost_per_1k_tokens": 0.01,
            },
        ]

        suitable = model_manager._filter_suitable_models(models, "en", 0.005)

        assert len(suitable) == 1
        assert suitable[0]["cost_per_1k_tokens"] <= 0.005

    def test_calculate_model_score(self, model_manager):
        """Test calculating optimization score"""
        model = {
            "quality_score": 0.9,
            "reliability_score": 0.95,
            "supported_languages": ["en", "es"],
            "primary_languages": ["en"],
            "cost_per_1k_tokens": 0.005,
            "avg_response_time_ms": 1000,
            "category": "conversation",
            "priority": 1,
        }

        score = model_manager._calculate_model_score(model, "en", "conversation")

        assert score > 0
        assert isinstance(score, float)

    def test_get_quality_score(self, model_manager):
        """Test quality score contribution"""
        model = {"quality_score": 0.9}
        score = model_manager._get_quality_score(model)
        assert score == 0.9 * 40

    def test_get_reliability_score(self, model_manager):
        """Test reliability score contribution"""
        model = {"reliability_score": 0.95}
        score = model_manager._get_reliability_score(model)
        assert score == 0.95 * 20

    def test_get_language_match_score_primary(self, model_manager):
        """Test language match bonus for primary language"""
        model = {
            "primary_languages": ["fr", "en"],
            "supported_languages": ["fr", "en", "es"],
        }
        score = model_manager._get_language_match_score(model, "fr")
        assert score == 15

    def test_get_language_match_score_supported(self, model_manager):
        """Test language match bonus for supported language"""
        model = {"primary_languages": ["en"], "supported_languages": ["en", "es", "fr"]}
        score = model_manager._get_language_match_score(model, "es")
        assert score == 10

    def test_get_language_match_score_not_supported(self, model_manager):
        """Test no bonus for unsupported language"""
        model = {"primary_languages": ["en"], "supported_languages": ["en", "es"]}
        score = model_manager._get_language_match_score(model, "zh")
        assert score == 0

    def test_get_cost_efficiency_score(self, model_manager):
        """Test cost efficiency score calculation"""
        cheap_model = {"cost_per_1k_tokens": 0.001}
        expensive_model = {"cost_per_1k_tokens": 0.02}

        cheap_score = model_manager._get_cost_efficiency_score(cheap_model)
        expensive_score = model_manager._get_cost_efficiency_score(expensive_model)

        assert cheap_score > expensive_score

    def test_get_speed_score(self, model_manager):
        """Test speed score calculation"""
        fast_model = {"avg_response_time_ms": 500}
        slow_model = {"avg_response_time_ms": 3000}

        fast_score = model_manager._get_speed_score(fast_model)
        slow_score = model_manager._get_speed_score(slow_model)

        assert fast_score > slow_score

    def test_get_category_match_score_match(self, model_manager):
        """Test category match bonus"""
        model = {"category": "conversation"}
        score = model_manager._get_category_match_score(model, "conversation")
        assert score == 10

    def test_get_category_match_score_no_match(self, model_manager):
        """Test no category match bonus"""
        model = {"category": "grammar"}
        score = model_manager._get_category_match_score(model, "conversation")
        assert score == 0

    def test_get_priority_score(self, model_manager):
        """Test priority score calculation"""
        high_priority = {"priority": 1}
        low_priority = {"priority": 10}

        high_score = model_manager._get_priority_score(high_priority)
        low_score = model_manager._get_priority_score(low_priority)

        assert high_score == 10
        assert low_score == 1
        assert high_score > low_score

    def test_select_top_models(self, model_manager):
        """Test selecting top models by score"""
        models = [
            {"id": "model1", "optimization_score": 100},
            {"id": "model2", "optimization_score": 85},
            {"id": "model3", "optimization_score": 95},
        ]

        top_ids = model_manager._select_top_models(models, limit=2)

        assert len(top_ids) == 2
        assert top_ids[0] == "model1"
        assert top_ids[1] == "model3"


# ============================================================================
# HEALTH STATUS TESTS
# ============================================================================


class TestHealthStatus:
    """Test health status monitoring"""

    @pytest.mark.asyncio
    async def test_get_health_status_structure(self, model_manager):
        """Test health status returns correct structure"""
        model_manager._load_default_models()

        with patch("app.services.ai_model_manager.ai_router") as mock_router:
            mock_router.get_router_status = AsyncMock(
                return_value={
                    "router_mode": "balanced",
                    "fallback_status": {"ollama_available": True},
                    "budget_status": {"remaining": 100.0},
                }
            )
            mock_router.check_provider_health = AsyncMock(
                return_value={
                    "status": "healthy",
                    "available": True,
                }
            )

            health = await model_manager.get_health_status()

        assert "system_health" in health
        assert "providers" in health
        assert "router_status" in health
        assert "total_models" in health
        assert "active_models" in health

    @pytest.mark.asyncio
    async def test_get_health_status_healthy_system(self, model_manager):
        """Test health status when system is healthy"""
        model_manager._load_default_models()

        with patch("app.services.ai_model_manager.ai_router") as mock_router:
            mock_router.get_router_status = AsyncMock(
                return_value={
                    "router_mode": "balanced",
                    "fallback_status": {"ollama_available": True},
                    "budget_status": {},
                }
            )
            mock_router.check_provider_health = AsyncMock(
                return_value={
                    "status": "healthy",
                    "available": True,
                }
            )

            health = await model_manager.get_health_status()

        assert health["system_health"] == "healthy"

    @pytest.mark.asyncio
    async def test_get_health_status_degraded_system(self, model_manager):
        """Test health status when all providers unavailable"""
        model_manager._load_default_models()

        with patch("app.services.ai_model_manager.ai_router") as mock_router:
            mock_router.get_router_status = AsyncMock(
                return_value={
                    "router_mode": "balanced",
                    "fallback_status": {"ollama_available": False},
                    "budget_status": {},
                }
            )
            mock_router.check_provider_health = AsyncMock(
                return_value={
                    "status": "unhealthy",
                    "available": False,
                }
            )

            health = await model_manager.get_health_status()

        assert health["system_health"] == "degraded"

    @pytest.mark.asyncio
    async def test_get_health_status_provider_breakdown(self, model_manager):
        """Test provider health breakdown"""
        model_manager._load_default_models()

        health_responses = {
            "claude": {"status": "healthy", "available": True},
            "mistral": {"status": "healthy", "available": True},
            "deepseek": {"status": "unhealthy", "available": False},
            "ollama": {"status": "healthy", "available": True},
        }

        with patch("app.services.ai_model_manager.ai_router") as mock_router:
            mock_router.get_router_status = AsyncMock(
                return_value={
                    "router_mode": "balanced",
                    "fallback_status": {"ollama_available": True},
                    "budget_status": {},
                }
            )
            mock_router.check_provider_health = AsyncMock(
                side_effect=lambda name: health_responses.get(
                    name, {"status": "unknown", "available": False}
                )
            )

            health = await model_manager.get_health_status()

        providers = health["providers"]
        assert providers["claude"]["available"] is True
        assert providers["deepseek"]["available"] is False
        assert all("models" in p for p in providers.values())


# ============================================================================
# GLOBAL INSTANCE TEST
# ============================================================================


class TestGlobalInstance:
    """Test global ai_model_manager instance"""

    def test_global_instance_exists(self):
        """Test global instance is created"""
        assert ai_model_manager is not None
        assert isinstance(ai_model_manager, AIModelManager)

    def test_global_instance_has_models(self):
        """Test global instance loads default models"""
        assert len(ai_model_manager.models) > 0

    def test_global_instance_has_database(self):
        """Test global instance has database connection"""
        assert ai_model_manager.db_path is not None
        assert Path(ai_model_manager.db_path).parent.exists()


# ============================================================================
# INTEGRATION TESTS (Real execution for coverage)
# ============================================================================


class TestRealExecution:
    """Tests that actually execute real code for coverage measurement"""

    @pytest.mark.asyncio
    async def test_calculate_model_rankings_real(self):
        """Test _calculate_model_rankings with real execution"""
        # Use the global instance with real models
        model_ids = list(ai_model_manager.models.keys())
        if model_ids:
            rankings = await ai_model_manager._calculate_model_rankings(model_ids[0])
            assert "cost" in rankings
            assert "speed" in rankings
            assert "quality" in rankings
            assert "overall" in rankings

    def test_score_models_real(self):
        """Test _score_models with real execution"""
        models = [
            {
                "quality_score": 0.9,
                "reliability_score": 0.95,
                "supported_languages": ["en"],
                "primary_languages": ["en"],
                "cost_per_1k_tokens": 0.01,
                "avg_response_time_ms": 1000,
                "category": "conversation",
                "priority": 1,
            }
        ]
        scored = ai_model_manager._score_models(models, "en", "conversation")
        assert "optimization_score" in scored[0]

    def test_filter_suitable_models_real(self):
        """Test _filter_suitable_models with real execution"""
        models = [
            {
                "supported_languages": ["en", "es"],
                "primary_languages": ["en"],
                "cost_per_1k_tokens": 0.01,
            }
        ]
        suitable = ai_model_manager._filter_suitable_models(models, "en", 0.02)
        assert len(suitable) == 1

    @pytest.mark.asyncio
    async def test_update_model_real_field_check(self):
        """Test update_model with non-updateable field"""
        # Get a real model
        model_ids = list(ai_model_manager.models.keys())
        if model_ids:
            model_id = model_ids[0]
            original_provider = ai_model_manager.models[model_id].provider

            # Try to update non-updateable field (provider)
            await ai_model_manager.update_model(model_id, {"provider": "new_provider"})

            # Provider should not have changed
            assert ai_model_manager.models[model_id].provider == original_provider


# ============================================================================
# MISSING BRANCH COVERAGE TESTS
# ============================================================================

class TestMissingBranches:
    """Tests to cover the remaining missing branches for TRUE 100%"""

    def test_load_default_models_existing_usage_stats(self, model_manager):
        """Test loading models when usage stats already exist (line 405 else branch)"""
        model_manager._load_default_models()
        
        # Get count before reloading
        initial_count = len(model_manager.usage_stats)
        
        # Load again - should skip creating new usage stats for existing models
        model_manager._load_default_models()
        
        # Count should be same (doesn't double up)
        assert len(model_manager.usage_stats) == initial_count

    @pytest.mark.asyncio
    async def test_update_model_field_without_hasattr(self, model_manager, sample_model_config):
        """Test update with field that doesn't exist on model (line 589 else branch)"""
        model_id = "test_model"
        model_manager.models[model_id] = sample_model_config
        
        # Temporarily add a field to updateable_fields that model doesn't have
        # This requires patching the update_model method logic
        # Instead, test with a valid updateable field first, then an invalid one
        result = await model_manager.update_model(
            model_id,
            {"priority": 5, "nonexistent_invalid_field": "value"}
        )
        
        # Should succeed (priority updated) and skip nonexistent field
        assert result is True
        assert model_manager.models[model_id].priority == 5
        assert not hasattr(model_manager.models[model_id], "nonexistent_invalid_field")

    @pytest.mark.asyncio
    async def test_calculate_model_rankings_model_not_found(self, model_manager):
        """Test rankings when model not found in lists (lines 776-782 defaults)"""
        # Create models list without the target model
        model_manager._load_default_models()
        
        # Create a model that won't be in the enabled list
        test_model_id = "nonexistent_model"
        
        # Directly call with nonexistent model to trigger default values
        rankings = await model_manager._calculate_model_rankings(test_model_id)
        
        # Should return 999 for all ranks (the default)
        assert rankings["cost"] == 999
        assert rankings["speed"] == 999
        assert rankings["quality"] == 999

    def test_generate_model_recommendations_low_quality(self, model_manager):
        """Test recommendations for low quality model (line 802 false branch)"""
        model = ModelConfiguration(
            provider="test",
            model_name="test",
            display_name="Test",
            category=ModelCategory.GRAMMAR,
            size=ModelSize.SMALL,
            status=ModelStatus.ACTIVE,
            cost_per_1k_tokens=0.01,
            avg_response_time_ms=1000,
            quality_score=0.75,  # <= 0.8, false branch
            reliability_score=0.85,
            supported_languages=["en"],
            primary_languages=["en"],
            max_tokens=2048,
            context_window=4096,
            supports_streaming=False,
            supports_functions=False,
        )
        
        recommendations = model_manager._generate_model_recommendations(model)
        
        # Should not include "complex_tasks" for low quality
        assert "complex_tasks" not in recommendations


    @pytest.mark.asyncio
    async def test_update_model_field_not_on_model(self, model_manager, sample_model_config):
        """Test update when field in updateable_fields but not on model (589->585 branch)"""
        model_id = "test_model"
        model_manager.models[model_id] = sample_model_config
        
        # Mock hasattr to return False for a specific field to trigger the else branch
        original_hasattr = hasattr
        def mock_hasattr(obj, name):
            # Return False for frequency_penalty to simulate missing attribute
            if name == "frequency_penalty":
                return False
            return original_hasattr(obj, name)
        
        # Patch hasattr in the update_model context
        with patch('builtins.hasattr', side_effect=mock_hasattr):
            result = await model_manager.update_model(
                model_id,
                {"frequency_penalty": 0.5, "priority": 3}
            )
        
        # Should succeed and update priority (frequency_penalty skipped due to hasattr=False)
        assert result is True
        assert model_manager.models[model_id].priority == 3

    def test_calculate_provider_breakdown_inactive_model(self, model_manager):
        """Test provider breakdown with inactive/disabled model (line 886 false branch)"""
        models = [
            {
                "provider": "test",
                "status": "inactive",  # Not active
                "enabled": True,
                "usage_stats": {"total_requests": 100, "total_cost": 5.0}
            },
            {
                "provider": "test",
                "status": "active",
                "enabled": False,  # Not enabled
                "usage_stats": {"total_requests": 50, "total_cost": 2.0}
            },
        ]
        
        breakdown = model_manager._calculate_provider_breakdown(models)
        
        # Both models should not count as active
        assert breakdown["test"]["models"] == 2
        assert breakdown["test"]["active_models"] == 0
