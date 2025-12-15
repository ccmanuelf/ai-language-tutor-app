"""
Admin Budget Management UI

FastHTML-based admin interface for managing user budgets:
- View all user budget settings
- Configure individual user budgets
- Set budget visibility and permissions
- View budget usage analytics
- Manual budget reset capability
"""

from fasthtml.common import *


def create_budget_overview_card(budget_data: dict) -> Div:
    """Create overview card showing system-wide budget statistics"""

    stats = budget_data.get("stats", {})

    return Div(
        H2("Budget System Overview", style="margin-bottom: 1.5rem;"),
        Div(
            # Total users card
            Div(
                Div(
                    Div(str(stats.get("total_users", 0)), cls="stat-value"),
                    Div("Total Users", cls="stat-label"),
                    cls="stat-card",
                ),
                style="flex: 1;",
            ),
            # Total budget allocated
            Div(
                Div(
                    Div(
                        f"${stats.get('total_budget_allocated', 0):.2f}",
                        cls="stat-value",
                    ),
                    Div("Total Budget Allocated", cls="stat-label"),
                    cls="stat-card",
                ),
                style="flex: 1;",
            ),
            # Total spent this month
            Div(
                Div(
                    Div(f"${stats.get('total_spent', 0):.2f}", cls="stat-value"),
                    Div("Total Spent", cls="stat-label"),
                    cls="stat-card",
                ),
                style="flex: 1;",
            ),
            # Users over budget
            Div(
                Div(
                    Div(
                        str(stats.get("users_over_budget", 0)),
                        cls="stat-value",
                        style="color: var(--danger-color);"
                        if stats.get("users_over_budget", 0) > 0
                        else "",
                    ),
                    Div("Users Over Budget", cls="stat-label"),
                    cls="stat-card",
                ),
                style="flex: 1;",
            ),
            style="display: flex; gap: 1.5rem; margin-bottom: 2rem;",
        ),
        cls="card",
    )


def create_user_budget_row(user_budget: dict) -> Tr:
    """Create table row for a single user's budget"""

    user_id = user_budget.get("user_id", "")
    monthly_limit = user_budget.get("monthly_limit_usd", 30.0)
    used = user_budget.get("current_usage", 0.0)
    percentage = (used / monthly_limit * 100) if monthly_limit > 0 else 0

    # Determine status badge
    if percentage >= 100:
        status_badge = Span("OVER BUDGET", cls="badge badge-danger")
    elif percentage >= 90:
        status_badge = Span("CRITICAL", cls="badge badge-warning")
    elif percentage >= 75:
        status_badge = Span("HIGH", cls="badge badge-orange")
    elif percentage >= 50:
        status_badge = Span("MODERATE", cls="badge badge-yellow")
    else:
        status_badge = Span("OK", cls="badge badge-success")

    # Permission indicators
    permissions = []
    if user_budget.get("budget_visible_to_user", True):
        permissions.append("👁️ Visible")
    if user_budget.get("user_can_modify_limit", False):
        permissions.append("✏️ Can Modify")
    if user_budget.get("user_can_reset_budget", False):
        permissions.append("🔄 Can Reset")

    return Tr(
        Td(user_id),
        Td(f"${monthly_limit:.2f}"),
        Td(f"${used:.2f}"),
        Td(
            Div(
                Div(
                    style=f"width: {min(percentage, 100)}%; height: 100%; background: {'var(--danger-color)' if percentage >= 90 else 'var(--warning-color)' if percentage >= 75 else 'var(--success-color)'}; border-radius: var(--radius);"
                ),
                style="width: 100px; height: 20px; background: var(--bg-tertiary); border-radius: var(--radius); position: relative;",
            ),
            f" {percentage:.1f}%",
        ),
        Td(status_badge),
        Td(" | ".join(permissions) if permissions else "None"),
        Td(
            Button(
                "Configure",
                onclick=f"openBudgetConfigModal('{user_id}')",
                cls="btn btn-sm btn-primary",
                style="margin-right: 0.5rem;",
            ),
            Button(
                "Reset",
                onclick=f"resetUserBudget('{user_id}')",
                cls="btn btn-sm btn-secondary",
            ),
        ),
    )


