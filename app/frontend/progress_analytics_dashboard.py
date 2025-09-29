"""
Progress Analytics Dashboard UI
Task 3.1.8 - Enhanced Progress Analytics Dashboard Frontend

Advanced frontend components for progress analytics dashboard that complement
the existing Learning Analytics Dashboard with sophisticated visualizations
and insights inspired by Airlearn AI and Pingo AI.

Features:
- Real-time conversation progress tracking with confidence metrics
- Multi-skill progress visualization with detailed breakdowns
- Personalized learning path recommendations and progress
- Advanced memory retention analytics and optimization insights
- Daily goals, streaks, and achievement integration
- Performance comparison and improvement trend analysis
"""

from fasthtml.common import *
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta
import statistics


def progress_analytics_styles():
    """Enhanced CSS styles for progress analytics dashboard"""
    return Style("""
        /* Enhanced Progress Analytics Dashboard Styles */
        .progress-analytics-dashboard {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }

        .progress-container {
            max-width: 1600px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.98);
            border-radius: 24px;
            padding: 2.5rem;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(15px);
        }

        .progress-header {
            text-align: center;
            margin-bottom: 3rem;
            position: relative;
        }

        .progress-title {
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 1rem;
            position: relative;
        }

        .progress-subtitle {
            color: #64748b;
            font-size: 1.2rem;
            margin-bottom: 2rem;
            font-weight: 500;
        }

        /* Enhanced Tab Navigation */
        .analytics-tabs {
            display: flex;
            justify-content: center;
            margin-bottom: 3rem;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 16px;
            padding: 0.5rem;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        }

        .tab-button {
            padding: 1rem 2rem;
            border: none;
            background: transparent;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 0 0.25rem;
            color: #64748b;
        }

        .tab-button.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .tab-button:hover:not(.active) {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
        }

        /* Conversation Analytics Styles */
        .conversation-analytics-section {
            background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(14, 165, 233, 0.1);
        }

        .conversation-metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }

        .conversation-metric-card {
            background: linear-gradient(135deg, #ffffff, #f8fafc);
            border-radius: 16px;
            padding: 1.5rem;
            border-left: 5px solid #0ea5e9;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .conversation-metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.12);
        }

        .conversation-metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 60px;
            height: 60px;
            background: radial-gradient(circle, rgba(14, 165, 233, 0.1), transparent);
            border-radius: 50%;
        }

        .metric-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }

        .metric-icon {
            font-size: 1.8rem;
            padding: 0.5rem;
            background: linear-gradient(135deg, #0ea5e9, #0284c7);
            color: white;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
        }

        .metric-value {
            font-size: 2.5rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 0.5rem;
        }

        .metric-label {
            font-size: 0.9rem;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .confidence-distribution {
            margin-top: 1rem;
        }

        .confidence-bar {
            display: flex;
            align-items: center;
            margin-bottom: 0.5rem;
            font-size: 0.85rem;
        }

        .confidence-label {
            width: 80px;
            font-weight: 500;
            color: #64748b;
        }

        .confidence-progress {
            flex: 1;
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            margin: 0 0.5rem;
            overflow: hidden;
        }

        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #f59e0b, #eab308);
            border-radius: 3px;
            transition: width 0.3s ease;
        }

        .confidence-percentage {
            width: 40px;
            text-align: right;
            font-weight: 600;
            color: #1e293b;
        }

        /* Multi-Skill Progress Styles */
        .multi-skill-section {
            background: linear-gradient(135deg, #fef3c7, #fed7aa);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }

        .skills-radar-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-top: 1.5rem;
        }

        .skill-progress-list {
            space-y: 1rem;
        }

        .skill-progress-item {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }

        .skill-progress-item:hover {
            transform: translateX(5px);
            box-shadow: 0 6px 25px rgba(0, 0, 0, 0.1);
        }

        .skill-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }

        .skill-name {
            font-weight: 700;
            color: #92400e;
            text-transform: capitalize;
        }

        .skill-level {
            font-size: 1.1rem;
            font-weight: 700;
            color: #d97706;
        }

        .skill-progress-bar {
            width: 100%;
            height: 10px;
            background: rgba(245, 158, 11, 0.2);
            border-radius: 5px;
            overflow: hidden;
            margin-bottom: 0.5rem;
        }

        .skill-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #f59e0b, #d97706);
            border-radius: 5px;
            transition: width 0.5s ease;
            position: relative;
        }

        .skill-progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            animation: shimmer 2s infinite;
        }

        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        .skill-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: #92400e;
        }

        .skill-confidence {
            display: flex;
            align-items: center;
        }

        .confidence-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }

        .confidence-very-high { background: #10b981; }
        .confidence-high { background: #34d399; }
        .confidence-moderate { background: #fbbf24; }
        .confidence-low { background: #fb7185; }
        .confidence-very-low { background: #ef4444; }

        /* Learning Path Styles */
        .learning-path-section {
            background: linear-gradient(135deg, #f3e8ff, #e9d5ff);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(139, 92, 246, 0.2);
        }

        .path-recommendation-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 16px;
            padding: 2rem;
            margin-top: 1.5rem;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
            border: 2px solid rgba(139, 92, 246, 0.1);
            position: relative;
            overflow: hidden;
        }

        .path-recommendation-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #8b5cf6, #a78bfa);
        }

        .path-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 1.5rem;
        }

        .path-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #5b21b6;
            margin-bottom: 0.5rem;
        }

        .path-description {
            color: #7c3aed;
            font-size: 1rem;
            line-height: 1.5;
        }

        .path-meta {
            display: flex;
            flex-direction: column;
            align-items: end;
        }

        .confidence-score {
            font-size: 2rem;
            font-weight: 800;
            color: #8b5cf6;
            margin-bottom: 0.25rem;
        }

        .confidence-label-small {
            font-size: 0.8rem;
            color: #64748b;
        }

        .path-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-top: 1.5rem;
        }

        .path-goals {
            background: rgba(139, 92, 246, 0.05);
            border-radius: 12px;
            padding: 1.5rem;
        }

        .path-goals h4 {
            color: #5b21b6;
            font-weight: 700;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
        }

        .path-goals h4::before {
            content: '🎯';
            margin-right: 0.5rem;
        }

        .goals-list {
            list-style: none;
            padding: 0;
        }

        .goals-list li {
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(139, 92, 246, 0.1);
            color: #7c3aed;
        }

        .goals-list li:last-child {
            border-bottom: none;
        }

        .goals-list li::before {
            content: '✓';
            color: #10b981;
            font-weight: bold;
            margin-right: 0.5rem;
        }

        /* Memory Retention Styles */
        .memory-retention-section {
            background: linear-gradient(135deg, #ecfdf5, #d1fae5);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(34, 197, 94, 0.2);
        }

        .retention-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }

        .retention-metric {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            border: 2px solid rgba(34, 197, 94, 0.1);
            transition: all 0.3s ease;
        }

        .retention-metric:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            border-color: rgba(34, 197, 94, 0.3);
        }

        .retention-percentage {
            font-size: 3rem;
            font-weight: 800;
            color: #15803d;
            margin-bottom: 0.5rem;
        }

        .retention-label {
            font-size: 0.9rem;
            color: #166534;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .retention-trend {
            margin-top: 0.5rem;
            font-size: 0.8rem;
            color: #059669;
        }

        /* Smart Recommendations */
        .smart-recommendations-section {
            background: linear-gradient(135deg, #fef2f2, #fee2e2);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }

        .recommendations-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }

        .recommendation-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 16px;
            padding: 1.5rem;
            border-left: 5px solid #ef4444;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
        }

        .recommendation-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        }

        .recommendation-header {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }

        .recommendation-icon {
            font-size: 1.5rem;
            margin-right: 0.75rem;
            padding: 0.5rem;
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
            border-radius: 10px;
        }

        .recommendation-priority {
            font-size: 0.8rem;
            font-weight: 700;
            color: #dc2626;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .recommendation-text {
            color: #1f2937;
            line-height: 1.6;
            font-weight: 500;
        }

        .recommendation-action {
            margin-top: 1rem;
        }

        .action-button {
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }

        .action-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .progress-analytics-dashboard {
                padding: 1rem;
            }

            .progress-container {
                padding: 1.5rem;
            }

            .progress-title {
                font-size: 2.2rem;
            }

            .conversation-metrics-grid,
            .skills-radar-container,
            .retention-metrics,
            .recommendations-grid {
                grid-template-columns: 1fr;
            }

            .analytics-tabs {
                flex-wrap: wrap;
            }

            .tab-button {
                padding: 0.75rem 1.25rem;
                font-size: 0.9rem;
            }
        }

        /* Enhanced Animations */
        .fade-in-up {
            animation: fadeInUp 0.6s ease-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .slide-in-left {
            animation: slideInLeft 0.7s ease-out;
        }

        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .pulse-glow {
            animation: pulseGlow 2s ease-in-out infinite alternate;
        }

        @keyframes pulseGlow {
            from {
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
            }
            to {
                box-shadow: 0 12px 35px rgba(102, 126, 234, 0.2);
            }
        }

        /* Loading States */
        .loading-shimmer {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
        }

        .metric-loading {
            height: 120px;
            border-radius: 16px;
            margin-bottom: 1rem;
        }

        /* Enhanced Tooltips */
        .tooltip {
            position: relative;
            cursor: help;
        }

        .tooltip::before {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.8rem;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
            z-index: 1000;
        }

        .tooltip::after {
            content: '';
            position: absolute;
            bottom: 115%;
            left: 50%;
            transform: translateX(-50%);
            border: 5px solid transparent;
            border-top-color: rgba(0, 0, 0, 0.9);
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }

        .tooltip:hover::before,
        .tooltip:hover::after {
            opacity: 1;
        }
    """)


