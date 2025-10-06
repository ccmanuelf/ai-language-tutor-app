"""
Admin Dashboard Frontend Module
AI Language Tutor App - Personal Family Educational Tool

This module provides the admin dashboard interface for user management,
system configuration, and administrative controls.
"""

from fasthtml.common import *
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.frontend.styles import load_styles
from app.frontend.layout import create_header, create_footer


def create_admin_header(current_user: Dict[str, Any]) -> Div:
    """Create admin-specific header with dashboard navigation"""
    return Div(
        # Main header
        create_header(current_user),
        # Admin navigation bar
        Nav(
            Div(
                H2(
                    "Admin Dashboard",
                    style="color: white; margin: 0; font-size: 1.5rem; font-weight: 600;",
                ),
                Div(
                    A(
                        "Users",
                        href="/dashboard/admin/users",
                        style="color: white; text-decoration: none; padding: 8px 16px; border-radius: 6px; background: rgba(255,255,255,0.1); margin-right: 8px;",
                    ),
                    A(
                        "Languages",
                        href="/dashboard/admin/languages",
                        style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px; margin-right: 8px;",
                    ),
                    A(
                        "Features",
                        href="/dashboard/admin/features",
                        style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px; margin-right: 8px;",
                    ),
                    A(
                        "System",
                        href="/dashboard/admin/system",
                        style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px;",
                    ),
                    style="display: flex; align-items: center;",
                ),
                style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 20px;",
            ),
            style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 12px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);",
        ),
        style="margin-bottom: 24px;",
    )


def create_user_card(user: Dict[str, Any]) -> Div:
    """Create a user card for the user management interface"""

    # Role-specific styling
    role_colors = {
        "ADMIN": "#dc2626",  # Red
        "PARENT": "#2563eb",  # Blue
        "CHILD": "#16a34a",  # Green
        "GUEST": "#6b7280",  # Gray
    }

    role = user.get("role", "CHILD")
    role_color = role_colors.get(role, "#6b7280")

    # Status indicator
    status_color = "#16a34a" if user.get("is_active", True) else "#dc2626"
    status_text = "Active" if user.get("is_active", True) else "Inactive"

    return Div(
        # User header
        Div(
            Div(
                H3(
                    f"{user.get('first_name', '')} {user.get('last_name', '')}"
                    or user.get("username", "Unknown User"),
                    style="margin: 0; color: #1f2937; font-size: 1.1rem; font-weight: 600;",
                ),
                P(
                    user.get("email", "No email"),
                    style="margin: 4px 0 0 0; color: #6b7280; font-size: 0.9rem;",
                ),
                style="flex: 1;",
            ),
            Div(
                Span(
                    role,
                    style=f"background: {role_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 500; margin-right: 8px;",
                ),
                Span(
                    status_text,
                    style=f"background: {status_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 500;",
                ),
                style="display: flex; align-items: center;",
            ),
            style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;",
        ),
        # User details
        Div(
            Div(
                Strong("User ID: "),
                user.get("user_id", "N/A"),
                style="margin-bottom: 8px; color: #4b5563; font-size: 0.9rem;",
            ),
            Div(
                Strong("Created: "),
                datetime.fromisoformat(
                    user.get("created_at", "").replace("Z", "+00:00")
                ).strftime("%Y-%m-%d %H:%M")
                if user.get("created_at")
                else "Unknown",
                style="margin-bottom: 8px; color: #4b5563; font-size: 0.9rem;",
            ),
            Div(
                Strong("Last Login: "),
                datetime.fromisoformat(
                    user.get("last_login", "").replace("Z", "+00:00")
                ).strftime("%Y-%m-%d %H:%M")
                if user.get("last_login")
                else "Never",
                style="margin-bottom: 16px; color: #4b5563; font-size: 0.9rem;",
            )
            if user.get("last_login")
            else None,
            style="margin-bottom: 16px;",
        ),
        # Action buttons
        Div(
            Button(
                "Edit",
                onclick=f"editUser('{user.get('user_id')}')",
                style="background: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; margin-right: 8px; font-size: 0.9rem;",
            ),
            Button(
                "Toggle Status",
                onclick=f"toggleUserStatus('{user.get('user_id')}')",
                style="background: #6b7280; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; margin-right: 8px; font-size: 0.9rem;",
            ),
            Button(
                "Delete" if role != "ADMIN" else "Protected",
                onclick=f"deleteUser('{user.get('user_id')}')"
                if role != "ADMIN"
                else "alert('Admin users cannot be deleted')",
                disabled=role == "ADMIN",
                style=f"background: {'#dc2626' if role != 'ADMIN' else '#9ca3af'}; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: {'pointer' if role != 'ADMIN' else 'not-allowed'}; font-size: 0.9rem;",
            ),
            style="display: flex; justify-content: flex-end;",
        ),
        style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); border: 1px solid #e5e7eb; margin-bottom: 16px;",
    )