def create_user_budget_list(users_budget: list) -> Div:
    """Create list of all users with their budget settings"""

    return Div(
        H2("User Budget Management", style="margin-bottom: 1.5rem;"),
        Div(
            Input(
                type="text",
                id="userSearch",
                placeholder="Search users...",
                oninput="filterUserBudgets()",
                style="padding: 0.75rem; border: 1px solid var(--border-color); border-radius: var(--radius); width: 100%; margin-bottom: 1rem;",
            )
        ),
        Table(
            Thead(
                Tr(
                    Th("User ID"),
                    Th("Monthly Limit"),
                    Th("Current Usage"),
                    Th("Usage"),
                    Th("Status"),
                    Th("Permissions"),
                    Th("Actions"),
                )
            ),
            Tbody(
                *[create_user_budget_row(user) for user in users_budget],
                id="userBudgetTable",
            ),
            cls="data-table",
            style="width: 100%;",
        ),
        cls="card",
    )


def create_budget_config_modal() -> Div:
    """Create modal for configuring individual user budgets"""

    return Div(
        Div(
            Div(
                H2("Configure User Budget", style="margin-bottom: 1.5rem;"),
                Form(
                    # User ID (read-only)
                    Div(
                        Label("User ID", For="configUserId"),
                        Input(
                            type="text",
                            id="configUserId",
                            readonly=True,
                            style="padding: 0.75rem; border: 1px solid var(--border-color); border-radius: var(--radius); width: 100%; background: var(--bg-tertiary);",
                        ),
                        style="margin-bottom: 1rem;",
                    ),
                    # Monthly limit
                    Div(
                        Label("Monthly Budget Limit (USD)", For="configMonthlyLimit"),
                        Input(
                            type="number",
                            id="configMonthlyLimit",
                            min="0",
                            max="10000",
                            step="1",
                            value="30",
                            style="padding: 0.75rem; border: 1px solid var(--border-color); border-radius: var(--radius); width: 100%;",
                        ),
                        style="margin-bottom: 1rem;",
                    ),
                    # Budget visibility
                    Div(
                        Label(
                            Input(
                                type="checkbox",
                                id="configVisible",
                                checked=True,
                                style="margin-right: 0.5rem;",
                            ),
                            "Budget Visible to User",
                            style="display: flex; align-items: center;",
                        ),
                        P(
                            "If disabled, user cannot see their budget information",
                            style="margin: 0.5rem 0 0 1.75rem; font-size: 0.875rem; color: var(--text-secondary);",
                        ),
                        style="margin-bottom: 1rem;",
                    ),
                    # Can modify limit
                    Div(
                        Label(
                            Input(
                                type="checkbox",
                                id="configCanModify",
                                style="margin-right: 0.5rem;",
                            ),
                            "User Can Modify Limit",
                            style="display: flex; align-items: center;",
                        ),
                        P(
                            "Allow user to change their own budget limit",
                            style="margin: 0.5rem 0 0 1.75rem; font-size: 0.875rem; color: var(--text-secondary);",
                        ),
                        style="margin-bottom: 1rem;",
                    ),
                    # Can reset budget
                    Div(
                        Label(
                            Input(
                                type="checkbox",
                                id="configCanReset",
                                style="margin-right: 0.5rem;",
                            ),
                            "User Can Reset Budget",
                            style="display: flex; align-items: center;",
                        ),
                        P(
                            "Allow user to manually reset their budget period",
                            style="margin: 0.5rem 0 0 1.75rem; font-size: 0.875rem; color: var(--text-secondary);",
                        ),
                        style="margin-bottom: 1rem;",
                    ),
                    # Admin notes
                    Div(
                        Label("Admin Notes (optional)", For="configNotes"),
                        Textarea(
                            id="configNotes",
                            rows="3",
                            placeholder="Add notes about this configuration...",
                            style="padding: 0.75rem; border: 1px solid var(--border-color); border-radius: var(--radius); width: 100%; resize: vertical;",
                        ),
                        style="margin-bottom: 1.5rem;",
                    ),
                    # Action buttons
                    Div(
                        Button(
                            "Cancel",
                            type="button",
                            onclick="closeBudgetConfigModal()",
                            cls="btn btn-secondary",
                            style="margin-right: 1rem;",
                        ),
                        Button(
                            "Save Configuration",
                            type="button",
                            onclick="saveBudgetConfig()",
                            cls="btn btn-primary",
                        ),
                        style="display: flex; justify-content: flex-end;",
                    ),
                    id="budgetConfigForm",
                ),
                style="background: var(--bg-primary); padding: 2rem; border-radius: var(--radius); max-width: 600px; width: 100%; max-height: 90vh; overflow-y: auto;",
            ),
            style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); display: none; justify-content: center; align-items: center; z-index: 1000;",
            id="budgetConfigModal",
            onclick="event.target.id === 'budgetConfigModal' && closeBudgetConfigModal()",
        )
    )


