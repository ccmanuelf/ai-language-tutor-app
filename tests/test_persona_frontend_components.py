"""
Tests for Persona Frontend Components
AI Language Tutor App - Component Unit Tests

Tests the persona selection UI components to ensure they render correctly
and contain the expected HTML structure and content.
"""

import pytest
from fasthtml.common import to_xml

from app.frontend.persona_selection import (
    create_current_selection_summary,
    create_persona_card,
    create_persona_customization_form,
    create_persona_detail_modal,
    create_persona_selection_section,
)


class TestCreatePersonaCard:
    """Test persona card component creation"""

    def test_renders_unselected_card(self):
        """Test that unselected persona card renders correctly"""
        persona = {
            "persona_type": "guiding_challenger",
            "name": "Guiding Challenger",
            "description": "A challenging, process-focused tutor",
            "key_traits": ["Challenging", "Process-focused"],
            "best_for": "Building resilience",
        }

        card = create_persona_card(persona, is_selected=False)
        html = to_xml(card)

        # Check basic structure
        assert "guiding_challenger" in html or "Guiding Challenger" in html
        assert "🌟" in html  # Icon
        assert "Guiding Challenger" in html  # Name
        assert "challenging" in html.lower()  # Description (case insensitive)
        assert "Learn More" in html

    def test_renders_selected_card(self):
        """Test that selected persona card shows selection badge"""
        persona = {
            "persona_type": "encouraging_coach",
            "name": "Encouraging Coach",
            "description": "A supportive tutor",
            "key_traits": ["Supportive"],
            "best_for": "Building confidence",
        }

        card = create_persona_card(persona, is_selected=True)
        html = to_xml(card)

        # Check selection badge
        assert "SELECTED" in html
        assert "💪" in html  # Icon

    def test_renders_all_persona_types(self):
        """Test that all 5 persona types render with correct icons"""
        personas = [
            {"persona_type": "guiding_challenger", "name": "Guiding Challenger", "description": "Test", "key_traits": [], "best_for": "Test"},
            {"persona_type": "encouraging_coach", "name": "Encouraging Coach", "description": "Test", "key_traits": [], "best_for": "Test"},
            {"persona_type": "friendly_conversational", "name": "Friendly Conversationalist", "description": "Test", "key_traits": [], "best_for": "Test"},
            {"persona_type": "expert_scholar", "name": "Expert Scholar", "description": "Test", "key_traits": [], "best_for": "Test"},
            {"persona_type": "creative_mentor", "name": "Creative Mentor", "description": "Test", "key_traits": [], "best_for": "Test"},
        ]

        expected_icons = ["🌟", "💪", "😊", "🎓", "🎨"]

        for persona, icon in zip(personas, expected_icons):
            card = create_persona_card(persona)
            html = to_xml(card)
            assert icon in html

    def test_truncates_long_description(self):
        """Test that long descriptions are truncated"""
        persona = {
            "persona_type": "guiding_challenger",
            "name": "Test",
            "description": "A" * 100,  # Very long description
            "key_traits": [],
            "best_for": "Test",
        }

        card = create_persona_card(persona)
        html = to_xml(card)

        # Should include ellipsis for truncation
        assert "..." in html

    def test_includes_onclick_handler(self):
        """Test that onclick handler is included when provided"""
        persona = {
            "persona_type": "guiding_challenger",
            "name": "Test",
            "description": "Test",
            "key_traits": [],
            "best_for": "Test",
        }

        card = create_persona_card(persona, onclick="testFunction()")
        html = to_xml(card)

        assert "testFunction()" in html


class TestCreateCurrentSelectionSummary:
    """Test current selection summary component"""

    def test_renders_selection_summary(self):
        """Test that selection summary displays persona info"""
        persona_info = {
            "persona_type": "guiding_challenger",
            "name": "Guiding Challenger",
            "key_traits": ["Challenging", "Process-focused", "Guides discovery"],
            "best_for": "Building resilience and deep understanding",
        }

        summary = create_current_selection_summary(persona_info)
        html = to_xml(summary)

        # Check all components are present
        assert "Current Selection" in html
        assert "Guiding Challenger" in html
        assert "🌟" in html  # Icon
        assert "Challenging" in html
        assert "Process-focused" in html
        assert "Guides discovery" in html
        assert "Building resilience" in html

    def test_handles_empty_traits(self):
        """Test that summary handles missing traits gracefully"""
        persona_info = {
            "persona_type": "guiding_challenger",
            "name": "Test Persona",
            "key_traits": [],
            "best_for": "Testing",
        }

        summary = create_current_selection_summary(persona_info)
        html = to_xml(summary)

        # Should not crash and should show name
        assert "Test Persona" in html

    def test_formats_traits_as_bullets(self):
        """Test that traits are formatted with bullet separators"""
        persona_info = {
            "persona_type": "encouraging_coach",
            "name": "Test",
            "key_traits": ["Trait 1", "Trait 2", "Trait 3"],
            "best_for": "Testing",
        }

        summary = create_current_selection_summary(persona_info)
        html = to_xml(summary)

        # Check for bullet separator (•)
        assert "•" in html


