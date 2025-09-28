"""
Admin Feature Toggles Interface

Provides administrative interface for managing system feature toggles.
Allows admins to enable/disable features dynamically.

Author: AI Assistant
Date: 2025-09-27
"""

from fasthtml.common import *
from typing import Dict, List, Any, Optional
import logging

from ..services.feature_toggle_manager import (
    feature_toggle_manager,
    FeatureToggle,
    FeatureCategory,
    UserRole,
)

logger = logging.getLogger(__name__)


def create_feature_toggle_card(feature: FeatureToggle) -> Div:
    """Create a card component for a single feature toggle"""

    # Category color mapping
    category_colors = {
        "learning": "bg-blue-50 border-blue-200",
        "speech": "bg-green-50 border-green-200",
        "admin": "bg-red-50 border-red-200",
        "access": "bg-yellow-50 border-yellow-200",
        "performance": "bg-purple-50 border-purple-200",
        "general": "bg-gray-50 border-gray-200",
    }

    # Status colors
    status_class = (
        "bg-green-100 text-green-800"
        if feature.is_enabled
        else "bg-red-100 text-red-800"
    )
    status_text = "Enabled" if feature.is_enabled else "Disabled"

    card_class = category_colors.get(feature.category, "bg-gray-50 border-gray-200")

    return Div(
        Div(
            Div(
                Div(
                    H3(
                        feature.feature_name.replace("_", " ").title(),
                        cls="text-lg font-semibold text-gray-900 mb-2",
                    ),
                    Span(
                        status_text,
                        cls=f"inline-flex px-2 py-1 text-xs font-medium rounded-full {status_class}",
                    ),
                    cls="flex justify-between items-start mb-3",
                ),
                P(
                    feature.description or "No description available",
                    cls="text-gray-600 text-sm mb-3",
                ),
                Div(
                    Span(
                        f"Category: {feature.category.title()}",
                        cls="text-xs text-gray-500 mr-4",
                    ),
                    Span(
                        f"Min Role: {feature.min_role}",
                        cls="text-xs text-gray-500 mr-4",
                    ),
                    Span(
                        "Requires Restart"
                        if feature.requires_restart
                        else "No Restart",
                        cls="text-xs text-gray-500",
                    ),
                    cls="mb-4",
                ),
                Div(
                    Button(
                        "Disable" if feature.is_enabled else "Enable",
                        hx_post=f"/dashboard/admin/feature-toggles/toggle/{feature.feature_name}",
                        hx_target="#feature-toggles-container",
                        hx_swap="outerHTML",
                        cls=f"px-4 py-2 text-sm font-medium rounded-lg transition-colors duration-200 mr-2 "
                        + (
                            "bg-red-600 text-white hover:bg-red-700"
                            if feature.is_enabled
                            else "bg-green-600 text-white hover:bg-green-700"
                        ),
                    ),
                    Button(
                        "Configure",
                        onclick=f"openConfigModal('{feature.feature_name}')",
                        cls="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 mr-2",
                    ),
                    Button(
                        "Details",
                        onclick=f"openDetailsModal('{feature.feature_name}')",
                        cls="px-4 py-2 text-sm font-medium bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors duration-200",
                    ),
                    cls="flex flex-wrap gap-2",
                ),
                cls="p-6",
            ),
            cls=f"rounded-lg border-2 {card_class} shadow-sm hover:shadow-md transition-shadow duration-200",
        ),
        cls="feature-toggle-card",
    )