def create_add_user_modal() -> Div:
    """Create modal for adding new users"""
    return Div(
        Div(
            Div(
                Div(
                    H3(
                        "Add New User",
                        style="margin: 0; color: #1f2937; font-size: 1.3rem; font-weight: 600;",
                    ),
                    Button(
                        "×",
                        onclick="closeAddUserModal()",
                        style="background: none; border: none; font-size: 24px; color: #6b7280; cursor: pointer; line-height: 1;",
                    ),
                    style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;",
                ),
                Form(
                    Div(
                        Label(
                            "First Name:",
                            style="display: block; margin-bottom: 6px; color: #374151; font-weight: 500;",
                        ),
                        Input(
                            id="newUserFirstName",
                            type="text",
                            required=True,
                            style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.9rem;",
                        ),
                        style="margin-bottom: 16px;",
                    ),
                    Div(
                        Label(
                            "Last Name:",
                            style="display: block; margin-bottom: 6px; color: #374151; font-weight: 500;",
                        ),
                        Input(
                            id="newUserLastName",
                            type="text",
                            required=True,
                            style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.9rem;",
                        ),
                        style="margin-bottom: 16px;",
                    ),
                    Div(
                        Label(
                            "Email:",
                            style="display: block; margin-bottom: 6px; color: #374151; font-weight: 500;",
                        ),
                        Input(
                            id="newUserEmail",
                            type="email",
                            required=True,
                            style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.9rem;",
                        ),
                        style="margin-bottom: 16px;",
                    ),
                    Div(
                        Label(
                            "Username:",
                            style="display: block; margin-bottom: 6px; color: #374151; font-weight: 500;",
                        ),
                        Input(
                            id="newUserUsername",
                            type="text",
                            required=True,
                            style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.9rem;",
                        ),
                        style="margin-bottom: 16px;",
                    ),
                    Div(
                        Label(
                            "Role:",
                            style="display: block; margin-bottom: 6px; color: #374151; font-weight: 500;",
                        ),
                        Select(
                            Option("Parent", value="PARENT"),
                            Option("Child", value="CHILD"),
                            id="newUserRole",
                            style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.9rem;",
                        ),
                        style="margin-bottom: 16px;",
                    ),
                    Div(
                        Label(
                            "Password:",
                            style="display: block; margin-bottom: 6px; color: #374151; font-weight: 500;",
                        ),
                        Input(
                            id="newUserPassword",
                            type="password",
                            required=True,
                            style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.9rem;",
                        ),
                        style="margin-bottom: 20px;",
                    ),
                    Div(
                        Button(
                            "Cancel",
                            type="button",
                            onclick="closeAddUserModal()",
                            style="background: #6b7280; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; margin-right: 12px;",
                        ),
                        Button(
                            "Create User",
                            type="submit",
                            style="background: #16a34a; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer;",
                        ),
                        style="display: flex; justify-content: flex-end;",
                    ),
                    onsubmit="createUser(event)",
                    style="max-width: 100%;",
                ),
                style="background: white; border-radius: 12px; padding: 24px; max-width: 500px; width: 90vw; max-height: 90vh; overflow-y: auto;",
            ),
            style="display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px;",
        ),
        id="addUserModal",
        style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 1000;",
    )


