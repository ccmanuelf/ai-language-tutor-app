"""
User Budget Dashboard - Frontend Component
AI Language Tutor App - Personal Family Educational Tool

This module provides the user-facing budget dashboard UI component.
Users can view their budget status, usage history, and modify settings
based on permissions granted by admins.
"""

from datetime import datetime
from typing import Dict, List, Optional

from fasthtml.common import *


def create_budget_status_card(budget_data: Dict) -> Div:
    """
    Create budget status overview card

    Args:
        budget_data: Dictionary containing:
            - monthly_limit: Monthly budget limit in USD
            - current_spent: Amount spent in current period
            - period_start: Period start date
            - period_end: Period end date
            - alert_level: Current alert level (green/yellow/orange/red)
            - percentage_used: Percentage of budget used
    """
    monthly_limit = budget_data.get("monthly_limit", 30.0)
    current_spent = budget_data.get("current_spent", 0.0)
    period_start = budget_data.get("period_start", "")
    period_end = budget_data.get("period_end", "")
    alert_level = budget_data.get("alert_level", "green")
    percentage_used = budget_data.get("percentage_used", 0.0)
    remaining = monthly_limit - current_spent

    # Determine status badge and colors
    if alert_level == "red" or percentage_used >= 100:
        status_color = "bg-red-100 text-red-800 border-red-300"
        status_text = "⚠️ OVER BUDGET"
        progress_color = "bg-red-500"
    elif alert_level == "orange" or percentage_used >= 90:
        status_color = "bg-orange-100 text-orange-800 border-orange-300"
        status_text = "⚠️ CRITICAL"
        progress_color = "bg-orange-500"
    elif alert_level == "yellow" or percentage_used >= 75:
        status_color = "bg-yellow-100 text-yellow-800 border-yellow-300"
        status_text = "⚡ WARNING"
        progress_color = "bg-yellow-500"
    else:
        status_color = "bg-green-100 text-green-800 border-green-300"
        status_text = "✅ HEALTHY"
        progress_color = "bg-green-500"

    return Div(
        # Card Header
        Div(
            H2("💰 My Budget Status", cls="text-2xl font-bold text-white mb-2"),
            Div(
                Span(
                    status_text,
                    cls=f"px-3 py-1 rounded-full text-sm font-semibold {status_color}",
                ),
                cls="mb-4",
            ),
            cls="mb-6",
        ),
        # Budget Overview Stats
        Div(
            # Spent vs Limit
            Div(
                Div(
                    Span("💸 Spent", cls="text-gray-300 text-sm"),
                    Span(
                        f"${current_spent:.2f}",
                        cls="text-3xl font-bold text-white block mt-1",
                    ),
                    cls="p-4 bg-gray-800 rounded-lg",
                ),
                cls="col-span-1",
            ),
            Div(
                Div(
                    Span("🎯 Budget Limit", cls="text-gray-300 text-sm"),
                    Span(
                        f"${monthly_limit:.2f}",
                        cls="text-3xl font-bold text-white block mt-1",
                    ),
                    cls="p-4 bg-gray-800 rounded-lg",
                ),
                cls="col-span-1",
            ),
            Div(
                Div(
                    Span("💵 Remaining", cls="text-gray-300 text-sm"),
                    Span(
                        f"${remaining:.2f}",
                        cls=f"text-3xl font-bold block mt-1 {'text-green-400' if remaining > 0 else 'text-red-400'}",
                    ),
                    cls="p-4 bg-gray-800 rounded-lg",
                ),
                cls="col-span-1",
            ),
            cls="grid grid-cols-3 gap-4 mb-6",
        ),
        # Progress Bar
        Div(
            Div(
                Span(
                    f"Budget Usage: {percentage_used:.1f}%",
                    cls="text-sm text-gray-300 mb-2 block",
                ),
                Div(
                    Div(
                        style=f"width: {min(percentage_used, 100)}%",
                        cls=f"h-full {progress_color} rounded-full transition-all duration-300",
                    ),
                    cls="w-full bg-gray-700 rounded-full h-4 overflow-hidden",
                ),
                cls="mb-4",
            ),
        ),
        # Budget Period
        Div(
            Div(
                Span("📅 Current Period", cls="text-gray-300 text-sm"),
                Span(
                    f"{period_start} → {period_end}",
                    cls="text-white text-sm block mt-1",
                ),
                cls="p-3 bg-gray-800 rounded-lg",
            ),
        ),
        cls="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg shadow-lg p-6 border border-gray-700 mb-6",
    )