def create_category_section(category: str, features: List[FeatureToggle]) -> Div:
    """Create a section for features in a specific category"""

    # Category icons and descriptions
    category_info = {
        "learning": {"icon": "🎓", "desc": "Core learning and educational features"},
        "speech": {"icon": "🎤", "desc": "Speech recognition and synthesis features"},
        "admin": {"icon": "⚙️", "desc": "Administrative and management features"},
        "access": {"icon": "🔐", "desc": "User access and permission features"},
        "performance": {"icon": "⚡", "desc": "Performance optimization features"},
        "general": {"icon": "📋", "desc": "General system features"},
    }

    info = category_info.get(category, {"icon": "📌", "desc": "System features"})
    enabled_count = sum(1 for f in features if f.is_enabled)
    total_count = len(features)

    return Div(
        Div(
            Div(
                Span(info["icon"], cls="text-2xl mr-3"),
                H2(category.title(), cls="text-xl font-bold text-gray-900"),
                Span(
                    f"{enabled_count}/{total_count} enabled",
                    cls="text-sm text-gray-500 ml-auto",
                ),
                cls="flex items-center mb-2",
            ),
            P(info["desc"], cls="text-gray-600 text-sm mb-4"),
            cls="mb-6",
        ),
        Div(
            *[create_feature_toggle_card(feature) for feature in features],
            cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
        ),
        cls="mb-8",
    )


