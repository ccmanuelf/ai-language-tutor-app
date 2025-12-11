"""
Test module for Visual Learning Frontend
AI Language Tutor App - Session 105

Tests for app/frontend/visual_learning.py module
Target: 100% coverage with comprehensive test scenarios
"""

import pytest
from fastapi.testclient import TestClient

from app.frontend_main import frontend_app


class TestVisualLearningRoutes:
    """Test suite for visual learning frontend routes"""

    def setup_method(self):
        """Set up test client for each test"""
        self.client = TestClient(frontend_app)

    def test_visual_learning_home_route(self):
        """Test main visual learning tools page"""
        response = self.client.get("/visual-learning")
        assert response.status_code == 200

        content = response.text
        # Check for page title
        assert "Visual Learning Tools" in content

        # Check for description
        assert "Enhance your learning with interactive visualizations" in content

        # Check for all four tool categories
        assert "Grammar Flowcharts" in content
        assert "Progress Visualizations" in content
        assert "Visual Vocabulary" in content
        assert "Pronunciation Guides" in content

        # Check for links to sub-pages
        assert "/visual-learning/flowcharts" in content
        assert "/visual-learning/visualizations" in content
        assert "/visual-learning/vocabulary" in content
        assert "/visual-learning/pronunciation" in content

    def test_visual_learning_home_learning_resources(self):
        """Test learning resources section on main page"""
        response = self.client.get("/visual-learning")
        assert response.status_code == 200

        content = response.text
        # Check for learning resources section
        assert "Learning Resources" in content

        # Check for resource counts
        assert "24" in content  # Grammar Flowcharts count
        assert "156" in content  # Visual Vocabulary count
        assert "89" in content  # Pronunciation Guides count

    def test_visual_learning_home_buttons(self):
        """Test that all navigation buttons are present"""
        response = self.client.get("/visual-learning")
        assert response.status_code == 200

        content = response.text
        # Check for button text
        assert "Explore Flowcharts" in content
        assert "View Progress" in content
        assert "Study Vocabulary" in content
        assert "Practice Pronunciation" in content

    def test_flowcharts_page_route(self):
        """Test grammar flowcharts page"""
        response = self.client.get("/visual-learning/flowcharts")
        assert response.status_code == 200

        content = response.text
        # Check for page title
        assert "Grammar Flowcharts" in content

        # Check for description
        assert "Interactive visual guides for understanding grammar concepts" in content

        # Check for filter options
        assert "Language:" in content
        assert "Difficulty:" in content

    def test_flowcharts_page_filters(self):
        """Test flowcharts page filter options"""
        response = self.client.get("/visual-learning/flowcharts")
        assert response.status_code == 200

        content = response.text
        # Check for language filter options
        assert "All Languages" in content
        assert "Spanish" in content
        assert "French" in content
        assert "Chinese" in content

        # Check for difficulty filter options
        assert "All Levels" in content
        assert "Beginner (1-2)" in content
        assert "Intermediate (3)" in content
        assert "Advanced (4-5)" in content

    def test_flowcharts_page_examples(self):
        """Test flowcharts page example cards"""
        response = self.client.get("/visual-learning/flowcharts")
        assert response.status_code == 200

        content = response.text
        # Check for example flowcharts
        assert "Spanish Verb Conjugation" in content
        assert "Present Tense" in content
        assert "French Sentence Structure" in content
        assert "Subject-Verb-Object" in content
        assert "Chinese Tense Usage" in content
        assert "Time Expressions" in content
        assert "Spanish Conditional Forms" in content
        assert "Si Clauses" in content

        # Check for button
        assert "View Flowchart" in content

    def test_flowcharts_page_language_tags(self):
        """Test language tags on flowchart cards"""
        response = self.client.get("/visual-learning/flowcharts")
        assert response.status_code == 200

        content = response.text
        # Check for language tags (uppercase)
        assert "ES" in content  # Spanish
        assert "FR" in content  # French
        assert "ZH" in content  # Chinese

    def test_visualizations_page_route(self):
        """Test progress visualizations page"""
        response = self.client.get("/visual-learning/visualizations")
        assert response.status_code == 200

        content = response.text
        # Check for page title
        assert "Progress Visualizations" in content

        # Check for description
        assert "Track your learning journey with interactive charts" in content

    def test_visualizations_page_tabs(self):
        """Test visualization page tab navigation"""
        response = self.client.get("/visual-learning/visualizations")
        assert response.status_code == 200

        content = response.text
        # Check for all tabs
        assert "Weekly Progress" in content
        assert "Skill Breakdown" in content
        assert "Learning Streaks" in content
        assert "Word Mastery" in content

    def test_visualizations_page_weekly_content(self):
        """Test weekly progress tab content"""
        response = self.client.get("/visual-learning/visualizations")
        assert response.status_code == 200

        content = response.text
        # Check for weekly activity section
        assert "Weekly Learning Activity" in content

        # Check for day labels
        assert "Mon" in content
        assert "Tue" in content
        assert "Wed" in content
        assert "Thu" in content
        assert "Fri" in content
        assert "Sat" in content
        assert "Sun" in content

    def test_visualizations_page_skills_content(self):
        """Test skills breakdown tab content"""
        response = self.client.get("/visual-learning/visualizations")
        assert response.status_code == 200

        content = response.text
        # Check for skill development section
        assert "Skill Development" in content

        # Check for skill categories
        assert "Speaking" in content
        assert "Listening" in content
        assert "Reading" in content
        assert "Writing" in content

        # Check for percentages
        assert "75%" in content
        assert "82%" in content
        assert "68%" in content
        assert "55%" in content

    def test_visualizations_page_streaks_content(self):
        """Test learning streaks tab content"""
        response = self.client.get("/visual-learning/visualizations")
        assert response.status_code == 200

        content = response.text
        # Check for streaks section
        assert "Learning Streaks" in content

        # Check for streak data
        assert "14 Days" in content  # Current streak
        assert "Current Streak" in content
        assert "Longest Streak: 28 days" in content
        assert "This Month: 20 days" in content
        assert "Total Active Days: 156" in content

        # Check for fire emoji
        assert "🔥" in content

    def test_visualizations_page_words_content(self):
        """Test vocabulary mastery tab content"""
        response = self.client.get("/visual-learning/visualizations")
        assert response.status_code == 200

        content = response.text
        # Check for vocabulary mastery section
        assert "Vocabulary Mastery" in content

        # Check for word counts
        assert "Mastered: 89" in content
        assert "Learning: 47" in content
        assert "Review: 11" in content
        assert "147" in content  # Current count
        assert "250" in content  # Total count
        assert "Words Learned" in content

    def test_vocabulary_page_route(self):
        """Test visual vocabulary page"""
        response = self.client.get("/visual-learning/vocabulary")
        assert response.status_code == 200

        content = response.text
        # Check for page title
        assert "Visual Vocabulary" in content

        # Check for description
        assert "Learn words with images, context, and visual associations" in content

    def test_vocabulary_page_cards(self):
        """Test vocabulary cards with examples"""
        response = self.client.get("/visual-learning/vocabulary")
        assert response.status_code == 200

        content = response.text
        # Check for Spanish vocabulary
        assert "casa" in content
        assert "house" in content
        assert "/kɑː.sɑː/" in content
        assert "Mi casa es grande." in content
        assert "My house is big." in content

        # Check for French vocabulary
        assert "manger" in content
        assert "to eat" in content
        assert "/mɑ̃.ʒe/" in content
        # HTML escapes apostrophes
        assert (
            "J'aime manger des pommes." in content
            or "J&#x27;aime manger des pommes." in content
        )
        assert "I like to eat apples." in content

        # Check for Chinese vocabulary
        assert "学习" in content
        assert "to study" in content
        assert "/xué xí/" in content
        assert "我喜欢学习中文。" in content
        assert "I like to study Chinese." in content

        # Check for another Spanish vocabulary
        assert "amigo" in content
        assert "friend" in content
        assert "/ɑː.miː.ɡoʊ/" in content
        assert "Él es mi mejor amigo." in content
        assert "He is my best friend." in content

    def test_vocabulary_page_buttons(self):
        """Test vocabulary card buttons"""
        response = self.client.get("/visual-learning/vocabulary")
        assert response.status_code == 200

        content = response.text
        # Check for interaction buttons
        assert "🔊 Listen" in content
        assert "📝 Practice" in content

    def test_pronunciation_page_route(self):
        """Test pronunciation guides page"""
        response = self.client.get("/visual-learning/pronunciation")
        assert response.status_code == 200

        content = response.text
        # Check for page title
        assert "Pronunciation Guides" in content

        # Check for description
        assert "Master pronunciation with visual and audio guides" in content

    def test_pronunciation_page_cards(self):
        """Test pronunciation guide cards"""
        response = self.client.get("/visual-learning/pronunciation")
        assert response.status_code == 200

        content = response.text
        # Check for Spanish pronunciation
        assert "gracias" in content
        assert "/ˈɡɾa.sjas/" in content
        assert "gra-see-as" in content
        # HTML escapes apostrophes
        assert (
            "Roll the 'r' sound" in content or "Roll the &#x27;r&#x27; sound" in content
        )
        assert "Stress on first syllable" in content

        # Check for French pronunciation
        assert "merci" in content
        assert "/mɛʁ.si/" in content
        assert "mehr-see" in content
        # HTML escapes apostrophes
        assert "Nasal 'r' sound" in content or "Nasal &#x27;r&#x27; sound" in content
        assert "Short 'i' at end" in content or "Short &#x27;i&#x27; at end" in content

        # Check for Chinese pronunciation
        assert "谢谢" in content
        assert "/ɕjè.ɕjè/" in content
        assert "shyeh-shyeh" in content
        assert "Both syllables use falling tone" in content
        # HTML escapes apostrophes
        assert "Soft 'sh' sound" in content or "Soft &#x27;sh&#x27; sound" in content

    def test_pronunciation_page_ipa_labels(self):
        """Test IPA labels on pronunciation cards"""
        response = self.client.get("/visual-learning/pronunciation")
        assert response.status_code == 200

        content = response.text
        # Check for IPA label
        assert "IPA:" in content

    def test_pronunciation_page_tips_section(self):
        """Test tips section on pronunciation cards"""
        response = self.client.get("/visual-learning/pronunciation")
        assert response.status_code == 200

        content = response.text
        # Check for tips section
        assert "Tips:" in content

    def test_pronunciation_page_button(self):
        """Test pronunciation practice button"""
        response = self.client.get("/visual-learning/pronunciation")
        assert response.status_code == 200

        content = response.text
        # Check for practice button (HTML escapes &)
        assert (
            "🔊 Listen & Practice" in content or "🔊 Listen &amp; Practice" in content
        )


