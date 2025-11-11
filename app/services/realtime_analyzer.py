"""
Real-Time Analysis Engine for AI Language Tutor App (Fluently Functionality)

This module provides comprehensive real-time language analysis including:
- Pronunciation analysis and scoring
- Grammar detection and correction
- Fluency metrics (pace, hesitation, filler words)
- Live feedback generation
- Progress tracking and analytics
- Real-time conversation assessment

Features:
- Real-time pronunciation scoring with phonetic analysis
- Grammar error detection and correction suggestions
- Fluency metrics: speech rate, pauses, confidence analysis
- Live feedback with immediate corrections
- Progress analytics and improvement tracking
- Multi-language support (en, es, fr, de, zh)
- Integration with existing speech processing pipeline
"""

import json
import logging
import statistics
import time
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union


def safe_mean(values: List[Union[int, float]], default: float = 0.0) -> float:
    """Safely calculate mean, returning default if empty list"""
    if not values:
        return default
    return statistics.mean(values)


from app.core.config import get_settings
from app.services.ai_router import (
    ai_router,  # noqa: E402 - Required after logger configuration
)
from app.services.ai_service_base import (
    AIResponseStatus,  # noqa: E402 - Required after logger configuration
)
from app.services.speech_processor import (
    SpeechProcessor,  # noqa: E402 - Required after logger configuration
)

logger = logging.getLogger(__name__)


