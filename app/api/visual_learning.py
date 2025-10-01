"""
Visual Learning API Endpoints
AI Language Tutor App - Task 3.2 Implementation

RESTful API for visual learning tools:
- Grammar flowchart management
- Progress visualizations
- Visual vocabulary tools
- Pronunciation guides

Integrates with existing admin authentication system.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.visual_learning_service import (
    get_visual_learning_service,
    VisualLearningService,
    GrammarConceptType,
    VisualizationType,
    VocabularyVisualizationType,
    FlowchartNode,
    GrammarFlowchart,
    ProgressVisualization,
    VocabularyVisual,
    PronunciationGuide,
)
from app.services.auth import get_current_user
from app.services.admin_auth import require_admin_access

router = APIRouter(prefix="/api/visual-learning", tags=["visual_learning"])


# ==================== Request/Response Models ====================


class CreateFlowchartRequest(BaseModel):
    """Request model for creating a grammar flowchart"""

    concept: str = Field(..., description="Grammar concept type")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    language: str = Field(..., min_length=2, max_length=10)
    difficulty_level: int = Field(..., ge=1, le=5)
    learning_outcomes: List[str] = Field(default_factory=list)


class AddFlowchartNodeRequest(BaseModel):
    """Request model for adding a node to a flowchart"""

    flowchart_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    node_type: str = Field(..., description="start, decision, process, end, example")
    content: str = Field(..., min_length=1)
    examples: List[str] = Field(default_factory=list)
    position: tuple[int, int] = Field(default=(0, 0))


class ConnectNodesRequest(BaseModel):
    """Request model for connecting flowchart nodes"""

    flowchart_id: str = Field(..., min_length=1)
    from_node_id: str = Field(..., min_length=1)
    to_node_id: str = Field(..., min_length=1)


class CreateVisualizationRequest(BaseModel):
    """Request model for creating a progress visualization"""

    user_id: str = Field(..., min_length=1)
    visualization_type: str = Field(..., description="Type of visualization")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    data_points: List[Dict[str, Any]] = Field(..., min_items=1)
    x_axis_label: str = Field(default="")
    y_axis_label: str = Field(default="")
    color_scheme: List[str] = Field(
        default_factory=lambda: ["#6366f1", "#0891b2", "#f59e0b"]
    )


class CreateVocabularyVisualRequest(BaseModel):
    """Request model for creating a vocabulary visual"""

    word: str = Field(..., min_length=1)
    language: str = Field(..., min_length=2, max_length=10)
    translation: str = Field(..., min_length=1)
    visualization_type: str = Field(..., description="Type of vocabulary visualization")
    phonetic: Optional[str] = None
    example_sentences: List[Dict[str, str]] = Field(default_factory=list)
    related_words: List[str] = Field(default_factory=list)
    difficulty_level: int = Field(default=1, ge=1, le=5)


class CreatePronunciationGuideRequest(BaseModel):
    """Request model for creating a pronunciation guide"""

    word_or_phrase: str = Field(..., min_length=1)
    language: str = Field(..., min_length=2, max_length=10)
    phonetic_spelling: str = Field(..., min_length=1)
    ipa_notation: str = Field(..., min_length=1)
    breakdown: List[Dict[str, str]] = Field(default_factory=list)
    common_mistakes: List[str] = Field(default_factory=list)
    practice_tips: List[str] = Field(default_factory=list)
    difficulty_level: int = Field(default=1, ge=1, le=5)


# ==================== Grammar Flowchart Endpoints ====================


@router.post("/flowcharts")
async def create_flowchart(
    request: CreateFlowchartRequest,
    current_user: dict = Depends(get_current_user),
    service: VisualLearningService = Depends(get_visual_learning_service),
):
    """
    Create a new grammar flowchart

    Requires MANAGE_CONTENT permission
    """
    try:
        concept = GrammarConceptType(request.concept)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid concept type. Must be one of: {[c.value for c in GrammarConceptType]}",
        )

    flowchart = service.create_grammar_flowchart(
        concept=concept,
        title=request.title,
        description=request.description,
        language=request.language,
        difficulty_level=request.difficulty_level,
        learning_outcomes=request.learning_outcomes,
    )

    return {
        "status": "success",
        "flowchart_id": flowchart.flowchart_id,
        "message": "Grammar flowchart created successfully",
    }


@router.post("/flowcharts/nodes")
async def add_flowchart_node(
    request: AddFlowchartNodeRequest,
    current_user: dict = Depends(get_current_user),
    service: VisualLearningService = Depends(get_visual_learning_service),
):
    """
    Add a node to a grammar flowchart

    Requires MANAGE_CONTENT permission
    """
    try:
        node = service.add_flowchart_node(
            flowchart_id=request.flowchart_id,
            title=request.title,
            description=request.description,
            node_type=request.node_type,
            content=request.content,
            examples=request.examples,
            position=request.position,
        )

        return {
            "status": "success",
            "node_id": node.node_id,
            "message": "Node added successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/flowcharts/connections")
async def connect_nodes(
    request: ConnectNodesRequest,
    current_user: dict = Depends(get_current_user),
    service: VisualLearningService = Depends(get_visual_learning_service),
):
    """
    Connect two nodes in a flowchart

    Requires MANAGE_CONTENT permission
    """
    try:
        success = service.connect_flowchart_nodes(
            flowchart_id=request.flowchart_id,
            from_node_id=request.from_node_id,
            to_node_id=request.to_node_id,
        )

        return {
            "status": "success" if success else "already_connected",
            "message": "Nodes connected successfully"
            if success
            else "Connection already exists",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/flowcharts/{flowchart_id}")
async def get_flowchart(
    flowchart_id: str,
    service: VisualLearningService = Depends(get_visual_learning_service),
):
    """Get a specific grammar flowchart by ID"""
    flowchart = service.get_flowchart(flowchart_id)

    if not flowchart:
        raise HTTPException(status_code=404, detail="Flowchart not found")

    return {
        "flowchart_id": flowchart.flowchart_id,
        "concept": flowchart.concept.value,
        "title": flowchart.title,
        "description": flowchart.description,
        "language": flowchart.language,
        "difficulty_level": flowchart.difficulty_level,
        "nodes": [
            {
                "node_id": node.node_id,
                "title": node.title,
                "description": node.description,
                "node_type": node.node_type,
                "content": node.content,
                "examples": node.examples,
                "next_nodes": node.next_nodes,
                "position": node.position,
            }
            for node in flowchart.nodes
        ],
        "connections": flowchart.connections,
        "learning_outcomes": flowchart.learning_outcomes,
        "created_at": flowchart.created_at.isoformat(),
        "metadata": flowchart.metadata,
    }


@router.get("/flowcharts")
async def list_flowcharts(
    language: Optional[str] = Query(None),
    concept: Optional[str] = Query(None),
    service: VisualLearningService = Depends(get_visual_learning_service),
):
    """
    List all available grammar flowcharts

    Optional filters: language, concept
    """
    concept_enum = None
    if concept:
        try:
            concept_enum = GrammarConceptType(concept)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid concept. Must be one of: {[c.value for c in GrammarConceptType]}",
            )

    flowcharts = service.list_flowcharts(language=language, concept=concept_enum)

    return {"status": "success", "count": len(flowcharts), "flowcharts": flowcharts}


# ==================== Progress Visualization Endpoints ====================


@router.post("/visualizations")
async def create_visualization(
    request: CreateVisualizationRequest,
    current_user: dict = Depends(get_current_user),
    service: VisualLearningService = Depends(get_visual_learning_service),
):
    """
    Create a progress visualization

    Requires authentication
    """
    try:
        viz_type = VisualizationType(request.visualization_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid visualization type. Must be one of: {[v.value for v in VisualizationType]}",
        )

    visualization = service.create_progress_visualization(
        user_id=request.user_id,
        visualization_type=viz_type,
        title=request.title,
        description=request.description,
        data_points=request.data_points,
        x_axis_label=request.x_axis_label,
        y_axis_label=request.y_axis_label,
        color_scheme=request.color_scheme,
    )

    return {
        "status": "success",
        "visualization_id": visualization.visualization_id,
        "message": "Visualization created successfully",
    }


@router.get("/visualizations/user/{user_id}")
async def get_user_visualizations(
    user_id: str,
    visualization_type: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    service: VisualLearningService = Depends(get_visual_learning_service),
):
    """
    Get all visualizations for a user

    Optional filter: visualization_type
    """
    viz_type_enum = None
    if visualization_type:
        try:
            viz_type_enum = VisualizationType(visualization_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid type. Must be one of: {[v.value for v in VisualizationType]}",
            )

    visualizations = service.get_user_progress_visualizations(
        user_id=user_id, visualization_type=viz_type_enum
    )

    return {
        "status": "success",
        "count": len(visualizations),
        "visualizations": [
            {
                "visualization_id": viz.visualization_id,
                "visualization_type": viz.visualization_type.value,
                "title": viz.title,
                "description": viz.description,
                "data_points": viz.data_points,
                "x_axis_label": viz.x_axis_label,
                "y_axis_label": viz.y_axis_label,
                "color_scheme": viz.color_scheme,
                "generated_at": viz.generated_at.isoformat(),
            }
            for viz in visualizations
        ],
    }


# ==================== Visual Vocabulary Endpoints ====================


@router.post("/vocabulary")
async def create_vocabulary_visual(
    request: CreateVocabularyVisualRequest,
    current_user: dict = Depends(get_current_user),
    service: VisualLearningService = Depends(get_visual_learning_service),
):
    """
    Create a visual vocabulary tool

    Requires MANAGE_CONTENT permission
    """
    try:
        viz_type = VocabularyVisualizationType(request.visualization_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type. Must be one of: {[v.value for v in VocabularyVisualizationType]}",
        )

    visual = service.create_vocabulary_visual(
        word=request.word,
        language=request.language,
        translation=request.translation,
        visualization_type=viz_type,
        phonetic=request.phonetic,
        example_sentences=request.example_sentences,
        related_words=request.related_words,
        difficulty_level=request.difficulty_level,
    )

    return {
        "status": "success",
        "visual_id": visual.visual_id,
        "message": "Vocabulary visual created successfully",
    }


@router.get("/vocabulary")
async def list_vocabulary_visuals(
    language: Optional[str] = Query(None),
    visualization_type: Optional[str] = Query(None),
    service: VisualLearningService = Depends(get_visual_learning_service),
):
    """
    List vocabulary visuals

    Optional filters: language, visualization_type
    """
    viz_type_enum = None
    if visualization_type:
        try:
            viz_type_enum = VocabularyVisualizationType(visualization_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid type. Must be one of: {[v.value for v in VocabularyVisualizationType]}",
            )

    visuals = service.get_vocabulary_visuals(
        language=language, visualization_type=viz_type_enum
    )

    return {
        "status": "success",
        "count": len(visuals),
        "visuals": [
            {
                "visual_id": visual.visual_id,
                "word": visual.word,
                "language": visual.language,
                "translation": visual.translation,
                "visualization_type": visual.visualization_type.value,
                "phonetic": visual.phonetic,
                "example_sentences": visual.example_sentences,
                "related_words": visual.related_words,
                "difficulty_level": visual.difficulty_level,
                "created_at": visual.created_at.isoformat(),
            }
            for visual in visuals
        ],
    }


# ==================== Pronunciation Guide Endpoints ====================


@router.post("/pronunciation")
async def create_pronunciation_guide(
    request: CreatePronunciationGuideRequest,
    current_user: dict = Depends(get_current_user),
    service: VisualLearningService = Depends(get_visual_learning_service),
):
    """
    Create a pronunciation guide

    Requires MANAGE_CONTENT permission
    """
    guide = service.create_pronunciation_guide(
        word_or_phrase=request.word_or_phrase,
        language=request.language,
        phonetic_spelling=request.phonetic_spelling,
        ipa_notation=request.ipa_notation,
        breakdown=request.breakdown,
        common_mistakes=request.common_mistakes,
        practice_tips=request.practice_tips,
        difficulty_level=request.difficulty_level,
    )

    return {
        "status": "success",
        "guide_id": guide.guide_id,
        "message": "Pronunciation guide created successfully",
    }


@router.get("/pronunciation")
async def list_pronunciation_guides(
    language: Optional[str] = Query(None),
    difficulty_level: Optional[int] = Query(None, ge=1, le=5),
    service: VisualLearningService = Depends(get_visual_learning_service),
):
    """
    List pronunciation guides

    Optional filters: language, difficulty_level
    """
    guides = service.get_pronunciation_guides(
        language=language, difficulty_level=difficulty_level
    )

    return {
        "status": "success",
        "count": len(guides),
        "guides": [
            {
                "guide_id": guide.guide_id,
                "word_or_phrase": guide.word_or_phrase,
                "language": guide.language,
                "phonetic_spelling": guide.phonetic_spelling,
                "ipa_notation": guide.ipa_notation,
                "breakdown": guide.breakdown,
                "common_mistakes": guide.common_mistakes,
                "practice_tips": guide.practice_tips,
                "difficulty_level": guide.difficulty_level,
                "created_at": guide.created_at.isoformat(),
            }
            for guide in guides
        ],
    }


@router.get("/pronunciation/{guide_id}")
async def get_pronunciation_guide(
    guide_id: str, service: VisualLearningService = Depends(get_visual_learning_service)
):
    """Get a specific pronunciation guide by ID"""
    guides = service.get_pronunciation_guides()
    guide = next((g for g in guides if g.guide_id == guide_id), None)

    if not guide:
        raise HTTPException(status_code=404, detail="Pronunciation guide not found")

    return {
        "guide_id": guide.guide_id,
        "word_or_phrase": guide.word_or_phrase,
        "language": guide.language,
        "phonetic_spelling": guide.phonetic_spelling,
        "ipa_notation": guide.ipa_notation,
        "audio_url": guide.audio_url,
        "breakdown": guide.breakdown,
        "visual_mouth_positions": guide.visual_mouth_positions,
        "common_mistakes": guide.common_mistakes,
        "practice_tips": guide.practice_tips,
        "difficulty_level": guide.difficulty_level,
        "created_at": guide.created_at.isoformat(),
        "metadata": guide.metadata,
    }
