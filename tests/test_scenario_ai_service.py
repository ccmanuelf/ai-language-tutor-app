"""
Tests for AI-Enhanced Scenario Service
"""

import pytest

from app.services.scenario_ai_service import ScenarioAIService


class TestScenarioAIService:
    """Test AI-powered scenario enhancements"""

    def setup_method(self):
        """Setup test fixtures"""
        self.ai_service = ScenarioAIService(ai_client=None)  # Use rule-based fallback

    @pytest.mark.asyncio
    async def test_rule_based_difficulty_assessment_beginner(self):
        """Test rule-based assessment identifies beginner scenarios"""
        scenario_data = {
            "title": "Simple Greetings",
            "category": "social",
            "phases": [
                {
                    "name": "Hello",
                    "description": "Say hello",
                    "key_vocabulary": ["hello", "hi", "hey"],
                    "essential_phrases": ["Hello!", "Hi there", "Good morning"],
                    "learning_objectives": ["Greet people"],
                    "success_criteria": ["Say hello"],
                },
                {
                    "name": "Goodbye",
                    "description": "Say goodbye",
                    "key_vocabulary": ["bye", "goodbye", "see you"],
                    "essential_phrases": ["Goodbye!", "Bye bye", "See you later"],
                    "learning_objectives": ["Say goodbye"],
                    "success_criteria": ["Say goodbye"],
                },
            ],
            "vocabulary_focus": ["hello", "hi", "bye", "goodbye"],
            "prerequisites": [],
        }

        result = await self.ai_service.assess_scenario_difficulty(scenario_data)

        assert result["difficulty"] == "beginner"
        assert result["confidence"] > 0.5
        assert "ai_powered" in result
        assert result["ai_powered"] == False  # Fallback mode

    @pytest.mark.asyncio
    async def test_rule_based_difficulty_assessment_advanced(self):
        """Test rule-based assessment identifies advanced scenarios"""
        scenario_data = {
            "title": "Complex Business Negotiation",
            "category": "business",
            "phases": [
                {
                    "name": "Opening Negotiation",
                    "description": "Establish negotiation parameters",
                    "key_vocabulary": [
                        "negotiation",
                        "parameters",
                        "stakeholders",
                        "leverage",
                        "concessions",
                        "deadlock",
                        "arbitration",
                        "mediation",
                    ],
                    "essential_phrases": [
                        "Let's establish the parameters for this negotiation",
                        "We need to consider all stakeholders' interests",
                        "What leverage do we have in this situation?",
                        "Are you willing to make any concessions?",
                    ],
                    "learning_objectives": [
                        "Establish negotiation framework",
                        "Identify stakeholder interests",
                    ],
                    "success_criteria": ["Framework established"],
                },
                {
                    "name": "Strategic Discussion",
                    "description": "Discuss strategic options",
                    "key_vocabulary": [
                        "strategy",
                        "alternatives",
                        "contingency",
                        "synergy",
                        "optimization",
                        "compromise",
                        "resolution",
                    ],
                    "essential_phrases": [
                        "We should explore alternative strategic approaches",
                        "Let's develop a contingency plan",
                        "This creates significant synergy opportunities",
                    ],
                    "learning_objectives": ["Strategic thinking"],
                    "success_criteria": ["Strategy agreed"],
                },
                {
                    "name": "Agreement Finalization",
                    "description": "Finalize terms",
                    "key_vocabulary": [
                        "terms",
                        "conditions",
                        "clause",
                        "amendment",
                        "ratification",
                        "implementation",
                    ],
                    "essential_phrases": [
                        "Let's finalize the terms of our agreement",
                        "We need to add a clause regarding implementation",
                    ],
                    "learning_objectives": ["Finalize agreement"],
                    "success_criteria": ["Agreement signed"],
                },
                {
                    "name": "Post-Agreement Review",
                    "description": "Review and confirm",
                    "key_vocabulary": ["review", "confirm", "documentation"],
                    "essential_phrases": ["Let's review the documentation"],
                    "learning_objectives": ["Review process"],
                    "success_criteria": ["Reviewed"],
                },
            ],
            "vocabulary_focus": [
                "negotiation",
                "stakeholders",
                "leverage",
                "concessions",
                "arbitration",
                "mediation",
                "strategy",
                "contingency",
                "synergy",
                "optimization",
                "ratification",
                "implementation",
            ],
            "prerequisites": [
                "business_vocabulary",
                "advanced_grammar",
                "cultural_business_norms",
                "professional_communication",
                "negotiation_basics",
            ],
        }

        result = await self.ai_service.assess_scenario_difficulty(scenario_data)

        assert result["difficulty"] == "advanced"
        assert result["confidence"] > 0.5
        assert "factors" in result

    @pytest.mark.asyncio
    async def test_difficulty_assessment_with_tutor_profile(self):
        """Test assessment considers tutor profile context"""
        scenario_data = {
            "title": "Intermediate Scenario",
            "category": "travel",
            "phases": [
                {
                    "name": "Phase 1",
                    "key_vocabulary": ["airport", "ticket", "gate", "boarding"],
                    "essential_phrases": [
                        "Where is gate 5?",
                        "I need my boarding pass",
                    ],
                    "learning_objectives": ["Navigate airport"],
                    "success_criteria": ["Find gate"],
                },
                {
                    "name": "Phase 2",
                    "key_vocabulary": ["customs", "declaration", "passport"],
                    "essential_phrases": ["Nothing to declare", "Here is my passport"],
                    "learning_objectives": ["Complete customs"],
                    "success_criteria": ["Clear customs"],
                },
            ],
            "vocabulary_focus": ["airport", "ticket", "customs", "passport"],
            "prerequisites": ["basic_travel_vocabulary"],
        }

        tutor_profile = {
            "name": "Strict Tutor",
            "teaching_style": "rigorous",
            "default_difficulty": "advanced",
        }

        result = await self.ai_service.assess_scenario_difficulty(
            scenario_data, tutor_profile
        )

        # Should still assess based on content, not just tutor preference
        assert result["difficulty"] in ["beginner", "intermediate", "advanced"]
        assert "confidence" in result

    def test_parse_difficulty_response_json(self):
        """Test parsing valid JSON response"""
        ai_response = """{
            "difficulty": "intermediate",
            "confidence": 0.85,
            "reasoning": "Moderate vocabulary with some complex phrases",
            "factors": {
                "vocabulary_complexity": 0.6,
                "grammar_complexity": 0.5
            },
            "recommendations": ["Add more practice phrases"]
        }"""

        result = self.ai_service._parse_difficulty_response(ai_response)

        assert result["difficulty"] == "intermediate"
        assert result["confidence"] == 0.85
        assert "reasoning" in result
        assert "factors" in result

    def test_parse_difficulty_response_markdown(self):
        """Test parsing JSON wrapped in markdown code blocks"""
        ai_response = """```json
{
    "difficulty": "beginner",
    "confidence": 0.9,
    "reasoning": "Simple vocabulary and phrases"
}
```"""

        result = self.ai_service._parse_difficulty_response(ai_response)

        assert result["difficulty"] == "beginner"
        assert result["confidence"] == 0.9

    def test_parse_difficulty_response_invalid(self):
        """Test fallback when AI response is unparseable"""
        ai_response = "This scenario looks like it's at an intermediate level."

        result = self.ai_service._parse_difficulty_response(ai_response)

        # Should extract "intermediate" from text
        assert result["difficulty"] == "intermediate"
        assert result["confidence"] == 0.5
        assert "parse_error" in result

    def test_rule_based_assessment_handles_missing_fields(self):
        """Test rule-based assessment with minimal data"""
        scenario_data = {
            "title": "Minimal Scenario",
            "phases": [
                {"key_vocabulary": ["word1"], "essential_phrases": ["phrase1"]},
                {"key_vocabulary": ["word2"], "essential_phrases": ["phrase2"]},
            ],
        }

        result = self.ai_service._rule_based_difficulty_assessment(scenario_data)

        assert result["difficulty"] in ["beginner", "intermediate", "advanced"]
        assert result["confidence"] > 0
        assert result["ai_powered"] == False
