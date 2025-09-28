"""
Scenario-Based Conversation Manager for AI Language Tutor App (Pingo functionality)

This module provides structured scenario-based conversations for language learning,
similar to Pingo's approach of contextual practice sessions.

Features:
- Pre-defined conversation scenarios (restaurant, travel, business, etc.)
- Dynamic scenario generation based on learning goals
- Scenario-specific vocabulary and phrases
- Progress tracking within scenarios
- Adaptive difficulty based on user performance
- Cultural context integration
- Real-world situation practice
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

logger = logging.getLogger(__name__)


class ScenarioCategory(Enum):
    """Main scenario categories"""

    TRAVEL = "travel"
    RESTAURANT = "restaurant"
    SHOPPING = "shopping"
    BUSINESS = "business"
    HEALTHCARE = "healthcare"
    SOCIAL = "social"
    EMERGENCY = "emergency"
    EDUCATION = "education"
    DAILY_LIFE = "daily_life"
    HOBBIES = "hobbies"


class ScenarioDifficulty(Enum):
    """Scenario difficulty levels"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    NATIVE = "native"


class ConversationRole(Enum):
    """Roles in scenario conversations"""

    CUSTOMER = "customer"
    SERVICE_PROVIDER = "service_provider"
    FRIEND = "friend"
    COLLEAGUE = "colleague"
    STUDENT = "student"
    TEACHER = "teacher"
    TOURIST = "tourist"
    LOCAL = "local"


@dataclass
class ScenarioPhase:
    """Individual phase within a scenario"""

    phase_id: str
    name: str
    description: str
    expected_duration_minutes: int
    key_vocabulary: List[str]
    essential_phrases: List[str]
    learning_objectives: List[str]
    cultural_notes: Optional[str] = None
    success_criteria: List[str] = None

    def __post_init__(self):
        if self.success_criteria is None:
            self.success_criteria = []


@dataclass
class ConversationScenario:
    """Complete scenario definition"""

    scenario_id: str
    name: str
    category: ScenarioCategory
    difficulty: ScenarioDifficulty
    description: str
    user_role: ConversationRole
    ai_role: ConversationRole
    setting: str
    duration_minutes: int
    phases: List[ScenarioPhase]
    vocabulary_focus: List[str]
    cultural_context: Dict[str, Any]
    learning_goals: List[str]
    prerequisites: List[str] = None

    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []


@dataclass
class ScenarioProgress:
    """Track progress within a scenario"""

    scenario_id: str
    user_id: str
    current_phase: int
    phase_progress: Dict[str, float]  # phase_id -> completion percentage
    vocabulary_mastered: List[str]
    objectives_completed: List[str]
    start_time: datetime
    last_activity: datetime
    total_attempts: int
    success_rate: float
    difficulty_adjustments: List[str] = None

    def __post_init__(self):
        if self.difficulty_adjustments is None:
            self.difficulty_adjustments = []


@dataclass
class UniversalScenarioTemplate:
    """Universal template for creating comprehensive scenarios dynamically"""

    template_id: str
    name: str
    category: ScenarioCategory
    tier: int  # 1-4 based on priority (1=essential, 4=cultural)
    base_vocabulary: List[str]
    essential_phrases: Dict[str, List[str]]  # difficulty -> phrases
    cultural_context: Dict[str, Any]
    learning_objectives: List[str]
    conversation_starters: List[str]
    scenario_variations: List[Dict[str, Any]]
    difficulty_modifiers: Dict[str, Dict[str, Any]]
    success_metrics: List[str]

    def generate_scenario(
        self,
        difficulty: ScenarioDifficulty,
        user_role: ConversationRole,
        ai_role: ConversationRole,
        variation_id: Optional[str] = None,
    ) -> ConversationScenario:
        """Generate a complete scenario from this template"""

        # Select variation or use default
        variation = (
            self._get_variation(variation_id)
            if variation_id
            else self.scenario_variations[0]
        )

        # Apply difficulty modifiers
        difficulty_mods = self.difficulty_modifiers.get(difficulty.value, {})

        # Create phases based on variation and difficulty
        phases = self._create_phases(variation, difficulty_mods)

        # Adjust vocabulary based on difficulty
        vocab = self._adjust_vocabulary(difficulty)

        scenario_id = f"{self.template_id}_{difficulty.value}_{uuid4().hex[:8]}"

        return ConversationScenario(
            scenario_id=scenario_id,
            name=f"{self.name} ({difficulty.value.title()})",
            category=self.category,
            difficulty=difficulty,
            description=variation.get(
                "description",
                f"{difficulty.value.title()} level {self.name.lower()} practice",
            ),
            user_role=user_role,
            ai_role=ai_role,
            setting=variation.get("setting", "General context"),
            duration_minutes=difficulty_mods.get("duration", 15),
            phases=phases,
            vocabulary_focus=vocab,
            cultural_context=self.cultural_context,
            learning_goals=self.learning_objectives,
            prerequisites=difficulty_mods.get("prerequisites", []),
        )

    def _get_variation(self, variation_id: str) -> Dict[str, Any]:
        """Get specific scenario variation"""
        for variation in self.scenario_variations:
            if variation.get("id") == variation_id:
                return variation
        return self.scenario_variations[0]

    def _create_phases(
        self, variation: Dict[str, Any], difficulty_mods: Dict[str, Any]
    ) -> List[ScenarioPhase]:
        """Create scenario phases based on variation and difficulty"""
        base_phases = variation.get(
            "phases", ["introduction", "main_interaction", "conclusion"]
        )
        phases = []

        for i, phase_name in enumerate(base_phases):
            phase_vocab = self.base_vocabulary[
                : difficulty_mods.get("vocab_limit", len(self.base_vocabulary))
            ]
            phase_phrases = self.essential_phrases.get("beginner", [])

            phase = ScenarioPhase(
                phase_id=f"{phase_name}_{i + 1}",
                name=phase_name.replace("_", " ").title(),
                description=f"{phase_name.replace('_', ' ').title()} phase of the conversation",
                expected_duration_minutes=difficulty_mods.get("phase_duration", 5),
                key_vocabulary=phase_vocab[:5],  # Limit per phase
                essential_phrases=phase_phrases[:3],  # Key phrases per phase
                learning_objectives=[
                    obj
                    for obj in self.learning_objectives
                    if i < len(self.learning_objectives)
                ],
                cultural_notes=self.cultural_context.get("notes", ""),
                success_criteria=self.success_metrics[:2],  # Top success criteria
            )
            phases.append(phase)

        return phases

    def _adjust_vocabulary(self, difficulty: ScenarioDifficulty) -> List[str]:
        """Adjust vocabulary list based on difficulty level"""
        if difficulty == ScenarioDifficulty.BEGINNER:
            return self.base_vocabulary[:10]
        elif difficulty == ScenarioDifficulty.INTERMEDIATE:
            return self.base_vocabulary[:20]
        else:  # ADVANCED
            return self.base_vocabulary


