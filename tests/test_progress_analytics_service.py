"""
Comprehensive Test Suite for Progress Analytics Service
Phase 3A.2 - Helper Function Unit Tests

Tests all 53 helper methods from progress_analytics_service.py
Coverage target: >95% for all helper functions
"""

import os
import sqlite3
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.progress_analytics_service import (
    ConfidenceLevel,
    ConversationMetrics,
    LearningPathRecommendation,
    LearningPathType,
    MemoryRetentionAnalysis,
    ProgressAnalyticsService,
    SkillProgressMetrics,
    SkillType,
    safe_mean,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def service(temp_db):
    """Create a ProgressAnalyticsService instance with temp database"""
    return ProgressAnalyticsService(db_path=temp_db)


@pytest.fixture
def sample_sessions():
    """Sample conversation sessions for testing"""
    return [
        {
            "session_id": "session1",
            "user_id": 1,
            "language_code": "es",
            "conversation_type": "scenario",
            "duration_minutes": 15.5,
            "total_exchanges": 10,
            "fluency_score": 0.75,
            "grammar_accuracy_score": 0.80,
            "pronunciation_clarity_score": 0.70,
            "vocabulary_complexity_score": 0.65,
            "average_confidence_score": 0.72,
            "created_at": "2024-01-01 10:00:00",
        },
        {
            "session_id": "session2",
            "user_id": 1,
            "language_code": "es",
            "conversation_type": "tutor_mode",
            "duration_minutes": 20.0,
            "total_exchanges": 15,
            "fluency_score": 0.80,
            "grammar_accuracy_score": 0.85,
            "pronunciation_clarity_score": 0.75,
            "vocabulary_complexity_score": 0.70,
            "average_confidence_score": 0.78,
            "created_at": "2024-01-02 10:00:00",
        },
        {
            "session_id": "session3",
            "user_id": 1,
            "language_code": "es",
            "conversation_type": "free_form",
            "duration_minutes": 25.0,
            "total_exchanges": 20,
            "fluency_score": 0.85,
            "grammar_accuracy_score": 0.90,
            "pronunciation_clarity_score": 0.80,
            "vocabulary_complexity_score": 0.75,
            "average_confidence_score": 0.82,
            "created_at": "2024-01-03 10:00:00",
        },
    ]


@pytest.fixture
def sample_skills():
    """Sample skill progress data for testing"""
    return [
        {
            "user_id": 1,
            "language_code": "es",
            "skill_id": "vocab1",
            "skill_type": "vocabulary",
            "current_level": 75.0,
            "mastery_percentage": 75.0,
            "confidence_level": "high",
            "proficiency_level": 0.75,
            "improvement_rate": 0.05,
            "practice_time_minutes": 120,
            "total_practice_time_minutes": 120,
            "consistency_score": 0.80,
            "last_practice_date": "2024-01-03",
            "retention_rate": 0.85,
            "easy_items_percentage": 0.8,
            "moderate_items_percentage": 0.6,
            "hard_items_percentage": 0.3,
            "challenge_comfort_level": 0.7,
            "suggested_exercises": ["vocab_ex1", "vocab_ex2"],
            "next_assessment_due": None,
        },
        {
            "user_id": 1,
            "language_code": "es",
            "skill_id": "grammar1",
            "skill_type": "grammar",
            "current_level": 60.0,
            "mastery_percentage": 60.0,
            "confidence_level": "medium",
            "proficiency_level": 0.60,
            "improvement_rate": 0.03,
            "practice_time_minutes": 90,
            "total_practice_time_minutes": 90,
            "consistency_score": 0.70,
            "last_practice_date": "2024-01-02",
            "retention_rate": 0.75,
            "easy_items_percentage": 0.7,
            "moderate_items_percentage": 0.5,
            "hard_items_percentage": 0.2,
            "challenge_comfort_level": 0.6,
            "suggested_exercises": ["grammar_ex1", "grammar_ex2"],
            "next_assessment_due": None,
        },
        {
            "user_id": 1,
            "language_code": "es",
            "skill_id": "speaking1",
            "skill_type": "speaking",
            "current_level": 55.0,
            "mastery_percentage": 55.0,
            "confidence_level": "low",
            "proficiency_level": 0.55,
            "improvement_rate": -0.02,  # Declining
            "practice_time_minutes": 60,
            "total_practice_time_minutes": 60,
            "consistency_score": 0.50,
            "last_practice_date": "2023-12-30",
            "retention_rate": 0.65,
            "easy_items_percentage": 0.6,
            "moderate_items_percentage": 0.4,
            "hard_items_percentage": 0.1,
            "challenge_comfort_level": 0.5,
            "suggested_exercises": ["speaking_ex1", "speaking_ex2"],
            "next_assessment_due": None,
        },
    ]


# ==============================================================================
# MODULE-LEVEL HELPER TESTS
# ==============================================================================


class TestSafeMean:
    """Test the safe_mean utility function"""

    def test_safe_mean_with_values(self):
        """Test safe_mean with valid list of numbers"""
        values = [10.0, 20.0, 30.0, 40.0]
        result = safe_mean(values)
        assert result == 25.0

    def test_safe_mean_with_empty_list(self):
        """Test safe_mean returns default for empty list"""
        result = safe_mean([])
        assert result == 0.0

    def test_safe_mean_with_custom_default(self):
        """Test safe_mean uses custom default value"""
        result = safe_mean([], default=100.0)
        assert result == 100.0

    def test_safe_mean_with_single_value(self):
        """Test safe_mean with single value"""
        result = safe_mean([42.5])
        assert result == 42.5

    def test_safe_mean_with_integers(self):
        """Test safe_mean works with integers"""
        result = safe_mean([1, 2, 3, 4, 5])
        assert result == 3.0

    def test_safe_mean_with_mixed_numbers(self):
        """Test safe_mean with mixed int/float"""
        result = safe_mean([1, 2.5, 3, 4.5])
        assert result == 2.75


# ==============================================================================
# DATACLASS POST_INIT TESTS
# ==============================================================================


class TestDataclassInitialization:
    """Test dataclass __post_init__ initialization"""

    def test_conversation_metrics_post_init(self):
        """Test ConversationMetrics __post_init__ initializes fields"""
        metrics = ConversationMetrics(
            session_id="test1",
            user_id=1,
            language_code="en",
            conversation_type="scenario",
        )
        # Check fields initialized by __post_init__
        assert metrics.confidence_distribution == {}
        assert metrics.learning_objectives_met == []
        assert isinstance(metrics.started_at, datetime)

    def test_skill_progress_metrics_post_init(self):
        """Test SkillProgressMetrics __post_init__ initializes fields"""
        skill = SkillProgressMetrics(
            user_id=1,
            language_code="es",
            skill_type="vocabulary",
        )
        # Check dict/list fields initialized by __post_init__
        assert skill.forgetting_curve_analysis == {}
        assert skill.optimal_review_intervals == {}
        assert skill.recommended_focus_areas == []
        assert skill.suggested_exercises == []
        assert isinstance(skill.last_updated, datetime)


# ==============================================================================
# SERVICE INITIALIZATION HELPER TESTS
# ==============================================================================


class TestServiceInitialization:
    """Test ProgressAnalyticsService initialization helpers"""

    def test_get_connection_returns_connection(self, service):
        """Test _get_connection returns valid SQLite connection"""
        conn = service._get_connection()
        assert isinstance(conn, sqlite3.Connection)
        assert conn.row_factory == sqlite3.Row
        conn.close()

    def test_get_connection_row_factory_set(self, service):
        """Test _get_connection sets row factory correctly"""
        conn = service._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test_col")
        row = cursor.fetchone()
        # Should be able to access by column name
        assert row["test_col"] == 1
        conn.close()

    def test_initialize_enhanced_tables_creates_tables(self, service):
        """Test _initialize_enhanced_tables creates all required tables"""
        conn = service._get_connection()
        cursor = conn.cursor()

        # Check conversation_metrics table exists
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='conversation_metrics'
        """
        )
        assert cursor.fetchone() is not None

        # Check skill_progress_metrics table exists
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='skill_progress_metrics'
        """
        )
        assert cursor.fetchone() is not None

        conn.close()

    def test_initialize_enhanced_tables_idempotent(self, service):
        """Test _initialize_enhanced_tables can be called multiple times"""
        # Should not raise error when called again
        service._initialize_enhanced_tables()
        service._initialize_enhanced_tables()
        # Verify tables still exist
        conn = service._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='conversation_metrics'"
        )
        assert cursor.fetchone() is not None
        conn.close()