def progress_analytics_dashboard_page(
    user_data: Dict = None, analytics_data: Dict = None
):
    """Enhanced progress analytics dashboard page"""

    # Default data if none provided
    if not user_data:
        user_data = {
            "user_id": 1,
            "username": "demo_user",
            "language_code": "en",
            "language_name": "English",
        }

    if not analytics_data:
        analytics_data = {
            "conversation_analytics": get_sample_conversation_data(),
            "skill_analytics": get_sample_skill_data(),
            "learning_path": get_sample_learning_path_data(),
            "memory_retention": get_sample_memory_retention_data(),
            "recommendations": get_sample_recommendations_data(),
        }

    return Div(
        progress_analytics_styles(),
        # Dashboard Container
        Div(
            # Header Section
            Div(
                H1("🚀 Progress Analytics Dashboard", cls="progress-title fade-in-up"),
                P(
                    f"Advanced progress insights for {user_data['username']} in {user_data.get('language_name', 'English')}",
                    cls="progress-subtitle",
                ),
                P(
                    f"Real-time analytics • Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                    cls="progress-subtitle",
                    style="font-size: 1rem; color: #94a3b8; margin-bottom: 0;",
                ),
                cls="progress-header",
            ),
            # Tab Navigation
            create_analytics_tabs(),
            # Tab Content
            Div(
                # Conversation Analytics Tab
                Div(
                    create_conversation_analytics_section(
                        analytics_data.get("conversation_analytics", {})
                    ),
                    id="conversation-tab-content",
                    cls="tab-content",
                    style="display: block;",
                ),
                # Multi-Skill Progress Tab
                Div(
                    create_multi_skill_section(
                        analytics_data.get("skill_analytics", {})
                    ),
                    id="skills-tab-content",
                    cls="tab-content",
                    style="display: none;",
                ),
                # Learning Path Tab
                Div(
                    create_learning_path_section(
                        analytics_data.get("learning_path", {})
                    ),
                    id="path-tab-content",
                    cls="tab-content",
                    style="display: none;",
                ),
                # Memory & Retention Tab
                Div(
                    create_memory_retention_section(
                        analytics_data.get("memory_retention", {})
                    ),
                    id="retention-tab-content",
                    cls="tab-content",
                    style="display: none;",
                ),
                # Smart Recommendations Tab
                Div(
                    create_smart_recommendations_section(
                        analytics_data.get("recommendations", {})
                    ),
                    id="recommendations-tab-content",
                    cls="tab-content",
                    style="display: none;",
                ),
            ),
            cls="progress-container",
        ),
        # JavaScript for tab functionality
        Script("""
            function showTab(tabId) {
                // Hide all tab contents
                const contents = document.querySelectorAll('.tab-content');
                contents.forEach(content => content.style.display = 'none');

                // Remove active class from all buttons
                const buttons = document.querySelectorAll('.tab-button');
                buttons.forEach(button => button.classList.remove('active'));

                // Show selected tab content
                document.getElementById(tabId + '-tab-content').style.display = 'block';

                // Add active class to clicked button
                event.target.classList.add('active');
            }
        """),
        cls="progress-analytics-dashboard",
    )


