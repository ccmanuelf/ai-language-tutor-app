"""
AI Model Management Service
AI Language Tutor App - Task 3.1.5

Comprehensive AI model configuration and management system that provides:
- Model configuration and parameter management
- Provider health monitoring and performance tracking
- Dynamic model selection and routing
- Cost optimization and budget management
- Performance analytics and usage statistics
- Admin controls for model preferences
- Language-specific model optimization
- Quality metrics and response evaluation

This service extends the existing AI router with advanced management capabilities.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import sqlite3
from threading import Lock

# Register SQLite datetime adapters for Python 3.12+ compatibility
from app.utils.sqlite_adapters import register_sqlite_adapters

register_sqlite_adapters()

from app.services.ai_router import ai_router  # noqa: E402 - Required after logger configuration
from app.services.budget_manager import budget_manager  # noqa: E402 - Required after logger configuration
from app.core.config import get_settings  # noqa: E402 - Required after logger configuration

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """AI Model status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class ModelCategory(Enum):
    """AI Model categories"""

    CONVERSATION = "conversation"
    GRAMMAR = "grammar"
    TRANSLATION = "translation"
    PRONUNCIATION = "pronunciation"
    ANALYSIS = "analysis"
    GENERAL = "general"


class ModelSize(Enum):
    """AI Model sizes"""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"


@dataclass
class ModelConfiguration:
    """AI Model configuration"""

    provider: str
    model_name: str
    display_name: str
    category: ModelCategory
    size: ModelSize
    status: ModelStatus

    # Performance metrics
    cost_per_1k_tokens: float
    avg_response_time_ms: float
    quality_score: float  # 0.0 - 1.0
    reliability_score: float  # 0.0 - 1.0

    # Language support
    supported_languages: List[str]
    primary_languages: List[str]

    # Technical specs
    max_tokens: int
    context_window: int
    supports_streaming: bool
    supports_functions: bool

    # Configuration parameters
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    # Admin settings
    enabled: bool = True
    priority: int = 1  # 1 = highest, 10 = lowest
    weight: float = 1.0  # Routing weight

    # Metadata
    created_at: datetime = None
    updated_at: datetime = None
    last_used: datetime = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.updated_at:
            self.updated_at = datetime.now()


@dataclass
class ModelUsageStats:
    """Model usage statistics"""

    model_id: str
    provider: str
    model_name: str

    # Usage metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0

    # Performance metrics
    avg_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0

    # Quality metrics
    avg_quality_rating: float = 0.0
    user_satisfaction: float = 0.0

    # Time tracking
    last_24h_requests: int = 0
    last_7d_requests: int = 0
    last_30d_requests: int = 0

    first_used: datetime = None
    last_used: datetime = None


@dataclass
class ModelPerformanceReport:
    """Model performance analysis report"""

    model_id: str
    report_date: datetime

    # Efficiency metrics
    cost_efficiency: float  # Quality per dollar
    speed_efficiency: float  # Quality per second
    reliability_score: float

    # Comparative metrics
    rank_by_cost: int
    rank_by_speed: int
    rank_by_quality: int
    rank_overall: int

    # Recommendations
    recommended_for: List[str]
    optimization_suggestions: List[str]

    # Trend analysis
    performance_trend: str  # "improving", "stable", "declining"
    usage_trend: str


