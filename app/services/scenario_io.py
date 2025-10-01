"""
Scenario I/O Operations for AI Language Tutor App

This module handles all file I/O operations for scenarios including
loading from and saving to JSON files.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from .scenario_models import (
    ScenarioCategory,
    ScenarioDifficulty,
    ConversationRole,
    ScenarioPhase,
    ConversationScenario,
)

logger = logging.getLogger(__name__)


class ScenarioIO:
    """Handles scenario file I/O operations"""

    @staticmethod
    async def save_scenarios_to_file(scenarios: Dict[str, ConversationScenario]):
        """Save scenarios to JSON file for persistence"""
        try:
            data_dir = Path("data/scenarios")
            data_dir.mkdir(parents=True, exist_ok=True)
            scenarios_file = data_dir / "scenarios.json"

            # Convert scenarios to serializable format
            scenarios_data = {}
            for scenario_id, scenario in scenarios.items():
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

    @staticmethod
    async def load_scenarios_from_file() -> Dict[str, ConversationScenario]:
        """Load scenarios from JSON file"""
        scenarios = {}

        try:
            scenarios_file = Path("data/scenarios/scenarios.json")
            if not scenarios_file.exists():
                logger.info(
                    "No saved scenarios file found, starting with predefined scenarios only"
                )
                return scenarios

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
                scenarios[scenario_id] = scenario

            logger.info(f"Loaded {len(scenarios_data)} scenarios from file")

        except Exception as e:
            logger.error(f"Error loading scenarios from file: {str(e)}")

        return scenarios
