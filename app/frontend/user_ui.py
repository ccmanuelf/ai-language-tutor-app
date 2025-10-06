"""
User Profile UI Components for AI Language Tutor App

FastHTML-based user interface components for:
- User profile management
- User registration and login
- Profile editing and preferences
- Family account management
- Learning progress dashboard
"""

from fasthtml.common import *
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models.schemas import UserResponse, UserProfile


def user_profile_page(user_data: UserProfile) -> Div:
    """Create user profile page"""
    return Div(
        H1("User Profile", cls="text-3xl font-bold mb-6"),

        # Profile Overview Card
        Div(
            H2("Profile Information", cls="text-xl font-semibold mb-4"),
            Div(
                Div(
                    Label("Username:", cls="font-medium text-gray-700"),
                    P(user_data.username, cls="text-gray-900")
                ),
                Div(
                    Label("Role:", cls="font-medium text-gray-700"),
                    P(user_data.role.title(), cls="text-gray-900")
                ),
                Div(
                    Label("Languages:", cls="font-medium text-gray-700"),
                    P(f"{len(user_data.languages)} languages", cls="text-gray-900")
                ) if user_data.languages else None,
                cls="grid grid-cols-1 md:grid-cols-3 gap-4"
            ),
            cls="bg-white p-6 rounded-lg shadow-md mb-6"
        ),

        # Learning Progress Section
        learning_progress_section(user_data.learning_progress) if user_data.learning_progress else None,

        # Statistics Section
        statistics_section(user_data),

        # Actions
        Div(
            Button("Edit Profile",
                   hx_get=f"/users/{user_data.user_id}/edit",
                   cls="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2"),
            Button("View Settings",
                   hx_get=f"/users/{user_data.user_id}/settings",
                   cls="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"),
            cls="mt-6"
        ),

        cls="container mx-auto px-4 py-8"
    )


def learning_progress_section(progress_data: List[Dict[str, Any]]) -> Div:
    """Create learning progress section"""
    return Div(
        H2("Learning Progress", cls="text-xl font-semibold mb-4"),
        Div(
            *[progress_card(progress) for progress in progress_data],
            cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        ),
        cls="mb-6"
    )


def progress_card(progress: Dict[str, Any]) -> Div:
    """Create individual progress card"""
    progress_percentage = progress.get("progress_percentage", 0)

    return Div(
        Div(
            H3(f"{progress['language'].upper()} - {progress['skill_type'].title()}",
               cls="font-semibold text-gray-800"),
            Div(
                Div(
                    f"Level {progress.get('current_level', 1)}/{progress.get('target_level', 10)}",
                    cls="text-sm text-gray-600"
                ),
                Div(
                    Div(
                        style=f"width: {progress_percentage}%",
                        cls="bg-blue-500 h-2 rounded"
                    ),
                    cls="w-full bg-gray-200 rounded h-2"
                ),
                P(f"{progress_percentage:.1f}% Complete", cls="text-sm text-gray-600 mt-1")
            )
        ),
        cls="bg-white p-4 rounded-lg shadow border"
    )


def statistics_section(user_data: UserProfile) -> Div:
    """Create statistics section"""
    return Div(
        H2("Statistics", cls="text-xl font-semibold mb-4"),
        Div(
            stat_card("Total Conversations", user_data.total_conversations, "💬"),
            stat_card("Study Time", f"{user_data.total_study_time_minutes} min", "⏱️"),
            stat_card("Languages", len(user_data.languages), "🌍"),
            stat_card("Progress Items", len(user_data.learning_progress), "📊"),
            cls="grid grid-cols-2 md:grid-cols-4 gap-4"
        ),
        cls="bg-white p-6 rounded-lg shadow-md mb-6"
    )


def stat_card(title: str, value: Any, icon: str) -> Div:
    """Create individual statistic card"""
    return Div(
        Div(icon, cls="text-2xl mb-2"),
        Div(
            P(str(value), cls="text-2xl font-bold text-gray-900"),
            P(title, cls="text-sm text-gray-600")
        ),
        cls="text-center"
    )