def create_analytics_tabs():
    """Create the enhanced analytics tab navigation"""
    return Div(
        Button(
            "💬 Conversation Analytics",
            cls="tab-button active",
            onclick="showTab('conversation')",
        ),
        Button(
            "🎯 Multi-Skill Progress",
            cls="tab-button",
            onclick="showTab('skills')",
        ),
        Button(
            "🛤️ Learning Path",
            cls="tab-button",
            onclick="showTab('path')",
        ),
        Button(
            "🧠 Memory & Retention",
            cls="tab-button",
            onclick="showTab('retention')",
        ),
        Button(
            "💡 Smart Recommendations",
            cls="tab-button",
            onclick="showTab('recommendations')",
        ),
        cls="analytics-tabs",
    )


def create_conversation_analytics_section(conversation_data: Dict):
    """Create the conversation analytics section"""
    return Div(
        Div(
            Span("💬", cls="section-icon"),
            "Real-Time Conversation Analytics",
            cls="section-title",
            style="color: #0ea5e9; font-size: 1.6rem; margin-bottom: 1.5rem; display: flex; align-items: center;",
        ),
        # Conversation Performance Overview
        Div(
            create_conversation_metrics_grid(conversation_data),
            cls="conversation-metrics-grid",
        ),
        # Confidence Distribution Analysis
        create_confidence_analysis(conversation_data.get("performance_metrics", {})),
        # Recent Session Highlights
        create_recent_sessions_highlights(conversation_data.get("recent_sessions", [])),
        cls="conversation-analytics-section slide-in-left",
    )


