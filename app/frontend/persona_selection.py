"""
Persona Selection UI Components
AI Language Tutor App - Personal Family Educational Tool

This module provides frontend UI components for selecting and customizing
the AI tutor's teaching persona.
"""

from typing import Dict, List, Optional

from fasthtml.common import *


def create_persona_card(
    persona: Dict,
    is_selected: bool = False,
    onclick: Optional[str] = None,
) -> Div:
    """
    Create a persona card for the selection grid

    Args:
        persona: Persona metadata dict with:
            - persona_type: Type identifier
            - name: Display name
            - description: Short description
            - key_traits: List of key characteristics
            - best_for: Use case description
        is_selected: Whether this persona is currently selected
        onclick: Optional JavaScript onclick handler

    Returns:
        Div element containing the persona card
    """
    # Persona icons mapping
    persona_icons = {
        "guiding_challenger": "🌟",
        "encouraging_coach": "💪",
        "friendly_conversational": "😊",
        "expert_scholar": "🎓",
        "creative_mentor": "🎨",
    }

    persona_type = persona.get("persona_type", "")
    icon = persona_icons.get(persona_type, "🤖")
    name = persona.get("name", "Unknown")
    description = persona.get("description", "")

    # Determine card styling based on selection state
    if is_selected:
        card_class = "bg-gray-800 border-2 border-purple-500 rounded-lg p-4 cursor-pointer transition-all duration-200 hover:bg-gray-700 relative"
        badge = Div(
            Span("✅ SELECTED", cls="text-xs font-bold text-white"),
            cls="absolute top-2 right-2 bg-purple-600 px-2 py-1 rounded-full",
        )
    else:
        card_class = "bg-gray-800 border border-gray-700 rounded-lg p-4 cursor-pointer transition-all duration-200 hover:bg-gray-700 hover:border-purple-500"
        badge = None

    # Build card components
    card_content = [
        # Persona icon
        Div(
            Span(icon, cls="text-4xl"),
            cls="text-center mb-3",
        ),
        # Persona name
        H3(
            name,
            cls="text-lg font-bold text-white text-center mb-2",
        ),
        # Short description
        P(
            description[:80] + "..." if len(description) > 80 else description,
            cls="text-sm text-gray-300 text-center mb-3 line-clamp-3",
        ),
        # Learn more link
        Div(
            A(
                "Learn More →",
                href="#",
                onclick=f"event.preventDefault(); {onclick}" if onclick else "event.preventDefault();",
                cls="text-purple-400 hover:text-purple-300 text-sm font-medium",
            ),
            cls="text-center",
        ),
    ]

    # Add selection badge if selected
    if badge:
        card_content.insert(0, badge)

    # Add onclick handler to card
    card_attrs = {"cls": card_class}
    if onclick:
        card_attrs["onclick"] = onclick

    return Div(*card_content, **card_attrs)


def create_current_selection_summary(persona_info: Dict) -> Div:
    """
    Create summary of current persona selection

    Args:
        persona_info: Current persona information with:
            - name: Persona name
            - key_traits: List of traits
            - best_for: Use case description
            - persona_type: Type identifier

    Returns:
        Div element containing the selection summary
    """
    # Persona icons mapping
    persona_icons = {
        "guiding_challenger": "🌟",
        "encouraging_coach": "💪",
        "friendly_conversational": "😊",
        "expert_scholar": "🎓",
        "creative_mentor": "🎨",
    }

    persona_type = persona_info.get("persona_type", "")
    icon = persona_icons.get(persona_type, "🤖")
    name = persona_info.get("name", "Unknown")
    key_traits = persona_info.get("key_traits", [])
    best_for = persona_info.get("best_for", "")

    # Format key traits as bullet list
    traits_text = " • ".join(key_traits) if key_traits else "No traits available"

    return Div(
        Div(
            Span("Current Selection:", cls="text-gray-300 text-sm font-medium mr-2"),
            Span(
                f"{icon} {name}",
                cls="text-white text-lg font-bold",
            ),
            cls="mb-2",
        ),
        Div(
            Span("✅ ", cls="text-green-400"),
            Span(traits_text, cls="text-gray-300 text-sm"),
            cls="mb-2",
        ),
        Div(
            Span("Best for: ", cls="text-gray-400 text-sm font-medium"),
            Span(best_for, cls="text-gray-300 text-sm"),
        ),
        cls="bg-gray-800 rounded-lg p-4 border border-gray-700",
    )


