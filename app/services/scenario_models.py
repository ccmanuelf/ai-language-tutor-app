"""
Data models and structures for scenario-based conversations.

This module contains all enums, dataclasses, and data structures used
throughout the scenario management system.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass


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
    learning_goals: List[str] = None
    learning_outcomes: List[str] = None
    prerequisites: List[str] = None

    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.learning_outcomes is None:
            self.learning_outcomes = []
        if self.learning_goals is None:
            self.learning_goals = []


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
    scenario_variations: List[Dict[str, Any]] = None
    difficulty_modifiers: Dict[str, Dict[str, Any]] = None
    success_metrics: List[str] = None

    def __post_init__(self):
        if self.scenario_variations is None:
            self.scenario_variations = []
        if self.difficulty_modifiers is None:
            self.difficulty_modifiers = {}
        if self.success_metrics is None:
            self.success_metrics = []
