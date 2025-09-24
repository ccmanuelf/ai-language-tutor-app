"""
Fluently-Style Tutor Modes Manager for AI Language Tutor App

This module provides the complete set of tutor modes that define the Fluently experience:
1. Chit-chat free talking - Casual conversation with relaxed correction
2. One-on-One interview simulation - Job interview practice scenarios
3. Deadline negotiations - Business negotiation and pressure situations
4. Teacher mode - Structured lesson delivery and educational content
5. Vocabulary builder - Targeted vocabulary learning with spaced repetition
6. Open session talking - User-selected topic conversations

Features:
- Complete Fluently tutor mode compatibility
- AI-powered conversation generation per mode
- Real-time analysis integration
- Multi-language support
- Progress tracking per mode
- Adaptive difficulty and personalization
"""

import asyncio
import logging
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from uuid import uuid4
import random

from app.services.ai_router import ai_router, generate_ai_response
from app.services.budget_manager import budget_manager

logger = logging.getLogger(__name__)


class TutorMode(Enum):
    """Available Fluently-style tutor modes"""

    CHIT_CHAT = "chit_chat"
    INTERVIEW_SIMULATION = "interview_simulation"
    DEADLINE_NEGOTIATIONS = "deadline_negotiations"
    TEACHER_MODE = "teacher_mode"
    VOCABULARY_BUILDER = "vocabulary_builder"
    OPEN_SESSION = "open_session"


class TutorModeCategory(Enum):
    """Tutor mode categories"""

    CASUAL = "casual"  # Chit-chat, Open session
    PROFESSIONAL = "professional"  # Interview, Negotiations
    EDUCATIONAL = "educational"  # Teacher mode, Vocabulary builder


class DifficultyLevel(Enum):
    """Difficulty levels for tutor modes"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class TutorModeConfig:
    """Configuration for a specific tutor mode"""

    mode: TutorMode
    name: str
    description: str
    category: TutorModeCategory
    system_prompt_template: str
    conversation_starters: List[str]
    correction_approach: str  # "relaxed", "moderate", "strict"
    focus_areas: List[str]
    success_criteria: List[str]
    example_interactions: List[Dict[str, str]]
    difficulty_adjustments: Dict[str, Dict[str, Any]]
    multi_language_support: bool = True
    requires_topic_input: bool = False


@dataclass
class TutorSession:
    """Active tutor mode session"""

    session_id: str
    user_id: str
    mode: TutorMode
    language: str
    difficulty: DifficultyLevel
    topic: Optional[str] = None
    start_time: datetime = None
    last_activity: datetime = None
    interaction_count: int = 0
    progress_metrics: Dict[str, float] = None
    vocabulary_introduced: List[str] = None
    corrections_made: List[Dict[str, Any]] = None
    session_goals: List[str] = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
        if self.progress_metrics is None:
            self.progress_metrics = {}
        if self.vocabulary_introduced is None:
            self.vocabulary_introduced = []
        if self.corrections_made is None:
            self.corrections_made = []
        if self.session_goals is None:
            self.session_goals = []


class TutorModeManager:
    """
    Comprehensive Fluently-style tutor modes manager

    Provides all 6 core tutor modes with AI-powered conversation generation,
    real-time analysis integration, and adaptive learning features.
    """

    def __init__(self):
        """Initialize tutor mode manager"""
        self.modes = self._initialize_tutor_modes()
        self.active_sessions: Dict[str, TutorSession] = {}
        self.mode_analytics: Dict[TutorMode, Dict[str, Any]] = {}
        logger.info(f"TutorModeManager initialized with {len(self.modes)} modes")

    def _initialize_tutor_modes(self) -> Dict[TutorMode, TutorModeConfig]:
        """Initialize all tutor mode configurations"""

        modes = {
            # 1. CHIT-CHAT FREE TALKING
            TutorMode.CHIT_CHAT: TutorModeConfig(
                mode=TutorMode.CHIT_CHAT,
                name="Chit-chat Free Talking",
                description="Casual, relaxed conversation practice with minimal corrections",
                category=TutorModeCategory.CASUAL,
                system_prompt_template="""You are a friendly, casual conversation partner for language learning.