def create_budget_settings_card(
    settings: Dict, can_modify_limit: bool, can_reset_budget: bool
) -> Div:
    """
    Create budget settings configuration card

    Args:
        settings: Current budget settings
        can_modify_limit: Whether user can modify their budget limit
        can_reset_budget: Whether user can reset their budget
    """
    monthly_limit = settings.get("monthly_limit_usd", 30.0)
    enforce_budget = settings.get("enforce_budget", True)
    alert_threshold_yellow = settings.get("alert_threshold_yellow", 75.0)
    alert_threshold_orange = settings.get("alert_threshold_orange", 90.0)
    alert_threshold_red = settings.get("alert_threshold_red", 100.0)

    return Div(
        H2("⚙️ Budget Settings", cls="text-2xl font-bold text-white mb-6"),
        # Budget Limit Setting
        Div(
            Label("Monthly Budget Limit (USD)", cls="text-gray-300 text-sm mb-2 block"),
            Div(
                Input(
                    type="number",
                    id="monthlyLimitInput",
                    value=f"{monthly_limit:.2f}",
                    min="0",
                    step="0.01",
                    disabled=not can_modify_limit,
                    cls="bg-gray-700 text-white border border-gray-600 rounded-lg px-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-purple-500"
                    + (
                        " opacity-50 cursor-not-allowed" if not can_modify_limit else ""
                    ),
                ),
                Span(
                    "🔒 Contact admin to modify"
                    if not can_modify_limit
                    else "✏️ You can modify this",
                    cls=f"text-xs block mt-1 {'text-gray-400' if not can_modify_limit else 'text-green-400'}",
                ),
                cls="mb-4",
            ),
        ),
        # Budget Enforcement Toggle
        Div(
            Label("Enforce Budget Limit", cls="text-gray-300 text-sm mb-2 block"),
            Div(
                Input(
                    type="checkbox",
                    id="enforceBudgetCheckbox",
                    checked=enforce_budget,
                    disabled=not can_modify_limit,
                    cls="mr-2"
                    + (
                        " opacity-50 cursor-not-allowed" if not can_modify_limit else ""
                    ),
                ),
                Span(
                    "Block API calls when budget is exceeded",
                    cls="text-gray-300 text-sm",
                ),
                cls="flex items-center mb-4",
            ),
        ),
        # Alert Thresholds
        Div(
            Label("Alert Thresholds (%)", cls="text-gray-300 text-sm mb-2 block"),
            Div(
                Div(
                    Span("⚡ Yellow Alert", cls="text-yellow-400 text-xs"),
                    Input(
                        type="number",
                        id="alertYellowInput",
                        value=f"{alert_threshold_yellow:.0f}",
                        min="0",
                        max="100",
                        disabled=not can_modify_limit,
                        cls="bg-gray-700 text-white border border-gray-600 rounded px-2 py-1 w-20 text-sm"
                        + (
                            " opacity-50 cursor-not-allowed"
                            if not can_modify_limit
                            else ""
                        ),
                    ),
                    cls="flex items-center justify-between mb-2",
                ),
                Div(
                    Span("🔶 Orange Alert", cls="text-orange-400 text-xs"),
                    Input(
                        type="number",
                        id="alertOrangeInput",
                        value=f"{alert_threshold_orange:.0f}",
                        min="0",
                        max="100",
                        disabled=not can_modify_limit,
                        cls="bg-gray-700 text-white border border-gray-600 rounded px-2 py-1 w-20 text-sm"
                        + (
                            " opacity-50 cursor-not-allowed"
                            if not can_modify_limit
                            else ""
                        ),
                    ),
                    cls="flex items-center justify-between mb-2",
                ),
                Div(
                    Span("🔴 Red Alert", cls="text-red-400 text-xs"),
                    Input(
                        type="number",
                        id="alertRedInput",
                        value=f"{alert_threshold_red:.0f}",
                        min="0",
                        max="100",
                        disabled=not can_modify_limit,
                        cls="bg-gray-700 text-white border border-gray-600 rounded px-2 py-1 w-20 text-sm"
                        + (
                            " opacity-50 cursor-not-allowed"
                            if not can_modify_limit
                            else ""
                        ),
                    ),
                    cls="flex items-center justify-between",
                ),
                cls="p-3 bg-gray-800 rounded-lg mb-4",
            ),
        ),
        # Action Buttons
        Div(
            Button(
                "💾 Save Settings",
                onclick="saveBudgetSettings()",
                disabled=not can_modify_limit,
                cls="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded-lg mr-2 transition-colors"
                + (" opacity-50 cursor-not-allowed" if not can_modify_limit else ""),
            ),
            Button(
                "🔄 Reset Budget",
                onclick="resetBudget()",
                disabled=not can_reset_budget,
                cls="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                + (" opacity-50 cursor-not-allowed" if not can_reset_budget else ""),
            ),
            cls="flex gap-2",
        ),
        cls="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg shadow-lg p-6 border border-gray-700 mb-6",
    )


