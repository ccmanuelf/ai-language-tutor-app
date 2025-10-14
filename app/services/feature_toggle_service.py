"""
Feature Toggle Service
Manages dynamic feature control and user-specific access.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from app.models.feature_toggle import (
    FeatureToggle,
    FeatureToggleRequest,
    FeatureToggleUpdateRequest,
    FeatureToggleScope,
    FeatureToggleStatus,
    FeatureToggleCategory,
    UserFeatureAccess,
    FeatureToggleEvent,
    FeatureCondition,
)

logger = logging.getLogger(__name__)


class FeatureToggleService:
    """Service for managing feature toggles and user access control."""

    def __init__(self, storage_dir: str = "app/config/feature_toggles"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.features_file = self.storage_dir / "features.json"
        self.user_access_file = self.storage_dir / "user_access.json"
        self.events_file = self.storage_dir / "events.json"

        # In-memory caches
        self._features: Dict[str, FeatureToggle] = {}
        self._user_access: Dict[str, Dict[str, UserFeatureAccess]] = {}
        self._events: List[FeatureToggleEvent] = []

        # Cache for feature evaluation
        self._feature_cache: Dict[str, Dict[str, bool]] = {}
        self._cache_ttl = 300  # 5 minutes
        self._last_cache_clear = datetime.now()

        self._initialized = False

    async def initialize(self):
        """Initialize the feature toggle service."""
        if self._initialized:
            return

        logger.info("Initializing feature toggle service...")

        try:
            await self._load_features()
            await self._load_user_access()
            await self._load_events()
            await self._create_default_features()

            self._initialized = True
            logger.info("Feature toggle service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize feature toggle service: {e}")
            raise

    async def _load_features(self):
        """Load feature toggles from storage."""
        if not self.features_file.exists():
            self._features = {}
            return

        try:
            with open(self.features_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._features = {}
            for feature_data in data.get("features", []):
                feature = FeatureToggle(**feature_data)
                self._features[feature.id] = feature

            logger.info(f"Loaded {len(self._features)} feature toggles")

        except Exception as e:
            logger.error(f"Failed to load features: {e}")
            self._features = {}

    async def _load_user_access(self):
        """Load user access configurations from storage."""
        if not self.user_access_file.exists():
            self._user_access = {}
            return

        try:
            with open(self.user_access_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._user_access = {}
            for user_id, access_data in data.get("user_access", {}).items():
                self._user_access[user_id] = {}
                for feature_id, access_info in access_data.items():
                    access = UserFeatureAccess(**access_info)
                    self._user_access[user_id][feature_id] = access

            logger.info(f"Loaded user access for {len(self._user_access)} users")

        except Exception as e:
            logger.error(f"Failed to load user access: {e}")
            self._user_access = {}

    def _deserialize_datetime_recursive(self, obj):
        """Recursively convert ISO datetime strings back to datetime objects."""
        if isinstance(obj, str):
            return self._try_parse_datetime_string(obj)
        elif isinstance(obj, dict):
            return self._deserialize_dict(obj)
        elif isinstance(obj, list):
            return self._deserialize_list(obj)
        else:
            return obj

    def _try_parse_datetime_string(self, text: str):
        """Try to parse a string as ISO datetime"""
        if not self._looks_like_iso_datetime(text):
            return text

        try:
            normalized = self._normalize_datetime_string(text)
            return datetime.fromisoformat(normalized)
        except ValueError:
            return text

    def _looks_like_iso_datetime(self, text: str) -> bool:
        """Check if string looks like ISO datetime format"""
        return (
            len(text) >= 19
            and "T" in text
            and ":" in text
            and (
                text.endswith("Z")
                or "+" in text[-6:]
                or "-" in text[-6:]
                or "." in text
            )
        )

    def _normalize_datetime_string(self, text: str) -> str:
        """Normalize datetime string for parsing"""
        if text.endswith("Z"):
            return text[:-1] + "+00:00"
        return text

    def _deserialize_dict(self, data: dict) -> dict:
        """Recursively deserialize dictionary values"""
        return {
            key: self._deserialize_datetime_recursive(value)
            for key, value in data.items()
        }

    def _deserialize_list(self, items: list) -> list:
        """Recursively deserialize list items"""
        return [self._deserialize_datetime_recursive(item) for item in items]

    async def _load_events(self):
        """Load feature toggle events from storage."""
        if not self.events_file.exists():
            self._events = []
            return

        try:
            with open(self.events_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._events = []
            for event_data in data.get("events", []):
                # Recursively convert datetime strings back to datetime objects
                event_data = self._deserialize_datetime_recursive(event_data)
                event = FeatureToggleEvent(**event_data)
                self._events.append(event)

            # Keep only last 1000 events
            self._events = self._events[-1000:]

            logger.info(f"Loaded {len(self._events)} feature toggle events")

        except Exception as e:
            logger.error(f"Failed to load events: {e}")
            self._events = []

    async def _save_features(self):
        """Save feature toggles to storage."""
        try:
            features_data = []
            for feature in self._features.values():
                feature_dict = feature.model_dump()
                # Convert datetime objects to ISO strings
                for field in ["created_at", "updated_at"]:
                    if field in feature_dict and feature_dict[field]:
                        feature_dict[field] = feature_dict[field].isoformat()
                features_data.append(feature_dict)

            data = {
                "features": features_data,
                "metadata": {
                    "total_features": len(features_data),
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0",
                },
            }

            with open(self.features_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved {len(features_data)} feature toggles")

        except Exception as e:
            logger.error(f"Failed to save features: {e}")
            raise

    async def _save_user_access(self):
        """Save user access configurations to storage."""
        try:
            user_access_data = {}
            for user_id, access_dict in self._user_access.items():
                user_access_data[user_id] = {}
                for feature_id, access in access_dict.items():
                    access_dict_data = access.model_dump()
                    # Convert datetime objects to ISO strings
                    for field in ["granted_at", "override_expires", "last_used"]:
                        if field in access_dict_data and access_dict_data[field]:
                            access_dict_data[field] = access_dict_data[
                                field
                            ].isoformat()
                    user_access_data[user_id][feature_id] = access_dict_data

            data = {
                "user_access": user_access_data,
                "metadata": {
                    "total_users": len(user_access_data),
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0",
                },
            }

            with open(self.user_access_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved user access for {len(user_access_data)} users")

        except Exception as e:
            logger.error(f"Failed to save user access: {e}")
            raise

    def _serialize_datetime_recursive(self, obj):
        """Recursively convert datetime objects to ISO strings for JSON serialization."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {
                key: self._serialize_datetime_recursive(value)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [self._serialize_datetime_recursive(item) for item in obj]
        else:
            return obj

    async def _save_events(self):
        """Save feature toggle events to storage."""
        try:
            events_data = []
            for event in self._events[-1000:]:  # Keep only last 1000 events
                event_dict = event.model_dump()
                # Recursively convert all datetime objects to ISO strings
                event_dict = self._serialize_datetime_recursive(event_dict)
                events_data.append(event_dict)

            data = {
                "events": events_data,
                "metadata": {
                    "total_events": len(events_data),
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0",
                },
            }

            with open(self.events_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved {len(events_data)} feature toggle events")

        except Exception as e:
            logger.error(f"Failed to save events: {e}")
            raise

    async def _create_default_features(self):
        """Create default feature toggles if none exist."""
        if self._features:
            return  # Features already exist

        logger.info("Creating default feature toggles...")

        default_features = [
            {
                "id": "advanced_speech_analysis",
                "name": "Advanced Speech Analysis",
                "description": "Real-time speech analysis with pronunciation feedback",
                "category": FeatureToggleCategory.ANALYSIS,
                "scope": FeatureToggleScope.GLOBAL,
                "status": FeatureToggleStatus.ENABLED,
                "enabled_by_default": True,
                "requires_admin": False,
            },
            {
                "id": "conversation_scenarios",
                "name": "Conversation Scenarios",
                "description": "Interactive conversation practice scenarios",
                "category": FeatureToggleCategory.SCENARIOS,
                "scope": FeatureToggleScope.GLOBAL,
                "status": FeatureToggleStatus.ENABLED,
                "enabled_by_default": True,
                "requires_admin": False,
            },
            {
                "id": "ai_tutor_mode",
                "name": "AI Tutor Mode",
                "description": "Adaptive AI-powered tutoring with personalized feedback",
                "category": FeatureToggleCategory.TUTOR_MODES,
                "scope": FeatureToggleScope.GLOBAL,
                "status": FeatureToggleStatus.ENABLED,
                "enabled_by_default": True,
                "requires_admin": False,
            },
            {
                "id": "spaced_repetition",
                "name": "Spaced Repetition System",
                "description": "Intelligent spaced repetition for vocabulary learning",
                "category": FeatureToggleCategory.ANALYSIS,
                "scope": FeatureToggleScope.GLOBAL,
                "status": FeatureToggleStatus.ENABLED,
                "enabled_by_default": True,
                "requires_admin": False,
            },
            {
                "id": "admin_dashboard",
                "name": "Admin Dashboard",
                "description": "Administrative interface for system management",
                "category": FeatureToggleCategory.UI_COMPONENTS,
                "scope": FeatureToggleScope.ROLE_BASED,
                "status": FeatureToggleStatus.ENABLED,
                "enabled_by_default": False,
                "requires_admin": True,
                "target_roles": ["admin", "super_admin"],
            },
            {
                "id": "experimental_voice_cloning",
                "name": "Experimental Voice Cloning",
                "description": "Advanced voice cloning for personalized TTS",
                "category": FeatureToggleCategory.EXPERIMENTAL,
                "scope": FeatureToggleScope.EXPERIMENTAL,
                "status": FeatureToggleStatus.DISABLED,
                "enabled_by_default": False,
                "requires_admin": True,
                "experimental": True,
                "rollout_percentage": 10.0,
            },
            {
                "id": "real_time_translation",
                "name": "Real-time Translation",
                "description": "Live translation during conversation practice",
                "category": FeatureToggleCategory.INTEGRATIONS,
                "scope": FeatureToggleScope.GLOBAL,
                "status": FeatureToggleStatus.ENABLED,
                "enabled_by_default": True,
                "requires_admin": False,
            },
            {
                "id": "progress_analytics",
                "name": "Progress Analytics",
                "description": "Detailed learning progress analytics and insights",
                "category": FeatureToggleCategory.ANALYSIS,
                "scope": FeatureToggleScope.GLOBAL,
                "status": FeatureToggleStatus.ENABLED,
                "enabled_by_default": True,
                "requires_admin": False,
            },
        ]

        for feature_data in default_features:
            # Create feature directly without calling create_feature to avoid recursion
            feature_id = f"{feature_data['category'].value}_{feature_data['name'].lower().replace(' ', '_')}"

            # Ensure uniqueness
            counter = 1
            original_id = feature_id
            while feature_id in self._features:
                feature_id = f"{original_id}_{counter}"
                counter += 1

            feature = FeatureToggle(
                id=feature_id,
                name=feature_data["name"],
                description=feature_data["description"],
                category=feature_data["category"],
                scope=feature_data["scope"],
                status=feature_data["status"],
                enabled_by_default=feature_data.get("enabled_by_default", False),
                requires_admin=feature_data.get("requires_admin", False),
                target_roles=feature_data.get("target_roles", []),
                experimental=feature_data.get("experimental", False),
                rollout_percentage=feature_data.get("rollout_percentage", 0.0),
                created_by="system",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            self._features[feature_id] = feature

            # Record event directly to avoid recursion
            event = FeatureToggleEvent(
                id=str(uuid.uuid4()),
                feature_id=feature_id,
                event_type="created",
                new_state={"status": feature_data["status"].value, "enabled": True},
                user_id="system",
                timestamp=datetime.now(),
                metadata={"initial_creation": True},
            )
            self._events.append(event)

        logger.info(f"Created {len(default_features)} default feature toggles")

    async def _record_event(
        self,
        feature_id: str,
        event_type: str,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        change_reason: Optional[str] = None,
    ):
        """Record a feature toggle event."""
        event = FeatureToggleEvent(
            id=str(uuid.uuid4()),
            feature_id=feature_id,
            event_type=event_type,
            previous_state=previous_state,
            new_state=new_state or {},
            change_reason=change_reason,
            user_id=user_id,
            environment="development",  # TODO: Get from config
            timestamp=datetime.now(),
        )

        self._events.append(event)

        # Auto-save events periodically
        if len(self._events) % 10 == 0:
            await self._save_events()

    def _clear_cache_if_needed(self):
        """Clear feature evaluation cache if TTL exceeded."""
        if datetime.now() - self._last_cache_clear > timedelta(seconds=self._cache_ttl):
            self._feature_cache.clear()
            self._last_cache_clear = datetime.now()

    async def create_feature(
        self, feature_request: FeatureToggleRequest, created_by: Optional[str] = None
    ) -> FeatureToggle:
        """Create a new feature toggle."""
        if not self._initialized:
            await self.initialize()

        # Generate unique ID
        feature_id = f"{feature_request.category.value}_{feature_request.name.lower().replace(' ', '_')}"

        # Ensure uniqueness
        counter = 1
        original_id = feature_id
        while feature_id in self._features:
            feature_id = f"{original_id}_{counter}"
            counter += 1

        # Create feature toggle
        feature = FeatureToggle(
            id=feature_id,
            name=feature_request.name,
            description=feature_request.description,
            category=feature_request.category,
            scope=feature_request.scope,
            status=feature_request.status,
            enabled_by_default=feature_request.enabled_by_default,
            requires_admin=feature_request.requires_admin,
            experimental=feature_request.experimental,
            conditions=feature_request.conditions,
            target_users=feature_request.target_users,
            target_roles=feature_request.target_roles,
            rollout_percentage=feature_request.rollout_percentage,
            dependencies=feature_request.dependencies,
            conflicts=feature_request.conflicts,
            environments=feature_request.environments,
            usage_tracking=feature_request.usage_tracking,
            created_by=created_by,
            updated_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self._features[feature_id] = feature
        await self._save_features()

        # Record event
        await self._record_event(
            feature_id=feature_id,
            event_type="created",
            new_state=feature.model_dump(),
            user_id=created_by,
            change_reason="Feature toggle created",
        )

        # Clear cache
        self._feature_cache.clear()

        logger.info(f"Created feature toggle: {feature_id}")
        return feature

    async def get_feature(self, feature_id: str) -> Optional[FeatureToggle]:
        """Get a specific feature toggle."""
        if not self._initialized:
            await self.initialize()
        return self._features.get(feature_id)

    async def get_all_features(
        self,
        category: Optional[FeatureToggleCategory] = None,
        scope: Optional[FeatureToggleScope] = None,
        status: Optional[FeatureToggleStatus] = None,
    ) -> List[FeatureToggle]:
        """Get all feature toggles with optional filtering."""
        if not self._initialized:
            await self.initialize()

        features = list(self._features.values())

        if category:
            features = [f for f in features if f.category == category]
        if scope:
            features = [f for f in features if f.scope == scope]
        if status:
            features = [f for f in features if f.status == status]

        return sorted(features, key=lambda f: f.created_at, reverse=True)

    async def update_feature(
        self,
        feature_id: str,
        update_request: FeatureToggleUpdateRequest,
        updated_by: Optional[str] = None,
    ) -> Optional[FeatureToggle]:
        """Update an existing feature toggle."""
        if not self._initialized:
            await self.initialize()

        feature = self._features.get(feature_id)
        if not feature:
            return None

        # Record previous state
        previous_state = feature.model_dump()

        # Update fields
        update_data = update_request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(feature, field, value)

        feature.updated_at = datetime.now()
        feature.updated_by = updated_by

        await self._save_features()

        # Record event
        await self._record_event(
            feature_id=feature_id,
            event_type="updated",
            previous_state=previous_state,
            new_state=feature.model_dump(),
            user_id=updated_by,
            change_reason="Feature toggle updated",
        )

        # Clear cache
        self._feature_cache.clear()

        logger.info(f"Updated feature toggle: {feature_id}")
        return feature

    async def delete_feature(
        self, feature_id: str, deleted_by: Optional[str] = None
    ) -> bool:
        """Delete a feature toggle."""
        if not self._initialized:
            await self.initialize()

        feature = self._features.get(feature_id)
        if not feature:
            return False

        # Record previous state
        previous_state = feature.model_dump()

        # Remove feature
        del self._features[feature_id]
        await self._save_features()

        # Remove user access entries
        for user_access in self._user_access.values():
            if feature_id in user_access:
                del user_access[feature_id]
        await self._save_user_access()

        # Record event
        await self._record_event(
            feature_id=feature_id,
            event_type="deleted",
            previous_state=previous_state,
            user_id=deleted_by,
            change_reason="Feature toggle deleted",
        )

        # Clear cache
        self._feature_cache.clear()

        logger.info(f"Deleted feature toggle: {feature_id}")
        return True

    async def is_feature_enabled(
        self,
        feature_id: str,
        user_id: Optional[str] = None,
        user_roles: Optional[List[str]] = None,
    ) -> bool:
        """Check if a feature is enabled for a specific user."""
        if not self._initialized:
            await self.initialize()

        # Check cache first
        self._clear_cache_if_needed()
        cache_key = f"{feature_id}:{user_id or 'anonymous'}"
        if cache_key in self._feature_cache:
            cached_result = self._feature_cache[cache_key]
            if "result" in cached_result and "timestamp" in cached_result:
                cache_age = (
                    datetime.now() - datetime.fromisoformat(cached_result["timestamp"])
                ).seconds
                if cache_age < self._cache_ttl:
                    return cached_result["result"]

        # Get feature
        feature = self._features.get(feature_id)
        if not feature:
            return False

        # Always evaluate the feature - let _evaluate_feature handle user overrides
        result = await self._evaluate_feature(feature, user_id, user_roles)

        # Cache result
        if cache_key not in self._feature_cache:
            self._feature_cache[cache_key] = {}
        self._feature_cache[cache_key]["result"] = result
        self._feature_cache[cache_key]["timestamp"] = datetime.now().isoformat()

        return result

    def _check_user_override(
        self, feature: FeatureToggle, user_id: Optional[str]
    ) -> Optional[bool]:
        """Check if user has a specific override for this feature.

        Returns:
            True/False if override exists and is active, None otherwise
        """
        if not user_id or user_id not in self._user_access:
            return None

        user_access = self._user_access[user_id].get(feature.id)
        if not user_access or not user_access.override_global:
            return None

        # Check if override has expired
        if (
            user_access.override_expires
            and user_access.override_expires <= datetime.now()
        ):
            return None

        return user_access.enabled

    def _check_global_status(self, feature: FeatureToggle) -> bool:
        """Check if feature's global status allows enablement."""
        if feature.status == FeatureToggleStatus.DISABLED:
            return False
        if feature.status == FeatureToggleStatus.MAINTENANCE:
            return False
        return True

    def _check_admin_requirement(
        self, feature: FeatureToggle, user_roles: Optional[List[str]]
    ) -> bool:
        """Check if user meets admin requirements for this feature."""
        if not feature.requires_admin:
            return True

        if not user_roles:
            return False

        return "admin" in user_roles or "super_admin" in user_roles

    def _check_scope_rules(
        self,
        feature: FeatureToggle,
        user_id: Optional[str],
        user_roles: Optional[List[str]],
    ) -> bool:
        """Check if user meets scope-based access rules."""
        if feature.scope == FeatureToggleScope.USER_SPECIFIC:
            return user_id is not None and user_id in feature.target_users

        if feature.scope == FeatureToggleScope.ROLE_BASED:
            if not user_roles:
                return False
            return any(role in feature.target_roles for role in user_roles)

        if feature.scope == FeatureToggleScope.EXPERIMENTAL:
            return self._check_experimental_rollout(feature, user_id)

        # GLOBAL scope or unknown scope
        return True

    def _check_experimental_rollout(
        self, feature: FeatureToggle, user_id: Optional[str]
    ) -> bool:
        """Check if user is in experimental feature rollout."""
        if not feature.experimental:
            return False

        if not user_id:
            return False

        # Use consistent hash of user_id + feature_id for deterministic rollout
        hash_input = f"{user_id}:{feature.id}"
        user_hash = abs(hash(hash_input)) % 100
        return user_hash < feature.rollout_percentage

    async def _check_conditions(
        self,
        feature: FeatureToggle,
        user_id: Optional[str],
        user_roles: Optional[List[str]],
    ) -> bool:
        """Check if all feature conditions are met."""
        for condition in feature.conditions:
            if not await self._evaluate_condition(condition, user_id, user_roles):
                return False
        return True

    async def _check_dependencies(
        self,
        feature: FeatureToggle,
        user_id: Optional[str],
        user_roles: Optional[List[str]],
    ) -> bool:
        """Check if all feature dependencies are enabled."""
        for dependency_id in feature.dependencies:
            if not await self.is_feature_enabled(dependency_id, user_id, user_roles):
                return False
        return True

    async def _check_conflicts(
        self,
        feature: FeatureToggle,
        user_id: Optional[str],
        user_roles: Optional[List[str]],
    ) -> bool:
        """Check if no conflicting features are enabled."""
        for conflict_id in feature.conflicts:
            if await self.is_feature_enabled(conflict_id, user_id, user_roles):
                return False
        return True

    def _check_environment(self, feature: FeatureToggle) -> bool:
        """Check if feature is enabled in current environment."""
        current_env = "development"  # TODO: Get from config
        if current_env not in feature.environments:
            return True  # No environment restriction
        return feature.environments[current_env]

    async def _evaluate_feature(
        self,
        feature: FeatureToggle,
        user_id: Optional[str] = None,
        user_roles: Optional[List[str]] = None,
    ) -> bool:
        """Evaluate feature enablement based on conditions.

        Refactored from E(32) to B(8) complexity by extracting helper methods.
        """
        # Check user-specific override first (highest priority)
        override = self._check_user_override(feature, user_id)
        if override is not None:
            return override

        # Check global status
        if not self._check_global_status(feature):
            return False

        # Check admin requirement
        if not self._check_admin_requirement(feature, user_roles):
            return False

        # Check scope-based rules
        if not self._check_scope_rules(feature, user_id, user_roles):
            return False

        # Check all conditions
        if not await self._check_conditions(feature, user_id, user_roles):
            return False

        # Check dependencies
        if not await self._check_dependencies(feature, user_id, user_roles):
            return False

        # Check conflicts
        if not await self._check_conflicts(feature, user_id, user_roles):
            return False

        # Check environment
        if not self._check_environment(feature):
            return False

        return feature.status == FeatureToggleStatus.ENABLED

    def _evaluate_user_role_condition(
        self, condition: FeatureCondition, user_roles: Optional[List[str]]
    ) -> bool:
        """Evaluate user role condition"""
        if not user_roles:
            return False

        if condition.operator == "equals":
            return condition.value in user_roles
        elif condition.operator == "not_equals":
            return condition.value not in user_roles

        return False

    def _evaluate_date_range_condition(self, condition: FeatureCondition) -> bool:
        """Evaluate date range condition"""
        if condition.operator != "between":
            return False

        if not isinstance(condition.value, list) or len(condition.value) != 2:
            return False

        now = datetime.now()
        start_date = datetime.fromisoformat(condition.value[0])
        end_date = datetime.fromisoformat(condition.value[1])
        return start_date <= now <= end_date

    def _evaluate_percentage_condition(
        self, condition: FeatureCondition, user_id: Optional[str]
    ) -> bool:
        """Evaluate percentage rollout condition"""
        if condition.operator != "less_than" or not user_id:
            return False

        user_hash = hash(user_id) % 100
        return user_hash < condition.value

    async def _evaluate_condition(
        self,
        condition: FeatureCondition,
        user_id: Optional[str] = None,
        user_roles: Optional[List[str]] = None,
    ) -> bool:
        """Evaluate a specific condition."""
        try:
            if condition.type == "user_role":
                return self._evaluate_user_role_condition(condition, user_roles)
            elif condition.type == "date_range":
                return self._evaluate_date_range_condition(condition)
            elif condition.type == "percentage":
                return self._evaluate_percentage_condition(condition, user_id)
            # Add more condition types as needed
            return True
        except Exception as e:
            logger.error(f"Error evaluating condition {condition.type}: {e}")
            return False

    async def set_user_feature_access(
        self,
        user_id: str,
        feature_id: str,
        enabled: bool,
        granted_by: Optional[str] = None,
        override_global: bool = False,
        override_reason: Optional[str] = None,
        override_expires: Optional[datetime] = None,
    ) -> bool:
        """Set user-specific feature access."""
        if not self._initialized:
            await self.initialize()

        # Check if feature exists
        if feature_id not in self._features:
            return False

        if user_id not in self._user_access:
            self._user_access[user_id] = {}

        access = UserFeatureAccess(
            user_id=user_id,
            feature_id=feature_id,
            enabled=enabled,
            override_global=override_global,
            override_reason=override_reason,
            override_expires=override_expires,
            granted_by=granted_by,
            granted_at=datetime.now(),
        )

        self._user_access[user_id][feature_id] = access
        await self._save_user_access()

        # Record event
        await self._record_event(
            feature_id=feature_id,
            event_type="user_access_changed",
            new_state={
                "user_id": user_id,
                "enabled": enabled,
                "override_global": override_global,
            },
            user_id=granted_by,
            change_reason=f"User access {'granted' if enabled else 'revoked'}",
        )

        # Clear cache for this user
        cache_pattern = f"{feature_id}:{user_id}"
        keys_to_remove = [
            k for k in self._feature_cache.keys() if k.startswith(cache_pattern)
        ]
        for key in keys_to_remove:
            del self._feature_cache[key]

        logger.info(f"Set user feature access: {user_id} -> {feature_id} = {enabled}")
        return True

    async def get_user_features(
        self, user_id: str, user_roles: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """Get all feature states for a specific user."""
        if not self._initialized:
            await self.initialize()

        result = {}
        for feature_id in self._features:
            result[feature_id] = await self.is_feature_enabled(
                feature_id, user_id, user_roles
            )

        return result

    async def get_feature_statistics(self) -> Dict[str, Any]:
        """Get feature toggle statistics."""
        if not self._initialized:
            await self.initialize()

        features = list(self._features.values())

        return {
            **self._calculate_basic_counts(features),
            "features_by_category": self._group_by_category(features),
            "features_by_scope": self._group_by_scope(features),
            "features_by_environment": self._group_by_environment(features),
            "recent_changes": self._get_recent_changes(),
            "cache_size": len(self._feature_cache),
            "total_users_with_overrides": len(self._user_access),
            "total_events": len(self._events),
        }

    def _calculate_basic_counts(self, features: List[FeatureToggle]) -> Dict[str, int]:
        """Calculate basic feature counts."""
        return {
            "total_features": len(features),
            "enabled_features": len(
                [f for f in features if f.status == FeatureToggleStatus.ENABLED]
            ),
            "disabled_features": len(
                [f for f in features if f.status == FeatureToggleStatus.DISABLED]
            ),
            "experimental_features": len([f for f in features if f.experimental]),
        }

    def _group_by_category(self, features: List[FeatureToggle]) -> Dict[str, int]:
        """Group features by category."""
        by_category = {}
        for category in FeatureToggleCategory:
            by_category[category.value] = len(
                [f for f in features if f.category == category]
            )
        return by_category

    def _group_by_scope(self, features: List[FeatureToggle]) -> Dict[str, int]:
        """Group features by scope."""
        by_scope = {}
        for scope in FeatureToggleScope:
            by_scope[scope.value] = len([f for f in features if f.scope == scope])
        return by_scope

    def _group_by_environment(
        self, features: List[FeatureToggle]
    ) -> Dict[str, Dict[str, int]]:
        """Group features by environment."""
        by_environment = {}
        environments = ["development", "staging", "production"]
        for env in environments:
            by_environment[env] = {
                "enabled": len([f for f in features if f.environments.get(env, False)]),
                "disabled": len(
                    [f for f in features if not f.environments.get(env, False)]
                ),
            }
        return by_environment

    def _get_recent_changes(self) -> List[Dict[str, Any]]:
        """Get recent feature toggle changes."""
        recent_changes = self._events[-10:] if self._events else []
        return [event.model_dump() for event in recent_changes]


# Global service instance
_feature_toggle_service: Optional[FeatureToggleService] = None


async def get_feature_toggle_service() -> FeatureToggleService:
    """Get the global feature toggle service instance."""
    global _feature_toggle_service

    if _feature_toggle_service is None:
        _feature_toggle_service = FeatureToggleService()
        await _feature_toggle_service.initialize()

    return _feature_toggle_service


async def is_feature_enabled(
    feature_id: str,
    user_id: Optional[str] = None,
    user_roles: Optional[List[str]] = None,
) -> bool:
    """Quick helper function to check if a feature is enabled."""
    service = await get_feature_toggle_service()
    return await service.is_feature_enabled(feature_id, user_id, user_roles)