Your approach:
- Keep conversations light, fun, and natural
- Use relaxed, informal language appropriate for the target language
- Focus on communication over perfection
- Make gentle suggestions rather than corrections
- Encourage the learner to express themselves freely
- Ask follow-up questions to keep conversation flowing
- Share your own thoughts and experiences to model natural conversation

Language: {language}
User Level: {difficulty}

Be supportive, encouraging, and genuinely interested in what the learner has to say.""",
                conversation_starters=[
                    "Hey! How's your day going so far?",
                    "What's something interesting that happened to you recently?",
                    "I'm curious - what do you like to do for fun?",
                    "Tell me about your favorite place in your city.",
                    "What's something you're looking forward to this week?",
                    "Do you have any fun weekend plans?",
                    "What kind of music have you been listening to lately?",
                    "I love hearing about people's hobbies - what are yours?",
                ],
                correction_approach="relaxed",
                focus_areas=[
                    "Natural conversation flow",
                    "Informal expressions",
                    "Cultural small talk",
                    "Personal expression",
                    "Fluency over accuracy",
                ],
                success_criteria=[
                    "User feels comfortable expressing themselves",
                    "Natural conversation rhythm maintained",
                    "User initiates topics and questions",
                    "Reduced hesitation in speaking",
                ],
                example_interactions=[
                    {
                        "user": "I had a really good coffee this morning!",
                        "assistant": "Oh nice! I love a good coffee to start the day. What kind was it? Do you have a favorite coffee shop?",
                    },
                    {
                        "user": "I think I want go to movie tonight.",
                        "assistant": "That sounds fun! What movie are you thinking of seeing? (By the way, you'd say 'I want to go to a movie' - but I totally understood you!)",
                    },
                ],
                difficulty_adjustments={
                    "beginner": {
                        "vocabulary": "simple_everyday",
                        "grammar_complexity": "present_tense_focus",
                        "correction_frequency": "minimal",
                    },
                    "intermediate": {
                        "vocabulary": "expanded_topics",
                        "grammar_complexity": "mixed_tenses",
                        "correction_frequency": "gentle",
                    },
                    "advanced": {
                        "vocabulary": "idiomatic_expressions",
                        "grammar_complexity": "complex_structures",
                        "correction_frequency": "subtle",
                    },
                },
            ),
            # 2. ONE-ON-ONE INTERVIEW SIMULATION
            TutorMode.INTERVIEW_SIMULATION: TutorModeConfig(
                mode=TutorMode.INTERVIEW_SIMULATION,
                name="One-on-One Interview Simulation",
                description="Professional job interview practice with industry-specific scenarios",
                category=TutorModeCategory.PROFESSIONAL,
                system_prompt_template="""You are an experienced hiring manager conducting a job interview in {language}.

Your approach:
- Maintain a professional but friendly demeanor
- Ask realistic interview questions appropriate for the industry/role
- Provide constructive feedback on answers
- Help the candidate improve their responses
- Focus on professional communication skills
- Correct grammar and pronunciation when it affects clarity
- Model professional language and expressions

Industry: {topic}
Language: {language}
Candidate Level: {difficulty}

