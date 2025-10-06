"""
Progress Analytics Service
Task 3.1.8 - Enhanced Progress Analytics Dashboard

Advanced progress analytics service complementing the existing Learning Analytics Dashboard
with sophisticated tracking capabilities inspired by Airlearn AI and Pingo AI. This service
focuses on enhancement rather than duplication of existing functionality.

Features:
- Enhanced spaced repetition analytics with smart scheduling insights
- Real-time conversation progress tracking with confidence metrics
- Daily goals, streaks, and achievement system integration
- Multi-skill progress visualization (speaking, listening, pronunciation)
- Personalized learning path adjustment recommendations
- Advanced memory retention analytics and active recall metrics
- Performance comparison and improvement trend analysis
"""

import json
import logging
import sqlite3
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

# Register SQLite datetime adapters for Python 3.12+ compatibility
from app.utils.sqlite_adapters import register_sqlite_adapters

register_sqlite_adapters()

from app.services.spaced_repetition_manager import (  # noqa: E402 - Required after logger configuration
    SpacedRepetitionManager,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_mean(values: List[Union[int, float]], default: float = 0.0) -> float:
    """Safely calculate mean, returning default if empty list"""
    if not values:
        return default
    return statistics.mean(values)


class SkillType(Enum):
    """Types of language skills tracked"""

    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"
    LISTENING = "listening"
    SPEAKING = "speaking"
    PRONUNCIATION = "pronunciation"
    CONVERSATION = "conversation"
    COMPREHENSION = "comprehension"
    WRITING = "writing"


class LearningPathType(Enum):
    """Types of learning paths"""

    BEGINNER_FOUNDATION = "beginner_foundation"
    CONVERSATION_FOCUSED = "conversation_focused"
    VOCABULARY_INTENSIVE = "vocabulary_intensive"
    GRAMMAR_MASTERY = "grammar_mastery"
    PRONUNCIATION_PERFECTION = "pronunciation_perfection"
    COMPREHENSIVE_BALANCED = "comprehensive_balanced"
    RAPID_PROGRESS = "rapid_progress"
    RETENTION_FOCUSED = "retention_focused"


class ConfidenceLevel(Enum):
    """Confidence levels for responses"""

    VERY_LOW = "very_low"  # 0.0 - 0.2
    LOW = "low"  # 0.2 - 0.4
    MODERATE = "moderate"  # 0.4 - 0.6
    HIGH = "high"  # 0.6 - 0.8
    VERY_HIGH = "very_high"  # 0.8 - 1.0


@dataclass
class ConversationMetrics:
    """Comprehensive conversation performance metrics"""

    session_id: str
    user_id: int
    language_code: str
    conversation_type: str  # scenario, tutor_mode, free_form
    scenario_id: Optional[str] = None
    tutor_mode: Optional[str] = None

    # Basic metrics
    duration_minutes: float = 0.0
    total_exchanges: int = 0
    user_turns: int = 0
    ai_turns: int = 0

    # Language metrics
    words_spoken: int = 0
    unique_words_used: int = 0
    vocabulary_complexity_score: float = 0.0
    grammar_accuracy_score: float = 0.0
    pronunciation_clarity_score: float = 0.0
    fluency_score: float = 0.0

    # Confidence and engagement
    average_confidence_score: float = 0.0
    confidence_distribution: Dict[str, int] = None
    engagement_score: float = 0.0
    hesitation_count: int = 0
    self_correction_count: int = 0

    # Learning outcomes
    new_vocabulary_encountered: int = 0
    grammar_patterns_practiced: int = 0
    cultural_context_learned: int = 0
    learning_objectives_met: List[str] = None

    # Comparison metrics
    improvement_from_last_session: float = 0.0
    peer_comparison_percentile: float = 0.0

    # Timestamps
    started_at: datetime = None
    ended_at: Optional[datetime] = None

    def __post_init__(self):
        if self.confidence_distribution is None:
            self.confidence_distribution = {}
        if self.learning_objectives_met is None:
            self.learning_objectives_met = []
        if self.started_at is None:
            self.started_at = datetime.now()


@dataclass
class SkillProgressMetrics:
    """Multi-skill progress tracking"""

    user_id: int
    language_code: str
    skill_type: str

    # Current status
    current_level: float = 0.0  # 0.0 - 100.0
    mastery_percentage: float = 0.0
    confidence_level: str = "moderate"

    # Progress tracking
    initial_assessment_score: float = 0.0
    latest_assessment_score: float = 0.0
    total_improvement: float = 0.0
    improvement_rate: float = 0.0  # improvement per week

    # Practice statistics
    total_practice_sessions: int = 0
    total_practice_time_minutes: int = 0
    average_session_performance: float = 0.0
    consistency_score: float = 0.0  # how regularly they practice

    # Difficulty analysis
    easy_items_percentage: float = 0.0
    moderate_items_percentage: float = 0.0
    hard_items_percentage: float = 0.0
    challenge_comfort_level: float = 0.0

    # Retention metrics
    retention_rate: float = 0.0
    forgetting_curve_analysis: Dict[str, float] = None
    optimal_review_intervals: Dict[str, int] = None

    # Recommendations
    recommended_focus_areas: List[str] = None
    suggested_exercises: List[str] = None
    next_milestone_target: Optional[str] = None

    # Timestamps
    last_updated: datetime = None
    next_assessment_due: Optional[datetime] = None

    def __post_init__(self):
        if self.forgetting_curve_analysis is None:
            self.forgetting_curve_analysis = {}
        if self.optimal_review_intervals is None:
            self.optimal_review_intervals = {}
        if self.recommended_focus_areas is None:
            self.recommended_focus_areas = []
        if self.suggested_exercises is None:
            self.suggested_exercises = []
        if self.last_updated is None:
            self.last_updated = datetime.now()


@dataclass
class LearningPathRecommendation:
    """Personalized learning path recommendations"""

    user_id: int
    language_code: str
    recommendation_id: str

    # Path details
    recommended_path_type: str
    path_title: str
    path_description: str
    estimated_duration_weeks: int = 12
    difficulty_level: int = 2  # 1=easy, 2=moderate, 3=challenging

    # Rationale
    recommendation_reasons: List[str] = None
    user_strengths: List[str] = None
    user_weaknesses: List[str] = None
    learning_style_preferences: List[str] = None

    # Goals and milestones
    primary_goals: List[str] = None
    weekly_milestones: List[str] = None
    success_metrics: List[str] = None

    # Personalization
    time_commitment_hours_per_week: float = 5.0
    preferred_session_length_minutes: int = 30
    optimal_practice_times: List[str] = None

    # Progress tracking
    confidence_score: float = 0.0
    expected_success_rate: float = 0.0
    adaptation_triggers: List[str] = None

    # Timestamps
    generated_at: datetime = None
    expires_at: Optional[datetime] = None

    def __post_init__(self):
        if self.recommendation_reasons is None:
            self.recommendation_reasons = []
        if self.user_strengths is None:
            self.user_strengths = []
        if self.user_weaknesses is None:
            self.user_weaknesses = []
        if self.learning_style_preferences is None:
            self.learning_style_preferences = []
        if self.primary_goals is None:
            self.primary_goals = []
        if self.weekly_milestones is None:
            self.weekly_milestones = []
        if self.success_metrics is None:
            self.success_metrics = []
        if self.optimal_practice_times is None:
            self.optimal_practice_times = []
        if self.adaptation_triggers is None:
            self.adaptation_triggers = []
        if self.generated_at is None:
            self.generated_at = datetime.now()
        if self.expires_at is None:
            self.expires_at = datetime.now() + timedelta(weeks=4)


@dataclass
class MemoryRetentionAnalysis:
    """Advanced memory retention and active recall analytics"""

    user_id: int
    language_code: str
    analysis_period_days: int = 30

    # Retention curves
    short_term_retention_rate: float = 0.0  # 1-7 days
    medium_term_retention_rate: float = 0.0  # 1-4 weeks
    long_term_retention_rate: float = 0.0  # 1+ months

    # Active recall effectiveness
    active_recall_success_rate: float = 0.0
    passive_review_success_rate: float = 0.0
    recall_vs_recognition_ratio: float = 0.0

    # Forgetting patterns
    forgetting_curve_steepness: float = 0.0
    optimal_review_timing: Dict[str, float] = None
    interference_patterns: List[str] = None

    # Item-specific analysis
    most_retained_item_types: List[str] = None
    least_retained_item_types: List[str] = None
    retention_by_difficulty: Dict[str, float] = None
    retention_by_context: Dict[str, float] = None

    # Learning efficiency
    average_exposures_to_master: float = 0.0
    efficiency_compared_to_peers: float = 0.0
    learning_velocity: float = 0.0  # items mastered per hour

    # Recommendations
    optimal_study_schedule: Dict[str, List[str]] = None
    retention_improvement_strategies: List[str] = None

    # Timestamps
    analysis_date: datetime = None
    next_analysis_due: Optional[datetime] = None

    def __post_init__(self):
        if self.optimal_review_timing is None:
            self.optimal_review_timing = {}
        if self.interference_patterns is None:
            self.interference_patterns = []
        if self.most_retained_item_types is None:
            self.most_retained_item_types = []
        if self.least_retained_item_types is None:
            self.least_retained_item_types = []
        if self.retention_by_difficulty is None:
            self.retention_by_difficulty = {}
        if self.retention_by_context is None:
            self.retention_by_context = {}
        if self.optimal_study_schedule is None:
            self.optimal_study_schedule = {}
        if self.retention_improvement_strategies is None:
            self.retention_improvement_strategies = []
        if self.analysis_date is None:
            self.analysis_date = datetime.now()


class ProgressAnalyticsService:
    """Enhanced Progress Analytics Service - Task 3.1.8 Implementation"""

    def __init__(self, db_path: str = "data/ai_language_tutor.db"):
        self.db_path = db_path
        # Integrate with existing spaced repetition manager
        self.sr_manager = SpacedRepetitionManager(db_path)

        # Initialize enhancement tables
        self._initialize_enhanced_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_enhanced_tables(self):
        """Initialize additional tables for enhanced progress analytics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Conversation metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_metrics (
                        session_id TEXT PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        language_code TEXT NOT NULL,
                        conversation_type TEXT NOT NULL,
                        scenario_id TEXT,
                        tutor_mode TEXT,
                        duration_minutes REAL DEFAULT 0.0,
                        total_exchanges INTEGER DEFAULT 0,
                        user_turns INTEGER DEFAULT 0,
                        ai_turns INTEGER DEFAULT 0,
                        words_spoken INTEGER DEFAULT 0,
                        unique_words_used INTEGER DEFAULT 0,
                        vocabulary_complexity_score REAL DEFAULT 0.0,
                        grammar_accuracy_score REAL DEFAULT 0.0,
                        pronunciation_clarity_score REAL DEFAULT 0.0,
                        fluency_score REAL DEFAULT 0.0,
                        average_confidence_score REAL DEFAULT 0.0,
                        confidence_distribution TEXT DEFAULT '{}',
                        engagement_score REAL DEFAULT 0.0,
                        hesitation_count INTEGER DEFAULT 0,
                        self_correction_count INTEGER DEFAULT 0,
                        new_vocabulary_encountered INTEGER DEFAULT 0,
                        grammar_patterns_practiced INTEGER DEFAULT 0,
                        cultural_context_learned INTEGER DEFAULT 0,
                        learning_objectives_met TEXT DEFAULT '[]',
                        improvement_from_last_session REAL DEFAULT 0.0,
                        peer_comparison_percentile REAL DEFAULT 0.0,
                        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        ended_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Skill progress metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS skill_progress_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        language_code TEXT NOT NULL,
                        skill_type TEXT NOT NULL,
                        current_level REAL DEFAULT 0.0,
                        mastery_percentage REAL DEFAULT 0.0,
                        confidence_level TEXT DEFAULT 'moderate',
                        initial_assessment_score REAL DEFAULT 0.0,
                        latest_assessment_score REAL DEFAULT 0.0,
                        total_improvement REAL DEFAULT 0.0,
                        improvement_rate REAL DEFAULT 0.0,
                        total_practice_sessions INTEGER DEFAULT 0,
                        total_practice_time_minutes INTEGER DEFAULT 0,
                        average_session_performance REAL DEFAULT 0.0,
                        consistency_score REAL DEFAULT 0.0,
                        easy_items_percentage REAL DEFAULT 0.0,
                        moderate_items_percentage REAL DEFAULT 0.0,
                        hard_items_percentage REAL DEFAULT 0.0,
                        challenge_comfort_level REAL DEFAULT 0.0,
                        retention_rate REAL DEFAULT 0.0,
                        forgetting_curve_analysis TEXT DEFAULT '{}',
                        optimal_review_intervals TEXT DEFAULT '{}',
                        recommended_focus_areas TEXT DEFAULT '[]',
                        suggested_exercises TEXT DEFAULT '[]',
                        next_milestone_target TEXT,
                        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                        next_assessment_due DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, language_code, skill_type)
                    )
                """)

                # Learning path recommendations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learning_path_recommendations (
                        recommendation_id TEXT PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        language_code TEXT NOT NULL,
                        recommended_path_type TEXT NOT NULL,
                        path_title TEXT NOT NULL,
                        path_description TEXT,
                        estimated_duration_weeks INTEGER DEFAULT 12,
                        difficulty_level INTEGER DEFAULT 2,
                        recommendation_reasons TEXT DEFAULT '[]',
                        user_strengths TEXT DEFAULT '[]',
                        user_weaknesses TEXT DEFAULT '[]',
                        learning_style_preferences TEXT DEFAULT '[]',
                        primary_goals TEXT DEFAULT '[]',
                        weekly_milestones TEXT DEFAULT '[]',
                        success_metrics TEXT DEFAULT '[]',
                        time_commitment_hours_per_week REAL DEFAULT 5.0,
                        preferred_session_length_minutes INTEGER DEFAULT 30,
                        optimal_practice_times TEXT DEFAULT '[]',
                        confidence_score REAL DEFAULT 0.0,
                        expected_success_rate REAL DEFAULT 0.0,
                        adaptation_triggers TEXT DEFAULT '[]',
                        generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        expires_at DATETIME,
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Memory retention analysis table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory_retention_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        language_code TEXT NOT NULL,
                        analysis_period_days INTEGER DEFAULT 30,
                        short_term_retention_rate REAL DEFAULT 0.0,
                        medium_term_retention_rate REAL DEFAULT 0.0,
                        long_term_retention_rate REAL DEFAULT 0.0,
                        active_recall_success_rate REAL DEFAULT 0.0,
                        passive_review_success_rate REAL DEFAULT 0.0,
                        recall_vs_recognition_ratio REAL DEFAULT 0.0,
                        forgetting_curve_steepness REAL DEFAULT 0.0,
                        optimal_review_timing TEXT DEFAULT '{}',
                        interference_patterns TEXT DEFAULT '[]',
                        most_retained_item_types TEXT DEFAULT '[]',
                        least_retained_item_types TEXT DEFAULT '[]',
                        retention_by_difficulty TEXT DEFAULT '{}',
                        retention_by_context TEXT DEFAULT '{}',
                        average_exposures_to_master REAL DEFAULT 0.0,
                        efficiency_compared_to_peers REAL DEFAULT 0.0,
                        learning_velocity REAL DEFAULT 0.0,
                        optimal_study_schedule TEXT DEFAULT '{}',
                        retention_improvement_strategies TEXT DEFAULT '[]',
                        analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        next_analysis_due DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, language_code, analysis_date)
                    )
                """)

                conn.commit()
                logger.info(
                    "Enhanced progress analytics tables initialized successfully"
                )

        except Exception as e:
            logger.error(f"Error initializing enhanced tables: {e}")
            raise

    # ============= CONVERSATION ANALYTICS =============

    def track_conversation_session(self, metrics: ConversationMetrics) -> bool:
        """Track comprehensive conversation session metrics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO conversation_metrics (
                        session_id, user_id, language_code, conversation_type, scenario_id,
                        tutor_mode, duration_minutes, total_exchanges, user_turns, ai_turns,
                        words_spoken, unique_words_used, vocabulary_complexity_score,
                        grammar_accuracy_score, pronunciation_clarity_score, fluency_score,
                        average_confidence_score, confidence_distribution, engagement_score,
                        hesitation_count, self_correction_count, new_vocabulary_encountered,
                        grammar_patterns_practiced, cultural_context_learned, learning_objectives_met,
                        improvement_from_last_session, peer_comparison_percentile,
                        started_at, ended_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metrics.session_id,
                        metrics.user_id,
                        metrics.language_code,
                        metrics.conversation_type,
                        metrics.scenario_id,
                        metrics.tutor_mode,
                        metrics.duration_minutes,
                        metrics.total_exchanges,
                        metrics.user_turns,
                        metrics.ai_turns,
                        metrics.words_spoken,
                        metrics.unique_words_used,
                        metrics.vocabulary_complexity_score,
                        metrics.grammar_accuracy_score,
                        metrics.pronunciation_clarity_score,
                        metrics.fluency_score,
                        metrics.average_confidence_score,
                        json.dumps(metrics.confidence_distribution),
                        metrics.engagement_score,
                        metrics.hesitation_count,
                        metrics.self_correction_count,
                        metrics.new_vocabulary_encountered,
                        metrics.grammar_patterns_practiced,
                        metrics.cultural_context_learned,
                        json.dumps(metrics.learning_objectives_met),
                        metrics.improvement_from_last_session,
                        metrics.peer_comparison_percentile,
                        metrics.started_at,
                        metrics.ended_at,
                    ),
                )

                conn.commit()
                logger.info(
                    f"Conversation metrics tracked for session {metrics.session_id}"
                )
                return True

        except Exception as e:
            logger.error(f"Error tracking conversation session: {e}")
            return False

    def get_conversation_analytics(
        self, user_id: int, language_code: str, period_days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive conversation analytics for a user"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Date range for analysis
                end_date = datetime.now()
                start_date = end_date - timedelta(days=period_days)

                # Get conversation sessions
                cursor.execute(
                    """
                    SELECT * FROM conversation_metrics
                    WHERE user_id = ? AND language_code = ?
                    AND started_at BETWEEN ? AND ?
                    ORDER BY started_at DESC
                """,
                    (user_id, language_code, start_date, end_date),
                )

                sessions = [dict(row) for row in cursor.fetchall()]

                if not sessions:
                    return self._get_empty_conversation_analytics()

                # Calculate analytics
                analytics = {
                    "overview": {
                        "total_conversations": len(sessions),
                        "total_conversation_time": sum(
                            s["duration_minutes"] for s in sessions
                        ),
                        "average_session_length": safe_mean(
                            [
                                s["duration_minutes"]
                                for s in sessions
                                if s["duration_minutes"] > 0
                            ]
                        ),
                        "total_exchanges": sum(s["total_exchanges"] for s in sessions),
                        "average_exchanges_per_session": safe_mean(
                            [
                                s["total_exchanges"]
                                for s in sessions
                                if s["total_exchanges"] > 0
                            ]
                        ),
                    },
                    "performance_metrics": {
                        "average_fluency_score": safe_mean(
                            [
                                s["fluency_score"]
                                for s in sessions
                                if s["fluency_score"] > 0
                            ]
                        ),
                        "average_grammar_accuracy": safe_mean(
                            [
                                s["grammar_accuracy_score"]
                                for s in sessions
                                if s["grammar_accuracy_score"] > 0
                            ]
                        ),
                        "average_pronunciation_clarity": safe_mean(
                            [
                                s["pronunciation_clarity_score"]
                                for s in sessions
                                if s["pronunciation_clarity_score"] > 0
                            ]
                        ),
                        "average_vocabulary_complexity": safe_mean(
                            [
                                s["vocabulary_complexity_score"]
                                for s in sessions
                                if s["vocabulary_complexity_score"] > 0
                            ]
                        ),
                        "average_confidence_level": safe_mean(
                            [
                                s["average_confidence_score"]
                                for s in sessions
                                if s["average_confidence_score"] > 0
                            ]
                        ),
                    },
                    "learning_progress": {
                        "total_new_vocabulary": sum(
                            s["new_vocabulary_encountered"] for s in sessions
                        ),
                        "total_grammar_patterns": sum(
                            s["grammar_patterns_practiced"] for s in sessions
                        ),
                        "total_cultural_contexts": sum(
                            s["cultural_context_learned"] for s in sessions
                        ),
                        "average_improvement_trend": safe_mean(
                            [
                                s["improvement_from_last_session"]
                                for s in sessions
                                if s["improvement_from_last_session"] != 0
                            ]
                        ),
                    },
                    "engagement_analysis": {
                        "average_engagement_score": safe_mean(
                            [
                                s["engagement_score"]
                                for s in sessions
                                if s["engagement_score"] > 0
                            ]
                        ),
                        "total_hesitations": sum(
                            s["hesitation_count"] for s in sessions
                        ),
                        "total_self_corrections": sum(
                            s["self_correction_count"] for s in sessions
                        ),
                        "hesitation_rate": sum(s["hesitation_count"] for s in sessions)
                        / sum(s["total_exchanges"] for s in sessions)
                        if sum(s["total_exchanges"] for s in sessions) > 0
                        else 0,
                    },
                    "trends": self._calculate_conversation_trends(sessions),
                    "recommendations": self._generate_conversation_recommendations(
                        sessions
                    ),
                    "recent_sessions": sessions[:5],  # Most recent 5 sessions
                }

                return analytics

        except Exception as e:
            logger.error(f"Error getting conversation analytics: {e}")
            return self._get_empty_conversation_analytics()

    def _get_empty_conversation_analytics(self) -> Dict[str, Any]:
        """Return empty conversation analytics structure"""
        return {
            "overview": {
                "total_conversations": 0,
                "total_conversation_time": 0,
                "average_session_length": 0,
                "total_exchanges": 0,
                "average_exchanges_per_session": 0,
            },
            "performance_metrics": {
                "average_fluency_score": 0,
                "average_grammar_accuracy": 0,
                "average_pronunciation_clarity": 0,
                "average_vocabulary_complexity": 0,
                "average_confidence_level": 0,
            },
            "learning_progress": {
                "total_new_vocabulary": 0,
                "total_grammar_patterns": 0,
                "total_cultural_contexts": 0,
                "average_improvement_trend": 0,
            },
            "engagement_analysis": {
                "average_engagement_score": 0,
                "total_hesitations": 0,
                "total_self_corrections": 0,
                "hesitation_rate": 0,
            },
            "trends": {},
            "recommendations": [],
            "recent_sessions": [],
        }

    def _calculate_conversation_trends(self, sessions: List[Dict]) -> Dict[str, Any]:
        """Calculate conversation performance trends"""
        if len(sessions) < 2:
            return {}

        # Sort by date for trend analysis
        sorted_sessions = sorted(sessions, key=lambda x: x["started_at"])

        # Calculate trends for key metrics
        fluency_scores = [
            s["fluency_score"] for s in sorted_sessions if s["fluency_score"] > 0
        ]
        confidence_scores = [
            s["average_confidence_score"]
            for s in sorted_sessions
            if s["average_confidence_score"] > 0
        ]
        vocabulary_scores = [
            s["vocabulary_complexity_score"]
            for s in sorted_sessions
            if s["vocabulary_complexity_score"] > 0
        ]

        trends = {}

        # Fluency trend
        if len(fluency_scores) >= 2:
            trends["fluency_trend"] = self._calculate_linear_trend(fluency_scores)

        # Confidence trend
        if len(confidence_scores) >= 2:
            trends["confidence_trend"] = self._calculate_linear_trend(confidence_scores)

        # Vocabulary complexity trend
        if len(vocabulary_scores) >= 2:
            trends["vocabulary_trend"] = self._calculate_linear_trend(vocabulary_scores)

        return trends

    def _calculate_linear_trend(self, values: List[float]) -> Dict[str, float]:
        """Calculate linear trend for a series of values"""
        if len(values) < 2:
            return {"slope": 0.0, "direction": "stable"}

        n = len(values)
        x_values = list(range(n))

        # Calculate linear regression slope
        x_mean = safe_mean(x_values)
        y_mean = safe_mean(values)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        slope = numerator / denominator if denominator != 0 else 0.0

        # Determine trend direction
        if slope > 0.1:
            direction = "improving"
        elif slope < -0.1:
            direction = "declining"
        else:
            direction = "stable"

        return {"slope": slope, "direction": direction}

    def _generate_conversation_recommendations(self, sessions: List[Dict]) -> List[str]:
        """Generate personalized conversation recommendations"""
        if not sessions:
            return ["Start having conversations to get personalized recommendations!"]

        recommendations = []
        latest_session = sessions[0]  # Most recent session

        # Fluency recommendations
        if latest_session["fluency_score"] < 0.6:
            recommendations.append(
                "Focus on speaking more smoothly - try reading aloud daily to improve fluency"
            )

        # Confidence recommendations
        if latest_session["average_confidence_score"] < 0.5:
            recommendations.append(
                "Build confidence by practicing with easier topics before advancing to complex conversations"
            )

        # Grammar recommendations
        if latest_session["grammar_accuracy_score"] < 0.7:
            recommendations.append(
                "Review grammar fundamentals - your accuracy could improve with focused practice"
            )

        # Pronunciation recommendations
        if latest_session["pronunciation_clarity_score"] < 0.6:
            recommendations.append(
                "Work on pronunciation clarity - try listening to native speakers and repeating phrases"
            )

        # Vocabulary recommendations
        if latest_session["vocabulary_complexity_score"] < 0.5:
            recommendations.append(
                "Expand your vocabulary by learning 5-10 new words daily and using them in conversations"
            )

        # Engagement recommendations
        if latest_session["engagement_score"] < 0.6:
            recommendations.append(
                "Try different conversation topics to maintain higher engagement levels"
            )

        # Hesitation recommendations
        hesitation_rate = latest_session["hesitation_count"] / max(
            latest_session["total_exchanges"], 1
        )
        if hesitation_rate > 0.3:
            recommendations.append(
                "Practice common phrases to reduce hesitations during conversations"
            )

        # Default recommendation if performance is good
        if not recommendations:
            recommendations.append(
                "Excellent conversation skills! Try more challenging scenarios to continue growing"
            )

        return recommendations[:5]  # Limit to top 5 recommendations

    # ============= MULTI-SKILL PROGRESS TRACKING =============

    def update_skill_progress(self, skill_metrics: SkillProgressMetrics) -> bool:
        """Update comprehensive skill progress metrics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO skill_progress_metrics (
                        user_id, language_code, skill_type, current_level, mastery_percentage,
                        confidence_level, initial_assessment_score, latest_assessment_score,
                        total_improvement, improvement_rate, total_practice_sessions,
                        total_practice_time_minutes, average_session_performance, consistency_score,
                        easy_items_percentage, moderate_items_percentage, hard_items_percentage,
                        challenge_comfort_level, retention_rate, forgetting_curve_analysis,
                        optimal_review_intervals, recommended_focus_areas, suggested_exercises,
                        next_milestone_target, last_updated, next_assessment_due
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        skill_metrics.user_id,
                        skill_metrics.language_code,
                        skill_metrics.skill_type,
                        skill_metrics.current_level,
                        skill_metrics.mastery_percentage,
                        skill_metrics.confidence_level,
                        skill_metrics.initial_assessment_score,
                        skill_metrics.latest_assessment_score,
                        skill_metrics.total_improvement,
                        skill_metrics.improvement_rate,
                        skill_metrics.total_practice_sessions,
                        skill_metrics.total_practice_time_minutes,
                        skill_metrics.average_session_performance,
                        skill_metrics.consistency_score,
                        skill_metrics.easy_items_percentage,
                        skill_metrics.moderate_items_percentage,
                        skill_metrics.hard_items_percentage,
                        skill_metrics.challenge_comfort_level,
                        skill_metrics.retention_rate,
                        json.dumps(skill_metrics.forgetting_curve_analysis),
                        json.dumps(skill_metrics.optimal_review_intervals),
                        json.dumps(skill_metrics.recommended_focus_areas),
                        json.dumps(skill_metrics.suggested_exercises),
                        skill_metrics.next_milestone_target,
                        skill_metrics.last_updated,
                        skill_metrics.next_assessment_due,
                    ),
                )

                conn.commit()
                logger.info(f"Skill progress updated for {skill_metrics.skill_type}")
                return True

        except Exception as e:
            logger.error(f"Error updating skill progress: {e}")
            return False

    def get_multi_skill_analytics(
        self, user_id: int, language_code: str
    ) -> Dict[str, Any]:
        """Get comprehensive multi-skill progress analytics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM skill_progress_metrics
                    WHERE user_id = ? AND language_code = ?
                    ORDER BY current_level DESC
                """,
                    (user_id, language_code),
                )

                skills = [dict(row) for row in cursor.fetchall()]

                if not skills:
                    return self._get_empty_skill_analytics()

                # Parse JSON fields
                for skill in skills:
                    skill["forgetting_curve_analysis"] = json.loads(
                        skill.get("forgetting_curve_analysis", "{}")
                    )
                    skill["optimal_review_intervals"] = json.loads(
                        skill.get("optimal_review_intervals", "{}")
                    )
                    skill["recommended_focus_areas"] = json.loads(
                        skill.get("recommended_focus_areas", "[]")
                    )
                    skill["suggested_exercises"] = json.loads(
                        skill.get("suggested_exercises", "[]")
                    )

                # Calculate overall analytics
                analytics = {
                    "skill_overview": {
                        "total_skills_tracked": len(skills),
                        "average_skill_level": safe_mean(
                            [s["current_level"] for s in skills]
                        ),
                        "overall_mastery_percentage": safe_mean(
                            [s["mastery_percentage"] for s in skills]
                        ),
                        "strongest_skill": max(
                            skills, key=lambda x: x["current_level"]
                        )["skill_type"]
                        if skills
                        else None,
                        "weakest_skill": min(skills, key=lambda x: x["current_level"])[
                            "skill_type"
                        ]
                        if skills
                        else None,
                    },
                    "progress_trends": {
                        "average_improvement_rate": safe_mean(
                            [
                                s["improvement_rate"]
                                for s in skills
                                if s["improvement_rate"] > 0
                            ]
                        ),
                        "total_practice_time": sum(
                            s["total_practice_time_minutes"] for s in skills
                        ),
                        "average_consistency_score": safe_mean(
                            [s["consistency_score"] for s in skills]
                        ),
                        "skills_improving": len(
                            [s for s in skills if s["improvement_rate"] > 0]
                        ),
                        "skills_stable": len(
                            [s for s in skills if s["improvement_rate"] == 0]
                        ),
                        "skills_declining": len(
                            [s for s in skills if s["improvement_rate"] < 0]
                        ),
                    },
                    "difficulty_analysis": {
                        "comfort_with_easy_items": safe_mean(
                            [s["easy_items_percentage"] for s in skills]
                        ),
                        "comfort_with_moderate_items": safe_mean(
                            [s["moderate_items_percentage"] for s in skills]
                        ),
                        "comfort_with_hard_items": safe_mean(
                            [s["hard_items_percentage"] for s in skills]
                        ),
                        "average_challenge_comfort": safe_mean(
                            [s["challenge_comfort_level"] for s in skills]
                        ),
                    },
                    "retention_performance": {
                        "average_retention_rate": safe_mean(
                            [s["retention_rate"] for s in skills]
                        ),
                        "skills_with_good_retention": len(
                            [s for s in skills if s["retention_rate"] > 0.7]
                        ),
                        "skills_needing_review_improvement": len(
                            [s for s in skills if s["retention_rate"] < 0.5]
                        ),
                    },
                    "individual_skills": skills,
                    "recommendations": self._generate_skill_recommendations(skills),
                    "next_actions": self._generate_next_actions(skills),
                }

                return analytics

        except Exception as e:
            logger.error(f"Error getting multi-skill analytics: {e}")
            return self._get_empty_skill_analytics()

    def _get_empty_skill_analytics(self) -> Dict[str, Any]:
        """Return empty skill analytics structure"""
        return {
            "skill_overview": {
                "total_skills_tracked": 0,
                "average_skill_level": 0,
                "overall_mastery_percentage": 0,
                "strongest_skill": None,
                "weakest_skill": None,
            },
            "progress_trends": {
                "average_improvement_rate": 0,
                "total_practice_time": 0,
                "average_consistency_score": 0,
                "skills_improving": 0,
                "skills_stable": 0,
                "skills_declining": 0,
            },
            "difficulty_analysis": {
                "comfort_with_easy_items": 0,
                "comfort_with_moderate_items": 0,
                "comfort_with_hard_items": 0,
                "average_challenge_comfort": 0,
            },
            "retention_performance": {
                "average_retention_rate": 0,
                "skills_with_good_retention": 0,
                "skills_needing_review_improvement": 0,
            },
            "individual_skills": [],
            "recommendations": [],
            "next_actions": [],
        }

    def _generate_skill_recommendations(self, skills: List[Dict]) -> List[str]:
        """Generate personalized skill improvement recommendations"""
        if not skills:
            return ["Complete skill assessments to get personalized recommendations"]

        recommendations = []

        # Find weakest skills
        weakest_skills = sorted(skills, key=lambda x: x["current_level"])[:2]
        for skill in weakest_skills:
            recommendations.append(
                f"Focus on {skill['skill_type']}: current level {skill['current_level']:.1f}%, suggested exercises: {', '.join(skill['suggested_exercises'][:2])}"
            )

        # Check for skills with poor retention
        poor_retention = [s for s in skills if s["retention_rate"] < 0.5]
        if poor_retention:
            skill_names = [s["skill_type"] for s in poor_retention[:2]]
            recommendations.append(
                f"Improve retention for {', '.join(skill_names)} with more frequent review sessions"
            )

        # Check for low consistency
        inconsistent_skills = [s for s in skills if s["consistency_score"] < 0.6]
        if inconsistent_skills:
            recommendations.append(
                "Maintain more consistent practice schedule to improve learning efficiency"
            )

        # Challenge level recommendations
        avoiding_challenge = [s for s in skills if s["challenge_comfort_level"] < 0.4]
        if avoiding_challenge:
            recommendations.append(
                "Try more challenging exercises to accelerate skill development"
            )

        return recommendations[:5]

    def _generate_next_actions(self, skills: List[Dict]) -> List[str]:
        """Generate specific next actions for skill improvement"""
        if not skills:
            return ["Take skill assessments to determine current levels"]

        actions = []

        # Skills needing immediate attention
        urgent_skills = [s for s in skills if s["current_level"] < 30]
        if urgent_skills:
            skill = urgent_skills[0]
            actions.append(
                f"Priority: Complete {skill['skill_type']} fundamentals assessment"
            )

        # Skills ready for advancement
        advancing_skills = [
            s
            for s in skills
            if 70 <= s["current_level"] < 85 and s["improvement_rate"] > 0
        ]
        if advancing_skills:
            skill = advancing_skills[0]
            actions.append(
                f"Level up: Take advanced {skill['skill_type']} challenge exercises"
            )

        # Overdue assessments
        overdue_assessments = [
            s
            for s in skills
            if s["next_assessment_due"]
            and datetime.fromisoformat(s["next_assessment_due"].replace("Z", "+00:00"))
            < datetime.now()
        ]
        if overdue_assessments:
            actions.append(
                f"Schedule overdue assessment for {overdue_assessments[0]['skill_type']}"
            )

        return actions[:3]

    # ============= LEARNING PATH RECOMMENDATIONS =============

    def create_learning_path_recommendation(
        self, recommendation: LearningPathRecommendation
    ) -> bool:
        """Create and store a personalized learning path recommendation"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO learning_path_recommendations (
                        recommendation_id, user_id, language_code, recommended_path_type,
                        path_title, path_description, estimated_duration_weeks, difficulty_level,
                        recommendation_reasons, user_strengths, user_weaknesses,
                        learning_style_preferences, primary_goals, weekly_milestones,
                        success_metrics, time_commitment_hours_per_week, preferred_session_length_minutes,
                        optimal_practice_times, confidence_score, expected_success_rate,
                        adaptation_triggers, generated_at, expires_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        recommendation.recommendation_id,
                        recommendation.user_id,
                        recommendation.language_code,
                        recommendation.recommended_path_type,
                        recommendation.path_title,
                        recommendation.path_description,
                        recommendation.estimated_duration_weeks,
                        recommendation.difficulty_level,
                        json.dumps(recommendation.recommendation_reasons),
                        json.dumps(recommendation.user_strengths),
                        json.dumps(recommendation.user_weaknesses),
                        json.dumps(recommendation.learning_style_preferences),
                        json.dumps(recommendation.primary_goals),
                        json.dumps(recommendation.weekly_milestones),
                        json.dumps(recommendation.success_metrics),
                        recommendation.time_commitment_hours_per_week,
                        recommendation.preferred_session_length_minutes,
                        json.dumps(recommendation.optimal_practice_times),
                        recommendation.confidence_score,
                        recommendation.expected_success_rate,
                        json.dumps(recommendation.adaptation_triggers),
                        recommendation.generated_at,
                        recommendation.expires_at,
                    ),
                )

                conn.commit()
                logger.info(
                    f"Learning path recommendation created: {recommendation.recommendation_id}"
                )
                return True

        except Exception as e:
            logger.error(f"Error creating learning path recommendation: {e}")
            return False

    # ============= MEMORY RETENTION ANALYTICS =============

    def create_memory_retention_analysis(
        self, analysis: MemoryRetentionAnalysis
    ) -> bool:
        """Create and store memory retention analysis"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO memory_retention_analysis (
                        user_id, language_code, analysis_period_days, short_term_retention_rate,
                        medium_term_retention_rate, long_term_retention_rate, active_recall_success_rate,
                        passive_review_success_rate, recall_vs_recognition_ratio, forgetting_curve_steepness,
                        optimal_review_timing, interference_patterns, most_retained_item_types,
                        least_retained_item_types, retention_by_difficulty, retention_by_context,
                        average_exposures_to_master, efficiency_compared_to_peers, learning_velocity,
                        optimal_study_schedule, retention_improvement_strategies, analysis_date,
                        next_analysis_due
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        analysis.user_id,
                        analysis.language_code,
                        analysis.analysis_period_days,
                        analysis.short_term_retention_rate,
                        analysis.medium_term_retention_rate,
                        analysis.long_term_retention_rate,
                        analysis.active_recall_success_rate,
                        analysis.passive_review_success_rate,
                        analysis.recall_vs_recognition_ratio,
                        analysis.forgetting_curve_steepness,
                        json.dumps(analysis.optimal_review_timing),
                        json.dumps(analysis.interference_patterns),
                        json.dumps(analysis.most_retained_item_types),
                        json.dumps(analysis.least_retained_item_types),
                        json.dumps(analysis.retention_by_difficulty),
                        json.dumps(analysis.retention_by_context),
                        analysis.average_exposures_to_master,
                        analysis.efficiency_compared_to_peers,
                        analysis.learning_velocity,
                        json.dumps(analysis.optimal_study_schedule),
                        json.dumps(analysis.retention_improvement_strategies),
                        analysis.analysis_date,
                        analysis.next_analysis_due,
                    ),
                )

                conn.commit()
                logger.info(
                    f"Memory retention analysis created for user {analysis.user_id}"
                )
                return True

        except Exception as e:
            logger.error(f"Error creating memory retention analysis: {e}")
            return False
            return self._get_empty_skill_analytics()

        """Generate personalized skill improvement recommendations"""
        if not skills:
            return ["Start practicing to get personalized skill recommendations!"]

        recommendations = []

        # Find skills needing attention
        weak_skills = [s for s in skills if s["current_level"] < 30]
        inconsistent_skills = [s for s in skills if s["consistency_score"] < 0.5]
        low_retention_skills = [s for s in skills if s["retention_rate"] < 0.6]

        # Weak skill recommendations
        if weak_skills:
            skill_name = weak_skills[0]["skill_type"].replace("_", " ").title()
            recommendations.append(
                f"Focus on improving your {skill_name} - it's currently your weakest area"
            )

        # Consistency recommendations
        if inconsistent_skills:
            skill_name = inconsistent_skills[0]["skill_type"].replace("_", " ").title()
            recommendations.append(
                f"Practice {skill_name} more regularly to improve consistency"
            )

        # Retention recommendations
        if low_retention_skills:
            skill_name = low_retention_skills[0]["skill_type"].replace("_", " ").title()
            recommendations.append(
                f"Review {skill_name} items more frequently to improve retention"
            )

        # Challenge level recommendations
        avg_challenge_comfort = safe_mean(
            [s["challenge_comfort_level"] for s in skills]
        )
        if avg_challenge_comfort < 0.4:
            recommendations.append(
                "Try easier exercises to build confidence before tackling harder material"
            )
        elif avg_challenge_comfort > 0.8:
            recommendations.append(
                "Challenge yourself with more difficult material to accelerate progress"
            )

        # Balance recommendations
        skill_levels = [s["current_level"] for s in skills]
        if max(skill_levels) - min(skill_levels) > 40:
            recommendations.append(
                "Work on balancing your skills - focus on your weaker areas"
            )

        # Practice time recommendations
        total_practice = sum(s["total_practice_time_minutes"] for s in skills)
        if total_practice < 300:  # Less than 5 hours total
            recommendations.append(
                "Increase your practice time to see faster improvements"
            )

        # Default recommendation
        if not recommendations:
            recommendations.append(
                "Great progress across all skills! Continue your current practice routine"
            )

        return recommendations[:4]  # Limit to top 4 recommendations


# Export main class
__all__ = [
    "ProgressAnalyticsService",
    "ConversationMetrics",
    "SkillProgressMetrics",
    "LearningPathRecommendation",
    "MemoryRetentionAnalysis",
    "SkillType",
    "LearningPathType",
    "ConfidenceLevel",
]