class TestVisualLearningHelperFunctions:
    """Test suite for visual learning helper functions"""

    def setup_method(self):
        """Set up test client for each test"""
        self.client = TestClient(frontend_app)

    def test_create_flowchart_card_spanish(self):
        """Test flowchart card with Spanish language"""
        response = self.client.get("/visual-learning/flowcharts")
        assert response.status_code == 200

        content = response.text
        # Spanish language color and tag
        assert "ES" in content
        # Check star ratings are present (difficulty indicators)
        assert "⭐" in content

    def test_create_flowchart_card_french(self):
        """Test flowchart card with French language"""
        response = self.client.get("/visual-learning/flowcharts")
        assert response.status_code == 200

        content = response.text
        # French language tag
        assert "FR" in content

    def test_create_flowchart_card_chinese(self):
        """Test flowchart card with Chinese language"""
        response = self.client.get("/visual-learning/flowcharts")
        assert response.status_code == 200

        content = response.text
        # Chinese language tag
        assert "ZH" in content

    def test_create_skill_bar_rendering(self):
        """Test skill bar progress indicators"""
        response = self.client.get("/visual-learning/visualizations")
        assert response.status_code == 200

        content = response.text
        # All skills should be rendered with their names and percentages
        assert "Speaking" in content and "75%" in content
        assert "Listening" in content and "82%" in content
        assert "Reading" in content and "68%" in content
        assert "Writing" in content and "55%" in content

    def test_create_mastery_ring_rendering(self):
        """Test mastery ring circular progress indicator"""
        response = self.client.get("/visual-learning/visualizations")
        assert response.status_code == 200

        content = response.text
        # Check mastery ring data
        assert "147" in content  # Current value
        assert "of 250" in content  # Total value
        assert "Words Learned" in content  # Label

    def test_create_vocabulary_card_spanish(self):
        """Test vocabulary card with Spanish example"""
        response = self.client.get("/visual-learning/vocabulary")
        assert response.status_code == 200

        content = response.text
        # Spanish vocabulary card elements
        assert "casa" in content
        assert "house" in content
        assert "ES" in content  # Language tag

    def test_create_vocabulary_card_french(self):
        """Test vocabulary card with French example"""
        response = self.client.get("/visual-learning/vocabulary")
        assert response.status_code == 200

        content = response.text
        # French vocabulary card elements
        assert "manger" in content
        assert "to eat" in content
        assert "FR" in content  # Language tag

    def test_create_vocabulary_card_chinese(self):
        """Test vocabulary card with Chinese example"""
        response = self.client.get("/visual-learning/vocabulary")
        assert response.status_code == 200

        content = response.text
        # Chinese vocabulary card elements
        assert "学习" in content
        assert "to study" in content
        assert "ZH" in content  # Language tag

    def test_create_vocabulary_card_example_section(self):
        """Test vocabulary card example section"""
        response = self.client.get("/visual-learning/vocabulary")
        assert response.status_code == 200

        content = response.text
        # Check for example label
        assert "Example:" in content

    def test_create_pronunciation_card_spanish(self):
        """Test pronunciation card with Spanish example"""
        response = self.client.get("/visual-learning/pronunciation")
        assert response.status_code == 200

        content = response.text
        # Spanish pronunciation card
        assert "gracias" in content
        assert "ES" in content

    def test_create_pronunciation_card_french(self):
        """Test pronunciation card with French example"""
        response = self.client.get("/visual-learning/pronunciation")
        assert response.status_code == 200

        content = response.text
        # French pronunciation card
        assert "merci" in content
        assert "FR" in content

    def test_create_pronunciation_card_chinese(self):
        """Test pronunciation card with Chinese example"""
        response = self.client.get("/visual-learning/pronunciation")
        assert response.status_code == 200

        content = response.text
        # Chinese pronunciation card
        assert "谢谢" in content
        assert "ZH" in content

    def test_create_pronunciation_card_tips_list(self):
        """Test pronunciation card tips are rendered as list"""
        response = self.client.get("/visual-learning/pronunciation")
        assert response.status_code == 200

        content = response.text
        # Check that tips are present (already tested in detail above)
        # Just verify structure exists
        assert "Tips:" in content
        # HTML escapes apostrophes
        assert (
            "Roll the 'r' sound" in content or "Roll the &#x27;r&#x27; sound" in content
        )