# ==============================================================================
# DATA EXTRACTION HELPER TESTS
# ==============================================================================


class TestDataExtractionHelpers:
    """Test helper methods that extract data from sessions"""

    def test_extract_fluency_scores_valid_data(self, service, sample_sessions):
        """Test _extract_fluency_scores extracts all scores"""
        scores = service._extract_fluency_scores(sample_sessions)
        assert len(scores) == 3
        assert scores == [0.75, 0.80, 0.85]

    def test_extract_fluency_scores_empty_sessions(self, service):
        """Test _extract_fluency_scores with empty list"""
        scores = service._extract_fluency_scores([])
        assert scores == []

    def test_extract_fluency_scores_filters_zeros(self, service):
        """Test _extract_fluency_scores filters out zero scores"""
        sessions = [
            {"fluency_score": 0.75},
            {"fluency_score": 0.0},  # Should be filtered
            {"fluency_score": 0.85},
        ]
        scores = service._extract_fluency_scores(sessions)
        # Should only include non-zero scores
        assert len(scores) == 2
        assert scores == [0.75, 0.85]

    def test_extract_grammar_scores_valid_data(self, service, sample_sessions):
        """Test _extract_grammar_scores extracts all scores"""
        scores = service._extract_grammar_scores(sample_sessions)
        assert len(scores) == 3
        assert scores == [0.80, 0.85, 0.90]

    def test_extract_grammar_scores_empty_sessions(self, service):
        """Test _extract_grammar_scores with empty list"""
        scores = service._extract_grammar_scores([])
        assert scores == []

    def test_extract_pronunciation_scores_valid_data(self, service, sample_sessions):
        """Test _extract_pronunciation_scores extracts all scores"""
        scores = service._extract_pronunciation_scores(sample_sessions)
        assert len(scores) == 3
        assert scores == [0.70, 0.75, 0.80]

    def test_extract_vocabulary_scores_valid_data(self, service, sample_sessions):
        """Test _extract_vocabulary_scores extracts all scores"""
        scores = service._extract_vocabulary_scores(sample_sessions)
        assert len(scores) == 3
        assert scores == [0.65, 0.70, 0.75]

    def test_extract_confidence_scores_valid_data(self, service, sample_sessions):
        """Test _extract_confidence_scores extracts all scores"""
        scores = service._extract_confidence_scores(sample_sessions)
        assert len(scores) == 3
        assert scores == [0.72, 0.78, 0.82]


