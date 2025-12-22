"""
AI-Enhanced Scenario Service for AI Language Tutor App

This service provides AI-powered enhancements for scenario creation:
- Automatic difficulty assessment
- Tutor profile-based vocabulary suggestions
- AI-assisted scenario generation
- Cultural note generation

Integrates with tutor profiles for consistent, personality-aligned content.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ScenarioAIService:
    """AI-powered scenario enhancement service"""

    def __init__(self, ai_client=None):
        """
        Initialize AI service for scenarios

        Args:
            ai_client: AI client instance (Claude, OpenAI, etc.)
        """
        self.ai_client = ai_client or self._get_default_ai_client()
        settings = get_settings()
        self.model = getattr(settings, "AI_MODEL", "claude-3-5-sonnet-20241022")

    def _get_default_ai_client(self):
        """Get default AI client from app settings"""
        try:
            from app.core.ai_client import get_ai_client

            return get_ai_client()
        except Exception as e:
            logger.warning(f"Could not get AI client: {e}")
            return None

    async def assess_scenario_difficulty(
        self,
        scenario_data: Dict[str, Any],
        tutor_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Automatically assess scenario difficulty using AI

        Analyzes:
        - Vocabulary complexity
        - Grammar structures
        - Phrase length and complexity
        - Number of phases
        - Cultural context depth
        - Prerequisites

        Args:
            scenario_data: Scenario information (title, phases, vocabulary, etc.)
            tutor_profile: Optional tutor profile for context

        Returns:
            {
                "difficulty": "beginner" | "intermediate" | "advanced",
                "confidence": 0.0-1.0,
                "reasoning": "Explanation of assessment",
                "factors": {
                    "vocabulary_complexity": 0.0-1.0,
                    "grammar_complexity": 0.0-1.0,
                    "cultural_depth": 0.0-1.0,
                    "prerequisite_level": 0.0-1.0
                },
                "recommendations": ["suggestion1", "suggestion2"]
            }
        """
        if not self.ai_client:
            # Fallback to rule-based assessment
            return self._rule_based_difficulty_assessment(scenario_data)

        try:
            # Prepare analysis prompt
            prompt = self._build_difficulty_assessment_prompt(
                scenario_data, tutor_profile
            )

            # Call AI for analysis
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert language learning curriculum designer. Assess the difficulty level of language learning scenarios with precision.",
                },
                {"role": "user", "content": prompt},
            ]

            response = await self.ai_client.generate_response(
                messages=messages,
                temperature=0.3,  # Low temperature for consistent assessment
                max_tokens=1000,
            )

            # Parse AI response
            result = self._parse_difficulty_response(response.content)
            result["ai_powered"] = True
            result["model_used"] = response.model

            logger.info(
                f"AI difficulty assessment: {result['difficulty']} "
                f"(confidence: {result['confidence']:.2f})"
            )

            return result

        except Exception as e:
            logger.error(f"AI difficulty assessment failed: {e}")
            # Fallback to rule-based
            fallback = self._rule_based_difficulty_assessment(scenario_data)
            fallback["ai_powered"] = False
            fallback["error"] = str(e)
            return fallback

    def _build_difficulty_assessment_prompt(
        self, scenario_data: Dict[str, Any], tutor_profile: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for difficulty assessment"""

        # Extract scenario details
        title = scenario_data.get("title", "Untitled")
        category = scenario_data.get("category", "general")
        phases = scenario_data.get("phases", [])
        vocabulary = scenario_data.get("vocabulary_focus", [])
        prerequisites = scenario_data.get("prerequisites", [])

        # Count complexity indicators
        total_vocabulary = len(vocabulary)
        total_phases = len(phases)

        # Collect all phrases for analysis
        all_phrases = []
        for phase in phases:
            all_phrases.extend(phase.get("essential_phrases", []))

        # Build tutor context
        tutor_context = ""
        if tutor_profile:
            tutor_context = f"""
Tutor Profile Context:
- Name: {tutor_profile.get("name", "Unknown")}
- Teaching Style: {tutor_profile.get("teaching_style", "balanced")}
- Difficulty Preference: {tutor_profile.get("default_difficulty", "intermediate")}
"""

        prompt = f"""Assess the difficulty level of this language learning scenario.

Scenario Title: {title}
Category: {category}
Number of Phases: {total_phases}
Total Vocabulary Items: {total_vocabulary}
Prerequisites: {", ".join(prerequisites) if prerequisites else "None"}

Sample Vocabulary: {", ".join(vocabulary[:10])}
{f"(+{total_vocabulary - 10} more)" if total_vocabulary > 10 else ""}

Sample Phrases:
{chr(10).join(f"- {phrase}" for phrase in all_phrases[:5])}
{f"(+{len(all_phrases) - 5} more phrases)" if len(all_phrases) > 5 else ""}

{tutor_context}

Analyze the following factors:
1. **Vocabulary Complexity**: Are the words common (beginner), moderately complex (intermediate), or advanced/specialized (advanced)?
2. **Grammar Structures**: Simple present tense vs complex tenses, conditionals, subjunctive, etc.
3. **Phrase Length**: Short simple phrases vs long complex sentences
4. **Cultural Context**: Basic cultural awareness vs deep cultural understanding required
5. **Prerequisites**: What prior knowledge is needed?

Respond in JSON format:
{{
  "difficulty": "beginner" | "intermediate" | "advanced",
  "confidence": 0.0-1.0,
  "reasoning": "2-3 sentence explanation",
  "factors": {{
    "vocabulary_complexity": 0.0-1.0,
    "grammar_complexity": 0.0-1.0,
    "cultural_depth": 0.0-1.0,
    "prerequisite_level": 0.0-1.0
  }},
  "recommendations": ["suggestion1", "suggestion2", "suggestion3"]
}}

Be precise and consistent. Consider the holistic difficulty, not just vocabulary count."""

        return prompt

    def _parse_difficulty_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into structured difficulty assessment"""
        try:
            # Try to extract JSON from response
            # Handle cases where AI wraps JSON in markdown code blocks
            response_cleaned = ai_response.strip()

            if "```json" in response_cleaned:
                # Extract JSON from code block
                start = response_cleaned.find("```json") + 7
                end = response_cleaned.find("```", start)
                response_cleaned = response_cleaned[start:end].strip()
            elif "```" in response_cleaned:
                start = response_cleaned.find("```") + 3
                end = response_cleaned.find("```", start)
                response_cleaned = response_cleaned[start:end].strip()

            result = json.loads(response_cleaned)

            # Validate required fields
            if "difficulty" not in result:
                raise ValueError("Missing 'difficulty' field in AI response")

            # Ensure difficulty is valid
            if result["difficulty"] not in ["beginner", "intermediate", "advanced"]:
                raise ValueError(f"Invalid difficulty: {result['difficulty']}")

            # Set defaults for optional fields
            result.setdefault("confidence", 0.8)
            result.setdefault("reasoning", "AI assessment completed")
            result.setdefault("factors", {})
            result.setdefault("recommendations", [])

            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI difficulty response: {e}")
            logger.debug(f"AI response was: {ai_response}")

            # Attempt to extract difficulty from text
            response_lower = ai_response.lower()
            if "beginner" in response_lower:
                difficulty = "beginner"
            elif "advanced" in response_lower:
                difficulty = "advanced"
            else:
                difficulty = "intermediate"

            return {
                "difficulty": difficulty,
                "confidence": 0.5,
                "reasoning": "Extracted from unstructured AI response",
                "factors": {},
                "recommendations": [],
                "parse_error": str(e),
            }

    def _rule_based_difficulty_assessment(
        self, scenario_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback rule-based difficulty assessment

        Uses heuristics when AI is unavailable
        """
        phases = scenario_data.get("phases", [])
        vocabulary = scenario_data.get("vocabulary_focus", [])
        prerequisites = scenario_data.get("prerequisites", [])

        # Calculate complexity score (0.0 - 1.0)
        scores = []

        # Factor 1: Number of phases (more phases = harder)
        phase_count = len(phases)
        phase_score = min(phase_count / 6.0, 1.0)  # 6+ phases = 1.0
        scores.append(phase_score)

        # Factor 2: Vocabulary count (more words = harder)
        vocab_count = len(vocabulary)
        vocab_score = min(vocab_count / 30.0, 1.0)  # 30+ words = 1.0
        scores.append(vocab_score)

        # Factor 3: Prerequisites (more prereqs = harder)
        prereq_count = len(prerequisites)
        prereq_score = min(prereq_count / 5.0, 1.0)  # 5+ prereqs = 1.0
        scores.append(prereq_score)

        # Factor 4: Phrase complexity (average phrase length)
        all_phrases = []
        for phase in phases:
            all_phrases.extend(phase.get("essential_phrases", []))

        if all_phrases:
            avg_phrase_length = sum(len(p.split()) for p in all_phrases) / len(
                all_phrases
            )
            phrase_score = min((avg_phrase_length - 3) / 7.0, 1.0)  # 3-10 words
            phrase_score = max(phrase_score, 0.0)  # Ensure >= 0
            scores.append(phrase_score)

        # Calculate overall complexity
        overall_complexity = sum(scores) / len(scores)

        # Boost complexity if prerequisites suggest advanced level
        if prereq_count >= 4:
            overall_complexity = min(overall_complexity + 0.15, 1.0)

        # Boost complexity if vocabulary is very extensive
        if vocab_count >= 25:
            overall_complexity = min(overall_complexity + 0.1, 1.0)

        # Map to difficulty level
        if overall_complexity < 0.35:
            difficulty = "beginner"
            confidence = 0.7
        elif overall_complexity < 0.60:
            difficulty = "intermediate"
            confidence = 0.75
        else:
            difficulty = "advanced"
            confidence = 0.7

        return {
            "difficulty": difficulty,
            "confidence": confidence,
            "reasoning": f"Rule-based assessment: {phase_count} phases, {vocab_count} vocabulary items, complexity score {overall_complexity:.2f}",
            "factors": {
                "vocabulary_complexity": vocab_score,
                "grammar_complexity": phrase_score if all_phrases else 0.5,
                "cultural_depth": prereq_score,
                "prerequisite_level": prereq_score,
            },
            "recommendations": [
                f"Consider adjusting vocabulary to match {difficulty} level",
                f"Current complexity score: {overall_complexity:.2f}",
            ],
            "ai_powered": False,
            "method": "rule_based",
        }

    async def suggest_vocabulary(
        self,
        scenario_data: Dict[str, Any],
        difficulty: str,
        tutor_profile: Optional[Dict[str, Any]] = None,
        count: int = 15,
    ) -> Dict[str, Any]:
        """
        Suggest appropriate vocabulary based on difficulty and tutor profile

        Args:
            scenario_data: Scenario context (title, category, description)
            difficulty: Target difficulty level
            tutor_profile: Tutor profile for personality-aligned suggestions
            count: Number of vocabulary items to suggest

        Returns:
            {
                "vocabulary": ["word1", "word2", ...],
                "definitions": {"word1": "definition", ...},
                "difficulty_match": "beginner" | "intermediate" | "advanced",
                "tutor_aligned": bool,
                "example_usage": {"word1": "example sentence", ...}
            }
        """
        if not self.ai_client:
            # Fallback to basic vocabulary
            return self._fallback_vocabulary_suggestions(
                scenario_data, difficulty, count
            )

        try:
            # Build vocabulary suggestion prompt
            prompt = self._build_vocabulary_prompt(
                scenario_data, difficulty, tutor_profile, count
            )

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert language educator specializing in vocabulary selection for different proficiency levels.",
                },
                {"role": "user", "content": prompt},
            ]

            response = await self.ai_client.generate_response(
                messages=messages,
                temperature=0.4,  # Moderate creativity
                max_tokens=2000,
            )

            # Parse response
            result = self._parse_vocabulary_response(response.content)
            result["ai_powered"] = True
            result["difficulty_match"] = difficulty
            result["tutor_aligned"] = tutor_profile is not None

            logger.info(
                f"AI vocabulary suggestions: {len(result.get('vocabulary', []))} words "
                f"for {difficulty} level"
            )

            return result

        except Exception as e:
            logger.error(f"AI vocabulary suggestion failed: {e}")
            # Fallback
            fallback = self._fallback_vocabulary_suggestions(
                scenario_data, difficulty, count
            )
            fallback["ai_powered"] = False
            fallback["error"] = str(e)
            return fallback

    async def generate_scenario_content(
        self,
        prompt: str,
        category: str,
        difficulty: str,
        tutor_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate complete scenario content from a simple prompt

        Args:
            prompt: User's scenario idea (e.g., "Ordering food at a restaurant")
            category: Scenario category
            difficulty: Target difficulty
            tutor_profile: Tutor profile for style alignment

        Returns:
            Complete scenario structure ready to save
        """
        if not self.ai_client:
            return self._fallback_scenario_generation(prompt, category, difficulty)

        try:
            generation_prompt = self._build_scenario_generation_prompt(
                prompt, category, difficulty, tutor_profile
            )

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert language learning curriculum designer. Create engaging, pedagogically sound conversation scenarios for language learners.",
                },
                {"role": "user", "content": generation_prompt},
            ]

            response = await self.ai_client.generate_response(
                messages=messages, temperature=0.7, max_tokens=3000
            )

            result = self._parse_scenario_generation_response(response.content)
            result["ai_powered"] = True
            result["generated_from"] = prompt
            result["category"] = category
            result["difficulty"] = difficulty

            logger.info(
                f"AI scenario generation: '{result.get('title', 'Untitled')}' "
                f"with {len(result.get('phases', []))} phases"
            )

            return result

        except Exception as e:
            logger.error(f"AI scenario generation failed: {e}")
            fallback = self._fallback_scenario_generation(prompt, category, difficulty)
            fallback["ai_powered"] = False
            fallback["error"] = str(e)
            return fallback

    def _build_vocabulary_prompt(
        self,
        scenario_data: Dict[str, Any],
        difficulty: str,
        tutor_profile: Optional[Dict[str, Any]],
        count: int,
    ) -> str:
        """Build prompt for vocabulary suggestions"""

        title = scenario_data.get("title", "Untitled")
        category = scenario_data.get("category", "general")
        description = scenario_data.get("description", "")
        existing_vocab = scenario_data.get("vocabulary_focus", [])

        # Tutor profile context
        tutor_context = ""
        if tutor_profile:
            tutor_name = tutor_profile.get("name", "Unknown")
            teaching_style = tutor_profile.get("teaching_style", "balanced")
            personality = tutor_profile.get("personality_traits", [])

            tutor_context = f"""
Tutor Profile Context:
- Tutor Name: {tutor_name}
- Teaching Style: {teaching_style}
- Personality: {", ".join(personality) if personality else "balanced"}

The vocabulary should match this tutor's teaching approach:
- Formal tutors prefer academic/professional vocabulary
- Casual tutors prefer everyday conversational terms
- Encouraging tutors choose accessible, confidence-building words
- Strict tutors select precise, challenging vocabulary
"""

        # Difficulty guidelines
        difficulty_guidelines = {
            "beginner": "Use common, everyday words. Avoid idioms, slang, or technical terms. Focus on high-frequency vocabulary (top 1000-2000 words).",
            "intermediate": "Use moderately complex vocabulary. Include some idiomatic expressions and semi-technical terms. Assume familiarity with basic grammar.",
            "advanced": "Use sophisticated, nuanced vocabulary. Include idioms, colloquialisms, technical terms, and specialized language appropriate to the scenario.",
        }

        prompt = f"""Suggest {count} vocabulary words for this language learning scenario.

Scenario Title: {title}
Category: {category}
Description: {description if description else "Not provided"}
Difficulty Level: {difficulty}

{tutor_context}

Difficulty Guidelines:
{difficulty_guidelines.get(difficulty, difficulty_guidelines["intermediate"])}

Existing Vocabulary: {", ".join(existing_vocab[:10]) if existing_vocab else "None yet"}

Requirements:
1. Suggest exactly {count} vocabulary words appropriate for {difficulty} level
2. Words should be directly relevant to the scenario category ({category})
3. Include a mix of nouns, verbs, and adjectives
4. Avoid repeating words from the existing vocabulary list
5. Provide simple definitions (10-15 words each)
6. Include one example sentence per word showing natural usage

Respond in JSON format:
{{
  "vocabulary": ["word1", "word2", ...],
  "definitions": {{
    "word1": "concise definition",
    "word2": "concise definition"
  }},
  "example_usage": {{
    "word1": "Example sentence using word1 in context",
    "word2": "Example sentence using word2 in context"
  }},
  "word_types": {{
    "word1": "noun",
    "word2": "verb"
  }}
}}

Ensure all words are at the {difficulty} proficiency level."""

        return prompt

    def _parse_vocabulary_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI vocabulary response"""
        try:
            # Clean response
            response_cleaned = ai_response.strip()

            if "```json" in response_cleaned:
                start = response_cleaned.find("```json") + 7
                end = response_cleaned.find("```", start)
                response_cleaned = response_cleaned[start:end].strip()
            elif "```" in response_cleaned:
                start = response_cleaned.find("```") + 3
                end = response_cleaned.find("```", start)
                response_cleaned = response_cleaned[start:end].strip()

            result = json.loads(response_cleaned)

            # Validate structure
            if "vocabulary" not in result or not isinstance(result["vocabulary"], list):
                raise ValueError("Invalid vocabulary structure")

            # Set defaults
            result.setdefault("definitions", {})
            result.setdefault("example_usage", {})
            result.setdefault("word_types", {})

            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse vocabulary response: {e}")
            logger.debug(f"Response was: {ai_response}")

            # Try to extract words from text
            words = []
            for line in ai_response.split("\n"):
                line = line.strip()
                if line and len(line.split()) <= 3 and line[0].islower():
                    words.append(line.split()[0])

            return {
                "vocabulary": words[:15] if words else [],
                "definitions": {},
                "example_usage": {},
                "word_types": {},
                "parse_error": str(e),
            }

    def _fallback_vocabulary_suggestions(
        self, scenario_data: Dict[str, Any], difficulty: str, count: int
    ) -> Dict[str, Any]:
        """Fallback vocabulary suggestions by category"""

        category = scenario_data.get("category", "general")

        # Basic vocabulary by category and difficulty
        vocabulary_bank = {
            "restaurant": {
                "beginner": [
                    "menu",
                    "table",
                    "food",
                    "drink",
                    "waiter",
                    "bill",
                    "order",
                    "eat",
                    "hungry",
                    "delicious",
                    "reservation",
                    "seat",
                    "tip",
                    "breakfast",
                    "lunch",
                ],
                "intermediate": [
                    "appetizer",
                    "entree",
                    "cuisine",
                    "portions",
                    "recommendation",
                    "allergies",
                    "vegetarian",
                    "specialty",
                    "beverage",
                    "receipt",
                    "gratuity",
                    "utensils",
                    "napkin",
                    "condiments",
                    "garnish",
                ],
                "advanced": [
                    "sommelier",
                    "amuse-bouche",
                    "al dente",
                    "blanched",
                    "braised",
                    "caramelized",
                    "julienned",
                    "reduction",
                    "roux",
                    "sautéed",
                    "accompaniment",
                    "palate",
                    "gastronomy",
                    "epicurean",
                    "culinary",
                ],
            },
            "travel": {
                "beginner": [
                    "ticket",
                    "passport",
                    "luggage",
                    "airport",
                    "hotel",
                    "taxi",
                    "map",
                    "tourist",
                    "visit",
                    "trip",
                    "bag",
                    "flight",
                    "seat",
                    "gate",
                    "boarding",
                ],
                "intermediate": [
                    "itinerary",
                    "accommodation",
                    "departure",
                    "arrival",
                    "connection",
                    "customs",
                    "immigration",
                    "exchange rate",
                    "currency",
                    "reservation",
                    "concierge",
                    "amenities",
                    "layover",
                    "terminal",
                    "carryon",
                ],
                "advanced": [
                    "expatriate",
                    "sojourn",
                    "excursion",
                    "pilgrimage",
                    "odyssey",
                    "wanderlust",
                    "itinerant",
                    "cosmopolitan",
                    "provincial",
                    "vernacular",
                    "indigenous",
                    "expatriate",
                    "diaspora",
                    "nomadic",
                    "transient",
                ],
            },
            "shopping": {
                "beginner": [
                    "buy",
                    "sell",
                    "price",
                    "money",
                    "store",
                    "shop",
                    "clothes",
                    "shoes",
                    "bag",
                    "pay",
                    "cheap",
                    "expensive",
                    "sale",
                    "discount",
                    "cash",
                ],
                "intermediate": [
                    "purchase",
                    "transaction",
                    "receipt",
                    "refund",
                    "exchange",
                    "warranty",
                    "bargain",
                    "merchandise",
                    "inventory",
                    "checkout",
                    "fitting room",
                    "cashier",
                    "credit card",
                    "debit",
                    "payment",
                ],
                "advanced": [
                    "procurement",
                    "acquisition",
                    "consumerism",
                    "retail therapy",
                    "bulk purchase",
                    "liquidation",
                    "markdown",
                    "markup",
                    "overhead",
                    "profit margin",
                    "wholesale",
                    "boutique",
                    "emporium",
                    "purveyor",
                    "vendor",
                ],
            },
            "business": {
                "beginner": [
                    "work",
                    "job",
                    "office",
                    "boss",
                    "meeting",
                    "computer",
                    "email",
                    "phone",
                    "desk",
                    "paper",
                    "pen",
                    "colleague",
                    "schedule",
                    "break",
                    "lunch",
                ],
                "intermediate": [
                    "presentation",
                    "proposal",
                    "deadline",
                    "project",
                    "client",
                    "conference",
                    "agenda",
                    "minutes",
                    "report",
                    "budget",
                    "profit",
                    "revenue",
                    "expenses",
                    "negotiation",
                    "contract",
                ],
                "advanced": [
                    "stakeholder",
                    "paradigm",
                    "synergy",
                    "leverage",
                    "optimization",
                    "scalability",
                    "bandwidth",
                    "deliverables",
                    "metrics",
                    "benchmarking",
                    "sustainability",
                    "diversification",
                    "monetization",
                    "valuation",
                    "arbitrage",
                ],
            },
            "social": {
                "beginner": [
                    "friend",
                    "talk",
                    "hello",
                    "goodbye",
                    "party",
                    "fun",
                    "happy",
                    "meet",
                    "invite",
                    "weekend",
                    "hobby",
                    "like",
                    "enjoy",
                    "laugh",
                    "smile",
                ],
                "intermediate": [
                    "acquaintance",
                    "gathering",
                    "celebration",
                    "introduction",
                    "conversation",
                    "socialize",
                    "mingle",
                    "reconnect",
                    "catch up",
                    "get-together",
                    "hangout",
                    "companionship",
                    "fellowship",
                    "camaraderie",
                    "rapport",
                ],
                "advanced": [
                    "gregarious",
                    "affable",
                    "convivial",
                    "vivacious",
                    "ebullient",
                    "effervescent",
                    "loquacious",
                    "taciturn",
                    "reticent",
                    "introverted",
                    "extroverted",
                    "charismatic",
                    "magnanimous",
                    "benevolent",
                    "philanthropic",
                ],
            },
        }

        # Get vocabulary for category and difficulty
        vocab_list = vocabulary_bank.get(category, {}).get(
            difficulty, vocabulary_bank["social"]["beginner"]
        )

        # Return first 'count' items
        selected = vocab_list[:count]

        return {
            "vocabulary": selected,
            "definitions": {word: f"Definition for {word}" for word in selected},
            "example_usage": {
                word: f"Example sentence with {word}." for word in selected
            },
            "word_types": {},
            "difficulty_match": difficulty,
            "tutor_aligned": False,
            "ai_powered": False,
            "method": "fallback_category_based",
        }

    def _build_scenario_generation_prompt(
        self,
        user_prompt: str,
        category: str,
        difficulty: str,
        tutor_profile: Optional[Dict[str, Any]],
    ) -> str:
        """Build comprehensive prompt for scenario generation"""

        tutor_context = ""
        if tutor_profile:
            name = tutor_profile.get("name", "Unknown")
            style = tutor_profile.get("teaching_style", "balanced")
            tutor_context = f"\nTutor: {name} ({style} style)"

        difficulty_specs = {
            "beginner": "2-3 phases, simple vocabulary, 3-5 word phrases",
            "intermediate": "3-4 phases, moderate vocabulary, 5-10 word phrases",
            "advanced": "4-6 phases, sophisticated vocabulary, complex expressions",
        }

        spec = difficulty_specs.get(difficulty, difficulty_specs["intermediate"])

        return f"""Create a language learning scenario: "{user_prompt}"
