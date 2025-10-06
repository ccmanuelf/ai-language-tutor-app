"""
Admin AI Model Management Interface
AI Language Tutor App - Task 3.1.5

Modern, responsive admin interface for managing AI models and providers:
- Model configuration dashboard
- Provider health monitoring
- Performance analytics and reports
- Cost optimization controls
- Real-time usage statistics
- Model comparison tools
- Health monitoring alerts
- Advanced filtering and search

Follows YouLearn design patterns with modern responsive layout.
"""

from fasthtml import *
from fasthtml.common import *
from typing import Dict, List, Any

from app.frontend.layout import create_admin_sidebar, create_admin_header


def create_ai_models_page():
    """Create the main AI models management page"""

    # Page styles
    styles = Style("""
        .ai-models-container {
            display: flex;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .ai-models-content {
            flex: 1;
            padding: 2rem;
            margin-left: 280px;
            background: rgba(255, 255, 255, 0.95);
            min-height: 100vh;
        }

        .models-header {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
            border: 1px solid rgba(102, 126, 234, 0.1);
        }

        .models-title {
            color: #2d3748;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .models-subtitle {
            color: #666;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(102, 126, 234, 0.1);
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .models-controls {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            margin-bottom: 2rem;
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: center;
            justify-content: space-between;
        }

        .filter-group {
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .filter-select {
            padding: 0.75rem 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            background: white;
            color: #2d3748;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }

        .filter-select:focus {
            border-color: #667eea;
            outline: none;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .search-input {
            padding: 0.75rem 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            background: white;
            color: #2d3748;
            font-size: 0.9rem;
            width: 300px;
            transition: all 0.3s ease;
        }

        .search-input:focus {
            border-color: #667eea;
            outline: none;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .action-buttons {
            display: flex;
            gap: 0.75rem;
        }

        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        }

        .btn-secondary {
            background: #f7fafc;
            color: #4a5568;
            border: 2px solid #e2e8f0;
        }

        .btn-secondary:hover {
            background: #edf2f7;
            border-color: #cbd5e0;
        }

        .models-grid {
            display: grid;
            gap: 1.5rem;
        }

        .model-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            transition: all 0.3s ease;
            border: 1px solid rgba(102, 126, 234, 0.1);
        }

        .model-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(102, 126, 234, 0.15);
        }

        .model-header {
            padding: 1.5rem;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }

        .model-info {
            flex: 1;
        }

        .model-name {
            font-size: 1.25rem;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 0.25rem;
        }

        .model-provider {
            color: #667eea;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .model-status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .status-active {
            background: #c6f6d5;
            color: #2f855a;
        }

        .status-inactive {
            background: #fed7d7;
            color: #c53030;
        }

        .status-maintenance {
            background: #feebc8;
            color: #dd6b20;
        }

        .model-body {
            padding: 1.5rem;
        }

        .model-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .metric {
            text-align: center;
        }

        .metric-value {
            font-size: 1.25rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 0.25rem;
        }

        .metric-label {
            color: #666;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .model-languages {
            margin-bottom: 1rem;
        }

        .languages-label {
            font-size: 0.9rem;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 0.5rem;
        }

        .language-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .language-tag {
            padding: 0.25rem 0.75rem;
            background: #edf2f7;
            color: #4a5568;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .language-tag.primary {
            background: #667eea;
            color: white;
        }

        .model-actions {
            display: flex;
            gap: 0.75rem;
            justify-content: flex-end;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid #e2e8f0;
        }

        .btn-sm {
            padding: 0.5rem 1rem;
            font-size: 0.8rem;
        }

        .btn-success {
            background: #48bb78;
            color: white;
        }

        .btn-success:hover {
            background: #38a169;
        }

        .btn-warning {
            background: #ed8936;
            color: white;
        }

        .btn-warning:hover {
            background: #dd6b20;
        }

        .btn-info {
            background: #4299e1;
            color: white;
        }

        .btn-info:hover {
            background: #3182ce;
        }

        .empty-state {
            text-align: center;
            padding: 4rem 2rem;
            color: #666;
        }

        .empty-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.3;
        }

        .empty-message {
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
        }

        .empty-submessage {
            font-size: 0.9rem;
            opacity: 0.7;
        }

        .health-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 0.5rem;
        }

        .health-healthy {
            background: #48bb78;
        }

        .health-warning {
            background: #ed8936;
        }

        .health-error {
            background: #f56565;
        }

        .performance-chart {
            background: #f7fafc;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }

        .chart-placeholder {
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            font-style: italic;
        }

        @media (max-width: 768px) {
            .ai-models-content {
                margin-left: 0;
                padding: 1rem;
            }

            .models-controls {
                flex-direction: column;
                align-items: stretch;
            }

            .filter-group {
                justify-content: space-between;
            }

            .search-input {
                width: 100%;
            }

            .action-buttons {
                justify-content: center;
            }
        }
    """)

    return Div(
        styles,
        create_admin_sidebar(active="ai_models"),
        Div(
            create_admin_header("AI Model Management"),
            # System Overview Section
            Div(
                H1("AI Model Management", cls="models-title"),
                P(
                    "Monitor, configure, and optimize AI models and providers",
                    cls="models-subtitle",
                ),
                Div(id="system-stats", cls="stats-grid"),
                cls="models-header",
            ),
            # Controls Section
            Div(
                Div(
                    Select(
                        Option("All Categories", value=""),
                        Option("Conversation", value="conversation"),
                        Option("Grammar", value="grammar"),
                        Option("Translation", value="translation"),
                        Option("Analysis", value="analysis"),
                        Option("General", value="general"),
                        name="category_filter",
                        cls="filter-select",
                        hx_get="/admin/ai-models/models",
                        hx_target="#models-list",
                        hx_trigger="change",
                    ),
                    Select(
                        Option("All Providers", value=""),
                        Option("Claude", value="claude"),
                        Option("Mistral", value="mistral"),
                        Option("DeepSeek", value="deepseek"),
                        Option("Ollama", value="ollama"),
                        name="provider_filter",
                        cls="filter-select",
                        hx_get="/admin/ai-models/models",
                        hx_target="#models-list",
                        hx_trigger="change",
                    ),
                    Select(
                        Option("All Status", value=""),
                        Option("Active", value="active"),
                        Option("Inactive", value="inactive"),
                        Option("Maintenance", value="maintenance"),
                        Option("Error", value="error"),
                        name="status_filter",
                        cls="filter-select",
                        hx_get="/admin/ai-models/models",
                        hx_target="#models-list",
                        hx_trigger="change",
                    ),
                    cls="filter-group",
                ),
                Input(
                    type="text",
                    placeholder="Search models...",
                    name="search",
                    cls="search-input",
                    hx_get="/admin/ai-models/models",
                    hx_target="#models-list",
                    hx_trigger="keyup changed delay:500ms",
                ),
                Div(
                    A(
                        "Health Check",
                        href="#",
                        cls="btn btn-secondary",
                        hx_post="/admin/ai-models/health-check",
                        hx_target="#system-stats",
                    ),
                    A(
                        "Optimize Models",
                        href="#",
                        cls="btn btn-secondary",
                        hx_get="/admin/ai-models/optimize",
                    ),
                    A(
                        "Performance Report",
                        href="#",
                        cls="btn btn-primary",
                        hx_get="/admin/ai-models/performance",
                    ),
                    cls="action-buttons",
                ),
                cls="models-controls",
            ),
            # Models List Section
            Div(id="models-list", cls="models-grid"),
            cls="ai-models-content",
        ),
        # JavaScript for interactivity
        Script("""
            // Auto-refresh health status every 30 seconds
            setInterval(function() {
                htmx.trigger('#system-stats', 'refresh');
            }, 30000);

            // Initialize page
            document.addEventListener('DOMContentLoaded', function() {
                // Load initial data
                htmx.ajax('GET', '/admin/ai-models/overview', {target: '#system-stats'});
                htmx.ajax('GET', '/admin/ai-models/models', {target: '#models-list'});
            });
        """),
        cls="ai-models-container",
    )


