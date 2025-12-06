"""
Real-Time Analysis API Endpoints for AI Language Tutor App

This module provides REST API endpoints for real-time language analysis including:
- Starting/ending analysis sessions
- Real-time speech analysis
- Live feedback delivery
- Performance analytics
- Progress tracking

Features:
- WebSocket support for real-time feedback
- RESTful API for session management
- Real-time pronunciation analysis
- Grammar correction endpoints
- Fluency metrics API
- Analytics dashboard endpoints
"""

import base64
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.models.database import User
from app.services.auth import get_current_user
from app.services.realtime_analyzer import (
    AnalysisType,
    analyze_speech_realtime,
    end_realtime_session,
    get_realtime_analytics,
    realtime_analyzer,
    start_realtime_analysis,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/realtime", tags=["Real-Time Analysis"])


# Request/Response Models
class StartAnalysisRequest(BaseModel):
    """Request to start real-time analysis"""

    language: str = Field(..., description="Target language for analysis")
    analysis_types: List[str] = Field(
        default=["comprehensive"], description="Types of analysis to perform"
    )
    user_preferences: Dict[str, Any] = Field(
        default_factory=dict, description="User preferences for analysis"
    )


class StartAnalysisResponse(BaseModel):
    """Response for starting analysis session"""

    session_id: str
    user_id: str
    language: str
    analysis_types: List[str]
    started_at: datetime
    status: str = "active"


class AnalyzeAudioRequest(BaseModel):
    """Request to analyze audio segment"""

    session_id: str = Field(..., description="Analysis session ID")
    audio_data: str = Field(..., description="Base64 encoded audio data")
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Transcription confidence"
    )
    timestamp: datetime = Field(default_factory=datetime.now)


class FeedbackResponse(BaseModel):
    """Real-time feedback response"""

    feedback_id: str
    timestamp: datetime
    analysis_type: str
    priority: str
    message: str
    correction: Optional[str]
    explanation: str
    confidence: float
    actionable: bool

    # Detailed analysis data
    pronunciation_score: Optional[float] = None
    grammar_errors: Optional[List[Dict[str, Any]]] = None
    fluency_metrics: Optional[Dict[str, Any]] = None


class AnalyticsResponse(BaseModel):
    """Analytics response model"""

    session_info: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    feedback_summary: Dict[str, Any]
    improvement_areas: List[str]
    overall_score: float