def create_usage_history_table(usage_history: List[Dict]) -> Div:
    """
    Create usage history table showing recent API calls

    Args:
        usage_history: List of usage records with:
            - timestamp: When the call was made
            - provider: AI provider used
            - model: Model name
            - cost: Estimated cost in USD
            - tokens: Token count
    """
    if not usage_history:
        return Div(
            H2("📊 Usage History", cls="text-2xl font-bold text-white mb-6"),
            Div(
                P(
                    "No usage history available yet.",
                    cls="text-gray-400 text-center py-8",
                ),
                cls="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg shadow-lg p-6 border border-gray-700",
            ),
        )

    # Create table rows
    rows = []
    for record in usage_history:
        timestamp = record.get("timestamp", "")
        provider = record.get("provider", "Unknown")
        model = record.get("model", "Unknown")
        cost = record.get("cost", 0.0)
        tokens = record.get("tokens", 0)

        rows.append(
            Tr(
                Td(timestamp, cls="px-4 py-3 text-gray-300 text-sm"),
                Td(
                    Span(
                        provider,
                        cls="px-2 py-1 bg-purple-600 text-white text-xs rounded",
                    ),
                    cls="px-4 py-3",
                ),
                Td(model, cls="px-4 py-3 text-gray-300 text-sm"),
                Td(f"{tokens:,}", cls="px-4 py-3 text-gray-300 text-sm text-right"),
                Td(
                    f"${cost:.4f}",
                    cls="px-4 py-3 text-green-400 text-sm text-right font-semibold",
                ),
                cls="border-b border-gray-700 hover:bg-gray-800 transition-colors",
            )
        )

    return Div(
        H2("📊 Recent Usage History", cls="text-2xl font-bold text-white mb-6"),
        Div(
            Div(
                Table(
                    Thead(
                        Tr(
                            Th(
                                "Timestamp",
                                cls="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase",
                            ),
                            Th(
                                "Provider",
                                cls="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase",
                            ),
                            Th(
                                "Model",
                                cls="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase",
                            ),
                            Th(
                                "Tokens",
                                cls="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase",
                            ),
                            Th(
                                "Cost",
                                cls="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase",
                            ),
                            cls="border-b-2 border-gray-600",
                        )
                    ),
                    Tbody(*rows),
                    cls="w-full",
                ),
                cls="overflow-x-auto",
            ),
            cls="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg shadow-lg p-6 border border-gray-700",
        ),
    )


def create_budget_breakdown_chart(breakdown: Dict) -> Div:
    """
    Create budget breakdown by provider/category

    Args:
        breakdown: Dictionary with provider/category breakdowns
            - by_provider: Dict of provider -> cost
            - by_model: Dict of model -> cost
    """
    by_provider = breakdown.get("by_provider", {})
    by_model = breakdown.get("by_model", {})

    if not by_provider and not by_model:
        return Div()  # Empty if no data

    # Create provider breakdown rows
    provider_rows = []
    total_provider_cost = sum(by_provider.values())

    for provider, cost in sorted(by_provider.items(), key=lambda x: x[1], reverse=True):
        percentage = (
            (cost / total_provider_cost * 100) if total_provider_cost > 0 else 0
        )
        provider_rows.append(
            Div(
                Div(
                    Span(provider, cls="text-gray-300 text-sm font-medium"),
                    Span(f"${cost:.3f}", cls="text-green-400 text-sm font-semibold"),
                    cls="flex justify-between mb-1",
                ),
                Div(
                    Div(
                        style=f"width: {percentage}%",
                        cls="h-2 bg-purple-600 rounded-full",
                    ),
                    cls="w-full bg-gray-700 rounded-full h-2 overflow-hidden",
                ),
                cls="mb-3",
            )
        )

    return Div(
        H2("📈 Spending Breakdown", cls="text-2xl font-bold text-white mb-6"),
        Div(
            Div(
                H3("By Provider", cls="text-lg font-semibold text-white mb-4"),
                *provider_rows
                if provider_rows
                else [P("No data available", cls="text-gray-400 text-sm")],
                cls="mb-6",
            ),
            cls="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg shadow-lg p-6 border border-gray-700",
        ),
    )