class ScenarioFactory:
    """Factory for creating scenarios from templates and configurations"""

    def __init__(self, template_directory: str = "scenario_templates"):
        self.template_directory = Path(template_directory)
        self.universal_templates: Dict[str, UniversalScenarioTemplate] = {}
        self.content_cache: Dict[str, Dict[str, Any]] = {}
        self._load_universal_templates()

    def _load_universal_templates(self):
        """Load universal scenario templates from configuration files"""
        templates_path = Path(__file__).parent.parent / "config" / "scenarios"

        if not templates_path.exists():
            logger.warning(f"Scenario templates directory not found: {templates_path}")
            self._create_default_templates()
            return

        for template_file in templates_path.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)
                    template = self._create_universal_template(template_data)
                    self.universal_templates[template.template_id] = template
                    logger.info(f"Loaded template: {template.name}")
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")

    def _create_universal_template(
        self, data: Dict[str, Any]
    ) -> UniversalScenarioTemplate:
        """Create UniversalScenarioTemplate from JSON data"""
        return UniversalScenarioTemplate(
            template_id=data["template_id"],
            name=data["name"],
            category=ScenarioCategory(data["category"]),
            tier=data["tier"],
            base_vocabulary=data["base_vocabulary"],
            essential_phrases=data["essential_phrases"],
            cultural_context=data["cultural_context"],
            learning_objectives=data["learning_objectives"],
            conversation_starters=data["conversation_starters"],
            scenario_variations=data["scenario_variations"],
            difficulty_modifiers=data["difficulty_modifiers"],
            success_metrics=data["success_metrics"],
        )

    def _create_default_templates(self):
        """Create default templates when no configuration files exist"""
        logger.info("Creating comprehensive 32-scenario template system")

        # Load Tier 1 templates (defined in this file)
        tier1_templates = [
            self._create_greetings_template(),
            self._create_family_template(),
            self._create_restaurant_template(),
            self._create_transportation_template(),
            self._create_home_neighborhood_template(),
        ]

        # Load extended templates (Tiers 2-4) from extended module
        try:
            from app.services.scenario_templates_extended import (
                ExtendedScenarioTemplates,
            )

            extended_templates = ExtendedScenarioTemplates.get_all_extended_templates()
            all_templates = tier1_templates + extended_templates
            logger.info(
                f"Successfully loaded {len(tier1_templates)} Tier 1 + {len(extended_templates)} extended scenario templates = {len(all_templates)} total"
            )
        except ImportError as e:
            logger.warning(f"Could not load extended templates: {e}, using Tier 1 only")
            all_templates = tier1_templates

        for template in all_templates:
            self.universal_templates[template.template_id] = template
            logger.info(f"Created template: {template.name} (Tier {template.tier})")

    def _create_greetings_template(self) -> UniversalScenarioTemplate:
        """Create greetings and introductions template"""
        return UniversalScenarioTemplate(
            template_id="greetings_introductions",
            name="Greetings and Introductions",
            category=ScenarioCategory.SOCIAL,
            tier=1,
            base_vocabulary=[
                "hello",
                "hi",
                "good morning",
                "good afternoon",
                "good evening",
                "goodbye",
                "see you later",
                "nice to meet you",
                "my name is",
                "what's your name",
                "how are you",
                "I'm fine",
                "thank you",
                "please",
                "excuse me",
                "sorry",
                "where are you from",
                "I'm from",
                "how old are you",
                "occupation",
                "student",
                "work",
            ],
            essential_phrases={
                "beginner": [
                    "Hello, my name is...",
                    "Nice to meet you",
                    "How are you?",
                    "I'm fine, thank you",
                    "Where are you from?",
                    "I'm from...",
                ],
                "intermediate": [
                    "It's a pleasure to meet you",
                    "How has your day been?",
                    "What do you do for work?",
                    "I work as a...",
                    "How long have you been here?",
                    "What brings you here?",
                ],
                "advanced": [
                    "I'd like to introduce myself",
                    "May I ask what you do professionally?",
                    "I've heard so much about this place",
                    "What's your impression of...?",
                    "How do you find living here?",
                    "It's been wonderful meeting you",
                ],
            },
            cultural_context={
                "notes": "Greeting customs vary by culture. Some prefer formal titles, others are more casual. Physical contact (handshakes, cheek kisses) varies by region.",
                "formality_levels": ["very_formal", "formal", "casual", "informal"],
                "time_sensitivity": "morning/afternoon/evening greetings",
                "regional_variations": True,
            },
            learning_objectives=[
                "Master basic greeting expressions",
                "Learn to introduce yourself confidently",
                "Practice asking and answering personal questions",
                "Understand cultural greeting norms",
                "Build confidence in first conversations",
            ],
            conversation_starters=[
                "Hello! I don't think we've met.",
                "Good morning! How are you today?",
                "Hi there! Are you new here?",
                "Excuse me, could you help me with something?",
                "I'm sorry, but do I know you from somewhere?",
            ],
            scenario_variations=[
                {
                    "id": "formal_meeting",
                    "description": "Formal introduction at business or academic setting",
                    "setting": "Professional conference or business meeting",
                    "phases": [
                        "formal_greeting",
                        "title_exchange",
                        "business_cards",
                        "small_talk",
                        "polite_departure",
                    ],
                },
                {
                    "id": "casual_meeting",
                    "description": "Casual introduction at social gathering",
                    "setting": "Party, coffee shop, or social event",
                    "phases": [
                        "casual_greeting",
                        "name_exchange",
                        "background_sharing",
                        "interest_discussion",
                        "contact_exchange",
                    ],
                },
                {
                    "id": "neighbor_meeting",
                    "description": "Meeting a new neighbor",
                    "setting": "Apartment building, neighborhood, local area",
                    "phases": [
                        "neighborly_greeting",
                        "location_discussion",
                        "local_recommendations",
                        "future_contact",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {
                    "duration": 10,
                    "phase_duration": 3,
                    "vocab_limit": 15,
                    "prerequisites": [],
                },
                "intermediate": {
                    "duration": 15,
                    "phase_duration": 4,
                    "vocab_limit": 20,
                    "prerequisites": ["basic_vocabulary", "simple_questions"],
                },
                "advanced": {
                    "duration": 20,
                    "phase_duration": 5,
                    "vocab_limit": 25,
                    "prerequisites": [
                        "intermediate_conversation",
                        "cultural_awareness",
                    ],
                },
            },
            success_metrics=[
                "Successfully exchange names",
                "Ask and answer 3 personal questions",
                "Use appropriate greeting for time/context",
                "Maintain natural conversation flow",
                "End conversation politely",
            ],
        )

    # Tier 2: Daily Routines and Activities (6-15)
    def _create_daily_routine_template(self) -> UniversalScenarioTemplate:
        """Create daily routine template"""
        return UniversalScenarioTemplate(
            template_id="daily_routine",
            name="Daily Routine",
            category=ScenarioCategory.DAILY_LIFE,
            tier=2,
            base_vocabulary=[
                "morning",
                "afternoon",
                "evening",
                "night",
                "wake up",
                "get up",
                "brush teeth",
                "shower",
                "breakfast",
                "lunch",
                "dinner",
                "work",
                "school",
                "sleep",
                "exercise",
                "hobby",
                "schedule",
                "time",
                "early",
                "late",
                "busy",
                "free time",
                "weekend",
                "weekday",
            ],
            essential_phrases={
                "beginner": [
                    "I wake up at...",
                    "I go to work",
                    "I have breakfast",
                    "What time do you...?",
                ],
                "intermediate": [
                    "My daily routine is...",
                    "I usually start my day with...",
                    "In the evening, I like to...",
                ],
                "advanced": [
                    "I'm trying to establish a better routine",
                    "My schedule varies depending on...",
                ],
            },
            cultural_context={
                "notes": "Daily routines vary significantly across cultures and lifestyles"
            },
            learning_objectives=[
                "Describe daily activities",
                "Talk about time and schedules",
                "Express habits and routines",
            ],
            conversation_starters=[
                "What's your typical day like?",
                "When do you usually wake up?",
            ],
            scenario_variations=[
                {
                    "id": "workday",
                    "description": "Typical working day routine",
                    "phases": [
                        "morning_routine",
                        "work_preparation",
                        "work_day",
                        "evening_activities",
                    ],
                },
                {
                    "id": "weekend",
                    "description": "Weekend routine discussion",
                    "phases": [
                        "weekend_morning",
                        "leisure_activities",
                        "social_time",
                        "relaxation",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 10},
                "intermediate": {"duration": 15},
                "advanced": {"duration": 20},
            },
            success_metrics=[
                "Describe complete daily routine",
                "Use time expressions correctly",
                "Express preferences about activities",
            ],
        )

    def _create_basic_conversations_template(self) -> UniversalScenarioTemplate:
        """Create basic conversations template"""
        return UniversalScenarioTemplate(
            template_id="basic_conversations",
            name="Basic Conversations",
            category=ScenarioCategory.SOCIAL,
            tier=2,
            base_vocabulary=[
                "yes",
                "no",
                "maybe",
                "please",
                "thank you",
                "sorry",
                "excuse me",
                "help",
                "understand",
                "speak",
                "listen",
                "repeat",
                "slow",
                "fast",
                "question",
                "answer",
                "problem",
                "solution",
                "agree",
                "disagree",
            ],
            essential_phrases={
                "beginner": [
                    "Can you help me?",
                    "I don't understand",
                    "Could you repeat that?",
                    "Thank you very much",
                ],
                "intermediate": [
                    "Could you speak more slowly?",
                    "What does that mean?",
                    "I'm not sure I follow",
                ],
                "advanced": [
                    "I beg your pardon?",
                    "Could you clarify what you mean by...?",
                    "I'm afraid I didn't catch that",
                ],
            },
            cultural_context={
                "notes": "Politeness levels and conversation patterns vary by culture"
            },
            learning_objectives=[
                "Master essential conversation phrases",
                "Learn to ask for clarification",
                "Practice polite interruptions",
            ],
            conversation_starters=[
                "Excuse me, could you help me?",
                "I have a question",
                "Sorry to bother you",
            ],
            scenario_variations=[
                {
                    "id": "asking_help",
                    "description": "Asking for help or assistance",
                    "phases": [
                        "polite_approach",
                        "explain_need",
                        "receive_help",
                        "thank_and_close",
                    ],
                },
                {
                    "id": "clarification",
                    "description": "Asking for clarification",
                    "phases": [
                        "indicate_confusion",
                        "request_explanation",
                        "confirm_understanding",
                        "continue_conversation",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 8},
                "intermediate": {"duration": 12},
                "advanced": {"duration": 15},
            },
            success_metrics=[
                "Use polite expressions correctly",
                "Ask for help appropriately",
                "Handle misunderstandings gracefully",
            ],
        )

    def _create_family_template(self) -> UniversalScenarioTemplate:
        """Create family and relationships template"""
        return UniversalScenarioTemplate(
            template_id="family_relationships",
            name="Family and Relationships",
            category=ScenarioCategory.SOCIAL,
            tier=1,
            base_vocabulary=[
                "family",
                "mother",
                "father",
                "parents",
                "sister",
                "brother",
                "grandmother",
                "grandfather",
                "aunt",
                "uncle",
                "cousin",
                "husband",
                "wife",
                "son",
                "daughter",
                "children",
                "baby",
                "married",
                "single",
                "divorced",
                "relationship",
                "love",
                "close",
                "live with",
                "visit",
                "call",
                "text",
                "birthday",
            ],
            essential_phrases={
                "beginner": [
                    "I have a...",
                    "My family is...",
                    "Do you have children?",
                    "How many brothers and sisters?",
                    "My parents live in...",
                    "I live with...",
                ],
                "intermediate": [
                    "I'm very close to my...",
                    "We get together every...",
                    "My family means a lot to me",
                    "Do you see your family often?",
                    "We have family traditions",
                    "My relatives are scattered around...",
                ],
                "advanced": [
                    "Family dynamics can be complex",
                    "We maintain strong family bonds",
                    "There's always been tension between...",
                    "Family gatherings are important to us",
                    "We have different perspectives on...",
                    "Extended family plays a significant role",
                ],
            },
            cultural_context={
                "notes": "Family structures and relationships vary greatly across cultures. Some cultures emphasize extended family, others focus on nuclear family.",
                "family_values": [
                    "collectivist",
                    "individualist",
                    "hierarchical",
                    "egalitarian",
                ],
                "sensitive_topics": ["divorce", "childlessness", "family conflicts"],
                "celebration_customs": ["birthdays", "anniversaries", "reunions"],
            },
            learning_objectives=[
                "Describe family members and relationships",
                "Discuss family activities and traditions",
                "Express feelings about family",
                "Ask appropriate questions about family",
                "Understand cultural family differences",
            ],
            conversation_starters=[
                "Tell me about your family.",
                "Do you have any siblings?",
                "What's your family like?",
                "Are you close to your relatives?",
                "Do you have family traditions?",
            ],
            scenario_variations=[
                {
                    "id": "family_introduction",
                    "description": "Introducing family members to someone new",
                    "setting": "Social gathering where family meets friends",
                    "phases": [
                        "family_overview",
                        "individual_introductions",
                        "family_stories",
                        "shared_activities",
                    ],
                },
                {
                    "id": "family_discussion",
                    "description": "Casual conversation about family life",
                    "setting": "Coffee with a friend or colleague",
                    "phases": [
                        "family_updates",
                        "relationship_dynamics",
                        "family_challenges",
                        "family_celebrations",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 12, "phase_duration": 4, "vocab_limit": 15},
                "intermediate": {
                    "duration": 18,
                    "phase_duration": 5,
                    "vocab_limit": 22,
                },
                "advanced": {"duration": 25, "phase_duration": 6, "vocab_limit": 26},
            },
            success_metrics=[
                "Accurately describe immediate family",
                "Use appropriate relationship vocabulary",
                "Share family story or tradition",
                "Ask follow-up questions about family",
                "Navigate sensitive topics appropriately",
            ],
        )

    def _create_restaurant_template(self) -> UniversalScenarioTemplate:
        """Create restaurant and dining template"""
        return UniversalScenarioTemplate(
            template_id="restaurant_dining",
            name="Restaurant and Dining",
            category=ScenarioCategory.RESTAURANT,
            tier=1,
            base_vocabulary=[
                "restaurant",
                "menu",
                "waiter",
                "waitress",
                "table",
                "reservation",
                "order",
                "appetizer",
                "main course",
                "dessert",
                "drink",
                "beverage",
                "bill",
                "check",
                "tip",
                "payment",
                "credit card",
                "cash",
                "delicious",
                "tasty",
                "spicy",
                "mild",
                "vegetarian",
                "allergy",
            ],
            essential_phrases={
                "beginner": [
                    "Table for two, please",
                    "Can I see the menu?",
                    "I would like...",
                    "What do you recommend?",
                    "The check, please",
                    "How much is the tip?",
                ],
                "intermediate": [
                    "Do you have a table available?",
                    "What's the specialty of the house?",
                    "I'm allergic to...",
                    "Could you make that less spicy?",
                    "We're ready to order",
                    "Could we get separate checks?",
                ],
                "advanced": [
                    "We'd like to make a reservation",
                    "Could you describe this dish?",
                    "What wine would pair well with...?",
                    "Is this dish prepared with...?",
                    "We're celebrating a special occasion",
                    "The service has been excellent",
                ],
            },
            cultural_context={
                "notes": "Dining customs vary globally. Tipping practices, meal timing, and dining etiquette differ significantly between cultures.",
                "tipping_customs": ["included", "expected", "optional", "offensive"],
                "dining_styles": [
                    "family_style",
                    "individual_plates",
                    "buffet",
                    "course_by_course",
                ],
                "meal_times": ["early", "late", "multiple_seatings"],
            },
            learning_objectives=[
                "Navigate restaurant interactions confidently",
                "Order food and drinks appropriately",
                "Handle payment and tipping",
                "Express dietary restrictions and preferences",
                "Engage in pleasant dining conversation",
            ],
            conversation_starters=[
                "Have you been here before?",
                "What looks good to you?",
                "Excuse me, could we order?",
                "Is this your first time trying this cuisine?",
                "How's your meal?",
            ],
            scenario_variations=[
                {
                    "id": "casual_dining",
                    "description": "Casual restaurant or cafe experience",
                    "setting": "Local restaurant, cafe, or bistro",
                    "phases": [
                        "arrival_seating",
                        "menu_browsing",
                        "ordering",
                        "dining_conversation",
                        "payment_departure",
                    ],
                },
                {
                    "id": "fine_dining",
                    "description": "Upscale restaurant experience",
                    "setting": "High-end restaurant with formal service",
                    "phases": [
                        "reservation_arrival",
                        "wine_selection",
                        "course_ordering",
                        "dining_etiquette",
                        "appreciation_payment",
                    ],
                },
                {
                    "id": "fast_casual",
                    "description": "Quick service restaurant",
                    "setting": "Fast-casual chain or counter service",
                    "phases": [
                        "menu_decision",
                        "counter_ordering",
                        "payment",
                        "pickup_seating",
                        "quick_meal",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 15, "phase_duration": 4, "vocab_limit": 15},
                "intermediate": {
                    "duration": 20,
                    "phase_duration": 5,
                    "vocab_limit": 20,
                },
                "advanced": {"duration": 25, "phase_duration": 6, "vocab_limit": 25},
            },
            success_metrics=[
                "Successfully place an order",
                "Handle dietary restrictions",
                "Calculate appropriate tip",
                "Engage in mealtime conversation",
                "Complete payment process",
            ],
        )

    def _create_transportation_template(self) -> UniversalScenarioTemplate:
        """Create transportation template"""
        return UniversalScenarioTemplate(
            template_id="transportation",
            name="Transportation",
            category=ScenarioCategory.TRAVEL,
            tier=1,
            base_vocabulary=[
                "bus",
                "train",
                "subway",
                "taxi",
                "uber",
                "car",
                "bicycle",
                "airport",
                "station",
                "stop",
                "ticket",
                "fare",
                "schedule",
                "departure",
                "arrival",
                "platform",
                "gate",
                "seat",
                "luggage",
                "directions",
                "map",
                "GPS",
                "traffic",
                "delayed",
                "on time",
            ],
            essential_phrases={
                "beginner": [
                    "Where is the bus stop?",
                    "How much is the ticket?",
                    "When does the next train arrive?",
                    "I need to go to...",
                    "Is this the right platform?",
                    "Excuse me, is this seat taken?",
                ],
                "intermediate": [
                    "What's the best way to get to...?",
                    "How long does the journey take?",
                    "Do I need to transfer?",
                    "Is there a direct route?",
                    "What time does the last bus leave?",
                    "Can you call me a taxi?",
                ],
                "advanced": [
                    "Are there any delays on this route?",
                    "What's the most efficient route during rush hour?",
                    "Is there a monthly pass available?",
                    "Could you help me with the ticket machine?",
                    "What are the peak travel times?",
                    "Is there wheelchair accessibility?",
                ],
            },
            cultural_context={
                "notes": "Transportation systems vary greatly between cities and countries. Payment methods, etiquette, and accessibility differ.",
                "payment_methods": ["cash", "card", "mobile_app", "contactless"],
                "etiquette": ["quiet_zones", "priority_seating", "boarding_order"],
                "accessibility": ["wheelchair", "elderly", "pregnant", "disabled"],
            },
            learning_objectives=[
                "Navigate public transportation systems",
                "Purchase tickets and understand pricing",
                "Ask for and understand directions",
                "Handle transportation delays and changes",
                "Practice transportation-related vocabulary",
            ],
            conversation_starters=[
                "Excuse me, how do I get to...?",
                "Is this the right train for...?",
                "Do you know when the next bus comes?",
                "What's the best way to the airport?",
                "Have you used this app before?",
            ],
            scenario_variations=[
                {
                    "id": "public_transit",
                    "description": "Using buses, trains, or subway systems",
                    "setting": "Public transportation network",
                    "phases": [
                        "route_planning",
                        "ticket_purchase",
                        "boarding",
                        "journey",
                        "arrival_exit",
                    ],
                },
                {
                    "id": "ride_sharing",
                    "description": "Using taxi, Uber, or similar services",
                    "setting": "City streets and ride-sharing apps",
                    "phases": [
                        "booking_request",
                        "driver_communication",
                        "pickup",
                        "journey_conversation",
                        "payment_rating",
                    ],
                },
                {
                    "id": "airport_travel",
                    "description": "Navigating airport transportation",
                    "setting": "Airport and surrounding transport hubs",
                    "phases": [
                        "transport_selection",
                        "luggage_handling",
                        "check_in_process",
                        "security_navigation",
                        "gate_finding",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 12, "phase_duration": 3, "vocab_limit": 15},
                "intermediate": {
                    "duration": 18,
                    "phase_duration": 4,
                    "vocab_limit": 20,
                },
                "advanced": {"duration": 22, "phase_duration": 5, "vocab_limit": 25},
            },
            success_metrics=[
                "Successfully navigate to destination",
                "Purchase correct ticket or fare",
                "Understand schedule and timing",
                "Ask for help when needed",
                "Handle unexpected delays",
            ],
        )

    def _create_home_neighborhood_template(self) -> UniversalScenarioTemplate:
        """Create home and neighborhood template"""
        return UniversalScenarioTemplate(
            template_id="home_neighborhood",
            name="Home and Neighborhood",
            category=ScenarioCategory.DAILY_LIFE,
            tier=1,
            base_vocabulary=[
                "home",
                "house",
                "apartment",
                "building",
                "neighborhood",
                "street",
                "address",
                "mailbox",
                "key",
                "door",
                "window",
                "garden",
                "yard",
                "neighbor",
                "landlord",
                "rent",
                "utilities",
                "electricity",
                "water",
                "heating",
                "air conditioning",
                "furniture",
                "kitchen",
                "bathroom",
                "bedroom",
            ],
            essential_phrases={
                "beginner": [
                    "I live in...",
                    "My address is...",
                    "Where do you live?",
                    "Is this a good neighborhood?",
                    "How long have you lived here?",
                    "I like my apartment",
                ],
                "intermediate": [
                    "What's the neighborhood like?",
                    "Are there good schools nearby?",
                    "Is it safe to walk at night?",
                    "Where's the closest grocery store?",
                    "How's the public transportation?",
                    "The rent is reasonable",
                ],
                "advanced": [
                    "What amenities are available in the area?",
                    "How's the cost of living here?",
                    "Are there any noise issues?",
                    "What's the community like?",
                    "Are there local events or activities?",
                    "I'm thinking of buying in this area",
                ],
            },
            cultural_context={
                "notes": "Living arrangements and neighborhood concepts vary culturally. Some cultures emphasize community, others privacy.",
                "housing_types": [
                    "single_family",
                    "apartment",
                    "condo",
                    "shared_housing",
                ],
                "community_aspects": [
                    "neighborhood_watch",
                    "local_events",
                    "shared_spaces",
                ],
                "privacy_norms": [
                    "close_neighbors",
                    "distant_neighbors",
                    "community_involvement",
                ],
            },
            learning_objectives=[
                "Describe living situation and home",
                "Discuss neighborhood characteristics",
                "Ask about local amenities and services",
                "Express preferences about housing",
                "Navigate housing-related conversations",
            ],
            conversation_starters=[
                "Do you live around here?",
                "What's this area like?",
                "I'm new to the neighborhood",
                "Can you recommend any local places?",
                "How do you like living here?",
            ],
            scenario_variations=[
                {
                    "id": "new_resident",
                    "description": "Just moved to a new area",
                    "setting": "New neighborhood exploration",
                    "phases": [
                        "area_orientation",
                        "neighbor_introductions",
                        "local_services",
                        "community_integration",
                    ],
                },
                {
                    "id": "house_hunting",
                    "description": "Looking for a new place to live",
                    "setting": "Apartment viewing or house hunting",
                    "phases": [
                        "location_discussion",
                        "property_features",
                        "neighborhood_assessment",
                        "decision_making",
                    ],
                },
                {
                    "id": "neighbor_chat",
                    "description": "Casual conversation with neighbors",
                    "setting": "Building hallway, garden, or local area",
                    "phases": [
                        "friendly_greeting",
                        "local_updates",
                        "shared_concerns",
                        "future_interactions",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 10, "phase_duration": 3, "vocab_limit": 15},
                "intermediate": {
                    "duration": 15,
                    "phase_duration": 4,
                    "vocab_limit": 20,
                },
                "advanced": {"duration": 20, "phase_duration": 5, "vocab_limit": 25},
            },
            success_metrics=[
                "Describe home and living situation",
                "Discuss neighborhood features",
                "Ask relevant questions about area",
                "Express housing preferences",
                "Build neighborly relationships",
            ],
        )

    def create_scenario(
        self,
        template_id: str,
        difficulty: ScenarioDifficulty,
        user_role: ConversationRole,
        ai_role: ConversationRole,
        variation_id: Optional[str] = None,
    ) -> Optional[ConversationScenario]:
        """Create a scenario from a template"""
        template = self.universal_templates.get(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return None

        return template.generate_scenario(difficulty, user_role, ai_role, variation_id)

    def get_available_templates(
        self, tier: Optional[int] = None
    ) -> List[UniversalScenarioTemplate]:
        """Get all available templates, optionally filtered by tier"""
        templates = list(self.universal_templates.values())
        if tier is not None:
            templates = [t for t in templates if t.tier == tier]
        return sorted(templates, key=lambda t: (t.tier, t.name))

    def get_templates_by_category(
        self, category: ScenarioCategory
    ) -> List[UniversalScenarioTemplate]:
        """Get templates by category"""
        return [t for t in self.universal_templates.values() if t.category == category]


class ScenarioManager:
    """Main scenario management class"""

    def __init__(self):
        self.scenarios: Dict[str, ConversationScenario] = {}
        self.active_scenarios: Dict[str, ScenarioProgress] = {}
        self.scenario_templates = self._initialize_scenario_templates()
        self.scenario_factory = ScenarioFactory()
        self._load_predefined_scenarios()
        self._initialized = False

    async def initialize(self):
        """Initialize async components"""
        if not self._initialized:
            await self._load_scenarios_from_file()
            self._initialized = True

    def _initialize_scenario_templates(self) -> Dict[str, Any]:
        """Initialize scenario templates for different categories"""
        return {
            "restaurant": {
                "phases": ["arrival", "ordering", "dining", "payment"],
                "vocabulary": ["menu", "waiter", "order", "bill", "tip", "reservation"],
                "cultural_aspects": [
                    "dining_etiquette",
                    "tipping_customs",
                    "meal_times",
                ],
            },
            "travel": {
                "phases": [
                    "booking",
                    "check_in",
                    "navigation",
                    "sightseeing",
                    "check_out",
                ],
                "vocabulary": [
                    "passport",
                    "ticket",
                    "luggage",
                    "directions",
                    "tourist",
                    "hotel",
                ],
                "cultural_aspects": [
                    "travel_customs",
                    "local_transportation",
                    "tourist_attractions",
                ],
            },
            "shopping": {
                "phases": [
                    "browsing",
                    "inquiring",
                    "trying_on",
                    "negotiating",
                    "purchasing",
                ],
                "vocabulary": [
                    "price",
                    "size",
                    "color",
                    "quality",
                    "discount",
                    "receipt",
                ],
                "cultural_aspects": [
                    "bargaining_culture",
                    "shopping_etiquette",
                    "payment_methods",
                ],
            },
            "business": {
                "phases": [
                    "introduction",
                    "presentation",
                    "discussion",
                    "negotiation",
                    "conclusion",
                ],
                "vocabulary": [
                    "meeting",
                    "proposal",
                    "deadline",
                    "contract",
                    "agreement",
                    "schedule",
                ],
                "cultural_aspects": [
                    "business_etiquette",
                    "hierarchy",
                    "communication_style",
                ],
            },
        }

    def _load_predefined_scenarios(self):
        """Load predefined scenarios into the system"""

        # Restaurant scenario
        restaurant_scenario = ConversationScenario(
            scenario_id="restaurant_dinner_reservation",
            name="Making a Dinner Reservation",
            category=ScenarioCategory.RESTAURANT,
            difficulty=ScenarioDifficulty.BEGINNER,
            description="Practice making a dinner reservation at a restaurant, ordering food, and handling the bill.",
            user_role=ConversationRole.CUSTOMER,
            ai_role=ConversationRole.SERVICE_PROVIDER,
            setting="An upscale restaurant in the city center",
            duration_minutes=15,
            phases=[
                ScenarioPhase(
                    phase_id="reservation",
                    name="Making the Reservation",
                    description="Call or visit to make a dinner reservation",
                    expected_duration_minutes=3,
                    key_vocabulary=[
                        "reservation",
                        "table",
                        "party",
                        "time",
                        "available",
                    ],
                    essential_phrases=[
                        "I'd like to make a reservation",
                        "For how many people?",
                        "What time would you prefer?",
                        "We have availability at...",
                    ],
                    learning_objectives=[
                        "Use polite language for requests",
                        "Understand time expressions",
                        "Handle scheduling conflicts",
                    ],
                    cultural_notes="In many cultures, advance reservations are expected for dinner at upscale restaurants.",
                    success_criteria=[
                        "Successfully request a reservation",
                        "Provide party size and preferred time",
                        "Confirm reservation details",
                    ],
                ),
                ScenarioPhase(
                    phase_id="arrival_seating",
                    name="Arrival and Seating",
                    description="Arrive at the restaurant and get seated",
                    expected_duration_minutes=2,
                    key_vocabulary=[
                        "host",
                        "hostess",
                        "table",
                        "booth",
                        "window",
                        "ready",
                    ],
                    essential_phrases=[
                        "We have a reservation under...",
                        "Right this way, please",
                        "Your table is ready",
                        "Would you prefer a table or booth?",
                    ],
                    learning_objectives=[
                        "Check in for reservation",
                        "Express seating preferences",
                        "Follow directions",
                    ],
                    success_criteria=[
                        "Check in with reservation name",
                        "Follow host to table",
                        "Express any seating preferences",
                    ],
                ),
                ScenarioPhase(
                    phase_id="ordering",
                    name="Ordering Food and Drinks",
                    description="Review menu and place your order",
                    expected_duration_minutes=7,
                    key_vocabulary=[
                        "menu",
                        "appetizer",
                        "entrée",
                        "beverage",
                        "special",
                        "allergy",
                    ],
                    essential_phrases=[
                        "What would you recommend?",
                        "I'll have the...",
                        "How is that prepared?",
                        "Any allergies or dietary restrictions?",
                    ],
                    learning_objectives=[
                        "Ask for recommendations",
                        "Place complete order",
                        "Ask about food preparation",
                        "Communicate dietary needs",
                    ],
                    success_criteria=[
                        "Order appetizer and main course",
                        "Ask at least one question about the menu",
                        "Choose appropriate beverages",
                    ],
                ),
                ScenarioPhase(
                    phase_id="payment",
                    name="Paying the Bill",
                    description="Review bill, tip appropriately, and complete payment",
                    expected_duration_minutes=3,
                    key_vocabulary=[
                        "bill",
                        "check",
                        "tip",
                        "credit card",
                        "cash",
                        "receipt",
                    ],
                    essential_phrases=[
                        "Could we have the check, please?",
                        "Is tip included?",
                        "I'll pay with credit card",
                        "Thank you for excellent service",
                    ],
                    learning_objectives=[
                        "Request the bill politely",
                        "Understand tipping customs",
                        "Complete payment transaction",
                        "Express satisfaction",
                    ],
                    success_criteria=[
                        "Request and review the bill",
                        "Calculate and add appropriate tip",
                        "Complete payment successfully",
                    ],
                ),
            ],
            vocabulary_focus=[
                "reservation",
                "table",
                "menu",
                "order",
                "waiter",
                "waitress",
                "appetizer",
                "entrée",
                "dessert",
                "beverage",
                "bill",
                "tip",
            ],
            cultural_context={
                "tipping_culture": "Standard tip is 15-20% for good service",
                "dining_etiquette": "Wait for everyone to be served before eating",
                "payment_customs": "Usually one person pays for the group",
            },
            learning_goals=[
                "Navigate restaurant interactions confidently",
                "Use polite service language",
                "Understand dining cultural norms",
            ],
            prerequisites=["basic_greetings", "numbers", "time_expressions"],
        )

        # Travel scenario
        travel_scenario = ConversationScenario(
            scenario_id="hotel_check_in",
            name="Hotel Check-in Process",
            category=ScenarioCategory.TRAVEL,
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            description="Check into a hotel, handle room requests, and get local information.",
            user_role=ConversationRole.TOURIST,
            ai_role=ConversationRole.SERVICE_PROVIDER,
            setting="Hotel reception desk in a foreign country",
            duration_minutes=12,
            phases=[
                ScenarioPhase(
                    phase_id="check_in",
                    name="Hotel Check-in",
                    description="Provide reservation details and complete check-in process",
                    expected_duration_minutes=4,
                    key_vocabulary=[
                        "reservation",
                        "passport",
                        "ID",
                        "confirmation",
                        "room key",
                    ],
                    essential_phrases=[
                        "I have a reservation under...",
                        "Could I see your ID please?",
                        "Here's your room key",
                        "Your room is on the third floor",
                    ],
                    learning_objectives=[
                        "Present reservation information",
                        "Understand check-in procedures",
                        "Handle document requests",
                    ],
                    success_criteria=[
                        "Provide reservation details",
                        "Present required documents",
                        "Receive room assignment",
                    ],
                ),
                ScenarioPhase(
                    phase_id="room_preferences",
                    name="Room Preferences and Requests",
                    description="Discuss room features and make special requests",
                    expected_duration_minutes=3,
                    key_vocabulary=[
                        "view",
                        "balcony",
                        "smoking",
                        "non-smoking",
                        "upgrade",
                        "amenities",
                    ],
                    essential_phrases=[
                        "Is there a room with a view?",
                        "Could I request a non-smoking room?",
                        "Are there any upgrades available?",
                        "What amenities are included?",
                    ],
                    learning_objectives=[
                        "Express preferences politely",
                        "Ask about available options",
                        "Understand room features",
                    ],
                    success_criteria=[
                        "Make at least one room preference request",
                        "Ask about hotel amenities",
                        "Understand upgrade options",
                    ],
                ),
                ScenarioPhase(
                    phase_id="local_information",
                    name="Getting Local Information",
                    description="Ask for directions and recommendations for local attractions",
                    expected_duration_minutes=5,
                    key_vocabulary=[
                        "directions",
                        "restaurant",
                        "tourist",
                        "attraction",
                        "transportation",
                        "map",
                    ],
                    essential_phrases=[
                        "What would you recommend for sightseeing?",
                        "How do I get to...?",
                        "Are there good restaurants nearby?",
                        "Could you mark it on the map?",
                    ],
                    learning_objectives=[
                        "Ask for recommendations",
                        "Understand directions",
                        "Get local insights",
                    ],
                    success_criteria=[
                        "Ask for restaurant recommendations",
                        "Get directions to at least one attraction",
                        "Understand transportation options",
                    ],
                ),
            ],
            vocabulary_focus=[
                "reservation",
                "check-in",
                "passport",
                "room",
                "key",
                "floor",
                "elevator",
                "directions",
                "restaurant",
                "attraction",
                "map",
            ],
            cultural_context={
                "hospitality_customs": "Hotel staff are usually very helpful with tourist information",
                "tipping_culture": "Small tips for helpful service are appreciated",
                "local_etiquette": "Always be polite and patient with language barriers",
            },
            learning_goals=[
                "Handle travel check-in procedures",
                "Ask for local recommendations",
                "Navigate tourist interactions",
            ],
            prerequisites=["travel_vocabulary", "directions", "polite_requests"],
        )

        # Shopping scenario
        shopping_scenario = ConversationScenario(
            scenario_id="clothing_shopping",
            name="Clothes Shopping Experience",
            category=ScenarioCategory.SHOPPING,
            difficulty=ScenarioDifficulty.BEGINNER,
            description="Shop for clothes, try on items, and make purchases.",
            user_role=ConversationRole.CUSTOMER,
            ai_role=ConversationRole.SERVICE_PROVIDER,
            setting="Clothing store in a shopping mall",
            duration_minutes=10,
            phases=[
                ScenarioPhase(
                    phase_id="browsing",
                    name="Browsing and Initial Inquiry",
                    description="Look around the store and ask for help",
                    expected_duration_minutes=3,
                    key_vocabulary=[
                        "size",
                        "color",
                        "style",
                        "price",
                        "section",
                        "looking for",
                    ],
                    essential_phrases=[
                        "I'm looking for...",
                        "What size do you need?",
                        "Do you have this in blue?",
                        "Where can I find...?",
                    ],
                    learning_objectives=[
                        "Express what you're looking for",
                        "Ask about sizes and colors",
                        "Navigate store layout",
                    ],
                    success_criteria=[
                        "Ask for help finding items",
                        "Specify size and color preferences",
                        "Understand store organization",
                    ],
                ),
                ScenarioPhase(
                    phase_id="trying_on",
                    name="Trying on Clothes",
                    description="Use fitting room and get feedback on fit",
                    expected_duration_minutes=4,
                    key_vocabulary=[
                        "fitting room",
                        "try on",
                        "fit",
                        "tight",
                        "loose",
                        "perfect",
                    ],
                    essential_phrases=[
                        "Where are the fitting rooms?",
                        "How does it fit?",
                        "It's a bit tight",
                        "Do you have a larger size?",
                    ],
                    learning_objectives=[
                        "Use fitting room facilities",
                        "Describe how clothes fit",
                        "Ask for different sizes",
                    ],
                    success_criteria=[
                        "Successfully use fitting room",
                        "Describe fit using appropriate vocabulary",
                        "Request size adjustments",
                    ],
                ),
                ScenarioPhase(
                    phase_id="purchasing",
                    name="Making the Purchase",
                    description="Decide on items and complete the purchase",
                    expected_duration_minutes=3,
                    key_vocabulary=[
                        "buy",
                        "purchase",
                        "receipt",
                        "credit card",
                        "cash",
                        "total",
                    ],
                    essential_phrases=[
                        "I'll take this one",
                        "How much is the total?",
                        "Do you accept credit cards?",
                        "Could I have a receipt?",
                    ],
                    learning_objectives=[
                        "Make purchase decisions",
                        "Handle payment process",
                        "Get transaction documentation",
                    ],
                    success_criteria=[
                        "Decide on items to purchase",
                        "Complete payment successfully",
                        "Receive receipt and items",
                    ],
                ),
            ],
            vocabulary_focus=[
                "clothes",
                "shirt",
                "pants",
                "dress",
                "shoes",
                "size",
                "color",
                "fitting room",
                "try on",
                "buy",
                "price",
                "receipt",
            ],
            cultural_context={
                "shopping_etiquette": "It's normal to try on clothes before buying",
                "payment_methods": "Most stores accept both cash and cards",
                "return_policy": "Keep receipts for returns or exchanges",
            },
            learning_goals=[
                "Shop for personal items confidently",
                "Describe clothing and fit",
                "Handle retail transactions",
            ],
            prerequisites=["colors", "numbers", "clothing_vocabulary"],
        )

        # Store scenarios
        self.scenarios[restaurant_scenario.scenario_id] = restaurant_scenario
        self.scenarios[travel_scenario.scenario_id] = travel_scenario
        self.scenarios[shopping_scenario.scenario_id] = shopping_scenario

        logger.info(f"Loaded {len(self.scenarios)} predefined scenarios")

    def get_available_scenarios(
        self,
        category: Optional[ScenarioCategory] = None,
        difficulty: Optional[ScenarioDifficulty] = None,
        user_level: str = "intermediate",
    ) -> List[Dict[str, Any]]:
        """Get list of available scenarios with optional filtering"""

        scenarios = list(self.scenarios.values())

        # Filter by category
        if category:
            scenarios = [s for s in scenarios if s.category == category]

        # Filter by difficulty
        if difficulty:
            scenarios = [s for s in scenarios if s.difficulty == difficulty]

        # Convert to dictionary format for API response
        scenario_list = []
        for scenario in scenarios:
            scenario_list.append(
                {
                    "scenario_id": scenario.scenario_id,
                    "name": scenario.name,
                    "category": scenario.category.value,
                    "difficulty": scenario.difficulty.value,
                    "description": scenario.description,
                    "duration_minutes": scenario.duration_minutes,
                    "user_role": scenario.user_role.value,
                    "ai_role": scenario.ai_role.value,
                    "setting": scenario.setting,
                    "vocabulary_count": len(scenario.vocabulary_focus),
                    "phase_count": len(scenario.phases),
                    "learning_goals": scenario.learning_goals[
                        :3
                    ],  # First 3 goals for preview
                }
            )

        return scenario_list

    def get_scenario_details(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific scenario"""

        if scenario_id not in self.scenarios:
            return None

        scenario = self.scenarios[scenario_id]

        return {
            "scenario_id": scenario.scenario_id,
            "name": scenario.name,
            "category": scenario.category.value,
            "difficulty": scenario.difficulty.value,
            "description": scenario.description,
            "user_role": scenario.user_role.value,
            "ai_role": scenario.ai_role.value,
            "setting": scenario.setting,
            "duration_minutes": scenario.duration_minutes,
            "phases": [
                {
                    "phase_id": phase.phase_id,
                    "name": phase.name,
                    "description": phase.description,
                    "duration_minutes": phase.expected_duration_minutes,
                    "vocabulary": phase.key_vocabulary,
                    "phrases": phase.essential_phrases,
                    "objectives": phase.learning_objectives,
                    "cultural_notes": phase.cultural_notes,
                    "success_criteria": phase.success_criteria,
                }
                for phase in scenario.phases
            ],
            "vocabulary_focus": scenario.vocabulary_focus,
            "cultural_context": scenario.cultural_context,
            "learning_goals": scenario.learning_goals,
            "prerequisites": scenario.prerequisites,
        }

    def get_universal_templates(
        self, tier: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get available universal scenario templates"""
        templates = self.scenario_factory.get_available_templates(tier)

        return [
            {
                "template_id": template.template_id,
                "name": template.name,
                "category": template.category.value,
                "tier": template.tier,
                "description": f"Tier {template.tier} - {template.name}",
                "vocabulary_count": len(template.base_vocabulary),
                "variations": len(template.scenario_variations),
                "learning_objectives": template.learning_objectives[:3],  # Preview
                "conversation_starters": template.conversation_starters[:2],  # Preview
            }
            for template in templates
        ]

    def create_scenario_from_template(
        self,
        template_id: str,
        difficulty: ScenarioDifficulty,
        user_role: ConversationRole = ConversationRole.STUDENT,
        ai_role: ConversationRole = ConversationRole.TEACHER,
        variation_id: Optional[str] = None,
    ) -> Optional[ConversationScenario]:
        """Create a new scenario instance from a universal template"""
        scenario = self.scenario_factory.create_scenario(
            template_id, difficulty, user_role, ai_role, variation_id
        )

        if scenario:
            # Add to scenarios collection for immediate use
            self.scenarios[scenario.scenario_id] = scenario
            logger.info(
                f"Created scenario from template {template_id}: {scenario.scenario_id}"
            )

        return scenario

    def get_tier1_scenarios(self) -> List[Dict[str, Any]]:
        """Get all Tier 1 (essential) scenario templates"""
        return self.get_universal_templates(tier=1)

    def get_scenarios_by_category(
        self, category: ScenarioCategory
    ) -> List[Dict[str, Any]]:
        """Get all available scenarios (both predefined and template-based) by category"""
        # Get predefined scenarios
        predefined = [
            {
                "scenario_id": s.scenario_id,
                "name": s.name,
                "type": "predefined",
                "difficulty": s.difficulty.value,
                "description": s.description,
            }
            for s in self.scenarios.values()
            if s.category == category
        ]

        # Get universal templates for this category
        templates = [
            {
                "template_id": t.template_id,
                "name": t.name,
                "type": "template",
                "tier": t.tier,
                "description": f"Tier {t.tier} - {t.name} (customizable)",
                "variations": len(t.scenario_variations),
            }
            for t in self.scenario_factory.get_templates_by_category(category)
        ]

        return {
            "category": category.value,
            "predefined_scenarios": predefined,
            "universal_templates": templates,
            "total_count": len(predefined) + len(templates),
        }

    async def start_scenario_conversation(
        self, user_id: str, scenario_id: str, language: str = "en"
    ) -> Dict[str, Any]:
        """Start a new scenario-based conversation"""

        if scenario_id not in self.scenarios:
            raise ValueError(f"Scenario {scenario_id} not found")

        scenario = self.scenarios[scenario_id]

        # Create scenario progress tracking
        progress = ScenarioProgress(
            scenario_id=scenario_id,
            user_id=user_id,
            current_phase=0,
            phase_progress={},
            vocabulary_mastered=[],
            objectives_completed=[],
            start_time=datetime.now(),
            last_activity=datetime.now(),
            total_attempts=1,
            success_rate=0.0,
        )

        # Store active scenario
        progress_id = f"{user_id}_{scenario_id}_{int(datetime.now().timestamp())}"
        self.active_scenarios[progress_id] = progress

        # Generate opening message for the scenario
        opening_message = self._generate_scenario_opening(scenario, language)

        logger.info(f"Started scenario {scenario_id} for user {user_id}")

        return {
            "progress_id": progress_id,
            "scenario": scenario.name,
            "current_phase": scenario.phases[0].name,
            "setting": scenario.setting,
            "your_role": scenario.user_role.value,
            "ai_role": scenario.ai_role.value,
            "opening_message": opening_message,
            "phase_objectives": scenario.phases[0].learning_objectives,
            "key_vocabulary": scenario.phases[0].key_vocabulary,
            "cultural_context": scenario.cultural_context,
        }

    def _generate_scenario_opening(
        self, scenario: ConversationScenario, language: str = "en"
    ) -> str:
        """Generate an opening message for the scenario"""

        first_phase = scenario.phases[0]

        # Create contextual opening based on scenario
        opening_templates = {
            ScenarioCategory.RESTAURANT: f"Welcome! You are now at {scenario.setting}. As a {scenario.user_role.value}, you want to {first_phase.description.lower()}. I'm the {scenario.ai_role.value} here to help you. How may I assist you today?",
            ScenarioCategory.TRAVEL: f"Hello! You've just arrived at {scenario.setting}. As a {scenario.user_role.value}, you need to {first_phase.description.lower()}. I'm here as the {scenario.ai_role.value} to help you. What can I do for you?",
            ScenarioCategory.SHOPPING: f"Good day! Welcome to our store. You're here as a {scenario.user_role.value} looking to {first_phase.description.lower()}. I'm a {scenario.ai_role.value} ready to help. What are you looking for today?",
            ScenarioCategory.BUSINESS: f"Good morning! Welcome to our {scenario.setting}. In your role as {scenario.user_role.value}, you're here to {first_phase.description.lower()}. As the {scenario.ai_role.value}, I'm pleased to meet with you. Shall we begin?",
        }

        base_message = opening_templates.get(
            scenario.category,
            f"Welcome to this {scenario.category.value} scenario! You are a {scenario.user_role.value} and I am the {scenario.ai_role.value}. Let's begin this conversation practice.",
        )

        # Add vocabulary hint
        vocab_hint = f"\n\n📚 Key vocabulary for this phase: {', '.join(first_phase.key_vocabulary[:5])}"
        if len(first_phase.key_vocabulary) > 5:
            vocab_hint += "..."

        # Add cultural note if available
        cultural_note = ""
        if first_phase.cultural_notes:
            cultural_note = f"\n\n🌍 Cultural note: {first_phase.cultural_notes}"

        return base_message + vocab_hint + cultural_note

    async def process_scenario_message(
        self, progress_id: str, user_message: str, ai_response: str
    ) -> Dict[str, Any]:
        """Process a message within a scenario and track progress"""

        if progress_id not in self.active_scenarios:
            raise ValueError(f"Scenario progress {progress_id} not found")

        progress = self.active_scenarios[progress_id]
        scenario = self.scenarios[progress.scenario_id]
        current_phase = scenario.phases[progress.current_phase]

        # Analyze user message for learning progress
        analysis = await self._analyze_scenario_message(
            user_message=user_message,
            ai_response=ai_response,
            current_phase=current_phase,
            progress=progress,
        )

        # Update progress
        progress.last_activity = datetime.now()

        # Check if phase objectives are met
        phase_completion = self._check_phase_completion(
            analysis=analysis, current_phase=current_phase, progress=progress
        )

        # Advance to next phase if current phase is complete
        next_phase_info = None
        if (
            phase_completion["is_complete"]
            and progress.current_phase < len(scenario.phases) - 1
        ):
            progress.current_phase += 1
            next_phase = scenario.phases[progress.current_phase]
            next_phase_info = {
                "phase_name": next_phase.name,
                "description": next_phase.description,
                "objectives": next_phase.learning_objectives,
                "vocabulary": next_phase.key_vocabulary,
                "essential_phrases": next_phase.essential_phrases,
            }

        # Calculate overall scenario completion
        overall_completion = (progress.current_phase + 1) / len(scenario.phases)

        return {
            "progress_id": progress_id,
            "current_phase": current_phase.name,
            "phase_completion": phase_completion,
            "overall_completion": overall_completion,
            "vocabulary_progress": analysis["vocabulary_used"],
            "objectives_met": analysis["objectives_addressed"],
            "learning_feedback": analysis["learning_feedback"],
            "next_phase": next_phase_info,
            "scenario_complete": progress.current_phase >= len(scenario.phases) - 1
            and phase_completion["is_complete"],
        }

    async def _analyze_scenario_message(
        self,
        user_message: str,
        ai_response: str,
        current_phase: ScenarioPhase,
        progress: ScenarioProgress,
    ) -> Dict[str, Any]:
        """Analyze user message within scenario context"""

        # Check vocabulary usage
        user_words = set(user_message.lower().split())
        phase_vocab = set(word.lower() for word in current_phase.key_vocabulary)
        vocabulary_used = list(user_words.intersection(phase_vocab))

        # Check essential phrases usage
        essential_phrases_used = []
        for phrase in current_phase.essential_phrases:
            if phrase.lower() in user_message.lower():
                essential_phrases_used.append(phrase)

        # Check objectives addressed (simple keyword matching)
        objectives_addressed = []
        for objective in current_phase.learning_objectives:
            # Simple heuristic: if user message relates to objective keywords
            objective_keywords = objective.lower().split()
            if any(keyword in user_message.lower() for keyword in objective_keywords):
                objectives_addressed.append(objective)

        # Generate learning feedback
        feedback = []
        if vocabulary_used:
            feedback.append(
                f"Great use of key vocabulary: {', '.join(vocabulary_used)}"
            )
        if essential_phrases_used:
            feedback.append(
                f"Perfect! You used essential phrases: {', '.join(essential_phrases_used)}"
            )
        if len(user_message.split()) >= 5:
            feedback.append(
                "Good sentence length - you're expressing complete thoughts"
            )

        return {
            "vocabulary_used": vocabulary_used,
            "phrases_used": essential_phrases_used,
            "objectives_addressed": objectives_addressed,
            "learning_feedback": feedback,
            "engagement_score": min(len(user_message) / 50, 1.0),
            "message_complexity": len(user_message.split()),
        }

    def _check_phase_completion(
        self,
        analysis: Dict[str, Any],
        current_phase: ScenarioPhase,
        progress: ScenarioProgress,
    ) -> Dict[str, Any]:
        """Check if current phase objectives are completed"""

        # Calculate completion score based on success criteria
        criteria_met = 0
        total_criteria = len(current_phase.success_criteria)

        if total_criteria == 0:
            # If no specific criteria, use general heuristics
            completion_score = 0.0
            if analysis["vocabulary_used"]:
                completion_score += 0.3
            if analysis["phrases_used"]:
                completion_score += 0.3
            if analysis["objectives_addressed"]:
                completion_score += 0.4

            is_complete = completion_score >= 0.6
        else:
            # Check specific success criteria (simplified)
            for criterion in current_phase.success_criteria:
                # Simple keyword matching for criteria
                if any(
                    word in criterion.lower() for word in analysis["vocabulary_used"]
                ):
                    criteria_met += 1
                elif analysis["objectives_addressed"]:
                    criteria_met += 0.5

            completion_score = criteria_met / total_criteria
            is_complete = completion_score >= 0.7

        return {
            "is_complete": is_complete,
            "completion_score": completion_score,
            "criteria_met": criteria_met,
            "total_criteria": total_criteria,
            "next_steps": current_phase.learning_objectives
            if not is_complete
            else ["Phase complete! Moving to next phase."],
        }

    async def get_scenario_progress(self, progress_id: str) -> Optional[Dict[str, Any]]:
        """Get current progress for a scenario"""

        if progress_id not in self.active_scenarios:
            return None

        progress = self.active_scenarios[progress_id]
        scenario = self.scenarios[progress.scenario_id]

        current_phase = scenario.phases[progress.current_phase]
        session_duration = (
            datetime.now() - progress.start_time
        ).total_seconds() / 60  # minutes

        return {
            "progress_id": progress_id,
            "scenario_name": scenario.name,
            "current_phase": {
                "name": current_phase.name,
                "description": current_phase.description,
                "phase_number": progress.current_phase + 1,
                "total_phases": len(scenario.phases),
            },
            "session_stats": {
                "duration_minutes": round(session_duration, 2),
                "completion_percentage": (
                    (progress.current_phase + 1) / len(scenario.phases)
                )
                * 100,
                "vocabulary_mastered": len(progress.vocabulary_mastered),
                "objectives_completed": len(progress.objectives_completed),
            },
            "learning_progress": {
                "vocabulary_mastered": progress.vocabulary_mastered,
                "objectives_completed": progress.objectives_completed,
                "success_rate": progress.success_rate,
            },
        }

    async def complete_scenario(self, progress_id: str) -> Dict[str, Any]:
        """Complete a scenario and generate final summary"""

        if progress_id not in self.active_scenarios:
            raise ValueError(f"Scenario progress {progress_id} not found")

        progress = self.active_scenarios[progress_id]
        scenario = self.scenarios[progress.scenario_id]

        # Calculate final statistics
        session_duration = (datetime.now() - progress.start_time).total_seconds() / 60
        completion_rate = (progress.current_phase + 1) / len(scenario.phases)

        # Generate completion summary
        summary = {
            "progress_id": progress_id,
            "scenario_completed": scenario.name,
            "completion_stats": {
                "duration_minutes": round(session_duration, 2),
                "phases_completed": progress.current_phase + 1,
                "total_phases": len(scenario.phases),
                "completion_rate": round(completion_rate * 100, 1),
                "vocabulary_learned": len(progress.vocabulary_mastered),
                "objectives_achieved": len(progress.objectives_completed),
            },
            "learning_achievements": {
                "vocabulary_mastered": progress.vocabulary_mastered,
                "skills_practiced": [
                    phase.name
                    for phase in scenario.phases[: progress.current_phase + 1]
                ],
                "cultural_insights": list(scenario.cultural_context.values())[:2],
                "next_recommendations": self._get_next_scenario_recommendations(
                    scenario, progress
                ),
            },
            "performance_feedback": {
                "success_rate": progress.success_rate,
                "engagement_level": "high"
                if session_duration >= scenario.duration_minutes * 0.8
                else "moderate",
                "difficulty_assessment": "appropriate"
                if completion_rate >= 0.7
                else "challenging",
            },
        }

        # Clean up completed scenario
        del self.active_scenarios[progress_id]

        logger.info(
            f"Completed scenario {progress.scenario_id} for user {progress.user_id}"
        )

        return summary

    def _get_next_scenario_recommendations(
        self, completed_scenario: ConversationScenario, progress: ScenarioProgress
    ) -> List[Dict[str, str]]:
        """Get recommendations for next scenarios"""

        recommendations = []

        # Same category, higher difficulty
        for scenario in self.scenarios.values():
            if (
                scenario.category == completed_scenario.category
                and scenario.difficulty.value > completed_scenario.difficulty.value
                and scenario.scenario_id != completed_scenario.scenario_id
            ):
                recommendations.append(
                    {
                        "scenario_id": scenario.scenario_id,
                        "name": scenario.name,
                        "reason": f"Advanced {scenario.category.value} practice",
                    }
                )

        # Different category, same difficulty
        for scenario in self.scenarios.values():
            if (
                scenario.category != completed_scenario.category
                and scenario.difficulty == completed_scenario.difficulty
                and len(recommendations) < 3
            ):
                recommendations.append(
                    {
                        "scenario_id": scenario.scenario_id,
                        "name": scenario.name,
                        "reason": f"Practice {scenario.category.value} skills",
                    }
                )

        return recommendations[:3]  # Return top 3 recommendations

    # ===========================
    # Persistence Methods for Admin API
    # ===========================

    async def get_all_scenarios(self) -> List[ConversationScenario]:
        """Get all scenarios for admin management"""
        return list(self.scenarios.values())

    async def get_scenario_by_id(
        self, scenario_id: str
    ) -> Optional[ConversationScenario]:
        """Get a specific scenario by ID"""
        return self.scenarios.get(scenario_id)

    async def save_scenario(self, scenario: ConversationScenario) -> bool:
        """Save or update a scenario"""
        try:
            # Store in memory (in production, this would save to database)
            self.scenarios[scenario.scenario_id] = scenario

            # Save to JSON file for persistence across restarts
            await self._save_scenarios_to_file()

            logger.info(f"Saved scenario: {scenario.name} ({scenario.scenario_id})")
            return True

        except Exception as e:
            logger.error(f"Error saving scenario {scenario.scenario_id}: {str(e)}")
            return False

    async def update_scenario(
        self, scenario_id: str, scenario: ConversationScenario
    ) -> bool:
        """Update an existing scenario (alias for save_scenario)"""
        return await self.save_scenario(scenario)

    async def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario"""
        try:
            if scenario_id in self.scenarios:
                scenario_name = self.scenarios[scenario_id].name
                del self.scenarios[scenario_id]

                # Remove from file storage
                await self._save_scenarios_to_file()

                logger.info(f"Deleted scenario: {scenario_name} ({scenario_id})")
                return True
            else:
                logger.warning(f"Scenario {scenario_id} not found for deletion")
                return False

        except Exception as e:
            logger.error(f"Error deleting scenario {scenario_id}: {str(e)}")
            return False

    async def set_scenario_active(self, scenario_id: str, is_active: bool) -> bool:
        """Set scenario active/inactive status"""
        try:
            if scenario_id in self.scenarios:
                scenario = self.scenarios[scenario_id]
                # Add is_active attribute if it doesn't exist
                scenario.is_active = is_active

                # Save changes
                await self._save_scenarios_to_file()

                status = "activated" if is_active else "deactivated"
                logger.info(f"Scenario {scenario.name} ({scenario_id}) {status}")
                return True
            else:
                logger.warning(f"Scenario {scenario_id} not found")
                return False

        except Exception as e:
            logger.error(f"Error updating scenario {scenario_id} status: {str(e)}")
            return False

    async def _save_scenarios_to_file(self):
        """Save scenarios to JSON file for persistence"""
        try:
            data_dir = Path("data/scenarios")
            data_dir.mkdir(parents=True, exist_ok=True)
            scenarios_file = data_dir / "scenarios.json"

            # Convert scenarios to serializable format
            scenarios_data = {}
            for scenario_id, scenario in self.scenarios.items():
                scenario_dict = {
                    "scenario_id": scenario.scenario_id,
                    "name": scenario.name,
                    "category": scenario.category.value,
                    "difficulty": scenario.difficulty.value,
                    "description": scenario.description,
                    "user_role": scenario.user_role.value,
                    "ai_role": scenario.ai_role.value,
                    "setting": scenario.setting,
                    "duration_minutes": scenario.duration_minutes,
                    "phases": [
                        {
                            "phase_id": phase.phase_id,
                            "name": phase.name,
                            "description": phase.description,
                            "expected_duration_minutes": phase.expected_duration_minutes,
                            "key_vocabulary": phase.key_vocabulary,
                            "essential_phrases": phase.essential_phrases,
                            "learning_objectives": phase.learning_objectives,
                            "cultural_notes": phase.cultural_notes,
                            "success_criteria": phase.success_criteria or [],
                        }
                        for phase in scenario.phases
                    ],
                    "prerequisites": getattr(scenario, "prerequisites", []),
                    "learning_outcomes": getattr(scenario, "learning_outcomes", []),
                    "vocabulary_focus": getattr(scenario, "vocabulary_focus", []),
                    "cultural_context": getattr(scenario, "cultural_context", None),
                    "is_active": getattr(scenario, "is_active", True),
                    "created_at": getattr(
                        scenario, "created_at", datetime.now()
                    ).isoformat()
                    if hasattr(scenario, "created_at") and scenario.created_at
                    else datetime.now().isoformat(),
                    "updated_at": getattr(
                        scenario, "updated_at", datetime.now()
                    ).isoformat()
                    if hasattr(scenario, "updated_at") and scenario.updated_at
                    else datetime.now().isoformat(),
                }
                scenarios_data[scenario_id] = scenario_dict

            # Write to file
            with open(scenarios_file, "w", encoding="utf-8") as f:
                json.dump(scenarios_data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved {len(scenarios_data)} scenarios to {scenarios_file}")

        except Exception as e:
            logger.error(f"Error saving scenarios to file: {str(e)}")

    async def _load_scenarios_from_file(self):
        """Load scenarios from JSON file"""
        try:
            scenarios_file = Path("data/scenarios/scenarios.json")
            if not scenarios_file.exists():
                logger.info(
                    "No saved scenarios file found, starting with predefined scenarios only"
                )
                return

            with open(scenarios_file, "r", encoding="utf-8") as f:
                scenarios_data = json.load(f)

            # Convert back to ConversationScenario objects
            for scenario_id, scenario_dict in scenarios_data.items():
                # Convert phases
                phases = []
                for phase_data in scenario_dict.get("phases", []):
                    phase = ScenarioPhase(
                        phase_id=phase_data["phase_id"],
                        name=phase_data["name"],
                        description=phase_data["description"],
                        expected_duration_minutes=phase_data[
                            "expected_duration_minutes"
                        ],
                        key_vocabulary=phase_data.get("key_vocabulary", []),
                        essential_phrases=phase_data.get("essential_phrases", []),
                        learning_objectives=phase_data.get("learning_objectives", []),
                        cultural_notes=phase_data.get("cultural_notes"),
                        success_criteria=phase_data.get("success_criteria", []),
                    )
                    phases.append(phase)

                # Create scenario object
                scenario = ConversationScenario(
                    scenario_id=scenario_dict["scenario_id"],
                    name=scenario_dict["name"],
                    category=ScenarioCategory(scenario_dict["category"]),
                    difficulty=ScenarioDifficulty(scenario_dict["difficulty"]),
                    description=scenario_dict["description"],
                    user_role=ConversationRole(scenario_dict["user_role"]),
                    ai_role=ConversationRole(scenario_dict["ai_role"]),
                    setting=scenario_dict["setting"],
                    duration_minutes=scenario_dict["duration_minutes"],
                    phases=phases,
                    prerequisites=scenario_dict.get("prerequisites", []),
                    learning_outcomes=scenario_dict.get("learning_outcomes", []),
                    vocabulary_focus=scenario_dict.get("vocabulary_focus", []),
                    cultural_context=scenario_dict.get("cultural_context"),
                )

                # Add additional attributes
                scenario.is_active = scenario_dict.get("is_active", True)
                scenario.created_at = datetime.fromisoformat(
                    scenario_dict.get("created_at", datetime.now().isoformat())
                )
                scenario.updated_at = datetime.fromisoformat(
                    scenario_dict.get("updated_at", datetime.now().isoformat())
                )

                # Store the scenario
                self.scenarios[scenario_id] = scenario

            logger.info(f"Loaded {len(scenarios_data)} scenarios from file")

        except Exception as e:
            logger.error(f"Error loading scenarios from file: {str(e)}")


# Global scenario manager instance
scenario_manager = ScenarioManager()


# Convenience functions
async def get_available_scenarios(
    category: Optional[str] = None, difficulty: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get available scenarios with optional filtering"""
    category_enum = ScenarioCategory(category) if category else None
    difficulty_enum = ScenarioDifficulty(difficulty) if difficulty else None

    return scenario_manager.get_available_scenarios(
        category=category_enum, difficulty=difficulty_enum
    )


async def start_scenario(
    user_id: str, scenario_id: str, language: str = "en"
) -> Dict[str, Any]:
    """Start a new scenario conversation"""
    return await scenario_manager.start_scenario_conversation(
        user_id=user_id, scenario_id=scenario_id, language=language
    )


async def process_scenario_interaction(
    progress_id: str, user_message: str, ai_response: str
) -> Dict[str, Any]:
    """Process interaction within a scenario"""
    return await scenario_manager.process_scenario_message(
        progress_id=progress_id, user_message=user_message, ai_response=ai_response
    )


async def get_scenario_status(progress_id: str) -> Optional[Dict[str, Any]]:
    """Get current scenario progress"""
    return await scenario_manager.get_scenario_progress(progress_id)


async def finish_scenario(progress_id: str) -> Dict[str, Any]:
    """Complete a scenario and get summary"""
    return await scenario_manager.complete_scenario(progress_id)
