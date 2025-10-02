"""
User Profile Management Service for AI Language Tutor App

This module provides comprehensive user management functionality including:
- User profile CRUD operations
- Family account management
- User preferences and settings
- Learning progress tracking
- Privacy and safety controls
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func
import json

from app.database.config import get_db_session
from app.database.local_config import local_db_manager
from app.models.database import (
    User,
    Language,
    LearningProgress,
    VocabularyItem,
    UserRole,
    LanguageCode,
    LearningStatus,
    user_languages,
)
from app.models.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfile,
    LearningProgressCreate,
    LearningProgressUpdate,
    LearningProgressResponse,
    UserRoleEnum,
    LanguageEnum,
    LearningStatusEnum,
)
from app.services.auth import auth_service


logger = logging.getLogger(__name__)


class UserProfileService:
    """Service for managing user profiles and related data"""

    def __init__(self):
        self.auth_service = auth_service

    def _get_session(self):
        """Helper to get database session from generator"""
        return next(get_db_session())

    # User CRUD Operations
    def create_user(
        self, user_data: UserCreate, password: Optional[str] = None
    ) -> UserResponse:
        """
        Create a new user profile

        Args:
            user_data: User creation data
            password: Optional password (for parent accounts)

        Returns:
            Created user data
        """
        session = self._get_session()
        try:
            # Check if user_id already exists
            existing_user = (
                session.query(User).filter(User.user_id == user_data.user_id).first()
            )
            if existing_user:
                raise ValueError(f"User ID {user_data.user_id} already exists")

            # Check if email already exists (if provided)
            if user_data.email:
                existing_email = (
                    session.query(User).filter(User.email == user_data.email).first()
                )
                if existing_email:
                    raise ValueError(f"Email {user_data.email} already exists")

            # Create user record
            user = User(
                user_id=user_data.user_id,
                username=user_data.username,
                email=user_data.email,
                role=UserRole(user_data.role.value.upper()),
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                ui_language=user_data.ui_language,
                timezone=user_data.timezone,
                preferences=user_data.preferences or {},
                privacy_settings=user_data.privacy_settings or {},
                is_active=True,
                is_verified=False,
            )

            # Set password hash if provided
            if password:
                user.password_hash = self.auth_service.hash_password(password)
            elif user_data.role == UserRoleEnum.CHILD:
                # Generate PIN for child accounts
                pin = self.auth_service.generate_child_pin()
                user.password_hash = self.auth_service.hash_pin(pin)
                logger.info(f"Generated PIN for child user {user_data.user_id}: {pin}")

            session.add(user)
            session.flush()  # Get the ID

            # Create local profile copy
            local_db_manager.add_user_profile(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                preferences=user.preferences,
            )

            session.commit()

            # Convert to response schema - need to convert role from DB enum (UPPERCASE) to API enum (lowercase)
            user_dict = {
                "id": user.id,
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": UserRoleEnum(
                    user.role.value.lower()
                ),  # Convert ADMIN -> admin, CHILD -> child, PARENT -> parent
                "first_name": user.first_name,
                "last_name": user.last_name,
                "ui_language": user.ui_language,
                "timezone": user.timezone,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
            user_response = UserResponse(**user_dict)

            logger.info(f"User created successfully: {user.user_id}")
            return user_response

        except IntegrityError as e:
            session.rollback()
            logger.error(f"Database integrity error creating user: {e}")
            raise ValueError("User creation failed due to data constraints")
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating user: {e}")
            raise
        finally:
            session.close()

    def get_user_by_id(
        self, user_id: str, include_sensitive: bool = False
    ) -> Optional[UserResponse]:
        """
        Get user by user_id

        Args:
            user_id: User identifier
            include_sensitive: Whether to include sensitive data

        Returns:
            User data or None if not found
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return None

            user_data = user.to_dict(include_sensitive=include_sensitive)
            return UserResponse(**user_data)

        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
        finally:
            session.close()

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get complete user profile with learning data

        Args:
            user_id: User identifier

        Returns:
            Complete user profile
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return None

            # Get user languages
            languages = []
            for lang_assoc in (
                session.query(user_languages)
                .filter(user_languages.c.user_id == user.id)
                .all()
            ):
                languages.append(
                    {
                        "language": lang_assoc.language,
                        "proficiency_level": lang_assoc.proficiency_level,
                        "is_primary": lang_assoc.is_primary,
                        "created_at": lang_assoc.created_at.isoformat()
                        if lang_assoc.created_at
                        else None,
                    }
                )

            # Get learning progress
            progress_records = (
                session.query(LearningProgress)
                .filter(LearningProgress.user_id == user.id)
                .all()
            )

            learning_progress = [prog.to_dict() for prog in progress_records]

            # Get conversation and study statistics
            total_conversations = len(user.conversations)
            total_study_time = sum(
                prog.total_study_time_minutes for prog in progress_records
            )

            # Build profile
            profile_data = user.to_dict(include_sensitive=False)
            profile_data.update(
                {
                    "languages": languages,
                    "learning_progress": learning_progress,
                    "total_conversations": total_conversations,
                    "total_study_time_minutes": total_study_time,
                }
            )

            return UserProfile(**profile_data)

        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            return None
        finally:
            session.close()

    def update_user(
        self, user_id: str, user_updates: UserUpdate
    ) -> Optional[UserResponse]:
        """
        Update user profile

        Args:
            user_id: User identifier
            user_updates: Updated user data

        Returns:
            Updated user data
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return None

            # Update fields if provided
            update_fields = user_updates.dict(exclude_unset=True)
            for field, value in update_fields.items():
                if hasattr(user, field) and value is not None:
                    setattr(user, field, value)

            user.updated_at = datetime.now(timezone.utc)
            session.commit()

            # Update local profile
            local_db_manager.add_user_profile(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                preferences=user.preferences,
            )

            user_response = UserResponse.from_orm(user)
            logger.info(f"User updated successfully: {user_id}")
            return user_response

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating user {user_id}: {e}")
            return None
        finally:
            session.close()

    def delete_user(self, user_id: str, soft_delete: bool = True) -> bool:
        """
        Delete user account

        Args:
            user_id: User identifier
            soft_delete: Whether to soft delete (deactivate) or hard delete

        Returns:
            Success status
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False

            if soft_delete:
                # Soft delete - deactivate user
                user.is_active = False
                user.updated_at = datetime.now(timezone.utc)
                session.commit()
                logger.info(f"User soft deleted: {user_id}")
            else:
                # Hard delete - remove all user data
                session.delete(user)
                session.commit()

                # Delete local data
                local_db_manager.delete_user_data_locally(user_id)

                logger.info(f"User hard deleted: {user_id}")

            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
        finally:
            session.close()

    def list_users(
        self,
        role: Optional[UserRoleEnum] = None,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[UserResponse]:
        """
        List users with optional filtering

        Args:
            role: Filter by user role
            is_active: Filter by active status
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of users
        """
        session = self._get_session()
        try:
            query = session.query(User)

            # Apply filters
            if role:
                query = query.filter(User.role == UserRole(role.value))
            if is_active is not None:
                query = query.filter(User.is_active == is_active)

            # Apply pagination
            users = query.offset(offset).limit(limit).all()

            return [UserResponse.from_orm(user) for user in users]

        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []
        finally:
            session.close()

    # Language Management
    def add_user_language(
        self,
        user_id: str,
        language: str,
        proficiency_level: int = 1,
        is_primary: bool = False,
    ) -> bool:
        """
        Add a language to user's profile

        Args:
            user_id: User identifier
            language: Language code
            proficiency_level: Proficiency level (1-10)
            is_primary: Whether this is the primary language

        Returns:
            Success status
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False

            # Check if language already exists for user
            existing = (
                session.query(user_languages)
                .filter(
                    and_(
                        user_languages.c.user_id == user.id,
                        user_languages.c.language == language,
                    )
                )
                .first()
            )

            if existing:
                # Update existing
                session.execute(
                    user_languages.update()
                    .where(
                        and_(
                            user_languages.c.user_id == user.id,
                            user_languages.c.language == language,
                        )
                    )
                    .values(proficiency_level=proficiency_level, is_primary=is_primary)
                )
            else:
                # Insert new
                session.execute(
                    user_languages.insert().values(
                        user_id=user.id,
                        language=language,
                        proficiency_level=proficiency_level,
                        is_primary=is_primary,
                    )
                )

            # Ensure only one primary language
            if is_primary:
                session.execute(
                    user_languages.update()
                    .where(
                        and_(
                            user_languages.c.user_id == user.id,
                            user_languages.c.language != language,
                        )
                    )
                    .values(is_primary=False)
                )

            session.commit()
            logger.info(f"Language {language} added for user {user_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error adding language for user {user_id}: {e}")
            return False
        finally:
            session.close()

    def get_user_languages(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's languages

        Args:
            user_id: User identifier

        Returns:
            List of user languages
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return []

            languages = (
                session.query(user_languages)
                .filter(user_languages.c.user_id == user.id)
                .all()
            )

            return [
                {
                    "language": lang.language,
                    "proficiency_level": lang.proficiency_level,
                    "is_primary": lang.is_primary,
                    "created_at": lang.created_at.isoformat()
                    if lang.created_at
                    else None,
                }
                for lang in languages
            ]

        except Exception as e:
            logger.error(f"Error getting languages for user {user_id}: {e}")
            return []
        finally:
            session.close()

    def remove_user_language(self, user_id: str, language: str) -> bool:
        """
        Remove a language from user's profile

        Args:
            user_id: User identifier
            language: Language code

        Returns:
            Success status
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False

            session.execute(
                user_languages.delete().where(
                    and_(
                        user_languages.c.user_id == user.id,
                        user_languages.c.language == language,
                    )
                )
            )

            session.commit()
            logger.info(f"Language {language} removed for user {user_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error removing language for user {user_id}: {e}")
            return False
        finally:
            session.close()

    # Learning Progress Management
    def create_learning_progress(
        self, user_id: str, progress_data: LearningProgressCreate
    ) -> Optional[LearningProgressResponse]:
        """
        Create learning progress record

        Args:
            user_id: User identifier
            progress_data: Learning progress data

        Returns:
            Created progress record
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return None

            # Check if progress already exists for this skill
            existing = (
                session.query(LearningProgress)
                .filter(
                    and_(
                        LearningProgress.user_id == user.id,
                        LearningProgress.language == progress_data.language,
                        LearningProgress.skill_type == progress_data.skill_type,
                    )
                )
                .first()
            )

            if existing:
                raise ValueError(
                    f"Learning progress already exists for {progress_data.skill_type} in {progress_data.language}"
                )

            progress = LearningProgress(
                user_id=user.id,
                language=progress_data.language,
                skill_type=progress_data.skill_type,
                current_level=progress_data.current_level,
                target_level=progress_data.target_level,
                status=LearningStatus.IN_PROGRESS,
                goals=progress_data.goals or {},
                started_at=datetime.now(timezone.utc),
            )

            session.add(progress)
            session.commit()

            return LearningProgressResponse.from_orm(progress)

        except Exception as e:
            session.rollback()
            logger.error(f"Error creating learning progress for user {user_id}: {e}")
            return None
        finally:
            session.close()

    def update_learning_progress(
        self,
        user_id: str,
        language: str,
        skill_type: str,
        progress_updates: LearningProgressUpdate,
    ) -> Optional[LearningProgressResponse]:
        """
        Update learning progress

        Args:
            user_id: User identifier
            language: Language code
            skill_type: Skill type
            progress_updates: Updated progress data

        Returns:
            Updated progress record
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return None

            progress = (
                session.query(LearningProgress)
                .filter(
                    and_(
                        LearningProgress.user_id == user.id,
                        LearningProgress.language == language,
                        LearningProgress.skill_type == skill_type,
                    )
                )
                .first()
            )

            if not progress:
                return None

            # Update fields
            update_fields = progress_updates.dict(exclude_unset=True)
            for field, value in update_fields.items():
                if hasattr(progress, field) and value is not None:
                    setattr(progress, field, value)

            progress.last_activity = datetime.now(timezone.utc)
            progress.updated_at = datetime.now(timezone.utc)

            session.commit()

            return LearningProgressResponse.from_orm(progress)

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating learning progress for user {user_id}: {e}")
            return None
        finally:
            session.close()

    def get_learning_progress(
        self, user_id: str, language: Optional[str] = None
    ) -> List[LearningProgressResponse]:
        """
        Get learning progress for user

        Args:
            user_id: User identifier
            language: Optional language filter

        Returns:
            List of learning progress records
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return []

            query = session.query(LearningProgress).filter(
                LearningProgress.user_id == user.id
            )

            if language:
                query = query.filter(LearningProgress.language == language)

            progress_records = query.all()

            return [
                LearningProgressResponse.from_orm(record) for record in progress_records
            ]

        except Exception as e:
            logger.error(f"Error getting learning progress for user {user_id}: {e}")
            return []
        finally:
            session.close()

    # User Preferences and Settings
    def update_user_preferences(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> bool:
        """
        Update user preferences

        Args:
            user_id: User identifier
            preferences: Preferences dictionary

        Returns:
            Success status
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False

            # Merge with existing preferences
            current_prefs = user.preferences or {}
            current_prefs.update(preferences)

            user.preferences = current_prefs
            user.updated_at = datetime.now(timezone.utc)

            session.commit()

            # Update local copy
            local_db_manager.add_user_profile(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                preferences=user.preferences,
            )

            logger.info(f"Preferences updated for user {user_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating preferences for user {user_id}: {e}")
            return False
        finally:
            session.close()

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences

        Args:
            user_id: User identifier

        Returns:
            User preferences dictionary
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return {}

            return user.preferences or {}

        except Exception as e:
            logger.error(f"Error getting preferences for user {user_id}: {e}")
            return {}
        finally:
            session.close()

    # Family Management
    def get_family_members(self, parent_user_id: str) -> List[UserResponse]:
        """
        Get family members for a parent account

        Args:
            parent_user_id: Parent user identifier

        Returns:
            List of family members
        """
        session = self._get_session()
        try:
            # For this implementation, we'll look for users with similar email domain
            # or users created by the same parent (this could be enhanced with explicit family relationships)

            parent = session.query(User).filter(User.user_id == parent_user_id).first()
            if not parent or parent.role != UserRole.PARENT:
                return []

            # Simple implementation: return child users created around the same time or with similar preferences
            # In a real implementation, you'd have a family relationship table

            family_members = (
                session.query(User)
                .filter(
                    and_(
                        User.role == UserRole.CHILD,
                        User.is_active == True,
                        User.id != parent.id,
                    )
                )
                .limit(10)
                .all()
            )  # Simplified for demo

            return [UserResponse.from_orm(user) for user in family_members]

        except Exception as e:
            logger.error(f"Error getting family members for {parent_user_id}: {e}")
            return []
        finally:
            session.close()

    # User Statistics
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get user activity statistics

        Args:
            user_id: User identifier

        Returns:
            User statistics dictionary
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return {}

            # Get basic counts
            total_conversations = len(user.conversations)
            total_documents = len(user.documents)
            total_vocabulary = len(user.vocabulary_lists)

            # Get learning progress summary
            progress_records = (
                session.query(LearningProgress)
                .filter(LearningProgress.user_id == user.id)
                .all()
            )

            total_study_time = sum(p.total_study_time_minutes for p in progress_records)
            total_sessions = sum(p.sessions_completed for p in progress_records)

            # Recent activity (last 30 days)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_conversations = (
                session.query(func.count())
                .filter(
                    and_(
                        user.conversations.any(),
                        user.conversations.filter(
                            lambda c: c.started_at >= thirty_days_ago
                        ).exists(),
                    )
                )
                .scalar()
            )

            return {
                "total_conversations": total_conversations,
                "total_documents": total_documents,
                "total_vocabulary_items": total_vocabulary,
                "total_study_time_minutes": total_study_time,
                "total_sessions_completed": total_sessions,
                "recent_conversations_30d": recent_conversations or 0,
                "languages_learning": len(self.get_user_languages(user_id)),
                "account_age_days": (datetime.now(timezone.utc) - user.created_at).days,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }

        except Exception as e:
            logger.error(f"Error getting statistics for user {user_id}: {e}")
            return {}
        finally:
            session.close()


# Global user profile service
user_service = UserProfileService()


# Convenience functions
def create_user(user_data: UserCreate, password: Optional[str] = None) -> UserResponse:
    """Create a new user"""
    return user_service.create_user(user_data, password)


def get_user_by_id(user_id: str) -> Optional[UserResponse]:
    """Get user by ID"""
    return user_service.get_user_by_id(user_id)


def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """Get complete user profile"""
    return user_service.get_user_profile(user_id)


def update_user(user_id: str, updates: UserUpdate) -> Optional[UserResponse]:
    """Update user profile"""
    return user_service.update_user(user_id, updates)
