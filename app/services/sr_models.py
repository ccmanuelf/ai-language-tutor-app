"""
Data models for Spaced Repetition system
Defines enums and dataclasses used across SR modules
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ItemType(Enum):
    """Types of learning items for spaced repetition"""

    VOCABULARY = "vocabulary"
    PHRASE = "phrase"
    GRAMMAR = "grammar"
    PRONUNCIATION = "pronunciation"


class SessionType(Enum):
    """Types of learning sessions"""

    VOCABULARY = "vocabulary"
    CONVERSATION = "conversation"
    TUTOR_MODE = "tutor_mode"
    SCENARIO = "scenario"
    CONTENT_REVIEW = "content_review"


class ReviewResult(Enum):
    """Results of item review (SM-2 algorithm grades)"""

    AGAIN = 0  # Incorrect, review again soon
    HARD = 1  # Correct but difficult
    GOOD = 2  # Correct with normal effort
    EASY = 3  # Correct and easy


class AchievementType(Enum):
    """Types of achievements for gamification"""

    STREAK = "streak"
    VOCABULARY = "vocabulary"
    CONVERSATION = "conversation"
    GOAL = "goal"
    MASTERY = "mastery"
    DEDICATION = "dedication"


@dataclass
class SpacedRepetitionItem:
    """
    Data class for spaced repetition items
    Implements SM-2 algorithm data structure
    """

    item_id: str
    user_id: int
    language_code: str
    item_type: str
    content: str
    translation: str = ""
    definition: str = ""
    pronunciation_guide: str = ""
    example_usage: str = ""
    context_tags: List[str] = None
    difficulty_level: int = 1
    ease_factor: float = 2.5
    repetition_number: int = 0
    interval_days: int = 1
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    total_reviews: int = 0
    correct_reviews: int = 0
    incorrect_reviews: int = 0
    streak_count: int = 0
    mastery_level: float = 0.0
    confidence_score: float = 0.0
    first_seen_date: datetime = None
    last_studied_date: Optional[datetime] = None
    average_response_time_ms: int = 0
    learning_speed_factor: float = 1.0
    retention_rate: float = 0.0
    source_session_id: str = ""
    source_content: str = ""
    metadata: Dict = None
    is_active: bool = True

    def __post_init__(self):
        if self.context_tags is None:
            self.context_tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.first_seen_date is None:
            self.first_seen_date = datetime.now()


@dataclass
class LearningSession:
    """Data class for learning sessions"""

    session_id: str
    user_id: int
    language_code: str
    session_type: str
    mode_specific_data: Dict = None
    duration_minutes: int = 0
    items_studied: int = 0
    items_correct: int = 0
    items_incorrect: int = 0
    accuracy_percentage: float = 0.0
    average_response_time_ms: int = 0
    confidence_score: float = 0.0
    engagement_score: float = 0.0
    difficulty_level: int = 1
    new_items_learned: int = 0
    items_reviewed: int = 0
    streak_contributions: int = 0
    goal_progress: float = 0.0
    content_source: str = ""
    ai_model_used: str = ""
    tutor_mode: str = ""
    scenario_id: str = ""
    started_at: datetime = None
    ended_at: Optional[datetime] = None

    def __post_init__(self):
        if self.mode_specific_data is None:
            self.mode_specific_data = {}
        if self.started_at is None:
            self.started_at = datetime.now()


@dataclass
class LearningGoal:
    """Data class for learning goals"""

    goal_id: str
    user_id: int
    language_code: str
    goal_type: str
    title: str
    description: str
    target_value: float
    current_value: float = 0.0
    unit: str = "items"
    difficulty_level: int = 2
    priority: int = 2
    is_daily: bool = False
    is_weekly: bool = False
    is_monthly: bool = False
    is_custom: bool = True
    progress_percentage: float = 0.0
    milestones_reached: int = 0
    total_milestones: int = 5
    last_progress_update: Optional[datetime] = None
    start_date: datetime = None
    target_date: datetime = None
    completed_date: Optional[datetime] = None
    status: str = "active"

    def __post_init__(self):
        if self.start_date is None:
            self.start_date = datetime.now()
        if self.target_date is None:
            self.target_date = datetime.now() + timedelta(days=30)
