"""
Visual Learning Service
AI Language Tutor App - Task 3.2 Implementation

Provides comprehensive visual learning tools:
- Interactive grammar flowcharts
- Progress visualization and charts
- Visual vocabulary tools
- Interactive pronunciation guides
- Learning path visualizations

Integrates with existing learning analytics and progress tracking systems.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class VisualizationType(Enum):
    """Types of visualizations available"""

    FLOWCHART = "flowchart"
    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    PROGRESS_BAR = "progress_bar"
    HEATMAP = "heatmap"
    NETWORK_DIAGRAM = "network_diagram"
    TIMELINE = "timeline"


class GrammarConceptType(Enum):
    """Grammar concept categories"""

    VERB_CONJUGATION = "verb_conjugation"
    SENTENCE_STRUCTURE = "sentence_structure"
    TENSE_USAGE = "tense_usage"
    CONDITIONAL_FORMS = "conditional_forms"
    PRONOUN_USAGE = "pronoun_usage"
    ARTICLE_RULES = "article_rules"
    PREPOSITIONS = "prepositions"
    ADJECTIVE_AGREEMENT = "adjective_agreement"


class VocabularyVisualizationType(Enum):
    """Vocabulary visualization types"""

    WORD_CLOUD = "word_cloud"
    SEMANTIC_MAP = "semantic_map"
    ETYMOLOGY_TREE = "etymology_tree"
    FREQUENCY_CHART = "frequency_chart"
    CONTEXT_EXAMPLES = "context_examples"
    ASSOCIATION_NETWORK = "association_network"


@dataclass
class FlowchartNode:
    """Represents a node in a grammar flowchart"""

    node_id: str
    title: str
    description: str
    node_type: str  # "start", "decision", "process", "end", "example"
    content: str
    examples: List[str] = field(default_factory=list)
    next_nodes: List[str] = field(default_factory=list)
    position: Tuple[int, int] = (0, 0)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GrammarFlowchart:
    """Interactive grammar flowchart structure"""

    flowchart_id: str
    concept: GrammarConceptType
    title: str
    description: str
    language: str
    difficulty_level: int  # 1-5
    nodes: List[FlowchartNode] = field(default_factory=list)
    connections: List[Tuple[str, str]] = field(default_factory=list)
    learning_outcomes: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProgressVisualization:
    """Progress visualization data structure"""

    visualization_id: str
    user_id: str
    visualization_type: VisualizationType
    title: str
    description: str
    data_points: List[Dict[str, Any]] = field(default_factory=list)
    x_axis_label: str = ""
    y_axis_label: str = ""
    color_scheme: List[str] = field(
        default_factory=lambda: ["#6366f1", "#0891b2", "#f59e0b"]
    )
    generated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VocabularyVisual:
    """Visual vocabulary learning tool"""

    visual_id: str
    word: str
    language: str
    translation: str
    visualization_type: VocabularyVisualizationType
    visual_data: Dict[str, Any] = field(default_factory=dict)
    phonetic: Optional[str] = None
    audio_url: Optional[str] = None
    images: List[str] = field(default_factory=list)
    example_sentences: List[Dict[str, str]] = field(default_factory=list)
    related_words: List[str] = field(default_factory=list)
    difficulty_level: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PronunciationGuide:
    """Interactive pronunciation guide"""

    guide_id: str
    word_or_phrase: str
    language: str
    phonetic_spelling: str
    ipa_notation: str
    audio_url: Optional[str] = None
    breakdown: List[Dict[str, str]] = field(default_factory=list)  # syllable breakdown
    visual_mouth_positions: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)
    practice_tips: List[str] = field(default_factory=list)
    difficulty_level: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class VisualLearningService:
    """
    Core service for visual learning tools management

    Provides:
    - Grammar flowchart generation and management
    - Progress visualization creation
    - Visual vocabulary tools
    - Interactive pronunciation guides
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize visual learning service"""
        self.data_dir = data_dir or Path("data/visual_learning")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Storage paths
        self.flowcharts_dir = self.data_dir / "flowcharts"
        self.visualizations_dir = self.data_dir / "visualizations"
        self.vocabulary_dir = self.data_dir / "vocabulary"
        self.pronunciation_dir = self.data_dir / "pronunciation"

        for directory in [
            self.flowcharts_dir,
            self.visualizations_dir,
            self.vocabulary_dir,
            self.pronunciation_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        logger.info("VisualLearningService initialized")

    # ==================== Grammar Flowcharts ====================

    def create_grammar_flowchart(
        self,
        concept: GrammarConceptType,
        title: str,
        description: str,
        language: str,
        difficulty_level: int,
        learning_outcomes: Optional[List[str]] = None,
    ) -> GrammarFlowchart:
        """
        Create a new grammar flowchart

        Args:
            concept: Grammar concept type
            title: Flowchart title
            description: Detailed description
            language: Target language
            difficulty_level: 1-5 difficulty rating
            learning_outcomes: Expected learning outcomes

        Returns:
            Created GrammarFlowchart object
        """
        flowchart_id = f"flowchart_{language}_{concept.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        flowchart = GrammarFlowchart(
            flowchart_id=flowchart_id,
            concept=concept,
            title=title,
            description=description,
            language=language,
            difficulty_level=difficulty_level,
            learning_outcomes=learning_outcomes or [],
            nodes=[],
            connections=[],
            metadata={"version": "1.0"},
        )

        self._save_flowchart(flowchart)
        logger.info(f"Created grammar flowchart: {flowchart_id}")
        return flowchart

    def add_flowchart_node(
        self,
        flowchart_id: str,
        title: str,
        description: str,
        node_type: str,
        content: str,
        examples: Optional[List[str]] = None,
        position: Tuple[int, int] = (0, 0),
    ) -> FlowchartNode:
        """Add a node to a grammar flowchart"""
        flowchart = self.get_flowchart(flowchart_id)
        if not flowchart:
            raise ValueError(f"Flowchart not found: {flowchart_id}")

        node_id = f"node_{len(flowchart.nodes) + 1}"
        node = FlowchartNode(
            node_id=node_id,
            title=title,
            description=description,
            node_type=node_type,
            content=content,
            examples=examples or [],
            position=position,
        )

        flowchart.nodes.append(node)
        self._save_flowchart(flowchart)
        logger.info(f"Added node {node_id} to flowchart {flowchart_id}")
        return node

    def connect_flowchart_nodes(
        self, flowchart_id: str, from_node_id: str, to_node_id: str
    ) -> bool:
        """Connect two nodes in a flowchart"""
        flowchart = self.get_flowchart(flowchart_id)
        if not flowchart:
            raise ValueError(f"Flowchart not found: {flowchart_id}")

        # Add connection
        connection = (from_node_id, to_node_id)
        if connection not in flowchart.connections:
            flowchart.connections.append(connection)

            # Update node's next_nodes list
            for node in flowchart.nodes:
                if node.node_id == from_node_id:
                    if to_node_id not in node.next_nodes:
                        node.next_nodes.append(to_node_id)
                    break

            self._save_flowchart(flowchart)
            logger.info(f"Connected nodes: {from_node_id} -> {to_node_id}")
            return True

        return False

    def get_flowchart(self, flowchart_id: str) -> Optional[GrammarFlowchart]:
        """Retrieve a grammar flowchart by ID"""
        file_path = self.flowcharts_dir / f"{flowchart_id}.json"
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Reconstruct flowchart object
            flowchart = GrammarFlowchart(
                flowchart_id=data["flowchart_id"],
                concept=GrammarConceptType(data["concept"]),
                title=data["title"],
                description=data["description"],
                language=data["language"],
                difficulty_level=data["difficulty_level"],
                nodes=[FlowchartNode(**node) for node in data.get("nodes", [])],
                connections=[tuple(conn) for conn in data.get("connections", [])],
                learning_outcomes=data.get("learning_outcomes", []),
                created_at=datetime.fromisoformat(data["created_at"]),
                metadata=data.get("metadata", {}),
            )

            return flowchart
        except Exception as e:
            logger.error(f"Error loading flowchart {flowchart_id}: {e}")
            return None

    def list_flowcharts(
        self,
        language: Optional[str] = None,
        concept: Optional[GrammarConceptType] = None,
    ) -> List[Dict[str, Any]]:
        """List all available flowcharts with optional filtering"""
        flowcharts = []

        for file_path in self.flowcharts_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Apply filters
                if language and data.get("language") != language:
                    continue
                if concept and data.get("concept") != concept.value:
                    continue

                flowcharts.append(
                    {
                        "flowchart_id": data["flowchart_id"],
                        "title": data["title"],
                        "concept": data["concept"],
                        "language": data["language"],
                        "difficulty_level": data["difficulty_level"],
                        "node_count": len(data.get("nodes", [])),
                        "created_at": data["created_at"],
                    }
                )
            except Exception as e:
                logger.error(f"Error reading flowchart {file_path}: {e}")

        return flowcharts

    # ==================== Progress Visualizations ====================

    def create_progress_visualization(
        self,
        user_id: str,
        visualization_type: VisualizationType,
        title: str,
        description: str,
        data_points: List[Dict[str, Any]],
        x_axis_label: str = "",
        y_axis_label: str = "",
        color_scheme: Optional[List[str]] = None,
    ) -> ProgressVisualization:
        """Create a progress visualization"""
        visualization_id = f"viz_{user_id}_{visualization_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        visualization = ProgressVisualization(
            visualization_id=visualization_id,
            user_id=user_id,
            visualization_type=visualization_type,
            title=title,
            description=description,
            data_points=data_points,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            color_scheme=color_scheme or ["#6366f1", "#0891b2", "#f59e0b"],
        )

        self._save_visualization(visualization)
        logger.info(f"Created progress visualization: {visualization_id}")
        return visualization

    def get_user_progress_visualizations(
        self, user_id: str, visualization_type: Optional[VisualizationType] = None
    ) -> List[ProgressVisualization]:
        """Get all progress visualizations for a user"""
        visualizations = []

        for file_path in self.visualizations_dir.glob(f"viz_{user_id}_*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                viz = ProgressVisualization(
                    visualization_id=data["visualization_id"],
                    user_id=data["user_id"],
                    visualization_type=VisualizationType(data["visualization_type"]),
                    title=data["title"],
                    description=data["description"],
                    data_points=data.get("data_points", []),
                    x_axis_label=data.get("x_axis_label", ""),
                    y_axis_label=data.get("y_axis_label", ""),
                    color_scheme=data.get("color_scheme", []),
                    generated_at=datetime.fromisoformat(data["generated_at"]),
                    metadata=data.get("metadata", {}),
                )

                if (
                    visualization_type is None
                    or viz.visualization_type == visualization_type
                ):
                    visualizations.append(viz)
            except Exception as e:
                logger.error(f"Error loading visualization {file_path}: {e}")

        return visualizations

    # ==================== Visual Vocabulary Tools ====================

    def create_vocabulary_visual(
        self,
        word: str,
        language: str,
        translation: str,
        visualization_type: VocabularyVisualizationType,
        phonetic: Optional[str] = None,
        example_sentences: Optional[List[Dict[str, str]]] = None,
        related_words: Optional[List[str]] = None,
        difficulty_level: int = 1,
    ) -> VocabularyVisual:
        """Create a visual vocabulary learning tool"""
        visual_id = f"vocab_{language}_{word.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        visual = VocabularyVisual(
            visual_id=visual_id,
            word=word,
            language=language,
            translation=translation,
            visualization_type=visualization_type,
            phonetic=phonetic,
            example_sentences=example_sentences or [],
            related_words=related_words or [],
            difficulty_level=difficulty_level,
        )

        self._save_vocabulary_visual(visual)
        logger.info(f"Created vocabulary visual: {visual_id}")
        return visual

    def get_vocabulary_visuals(
        self,
        language: Optional[str] = None,
        visualization_type: Optional[VocabularyVisualizationType] = None,
    ) -> List[VocabularyVisual]:
        """Get vocabulary visuals with optional filtering"""
        visuals = []

        for file_path in self.vocabulary_dir.glob("vocab_*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                visual = VocabularyVisual(
                    visual_id=data["visual_id"],
                    word=data["word"],
                    language=data["language"],
                    translation=data["translation"],
                    visualization_type=VocabularyVisualizationType(
                        data["visualization_type"]
                    ),
                    visual_data=data.get("visual_data", {}),
                    phonetic=data.get("phonetic"),
                    audio_url=data.get("audio_url"),
                    images=data.get("images", []),
                    example_sentences=data.get("example_sentences", []),
                    related_words=data.get("related_words", []),
                    difficulty_level=data.get("difficulty_level", 1),
                    created_at=datetime.fromisoformat(data["created_at"]),
                    metadata=data.get("metadata", {}),
                )

                if (language is None or visual.language == language) and (
                    visualization_type is None
                    or visual.visualization_type == visualization_type
                ):
                    visuals.append(visual)
            except Exception as e:
                logger.error(f"Error loading vocabulary visual {file_path}: {e}")

        return visuals

    # ==================== Pronunciation Guides ====================

    def create_pronunciation_guide(
        self,
        word_or_phrase: str,
        language: str,
        phonetic_spelling: str,
        ipa_notation: str,
        breakdown: Optional[List[Dict[str, str]]] = None,
        common_mistakes: Optional[List[str]] = None,
        practice_tips: Optional[List[str]] = None,
        difficulty_level: int = 1,
    ) -> PronunciationGuide:
        """Create an interactive pronunciation guide"""
        guide_id = f"pronunciation_{language}_{word_or_phrase.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        guide = PronunciationGuide(
            guide_id=guide_id,
            word_or_phrase=word_or_phrase,
            language=language,
            phonetic_spelling=phonetic_spelling,
            ipa_notation=ipa_notation,
            breakdown=breakdown or [],
            common_mistakes=common_mistakes or [],
            practice_tips=practice_tips or [],
            difficulty_level=difficulty_level,
        )

        self._save_pronunciation_guide(guide)
        logger.info(f"Created pronunciation guide: {guide_id}")
        return guide

    def get_pronunciation_guides(
        self, language: Optional[str] = None, difficulty_level: Optional[int] = None
    ) -> List[PronunciationGuide]:
        """Get pronunciation guides with optional filtering"""
        guides = []

        for file_path in self.pronunciation_dir.glob("pronunciation_*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                guide = PronunciationGuide(
                    guide_id=data["guide_id"],
                    word_or_phrase=data["word_or_phrase"],
                    language=data["language"],
                    phonetic_spelling=data["phonetic_spelling"],
                    ipa_notation=data["ipa_notation"],
                    audio_url=data.get("audio_url"),
                    breakdown=data.get("breakdown", []),
                    visual_mouth_positions=data.get("visual_mouth_positions", []),
                    common_mistakes=data.get("common_mistakes", []),
                    practice_tips=data.get("practice_tips", []),
                    difficulty_level=data.get("difficulty_level", 1),
                    created_at=datetime.fromisoformat(data["created_at"]),
                    metadata=data.get("metadata", {}),
                )

                if (language is None or guide.language == language) and (
                    difficulty_level is None
                    or guide.difficulty_level == difficulty_level
                ):
                    guides.append(guide)
            except Exception as e:
                logger.error(f"Error loading pronunciation guide {file_path}: {e}")

        return guides

    # ==================== Helper Methods ====================

    def _save_flowchart(self, flowchart: GrammarFlowchart) -> None:
        """Save flowchart to file"""
        self.flowcharts_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.flowcharts_dir / f"{flowchart.flowchart_id}.json"

        # Convert to serializable format
        data = {
            "flowchart_id": flowchart.flowchart_id,
            "concept": flowchart.concept.value,
            "title": flowchart.title,
            "description": flowchart.description,
            "language": flowchart.language,
            "difficulty_level": flowchart.difficulty_level,
            "nodes": [asdict(node) for node in flowchart.nodes],
            "connections": flowchart.connections,
            "learning_outcomes": flowchart.learning_outcomes,
            "created_at": flowchart.created_at.isoformat(),
            "metadata": flowchart.metadata,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_visualization(self, visualization: ProgressVisualization) -> None:
        """Save visualization to file"""
        self.visualizations_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.visualizations_dir / f"{visualization.visualization_id}.json"

        data = {
            "visualization_id": visualization.visualization_id,
            "user_id": visualization.user_id,
            "visualization_type": visualization.visualization_type.value,
            "title": visualization.title,
            "description": visualization.description,
            "data_points": visualization.data_points,
            "x_axis_label": visualization.x_axis_label,
            "y_axis_label": visualization.y_axis_label,
            "color_scheme": visualization.color_scheme,
            "generated_at": visualization.generated_at.isoformat(),
            "metadata": visualization.metadata,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_vocabulary_visual(self, visual: VocabularyVisual) -> None:
        """Save vocabulary visual to file"""
        self.vocabulary_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.vocabulary_dir / f"{visual.visual_id}.json"

        data = {
            "visual_id": visual.visual_id,
            "word": visual.word,
            "language": visual.language,
            "translation": visual.translation,
            "visualization_type": visual.visualization_type.value,
            "visual_data": visual.visual_data,
            "phonetic": visual.phonetic,
            "audio_url": visual.audio_url,
            "images": visual.images,
            "example_sentences": visual.example_sentences,
            "related_words": visual.related_words,
            "difficulty_level": visual.difficulty_level,
            "created_at": visual.created_at.isoformat(),
            "metadata": visual.metadata,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_pronunciation_guide(self, guide: PronunciationGuide) -> None:
        """Save pronunciation guide to file"""
        self.pronunciation_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.pronunciation_dir / f"{guide.guide_id}.json"

        data = {
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

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# Global service instance
_visual_learning_service = None


def get_visual_learning_service() -> VisualLearningService:
    """Get or create the global visual learning service instance"""
    global _visual_learning_service
    if _visual_learning_service is None:
        _visual_learning_service = VisualLearningService()
    return _visual_learning_service