def create_guest_session_panel(guest_info: Optional[Dict[str, Any]] = None) -> Div:
    """Create guest session management panel"""
    if guest_info:
        return Div(
            H3(
                "Current Guest Session",
                style="margin: 0 0 16px 0; color: #1f2937; font-size: 1.2rem; font-weight: 600;",
            ),
            Div(
                Div(
                    P(
                        f"Guest ID: {guest_info.get('user_id', 'Unknown')}",
                        style="margin: 0 0 8px 0; color: #4b5563;",
                    ),
                    P(
                        f"Session Started: {guest_info.get('created_at', 'Unknown')}",
                        style="margin: 0 0 8px 0; color: #4b5563;",
                    ),
                    P(
                        f"Status: Active",
                        style="margin: 0; color: #16a34a; font-weight: 500;",
                    ),
                    style="flex: 1;",
                ),
                Button(
                    "Terminate Session",
                    onclick="terminateGuestSession()",
                    style="background: #dc2626; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;",
                ),
                style="display: flex; justify-content: space-between; align-items: center;",
            ),
            style="background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; padding: 16px; margin-bottom: 24px;",
        )
    else:
        return Div(
            H3(
                "Guest Session Management",
                style="margin: 0 0 16px 0; color: #1f2937; font-size: 1.2rem; font-weight: 600;",
            ),
            Div(
                P(
                    "No active guest sessions",
                    style="margin: 0; color: #6b7280; font-style: italic;",
                ),
                Button(
                    "Create Guest Session",
                    onclick="createGuestSession()",
                    style="background: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; margin-left: 16px;",
                ),
                style="display: flex; justify-content: space-between; align-items: center;",
            ),
            style="background: #f3f4f6; border: 1px solid #d1d5db; border-radius: 8px; padding: 16px; margin-bottom: 24px;",
        )