def create_system_overview_card(overview_data: Dict[str, Any]):
    """Create system overview statistics cards"""

    overview = overview_data.get("overview", {})
    budget = overview_data.get("budget_status", {})

    return Div(
        # System Stats
        Div(
            Div(str(overview.get("total_models", 0)), cls="stat-value"),
            Div("Total Models", cls="stat-label"),
            cls="stat-card",
        ),
        Div(
            Div(str(overview.get("active_models", 0)), cls="stat-value"),
            Div("Active Models", cls="stat-label"),
            cls="stat-card",
        ),
        Div(
            Div(f"${overview.get('total_cost', 0):.4f}", cls="stat-value"),
            Div("Total Cost", cls="stat-label"),
            cls="stat-card",
        ),
        Div(
            Div(f"${budget.get('remaining_budget', 0):.2f}", cls="stat-value"),
            Div("Budget Remaining", cls="stat-label"),
            cls="stat-card",
        ),
        Div(
            Div(str(overview.get("total_requests", 0)), cls="stat-value"),
            Div("Total Requests", cls="stat-label"),
            cls="stat-card",
        ),
        Div(
            Div(f"{budget.get('percentage_used', 0):.1f}%", cls="stat-value"),
            Div("Budget Used", cls="stat-label"),
            cls="stat-card",
        ),
    )


