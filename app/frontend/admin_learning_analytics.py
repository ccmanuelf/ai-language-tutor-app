"""
Admin Learning Analytics Configuration Panel
Task 3.1.4 - Admin Configuration Panel for Learning Analytics

FastHTML components for admin configuration of spaced repetition algorithms,
learning analytics settings, and gamification parameters.
"""

from typing import Dict, Optional

from fasthtml.common import *


def admin_learning_analytics_styles():
    """CSS styles for admin learning analytics configuration"""
    return Style("""
        /* Admin Learning Analytics Configuration Styles */
        .admin-analytics-page {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            min-height: 100vh;
            padding: 2rem;
        }

        .admin-analytics-container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(10px);
        }

        .admin-header {
            text-align: center;
            margin-bottom: 3rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 2rem;
        }

        .admin-title {
            background: linear-gradient(135deg, #1e293b, #475569);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .admin-subtitle {
            color: #64748b;
            font-size: 1rem;
            margin-bottom: 1rem;
        }

        .admin-breadcrumb {
            color: #94a3b8;
            font-size: 0.9rem;
        }

        /* Configuration Sections */
        .config-sections {
            display: grid;
            gap: 2rem;
        }

        .config-section {
            background: #ffffff;
            border-radius: 16px;
            padding: 2rem;
            border: 1px solid rgba(0, 0, 0, 0.05);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }

        .config-section:hover {
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }

        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #f1f5f9;
        }

        .section-title {
            display: flex;
            align-items: center;
            font-size: 1.4rem;
            font-weight: 700;
            color: #1e293b;
        }

        .section-icon {
            font-size: 1.5rem;
            margin-right: 0.75rem;
            background: linear-gradient(135deg, #1e293b, #475569);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .section-status {
            background: linear-gradient(135deg, #10b981, #22c55e);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        /* Configuration Forms */
        .config-form {
            display: grid;
            gap: 1.5rem;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-label {
            font-weight: 600;
            color: #374151;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }

        .form-help {
            font-size: 0.8rem;
            color: #6b7280;
            margin-top: 0.25rem;
        }

        .form-input {
            padding: 0.75rem;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            background: #fafafa;
        }

        .form-input:focus {
            outline: none;
            border-color: #3b82f6;
            background: #ffffff;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .form-select {
            padding: 0.75rem;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 0.9rem;
            background: #fafafa;
            transition: all 0.3s ease;
        }

        .form-select:focus {
            outline: none;
            border-color: #3b82f6;
            background: #ffffff;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .form-checkbox {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }

        .checkbox {
            width: 18px;
            height: 18px;
            accent-color: #3b82f6;
        }

        /* Algorithm Configuration */
        .algorithm-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
        }

        .algorithm-param {
            background: linear-gradient(135deg, #f8fafc, #e2e8f0);
            border-radius: 12px;
            padding: 1.5rem;
            border-left: 4px solid #3b82f6;
        }

        .param-name {
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.5rem;
        }

        .param-description {
            color: #64748b;
            font-size: 0.85rem;
            margin-bottom: 1rem;
        }

        .param-input {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 0.9rem;
        }

        .param-current {
            color: #6b7280;
            font-size: 0.8rem;
            margin-top: 0.25rem;
        }

        /* System Analytics */
        .analytics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
        }

        .analytics-card {
            background: linear-gradient(135deg, #fef3c7, #fbbf24);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            border: 2px solid #f59e0b;
        }

        .analytics-value {
            font-size: 2rem;
            font-weight: 700;
            color: #92400e;
            margin-bottom: 0.5rem;
        }

        .analytics-label {
            color: #b45309;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.5px;
        }

        /* Action Buttons */
        .action-buttons {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 2px solid #f1f5f9;
        }

        .btn-primary {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(59, 130, 246, 0.3);
        }

        .btn-secondary {
            background: #f1f5f9;
            color: #475569;
            border: 2px solid #e2e8f0;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }

        .btn-secondary:hover {
            background: #e2e8f0;
            transform: translateY(-1px);
        }

        .btn-danger {
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }

        .btn-danger:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(239, 68, 68, 0.3);
        }

        /* Success/Error Messages */
        .message {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            font-weight: 500;
        }

        .message-success {
            background: #d1fae5;
            color: #065f46;
            border: 2px solid #10b981;
        }

        .message-error {
            background: #fee2e2;
            color: #991b1b;
            border: 2px solid #ef4444;
        }

        .message-warning {
            background: #fef3c7;
            color: #92400e;
            border: 2px solid #f59e0b;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .admin-analytics-page {
                padding: 1rem;
            }

            .admin-analytics-container {
                padding: 1rem;
            }

            .admin-title {
                font-size: 1.8rem;
            }

            .form-grid {
                grid-template-columns: 1fr;
            }

            .algorithm-grid {
                grid-template-columns: 1fr;
            }

            .analytics-grid {
                grid-template-columns: 1fr;
            }

            .action-buttons {
                flex-direction: column;
            }
        }

        /* Animation */
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    """)


