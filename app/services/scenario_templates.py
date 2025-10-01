"""
Template creation methods for scenario-based conversations.

This module contains all the template factory methods that create
UniversalScenarioTemplate instances for different scenario categories.
"""

from typing import List
from .scenario_models import (
    ScenarioCategory,
    UniversalScenarioTemplate,
)


class ScenarioTemplates:
    """Factory methods for creating scenario templates"""

    @staticmethod
    def create_greetings_template() -> UniversalScenarioTemplate:
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

    @staticmethod
    def create_daily_routine_template() -> UniversalScenarioTemplate:
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

    @staticmethod
    def create_basic_conversations_template() -> UniversalScenarioTemplate:
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

    @staticmethod
    def create_family_template() -> UniversalScenarioTemplate:
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

    @staticmethod
    def create_restaurant_template() -> UniversalScenarioTemplate:
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

    @staticmethod
    def create_transportation_template() -> UniversalScenarioTemplate:
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

    @staticmethod
    def create_home_neighborhood_template() -> UniversalScenarioTemplate:
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

    @staticmethod
    def get_tier1_templates() -> List[UniversalScenarioTemplate]:
        """Get all Tier 1 templates"""
        return [
            ScenarioTemplates.create_greetings_template(),
            ScenarioTemplates.create_family_template(),
            ScenarioTemplates.create_restaurant_template(),
            ScenarioTemplates.create_transportation_template(),
            ScenarioTemplates.create_home_neighborhood_template(),
        ]

    @staticmethod
    def get_tier2_templates() -> List[UniversalScenarioTemplate]:
        """Get all Tier 2 templates"""
        return [
            ScenarioTemplates.create_daily_routine_template(),
            ScenarioTemplates.create_basic_conversations_template(),
        ]
