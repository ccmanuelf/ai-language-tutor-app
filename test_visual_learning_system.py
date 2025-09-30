"""
Visual Learning System - Comprehensive Test Suite
AI Language Tutor App - Task 3.2 Validation

Tests all visual learning components:
- Grammar flowchart creation and management
- Progress visualization generation
- Visual vocabulary tools
- Pronunciation guides
- API endpoints
- Data persistence

Target: 100% success rate across all tests
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.visual_learning_service import (
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


class VisualLearningSystemTester:
    """Comprehensive test suite for visual learning system"""

    def __init__(self):
        self.test_data_dir = Path("data/test_visual_learning")
        self.service = VisualLearningService(data_dir=self.test_data_dir)
        self.test_results = []
        self.passed_tests = 0
        self.total_tests = 0

    def run_test(self, test_name: str, test_func):
        """Run a single test and record results"""
        self.total_tests += 1
        try:
            test_func()
            self.test_results.append(
                {
                    "test": test_name,
                    "status": "PASSED",
                    "message": "Test completed successfully",
                }
            )
            self.passed_tests += 1
            print(f"✅ PASS: {test_name}")
            return True
        except AssertionError as e:
            self.test_results.append(
                {"test": test_name, "status": "FAILED", "message": str(e)}
            )
            print(f"❌ FAIL: {test_name} - {str(e)}")
            return False
        except Exception as e:
            self.test_results.append(
                {
                    "test": test_name,
                    "status": "ERROR",
                    "message": f"Unexpected error: {str(e)}",
                }
            )
            print(f"❌ ERROR: {test_name} - {str(e)}")
            return False

    def setup(self):
        """Setup test environment"""
        print("\n🔧 Setting up test environment...")

        # Clean test data directory
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)

        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Test environment ready: {self.test_data_dir}")

    def teardown(self):
        """Clean up test environment"""
        print("\n🧹 Cleaning up test environment...")

        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)

        print("✅ Test environment cleaned")

    # ==================== Grammar Flowchart Tests ====================

    def test_create_grammar_flowchart(self):
        """Test 1: Create a grammar flowchart"""
        flowchart = self.service.create_grammar_flowchart(
            concept=GrammarConceptType.VERB_CONJUGATION,
            title="Spanish Present Tense Verbs",
            description="Learn to conjugate regular verbs in present tense",
            language="es",
            difficulty_level=2,
            learning_outcomes=[
                "Conjugate -ar verbs",
                "Conjugate -er verbs",
                "Conjugate -ir verbs",
            ],
        )

        assert flowchart is not None, "Flowchart creation failed"
        assert flowchart.concept == GrammarConceptType.VERB_CONJUGATION
        assert flowchart.title == "Spanish Present Tense Verbs"
        assert flowchart.language == "es"
        assert flowchart.difficulty_level == 2
        assert len(flowchart.learning_outcomes) == 3

    def test_add_flowchart_nodes(self):
        """Test 2: Add nodes to flowchart"""
        # Create flowchart
        flowchart = self.service.create_grammar_flowchart(
            concept=GrammarConceptType.SENTENCE_STRUCTURE,
            title="Basic French Sentence Structure",
            description="Understanding Subject-Verb-Object order",
            language="fr",
            difficulty_level=1,
        )

        # Add start node
        node1 = self.service.add_flowchart_node(
            flowchart_id=flowchart.flowchart_id,
            title="Start",
            description="Begin learning sentence structure",
            node_type="start",
            content="French sentences follow a basic Subject-Verb-Object pattern.",
            examples=["Je mange une pomme.", "Tu parles français."],
            position=(0, 0),
        )

        # Add process node
        node2 = self.service.add_flowchart_node(
            flowchart_id=flowchart.flowchart_id,
            title="Identify Subject",
            description="Find the subject of the sentence",
            node_type="process",
            content="The subject is the person or thing performing the action.",
            examples=["Je (I)", "Tu (You)", "Il/Elle (He/She)"],
            position=(1, 0),
        )

        assert node1 is not None
        assert node2 is not None
        assert node1.node_type == "start"
        assert node2.node_type == "process"
        assert len(node1.examples) == 2
        assert len(node2.examples) == 3

    def test_connect_flowchart_nodes(self):
        """Test 3: Connect flowchart nodes"""
        # Create flowchart with nodes
        flowchart = self.service.create_grammar_flowchart(
            concept=GrammarConceptType.TENSE_USAGE,
            title="Chinese Time Expressions",
            description="Understanding time in Mandarin",
            language="zh",
            difficulty_level=3,
        )

        node1 = self.service.add_flowchart_node(
            flowchart_id=flowchart.flowchart_id,
            title="Start",
            description="Begin",
            node_type="start",
            content="Learn time expressions",
        )

        node2 = self.service.add_flowchart_node(
            flowchart_id=flowchart.flowchart_id,
            title="Past",
            description="Past time",
            node_type="process",
            content="Use time markers for past",
        )

        # Connect nodes
        success = self.service.connect_flowchart_nodes(
            flowchart_id=flowchart.flowchart_id,
            from_node_id=node1.node_id,
            to_node_id=node2.node_id,
        )

        assert success is True, "Node connection failed"

        # Verify connection
        updated_flowchart = self.service.get_flowchart(flowchart.flowchart_id)
        assert (node1.node_id, node2.node_id) in updated_flowchart.connections

    def test_get_flowchart(self):
        """Test 4: Retrieve flowchart by ID"""
        # Create flowchart
        original = self.service.create_grammar_flowchart(
            concept=GrammarConceptType.PRONOUN_USAGE,
            title="Spanish Pronouns",
            description="Learn Spanish subject pronouns",
            language="es",
            difficulty_level=1,
        )

        # Retrieve flowchart
        retrieved = self.service.get_flowchart(original.flowchart_id)

        assert retrieved is not None, "Flowchart retrieval failed"
        assert retrieved.flowchart_id == original.flowchart_id
        assert retrieved.title == original.title
        assert retrieved.concept == original.concept

    def test_list_flowcharts(self):
        """Test 5: List flowcharts with filtering"""
        # Create multiple flowcharts
        self.service.create_grammar_flowchart(
            concept=GrammarConceptType.VERB_CONJUGATION,
            title="Spanish Verbs",
            description="Test",
            language="es",
            difficulty_level=2,
        )

        self.service.create_grammar_flowchart(
            concept=GrammarConceptType.SENTENCE_STRUCTURE,
            title="French Structure",
            description="Test",
            language="fr",
            difficulty_level=1,
        )

        # List all
        all_flowcharts = self.service.list_flowcharts()
        assert len(all_flowcharts) >= 2

        # Filter by language
        spanish_flowcharts = self.service.list_flowcharts(language="es")
        assert len(spanish_flowcharts) >= 1
        assert all(fc["language"] == "es" for fc in spanish_flowcharts)

    # ==================== Progress Visualization Tests ====================

    def test_create_progress_visualization(self):
        """Test 6: Create progress visualization"""
        viz = self.service.create_progress_visualization(
            user_id="user_123",
            visualization_type=VisualizationType.BAR_CHART,
            title="Weekly Learning Activity",
            description="Hours studied per day",
            data_points=[
                {"day": "Mon", "hours": 2.5},
                {"day": "Tue", "hours": 3.0},
                {"day": "Wed", "hours": 1.5},
                {"day": "Thu", "hours": 4.0},
                {"day": "Fri", "hours": 2.0},
            ],
            x_axis_label="Day",
            y_axis_label="Hours",
        )

        assert viz is not None
        assert viz.user_id == "user_123"
        assert viz.visualization_type == VisualizationType.BAR_CHART
        assert len(viz.data_points) == 5
        assert viz.x_axis_label == "Day"

    def test_get_user_visualizations(self):
        """Test 7: Retrieve user visualizations"""
        user_id = "user_456"

        # Create multiple visualizations
        self.service.create_progress_visualization(
            user_id=user_id,
            visualization_type=VisualizationType.LINE_CHART,
            title="Progress Over Time",
            description="Test",
            data_points=[{"week": 1, "score": 75}],
        )

        self.service.create_progress_visualization(
            user_id=user_id,
            visualization_type=VisualizationType.PIE_CHART,
            title="Skill Distribution",
            description="Test",
            data_points=[{"skill": "Speaking", "percentage": 40}],
        )

        # Retrieve all visualizations
        vizs = self.service.get_user_progress_visualizations(user_id)
        assert len(vizs) >= 2
        assert all(viz.user_id == user_id for viz in vizs)

        # Filter by type
        line_charts = self.service.get_user_progress_visualizations(
            user_id=user_id, visualization_type=VisualizationType.LINE_CHART
        )
        assert len(line_charts) >= 1
        assert all(
            viz.visualization_type == VisualizationType.LINE_CHART
            for viz in line_charts
        )

    # ==================== Visual Vocabulary Tests ====================

    def test_create_vocabulary_visual(self):
        """Test 8: Create visual vocabulary tool"""
        visual = self.service.create_vocabulary_visual(
            word="casa",
            language="es",
            translation="house",
            visualization_type=VocabularyVisualizationType.CONTEXT_EXAMPLES,
            phonetic="/ˈka.sa/",
            example_sentences=[
                {"spanish": "Mi casa es grande.", "english": "My house is big."},
                {"spanish": "Voy a casa.", "english": "I'm going home."},
            ],
            related_words=["hogar", "vivienda", "domicilio"],
            difficulty_level=1,
        )

        assert visual is not None
        assert visual.word == "casa"
        assert visual.language == "es"
        assert visual.translation == "house"
        assert len(visual.example_sentences) == 2
        assert len(visual.related_words) == 3
        assert visual.difficulty_level == 1

    def test_get_vocabulary_visuals(self):
        """Test 9: Retrieve vocabulary visuals"""
        # Create visuals
        self.service.create_vocabulary_visual(
            word="manger",
            language="fr",
            translation="to eat",
            visualization_type=VocabularyVisualizationType.SEMANTIC_MAP,
            difficulty_level=1,
        )

        self.service.create_vocabulary_visual(
            word="学习",
            language="zh",
            translation="to study",
            visualization_type=VocabularyVisualizationType.FREQUENCY_CHART,
            difficulty_level=2,
        )

        # Get all visuals
        all_visuals = self.service.get_vocabulary_visuals()
        assert len(all_visuals) >= 2

        # Filter by language
        french_visuals = self.service.get_vocabulary_visuals(language="fr")
        assert len(french_visuals) >= 1
        assert all(v.language == "fr" for v in french_visuals)

    # ==================== Pronunciation Guide Tests ====================

    def test_create_pronunciation_guide(self):
        """Test 10: Create pronunciation guide"""
        guide = self.service.create_pronunciation_guide(
            word_or_phrase="gracias",
            language="es",
            phonetic_spelling="gra-see-as",
            ipa_notation="/ˈɡɾa.sjas/",
            breakdown=[
                {"syllable": "gra", "sound": "/ɡɾa/", "tip": "Roll the 'r' sound"},
                {"syllable": "cias", "sound": "/sjas/", "tip": "Soft 'c' like 's'"},
            ],
            common_mistakes=["Pronouncing 'c' as 'k'", "Not rolling the 'r'"],
            practice_tips=[
                "Practice rolling 'r' with tongue",
                "Listen to native speakers",
            ],
            difficulty_level=2,
        )

        assert guide is not None
        assert guide.word_or_phrase == "gracias"
        assert guide.language == "es"
        assert guide.phonetic_spelling == "gra-see-as"
        assert len(guide.breakdown) == 2
        assert len(guide.common_mistakes) == 2
        assert len(guide.practice_tips) == 2

    def test_get_pronunciation_guides(self):
        """Test 11: Retrieve pronunciation guides"""
        # Create guides
        self.service.create_pronunciation_guide(
            word_or_phrase="merci",
            language="fr",
            phonetic_spelling="mehr-see",
            ipa_notation="/mɛʁ.si/",
            difficulty_level=1,
        )

        self.service.create_pronunciation_guide(
            word_or_phrase="谢谢",
            language="zh",
            phonetic_spelling="shyeh-shyeh",
            ipa_notation="/ɕjè.ɕjè/",
            difficulty_level=3,
        )

        # Get all guides
        all_guides = self.service.get_pronunciation_guides()
        assert len(all_guides) >= 2

        # Filter by language
        french_guides = self.service.get_pronunciation_guides(language="fr")
        assert len(french_guides) >= 1
        assert all(g.language == "fr" for g in french_guides)

        # Filter by difficulty
        easy_guides = self.service.get_pronunciation_guides(difficulty_level=1)
        assert len(easy_guides) >= 1
        assert all(g.difficulty_level == 1 for g in easy_guides)

    # ==================== Data Persistence Tests ====================

    def test_flowchart_persistence(self):
        """Test 12: Verify flowchart data persistence"""
        # Create flowchart
        original = self.service.create_grammar_flowchart(
            concept=GrammarConceptType.CONDITIONAL_FORMS,
            title="Spanish Conditionals",
            description="Si clauses and conditional sentences",
            language="es",
            difficulty_level=4,
            learning_outcomes=["Understand si clauses", "Form conditional sentences"],
        )

        # Verify file exists
        file_path = self.service.flowcharts_dir / f"{original.flowchart_id}.json"
        assert file_path.exists(), "Flowchart file not created"

        # Load and verify JSON
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["flowchart_id"] == original.flowchart_id
        assert data["title"] == original.title
        assert data["concept"] == original.concept.value
        assert len(data["learning_outcomes"]) == 2

    def test_visualization_persistence(self):
        """Test 13: Verify visualization data persistence"""
        # Create visualization
        viz = self.service.create_progress_visualization(
            user_id="user_789",
            visualization_type=VisualizationType.HEATMAP,
            title="Learning Heatmap",
            description="Activity intensity by time",
            data_points=[{"hour": 9, "intensity": 0.8}],
        )

        # Verify file exists
        file_path = self.service.visualizations_dir / f"{viz.visualization_id}.json"
        assert file_path.exists(), "Visualization file not created"

        # Load and verify JSON
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["visualization_id"] == viz.visualization_id
        assert data["user_id"] == viz.user_id
        assert data["visualization_type"] == viz.visualization_type.value

    def test_vocabulary_persistence(self):
        """Test 14: Verify vocabulary visual persistence"""
        # Create vocabulary visual
        visual = self.service.create_vocabulary_visual(
            word="amigo",
            language="es",
            translation="friend",
            visualization_type=VocabularyVisualizationType.ASSOCIATION_NETWORK,
            phonetic="/aˈmi.ɣo/",
            related_words=["amistad", "compañero"],
        )

        # Verify file exists
        file_path = self.service.vocabulary_dir / f"{visual.visual_id}.json"
        assert file_path.exists(), "Vocabulary file not created"

        # Load and verify JSON
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["visual_id"] == visual.visual_id
        assert data["word"] == visual.word
        assert data["translation"] == visual.translation

    def test_pronunciation_persistence(self):
        """Test 15: Verify pronunciation guide persistence"""
        # Create pronunciation guide
        guide = self.service.create_pronunciation_guide(
            word_or_phrase="bonjour",
            language="fr",
            phonetic_spelling="bon-zhoor",
            ipa_notation="/bɔ̃.ʒuʁ/",
            difficulty_level=1,
        )

        # Verify file exists
        file_path = self.service.pronunciation_dir / f"{guide.guide_id}.json"
        assert file_path.exists(), "Pronunciation guide file not created"

        # Load and verify JSON
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["guide_id"] == guide.guide_id
        assert data["word_or_phrase"] == guide.word_or_phrase
        assert data["language"] == guide.language

    # ==================== Integration Tests ====================

    def test_complete_workflow(self):
        """Test 16: Complete visual learning workflow"""
        # Create comprehensive learning resource
        flowchart = self.service.create_grammar_flowchart(
            concept=GrammarConceptType.VERB_CONJUGATION,
            title="Complete Spanish Verb Guide",
            description="Comprehensive verb conjugation",
            language="es",
            difficulty_level=3,
        )

        # Add nodes
        self.service.add_flowchart_node(
            flowchart_id=flowchart.flowchart_id,
            title="Identify Verb",
            description="Determine verb ending",
            node_type="decision",
            content="Look at the verb ending: -ar, -er, or -ir",
        )

        # Create related vocabulary
        self.service.create_vocabulary_visual(
            word="hablar",
            language="es",
            translation="to speak",
            visualization_type=VocabularyVisualizationType.CONTEXT_EXAMPLES,
            example_sentences=[
                {"spanish": "Yo hablo español.", "english": "I speak Spanish."}
            ],
        )

        # Create pronunciation guide
        self.service.create_pronunciation_guide(
            word_or_phrase="hablo",
            language="es",
            phonetic_spelling="ah-blow",
            ipa_notation="/ˈa.βlo/",
        )

        # Create progress visualization
        self.service.create_progress_visualization(
            user_id="test_user",
            visualization_type=VisualizationType.LINE_CHART,
            title="Verb Mastery Progress",
            description="Track verb learning",
            data_points=[{"lesson": 1, "mastery": 45}],
        )

        # Verify all components exist
        assert self.service.get_flowchart(flowchart.flowchart_id) is not None
        assert len(self.service.get_vocabulary_visuals(language="es")) >= 1
        assert len(self.service.get_pronunciation_guides(language="es")) >= 1
        assert len(self.service.get_user_progress_visualizations("test_user")) >= 1

    def run_all_tests(self):
        """Run all tests and generate report"""
        print("\n" + "=" * 70)
        print("🧪 VISUAL LEARNING SYSTEM - COMPREHENSIVE TEST SUITE")
        print("=" * 70)

        self.setup()

        # Run all tests
        print("\n📝 Running Grammar Flowchart Tests...")
        self.run_test(
            "Test 1: Create Grammar Flowchart", self.test_create_grammar_flowchart
        )
        self.run_test("Test 2: Add Flowchart Nodes", self.test_add_flowchart_nodes)
        self.run_test(
            "Test 3: Connect Flowchart Nodes", self.test_connect_flowchart_nodes
        )
        self.run_test("Test 4: Get Flowchart", self.test_get_flowchart)
        self.run_test("Test 5: List Flowcharts", self.test_list_flowcharts)

        print("\n📊 Running Progress Visualization Tests...")
        self.run_test(
            "Test 6: Create Progress Visualization",
            self.test_create_progress_visualization,
        )
        self.run_test(
            "Test 7: Get User Visualizations", self.test_get_user_visualizations
        )

        print("\n📚 Running Visual Vocabulary Tests...")
        self.run_test(
            "Test 8: Create Vocabulary Visual", self.test_create_vocabulary_visual
        )
        self.run_test(
            "Test 9: Get Vocabulary Visuals", self.test_get_vocabulary_visuals
        )

        print("\n🗣️ Running Pronunciation Guide Tests...")
        self.run_test(
            "Test 10: Create Pronunciation Guide", self.test_create_pronunciation_guide
        )
        self.run_test(
            "Test 11: Get Pronunciation Guides", self.test_get_pronunciation_guides
        )

        print("\n💾 Running Data Persistence Tests...")
        self.run_test("Test 12: Flowchart Persistence", self.test_flowchart_persistence)
        self.run_test(
            "Test 13: Visualization Persistence", self.test_visualization_persistence
        )
        self.run_test(
            "Test 14: Vocabulary Persistence", self.test_vocabulary_persistence
        )
        self.run_test(
            "Test 15: Pronunciation Persistence", self.test_pronunciation_persistence
        )

        print("\n🔗 Running Integration Tests...")
        self.run_test("Test 16: Complete Workflow", self.test_complete_workflow)

        self.teardown()

        # Generate final report
        self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        success_rate = (
            (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        )

        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 70)

        if success_rate == 100.0:
            print("\n🎉 ALL TESTS PASSED - 100% SUCCESS RATE ACHIEVED!")
        elif success_rate >= 90.0:
            print("\n⚠️  PARTIAL SUCCESS - Some tests failed")
        else:
            print("\n❌ SIGNIFICANT FAILURES - Review test results")

        # Save detailed results
        results_file = Path("validation_results/visual_learning_test_results.json")
        results_file.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "test_suite": "Visual Learning System",
            "timestamp": datetime.now().isoformat(),
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "success_rate": f"{success_rate:.1f}%",
            "test_results": self.test_results,
        }

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Detailed results saved to: {results_file}")

        return success_rate == 100.0


def main():
    """Main test execution"""
    tester = VisualLearningSystemTester()
    success = tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
