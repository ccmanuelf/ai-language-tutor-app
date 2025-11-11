"""
Comprehensive tests for Visual Learning Service
Targeting 100% code coverage

Test Coverage:
- Enum classes (3 enums)
- Dataclass models (5 dataclasses)
- Service initialization and directory creation
- Grammar flowchart operations (CRUD)
- Progress visualization operations (CRUD)
- Vocabulary visual operations (CRUD)
- Pronunciation guide operations (CRUD)
- File storage and retrieval (JSON operations)
- Error handling and edge cases
- Global instance management
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock, mock_open, patch

import pytest

from app.services.visual_learning_service import (
    FlowchartNode,
    GrammarConceptType,
    GrammarFlowchart,
    ProgressVisualization,
    PronunciationGuide,
    VisualizationType,
    VisualLearningService,
    VocabularyVisual,
    VocabularyVisualizationType,
    get_visual_learning_service,
)

# ==================== Test Fixtures ====================


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def service(temp_dir):
    """Create service instance with temporary directory"""
    return VisualLearningService(data_dir=temp_dir)


@pytest.fixture
def sample_flowchart(service):
    """Create a sample grammar flowchart"""
    return service.create_grammar_flowchart(
        concept=GrammarConceptType.VERB_CONJUGATION,
        title="French Verb Conjugation",
        description="Learn French verb conjugation patterns",
        language="french",
        difficulty_level=3,
        learning_outcomes=["Understand present tense", "Apply conjugation rules"],
    )


@pytest.fixture
def sample_visualization(service):
    """Create a sample progress visualization"""
    return service.create_progress_visualization(
        user_id="user123",
        visualization_type=VisualizationType.LINE_CHART,
        title="Weekly Progress",
        description="Track learning progress over time",
        data_points=[
            {"date": "2025-01-01", "score": 75},
            {"date": "2025-01-02", "score": 82},
        ],
        x_axis_label="Date",
        y_axis_label="Score",
        color_scheme=["#ff0000", "#00ff00"],
    )


@pytest.fixture
def sample_vocabulary_visual(service):
    """Create a sample vocabulary visual"""
    return service.create_vocabulary_visual(
        word="bonjour",
        language="french",
        translation="hello",
        visualization_type=VocabularyVisualizationType.WORD_CLOUD,
        phonetic="bon-zhoor",
        example_sentences=[
            {"french": "Bonjour!", "english": "Hello!"},
            {
                "french": "Bonjour, comment allez-vous?",
                "english": "Hello, how are you?",
            },
        ],
        related_words=["salut", "allô"],
        difficulty_level=1,
    )


@pytest.fixture
def sample_pronunciation_guide(service):
    """Create a sample pronunciation guide"""
    return service.create_pronunciation_guide(
        word_or_phrase="je t'aime",
        language="french",
        phonetic_spelling="zhuh tem",
        ipa_notation="ʒə tɛm",
        breakdown=[
            {"syllable": "je", "ipa": "ʒə", "tips": "Soft 'j' sound"},
            {"syllable": "t'aime", "ipa": "tɛm", "tips": "Silent 'e'"},
        ],
        common_mistakes=["Pronouncing the 'e' at the end", "Hard 'j' sound"],
        practice_tips=["Practice soft 'zh' sound", "Connect words smoothly"],
        difficulty_level=2,
    )


# ==================== Test Enum Classes ====================


class TestVisualizationTypeEnum:
    """Test VisualizationType enum"""

    def test_visualization_type_values(self):
        """Test all visualization type enum values"""
        assert VisualizationType.FLOWCHART.value == "flowchart"
        assert VisualizationType.BAR_CHART.value == "bar_chart"
        assert VisualizationType.LINE_CHART.value == "line_chart"
        assert VisualizationType.PIE_CHART.value == "pie_chart"
        assert VisualizationType.PROGRESS_BAR.value == "progress_bar"
        assert VisualizationType.HEATMAP.value == "heatmap"
        assert VisualizationType.NETWORK_DIAGRAM.value == "network_diagram"
        assert VisualizationType.TIMELINE.value == "timeline"

    def test_visualization_type_count(self):
        """Test total number of visualization types"""
        assert len(VisualizationType) == 8


class TestGrammarConceptTypeEnum:
    """Test GrammarConceptType enum"""

    def test_grammar_concept_type_values(self):
        """Test all grammar concept type enum values"""
        assert GrammarConceptType.VERB_CONJUGATION.value == "verb_conjugation"
        assert GrammarConceptType.SENTENCE_STRUCTURE.value == "sentence_structure"
        assert GrammarConceptType.TENSE_USAGE.value == "tense_usage"
        assert GrammarConceptType.CONDITIONAL_FORMS.value == "conditional_forms"
        assert GrammarConceptType.PRONOUN_USAGE.value == "pronoun_usage"
        assert GrammarConceptType.ARTICLE_RULES.value == "article_rules"
        assert GrammarConceptType.PREPOSITIONS.value == "prepositions"
        assert GrammarConceptType.ADJECTIVE_AGREEMENT.value == "adjective_agreement"

    def test_grammar_concept_type_count(self):
        """Test total number of grammar concept types"""
        assert len(GrammarConceptType) == 8


class TestVocabularyVisualizationTypeEnum:
    """Test VocabularyVisualizationType enum"""

    def test_vocabulary_visualization_type_values(self):
        """Test all vocabulary visualization type enum values"""
        assert VocabularyVisualizationType.WORD_CLOUD.value == "word_cloud"
        assert VocabularyVisualizationType.SEMANTIC_MAP.value == "semantic_map"
        assert VocabularyVisualizationType.ETYMOLOGY_TREE.value == "etymology_tree"
        assert VocabularyVisualizationType.FREQUENCY_CHART.value == "frequency_chart"
        assert VocabularyVisualizationType.CONTEXT_EXAMPLES.value == "context_examples"
        assert (
            VocabularyVisualizationType.ASSOCIATION_NETWORK.value
            == "association_network"
        )

    def test_vocabulary_visualization_type_count(self):
        """Test total number of vocabulary visualization types"""
        assert len(VocabularyVisualizationType) == 6


# ==================== Test Dataclass Models ====================


class TestFlowchartNode:
    """Test FlowchartNode dataclass"""

    def test_flowchart_node_creation_all_fields(self):
        """Test FlowchartNode creation with all fields"""
        node = FlowchartNode(
            node_id="node1",
            title="Start",
            description="Starting point",
            node_type="start",
            content="Begin here",
            examples=["Example 1", "Example 2"],
            next_nodes=["node2", "node3"],
            position=(10, 20),
            metadata={"key": "value"},
        )

        assert node.node_id == "node1"
        assert node.title == "Start"
        assert node.description == "Starting point"
        assert node.node_type == "start"
        assert node.content == "Begin here"
        assert node.examples == ["Example 1", "Example 2"]
        assert node.next_nodes == ["node2", "node3"]
        assert node.position == (10, 20)
        assert node.metadata == {"key": "value"}

    def test_flowchart_node_creation_minimal_fields(self):
        """Test FlowchartNode creation with minimal fields"""
        node = FlowchartNode(
            node_id="node1",
            title="Start",
            description="Starting point",
            node_type="start",
            content="Begin here",
        )

        assert node.node_id == "node1"
        assert node.examples == []
        assert node.next_nodes == []
        assert node.position == (0, 0)
        assert node.metadata == {}


class TestGrammarFlowchart:
    """Test GrammarFlowchart dataclass"""

    def test_grammar_flowchart_creation_all_fields(self):
        """Test GrammarFlowchart creation with all fields"""
        node1 = FlowchartNode(
            node_id="n1",
            title="Start",
            description="Start",
            node_type="start",
            content="Begin",
        )

        flowchart = GrammarFlowchart(
            flowchart_id="fc1",
            concept=GrammarConceptType.VERB_CONJUGATION,
            title="Verb Conjugation",
            description="Learn verbs",
            language="french",
            difficulty_level=3,
            nodes=[node1],
            connections=[("n1", "n2")],
            learning_outcomes=["Outcome 1"],
            created_at=datetime(2025, 1, 1),
            metadata={"version": "1.0"},
        )

        assert flowchart.flowchart_id == "fc1"
        assert flowchart.concept == GrammarConceptType.VERB_CONJUGATION
        assert flowchart.title == "Verb Conjugation"
        assert flowchart.description == "Learn verbs"
        assert flowchart.language == "french"
        assert flowchart.difficulty_level == 3
        assert len(flowchart.nodes) == 1
        assert flowchart.connections == [("n1", "n2")]
        assert flowchart.learning_outcomes == ["Outcome 1"]
        assert flowchart.metadata == {"version": "1.0"}

    def test_grammar_flowchart_creation_minimal_fields(self):
        """Test GrammarFlowchart creation with minimal fields"""
        flowchart = GrammarFlowchart(
            flowchart_id="fc1",
            concept=GrammarConceptType.VERB_CONJUGATION,
            title="Verb Conjugation",
            description="Learn verbs",
            language="french",
            difficulty_level=3,
        )

        assert flowchart.nodes == []
        assert flowchart.connections == []
        assert flowchart.learning_outcomes == []
        assert flowchart.metadata == {}
        assert isinstance(flowchart.created_at, datetime)


class TestProgressVisualization:
    """Test ProgressVisualization dataclass"""

    def test_progress_visualization_creation_all_fields(self):
        """Test ProgressVisualization creation with all fields"""
        viz = ProgressVisualization(
            visualization_id="viz1",
            user_id="user123",
            visualization_type=VisualizationType.LINE_CHART,
            title="Progress",
            description="Track progress",
            data_points=[{"x": 1, "y": 2}],
            x_axis_label="Time",
            y_axis_label="Score",
            color_scheme=["#ff0000"],
            generated_at=datetime(2025, 1, 1),
            metadata={"key": "value"},
        )

        assert viz.visualization_id == "viz1"
        assert viz.user_id == "user123"
        assert viz.visualization_type == VisualizationType.LINE_CHART
        assert viz.title == "Progress"
        assert viz.description == "Track progress"
        assert viz.data_points == [{"x": 1, "y": 2}]
        assert viz.x_axis_label == "Time"
        assert viz.y_axis_label == "Score"
        assert viz.color_scheme == ["#ff0000"]
        assert viz.metadata == {"key": "value"}

    def test_progress_visualization_creation_minimal_fields(self):
        """Test ProgressVisualization creation with minimal fields"""
        viz = ProgressVisualization(
            visualization_id="viz1",
            user_id="user123",
            visualization_type=VisualizationType.LINE_CHART,
            title="Progress",
            description="Track progress",
        )

        assert viz.data_points == []
        assert viz.x_axis_label == ""
        assert viz.y_axis_label == ""
        assert viz.color_scheme == ["#6366f1", "#0891b2", "#f59e0b"]
        assert isinstance(viz.generated_at, datetime)
        assert viz.metadata == {}


class TestVocabularyVisual:
    """Test VocabularyVisual dataclass"""

    def test_vocabulary_visual_creation_all_fields(self):
        """Test VocabularyVisual creation with all fields"""
        visual = VocabularyVisual(
            visual_id="v1",
            word="hello",
            language="english",
            translation="bonjour",
            visualization_type=VocabularyVisualizationType.WORD_CLOUD,
            visual_data={"key": "value"},
            phonetic="heh-loh",
            audio_url="http://example.com/audio.mp3",
            images=["img1.jpg"],
            example_sentences=[{"en": "Hello!", "fr": "Bonjour!"}],
            related_words=["hi", "greetings"],
            difficulty_level=1,
            created_at=datetime(2025, 1, 1),
            metadata={"key": "value"},
        )

        assert visual.visual_id == "v1"
        assert visual.word == "hello"
        assert visual.language == "english"
        assert visual.translation == "bonjour"
        assert visual.visualization_type == VocabularyVisualizationType.WORD_CLOUD
        assert visual.visual_data == {"key": "value"}
        assert visual.phonetic == "heh-loh"
        assert visual.audio_url == "http://example.com/audio.mp3"
        assert visual.images == ["img1.jpg"]
        assert visual.example_sentences == [{"en": "Hello!", "fr": "Bonjour!"}]
        assert visual.related_words == ["hi", "greetings"]
        assert visual.difficulty_level == 1
        assert visual.metadata == {"key": "value"}

    def test_vocabulary_visual_creation_minimal_fields(self):
        """Test VocabularyVisual creation with minimal fields"""
        visual = VocabularyVisual(
            visual_id="v1",
            word="hello",
            language="english",
            translation="bonjour",
            visualization_type=VocabularyVisualizationType.WORD_CLOUD,
        )

        assert visual.visual_data == {}
        assert visual.phonetic is None
        assert visual.audio_url is None
        assert visual.images == []
        assert visual.example_sentences == []
        assert visual.related_words == []
        assert visual.difficulty_level == 1
        assert isinstance(visual.created_at, datetime)
        assert visual.metadata == {}


class TestPronunciationGuide:
    """Test PronunciationGuide dataclass"""

    def test_pronunciation_guide_creation_all_fields(self):
        """Test PronunciationGuide creation with all fields"""
        guide = PronunciationGuide(
            guide_id="g1",
            word_or_phrase="hello",
            language="english",
            phonetic_spelling="heh-loh",
            ipa_notation="həˈloʊ",
            audio_url="http://example.com/audio.mp3",
            breakdown=[{"syllable": "hel", "ipa": "hɛl"}],
            visual_mouth_positions=["pos1.jpg"],
            common_mistakes=["Mistake 1"],
            practice_tips=["Tip 1"],
            difficulty_level=2,
            created_at=datetime(2025, 1, 1),
            metadata={"key": "value"},
        )

        assert guide.guide_id == "g1"
        assert guide.word_or_phrase == "hello"
        assert guide.language == "english"
        assert guide.phonetic_spelling == "heh-loh"
        assert guide.ipa_notation == "həˈloʊ"
        assert guide.audio_url == "http://example.com/audio.mp3"
        assert guide.breakdown == [{"syllable": "hel", "ipa": "hɛl"}]
        assert guide.visual_mouth_positions == ["pos1.jpg"]
        assert guide.common_mistakes == ["Mistake 1"]
        assert guide.practice_tips == ["Tip 1"]
        assert guide.difficulty_level == 2
        assert guide.metadata == {"key": "value"}

    def test_pronunciation_guide_creation_minimal_fields(self):
        """Test PronunciationGuide creation with minimal fields"""
        guide = PronunciationGuide(
            guide_id="g1",
            word_or_phrase="hello",
            language="english",
            phonetic_spelling="heh-loh",
            ipa_notation="həˈloʊ",
        )

        assert guide.audio_url is None
        assert guide.breakdown == []
        assert guide.visual_mouth_positions == []
        assert guide.common_mistakes == []
        assert guide.practice_tips == []
        assert guide.difficulty_level == 1
        assert isinstance(guide.created_at, datetime)
        assert guide.metadata == {}


# ==================== Test Service Initialization ====================


class TestVisualLearningServiceInitialization:
    """Test VisualLearningService initialization"""

    def test_service_initialization_with_custom_directory(self, temp_dir):
        """Test service initialization with custom directory"""
        service = VisualLearningService(data_dir=temp_dir)

        assert service.data_dir == temp_dir
        assert service.data_dir.exists()
        assert service.flowcharts_dir.exists()
        assert service.visualizations_dir.exists()
        assert service.vocabulary_dir.exists()
        assert service.pronunciation_dir.exists()

    def test_service_initialization_without_directory(self):
        """Test service initialization without custom directory (default)"""
        service = VisualLearningService()

        assert service.data_dir == Path("data/visual_learning")
        assert service.flowcharts_dir == service.data_dir / "flowcharts"
        assert service.visualizations_dir == service.data_dir / "visualizations"
        assert service.vocabulary_dir == service.data_dir / "vocabulary"
        assert service.pronunciation_dir == service.data_dir / "pronunciation"

    def test_service_creates_subdirectories(self, temp_dir):
        """Test that service creates all required subdirectories"""
        service = VisualLearningService(data_dir=temp_dir)

        assert (temp_dir / "flowcharts").exists()
        assert (temp_dir / "visualizations").exists()
        assert (temp_dir / "vocabulary").exists()
        assert (temp_dir / "pronunciation").exists()


# ==================== Test Grammar Flowchart Operations ====================


class TestGrammarFlowchartOperations:
    """Test grammar flowchart CRUD operations"""

    def test_create_grammar_flowchart_with_all_parameters(self, service):
        """Test creating a grammar flowchart with all parameters"""
        flowchart = service.create_grammar_flowchart(
            concept=GrammarConceptType.VERB_CONJUGATION,
            title="French Verbs",
            description="Learn French verb conjugation",
            language="french",
            difficulty_level=3,
            learning_outcomes=["Understand present tense", "Apply rules"],
        )

        assert flowchart.concept == GrammarConceptType.VERB_CONJUGATION
        assert flowchart.title == "French Verbs"
        assert flowchart.description == "Learn French verb conjugation"
        assert flowchart.language == "french"
        assert flowchart.difficulty_level == 3
        assert flowchart.learning_outcomes == [
            "Understand present tense",
            "Apply rules",
        ]
        assert "flowchart_french_verb_conjugation" in flowchart.flowchart_id

    def test_create_grammar_flowchart_without_learning_outcomes(self, service):
        """Test creating a flowchart without learning outcomes"""
        flowchart = service.create_grammar_flowchart(
            concept=GrammarConceptType.TENSE_USAGE,
            title="Tenses",
            description="Learn tenses",
            language="spanish",
            difficulty_level=2,
        )

        assert flowchart.learning_outcomes == []

    def test_add_flowchart_node_success(self, service, sample_flowchart):
        """Test adding a node to a flowchart"""
        node = service.add_flowchart_node(
            flowchart_id=sample_flowchart.flowchart_id,
            title="Step 1",
            description="First step",
            node_type="process",
            content="Do this",
            examples=["Example 1", "Example 2"],
            position=(10, 20),
        )

        assert node.node_id == "node_1"
        assert node.title == "Step 1"
        assert node.description == "First step"
        assert node.node_type == "process"
        assert node.content == "Do this"
        assert node.examples == ["Example 1", "Example 2"]
        assert node.position == (10, 20)

    def test_add_flowchart_node_without_examples(self, service, sample_flowchart):
        """Test adding a node without examples"""
        node = service.add_flowchart_node(
            flowchart_id=sample_flowchart.flowchart_id,
            title="Step 1",
            description="First step",
            node_type="process",
            content="Do this",
        )

        assert node.examples == []
        assert node.position == (0, 0)

    def test_add_flowchart_node_to_nonexistent_flowchart(self, service):
        """Test adding a node to a nonexistent flowchart"""
        with pytest.raises(ValueError, match="Flowchart not found"):
            service.add_flowchart_node(
                flowchart_id="nonexistent_id",
                title="Step 1",
                description="First step",
                node_type="process",
                content="Do this",
            )

    def test_connect_flowchart_nodes_success(self, service, sample_flowchart):
        """Test connecting two nodes in a flowchart"""
        # Add two nodes
        node1 = service.add_flowchart_node(
            flowchart_id=sample_flowchart.flowchart_id,
            title="Node 1",
            description="First node",
            node_type="start",
            content="Start here",
        )
        node2 = service.add_flowchart_node(
            flowchart_id=sample_flowchart.flowchart_id,
            title="Node 2",
            description="Second node",
            node_type="process",
            content="Continue here",
        )

        # Connect nodes
        result = service.connect_flowchart_nodes(
            flowchart_id=sample_flowchart.flowchart_id,
            from_node_id=node1.node_id,
            to_node_id=node2.node_id,
        )

        assert result is True

        # Verify connection
        flowchart = service.get_flowchart(sample_flowchart.flowchart_id)
        assert (node1.node_id, node2.node_id) in flowchart.connections

        # Verify next_nodes updated
        from_node = [n for n in flowchart.nodes if n.node_id == node1.node_id][0]
        assert node2.node_id in from_node.next_nodes

    def test_connect_flowchart_nodes_duplicate_connection(
        self, service, sample_flowchart
    ):
        """Test connecting nodes with duplicate connection"""
        # Add two nodes and connect them
        node1 = service.add_flowchart_node(
            flowchart_id=sample_flowchart.flowchart_id,
            title="Node 1",
            description="First node",
            node_type="start",
            content="Start here",
        )
        node2 = service.add_flowchart_node(
            flowchart_id=sample_flowchart.flowchart_id,
            title="Node 2",
            description="Second node",
            node_type="process",
            content="Continue here",
        )

        service.connect_flowchart_nodes(
            flowchart_id=sample_flowchart.flowchart_id,
            from_node_id=node1.node_id,
            to_node_id=node2.node_id,
        )

        # Try connecting again
        result = service.connect_flowchart_nodes(
            flowchart_id=sample_flowchart.flowchart_id,
            from_node_id=node1.node_id,
            to_node_id=node2.node_id,
        )

        assert result is False

    def test_connect_flowchart_nodes_nonexistent_flowchart(self, service):
        """Test connecting nodes in a nonexistent flowchart"""
        with pytest.raises(ValueError, match="Flowchart not found"):
            service.connect_flowchart_nodes(
                flowchart_id="nonexistent_id",
                from_node_id="node1",
                to_node_id="node2",
            )

    def test_get_flowchart_success(self, service, sample_flowchart):
        """Test retrieving an existing flowchart"""
        flowchart = service.get_flowchart(sample_flowchart.flowchart_id)

        assert flowchart is not None
        assert flowchart.flowchart_id == sample_flowchart.flowchart_id
        assert flowchart.title == "French Verb Conjugation"
        assert flowchart.language == "french"

    def test_get_flowchart_nonexistent(self, service):
        """Test retrieving a nonexistent flowchart"""
        flowchart = service.get_flowchart("nonexistent_id")

        assert flowchart is None

    def test_get_flowchart_with_json_error(self, service, sample_flowchart):
        """Test retrieving a flowchart with JSON error"""
        # Corrupt the JSON file
        file_path = service.flowcharts_dir / f"{sample_flowchart.flowchart_id}.json"
        with open(file_path, "w") as f:
            f.write("invalid json {{{")

        flowchart = service.get_flowchart(sample_flowchart.flowchart_id)

        assert flowchart is None

    def test_list_flowcharts_no_filters(self, service):
        """Test listing all flowcharts without filters"""
        # Create multiple flowcharts
        service.create_grammar_flowchart(
            concept=GrammarConceptType.VERB_CONJUGATION,
            title="French Verbs",
            description="Learn verbs",
            language="french",
            difficulty_level=3,
        )
        service.create_grammar_flowchart(
            concept=GrammarConceptType.TENSE_USAGE,
            title="Spanish Tenses",
            description="Learn tenses",
            language="spanish",
            difficulty_level=2,
        )

        flowcharts = service.list_flowcharts()

        assert len(flowcharts) == 2

    def test_list_flowcharts_filter_by_language(self, service):
        """Test listing flowcharts filtered by language"""
        # Create flowcharts in different languages
        service.create_grammar_flowchart(
            concept=GrammarConceptType.VERB_CONJUGATION,
            title="French Verbs",
            description="Learn verbs",
            language="french",
            difficulty_level=3,
        )
        service.create_grammar_flowchart(
            concept=GrammarConceptType.TENSE_USAGE,
            title="Spanish Tenses",
            description="Learn tenses",
            language="spanish",
            difficulty_level=2,
        )

        flowcharts = service.list_flowcharts(language="french")

        assert len(flowcharts) == 1
        assert flowcharts[0]["language"] == "french"

    def test_list_flowcharts_filter_by_concept(self, service):
        """Test listing flowcharts filtered by concept"""
        # Create flowcharts with different concepts
        service.create_grammar_flowchart(
            concept=GrammarConceptType.VERB_CONJUGATION,
            title="Verbs 1",
            description="Learn verbs",
            language="french",
            difficulty_level=3,
        )
        service.create_grammar_flowchart(
            concept=GrammarConceptType.VERB_CONJUGATION,
            title="Verbs 2",
            description="More verbs",
            language="spanish",
            difficulty_level=2,
        )
        service.create_grammar_flowchart(
            concept=GrammarConceptType.TENSE_USAGE,
            title="Tenses",
            description="Learn tenses",
            language="french",
            difficulty_level=2,
        )

        flowcharts = service.list_flowcharts(
            concept=GrammarConceptType.VERB_CONJUGATION
        )

        assert len(flowcharts) == 2
        assert all(fc["concept"] == "verb_conjugation" for fc in flowcharts)

    def test_list_flowcharts_filter_by_language_and_concept(self, service):
        """Test listing flowcharts filtered by both language and concept"""
        # Create multiple flowcharts
        service.create_grammar_flowchart(
            concept=GrammarConceptType.VERB_CONJUGATION,
            title="French Verbs",
            description="Learn verbs",
            language="french",
            difficulty_level=3,
        )
        service.create_grammar_flowchart(
            concept=GrammarConceptType.TENSE_USAGE,
            title="French Tenses",
            description="Learn tenses",
            language="french",
            difficulty_level=2,
        )
        service.create_grammar_flowchart(
            concept=GrammarConceptType.VERB_CONJUGATION,
            title="Spanish Verbs",
            description="Learn verbs",
            language="spanish",
            difficulty_level=2,
        )

        flowcharts = service.list_flowcharts(
            language="french", concept=GrammarConceptType.VERB_CONJUGATION
        )

        assert len(flowcharts) == 1
        assert flowcharts[0]["language"] == "french"
        assert flowcharts[0]["concept"] == "verb_conjugation"

    def test_list_flowcharts_with_json_error(self, service, sample_flowchart):
        """Test listing flowcharts with JSON error in one file"""
        # Create a valid flowchart
        service.create_grammar_flowchart(
            concept=GrammarConceptType.TENSE_USAGE,
            title="Valid Flowchart",
            description="This one is valid",
            language="french",
            difficulty_level=2,
        )

        # Corrupt one JSON file
        file_path = service.flowcharts_dir / f"{sample_flowchart.flowchart_id}.json"
        with open(file_path, "w") as f:
            f.write("invalid json {{{")

        flowcharts = service.list_flowcharts()

        # Should return only the valid flowchart
        assert len(flowcharts) == 1
        assert flowcharts[0]["title"] == "Valid Flowchart"


# ==================== Test Progress Visualization Operations ====================


class TestProgressVisualizationOperations:
    """Test progress visualization CRUD operations"""

    def test_create_progress_visualization_with_all_parameters(self, service):
        """Test creating a progress visualization with all parameters"""
        viz = service.create_progress_visualization(
            user_id="user123",
            visualization_type=VisualizationType.BAR_CHART,
            title="Weekly Progress",
            description="Track weekly learning progress",
            data_points=[{"day": "Mon", "score": 85}, {"day": "Tue", "score": 90}],
            x_axis_label="Day",
            y_axis_label="Score",
            color_scheme=["#ff0000", "#00ff00", "#0000ff"],
        )

        assert viz.user_id == "user123"
        assert viz.visualization_type == VisualizationType.BAR_CHART
        assert viz.title == "Weekly Progress"
        assert viz.description == "Track weekly learning progress"
        assert len(viz.data_points) == 2
        assert viz.x_axis_label == "Day"
        assert viz.y_axis_label == "Score"
        assert viz.color_scheme == ["#ff0000", "#00ff00", "#0000ff"]
        assert "viz_user123_bar_chart" in viz.visualization_id

    def test_create_progress_visualization_without_color_scheme(self, service):
        """Test creating a visualization without custom color scheme"""
        viz = service.create_progress_visualization(
            user_id="user123",
            visualization_type=VisualizationType.LINE_CHART,
            title="Progress",
            description="Track progress",
            data_points=[{"x": 1, "y": 2}],
        )

        assert viz.color_scheme == ["#6366f1", "#0891b2", "#f59e0b"]

    def test_get_user_progress_visualizations_no_filter(self, service):
        """Test getting all visualizations for a user"""
        # Create multiple visualizations
        service.create_progress_visualization(
            user_id="user123",
            visualization_type=VisualizationType.LINE_CHART,
            title="Progress 1",
            description="First visualization",
            data_points=[],
        )
        service.create_progress_visualization(
            user_id="user123",
            visualization_type=VisualizationType.BAR_CHART,
            title="Progress 2",
            description="Second visualization",
            data_points=[],
        )
        service.create_progress_visualization(
            user_id="user456",
            visualization_type=VisualizationType.PIE_CHART,
            title="Progress 3",
            description="Another user's visualization",
            data_points=[],
        )

        visualizations = service.get_user_progress_visualizations(user_id="user123")

        assert len(visualizations) == 2
        assert all(viz.user_id == "user123" for viz in visualizations)

    def test_get_user_progress_visualizations_with_type_filter(self, service):
        """Test getting visualizations filtered by type"""
        # Create multiple visualizations
        service.create_progress_visualization(
            user_id="user123",
            visualization_type=VisualizationType.LINE_CHART,
            title="Progress 1",
            description="Line chart",
            data_points=[],
        )
        service.create_progress_visualization(
            user_id="user123",
            visualization_type=VisualizationType.BAR_CHART,
            title="Progress 2",
            description="Bar chart",
            data_points=[],
        )

        visualizations = service.get_user_progress_visualizations(
            user_id="user123", visualization_type=VisualizationType.LINE_CHART
        )

        assert len(visualizations) == 1
        assert visualizations[0].visualization_type == VisualizationType.LINE_CHART

    def test_get_user_progress_visualizations_with_json_error(
        self, service, sample_visualization
    ):
        """Test getting visualizations with JSON error in one file"""
        # Create a valid visualization
        service.create_progress_visualization(
            user_id="user123",
            visualization_type=VisualizationType.BAR_CHART,
            title="Valid Viz",
            description="This one is valid",
            data_points=[],
        )

        # Corrupt one JSON file
        file_path = (
            service.visualizations_dir / f"{sample_visualization.visualization_id}.json"
        )
        with open(file_path, "w") as f:
            f.write("invalid json {{{")

        visualizations = service.get_user_progress_visualizations(user_id="user123")

        # Should return only the valid visualization
        assert len(visualizations) == 1
        assert visualizations[0].title == "Valid Viz"


# ==================== Test Vocabulary Visual Operations ====================


class TestVocabularyVisualOperations:
    """Test vocabulary visual CRUD operations"""

    def test_create_vocabulary_visual_with_all_parameters(self, service):
        """Test creating a vocabulary visual with all parameters"""
        visual = service.create_vocabulary_visual(
            word="hello",
            language="english",
            translation="bonjour",
            visualization_type=VocabularyVisualizationType.SEMANTIC_MAP,
            phonetic="heh-loh",
            example_sentences=[
                {"english": "Hello!", "french": "Bonjour!"},
                {"english": "Say hello", "french": "Dire bonjour"},
            ],
            related_words=["hi", "greetings", "salutations"],
            difficulty_level=1,
        )

        assert visual.word == "hello"
        assert visual.language == "english"
        assert visual.translation == "bonjour"
        assert visual.visualization_type == VocabularyVisualizationType.SEMANTIC_MAP
        assert visual.phonetic == "heh-loh"
        assert len(visual.example_sentences) == 2
        assert len(visual.related_words) == 3
        assert visual.difficulty_level == 1
        assert "vocab_english_hello" in visual.visual_id

    def test_create_vocabulary_visual_without_optional_parameters(self, service):
        """Test creating a vocabulary visual without optional parameters"""
        visual = service.create_vocabulary_visual(
            word="goodbye",
            language="english",
            translation="au revoir",
            visualization_type=VocabularyVisualizationType.WORD_CLOUD,
        )

        assert visual.phonetic is None
        assert visual.example_sentences == []
        assert visual.related_words == []
        assert visual.difficulty_level == 1

    def test_get_vocabulary_visuals_no_filters(self, service):
        """Test getting all vocabulary visuals without filters"""
        # Create multiple visuals
        service.create_vocabulary_visual(
            word="hello",
            language="english",
            translation="bonjour",
            visualization_type=VocabularyVisualizationType.WORD_CLOUD,
        )
        service.create_vocabulary_visual(
            word="goodbye",
            language="english",
            translation="au revoir",
            visualization_type=VocabularyVisualizationType.SEMANTIC_MAP,
        )

        visuals = service.get_vocabulary_visuals()

        assert len(visuals) == 2

    def test_get_vocabulary_visuals_filter_by_language(self, service):
        """Test getting vocabulary visuals filtered by language"""
        # Create visuals in different languages
        service.create_vocabulary_visual(
            word="hello",
            language="english",
            translation="bonjour",
            visualization_type=VocabularyVisualizationType.WORD_CLOUD,
        )
        service.create_vocabulary_visual(
            word="hola",
            language="spanish",
            translation="hello",
            visualization_type=VocabularyVisualizationType.WORD_CLOUD,
        )

        visuals = service.get_vocabulary_visuals(language="english")

        assert len(visuals) == 1
        assert visuals[0].language == "english"

    def test_get_vocabulary_visuals_filter_by_visualization_type(self, service):
        """Test getting vocabulary visuals filtered by visualization type"""
        # Create visuals with different types
        service.create_vocabulary_visual(
            word="hello",
            language="english",
            translation="bonjour",
            visualization_type=VocabularyVisualizationType.WORD_CLOUD,
        )
        service.create_vocabulary_visual(
            word="goodbye",
            language="english",
            translation="au revoir",
            visualization_type=VocabularyVisualizationType.SEMANTIC_MAP,
        )

        visuals = service.get_vocabulary_visuals(
            visualization_type=VocabularyVisualizationType.WORD_CLOUD
        )

        assert len(visuals) == 1
        assert visuals[0].visualization_type == VocabularyVisualizationType.WORD_CLOUD

    def test_get_vocabulary_visuals_filter_by_language_and_type(self, service):
        """Test getting vocabulary visuals filtered by both language and type"""
        # Create multiple visuals
        service.create_vocabulary_visual(
            word="hello",
            language="english",
            translation="bonjour",
            visualization_type=VocabularyVisualizationType.WORD_CLOUD,
        )
        service.create_vocabulary_visual(
            word="goodbye",
            language="english",
            translation="au revoir",
            visualization_type=VocabularyVisualizationType.SEMANTIC_MAP,
        )
        service.create_vocabulary_visual(
            word="hola",
            language="spanish",
            translation="hello",
            visualization_type=VocabularyVisualizationType.WORD_CLOUD,
        )

        visuals = service.get_vocabulary_visuals(
            language="english",
            visualization_type=VocabularyVisualizationType.WORD_CLOUD,
        )

        assert len(visuals) == 1
        assert visuals[0].language == "english"
        assert visuals[0].visualization_type == VocabularyVisualizationType.WORD_CLOUD

    def test_get_vocabulary_visuals_with_json_error(
        self, service, sample_vocabulary_visual
    ):
        """Test getting vocabulary visuals with JSON error in one file"""
        # Create a valid visual
        service.create_vocabulary_visual(
            word="valid",
            language="english",
            translation="valide",
            visualization_type=VocabularyVisualizationType.WORD_CLOUD,
        )

        # Corrupt one JSON file
        file_path = (
            service.vocabulary_dir / f"{sample_vocabulary_visual.visual_id}.json"
        )
        with open(file_path, "w") as f:
            f.write("invalid json {{{")

        visuals = service.get_vocabulary_visuals()

        # Should return only the valid visual
        assert len(visuals) == 1
        assert visuals[0].word == "valid"


# ==================== Test Pronunciation Guide Operations ====================


class TestPronunciationGuideOperations:
    """Test pronunciation guide CRUD operations"""

    def test_create_pronunciation_guide_with_all_parameters(self, service):
        """Test creating a pronunciation guide with all parameters"""
        guide = service.create_pronunciation_guide(
            word_or_phrase="bonjour",
            language="french",
            phonetic_spelling="bon-zhoor",
            ipa_notation="bɔ̃ʒuʁ",
            breakdown=[
                {"syllable": "bon", "ipa": "bɔ̃", "tips": "Nasal sound"},
                {"syllable": "jour", "ipa": "ʒuʁ", "tips": "Soft 'j'"},
            ],
            common_mistakes=["Pronouncing 'j' as English 'j'", "Not nasalizing 'on'"],
            practice_tips=["Practice nasal sounds", "Listen to native speakers"],
            difficulty_level=2,
        )

        assert guide.word_or_phrase == "bonjour"
        assert guide.language == "french"
        assert guide.phonetic_spelling == "bon-zhoor"
        assert guide.ipa_notation == "bɔ̃ʒuʁ"
        assert len(guide.breakdown) == 2
        assert len(guide.common_mistakes) == 2
        assert len(guide.practice_tips) == 2
        assert guide.difficulty_level == 2
        assert "pronunciation_french_bonjour" in guide.guide_id

    def test_create_pronunciation_guide_without_optional_parameters(self, service):
        """Test creating a pronunciation guide without optional parameters"""
        guide = service.create_pronunciation_guide(
            word_or_phrase="hello",
            language="english",
            phonetic_spelling="heh-loh",
            ipa_notation="həˈloʊ",
        )

        assert guide.breakdown == []
        assert guide.common_mistakes == []
        assert guide.practice_tips == []
        assert guide.difficulty_level == 1

    def test_get_pronunciation_guides_no_filters(self, service):
        """Test getting all pronunciation guides without filters"""
        # Create multiple guides
        service.create_pronunciation_guide(
            word_or_phrase="bonjour",
            language="french",
            phonetic_spelling="bon-zhoor",
            ipa_notation="bɔ̃ʒuʁ",
        )
        service.create_pronunciation_guide(
            word_or_phrase="au revoir",
            language="french",
            phonetic_spelling="oh ruh-vwahr",
            ipa_notation="o ʁəvwaʁ",
        )

        guides = service.get_pronunciation_guides()

        assert len(guides) == 2

    def test_get_pronunciation_guides_filter_by_language(self, service):
        """Test getting pronunciation guides filtered by language"""
        # Create guides in different languages
        service.create_pronunciation_guide(
            word_or_phrase="bonjour",
            language="french",
            phonetic_spelling="bon-zhoor",
            ipa_notation="bɔ̃ʒuʁ",
        )
        service.create_pronunciation_guide(
            word_or_phrase="hola",
            language="spanish",
            phonetic_spelling="oh-lah",
            ipa_notation="ˈola",
        )

        guides = service.get_pronunciation_guides(language="french")

        assert len(guides) == 1
        assert guides[0].language == "french"

    def test_get_pronunciation_guides_filter_by_difficulty(self, service):
        """Test getting pronunciation guides filtered by difficulty level"""
        # Create guides with different difficulty levels
        service.create_pronunciation_guide(
            word_or_phrase="hello",
            language="english",
            phonetic_spelling="heh-loh",
            ipa_notation="həˈloʊ",
            difficulty_level=1,
        )
        service.create_pronunciation_guide(
            word_or_phrase="difficult",
            language="english",
            phonetic_spelling="dif-i-kult",
            ipa_notation="ˈdɪfɪkəlt",
            difficulty_level=3,
        )

        guides = service.get_pronunciation_guides(difficulty_level=1)

        assert len(guides) == 1
        assert guides[0].difficulty_level == 1

    def test_get_pronunciation_guides_filter_by_language_and_difficulty(self, service):
        """Test getting pronunciation guides filtered by both language and difficulty"""
        # Create multiple guides
        service.create_pronunciation_guide(
            word_or_phrase="bonjour",
            language="french",
            phonetic_spelling="bon-zhoor",
            ipa_notation="bɔ̃ʒuʁ",
            difficulty_level=1,
        )
        service.create_pronunciation_guide(
            word_or_phrase="serendipité",
            language="french",
            phonetic_spelling="seh-rahn-dee-pee-tay",
            ipa_notation="seʁɑ̃dipite",
            difficulty_level=3,
        )
        service.create_pronunciation_guide(
            word_or_phrase="hello",
            language="english",
            phonetic_spelling="heh-loh",
            ipa_notation="həˈloʊ",
            difficulty_level=1,
        )

        guides = service.get_pronunciation_guides(language="french", difficulty_level=1)

        assert len(guides) == 1
        assert guides[0].language == "french"
        assert guides[0].difficulty_level == 1

    def test_get_pronunciation_guides_with_json_error(
        self, service, sample_pronunciation_guide
    ):
        """Test getting pronunciation guides with JSON error in one file"""
        # Create a valid guide
        service.create_pronunciation_guide(
            word_or_phrase="valid",
            language="english",
            phonetic_spelling="val-id",
            ipa_notation="ˈvælɪd",
        )

        # Corrupt one JSON file
        file_path = (
            service.pronunciation_dir / f"{sample_pronunciation_guide.guide_id}.json"
        )
        with open(file_path, "w") as f:
            f.write("invalid json {{{")

        guides = service.get_pronunciation_guides()

        # Should return only the valid guide
        assert len(guides) == 1
        assert guides[0].word_or_phrase == "valid"


# ==================== Test Global Instance ====================


class TestGlobalInstance:
    """Test global instance management"""

    def test_get_visual_learning_service_creates_instance(self):
        """Test that get_visual_learning_service creates a global instance"""
        # Clear the global instance
        import app.services.visual_learning_service as vls_module

        vls_module._visual_learning_service = None

        service = get_visual_learning_service()

        assert service is not None
        assert isinstance(service, VisualLearningService)

    def test_get_visual_learning_service_returns_same_instance(self):
        """Test that get_visual_learning_service returns the same instance"""
        service1 = get_visual_learning_service()
        service2 = get_visual_learning_service()

        assert service1 is service2


# ==================== Summary ====================

"""
Test Coverage Summary:
- 3 Enum classes: 6 tests
- 5 Dataclass models: 10 tests
- Service initialization: 3 tests
- Grammar flowchart operations: 16 tests
- Progress visualization operations: 6 tests
- Vocabulary visual operations: 7 tests
- Pronunciation guide operations: 7 tests
- Global instance: 2 tests

Total: 57 comprehensive tests targeting 100% coverage
"""
