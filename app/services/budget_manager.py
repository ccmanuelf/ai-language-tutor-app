"""
Budget Management and Cost Tracking System for AI Language Tutor App

This module manages the $30/month budget constraint by:
- Tracking real-time API costs across all providers
- Implementing intelligent fallback mechanisms
- Providing cost alerts and budget enforcement
- Optimizing provider selection based on cost
- Generating detailed cost reports and analytics
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import func

from app.core.config import get_settings
from app.database.config import get_primary_db_session
from app.models.database import APIUsage, User

logger = logging.getLogger(__name__)


class BudgetAlert(Enum):
    """Budget alert levels"""

    GREEN = "green"  # 0-50% of budget used
    YELLOW = "yellow"  # 50-75% of budget used
    ORANGE = "orange"  # 75-90% of budget used
    RED = "red"  # 90-100% of budget used
    CRITICAL = "critical"  # >100% of budget used


class CostOptimizationStrategy(Enum):
    """Cost optimization strategies"""

    CHEAPEST_FIRST = "cheapest_first"
    BALANCED = "balanced"
    QUALITY_FIRST = "quality_first"
    EMERGENCY_ONLY = "emergency_only"


@dataclass
class BudgetStatus:
    """Current budget status"""

    total_budget: float
    used_budget: float
    remaining_budget: float
    percentage_used: float
    alert_level: BudgetAlert
    days_remaining: int
    projected_monthly_cost: float
    is_over_budget: bool


@dataclass
class CostEstimate:
    """Cost estimate for API operations"""

    estimated_cost: float
    provider: str
    service_type: str
    tokens_estimated: int
    confidence: float


class BudgetManager:
    """Manages budget constraints and cost optimization"""

    def __init__(self):
        self.settings = get_settings()
        self.monthly_budget = float(self.settings.MONTHLY_BUDGET_USD)  # $30/month
        self.alert_thresholds = {
            BudgetAlert.YELLOW: 0.50,  # 50%
            BudgetAlert.ORANGE: 0.75,  # 75%
            BudgetAlert.RED: 0.90,  # 90%
            BudgetAlert.CRITICAL: 1.00,  # 100%
        }

        # Provider cost per 1K tokens (USD) - estimated rates
        self.provider_costs = {
            "anthropic": {
                "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
                "claude-3-sonnet": {"input": 0.003, "output": 0.015},
                "claude-3-opus": {"input": 0.015, "output": 0.075},
            },
            "mistral": {
                "mistral-tiny": {"input": 0.00014, "output": 0.00042},
                "mistral-small": {"input": 0.0006, "output": 0.0018},
                "mistral-medium": {"input": 0.0027, "output": 0.0081},
            },
        }

    def get_current_budget_status(self, user_id: str = None) -> BudgetStatus:
        """
        Get current budget status for the user

        Args:
            user_id: Optional user ID. If None, uses global budget.

        Returns:
            BudgetStatus with current usage and limits
        """
        session = get_primary_db_session()
        try:
            # Import here to avoid circular dependency
            from app.models.budget import UserBudgetSettings

            # Get user-specific budget settings if user_id provided
            if user_id:
                user_settings = (
                    session.query(UserBudgetSettings)
                    .filter(UserBudgetSettings.user_id == user_id)
                    .first()
                )

                if user_settings:
                    # Use per-user budget settings
                    budget_limit = user_settings.get_effective_limit()
                    period_start = user_settings.current_period_start
                    period_end = user_settings.current_period_end

                    # Calculate total costs for current period
                    total_cost = (
                        session.query(func.sum(APIUsage.estimated_cost))
                        .filter(
                            APIUsage.user_id == user_id,
                            APIUsage.created_at >= period_start,
                        )
                        .scalar()
                        or 0.0
                    )

                    # Calculate remaining budget
                    remaining = max(0, budget_limit - total_cost)
                    percentage_used = (
                        (total_cost / budget_limit * 100) if budget_limit > 0 else 0
                    )

                    # Determine alert level using user's custom thresholds
                    if percentage_used >= 100:
                        alert_level = BudgetAlert.CRITICAL
                    elif percentage_used >= user_settings.alert_threshold_red:
                        alert_level = BudgetAlert.RED
                    elif percentage_used >= user_settings.alert_threshold_orange:
                        alert_level = BudgetAlert.ORANGE
                    elif percentage_used >= user_settings.alert_threshold_yellow:
                        alert_level = BudgetAlert.YELLOW
                    else:
                        alert_level = BudgetAlert.GREEN

                    # Calculate days remaining in period
                    now = datetime.now()
                    days_remaining = 0
                    if period_end:
                        days_remaining = max(0, (period_end - now).days)

                    # Project period cost
                    days_elapsed = (now - period_start).days + 1
                    daily_average = total_cost / days_elapsed if days_elapsed > 0 else 0

                    # Calculate projection based on period type
                    if user_settings.budget_period.value == "monthly":
                        projected_cost = daily_average * 30
                    elif user_settings.budget_period.value == "weekly":
                        projected_cost = daily_average * 7
                    elif user_settings.budget_period.value == "daily":
                        projected_cost = total_cost
                    elif (
                        user_settings.budget_period.value == "custom"
                        and user_settings.custom_period_days
                    ):
                        projected_cost = (
                            daily_average * user_settings.custom_period_days
                        )
                    else:
                        projected_cost = daily_average * 30

                    return BudgetStatus(
                        total_budget=budget_limit,
                        used_budget=total_cost,
                        remaining_budget=remaining,
                        percentage_used=percentage_used,
                        alert_level=alert_level,
                        days_remaining=days_remaining,
                        projected_monthly_cost=projected_cost,
                        is_over_budget=total_cost > budget_limit,
                    )

            # Fallback to global budget (legacy behavior)
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # Calculate total costs for current month (all users if no user_id)
            query = session.query(func.sum(APIUsage.estimated_cost)).filter(
                APIUsage.created_at >= month_start
            )
            if user_id:
                query = query.filter(APIUsage.user_id == user_id)

            total_cost = query.scalar() or 0.0

            # Calculate remaining budget
            remaining = max(0, self.monthly_budget - total_cost)
            percentage_used = (total_cost / self.monthly_budget) * 100

            # Determine alert level
            alert_level = self._determine_alert_level(percentage_used / 100)

            # Calculate days remaining in month
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month + 1, day=1)
            days_remaining = (next_month - now).days

            # Project monthly cost
            days_elapsed = (now - month_start).days + 1
            daily_average = total_cost / days_elapsed if days_elapsed > 0 else 0
            projected_monthly = daily_average * 30

            return BudgetStatus(
                total_budget=self.monthly_budget,
                used_budget=total_cost,
                remaining_budget=remaining,
                percentage_used=percentage_used,
                alert_level=alert_level,
                days_remaining=days_remaining,
                projected_monthly_cost=projected_monthly,
                is_over_budget=total_cost > self.monthly_budget,
            )

        except Exception as e:
            logger.error(f"Error getting budget status: {e}")
            return BudgetStatus(
                total_budget=self.monthly_budget,
                used_budget=0.0,
                remaining_budget=self.monthly_budget,
                percentage_used=0.0,
                alert_level=BudgetAlert.GREEN,
                days_remaining=30,
                projected_monthly_cost=0.0,
                is_over_budget=False,
            )
        finally:
            session.close()

    def _determine_alert_level(self, percentage_used: float) -> BudgetAlert:
        """Determine alert level based on budget usage"""
        if percentage_used >= 1.0:
            return BudgetAlert.CRITICAL
        elif percentage_used >= self.alert_thresholds[BudgetAlert.RED]:
            return BudgetAlert.RED
        elif percentage_used >= self.alert_thresholds[BudgetAlert.ORANGE]:
            return BudgetAlert.ORANGE
        elif percentage_used >= self.alert_thresholds[BudgetAlert.YELLOW]:
            return BudgetAlert.YELLOW
        else:
            return BudgetAlert.GREEN

    def estimate_cost(
        self,
        provider: str,
        model: str,
        service_type: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        audio_minutes: float = 0,
        characters: int = 0,
    ) -> CostEstimate:
        """
        Estimate cost for an API operation

        Args:
            provider: AI provider name
            model: Model name
            service_type: Type of service (llm, stt, tts)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            audio_minutes: Minutes of audio (for STT)
            characters: Number of characters (for TTS)

        Returns:
            Cost estimate
        """
        try:
            cost, confidence = self._calculate_cost_from_pricing(
                provider,
                model,
                service_type,
                input_tokens,
                output_tokens,
                audio_minutes,
                characters,
            )

            return CostEstimate(
                estimated_cost=cost,
                provider=provider,
                service_type=service_type,
                tokens_estimated=input_tokens + output_tokens,
                confidence=confidence,
            )

        except Exception as e:
            logger.error(f"Error estimating cost: {e}")
            return self._build_fallback_estimate(
                provider, service_type, input_tokens, output_tokens
            )

    def _calculate_cost_from_pricing(
        self,
        provider: str,
        model: str,
        service_type: str,
        input_tokens: int,
        output_tokens: int,
        audio_minutes: float,
        characters: int,
    ) -> tuple:
        """Calculate cost from provider pricing data"""
        if provider not in self.provider_costs:
            return self._use_fallback_pricing(
                service_type, input_tokens, output_tokens, audio_minutes, characters
            )

        provider_pricing = self.provider_costs[provider]
        if model not in provider_pricing:
            return self._use_fallback_pricing(
                service_type, input_tokens, output_tokens, audio_minutes, characters
            )

        model_pricing = provider_pricing[model]
        return self._calculate_service_cost(
            service_type,
            model_pricing,
            input_tokens,
            output_tokens,
            audio_minutes,
            characters,
        )

    def _calculate_service_cost(
        self,
        service_type: str,
        pricing: dict,
        input_tokens: int,
        output_tokens: int,
        audio_minutes: float,
        characters: int,
    ) -> tuple:
        """Calculate cost for specific service type"""
        if service_type == "llm":
            return self._calculate_llm_cost(pricing, input_tokens, output_tokens)
        elif service_type == "stt":
            return self._calculate_stt_cost(pricing, audio_minutes)
        elif service_type == "tts":
            return self._calculate_tts_cost(pricing, characters)
        else:
            return 0.0, 0.5

    def _calculate_llm_cost(
        self, pricing: dict, input_tokens: int, output_tokens: int
    ) -> tuple:
        """Calculate cost for LLM service"""
        cost = 0.0
        if "input" in pricing and input_tokens > 0:
            cost += (input_tokens / 1000) * pricing["input"]
        if "output" in pricing and output_tokens > 0:
            cost += (output_tokens / 1000) * pricing["output"]
        return cost, 0.9 if cost > 0 else 0.5

    def _calculate_stt_cost(self, pricing: dict, audio_minutes: float) -> tuple:
        """Calculate cost for STT service"""
        if "per_minute" in pricing:
            return audio_minutes * pricing["per_minute"], 0.85
        return 0.0, 0.5

    def _calculate_tts_cost(self, pricing: dict, characters: int) -> tuple:
        """Calculate cost for TTS service"""
        if "per_character" in pricing:
            return characters * pricing["per_character"], 0.85
        return 0.0, 0.5

    def _use_fallback_pricing(
        self,
        service_type: str,
        input_tokens: int,
        output_tokens: int,
        audio_minutes: float,
        characters: int,
    ) -> tuple:
        """Use fallback pricing when specific pricing unavailable"""
        cost = self._fallback_cost_estimate(
            service_type, input_tokens, output_tokens, audio_minutes, characters
        )
        return cost, 0.5

    def _build_fallback_estimate(
        self, provider: str, service_type: str, input_tokens: int, output_tokens: int
    ) -> CostEstimate:
        """Build conservative fallback cost estimate"""
        return CostEstimate(
            estimated_cost=0.01,
            provider=provider,
            service_type=service_type,
            tokens_estimated=input_tokens + output_tokens,
            confidence=0.1,
        )

    def _fallback_cost_estimate(
        self,
        service_type: str,
        input_tokens: int,
        output_tokens: int,
        audio_minutes: float,
        characters: int,
    ) -> float:
        """Fallback cost estimation when specific pricing unavailable"""
        if service_type == "llm":
            # Conservative estimate: $0.002 per 1K tokens
            return ((input_tokens + output_tokens) / 1000) * 0.002
        elif service_type == "stt":
            # Conservative estimate: $0.025 per minute
            return audio_minutes * 0.025
        elif service_type == "tts":
            # Conservative estimate: $0.025 per 1K characters
            return (characters / 1000) * 0.025
        else:
            return 0.01  # Minimal fallback

    def can_afford_operation(
        self, estimated_cost: float, buffer_percentage: float = 0.1
    ) -> bool:
        """
        Check if we can afford an operation given current budget status

        Args:
            estimated_cost: Estimated cost of the operation
            buffer_percentage: Safety buffer (10% by default)

        Returns:
            True if operation is affordable
        """
        budget_status = self.get_current_budget_status()

        # Add buffer to cost estimate
        cost_with_buffer = estimated_cost * (1 + buffer_percentage)

        # Check if we have enough remaining budget
        affordable = budget_status.remaining_budget >= cost_with_buffer

        # Additional checks for budget alerts
        if budget_status.alert_level == BudgetAlert.CRITICAL:
            # Only allow very small costs when over budget
            affordable = affordable and estimated_cost < 0.01
        elif budget_status.alert_level == BudgetAlert.RED:
            # Be more conservative when near budget limit
            affordable = affordable and estimated_cost < 0.05

        return affordable

    def record_api_usage(
        self,
        user_id: Optional[str],
        provider: str,
        endpoint: str,
        request_type: str,
        tokens_used: int = 0,
        estimated_cost: float = 0.0,
        actual_cost: Optional[float] = None,
        status: str = "success",
        metadata: Optional[Dict] = None,
    ) -> bool:
        """
        Record API usage for cost tracking

        Args:
            user_id: User ID (if applicable)
            provider: API provider name
            endpoint: API endpoint used
            request_type: Type of request
            tokens_used: Number of tokens consumed
            estimated_cost: Estimated cost
            actual_cost: Actual cost (if known)
            status: Request status
            metadata: Additional metadata

        Returns:
            Success status
        """
        session = get_primary_db_session()
        try:
            # Get user database ID if user_id provided
            db_user_id = None
            if user_id:
                user = session.query(User).filter(User.user_id == user_id).first()
                if user:
                    db_user_id = user.id

            # Create API usage record
            usage = APIUsage(
                user_id=db_user_id,
                api_provider=provider,
                api_endpoint=endpoint,
                request_type=request_type,
                tokens_used=tokens_used,
                estimated_cost=estimated_cost,
                actual_cost=actual_cost,
                status=status,
                request_metadata=metadata or {},
                response_metadata={},
            )

            session.add(usage)
            session.commit()

            logger.info(
                f"Recorded API usage: {provider}/{endpoint} - ${estimated_cost:.4f}"
            )
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error recording API usage: {e}")
            return False
        finally:
            session.close()

    def get_cost_breakdown(self, days: int = 30) -> Dict[str, Any]:
        """
        Get detailed cost breakdown for analysis

        Args:
            days: Number of days to analyze

        Returns:
            Cost breakdown data
        """
        session = get_primary_db_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            # Total costs by provider
            provider_costs = (
                session.query(
                    APIUsage.api_provider,
                    func.sum(APIUsage.estimated_cost).label("total_cost"),
                    func.count(APIUsage.id).label("request_count"),
                    func.sum(APIUsage.tokens_used).label("total_tokens"),
                )
                .filter(APIUsage.created_at >= cutoff_date)
                .group_by(APIUsage.api_provider)
                .all()
            )

            # Daily costs
            daily_costs = (
                session.query(
                    func.date(APIUsage.created_at).label("date"),
                    func.sum(APIUsage.estimated_cost).label("daily_cost"),
                )
                .filter(APIUsage.created_at >= cutoff_date)
                .group_by(func.date(APIUsage.created_at))
                .all()
            )

            # Request type breakdown
            request_type_costs = (
                session.query(
                    APIUsage.request_type,
                    func.sum(APIUsage.estimated_cost).label("total_cost"),
                    func.count(APIUsage.id).label("request_count"),
                )
                .filter(APIUsage.created_at >= cutoff_date)
                .group_by(APIUsage.request_type)
                .all()
            )

            return {
                "period_days": days,
                "total_cost": sum(row.total_cost for row in provider_costs),
                "total_requests": sum(row.request_count for row in provider_costs),
                "total_tokens": sum(row.total_tokens or 0 for row in provider_costs),
                "provider_breakdown": [
                    {
                        "provider": row.api_provider,
                        "cost": float(row.total_cost),
                        "requests": row.request_count,
                        "tokens": row.total_tokens or 0,
                    }
                    for row in provider_costs
                ],
                "daily_costs": [
                    {"date": row.date.isoformat(), "cost": float(row.daily_cost)}
                    for row in daily_costs
                ],
                "request_type_breakdown": [
                    {
                        "type": row.request_type,
                        "cost": float(row.total_cost),
                        "requests": row.request_count,
                    }
                    for row in request_type_costs
                ],
            }

        except Exception as e:
            logger.error(f"Error getting cost breakdown: {e}")
            return {
                "period_days": days,
                "total_cost": 0.0,
                "total_requests": 0,
                "total_tokens": 0,
                "provider_breakdown": [],
                "daily_costs": [],
                "request_type_breakdown": [],
            }
        finally:
            session.close()

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations"""
        budget_status = self.get_current_budget_status()
        cost_breakdown = self.get_cost_breakdown(30)

        recommendations = []

        # Budget-based recommendations
        if budget_status.alert_level in [BudgetAlert.RED, BudgetAlert.CRITICAL]:
            recommendations.append(
                {
                    "type": "urgent",
                    "title": "Budget Alert",
                    "description": f"You've used {budget_status.percentage_used:.1f}% of your monthly budget",
                    "action": "Consider using cheaper models or reducing API calls",
                }
            )

        # Provider optimization
        provider_costs = {
            item["provider"]: item["cost"]
            for item in cost_breakdown["provider_breakdown"]
        }
        if provider_costs:
            most_expensive = max(provider_costs, key=provider_costs.get)
            recommendations.append(
                {
                    "type": "optimization",
                    "title": "Provider Optimization",
                    "description": f"{most_expensive} is your most expensive provider",
                    "action": "Consider using alternative providers for similar tasks",
                }
            )

        # Model recommendations
        if budget_status.projected_monthly_cost > self.monthly_budget * 1.1:
            recommendations.append(
                {
                    "type": "warning",
                    "title": "Budget Projection",
                    "description": f"Projected monthly cost: ${budget_status.projected_monthly_cost:.2f}",
                    "action": "Reduce usage or switch to cheaper models",
                }
            )

        return recommendations

    def get_recommended_strategy(
        self, budget_status: Optional[BudgetStatus] = None
    ) -> CostOptimizationStrategy:
        """Get recommended cost optimization strategy based on current budget"""
        if budget_status is None:
            budget_status = self.get_current_budget_status()

        if budget_status.alert_level == BudgetAlert.CRITICAL:
            return CostOptimizationStrategy.EMERGENCY_ONLY
        elif budget_status.alert_level == BudgetAlert.RED:
            return CostOptimizationStrategy.CHEAPEST_FIRST
        elif budget_status.alert_level == BudgetAlert.ORANGE:
            return CostOptimizationStrategy.BALANCED
        else:
            return CostOptimizationStrategy.QUALITY_FIRST

    async def check_budget_alerts(self) -> List[Dict[str, Any]]:
        """Check for budget alerts and return notifications (legacy format)"""
        budget_status = self.get_current_budget_status()
        alerts = []

        if budget_status.alert_level == BudgetAlert.CRITICAL:
            alerts.append(
                {
                    "level": "critical",
                    "title": "Budget Exceeded",
                    "message": f"You've exceeded your monthly budget by ${budget_status.used_budget - budget_status.total_budget:.2f}",
                    "action_required": True,
                }
            )

        elif budget_status.alert_level == BudgetAlert.RED:
            alerts.append(
                {
                    "level": "warning",
                    "title": "Budget Almost Exhausted",
                    "message": f"You've used {budget_status.percentage_used:.1f}% of your monthly budget",
                    "action_required": True,
                }
            )

        elif budget_status.alert_level == BudgetAlert.ORANGE:
            alerts.append(
                {
                    "level": "info",
                    "title": "Budget Watch",
                    "message": f"You've used {budget_status.percentage_used:.1f}% of your monthly budget",
                    "action_required": False,
                }
            )

        return alerts

    def check_budget_threshold_alerts(
        self, user_id: Optional[str] = None
    ) -> List["BudgetThresholdAlert"]:
        """
        Check if budget thresholds have been crossed and return structured alerts

        Args:
            user_id: Optional user ID for user-specific budget tracking

        Returns:
            List of BudgetThresholdAlert objects
        """
        from app.models.schemas import BudgetAlertSeverity, BudgetThresholdAlert

        budget_status = self.get_current_budget_status()
        alerts = []

        percentage = budget_status.percentage_used

        # 80% threshold - Warning
        if 80.0 <= percentage < 90.0:
            alerts.append(
                BudgetThresholdAlert.create(
                    budget_status=budget_status,
                    threshold=80.0,
                    severity=BudgetAlertSeverity.WARNING,
                )
            )

        # 90% threshold - Critical
        elif 90.0 <= percentage < 100.0:
            alerts.append(
                BudgetThresholdAlert.create(
                    budget_status=budget_status,
                    threshold=90.0,
                    severity=BudgetAlertSeverity.CRITICAL,
                )
            )

        # 100%+ threshold - Critical with overage
        elif percentage >= 100.0:
            alerts.append(
                BudgetThresholdAlert.create(
                    budget_status=budget_status,
                    threshold=100.0,
                    severity=BudgetAlertSeverity.CRITICAL,
                )
            )

        # Also check if approaching threshold (75-79%)
        elif 75.0 <= percentage < 80.0:
            alerts.append(
                BudgetThresholdAlert.create(
                    budget_status=budget_status,
                    threshold=75.0,
                    severity=BudgetAlertSeverity.INFO,
                )
            )

        return alerts

    def should_enforce_budget(
        self, user_id: str = None, user_preferences: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Determine if budget should be enforced based on user settings

        Args:
            user_id: Optional user ID to check per-user budget settings
            user_preferences: User's preference settings

        Returns:
            True if budget should be enforced
        """
        # Check per-user budget settings first
        if user_id:
            try:
                from app.models.budget import UserBudgetSettings

                session = get_primary_db_session()
                user_settings = (
                    session.query(UserBudgetSettings)
                    .filter(UserBudgetSettings.user_id == user_id)
                    .first()
                )
                session.close()

                if user_settings:
                    return user_settings.enforce_budget
            except Exception as e:
                logger.error(f"Error checking user budget settings: {e}")

        # Fallback to user preferences
        if not user_preferences:
            return True  # Default: enforce budget

        ai_settings = user_preferences.get("ai_provider_settings", {})
        return ai_settings.get("enforce_budget_limits", True)

    def can_override_budget(
        self, user_preferences: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if user is allowed to override budget limits

        Args:
            user_preferences: User's preference settings

        Returns:
            True if user can override budget
        """
        if not user_preferences:
            return True  # Default: allow override

        ai_settings = user_preferences.get("ai_provider_settings", {})
        return ai_settings.get("budget_override_allowed", True)

    def track_usage(
        self,
        provider: str,
        model: str,
        cost: float,
        tokens_used: int = 0,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Track API usage for budget monitoring

        Args:
            provider: API provider name
            model: Model name
            cost: Actual cost of the operation
            tokens_used: Number of tokens used
            user_id: Optional user ID

        Returns:
            Success status
        """
        try:
            return self.record_api_usage(
                user_id=user_id,
                provider=provider,
                endpoint=model,
                request_type="ai_generation",
                tokens_used=tokens_used,
                estimated_cost=cost,
                actual_cost=cost,
                status="success",
            )
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
            return False


# Global budget manager instance
budget_manager = BudgetManager()


# Convenience functions
def get_budget_status() -> BudgetStatus:
    """Get current budget status"""
    return budget_manager.get_current_budget_status()


def can_afford(estimated_cost: float) -> bool:
    """Check if operation is affordable"""
    return budget_manager.can_afford_operation(estimated_cost)


def record_usage(
    user_id: str,
    provider: str,
    endpoint: str,
    request_type: str,
    tokens: int = 0,
    cost: float = 0.0,
) -> bool:
    """Record API usage"""
    return budget_manager.record_api_usage(
        user_id, provider, endpoint, request_type, tokens, cost
    )


def estimate_cost(
    provider: str, model: str, service_type: str, **kwargs
) -> CostEstimate:
    """Estimate operation cost"""
    return budget_manager.estimate_cost(provider, model, service_type, **kwargs)