def create_persona_customization_form(
    current_subject: str = "",
    current_level: str = "beginner",
) -> Div:
    """
    Create persona customization form (subject, learner level)

    Args:
        current_subject: Currently set subject
        current_level: Currently set learner level

    Returns:
        Div element containing the customization form
    """
    return Div(
        H4(
            "Customize Your Persona (Optional)",
            cls="text-lg font-bold text-white mb-4",
        ),
        # Subject field
        Div(
            Label("Subject (optional):", cls="text-gray-300 text-sm font-medium mb-1 block"),
            Input(
                type="text",
                name="subject",
                id="persona-subject",
                value=current_subject,
                placeholder="e.g., Spanish, Math, Science",
                cls="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500",
            ),
            P(
                "What are you learning? This helps personalize the tutor's examples.",
                cls="text-gray-400 text-xs mt-1",
            ),
            cls="mb-4",
        ),
        # Learner level dropdown
        Div(
            Label("Your Learning Level:", cls="text-gray-300 text-sm font-medium mb-1 block"),
            Select(
                Option("Beginner", value="beginner", selected=current_level == "beginner"),
                Option("Intermediate", value="intermediate", selected=current_level == "intermediate"),
                Option("Advanced", value="advanced", selected=current_level == "advanced"),
                name="learner_level",
                id="persona-learner-level",
                cls="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-500",
            ),
            cls="mb-4",
        ),
        cls="bg-gray-900 rounded-lg p-4 border border-gray-700",
    )


def create_persona_detail_modal(persona: Dict, current_customization: Dict = None) -> Div:
    """
    Create detailed persona information modal

    Args:
        persona: Full persona information
        current_customization: Current subject and learner_level (if any)

    Returns:
        Div element containing the modal (hidden by default)
    """
    if current_customization is None:
        current_customization = {"subject": "", "learner_level": "beginner"}

    # Persona icons mapping
    persona_icons = {
        "guiding_challenger": "🌟",
        "encouraging_coach": "💪",
        "friendly_conversational": "😊",
        "expert_scholar": "🎓",
        "creative_mentor": "🎨",
    }

    persona_type = persona.get("persona_type", "")
    icon = persona_icons.get(persona_type, "🤖")
    name = persona.get("name", "Unknown")
    description = persona.get("description", "")
    key_traits = persona.get("key_traits", [])
    best_for = persona.get("best_for", "")

    return Div(
        # Modal overlay
        Div(
            cls="fixed inset-0 bg-black bg-opacity-50 z-40",
            id=f"modal-overlay-{persona_type}",
            onclick=f"closePersonaModal('{persona_type}')",
            style="display: none;",
        ),
        # Modal content
        Div(
            # Modal header
            Div(
                Div(
                    Span(icon, cls="text-3xl mr-3"),
                    H3(name, cls="text-2xl font-bold text-white"),
                    cls="flex items-center",
                ),
                Button(
                    "×",
                    onclick=f"closePersonaModal('{persona_type}')",
                    cls="text-gray-400 hover:text-white text-3xl font-bold",
                ),
                cls="flex justify-between items-start mb-4 pb-4 border-b border-gray-700",
            ),
            # Description
            Div(
                H4("Description", cls="text-lg font-bold text-white mb-2"),
                P(description, cls="text-gray-300 text-sm mb-4"),
                cls="mb-4",
            ),
            # Key traits
            Div(
                H4("Key Traits", cls="text-lg font-bold text-white mb-2"),
                Ul(
                    *[
                        Li(
                            Span("✅ ", cls="text-green-400"),
                            Span(trait, cls="text-gray-300"),
                            cls="mb-1",
                        )
                        for trait in key_traits
                    ],
                    cls="list-none",
                ),
                cls="mb-4",
            ),
            # Best for
            Div(
                H4("Best For", cls="text-lg font-bold text-white mb-2"),
                P(best_for, cls="text-gray-300 text-sm"),
                cls="mb-6",
            ),
            # Customization form
            create_persona_customization_form(
                current_subject=current_customization.get("subject", ""),
                current_level=current_customization.get("learner_level", "beginner"),
            ),
            # Action buttons
            Div(
                Button(
                    "Select This Persona",
                    onclick=f"selectPersona('{persona_type}')",
                    cls="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium",
                ),
                Button(
                    "Cancel",
                    onclick=f"closePersonaModal('{persona_type}')",
                    cls="px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors font-medium ml-3",
                ),
                cls="flex justify-end mt-6",
            ),
            cls="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-gray-800 rounded-lg shadow-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto z-50 border border-gray-700",
            id=f"modal-{persona_type}",
            style="display: none;",
        ),
    )