def create_user_management_page(
    users: List[Dict[str, Any]],
    current_user: Dict[str, Any],
    guest_info: Optional[Dict[str, Any]] = None,
) -> Html:
    """Create the main user management page"""

    return Html(
        Head(
            Title("Admin Dashboard - User Management"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            load_styles(),
            Style("""
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 16px;
                    margin-bottom: 24px;
                }

                .stat-card {
                    background: white;
                    border-radius: 8px;
                    padding: 16px;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    border: 1px solid #e5e7eb;
                }

                .stat-number {
                    font-size: 2rem;
                    font-weight: 700;
                    color: #1f2937;
                    margin: 0;
                }

                .stat-label {
                    color: #6b7280;
                    font-size: 0.9rem;
                    margin: 4px 0 0 0;
                }

                .search-bar {
                    background: white;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 24px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    border: 1px solid #e5e7eb;
                }

                @media (max-width: 768px) {
                    .stats-grid {
                        grid-template-columns: repeat(2, 1fr);
                    }
                }
            """),
            Script("""
                function openAddUserModal() {
                    document.getElementById('addUserModal').style.display = 'block';
                }

                function closeAddUserModal() {
                    document.getElementById('addUserModal').style.display = 'none';
                }

                function createUser(event) {
                    event.preventDefault();

                    const userData = {
                        first_name: document.getElementById('newUserFirstName').value,
                        last_name: document.getElementById('newUserLastName').value,
                        email: document.getElementById('newUserEmail').value,
                        username: document.getElementById('newUserUsername').value,
                        role: document.getElementById('newUserRole').value,
                        password: document.getElementById('newUserPassword').value
                    };

                    fetch('/api/admin/users', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(userData)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('User created successfully!');
                            location.reload();
                        } else {
                            alert('Error creating user: ' + data.message);
                        }
                    })
                    .catch(error => {
                        alert('Error creating user: ' + error.message);
                    });
                }

                function editUser(userId) {
                    // TODO: Implement edit user functionality
                    alert('Edit user functionality coming soon!');
                }

                function toggleUserStatus(userId) {
                    fetch(`/api/admin/users/${userId}/toggle-status`, {
                        method: 'POST'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('Error toggling user status: ' + data.message);
                        }
                    })
                    .catch(error => {
                        alert('Error toggling user status: ' + error.message);
                    });
                }

                function deleteUser(userId) {
                    if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
                        fetch(`/api/admin/users/${userId}`, {
                            method: 'DELETE'
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                alert('User deleted successfully!');
                                location.reload();
                            } else {
                                alert('Error deleting user: ' + data.message);
                            }
                        })
                        .catch(error => {
                            alert('Error deleting user: ' + error.message);
                        });
                    }
                }

                function createGuestSession() {
                    fetch('/api/admin/guest-session', {
                        method: 'POST'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('Guest session created successfully!');
                            location.reload();
                        } else {
                            alert('Error creating guest session: ' + data.message);
                        }
                    })
                    .catch(error => {
                        alert('Error creating guest session: ' + error.message);
                    });
                }

                function terminateGuestSession() {
                    if (confirm('Are you sure you want to terminate the current guest session?')) {
                        fetch('/api/admin/guest-session', {
                            method: 'DELETE'
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                alert('Guest session terminated successfully!');
                                location.reload();
                            } else {
                                alert('Error terminating guest session: ' + data.message);
                            }
                        })
                        .catch(error => {
                            alert('Error terminating guest session: ' + error.message);
                        });
                    }
                }

                function searchUsers() {
                    const searchTerm = document.getElementById('userSearch').value.toLowerCase();
                    const userCards = document.querySelectorAll('.user-card');

                    userCards.forEach(card => {
                        const text = card.textContent.toLowerCase();
                        if (text.includes(searchTerm)) {
                            card.style.display = 'block';
                        } else {
                            card.style.display = 'none';
                        }
                    });
                }
            """),
        ),
        Body(
            create_admin_header(current_user),
            # Main content
            Div(
                # Statistics
                Div(
                    Div(
                        H2(str(len(users)), className="stat-number"),
                        P("Total Users", className="stat-label"),
                        className="stat-card",
                    ),
                    Div(
                        H2(
                            str(len([u for u in users if u.get("role") == "ADMIN"])),
                            className="stat-number",
                        ),
                        P("Admins", className="stat-label"),
                        className="stat-card",
                    ),
                    Div(
                        H2(
                            str(len([u for u in users if u.get("role") == "PARENT"])),
                            className="stat-number",
                        ),
                        P("Parents", className="stat-label"),
                        className="stat-card",
                    ),
                    Div(
                        H2(
                            str(len([u for u in users if u.get("role") == "CHILD"])),
                            className="stat-number",
                        ),
                        P("Children", className="stat-label"),
                        className="stat-card",
                    ),
                    Div(
                        H2(
                            str(len([u for u in users if u.get("is_active", True)])),
                            className="stat-number",
                        ),
                        P("Active Users", className="stat-label"),
                        className="stat-card",
                    ),
                    className="stats-grid",
                ),
                # Guest session management
                create_guest_session_panel(guest_info),
                # Search and actions
                Div(
                    Div(
                        Input(
                            id="userSearch",
                            type="text",
                            placeholder="Search users by name, email, or role...",
                            onkeyup="searchUsers()",
                            style="flex: 1; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.9rem;",
                        ),
                        Button(
                            "Add New User",
                            onclick="openAddUserModal()",
                            style="background: #16a34a; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; margin-left: 12px; font-weight: 500;",
                        ),
                        style="display: flex; align-items: center;",
                    ),
                    className="search-bar",
                ),
                # User list
                Div(
                    H2(
                        "User Management",
                        style="margin: 0 0 20px 0; color: #1f2937; font-size: 1.5rem; font-weight: 600;",
                    ),
                    Div(
                        *[
                            Div(create_user_card(user), className="user-card")
                            for user in users
                        ],
                        style="display: grid; gap: 16px;",
                    ),
                    style="background: #f9fafb; border-radius: 12px; padding: 24px;",
                ),
                style="max-width: 1200px; margin: 0 auto; padding: 0 20px;",
            ),
            create_footer(),
            create_add_user_modal(),
            style="min-height: 100vh; background: #f3f4f6;",
        ),
    )