# ==============================================================================
# CALCULATION HELPER TESTS
# ==============================================================================


class TestCalculationHelpers:
    """Test helper methods that perform calculations"""

    def test_calculate_overview_metrics_valid_data(self, service, sample_sessions):
        """Test _calculate_overview_metrics computes correct metrics"""
        metrics = service._calculate_overview_metrics(sample_sessions)

        assert "total_conversations" in metrics
        assert metrics["total_conversations"] == 3
        assert "total_conversation_time" in metrics
        assert metrics["total_conversation_time"] == 60.5  # 15.5 + 20.0 + 25.0
        assert "total_exchanges" in metrics
        assert metrics["total_exchanges"] == 45  # 10 + 15 + 20

    def test_calculate_overview_metrics_empty_sessions(self, service):
        """Test _calculate_overview_metrics with empty list"""
        metrics = service._calculate_overview_metrics([])
        assert metrics["total_conversations"] == 0
        assert metrics["total_conversation_time"] == 0
        assert metrics["total_exchanges"] == 0

    def test_calculate_performance_metrics_with_data(self, service, sample_sessions):
        """Test _calculate_performance_metrics computes averages"""
        metrics = service._calculate_performance_metrics(sample_sessions)

        assert "average_fluency_score" in metrics
        assert metrics["average_fluency_score"] == pytest.approx(0.80, rel=0.01)
        assert "average_grammar_accuracy" in metrics
        assert metrics["average_grammar_accuracy"] == pytest.approx(0.85, rel=0.01)

    def test_calculate_learning_progress_with_data(self, service):
        """Test _calculate_learning_progress calculates totals"""
        sessions = [
            {
                "new_vocabulary_encountered": 10,
                "grammar_patterns_practiced": 5,
                "cultural_context_learned": 2,
                "improvement_from_last_session": 0.05,
            },
            {
                "new_vocabulary_encountered": 8,
                "grammar_patterns_practiced": 3,
                "cultural_context_learned": 1,
                "improvement_from_last_session": 0.03,
            },
        ]
        progress = service._calculate_learning_progress(sessions)

        assert "total_new_vocabulary" in progress
        assert progress["total_new_vocabulary"] == 18
        assert "total_grammar_patterns" in progress
        assert progress["total_grammar_patterns"] == 8

    def test_calculate_engagement_analysis_with_data(self, service):
        """Test _calculate_engagement_analysis computes engagement metrics"""
        sessions = [
            {
                "total_exchanges": 10,
                "engagement_score": 0.8,
                "hesitation_count": 2,
                "self_correction_count": 1,
            },
            {
                "total_exchanges": 15,
                "engagement_score": 0.9,
                "hesitation_count": 1,
                "self_correction_count": 2,
            },
        ]
        analysis = service._calculate_engagement_analysis(sessions)

        assert "total_hesitations" in analysis
        assert analysis["total_hesitations"] == 3
        assert "total_self_corrections" in analysis
        assert analysis["total_self_corrections"] == 3
        assert "hesitation_rate" in analysis