def create_model_card(model: Dict[str, Any]):
    """Create individual model configuration card"""

    # Status styling
    status = model.get("status", "unknown")
    status_class = {
        "active": "status-active",
        "inactive": "status-inactive",
        "maintenance": "status-maintenance",
        "error": "status-inactive",
    }.get(status, "status-inactive")

    # Usage stats
    usage = model.get("usage_stats", {})
    success_rate = usage.get("success_rate", 0) * 100

    return Div(
        # Model Header
        Div(
            Div(
                Div(model.get("display_name", "Unknown Model"), cls="model-name"),
                Div(model.get("provider", "unknown").upper(), cls="model-provider"),
                cls="model-info",
            ),
            Div(
                Span(
                    cls=f"health-indicator health-{'healthy' if model.get('enabled') else 'error'}"
                ),
                Span(status.title(), cls=f"status-badge {status_class}"),
                cls="model-status",
            ),
            cls="model-header",
        ),
        # Model Body
        Div(
            # Performance Metrics
            Div(
                Div(
                    Div(f"{model.get('quality_score', 0):.2f}", cls="metric-value"),
                    Div("Quality Score", cls="metric-label"),
                    cls="metric",
                ),
                Div(
                    Div(f"{success_rate:.1f}%", cls="metric-value"),
                    Div("Success Rate", cls="metric-label"),
                    cls="metric",
                ),
                Div(
                    Div(
                        f"${model.get('cost_per_1k_tokens', 0):.4f}", cls="metric-value"
                    ),
                    Div("Cost/1K Tokens", cls="metric-label"),
                    cls="metric",
                ),
                Div(
                    Div(
                        f"{model.get('avg_response_time_ms', 0):.0f}ms",
                        cls="metric-value",
                    ),
                    Div("Avg Response", cls="metric-label"),
                    cls="metric",
                ),
                Div(
                    Div(str(usage.get("total_requests", 0)), cls="metric-value"),
                    Div("Total Requests", cls="metric-label"),
                    cls="metric",
                ),
                Div(
                    Div(f"Priority {model.get('priority', 1)}", cls="metric-value"),
                    Div("Priority Level", cls="metric-label"),
                    cls="metric",
                ),
                cls="model-metrics",
            ),
            # Supported Languages
            Div(
                Div("Supported Languages", cls="languages-label"),
                Div(
                    *[
                        Span(
                            lang.upper(),
                            cls=f"language-tag {'primary' if lang in model.get('primary_languages', []) else ''}",
                        )
                        for lang in model.get("supported_languages", [])
                    ],
                    cls="language-tags",
                ),
                cls="model-languages",
            ),
            # Technical Specs
            Div(
                P(f"Context Window: {model.get('context_window', 0):,} tokens"),
                P(f"Max Tokens: {model.get('max_tokens', 0):,}"),
                P(f"Streaming: {'Yes' if model.get('supports_streaming') else 'No'}"),
                P(f"Functions: {'Yes' if model.get('supports_functions') else 'No'}"),
                style="font-size: 0.8rem; color: #666; margin: 1rem 0;",
            ),
            # Action Buttons
            Div(
                Button(
                    "Configure",
                    cls="btn btn-info btn-sm",
                    hx_get=f"/admin/ai-models/configure/{model.get('id')}",
                    hx_target="#modal-content",
                ),
                Button(
                    "Performance",
                    cls="btn btn-secondary btn-sm",
                    hx_get=f"/admin/ai-models/performance/{model.get('id')}",
                    hx_target="#modal-content",
                ),
                Button(
                    "Enable" if not model.get("enabled") else "Disable",
                    cls=f"btn {'btn-success' if not model.get('enabled') else 'btn-warning'} btn-sm",
                    hx_post=f"/admin/ai-models/toggle/{model.get('id')}",
                    hx_target="#models-list",
                    hx_confirm="Are you sure?",
                ),
                cls="model-actions",
            ),
            cls="model-body",
        ),
        cls="model-card",
    )