Create a realistic interview experience that builds confidence and professional communication skills.""",
                conversation_starters=[
                    "Thank you for coming in today. Could you start by telling me a bit about yourself?",
                    "I've reviewed your background. What interests you most about this position?",
                    "Can you walk me through your experience with [relevant skill]?",
                    "Tell me about a challenging project you worked on recently.",
                    "How do you handle working under pressure or tight deadlines?",
                    "What do you consider your greatest professional strength?",
                    "Where do you see yourself professionally in five years?",
                ],
                correction_approach="moderate",
                focus_areas=[
                    "Professional vocabulary",
                    "Formal communication",
                    "Interview confidence",
                    "Industry terminology",
                    "Clear articulation",
                ],
                success_criteria=[
                    "Professional language usage",
                    "Clear, structured responses",
                    "Confident delivery",
                    "Appropriate industry vocabulary",
                ],
                example_interactions=[
                    {
                        "user": "I am very passionate about this field and I have five years experience.",
                        "assistant": "That's great to hear! Could you tell me more about what specifically draws you to this field? And perhaps share an example from those five years that demonstrates your passion?",
                    }
                ],
                difficulty_adjustments={
                    "beginner": {
                        "question_complexity": "basic_personal_questions",
                        "vocabulary": "general_professional",
                        "feedback_detail": "detailed_corrections",
                    },
                    "intermediate": {
                        "question_complexity": "behavioral_questions",
                        "vocabulary": "industry_specific",
                        "feedback_detail": "targeted_improvement",
                    },
                    "advanced": {
                        "question_complexity": "strategic_thinking",
                        "vocabulary": "advanced_professional",
                        "feedback_detail": "subtle_refinement",
                    },
                },
                requires_topic_input=True,
            ),
            # 3. DEADLINE NEGOTIATIONS
            TutorMode.DEADLINE_NEGOTIATIONS: TutorModeConfig(
                mode=TutorMode.DEADLINE_NEGOTIATIONS,
                name="Deadline Negotiations",
                description="Business negotiation scenarios with time pressure and professional stakes",
                category=TutorModeCategory.PROFESSIONAL,
                system_prompt_template="""You are a business professional in a negotiation scenario involving deadlines and deliverables.

Your approach:
- Create realistic time pressure situations
- Use professional business language
- Demonstrate negotiation tactics and language
- Help user practice assertiveness while remaining professional
- Focus on clear, persuasive communication
- Provide immediate feedback on negotiation language
- Model diplomatic but firm expressions

Scenario: {topic}
Language: {language}
Negotiation Level: {difficulty}

Create challenging but realistic scenarios that improve business communication and negotiation skills.""",
                conversation_starters=[
                    "I understand you're looking to move the deadline up by two weeks. Let's discuss what that would involve.",
                    "We have a concern about the proposed timeline. Can we explore some alternatives?",
                    "The client is pushing for an earlier delivery date. What are your thoughts on this?",
                    "I need to discuss the feasibility of the current project timeline.",
                    "There's been a change in priorities that affects our agreed-upon deadlines.",
                    "Let's talk about how we can meet this accelerated timeline without compromising quality.",
                ],
                correction_approach="strict",
                focus_areas=[
                    "Business negotiation language",
                    "Professional assertiveness",
                    "Diplomatic communication",
                    "Time management vocabulary",
                    "Persuasive expressions",
                ],
                success_criteria=[
                    "Clear position statements",
                    "Professional tone under pressure",
                    "Effective counter-proposals",
                    "Diplomatic language usage",
                ],
                example_interactions=[
                    {
                        "user": "The deadline is too tight. We need more time.",
                        "assistant": "I understand your concern about the timeline. Could you be more specific about what aspects are challenging? Perhaps we could explore which deliverables are most critical and see if there's flexibility in phasing the project.",
                    }
                ],
                difficulty_adjustments={
                    "beginner": {
                        "scenario_complexity": "simple_deadline_changes",
                        "pressure_level": "low",
                        "vocabulary": "basic_business_terms",
                    },
                    "intermediate": {
                        "scenario_complexity": "multi_stakeholder_negotiations",
                        "pressure_level": "medium",
                        "vocabulary": "negotiation_language",
                    },
                    "advanced": {
                        "scenario_complexity": "complex_contract_negotiations",
                        "pressure_level": "high",
                        "vocabulary": "advanced_business_diplomacy",
                    },
                },
                requires_topic_input=True,
            ),
            # 4. TEACHER MODE
            TutorMode.TEACHER_MODE: TutorModeConfig(
                mode=TutorMode.TEACHER_MODE,
                name="Teacher Mode",
                description="Structured lesson delivery with educational content and systematic learning",
                category=TutorModeCategory.EDUCATIONAL,
                system_prompt_template="""You are an experienced language teacher providing structured lessons in {language}.

Your approach:
- Present lessons in a clear, organized manner
- Use the target language for instruction with explanations
- Provide examples and practice opportunities
- Check for understanding regularly
- Correct mistakes constructively with explanations
- Build lessons progressively from simple to complex
- Encourage questions and active participation
- Provide cultural context when relevant

