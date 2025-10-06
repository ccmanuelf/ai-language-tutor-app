"""
Feature Toggle Decorators

Provides decorators and utilities for integrating feature toggles with application services.
Allows functions and endpoints to be conditionally enabled based on feature toggle configuration.

Author: AI Assistant
Date: 2025-09-27
"""

from functools import wraps
from typing import Optional, Callable, Any
import logging

from ..services.feature_toggle_manager import is_feature_enabled

logger = logging.getLogger(__name__)


def require_feature(
    feature_name: str,
    user_role: str = "CHILD",
    fallback_response: Any = None,
    raise_exception: bool = True,
):
    """
    Decorator to require a feature to be enabled for function execution

    Args:
        feature_name: Name of the feature to check
        user_role: User role for permission checking
        fallback_response: Response to return if feature is disabled
        raise_exception: Whether to raise exception or return fallback

    Usage:
        @require_feature("content_processing")
        def process_youtube_content(url: str):
            # Function only executes if content_processing is enabled
            pass

        @require_feature("tutor_modes", user_role="CHILD", fallback_response={"error": "Feature disabled"})
        def get_tutor_modes():
            # Returns fallback if feature disabled
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Check if feature is enabled
                if not is_feature_enabled(feature_name, user_role):
                    message = f"Feature '{feature_name}' is disabled or not available for role '{user_role}'"

                    if raise_exception:
                        from fastapi import HTTPException

                        raise HTTPException(status_code=403, detail=message)
                    else:
                        logger.warning(f"Feature check failed: {message}")
                        return fallback_response

                # Feature is enabled, execute function
                return func(*args, **kwargs)

            except Exception as e:
                logger.error(f"Feature toggle check failed for '{feature_name}': {e}")

                if raise_exception:
                    raise
                else:
                    return fallback_response

        return wrapper

    return decorator


def feature_gate(feature_name: str, user_role: str = "CHILD"):
    """
    Decorator for feature gating with simple boolean check

    Args:
        feature_name: Name of the feature to check
        user_role: User role for permission checking

    Returns:
        True if feature is enabled, False otherwise

    Usage:
        @feature_gate("real_time_analysis")
        def analyze_speech(audio_data):
            if not analyze_speech.enabled:
                return {"error": "Real-time analysis disabled"}
            # Process normally
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add enabled property to function
            wrapper.enabled = is_feature_enabled(feature_name, user_role)
            wrapper.feature_name = feature_name
            wrapper.user_role = user_role

            return func(*args, **kwargs)

        # Initialize enabled state
        wrapper.enabled = is_feature_enabled(feature_name, user_role)
        wrapper.feature_name = feature_name
        wrapper.user_role = user_role

        return wrapper

    return decorator


class FeatureToggleService:
    """
    Service class for checking feature toggles in services that need multiple checks
    """

    def __init__(self, user_role: str = "CHILD"):
        """
        Initialize with default user role

        Args:
            user_role: Default user role for feature checks
        """
        self.user_role = user_role

    def is_enabled(self, feature_name: str, user_role: Optional[str] = None) -> bool:
        """Check if a feature is enabled for the given user role"""
        role = user_role or self.user_role
        return is_feature_enabled(feature_name, role)

    def require(self, feature_name: str, user_role: Optional[str] = None):
        """
        Check if feature is enabled, raise exception if not

        Args:
            feature_name: Name of the feature to check
            user_role: User role (uses default if not provided)

        Raises:
            HTTPException: If feature is disabled
        """
        role = user_role or self.user_role

        if not is_feature_enabled(feature_name, role):
            from fastapi import HTTPException

            raise HTTPException(
                status_code=403,
                detail=f"Feature '{feature_name}' is disabled or not available for role '{role}'",
            )

    def get_enabled_features(
        self, feature_list: list, user_role: Optional[str] = None
    ) -> list:
        """
        Filter a list of features to only include enabled ones

        Args:
            feature_list: List of feature names to check
            user_role: User role (uses default if not provided)

        Returns:
            List of enabled feature names
        """
        role = user_role or self.user_role
        return [
            feature for feature in feature_list if is_feature_enabled(feature, role)
        ]

    def conditional_execute(
        self,
        feature_name: str,
        func: Callable,
        fallback: Any = None,
        user_role: Optional[str] = None,
    ):
        """
        Execute function only if feature is enabled

        Args:
            feature_name: Name of the feature to check
            func: Function to execute if enabled
            fallback: Value to return if disabled
            user_role: User role (uses default if not provided)

        Returns:
            Function result if enabled, fallback if disabled
        """
        role = user_role or self.user_role

        if is_feature_enabled(feature_name, role):
            try:
                return func()
            except Exception as e:
                logger.error(f"Error executing feature '{feature_name}' function: {e}")
                return fallback
        else:
            logger.debug(
                f"Feature '{feature_name}' disabled for role '{role}', returning fallback"
            )
            return fallback


# Convenience functions for common use cases
def check_content_processing(user_role: str = "CHILD") -> bool:
    """Check if content processing is enabled"""
    return is_feature_enabled("content_processing", user_role)


def check_real_time_analysis(user_role: str = "CHILD") -> bool:
    """Check if real-time analysis is enabled"""
    return is_feature_enabled("real_time_analysis", user_role)


def check_tutor_modes(user_role: str = "CHILD") -> bool:
    """Check if tutor modes are enabled"""
    return is_feature_enabled("tutor_modes", user_role)


def check_scenario_modes(user_role: str = "CHILD") -> bool:
    """Check if scenario modes are enabled"""
    return is_feature_enabled("scenario_modes", user_role)


def check_speech_recognition(user_role: str = "CHILD") -> bool:
    """Check if speech recognition is enabled"""
    return is_feature_enabled("speech_recognition", user_role)


def check_text_to_speech(user_role: str = "CHILD") -> bool:
    """Check if text-to-speech is enabled"""
    return is_feature_enabled("text_to_speech", user_role)


# Feature toggle context manager
class FeatureContext:
    """Context manager for feature-gated code blocks"""

    def __init__(
        self, feature_name: str, user_role: str = "CHILD", silent: bool = True
    ):
        """
        Initialize feature context

        Args:
            feature_name: Name of the feature to check
            user_role: User role for permission checking
            silent: If True, silently skip disabled features instead of raising
        """
        self.feature_name = feature_name
        self.user_role = user_role
        self.silent = silent
        self.enabled = False

    def __enter__(self):
        """Enter the context - check if feature is enabled"""
        self.enabled = is_feature_enabled(self.feature_name, self.user_role)

        if not self.enabled and not self.silent:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=403, detail=f"Feature '{self.feature_name}' is disabled"
            )

        return self.enabled

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context"""


# Usage example:
# with FeatureContext("content_processing") as enabled:
#     if enabled:
#         # Code only runs if feature is enabled
#         process_content()