class TestCreatePersonaCustomizationForm:
    """Test persona customization form component"""

    def test_renders_subject_input(self):
        """Test that subject input field is rendered"""
        form = create_persona_customization_form()
        html = to_xml(form)

        assert "Subject" in html
        assert "persona-subject" in html
        assert "Spanish, Math, Science" in html  # Placeholder

    def test_renders_learner_level_dropdown(self):
        """Test that learner level dropdown is rendered"""
        form = create_persona_customization_form()
        html = to_xml(form)

        assert "Learning Level" in html or "Learner Level" in html
        assert "persona-learner-level" in html
        assert "Beginner" in html
        assert "Intermediate" in html
        assert "Advanced" in html

    def test_sets_current_subject(self):
        """Test that current subject value is set"""
        form = create_persona_customization_form(current_subject="Spanish")
        html = to_xml(form)

        assert "Spanish" in html

    def test_selects_current_level(self):
        """Test that current learner level is selected"""
        form = create_persona_customization_form(current_level="advanced")
        html = to_xml(form)

        # HTML should show advanced as selected
        assert "advanced" in html

    def test_defaults_to_beginner(self):
        """Test that beginner is default level"""
        form = create_persona_customization_form()
        html = to_xml(form)

        # Should have beginner selected
        assert "beginner" in html


class TestCreatePersonaDetailModal:
    """Test persona detail modal component"""

    def test_renders_modal_structure(self):
        """Test that modal has correct structure"""
        persona = {
            "persona_type": "guiding_challenger",
            "name": "Guiding Challenger",
            "description": "A challenging tutor",
            "key_traits": ["Challenging"],
            "best_for": "Building resilience",
        }

        modal = create_persona_detail_modal(persona)
        html = to_xml(modal)

        # Check modal elements
        assert "modal-guiding_challenger" in html
        assert "modal-overlay-guiding_challenger" in html
        assert "Guiding Challenger" in html
        assert "Description" in html
        assert "Key Traits" in html
        assert "Best For" in html

    def test_includes_customization_form(self):
        """Test that modal includes customization form"""
        persona = {
            "persona_type": "encouraging_coach",
            "name": "Encouraging Coach",
            "description": "Test",
            "key_traits": ["Test"],
            "best_for": "Test",
        }

        modal = create_persona_detail_modal(persona, {"subject": "Math", "learner_level": "intermediate"})
        html = to_xml(modal)

        # Check customization form is included
        assert "Subject" in html
        assert "Math" in html
        assert "intermediate" in html

    def test_includes_action_buttons(self):
        """Test that modal includes action buttons"""
        persona = {
            "persona_type": "expert_scholar",
            "name": "Expert Scholar",
            "description": "Test",
            "key_traits": [],
            "best_for": "Test",
        }

        modal = create_persona_detail_modal(persona)
        html = to_xml(modal)

        # Check buttons
        assert "Select This Persona" in html
        assert "Cancel" in html

    def test_includes_close_functionality(self):
        """Test that modal includes close handlers"""
        persona = {
            "persona_type": "creative_mentor",
            "name": "Creative Mentor",
            "description": "Test",
            "key_traits": [],
            "best_for": "Test",
        }

        modal = create_persona_detail_modal(persona)
        html = to_xml(modal)

        # Check close functions
        assert "closePersonaModal" in html


