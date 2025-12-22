"""
Scenario Builder Service
AI Language Tutor App - Session 131

Provides comprehensive scenario management for user-generated content:
- Create, read, update, delete scenarios
- Template-based scenario creation
- Scenario duplication and customization
- Public/private sharing
- Ownership and permission management
- Validation of scenario structure

This service enables users to create unlimited custom scenarios beyond
the 30 system scenarios, fostering community-driven content creation.
"""

import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from app.models.database import Scenario, ScenarioPhase
from app.services.scenario_ai_service import get_scenario_ai_service
from app.services.scenario_models import ScenarioCategory
from app.services.scenario_templates import (
    get_all_templates,
    get_template_by_id,
    get_templates_by_category,
)

logger = logging.getLogger(__name__)


class ScenarioBuilderService:
    """Service for user scenario creation and management"""

    def __init__(self, db: Session):
        """
        Initialize the service with a database session

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.ai_service = get_scenario_ai_service()

    def _generate_scenario_id(self, title: str, user_id: int) -> str:
        """Generate unique scenario ID from title and user ID"""
        timestamp = datetime.now().isoformat()
        # Create slug from title
        slug = title.lower().replace(" ", "_")[:30]
        unique_string = f"{slug}_{user_id}_{timestamp}"
        hash_suffix = hashlib.md5(unique_string.encode()).hexdigest()[:8]
        return f"{slug}_{hash_suffix}"

    def _generate_phase_id(
        self, scenario_id: str, phase_name: str, phase_number: int
    ) -> str:
        """Generate unique phase ID"""
        slug = phase_name.lower().replace(" ", "_")[:20]
        return f"{scenario_id}_phase{phase_number}_{slug}"

    # ============================================================================
    # CRUD OPERATIONS
    # ============================================================================

    async def create_scenario(self, user_id: int, scenario_data: Dict) -> Scenario:
        """
        Create new user scenario

        Args:
            user_id: ID of the user creating the scenario
            scenario_data: Dictionary containing scenario details

        Returns:
            Created Scenario object

        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            # Validate data
            is_valid, errors = self.validate_scenario_data(scenario_data)
            if not is_valid:
                raise ValueError(f"Scenario validation failed: {', '.join(errors)}")

            # Generate unique scenario ID
            scenario_id = self._generate_scenario_id(scenario_data["title"], user_id)

            # Create scenario record
            scenario = Scenario(
                scenario_id=scenario_id,
                title=scenario_data["title"],
                description=scenario_data.get("description", ""),
                category=scenario_data["category"],
                difficulty=scenario_data["difficulty"],
                estimated_duration=scenario_data["estimated_duration"],
                language=scenario_data.get("language", "en"),
                user_role=scenario_data.get("user_role"),
                ai_role=scenario_data.get("ai_role"),
                setting=scenario_data.get("setting"),
                created_by=user_id,
                is_system_scenario=False,
                is_public=scenario_data.get("is_public", False),
                prerequisites=scenario_data.get("prerequisites", []),
                learning_outcomes=scenario_data.get("learning_outcomes", []),
                vocabulary_focus=scenario_data.get("vocabulary_focus", []),
                cultural_context=scenario_data.get("cultural_context", {}),
            )

            self.db.add(scenario)
            self.db.flush()  # Get the scenario.id before creating phases

            # Create phases
            for idx, phase_data in enumerate(scenario_data["phases"]):
                phase_id = self._generate_phase_id(
                    scenario_id, phase_data["name"], idx + 1
                )

                phase = ScenarioPhase(
                    scenario_id=scenario.id,
                    phase_number=idx + 1,
                    phase_id=phase_id,
                    name=phase_data["name"],
                    description=phase_data.get("description", ""),
                    expected_duration_minutes=phase_data.get(
                        "expected_duration_minutes", 5
                    ),
                    key_vocabulary=phase_data.get("key_vocabulary", []),
                    essential_phrases=phase_data.get("essential_phrases", []),
                    learning_objectives=phase_data.get("learning_objectives", []),
                    success_criteria=phase_data.get("success_criteria", []),
                    cultural_notes=phase_data.get("cultural_notes"),
                )
                self.db.add(phase)

            self.db.commit()
            self.db.refresh(scenario)

            logger.info(f"Created scenario {scenario_id} for user {user_id}")
            return scenario

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating scenario: {e}")
            raise

    async def get_scenario(
        self, scenario_id: str, user_id: Optional[int] = None
    ) -> Optional[Scenario]:
        """
        Get scenario by ID with permission check

        Args:
            scenario_id: Scenario identifier
            user_id: User ID for permission check (optional)

        Returns:
            Scenario object if found and accessible, None otherwise
        """
        try:
            scenario = (
                self.db.query(Scenario)
                .filter(Scenario.scenario_id == scenario_id)
                .first()
            )

            if not scenario:
                return None

            # Permission check: scenario must be public, system, or owned by user
            if user_id is not None:
                if not (
                    scenario.is_public
                    or scenario.is_system_scenario
                    or scenario.created_by == user_id
                ):
                    return None

            return scenario

        except Exception as e:
            logger.error(f"Error retrieving scenario {scenario_id}: {e}")
            raise

    async def update_scenario(
        self, scenario_id: str, user_id: int, updates: Dict
    ) -> Scenario:
        """
        Update existing scenario

        Args:
            scenario_id: Scenario identifier
            user_id: User ID (must own the scenario)
            updates: Dictionary of fields to update

        Returns:
            Updated Scenario object

        Raises:
            ValueError: If user doesn't own scenario or validation fails
            Exception: If database operation fails
        """
        try:
            # Get scenario and check ownership
            scenario = await self.get_scenario(scenario_id, user_id)
            if not scenario:
                raise ValueError("Scenario not found")

            if scenario.created_by != user_id:
                raise ValueError("You don't own this scenario")

            if scenario.is_system_scenario:
                raise ValueError("Cannot edit system scenarios")

            # Validate updates if phases are being changed
            if "phases" in updates:
                is_valid, errors = self.validate_scenario_data(
                    {**scenario.to_dict(), **updates}
                )
                if not is_valid:
                    raise ValueError(f"Validation failed: {', '.join(errors)}")

            # Update scalar fields
            scalar_fields = [
                "title",
                "description",
                "difficulty",
                "estimated_duration",
                "user_role",
                "ai_role",
                "setting",
                "is_public",
                "prerequisites",
                "learning_outcomes",
                "vocabulary_focus",
                "cultural_context",
            ]

            for field in scalar_fields:
                if field in updates:
                    setattr(scenario, field, updates[field])

            # Update phases if provided
            if "phases" in updates:
                # Delete existing phases
                self.db.query(ScenarioPhase).filter(
                    ScenarioPhase.scenario_id == scenario.id
                ).delete()

                # Create new phases
                for idx, phase_data in enumerate(updates["phases"]):
                    phase_id = self._generate_phase_id(
                        scenario_id, phase_data["name"], idx + 1
                    )

                    phase = ScenarioPhase(
                        scenario_id=scenario.id,
                        phase_number=idx + 1,
                        phase_id=phase_id,
                        name=phase_data["name"],
                        description=phase_data.get("description", ""),
                        expected_duration_minutes=phase_data.get(
                            "expected_duration_minutes", 5
                        ),
                        key_vocabulary=phase_data.get("key_vocabulary", []),
                        essential_phrases=phase_data.get("essential_phrases", []),
                        learning_objectives=phase_data.get("learning_objectives", []),
                        success_criteria=phase_data.get("success_criteria", []),
                        cultural_notes=phase_data.get("cultural_notes"),
                    )
                    self.db.add(phase)

            scenario.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(scenario)

            logger.info(f"Updated scenario {scenario_id}")
            return scenario

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating scenario {scenario_id}: {e}")
            raise

    async def delete_scenario(self, scenario_id: str, user_id: int) -> bool:
        """
        Delete scenario (cascade deletes phases)

        Args:
            scenario_id: Scenario identifier
            user_id: User ID (must own the scenario)

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If user doesn't own scenario or it's a system scenario
        """
        try:
            # Get scenario and check ownership
            scenario = await self.get_scenario(scenario_id, user_id)
            if not scenario:
                raise ValueError("Scenario not found")

            if scenario.created_by != user_id:
                raise ValueError("You don't own this scenario")

            if scenario.is_system_scenario:
                raise ValueError("Cannot delete system scenarios")

            # Delete scenario (phases auto-deleted by cascade)
            self.db.delete(scenario)
            self.db.commit()

            logger.info(f"Deleted scenario {scenario_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting scenario {scenario_id}: {e}")
            raise

    # ============================================================================
    # LISTING & DISCOVERY
    # ============================================================================

    async def get_user_scenarios(
        self, user_id: int, include_public: bool = False
    ) -> List[Scenario]:
        """
        Get user's scenarios (optionally include public)

        Args:
            user_id: User ID
            include_public: Whether to include public scenarios

        Returns:
            List of Scenario objects
        """
        try:
            query = self.db.query(Scenario)

            if include_public:
                query = query.filter(
                    or_(Scenario.created_by == user_id, Scenario.is_public == True)
                )
            else:
                query = query.filter(Scenario.created_by == user_id)

            scenarios = query.order_by(desc(Scenario.created_at)).all()
            return scenarios

        except Exception as e:
            logger.error(f"Error getting user scenarios: {e}")
            raise

    async def get_public_scenarios(
        self, category: Optional[str] = None, difficulty: Optional[str] = None
    ) -> List[Scenario]:
        """
        Get publicly shared scenarios

        Args:
            category: Filter by category (optional)
            difficulty: Filter by difficulty (optional)

        Returns:
            List of public Scenario objects
        """
        try:
            query = self.db.query(Scenario).filter(Scenario.is_public == True)

            if category:
                query = query.filter(Scenario.category == category)

            if difficulty:
                query = query.filter(Scenario.difficulty == difficulty)

            scenarios = query.order_by(desc(Scenario.created_at)).all()
            return scenarios

        except Exception as e:
            logger.error(f"Error getting public scenarios: {e}")
            raise

    async def get_system_scenarios(self) -> List[Scenario]:
        """
        Get system scenarios (the original 30+)

        Returns:
            List of system Scenario objects
        """
        try:
            scenarios = (
                self.db.query(Scenario)
                .filter(Scenario.is_system_scenario == True)
                .order_by(Scenario.category, Scenario.title)
                .all()
            )
            return scenarios

        except Exception as e:
            logger.error(f"Error getting system scenarios: {e}")
            raise

    # ============================================================================
    # TEMPLATE MANAGEMENT
    # ============================================================================

    async def get_scenario_templates(self) -> List[Dict]:
        """
        Get all scenario templates (1 per category)

        Returns:
            List of template dictionaries
        """
        return get_all_templates()

    async def create_from_template(
        self, template_id: str, user_id: int, customization: Dict
    ) -> Scenario:
        """
        Create scenario from template

        Args:
            template_id: Template identifier
            user_id: User ID who will own the scenario
            customization: Dictionary with custom title, description, etc.

        Returns:
            Created Scenario object

        Raises:
            ValueError: If template not found
        """
        try:
            # Get template
            template = get_template_by_id(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")

            # Apply customization
            scenario_data = {**template}

            # Remove template_id from data
            scenario_data.pop("template_id", None)

            # Apply custom overrides
            if "title" in customization:
                scenario_data["title"] = customization["title"]
            if "description" in customization:
                scenario_data["description"] = customization["description"]
            if "difficulty" in customization:
                scenario_data["difficulty"] = customization["difficulty"]

            # Create scenario from template
            scenario = await self.create_scenario(user_id, scenario_data)

            logger.info(
                f"Created scenario from template {template_id} for user {user_id}"
            )
            return scenario

        except Exception as e:
            logger.error(f"Error creating from template {template_id}: {e}")
            raise

    # ============================================================================
    # DUPLICATION
    # ============================================================================

    async def duplicate_scenario(
        self, scenario_id: str, user_id: int, new_title: str
    ) -> Scenario:
        """
        Duplicate existing scenario for customization

        Args:
            scenario_id: Source scenario ID
            user_id: User ID who will own the copy
            new_title: Title for the duplicated scenario

        Returns:
            New Scenario object

        Raises:
            ValueError: If source scenario not found
        """
        try:
            # Get source scenario (allow public or system scenarios)
            source = await self.get_scenario(scenario_id, user_id)
            if not source:
                raise ValueError("Source scenario not found or not accessible")

            # Create new scenario data
            scenario_data = {
                "title": new_title,
                "description": source.description,
                "category": source.category,
                "difficulty": source.difficulty,
                "estimated_duration": source.estimated_duration,
                "language": source.language,
                "user_role": source.user_role,
                "ai_role": source.ai_role,
                "setting": source.setting,
                "is_public": False,  # Duplicates start as private
                "prerequisites": source.prerequisites,
                "learning_outcomes": source.learning_outcomes,
                "vocabulary_focus": source.vocabulary_focus,
                "cultural_context": source.cultural_context,
                "phases": [
                    {
                        "name": phase.name,
                        "description": phase.description,
                        "expected_duration_minutes": phase.expected_duration_minutes,
                        "key_vocabulary": phase.key_vocabulary,
                        "essential_phrases": phase.essential_phrases,
                        "learning_objectives": phase.learning_objectives,
                        "success_criteria": phase.success_criteria,
                        "cultural_notes": phase.cultural_notes,
                    }
                    for phase in sorted(source.phases, key=lambda p: p.phase_number)
                ],
            }

            # Create duplicate
            duplicate = await self.create_scenario(user_id, scenario_data)
            logger.info(f"Duplicated scenario {scenario_id} to {duplicate.scenario_id}")
            return duplicate

        except Exception as e:
            logger.error(f"Error duplicating scenario {scenario_id}: {e}")
            raise

    # ============================================================================
    # VALIDATION
    # ============================================================================

    def validate_scenario_data(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate scenario structure and content

        Args:
            data: Scenario data dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Required fields
        if not data.get("title") or len(data["title"]) < 3:
            errors.append("Title must be at least 3 characters")

        if not data.get("category"):
            errors.append("Category is required")
        elif data["category"] not in [cat.value for cat in ScenarioCategory]:
            errors.append(f"Invalid category: {data['category']}")

        if not data.get("difficulty"):
            errors.append("Difficulty is required")
        elif data["difficulty"] not in ["beginner", "intermediate", "advanced"]:
            errors.append("Difficulty must be beginner, intermediate, or advanced")

        # Duration validation
        duration = data.get("estimated_duration", 0)
        if not isinstance(duration, int) or duration < 5 or duration > 60:
            errors.append("Duration must be between 5 and 60 minutes")

        # Phases validation
        phases = data.get("phases", [])
        if not phases or len(phases) < 2:
            errors.append("Scenario must have at least 2 phases")
        elif len(phases) > 6:
            errors.append("Scenario cannot have more than 6 phases")

        # Validate each phase
        for idx, phase in enumerate(phases):
            if not phase.get("name"):
                errors.append(f"Phase {idx + 1} must have a name")

            if not phase.get("description"):
                errors.append(f"Phase {idx + 1} must have a description")

            vocab = phase.get("key_vocabulary", [])
            if not vocab or len(vocab) < 3:
                errors.append(f"Phase {idx + 1} must have at least 3 vocabulary words")

            phrases = phase.get("essential_phrases", [])
            if not phrases or len(phrases) < 3:
                errors.append(f"Phase {idx + 1} must have at least 3 essential phrases")

            objectives = phase.get("learning_objectives", [])
            if not objectives:
                errors.append(f"Phase {idx + 1} must have learning objectives")

        # Overall vocabulary check
        total_vocab = sum(len(p.get("key_vocabulary", [])) for p in phases)
        if total_vocab < 5:
            errors.append("Scenario must have at least 5 total vocabulary words")

        # Overall phrases check
        total_phrases = sum(len(p.get("essential_phrases", [])) for p in phases)
        if total_phrases < 5:
            errors.append("Scenario must have at least 5 total essential phrases")

        return (len(errors) == 0, errors)

    # ============================================================================
    # AI-POWERED ENHANCEMENTS
    # ============================================================================

    async def assess_difficulty(
        self, scenario_data: Dict, tutor_profile: Optional[Dict] = None
    ) -> Dict:
        """
        AI-powered difficulty assessment for scenario

        Args:
            scenario_data: Scenario information
            tutor_profile: Optional tutor profile for context

        Returns:
            Assessment result with difficulty, confidence, and recommendations
        """
        try:
            result = await self.ai_service.assess_scenario_difficulty(
                scenario_data, tutor_profile
            )

            logger.info(
                f"AI difficulty assessment: {result.get('difficulty')} "
                f"(confidence: {result.get('confidence', 0):.2f})"
            )

            return result

        except Exception as e:
            logger.error(f"Error in difficulty assessment: {e}")
            # Return safe fallback
            return {
                "difficulty": "intermediate",
                "confidence": 0.5,
                "reasoning": "Error in AI assessment, defaulting to intermediate",
                "error": str(e),
            }

    async def auto_suggest_difficulty(
        self, scenario_data: Dict, tutor_profile: Optional[Dict] = None
    ) -> str:
        """
        Get AI-suggested difficulty level (simple wrapper)

        Returns just the difficulty string for convenience
        """
        assessment = await self.assess_difficulty(scenario_data, tutor_profile)
        return assessment.get("difficulty", "intermediate")

    # ============================================================================
    # PERMISSION CHECKS
    # ============================================================================

    def user_owns_scenario(self, user_id: int, scenario_id: str) -> bool:
        """
        Check if user owns scenario

        Args:
            user_id: User ID
            scenario_id: Scenario identifier

        Returns:
            True if user owns the scenario
        """
        try:
            scenario = (
                self.db.query(Scenario)
                .filter(
                    and_(
                        Scenario.scenario_id == scenario_id,
                        Scenario.created_by == user_id,
                    )
                )
                .first()
            )
            return scenario is not None

        except Exception as e:
            logger.error(f"Error checking scenario ownership: {e}")
            return False

    def can_edit_scenario(self, user_id: int, scenario_id: str) -> bool:
        """
        Check if user can edit scenario (owns + not system scenario)

        Args:
            user_id: User ID
            scenario_id: Scenario identifier

        Returns:
            True if user can edit the scenario
        """
        try:
            scenario = (
                self.db.query(Scenario)
                .filter(
                    and_(
                        Scenario.scenario_id == scenario_id,
                        Scenario.created_by == user_id,
                        Scenario.is_system_scenario == False,
                    )
                )
                .first()
            )
            return scenario is not None

        except Exception as e:
            logger.error(f"Error checking edit permission: {e}")
            return False