Topic: {topic}
Language: {language}
Student Level: {difficulty}

Create engaging, educational experiences that systematically build language skills.""",
                conversation_starters=[
                    "Today we're going to learn about [topic]. Are you ready to begin?",
                    "Let's start with a quick review of what we covered last time.",
                    "I'd like to introduce you to some new vocabulary related to [topic].",
                    "Can you tell me what you already know about [topic]?",
                    "Today's lesson will focus on [grammar point]. Let's see it in action.",
                    "Let's practice using [language structure] in different contexts.",
                    "I have some interesting cultural information to share about [topic].",
                ],
                correction_approach="moderate",
                focus_areas=[
                    "Systematic grammar instruction",
                    "Vocabulary building",
                    "Cultural context",
                    "Progressive skill building",
                    "Educational methodology",
                ],
                success_criteria=[
                    "Clear understanding of lesson objectives",
                    "Correct usage of taught structures",
                    "Active participation in exercises",
                    "Retention of key vocabulary",
                ],
                example_interactions=[
                    {
                        "user": "Can you explain the past tense again?",
                        "assistant": "Of course! In [language], the past tense is formed by... Let me give you some examples: [examples]. Now, can you try making a sentence using this pattern?",
                    }
                ],
                difficulty_adjustments={
                    "beginner": {
                        "lesson_complexity": "basic_structures",
                        "explanation_detail": "very_detailed",
                        "practice_frequency": "high_repetition",
                    },
                    "intermediate": {
                        "lesson_complexity": "intermediate_grammar",
                        "explanation_detail": "balanced",
                        "practice_frequency": "varied_contexts",
                    },
                    "advanced": {
                        "lesson_complexity": "nuanced_language",
                        "explanation_detail": "conceptual",
                        "practice_frequency": "application_focused",
                    },
                },
                requires_topic_input=True,
            ),
            # 5. VOCABULARY BUILDER
            TutorMode.VOCABULARY_BUILDER: TutorModeConfig(
                mode=TutorMode.VOCABULARY_BUILDER,
                name="Vocabulary Builder",
                description="Targeted vocabulary learning with context, usage, and spaced repetition",
                category=TutorModeCategory.EDUCATIONAL,
                system_prompt_template="""You are a vocabulary specialist helping to build targeted language skills in {language}.

Your approach:
- Introduce new vocabulary in meaningful contexts
- Provide multiple examples of word usage
- Create connections between related words
- Use spaced repetition principles
- Focus on practical, high-frequency vocabulary
- Explain nuances and collocations
- Create memorable associations and mnemonics
- Test retention through varied exercises

Topic Area: {topic}
Language: {language}
Vocabulary Level: {difficulty}

Make vocabulary learning engaging, contextual, and memorable.""",
                conversation_starters=[
                    "Let's explore some essential vocabulary for [topic]. Which words would you like to learn first?",
                    "I have some high-frequency words that will really improve your [language] skills.",
                    "Today we'll focus on vocabulary related to [topic]. Let's start with the most useful ones.",
                    "Can you think of any words you've heard related to [topic] that you'd like to understand better?",
                    "Let's learn some expressions that native speakers use when talking about [topic].",
                    "I'll teach you some vocabulary, then we'll practice using it in different contexts.",
                ],
                correction_approach="moderate",
                focus_areas=[
                    "Contextual vocabulary learning",
                    "Word families and connections",
                    "Practical usage patterns",
                    "Cultural word meanings",
                    "Memory techniques",
                ],
                success_criteria=[
                    "Correct word usage in context",
                    "Understanding of word nuances",
                    "Retention over time",
                    "Active use in conversation",
                ],
                example_interactions=[
                    {
                        "user": "What does 'deadline' mean exactly?",
                        "assistant": "Great question! A 'deadline' is the latest time or date by which something must be completed. For example: 'The project deadline is Friday.' It comes from the idea of a line you cannot cross. Related words include 'due date,' 'time limit,' and 'cutoff.' Can you make a sentence using 'deadline'?",
                    }
                ],
                difficulty_adjustments={
                    "beginner": {
                        "word_complexity": "high_frequency_basic",
                        "context_examples": "simple_sentences",
                        "retention_method": "repetition_drilling",
                    },
                    "intermediate": {
                        "word_complexity": "topic_specific",
                        "context_examples": "varied_situations",
                        "retention_method": "contextual_association",
                    },
                    "advanced": {
                        "word_complexity": "nuanced_idiomatic",
                        "context_examples": "authentic_usage",
                        "retention_method": "semantic_networks",
                    },
                },
                requires_topic_input=True,
            ),
            # 6. OPEN SESSION
            TutorMode.OPEN_SESSION: TutorModeConfig(
                mode=TutorMode.OPEN_SESSION,
                name="Open Session Talking",
                description="User-selected topic conversations with balanced correction and engagement",
                category=TutorModeCategory.CASUAL,
                system_prompt_template="""You are an intelligent conversation partner focused on the topic: {topic}

