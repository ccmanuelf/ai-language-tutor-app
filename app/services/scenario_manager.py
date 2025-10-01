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
from dataclasses import asdict
from uuid import uuid4
import random

from .scenario_models import (
    ScenarioCategory,
    ScenarioDifficulty,
    ConversationRole,
    ScenarioPhase,
    ConversationScenario,
    ScenarioProgress,
)
from .scenario_factory import ScenarioFactory
from .scenario_io import ScenarioIO

logger = logging.getLogger(__name__)


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
            loaded_scenarios = await ScenarioIO.load_scenarios_from_file()
            self.scenarios.update(loaded_scenarios)
            self._initialized = True

    def get_scenario_templates(self) -> Dict[str, Any]:
        """Get scenario templates for different categories"""
        return self.scenario_templates

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
            "social": {
                "phases": [
                    "greeting",
                    "small_talk",
                    "main_conversation",
                    "planning",
                    "farewell",
                ],
                "vocabulary": [
                    "friend",
                    "party",
                    "weekend",
                    "hobby",
                    "movie",
                    "invitation",
                ],
                "cultural_aspects": [
                    "social_customs",
                    "friendship_norms",
                    "casual_communication",
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
            # Validate scenario before saving
            if not self._validate_scenario(scenario):
                logger.warning(f"Scenario validation failed: {scenario.scenario_id}")
                return False

            # Store in memory (in production, this would save to database)
            self.scenarios[scenario.scenario_id] = scenario

            # Save to JSON file for persistence across restarts
            await ScenarioIO.save_scenarios_to_file(self.scenarios)

            logger.info(f"Saved scenario: {scenario.name} ({scenario.scenario_id})")
            return True

        except Exception as e:
            logger.error(f"Error saving scenario {scenario.scenario_id}: {str(e)}")
            return False

    def _validate_scenario(self, scenario: ConversationScenario) -> bool:
        """Validate scenario data before saving"""
        if not scenario.scenario_id or not scenario.scenario_id.strip():
            return False
        if not scenario.name or not scenario.name.strip():
            return False
        if scenario.duration_minutes <= 0:
            return False
        if not scenario.phases or len(scenario.phases) == 0:
            return False
        return True

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
                await ScenarioIO.save_scenarios_to_file(self.scenarios)

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
                await ScenarioIO.save_scenarios_to_file(self.scenarios)

                status = "activated" if is_active else "deactivated"
                logger.info(f"Scenario {scenario.name} ({scenario_id}) {status}")
                return True
            else:
                logger.warning(f"Scenario {scenario_id} not found")
                return False

        except Exception as e:
            logger.error(f"Error updating scenario {scenario_id} status: {str(e)}")
            return False

    # I/O methods moved to scenario_io.py module


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