def user_edit_form(user_data: UserResponse) -> Form:
    """Create user edit form"""
    return Form(
        H1("Edit Profile", cls="text-2xl font-bold mb-6"),

        Div(
            Label("Username", cls="block text-sm font-medium text-gray-700"),
            Input(
                type="text",
                name="username",
                value=user_data.username,
                required=True,
                cls="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            ),
            cls="mb-4"
        ),

        Div(
            Label("Email", cls="block text-sm font-medium text-gray-700"),
            Input(
                type="email",
                name="email",
                value=user_data.email or "",
                cls="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            ),
            cls="mb-4"
        ),

        Div(
            Label("First Name", cls="block text-sm font-medium text-gray-700"),
            Input(
                type="text",
                name="first_name",
                value=user_data.first_name or "",
                cls="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            ),
            cls="mb-4"
        ),

        Div(
            Label("Last Name", cls="block text-sm font-medium text-gray-700"),
            Input(
                type="text",
                name="last_name",
                value=user_data.last_name or "",
                cls="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            ),
            cls="mb-4"
        ),

        Div(
            Label("UI Language", cls="block text-sm font-medium text-gray-700"),
            Select(
                Option("English", value="en", selected=user_data.ui_language == "en"),
                Option("中文", value="zh", selected=user_data.ui_language == "zh"),
                Option("Français", value="fr", selected=user_data.ui_language == "fr"),
                Option("Deutsch", value="de", selected=user_data.ui_language == "de"),
                Option("日本語", value="ja", selected=user_data.ui_language == "ja"),
                name="ui_language",
                cls="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            ),
            cls="mb-6"
        ),

        Div(
            Button("Save Changes",
                   type="submit",
                   cls="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2"),
            Button("Cancel",
                   type="button",
                   hx_get=f"/users/{user_data.user_id}",
                   cls="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"),
            cls="flex space-x-2"
        ),

        hx_put=f"/users/{user_data.user_id}",
        hx_target="#main-content",
        cls="max-w-lg mx-auto bg-white p-6 rounded-lg shadow-md"
    )


def login_form() -> Form:
    """Create login form"""
    return Form(
        H1("Login", cls="text-2xl font-bold mb-6 text-center"),

        Div(
            Label("User ID", cls="block text-sm font-medium text-gray-700"),
            Input(
                type="text",
                name="user_id",
                required=True,
                placeholder="Enter your user ID",
                cls="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            ),
            cls="mb-4"
        ),

        Div(
            Label("Password", cls="block text-sm font-medium text-gray-700"),
            Input(
                type="password",
                name="password",
                required=True,
                placeholder="Enter your password",
                cls="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            ),
            cls="mb-6"
        ),

        Button("Login",
               type="submit",
               cls="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"),

        Div(
            A("Create Account", href="/register", cls="text-blue-500 hover:text-blue-700"),
            cls="text-center mt-4"
        ),

        hx_post="/auth/login",
        hx_target="#main-content",
        cls="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md"
    )


def child_pin_form() -> Form:
    """Create child PIN login form"""
    return Form(
        H1("Enter Your PIN", cls="text-2xl font-bold mb-6 text-center"),

        Div(
            Input(
                type="password",
                name="pin",
                maxlength="4",
                required=True,
                placeholder="****",
                cls="text-center text-2xl tracking-widest w-32 mx-auto block rounded-md border-gray-300 shadow-sm"
            ),
            cls="mb-6"
        ),

        Button("Continue",
               type="submit",
               cls="w-full bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"),

        hx_post="/auth/pin-login",
        hx_target="#main-content",
        cls="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md"
    )


def registration_form() -> Form:
    """Create user registration form"""
    return Form(
        H1("Create Account", cls="text-2xl font-bold mb-6 text-center"),

        Div(
            Label("User ID", cls="block text-sm font-medium text-gray-700"),
            Input(
                type="text",
                name="user_id",
                required=True,
                placeholder="Choose a unique user ID",
                cls="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            ),
            P("This will be your login identifier", cls="text-sm text-gray-500 mt-1"),
            cls="mb-4"
        ),

        Div(
            Label("Username", cls="block text-sm font-medium text-gray-700"),
            Input(
                type="text",
                name="username",
                required=True,
                placeholder="Your display name",
                cls="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            ),
            cls="mb-4"
        ),

        Div(
            Label("Email", cls="block text-sm font-medium text-gray-700"),
            Input(
                type="email",
                name="email",
                placeholder="your.email@example.com",
                cls="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            ),
            cls="mb-4"
        ),

        Div(
            Label("Account Type", cls="block text-sm font-medium text-gray-700"),
            Select(
                Option("Child Account", value="child", selected=True),
                Option("Parent Account", value="parent"),
                name="role",
                cls="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            ),
            cls="mb-4"
        ),

        Div(
            Label("Password", cls="block text-sm font-medium text-gray-700"),
            Input(
                type="password",
                name="password",
                placeholder="Enter a secure password",
                cls="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            ),
            P("Leave blank for child accounts (PIN will be generated)",
              cls="text-sm text-gray-500 mt-1"),
            cls="mb-6"
        ),

        Button("Create Account",
               type="submit",
               cls="w-full bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"),

        Div(
            A("Already have an account?", href="/login", cls="text-blue-500 hover:text-blue-700"),
            cls="text-center mt-4"
        ),

        hx_post="/auth/register",
        hx_target="#main-content",
        cls="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md"
    )


def user_dashboard(user_data: UserProfile) -> Div:
    """Create user dashboard"""
    return Div(
        # Header
        Div(
            H1(f"Welcome back, {user_data.username}!", cls="text-3xl font-bold text-gray-900"),
            P(f"Role: {user_data.role.title()}", cls="text-gray-600"),
            cls="mb-8"
        ),

        # Quick Stats
        Div(
            H2("Your Progress", cls="text-xl font-semibold mb-4"),
            statistics_section(user_data),
            cls="mb-8"
        ),

        # Recent Activity or Learning Progress
        learning_progress_section(user_data.learning_progress) if user_data.learning_progress else Div(
            H2("Get Started", cls="text-xl font-semibold mb-4"),
            P("Welcome to your language learning journey! Set up your first language to begin.",
              cls="text-gray-600 mb-4"),
            Button("Add Language",
                   hx_get=f"/users/{user_data.user_id}/languages/add",
                   cls="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"),
            cls="bg-white p-6 rounded-lg shadow-md"
        ),

        # Quick Actions
        Div(
            H2("Quick Actions", cls="text-xl font-semibold mb-4"),
            Div(
                Button("Start Conversation",
                       hx_get="/chat/new",
                       cls="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded mr-2"),
                Button("Upload Document",
                       hx_get="/documents/upload",
                       cls="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded mr-2"),
                Button("View Progress",
                       hx_get=f"/users/{user_data.user_id}/progress",
                       cls="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"),
                cls="flex flex-wrap gap-2"
            ),
            cls="bg-white p-6 rounded-lg shadow-md"
        ),

        cls="container mx-auto px-4 py-8"
    )


def error_message(message: str, error_type: str = "error") -> Div:
    """Create error message component"""
    colors = {
        "error": "bg-red-100 border-red-400 text-red-700",
        "warning": "bg-yellow-100 border-yellow-400 text-yellow-700",
        "success": "bg-green-100 border-green-400 text-green-700",
        "info": "bg-blue-100 border-blue-400 text-blue-700"
    }

    return Div(
        P(message),
        cls=f"border px-4 py-3 rounded {colors.get(error_type, colors['error'])}"
    )


def loading_spinner() -> Div:
    """Create loading spinner"""
    return Div(
        Div(cls="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"),
        P("Loading...", cls="mt-2 text-gray-600"),
        cls="flex flex-col items-center justify-center py-8"
    )


# Navigation and Layout Components
def main_layout(content: Any, user_data: Optional[UserResponse] = None) -> Html:
    """Create main layout wrapper"""
    return Html(
        Head(
            Title("AI Language Tutor"),
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Script(src="https://unpkg.com/htmx.org@1.9.6"),
            Script(src="https://cdn.tailwindcss.com"),
        ),
        Body(
            # Navigation
            nav_bar(user_data) if user_data else None,

            # Main Content
            Div(
                content,
                id="main-content",
                cls="min-h-screen bg-gray-50"
            ),

            # Footer
            footer(),

            cls="bg-gray-50"
        )
    )


def nav_bar(user_data: UserResponse) -> Nav:
    """Create navigation bar"""
    return Nav(
        Div(
            # Logo/Brand
            Div(
                A("AI Language Tutor", href="/dashboard", cls="text-xl font-bold text-white"),
                cls="flex-shrink-0"
            ),

            # Navigation Links
            Div(
                A("Dashboard", href="/dashboard", cls="text-white hover:text-gray-300 px-3 py-2"),
                A("Chat", href="/chat", cls="text-white hover:text-gray-300 px-3 py-2"),
                A("Documents", href="/documents", cls="text-white hover:text-gray-300 px-3 py-2"),
                A("Progress", href=f"/users/{user_data.user_id}/progress", cls="text-white hover:text-gray-300 px-3 py-2"),
                cls="hidden md:flex space-x-1"
            ),

            # User Menu
            Div(
                A(user_data.username, href=f"/users/{user_data.user_id}", cls="text-white hover:text-gray-300 px-3 py-2"),
                A("Logout", href="/auth/logout", cls="text-white hover:text-gray-300 px-3 py-2"),
                cls="flex space-x-1"
            ),

            cls="flex items-center justify-between px-4"
        ),
        cls="bg-blue-600 shadow-lg"
    )


def footer() -> Footer:
    """Create footer"""
    return Footer(
        Div(
            P(f"© {datetime.now().year} AI Language Tutor - Personal Family Educational Tool",
              cls="text-center text-gray-600"),
            cls="container mx-auto px-4 py-6"
        ),
        cls="bg-white border-t mt-auto"
    )
