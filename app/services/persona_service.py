"""
Persona Service - Manage AI tutor teaching personas

This service loads persona system prompts from markdown files and provides
them to AI services for personality-driven conversations.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class PersonaType(str, Enum):
    """Available tutor persona types"""

    GUIDING_CHALLENGER = "guiding_challenger"
    ENCOURAGING_COACH = "encouraging_coach"
    FRIENDLY_CONVERSATIONALIST = "friendly_conversational"
    EXPERT_SCHOLAR = "expert_scholar"
    CREATIVE_MENTOR = "creative_mentor"


class PersonaService:
    """Service for managing tutor persona system prompts"""

    # Persona metadata for API responses and UI
    PERSONA_METADATA = {
        PersonaType.GUIDING_CHALLENGER: {
            "name": "Guiding Challenger",
            "description": "A challenging, process-focused tutor that guides learners to discover answers instead of doing the work for them.",
            "key_traits": ["Challenging", "Process-focused", "Guides discovery"],
            "best_for": "Building resilience, problem-solving skills, and deep understanding",
            "file": "guiding_challenger.md",
        },
        PersonaType.ENCOURAGING_COACH: {
            "name": "Encouraging Coach",
            "description": "A supportive, motivational tutor that focuses on confidence and steady progress.",
            "key_traits": ["Supportive", "Motivational", "Builds confidence"],
            "best_for": "Learners who need positive reinforcement and step-by-step guidance",
            "file": "encouraging_coach.md",
        },
        PersonaType.FRIENDLY_CONVERSATIONALIST: {
            "name": "Friendly Conversationalist",
            "description": "An informal, approachable tutor that teaches through relaxed, back-and-forth dialogue.",
            "key_traits": ["Friendly", "Informal", "Conversational"],
            "best_for": "Learners who benefit from a low-pressure, talk-through-it style",
            "file": "friendly_conversational.md",
        },
        PersonaType.EXPERT_SCHOLAR: {
            "name": "Expert Scholar",
            "description": "A formal, academically rigorous tutor focused on precision and depth.",
            "key_traits": ["Formal", "Rigorous", "Precise"],
            "best_for": "Advanced learners who value technical accuracy and academic depth",
            "file": "expert_scholar.md",
        },
        PersonaType.CREATIVE_MENTOR: {
            "name": "Creative Mentor",
            "description": "An imaginative tutor that puts analogies, stories, and cross-domain connections at the center of teaching.",
            "key_traits": ["Creative", "Analogy-driven", "Imaginative"],
            "best_for": "Learners who understand best through metaphors and creative examples",
            "file": "creative_mentor.md",
        },
    }

    def __init__(self, personas_directory: Optional[Path] = None):
        """
        Initialize PersonaService

        Args:
            personas_directory: Path to personas directory (default: project_root/personas)
        """
        if personas_directory is None:
            # Default to project root / personas
            project_root = Path(__file__).parent.parent.parent
            personas_directory = project_root / "personas"

        self.personas_dir = Path(personas_directory)
        self._persona_cache: Dict[str, str] = {}
        self._global_guidelines: Optional[str] = None

        # Validate personas directory exists
        if not self.personas_dir.exists():
            logger.error(f"Personas directory not found: {self.personas_dir}")
            raise FileNotFoundError(f"Personas directory not found: {self.personas_dir}")

    def get_available_personas(self) -> List[Dict[str, any]]:
        """
        Get list of available personas with metadata

        Returns:
            List of persona metadata dictionaries
        """
        personas = []
        for persona_type, metadata in self.PERSONA_METADATA.items():
            personas.append({
                "persona_type": persona_type.value,
                "name": metadata["name"],
                "description": metadata["description"],
                "key_traits": metadata["key_traits"],
                "best_for": metadata["best_for"],
            })
        return personas

    def _load_file(self, filename: str) -> str:
        """
        Load content from a persona file

        Args:
            filename: Filename relative to personas directory

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        filepath = self.personas_dir / filename

        if not filepath.exists():
            logger.error(f"Persona file not found: {filepath}")
            raise FileNotFoundError(f"Persona file not found: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"Error reading persona file {filepath}: {e}")
            raise

    def get_global_guidelines(self) -> str:
        """
        Get global guidelines that apply to all personas

        Returns:
            Global guidelines content
        """
        if self._global_guidelines is None:
            self._global_guidelines = self._load_file("global_guidelines.md")

        return self._global_guidelines

    def get_persona_prompt(
        self,
        persona_type: PersonaType,
        subject: str = "",
        learner_level: str = "beginner",
        language: str = "en",
    ) -> str:
        """
        Get complete system prompt for a persona with dynamic field injection

        Args:
            persona_type: Type of persona to load
            subject: Subject or domain for the conversation (e.g., "calculus", "Python")
            learner_level: Learner proficiency level ("beginner", "intermediate", "advanced")
            language: Learner's preferred language code (e.g., "en", "es", "fr")

        Returns:
            Complete system prompt (global guidelines + persona + dynamic fields)
        """
        # Get persona filename from metadata
        if persona_type not in self.PERSONA_METADATA:
            logger.error(f"Invalid persona type: {persona_type}")
            raise ValueError(f"Invalid persona type: {persona_type}")

        persona_filename = self.PERSONA_METADATA[persona_type]["file"]

        # Load persona content (with caching)
        cache_key = f"{persona_type.value}"
        if cache_key not in self._persona_cache:
            persona_content = self._load_file(persona_filename)
            self._persona_cache[cache_key] = persona_content
        else:
            persona_content = self._persona_cache[cache_key]

        # Load global guidelines
        global_guidelines = self.get_global_guidelines()

        # Inject dynamic fields
        persona_with_fields = self._inject_dynamic_fields(
            persona_content,
            subject=subject,
            learner_level=learner_level,
            language=language,
        )

        # Combine global guidelines + persona-specific content
        complete_prompt = f"""{global_guidelines}

---

{persona_with_fields}"""

        return complete_prompt

    def _inject_dynamic_fields(
        self,
        content: str,
        subject: str,
        learner_level: str,
        language: str,
    ) -> str:
        """
        Inject dynamic field values into persona template

        Args:
            content: Persona template content with placeholders
            subject: Subject value
            learner_level: Learner level value
            language: Language code value

        Returns:
            Content with placeholders replaced by actual values
        """
        # Replace placeholder fields
        content = content.replace("{subject}", subject or "general learning")
        content = content.replace("{learner_level}", learner_level)
        content = content.replace("{language}", language)

        return content

    def get_persona_metadata(self, persona_type: PersonaType) -> Dict[str, any]:
        """
        Get metadata for a specific persona

        Args:
            persona_type: Type of persona

        Returns:
            Persona metadata dictionary
        """
        if persona_type not in self.PERSONA_METADATA:
            raise ValueError(f"Invalid persona type: {persona_type}")

        metadata = self.PERSONA_METADATA[persona_type].copy()
        metadata["persona_type"] = persona_type.value
        del metadata["file"]  # Don't expose internal file structure

        return metadata

    def validate_persona_type(self, persona_type_str: str) -> bool:
        """
        Validate if a persona type string is valid

        Args:
            persona_type_str: Persona type as string

        Returns:
            True if valid, False otherwise
        """
        try:
            PersonaType(persona_type_str)
            return True
        except ValueError:
            return False

    def get_default_persona(self) -> PersonaType:
        """
        Get the default persona for new users

        Returns:
            Default persona type
        """
        return PersonaType.FRIENDLY_CONVERSATIONALIST


# Global persona service instance
_persona_service: Optional[PersonaService] = None


def get_persona_service() -> PersonaService:
    """
    Get global PersonaService instance (singleton pattern)

    Returns:
        PersonaService instance
    """
    global _persona_service
    if _persona_service is None:
        _persona_service = PersonaService()
    return _persona_service