class WebSocketManager:
    """Manage WebSocket connections for real-time feedback"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, List[str]] = {}

    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Connect a WebSocket client"""
        await websocket.accept()
        connection_id = f"{user_id}_{session_id}_{datetime.now().timestamp()}"
        self.active_connections[connection_id] = websocket

        if session_id not in self.session_connections:
            self.session_connections[session_id] = []
        self.session_connections[session_id].append(connection_id)

        logger.info(f"WebSocket connected: {connection_id}")
        return connection_id

    def disconnect(self, connection_id: str, session_id: str):
        """Disconnect a WebSocket client"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        if session_id in self.session_connections:
            self.session_connections[session_id] = [
                conn
                for conn in self.session_connections[session_id]
                if conn != connection_id
            ]
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]

        logger.info(f"WebSocket disconnected: {connection_id}")

    async def send_feedback(self, session_id: str, feedback_data: Dict[str, Any]):
        """Send feedback to all connections for a session"""
        if session_id in self.session_connections:
            disconnected = []
            for connection_id in self.session_connections[session_id]:
                if connection_id in self.active_connections:
                    try:
                        websocket = self.active_connections[connection_id]
                        await websocket.send_json(feedback_data)
                    except Exception as e:
                        logger.warning(
                            f"Failed to send feedback to {connection_id}: {e}"
                        )
                        disconnected.append(connection_id)

            # Clean up disconnected connections
            for connection_id in disconnected:
                self.disconnect(connection_id, session_id)


# Global WebSocket manager
websocket_manager = WebSocketManager()


# REST API Endpoints


@router.post("/start", response_model=StartAnalysisResponse)
async def start_analysis_session(
    request: StartAnalysisRequest, current_user: User = Depends(get_current_user)
):
    """Start a new real-time analysis session"""

    try:
        # Convert analysis type strings to enums
        analysis_types = []
        for analysis_type in request.analysis_types:
            try:
                analysis_types.append(AnalysisType(analysis_type))
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid analysis type: {analysis_type}"
                )

        # Start analysis session
        session_id = await start_realtime_analysis(
            user_id=str(current_user.id),
            language=request.language,
            analysis_types=analysis_types,
        )

        response = StartAnalysisResponse(
            session_id=session_id,
            user_id=str(current_user.id),
            language=request.language,
            analysis_types=request.analysis_types,
            started_at=datetime.now(),
        )

        logger.info(f"Started analysis session {session_id} for user {current_user.id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting analysis session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=List[FeedbackResponse])
def _decode_audio_data(audio_data: str) -> bytes:
    """Decode base64 audio data"""
    try:
        return base64.b64decode(audio_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid audio data: {e}")


def _get_session_data(session_id: str):
    """Get and validate session data"""
    session_data = realtime_analyzer.active_sessions.get(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Analysis session not found")
    return session_data


def _create_base_feedback_response(feedback) -> FeedbackResponse:
    """Create base feedback response object"""
    return FeedbackResponse(
        feedback_id=feedback.feedback_id,
        timestamp=feedback.timestamp,
        analysis_type=feedback.analysis_type.value,
        priority=feedback.priority.value,
        message=feedback.message,
        correction=feedback.correction,
        explanation=feedback.explanation,
        confidence=feedback.confidence,
        actionable=feedback.actionable,
    )


def _add_specific_feedback_data(feedback_response: FeedbackResponse, feedback):
    """Add specific analysis data to feedback response"""
    if feedback.pronunciation_data:
        feedback_response.pronunciation_score = feedback.pronunciation_data.score

    if feedback.grammar_data:
        feedback_response.grammar_errors = [
            {
                "error_type": feedback.grammar_data.error_type,
                "correction": feedback.grammar_data.correction,
                "explanation": feedback.grammar_data.explanation,
                "confidence": feedback.grammar_data.confidence,
            }
        ]

    if feedback.fluency_data:
        feedback_response.fluency_metrics = {
            "speech_rate": feedback.fluency_data.speech_rate,
            "confidence_score": feedback.fluency_data.confidence_score,
            "hesitation_count": feedback.fluency_data.hesitation_count,
        }


def _convert_feedback_to_responses(feedback_list) -> List[FeedbackResponse]:
    """Convert feedback list to response format"""
    response_list = []
    for feedback in feedback_list:
        feedback_response = _create_base_feedback_response(feedback)
        _add_specific_feedback_data(feedback_response, feedback)
        response_list.append(feedback_response)
    return response_list


async def _send_websocket_feedback(
    session_id: str, response_list: List[FeedbackResponse]
):
    """Send feedback via WebSocket if connected"""
    if response_list:
        websocket_data = {
            "type": "realtime_feedback",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "feedback": [
                feedback_response.model_dump() for feedback_response in response_list
            ],
        }
        await websocket_manager.send_feedback(session_id, websocket_data)


async def analyze_audio_segment(
    request: AnalyzeAudioRequest, current_user: User = Depends(get_current_user)
):
    """Analyze an audio segment and return real-time feedback"""
    try:
        audio_data = _decode_audio_data(request.audio_data)
        session_data = _get_session_data(request.session_id)

        feedback_list = await analyze_speech_realtime(
            session_id=request.session_id,
            audio_data=audio_data,
            text=request.text,
            confidence=request.confidence,
            language=session_data.language,
        )

        response_list = _convert_feedback_to_responses(feedback_list)
        await _send_websocket_feedback(request.session_id, response_list)

        logger.debug(
            f"Analyzed audio for session {request.session_id}: {len(response_list)} feedback items"
        )
        return response_list

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing audio segment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/{session_id}", response_model=AnalyticsResponse)
async def get_session_analytics(
    session_id: str, current_user: User = Depends(get_current_user)
):
    """Get comprehensive analytics for an analysis session"""

    try:
        analytics = await get_realtime_analytics(session_id)

        # Verify user owns this session
        if analytics["session_info"]["user_id"] != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied to this session")

        response = AnalyticsResponse(
            session_info=analytics["session_info"],
            performance_metrics=analytics["performance_metrics"],
            feedback_summary=analytics["feedback_summary"],
            improvement_areas=analytics["improvement_areas"],
            overall_score=analytics["overall_score"],
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/end/{session_id}")
async def end_analysis_session(
    session_id: str, current_user: User = Depends(get_current_user)
):
    """End a real-time analysis session"""

    try:
        final_analytics = await end_realtime_session(session_id)

        # Verify user owns this session
        if final_analytics["session_info"]["user_id"] != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied to this session")

        # Notify WebSocket clients
        websocket_data = {
            "type": "session_ended",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "final_analytics": final_analytics,
        }
        await websocket_manager.send_feedback(session_id, websocket_data)

        logger.info(f"Ended analysis session {session_id}")
        return {
            "status": "ended",
            "session_id": session_id,
            "final_analytics": final_analytics,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending analysis session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/{session_id}")
async def get_recent_feedback(
    session_id: str, limit: int = 10, current_user: User = Depends(get_current_user)
):
    """Get recent feedback for a session"""

    try:
        # Verify session exists and user has access
        session_data = realtime_analyzer.active_sessions.get(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Analysis session not found")

        if session_data.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied to this session")

        feedback_list = await realtime_analyzer.get_live_feedback(session_id, limit)

        # Convert to response format
        response_list = []
        for feedback in feedback_list:
            feedback_response = FeedbackResponse(
                feedback_id=feedback.feedback_id,
                timestamp=feedback.timestamp,
                analysis_type=feedback.analysis_type.value,
                priority=feedback.priority.value,
                message=feedback.message,
                correction=feedback.correction,
                explanation=feedback.explanation,
                confidence=feedback.confidence,
                actionable=feedback.actionable,
            )
            response_list.append(feedback_response)

        return response_list

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recent feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket Endpoint


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time feedback delivery"""

    connection_id = None

    try:
        # For simplicity, we'll accept the connection without full auth
        # In production, you'd want to validate the session and user
        connection_id = await websocket_manager.connect(websocket, session_id, "user")

        await websocket.send_json(
            {
                "type": "connected",
                "session_id": session_id,
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                message = await websocket.receive_json()

                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_json(
                        {"type": "pong", "timestamp": datetime.now().isoformat()}
                    )

                elif message.get("type") == "request_analytics":
                    # Send current analytics
                    try:
                        analytics = await get_realtime_analytics(session_id)
                        await websocket.send_json(
                            {
                                "type": "analytics_update",
                                "session_id": session_id,
                                "analytics": analytics,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                    except Exception as e:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": f"Failed to get analytics: {e}",
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error for {connection_id}: {e}")
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        if connection_id:
            websocket_manager.disconnect(connection_id, session_id)


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for real-time analysis service"""

    return {
        "status": "healthy",
        "service": "realtime_analysis",
        "active_sessions": len(realtime_analyzer.active_sessions),
        "active_websockets": len(websocket_manager.active_connections),
        "timestamp": datetime.now().isoformat(),
    }
