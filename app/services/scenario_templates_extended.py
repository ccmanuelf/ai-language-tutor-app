"""
Extended Scenario Templates for AI Language Tutor App (32 Comprehensive Scenarios)

This module contains the expanded scenario templates covering all essential language
learning situations as requested. Organized in 4 tiers for systematic learning progression.

Tier 1: Essential Daily Interactions (1-5) - Already implemented in scenario_manager.py
Tier 2: Daily Routines and Activities (6-15)
Tier 3: Extended Core Activities (16-25)
Tier 4: Advanced Topics (26-32)
"""

from typing import List, Dict, Any
from app.services.scenario_manager import (
    UniversalScenarioTemplate,
    ScenarioCategory,
    ScenarioDifficulty,
    ConversationRole,
)


class ExtendedScenarioTemplates:
    """Factory class for creating extended scenario templates"""

    @staticmethod
    def get_tier2_templates() -> List[UniversalScenarioTemplate]:
        """Get Tier 2: Daily Routines and Activities (6-15)"""
        return [
            ExtendedScenarioTemplates._create_daily_routine_template(),
            ExtendedScenarioTemplates._create_basic_conversations_template(),
            ExtendedScenarioTemplates._create_job_work_template(),
            ExtendedScenarioTemplates._create_weather_climate_template(),
            ExtendedScenarioTemplates._create_clothing_template(),
            ExtendedScenarioTemplates._create_shopping_template(),
            ExtendedScenarioTemplates._create_plans_template(),
            ExtendedScenarioTemplates._create_common_topics_template(),
            ExtendedScenarioTemplates._create_numbers_template(),
            ExtendedScenarioTemplates._create_celebrations_template(),
        ]

    @staticmethod
    def get_tier3_templates() -> List[UniversalScenarioTemplate]:
        """Get Tier 3: Extended Core Activities (16-25)"""
        return [
            ExtendedScenarioTemplates._create_sports_activities_template(),
            ExtendedScenarioTemplates._create_grocery_shopping_template(),
            ExtendedScenarioTemplates._create_education_template(),
            ExtendedScenarioTemplates._create_office_work_life_template(),
            ExtendedScenarioTemplates._create_permissions_etiquette_template(),
            ExtendedScenarioTemplates._create_physical_health_template(),
            ExtendedScenarioTemplates._create_trip_places_template(),
            ExtendedScenarioTemplates._create_public_places_template(),
            ExtendedScenarioTemplates._create_describing_someone_template(),
            ExtendedScenarioTemplates._create_feelings_emotions_template(),
        ]

    @staticmethod
    def get_tier4_templates() -> List[UniversalScenarioTemplate]:
        """Get Tier 4: Advanced Topics (26-32)"""
        return [
            ExtendedScenarioTemplates._create_difficulties_solutions_template(),
            ExtendedScenarioTemplates._create_health_wellbeing_template(),
            ExtendedScenarioTemplates._create_making_plans_template(),
            ExtendedScenarioTemplates._create_getting_house_template(),
            ExtendedScenarioTemplates._create_music_performing_arts_template(),
            ExtendedScenarioTemplates._create_past_activities_template(),
            ExtendedScenarioTemplates._create_money_finances_template(),
        ]

    @staticmethod
    def get_all_extended_templates() -> List[UniversalScenarioTemplate]:
        """Get all extended templates (Tiers 2-4)"""
        return (
            ExtendedScenarioTemplates.get_tier2_templates()
            + ExtendedScenarioTemplates.get_tier3_templates()
            + ExtendedScenarioTemplates.get_tier4_templates()
        )

    # TIER 2: Daily Routines and Activities (6-15)

    @staticmethod
    def _create_daily_routine_template() -> UniversalScenarioTemplate:
        """Create daily routine template (6)"""
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
    def _create_basic_conversations_template() -> UniversalScenarioTemplate:
        """Create basic conversations template (7)"""
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
    def _create_job_work_template() -> UniversalScenarioTemplate:
        """Create job and work template (8)"""
        return UniversalScenarioTemplate(
            template_id="job_work",
            name="Job and Work",
            category=ScenarioCategory.BUSINESS,
            tier=2,
            base_vocabulary=[
                "job",
                "work",
                "career",
                "office",
                "company",
                "employee",
                "boss",
                "colleague",
                "meeting",
                "project",
                "deadline",
                "salary",
                "interview",
                "resume",
                "experience",
                "skills",
                "responsible",
                "manager",
                "team",
            ],
            essential_phrases={
                "beginner": [
                    "I work as a...",
                    "What's your job?",
                    "I like my work",
                    "I'm looking for a job",
                ],
                "intermediate": [
                    "I'm responsible for...",
                    "We have a meeting tomorrow",
                    "I work in the... department",
                ],
                "advanced": [
                    "I'm considering a career change",
                    "The project deadline is approaching",
                    "I've been promoted to...",
                ],
            },
            cultural_context={
                "notes": "Work cultures vary significantly - hierarchy, communication styles, work-life balance"
            },
            learning_objectives=[
                "Describe jobs and responsibilities",
                "Discuss work activities",
                "Handle professional conversations",
            ],
            conversation_starters=[
                "What do you do for work?",
                "How do you like your job?",
                "What's your company like?",
            ],
            scenario_variations=[
                {
                    "id": "job_interview",
                    "description": "Job interview scenario",
                    "phases": [
                        "introduction",
                        "experience_discussion",
                        "questions_answers",
                        "next_steps",
                    ],
                },
                {
                    "id": "workplace_chat",
                    "description": "Casual workplace conversation",
                    "phases": [
                        "greeting",
                        "work_updates",
                        "project_discussion",
                        "social_chat",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 12},
                "intermediate": {"duration": 18},
                "advanced": {"duration": 25},
            },
            success_metrics=[
                "Describe job clearly",
                "Use work-related vocabulary",
                "Handle professional situations",
            ],
        )

    @staticmethod
    def _create_weather_climate_template() -> UniversalScenarioTemplate:
        """Create weather and climate template (9)"""
        return UniversalScenarioTemplate(
            template_id="weather_climate",
            name="Weather and Climate",
            category=ScenarioCategory.DAILY_LIFE,
            tier=2,
            base_vocabulary=[
                "weather",
                "sunny",
                "cloudy",
                "rainy",
                "snowy",
                "windy",
                "hot",
                "cold",
                "warm",
                "cool",
                "temperature",
                "degrees",
                "forecast",
                "umbrella",
                "coat",
                "season",
                "spring",
                "summer",
                "autumn",
                "winter",
                "climate",
            ],
            essential_phrases={
                "beginner": [
                    "It's sunny today",
                    "It's raining",
                    "It's very hot",
                    "What's the weather like?",
                ],
                "intermediate": [
                    "The forecast says it will rain",
                    "I need to bring an umbrella",
                    "The temperature is 20 degrees",
                ],
                "advanced": [
                    "The climate here is quite different from my home country",
                    "We're experiencing unusual weather patterns",
                ],
            },
            cultural_context={
                "notes": "Weather talk is common small talk in many cultures, but importance varies"
            },
            learning_objectives=[
                "Describe current weather",
                "Discuss weather preferences",
                "Make weather-related plans",
            ],
            conversation_starters=[
                "Nice weather today, isn't it?",
                "What's the weather forecast?",
                "How's the weather been?",
            ],
            scenario_variations=[
                {
                    "id": "daily_weather",
                    "description": "Daily weather discussion",
                    "phases": [
                        "current_weather",
                        "forecast_check",
                        "clothing_decisions",
                        "activity_planning",
                    ],
                },
                {
                    "id": "seasonal_talk",
                    "description": "Seasonal weather conversation",
                    "phases": [
                        "season_comparison",
                        "preferences",
                        "activities",
                        "climate_discussion",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 8},
                "intermediate": {"duration": 12},
                "advanced": {"duration": 16},
            },
            success_metrics=[
                "Use weather vocabulary correctly",
                "Make weather-related small talk",
                "Plan activities based on weather",
            ],
        )

    @staticmethod
    def _create_clothing_template() -> UniversalScenarioTemplate:
        """Create clothing template (10)"""
        return UniversalScenarioTemplate(
            template_id="clothing",
            name="Clothing",
            category=ScenarioCategory.SHOPPING,
            tier=2,
            base_vocabulary=[
                "clothes",
                "shirt",
                "pants",
                "dress",
                "shoes",
                "hat",
                "jacket",
                "color",
                "size",
                "small",
                "medium",
                "large",
                "fit",
                "style",
                "comfortable",
                "fashionable",
                "expensive",
                "cheap",
                "try on",
                "wear",
            ],
            essential_phrases={
                "beginner": [
                    "I like this shirt",
                    "What size is this?",
                    "Can I try it on?",
                    "It's too big",
                ],
                "intermediate": [
                    "This color suits you",
                    "Do you have this in a different size?",
                    "It fits perfectly",
                ],
                "advanced": [
                    "I'm looking for something more formal",
                    "The style is very trendy",
                    "This fabric is high quality",
                ],
            },
            cultural_context={
                "notes": "Clothing styles, colors, and appropriateness vary significantly by culture"
            },
            learning_objectives=[
                "Describe clothing and appearance",
                "Shop for clothes",
                "Express preferences about style",
            ],
            conversation_starters=[
                "I like your shirt",
                "Where did you get that?",
                "What do you think of this?",
            ],
            scenario_variations=[
                {
                    "id": "clothes_shopping",
                    "description": "Shopping for clothes",
                    "phases": [
                        "browsing",
                        "asking_assistance",
                        "trying_on",
                        "purchasing",
                    ],
                },
                {
                    "id": "style_discussion",
                    "description": "Discussing fashion and style",
                    "phases": [
                        "outfit_compliments",
                        "style_preferences",
                        "shopping_recommendations",
                        "fashion_trends",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 10},
                "intermediate": {"duration": 15},
                "advanced": {"duration": 20},
            },
            success_metrics=[
                "Use clothing vocabulary",
                "Shop effectively",
                "Discuss style preferences",
            ],
        )

    @staticmethod
    def _create_shopping_template() -> UniversalScenarioTemplate:
        """Create general shopping template (11)"""
        return UniversalScenarioTemplate(
            template_id="general_shopping",
            name="General Shopping",
            category=ScenarioCategory.SHOPPING,
            tier=2,
            base_vocabulary=[
                "shop",
                "store",
                "buy",
                "sell",
                "price",
                "cost",
                "money",
                "cash",
                "card",
                "receipt",
                "discount",
                "sale",
                "expensive",
                "cheap",
                "quality",
                "brand",
                "customer",
                "service",
                "return",
                "exchange",
            ],
            essential_phrases={
                "beginner": [
                    "How much is this?",
                    "Can I pay by card?",
                    "Where is the...?",
                    "I want to buy...",
                ],
                "intermediate": [
                    "Is there a discount?",
                    "Can I get a receipt?",
                    "I'd like to return this",
                ],
                "advanced": [
                    "I'm comparing different brands",
                    "What's your return policy?",
                    "Do you have this item in stock?",
                ],
            },
            cultural_context={
                "notes": "Shopping customs, bargaining, and payment methods vary by culture"
            },
            learning_objectives=[
                "Navigate shopping situations",
                "Handle transactions",
                "Compare and evaluate products",
            ],
            conversation_starters=[
                "Excuse me, where can I find...?",
                "How much does this cost?",
                "Can you help me?",
            ],
            scenario_variations=[
                {
                    "id": "department_store",
                    "description": "Shopping in a department store",
                    "phases": [
                        "store_navigation",
                        "product_inquiry",
                        "comparison_shopping",
                        "checkout",
                    ],
                },
                {
                    "id": "market_shopping",
                    "description": "Shopping at a local market",
                    "phases": [
                        "browsing_stalls",
                        "price_negotiation",
                        "product_selection",
                        "payment",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 12},
                "intermediate": {"duration": 18},
                "advanced": {"duration": 24},
            },
            success_metrics=[
                "Complete shopping transactions",
                "Ask for help effectively",
                "Handle payment and receipts",
            ],
        )

    @staticmethod
    def _create_plans_template() -> UniversalScenarioTemplate:
        """Create making plans template (12)"""
        return UniversalScenarioTemplate(
            template_id="making_plans",
            name="Making Plans",
            category=ScenarioCategory.SOCIAL,
            tier=2,
            base_vocabulary=[
                "plan",
                "meet",
                "appointment",
                "schedule",
                "available",
                "busy",
                "free",
                "time",
                "date",
                "place",
                "activity",
                "movie",
                "dinner",
                "party",
                "event",
                "invitation",
                "confirm",
                "cancel",
                "reschedule",
            ],
            essential_phrases={
                "beginner": [
                    "Are you free tomorrow?",
                    "Let's meet at...",
                    "What time?",
                    "I can't come",
                ],
                "intermediate": [
                    "When are you available?",
                    "Should we reschedule?",
                    "I'll confirm later",
                ],
                "advanced": [
                    "I'm afraid I have a prior engagement",
                    "Would it be possible to meet earlier?",
                    "Let me check my calendar",
                ],
            },
            cultural_context={
                "notes": "Planning styles vary - some cultures prefer advance planning, others are more spontaneous"
            },
            learning_objectives=[
                "Make social plans",
                "Suggest activities",
                "Handle scheduling conflicts",
            ],
            conversation_starters=[
                "What are you doing this weekend?",
                "Would you like to...?",
                "Are you available for...?",
            ],
            scenario_variations=[
                {
                    "id": "weekend_plans",
                    "description": "Planning weekend activities",
                    "phases": [
                        "availability_check",
                        "activity_suggestions",
                        "time_place_agreement",
                        "confirmation",
                    ],
                },
                {
                    "id": "business_meeting",
                    "description": "Scheduling business meetings",
                    "phases": [
                        "purpose_discussion",
                        "calendar_coordination",
                        "meeting_details",
                        "follow_up",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 10},
                "intermediate": {"duration": 15},
                "advanced": {"duration": 20},
            },
            success_metrics=[
                "Successfully arrange meetings",
                "Handle schedule changes",
                "Use time expressions correctly",
            ],
        )

    @staticmethod
    def _create_common_topics_template() -> UniversalScenarioTemplate:
        """Create common topics template (13)"""
        return UniversalScenarioTemplate(
            template_id="common_topics",
            name="Common Topics",
            category=ScenarioCategory.SOCIAL,
            tier=2,
            base_vocabulary=[
                "hobby",
                "interest",
                "movie",
                "book",
                "music",
                "sport",
                "travel",
                "food",
                "culture",
                "news",
                "opinion",
                "like",
                "dislike",
                "prefer",
                "enjoy",
                "hate",
                "love",
                "favorite",
                "recommend",
                "experience",
            ],
            essential_phrases={
                "beginner": [
                    "I like...",
                    "I don't like...",
                    "What's your favorite...?",
                    "Do you like...?",
                ],
                "intermediate": [
                    "I'm interested in...",
                    "Have you ever...?",
                    "I'd recommend...",
                    "What do you think of...?",
                ],
                "advanced": [
                    "I'm particularly fond of...",
                    "That's not really my cup of tea",
                    "I have mixed feelings about...",
                ],
            },
            cultural_context={
                "notes": "Safe conversation topics vary by culture - politics, religion may be sensitive"
            },
            learning_objectives=[
                "Discuss personal interests",
                "Share opinions",
                "Find common ground",
            ],
            conversation_starters=[
                "What do you like to do for fun?",
                "Have you seen any good movies lately?",
                "What kind of music do you like?",
            ],
            scenario_variations=[
                {
                    "id": "interests_hobbies",
                    "description": "Discussing hobbies and interests",
                    "phases": [
                        "hobby_sharing",
                        "interest_discovery",
                        "experience_exchange",
                        "recommendation_giving",
                    ],
                },
                {
                    "id": "entertainment_chat",
                    "description": "Talking about entertainment",
                    "phases": [
                        "current_entertainment",
                        "preferences",
                        "reviews_opinions",
                        "future_plans",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 12},
                "intermediate": {"duration": 18},
                "advanced": {"duration": 25},
            },
            success_metrics=[
                "Express preferences clearly",
                "Ask follow-up questions",
                "Maintain engaging conversation",
            ],
        )

    @staticmethod
    def _create_numbers_template() -> UniversalScenarioTemplate:
        """Create numbers template (14)"""
        return UniversalScenarioTemplate(
            template_id="numbers",
            name="Numbers",
            category=ScenarioCategory.DAILY_LIFE,
            tier=2,
            base_vocabulary=[
                "number",
                "count",
                "phone",
                "address",
                "age",
                "price",
                "time",
                "date",
                "quantity",
                "amount",
                "percent",
                "half",
                "quarter",
                "dozen",
                "hundred",
                "thousand",
                "million",
                "first",
                "second",
                "third",
            ],
            essential_phrases={
                "beginner": [
                    "My phone number is...",
                    "I'm ... years old",
                    "It costs...",
                    "What's your address?",
                ],
                "intermediate": [
                    "Can you give me your contact information?",
                    "The meeting is on the 15th",
                    "It's about 50 percent",
                ],
                "advanced": [
                    "The statistics show approximately...",
                    "There's been a threefold increase",
                    "The probability is roughly...",
                ],
            },
            cultural_context={
                "notes": "Number systems, date formats, and measurement units vary by country"
            },
            learning_objectives=[
                "Use numbers in context",
                "Give contact information",
                "Understand quantities and measurements",
            ],
            conversation_starters=[
                "What's your phone number?",
                "How old are you?",
                "What time is it?",
            ],
            scenario_variations=[
                {
                    "id": "contact_exchange",
                    "description": "Exchanging contact information",
                    "phases": [
                        "phone_numbers",
                        "addresses",
                        "email_sharing",
                        "social_media",
                    ],
                },
                {
                    "id": "shopping_quantities",
                    "description": "Using numbers while shopping",
                    "phases": [
                        "price_inquiry",
                        "quantity_selection",
                        "calculation",
                        "payment_amount",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 8},
                "intermediate": {"duration": 12},
                "advanced": {"duration": 16},
            },
            success_metrics=[
                "Use numbers accurately",
                "Give/receive contact info",
                "Handle basic calculations",
            ],
        )

    @staticmethod
    def _create_celebrations_template() -> UniversalScenarioTemplate:
        """Create celebrations template (15)"""
        return UniversalScenarioTemplate(
            template_id="celebrations",
            name="Celebrations",
            category=ScenarioCategory.SOCIAL,
            tier=2,
            base_vocabulary=[
                "birthday",
                "party",
                "celebration",
                "holiday",
                "festival",
                "gift",
                "present",
                "cake",
                "candle",
                "invitation",
                "guest",
                "tradition",
                "custom",
                "ceremony",
                "congratulations",
                "wishes",
                "special",
                "anniversary",
            ],
            essential_phrases={
                "beginner": [
                    "Happy birthday!",
                    "Congratulations!",
                    "I have a gift for you",
                    "When is your birthday?",
                ],
                "intermediate": [
                    "We're having a party",
                    "Would you like to come?",
                    "What do you usually do for...?",
                ],
                "advanced": [
                    "We have a family tradition of...",
                    "It's customary to...",
                    "The celebration was magnificent",
                ],
            },
            cultural_context={
                "notes": "Celebrations, traditions, and gift-giving customs vary dramatically across cultures"
            },
            learning_objectives=[
                "Discuss celebrations and traditions",
                "Give congratulations",
                "Understand cultural customs",
            ],
            conversation_starters=[
                "How do you celebrate...?",
                "What's your favorite holiday?",
                "Do you have any special traditions?",
            ],
            scenario_variations=[
                {
                    "id": "birthday_party",
                    "description": "Birthday party scenario",
                    "phases": [
                        "invitation",
                        "party_preparation",
                        "celebration",
                        "gift_giving",
                    ],
                },
                {
                    "id": "cultural_celebration",
                    "description": "Cultural holiday discussion",
                    "phases": [
                        "tradition_explanation",
                        "personal_experiences",
                        "comparison",
                        "invitation_sharing",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 10},
                "intermediate": {"duration": 15},
                "advanced": {"duration": 20},
            },
            success_metrics=[
                "Use celebration vocabulary",
                "Describe traditions",
                "Give appropriate congratulations",
            ],
        )

    # TIER 3: Extended Core Activities (16-25)

    @staticmethod
    def _create_sports_activities_template() -> UniversalScenarioTemplate:
        """Create sports and physical activities template (16)"""
        return UniversalScenarioTemplate(
            template_id="sports_activities",
            name="Sports and Physical Activities",
            category=ScenarioCategory.HOBBIES,
            tier=3,
            base_vocabulary=[
                "sport",
                "exercise",
                "gym",
                "running",
                "swimming",
                "football",
                "basketball",
                "tennis",
                "yoga",
                "workout",
                "training",
                "fitness",
                "team",
                "player",
                "coach",
                "match",
                "game",
                "score",
                "win",
                "lose",
                "practice",
                "competition",
            ],
            essential_phrases={
                "beginner": [
                    "I play football",
                    "Do you like sports?",
                    "I go to the gym",
                    "Who won the game?",
                ],
                "intermediate": [
                    "I'm training for a marathon",
                    "Our team practices twice a week",
                    "The score was 2-1",
                ],
                "advanced": [
                    "I'm passionate about endurance sports",
                    "The championship was quite competitive",
                    "I follow professional leagues",
                ],
            },
            cultural_context={"notes": "Popular sports vary by country and culture"},
            learning_objectives=[
                "Discuss sports and fitness",
                "Talk about teams and competitions",
                "Express athletic interests",
            ],
            conversation_starters=[
                "Do you play any sports?",
                "Did you watch the game?",
                "How do you stay fit?",
            ],
            scenario_variations=[
                {
                    "id": "gym_conversation",
                    "description": "Talking at the gym",
                    "phases": [
                        "workout_discussion",
                        "fitness_goals",
                        "exercise_tips",
                        "schedule_coordination",
                    ],
                },
                {
                    "id": "sports_event",
                    "description": "Discussing sports events",
                    "phases": [
                        "game_recap",
                        "player_performance",
                        "predictions",
                        "team_loyalty",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 12},
                "intermediate": {"duration": 18},
                "advanced": {"duration": 25},
            },
            success_metrics=[
                "Use sports vocabulary",
                "Describe physical activities",
                "Discuss competitions and results",
            ],
        )

    @staticmethod
    def _create_grocery_shopping_template() -> UniversalScenarioTemplate:
        """Create grocery shopping template (17)"""
        return UniversalScenarioTemplate(
            template_id="grocery_shopping",
            name="Grocery Shopping",
            category=ScenarioCategory.SHOPPING,
            tier=3,
            base_vocabulary=[
                "grocery",
                "supermarket",
                "fruit",
                "vegetable",
                "meat",
                "bread",
                "milk",
                "cheese",
                "fresh",
                "organic",
                "aisle",
                "checkout",
                "cart",
                "basket",
                "price",
                "discount",
                "sale",
                "coupon",
                "expiry date",
                "quantity",
                "list",
            ],
            essential_phrases={
                "beginner": [
                    "Where are the apples?",
                    "How much is this?",
                    "I need some bread",
                    "Do you have milk?",
                ],
                "intermediate": [
                    "Is this fruit fresh?",
                    "Are there any discounts?",
                    "I'm looking for organic vegetables",
                ],
                "advanced": [
                    "I prefer free-range products",
                    "Do you have any seasonal specials?",
                    "What's the expiry date on this?",
                ],
            },
            cultural_context={
                "notes": "Food preferences, shopping habits, and market types vary by culture"
            },
            learning_objectives=[
                "Navigate grocery stores",
                "Ask about food products",
                "Handle food shopping transactions",
            ],
            conversation_starters=[
                "Excuse me, where can I find...?",
                "Is this on sale?",
                "Do you know if this is fresh?",
            ],
            scenario_variations=[
                {
                    "id": "supermarket_shopping",
                    "description": "Shopping at a supermarket",
                    "phases": [
                        "store_navigation",
                        "product_selection",
                        "price_comparison",
                        "checkout_process",
                    ],
                },
                {
                    "id": "farmers_market",
                    "description": "Shopping at farmers market",
                    "phases": [
                        "vendor_interaction",
                        "quality_assessment",
                        "price_negotiation",
                        "local_product_discussion",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 15},
                "intermediate": {"duration": 20},
                "advanced": {"duration": 25},
            },
            success_metrics=[
                "Navigate food shopping",
                "Ask about product details",
                "Complete grocery transactions",
            ],
        )

    @staticmethod
    def _create_education_template() -> UniversalScenarioTemplate:
        """Create education template (18)"""
        return UniversalScenarioTemplate(
            template_id="education",
            name="Education",
            category=ScenarioCategory.EDUCATION,
            tier=3,
            base_vocabulary=[
                "school",
                "university",
                "student",
                "teacher",
                "professor",
                "class",
                "course",
                "subject",
                "homework",
                "assignment",
                "exam",
                "grade",
                "degree",
                "major",
                "study",
                "learn",
                "education",
                "knowledge",
                "skill",
            ],
            essential_phrases={
                "beginner": [
                    "I'm a student",
                    "What do you study?",
                    "I have homework",
                    "When is the exam?",
                ],
                "intermediate": [
                    "I'm majoring in...",
                    "The professor is very knowledgeable",
                    "I need to study more",
                ],
                "advanced": [
                    "I'm pursuing a graduate degree",
                    "The curriculum is quite comprehensive",
                    "I'm researching...",
                ],
            },
            cultural_context={
                "notes": "Education systems, teaching styles, and academic expectations vary significantly"
            },
            learning_objectives=[
                "Discuss education and learning",
                "Talk about academic subjects",
                "Navigate educational environments",
            ],
            conversation_starters=[
                "What did you study?",
                "How do you like school?",
                "What's your favorite subject?",
            ],
            scenario_variations=[
                {
                    "id": "classroom_interaction",
                    "description": "Classroom conversations",
                    "phases": [
                        "subject_discussion",
                        "assignment_clarification",
                        "study_group_formation",
                        "academic_support",
                    ],
                },
                {
                    "id": "academic_planning",
                    "description": "Academic planning discussion",
                    "phases": [
                        "course_selection",
                        "career_goals",
                        "study_strategies",
                        "academic_resources",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 12},
                "intermediate": {"duration": 18},
                "advanced": {"duration": 25},
            },
            success_metrics=[
                "Discuss educational topics",
                "Use academic vocabulary",
                "Navigate school conversations",
            ],
        )

    @staticmethod
    def _create_office_work_life_template() -> UniversalScenarioTemplate:
        """Create office and work life template (19)"""
        return UniversalScenarioTemplate(
            template_id="office_work_life",
            name="Office and Work Life",
            category=ScenarioCategory.BUSINESS,
            tier=3,
            base_vocabulary=[
                "office",
                "desk",
                "computer",
                "meeting",
                "presentation",
                "project",
                "deadline",
                "colleague",
                "boss",
                "manager",
                "department",
                "hierarchy",
                "supplies",
                "printer",
                "email",
                "schedule",
                "report",
                "conference",
                "teamwork",
            ],
            essential_phrases={
                "beginner": [
                    "I work in an office",
                    "Where is the printer?",
                    "We have a meeting",
                    "I need supplies",
                ],
                "intermediate": [
                    "I'm working on a project",
                    "The deadline is next week",
                    "Could you send me that report?",
                ],
                "advanced": [
                    "We need to coordinate our efforts",
                    "I'll schedule a conference call",
                    "Let's discuss the hierarchy",
                ],
            },
            cultural_context={
                "notes": "Office cultures, hierarchy respect, and work communication styles vary"
            },
            learning_objectives=[
                "Navigate office environments",
                "Discuss work tasks",
                "Handle professional communications",
            ],
            conversation_starters=[
                "How's your project going?",
                "Do you have time for a quick meeting?",
                "Where can I find...?",
            ],
            scenario_variations=[
                {
                    "id": "office_orientation",
                    "description": "Office orientation for new employee",
                    "phases": [
                        "facility_tour",
                        "colleague_introductions",
                        "systems_training",
                        "culture_explanation",
                    ],
                },
                {
                    "id": "project_collaboration",
                    "description": "Working on team projects",
                    "phases": [
                        "task_assignment",
                        "progress_updates",
                        "problem_solving",
                        "deadline_management",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 15},
                "intermediate": {"duration": 20},
                "advanced": {"duration": 30},
            },
            success_metrics=[
                "Navigate office settings",
                "Use professional vocabulary",
                "Collaborate effectively",
            ],
        )

    @staticmethod
    def _create_permissions_etiquette_template() -> UniversalScenarioTemplate:
        """Create permissions and etiquette template (20)"""
        return UniversalScenarioTemplate(
            template_id="permissions_etiquette",
            name="Permissions and Etiquette",
            category=ScenarioCategory.SOCIAL,
            tier=3,
            base_vocabulary=[
                "permission",
                "please",
                "may I",
                "could I",
                "excuse me",
                "sorry",
                "polite",
                "rude",
                "appropriate",
                "respectful",
                "formal",
                "informal",
                "etiquette",
                "manners",
                "custom",
                "tradition",
                "behavior",
                "social",
            ],
            essential_phrases={
                "beginner": ["May I come in?", "Excuse me", "I'm sorry", "Please"],
                "intermediate": [
                    "Could I ask you a favor?",
                    "Would it be okay if...?",
                    "I hope you don't mind",
                ],
                "advanced": [
                    "I'd be most grateful if...",
                    "Would it be presumptuous to ask...?",
                    "I hope I'm not overstepping",
                ],
            },
            cultural_context={
                "notes": "Politeness levels, formality, and social etiquette vary dramatically between cultures"
            },
            learning_objectives=[
                "Use polite language",
                "Ask for permission appropriately",
                "Understand social etiquette",
            ],
            conversation_starters=[
                "Excuse me, may I...?",
                "I hope I'm not bothering you",
                "Could I please...?",
            ],
            scenario_variations=[
                {
                    "id": "formal_requests",
                    "description": "Making formal requests",
                    "phases": [
                        "polite_approach",
                        "request_explanation",
                        "permission_granting",
                        "grateful_acknowledgment",
                    ],
                },
                {
                    "id": "social_etiquette",
                    "description": "Learning social etiquette",
                    "phases": [
                        "situation_assessment",
                        "appropriate_behavior",
                        "cultural_guidance",
                        "practice_application",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 10},
                "intermediate": {"duration": 15},
                "advanced": {"duration": 20},
            },
            success_metrics=[
                "Use polite expressions",
                "Ask permission appropriately",
                "Show cultural awareness",
            ],
        )

    @staticmethod
    def _create_physical_health_template() -> UniversalScenarioTemplate:
        """Create physical health template (21)"""
        return UniversalScenarioTemplate(
            template_id="physical_health",
            name="Physical Health",
            category=ScenarioCategory.HEALTHCARE,
            tier=3,
            base_vocabulary=[
                "health",
                "sick",
                "pain",
                "headache",
                "fever",
                "cold",
                "flu",
                "doctor",
                "medicine",
                "pharmacy",
                "prescription",
                "appointment",
                "symptoms",
                "treatment",
                "recovery",
                "wellness",
                "checkup",
                "advice",
            ],
            essential_phrases={
                "beginner": [
                    "I feel sick",
                    "I have a headache",
                    "I need medicine",
                    "Where is the doctor?",
                ],
                "intermediate": [
                    "I'd like to make an appointment",
                    "What are your symptoms?",
                    "The doctor prescribed...",
                ],
                "advanced": [
                    "I've been experiencing some discomfort",
                    "Could you recommend a specialist?",
                    "What's the prognosis?",
                ],
            },
            cultural_context={
                "notes": "Healthcare systems, traditional medicine, and health discussions vary by culture"
            },
            learning_objectives=[
                "Describe health problems",
                "Seek medical help",
                "Understand health advice",
            ],
            conversation_starters=[
                "How are you feeling?",
                "Are you okay?",
                "Do you need to see a doctor?",
            ],
            scenario_variations=[
                {
                    "id": "doctor_visit",
                    "description": "Visiting the doctor",
                    "phases": [
                        "symptom_description",
                        "examination",
                        "diagnosis_discussion",
                        "treatment_plan",
                    ],
                },
                {
                    "id": "pharmacy_visit",
                    "description": "Getting medicine at pharmacy",
                    "phases": [
                        "prescription_presentation",
                        "medication_explanation",
                        "dosage_instructions",
                        "payment",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 12},
                "intermediate": {"duration": 18},
                "advanced": {"duration": 25},
            },
            success_metrics=[
                "Describe health issues",
                "Understand medical advice",
                "Navigate healthcare settings",
            ],
        )

    @staticmethod
    def _create_trip_places_template() -> UniversalScenarioTemplate:
        """Create trip to places template (22)"""
        return UniversalScenarioTemplate(
            template_id="trip_places",
            name="Trip to Places",
            category=ScenarioCategory.TRAVEL,
            tier=3,
            base_vocabulary=[
                "trip",
                "travel",
                "vacation",
                "destination",
                "hotel",
                "booking",
                "sightseeing",
                "tourist",
                "attraction",
                "map",
                "guide",
                "itinerary",
                "luggage",
                "passport",
                "ticket",
                "flight",
                "journey",
                "adventure",
            ],
            essential_phrases={
                "beginner": [
                    "I'm going on a trip",
                    "Where should I visit?",
                    "How do I get there?",
                    "Is it far?",
                ],
                "intermediate": [
                    "I've booked a hotel",
                    "What are the main attractions?",
                    "How long does it take to get there?",
                ],
                "advanced": [
                    "I'm planning an itinerary",
                    "Could you recommend some off-the-beaten-path destinations?",
                    "What's the best time to visit?",
                ],
            },
            cultural_context={
                "notes": "Travel customs, tipping, and tourist expectations vary by destination"
            },
            learning_objectives=[
                "Plan trips and travel",
                "Ask for directions and recommendations",
                "Handle travel situations",
            ],
            conversation_starters=[
                "Have you been to...?",
                "What's the best way to get to...?",
                "Any travel recommendations?",
            ],
            scenario_variations=[
                {
                    "id": "trip_planning",
                    "description": "Planning a trip",
                    "phases": [
                        "destination_selection",
                        "accommodation_booking",
                        "activity_planning",
                        "travel_preparation",
                    ],
                },
                {
                    "id": "tourist_information",
                    "description": "Getting tourist information",
                    "phases": [
                        "information_request",
                        "recommendation_seeking",
                        "map_consultation",
                        "booking_assistance",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 15},
                "intermediate": {"duration": 20},
                "advanced": {"duration": 30},
            },
            success_metrics=[
                "Plan travel effectively",
                "Get tourist information",
                "Handle travel conversations",
            ],
        )

    @staticmethod
    def _create_public_places_template() -> UniversalScenarioTemplate:
        """Create public places template (23)"""
        return UniversalScenarioTemplate(
            template_id="public_places",
            name="Public Places",
            category=ScenarioCategory.DAILY_LIFE,
            tier=3,
            base_vocabulary=[
                "park",
                "library",
                "museum",
                "theater",
                "cinema",
                "mall",
                "store",
                "bank",
                "post office",
                "hospital",
                "police",
                "station",
                "airport",
                "public",
                "entrance",
                "exit",
                "information",
                "ticket",
                "hours",
            ],
            essential_phrases={
                "beginner": [
                    "Where is the library?",
                    "Is the museum open?",
                    "How much is a ticket?",
                    "What time do you close?",
                ],
                "intermediate": [
                    "Could you give me directions to...?",
                    "Are there any guided tours?",
                    "What are your opening hours?",
                ],
                "advanced": [
                    "I'm looking for information about...",
                    "Are there any special exhibitions?",
                    "What facilities are available?",
                ],
            },
            cultural_context={
                "notes": "Public spaces, opening hours, and access rules vary by location"
            },
            learning_objectives=[
                "Navigate public spaces",
                "Get information about facilities",
                "Use public services",
            ],
            conversation_starters=[
                "Excuse me, where is...?",
                "Is this place open?",
                "How can I get to...?",
            ],
            scenario_variations=[
                {
                    "id": "public_facility",
                    "description": "Using public facilities",
                    "phases": [
                        "location_finding",
                        "information_gathering",
                        "service_access",
                        "facility_use",
                    ],
                },
                {
                    "id": "entertainment_venue",
                    "description": "Visiting entertainment venues",
                    "phases": [
                        "venue_selection",
                        "ticket_purchase",
                        "event_information",
                        "experience_sharing",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 12},
                "intermediate": {"duration": 18},
                "advanced": {"duration": 24},
            },
            success_metrics=[
                "Find and use public places",
                "Get facility information",
                "Access public services",
            ],
        )

    @staticmethod
    def _create_describing_someone_template() -> UniversalScenarioTemplate:
        """Create describing someone template (24)"""
        return UniversalScenarioTemplate(
            template_id="describing_someone",
            name="Describing Someone",
            category=ScenarioCategory.SOCIAL,
            tier=3,
            base_vocabulary=[
                "tall",
                "short",
                "thin",
                "heavy",
                "young",
                "old",
                "hair",
                "eyes",
                "appearance",
                "personality",
                "friendly",
                "kind",
                "funny",
                "serious",
                "smart",
                "creative",
                "outgoing",
                "shy",
                "confident",
                "patient",
            ],
            essential_phrases={
                "beginner": [
                    "He is tall",
                    "She has brown hair",
                    "They are very nice",
                    "What does he look like?",
                ],
                "intermediate": [
                    "She's quite outgoing",
                    "He has a great sense of humor",
                    "She's very patient with children",
                ],
                "advanced": [
                    "He's remarkably articulate",
                    "She has an infectious personality",
                    "He's incredibly perceptive",
                ],
            },
            cultural_context={
                "notes": "Appropriateness of physical descriptions and compliments varies by culture"
            },
            learning_objectives=[
                "Describe physical appearance",
                "Talk about personality traits",
                "Give appropriate compliments",
            ],
            conversation_starters=[
                "What's your friend like?",
                "Can you describe him?",
                "What does she look like?",
            ],
            scenario_variations=[
                {
                    "id": "person_description",
                    "description": "Describing people",
                    "phases": [
                        "physical_description",
                        "personality_traits",
                        "behavioral_patterns",
                        "overall_impression",
                    ],
                },
                {
                    "id": "meeting_someone",
                    "description": "Introducing and describing people",
                    "phases": [
                        "introduction",
                        "basic_description",
                        "personality_highlights",
                        "relationship_context",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 10},
                "intermediate": {"duration": 15},
                "advanced": {"duration": 20},
            },
            success_metrics=[
                "Describe appearance accurately",
                "Discuss personality traits",
                "Give appropriate compliments",
            ],
        )

    @staticmethod
    def _create_feelings_emotions_template() -> UniversalScenarioTemplate:
        """Create feelings and emotions template (25)"""
        return UniversalScenarioTemplate(
            template_id="feelings_emotions",
            name="Feelings and Emotions",
            category=ScenarioCategory.SOCIAL,
            tier=3,
            base_vocabulary=[
                "happy",
                "sad",
                "angry",
                "excited",
                "nervous",
                "worried",
                "calm",
                "tired",
                "energetic",
                "frustrated",
                "disappointed",
                "proud",
                "grateful",
                "emotions",
                "feelings",
                "mood",
                "stress",
                "relaxed",
                "anxious",
            ],
            essential_phrases={
                "beginner": ["I'm happy", "I feel sad", "Are you okay?", "I'm excited"],
                "intermediate": [
                    "I'm feeling a bit stressed",
                    "That makes me nervous",
                    "I'm really proud of you",
                ],
                "advanced": [
                    "I'm experiencing mixed emotions",
                    "I'm overwhelmed with gratitude",
                    "I'm feeling quite apprehensive",
                ],
            },
            cultural_context={
                "notes": "Emotional expression and discussion varies greatly between cultures"
            },
            learning_objectives=[
                "Express emotions appropriately",
                "Ask about feelings",
                "Offer emotional support",
            ],
            conversation_starters=[
                "How are you feeling?",
                "You seem happy today",
                "Is everything alright?",
            ],
            scenario_variations=[
                {
                    "id": "emotional_support",
                    "description": "Providing emotional support",
                    "phases": [
                        "emotion_recognition",
                        "empathetic_response",
                        "support_offering",
                        "resolution_discussion",
                    ],
                },
                {
                    "id": "sharing_feelings",
                    "description": "Sharing personal feelings",
                    "phases": [
                        "emotion_expression",
                        "situation_explanation",
                        "support_seeking",
                        "appreciation",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 10},
                "intermediate": {"duration": 15},
                "advanced": {"duration": 20},
            },
            success_metrics=[
                "Express emotions clearly",
                "Show empathy",
                "Handle emotional conversations",
            ],
        )

    # TIER 4: Advanced Topics (26-32)

    @staticmethod
    def _create_difficulties_solutions_template() -> UniversalScenarioTemplate:
        """Create difficulties and solutions template (26)"""
        return UniversalScenarioTemplate(
            template_id="difficulties_solutions",
            name="Difficulties and Solutions",
            category=ScenarioCategory.SOCIAL,
            tier=4,
            base_vocabulary=[
                "problem",
                "difficulty",
                "challenge",
                "solution",
                "help",
                "advice",
                "suggestion",
                "option",
                "alternative",
                "resolve",
                "fix",
                "improve",
                "overcome",
                "struggle",
                "support",
                "assistance",
                "guidance",
                "strategy",
            ],
            essential_phrases={
                "beginner": [
                    "I have a problem",
                    "Can you help me?",
                    "What should I do?",
                    "Thank you for your help",
                ],
                "intermediate": [
                    "I'm having trouble with...",
                    "Do you have any suggestions?",
                    "Maybe we could try...",
                ],
                "advanced": [
                    "I'm seeking some guidance on...",
                    "I'd appreciate your perspective",
                    "What would you recommend?",
                ],
            },
            cultural_context={
                "notes": "Problem-solving approaches and help-seeking behaviors vary by culture"
            },
            learning_objectives=[
                "Describe problems clearly",
                "Ask for help appropriately",
                "Offer solutions and advice",
            ],
            conversation_starters=[
                "I'm having trouble with...",
                "Could you give me some advice?",
                "How did you solve...?",
            ],
            scenario_variations=[
                {
                    "id": "problem_solving",
                    "description": "Collaborative problem solving",
                    "phases": [
                        "problem_identification",
                        "solution_brainstorming",
                        "option_evaluation",
                        "action_planning",
                    ],
                },
                {
                    "id": "seeking_advice",
                    "description": "Seeking and giving advice",
                    "phases": [
                        "situation_explanation",
                        "advice_request",
                        "guidance_provision",
                        "gratitude_expression",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 12},
                "intermediate": {"duration": 18},
                "advanced": {"duration": 25},
            },
            success_metrics=[
                "Describe problems clearly",
                "Ask for appropriate help",
                "Offer useful solutions",
            ],
        )

    @staticmethod
    def _create_health_wellbeing_template() -> UniversalScenarioTemplate:
        """Create health and well-being template (27)"""
        return UniversalScenarioTemplate(
            template_id="health_wellbeing",
            name="Health and Well-being",
            category=ScenarioCategory.HEALTHCARE,
            tier=4,
            base_vocabulary=[
                "wellness",
                "fitness",
                "nutrition",
                "diet",
                "exercise",
                "mental health",
                "stress",
                "relaxation",
                "meditation",
                "lifestyle",
                "habits",
                "balance",
                "healthy",
                "unhealthy",
                "prevention",
                "self-care",
                "therapy",
                "counseling",
            ],
            essential_phrases={
                "beginner": [
                    "I want to be healthy",
                    "I exercise every day",
                    "I eat vegetables",
                    "How do you stay fit?",
                ],
                "intermediate": [
                    "I'm trying to maintain a healthy lifestyle",
                    "What's good for stress relief?",
                    "I need better work-life balance",
                ],
                "advanced": [
                    "I'm focusing on holistic wellness",
                    "Mental health is equally important",
                    "I practice mindfulness regularly",
                ],
            },
            cultural_context={
                "notes": "Health concepts, traditional medicine, and wellness practices vary culturally"
            },
            learning_objectives=[
                "Discuss health and wellness",
                "Talk about lifestyle choices",
                "Share wellness strategies",
            ],
            conversation_starters=[
                "How do you stay healthy?",
                "What's your wellness routine?",
                "Any tips for better health?",
            ],
            scenario_variations=[
                {
                    "id": "wellness_discussion",
                    "description": "Discussing wellness practices",
                    "phases": [
                        "current_practices",
                        "health_goals",
                        "strategy_sharing",
                        "motivation_support",
                    ],
                },
                {
                    "id": "lifestyle_choices",
                    "description": "Talking about lifestyle choices",
                    "phases": [
                        "habit_assessment",
                        "improvement_areas",
                        "change_planning",
                        "accountability_partnership",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 15},
                "intermediate": {"duration": 20},
                "advanced": {"duration": 30},
            },
            success_metrics=[
                "Discuss health topics",
                "Share wellness practices",
                "Set health goals",
            ],
        )

    @staticmethod
    def _create_making_plans_template() -> UniversalScenarioTemplate:
        """Create advanced making plans template (28)"""
        return UniversalScenarioTemplate(
            template_id="advanced_making_plans",
            name="Advanced Making Plans",
            category=ScenarioCategory.SOCIAL,
            tier=4,
            base_vocabulary=[
                "strategy",
                "goal",
                "objective",
                "timeline",
                "milestone",
                "priority",
                "schedule",
                "deadline",
                "coordination",
                "collaboration",
                "planning",
                "preparation",
                "execution",
                "evaluation",
                "adjustment",
                "flexibility",
            ],
            essential_phrases={
                "beginner": [
                    "Let's make a plan",
                    "When should we start?",
                    "What's the goal?",
                    "I need to prepare",
                ],
                "intermediate": [
                    "We need to coordinate our efforts",
                    "What's our timeline?",
                    "Let's set some milestones",
                ],
                "advanced": [
                    "We should establish clear objectives",
                    "How shall we prioritize these tasks?",
                    "We need contingency planning",
                ],
            },
            cultural_context={
                "notes": "Planning styles, time orientation, and goal-setting vary between cultures"
            },
            learning_objectives=[
                "Create detailed plans",
                "Coordinate complex activities",
                "Manage timelines and priorities",
            ],
            conversation_starters=[
                "What's our strategy for...?",
                "How should we approach this?",
                "What are our priorities?",
            ],
            scenario_variations=[
                {
                    "id": "project_planning",
                    "description": "Planning complex projects",
                    "phases": [
                        "goal_setting",
                        "resource_allocation",
                        "timeline_creation",
                        "risk_assessment",
                    ],
                },
                {
                    "id": "life_planning",
                    "description": "Personal life planning",
                    "phases": [
                        "aspiration_discussion",
                        "goal_breakdown",
                        "action_steps",
                        "progress_tracking",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 15},
                "intermediate": {"duration": 25},
                "advanced": {"duration": 35},
            },
            success_metrics=[
                "Create comprehensive plans",
                "Coordinate effectively",
                "Manage complex timelines",
            ],
        )

    @staticmethod
    def _create_getting_house_template() -> UniversalScenarioTemplate:
        """Create getting a house template (29)"""
        return UniversalScenarioTemplate(
            template_id="getting_house",
            name="Getting a House",
            category=ScenarioCategory.DAILY_LIFE,
            tier=4,
            base_vocabulary=[
                "house",
                "apartment",
                "rent",
                "buy",
                "mortgage",
                "deposit",
                "lease",
                "property",
                "real estate",
                "agent",
                "viewing",
                "inspection",
                "contract",
                "utilities",
                "furnishing",
                "moving",
                "neighborhood",
                "location",
            ],
            essential_phrases={
                "beginner": [
                    "I need a house",
                    "How much is the rent?",
                    "Can I see the apartment?",
                    "When can I move in?",
                ],
                "intermediate": [
                    "I'm looking for a two-bedroom apartment",
                    "What's included in the rent?",
                    "Are pets allowed?",
                ],
                "advanced": [
                    "I'm interested in purchasing property",
                    "What are the terms of the lease?",
                    "Could you arrange a viewing?",
                ],
            },
            cultural_context={
                "notes": "Housing markets, rental practices, and home-buying processes vary by country"
            },
            learning_objectives=[
                "Navigate housing markets",
                "Understand rental/buying processes",
                "Discuss housing preferences",
            ],
            conversation_starters=[
                "Are you looking for a place?",
                "How's the house hunting going?",
                "What kind of place do you want?",
            ],
            scenario_variations=[
                {
                    "id": "house_hunting",
                    "description": "Searching for housing",
                    "phases": [
                        "requirement_definition",
                        "property_viewing",
                        "comparison_evaluation",
                        "decision_making",
                    ],
                },
                {
                    "id": "rental_process",
                    "description": "Renting an apartment",
                    "phases": [
                        "application_process",
                        "lease_negotiation",
                        "move_in_preparation",
                        "settling_in",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 20},
                "intermediate": {"duration": 30},
                "advanced": {"duration": 40},
            },
            success_metrics=[
                "Navigate housing processes",
                "Discuss property features",
                "Handle housing transactions",
            ],
        )

    @staticmethod
    def _create_music_performing_arts_template() -> UniversalScenarioTemplate:
        """Create music and performing arts template (30)"""
        return UniversalScenarioTemplate(
            template_id="music_performing_arts",
            name="Music and Performing Arts",
            category=ScenarioCategory.HOBBIES,
            tier=4,
            base_vocabulary=[
                "music",
                "song",
                "instrument",
                "piano",
                "guitar",
                "violin",
                "dance",
                "theater",
                "performance",
                "concert",
                "show",
                "artist",
                "musician",
                "audience",
                "stage",
                "rehearsal",
                "practice",
                "talent",
                "creative",
            ],
            essential_phrases={
                "beginner": [
                    "I like music",
                    "Can you play piano?",
                    "I went to a concert",
                    "She's a good singer",
                ],
                "intermediate": [
                    "I'm learning to play guitar",
                    "The performance was amazing",
                    "I enjoy classical music",
                ],
                "advanced": [
                    "I'm passionate about performing arts",
                    "The acoustics were exceptional",
                    "I appreciate various musical genres",
                ],
            },
            cultural_context={
                "notes": "Musical traditions, performance styles, and artistic appreciation vary widely"
            },
            learning_objectives=[
                "Discuss musical interests",
                "Talk about performances",
                "Express artistic appreciation",
            ],
            conversation_starters=[
                "What kind of music do you like?",
                "Do you play any instruments?",
                "Have you been to any good shows?",
            ],
            scenario_variations=[
                {
                    "id": "musical_interests",
                    "description": "Discussing musical preferences",
                    "phases": [
                        "genre_preferences",
                        "favorite_artists",
                        "concert_experiences",
                        "musical_memories",
                    ],
                },
                {
                    "id": "performance_review",
                    "description": "Reviewing artistic performances",
                    "phases": [
                        "performance_description",
                        "artistic_evaluation",
                        "personal_impact",
                        "recommendation_sharing",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 12},
                "intermediate": {"duration": 18},
                "advanced": {"duration": 25},
            },
            success_metrics=[
                "Discuss music and arts",
                "Express artistic preferences",
                "Review performances effectively",
            ],
        )

    @staticmethod
    def _create_past_activities_template() -> UniversalScenarioTemplate:
        """Create past activities template (31)"""
        return UniversalScenarioTemplate(
            template_id="past_activities",
            name="Past Activities",
            category=ScenarioCategory.SOCIAL,
            tier=4,
            base_vocabulary=[
                "yesterday",
                "last week",
                "ago",
                "before",
                "previously",
                "used to",
                "happened",
                "occurred",
                "experience",
                "memory",
                "remember",
                "forget",
                "past",
                "history",
                "childhood",
                "teenage",
                "young",
                "growing up",
            ],
            essential_phrases={
                "beginner": [
                    "Yesterday I went...",
                    "Last week I...",
                    "I used to...",
                    "Do you remember when...?",
                ],
                "intermediate": [
                    "I have many memories of...",
                    "When I was younger, I...",
                    "I'll never forget...",
                ],
                "advanced": [
                    "Looking back, I realize...",
                    "In retrospect, that experience...",
                    "I have vivid recollections of...",
                ],
            },
            cultural_context={
                "notes": "Storytelling styles and sharing personal history varies by culture"
            },
            learning_objectives=[
                "Talk about past experiences",
                "Share memories and stories",
                "Use past tenses correctly",
            ],
            conversation_starters=[
                "What did you do yesterday?",
                "Tell me about when you were young",
                "Do you remember...?",
            ],
            scenario_variations=[
                {
                    "id": "childhood_memories",
                    "description": "Sharing childhood memories",
                    "phases": [
                        "memory_sharing",
                        "detail_elaboration",
                        "emotion_expression",
                        "comparison_making",
                    ],
                },
                {
                    "id": "recent_experiences",
                    "description": "Discussing recent activities",
                    "phases": [
                        "activity_description",
                        "experience_evaluation",
                        "learning_outcomes",
                        "future_implications",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 12},
                "intermediate": {"duration": 18},
                "advanced": {"duration": 25},
            },
            success_metrics=[
                "Use past tenses correctly",
                "Share experiences clearly",
                "Tell engaging stories",
            ],
        )

    @staticmethod
    def _create_money_finances_template() -> UniversalScenarioTemplate:
        """Create money and finances template (32)"""
        return UniversalScenarioTemplate(
            template_id="money_finances",
            name="Money and Finances",
            category=ScenarioCategory.BUSINESS,
            tier=4,
            base_vocabulary=[
                "money",
                "budget",
                "savings",
                "investment",
                "bank",
                "account",
                "loan",
                "debt",
                "interest",
                "credit",
                "expense",
                "income",
                "financial",
                "economy",
                "cost",
                "value",
                "worth",
                "affordable",
            ],
            essential_phrases={
                "beginner": [
                    "How much money?",
                    "I need to save",
                    "It's expensive",
                    "I can't afford it",
                ],
                "intermediate": [
                    "I'm on a tight budget",
                    "I'm saving for...",
                    "What's the interest rate?",
                ],
                "advanced": [
                    "I'm considering various investment options",
                    "We need to analyze the cost-benefit",
                    "What's the return on investment?",
                ],
            },
            cultural_context={
                "notes": "Money discussions, financial planning, and economic concepts vary by culture"
            },
            learning_objectives=[
                "Discuss financial topics",
                "Talk about budgeting and saving",
                "Understand basic economic concepts",
            ],
            conversation_starters=[
                "How do you manage your budget?",
                "Are you saving for anything?",
                "What do you think of the economy?",
            ],
            scenario_variations=[
                {
                    "id": "personal_budgeting",
                    "description": "Discussing personal finances",
                    "phases": [
                        "income_expenses",
                        "saving_goals",
                        "budgeting_strategies",
                        "financial_planning",
                    ],
                },
                {
                    "id": "financial_advice",
                    "description": "Seeking financial guidance",
                    "phases": [
                        "situation_assessment",
                        "goal_clarification",
                        "option_exploration",
                        "decision_support",
                    ],
                },
            ],
            difficulty_modifiers={
                "beginner": {"duration": 15},
                "intermediate": {"duration": 25},
                "advanced": {"duration": 35},
            },
            success_metrics=[
                "Discuss financial topics appropriately",
                "Use economic vocabulary",
                "Handle money-related conversations",
            ],
        )
