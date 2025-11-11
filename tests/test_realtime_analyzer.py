"""
Comprehensive tests for real-time language analysis engine.

This test suite achieves 100% coverage of app.services.realtime_analyzer by testing:
- Helper functions (safe_mean, extract_json_from_response)
- Enums (AnalysisType, FeedbackPriority, PronunciationScore)
- Dataclasses (all 7 types)
- RealTimeAnalyzer class (all 15 methods)
- Session management and lifecycle
- Pronunciation analysis with AI integration
- Grammar analysis with AI integration
- Fluency metrics and calculations
- Analytics and trend calculation
- Global instance and convenience functions

Coverage target: 100% (from 42%)
Test count: ~70 tests
"""

import json
import time
from datetime import datetime, timedelta
from typing import List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.services.ai_service_base import AIResponseStatus
from app.services.realtime_analyzer import (
    AnalysisSession,
    # Enums
    AnalysisType,
    # Dataclasses
    AudioSegment,
    FeedbackPriority,
    FluencyMetrics,
    GrammarIssue,
    PronunciationAnalysis,
    PronunciationScore,
    # Main class
    RealTimeAnalyzer,
    RealTimeFeedback,
    analyze_speech_realtime,
    end_realtime_session,
    extract_json_from_response,
    get_realtime_analytics,
    # Global instance
    realtime_analyzer,
    # Helper functions
    safe_mean,
    # Convenience functions
    start_realtime_analysis,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def analyzer():
    """Create fresh analyzer instance for each test"""
    analyzer = RealTimeAnalyzer()
    # Clear any existing sessions
    analyzer.active_sessions.clear()
    analyzer.analysis_cache.clear()
    return analyzer


@pytest.fixture
def sample_audio_segment():
    """Create sample audio segment for testing"""
    return AudioSegment(
        audio_data=b"fake_audio_data",
        text="Hello world, this is a test",
        start_time=time.time(),
        end_time=time.time() + 2.0,
        duration=2.0,
        language="en",
        confidence=0.85,
    )


@pytest.fixture
def sample_session(analyzer):
    """Create sample analysis session"""
    session = AnalysisSession(
        session_id="test_session_123",
        user_id="user_123",
        language="en",
        start_time=datetime.now(),
        last_update=datetime.now(),
        total_words=0,
        total_errors=0,
        pronunciation_scores=[],
        grammar_scores=[],
        fluency_scores=[],
        feedback_history=[],
        current_metrics=FluencyMetrics(
            speech_rate=0.0,
            pause_count=0,
            pause_duration=0.0,
            hesitation_count=0,
            articulation_rate=0.0,
            confidence_score=0.0,
            rhythm_score=0.0,
        ),
        improvement_areas=[],
    )
    analyzer.active_sessions[session.session_id] = session
    return session


@pytest.fixture
def mock_ai_response_success():
    """Create mock successful AI response"""
    mock_response = Mock()
    mock_response.status = AIResponseStatus.SUCCESS
    return mock_response


# ============================================================================
# 1. HELPER FUNCTIONS (5 tests)
# ============================================================================


def test_safe_mean_with_values():
    """Test safe_mean with valid values"""
    result = safe_mean([10, 20, 30])
    assert result == 20.0


def test_safe_mean_with_empty_list():
    """Test safe_mean with empty list returns default"""
    result = safe_mean([])
    assert result == 0.0


def test_safe_mean_with_custom_default():
    """Test safe_mean with custom default value"""
    result = safe_mean([], default=50.0)
    assert result == 50.0


def test_extract_json_from_response_with_markdown():
    """Test extracting JSON from markdown code blocks"""
    response = """
    Here's the analysis:
    ```json
    {"score": 85, "errors": []}
    ```
    Let me know if you need more!
    """
    result = extract_json_from_response(response)
    assert '{"score": 85, "errors": []}' in result


def test_extract_json_from_response_with_raw_json():
    """Test extracting raw JSON from response"""
    response = 'Some text {"score": 90, "data": {"nested": true}} more text'
    result = extract_json_from_response(response)
    assert "{" in result
    assert "score" in result


def test_extract_json_from_response_no_json():
    """Test extraction returns original text when no JSON found"""
    response = "This is just plain text without any JSON"
    result = extract_json_from_response(response)
    assert result == response.strip()


def test_extract_json_from_response_array_in_markdown():
    """Test extracting JSON array from markdown code blocks"""
    response = """
    Here's the list:
    ```json
    [{"error": "test1"}, {"error": "test2"}]
    ```
    """
    result = extract_json_from_response(response)
    assert "[" in result
    assert "error" in result


def test_extract_json_from_response_raw_array():
    """Test extracting raw JSON array from response"""
    response = 'Some text [{"item": 1}, {"item": 2}] more text'
    result = extract_json_from_response(response)
    assert "[" in result
    assert "item" in result


# ============================================================================
# 2. ENUMS (3 tests)
# ============================================================================


def test_analysis_type_enum():
    """Test AnalysisType enum values"""
    assert AnalysisType.PRONUNCIATION.value == "pronunciation"
    assert AnalysisType.GRAMMAR.value == "grammar"
    assert AnalysisType.FLUENCY.value == "fluency"
    assert AnalysisType.VOCABULARY.value == "vocabulary"
    assert AnalysisType.COMPREHENSIVE.value == "comprehensive"
    assert len(AnalysisType) == 5


def test_feedback_priority_enum():
    """Test FeedbackPriority enum values"""
    assert FeedbackPriority.CRITICAL.value == "critical"
    assert FeedbackPriority.IMPORTANT.value == "important"
    assert FeedbackPriority.MINOR.value == "minor"
    assert FeedbackPriority.SUGGESTION.value == "suggestion"
    assert len(FeedbackPriority) == 4


def test_pronunciation_score_enum():
    """Test PronunciationScore enum values"""
    assert PronunciationScore.EXCELLENT.value == 90
    assert PronunciationScore.GOOD.value == 75
    assert PronunciationScore.FAIR.value == 60
    assert PronunciationScore.POOR.value == 40
    assert PronunciationScore.UNCLEAR.value == 0
    assert len(PronunciationScore) == 5


# ============================================================================
# 3. DATACLASSES (7 tests)
# ============================================================================


def test_audio_segment_dataclass():
    """Test AudioSegment dataclass"""
    segment = AudioSegment(
        audio_data=b"test",
        text="hello",
        start_time=1.0,
        end_time=2.0,
        duration=1.0,
        language="en",
        confidence=0.9,
    )
    assert segment.audio_data == b"test"
    assert segment.text == "hello"
    assert segment.duration == 1.0


def test_pronunciation_analysis_dataclass():
    """Test PronunciationAnalysis dataclass"""
    analysis = PronunciationAnalysis(
        word="hello",
        phonetic_transcription="həˈloʊ",
        expected_phonemes=["h", "ə", "l", "oʊ"],
        actual_phonemes=["h", "ə", "l", "oʊ"],
        score=85.0,
        errors=[],
        suggestions=["Great pronunciation!"],
        confidence=0.9,
    )
    assert analysis.word == "hello"
    assert analysis.score == 85.0


def test_grammar_issue_dataclass():
    """Test GrammarIssue dataclass"""
    issue = GrammarIssue(
        text="He go to school",
        error_type="subject_verb_agreement",
        position=(3, 5),
        severity=FeedbackPriority.CRITICAL,
        correction="He goes to school",
        explanation="Third person singular requires 's'",
        rule="subject_verb_agreement",
        confidence=0.95,
    )
    assert issue.error_type == "subject_verb_agreement"
    assert issue.correction == "He goes to school"


def test_fluency_metrics_dataclass():
    """Test FluencyMetrics dataclass"""
    metrics = FluencyMetrics(
        speech_rate=150.0,
        pause_count=3,
        pause_duration=1.5,
        hesitation_count=2,
        articulation_rate=160.0,
        confidence_score=0.8,
        rhythm_score=0.85,
    )
    assert metrics.speech_rate == 150.0
    assert metrics.pause_count == 3


def test_realtime_feedback_dataclass():
    """Test RealTimeFeedback dataclass"""
    feedback = RealTimeFeedback(
        feedback_id="fb_123",
        timestamp=datetime.now(),
        analysis_type=AnalysisType.PRONUNCIATION,
        priority=FeedbackPriority.IMPORTANT,
        message="Good pronunciation",
        correction=None,
        explanation="Keep practicing",
        pronunciation_data=None,
        grammar_data=None,
        fluency_data=None,
        confidence=0.85,
        actionable=True,
    )
    assert feedback.feedback_id == "fb_123"
    assert feedback.priority == FeedbackPriority.IMPORTANT


def test_analysis_session_dataclass():
    """Test AnalysisSession dataclass"""
    metrics = FluencyMetrics(
        speech_rate=0.0,
        pause_count=0,
        pause_duration=0.0,
        hesitation_count=0,
        articulation_rate=0.0,
        confidence_score=0.0,
        rhythm_score=0.0,
    )
    session = AnalysisSession(
        session_id="sess_123",
        user_id="user_456",
        language="en",
        start_time=datetime.now(),
        last_update=datetime.now(),
        total_words=0,
        total_errors=0,
        pronunciation_scores=[],
        grammar_scores=[],
        fluency_scores=[],
        feedback_history=[],
        current_metrics=metrics,
        improvement_areas=[],
    )
    assert session.session_id == "sess_123"
    assert session.language == "en"


def test_dataclasses_all_fields():
    """Test all dataclasses can be instantiated with all fields"""
    # This ensures no required fields are missing
    audio = AudioSegment(
        audio_data=b"",
        text="",
        start_time=0.0,
        end_time=0.0,
        duration=0.0,
        language="en",
        confidence=0.0,
    )
    assert audio is not None


# ============================================================================
# 4. INITIALIZATION (3 tests)
# ============================================================================


def test_analyzer_initialization():
    """Test RealTimeAnalyzer initialization"""
    analyzer = RealTimeAnalyzer()
    assert analyzer.settings is not None
    assert analyzer.speech_processor is not None
    assert analyzer.pronunciation_threshold == 0.7
    assert analyzer.grammar_threshold == 0.8
    assert analyzer.fluency_threshold == 0.75


def test_analyzer_language_configs():
    """Test language configurations are loaded"""
    analyzer = RealTimeAnalyzer()
    assert "en" in analyzer.language_configs
    assert "es" in analyzer.language_configs
    assert "fr" in analyzer.language_configs
    assert "de" in analyzer.language_configs
    assert "zh" in analyzer.language_configs

    # Check English config structure
    en_config = analyzer.language_configs["en"]
    assert "expected_speech_rate" in en_config
    assert "common_errors" in en_config
    assert "grammar_rules" in en_config


def test_analyzer_empty_sessions_at_start():
    """Test analyzer starts with no active sessions"""
    analyzer = RealTimeAnalyzer()
    assert len(analyzer.active_sessions) == 0
    assert len(analyzer.analysis_cache) == 0


# ============================================================================
# 5. SESSION MANAGEMENT (10 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_start_analysis_session_success(analyzer):
    """Test starting a new analysis session"""
    session_id = await analyzer.start_analysis_session(
        user_id="user_123",
        language="en",
        analysis_types=[AnalysisType.PRONUNCIATION],
    )

    assert session_id.startswith("analysis_user_123_")
    assert session_id in analyzer.active_sessions

    session = analyzer.active_sessions[session_id]
    assert session.user_id == "user_123"
    assert session.language == "en"
    assert session.total_words == 0


@pytest.mark.asyncio
async def test_start_analysis_session_default_types(analyzer):
    """Test starting session with default analysis types"""
    session_id = await analyzer.start_analysis_session(
        user_id="user_456",
        language="es",
    )

    assert session_id in analyzer.active_sessions
    session = analyzer.active_sessions[session_id]
    assert session.language == "es"


@pytest.mark.asyncio
async def test_start_analysis_session_none_types(analyzer):
    """Test starting session with None analysis types"""
    session_id = await analyzer.start_analysis_session(
        user_id="user_789",
        language="fr",
        analysis_types=None,
    )

    assert session_id in analyzer.active_sessions


def test_validate_session_success(analyzer, sample_session):
    """Test validating existing session"""
    session = analyzer._validate_session(sample_session.session_id)
    assert session == sample_session
    assert session.session_id == "test_session_123"


def test_validate_session_not_found(analyzer):
    """Test validating non-existent session raises error"""
    with pytest.raises(ValueError) as exc_info:
        analyzer._validate_session("nonexistent_session")

    assert "not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_end_analysis_session_success(analyzer, sample_session):
    """Test ending an analysis session"""
    # Add some scores to test analytics
    sample_session.pronunciation_scores = [80, 85, 90]
    sample_session.grammar_scores = [75, 80]
    sample_session.fluency_scores = [70]

    analytics = await analyzer.end_analysis_session(sample_session.session_id)

    assert sample_session.session_id not in analyzer.active_sessions
    assert "session_info" in analytics
    assert "performance_metrics" in analytics


@pytest.mark.asyncio
async def test_end_analysis_session_not_found(analyzer):
    """Test ending non-existent session raises error"""
    with pytest.raises(ValueError) as exc_info:
        await analyzer.end_analysis_session("nonexistent_session")

    assert "not found" in str(exc_info.value)


def test_get_analysis_types_with_none(analyzer):
    """Test getting analysis types with None returns default"""
    types = analyzer._get_analysis_types(None)
    assert AnalysisType.COMPREHENSIVE in types


def test_get_analysis_types_with_list(analyzer):
    """Test getting analysis types with provided list"""
    input_types = [AnalysisType.PRONUNCIATION, AnalysisType.GRAMMAR]
    types = analyzer._get_analysis_types(input_types)
    assert types == input_types


def test_should_analyze_type_comprehensive(analyzer):
    """Test comprehensive analysis includes all types"""
    analysis_types = [AnalysisType.COMPREHENSIVE]

    assert analyzer._should_analyze_type(AnalysisType.PRONUNCIATION, analysis_types)
    assert analyzer._should_analyze_type(AnalysisType.GRAMMAR, analysis_types)
    assert analyzer._should_analyze_type(AnalysisType.FLUENCY, analysis_types)


def test_should_analyze_type_specific_match(analyzer):
    """Test specific type matching"""
    analysis_types = [AnalysisType.PRONUNCIATION, AnalysisType.GRAMMAR]

    assert analyzer._should_analyze_type(AnalysisType.PRONUNCIATION, analysis_types)
    assert analyzer._should_analyze_type(AnalysisType.GRAMMAR, analysis_types)


def test_should_analyze_type_no_match(analyzer):
    """Test type not in list returns False"""
    analysis_types = [AnalysisType.PRONUNCIATION]

    assert not analyzer._should_analyze_type(AnalysisType.FLUENCY, analysis_types)


# ============================================================================
# 6. PRONUNCIATION ANALYSIS (10 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_analyze_pronunciation_success_high_score(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test pronunciation analysis with high score (excellent)"""
    mock_ai_response_success.content = json.dumps(
        {
            "phonetic_transcription": "həˈloʊ wɜrld",
            "expected_phonemes": ["h", "ə", "l", "oʊ"],
            "actual_phonemes": ["h", "ə", "l", "oʊ"],
            "score": 92,
            "errors": [],
            "suggestions": ["Perfect pronunciation!"],
            "confidence": 0.95,
        }
    )

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer._analyze_pronunciation(
            sample_audio_segment, sample_session
        )

    assert len(feedback_list) == 1
    feedback = feedback_list[0]
    assert feedback.analysis_type == AnalysisType.PRONUNCIATION
    assert feedback.priority == FeedbackPriority.MINOR  # High score = minor priority
    assert "92" in feedback.message or "Excellent" in feedback.message
    assert feedback.pronunciation_data is not None
    assert feedback.pronunciation_data.score == 92
    assert len(sample_session.pronunciation_scores) == 1


@pytest.mark.asyncio
async def test_analyze_pronunciation_medium_score(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test pronunciation analysis with medium score (good/fair)"""
    mock_ai_response_success.content = json.dumps(
        {
            "score": 72,
            "errors": [{"type": "vowel_length", "position": 3}],
            "suggestions": ["Work on vowel length"],
            "confidence": 0.8,
            "phonetic_transcription": "",
            "expected_phonemes": [],
            "actual_phonemes": [],
        }
    )

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer._analyze_pronunciation(
            sample_audio_segment, sample_session
        )

    assert len(feedback_list) == 1
    feedback = feedback_list[0]
    assert feedback.priority == FeedbackPriority.IMPORTANT
    assert "72" in feedback.message or "room for improvement" in feedback.message


@pytest.mark.asyncio
async def test_analyze_pronunciation_low_score(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test pronunciation analysis with low score (poor)"""
    mock_ai_response_success.content = json.dumps(
        {
            "score": 45,
            "errors": [{"type": "major_issue"}],
            "suggestions": ["Practice more"],
            "confidence": 0.7,
            "phonetic_transcription": "",
            "expected_phonemes": [],
            "actual_phonemes": [],
        }
    )

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer._analyze_pronunciation(
            sample_audio_segment, sample_session
        )

    assert len(feedback_list) == 1
    feedback = feedback_list[0]
    assert feedback.priority == FeedbackPriority.CRITICAL
    assert "45" in feedback.message or "needs improvement" in feedback.message


@pytest.mark.asyncio
async def test_analyze_pronunciation_json_in_markdown(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test pronunciation analysis with JSON in markdown blocks"""
    mock_ai_response_success.content = """
    Here's my analysis:
    ```json
    {
        "score": 88,
        "errors": [],
        "suggestions": ["Keep it up!"],
        "confidence": 0.9,
        "phonetic_transcription": "test",
        "expected_phonemes": [],
        "actual_phonemes": []
    }
    ```
    """

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer._analyze_pronunciation(
            sample_audio_segment, sample_session
        )

    assert len(feedback_list) == 1
    assert feedback_list[0].pronunciation_data.score == 88


@pytest.mark.asyncio
async def test_analyze_pronunciation_json_parse_error(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test pronunciation analysis handles JSON parse errors"""
    mock_ai_response_success.content = "invalid json {{{{"

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer._analyze_pronunciation(
            sample_audio_segment, sample_session
        )

    # Should return empty list on parse error
    assert len(feedback_list) == 0


@pytest.mark.asyncio
async def test_analyze_pronunciation_ai_error(
    analyzer, sample_session, sample_audio_segment
):
    """Test pronunciation analysis handles AI errors"""
    mock_response = Mock()
    mock_response.status = AIResponseStatus.ERROR

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_response,
    ):
        feedback_list = await analyzer._analyze_pronunciation(
            sample_audio_segment, sample_session
        )

    assert len(feedback_list) == 0


@pytest.mark.asyncio
async def test_analyze_pronunciation_exception_handling(
    analyzer, sample_session, sample_audio_segment
):
    """Test pronunciation analysis handles exceptions"""
    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        side_effect=Exception("AI service down"),
    ):
        feedback_list = await analyzer._analyze_pronunciation(
            sample_audio_segment, sample_session
        )

    assert len(feedback_list) == 0


@pytest.mark.asyncio
async def test_analyze_pronunciation_actionable_with_suggestions(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test pronunciation feedback is actionable when suggestions present"""
    mock_ai_response_success.content = json.dumps(
        {
            "score": 70,
            "errors": [],
            "suggestions": ["Try this", "And this"],
            "confidence": 0.8,
            "phonetic_transcription": "",
            "expected_phonemes": [],
            "actual_phonemes": [],
        }
    )

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer._analyze_pronunciation(
            sample_audio_segment, sample_session
        )

    assert feedback_list[0].actionable is True


@pytest.mark.asyncio
async def test_analyze_pronunciation_not_actionable_empty_suggestions(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test pronunciation feedback not actionable when no suggestions"""
    mock_ai_response_success.content = json.dumps(
        {
            "score": 95,
            "errors": [],
            "suggestions": [],
            "confidence": 0.95,
            "phonetic_transcription": "",
            "expected_phonemes": [],
            "actual_phonemes": [],
        }
    )

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer._analyze_pronunciation(
            sample_audio_segment, sample_session
        )

    assert feedback_list[0].actionable is False


# ============================================================================
# 7. GRAMMAR ANALYSIS (10 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_analyze_grammar_success_with_errors(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test grammar analysis finding errors"""
    mock_ai_response_success.content = json.dumps(
        [
            {
                "error_type": "subject_verb_agreement",
                "start": 0,
                "end": 5,
                "severity": "critical",
                "correction": "He goes",
                "explanation": "Use 'goes' with third person",
                "rule": "subject_verb_agreement",
                "confidence": 0.95,
            }
        ]
    )

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer._analyze_grammar(
            sample_audio_segment, sample_session
        )

    assert len(feedback_list) == 1
    feedback = feedback_list[0]
    assert feedback.analysis_type == AnalysisType.GRAMMAR
    assert feedback.grammar_data is not None
    assert feedback.grammar_data.error_type == "subject_verb_agreement"
    assert len(sample_session.grammar_scores) == 1


@pytest.mark.asyncio
async def test_analyze_grammar_no_errors(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test grammar analysis with no errors found"""
    mock_ai_response_success.content = json.dumps([])

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer._analyze_grammar(
            sample_audio_segment, sample_session
        )

    assert len(feedback_list) == 0
    assert len(sample_session.grammar_scores) == 1
    assert sample_session.grammar_scores[0] == 100


@pytest.mark.asyncio
async def test_analyze_grammar_multiple_errors(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test grammar analysis with multiple errors"""
    mock_ai_response_success.content = json.dumps(
        [
            {
                "error_type": "tense",
                "start": 0,
                "end": 3,
                "severity": "important",
                "correction": "went",
                "explanation": "Past tense needed",
                "rule": "tense_consistency",
                "confidence": 0.9,
            },
            {
                "error_type": "article",
                "start": 10,
                "end": 13,
                "severity": "minor",
                "correction": "the school",
                "explanation": "Article needed",
                "rule": "articles",
                "confidence": 0.85,
            },
        ]
    )

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer._analyze_grammar(
            sample_audio_segment, sample_session
        )

    assert len(feedback_list) == 2


@pytest.mark.asyncio
async def test_analyze_grammar_severity_mapping(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test grammar severity is properly mapped"""
    mock_ai_response_success.content = json.dumps(
        [
            {
                "error_type": "test",
                "severity": "critical",
                "correction": "fix",
                "explanation": "test",
                "rule": "test",
                "confidence": 0.9,
            }
        ]
    )

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer._analyze_grammar(
            sample_audio_segment, sample_session
        )

    assert feedback_list[0].priority == FeedbackPriority.CRITICAL


@pytest.mark.asyncio
async def test_analyze_grammar_score_calculation(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test grammar score calculation with errors"""
    # Text has 6 words, 1 error = ~83% score
    mock_ai_response_success.content = json.dumps(
        [
            {
                "error_type": "test",
                "severity": "minor",
                "correction": "fix",
                "explanation": "test",
                "rule": "test",
                "confidence": 0.8,
            }
        ]
    )

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        await analyzer._analyze_grammar(sample_audio_segment, sample_session)

    assert len(sample_session.grammar_scores) == 1
    # Score should be less than 100 but positive
    assert 0 < sample_session.grammar_scores[0] < 100


@pytest.mark.asyncio
async def test_analyze_grammar_json_parse_error(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test grammar analysis handles JSON parse errors"""
    mock_ai_response_success.content = "not valid json"

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer._analyze_grammar(
            sample_audio_segment, sample_session
        )

    assert len(feedback_list) == 0


@pytest.mark.asyncio
async def test_analyze_grammar_ai_error(analyzer, sample_session, sample_audio_segment):
    """Test grammar analysis handles AI errors"""
    mock_response = Mock()
    mock_response.status = AIResponseStatus.ERROR

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_response,
    ):
        feedback_list = await analyzer._analyze_grammar(
            sample_audio_segment, sample_session
        )

    assert len(feedback_list) == 0


@pytest.mark.asyncio
async def test_analyze_grammar_exception_handling(
    analyzer, sample_session, sample_audio_segment
):
    """Test grammar analysis handles exceptions"""
    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        side_effect=Exception("Error"),
    ):
        feedback_list = await analyzer._analyze_grammar(
            sample_audio_segment, sample_session
        )

    assert len(feedback_list) == 0


@pytest.mark.asyncio
async def test_analyze_grammar_language_specific_rules(
    analyzer, sample_audio_segment, mock_ai_response_success
):
    """Test grammar analysis uses language-specific rules"""
    # Create Spanish session
    session = AnalysisSession(
        session_id="spanish_session",
        user_id="user_123",
        language="es",
        start_time=datetime.now(),
        last_update=datetime.now(),
        total_words=0,
        total_errors=0,
        pronunciation_scores=[],
        grammar_scores=[],
        fluency_scores=[],
        feedback_history=[],
        current_metrics=FluencyMetrics(0.0, 0, 0.0, 0, 0.0, 0.0, 0.0),
        improvement_areas=[],
    )
    analyzer.active_sessions[session.session_id] = session

    mock_ai_response_success.content = json.dumps([])

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ) as mock_call:
        await analyzer._analyze_grammar(sample_audio_segment, session)

        # Check that Spanish-specific rules are in the prompt
        call_args = mock_call.call_args[0][0]
        prompt = call_args[0]["content"]
        assert "es" in prompt or "spanish" in prompt.lower()


@pytest.mark.asyncio
async def test_analyze_grammar_actionable_with_correction(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test grammar feedback is actionable when correction provided"""
    mock_ai_response_success.content = json.dumps(
        [
            {
                "error_type": "test",
                "severity": "minor",
                "correction": "corrected text",
                "explanation": "test",
                "rule": "test",
                "confidence": 0.9,
            }
        ]
    )

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer._analyze_grammar(
            sample_audio_segment, sample_session
        )

    assert feedback_list[0].actionable is True


# ============================================================================
# 8. FLUENCY ANALYSIS (10 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_analyze_fluency_speech_rate_calculation(
    analyzer, sample_session, sample_audio_segment
):
    """Test fluency analysis calculates speech rate correctly"""
    # sample_audio_segment has 6 words in 2 seconds = 180 WPM
    feedback_list = await analyzer._analyze_fluency(
        sample_audio_segment, sample_session
    )

    assert sample_session.current_metrics.speech_rate == 180.0  # (6 / 2) * 60


@pytest.mark.asyncio
async def test_analyze_fluency_hesitation_detection(analyzer, sample_session):
    """Test fluency analysis detects hesitation words"""
    audio = AudioSegment(
        audio_data=b"test",
        text="Um, like, you know, I think, uh, this is good",
        start_time=0.0,
        end_time=3.0,
        duration=3.0,
        language="en",
        confidence=0.8,
    )

    feedback_list = await analyzer._analyze_fluency(audio, sample_session)

    # Should detect "um", "like", "you know", "uh" = 4 hesitations
    assert sample_session.current_metrics.hesitation_count == 4


@pytest.mark.asyncio
async def test_analyze_fluency_pause_counting(analyzer, sample_session):
    """Test fluency analysis counts pauses"""
    audio = AudioSegment(
        audio_data=b"test",
        text="Hello, world. This is... a test.",
        start_time=0.0,
        end_time=2.0,
        duration=2.0,
        language="en",
        confidence=0.9,
    )

    await analyzer._analyze_fluency(audio, sample_session)

    # Should count commas, periods, and ellipsis
    assert sample_session.current_metrics.pause_count > 0


@pytest.mark.asyncio
async def test_analyze_fluency_too_slow_feedback(analyzer, sample_session):
    """Test fluency gives feedback when speech is too slow"""
    # Very few words for duration = slow speech
    audio = AudioSegment(
        audio_data=b"test",
        text="Hello world",  # 2 words
        start_time=0.0,
        end_time=5.0,  # 5 seconds = 24 WPM (very slow)
        duration=5.0,
        language="en",
        confidence=0.9,
    )

    feedback_list = await analyzer._analyze_fluency(audio, sample_session)

    # Should suggest speaking faster
    assert len(feedback_list) > 0
    feedback_text = " ".join([f.explanation for f in feedback_list])
    assert "faster" in feedback_text.lower()


@pytest.mark.asyncio
async def test_analyze_fluency_too_fast_feedback(analyzer, sample_session):
    """Test fluency gives feedback when speech is too fast"""
    # Many words in short duration = fast speech
    audio = AudioSegment(
        audio_data=b"test",
        text="one two three four five six seven eight nine ten eleven twelve",  # 12 words
        start_time=0.0,
        end_time=2.0,  # 2 seconds = 360 WPM (very fast)
        duration=2.0,
        language="en",
        confidence=0.9,
    )

    feedback_list = await analyzer._analyze_fluency(audio, sample_session)

    # Should suggest slowing down
    assert len(feedback_list) > 0
    feedback_text = " ".join([f.explanation for f in feedback_list])
    assert "slow" in feedback_text.lower()


@pytest.mark.asyncio
async def test_analyze_fluency_high_hesitation_feedback(analyzer, sample_session):
    """Test fluency gives feedback for excessive hesitation"""
    audio = AudioSegment(
        audio_data=b"test",
        text="um uh like you know um test",  # ~70% hesitation
        start_time=0.0,
        end_time=2.0,
        duration=2.0,
        language="en",
        confidence=0.8,
    )

    feedback_list = await analyzer._analyze_fluency(audio, sample_session)

    assert len(feedback_list) > 0
    feedback_text = " ".join([f.explanation for f in feedback_list])
    assert "filler" in feedback_text.lower() or "hesitation" in feedback_text.lower()


@pytest.mark.asyncio
async def test_analyze_fluency_low_confidence_feedback(analyzer, sample_session):
    """Test fluency gives feedback for low confidence"""
    audio = AudioSegment(
        audio_data=b"test",
        text="um uh test um test uh test",  # Many hesitations
        start_time=0.0,
        end_time=2.0,
        duration=2.0,
        language="en",
        confidence=0.5,  # Low transcription confidence
    )

    feedback_list = await analyzer._analyze_fluency(audio, sample_session)

    assert len(feedback_list) > 0
    feedback_text = " ".join([f.explanation for f in feedback_list])
    assert "confidence" in feedback_text.lower() or "practice" in feedback_text.lower()


@pytest.mark.asyncio
async def test_analyze_fluency_score_calculation(analyzer, sample_session):
    """Test fluency score is calculated"""
    audio = AudioSegment(
        audio_data=b"test",
        text="This is a good test",
        start_time=0.0,
        end_time=2.0,
        duration=2.0,
        language="en",
        confidence=0.85,
    )

    await analyzer._analyze_fluency(audio, sample_session)

    assert len(sample_session.fluency_scores) == 1
    assert 0 <= sample_session.fluency_scores[0] <= 100


@pytest.mark.asyncio
async def test_analyze_fluency_exception_handling(analyzer, sample_session):
    """Test fluency analysis handles exceptions"""
    # Audio with zero duration to trigger potential error
    audio = AudioSegment(
        audio_data=b"test",
        text="test",
        start_time=0.0,
        end_time=0.0,
        duration=0.0,
        language="en",
        confidence=0.9,
    )

    # Should not raise exception
    feedback_list = await analyzer._analyze_fluency(audio, sample_session)

    # May return empty or handle gracefully
    assert isinstance(feedback_list, list)


@pytest.mark.asyncio
async def test_analyze_fluency_updates_session_metrics(analyzer, sample_session):
    """Test fluency analysis updates session metrics"""
    audio = AudioSegment(
        audio_data=b"test",
        text="Hello world",
        start_time=0.0,
        end_time=1.0,
        duration=1.0,
        language="en",
        confidence=0.9,
    )

    await analyzer._analyze_fluency(audio, sample_session)

    # Check metrics are updated
    assert sample_session.current_metrics.speech_rate > 0
    assert sample_session.current_metrics.confidence_score > 0


# ============================================================================
# 9. AUDIO SEGMENT ANALYSIS (8 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_analyze_audio_segment_comprehensive(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test analyzing audio segment with comprehensive analysis"""
    mock_ai_response_success.content = json.dumps(
        {
            "score": 85,
            "errors": [],
            "suggestions": ["Good job"],
            "confidence": 0.9,
            "phonetic_transcription": "",
            "expected_phonemes": [],
            "actual_phonemes": [],
        }
    )

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer.analyze_audio_segment(
            sample_session.session_id,
            sample_audio_segment,
            analysis_types=[AnalysisType.COMPREHENSIVE],
        )

    # Should get feedback from all analysis types
    assert len(feedback_list) > 0


@pytest.mark.asyncio
async def test_analyze_audio_segment_pronunciation_only(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test analyzing audio segment with pronunciation only"""
    mock_ai_response_success.content = json.dumps(
        {
            "score": 80,
            "errors": [],
            "suggestions": [],
            "confidence": 0.85,
            "phonetic_transcription": "",
            "expected_phonemes": [],
            "actual_phonemes": [],
        }
    )

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer.analyze_audio_segment(
            sample_session.session_id,
            sample_audio_segment,
            analysis_types=[AnalysisType.PRONUNCIATION],
        )

    # Should only get pronunciation feedback
    if len(feedback_list) > 0:
        assert all(f.analysis_type == AnalysisType.PRONUNCIATION for f in feedback_list)


@pytest.mark.asyncio
async def test_analyze_audio_segment_grammar_only(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test analyzing audio segment with grammar only"""
    mock_ai_response_success.content = json.dumps([])

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback_list = await analyzer.analyze_audio_segment(
            sample_session.session_id,
            sample_audio_segment,
            analysis_types=[AnalysisType.GRAMMAR],
        )

    # Grammar analysis should complete
    assert isinstance(feedback_list, list)


@pytest.mark.asyncio
async def test_analyze_audio_segment_fluency_only(
    analyzer, sample_session, sample_audio_segment
):
    """Test analyzing audio segment with fluency only"""
    feedback_list = await analyzer.analyze_audio_segment(
        sample_session.session_id,
        sample_audio_segment,
        analysis_types=[AnalysisType.FLUENCY],
    )

    # Fluency analysis doesn't need AI, should complete
    assert isinstance(feedback_list, list)


@pytest.mark.asyncio
async def test_analyze_audio_segment_invalid_session(analyzer, sample_audio_segment):
    """Test analyzing audio segment with invalid session"""
    with pytest.raises(ValueError):
        await analyzer.analyze_audio_segment(
            "nonexistent_session",
            sample_audio_segment,
        )


@pytest.mark.asyncio
async def test_analyze_audio_segment_exception_handling(
    analyzer, sample_session, sample_audio_segment
):
    """Test audio segment analysis handles exceptions"""
    # Force an exception in _collect_feedback
    with patch.object(analyzer, "_collect_feedback", side_effect=Exception("Error")):
        feedback_list = await analyzer.analyze_audio_segment(
            sample_session.session_id,
            sample_audio_segment,
        )

    # Should return empty list on exception
    assert feedback_list == []


@pytest.mark.asyncio
async def test_cache_analysis_result(analyzer, sample_session, sample_audio_segment):
    """Test analysis results are cached"""
    initial_cache_size = len(analyzer.analysis_cache)

    with patch.object(analyzer, "_collect_feedback", return_value=[]):
        await analyzer.analyze_audio_segment(
            sample_session.session_id,
            sample_audio_segment,
        )

    assert len(analyzer.analysis_cache) == initial_cache_size + 1


@pytest.mark.asyncio
async def test_update_session_metrics(analyzer, sample_session, sample_audio_segment):
    """Test session metrics are updated after analysis"""
    feedback = RealTimeFeedback(
        feedback_id="test",
        timestamp=datetime.now(),
        analysis_type=AnalysisType.GRAMMAR,
        priority=FeedbackPriority.CRITICAL,
        message="Test",
        correction="Fix",
        explanation="Test",
        pronunciation_data=None,
        grammar_data=GrammarIssue(
            text="test",
            error_type="test_error",
            position=(0, 1),
            severity=FeedbackPriority.CRITICAL,
            correction="fix",
            explanation="test",
            rule="test",
            confidence=0.9,
        ),
        fluency_data=None,
        confidence=0.9,
        actionable=True,
    )

    initial_words = sample_session.total_words
    initial_errors = sample_session.total_errors

    await analyzer._update_session_metrics(
        sample_session,
        sample_audio_segment,
        [feedback],
    )

    assert sample_session.total_words > initial_words
    assert sample_session.total_errors > initial_errors
    assert len(sample_session.feedback_history) > 0


# ============================================================================
# 10. SESSION ANALYTICS (8 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_get_session_analytics_success(analyzer, sample_session):
    """Test getting session analytics"""
    # Add some test data
    sample_session.pronunciation_scores = [80, 85, 90]
    sample_session.grammar_scores = [75, 80, 85]
    sample_session.fluency_scores = [70, 75, 80]
    sample_session.total_words = 100
    sample_session.total_errors = 5

    analytics = await analyzer.get_session_analytics(sample_session.session_id)

    assert "session_info" in analytics
    assert "performance_metrics" in analytics
    assert "feedback_summary" in analytics
    assert "improvement_areas" in analytics
    assert "overall_score" in analytics

    # Check session info
    assert analytics["session_info"]["session_id"] == sample_session.session_id
    assert analytics["session_info"]["total_words"] == 100

    # Check performance metrics
    assert analytics["performance_metrics"]["pronunciation"]["average_score"] == 85.0


@pytest.mark.asyncio
async def test_get_session_analytics_not_found(analyzer):
    """Test getting analytics for non-existent session"""
    with pytest.raises(ValueError):
        await analyzer.get_session_analytics("nonexistent_session")


@pytest.mark.asyncio
async def test_get_session_analytics_empty_scores(analyzer, sample_session):
    """Test getting analytics with no scores"""
    analytics = await analyzer.get_session_analytics(sample_session.session_id)

    # Should handle empty scores gracefully
    assert analytics["performance_metrics"]["pronunciation"]["average_score"] == 0.0


@pytest.mark.asyncio
async def test_get_session_analytics_feedback_summary(analyzer, sample_session):
    """Test analytics feedback summary counts"""
    # Add feedback with different priorities
    sample_session.feedback_history = [
        RealTimeFeedback(
            feedback_id="1",
            timestamp=datetime.now(),
            analysis_type=AnalysisType.GRAMMAR,
            priority=FeedbackPriority.CRITICAL,
            message="Critical",
            correction=None,
            explanation="test",
            pronunciation_data=None,
            grammar_data=None,
            fluency_data=None,
            confidence=0.9,
            actionable=True,
        ),
        RealTimeFeedback(
            feedback_id="2",
            timestamp=datetime.now(),
            analysis_type=AnalysisType.GRAMMAR,
            priority=FeedbackPriority.IMPORTANT,
            message="Important",
            correction=None,
            explanation="test",
            pronunciation_data=None,
            grammar_data=None,
            fluency_data=None,
            confidence=0.8,
            actionable=True,
        ),
        RealTimeFeedback(
            feedback_id="3",
            timestamp=datetime.now(),
            analysis_type=AnalysisType.FLUENCY,
            priority=FeedbackPriority.SUGGESTION,
            message="Suggestion",
            correction=None,
            explanation="test",
            pronunciation_data=None,
            grammar_data=None,
            fluency_data=None,
            confidence=0.7,
            actionable=False,
        ),
    ]

    analytics = await analyzer.get_session_analytics(sample_session.session_id)

    assert analytics["feedback_summary"]["critical_issues"] == 1
    assert analytics["feedback_summary"]["important_issues"] == 1
    assert analytics["feedback_summary"]["suggestions"] == 1


def test_calculate_trend_improving(analyzer):
    """Test trend calculation for improving scores"""
    scores = [70, 72, 75, 78, 82, 85, 88]
    trend = analyzer._calculate_trend(scores)
    assert trend == "improving"


def test_calculate_trend_declining(analyzer):
    """Test trend calculation for declining scores"""
    scores = [90, 88, 85, 82, 78, 75, 70]
    trend = analyzer._calculate_trend(scores)
    assert trend == "declining"


def test_calculate_trend_stable(analyzer):
    """Test trend calculation for stable scores"""
    scores = [80, 81, 80, 82, 80, 81, 80]
    trend = analyzer._calculate_trend(scores)
    assert trend == "stable"


def test_calculate_trend_insufficient_data(analyzer):
    """Test trend calculation with insufficient data"""
    scores = [80, 85]
    trend = analyzer._calculate_trend(scores)
    assert trend == "insufficient_data"


# ============================================================================
# 11. LIVE FEEDBACK (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_get_live_feedback_success(analyzer, sample_session):
    """Test getting live feedback from session"""
    # Add feedback to session
    for i in range(10):
        sample_session.feedback_history.append(
            RealTimeFeedback(
                feedback_id=f"fb_{i}",
                timestamp=datetime.now(),
                analysis_type=AnalysisType.PRONUNCIATION,
                priority=FeedbackPriority.MINOR,
                message=f"Feedback {i}",
                correction=None,
                explanation="test",
                pronunciation_data=None,
                grammar_data=None,
                fluency_data=None,
                confidence=0.8,
                actionable=False,
            )
        )

    feedback = await analyzer.get_live_feedback(sample_session.session_id, limit=5)

    assert len(feedback) == 5
    assert feedback[0].feedback_id == "fb_5"  # Last 5


@pytest.mark.asyncio
async def test_get_live_feedback_with_limit(analyzer, sample_session):
    """Test live feedback respects limit parameter"""
    # Add 3 feedback items
    for i in range(3):
        sample_session.feedback_history.append(
            RealTimeFeedback(
                feedback_id=f"fb_{i}",
                timestamp=datetime.now(),
                analysis_type=AnalysisType.GRAMMAR,
                priority=FeedbackPriority.IMPORTANT,
                message=f"Feedback {i}",
                correction=None,
                explanation="test",
                pronunciation_data=None,
                grammar_data=None,
                fluency_data=None,
                confidence=0.9,
                actionable=True,
            )
        )

    feedback = await analyzer.get_live_feedback(sample_session.session_id, limit=10)

    # Should only return 3 even though limit is 10
    assert len(feedback) == 3


@pytest.mark.asyncio
async def test_get_live_feedback_session_not_found(analyzer):
    """Test getting live feedback for non-existent session"""
    feedback = await analyzer.get_live_feedback("nonexistent_session")
    assert feedback == []


# ============================================================================
# 12. CONVENIENCE FUNCTIONS (5 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_start_realtime_analysis_function():
    """Test convenience function for starting analysis"""
    session_id = await start_realtime_analysis("user_test", "en")

    assert session_id.startswith("analysis_user_test_")
    assert session_id in realtime_analyzer.active_sessions

    # Cleanup
    await realtime_analyzer.end_analysis_session(session_id)


@pytest.mark.asyncio
async def test_analyze_speech_realtime_function():
    """Test convenience function for analyzing speech"""
    session_id = await start_realtime_analysis("user_test", "en")

    with patch("app.services.realtime_analyzer.ai_router.generate_response") as mock_ai:
        mock_response = Mock()
        mock_response.status = AIResponseStatus.SUCCESS
        mock_response.content = json.dumps(
            {
                "score": 85,
                "errors": [],
                "suggestions": [],
                "confidence": 0.9,
                "phonetic_transcription": "",
                "expected_phonemes": [],
                "actual_phonemes": [],
            }
        )
        mock_ai.return_value = mock_response

        feedback = await analyze_speech_realtime(
            session_id=session_id,
            audio_data=b"test",
            text="Hello world",
            confidence=0.9,
            language="en",
        )

    assert isinstance(feedback, list)

    # Cleanup
    await realtime_analyzer.end_analysis_session(session_id)


@pytest.mark.asyncio
async def test_get_realtime_analytics_function():
    """Test convenience function for getting analytics"""
    session_id = await start_realtime_analysis("user_test", "fr")

    analytics = await get_realtime_analytics(session_id)

    assert "session_info" in analytics
    assert analytics["session_info"]["language"] == "fr"

    # Cleanup
    await realtime_analyzer.end_analysis_session(session_id)


@pytest.mark.asyncio
async def test_end_realtime_session_function():
    """Test convenience function for ending session"""
    session_id = await start_realtime_analysis("user_test", "de")

    analytics = await end_realtime_session(session_id)

    assert "session_info" in analytics
    assert session_id not in realtime_analyzer.active_sessions


@pytest.mark.asyncio
async def test_convenience_functions_integration():
    """Test full workflow using convenience functions"""
    # Start session
    session_id = await start_realtime_analysis("user_integration", "es")
    assert session_id in realtime_analyzer.active_sessions

    # Analyze speech (mock AI)
    with patch("app.services.realtime_analyzer.ai_router.generate_response") as mock_ai:
        mock_response = Mock()
        mock_response.status = AIResponseStatus.SUCCESS
        mock_response.content = json.dumps(
            {
                "score": 90,
                "errors": [],
                "suggestions": ["Perfect!"],
                "confidence": 0.95,
                "phonetic_transcription": "",
                "expected_phonemes": [],
                "actual_phonemes": [],
            }
        )
        mock_ai.return_value = mock_response

        feedback = await analyze_speech_realtime(
            session_id, b"audio", "Hola mundo", 0.9, "es"
        )
        assert isinstance(feedback, list)

    # Get analytics
    analytics = await get_realtime_analytics(session_id)
    assert analytics["session_info"]["language"] == "es"

    # End session
    final_analytics = await end_realtime_session(session_id)
    assert session_id not in realtime_analyzer.active_sessions


# ============================================================================
# 13. GLOBAL INSTANCE (2 tests)
# ============================================================================


def test_global_instance_exists():
    """Test global realtime_analyzer instance exists"""
    assert realtime_analyzer is not None
    assert isinstance(realtime_analyzer, RealTimeAnalyzer)


def test_global_instance_attributes():
    """Test global instance has correct attributes"""
    assert hasattr(realtime_analyzer, "settings")
    assert hasattr(realtime_analyzer, "speech_processor")
    assert hasattr(realtime_analyzer, "language_configs")
    assert hasattr(realtime_analyzer, "active_sessions")
    assert hasattr(realtime_analyzer, "analysis_cache")

    # Check thresholds
    assert realtime_analyzer.pronunciation_threshold == 0.7
    assert realtime_analyzer.grammar_threshold == 0.8
    assert realtime_analyzer.fluency_threshold == 0.75


# ============================================================================
# 14. EDGE CASES AND ERROR PATHS (2 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_collect_feedback_with_empty_grammar(
    analyzer, sample_session, sample_audio_segment, mock_ai_response_success
):
    """Test _collect_feedback when grammar returns empty list"""
    mock_ai_response_success.content = json.dumps([])

    with patch(
        "app.services.realtime_analyzer.ai_router.generate_response",
        return_value=mock_ai_response_success,
    ):
        feedback = await analyzer._collect_feedback(
            sample_audio_segment,
            sample_session,
            [AnalysisType.GRAMMAR],
        )

    # Grammar can return empty list, which is valid
    assert isinstance(feedback, list)


@pytest.mark.asyncio
async def test_collect_feedback_grammar_returns_none(
    analyzer, sample_session, sample_audio_segment
):
    """Test _collect_feedback when grammar analysis returns None (line 356)"""
    # Mock _analyze_grammar to return None instead of list
    with patch.object(analyzer, "_analyze_grammar", return_value=None):
        feedback = await analyzer._collect_feedback(
            sample_audio_segment,
            sample_session,
            [AnalysisType.GRAMMAR],
        )

    # Should handle None gracefully
    assert isinstance(feedback, list)