class TestLinearTrendCalculation:
    """Test _calculate_linear_trend helper"""

    def test_calculate_linear_trend_increasing(self, service):
        """Test _calculate_linear_trend with increasing values"""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        trend = service._calculate_linear_trend(values)

        assert "slope" in trend
        assert "direction" in trend
        assert trend["slope"] > 0
        assert trend["direction"] == "improving"

    def test_calculate_linear_trend_decreasing(self, service):
        """Test _calculate_linear_trend with decreasing values"""
        values = [5.0, 4.0, 3.0, 2.0, 1.0]
        trend = service._calculate_linear_trend(values)

        assert trend["slope"] < 0
        assert trend["direction"] == "declining"

    def test_calculate_linear_trend_stable(self, service):
        """Test _calculate_linear_trend with stable values"""
        values = [3.0, 3.0, 3.0, 3.0, 3.0]
        trend = service._calculate_linear_trend(values)

        assert trend["slope"] == pytest.approx(0.0, abs=0.01)
        assert trend["direction"] == "stable"

    def test_calculate_linear_trend_insufficient_data(self, service):
        """Test _calculate_linear_trend with < 2 values"""
        values = [1.0]
        trend = service._calculate_linear_trend(values)

        # Should handle gracefully
        assert "slope" in trend
        assert trend["slope"] == 0.0


# ==============================================================================
# SORTING AND BUILDING HELPER TESTS
# ==============================================================================


class TestSortingHelpers:
    """Test helper methods that sort data"""

    def test_sort_sessions_by_date_ascending(self, service):
        """Test _sort_sessions_by_date sorts by started_at"""
        sessions = [
            {"session_id": "s3", "started_at": "2024-01-03 10:00:00"},
            {"session_id": "s1", "started_at": "2024-01-01 10:00:00"},
            {"session_id": "s2", "started_at": "2024-01-02 10:00:00"},
        ]
        sorted_sessions = service._sort_sessions_by_date(sessions)

        # Should be in chronological order
        assert sorted_sessions[0]["session_id"] == "s1"
        assert sorted_sessions[1]["session_id"] == "s2"
        assert sorted_sessions[2]["session_id"] == "s3"

    def test_sort_sessions_by_date_empty(self, service):
        """Test _sort_sessions_by_date with empty list"""
        sorted_sessions = service._sort_sessions_by_date([])
        assert sorted_sessions == []

    def test_extract_sorted_fluency_scores(self, service, sample_sessions):
        """Test _extract_sorted_fluency_scores returns sorted scores"""
        scores = service._extract_sorted_fluency_scores(sample_sessions)
        # Should extract and maintain sorted order
        assert scores == [0.75, 0.80, 0.85]

    def test_extract_sorted_confidence_scores(self, service, sample_sessions):
        """Test _extract_sorted_confidence_scores returns sorted scores"""
        scores = service._extract_sorted_confidence_scores(sample_sessions)
        assert scores == [0.72, 0.78, 0.82]

    def test_extract_sorted_vocabulary_scores(self, service, sample_sessions):
        """Test _extract_sorted_vocabulary_scores returns sorted scores"""
        scores = service._extract_sorted_vocabulary_scores(sample_sessions)
        assert scores == [0.65, 0.70, 0.75]


class TestBuildingHelpers:
    """Test helper methods that build data structures"""

    def test_build_trends_dict_with_valid_scores(self, service):
        """Test _build_trends_dict creates proper structure"""
        fluency_scores = [0.70, 0.75, 0.80]
        confidence_scores = [0.65, 0.70, 0.75]
        vocabulary_scores = [0.60, 0.65, 0.70]

        trends = service._build_trends_dict(
            fluency_scores=fluency_scores,
            confidence_scores=confidence_scores,
            vocabulary_scores=vocabulary_scores,
        )

        assert "fluency_trend" in trends
        assert "confidence_trend" in trends
        assert "vocabulary_trend" in trends
        assert isinstance(trends["fluency_trend"], dict)
        assert isinstance(trends["confidence_trend"], dict)

    def test_build_trends_dict_insufficient_data(self, service):
        """Test _build_trends_dict with insufficient data points"""
        trends = service._build_trends_dict(
            fluency_scores=[0.5],  # Only 1 data point
            confidence_scores=[],
            vocabulary_scores=[],
        )

        # Should not include trends with < 2 data points
        assert "fluency_trend" not in trends
        assert "confidence_trend" not in trends


