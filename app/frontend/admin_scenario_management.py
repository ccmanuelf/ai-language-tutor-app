"""
Admin Scenario & Content Management Interface
AI Language Tutor App - Admin Configuration System

This module provides FastHTML components for managing scenarios and content
processing configuration through the admin dashboard.

Features:
- Scenario listing and filtering interface
- Scenario creation and editing forms
- Content processing configuration panel
- Bulk operations interface
- Statistics and analytics display
"""

from fasthtml.common import *
from typing import Dict, List, Any, Optional
import json
from datetime import datetime


def scenario_management_styles():
    """CSS styles for scenario management interface"""
    return Style("""
        .scenario-management-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .scenario-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            color: white;
        }

        .scenario-header h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 600;
        }

        .scenario-tabs {
            display: flex;
            border-bottom: 2px solid #e2e8f0;
            margin-bottom: 30px;
            background: white;
            border-radius: 8px 8px 0 0;
            overflow: hidden;
        }

        .scenario-tab {
            padding: 15px 25px;
            cursor: pointer;
            border: none;
            background: #f8fafc;
            color: #64748b;
            font-weight: 500;
            transition: all 0.3s ease;
            flex: 1;
            text-align: center;
        }

        .scenario-tab.active {
            background: #667eea;
            color: white;
        }

        .scenario-tab:hover:not(.active) {
            background: #e2e8f0;
        }

        .scenario-filters {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            padding: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            align-items: center;
            flex-wrap: wrap;
        }

        .scenario-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .scenario-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border: 1px solid #e2e8f0;
        }

        .scenario-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }

        .scenario-card-header {
            display: flex;
            justify-content: between;
            align-items: start;
            margin-bottom: 15px;
        }

        .scenario-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1e293b;
            margin: 0 0 5px 0;
        }

        .scenario-badges {
            display: flex;
            gap: 8px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }

        .scenario-badge {
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
        }

        .badge-category { background: #ddd6fe; color: #7c3aed; }
        .badge-difficulty { background: #fef3c7; color: #d97706; }
        .badge-duration { background: #d1fae5; color: #059669; }
        .badge-active { background: #dcfce7; color: #16a34a; }
        .badge-inactive { background: #fee2e2; color: #dc2626; }

        .scenario-description {
            color: #64748b;
            margin-bottom: 15px;
            line-height: 1.5;
        }

        .scenario-actions {
            display: flex;
            gap: 8px;
            justify-content: flex-end;
        }

        .btn-scenario {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-primary { background: #3b82f6; color: white; }
        .btn-primary:hover { background: #2563eb; }
        .btn-secondary { background: #6b7280; color: white; }
        .btn-secondary:hover { background: #4b5563; }
        .btn-success { background: #10b981; color: white; }
        .btn-success:hover { background: #059669; }
        .btn-danger { background: #ef4444; color: white; }
        .btn-danger:hover { background: #dc2626; }

        .scenario-form {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 800px;
            margin: 0 auto;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-label {
            display: block;
            font-weight: 600;
            color: #374151;
            margin-bottom: 6px;
        }

        .form-control {
            width: 100%;
            padding: 12px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.2s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .form-control-small {
            width: auto;
            min-width: 120px;
        }

        .phase-section {
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            background: #f9fafb;
        }

        .phase-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .config-panel {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .config-section {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e5e7eb;
        }

        .config-section:last-child {
            border-bottom: none;
            margin-bottom: 0;
        }

        .config-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 15px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 8px;
        }

        .stat-label {
            color: #64748b;
            font-weight: 500;
        }

        .bulk-actions {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .bulk-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .checkbox-scenario {
            position: absolute;
            top: 15px;
            right: 15px;
            width: 20px;
            height: 20px;
            cursor: pointer;
        }

        .error-message {
            background: #fee2e2;
            color: #dc2626;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #fecaca;
        }

        .success-message {
            background: #dcfce7;
            color: #16a34a;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #bbf7d0;
        }

        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }

        .modal-content {
            background: white;
            border-radius: 12px;
            padding: 30px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }

        @media (max-width: 768px) {
            .scenario-grid {
                grid-template-columns: 1fr;
            }

            .scenario-filters {
                flex-direction: column;
                align-items: stretch;
            }

            .scenario-header {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }

            .scenario-tabs {
                flex-direction: column;
            }
        }
    """)