Category: {category} | Difficulty: {difficulty}{tutor_context}

Specs: {spec}

JSON format:
{{
  "title": "Clear Title",
  "description": "2-3 sentence description",
  "setting": "Specific location",
  "user_role": "learner role",
  "ai_role": "AI role",
  "estimated_duration": 15,
  "phases": [
    {{
      "name": "Phase Name",
      "description": "What happens",
      "expected_duration_minutes": 5,
      "key_vocabulary": ["word1", ...],
      "essential_phrases": ["phrase1", ...],
      "learning_objectives": ["objective1", ...],
      "success_criteria": ["criterion1", ...],
      "cultural_notes": "Cultural context"
    }}
  ],
  "vocabulary_focus": ["word1", ...],
  "prerequisites": ["prereq1", ...],
  "learning_outcomes": ["outcome1", ...]
}}"""

    def _parse_scenario_generation_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI-generated scenario response"""
        try:
            response_cleaned = ai_response.strip()

            if "```json" in response_cleaned:
                start = response_cleaned.find("```json") + 7
                end = response_cleaned.find("```", start)
                response_cleaned = response_cleaned[start:end].strip()
            elif "```" in response_cleaned:
                start = response_cleaned.find("```") + 3
                end = response_cleaned.find("```", start)
                response_cleaned = response_cleaned[start:end].strip()

            result = json.loads(response_cleaned)

            required_fields = ["title", "description", "phases"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")

            if not isinstance(result["phases"], list) or len(result["phases"]) < 2:
                raise ValueError("Scenario must have at least 2 phases")

            result.setdefault("setting", "General setting")
            result.setdefault("user_role", "student")
            result.setdefault("ai_role", "teacher")
            result.setdefault("estimated_duration", 15)
            result.setdefault("vocabulary_focus", [])
            result.setdefault("prerequisites", [])
            result.setdefault("learning_outcomes", [])

            for idx, phase in enumerate(result["phases"]):
                phase.setdefault("name", f"Phase {idx + 1}")
                phase.setdefault("description", "")
                phase.setdefault("expected_duration_minutes", 5)
                phase.setdefault("key_vocabulary", [])
                phase.setdefault("essential_phrases", [])
                phase.setdefault("learning_objectives", [])
                phase.setdefault("success_criteria", [])
                phase.setdefault("cultural_notes", "")

            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse scenario generation: {e}")
            return self._create_minimal_scenario_structure()

    def _create_minimal_scenario_structure(self) -> Dict[str, Any]:
        """Create minimal valid scenario structure as fallback"""
        return {
            "title": "Generated Scenario",
            "description": "AI-generated scenario",
            "setting": "General setting",
            "user_role": "student",
            "ai_role": "teacher",
            "estimated_duration": 15,
            "phases": [
                {
                    "name": "Introduction",
                    "description": "Getting started",
                    "expected_duration_minutes": 5,
                    "key_vocabulary": [],
                    "essential_phrases": [],
                    "learning_objectives": [],
                    "success_criteria": [],
                },
                {
                    "name": "Main Activity",
                    "description": "Core interaction",
                    "expected_duration_minutes": 10,
                    "key_vocabulary": [],
                    "essential_phrases": [],
                    "learning_objectives": [],
                    "success_criteria": [],
                },
            ],
            "vocabulary_focus": [],
            "prerequisites": [],
            "learning_outcomes": [],
        }

    def _fallback_scenario_generation(
        self, prompt: str, category: str, difficulty: str
    ) -> Dict[str, Any]:
        """Fallback scenario generation when AI unavailable"""

        prompt_words = prompt.lower().split()
        action_words = [w for w in prompt_words if len(w) > 3]
        title = prompt.title() if len(prompt) < 50 else f"{category.title()} Scenario"

        return {
            "title": title,
            "description": f"A {difficulty} level scenario about {prompt.lower()}.",
            "setting": f"A typical {category} setting",
            "user_role": "student",
            "ai_role": "conversation partner",
            "estimated_duration": 15,
            "phases": [
                {
                    "name": "Introduction",
                    "description": f"Begin the {prompt.lower()} activity",
                    "expected_duration_minutes": 5,
                    "key_vocabulary": action_words[:5]
                    if action_words
                    else ["hello", "start"],
                    "essential_phrases": [
                        f"Let's {prompt.lower()}",
                        "How do we start?",
                    ],
                    "learning_objectives": ["Initiate conversation"],
                    "success_criteria": ["Start conversation successfully"],
                    "cultural_notes": "",
                },
                {
                    "name": "Main Activity",
                    "description": f"Complete the {prompt.lower()} task",
                    "expected_duration_minutes": 8,
                    "key_vocabulary": action_words[5:10]
                    if len(action_words) > 5
                    else ["continue", "next"],
                    "essential_phrases": [
                        f"I would like to {prompt.lower()}",
                        "Can you help me?",
                    ],
                    "learning_objectives": ["Complete main task"],
                    "success_criteria": ["Task completed"],
                    "cultural_notes": "",
                },
                {
                    "name": "Conclusion",
                    "description": "Finish and reflect",
                    "expected_duration_minutes": 2,
                    "key_vocabulary": ["finish", "thank you", "goodbye"],
                    "essential_phrases": ["Thank you", "Goodbye"],
                    "learning_objectives": ["End conversation politely"],
                    "success_criteria": ["Polite conclusion"],
                    "cultural_notes": "",
                },
            ],
            "vocabulary_focus": action_words[:15] if action_words else [],
            "prerequisites": [f"basic_{category}_vocabulary"],
            "learning_outcomes": [f"Ability to {prompt.lower()}"],
            "ai_powered": False,
            "method": "template_based_fallback",
        }

    async def generate_cultural_notes(
        self,
        scenario_data: Dict[str, Any],
        tutor_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate culturally relevant notes for scenario

        Args:
            scenario_data: Scenario context
            tutor_profile: Tutor profile for tone/style

        Returns:
            {
                "cultural_notes": "Detailed cultural context",
                "etiquette_tips": ["tip1", "tip2", ...],
                "common_mistakes": ["mistake1", "mistake2", ...],
                "regional_variations": {"region": "variation", ...}
            }
        """
        if not self.ai_client:
            return self._fallback_cultural_notes(scenario_data)

        try:
            prompt = self._build_cultural_notes_prompt(scenario_data, tutor_profile)

            messages = [
                {
                    "role": "system",
                    "content": "You are a cultural anthropologist and language educator specializing in cross-cultural communication and etiquette.",
                },
                {"role": "user", "content": prompt},
            ]

            response = await self.ai_client.generate_response(
                messages=messages, temperature=0.5, max_tokens=1500
            )

            result = self._parse_cultural_notes_response(response.content)
            result["ai_powered"] = True

            logger.info(
                f"AI cultural notes generated for {scenario_data.get('category', 'unknown')} scenario"
            )

            return result

        except Exception as e:
            logger.error(f"AI cultural notes generation failed: {e}")
            fallback = self._fallback_cultural_notes(scenario_data)
            fallback["ai_powered"] = False
            fallback["error"] = str(e)
            return fallback

    def _build_cultural_notes_prompt(
        self, scenario_data: Dict[str, Any], tutor_profile: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for cultural notes generation"""

        title = scenario_data.get("title", "Untitled")
        category = scenario_data.get("category", "general")
        setting = scenario_data.get("setting", f"A {category} setting")
        difficulty = scenario_data.get("difficulty", "intermediate")

        tutor_context = ""
        if tutor_profile:
            style = tutor_profile.get("teaching_style", "balanced")
            tutor_context = f"\nTutor Style: {style} (adjust tone accordingly)"

        return f"""Generate cultural notes for this language learning scenario:

Title: {title}
Category: {category}
Setting: {setting}
Difficulty: {difficulty}{tutor_context}

Provide comprehensive cultural context including:

1. **Cultural Notes**: 2-3 paragraphs about cultural context, customs, and social norms
2. **Etiquette Tips**: 4-6 specific dos and don'ts
3. **Common Mistakes**: 3-5 mistakes learners often make
4. **Regional Variations**: How practices differ by region (if applicable)

Focus on practical, actionable insights. Be respectful and nuanced.

JSON format:
{{
  "cultural_notes": "Detailed 2-3 paragraph explanation...",
  "etiquette_tips": [
    "Tip 1: Specific actionable advice",
    "Tip 2: Another specific tip",
    ...
  ],
  "common_mistakes": [
    "Mistake 1: What to avoid and why",
    "Mistake 2: Another common error",
    ...
  ],
  "regional_variations": {{
    "Region 1": "How it differs here",
    "Region 2": "How it differs there"
  }},
  "sensitivity_notes": "Any cultural sensitivities to be aware of"
}}"""

    def _parse_cultural_notes_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI cultural notes response"""
        try:
            response_cleaned = ai_response.strip()

            if "```json" in response_cleaned:
                start = response_cleaned.find("```json") + 7
                end = response_cleaned.find("```", start)
                response_cleaned = response_cleaned[start:end].strip()
            elif "```" in response_cleaned:
                start = response_cleaned.find("```") + 3
                end = response_cleaned.find("```", start)
                response_cleaned = response_cleaned[start:end].strip()

            result = json.loads(response_cleaned)

            # Set defaults
            result.setdefault("cultural_notes", "")
            result.setdefault("etiquette_tips", [])
            result.setdefault("common_mistakes", [])
            result.setdefault("regional_variations", {})
            result.setdefault("sensitivity_notes", "")

            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse cultural notes: {e}")

            # Try to extract text sections
            return {
                "cultural_notes": ai_response[:500]
                if len(ai_response) > 500
                else ai_response,
                "etiquette_tips": [],
                "common_mistakes": [],
                "regional_variations": {},
                "sensitivity_notes": "",
                "parse_error": str(e),
            }

    def _fallback_cultural_notes(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback cultural notes by category"""

        category = scenario_data.get("category", "general")

        cultural_notes_bank = {
            "restaurant": {
                "cultural_notes": "Dining customs vary significantly across cultures. In many Western countries, tipping is expected (15-20%), while in some Asian countries it may be considered rude. Table manners, noise levels, and dining duration expectations also differ widely.",
                "etiquette_tips": [
                    "Wait to be seated in formal restaurants",
                    "Place napkin on lap when seated",
                    "Don't start eating until everyone is served",
                    "Use utensils from outside in",
                    "Signal you're finished by placing utensils together",
                ],
                "common_mistakes": [
                    "Tipping incorrectly or not at all",
                    "Speaking too loudly in quiet establishments",
                    "Not making eye contact with servers",
                    "Using phone at the table",
                ],
                "regional_variations": {
                    "USA": "15-20% tip expected, casual atmosphere common",
                    "France": "Service included, quiet dining preferred",
                    "Japan": "No tipping, slurping noodles acceptable",
                },
            },
            "travel": {
                "cultural_notes": "Travel customs and expectations vary by destination. Personal space, queuing behavior, and interaction with service staff differ across cultures. Understanding local norms helps avoid misunderstandings.",
                "etiquette_tips": [
                    "Research visa requirements in advance",
                    "Dress appropriately for the destination",
                    "Learn basic phrases in the local language",
                    "Respect local customs and religious sites",
                    "Keep important documents secure",
                ],
                "common_mistakes": [
                    "Not declaring items at customs",
                    "Assuming English is spoken everywhere",
                    "Ignoring local dress codes",
                    "Taking photos without permission",
                ],
                "regional_variations": {
                    "Europe": "Quiet public transport, formal greetings",
                    "Asia": "Remove shoes indoors, bow in greetings",
                    "Middle East": "Conservative dress, gender norms",
                },
            },
            "shopping": {
                "cultural_notes": "Shopping cultures range from fixed-price systems to bargaining traditions. Return policies, payment methods, and customer service expectations vary significantly.",
                "etiquette_tips": [
                    "Ask before touching items in some cultures",
                    "Bargaining is expected in some markets",
                    "Keep receipts for returns",
                    "Respect store hours and closing times",
                    "Be patient during busy periods",
                ],
                "common_mistakes": [
                    "Not bargaining where expected",
                    "Bargaining where prices are fixed",
                    "Not checking return policies",
                    "Assuming credit cards accepted everywhere",
                ],
                "regional_variations": {
                    "Markets": "Bargaining expected and enjoyed",
                    "Malls": "Fixed prices, Western-style service",
                    "Boutiques": "Personal service, appointments common",
                },
            },
            "business": {
                "cultural_notes": "Business culture varies from hierarchical to egalitarian, formal to casual. Understanding power distance, communication styles, and meeting protocols is essential for success.",
                "etiquette_tips": [
                    "Exchange business cards properly",
                    "Dress according to company culture",
                    "Be punctual for meetings",
                    "Follow up in writing after discussions",
                    "Respect hierarchy in formal cultures",
                ],
                "common_mistakes": [
                    "Being too casual in formal cultures",
                    "Interrupting senior colleagues",
                    "Not preparing adequately for meetings",
                    "Ignoring email etiquette norms",
                ],
                "regional_variations": {
                    "USA": "Casual, direct communication",
                    "Japan": "Formal, hierarchical, indirect",
                    "Germany": "Punctual, structured, efficient",
                },
            },
            "social": {
                "cultural_notes": "Social norms for greetings, personal space, conversation topics, and friendship development vary widely. What's friendly in one culture may be intrusive in another.",
                "etiquette_tips": [
                    "Learn appropriate greetings for the culture",
                    "Respect personal space boundaries",
                    "Avoid sensitive topics initially",
                    "Be mindful of eye contact norms",
                    "Follow host's lead at social events",
                ],
                "common_mistakes": [
                    "Being too familiar too quickly",
                    "Discussing taboo topics",
                    "Misunderstanding humor across cultures",
                    "Not reciprocating invitations",
                ],
                "regional_variations": {
                    "Latin America": "Warm, close contact, late arrivals OK",
                    "Northern Europe": "Reserved, punctual, personal space",
                    "Middle East": "Hospitable, gender-segregated events common",
                },
            },
        }

        notes = cultural_notes_bank.get(category, cultural_notes_bank["social"])

        return {
            **notes,
            "sensitivity_notes": "Cultural practices vary; these are general guidelines, not universal rules.",
            "ai_powered": False,
            "method": "category_based_fallback",
        }


# Singleton instance
_scenario_ai_service: Optional[ScenarioAIService] = None


def get_scenario_ai_service(ai_client=None) -> ScenarioAIService:
    """Get or create scenario AI service instance"""
    global _scenario_ai_service
    if _scenario_ai_service is None:
        _scenario_ai_service = ScenarioAIService(ai_client)
    return _scenario_ai_service