class TestFetchingHelpers:
    """Test helper methods that fetch data from database"""

    def test_fetch_conversation_sessions_valid_period(self, service):
        """Test _fetch_conversation_sessions returns sessions within period"""
        from datetime import datetime, timedelta

        with service._get_connection() as conn:
            cursor = conn.cursor()

            # Create recent sessions within the period (last 30 days)
            recent_date = (datetime.now() - timedelta(days=5)).isoformat()

            cursor.execute(
                """
                INSERT INTO conversation_metrics (
                    session_id, user_id, language_code, conversation_type,
                    duration_minutes, total_exchanges, fluency_score,
                    grammar_accuracy_score, pronunciation_clarity_score,
                    vocabulary_complexity_score, average_confidence_score,
                    started_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "recent1",
                    1,
                    "es",
                    "scenario",
                    15.5,
                    10,
                    0.75,
                    0.80,
                    0.70,
                    0.65,
                    0.72,
                    recent_date,
                    recent_date,
                ),
            )
            conn.commit()

            # Fetch sessions
            sessions = service._fetch_conversation_sessions(1, "es", 30, cursor)

            assert isinstance(sessions, list)
            assert len(sessions) == 1

    def test_fetch_conversation_sessions_empty_result(self, service):
        """Test _fetch_conversation_sessions with no matching sessions"""
        with service._get_connection() as conn:
            cursor = conn.cursor()
            sessions = service._fetch_conversation_sessions(999, "fr", 30, cursor)

            assert isinstance(sessions, list)
            assert len(sessions) == 0

    def test_fetch_and_parse_skills_with_json_fields(self, service, sample_skills):
        """Test _fetch_and_parse_skills properly parses JSON fields"""
        import json

        with service._get_connection() as conn:
            cursor = conn.cursor()

            # Insert a skill with JSON fields
            skill = sample_skills[0]
            cursor.execute(
                """
                INSERT INTO skill_progress_metrics (
                    user_id, language_code, skill_type, current_level,
                    mastery_percentage, confidence_level, improvement_rate,
                    total_practice_time_minutes, consistency_score, retention_rate,
                    forgetting_curve_analysis, optimal_review_intervals,
                    recommended_focus_areas, suggested_exercises
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    skill["user_id"],
                    skill["language_code"],
                    skill["skill_type"],
                    skill["current_level"],
                    skill["mastery_percentage"],
                    skill["confidence_level"],
                    skill["improvement_rate"],
                    skill["total_practice_time_minutes"],
                    skill["consistency_score"],
                    skill["retention_rate"],
                    json.dumps({"rate": 0.1}),
                    json.dumps({"interval": 7}),
                    json.dumps(["grammar", "vocabulary"]),
                    json.dumps(["exercise1", "exercise2"]),
                ),
            )
            conn.commit()

            # Fetch and parse
            skills = service._fetch_and_parse_skills(1, "es", cursor)

            assert len(skills) > 0
            assert isinstance(skills[0]["forgetting_curve_analysis"], dict)
            assert isinstance(skills[0]["recommended_focus_areas"], list)

    def test_fetch_and_parse_skills_empty_result(self, service):
        """Test _fetch_and_parse_skills with no matching skills"""
        with service._get_connection() as conn:
            cursor = conn.cursor()
            skills = service._fetch_and_parse_skills(999, "fr", cursor)

            assert isinstance(skills, list)
            assert len(skills) == 0


class TestEmptyStateHelpers:
    """Test helper methods that return empty state structures"""

    def test_get_empty_conversation_analytics_structure(self, service):
        """Test _get_empty_conversation_analytics returns proper structure"""
        empty = service._get_empty_conversation_analytics()

        assert "overview" in empty
        assert "performance_metrics" in empty
        assert "learning_progress" in empty
        assert "engagement_analysis" in empty
        assert "trends" in empty
        assert "recommendations" in empty
        assert "recent_sessions" in empty

        # Verify all values are zeroed/empty
        assert empty["overview"]["total_conversations"] == 0
        assert empty["performance_metrics"]["average_fluency_score"] == 0
        assert empty["recommendations"] == []

    def test_get_empty_skill_analytics_structure(self, service):
        """Test _get_empty_skill_analytics returns proper structure"""
        empty = service._get_empty_skill_analytics()

        assert "skill_overview" in empty
        assert "progress_trends" in empty
        assert "difficulty_analysis" in empty
        assert "retention_performance" in empty

        # Verify all values are zeroed/empty
        assert empty["skill_overview"]["total_skills_tracked"] == 0
        assert empty["progress_trends"]["skills_improving"] == 0