def extract_json_from_response(response_text: str) -> str:
    """Extract JSON from AI response that may include conversational text and markdown"""
    import re

    # First, try to find JSON within markdown code blocks (objects or arrays)
    json_pattern = r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```"
    match = re.search(json_pattern, response_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Check what the first JSON character is to determine type
    # Find first occurrence of { or [
    first_brace = response_text.find("{")
    first_bracket = response_text.find("[")

    # Determine which comes first (-1 means not found)
    if first_bracket != -1 and (first_brace == -1 or first_bracket < first_brace):
        # Array comes first - try to match array
        json_array_pattern = r"\[\s*\{[^{}]*\}(?:\s*,\s*\{[^{}]*\})*\s*\]"
        match = re.search(json_array_pattern, response_text, re.DOTALL)
        if match:
            return match.group(0).strip()

    # Object comes first (or array match failed) - try to match object
    json_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
    match = re.search(json_pattern, response_text, re.DOTALL)
    if match:
        return match.group(0).strip()

    # If nothing found, return original text
    return response_text.strip()


class AnalysisType(Enum):
    """Types of real-time analysis"""

    PRONUNCIATION = "pronunciation"
    GRAMMAR = "grammar"
    FLUENCY = "fluency"
    VOCABULARY = "vocabulary"
    COMPREHENSIVE = "comprehensive"


class FeedbackPriority(Enum):
    """Priority levels for feedback"""

    CRITICAL = "critical"  # Major errors that impede communication
    IMPORTANT = "important"  # Errors that affect clarity
    MINOR = "minor"  # Small improvements
    SUGGESTION = "suggestion"  # Optional enhancements


class PronunciationScore(Enum):
    """Pronunciation quality scores"""

    EXCELLENT = 90  # 90-100%
    GOOD = 75  # 75-89%
    FAIR = 60  # 60-74%
    POOR = 40  # 40-59%
    UNCLEAR = 0  # 0-39%


@dataclass
class AudioSegment:
    """Audio segment for analysis"""

    audio_data: bytes
    text: str
    start_time: float
    end_time: float
    duration: float
    language: str
    confidence: float


@dataclass
class PronunciationAnalysis:
    """Pronunciation analysis result"""

    word: str
    phonetic_transcription: str
    expected_phonemes: List[str]
    actual_phonemes: List[str]
    score: float
    errors: List[Dict[str, Any]]
    suggestions: List[str]
    confidence: float


@dataclass
class GrammarIssue:
    """Grammar error detection result"""

    text: str
    error_type: str
    position: Tuple[int, int]  # Start, end character positions
    severity: FeedbackPriority
    correction: str
    explanation: str
    rule: str
    confidence: float


@dataclass
class FluencyMetrics:
    """Fluency analysis metrics"""

    speech_rate: float  # Words per minute
    pause_count: int  # Number of pauses
    pause_duration: float  # Total pause time
    hesitation_count: int  # Filler words, repetitions
    articulation_rate: float  # Speaking rate excluding pauses
    confidence_score: float  # Overall confidence
    rhythm_score: float  # Speech rhythm consistency


@dataclass
class RealTimeFeedback:
    """Real-time feedback structure"""

    feedback_id: str
    timestamp: datetime
    analysis_type: AnalysisType
    priority: FeedbackPriority
    message: str
    correction: Optional[str]
    explanation: str
    pronunciation_data: Optional[PronunciationAnalysis]
    grammar_data: Optional[GrammarIssue]
    fluency_data: Optional[FluencyMetrics]
    confidence: float
    actionable: bool


@dataclass
class AnalysisSession:
    """Real-time analysis session state"""

    session_id: str
    user_id: str
    language: str
    start_time: datetime
    last_update: datetime
    total_words: int
    total_errors: int
    pronunciation_scores: List[float]
    grammar_scores: List[float]
    fluency_scores: List[float]
    feedback_history: List[RealTimeFeedback]
    current_metrics: FluencyMetrics
    improvement_areas: List[str]


class RealTimeAnalyzer:
    """Real-time language analysis engine"""

    def __init__(self):
        self.settings = get_settings()
        self.speech_processor = SpeechProcessor()

        # Analysis configurations
        self.pronunciation_threshold = 0.7
        self.grammar_threshold = 0.8
        self.fluency_threshold = 0.75

        # Language-specific configurations
        self.language_configs = {
            "en": {
                "expected_speech_rate": (140, 180),  # WPM range
                "common_errors": ["th_sound", "r_sound", "vowel_length"],
                "grammar_rules": [
                    "subject_verb_agreement",
                    "tense_consistency",
                    "articles",
                ],
            },
            "es": {
                "expected_speech_rate": (160, 200),
                "common_errors": ["b_v_confusion", "rolled_r", "vowel_clarity"],
                "grammar_rules": ["gender_agreement", "ser_vs_estar", "subjunctive"],
            },
            "fr": {
                "expected_speech_rate": (150, 190),
                "common_errors": ["nasal_vowels", "liaison", "r_pronunciation"],
                "grammar_rules": [
                    "gender_agreement",
                    "partitive_articles",
                    "subjunctive",
                ],
            },
            "de": {
                "expected_speech_rate": (120, 160),
                "common_errors": ["umlauts", "ch_sound", "consonant_clusters"],
                "grammar_rules": ["case_system", "word_order", "separable_verbs"],
            },
            "zh": {
                "expected_speech_rate": (200, 250),  # Characters per minute
                "common_errors": ["tones", "aspirated_consonants", "vowel_quality"],
                "grammar_rules": ["measure_words", "aspect_markers", "word_order"],
            },
        }

        # Session tracking
        self.active_sessions: Dict[str, AnalysisSession] = {}
        self.analysis_cache = deque(maxlen=1000)

    async def start_analysis_session(
        self, user_id: str, language: str, analysis_types: List[AnalysisType] = None
    ) -> str:
        """Start a new real-time analysis session"""

        if analysis_types is None:
            analysis_types = [AnalysisType.COMPREHENSIVE]

        session_id = f"analysis_{user_id}_{int(time.time())}"

        session = AnalysisSession(
            session_id=session_id,
            user_id=user_id,
            language=language,
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

        self.active_sessions[session_id] = session

        logger.info(
            f"Started analysis session {session_id} for user {user_id} in {language}"
        )
        return session_id

    def _validate_session(self, session_id: str) -> AnalysisSession:
        """Validate and retrieve analysis session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Analysis session {session_id} not found")
        return self.active_sessions[session_id]

    def _get_analysis_types(
        self, analysis_types: Optional[List[AnalysisType]]
    ) -> List[AnalysisType]:
        """Get analysis types with default"""
        return (
            analysis_types
            if analysis_types is not None
            else [AnalysisType.COMPREHENSIVE]
        )

    def _should_analyze_type(
        self, target_type: AnalysisType, analysis_types: List[AnalysisType]
    ) -> bool:
        """Check if specific analysis type should be performed"""
        return (
            target_type in analysis_types
            or AnalysisType.COMPREHENSIVE in analysis_types
        )

    async def _collect_feedback(
        self,
        audio_segment: AudioSegment,
        session: AnalysisSession,
        analysis_types: List[AnalysisType],
    ) -> List[RealTimeFeedback]:
        """Collect all requested feedback types"""
        feedback_list = []

        if self._should_analyze_type(AnalysisType.PRONUNCIATION, analysis_types):
            pronunciation_feedback = await self._analyze_pronunciation(
                audio_segment, session
            )
            if pronunciation_feedback:
                feedback_list.extend(pronunciation_feedback)

        if self._should_analyze_type(AnalysisType.GRAMMAR, analysis_types):
            grammar_feedback = await self._analyze_grammar(audio_segment, session)
            if grammar_feedback:
                feedback_list.extend(grammar_feedback)

        if self._should_analyze_type(AnalysisType.FLUENCY, analysis_types):
            fluency_feedback = await self._analyze_fluency(audio_segment, session)
            if fluency_feedback:
                feedback_list.extend(fluency_feedback)

        return feedback_list

    def _cache_analysis_result(
        self, session_id: str, audio_segment: AudioSegment, feedback_count: int
    ) -> None:
        """Cache analysis results for performance tracking"""
        self.analysis_cache.append(
            {
                "session_id": session_id,
                "timestamp": datetime.now(),
                "feedback_count": feedback_count,
                "audio_duration": audio_segment.duration,
            }
        )

    async def analyze_audio_segment(
        self,
        session_id: str,
        audio_segment: AudioSegment,
        analysis_types: List[AnalysisType] = None,
    ) -> List[RealTimeFeedback]:
        """Analyze an audio segment in real-time"""
        session = self._validate_session(session_id)
        analysis_types = self._get_analysis_types(analysis_types)

        try:
            feedback_list = await self._collect_feedback(
                audio_segment, session, analysis_types
            )
            await self._update_session_metrics(session, audio_segment, feedback_list)
            self._cache_analysis_result(session_id, audio_segment, len(feedback_list))

            logger.debug(
                f"Analyzed audio segment for session {session_id}: {len(feedback_list)} feedback items"
            )
            return feedback_list

        except Exception as e:
            logger.error(f"Error analyzing audio segment for session {session_id}: {e}")
            return []

    async def _analyze_pronunciation(
        self, audio_segment: AudioSegment, session: AnalysisSession
    ) -> List[RealTimeFeedback]:
        """Analyze pronunciation in real-time"""

        feedback_list = []

        try:
            # Use AI to analyze pronunciation
            prompt = f"""
            Analyze the pronunciation quality of this transcribed speech in {session.language}:

            Text: "{audio_segment.text}"
            Language: {session.language}
            Duration: {audio_segment.duration:.2f}s
            Confidence: {audio_segment.confidence:.2f}

            Provide pronunciation analysis including:
            1. Overall pronunciation score (0-100)
            2. Specific pronunciation errors
            3. Phonetic issues to address
            4. Improvement suggestions

            Focus on common {session.language} pronunciation challenges.
            Return as JSON with: score, errors, suggestions, confidence.
            """

            response = await ai_router.generate_response(
                [{"role": "user", "content": prompt}],
                language=session.language,
                provider_preference=["mistral", "deepseek"],  # Cost-optimized
            )

            if response.status == AIResponseStatus.SUCCESS:
                try:
                    # Extract JSON from potentially conversational response
                    json_content = extract_json_from_response(response.content)
                    analysis_data = json.loads(json_content)

                    pronunciation_analysis = PronunciationAnalysis(
                        word=audio_segment.text,
                        phonetic_transcription=analysis_data.get(
                            "phonetic_transcription", ""
                        ),
                        expected_phonemes=analysis_data.get("expected_phonemes", []),
                        actual_phonemes=analysis_data.get("actual_phonemes", []),
                        score=analysis_data.get("score", 0),
                        errors=analysis_data.get("errors", []),
                        suggestions=analysis_data.get("suggestions", []),
                        confidence=analysis_data.get("confidence", 0.5),
                    )

                    # Generate feedback based on score
                    if pronunciation_analysis.score < 60:
                        priority = FeedbackPriority.CRITICAL
                        message = f"Pronunciation needs improvement (Score: {pronunciation_analysis.score:.0f}%)"
                    elif pronunciation_analysis.score < 75:
                        priority = FeedbackPriority.IMPORTANT
                        message = f"Good pronunciation with room for improvement (Score: {pronunciation_analysis.score:.0f}%)"
                    else:
                        priority = FeedbackPriority.MINOR
                        message = f"Excellent pronunciation! (Score: {pronunciation_analysis.score:.0f}%)"

                    feedback = RealTimeFeedback(
                        feedback_id=f"pron_{session.session_id}_{len(session.feedback_history)}",
                        timestamp=datetime.now(),
                        analysis_type=AnalysisType.PRONUNCIATION,
                        priority=priority,
                        message=message,
                        correction=None,
                        explanation="; ".join(pronunciation_analysis.suggestions),
                        pronunciation_data=pronunciation_analysis,
                        grammar_data=None,
                        fluency_data=None,
                        confidence=pronunciation_analysis.confidence,
                        actionable=len(pronunciation_analysis.suggestions) > 0,
                    )

                    feedback_list.append(feedback)
                    session.pronunciation_scores.append(pronunciation_analysis.score)

                except json.JSONDecodeError:
                    logger.warning("Failed to parse pronunciation analysis JSON")

        except Exception as e:
            logger.error(f"Error in pronunciation analysis: {e}")

        return feedback_list

    async def _analyze_grammar(
        self, audio_segment: AudioSegment, session: AnalysisSession
    ) -> List[RealTimeFeedback]:
        """Analyze grammar in real-time"""

        feedback_list = []

        try:
            # Use AI to analyze grammar
            language_rules = self.language_configs.get(session.language, {}).get(
                "grammar_rules", []
            )

            prompt = f"""
            Analyze the grammar of this {session.language} text for language learning feedback:

            Text: "{audio_segment.text}"
            Language: {session.language}
            Focus areas: {", ".join(language_rules)}

            Identify grammar errors and provide:
            1. Error type and position
            2. Severity (critical/important/minor)
            3. Correct version
            4. Simple explanation for language learners
            5. Grammar rule being violated

            Return as JSON array with: error_type, position, severity, correction, explanation, rule, confidence.
            Only include actual errors, not style suggestions.
            """

            response = await ai_router.generate_response(
                [{"role": "user", "content": prompt}],
                language=session.language,
                provider_preference=["mistral", "deepseek"],
            )

            if response.status == AIResponseStatus.SUCCESS:
                try:
                    # Extract JSON from potentially conversational response
                    json_content = extract_json_from_response(response.content)
                    grammar_errors = json.loads(json_content)

                    if isinstance(grammar_errors, list):
                        for error_data in grammar_errors:
                            grammar_issue = GrammarIssue(
                                text=audio_segment.text,
                                error_type=error_data.get(
                                    "error_type", "grammar_error"
                                ),
                                position=(
                                    error_data.get("start", 0),
                                    error_data.get("end", len(audio_segment.text)),
                                ),
                                severity=FeedbackPriority(
                                    error_data.get("severity", "minor")
                                ),
                                correction=error_data.get("correction", ""),
                                explanation=error_data.get("explanation", ""),
                                rule=error_data.get("rule", ""),
                                confidence=error_data.get("confidence", 0.7),
                            )

                            feedback = RealTimeFeedback(
                                feedback_id=f"gram_{session.session_id}_{len(session.feedback_history)}",
                                timestamp=datetime.now(),
                                analysis_type=AnalysisType.GRAMMAR,
                                priority=grammar_issue.severity,
                                message=f"Grammar: {grammar_issue.error_type}",
                                correction=grammar_issue.correction,
                                explanation=grammar_issue.explanation,
                                pronunciation_data=None,
                                grammar_data=grammar_issue,
                                fluency_data=None,
                                confidence=grammar_issue.confidence,
                                actionable=bool(grammar_issue.correction),
                            )

                            feedback_list.append(feedback)

                        # Calculate grammar score
                        if grammar_errors:
                            error_count = len(grammar_errors)
                            word_count = len(audio_segment.text.split())
                            grammar_score = max(
                                0, 100 - (error_count / word_count * 100)
                            )
                            session.grammar_scores.append(grammar_score)
                        else:
                            session.grammar_scores.append(100)

                except json.JSONDecodeError:
                    logger.warning("Failed to parse grammar analysis JSON")

        except Exception as e:
            logger.error(f"Error in grammar analysis: {e}")

        return feedback_list

    async def _analyze_fluency(
        self, audio_segment: AudioSegment, session: AnalysisSession
    ) -> List[RealTimeFeedback]:
        """Analyze fluency metrics in real-time"""

        feedback_list = []

        try:
            # Calculate basic fluency metrics
            word_count = len(audio_segment.text.split())
            duration = audio_segment.duration

            if duration > 0:
                speech_rate = (word_count / duration) * 60  # Words per minute

                # Get expected speech rate for language
                language_config = self.language_configs.get(session.language, {})
                expected_range = language_config.get("expected_speech_rate", (140, 180))

                # Analyze speech patterns
                hesitation_patterns = ["um", "uh", "er", "ah", "like", "you know"]
                hesitation_count = sum(
                    1
                    for pattern in hesitation_patterns
                    if pattern in audio_segment.text.lower()
                )

                # Simple pause detection (this would be enhanced with actual audio analysis)
                pause_count = (
                    audio_segment.text.count("...")
                    + audio_segment.text.count(",")
                    + audio_segment.text.count(".")
                )

                # Calculate confidence based on transcription confidence and hesitations
                confidence_score = audio_segment.confidence * (
                    1 - (hesitation_count / max(word_count, 1))
                )

                fluency_metrics = FluencyMetrics(
                    speech_rate=speech_rate,
                    pause_count=pause_count,
                    pause_duration=0.0,  # Would need audio analysis
                    hesitation_count=hesitation_count,
                    articulation_rate=speech_rate,  # Simplified
                    confidence_score=confidence_score,
                    rhythm_score=0.8,  # Placeholder
                )

                # Generate fluency feedback
                feedback_items = []

                # Speech rate feedback
                if speech_rate < expected_range[0]:
                    feedback_items.append(
                        "Consider speaking a bit faster for more natural flow"
                    )
                elif speech_rate > expected_range[1]:
                    feedback_items.append(
                        "Try slowing down slightly for better clarity"
                    )

                # Hesitation feedback
                if (
                    hesitation_count > word_count * 0.1
                ):  # More than 10% hesitation words
                    feedback_items.append(
                        "Try to reduce filler words like 'um' and 'uh'"
                    )

                # Confidence feedback
                if confidence_score < 0.7:
                    feedback_items.append(
                        "Practice will help build speaking confidence"
                    )

                if feedback_items:
                    feedback = RealTimeFeedback(
                        feedback_id=f"flu_{session.session_id}_{len(session.feedback_history)}",
                        timestamp=datetime.now(),
                        analysis_type=AnalysisType.FLUENCY,
                        priority=FeedbackPriority.SUGGESTION,
                        message="Fluency suggestions",
                        correction=None,
                        explanation="; ".join(feedback_items),
                        pronunciation_data=None,
                        grammar_data=None,
                        fluency_data=fluency_metrics,
                        confidence=0.8,
                        actionable=True,
                    )

                    feedback_list.append(feedback)

                # Update session fluency metrics
                session.current_metrics = fluency_metrics

                # Calculate fluency score
                fluency_score = (
                    (confidence_score * 40)
                    + (min(speech_rate / expected_range[1], 1.0) * 30)
                    + (max(0, 1 - hesitation_count / word_count) * 30)
                )
                session.fluency_scores.append(fluency_score)

        except Exception as e:
            logger.error(f"Error in fluency analysis: {e}")

        return feedback_list

    async def _update_session_metrics(
        self,
        session: AnalysisSession,
        audio_segment: AudioSegment,
        feedback_list: List[RealTimeFeedback],
    ):
        """Update session-level metrics"""

        session.last_update = datetime.now()
        session.total_words += len(audio_segment.text.split())
        session.total_errors += len(
            [
                f
                for f in feedback_list
                if f.priority in [FeedbackPriority.CRITICAL, FeedbackPriority.IMPORTANT]
            ]
        )
        session.feedback_history.extend(feedback_list)

        # Identify improvement areas
        error_types = [
            f.grammar_data.error_type for f in feedback_list if f.grammar_data
        ]
        pronunciation_issues = [
            issue
            for f in feedback_list
            if f.pronunciation_data
            for issue in f.pronunciation_data.errors
        ]

        # Update improvement areas (keep last 10 unique issues)
        all_issues = error_types + [str(issue) for issue in pronunciation_issues]
        session.improvement_areas = list(set(session.improvement_areas + all_issues))[
            -10:
        ]

    async def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for an analysis session"""

        if session_id not in self.active_sessions:
            raise ValueError(f"Analysis session {session_id} not found")

        session = self.active_sessions[session_id]

        # Calculate averages
        avg_pronunciation = safe_mean(session.pronunciation_scores)
        avg_grammar = safe_mean(session.grammar_scores)
        avg_fluency = safe_mean(session.fluency_scores)

        # Calculate improvement trends
        pronunciation_trend = self._calculate_trend(session.pronunciation_scores)
        grammar_trend = self._calculate_trend(session.grammar_scores)
        fluency_trend = self._calculate_trend(session.fluency_scores)

        analytics = {
            "session_info": {
                "session_id": session_id,
                "user_id": session.user_id,
                "language": session.language,
                "duration": (session.last_update - session.start_time).total_seconds(),
                "total_words": session.total_words,
                "total_errors": session.total_errors,
            },
            "performance_metrics": {
                "pronunciation": {
                    "average_score": avg_pronunciation,
                    "trend": pronunciation_trend,
                    "samples": len(session.pronunciation_scores),
                },
                "grammar": {
                    "average_score": avg_grammar,
                    "trend": grammar_trend,
                    "samples": len(session.grammar_scores),
                },
                "fluency": {
                    "average_score": avg_fluency,
                    "trend": fluency_trend,
                    "samples": len(session.fluency_scores),
                    "current_metrics": asdict(session.current_metrics),
                },
            },
            "feedback_summary": {
                "total_feedback": len(session.feedback_history),
                "critical_issues": len(
                    [
                        f
                        for f in session.feedback_history
                        if f.priority == FeedbackPriority.CRITICAL
                    ]
                ),
                "important_issues": len(
                    [
                        f
                        for f in session.feedback_history
                        if f.priority == FeedbackPriority.IMPORTANT
                    ]
                ),
                "suggestions": len(
                    [
                        f
                        for f in session.feedback_history
                        if f.priority == FeedbackPriority.SUGGESTION
                    ]
                ),
            },
            "improvement_areas": session.improvement_areas,
            "overall_score": (avg_pronunciation + avg_grammar + avg_fluency) / 3,
        }

        return analytics

    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend direction for scores"""
        if len(scores) < 3:
            return "insufficient_data"

        recent = scores[-3:]
        earlier = scores[:-3] if len(scores) > 3 else scores

        recent_avg = safe_mean(recent)
        earlier_avg = safe_mean(earlier)

        if recent_avg > earlier_avg + 5:
            return "improving"
        elif recent_avg < earlier_avg - 5:
            return "declining"
        else:
            return "stable"

    async def end_analysis_session(self, session_id: str) -> Dict[str, Any]:
        """End an analysis session and return final analytics"""

        if session_id not in self.active_sessions:
            raise ValueError(f"Analysis session {session_id} not found")

        # Get final analytics
        final_analytics = await self.get_session_analytics(session_id)

        # Clean up session
        del self.active_sessions[session_id]

        logger.info(f"Ended analysis session {session_id}")
        return final_analytics

    async def get_live_feedback(
        self, session_id: str, limit: int = 5
    ) -> List[RealTimeFeedback]:
        """Get recent live feedback for a session"""

        if session_id not in self.active_sessions:
            return []

        session = self.active_sessions[session_id]
        return session.feedback_history[-limit:] if session.feedback_history else []


# Global instance
realtime_analyzer = RealTimeAnalyzer()


# Convenience functions
async def start_realtime_analysis(
    user_id: str, language: str, analysis_types: List[AnalysisType] = None
) -> str:
    """Start real-time analysis session"""
    return await realtime_analyzer.start_analysis_session(
        user_id, language, analysis_types
    )


async def analyze_speech_realtime(
    session_id: str, audio_data: bytes, text: str, confidence: float, language: str
) -> List[RealTimeFeedback]:
    """Analyze speech segment in real-time"""

    audio_segment = AudioSegment(
        audio_data=audio_data,
        text=text,
        start_time=time.time(),
        end_time=time.time() + 1.0,  # Placeholder
        duration=1.0,  # Would be calculated from audio
        language=language,
        confidence=confidence,
    )

    return await realtime_analyzer.analyze_audio_segment(session_id, audio_segment)


async def get_realtime_analytics(session_id: str) -> Dict[str, Any]:
    """Get real-time analytics for session"""
    return await realtime_analyzer.get_session_analytics(session_id)


async def end_realtime_session(session_id: str) -> Dict[str, Any]:
    """End real-time analysis session"""
    return await realtime_analyzer.end_analysis_session(session_id)