def create_model_list(models: List[Dict[str, Any]]):
    """Create the models list display"""

    if not models:
        return Div(
            Div("🤖", cls="empty-icon"),
            Div("No AI models found", cls="empty-message"),
            Div(
                "Try adjusting your filters or check system configuration",
                cls="empty-submessage",
            ),
            cls="empty-state",
        )

    return Div(*[create_model_card(model) for model in models], cls="models-grid")


def create_model_configuration_modal(model: Dict[str, Any]):
    """Create model configuration modal"""

    return Div(
        H3(f"Configure {model.get('display_name')}", style="margin-bottom: 1.5rem;"),
        Form(
            # Basic Settings
            Div(
                Label(
                    "Display Name",
                    style="font-weight: 600; margin-bottom: 0.5rem; display: block;",
                ),
                Input(
                    type="text",
                    name="display_name",
                    value=model.get("display_name", ""),
                    style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 6px;",
                ),
                style="margin-bottom: 1rem;",
            ),
            # Status
            Div(
                Label(
                    "Status",
                    style="font-weight: 600; margin-bottom: 0.5rem; display: block;",
                ),
                Select(
                    Option(
                        "Active",
                        value="active",
                        selected=model.get("status") == "active",
                    ),
                    Option(
                        "Inactive",
                        value="inactive",
                        selected=model.get("status") == "inactive",
                    ),
                    Option(
                        "Maintenance",
                        value="maintenance",
                        selected=model.get("status") == "maintenance",
                    ),
                    name="status",
                    style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 6px;",
                ),
                style="margin-bottom: 1rem;",
            ),
            # Priority
            Div(
                Label(
                    "Priority (1-10)",
                    style="font-weight: 600; margin-bottom: 0.5rem; display: block;",
                ),
                Input(
                    type="number",
                    name="priority",
                    value=str(model.get("priority", 1)),
                    min="1",
                    max="10",
                    style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 6px;",
                ),
                style="margin-bottom: 1rem;",
            ),
            # Weight
            Div(
                Label(
                    "Routing Weight (0.1-2.0)",
                    style="font-weight: 600; margin-bottom: 0.5rem; display: block;",
                ),
                Input(
                    type="number",
                    name="weight",
                    value=str(model.get("weight", 1.0)),
                    min="0.1",
                    max="2.0",
                    step="0.1",
                    style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 6px;",
                ),
                style="margin-bottom: 1rem;",
            ),
            # Temperature
            Div(
                Label(
                    "Temperature (0.0-2.0)",
                    style="font-weight: 600; margin-bottom: 0.5rem; display: block;",
                ),
                Input(
                    type="number",
                    name="temperature",
                    value=str(model.get("temperature", 0.7)),
                    min="0.0",
                    max="2.0",
                    step="0.1",
                    style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 6px;",
                ),
                style="margin-bottom: 1rem;",
            ),
            # Quality and Reliability Scores (admin can adjust based on observations)
            Div(
                Label(
                    "Quality Score (0.0-1.0)",
                    style="font-weight: 600; margin-bottom: 0.5rem; display: block;",
                ),
                Input(
                    type="number",
                    name="quality_score",
                    value=str(model.get("quality_score", 0.8)),
                    min="0.0",
                    max="1.0",
                    step="0.1",
                    style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 6px;",
                ),
                style="margin-bottom: 1rem;",
            ),
            Div(
                Label(
                    "Reliability Score (0.0-1.0)",
                    style="font-weight: 600; margin-bottom: 0.5rem; display: block;",
                ),
                Input(
                    type="number",
                    name="reliability_score",
                    value=str(model.get("reliability_score", 0.9)),
                    min="0.0",
                    max="1.0",
                    step="0.1",
                    style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 6px;",
                ),
                style="margin-bottom: 1.5rem;",
            ),
            # Action Buttons
            Div(
                Button(
                    "Cancel",
                    type="button",
                    cls="btn btn-secondary",
                    onclick="closeModal()",
                ),
                Button("Save Changes", type="submit", cls="btn btn-primary"),
                style="display: flex; gap: 1rem; justify-content: flex-end;",
            ),
            hx_post=f"/admin/ai-models/update/{model.get('id')}",
            hx_target="#models-list",
        ),
    )