class AIModelManager:
    """Comprehensive AI Model Management System"""

    def __init__(self):
        self.settings = get_settings()
        self.db_path = "./data/ai_models.db"
        self._lock = Lock()
        self.models: Dict[str, ModelConfiguration] = {}
        self.usage_stats: Dict[str, ModelUsageStats] = {}
        self.performance_cache = {}
        self._initialize_database()
        self._load_default_models()

    def _initialize_database(self):
        """Initialize SQLite database for model management"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_configurations (
                    model_id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    size TEXT NOT NULL,
                    status TEXT NOT NULL,
                    cost_per_1k_tokens REAL NOT NULL,
                    avg_response_time_ms REAL NOT NULL,
                    quality_score REAL NOT NULL,
                    reliability_score REAL NOT NULL,
                    supported_languages TEXT NOT NULL,
                    primary_languages TEXT NOT NULL,
                    max_tokens INTEGER NOT NULL,
                    context_window INTEGER NOT NULL,
                    supports_streaming BOOLEAN NOT NULL,
                    supports_functions BOOLEAN NOT NULL,
                    temperature REAL NOT NULL,
                    top_p REAL NOT NULL,
                    frequency_penalty REAL NOT NULL,
                    presence_penalty REAL NOT NULL,
                    enabled BOOLEAN NOT NULL,
                    priority INTEGER NOT NULL,
                    weight REAL NOT NULL,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    last_used TIMESTAMP,
                    UNIQUE(provider, model_name)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_usage_stats (
                    model_id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    total_requests INTEGER DEFAULT 0,
                    successful_requests INTEGER DEFAULT 0,
                    failed_requests INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    total_cost REAL DEFAULT 0.0,
                    avg_response_time REAL DEFAULT 0.0,
                    min_response_time REAL DEFAULT 0.0,
                    max_response_time REAL DEFAULT 0.0,
                    avg_quality_rating REAL DEFAULT 0.0,
                    user_satisfaction REAL DEFAULT 0.0,
                    last_24h_requests INTEGER DEFAULT 0,
                    last_7d_requests INTEGER DEFAULT 0,
                    last_30d_requests INTEGER DEFAULT 0,
                    first_used TIMESTAMP,
                    last_used TIMESTAMP,
                    FOREIGN KEY(model_id) REFERENCES model_configurations(model_id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_performance_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    request_type TEXT,
                    language TEXT,
                    response_time_ms REAL,
                    tokens_used INTEGER,
                    cost REAL,
                    quality_rating REAL,
                    error_count INTEGER DEFAULT 0,
                    FOREIGN KEY(model_id) REFERENCES model_configurations(model_id)
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_performance_logs_model_timestamp
                ON model_performance_logs(model_id, timestamp)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_performance_logs_language
                ON model_performance_logs(language, timestamp)
            """)

    def _load_default_models(self):
        """Load default model configurations"""
        default_models = [
            ModelConfiguration(
                provider="claude",
                model_name="claude-3-haiku-20240307",
                display_name="Claude 3 Haiku",
                category=ModelCategory.CONVERSATION,
                size=ModelSize.MEDIUM,
                status=ModelStatus.ACTIVE,
                cost_per_1k_tokens=0.008,
                avg_response_time_ms=1200,
                quality_score=0.9,
                reliability_score=0.95,
                supported_languages=[
                    "en",
                    "es",
                    "fr",
                    "de",
                    "it",
                    "pt",
                    "ja",
                    "ko",
                    "zh",
                ],
                primary_languages=["en", "es", "fr"],
                max_tokens=4096,
                context_window=200000,
                supports_streaming=True,
                supports_functions=True,
                temperature=0.7,
                priority=1,
                weight=1.0,
            ),
            ModelConfiguration(
                provider="mistral",
                model_name="mistral-small-latest",
                display_name="Mistral Small",
                category=ModelCategory.CONVERSATION,
                size=ModelSize.SMALL,
                status=ModelStatus.ACTIVE,
                cost_per_1k_tokens=0.0007,
                avg_response_time_ms=800,
                quality_score=0.75,
                reliability_score=0.88,
                supported_languages=["en", "fr", "es", "de", "it"],
                primary_languages=["fr", "en"],
                max_tokens=2048,
                context_window=32000,
                supports_streaming=True,
                supports_functions=False,
                temperature=0.7,
                priority=2,
                weight=0.8,
            ),
            ModelConfiguration(
                provider="deepseek",
                model_name="deepseek-chat",
                display_name="DeepSeek Chat",
                category=ModelCategory.CONVERSATION,
                size=ModelSize.LARGE,
                status=ModelStatus.ACTIVE,
                cost_per_1k_tokens=0.0001,
                avg_response_time_ms=1500,
                quality_score=0.8,
                reliability_score=0.85,
                supported_languages=["zh", "zh-cn", "zh-tw", "en"],
                primary_languages=["zh", "zh-cn"],
                max_tokens=4096,
                context_window=64000,
                supports_streaming=True,
                supports_functions=True,
                temperature=0.7,
                priority=1,
                weight=1.0,
            ),
            ModelConfiguration(
                provider="ollama",
                model_name="llama2:7b",
                display_name="Llama 2 7B (Local)",
                category=ModelCategory.GENERAL,
                size=ModelSize.MEDIUM,
                status=ModelStatus.ACTIVE,
                cost_per_1k_tokens=0.0,
                avg_response_time_ms=3000,
                quality_score=0.65,
                reliability_score=0.9,
                supported_languages=["en", "es", "fr", "de"],
                primary_languages=["en"],
                max_tokens=2048,
                context_window=4096,
                supports_streaming=True,
                supports_functions=False,
                temperature=0.7,
                priority=5,
                weight=0.3,
            ),
            ModelConfiguration(
                provider="ollama",
                model_name="mistral:7b",
                display_name="Mistral 7B (Local)",
                category=ModelCategory.CONVERSATION,
                size=ModelSize.MEDIUM,
                status=ModelStatus.ACTIVE,
                cost_per_1k_tokens=0.0,
                avg_response_time_ms=2800,
                quality_score=0.7,
                reliability_score=0.92,
                supported_languages=["en", "fr", "es", "de", "it"],
                primary_languages=["en", "fr"],
                max_tokens=2048,
                context_window=8192,
                supports_streaming=True,
                supports_functions=False,
                temperature=0.7,
                priority=4,
                weight=0.5,
            ),
        ]

        # Load models into memory and database
        for model in default_models:
            model_id = f"{model.provider}_{model.model_name}"
            self.models[model_id] = model
            self._save_model_to_db(model_id, model)

            # Initialize usage stats
            if model_id not in self.usage_stats:
                self.usage_stats[model_id] = ModelUsageStats(
                    model_id=model_id,
                    provider=model.provider,
                    model_name=model.model_name,
                    first_used=datetime.now(),
                )
                self._save_usage_stats_to_db(model_id, self.usage_stats[model_id])

    def _save_model_to_db(self, model_id: str, model: ModelConfiguration):
        """Save model configuration to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO model_configurations VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """,
                (
                    model_id,
                    model.provider,
                    model.model_name,
                    model.display_name,
                    model.category.value,
                    model.size.value,
                    model.status.value,
                    model.cost_per_1k_tokens,
                    model.avg_response_time_ms,
                    model.quality_score,
                    model.reliability_score,
                    json.dumps(model.supported_languages),
                    json.dumps(model.primary_languages),
                    model.max_tokens,
                    model.context_window,
                    model.supports_streaming,
                    model.supports_functions,
                    model.temperature,
                    model.top_p,
                    model.frequency_penalty,
                    model.presence_penalty,
                    model.enabled,
                    model.priority,
                    model.weight,
                    model.created_at,
                    model.updated_at,
                    model.last_used,
                ),
            )

    def _save_usage_stats_to_db(self, model_id: str, stats: ModelUsageStats):
        """Save usage statistics to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO model_usage_stats VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """,
                (
                    model_id,
                    stats.provider,
                    stats.model_name,
                    stats.total_requests,
                    stats.successful_requests,
                    stats.failed_requests,
                    stats.total_tokens,
                    stats.total_cost,
                    stats.avg_response_time,
                    stats.min_response_time,
                    stats.max_response_time,
                    stats.avg_quality_rating,
                    stats.user_satisfaction,
                    stats.last_24h_requests,
                    stats.last_7d_requests,
                    stats.last_30d_requests,
                    stats.first_used,
                    stats.last_used,
                ),
            )

    async def get_all_models(
        self, category: Optional[str] = None, enabled_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all model configurations"""
        models = []

        for model_id, model in self.models.items():
            if category and model.category.value != category:
                continue
            if enabled_only and not model.enabled:
                continue

            # Get usage stats
            stats = self.usage_stats.get(
                model_id,
                ModelUsageStats(
                    model_id=model_id,
                    provider=model.provider,
                    model_name=model.model_name,
                ),
            )

            model_data = {
                "id": model_id,
                "provider": model.provider,
                "model_name": model.model_name,
                "display_name": model.display_name,
                "category": model.category.value,
                "size": model.size.value,
                "status": model.status.value,
                "cost_per_1k_tokens": model.cost_per_1k_tokens,
                "avg_response_time_ms": model.avg_response_time_ms,
                "quality_score": model.quality_score,
                "reliability_score": model.reliability_score,
                "supported_languages": model.supported_languages,
                "primary_languages": model.primary_languages,
                "max_tokens": model.max_tokens,
                "context_window": model.context_window,
                "supports_streaming": model.supports_streaming,
                "supports_functions": model.supports_functions,
                "temperature": model.temperature,
                "top_p": model.top_p,
                "frequency_penalty": model.frequency_penalty,
                "presence_penalty": model.presence_penalty,
                "enabled": model.enabled,
                "priority": model.priority,
                "weight": model.weight,
                "usage_stats": {
                    "total_requests": stats.total_requests,
                    "success_rate": stats.successful_requests
                    / max(stats.total_requests, 1),
                    "total_cost": stats.total_cost,
                    "avg_response_time": stats.avg_response_time,
                    "last_used": stats.last_used.isoformat()
                    if stats.last_used
                    else None,
                },
                "created_at": model.created_at.isoformat()
                if model.created_at
                else None,
                "updated_at": model.updated_at.isoformat()
                if model.updated_at
                else None,
            }

            models.append(model_data)

        # Sort by priority, then by quality score
        models.sort(key=lambda x: (x["priority"], -x["quality_score"]))
        return models

    async def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get specific model configuration"""
        models = await self.get_all_models()
        return next((m for m in models if m["id"] == model_id), None)

    async def update_model(self, model_id: str, updates: Dict[str, Any]) -> bool:
        """Update model configuration"""
        if model_id not in self.models:
            return False

        model = self.models[model_id]

        # Update allowed fields
        updateable_fields = {
            "display_name",
            "status",
            "cost_per_1k_tokens",
            "quality_score",
            "reliability_score",
            "enabled",
            "priority",
            "weight",
            "temperature",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
        }

        for field, value in updates.items():
            if field in updateable_fields:
                if field == "status":
                    model.status = ModelStatus(value)
                elif hasattr(model, field):
                    setattr(model, field, value)

        model.updated_at = datetime.now()
        self._save_model_to_db(model_id, model)

        # Clear performance cache
        self.performance_cache.clear()

        return True

    async def enable_model(self, model_id: str) -> bool:
        """Enable a model"""
        return await self.update_model(model_id, {"enabled": True})

    async def disable_model(self, model_id: str) -> bool:
        """Disable a model"""
        return await self.update_model(model_id, {"enabled": False})

    async def set_model_priority(self, model_id: str, priority: int) -> bool:
        """Set model priority (1 = highest, 10 = lowest)"""
        if not 1 <= priority <= 10:
            return False
        return await self.update_model(model_id, {"priority": priority})

    async def track_model_usage(
        self,
        model_id: str,
        response_time_ms: float,
        tokens_used: int,
        cost: float,
        success: bool = True,
        quality_rating: float = None,
    ):
        """Track model usage for analytics"""
        if model_id not in self.usage_stats:
            return

        with self._lock:
            stats = self.usage_stats[model_id]

            # Update basic metrics
            stats.total_requests += 1
            if success:
                stats.successful_requests += 1
            else:
                stats.failed_requests += 1

            stats.total_tokens += tokens_used
            stats.total_cost += cost
            stats.last_used = datetime.now()

            # Update response time metrics
            if stats.total_requests == 1:
                stats.avg_response_time = response_time_ms
                stats.min_response_time = response_time_ms
                stats.max_response_time = response_time_ms
            else:
                stats.avg_response_time = (
                    stats.avg_response_time * (stats.total_requests - 1)
                    + response_time_ms
                ) / stats.total_requests
                stats.min_response_time = min(stats.min_response_time, response_time_ms)
                stats.max_response_time = max(stats.max_response_time, response_time_ms)

            # Update quality rating
            if quality_rating is not None:
                if stats.avg_quality_rating == 0:
                    stats.avg_quality_rating = quality_rating
                else:
                    # Weighted average with more weight on recent ratings
                    stats.avg_quality_rating = (
                        stats.avg_quality_rating * 0.8 + quality_rating * 0.2
                    )

            # Save to database
            self._save_usage_stats_to_db(model_id, stats)

            # Log performance data
            self._log_performance(
                model_id, response_time_ms, tokens_used, cost, quality_rating
            )

    def _log_performance(
        self,
        model_id: str,
        response_time_ms: float,
        tokens_used: int,
        cost: float,
        quality_rating: float = None,
    ):
        """Log detailed performance data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO model_performance_logs
                (model_id, response_time_ms, tokens_used, cost, quality_rating)
                VALUES (?, ?, ?, ?, ?)
            """,
                (model_id, response_time_ms, tokens_used, cost, quality_rating),
            )

    async def get_model_performance_report(
        self, model_id: str, days: int = 30
    ) -> Optional[ModelPerformanceReport]:
        """Generate comprehensive performance report for a model"""
        if model_id not in self.models:
            return None

        # Fetch performance data
        perf_data = self._fetch_performance_data(model_id, days)
        if not perf_data:
            return None

        model = self.models[model_id]
        stats = self.usage_stats.get(model_id)

        # Calculate metrics
        efficiency = self._calculate_efficiency_metrics(model, perf_data)
        rankings = await self._calculate_model_rankings(model_id)
        recommendations = self._generate_model_recommendations(model)
        suggestions = self._generate_optimization_suggestions(model, stats)

        return ModelPerformanceReport(
            model_id=model_id,
            report_date=datetime.now(),
            cost_efficiency=efficiency["cost"],
            speed_efficiency=efficiency["speed"],
            reliability_score=model.reliability_score,
            rank_by_cost=rankings["cost"],
            rank_by_speed=rankings["speed"],
            rank_by_quality=rankings["quality"],
            rank_overall=rankings["overall"],
            recommended_for=recommendations,
            optimization_suggestions=suggestions,
            performance_trend="stable",
            usage_trend="stable",
        )

    def _fetch_performance_data(self, model_id: str, days: int) -> Optional[tuple]:
        """Fetch performance data from database"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total_requests,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(quality_rating) as avg_quality,
                    AVG(cost) as avg_cost,
                    SUM(tokens_used) as total_tokens
                FROM model_performance_logs
                WHERE model_id = ? AND timestamp >= ?
            """,
                (model_id, start_date),
            )
            perf_data = cursor.fetchone()

        if not perf_data or perf_data[0] == 0:
            return None
        return perf_data

    def _calculate_efficiency_metrics(
        self, model, perf_data: tuple
    ) -> Dict[str, float]:
        """Calculate cost and speed efficiency metrics"""
        avg_quality = perf_data[2] or model.quality_score
        avg_cost = perf_data[3] or model.cost_per_1k_tokens
        avg_response_time = perf_data[1] or model.avg_response_time_ms

        cost_efficiency = avg_quality / max(avg_cost, 0.0001)
        speed_efficiency = avg_quality / max(avg_response_time / 1000, 0.1)

        return {"cost": cost_efficiency, "speed": speed_efficiency}

    async def _calculate_model_rankings(self, model_id: str) -> Dict[str, int]:
        """Calculate model rankings across different metrics"""
        all_models = await self.get_all_models(enabled_only=True)

        cost_ranked = sorted(all_models, key=lambda x: x["cost_per_1k_tokens"])
        speed_ranked = sorted(all_models, key=lambda x: x["avg_response_time_ms"])
        quality_ranked = sorted(
            all_models, key=lambda x: x["quality_score"], reverse=True
        )

        rank_by_cost = next(
            (i + 1 for i, m in enumerate(cost_ranked) if m["id"] == model_id), 999
        )
        rank_by_speed = next(
            (i + 1 for i, m in enumerate(speed_ranked) if m["id"] == model_id), 999
        )
        rank_by_quality = next(
            (i + 1 for i, m in enumerate(quality_ranked) if m["id"] == model_id), 999
        )
        rank_overall = int((rank_by_cost + rank_by_speed + rank_by_quality * 2) / 4)

        return {
            "cost": rank_by_cost,
            "speed": rank_by_speed,
            "quality": rank_by_quality,
            "overall": rank_overall,
        }

    def _generate_model_recommendations(self, model) -> List[str]:
        """Generate use case recommendations for model"""
        recommendations = []

        if model.category == ModelCategory.CONVERSATION:
            recommendations.extend(["conversation", "chat"])
        if model.cost_per_1k_tokens < 0.001:
            recommendations.append("high_volume")
        if model.quality_score > 0.8:
            recommendations.append("complex_tasks")
        if "zh" in model.primary_languages:
            recommendations.append("chinese_language")
        if "fr" in model.primary_languages:
            recommendations.append("french_language")

        return recommendations

    def _generate_optimization_suggestions(self, model, stats) -> List[str]:
        """Generate optimization suggestions for model"""
        suggestions = []

        if model.cost_per_1k_tokens > 0.01:
            suggestions.append("Consider for cost-sensitive workloads")
        if model.avg_response_time_ms > 2000:
            suggestions.append("Monitor response time for time-critical applications")
        if stats and stats.total_requests > 100:
            success_rate = stats.successful_requests / stats.total_requests
            if success_rate < 0.95:
                suggestions.append("Investigate reliability issues")

        return suggestions

    async def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        models = await self.get_all_models()

        # Calculate totals
        total_models = len(models)
        active_models = len(
            [m for m in models if m["status"] == "active" and m["enabled"]]
        )
        total_requests = sum(m["usage_stats"]["total_requests"] for m in models)
        total_cost = sum(m["usage_stats"]["total_cost"] for m in models)

        # Get budget status
        budget_status = budget_manager.get_current_budget_status()

        # Provider breakdown
        providers = {}
        for model in models:
            provider = model["provider"]
            if provider not in providers:
                providers[provider] = {
                    "models": 0,
                    "active_models": 0,
                    "total_requests": 0,
                    "total_cost": 0.0,
                }

            providers[provider]["models"] += 1
            if model["status"] == "active" and model["enabled"]:
                providers[provider]["active_models"] += 1
            providers[provider]["total_requests"] += model["usage_stats"][
                "total_requests"
            ]
            providers[provider]["total_cost"] += model["usage_stats"]["total_cost"]

        # Top performing models
        top_models = sorted(
            models,
            key=lambda x: (x["usage_stats"]["total_requests"], x["quality_score"]),
            reverse=True,
        )[:5]

        return {
            "overview": {
                "total_models": total_models,
                "active_models": active_models,
                "total_requests": total_requests,
                "total_cost": round(total_cost, 4),
                "avg_cost_per_request": round(total_cost / max(total_requests, 1), 6),
            },
            "budget_status": {
                "remaining_budget": budget_status.remaining_budget,
                "percentage_used": budget_status.percentage_used,
                "alert_level": budget_status.alert_level.value
                if budget_status.alert_level
                else "green",
            },
            "providers": providers,
            "top_models": [
                {
                    "id": m["id"],
                    "display_name": m["display_name"],
                    "provider": m["provider"],
                    "total_requests": m["usage_stats"]["total_requests"],
                    "quality_score": m["quality_score"],
                }
                for m in top_models
            ],
            "categories": {
                category.value: len(
                    [m for m in models if m["category"] == category.value]
                )
                for category in ModelCategory
            },
        }

    async def optimize_model_selection(
        self,
        language: str = "en",
        use_case: str = "conversation",
        budget_limit: float = None,
    ) -> List[str]:
        """Get optimized model recommendations for specific use case"""
        models = await self.get_all_models(enabled_only=True)

        suitable_models = self._filter_suitable_models(models, language, budget_limit)
        scored_models = self._score_models(suitable_models, language, use_case)

        return self._select_top_models(scored_models, limit=5)

    def _filter_suitable_models(
        self, models: List[Dict], language: str, budget_limit: Optional[float]
    ) -> List[Dict]:
        """Filter models by language support and budget constraints"""
        suitable = [
            m
            for m in models
            if language in m["supported_languages"]
            or language in m["primary_languages"]
        ]

        if budget_limit:
            suitable = [m for m in suitable if m["cost_per_1k_tokens"] <= budget_limit]

        return suitable

    def _score_models(
        self, models: List[Dict], language: str, use_case: str
    ) -> List[Dict]:
        """Calculate optimization score for each model"""
        for model in models:
            score = self._calculate_model_score(model, language, use_case)
            model["optimization_score"] = score

        return models

    def _calculate_model_score(
        self, model: Dict, language: str, use_case: str
    ) -> float:
        """Calculate comprehensive optimization score for a model"""
        score = 0.0

        score += self._get_quality_score(model)
        score += self._get_reliability_score(model)
        score += self._get_language_match_score(model, language)
        score += self._get_cost_efficiency_score(model)
        score += self._get_speed_score(model)
        score += self._get_category_match_score(model, use_case)
        score += self._get_priority_score(model)

        return score

    def _get_quality_score(self, model: Dict) -> float:
        """Get base quality score contribution"""
        return model["quality_score"] * 40

    def _get_reliability_score(self, model: Dict) -> float:
        """Get reliability score contribution"""
        return model["reliability_score"] * 20

    def _get_language_match_score(self, model: Dict, language: str) -> float:
        """Get language match bonus score"""
        if language in model["primary_languages"]:
            return 15
        elif language in model["supported_languages"]:
            return 10
        return 0

    def _get_cost_efficiency_score(self, model: Dict) -> float:
        """Get cost efficiency score (lower cost = higher score)"""
        return max(0, 20 - (model["cost_per_1k_tokens"] * 1000))

    def _get_speed_score(self, model: Dict) -> float:
        """Get speed score (lower response time = higher score)"""
        return max(0, 10 - (model["avg_response_time_ms"] / 500))

    def _get_category_match_score(self, model: Dict, use_case: str) -> float:
        """Get category match bonus score"""
        if use_case == model["category"]:
            return 10
        return 0

    def _get_priority_score(self, model: Dict) -> float:
        """Get priority bonus score (lower priority number = higher score)"""
        return 11 - model["priority"]

    def _select_top_models(self, models: List[Dict], limit: int = 5) -> List[str]:
        """Sort by score and return top model IDs"""
        sorted_models = sorted(
            models, key=lambda x: x["optimization_score"], reverse=True
        )
        return [m["id"] for m in sorted_models[:limit]]

    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all models and providers"""
        router_status = await ai_router.get_router_status()
        models = await self.get_all_models()

        # Check each provider health
        provider_health = {}
        for provider_name in ["claude", "mistral", "deepseek", "ollama"]:
            health = await ai_router.check_provider_health(provider_name)
            provider_health[provider_name] = {
                "status": health.get("status", "unknown"),
                "available": health.get("available", False),
                "models": len([m for m in models if m["provider"] == provider_name]),
            }

        return {
            "system_health": "healthy"
            if len([p for p in provider_health.values() if p["available"]]) > 0
            else "degraded",
            "providers": provider_health,
            "router_status": router_status.get("router_mode", "unknown"),
            "fallback_available": router_status.get("fallback_status", {}).get(
                "ollama_available", False
            ),
            "budget_status": router_status.get("budget_status", {}),
            "total_models": len(models),
            "active_models": len(
                [m for m in models if m["enabled"] and m["status"] == "active"]
            ),
        }


# Global instance
ai_model_manager = AIModelManager()
