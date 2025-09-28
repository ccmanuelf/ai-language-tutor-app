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


def create_admin_sidebar(current_page: str = "users"):
    """Create admin dashboard sidebar navigation"""

    # Navigation items with icons and labels
    nav_items = [
        {
            "key": "users",
            "label": "User Management",
            "icon": "👥",
            "href": "/dashboard/admin/users",
            "description": "Manage user accounts and permissions",
        },
        {
            "key": "languages",
            "label": "Language Config",
            "icon": "🌐",
            "href": "/dashboard/admin/languages",
            "description": "Configure languages and voice models",
        },
        {
            "key": "features",
            "label": "Feature Toggles",
            "icon": "🎛️",
            "href": "/dashboard/admin/features",
            "description": "Enable/disable system features",
        },
        {
            "key": "ai_models",
            "label": "AI Models",
            "icon": "🤖",
            "href": "/dashboard/admin/ai-models",
            "description": "Manage AI models and providers",
        },
        {
            "key": "system",
            "label": "System Status",
            "icon": "📊",
            "href": "/dashboard/admin/system",
            "description": "Monitor system health and performance",
        },
        {
            "key": "analytics",
            "label": "Analytics",
            "icon": "📈",
            "href": "/dashboard/admin/analytics",
            "description": "View usage analytics and reports",
        },
    ]

    return Div(
        # Sidebar Header
        Div(
            Div(
                Span("⚙️", cls="text-2xl"),
                H2("Admin Panel", cls="text-xl font-bold text-white ml-3"),
                cls="flex items-center",
            ),
            cls="p-6 border-b border-gray-700",
        ),
        # Navigation Menu
        Nav(
            *[
                A(
                    Div(
                        Span(item["icon"], cls="text-xl"),
                        Div(
                            Span(item["label"], cls="font-medium text-white"),
                            Span(
                                item["description"],
                                cls="text-xs text-gray-300 block mt-1",
                            ),
                            cls="ml-3",
                        ),
                        cls="flex items-center p-3 rounded-lg transition-colors duration-200 "
                        + (
                            "bg-purple-600 text-white"
                            if current_page == item["key"]
                            else "text-gray-300 hover:bg-gray-700 hover:text-white"
                        ),
                    ),
                    href=item["href"],
                    cls="block mb-2",
                )
                for item in nav_items
            ],
            cls="p-4",
        ),
        # Footer section
        Div(
            Div(
                P("Admin Dashboard", cls="text-sm font-medium text-gray-300"),
                P("AI Language Tutor", cls="text-xs text-gray-400"),
                cls="text-center",
            ),
            cls="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-700",
        ),
        cls="fixed left-0 top-0 h-full w-64 bg-gray-800 shadow-lg z-40",
    )


def create_admin_header(current_user: dict, page_title: str = "Admin Dashboard"):
    """Create admin dashboard header"""

    user_name = (
        current_user.get("first_name", "") + " " + current_user.get("last_name", "")
    )
    if not user_name.strip():
        user_name = current_user.get("username", "Admin User")

    return Header(
        Div(
            # Page Title Section
            Div(
                H1(page_title, cls="text-2xl font-bold text-white"),
                P("Administrative Control Panel", cls="text-gray-300 text-sm"),
                cls="flex-1",
            ),
            # User Info and Actions
            Div(
                # Quick Actions
                Div(
                    Button(
                        "🔄 Refresh",
                        onclick="location.reload()",
                        cls="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors mr-3",
                    ),
                    Button(
                        "📊 System Status",
                        onclick="window.open('/dashboard/admin/system', '_blank')",
                        cls="px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors mr-3",
                    ),
                    cls="flex items-center",
                ),
                # User Profile Dropdown
                Div(
                    Div(
                        Span("👤", cls="text-lg mr-2"),
                        Span(user_name, cls="text-white font-medium mr-2"),
                        Span("▼", cls="text-gray-300 text-xs"),
                        cls="flex items-center px-4 py-2 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition-colors",
                        onclick="toggleUserMenu()",
                    ),
                    # Dropdown Menu (hidden by default)
                    Div(
                        A(
                            Span("👤", cls="mr-2"),
                            "Profile",
                            href="/profile",
                            cls="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white",
                        ),
                        A(
                            Span("🏠", cls="mr-2"),
                            "Return to App",
                            href="/",
                            cls="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white",
                        ),
                        A(
                            Span("🚪", cls="mr-2"),
                            "Logout",
                            href="/auth/logout",
                            cls="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white",
                        ),
                        cls="absolute right-0 top-12 w-48 bg-gray-800 rounded-lg shadow-lg border border-gray-700 hidden",
                        id="userMenu",
                    ),
                    cls="relative",
                ),
                cls="flex items-center space-x-4",
            ),
            cls="flex items-center justify-between",
        ),
        # JavaScript for dropdown functionality
        Script("""
            function toggleUserMenu() {
                const menu = document.getElementById('userMenu');
                menu.classList.toggle('hidden');
            }

            // Close dropdown when clicking outside
            document.addEventListener('click', function(event) {
                const menu = document.getElementById('userMenu');
                const button = event.target.closest('[onclick="toggleUserMenu()"]');
                if (!button && !menu.contains(event.target)) {
                    menu.classList.add('hidden');
                }
            });
        """),
        cls="bg-gray-900 shadow-lg p-4 mb-6",
    )