def create_feature_toggles_page(user_role: str = "ADMIN") -> Div:
    """Create the main feature toggles admin page"""

    try:
        # Get features organized by category
        features_by_category = feature_toggle_manager.get_features_by_category(
            user_role
        )
        statistics = feature_toggle_manager.get_feature_statistics()

        if not features_by_category:
            return Div(
                Div(
                    H1("Feature Toggles", cls="text-2xl font-bold text-gray-900 mb-4"),
                    Div(
                        P(
                            "No features found or database error occurred.",
                            cls="text-center text-gray-500 py-8",
                        ),
                        cls="bg-white rounded-lg shadow p-6",
                    ),
                    cls="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8",
                )
            )

        # Statistics summary
        total_features = statistics.get("total_features", 0)
        enabled_features = statistics.get("enabled_features", 0)
        disabled_features = statistics.get("disabled_features", 0)

        return Div(
            Div(
                # Header section
                Div(
                    H1("Feature Toggles", cls="text-3xl font-bold text-gray-900 mb-2"),
                    P(
                        "Manage system features and capabilities dynamically",
                        cls="text-gray-600 mb-6",
                    ),
                    # Statistics cards
                    Div(
                        Div(
                            Div(
                                Div(
                                    Span("📊", cls="text-2xl"),
                                    Div(
                                        P(
                                            str(total_features),
                                            cls="text-2xl font-bold text-gray-900",
                                        ),
                                        P(
                                            "Total Features",
                                            cls="text-sm text-gray-500",
                                        ),
                                        cls="ml-3",
                                    ),
                                    cls="flex items-center",
                                ),
                                cls="p-4",
                            ),
                            cls="bg-white rounded-lg shadow border-l-4 border-blue-500",
                        ),
                        Div(
                            Div(
                                Div(
                                    Span("✅", cls="text-2xl"),
                                    Div(
                                        P(
                                            str(enabled_features),
                                            cls="text-2xl font-bold text-green-600",
                                        ),
                                        P("Enabled", cls="text-sm text-gray-500"),
                                        cls="ml-3",
                                    ),
                                    cls="flex items-center",
                                ),
                                cls="p-4",
                            ),
                            cls="bg-white rounded-lg shadow border-l-4 border-green-500",
                        ),
                        Div(
                            Div(
                                Div(
                                    Span("❌", cls="text-2xl"),
                                    Div(
                                        P(
                                            str(disabled_features),
                                            cls="text-2xl font-bold text-red-600",
                                        ),
                                        P("Disabled", cls="text-sm text-gray-500"),
                                        cls="ml-3",
                                    ),
                                    cls="flex items-center",
                                ),
                                cls="p-4",
                            ),
                            cls="bg-white rounded-lg shadow border-l-4 border-red-500",
                        ),
                        cls="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8",
                    ),
                    # Action buttons
                    Div(
                        Button(
                            "🔄 Refresh All",
                            hx_get="/dashboard/admin/feature-toggles",
                            hx_target="#feature-toggles-container",
                            hx_swap="outerHTML",
                            cls="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 mr-3",
                        ),
                        Button(
                            "✅ Enable All",
                            hx_post="/dashboard/admin/feature-toggles/bulk-enable",
                            hx_target="#feature-toggles-container",
                            hx_swap="outerHTML",
                            hx_confirm="Are you sure you want to enable ALL features?",
                            cls="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200 mr-3",
                        ),
                        Button(
                            "❌ Disable All",
                            hx_post="/dashboard/admin/feature-toggles/bulk-disable",
                            hx_target="#feature-toggles-container",
                            hx_swap="outerHTML",
                            hx_confirm="Are you sure you want to disable ALL features? This may break the system!",
                            cls="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 mr-3",
                        ),
                        Button(
                            "📊 Export Config",
                            onclick="exportConfiguration()",
                            cls="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors duration-200",
                        ),
                        cls="flex flex-wrap gap-2 mb-8",
                    ),
                    cls="mb-8",
                ),
                # Features organized by category
                *[
                    create_category_section(category, features)
                    for category, features in sorted(features_by_category.items())
                ],
                cls="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8",
            ),
            # Configuration Modal
            create_config_modal(),
            # Details Modal
            create_details_modal(),
            # JavaScript for modal handling
            Script("""
                function openConfigModal(featureName) {
                    // Fetch current configuration and show modal
                    fetch(`/dashboard/admin/feature-toggles/${featureName}/config`)
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('config-feature-name').value = featureName;
                            document.getElementById('config-description').value = data.description || '';
                            document.getElementById('config-category').value = data.category || 'general';
                            document.getElementById('config-min-role').value = data.min_role || 'CHILD';
                            document.getElementById('config-requires-restart').checked = data.requires_restart || false;
                            document.getElementById('config-json').value = JSON.stringify(data.configuration || {}, null, 2);
                            document.getElementById('configModal').style.display = 'flex';
                        });
                }

                function closeConfigModal() {
                    document.getElementById('configModal').style.display = 'none';
                }

                function openDetailsModal(featureName) {
                    // Fetch feature details and show modal
                    fetch(`/dashboard/admin/feature-toggles/${featureName}/details`)
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('details-content').innerHTML = formatFeatureDetails(data);
                            document.getElementById('detailsModal').style.display = 'flex';
                        });
                }

                function closeDetailsModal() {
                    document.getElementById('detailsModal').style.display = 'none';
                }

                function formatFeatureDetails(feature) {
                    return `
                        <div class="space-y-4">
                            <div><strong>Name:</strong> ${feature.feature_name}</div>
                            <div><strong>Status:</strong>
                                <span class="${feature.is_enabled ? 'text-green-600' : 'text-red-600'}">
                                    ${feature.is_enabled ? 'Enabled' : 'Disabled'}
                                </span>
                            </div>
                            <div><strong>Description:</strong> ${feature.description || 'No description'}</div>
                            <div><strong>Category:</strong> ${feature.category}</div>
                            <div><strong>Minimum Role:</strong> ${feature.min_role}</div>
                            <div><strong>Requires Restart:</strong> ${feature.requires_restart ? 'Yes' : 'No'}</div>
                            <div><strong>Created:</strong> ${feature.created_at}</div>
                            <div><strong>Updated:</strong> ${feature.updated_at}</div>
                            <div><strong>Configuration:</strong>
                                <pre class="bg-gray-100 p-2 rounded text-sm mt-1">${JSON.stringify(feature.configuration || {}, null, 2)}</pre>
                            </div>
                        </div>
                    `;
                }

                function exportConfiguration() {
                    fetch('/dashboard/admin/feature-toggles/export')
                        .then(response => response.json())
                        .then(data => {
                            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = 'feature-toggles-config.json';
                            a.click();
                            URL.revokeObjectURL(url);
                        });
                }

                // Close modals when clicking outside
                window.onclick = function(event) {
                    const configModal = document.getElementById('configModal');
                    const detailsModal = document.getElementById('detailsModal');
                    if (event.target === configModal) {
                        configModal.style.display = 'none';
                    }
                    if (event.target === detailsModal) {
                        detailsModal.style.display = 'none';
                    }
                }
            """),
            id="feature-toggles-container",
            cls="min-h-screen bg-gray-50",
        )

    except Exception as e:
        logger.error(f"Error creating feature toggles page: {e}")
        return Div(
            P(
                f"Error loading feature toggles: {e}",
                cls="text-red-600 text-center py-8",
            ),
            id="feature-toggles-container",
        )