def create_conversation_metrics_grid(conversation_data: Dict):
    """Create the conversation metrics grid"""
    overview = conversation_data.get("overview", {})
    performance = conversation_data.get("performance_metrics", {})
    learning = conversation_data.get("learning_progress", {})
    engagement = conversation_data.get("engagement_analysis", {})

    return [
        # Total Conversations
        Div(
            Div(
                Span("🗨️", cls="metric-icon"),
                Div(
                    "High Priority",
                    style="font-size: 0.7rem; color: #0ea5e9; font-weight: 600;",
                ),
                cls="metric-header",
            ),
            Div(f"{overview.get('total_conversations', 0):,}", cls="metric-value"),
            Div("Total Conversations", cls="metric-label"),
            Div(
                f"Avg: {overview.get('average_exchanges_per_session', 0):.1f} exchanges",
                style="color: #64748b; font-size: 0.8rem; margin-top: 0.5rem;",
            ),
            cls="conversation-metric-card fade-in-up pulse-glow",
        ),
        # Fluency Score
        Div(
            Div(
                Span("🎵", cls="metric-icon"),
                Div(
                    "Performance",
                    style="font-size: 0.7rem; color: #0ea5e9; font-weight: 600;",
                ),
                cls="metric-header",
            ),
            Div(
                f"{performance.get('average_fluency_score', 0) * 100:.1f}%",
                cls="metric-value",
            ),
            Div("Fluency Score", cls="metric-label"),
            Div(
                "↗️ Improving steadily",
                style="color: #10b981; font-size: 0.8rem; margin-top: 0.5rem; font-weight: 600;",
            ),
            cls="conversation-metric-card fade-in-up",
        ),
        # Grammar Accuracy
        Div(
            Div(
                Span("📝", cls="metric-icon"),
                Div(
                    "Accuracy",
                    style="font-size: 0.7rem; color: #0ea5e9; font-weight: 600;",
                ),
                cls="metric-header",
            ),
            Div(
                f"{performance.get('average_grammar_accuracy', 0) * 100:.1f}%",
                cls="metric-value",
            ),
            Div("Grammar Accuracy", cls="metric-label"),
            Div(
                "Need focus area",
                style="color: #f59e0b; font-size: 0.8rem; margin-top: 0.5rem; font-weight: 600;",
            ),
            cls="conversation-metric-card fade-in-up",
        ),
        # Confidence Level
        Div(
            Div(
                Span("💪", cls="metric-icon"),
                Div(
                    "Confidence",
                    style="font-size: 0.7rem; color: #0ea5e9; font-weight: 600;",
                ),
                cls="metric-header",
            ),
            Div(
                f"{performance.get('average_confidence_level', 0) * 100:.0f}%",
                cls="metric-value",
            ),
            Div("Confidence Level", cls="metric-label"),
            Div(
                "Building momentum",
                style="color: #8b5cf6; font-size: 0.8rem; margin-top: 0.5rem; font-weight: 600;",
            ),
            cls="conversation-metric-card fade-in-up",
        ),
        # Learning Progress
        Div(
            Div(
                Span("📚", cls="metric-icon"),
                Div(
                    "Learning",
                    style="font-size: 0.7rem; color: #0ea5e9; font-weight: 600;",
                ),
                cls="metric-header",
            ),
            Div(f"{learning.get('total_new_vocabulary', 0):,}", cls="metric-value"),
            Div("New Vocabulary", cls="metric-label"),
            Div(
                f"{learning.get('total_grammar_patterns', 0)} grammar patterns",
                style="color: #64748b; font-size: 0.8rem; margin-top: 0.5rem;",
            ),
            cls="conversation-metric-card fade-in-up",
        ),
        # Engagement Score
        Div(
            Div(
                Span("⚡", cls="metric-icon"),
                Div(
                    "Engagement",
                    style="font-size: 0.7rem; color: #0ea5e9; font-weight: 600;",
                ),
                cls="metric-header",
            ),
            Div(
                f"{engagement.get('average_engagement_score', 0) * 100:.0f}%",
                cls="metric-value",
            ),
            Div("Engagement Score", cls="metric-label"),
            Div(
                f"Hesitation rate: {engagement.get('hesitation_rate', 0) * 100:.1f}%",
                style="color: #64748b; font-size: 0.8rem; margin-top: 0.5rem;",
            ),
            cls="conversation-metric-card fade-in-up",
        ),
    ]