def create_persona_selection_section(
    available_personas: List[Dict],
    current_persona: Dict,
    current_customization: Dict = None,
) -> Div:
    """
    Create complete persona selection section

    Args:
        available_personas: List of all available personas
        current_persona: Currently selected persona info
        current_customization: Current subject and learner_level

    Returns:
        Div element containing the full persona selection UI
    """
    if current_customization is None:
        current_customization = {"subject": "", "learner_level": "beginner"}

    current_persona_type = current_persona.get("persona_type", "friendly_conversational")

    return Div(
        # Section header
        Div(
            H2(
                "🎭 AI Tutor Persona",
                cls="text-2xl font-bold text-white mb-2",
            ),
            P(
                "Choose your preferred teaching style to personalize your learning experience",
                cls="text-gray-300 text-sm",
            ),
            cls="mb-6",
        ),
        # Persona cards grid
        Div(
            *[
                create_persona_card(
                    persona=persona,
                    is_selected=persona.get("persona_type") == current_persona_type,
                    onclick=f"openPersonaModal('{persona.get('persona_type')}')",
                )
                for persona in available_personas
            ],
            cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6",
        ),
        # Current selection summary
        create_current_selection_summary(current_persona),
        # Reset button
        Div(
            Button(
                "🔄 Reset to Default",
                onclick="resetPersonaToDefault()",
                cls="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm font-medium",
            ),
            cls="mt-4",
        ),
        # Modals for each persona
        *[
            create_persona_detail_modal(persona, current_customization)
            for persona in available_personas
        ],
        # JavaScript for modal interactions
        Script("""
            function openPersonaModal(personaType) {
                document.getElementById(`modal-${personaType}`).style.display = 'block';
                document.getElementById(`modal-overlay-${personaType}`).style.display = 'block';
                document.body.style.overflow = 'hidden';
            }

            function closePersonaModal(personaType) {
                document.getElementById(`modal-${personaType}`).style.display = 'none';
                document.getElementById(`modal-overlay-${personaType}`).style.display = 'none';
                document.body.style.overflow = 'auto';
            }

            async function selectPersona(personaType) {
                const subject = document.getElementById('persona-subject').value;
                const learnerLevel = document.getElementById('persona-learner-level').value;

                try {
                    const response = await fetch('/api/v1/personas/preference', {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            persona_type: personaType,
                            subject: subject,
                            learner_level: learnerLevel,
                        }),
                    });

                    if (response.ok) {
                        // Success - reload page to show updated selection
                        alert('✅ Persona updated successfully!');
                        window.location.reload();
                    } else {
                        const error = await response.json();
                        alert(`❌ Failed to update persona: ${error.detail || 'Unknown error'}`);
                    }
                } catch (error) {
                    console.error('Error updating persona:', error);
                    alert('❌ Failed to update persona. Please try again.');
                }
            }

            async function resetPersonaToDefault() {
                if (!confirm('Reset to default persona (Friendly Conversationalist)?')) {
                    return;
                }

                try {
                    const response = await fetch('/api/v1/personas/preference', {
                        method: 'DELETE',
                    });

                    if (response.ok) {
                        alert('✅ Persona reset to default!');
                        window.location.reload();
                    } else {
                        const error = await response.json();
                        alert(`❌ Failed to reset persona: ${error.detail || 'Unknown error'}`);
                    }
                } catch (error) {
                    console.error('Error resetting persona:', error);
                    alert('❌ Failed to reset persona. Please try again.');
                }
            }

            // Close modal on escape key
            document.addEventListener('keydown', function(event) {
                if (event.key === 'Escape') {
                    const modals = document.querySelectorAll('[id^="modal-"]');
                    modals.forEach(modal => {
                        if (modal.style.display === 'block') {
                            const personaType = modal.id.replace('modal-', '');
                            closePersonaModal(personaType);
                        }
                    });
                }
            });
        """),
        cls="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg shadow-lg p-6 border border-gray-700 mb-6",
        id="persona-selection-section",
    )
