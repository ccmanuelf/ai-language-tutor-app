"""
Frontend Profile Route
AI Language Tutor App - User Profile Management

Provides comprehensive user management:
- User authentication (login/register)
- Profile management
- Family member management
- Parental controls and safety features
"""

from fasthtml.common import *
from .layout import create_layout


def create_profile_route(app):
    """Create user profile management route"""

    @app.route("/profile")
    def profile():
        """User profile management page with authentication and family features"""
        return create_layout(
            Div(
                H1("User Profile Management", style="margin-bottom: 2rem;"),
                # Login/Registration Section
                Div(
                    H2("Login or Register"),
                    Div(
                        # Login Form
                        Div(
                            H3("Login"),
                            Form(
                                Div(
                                    Label("User ID", cls="form-label"),
                                    Input(
                                        type="text",
                                        name="user_id",
                                        id="login-user-id",
                                        placeholder="Enter your user ID",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label(
                                        "Password (optional for demo)", cls="form-label"
                                    ),
                                    Input(
                                        type="password",
                                        name="password",
                                        id="login-password",
                                        placeholder="Enter password",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Button(
                                    "Login",
                                    type="button",
                                    id="login-btn",
                                    cls="btn btn-primary",
                                ),
                                style="margin-bottom: 2rem;",
                            ),
                            cls="card",
                        ),
                        # Registration Form
                        Div(
                            H3("Create New Profile"),
                            Form(
                                Div(
                                    Label("User ID", cls="form-label"),
                                    Input(
                                        type="text",
                                        name="user_id",
                                        id="reg-user-id",
                                        placeholder="Choose a unique user ID",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Username", cls="form-label"),
                                    Input(
                                        type="text",
                                        name="username",
                                        id="reg-username",
                                        placeholder="Your display name",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Email (optional)", cls="form-label"),
                                    Input(
                                        type="email",
                                        name="email",
                                        id="reg-email",
                                        placeholder="Your email address",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Account Type", cls="form-label"),
                                    Select(
                                        Option("Child (default)", value="child"),
                                        Option("Parent/Adult", value="parent"),
                                        id="reg-role",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Button(
                                    "Register",
                                    type="button",
                                    id="register-btn",
                                    cls="btn btn-secondary",
                                ),
                                method="post",
                                action="/profile/register",
                            ),
                            cls="card",
                        ),
                        cls="grid grid-2",
                    ),
                    id="auth-section",
                ),
                # Current User Profile (hidden by default)
                Div(
                    H2("Your Profile"),
                    Div(
                        Div(
                            H3("Profile Information", id="profile-username"),
                            P(id="profile-details"),
                            Span("Active", cls="status-indicator status-success"),
                            Button(
                                "Logout",
                                type="button",
                                id="logout-btn",
                                cls="btn btn-secondary",
                                style="margin-top: 1rem;",
                            ),
                        ),
                        cls="card",
                    ),
                    id="profile-section",
                    style="display: none;",
                ),
                # Family Profiles (for parents/admins)
                Div(
                    H2("Family Management"),
                    Div(
                        # Add Family Member Form
                        Div(
                            H3("Add Family Member"),
                            Form(
                                Div(
                                    Label("User ID", cls="form-label"),
                                    Input(
                                        type="text",
                                        id="new-member-user-id",
                                        placeholder="Choose unique user ID",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Name", cls="form-label"),
                                    Input(
                                        type="text",
                                        id="new-member-name",
                                        placeholder="Family member's name",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Age Group", cls="form-label"),
                                    Select(
                                        Option("Child (0-12)", value="child"),
                                        Option("Teen (13-17)", value="teen"),
                                        Option("Adult (18+)", value="adult"),
                                        id="new-member-age",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Learning Languages", cls="form-label"),
                                    Select(
                                        Option("English", value="en"),
                                        Option("Spanish", value="es"),
                                        Option("French", value="fr"),
                                        Option("Chinese", value="zh"),
                                        Option("Japanese", value="ja"),
                                        id="new-member-languages",
                                        cls="form-input",
                                        multiple=True,
                                    ),
                                    cls="form-group",
                                ),
                                Button(
                                    "Add Family Member",
                                    type="button",
                                    id="add-member-btn",
                                    cls="btn btn-primary",
                                ),
                            ),
                            cls="card",
                        ),
                        # Family Members List
                        Div(
                            H3("Current Family Members"),
                            Div(
                                Div(
                                    H4("👨‍💼 familia_admin (You)"),
                                    P("Role: Parent/Admin"),
                                    P("Languages: English, Spanish, French"),
                                    P("Level: Advanced"),
                                    P("Total Sessions: 15 | This Week: 3"),
                                    Span(
                                        "Active", cls="status-indicator status-success"
                                    ),
                                    cls="card",
                                ),
                                Div(
                                    H4("👧 estudiante_1"),
                                    P("Role: Child"),
                                    P("Languages: Spanish"),
                                    P("Level: Beginner"),
                                    P("Total Sessions: 8 | This Week: 2"),
                                    Span(
                                        "Active", cls="status-indicator status-success"
                                    ),
                                    Div(
                                        Button(
                                            "View Progress",
                                            cls="btn btn-secondary",
                                            style="margin: 0.5rem 0.5rem 0 0;",
                                        ),
                                        Button(
                                            "Manage Settings",
                                            cls="btn btn-secondary",
                                            style="margin: 0.5rem 0.5rem 0 0;",
                                        ),
                                        Button(
                                            "Safety Controls", cls="btn btn-secondary"
                                        ),
                                    ),
                                    cls="card",
                                ),
                                Div(
                                    H4("👦 Add Another Child"),
                                    P("Create profiles for all family members"),
                                    P("Each member gets personalized learning"),
                                    Button(
                                        "Add Member",
                                        cls="btn btn-primary",
                                        onclick="document.getElementById('new-member-user-id').focus()",
                                    ),
                                    cls="card",
                                    style="border: 2px dashed var(--border-color); text-align: center;",
                                ),
                                cls="grid grid-3",
                            ),
                            id="family-members-list",
                        ),
                        cls="grid grid-1",
                    ),
                    cls="card",
                    id="family-section",
                    style="display: none;",
                ),
                # Parental Controls (for parents only)
                Div(
                    H2("Parental Controls & Safety"),
                    Div(
                        Div(
                            H3("⚡ Usage Limits"),
                            P("Set daily conversation limits"),
                            Div(
                                Label("Daily Sessions per Child:", cls="form-label"),
                                Select(
                                    Option("3 sessions", value="3"),
                                    Option("5 sessions", value="5"),
                                    Option("Unlimited", value="unlimited"),
                                    cls="form-input",
                                ),
                                cls="form-group",
                            ),
                            Button("Update Limits", cls="btn btn-secondary"),
                            cls="card",
                        ),
                        Div(
                            H3("🛡️ Content Safety"),
                            P("AI conversation monitoring"),
                            Div(
                                Label("Safety Level:", cls="form-label"),
                                Select(
                                    Option("High (Strict filtering)", value="high"),
                                    Option(
                                        "Medium (Balanced)",
                                        value="medium",
                                        selected=True,
                                    ),
                                    Option("Low (Minimal filtering)", value="low"),
                                    cls="form-input",
                                ),
                                cls="form-group",
                            ),
                            Button("Update Safety", cls="btn btn-secondary"),
                            cls="card",
                        ),
                        Div(
                            H3("📊 Activity Reports"),
                            P("Monitor learning progress"),
                            Button(
                                "View Weekly Report",
                                cls="btn btn-secondary",
                                style="margin-bottom: 1rem;",
                            ),
                            Button("Download CSV", cls="btn btn-secondary"),
                            cls="card",
                        ),
                        cls="grid grid-3",
                    ),
                    cls="card",
                    id="parental-controls",
                    style="display: none;",
                ),
                _create_profile_scripts(),
            ),
            current_page="profile",
            title="Profile Management - AI Language Tutor",
        )


def _create_profile_scripts():
    """Create JavaScript for profile management functionality"""
    return Script("""
        class AuthManager {
            constructor() {
                this.token = localStorage.getItem('auth_token');
                this.currentUser = null;
                this.setupEventListeners();
                this.checkAuthStatus();
            }

            setupEventListeners() {
                // Login button
                document.getElementById('login-btn')?.addEventListener('click', () => this.login());

                // Register button
                document.getElementById('register-btn')?.addEventListener('click', () => this.register());

                // Logout button
                document.getElementById('logout-btn')?.addEventListener('click', () => this.logout());

                // Add family member button
                document.getElementById('add-member-btn')?.addEventListener('click', () => this.addFamilyMember());
            }

            async checkAuthStatus() {
                try {
                    const response = await fetch('http://localhost:8000/api/v1/auth/me', {
                        headers: this.token ? {'Authorization': `Bearer ${this.token}`} : {}
                    });
                    const data = await response.json();

                    if (data.authenticated) {
                        this.currentUser = data.user;
                        this.showAuthenticatedView();
                    } else {
                        this.showUnauthenticatedView();
                    }
                } catch (error) {
                    console.error('Auth check failed:', error);
                    this.showUnauthenticatedView();
                }
            }

            async login() {
                const userId = document.getElementById('login-user-id').value;
                const password = document.getElementById('login-password').value;

                if (!userId) {
                    alert('Please enter a user ID');
                    return;
                }

                try {
                    const response = await fetch('http://localhost:8000/api/v1/auth/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            user_id: userId,
                            password: password || ''
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        this.token = data.access_token;
                        this.currentUser = data.user;
                        localStorage.setItem('auth_token', this.token);
                        this.showAuthenticatedView();
                        alert('Login successful!');
                    } else {
                        const error = await response.json();
                        alert(`Login failed: ${error.detail}`);
                    }
                } catch (error) {
                    console.error('Login error:', error);
                    alert('Login failed: Network error');
                }
            }

            async register() {
                const userId = document.getElementById('reg-user-id').value;
                const username = document.getElementById('reg-username').value;
                const email = document.getElementById('reg-email').value;
                const role = document.getElementById('reg-role').value;

                if (!userId || !username) {
                    alert('Please fill in User ID and Username');
                    return;
                }

                try {
                    const response = await fetch('http://localhost:8000/api/v1/auth/register', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            user_id: userId,
                            username: username,
                            email: email || null,
                            role: role
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        this.token = data.access_token;
                        this.currentUser = data.user;
                        localStorage.setItem('auth_token', this.token);
                        this.showAuthenticatedView();
                        alert('Registration successful!');
                    } else {
                        const error = await response.json();
                        alert(`Registration failed: ${error.detail}`);
                    }
                } catch (error) {
                    console.error('Registration error:', error);
                    alert('Registration failed: Network error');
                }
            }

            logout() {
                this.token = null;
                this.currentUser = null;
                localStorage.removeItem('auth_token');
                this.showUnauthenticatedView();
                alert('Logged out successfully!');
            }

            async addFamilyMember() {
                const userId = document.getElementById('new-member-user-id').value;
                const name = document.getElementById('new-member-name').value;
                const ageGroup = document.getElementById('new-member-age').value;
                const languages = Array.from(document.getElementById('new-member-languages').selectedOptions).map(opt => opt.value);

                if (!userId || !name) {
                    alert('Please fill in User ID and Name');
                    return;
                }

                try {
                    const response = await fetch('http://localhost:8000/api/v1/auth/register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${this.token}`
                        },
                        body: JSON.stringify({
                            user_id: userId,
                            username: name,
                            role: ageGroup === 'adult' ? 'parent' : 'child'
                        })
                    });

                    if (response.ok) {
                        alert(`Family member '${name}' added successfully!`);
                        this.refreshFamilyList();
                        this.clearAddMemberForm();
                    } else {
                        const error = await response.json();
                        alert(`Failed to add family member: ${error.detail}`);
                    }
                } catch (error) {
                    console.error('Add member error:', error);
                    alert('Failed to add family member: Network error');
                }
            }

            clearAddMemberForm() {
                ['new-member-user-id', 'new-member-name'].forEach(id => {
                    const element = document.getElementById(id);
                    if (element) element.value = '';
                });
                const ageSelect = document.getElementById('new-member-age');
                if (ageSelect) ageSelect.selectedIndex = 0;
                const langSelect = document.getElementById('new-member-languages');
                if (langSelect) {
                    for (let option of langSelect.options) {
                        option.selected = false;
                    }
                }
            }

            async refreshFamilyList() {
                // In a full implementation, this would fetch and update the family list
                console.log('Refreshing family member list...');
            }

            showAuthenticatedView() {
                document.getElementById('auth-section').style.display = 'none';
                document.getElementById('profile-section').style.display = 'block';

                // Update profile display
                if (this.currentUser) {
                    document.getElementById('profile-username').textContent = this.currentUser.username;
                    document.getElementById('profile-details').innerHTML = `
                        <strong>User ID:</strong> ${this.currentUser.user_id}<br>
                        <strong>Role:</strong> ${this.currentUser.role}<br>
                        <strong>Joined:</strong> ${new Date(Date.now()).toLocaleDateString()}
                    `;

                    // Show family section for parents
                    if (this.currentUser.role === 'parent' || this.currentUser.role === 'admin') {
                        document.getElementById('family-section').style.display = 'block';
                        document.getElementById('parental-controls').style.display = 'block';
                    }
                }
            }

            showUnauthenticatedView() {
                document.getElementById('auth-section').style.display = 'block';
                document.getElementById('profile-section').style.display = 'none';
                document.getElementById('family-section').style.display = 'none';
                document.getElementById('parental-controls').style.display = 'none';

                // Clear form fields
                ['login-user-id', 'login-password', 'reg-user-id', 'reg-username', 'reg-email'].forEach(id => {
                    const element = document.getElementById(id);
                    if (element) element.value = '';
                });
            }
        }

        // Initialize auth manager when page loads
        document.addEventListener('DOMContentLoaded', () => {
            window.authManager = new AuthManager();
        });
    """)