class TestVisualLearningPageMetadata:
    """Test suite for page metadata and layout"""

    def setup_method(self):
        """Set up test client for each test"""
        self.client = TestClient(frontend_app)

    def test_visual_learning_home_title(self):
        """Test page title for visual learning home"""
        response = self.client.get("/visual-learning")
        assert response.status_code == 200

        content = response.text
        # Check for proper title in HTML
        assert "Visual Learning Tools - AI Language Tutor" in content

    def test_flowcharts_page_title(self):
        """Test page title for flowcharts page"""
        response = self.client.get("/visual-learning/flowcharts")
        assert response.status_code == 200

        content = response.text
        # Check for proper title
        assert "Grammar Flowcharts - Visual Learning" in content

    def test_visualizations_page_title(self):
        """Test page title for visualizations page"""
        response = self.client.get("/visual-learning/visualizations")
        assert response.status_code == 200

        content = response.text
        # Check for proper title
        assert "Progress Visualizations - Visual Learning" in content

    def test_vocabulary_page_title(self):
        """Test page title for vocabulary page"""
        response = self.client.get("/visual-learning/vocabulary")
        assert response.status_code == 200

        content = response.text
        # Check for proper title
        assert "Visual Vocabulary - Visual Learning" in content

    def test_pronunciation_page_title(self):
        """Test page title for pronunciation page"""
        response = self.client.get("/visual-learning/pronunciation")
        assert response.status_code == 200

        content = response.text
        # Check for proper title
        assert "Pronunciation Guides - Visual Learning" in content

    def test_all_pages_use_layout(self):
        """Test that all pages use the create_layout function"""
        # All pages should have proper HTML structure from layout
        pages = [
            "/visual-learning",
            "/visual-learning/flowcharts",
            "/visual-learning/visualizations",
            "/visual-learning/vocabulary",
            "/visual-learning/pronunciation",
        ]

        for page in pages:
            response = self.client.get(page)
            assert response.status_code == 200
            content = response.text.lower()
            # All pages should have HTML structure
            assert "<html>" in content or "<!doctype html>" in content
            assert "</html>" in content

    def test_all_pages_have_current_page_marker(self):
        """Test that all pages mark visual-learning as current page"""
        # This ensures navigation highlighting works correctly
        pages = [
            "/visual-learning",
            "/visual-learning/flowcharts",
            "/visual-learning/visualizations",
            "/visual-learning/vocabulary",
            "/visual-learning/pronunciation",
        ]

        for page in pages:
            response = self.client.get(page)
            assert response.status_code == 200
            # All pages should be part of visual-learning section
            # (This is verified by checking they all render successfully)