def create_confidence_analysis(performance_data: Dict):
    """Create confidence distribution analysis"""
    # Sample confidence distribution data
    confidence_dist = {
        "Very High": 25,
        "High": 35,
        "Moderate": 30,
        "Low": 8,
        "Very Low": 2,
    }

    total = sum(confidence_dist.values())

    return Div(
        H3(
            "🎯 Confidence Distribution Analysis",
            style="color: #0ea5e9; margin: 2rem 0 1rem 0; font-size: 1.3rem;",
        ),
        Div(
            *[
                Div(
                    Span(level, cls="confidence-label"),
                    Div(
                        Div(
                            cls="confidence-fill",
                            style=f"width: {(count / total * 100):.1f}%",
                        ),
                        cls="confidence-progress",
                    ),
                    Span(f"{(count / total * 100):.1f}%", cls="confidence-percentage"),
                    cls="confidence-bar",
                )
                for level, count in confidence_dist.items()
            ],
            cls="confidence-distribution",
        ),
        style="margin-top: 2rem; background: rgba(255, 255, 255, 0.6); padding: 1.5rem; border-radius: 16px;",
    )


def create_recent_sessions_highlights(recent_sessions: List[Dict]):
    """Create recent session highlights"""
    if not recent_sessions:
        recent_sessions = [
            {
                "session_id": "conv_001",
                "conversation_type": "Restaurant Scenario",
                "fluency_score": 0.78,
                "started_at": "2025-09-29T10:30:00",
                "duration_minutes": 12.5,
                "improvement_from_last_session": 0.15,
            },
            {
                "session_id": "conv_002",
                "conversation_type": "Travel Planning",
                "fluency_score": 0.82,
                "started_at": "2025-09-28T15:45:00",
                "duration_minutes": 8.3,
                "improvement_from_last_session": 0.08,
            },
        ]

    return Div(
        H3(
            "🌟 Recent Session Highlights",
            style="color: #0ea5e9; margin: 2rem 0 1rem 0; font-size: 1.3rem;",
        ),
        Div(
            *[
                Div(
                    Div(
                        Div(
                            Strong(session["conversation_type"]),
                            Div(
                                f"Fluency: {session['fluency_score'] * 100:.0f}% • Duration: {session['duration_minutes']:.1f}min",
                                style="color: #64748b; font-size: 0.9rem; margin-top: 0.25rem;",
                            ),
                        ),
                        Div(
                            f"↗️ +{session['improvement_from_last_session'] * 100:.1f}%"
                            if session["improvement_from_last_session"] > 0
                            else "→ Stable",
                            style=f"color: {'#10b981' if session['improvement_from_last_session'] > 0 else '#64748b'}; font-weight: 600; font-size: 0.9rem;",
                        ),
                        style="display: flex; justify-content: space-between; align-items: start;",
                    ),
                    style="background: rgba(255, 255, 255, 0.7); padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem; border-left: 4px solid #0ea5e9;",
                )
                for session in recent_sessions[:3]
            ]
        ),
        style="margin-top: 2rem;",
    )


def create_multi_skill_section(skill_data: Dict):
    """Create the multi-skill progress section"""
    return Div(
        Div(
            Span("🎯", cls="section-icon"),
            "Multi-Skill Progress Visualization",
            cls="section-title",
            style="color: #d97706; font-size: 1.6rem; margin-bottom: 1.5rem; display: flex; align-items: center;",
        ),
        # Skill Overview Stats
        create_skill_overview(skill_data.get("skill_overview", {})),
        # Individual Skill Progress
        create_skill_progress_list(skill_data.get("individual_skills", [])),
        cls="multi-skill-section slide-in-left",
    )


def create_skill_overview(skill_overview: Dict):
    """Create skill overview statistics"""
    return Div(
        Div(
            Div(
                Div(
                    f"{skill_overview.get('total_skills_tracked', 0)}",
                    style="font-size: 2.5rem; font-weight: 800; color: #d97706;",
                ),
                Div(
                    "Skills Tracked",
                    style="color: #92400e; font-weight: 600; text-transform: uppercase; font-size: 0.9rem;",
                ),
                style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.8); border-radius: 12px;",
            ),
            Div(
                Div(
                    f"{skill_overview.get('average_skill_level', 0):.1f}%",
                    style="font-size: 2.5rem; font-weight: 800; color: #d97706;",
                ),
                Div(
                    "Average Level",
                    style="color: #92400e; font-weight: 600; text-transform: uppercase; font-size: 0.9rem;",
                ),
                style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.8); border-radius: 12px;",
            ),
            Div(
                Div(
                    f"{skill_overview.get('overall_mastery_percentage', 0):.1f}%",
                    style="font-size: 2.5rem; font-weight: 800; color: #d97706;",
                ),
                Div(
                    "Overall Mastery",
                    style="color: #92400e; font-weight: 600; text-transform: uppercase; font-size: 0.9rem;",
                ),
                style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.8); border-radius: 12px;",
            ),
            Div(
                Div(
                    skill_overview.get("strongest_skill", "Vocabulary")
                    .replace("_", " ")
                    .title()
                    if skill_overview.get("strongest_skill")
                    else "N/A",
                    style="font-size: 1.5rem; font-weight: 800; color: #d97706;",
                ),
                Div(
                    "Strongest Skill",
                    style="color: #92400e; font-weight: 600; text-transform: uppercase; font-size: 0.9rem;",
                ),
                style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.8); border-radius: 12px;",
            ),
            style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;",
        )
    )