def create_performance_report_modal(report: Dict[str, Any]):
    """Create performance report modal"""

    return Div(
        H3(
            f"Performance Report: {report.get('model_name', 'Unknown')}",
            style="margin-bottom: 1.5rem;",
        ),
        # Performance Metrics
        Div(
            H4("Performance Metrics", style="margin-bottom: 1rem; color: #667eea;"),
            Div(
                Div(
                    Div(f"{report.get('cost_efficiency', 0):.2f}", cls="metric-value"),
                    Div("Cost Efficiency", cls="metric-label"),
                    cls="metric",
                ),
                Div(
                    Div(f"{report.get('speed_efficiency', 0):.2f}", cls="metric-value"),
                    Div("Speed Efficiency", cls="metric-label"),
                    cls="metric",
                ),
                Div(
                    Div(
                        f"{report.get('reliability_score', 0):.2f}", cls="metric-value"
                    ),
                    Div("Reliability", cls="metric-label"),
                    cls="metric",
                ),
                style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2rem;",
            ),
        ),
        # Rankings
        Div(
            H4("Rankings", style="margin-bottom: 1rem; color: #667eea;"),
            Div(
                Div(
                    Div(f"#{report.get('rank_by_cost', '?')}", cls="metric-value"),
                    Div("Cost Rank", cls="metric-label"),
                    cls="metric",
                ),
                Div(
                    Div(f"#{report.get('rank_by_speed', '?')}", cls="metric-value"),
                    Div("Speed Rank", cls="metric-label"),
                    cls="metric",
                ),
                Div(
                    Div(f"#{report.get('rank_by_quality', '?')}", cls="metric-value"),
                    Div("Quality Rank", cls="metric-label"),
                    cls="metric",
                ),
                Div(
                    Div(f"#{report.get('rank_overall', '?')}", cls="metric-value"),
                    Div("Overall Rank", cls="metric-label"),
                    cls="metric",
                ),
                style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem;",
            ),
        ),
        # Recommendations
        Div(
            H4("Recommended For", style="margin-bottom: 1rem; color: #667eea;"),
            Div(
                *[
                    Span(rec.replace("_", " ").title(), cls="language-tag")
                    for rec in report.get("recommended_for", [])
                ],
                style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 2rem;",
            ),
        ),
        # Optimization Suggestions
        Div(
            H4(
                "Optimization Suggestions", style="margin-bottom: 1rem; color: #667eea;"
            ),
            Ul(
                *[
                    Li(suggestion, style="margin-bottom: 0.5rem;")
                    for suggestion in report.get("optimization_suggestions", [])
                ],
                style="margin-bottom: 2rem;",
            ),
        ),
        # Performance Chart Placeholder
        Div(
            H4("Performance Trend", style="margin-bottom: 1rem; color: #667eea;"),
            Div(
                "📊 Performance charts would be displayed here", cls="chart-placeholder"
            ),
            cls="performance-chart",
        ),
        # Close Button
        Div(
            Button(
                "Close", type="button", cls="btn btn-primary", onclick="closeModal()"
            ),
            style="text-align: center; margin-top: 2rem;",
        ),
    )