def create_scenario_management_page():
    """Create the main scenario management interface"""
    return Div(
        scenario_management_styles(),
        Div(
            # Header
            Div(
                H1("Scenario & Content Management"),
                Div(
                    Button(
                        "+ New Scenario",
                        cls="btn-scenario btn-primary",
                        onclick="showCreateScenario()",
                    ),
                    Button(
                        "Import",
                        cls="btn-scenario btn-secondary",
                        onclick="importScenarios()",
                    ),
                    Button(
                        "Export",
                        cls="btn-scenario btn-secondary",
                        onclick="exportScenarios()",
                    ),
                    style="display: flex; gap: 10px;",
                ),
                cls="scenario-header",
            ),
            # Tabs
            Div(
                Button(
                    "Scenarios",
                    cls="scenario-tab active",
                    onclick="showTab('scenarios')",
                ),
                Button(
                    "Content Config",
                    cls="scenario-tab",
                    onclick="showTab('content-config')",
                ),
                Button(
                    "Statistics", cls="scenario-tab", onclick="showTab('statistics')"
                ),
                cls="scenario-tabs",
            ),
            # Scenarios Tab Content
            Div(
                # Filters
                Div(
                    Select(
                        Option("All Categories", value=""),
                        Option("Restaurant", value="restaurant"),
                        Option("Travel", value="travel"),
                        Option("Shopping", value="shopping"),
                        Option("Business", value="business"),
                        Option("Social", value="social"),
                        name="category_filter",
                        cls="form-control form-control-small",
                        onchange="filterScenarios()",
                    ),
                    Select(
                        Option("All Difficulties", value=""),
                        Option("Beginner", value="beginner"),
                        Option("Intermediate", value="intermediate"),
                        Option("Advanced", value="advanced"),
                        name="difficulty_filter",
                        cls="form-control form-control-small",
                        onchange="filterScenarios()",
                    ),
                    Select(
                        Option("All Statuses", value=""),
                        Option("Active Only", value="active"),
                        Option("Inactive Only", value="inactive"),
                        name="status_filter",
                        cls="form-control form-control-small",
                        onchange="filterScenarios()",
                    ),
                    Input(
                        type="search",
                        placeholder="Search scenarios...",
                        name="search_filter",
                        cls="form-control",
                        oninput="filterScenarios()",
                        style="flex: 1;",
                    ),
                    cls="scenario-filters",
                ),
                # Bulk Actions
                Div(
                    Div(
                        H3("Bulk Actions", style="margin: 0; font-size: 1.1rem;"),
                        Span(
                            "0 selected", id="selected-count", style="color: #64748b;"
                        ),
                        cls="bulk-header",
                    ),
                    Div(
                        Button(
                            "Activate",
                            cls="btn-scenario btn-success",
                            onclick="bulkOperation('activate')",
                        ),
                        Button(
                            "Deactivate",
                            cls="btn-scenario btn-secondary",
                            onclick="bulkOperation('deactivate')",
                        ),
                        Button(
                            "Delete",
                            cls="btn-scenario btn-danger",
                            onclick="bulkOperation('delete')",
                        ),
                        style="display: flex; gap: 10px;",
                    ),
                    cls="bulk-actions",
                    id="bulk-actions",
                    style="display: none;",
                ),
                # Scenario Grid
                Div(id="scenario-grid", cls="scenario-grid"),
                id="scenarios-content",
            ),
            # Content Config Tab Content
            Div(
                create_content_config_panel(),
                id="content-config-content",
                style="display: none;",
            ),
            # Statistics Tab Content
            Div(
                create_statistics_panel(),
                id="statistics-content",
                style="display: none;",
            ),
            cls="scenario-management-container",
        ),
        # Modals
        create_scenario_modals(),
        # JavaScript
        scenario_management_javascript(),
    )