def create_skill_progress_list(skills: List[Dict]):
    """Create individual skill progress items"""
    if not skills:
        skills = get_sample_individual_skills()

    return Div(
        *[
            Div(
                Div(
                    Span(
                        skill["skill_type"].replace("_", " ").title(), cls="skill-name"
                    ),
                    Span(f"{skill['current_level']:.1f}%", cls="skill-level"),
                    cls="skill-header",
                ),
                Div(
                    Div(
                        cls="skill-progress-fill",
                        style=f"width: {skill['current_level']}%",
                    ),
                    cls="skill-progress-bar",
                ),
                Div(
                    Span(
                        f"Mastery: {skill['mastery_percentage']:.0f}%",
                        style="font-weight: 600;",
                    ),
                    Div(
                        Span(
                            cls=f"confidence-indicator confidence-{skill['confidence_level'].replace('_', '-')}"
                        ),
                        Span(skill["confidence_level"].replace("_", " ").title()),
                        cls="skill-confidence tooltip",
                        **{
                            "data-tooltip": f"Confidence level in {skill['skill_type'].replace('_', ' ')}"
                        },
                    ),
                    cls="skill-meta",
                ),
                cls="skill-progress-item fade-in-up",
                style=f"animation-delay: {idx * 0.1}s;",
            )
            for idx, skill in enumerate(skills[:8])  # Show top 8 skills
        ],
        cls="skill-progress-list",
    )


def create_learning_path_section(learning_path_data: Dict):
    """Create the learning path section"""
    return Div(
        Div(
            Span("🛤️", cls="section-icon"),
            "Personalized Learning Path",
            cls="section-title",
            style="color: #8b5cf6; font-size: 1.6rem; margin-bottom: 1.5rem; display: flex; align-items: center;",
        ),
        create_path_recommendation_card(learning_path_data),
        cls="learning-path-section slide-in-left",
    )


def create_path_recommendation_card(path_data: Dict):
    """Create the learning path recommendation card"""
    if not path_data:
        path_data = get_sample_learning_path_data()

    return Div(
        Div(
            Div(
                Div(
                    path_data.get("path_title", "Comprehensive Language Mastery"),
                    cls="path-title",
                ),
                Div(
                    path_data.get(
                        "path_description", "A balanced approach to language learning"
                    ),
                    cls="path-description",
                ),
            ),
            Div(
                Div(
                    f"{path_data.get('confidence_score', 0.85) * 100:.0f}%",
                    cls="confidence-score",
                ),
                Div("Confidence", cls="confidence-label-small"),
                cls="path-meta",
            ),
            cls="path-header",
        ),
        Div(
            # Goals Column
            Div(
                Div(
                    H4("Learning Goals"),
                    Ul(
                        *[
                            Li(goal)
                            for goal in path_data.get(
                                "primary_goals",
                                [
                                    "Improve conversation fluency",
                                    "Master essential grammar",
                                    "Build vocabulary systematically",
                                    "Develop pronunciation clarity",
                                ],
                            )
                        ],
                        cls="goals-list",
                    ),
                    cls="path-goals",
                )
            ),
            # Progress Column
            Div(
                Div(
                    H4(
                        "📊 Progress Metrics",
                        style="color: #8b5cf6; margin-bottom: 1rem;",
                    ),
                    Div(
                        Div(
                            f"{path_data.get('estimated_duration_weeks', 12)} weeks",
                            style="font-size: 1.2rem; font-weight: 700; color: #8b5cf6;",
                        ),
                        Div("Duration", style="color: #64748b; font-size: 0.9rem;"),
                        style="margin-bottom: 1rem;",
                    ),
                    Div(
                        Div(
                            f"{path_data.get('expected_success_rate', 0.78) * 100:.0f}%",
                            style="font-size: 1.2rem; font-weight: 700; color: #8b5cf6;",
                        ),
                        Div("Success Rate", style="color: #64748b; font-size: 0.9rem;"),
                        style="margin-bottom: 1rem;",
                    ),
                    Div(
                        Div(
                            f"{path_data.get('time_commitment_hours_per_week', 5)} hrs/week",
                            style="font-size: 1.2rem; font-weight: 700; color: #8b5cf6;",
                        ),
                        Div(
                            "Time Commitment",
                            style="color: #64748b; font-size: 0.9rem;",
                        ),
                    ),
                    style="background: rgba(139, 92, 246, 0.05); border-radius: 12px; padding: 1.5rem;",
                )
            ),
            cls="path-details",
        ),
        cls="path-recommendation-card fade-in-up pulse-glow",
    )