def admin_learning_analytics_page(
    current_config: Optional[Dict] = None, system_stats: Optional[Dict] = None
):
    """Main admin learning analytics configuration page"""

    # Default configuration if none provided
    if not current_config:
        current_config = {
            "initial_ease_factor": 2.5,
            "minimum_ease_factor": 1.3,
            "maximum_ease_factor": 3.0,
            "ease_factor_change": 0.15,
            "initial_interval_days": 1,
            "graduation_interval_days": 4,
            "easy_interval_days": 7,
            "maximum_interval_days": 365,
            "mastery_threshold": 0.85,
            "review_threshold": 0.7,
            "difficulty_threshold": 0.5,
            "retention_threshold": 0.8,
            "points_per_correct": 10,
            "points_per_streak_day": 5,
            "points_per_goal_achieved": 100,
            "daily_goal_default": 30,
        }

    # Default system stats if none provided
    if not system_stats:
        system_stats = {
            "total_users": 45,
            "total_sessions": 1250,
            "total_study_time": 34500,
            "avg_accuracy": 76.8,
            "total_items": 15800,
            "avg_mastery": 0.68,
            "mastered_items": 8945,
        }

    return Div(
        admin_learning_analytics_styles(),
        # Admin Container
        Div(
            # Header Section
            Div(
                H1("Learning Analytics Configuration", cls="admin-title fade-in"),
                P(
                    "Configure spaced repetition algorithms, gamification, and analytics settings",
                    cls="admin-subtitle",
                ),
                P("Dashboard > Admin > Learning Analytics", cls="admin-breadcrumb"),
                cls="admin-header",
            ),
            # Configuration Sections
            Div(
                # System Analytics Overview
                create_system_analytics_section(system_stats),
                # Spaced Repetition Algorithm Configuration
                create_algorithm_config_section(current_config),
                # Gamification Settings
                create_gamification_config_section(current_config),
                # Performance Thresholds
                create_thresholds_config_section(current_config),
                # Advanced Settings
                create_advanced_settings_section(),
                cls="config-sections",
            ),
            cls="admin-analytics-container",
        ),
        cls="admin-analytics-page",
    )


def create_system_analytics_section(system_stats: Dict):
    """Create system analytics overview section"""

    return Div(
        Div(
            Div(
                Span("📊", cls="section-icon"),
                "System Analytics Overview",
                cls="section-title",
            ),
            Span("Live Data", cls="section-status"),
            cls="section-header",
        ),
        Div(
            Div(
                Div(f"{system_stats.get('total_users', 0):,}", cls="analytics-value"),
                Div("Active Users", cls="analytics-label"),
                cls="analytics-card",
            ),
            Div(
                Div(
                    f"{system_stats.get('total_sessions', 0):,}", cls="analytics-value"
                ),
                Div("Learning Sessions", cls="analytics-label"),
                cls="analytics-card",
            ),
            Div(
                Div(
                    f"{system_stats.get('total_study_time', 0):,}",
                    cls="analytics-value",
                ),
                Div("Study Minutes", cls="analytics-label"),
                cls="analytics-card",
            ),
            Div(
                Div(
                    f"{system_stats.get('avg_accuracy', 0):.1f}%", cls="analytics-value"
                ),
                Div("Average Accuracy", cls="analytics-label"),
                cls="analytics-card",
            ),
            Div(
                Div(f"{system_stats.get('total_items', 0):,}", cls="analytics-value"),
                Div("Learning Items", cls="analytics-label"),
                cls="analytics-card",
            ),
            Div(
                Div(
                    f"{system_stats.get('avg_mastery', 0) * 100:.0f}%",
                    cls="analytics-value",
                ),
                Div("Average Mastery", cls="analytics-label"),
                cls="analytics-card",
            ),
            cls="analytics-grid",
        ),
        cls="config-section fade-in",
    )