class TestSkillAnalysisHelpers:
    """Test helper methods for skill analysis calculations"""

    def test_calculate_skill_overview_with_skills(self, service, sample_skills):
        """Test _calculate_skill_overview with valid skill data"""
        overview = service._calculate_skill_overview(sample_skills)

        assert overview["total_skills_tracked"] == 3
        assert "average_skill_level" in overview
        assert "overall_mastery_percentage" in overview
        assert overview["strongest_skill"] is not None
        assert overview["weakest_skill"] is not None

    def test_calculate_skill_overview_empty_skills(self, service):
        """Test _calculate_skill_overview with empty skill list"""
        overview = service._calculate_skill_overview([])

        assert overview["total_skills_tracked"] == 0
        assert overview["strongest_skill"] is None
        assert overview["weakest_skill"] is None

    def test_extract_positive_improvement_rates(self, service, sample_skills):
        """Test _extract_positive_improvement_rates filters correctly"""
        rates = service._extract_positive_improvement_rates(sample_skills)

        assert isinstance(rates, list)
        assert all(rate > 0 for rate in rates)

    def test_calculate_total_practice_time(self, service, sample_skills):
        """Test _calculate_total_practice_time sums correctly"""
        total = service._calculate_total_practice_time(sample_skills)

        expected = sum(s["total_practice_time_minutes"] for s in sample_skills)
        assert total == expected
        assert total > 0

    def test_extract_consistency_scores(self, service, sample_skills):
        """Test _extract_consistency_scores extracts all scores"""
        scores = service._extract_consistency_scores(sample_skills)

        assert isinstance(scores, list)
        assert len(scores) == len(sample_skills)
        assert all(0 <= score <= 1 for score in scores)

    def test_count_improving_skills(self, service, sample_skills):
        """Test _count_improving_skills counts positive rates"""
        count = service._count_improving_skills(sample_skills)

        expected = len([s for s in sample_skills if s["improvement_rate"] > 0])
        assert count == expected

    def test_count_stable_skills(self, service, sample_skills):
        """Test _count_stable_skills counts zero rates"""
        count = service._count_stable_skills(sample_skills)

        expected = len([s for s in sample_skills if s["improvement_rate"] == 0])
        assert count == expected

    def test_count_declining_skills(self, service, sample_skills):
        """Test _count_declining_skills counts negative rates"""
        count = service._count_declining_skills(sample_skills)

        expected = len([s for s in sample_skills if s["improvement_rate"] < 0])
        assert count == expected

    def test_calculate_progress_trends(self, service, sample_skills):
        """Test _calculate_progress_trends aggregates metrics"""
        trends = service._calculate_progress_trends(sample_skills)

        assert "average_improvement_rate" in trends
        assert "total_practice_time" in trends
        assert "average_consistency_score" in trends
        assert "skills_improving" in trends
        assert "skills_stable" in trends
        assert "skills_declining" in trends

    def test_calculate_difficulty_analysis(self, service, sample_skills):
        """Test _calculate_difficulty_analysis computes averages"""
        analysis = service._calculate_difficulty_analysis(sample_skills)

        assert "comfort_with_easy_items" in analysis
        assert "comfort_with_moderate_items" in analysis
        assert "comfort_with_hard_items" in analysis
        assert "average_challenge_comfort" in analysis

    def test_calculate_retention_performance(self, service, sample_skills):
        """Test _calculate_retention_performance analyzes retention"""
        performance = service._calculate_retention_performance(sample_skills)

        assert "average_retention_rate" in performance
        assert "skills_with_good_retention" in performance
        assert "skills_needing_review_improvement" in performance


class TestConversationRecommendationHelpers:
    """Test helper methods for generating conversation recommendations"""

    def test_generate_conversation_recommendations_empty_sessions(self, service):
        """Test _generate_conversation_recommendations with no sessions"""
        recommendations = service._generate_conversation_recommendations([])

        assert isinstance(recommendations, list)
        assert len(recommendations) == 1
        assert "Start having conversations" in recommendations[0]

    def test_generate_conversation_recommendations_low_fluency(self, service):
        """Test _generate_conversation_recommendations detects low fluency"""
        sessions = [
            {
                "session_id": "test1",
                "fluency_score": 0.4,
                "average_confidence_score": 0.8,
                "grammar_accuracy_score": 0.8,
                "pronunciation_clarity_score": 0.8,
                "vocabulary_complexity_score": 0.8,
                "engagement_score": 0.8,
                "hesitation_count": 2,
                "total_exchanges": 10,
            }
        ]

        recommendations = service._generate_conversation_recommendations(sessions)

        assert any(
            "fluency" in r.lower() or "smoothly" in r.lower() for r in recommendations
        )

    def test_generate_conversation_recommendations_low_confidence(self, service):
        """Test _generate_conversation_recommendations detects low confidence"""
        sessions = [
            {
                "session_id": "test1",
                "fluency_score": 0.8,
                "average_confidence_score": 0.3,
                "grammar_accuracy_score": 0.8,
                "pronunciation_clarity_score": 0.8,
                "vocabulary_complexity_score": 0.8,
                "engagement_score": 0.8,
                "hesitation_count": 2,
                "total_exchanges": 10,
            }
        ]

        recommendations = service._generate_conversation_recommendations(sessions)

        assert any("confidence" in r.lower() for r in recommendations)

    def test_generate_conversation_recommendations_limits_to_five(self, service):
        """Test _generate_conversation_recommendations limits output"""
        sessions = [
            {
                "session_id": "test1",
                "fluency_score": 0.4,
                "average_confidence_score": 0.3,
                "grammar_accuracy_score": 0.5,
                "pronunciation_clarity_score": 0.4,
                "vocabulary_complexity_score": 0.3,
                "engagement_score": 0.4,
                "hesitation_count": 8,
                "total_exchanges": 10,
            }
        ]

        recommendations = service._generate_conversation_recommendations(sessions)

        assert len(recommendations) <= 5

    def test_generate_conversation_recommendations_excellent_performance(self, service):
        """Test _generate_conversation_recommendations for excellent scores"""
        sessions = [
            {
                "session_id": "test1",
                "fluency_score": 0.95,
                "average_confidence_score": 0.95,
                "grammar_accuracy_score": 0.95,
                "pronunciation_clarity_score": 0.95,
                "vocabulary_complexity_score": 0.95,
                "engagement_score": 0.95,
                "hesitation_count": 1,
                "total_exchanges": 20,
            }
        ]

        recommendations = service._generate_conversation_recommendations(sessions)

        assert any(
            "excellent" in r.lower() or "challenging" in r.lower()
            for r in recommendations
        )