def create_scenario_card(scenario_data):
    """Create a scenario card component"""
    return Div(
        Input(
            type="checkbox",
            cls="checkbox-scenario",
            value=scenario_data.get("scenario_id", ""),
            onchange="updateSelection()",
        ),
        Div(
            H3(scenario_data.get("name", "Untitled"), cls="scenario-title"),
            Div(
                Span(
                    scenario_data.get("category", "").title(),
                    cls="scenario-badge badge-category",
                ),
                Span(
                    scenario_data.get("difficulty", "").title(),
                    cls="scenario-badge badge-difficulty",
                ),
                Span(
                    f"{scenario_data.get('duration_minutes', 0)} min",
                    cls="scenario-badge badge-duration",
                ),
                Span(
                    "Active" if scenario_data.get("is_active", True) else "Inactive",
                    cls=f"scenario-badge {'badge-active' if scenario_data.get('is_active', True) else 'badge-inactive'}",
                ),
                cls="scenario-badges",
            ),
            cls="scenario-card-header",
        ),
        P(
            scenario_data.get("description", "No description"),
            cls="scenario-description",
        ),
        Div(
            f"Roles: {scenario_data.get('user_role', 'N/A')} ↔ {scenario_data.get('ai_role', 'N/A')}",
            style="color: #64748b; font-size: 0.875rem; margin-bottom: 15px;",
        ),
        Div(
            f"Phases: {len(scenario_data.get('phases', []))}, Setting: {scenario_data.get('setting', 'N/A')}",
            style="color: #64748b; font-size: 0.875rem; margin-bottom: 15px;",
        ),
        Div(
            Button(
                "Edit",
                cls="btn-scenario btn-primary",
                onclick=f"editScenario('{scenario_data.get('scenario_id', '')}')",
            ),
            Button(
                "Duplicate",
                cls="btn-scenario btn-secondary",
                onclick=f"duplicateScenario('{scenario_data.get('scenario_id', '')}')",
            ),
            Button(
                "Test",
                cls="btn-scenario btn-success",
                onclick=f"testScenario('{scenario_data.get('scenario_id', '')}')",
            ),
            Button(
                "Delete" if scenario_data.get("is_active", True) else "Restore",
                cls=f"btn-scenario {'btn-danger' if scenario_data.get('is_active', True) else 'btn-success'}",
                onclick=f"toggleScenario('{scenario_data.get('scenario_id', '')}')",
            ),
            cls="scenario-actions",
        ),
        cls="scenario-card",
    )


