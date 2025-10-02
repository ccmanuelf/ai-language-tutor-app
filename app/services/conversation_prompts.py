"""
System Prompt Generation for Conversation Management

This module provides pure functions for generating system prompts tailored to
different learning contexts and scenarios. These prompts guide the AI tutor's
behavior and ensure appropriate learning support.

Features:
- Learning-focused system prompts
- Scenario-based system prompts
- Customizable learning instructions
- Multi-language support
- Role-based conversation guidance

All functions are stateless and have no side effects.
"""

import logging
from typing import Dict, Any

from app.services.conversation_models import (
    ConversationContext,
    LearningFocus,
)

logger = logging.getLogger(__name__)


class PromptGenerator:
    """
    Generator for AI tutor system prompts.

    This class provides static methods to create context-appropriate system
    messages for different learning scenarios. All methods are pure functions
    with no side effects.
    """

    # Language name mappings for prompt generation
    LANGUAGE_NAMES = {
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
    }

    # Learning focus instructions
    FOCUS_INSTRUCTIONS = {
        LearningFocus.CONVERSATION: "Focus on natural conversation flow and practical language use.",
        LearningFocus.GRAMMAR: "Pay special attention to grammar correction and explanation.",
        LearningFocus.VOCABULARY: "Introduce new vocabulary and reinforce word usage.",
        LearningFocus.PRONUNCIATION: "Provide pronunciation guidance and phonetic help.",
        LearningFocus.READING: "Focus on reading comprehension and text analysis.",
        LearningFocus.WRITING: "Help improve writing skills and structure.",
    }

    @staticmethod
    def create_learning_system_message(context: ConversationContext) -> str:
        """
        Create a system message tailored for general language learning.

        This prompt configures the AI to act as a language tutor focused on
        the user's specific learning goals and proficiency level. It provides
        clear instructions for the AI's teaching approach.

        Args:
            context: ConversationContext containing learning parameters including
                    language, learning focus, vocabulary level, current topic,
                    and learning goals

        Returns:
            str: A formatted system prompt that instructs the AI tutor on how
                 to conduct the learning session

        Example:
            >>> context = ConversationContext(
            ...     language="es",
            ...     learning_focus=LearningFocus.CONVERSATION,
            ...     vocabulary_level="intermediate"
            ... )
            >>> prompt = PromptGenerator.create_learning_system_message(context)
            >>> "Spanish" in prompt
            True
        """
        language_name = PromptGenerator.LANGUAGE_NAMES.get(
            context.language, context.language
        )
        focus_instruction = PromptGenerator.FOCUS_INSTRUCTIONS.get(
            context.learning_focus, "Provide helpful language learning support."
        )

        system_message = f"""You are a helpful {language_name} language tutor. {focus_instruction}

Learning Context:
- Student's level: {context.vocabulary_level}
- Learning focus: {context.learning_focus.value}
- Current topic: {context.current_topic or "General conversation"}
- Learning goals: {", ".join(context.learning_goals) if context.learning_goals else "General improvement"}

Instructions:
1. Respond naturally in {language_name}
2. Gently correct mistakes when you notice them
3. Introduce new vocabulary gradually
4. Encourage the student and provide positive feedback
5. Ask follow-up questions to maintain engagement
6. Adapt your language complexity to the student's level

Remember: Be patient, encouraging, and focus on practical language use."""

        return system_message

    @staticmethod
    def create_scenario_system_message(
        context: ConversationContext, scenario_data: Dict[str, Any]
    ) -> str:
        """
        Create a system message tailored for scenario-based learning.

        This prompt configures the AI to role-play in a structured learning
        scenario, maintaining character while guiding the student through
        specific learning objectives and vocabulary goals.

        Args:
            context: ConversationContext containing language and role information
            scenario_data: Dictionary containing scenario details including:
                          - scenario_name: Name of the scenario
                          - current_phase: Current phase with objectives and vocabulary
                          - setting: Description of the scenario setting
                          - cultural_context: Cultural guidance for the scenario

        Returns:
            str: A formatted system prompt that instructs the AI tutor on how
                 to conduct the scenario-based learning session with role-play
                 and phase-specific objectives

        Example:
            >>> scenario_data = {
            ...     "scenario_name": "At the Restaurant",
            ...     "current_phase": {
            ...         "name": "Ordering Food",
            ...         "phase_number": 1,
            ...         "total_phases": 3,
            ...         "objectives": ["Order a meal", "Ask questions"],
            ...         "vocabulary": ["menu", "order", "recommendation"]
            ...     }
            ... }
            >>> prompt = PromptGenerator.create_scenario_system_message(context, scenario_data)
            >>> "scenario-based" in prompt
            True
        """
        language_name = PromptGenerator.LANGUAGE_NAMES.get(
            context.language, context.language
        )
        current_phase = scenario_data.get("current_phase", {})
        phase_name = current_phase.get("name", "Current Phase")
        phase_number = current_phase.get("phase_number", 1)
        total_phases = current_phase.get("total_phases", 1)

        # Extract role information from context or use defaults
        ai_role = getattr(context, "ai_role", "conversation partner")
        user_role = getattr(context, "user_role", "conversation participant")

        system_message = f"""You are a helpful {language_name} language tutor conducting a scenario-based conversation practice session.

SCENARIO CONTEXT:
- Scenario: {scenario_data.get("scenario_name", context.current_topic)}
- Current Phase: {phase_name} ({phase_number}/{total_phases})
- Your Role: You are playing the role of a {ai_role}
- Student's Role: The student is playing the role of a {user_role}
- Setting: {scenario_data.get("setting", "A realistic conversation scenario")}

LEARNING OBJECTIVES FOR THIS PHASE:
{chr(10).join(f"- {obj}" for obj in current_phase.get("objectives", ["Practice natural conversation"]))}

VOCABULARY FOCUS:
{", ".join(current_phase.get("vocabulary", ["general vocabulary"]))}

INSTRUCTIONS:
1. Stay in character as the {ai_role}
2. Respond naturally in {language_name} appropriate to the scenario
3. Gently guide the conversation toward the learning objectives
4. Use vocabulary from the focus list naturally in context
5. Provide encouragement and gentle corrections when needed
6. Keep responses realistic for the scenario setting
7. Help the student achieve the phase objectives through natural interaction

CULTURAL CONTEXT:
{scenario_data.get("cultural_context", "Be mindful of cultural norms and etiquette appropriate to the scenario.")}

Remember: Make this feel like a real conversation in the scenario while supporting the student's learning goals."""

        return system_message


# Convenience functions for backward compatibility and ease of use


def create_learning_system_message(context: ConversationContext) -> str:
    """
    Convenience function to create a learning system message.

    Args:
        context: ConversationContext with learning parameters

    Returns:
        str: Formatted system prompt for general language learning
    """
    return PromptGenerator.create_learning_system_message(context)


def create_scenario_system_message(
    context: ConversationContext, scenario_data: Dict[str, Any]
) -> str:
    """
    Convenience function to create a scenario-based system message.

    Args:
        context: ConversationContext with language and role information
        scenario_data: Dictionary with scenario details and phases

    Returns:
        str: Formatted system prompt for scenario-based learning
    """
    return PromptGenerator.create_scenario_system_message(context, scenario_data)
