"""
Comprehensive Test Suite for Progress Analytics Service
Phase 3A.2 - Helper Function Unit Tests

Tests all 53 helper methods from progress_analytics_service.py
Coverage target: >95% for all helper functions
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from typing import Dict, List
from unittest.mock import Mock, patch, MagicMock

from app.services.progress_analytics_service import (
    ProgressAnalyticsService,
    ConversationMetrics,
    SkillProgressMetrics,
    LearningPathRecommendation,
    MemoryRetentionAnalysis,
    SkillType,
    LearningPathType,
    ConfidenceLevel,
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
            "skill_id": "vocab1",
            "skill_type": "vocabulary",
            "proficiency_level": 0.75,
            "improvement_rate": 0.05,
            "practice_time_minutes": 120,
            "consistency_score": 0.80,
            "last_practice_date": "2024-01-03",
            "retention_rate": 0.85,
        },
        {
            "skill_id": "grammar1",
            "skill_type": "grammar",
            "proficiency_level": 0.60,
            "improvement_rate": 0.03,
            "practice_time_minutes": 90,
            "consistency_score": 0.70,
            "last_practice_date": "2024-01-02",
            "retention_rate": 0.75,
        },
        {
            "skill_id": "speaking1",
            "skill_type": "speaking",
            "proficiency_level": 0.55,
            "improvement_rate": -0.02,  # Declining
            "practice_time_minutes": 60,
            "consistency_score": 0.50,
            "last_practice_date": "2023-12-30",
            "retention_rate": 0.65,
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


# Test file continues with remaining helper tests...
# This is the first batch covering ~20 of 53 helper methods
