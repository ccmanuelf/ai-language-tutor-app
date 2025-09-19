"""
Frontend Layout Components
AI Language Tutor App - Reusable UI Layout Elements

Provides consistent layout components:
- Navigation header
- Page layout wrapper
- Footer component
"""

from fasthtml.common import *
from .styles import load_styles


def create_header(current_page: str = "home"):
    """Create navigation header with active page highlighting"""
    return Header(
        Nav(
            A("🎯 AI Language Tutor", href="/", cls="logo"),
            Ul(
                Li(A("Home", href="/", cls="active" if current_page == "home" else "")),
                Li(
                    A(
                        "Profile",
                        href="/profile",
                        cls="active" if current_page == "profile" else "",
                    )
                ),
                Li(
                    A(
                        "Conversation",
                        href="/chat",
                        cls="active" if current_page == "chat" else "",
                    )
                ),
                Li(
                    A(
                        "Progress",
                        href="/progress",
                        cls="active" if current_page == "progress" else "",
                    )
                ),
                cls="nav-links",
            ),
            cls="nav",
        ),
        cls="header",
    )


def create_footer():
    """Create consistent footer component"""
    return Footer(
        Div(
            P("AI Language Tutor - Personal Family Educational Tool"),
            P("Backend: Operational | Speech: Ready | Database: Connected"),
            cls="container",
            style="text-align: center; padding: 2rem; color: var(--text-secondary); border-top: 1px solid var(--border-color); margin-top: 4rem;",
        )
    )


def create_layout(
    content, current_page: str = "home", title: str = "AI Language Tutor"
):
    """Create consistent page layout with header, content, and footer"""
    return Html(
        Head(
            Title(title),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            load_styles(),
        ),
        Body(
            create_header(current_page), Main(content, cls="container"), create_footer()
        ),
    )


def create_card(content, title: str = None, class_name: str = "card"):
    """Create a styled card component"""
    card_content = []
    if title:
        card_content.append(H3(title, style="margin-bottom: 1rem;"))

    if isinstance(content, list):
        card_content.extend(content)
    else:
        card_content.append(content)

    return Div(*card_content, cls=class_name)


def create_grid(items: list, columns: int = 2):
    """Create a responsive grid layout"""
    grid_class = f"grid grid-{columns}"
    return Div(*items, cls=grid_class)


def create_status_indicator(text: str, status: str = "success"):
    """Create a status indicator badge"""
    from .styles import get_status_class

    status_icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "connected": "🟢",
        "disconnected": "🔴",
        "ready": "✅",
        "loading": "⏳",
    }

    icon = status_icons.get(status, "⚠️")
    css_class = f"status-indicator {get_status_class(status)}"

    return Span(icon, text, cls=css_class)


def create_alert(message: str, alert_type: str = "info"):
    """Create an alert message component"""
    from .styles import get_alert_class

    alert_icons = {"success": "✅", "warning": "⚠️", "error": "❌", "info": "ℹ️"}

    icon = alert_icons.get(alert_type, "ℹ️")
    css_class = f"alert {get_alert_class(alert_type)}"

    return Div(Span(icon, style="margin-right: 0.5rem;"), message, cls=css_class)


def create_form_group(label: str, input_element, help_text: str = None):
    """Create a styled form group with label and input"""
    form_group = [Label(label, cls="form-label"), input_element]

    if help_text:
        form_group.append(
            Small(help_text, style="color: var(--text-secondary); font-size: 0.875rem;")
        )

    return Div(*form_group, cls="form-group")


def create_button(
    text: str, button_type: str = "primary", onclick: str = None, **kwargs
):
    """Create a styled button component"""
    css_class = f"btn btn-{button_type}"

    button_attrs = {"cls": css_class, **kwargs}

    if onclick:
        button_attrs["onclick"] = onclick

    return Button(text, **button_attrs)