def create_content_config_panel():
    """Create content processing configuration panel"""
    return Div(
        H2(
            "Content Processing Configuration",
            style="margin-bottom: 30px; color: #1e293b;",
        ),
        Div(
            # Video Processing Section
            Div(
                H3("Video Processing", cls="config-title"),
                Div(
                    Div(
                        Label("Max Video Length (minutes)", cls="form-label"),
                        Input(
                            type="number",
                            value="60",
                            min="1",
                            max="480",
                            cls="form-control",
                            name="max_video_length",
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Label("AI Provider Preference", cls="form-label"),
                        Select(
                            Option("Mistral", value="mistral", selected=True),
                            Option("DeepSeek", value="deepseek"),
                            Option("Claude", value="claude"),
                            Option("OpenAI", value="openai"),
                            cls="form-control",
                            name="ai_provider_preference",
                        ),
                        cls="form-group",
                    ),
                    style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;",
                ),
                cls="config-section",
            ),
            # Content Generation Section
            Div(
                H3("Content Generation", cls="config-title"),
                Div(
                    Label(
                        Input(
                            type="checkbox", checked=True, name="enable_auto_flashcards"
                        ),
                        " Enable Auto-Flashcards",
                        style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;",
                    ),
                    Label(
                        Input(
                            type="checkbox", checked=True, name="enable_auto_quizzes"
                        ),
                        " Enable Auto-Quizzes",
                        style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;",
                    ),
                    Label(
                        Input(
                            type="checkbox", checked=True, name="enable_auto_summaries"
                        ),
                        " Enable Auto-Summaries",
                        style="display: flex; align-items: center; gap: 8px; margin-bottom: 20px;",
                    ),
                ),
                Div(
                    Div(
                        Label("Max Flashcards per Content", cls="form-label"),
                        Input(
                            type="number",
                            value="20",
                            min="5",
                            max="100",
                            cls="form-control",
                            name="max_flashcards",
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Label("Max Quiz Questions", cls="form-label"),
                        Input(
                            type="number",
                            value="10",
                            min="3",
                            max="50",
                            cls="form-control",
                            name="max_quiz_questions",
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Label("Summary Length", cls="form-label"),
                        Select(
                            Option("Short", value="short"),
                            Option("Medium", value="medium", selected=True),
                            Option("Long", value="long"),
                            cls="form-control",
                            name="summary_length",
                        ),
                        cls="form-group",
                    ),
                    style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;",
                ),
                cls="config-section",
            ),
            # Quality & Moderation Section
            Div(
                H3("Quality & Moderation", cls="config-title"),
                Div(
                    Div(
                        Label("Content Quality Threshold", cls="form-label"),
                        Input(
                            type="range",
                            min="0.1",
                            max="1.0",
                            step="0.1",
                            value="0.7",
                            cls="form-control",
                            name="quality_threshold",
                        ),
                        Small("Current: 0.7 (70%)", style="color: #64748b;"),
                        cls="form-group",
                    ),
                    Div(
                        Label(
                            Input(
                                type="checkbox", checked=True, name="language_detection"
                            ),
                            " Enable Language Detection",
                            style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;",
                        ),
                        Label(
                            Input(
                                type="checkbox", checked=True, name="content_moderation"
                            ),
                            " Enable Content Moderation",
                            style="display: flex; align-items: center; gap: 8px;",
                        ),
                    ),
                    style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;",
                ),
                cls="config-section",
            ),
            # Save Button
            Div(
                Button(
                    "Save Configuration",
                    cls="btn-scenario btn-primary",
                    onclick="saveContentConfig()",
                    style="padding: 12px 30px; font-size: 1rem;",
                ),
                Button(
                    "Reset to Defaults",
                    cls="btn-scenario btn-secondary",
                    onclick="resetContentConfig()",
                    style="padding: 12px 30px; font-size: 1rem;",
                ),
                style="display: flex; gap: 15px; justify-content: center; margin-top: 30px;",
            ),
            cls="config-panel",
        ),
    )


def create_statistics_panel():
    """Create statistics and analytics panel"""
    return Div(
        H2(
            "Scenario Statistics & Analytics",
            style="margin-bottom: 30px; color: #1e293b;",
        ),
        # Stats Grid
        Div(
            Div(
                Div("15", cls="stat-value"),
                Div("Total Scenarios", cls="stat-label"),
                cls="stat-card",
            ),
            Div(
                Div("12", cls="stat-value"),
                Div("Active Scenarios", cls="stat-label"),
                cls="stat-card",
            ),
            Div(
                Div("156", cls="stat-value"),
                Div("Total Sessions", cls="stat-label"),
                cls="stat-card",
            ),
            Div(
                Div("85%", cls="stat-value"),
                Div("Avg Completion Rate", cls="stat-label"),
                cls="stat-card",
            ),
            cls="stats-grid",
        ),
        # Charts and detailed stats would go here
        Div(
            H3("Most Popular Scenarios", style="margin-bottom: 20px;"),
            Div(
                Div(
                    "1. Restaurant Dinner Reservation",
                    style="padding: 10px; border-bottom: 1px solid #e5e7eb;",
                ),
                Div(
                    "2. Hotel Check-in",
                    style="padding: 10px; border-bottom: 1px solid #e5e7eb;",
                ),
                Div(
                    "3. Clothes Shopping",
                    style="padding: 10px; border-bottom: 1px solid #e5e7eb;",
                ),
                style="background: white; border-radius: 8px; border: 1px solid #e5e7eb;",
            ),
            style="margin-bottom: 30px;",
        ),
        Div(
            H3("Category Distribution", style="margin-bottom: 20px;"),
            Div(
                Div(
                    "Restaurant: 4 scenarios",
                    style="padding: 10px; border-bottom: 1px solid #e5e7eb;",
                ),
                Div(
                    "Travel: 3 scenarios",
                    style="padding: 10px; border-bottom: 1px solid #e5e7eb;",
                ),
                Div(
                    "Business: 3 scenarios",
                    style="padding: 10px; border-bottom: 1px solid #e5e7eb;",
                ),
                Div(
                    "Social: 3 scenarios",
                    style="padding: 10px; border-bottom: 1px solid #e5e7eb;",
                ),
                Div("Shopping: 2 scenarios", style="padding: 10px;"),
                style="background: white; border-radius: 8px; border: 1px solid #e5e7eb;",
            ),
        ),
    )


def create_scenario_modals():
    """Create modal dialogs for scenario operations"""
    return Div(
        # Create/Edit Scenario Modal
        Div(
            Div(
                H2(
                    "Create New Scenario",
                    id="modal-title",
                    style="margin-bottom: 25px;",
                ),
                create_scenario_form(),
                cls="modal-content",
            ),
            cls="modal-overlay",
            id="scenario-modal",
            style="display: none;",
            onclick="closeModal(event)",
        ),
        # Confirmation Modal
        Div(
            Div(
                H3("Confirm Action", style="margin-bottom: 20px;"),
                P(
                    "Are you sure you want to perform this action?",
                    id="confirm-message",
                ),
                Div(
                    Button(
                        "Cancel",
                        cls="btn-scenario btn-secondary",
                        onclick="closeConfirmModal()",
                    ),
                    Button(
                        "Confirm",
                        cls="btn-scenario btn-danger",
                        onclick="confirmAction()",
                        id="confirm-btn",
                    ),
                    style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;",
                ),
                cls="modal-content",
            ),
            cls="modal-overlay",
            id="confirm-modal",
            style="display: none;",
            onclick="closeConfirmModal(event)",
        ),
    )


def create_scenario_form():
    """Create scenario creation/editing form"""
    return Form(
        Div(
            Div(
                Label("Scenario Name", cls="form-label"),
                Input(
                    type="text",
                    name="name",
                    cls="form-control",
                    required=True,
                    placeholder="e.g., Restaurant Dinner Reservation",
                ),
                cls="form-group",
            ),
            Div(
                Label("Category", cls="form-label"),
                Select(
                    Option("Restaurant", value="restaurant"),
                    Option("Travel", value="travel"),
                    Option("Shopping", value="shopping"),
                    Option("Business", value="business"),
                    Option("Social", value="social"),
                    Option("Healthcare", value="healthcare"),
                    Option("Education", value="education"),
                    name="category",
                    cls="form-control",
                    required=True,
                ),
                cls="form-group",
            ),
            Div(
                Label("Difficulty", cls="form-label"),
                Select(
                    Option("Beginner", value="beginner"),
                    Option("Intermediate", value="intermediate"),
                    Option("Advanced", value="advanced"),
                    name="difficulty",
                    cls="form-control",
                    required=True,
                ),
                cls="form-group",
            ),
            style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 20px;",
        ),
        Div(
            Label("Description", cls="form-label"),
            Textarea(
                name="description",
                cls="form-control",
                required=True,
                placeholder="Describe the scenario and learning objectives...",
                rows="3",
            ),
            cls="form-group",
        ),
        Div(
            Div(
                Label("User Role", cls="form-label"),
                Select(
                    Option("Customer", value="customer"),
                    Option("Tourist", value="tourist"),
                    Option("Student", value="student"),
                    Option("Colleague", value="colleague"),
                    Option("Friend", value="friend"),
                    name="user_role",
                    cls="form-control",
                    required=True,
                ),
                cls="form-group",
            ),
            Div(
                Label("AI Role", cls="form-label"),
                Select(
                    Option("Service Provider", value="service_provider"),
                    Option("Local", value="local"),
                    Option("Teacher", value="teacher"),
                    Option("Colleague", value="colleague"),
                    Option("Friend", value="friend"),
                    name="ai_role",
                    cls="form-control",
                    required=True,
                ),
                cls="form-group",
            ),
            Div(
                Label("Duration (minutes)", cls="form-label"),
                Input(
                    type="number",
                    name="duration_minutes",
                    cls="form-control",
                    min="5",
                    max="120",
                    value="20",
                    required=True,
                ),
                cls="form-group",
            ),
            style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;",
        ),
        Div(
            Label("Setting", cls="form-label"),
            Input(
                type="text",
                name="setting",
                cls="form-control",
                required=True,
                placeholder="e.g., A busy restaurant in downtown",
            ),
            cls="form-group",
        ),
        # Phases Section
        Div(
            H3("Scenario Phases", style="margin-bottom: 15px;"),
            Div(id="phases-container"),
            Button(
                "+ Add Phase",
                type="button",
                cls="btn-scenario btn-secondary",
                onclick="addPhase()",
            ),
            style="margin: 30px 0;",
        ),
        # Form Actions
        Div(
            Button(
                "Cancel",
                type="button",
                cls="btn-scenario btn-secondary",
                onclick="closeModal()",
            ),
            Button("Save Scenario", type="submit", cls="btn-scenario btn-primary"),
            style="display: flex; gap: 15px; justify-content: flex-end; margin-top: 30px;",
        ),
        onsubmit="saveScenario(event)",
        id="scenario-form",
    )


def scenario_management_javascript():
    """JavaScript for scenario management functionality"""
    return Script("""
        let scenarios = [];
        let selectedScenarios = new Set();
        let currentEditingId = null;

        // Initialize the page
        document.addEventListener('DOMContentLoaded', function() {
            loadScenarios();
            addInitialPhase();
        });

        // Tab management
        function showTab(tabName) {
            // Hide all tab contents
            document.getElementById('scenarios-content').style.display = 'none';
            document.getElementById('content-config-content').style.display = 'none';
            document.getElementById('statistics-content').style.display = 'none';

            // Remove active class from all tabs
            document.querySelectorAll('.scenario-tab').forEach(tab => tab.classList.remove('active'));

            // Show selected tab content
            document.getElementById(tabName + '-content').style.display = 'block';

            // Add active class to clicked tab
            event.target.classList.add('active');
        }

        // Load scenarios from API
        async function loadScenarios() {
            try {
                const response = await fetch('/api/admin/scenario-management/scenarios');
                scenarios = await response.json();
                renderScenarios();
            } catch (error) {
                console.error('Error loading scenarios:', error);
                showMessage('Error loading scenarios', 'error');
            }
        }

        // Render scenarios grid
        function renderScenarios() {
            const grid = document.getElementById('scenario-grid');
            grid.innerHTML = '';

            scenarios.forEach(scenario => {
                grid.appendChild(createScenarioCard(scenario));
            });
        }

        // Create scenario card HTML
        function createScenarioCard(scenario) {
            const card = document.createElement('div');
            card.className = 'scenario-card';
            card.innerHTML = `
                <input type="checkbox" class="checkbox-scenario" value="${scenario.scenario_id}" onchange="updateSelection()">
                <div class="scenario-card-header">
                    <h3 class="scenario-title">${scenario.name}</h3>
                    <div class="scenario-badges">
                        <span class="scenario-badge badge-category">${scenario.category}</span>
                        <span class="scenario-badge badge-difficulty">${scenario.difficulty}</span>
                        <span class="scenario-badge badge-duration">${scenario.duration_minutes} min</span>
                        <span class="scenario-badge ${scenario.is_active ? 'badge-active' : 'badge-inactive'}">
                            ${scenario.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </div>
                </div>
                <p class="scenario-description">${scenario.description}</p>
                <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 15px;">
                    Roles: ${scenario.user_role} ↔ ${scenario.ai_role}
                </div>
                <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 15px;">
                    Phases: ${scenario.phases.length}, Setting: ${scenario.setting}
                </div>
                <div class="scenario-actions">
                    <button class="btn-scenario btn-primary" onclick="editScenario('${scenario.scenario_id}')">Edit</button>
                    <button class="btn-scenario btn-secondary" onclick="duplicateScenario('${scenario.scenario_id}')">Duplicate</button>
                    <button class="btn-scenario btn-success" onclick="testScenario('${scenario.scenario_id}')">Test</button>
                    <button class="btn-scenario ${scenario.is_active ? 'btn-danger' : 'btn-success'}" onclick="toggleScenario('${scenario.scenario_id}')">
                        ${scenario.is_active ? 'Delete' : 'Restore'}
                    </button>
                </div>
            `;
            return card;
        }

        // Filter scenarios
        function filterScenarios() {
            const category = document.querySelector('select[name="category_filter"]').value;
            const difficulty = document.querySelector('select[name="difficulty_filter"]').value;
            const status = document.querySelector('select[name="status_filter"]').value;
            const search = document.querySelector('input[name="search_filter"]').value.toLowerCase();

            const filtered = scenarios.filter(scenario => {
                const matchesCategory = !category || scenario.category === category;
                const matchesDifficulty = !difficulty || scenario.difficulty === difficulty;
                const matchesStatus = !status ||
                    (status === 'active' && scenario.is_active) ||
                    (status === 'inactive' && !scenario.is_active);
                const matchesSearch = !search ||
                    scenario.name.toLowerCase().includes(search) ||
                    scenario.description.toLowerCase().includes(search);

                return matchesCategory && matchesDifficulty && matchesStatus && matchesSearch;
            });

            const grid = document.getElementById('scenario-grid');
            grid.innerHTML = '';
            filtered.forEach(scenario => {
                grid.appendChild(createScenarioCard(scenario));
            });
        }

        // Selection management
        function updateSelection() {
            const checkboxes = document.querySelectorAll('.checkbox-scenario:checked');
            selectedScenarios.clear();
            checkboxes.forEach(cb => selectedScenarios.add(cb.value));

            const count = selectedScenarios.size;
            document.getElementById('selected-count').textContent = `${count} selected`;
            document.getElementById('bulk-actions').style.display = count > 0 ? 'block' : 'none';
        }

        // Modal management
        function showCreateScenario() {
            currentEditingId = null;
            document.getElementById('modal-title').textContent = 'Create New Scenario';
            document.getElementById('scenario-form').reset();
            clearPhases();
            addInitialPhase();
            document.getElementById('scenario-modal').style.display = 'flex';
        }

        function editScenario(scenarioId) {
            currentEditingId = scenarioId;
            const scenario = scenarios.find(s => s.scenario_id === scenarioId);
            if (!scenario) return;

            document.getElementById('modal-title').textContent = 'Edit Scenario';
            populateForm(scenario);
            document.getElementById('scenario-modal').style.display = 'flex';
        }

        function closeModal(event) {
            if (event && event.target !== event.currentTarget) return;
            document.getElementById('scenario-modal').style.display = 'none';
        }

        // Phase management
        function addInitialPhase() {
            const container = document.getElementById('phases-container');
            if (container.children.length === 0) {
                addPhase();
            }
        }

        function addPhase() {
            const container = document.getElementById('phases-container');
            const phaseIndex = container.children.length;

            const phaseDiv = document.createElement('div');
            phaseDiv.className = 'phase-section';
            phaseDiv.innerHTML = `
                <div class="phase-header">
                    <h4>Phase ${phaseIndex + 1}</h4>
                    <button type="button" class="btn-scenario btn-danger" onclick="removePhase(this)">Remove</button>
                </div>
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 15px; margin-bottom: 15px;">
                    <div class="form-group">
                        <label class="form-label">Phase Name</label>
                        <input type="text" name="phase_name[]" class="form-control" required placeholder="e.g., Introduction">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Duration (minutes)</label>
                        <input type="number" name="phase_duration[]" class="form-control" min="1" max="60" value="5" required>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <textarea name="phase_description[]" class="form-control" rows="2" required placeholder="Describe what happens in this phase..."></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">Key Vocabulary (comma-separated)</label>
                    <input type="text" name="phase_vocabulary[]" class="form-control" placeholder="hello, table, reservation">
                </div>
                <div class="form-group">
                    <label class="form-label">Essential Phrases (comma-separated)</label>
                    <input type="text" name="phase_phrases[]" class="form-control" placeholder="I'd like to make a reservation, What time works for you?">
                </div>
            `;

            container.appendChild(phaseDiv);
        }

        function removePhase(button) {
            button.closest('.phase-section').remove();
            updatePhaseNumbers();
        }

        function clearPhases() {
            document.getElementById('phases-container').innerHTML = '';
        }

        function updatePhaseNumbers() {
            const phases = document.querySelectorAll('.phase-section');
            phases.forEach((phase, index) => {
                phase.querySelector('h4').textContent = `Phase ${index + 1}`;
            });
        }

        // Form handling
        async function saveScenario(event) {
            event.preventDefault();

            const formData = new FormData(event.target);
            const scenarioData = {
                name: formData.get('name'),
                category: formData.get('category'),
                difficulty: formData.get('difficulty'),
                description: formData.get('description'),
                user_role: formData.get('user_role'),
                ai_role: formData.get('ai_role'),
                setting: formData.get('setting'),
                duration_minutes: parseInt(formData.get('duration_minutes')),
                phases: []
            };

            // Collect phases
            const phaseNames = formData.getAll('phase_name[]');
            const phaseDurations = formData.getAll('phase_duration[]');
            const phaseDescriptions = formData.getAll('phase_description[]');
            const phaseVocabulary = formData.getAll('phase_vocabulary[]');
            const phasePhrases = formData.getAll('phase_phrases[]');

            for (let i = 0; i < phaseNames.length; i++) {
                scenarioData.phases.push({
                    phase_id: `phase_${i + 1}`,
                    name: phaseNames[i],
                    description: phaseDescriptions[i],
                    expected_duration_minutes: parseInt(phaseDurations[i]),
                    key_vocabulary: phaseVocabulary[i] ? phaseVocabulary[i].split(',').map(v => v.trim()) : [],
                    essential_phrases: phasePhrases[i] ? phasePhrases[i].split(',').map(p => p.trim()) : [],
                    learning_objectives: [],
                    success_criteria: []
                });
            }

            try {
                const url = currentEditingId
                    ? `/api/admin/scenario-management/scenarios/${currentEditingId}`
                    : '/api/admin/scenario-management/scenarios';
                const method = currentEditingId ? 'PUT' : 'POST';

                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(scenarioData)
                });

                if (response.ok) {
                    showMessage(`Scenario ${currentEditingId ? 'updated' : 'created'} successfully`, 'success');
                    closeModal();
                    loadScenarios();
                } else {
                    const error = await response.text();
                    showMessage(`Error: ${error}`, 'error');
                }
            } catch (error) {
                console.error('Error saving scenario:', error);
                showMessage('Error saving scenario', 'error');
            }
        }

        // Content configuration
        async function saveContentConfig() {
            const form = document.querySelector('.config-panel');
            const formData = new FormData(form);

            const config = {
                max_video_length_minutes: parseInt(formData.get('max_video_length')),
                ai_provider_preference: formData.get('ai_provider_preference'),
                enable_auto_flashcards: formData.has('enable_auto_flashcards'),
                enable_auto_quizzes: formData.has('enable_auto_quizzes'),
                enable_auto_summaries: formData.has('enable_auto_summaries'),
                max_flashcards_per_content: parseInt(formData.get('max_flashcards')),
                max_quiz_questions: parseInt(formData.get('max_quiz_questions')),
                summary_length_preference: formData.get('summary_length'),
                language_detection_enabled: formData.has('language_detection'),
                content_quality_threshold: parseFloat(formData.get('quality_threshold')),
                enable_content_moderation: formData.has('content_moderation')
            };

            try {
                const response = await fetch('/api/admin/scenario-management/content-config', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(config)
                });

                if (response.ok) {
                    showMessage('Configuration saved successfully', 'success');
                } else {
                    showMessage('Error saving configuration', 'error');
                }
            } catch (error) {
                console.error('Error saving config:', error);
                showMessage('Error saving configuration', 'error');
            }
        }

        // Utility functions
        function showMessage(message, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = type === 'error' ? 'error-message' : 'success-message';
            messageDiv.textContent = message;

            const container = document.querySelector('.scenario-management-container');
            container.insertBefore(messageDiv, container.firstChild);

            setTimeout(() => {
                messageDiv.remove();
            }, 5000);
        }

        function populateForm(scenario) {
            document.querySelector('input[name="name"]').value = scenario.name;
            document.querySelector('select[name="category"]').value = scenario.category;
            document.querySelector('select[name="difficulty"]').value = scenario.difficulty;
            document.querySelector('textarea[name="description"]').value = scenario.description;
            document.querySelector('select[name="user_role"]').value = scenario.user_role;
            document.querySelector('select[name="ai_role"]').value = scenario.ai_role;
            document.querySelector('input[name="setting"]').value = scenario.setting;
            document.querySelector('input[name="duration_minutes"]').value = scenario.duration_minutes;

            // Populate phases
            clearPhases();
            scenario.phases.forEach((phase, index) => {
                addPhase();
                const phaseSection = document.querySelectorAll('.phase-section')[index];
                phaseSection.querySelector('input[name="phase_name[]"]').value = phase.name;
                phaseSection.querySelector('input[name="phase_duration[]"]').value = phase.expected_duration_minutes;
                phaseSection.querySelector('textarea[name="phase_description[]"]').value = phase.description;
                phaseSection.querySelector('input[name="phase_vocabulary[]"]').value = phase.key_vocabulary.join(', ');
                phaseSection.querySelector('input[name="phase_phrases[]"]').value = phase.essential_phrases.join(', ');
            });
        }

        // Bulk operations
        async function bulkOperation(operation) {
            if (selectedScenarios.size === 0) return;

            try {
                const response = await fetch('/api/admin/scenario-management/scenarios/bulk', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        operation: operation,
                        scenario_ids: Array.from(selectedScenarios)
                    })
                });

                if (response.ok) {
                    showMessage(`Bulk ${operation} completed successfully`, 'success');
                    loadScenarios();
                    selectedScenarios.clear();
                    updateSelection();
                } else {
                    showMessage(`Error performing bulk ${operation}`, 'error');
                }
            } catch (error) {
                console.error(`Error in bulk ${operation}:`, error);
                showMessage(`Error performing bulk ${operation}`, 'error');
            }
        }

        // Individual scenario operations
        async function toggleScenario(scenarioId) {
            // Implementation for toggle scenario active/inactive
            loadScenarios();
        }

        function duplicateScenario(scenarioId) {
            const scenario = scenarios.find(s => s.scenario_id === scenarioId);
            if (!scenario) return;

            // Create a copy with modified name
            const copy = {...scenario};
            copy.name = scenario.name + ' (Copy)';
            delete copy.scenario_id;

            currentEditingId = null;
            document.getElementById('modal-title').textContent = 'Duplicate Scenario';
            populateForm(copy);
            document.getElementById('scenario-modal').style.display = 'flex';
        }

        function testScenario(scenarioId) {
            // Implementation for testing scenario
            showMessage('Scenario test started', 'success');
        }

        function importScenarios() {
            // Implementation for importing scenarios
            showMessage('Import functionality coming soon', 'success');
        }

        function exportScenarios() {
            // Implementation for exporting scenarios
            showMessage('Export functionality coming soon', 'success');
        }

        function resetContentConfig() {
            // Reset form to defaults
            document.querySelector('input[name="max_video_length"]').value = '60';
            document.querySelector('select[name="ai_provider_preference"]').value = 'mistral';
            // ... reset other fields
            showMessage('Configuration reset to defaults', 'success');
        }
    """)
