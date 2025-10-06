"""
Feature Toggle Manager Service

Provides centralized management of feature toggles for the AI Language Tutor application.
Allows dynamic enabling/disabling of features based on admin configuration.

Author: AI Assistant
Date: 2025-09-27
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import threading

logger = logging.getLogger(__name__)


class FeatureCategory(Enum):
    """Feature categories for organization"""
    LEARNING = "learning"
    SPEECH = "speech"
    ADMIN = "admin"
    ACCESS = "access"
    PERFORMANCE = "performance"
    GENERAL = "general"


class UserRole(Enum):
    """User roles for permission checking"""
    CHILD = "CHILD"
    PARENT = "PARENT"
    ADMIN = "ADMIN"


@dataclass
class FeatureToggle:
    """Feature toggle data model"""
    id: Optional[int] = None
    feature_name: str = ""
    is_enabled: bool = True
    description: str = ""
    category: str = "general"
    requires_restart: bool = False
    min_role: str = "CHILD"
    configuration: Dict[str, Any] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        if self.configuration is None:
            self.configuration = {}


class FeatureToggleManager:
    """
    Central service for managing feature toggles

    Provides thread-safe access to feature toggle configuration with caching
    for performance and database persistence for reliability.
    """

    def __init__(self, db_path: str = "data/ai_language_tutor.db"):
        """
        Initialize the Feature Toggle Manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._cache: Dict[str, FeatureToggle] = {}
        self._cache_lock = threading.RLock()
        self._last_cache_update = None
        self.cache_ttl = 300  # 5 minutes cache TTL

        # Initialize cache
        self._refresh_cache()

        logger.info(f"FeatureToggleManager initialized with {len(self._cache)} features")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _refresh_cache(self) -> None:
        """Refresh the feature toggle cache from database"""
        try:
            with self._cache_lock:
                conn = self._get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, feature_name, is_enabled, description, category,
                           requires_restart, min_role, configuration,
                           created_at, updated_at
                    FROM admin_feature_toggles
                    ORDER BY category, feature_name
                """)

                self._cache.clear()
                for row in cursor.fetchall():
                    row_dict = dict(row)

                    # Parse JSON configuration
                    try:
                        row_dict['configuration'] = json.loads(row_dict['configuration'] or '{}')
                    except json.JSONDecodeError:
                        row_dict['configuration'] = {}

                    # Convert to boolean
                    row_dict['is_enabled'] = bool(row_dict['is_enabled'])
                    row_dict['requires_restart'] = bool(row_dict['requires_restart'])

                    feature = FeatureToggle(**row_dict)
                    self._cache[feature.feature_name] = feature

                self._last_cache_update = datetime.now()
                conn.close()

                logger.debug(f"Cache refreshed with {len(self._cache)} features")

        except Exception as e:
            logger.error(f"Failed to refresh feature toggle cache: {e}")

    def _should_refresh_cache(self) -> bool:
        """Check if cache should be refreshed based on TTL"""
        if self._last_cache_update is None:
            return True

        elapsed = (datetime.now() - self._last_cache_update).total_seconds()
        return elapsed > self.cache_ttl

    def is_feature_enabled(self, feature_name: str, user_role: str = "CHILD") -> bool:
        """
        Check if a feature is enabled for the given user role

        Args:
            feature_name: Name of the feature to check
            user_role: User role (CHILD, PARENT, ADMIN)

        Returns:
            True if feature is enabled and user has permission, False otherwise
        """
        try:
            # Refresh cache if needed
            if self._should_refresh_cache():
                self._refresh_cache()

            with self._cache_lock:
                feature = self._cache.get(feature_name)

                if not feature:
                    logger.warning(f"Feature '{feature_name}' not found, defaulting to disabled")
                    return False

                # Check if feature is enabled
                if not feature.is_enabled:
                    return False

                # Check role permission
                return self._check_role_permission(user_role, feature.min_role)

        except Exception as e:
            logger.error(f"Error checking feature '{feature_name}': {e}")
            return False

    def _check_role_permission(self, user_role: str, min_required_role: str) -> bool:
        """Check if user role meets minimum required role"""
        role_hierarchy = {
            "CHILD": 1,
            "PARENT": 2,
            "ADMIN": 3
        }

        user_level = role_hierarchy.get(user_role.upper(), 0)
        required_level = role_hierarchy.get(min_required_role.upper(), 1)

        return user_level >= required_level

    def get_feature(self, feature_name: str) -> Optional[FeatureToggle]:
        """Get complete feature toggle configuration"""
        try:
            if self._should_refresh_cache():
                self._refresh_cache()

            with self._cache_lock:
                return self._cache.get(feature_name)

        except Exception as e:
            logger.error(f"Error getting feature '{feature_name}': {e}")
            return None

    def get_all_features(self, category: Optional[str] = None,
                        user_role: str = "CHILD") -> Dict[str, FeatureToggle]:
        """
        Get all features, optionally filtered by category and user role

        Args:
            category: Optional category filter
            user_role: User role for permission filtering

        Returns:
            Dictionary of feature name -> FeatureToggle
        """
        try:
            if self._should_refresh_cache():
                self._refresh_cache()

            with self._cache_lock:
                result = {}

                for name, feature in self._cache.items():
                    # Apply category filter
                    if category and feature.category != category:
                        continue

                    # Apply role permission filter
                    if not self._check_role_permission(user_role, feature.min_role):
                        continue

                    result[name] = feature

                return result

        except Exception as e:
            logger.error(f"Error getting features: {e}")
            return {}

    def get_features_by_category(self, user_role: str = "CHILD") -> Dict[str, List[FeatureToggle]]:
        """Get features organized by category"""
        try:
            all_features = self.get_all_features(user_role=user_role)

            categories = {}
            for feature in all_features.values():
                category = feature.category
                if category not in categories:
                    categories[category] = []
                categories[category].append(feature)

            # Sort features within each category
            for category in categories:
                categories[category].sort(key=lambda f: f.feature_name)

            return categories

        except Exception as e:
            logger.error(f"Error organizing features by category: {e}")
            return {}

    def update_feature(self, feature_name: str, is_enabled: Optional[bool] = None,
                      description: Optional[str] = None,
                      configuration: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update feature toggle configuration

        Args:
            feature_name: Name of feature to update
            is_enabled: New enabled state
            description: New description
            configuration: New configuration dict

        Returns:
            True if update successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Build update query dynamically
            updates = []
            params = []

            if is_enabled is not None:
                updates.append("is_enabled = ?")
                params.append(is_enabled)

            if description is not None:
                updates.append("description = ?")
                params.append(description)

            if configuration is not None:
                updates.append("configuration = ?")
                params.append(json.dumps(configuration))

            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().isoformat())

                query = f"UPDATE admin_feature_toggles SET {', '.join(updates)} WHERE feature_name = ?"
                params.append(feature_name)

                cursor.execute(query, params)
                conn.commit()

                if cursor.rowcount > 0:
                    # Refresh cache to reflect changes
                    self._refresh_cache()
                    logger.info(f"Updated feature '{feature_name}'")
                    return True
                else:
                    logger.warning(f"Feature '{feature_name}' not found for update")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error updating feature '{feature_name}': {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def create_feature(self, feature: FeatureToggle) -> bool:
        """Create a new feature toggle"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO admin_feature_toggles
                (feature_name, is_enabled, description, category, requires_restart,
                 min_role, configuration, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feature.feature_name,
                feature.is_enabled,
                feature.description,
                feature.category,
                feature.requires_restart,
                feature.min_role,
                json.dumps(feature.configuration),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            conn.commit()

            # Refresh cache
            self._refresh_cache()

            logger.info(f"Created feature '{feature.feature_name}'")
            return True

        except Exception as e:
            logger.error(f"Error creating feature '{feature.feature_name}': {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def delete_feature(self, feature_name: str) -> bool:
        """Delete a feature toggle"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM admin_feature_toggles WHERE feature_name = ?", (feature_name,))
            conn.commit()

            if cursor.rowcount > 0:
                # Refresh cache
                self._refresh_cache()
                logger.info(f"Deleted feature '{feature_name}'")
                return True
            else:
                logger.warning(f"Feature '{feature_name}' not found for deletion")
                return False

        except Exception as e:
            logger.error(f"Error deleting feature '{feature_name}': {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def get_feature_statistics(self) -> Dict[str, Any]:
        """Get statistics about feature toggles"""
        try:
            features = self.get_all_features(user_role="ADMIN")

            stats = {
                "total_features": len(features),
                "enabled_features": sum(1 for f in features.values() if f.is_enabled),
                "disabled_features": sum(1 for f in features.values() if not f.is_enabled),
                "categories": {},
                "roles": {}
            }

            # Category breakdown
            for feature in features.values():
                category = feature.category
                if category not in stats["categories"]:
                    stats["categories"][category] = {"total": 0, "enabled": 0}

                stats["categories"][category]["total"] += 1
                if feature.is_enabled:
                    stats["categories"][category]["enabled"] += 1

            # Role breakdown
            for feature in features.values():
                role = feature.min_role
                if role not in stats["roles"]:
                    stats["roles"][role] = {"total": 0, "enabled": 0}

                stats["roles"][role]["total"] += 1
                if feature.is_enabled:
                    stats["roles"][role]["enabled"] += 1

            return stats

        except Exception as e:
            logger.error(f"Error getting feature statistics: {e}")
            return {}

    def bulk_update_features(self, updates: Dict[str, bool]) -> Dict[str, bool]:
        """
        Bulk update multiple features

        Args:
            updates: Dict of feature_name -> enabled state

        Returns:
            Dict of feature_name -> success status
        """
        results = {}

        for feature_name, enabled in updates.items():
            results[feature_name] = self.update_feature(feature_name, is_enabled=enabled)

        return results

    def export_configuration(self) -> Dict[str, Any]:
        """Export current feature toggle configuration"""
        try:
            features = self.get_all_features(user_role="ADMIN")

            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_features": len(features),
                "features": {}
            }

            for name, feature in features.items():
                export_data["features"][name] = {
                    "is_enabled": feature.is_enabled,
                    "description": feature.description,
                    "category": feature.category,
                    "requires_restart": feature.requires_restart,
                    "min_role": feature.min_role,
                    "configuration": feature.configuration
                }

            return export_data

        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return {}

    def import_configuration(self, config_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Import feature toggle configuration

        Args:
            config_data: Configuration data to import

        Returns:
            Dict of feature_name -> import success status
        """
        results = {}

        try:
            features_data = config_data.get("features", {})

            for feature_name, feature_config in features_data.items():
                success = self.update_feature(
                    feature_name,
                    is_enabled=feature_config.get("is_enabled"),
                    description=feature_config.get("description"),
                    configuration=feature_config.get("configuration")
                )
                results[feature_name] = success

            return results

        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            return {}


# Global instance for application use
feature_toggle_manager = FeatureToggleManager()

# Convenience functions for easy access


def is_feature_enabled(feature_name: str, user_role: str = "CHILD") -> bool:
    """Convenience function to check if feature is enabled"""
    return feature_toggle_manager.is_feature_enabled(feature_name, user_role)


def get_feature(feature_name: str) -> Optional[FeatureToggle]:
    """Convenience function to get feature configuration"""
    return feature_toggle_manager.get_feature(feature_name)


def get_features_by_category(user_role: str = "CHILD") -> Dict[str, List[FeatureToggle]]:
    """Convenience function to get features by category"""
    return feature_toggle_manager.get_features_by_category(user_role)