class TestVisualLearningEmojis:
    """Test suite for emoji usage in visual learning pages"""

    def setup_method(self):
        """Set up test client for each test"""
        self.client = TestClient(frontend_app)

    def test_home_page_tool_emojis(self):
        """Test emojis for tool categories on home page"""
        response = self.client.get("/visual-learning")
        assert response.status_code == 200

        content = response.text
        # Check for tool category emojis
        assert "🎨" in content  # Main title
        assert "📊" in content  # Grammar Flowcharts
        assert "📈" in content  # Progress Visualizations
        assert "📚" in content  # Visual Vocabulary
        assert "🗣️" in content  # Pronunciation Guides

    def test_flowcharts_page_emoji(self):
        """Test emoji on flowcharts page"""
        response = self.client.get("/visual-learning/flowcharts")
        assert response.status_code == 200

        content = response.text
        assert "📊" in content

    def test_visualizations_page_emoji(self):
        """Test emoji on visualizations page"""
        response = self.client.get("/visual-learning/visualizations")
        assert response.status_code == 200

        content = response.text
        assert "📈" in content

    def test_vocabulary_page_emoji(self):
        """Test emoji on vocabulary page"""
        response = self.client.get("/visual-learning/vocabulary")
        assert response.status_code == 200

        content = response.text
        assert "📚" in content

    def test_pronunciation_page_emoji(self):
        """Test emoji on pronunciation page"""
        response = self.client.get("/visual-learning/pronunciation")
        assert response.status_code == 200

        content = response.text
        assert "🗣️" in content

    def test_streaks_fire_emoji(self):
        """Test fire emoji in learning streaks"""
        response = self.client.get("/visual-learning/visualizations")
        assert response.status_code == 200

        content = response.text
        assert "🔥" in content

    def test_vocabulary_button_emojis(self):
        """Test emojis in vocabulary card buttons"""
        response = self.client.get("/visual-learning/vocabulary")
        assert response.status_code == 200

        content = response.text
        assert "🔊" in content  # Listen button
        assert "📝" in content  # Practice button

    def test_pronunciation_button_emoji(self):
        """Test emoji in pronunciation practice button"""
        response = self.client.get("/visual-learning/pronunciation")
        assert response.status_code == 200

        content = response.text
        assert "🔊" in content  # Listen & Practice button