Your approach:
- Engage deeply with the user's chosen topic
- Ask thoughtful, topic-relevant questions
- Share relevant information and perspectives
- Maintain natural conversation flow
- Provide moderate corrections that don't interrupt engagement
- Adapt to the user's interest level and knowledge
- Encourage the user to express complex thoughts
- Balance education with entertainment

Topic: {topic}
Language: {language}
User Level: {difficulty}

Create engaging, topic-focused conversations that improve language skills while exploring interesting subjects.""",
                conversation_starters=[
                    "You've chosen to talk about {topic} - what aspect interests you most?",
                    "I'd love to hear your thoughts on {topic}. What's your experience with it?",
                    "Tell me what drew you to want to discuss {topic} today.",
                    "{topic} is such an interesting subject. What would you like to explore about it?",
                    "What's something about {topic} that you've been curious about?",
                    "I'm curious about your perspective on {topic}. Could you share your views?",
                ],
                correction_approach="moderate",
                focus_areas=[
                    "Topic-specific vocabulary",
                    "Opinion expression",
                    "Complex idea articulation",
                    "Natural topic development",
                    "Balanced fluency and accuracy",
                ],
                success_criteria=[
                    "Sustained topic engagement",
                    "Complex idea expression",
                    "Natural question asking",
                    "Topic vocabulary acquisition",
                ],
                example_interactions=[
                    {
                        "user": "I really love cooking, especially Italian food.",
                        "assistant": "That's wonderful! Italian cuisine has such rich flavors and traditions. What's your favorite Italian dish to prepare? Do you prefer making pasta from scratch or do you have a go-to sauce recipe?",
                    }
                ],
                difficulty_adjustments={
                    "beginner": {
                        "topic_depth": "surface_level_discussion",
                        "vocabulary": "basic_topic_words",
                        "question_complexity": "simple_preferences",
                    },
                    "intermediate": {
                        "topic_depth": "detailed_exploration",
                        "vocabulary": "specialized_terms",
                        "question_complexity": "analytical_thinking",
                    },
                    "advanced": {
                        "topic_depth": "nuanced_analysis",
                        "vocabulary": "expert_terminology",
                        "question_complexity": "abstract_concepts",
                    },
                },
                requires_topic_input=True,
            ),
        }

        return modes

    def get_available_modes(self) -> List[Dict[str, Any]]:
        """Get list of available tutor modes with descriptions"""
        return [
            {
                "mode": mode.value,
                "name": config.name,
                "description": config.description,
                "category": config.category.value,
                "requires_topic": config.requires_topic_input,
            }
            for mode, config in self.modes.items()
        ]

    def start_tutor_session(
        self,
        user_id: str,
        mode: TutorMode,
        language: str,
        difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
        topic: Optional[str] = None,
    ) -> str:
        """Start a new tutor mode session"""

        session_id = str(uuid4())

        # Validate topic requirement
        mode_config = self.modes[mode]
        if mode_config.requires_topic_input and not topic:
            raise ValueError(f"Mode {mode.value} requires a topic to be specified")

        # Create session
        session = TutorSession(
            session_id=session_id,
            user_id=user_id,
            mode=mode,
            language=language,
            difficulty=difficulty,
            topic=topic,
        )

        self.active_sessions[session_id] = session

        logger.info(f"Started {mode.value} session {session_id} for user {user_id}")
        return session_id

    def get_session_system_prompt(self, session_id: str) -> str:
        """Generate system prompt for a tutor session"""

        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        mode_config = self.modes[session.mode]

        # Format system prompt with session details
        prompt = mode_config.system_prompt_template.format(
            language=session.language,
            difficulty=session.difficulty.value,
            topic=session.topic or "general conversation",
        )

        return prompt

    def get_conversation_starter(self, session_id: str) -> str:
        """Get an appropriate conversation starter for the session"""

        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        mode_config = self.modes[session.mode]
        starters = mode_config.conversation_starters.copy()

        # Format starters with topic if provided
        if session.topic:
            starters = [
                starter.format(topic=session.topic) if "{topic}" in starter else starter
                for starter in starters
            ]

        return random.choice(starters)

    async def generate_tutor_response(
        self,
        session_id: str,
        user_message: str,
        context_messages: List[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Generate AI response for tutor mode session"""

        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        mode_config = self.modes[session.mode]

        # Build conversation context
        messages = []

        # System prompt
        system_prompt = self.get_session_system_prompt(session_id)
        messages.append({"role": "system", "content": system_prompt})

        # Previous context
        if context_messages:
            messages.extend(context_messages)

        # Current user message
        messages.append({"role": "user", "content": user_message})

        # Generate response using AI router
        try:
            response = await generate_ai_response(
                messages=messages,
                language=session.language,
                context_type=f"tutor_mode_{session.mode.value}",
            )

            # Update session metrics
            session.interaction_count += 1
            session.last_activity = datetime.now()

            return {
                "response": response,
                "mode": session.mode.value,
                "correction_approach": mode_config.correction_approach,
                "session_progress": {
                    "interactions": session.interaction_count,
                    "duration_minutes": (
                        datetime.now() - session.start_time
                    ).total_seconds()
                    / 60,
                },
            }

        except Exception as e:
            logger.error(f"Error generating tutor response: {e}")
            raise

    def end_tutor_session(self, session_id: str) -> Dict[str, Any]:
        """End a tutor session and return summary"""

        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Calculate session metrics
        duration = (datetime.now() - session.start_time).total_seconds() / 60

        summary = {
            "session_id": session_id,
            "mode": session.mode.value,
            "language": session.language,
            "topic": session.topic,
            "duration_minutes": duration,
            "interactions": session.interaction_count,
            "vocabulary_introduced": session.vocabulary_introduced,
            "corrections_made": len(session.corrections_made),
        }

        # Remove from active sessions
        del self.active_sessions[session_id]

        logger.info(f"Ended tutor session {session_id}: {summary}")
        return summary

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about an active session"""

        session = self.active_sessions.get(session_id)
        if not session:
            return None

        return {
            "session_id": session_id,
            "mode": session.mode.value,
            "language": session.language,
            "topic": session.topic,
            "difficulty": session.difficulty.value,
            "start_time": session.start_time.isoformat(),
            "interaction_count": session.interaction_count,
            "progress_metrics": session.progress_metrics,
        }

    def get_mode_analytics(self) -> Dict[str, Any]:
        """Get analytics across all tutor modes"""

        analytics = {
            "active_sessions": len(self.active_sessions),
            "available_modes": len(self.modes),
            "modes_by_category": {},
            "session_distribution": {},
        }

        # Group by category
        for mode_config in self.modes.values():
            category = mode_config.category.value
            if category not in analytics["modes_by_category"]:
                analytics["modes_by_category"][category] = []
            analytics["modes_by_category"][category].append(mode_config.name)

        # Session distribution
        for session in self.active_sessions.values():
            mode = session.mode.value
            analytics["session_distribution"][mode] = (
                analytics["session_distribution"].get(mode, 0) + 1
            )

        return analytics


# Global tutor mode manager instance
tutor_mode_manager = TutorModeManager()