class TestSkillRecommendationHelpers:
    """Test helper methods for generating skill recommendations"""

    def test_add_weakest_skill_recommendations(self, service):
        """Test _add_weakest_skill_recommendations identifies weak skills"""
        skills = [
            {
                "skill_type": "grammar",
                "current_level": 30,
                "suggested_exercises": ["ex1", "ex2"],
            },
            {
                "skill_type": "vocabulary",
                "current_level": 50,
                "suggested_exercises": ["ex3", "ex4"],
            },
            {
                "skill_type": "pronunciation",
                "current_level": 20,
                "suggested_exercises": ["ex5", "ex6"],
            },
        ]
        recommendations = []

        service._add_weakest_skill_recommendations(skills, recommendations)

        assert len(recommendations) == 2
        assert any("pronunciation" in r for r in recommendations)
        assert any("grammar" in r for r in recommendations)

    def test_add_retention_recommendations(self, service):
        """Test _add_retention_recommendations detects poor retention"""
        skills = [
            {"skill_type": "grammar", "retention_rate": 0.3},
            {"skill_type": "vocabulary", "retention_rate": 0.8},
            {"skill_type": "pronunciation", "retention_rate": 0.4},
        ]
        recommendations = []

        service._add_retention_recommendations(skills, recommendations)

        assert len(recommendations) > 0
        assert any("retention" in r.lower() for r in recommendations)

    def test_add_retention_recommendations_no_poor_retention(self, service):
        """Test _add_retention_recommendations with good retention"""
        skills = [
            {"skill_type": "grammar", "retention_rate": 0.8},
            {"skill_type": "vocabulary", "retention_rate": 0.9},
        ]
        recommendations = []

        service._add_retention_recommendations(skills, recommendations)

        assert len(recommendations) == 0

    def test_add_consistency_recommendations(self, service):
        """Test _add_consistency_recommendations detects inconsistency"""
        skills = [
            {"skill_type": "grammar", "consistency_score": 0.4},
            {"skill_type": "vocabulary", "consistency_score": 0.5},
        ]
        recommendations = []

        service._add_consistency_recommendations(skills, recommendations)

        assert len(recommendations) > 0
        assert any("consistent" in r.lower() for r in recommendations)

    def test_add_consistency_recommendations_all_consistent(self, service):
        """Test _add_consistency_recommendations with consistent practice"""
        skills = [
            {"skill_type": "grammar", "consistency_score": 0.8},
            {"skill_type": "vocabulary", "consistency_score": 0.9},
        ]
        recommendations = []

        service._add_consistency_recommendations(skills, recommendations)

        assert len(recommendations) == 0

    def test_add_challenge_recommendations(self, service):
        """Test _add_challenge_recommendations detects avoidance"""
        skills = [
            {"skill_type": "grammar", "challenge_comfort_level": 0.2},
            {"skill_type": "vocabulary", "challenge_comfort_level": 0.8},
        ]
        recommendations = []

        service._add_challenge_recommendations(skills, recommendations)

        assert len(recommendations) > 0
        assert any("challenging" in r.lower() for r in recommendations)

    def test_add_challenge_recommendations_comfortable(self, service):
        """Test _add_challenge_recommendations with good comfort"""
        skills = [
            {"skill_type": "grammar", "challenge_comfort_level": 0.7},
            {"skill_type": "vocabulary", "challenge_comfort_level": 0.8},
        ]
        recommendations = []

        service._add_challenge_recommendations(skills, recommendations)

        assert len(recommendations) == 0

    def test_generate_skill_recommendations_empty(self, service):
        """Test _generate_skill_recommendations with no skills"""
        recommendations = service._generate_skill_recommendations([])

        assert isinstance(recommendations, list)
        assert len(recommendations) == 1
        assert "assessment" in recommendations[0].lower()

    def test_generate_skill_recommendations_with_issues(self, service):
        """Test _generate_skill_recommendations identifies issues"""
        skills = [
            {
                "skill_type": "grammar",
                "current_level": 25,
                "retention_rate": 0.3,
                "consistency_score": 0.4,
                "challenge_comfort_level": 0.2,
                "suggested_exercises": ["ex1", "ex2"],
            },
            {
                "skill_type": "vocabulary",
                "current_level": 60,
                "retention_rate": 0.8,
                "consistency_score": 0.9,
                "challenge_comfort_level": 0.7,
                "suggested_exercises": ["ex3", "ex4"],
            },
        ]

        recommendations = service._generate_skill_recommendations(skills)

        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5