def create_budget_scripts() -> Script:
    """Create JavaScript for budget management functionality"""

    return Script("""
        // Filter user budgets
        function filterUserBudgets() {
            const search = document.getElementById('userSearch').value.toLowerCase();
            const table = document.getElementById('userBudgetTable');
            const rows = table.getElementsByTagName('tr');

            for (let row of rows) {
                const userId = row.cells[0]?.textContent.toLowerCase() || '';
                row.style.display = userId.includes(search) ? '' : 'none';
            }
        }

        // Open budget configuration modal
        function openBudgetConfigModal(userId) {
            // Fetch current budget settings for user
            fetch(`/api/v1/budget/admin/users`)
                .then(response => response.json())
                .then(users => {
                    const user = users.find(u => u.user_id === userId);
                    if (user) {
                        document.getElementById('configUserId').value = userId;
                        document.getElementById('configMonthlyLimit').value = user.monthly_limit_usd;
                        document.getElementById('configVisible').checked = user.budget_visible_to_user;
                        document.getElementById('configCanModify').checked = user.user_can_modify_limit;
                        document.getElementById('configCanReset').checked = user.user_can_reset_budget;
                        document.getElementById('configNotes').value = user.admin_notes || '';

                        document.getElementById('budgetConfigModal').style.display = 'flex';
                    }
                })
                .catch(error => {
                    console.error('Error fetching budget settings:', error);
                    alert('Failed to load budget settings');
                });
        }

        // Close budget configuration modal
        function closeBudgetConfigModal() {
            document.getElementById('budgetConfigModal').style.display = 'none';
        }

        // Save budget configuration
        async function saveBudgetConfig() {
            const userId = document.getElementById('configUserId').value;
            const data = {
                target_user_id: userId,
                monthly_limit_usd: parseFloat(document.getElementById('configMonthlyLimit').value),
                budget_visible_to_user: document.getElementById('configVisible').checked,
                user_can_modify_limit: document.getElementById('configCanModify').checked,
                user_can_reset_budget: document.getElementById('configCanReset').checked,
                admin_notes: document.getElementById('configNotes').value || null
            };

            try {
                const response = await fetch('/api/v1/budget/admin/configure', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    alert('Budget configuration saved successfully!');
                    closeBudgetConfigModal();
                    location.reload(); // Refresh to show updated data
                } else {
                    const error = await response.json();
                    alert(`Failed to save: ${error.detail || 'Unknown error'}`);
                }
            } catch (error) {
                console.error('Error saving budget config:', error);
                alert('Failed to save budget configuration');
            }
        }

        // Reset user budget
        async function resetUserBudget(userId) {
            const reason = prompt('Enter reason for budget reset (optional):');
            if (reason === null) return; // User cancelled

            const confirmed = confirm(`Reset budget for user ${userId}?\\nThis will start a new budget period immediately.`);
            if (!confirmed) return;

            try {
                const response = await fetch(`/api/v1/budget/admin/reset/${userId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ reason: reason || 'Admin reset' })
                });

                if (response.ok) {
                    const result = await response.json();
                    alert(`Budget reset successful!\\nPrevious spent: $${result.previous_spent.toFixed(2)}`);
                    location.reload();
                } else {
                    const error = await response.json();
                    alert(`Failed to reset: ${error.detail || 'Unknown error'}`);
                }
            } catch (error) {
                console.error('Error resetting budget:', error);
                alert('Failed to reset budget');
            }
        }
    """)


def create_admin_budget_page() -> Div:
    """Create complete admin budget management page"""

    # Demo data - in real implementation, fetch from API
    budget_data = {
        "stats": {
            "total_users": 9,
            "total_budget_allocated": 310.0,  # 2 admins @ $100 + 7 users @ $30
            "total_spent": 45.67,
            "users_over_budget": 0,
        }
    }

    users_budget = [
        {
            "user_id": "admin_1758913874",
            "monthly_limit_usd": 100.0,
            "current_usage": 15.23,
            "budget_visible_to_user": True,
            "user_can_modify_limit": True,
            "user_can_reset_budget": True,
        },
        {
            "user_id": "user_001",
            "monthly_limit_usd": 30.0,
            "current_usage": 8.45,
            "budget_visible_to_user": True,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
        },
        # Add more users as needed
    ]

    return Div(
        H1("Budget Management", style="margin-bottom: 2rem;"),
        # Overview cards
        create_budget_overview_card(budget_data),
        # User budget list
        create_user_budget_list(users_budget),
        # Configuration modal
        create_budget_config_modal(),
        # Scripts
        create_budget_scripts(),
        style="padding: 2rem;",
    )