def create_algorithm_config_section(config: Dict):
    """Create spaced repetition algorithm configuration section"""

    return Div(
        Div(
            Div(
                Span("🧠", cls="section-icon"),
                "Spaced Repetition Algorithm",
                cls="section-title",
            ),
            Span("SM-2 Enhanced", cls="section-status"),
            cls="section-header",
        ),
        Form(
            P(
                "Configure the core parameters of the SM-2 spaced repetition algorithm that determines "
                "when items should be reviewed for optimal learning retention.",
                style="color: #64748b; margin-bottom: 2rem; line-height: 1.6;",
            ),
            Div(
                # Ease Factor Settings
                Div(
                    Div("Initial Ease Factor", cls="param-name"),
                    Div(
                        "Starting ease factor for new items (higher = longer intervals)",
                        cls="param-description",
                    ),
                    Input(
                        type="number",
                        step="0.1",
                        min="1.0",
                        max="5.0",
                        value=config.get("initial_ease_factor", 2.5),
                        name="initial_ease_factor",
                        cls="param-input",
                    ),
                    Div(
                        f"Current: {config.get('initial_ease_factor', 2.5)}",
                        cls="param-current",
                    ),
                    cls="algorithm-param",
                ),
                # Interval Settings
                Div(
                    Div("Initial Interval (Days)", cls="param-name"),
                    Div(
                        "Number of days before first review of a new item",
                        cls="param-description",
                    ),
                    Input(
                        type="number",
                        min="1",
                        max="7",
                        value=config.get("initial_interval_days", 1),
                        name="initial_interval_days",
                        cls="param-input",
                    ),
                    Div(
                        f"Current: {config.get('initial_interval_days', 1)} days",
                        cls="param-current",
                    ),
                    cls="algorithm-param",
                ),
                # Graduation Interval
                Div(
                    Div("Graduation Interval (Days)", cls="param-name"),
                    Div(
                        "Interval after the second successful review",
                        cls="param-description",
                    ),
                    Input(
                        type="number",
                        min="1",
                        max="14",
                        value=config.get("graduation_interval_days", 4),
                        name="graduation_interval_days",
                        cls="param-input",
                    ),
                    Div(
                        f"Current: {config.get('graduation_interval_days', 4)} days",
                        cls="param-current",
                    ),
                    cls="algorithm-param",
                ),
                # Easy Interval
                Div(
                    Div("Easy Interval (Days)", cls="param-name"),
                    Div(
                        "Interval when an item is marked as 'easy'",
                        cls="param-description",
                    ),
                    Input(
                        type="number",
                        min="1",
                        max="30",
                        value=config.get("easy_interval_days", 7),
                        name="easy_interval_days",
                        cls="param-input",
                    ),
                    Div(
                        f"Current: {config.get('easy_interval_days', 7)} days",
                        cls="param-current",
                    ),
                    cls="algorithm-param",
                ),
                # Maximum Interval
                Div(
                    Div("Maximum Interval (Days)", cls="param-name"),
                    Div(
                        "Maximum days between reviews (prevents extremely long intervals)",
                        cls="param-description",
                    ),
                    Input(
                        type="number",
                        min="30",
                        max="1000",
                        value=config.get("maximum_interval_days", 365),
                        name="maximum_interval_days",
                        cls="param-input",
                    ),
                    Div(
                        f"Current: {config.get('maximum_interval_days', 365)} days",
                        cls="param-current",
                    ),
                    cls="algorithm-param",
                ),
                # Ease Factor Change
                Div(
                    Div("Ease Factor Change", cls="param-name"),
                    Div(
                        "How much ease factor changes based on review performance",
                        cls="param-description",
                    ),
                    Input(
                        type="number",
                        step="0.01",
                        min="0.05",
                        max="0.5",
                        value=config.get("ease_factor_change", 0.15),
                        name="ease_factor_change",
                        cls="param-input",
                    ),
                    Div(
                        f"Current: {config.get('ease_factor_change', 0.15)}",
                        cls="param-current",
                    ),
                    cls="algorithm-param",
                ),
                cls="algorithm-grid",
            ),
            Div(
                Button(
                    "Reset to Defaults",
                    type="button",
                    cls="btn-secondary",
                    onclick="resetAlgorithmDefaults()",
                ),
                Button("Save Algorithm Settings", type="submit", cls="btn-primary"),
                cls="action-buttons",
            ),
            method="POST",
            action="/api/admin/learning-analytics/algorithm-config",
            cls="config-form",
        ),
        cls="config-section fade-in",
    )