def create_budget_javascript() -> Script:
    """JavaScript for budget dashboard interactivity"""
    return Script("""
        // Save budget settings
        async function saveBudgetSettings() {
            const monthlyLimit = parseFloat(document.getElementById('monthlyLimitInput').value);
            const enforceBudget = document.getElementById('enforceBudgetCheckbox').checked;
            const alertYellow = parseFloat(document.getElementById('alertYellowInput').value);
            const alertOrange = parseFloat(document.getElementById('alertOrangeInput').value);
            const alertRed = parseFloat(document.getElementById('alertRedInput').value);

            // Validate thresholds
            if (alertYellow >= alertOrange || alertOrange >= alertRed) {
                alert('Alert thresholds must be in ascending order: Yellow < Orange < Red');
                return;
            }

            const data = {
                monthly_limit_usd: monthlyLimit,
                enforce_budget: enforceBudget,
                alert_threshold_yellow: alertYellow,
                alert_threshold_orange: alertOrange,
                alert_threshold_red: alertRed
            };

            try {
                const response = await fetch('/api/v1/budget/settings', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    alert('✅ Budget settings saved successfully!');
                    location.reload();  // Reload to show updated data
                } else {
                    const error = await response.json();
                    alert('❌ Error saving settings: ' + (error.detail || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error saving budget settings:', error);
                alert('❌ Failed to save settings. Please try again.');
            }
        }

        // Reset budget
        async function resetBudget() {
            if (!confirm('Are you sure you want to reset your budget? This will clear your current usage and start a new period.')) {
                return;
            }

            try {
                const response = await fetch('/api/v1/budget/reset', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                if (response.ok) {
                    alert('✅ Budget reset successfully!');
                    location.reload();  // Reload to show updated data
                } else {
                    const error = await response.json();
                    alert('❌ Error resetting budget: ' + (error.detail || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error resetting budget:', error);
                alert('❌ Failed to reset budget. Please try again.');
            }
        }

        // Auto-refresh budget status every 30 seconds
        setInterval(() => {
            // Only reload if user hasn't modified inputs
            const inputs = document.querySelectorAll('input');
            let anyFocused = false;
            inputs.forEach(input => {
                if (document.activeElement === input) {
                    anyFocused = true;
                }
            });

            if (!anyFocused) {
                location.reload();
            }
        }, 30000);
    """)


def create_user_budget_page(
    budget_status: Dict,
    budget_settings: Dict,
    usage_history: List[Dict],
    breakdown: Dict,
    can_modify_limit: bool = False,
    can_reset_budget: bool = False,
) -> Div:
    """
    Create complete user budget dashboard page

    Args:
        budget_status: Current budget status data
        budget_settings: User's budget settings
        usage_history: List of recent usage records
        breakdown: Spending breakdown by provider/model
        can_modify_limit: Whether user can modify their budget limit
        can_reset_budget: Whether user can reset their budget
    """
    return Div(
        # Page Header
        Div(
            H1("💰 My Budget Dashboard", cls="text-3xl font-bold text-white mb-2"),
            P(
                "Monitor your AI API usage and manage your budget settings",
                cls="text-gray-300",
            ),
            cls="mb-8",
        ),
        # Budget Status Card
        create_budget_status_card(budget_status),
        # Two Column Layout
        Div(
            # Left Column - Settings
            Div(
                create_budget_settings_card(
                    budget_settings, can_modify_limit, can_reset_budget
                ),
                cls="lg:col-span-1",
            ),
            # Right Column - Breakdown
            Div(
                create_budget_breakdown_chart(breakdown),
                cls="lg:col-span-1",
            ),
            cls="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6",
        ),
        # Usage History Table
        create_usage_history_table(usage_history),
        # JavaScript
        create_budget_javascript(),
        cls="container mx-auto px-4 py-8",
    )