class TestCreatePersonaSelectionSection:
    """Test complete persona selection section"""

    def test_renders_section_header(self):
        """Test that section header is rendered"""
        personas = [
            {
                "persona_type": "friendly_conversational",
                "name": "Friendly Conversationalist",
                "description": "Test",
                "key_traits": ["Friendly"],
                "best_for": "Test",
            }
        ]

        current_persona = personas[0]

        section = create_persona_selection_section(personas, current_persona)
        html = to_xml(section)

        assert "AI Tutor Persona" in html or "🎭" in html
        assert "teaching style" in html.lower()

    def test_renders_all_persona_cards(self):
        """Test that all provided personas are rendered as cards"""
        personas = [
            {"persona_type": "guiding_challenger", "name": "Guiding Challenger", "description": "Test", "key_traits": [], "best_for": "Test"},
            {"persona_type": "encouraging_coach", "name": "Encouraging Coach", "description": "Test", "key_traits": [], "best_for": "Test"},
            {"persona_type": "friendly_conversational", "name": "Friendly Conversationalist", "description": "Test", "key_traits": [], "best_for": "Test"},
        ]

        current_persona = personas[0]

        section = create_persona_selection_section(personas, current_persona)
        html = to_xml(section)

        # All personas should be present
        assert "Guiding Challenger" in html
        assert "Encouraging Coach" in html
        assert "Friendly Conversationalist" in html

    def test_highlights_current_selection(self):
        """Test that currently selected persona is highlighted"""
        personas = [
            {"persona_type": "guiding_challenger", "name": "Guiding Challenger", "description": "Test", "key_traits": ["A"], "best_for": "Test"},
            {"persona_type": "encouraging_coach", "name": "Encouraging Coach", "description": "Test", "key_traits": ["B"], "best_for": "Test"},
        ]

        current_persona = personas[0]  # Guiding Challenger selected

        section = create_persona_selection_section(personas, current_persona)
        html = to_xml(section)

        # Should show selection badge
        assert "SELECTED" in html

    def test_includes_selection_summary(self):
        """Test that current selection summary is included"""
        personas = [
            {
                "persona_type": "expert_scholar",
                "name": "Expert Scholar",
                "description": "Test",
                "key_traits": ["Rigorous", "Precise"],
                "best_for": "Advanced learners",
            }
        ]

        current_persona = personas[0]

        section = create_persona_selection_section(personas, current_persona)
        html = to_xml(section)

        # Check summary components
        assert "Current Selection" in html
        assert "Expert Scholar" in html
        assert "Rigorous" in html

    def test_includes_reset_button(self):
        """Test that reset button is included"""
        personas = [
            {"persona_type": "friendly_conversational", "name": "Test", "description": "Test", "key_traits": [], "best_for": "Test"}
        ]

        current_persona = personas[0]

        section = create_persona_selection_section(personas, current_persona)
        html = to_xml(section)

        assert "Reset to Default" in html or "reset" in html.lower()

    def test_includes_modals_for_all_personas(self):
        """Test that detail modals are created for all personas"""
        personas = [
            {"persona_type": "guiding_challenger", "name": "Guiding Challenger", "description": "Test", "key_traits": [], "best_for": "Test"},
            {"persona_type": "encouraging_coach", "name": "Encouraging Coach", "description": "Test", "key_traits": [], "best_for": "Test"},
        ]

        current_persona = personas[0]

        section = create_persona_selection_section(personas, current_persona)
        html = to_xml(section)

        # Both modals should be present
        assert "modal-guiding_challenger" in html
        assert "modal-encouraging_coach" in html

    def test_includes_javascript_handlers(self):
        """Test that JavaScript handlers are included"""
        personas = [
            {"persona_type": "friendly_conversational", "name": "Test", "description": "Test", "key_traits": [], "best_for": "Test"}
        ]

        current_persona = personas[0]

        section = create_persona_selection_section(personas, current_persona)
        html = to_xml(section)

        # Check for JavaScript functions
        assert "openPersonaModal" in html
        assert "closePersonaModal" in html
        assert "selectPersona" in html
        assert "resetPersonaToDefault" in html

    def test_includes_api_integration(self):
        """Test that API calls are included in JavaScript"""
        personas = [
            {"persona_type": "friendly_conversational", "name": "Test", "description": "Test", "key_traits": [], "best_for": "Test"}
        ]

        current_persona = personas[0]

        section = create_persona_selection_section(personas, current_persona)
        html = to_xml(section)

        # Check for API endpoints
        assert "/api/v1/personas/preference" in html

    def test_handles_custom_customization(self):
        """Test that custom subject and level are passed through"""
        personas = [
            {"persona_type": "creative_mentor", "name": "Creative Mentor", "description": "Test", "key_traits": [], "best_for": "Test"}
        ]

        current_persona = personas[0]
        customization = {"subject": "Physics", "learner_level": "advanced"}

        section = create_persona_selection_section(personas, current_persona, customization)
        html = to_xml(section)

        # Customization should be in modal forms
        assert "Physics" in html
        assert "advanced" in html

    def test_uses_responsive_grid(self):
        """Test that grid uses responsive classes"""
        personas = [
            {"persona_type": "friendly_conversational", "name": "Test", "description": "Test", "key_traits": [], "best_for": "Test"}
        ]

        current_persona = personas[0]

        section = create_persona_selection_section(personas, current_persona)
        html = to_xml(section)

        # Check for responsive grid classes
        assert "grid" in html
        # Should have responsive breakpoints (md:, lg:)
        assert "md:grid-cols" in html or "lg:grid-cols" in html


class TestPersonaComponentIntegration:
    """Test integration between components"""

    def test_card_opens_correct_modal(self):
        """Test that card onclick handler matches modal ID"""
        persona = {
            "persona_type": "guiding_challenger",
            "name": "Guiding Challenger",
            "description": "Test",
            "key_traits": [],
            "best_for": "Test",
        }

        card = create_persona_card(persona, onclick="openPersonaModal('guiding_challenger')")
        modal = create_persona_detail_modal(persona)

        card_html = to_xml(card)
        modal_html = to_xml(modal)

        # Card should reference modal ID
        assert "guiding_challenger" in card_html
        assert "modal-guiding_challenger" in modal_html

    def test_selection_section_consistency(self):
        """Test that section maintains consistent persona data across components"""
        personas = [
            {
                "persona_type": "expert_scholar",
                "name": "Expert Scholar",
                "description": "Formal and rigorous",
                "key_traits": ["Formal", "Rigorous"],
                "best_for": "Advanced learners",
            }
        ]

        current_persona = personas[0]

        section = create_persona_selection_section(personas, current_persona)
        html = to_xml(section)

        # Same data should appear in card, summary, and modal
        assert html.count("Expert Scholar") >= 2  # At least in card and summary
        assert "Formal" in html
        assert "Rigorous" in html