def create_gamification_config_section(config: Dict):
    """Create gamification settings configuration section"""

    return Div(
        Div(
            Div(
                Span("🎮", cls="section-icon"),
                "Gamification Settings",
                cls="section-title",
            ),
            Span("Active", cls="section-status"),
            cls="section-header",
        ),
        Form(
            P(
                "Configure points, achievements, and daily goals to motivate learners and "
                "provide positive reinforcement for consistent study habits.",
                style="color: #64748b; margin-bottom: 2rem; line-height: 1.6;",
            ),
            Div(
                Div(
                    Label("Points per Correct Answer", cls="form-label"),
                    Input(
                        type="number",
                        min="1",
                        max="100",
                        value=config.get("points_per_correct", 10),
                        name="points_per_correct",
                        cls="form-input",
                    ),
                    P(
                        "Points awarded for each correctly answered item",
                        cls="form-help",
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Points per Streak Day", cls="form-label"),
                    Input(
                        type="number",
                        min="1",
                        max="50",
                        value=config.get("points_per_streak_day", 5),
                        name="points_per_streak_day",
                        cls="form-input",
                    ),
                    P(
                        "Daily bonus points for maintaining learning streaks",
                        cls="form-help",
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Points per Goal Achievement", cls="form-label"),
                    Input(
                        type="number",
                        min="10",
                        max="1000",
                        value=config.get("points_per_goal_achieved", 100),
                        name="points_per_goal_achieved",
                        cls="form-input",
                    ),
                    P(
                        "Points awarded when users complete learning goals",
                        cls="form-help",
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Default Daily Goal (minutes)", cls="form-label"),
                    Input(
                        type="number",
                        min="5",
                        max="300",
                        value=config.get("daily_goal_default", 30),
                        name="daily_goal_default",
                        cls="form-input",
                    ),
                    P("Default daily study time goal for new users", cls="form-help"),
                    cls="form-group",
                ),
                cls="form-grid",
            ),
            # Achievement Settings
            H3(
                "Achievement Settings",
                style="margin-top: 2rem; margin-bottom: 1rem; color: #1e293b;",
            ),
            Div(
                Div(
                    Label(cls="form-checkbox"),
                    Input(
                        type="checkbox",
                        checked=True,
                        name="enable_streak_achievements",
                        cls="checkbox",
                    ),
                    Span("Enable streak achievements"),
                    P("Award badges for consecutive study days", cls="form-help"),
                    cls="form-group",
                ),
                Div(
                    Label(cls="form-checkbox"),
                    Input(
                        type="checkbox",
                        checked=True,
                        name="enable_vocabulary_achievements",
                        cls="checkbox",
                    ),
                    Span("Enable vocabulary achievements"),
                    P("Award badges for learning new words", cls="form-help"),
                    cls="form-group",
                ),
                Div(
                    Label(cls="form-checkbox"),
                    Input(
                        type="checkbox",
                        checked=True,
                        name="enable_mastery_achievements",
                        cls="checkbox",
                    ),
                    Span("Enable mastery achievements"),
                    P("Award badges for achieving high proficiency", cls="form-help"),
                    cls="form-group",
                ),
                Div(
                    Label(cls="form-checkbox"),
                    Input(
                        type="checkbox",
                        checked=True,
                        name="enable_goal_achievements",
                        cls="checkbox",
                    ),
                    Span("Enable goal achievements"),
                    P("Award badges for completing learning goals", cls="form-help"),
                    cls="form-group",
                ),
                cls="form-grid",
            ),
            Div(
                Button("Preview Changes", type="button", cls="btn-secondary"),
                Button("Save Gamification Settings", type="submit", cls="btn-primary"),
                cls="action-buttons",
            ),
            method="POST",
            action="/api/admin/learning-analytics/gamification-config",
            cls="config-form",
        ),
        cls="config-section fade-in",
    )


def create_thresholds_config_section(config: Dict):
    """Create performance thresholds configuration section"""

    return Div(
        Div(
            Div(
                Span("🎯", cls="section-icon"),
                "Performance Thresholds",
                cls="section-title",
            ),
            Span("Optimized", cls="section-status"),
            cls="section-header",
        ),
        Form(
            P(
                "Set performance thresholds that determine when items are considered mastered, "
                "when to schedule reviews, and how to assess learning difficulty.",
                style="color: #64748b; margin-bottom: 2rem; line-height: 1.6;",
            ),
            Div(
                Div(
                    Label("Mastery Threshold", cls="form-label"),
                    Input(
                        type="number",
                        step="0.05",
                        min="0.5",
                        max="1.0",
                        value=config.get("mastery_threshold", 0.85),
                        name="mastery_threshold",
                        cls="form-input",
                    ),
                    P(
                        "Accuracy level considered 'mastered' (0.85 = 85%)",
                        cls="form-help",
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Review Threshold", cls="form-label"),
                    Input(
                        type="number",
                        step="0.05",
                        min="0.3",
                        max="1.0",
                        value=config.get("review_threshold", 0.7),
                        name="review_threshold",
                        cls="form-input",
                    ),
                    P(
                        "Accuracy level that triggers additional reviews",
                        cls="form-help",
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Difficulty Threshold", cls="form-label"),
                    Input(
                        type="number",
                        step="0.05",
                        min="0.1",
                        max="0.8",
                        value=config.get("difficulty_threshold", 0.5),
                        name="difficulty_threshold",
                        cls="form-input",
                    ),
                    P(
                        "Accuracy level that marks items as 'difficult'",
                        cls="form-help",
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Retention Threshold", cls="form-label"),
                    Input(
                        type="number",
                        step="0.05",
                        min="0.5",
                        max="1.0",
                        value=config.get("retention_threshold", 0.8),
                        name="retention_threshold",
                        cls="form-input",
                    ),
                    P("Long-term retention rate target", cls="form-help"),
                    cls="form-group",
                ),
                cls="form-grid",
            ),
            Div(
                Button("Run Threshold Analysis", type="button", cls="btn-secondary"),
                Button("Save Threshold Settings", type="submit", cls="btn-primary"),
                cls="action-buttons",
            ),
            method="POST",
            action="/api/admin/learning-analytics/thresholds-config",
            cls="config-form",
        ),
        cls="config-section fade-in",
    )


def create_advanced_settings_section():
    """Create advanced settings configuration section"""

    return Div(
        Div(
            Div(
                Span("⚙️", cls="section-icon"), "Advanced Settings", cls="section-title"
            ),
            Span(
                "Expert",
                cls="section-status",
                style="background: linear-gradient(135deg, #f59e0b, #d97706);",
            ),
            cls="section-header",
        ),
        Div(
            P(
                "⚠️ Advanced configuration options. Changes here may significantly impact "
                "the learning experience. Please review carefully before making modifications.",
                cls="message message-warning",
            ),
            Div(
                Div(
                    Label("Analytics Data Retention (days)", cls="form-label"),
                    Select(
                        Option("30 days", value="30"),
                        Option("90 days", value="90", selected=True),
                        Option("365 days", value="365"),
                        Option("Indefinite", value="-1"),
                        name="data_retention_days",
                        cls="form-select",
                    ),
                    P("How long to keep detailed analytics data", cls="form-help"),
                    cls="form-group",
                ),
                Div(
                    Label("Performance Calculation Method", cls="form-label"),
                    Select(
                        Option("Weighted Average", value="weighted", selected=True),
                        Option("Simple Average", value="simple"),
                        Option("Exponential Smoothing", value="exponential"),
                        name="performance_method",
                        cls="form-select",
                    ),
                    P(
                        "Method for calculating user performance metrics",
                        cls="form-help",
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Auto-Archive Inactive Items", cls="form-label"),
                    Div(
                        Input(
                            type="checkbox",
                            checked=True,
                            name="auto_archive_inactive",
                            cls="checkbox",
                        ),
                        Span("Archive items not reviewed for 6+ months"),
                        cls="form-checkbox",
                    ),
                    P("Automatically archive stale learning items", cls="form-help"),
                    cls="form-group",
                ),
                Div(
                    Label("Enable Debug Logging", cls="form-label"),
                    Div(
                        Input(
                            type="checkbox", name="enable_debug_logging", cls="checkbox"
                        ),
                        Span("Enable detailed algorithm logging"),
                        cls="form-checkbox",
                    ),
                    P("Log detailed spaced repetition calculations", cls="form-help"),
                    cls="form-group",
                ),
                cls="form-grid",
            ),
            # System Actions
            H3(
                "System Actions",
                style="margin-top: 2rem; margin-bottom: 1rem; color: #1e293b;",
            ),
            Div(
                Button(
                    "Export Configuration",
                    type="button",
                    cls="btn-secondary",
                    onclick="exportConfiguration()",
                ),
                Button("Import Configuration", type="button", cls="btn-secondary"),
                Button(
                    "Reset All Settings",
                    type="button",
                    cls="btn-danger",
                    onclick="confirmResetAll()",
                ),
                Button("Save Advanced Settings", type="submit", cls="btn-primary"),
                cls="action-buttons",
            ),
            cls="config-form",
        ),
        cls="config-section fade-in",
    )


# JavaScript for interactive functionality
def admin_analytics_scripts():
    """JavaScript for admin analytics configuration"""
    return Script("""
        function resetAlgorithmDefaults() {
            const defaults = {
                initial_ease_factor: 2.5,
                minimum_ease_factor: 1.3,
                maximum_ease_factor: 3.0,
                ease_factor_change: 0.15,
                initial_interval_days: 1,
                graduation_interval_days: 4,
                easy_interval_days: 7,
                maximum_interval_days: 365
            };

            for (const [key, value] of Object.entries(defaults)) {
                const input = document.querySelector(`input[name="${key}"]`);
                if (input) input.value = value;
            }
        }

        function confirmResetAll() {
            if (confirm('Are you sure you want to reset ALL learning analytics settings to defaults? This action cannot be undone.')) {
                // Reset all forms to defaults
                resetAlgorithmDefaults();

                // Reset gamification settings
                document.querySelector('input[name="points_per_correct"]').value = 10;
                document.querySelector('input[name="points_per_streak_day"]').value = 5;
                document.querySelector('input[name="points_per_goal_achieved"]').value = 100;
                document.querySelector('input[name="daily_goal_default"]').value = 30;

                // Reset thresholds
                document.querySelector('input[name="mastery_threshold"]').value = 0.85;
                document.querySelector('input[name="review_threshold"]').value = 0.7;
                document.querySelector('input[name="difficulty_threshold"]').value = 0.5;
                document.querySelector('input[name="retention_threshold"]').value = 0.8;

                alert('All settings have been reset to defaults. Remember to save your changes.');
            }
        }

        function exportConfiguration() {
            // This would trigger a download of current configuration
            alert('Configuration export would be implemented here');
        }

        // Form submission handling
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();

                const formData = new FormData(this);
                const action = this.action;

                // Show loading state
                const submitButton = this.querySelector('button[type="submit"]');
                const originalText = submitButton.textContent;
                submitButton.textContent = 'Saving...';
                submitButton.disabled = true;

                // Simulate API call
                setTimeout(() => {
                    submitButton.textContent = originalText;
                    submitButton.disabled = false;

                    // Show success message
                    const successMessage = document.createElement('div');
                    successMessage.className = 'message message-success';
                    successMessage.textContent = 'Configuration saved successfully!';
                    this.insertBefore(successMessage, this.firstChild);

                    // Remove message after 3 seconds
                    setTimeout(() => {
                        successMessage.remove();
                    }, 3000);
                }, 1000);
            });
        });

        // Add visual feedback for form inputs
        document.querySelectorAll('.form-input, .form-select').forEach(input => {
            input.addEventListener('change', function() {
                this.style.borderColor = '#10b981';
                setTimeout(() => {
                    this.style.borderColor = '#e5e7eb';
                }, 500);
            });
        });
    """)


def admin_learning_analytics_page_with_scripts(
    current_config: Optional[Dict] = None, system_stats: Optional[Dict] = None
):
    """Complete admin learning analytics page with scripts"""
    return Div(
        admin_learning_analytics_page(current_config, system_stats),
        admin_analytics_scripts(),
    )


# Export main functions
__all__ = [
    "admin_learning_analytics_page",
    "admin_learning_analytics_page_with_scripts",
    "admin_learning_analytics_styles",
]
