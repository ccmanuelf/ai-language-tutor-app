#!/usr/bin/env python3
"""
Add 9 new production scenarios to scenarios.json
Session 130: Production Scenarios
"""

import json
from datetime import datetime

# Read current scenarios
with open("data/scenarios/scenarios.json", "r") as f:
    scenarios = json.load(f)

timestamp = datetime.now().isoformat()

# Scenario 1: Business Meeting
scenarios["business_meeting_first_time"] = {
    "scenario_id": "business_meeting_first_time",
    "name": "First Business Meeting with International Partners",
    "category": "business",
    "difficulty": "beginner",
    "description": "Practice conducting your first business meeting with international colleagues, including introductions, small talk, discussing the agenda, and closing professionally.",
    "user_role": "business_professional",
    "ai_role": "business_colleague",
    "setting": "Modern conference room in an international company office",
    "duration_minutes": 15,
    "phases": [
        {
            "phase_id": "professional_introductions",
            "name": "Professional Introductions",
            "description": "Exchange introductions and business cards",
            "expected_duration_minutes": 3,
            "key_vocabulary": [
                "introduction",
                "colleague",
                "position",
                "department",
                "company",
                "pleased",
                "meet",
            ],
            "essential_phrases": [
                "Nice to meet you, I'm...",
                "I work in the... department",
                "What's your role in the company?",
                "Pleased to meet you too",
            ],
            "learning_objectives": [
                "Make professional introductions",
                "Exchange business card etiquette",
                "Use appropriate formal greetings",
            ],
            "cultural_notes": "In international business, firm handshakes and eye contact show professionalism. Business cards should be presented and received with both hands in many Asian cultures.",
            "success_criteria": [
                "Introduce yourself professionally",
                "Exchange roles and departments",
                "Show appropriate business etiquette",
            ],
        },
        {
            "phase_id": "small_talk_rapport",
            "name": "Small Talk and Rapport Building",
            "description": "Build professional rapport through appropriate small talk",
            "expected_duration_minutes": 3,
            "key_vocabulary": [
                "weather",
                "travel",
                "comfortable",
                "office",
                "facilities",
                "journey",
                "accommodation",
            ],
            "essential_phrases": [
                "How was your journey here?",
                "Have you had time to see the city?",
                "Is everything comfortable with your accommodation?",
                "The weather has been nice lately",
            ],
            "learning_objectives": [
                "Build professional rapport",
                "Engage in appropriate business small talk",
                "Show cultural awareness and courtesy",
            ],
            "cultural_notes": "Small talk before business is important in most cultures. Keep topics neutral (weather, travel) and avoid politics or religion.",
            "success_criteria": [
                "Engage in at least 2 minutes of small talk",
                "Ask courteous questions about their comfort",
                "Transition smoothly to business discussion",
            ],
        },
        {
            "phase_id": "agenda_discussion",
            "name": "Agenda Discussion",
            "description": "Review agenda and participate in business discussions",
            "expected_duration_minutes": 7,
            "key_vocabulary": [
                "agenda",
                "objective",
                "timeline",
                "proposal",
                "discussion",
                "review",
                "decision",
                "action items",
            ],
            "essential_phrases": [
                "Let's review today's agenda",
                "Our main objective is to...",
                "What are your thoughts on this proposal?",
                "Should we move to the next item?",
                "Let me make a note of that",
            ],
            "learning_objectives": [
                "Follow structured meeting agenda",
                "Participate in business discussions",
                "Express opinions professionally",
                "Take and assign action items",
            ],
            "cultural_notes": "In Western business culture, meetings are usually structured with a clear agenda. Everyone is expected to contribute. In some cultures, junior members speak less.",
            "success_criteria": [
                "Follow agenda structure",
                "Contribute to at least one discussion point",
                "Understand action items assigned",
            ],
        },
        {
            "phase_id": "professional_closing",
            "name": "Professional Closing",
            "description": "Summarize decisions and agree on next steps",
            "expected_duration_minutes": 2,
            "key_vocabulary": [
                "summary",
                "next steps",
                "follow up",
                "deadline",
                "meeting",
                "schedule",
                "contact",
            ],
            "essential_phrases": [
                "Let me summarize our key decisions",
                "What are our next steps?",
                "When should we schedule our follow-up?",
                "Thank you for your time today",
                "I'll send you the meeting notes",
            ],
            "learning_objectives": [
                "Summarize meeting outcomes",
                "Agree on follow-up actions",
                "Close meeting professionally",
            ],
            "cultural_notes": "Always end with clear next steps and deadlines. Following up with written notes is professional practice in most business cultures.",
            "success_criteria": [
                "Understand meeting summary",
                "Confirm next steps and timeline",
                "Exchange contact information if needed",
            ],
        },
    ],
    "prerequisites": ["basic_greetings", "professional_vocabulary", "time_expressions"],
    "learning_outcomes": [
        "Conduct professional business meetings",
        "Navigate intercultural business situations",
        "Follow meeting protocols effectively",
    ],
    "vocabulary_focus": [
        "meeting",
        "agenda",
        "colleague",
        "introduction",
        "department",
        "proposal",
        "discussion",
        "objective",
        "action items",
        "follow up",
        "schedule",
        "deadline",
        "professional",
        "presentation",
    ],
    "cultural_context": {
        "meeting_etiquette": "Arrive on time, silence phones, take notes, participate actively",
        "communication_style": "Direct but polite communication is valued in international business",
        "hierarchical_awareness": "Be aware that some cultures have stronger hierarchy than others",
    },
    "is_active": True,
    "created_at": timestamp,
    "updated_at": timestamp,
}

print("Added: Business Meeting")
print(f"Progress: 1/9 scenarios added")
print("Continuing with remaining scenarios...")