def create_memory_retention_section(retention_data: Dict):
    """Create the memory retention section"""
    return Div(
        Div(
            Span("🧠", cls="section-icon"),
            "Advanced Memory & Retention Analytics",
            cls="section-title",
            style="color: #15803d; font-size: 1.6rem; margin-bottom: 1.5rem; display: flex; align-items: center;",
        ),
        create_retention_metrics(retention_data),
        cls="memory-retention-section slide-in-left",
    )


def create_retention_metrics(retention_data: Dict):
    """Create retention metrics display"""
    if not retention_data:
        retention_data = get_sample_memory_retention_data()

    return Div(
        Div(
            Div(
                Div(
                    f"{retention_data.get('short_term_retention_rate', 0.82) * 100:.0f}%",
                    cls="retention-percentage",
                ),
                Div("Short-Term", cls="retention-label"),
                Div("1-7 days", cls="retention-trend"),
                cls="retention-metric fade-in-up",
                style="animation-delay: 0.1s;",
            ),
            Div(
                Div(
                    f"{retention_data.get('medium_term_retention_rate', 0.67) * 100:.0f}%",
                    cls="retention-percentage",
                ),
                Div("Medium-Term", cls="retention-label"),
                Div("1-4 weeks", cls="retention-trend"),
                cls="retention-metric fade-in-up",
                style="animation-delay: 0.2s;",
            ),
            Div(
                Div(
                    f"{retention_data.get('long_term_retention_rate', 0.54) * 100:.0f}%",
                    cls="retention-percentage",
                ),
                Div("Long-Term", cls="retention-label"),
                Div("1+ months", cls="retention-trend"),
                cls="retention-metric fade-in-up",
                style="animation-delay: 0.3s;",
            ),
            Div(
                Div(
                    f"{retention_data.get('active_recall_success_rate', 0.73) * 100:.0f}%",
                    cls="retention-percentage",
                ),
                Div("Active Recall", cls="retention-label"),
                Div("↗️ Improving", cls="retention-trend", style="color: #10b981;"),
                cls="retention-metric fade-in-up",
                style="animation-delay: 0.4s;",
            ),
            cls="retention-metrics",
        ),
        # Learning Efficiency Insights
        Div(
            H3(
                "⚡ Learning Efficiency Insights",
                style="color: #15803d; margin: 2rem 0 1rem 0; font-size: 1.3rem;",
            ),
            Div(
                Div(
                    f"Average exposures to master: {retention_data.get('average_exposures_to_master', 5.2):.1f}",
                    style="background: rgba(255, 255, 255, 0.8); padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem; border-left: 4px solid #15803d;",
                ),
                Div(
                    f"Learning velocity: {retention_data.get('learning_velocity', 12.3):.1f} items/hour",
                    style="background: rgba(255, 255, 255, 0.8); padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem; border-left: 4px solid #15803d;",
                ),
                Div(
                    f"Most retained: {', '.join(retention_data.get('most_retained_item_types', ['vocabulary', 'phrases']))}",
                    style="background: rgba(255, 255, 255, 0.8); padding: 1rem; border-radius: 12px; border-left: 4px solid #15803d;",
                ),
            ),
        ),
    )


def create_smart_recommendations_section(recommendations_data: Dict):
    """Create the smart recommendations section"""
    return Div(
        Div(
            Span("💡", cls="section-icon"),
            "AI-Powered Smart Recommendations",
            cls="section-title",
            style="color: #dc2626; font-size: 1.6rem; margin-bottom: 1.5rem; display: flex; align-items: center;",
        ),
        create_recommendations_grid(recommendations_data),
        cls="smart-recommendations-section slide-in-left",
    )


def create_recommendations_grid(recommendations_data: Dict):
    """Create the recommendations grid"""
    if not recommendations_data:
        recommendations_data = get_sample_recommendations_data()

    recommendations = recommendations_data.get("recommendations", [])

    return Div(
        *[
            Div(
                Div(
                    Span(rec["icon"], cls="recommendation-icon"),
                    Div(rec["priority"], cls="recommendation-priority"),
                    cls="recommendation-header",
                ),
                Div(rec["text"], cls="recommendation-text"),
                Div(
                    Button(rec["action"], cls="action-button"),
                    cls="recommendation-action",
                )
                if rec.get("action")
                else None,
                cls="recommendation-card fade-in-up",
                style=f"animation-delay: {idx * 0.1}s;",
            )
            for idx, rec in enumerate(recommendations)
        ],
        cls="recommendations-grid",
    )


# ============= SAMPLE DATA FUNCTIONS =============