class TestNextActionHelpers:
    """Test helper methods for generating next actions"""

    def test_add_urgent_skill_actions(self, service):
        """Test _add_urgent_skill_actions identifies urgent skills"""
        skills = [
            {"skill_type": "grammar", "current_level": 20},
            {"skill_type": "vocabulary", "current_level": 60},
        ]
        actions = []

        service._add_urgent_skill_actions(skills, actions)

        assert len(actions) > 0
        assert any("grammar" in a for a in actions)

    def test_add_urgent_skill_actions_no_urgent(self, service):
        """Test _add_urgent_skill_actions with no urgent skills"""
        skills = [
            {"skill_type": "grammar", "current_level": 60},
            {"skill_type": "vocabulary", "current_level": 70},
        ]
        actions = []

        service._add_urgent_skill_actions(skills, actions)

        assert len(actions) == 0

    def test_add_advancement_actions(self, service):
        """Test _add_advancement_actions identifies ready skills"""
        skills = [
            {"skill_type": "grammar", "current_level": 75, "improvement_rate": 0.5},
            {"skill_type": "vocabulary", "current_level": 50, "improvement_rate": 0.3},
        ]
        actions = []

        service._add_advancement_actions(skills, actions)

        assert len(actions) > 0
        assert any("grammar" in a for a in actions)

    def test_add_advancement_actions_no_ready(self, service):
        """Test _add_advancement_actions with no ready skills"""
        skills = [
            {"skill_type": "grammar", "current_level": 50, "improvement_rate": 0.5},
            {"skill_type": "vocabulary", "current_level": 90, "improvement_rate": -0.1},
        ]
        actions = []

        service._add_advancement_actions(skills, actions)

        assert len(actions) == 0

    def test_add_overdue_assessment_actions(self, service):
        """Test _add_overdue_assessment_actions detects overdue"""
        from datetime import datetime, timedelta

        past_date = (datetime.now() - timedelta(days=5)).isoformat()
        skills = [
            {"skill_type": "grammar", "next_assessment_due": past_date},
        ]
        actions = []

        service._add_overdue_assessment_actions(skills, actions)

        assert len(actions) > 0
        assert any("overdue" in a.lower() for a in actions)

    def test_add_overdue_assessment_actions_no_overdue(self, service):
        """Test _add_overdue_assessment_actions with no overdue"""
        from datetime import datetime, timedelta

        future_date = (datetime.now() + timedelta(days=5)).isoformat()
        skills = [
            {"skill_type": "grammar", "next_assessment_due": future_date},
        ]
        actions = []

        service._add_overdue_assessment_actions(skills, actions)

        assert len(actions) == 0

    def test_generate_next_actions_empty(self, service):
        """Test _generate_next_actions with no skills"""
        actions = service._generate_next_actions([])

        assert isinstance(actions, list)
        assert len(actions) == 1
        assert "assessment" in actions[0].lower()

    def test_generate_next_actions_with_various_needs(self, service):
        """Test _generate_next_actions generates appropriate actions"""
        from datetime import datetime, timedelta

        past_date = (datetime.now() - timedelta(days=5)).isoformat()
        skills = [
            {
                "skill_type": "grammar",
                "current_level": 25,
                "improvement_rate": 0.2,
                "next_assessment_due": past_date,
            },
            {
                "skill_type": "vocabulary",
                "current_level": 75,
                "improvement_rate": 0.5,
                "next_assessment_due": None,
            },
        ]

        actions = service._generate_next_actions(skills)

        assert isinstance(actions, list)
        assert len(actions) > 0