def create_config_modal() -> Div:
    """Create modal for configuring features"""
    return Div(
        Div(
            Div(
                Div(
                    H3("Configure Feature", cls="text-lg font-semibold text-gray-900"),
                    Button(
                        "×",
                        onclick="closeConfigModal()",
                        cls="text-gray-400 hover:text-gray-600 text-2xl",
                    ),
                    cls="flex justify-between items-center mb-4",
                ),
                Form(
                    Input(type="hidden", id="config-feature-name", name="feature_name"),
                    Div(
                        Label(
                            "Description:",
                            cls="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        Textarea(
                            id="config-description",
                            name="description",
                            rows="2",
                            cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                        ),
                        cls="mb-4",
                    ),
                    Div(
                        Label(
                            "Category:",
                            cls="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        Select(
                            Option("General", value="general"),
                            Option("Learning", value="learning"),
                            Option("Speech", value="speech"),
                            Option("Admin", value="admin"),
                            Option("Access", value="access"),
                            Option("Performance", value="performance"),
                            id="config-category",
                            name="category",
                            cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                        ),
                        cls="mb-4",
                    ),
                    Div(
                        Label(
                            "Minimum Role:",
                            cls="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        Select(
                            Option("Child", value="CHILD"),
                            Option("Parent", value="PARENT"),
                            Option("Admin", value="ADMIN"),
                            id="config-min-role",
                            name="min_role",
                            cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                        ),
                        cls="mb-4",
                    ),
                    Div(
                        Label(
                            Input(
                                type="checkbox",
                                id="config-requires-restart",
                                name="requires_restart",
                                cls="mr-2",
                            ),
                            "Requires System Restart",
                            cls="flex items-center text-sm font-medium text-gray-700",
                        ),
                        cls="mb-4",
                    ),
                    Div(
                        Label(
                            "Configuration (JSON):",
                            cls="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        Textarea(
                            id="config-json",
                            name="configuration",
                            rows="6",
                            placeholder='{"key": "value"}',
                            cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm",
                        ),
                        cls="mb-6",
                    ),
                    Div(
                        Button(
                            "Cancel",
                            type="button",
                            onclick="closeConfigModal()",
                            cls="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 mr-3",
                        ),
                        Button(
                            "Save Configuration",
                            type="submit",
                            cls="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700",
                        ),
                        cls="flex justify-end",
                    ),
                    hx_post="/dashboard/admin/feature-toggles/configure",
                    hx_target="#feature-toggles-container",
                    hx_swap="outerHTML",
                ),
                cls="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto",
            ),
            cls="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50",
        ),
        id="configModal",
        style="display: none;",
    )


def create_details_modal() -> Div:
    """Create modal for viewing feature details"""
    return Div(
        Div(
            Div(
                Div(
                    H3("Feature Details", cls="text-lg font-semibold text-gray-900"),
                    Button(
                        "×",
                        onclick="closeDetailsModal()",
                        cls="text-gray-400 hover:text-gray-600 text-2xl",
                    ),
                    cls="flex justify-between items-center mb-4",
                ),
                Div(id="details-content", cls="text-sm text-gray-700"),
                Div(
                    Button(
                        "Close",
                        onclick="closeDetailsModal()",
                        cls="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700",
                    ),
                    cls="flex justify-end mt-6",
                ),
                cls="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto",
            ),
            cls="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50",
        ),
        id="detailsModal",
        style="display: none;",
    )