def get_sample_conversation_data():
    """Get sample conversation analytics data"""
    return {
        "overview": {
            "total_conversations": 47,
            "total_conversation_time": 385.5,
            "average_session_length": 8.2,
            "total_exchanges": 1247,
            "average_exchanges_per_session": 26.5,
        },
        "performance_metrics": {
            "average_fluency_score": 0.78,
            "average_grammar_accuracy": 0.72,
            "average_pronunciation_clarity": 0.81,
            "average_vocabulary_complexity": 0.68,
            "average_confidence_level": 0.74,
        },
        "learning_progress": {
            "total_new_vocabulary": 156,
            "total_grammar_patterns": 23,
            "total_cultural_contexts": 18,
            "average_improvement_trend": 0.12,
        },
        "engagement_analysis": {
            "average_engagement_score": 0.83,
            "total_hesitations": 134,
            "total_self_corrections": 67,
            "hesitation_rate": 0.11,
        },
    }


def get_sample_skill_data():
    """Get sample skill analytics data"""
    return {
        "skill_overview": {
            "total_skills_tracked": 8,
            "average_skill_level": 67.3,
            "overall_mastery_percentage": 72.1,
            "strongest_skill": "vocabulary",
            "weakest_skill": "pronunciation",
        },
        "individual_skills": get_sample_individual_skills(),
    }


def get_sample_individual_skills():
    """Get sample individual skills data"""
    return [
        {
            "skill_type": "vocabulary",
            "current_level": 82.3,
            "mastery_percentage": 78,
            "confidence_level": "high",
        },
        {
            "skill_type": "grammar",
            "current_level": 71.8,
            "mastery_percentage": 69,
            "confidence_level": "moderate",
        },
        {
            "skill_type": "listening",
            "current_level": 76.2,
            "mastery_percentage": 73,
            "confidence_level": "high",
        },
        {
            "skill_type": "speaking",
            "current_level": 68.9,
            "mastery_percentage": 64,
            "confidence_level": "moderate",
        },
        {
            "skill_type": "pronunciation",
            "current_level": 59.4,
            "mastery_percentage": 56,
            "confidence_level": "low",
        },
        {
            "skill_type": "conversation",
            "current_level": 74.1,
            "mastery_percentage": 71,
            "confidence_level": "high",
        },
        {
            "skill_type": "comprehension",
            "current_level": 79.6,
            "mastery_percentage": 76,
            "confidence_level": "high",
        },
        {
            "skill_type": "writing",
            "current_level": 65.7,
            "mastery_percentage": 62,
            "confidence_level": "moderate",
        },
    ]


def get_sample_learning_path_data():
    """Get sample learning path data"""
    return {
        "path_title": "Comprehensive Language Mastery Path",
        "path_description": "A balanced approach focusing on conversation skills while strengthening grammar foundations",
        "confidence_score": 0.85,
        "expected_success_rate": 0.78,
        "estimated_duration_weeks": 12,
        "time_commitment_hours_per_week": 5.5,
        "primary_goals": [
            "Improve conversation fluency by 25%",
            "Master essential grammar patterns",
            "Build core vocabulary (500+ words)",
            "Develop pronunciation clarity",
            "Gain cultural context awareness",
        ],
    }


def get_sample_memory_retention_data():
    """Get sample memory retention data"""
    return {
        "short_term_retention_rate": 0.82,
        "medium_term_retention_rate": 0.67,
        "long_term_retention_rate": 0.54,
        "active_recall_success_rate": 0.73,
        "average_exposures_to_master": 5.2,
        "learning_velocity": 12.3,
        "most_retained_item_types": ["vocabulary", "phrases"],
        "least_retained_item_types": ["grammar", "pronunciation"],
    }


def get_sample_recommendations_data():
    """Get sample recommendations data"""
    return {
        "recommendations": [
            {
                "icon": "🎯",
                "priority": "High Priority",
                "text": "Focus on pronunciation practice - your clarity score could improve with 15 minutes of daily phonetic exercises",
                "action": "Start Pronunciation Course",
            },
            {
                "icon": "📚",
                "priority": "Medium Priority",
                "text": "Grammar accuracy needs attention. Review conditional sentences and subjunctive mood patterns",
                "action": "Review Grammar",
            },
            {
                "icon": "🗣️",
                "priority": "High Priority",
                "text": "Practice speaking in more challenging scenarios to build confidence in complex conversations",
                "action": "Try Advanced Scenarios",
            },
            {
                "icon": "🧠",
                "priority": "Medium Priority",
                "text": "Your retention drops after 2 weeks. Increase review frequency for better long-term memory",
                "action": "Optimize Schedule",
            },
            {
                "icon": "⚡",
                "priority": "Low Priority",
                "text": "Great progress in vocabulary! Consider learning specialized terms for your interests",
                "action": "Expand Vocabulary",
            },
            {
                "icon": "🎵",
                "priority": "Medium Priority",
                "text": "Work on speech rhythm and intonation patterns to sound more natural in conversations",
                "action": "Practice Rhythm",
            },
        ]
    }


# Export main function
__all__ = ["progress_analytics_dashboard_page", "progress_analytics_styles"]
