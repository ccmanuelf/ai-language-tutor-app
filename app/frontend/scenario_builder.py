"""
Scenario Builder Interface
AI Language Tutor App - Session 131

User-facing interface for creating, editing, and managing custom scenarios.
Enables users to build scenarios from scratch or use templates.

Features:
- Template selection grid (10 templates)
- Create from scratch form
- My scenarios management (CRUD)
- Public scenarios browser
- Dynamic phase management
"""

from fasthtml.common import *

from app.models.simple_user import SimpleUser


def scenario_builder_styles():
    """CSS styles for scenario builder interface"""
    return Style("""
        .builder-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .builder-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 12px;
            color: white;
            margin-bottom: 30px;
        }

        .builder-header h1 {
            margin: 0 0 10px 0;
            font-size: 2.5rem;
        }

        .builder-header p {
            margin: 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }

        .builder-tabs {
            display: flex;
            background: white;
            border-radius: 12px;
            margin-bottom: 30px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .builder-tab {
            flex: 1;
            padding: 18px 24px;
            background: #f8fafc;
            border: none;
            cursor: pointer;
            font-weight: 600;
            color: #64748b;
            transition: all 0.3s;
            text-align: center;
            font-size: 1rem;
        }

        .builder-tab.active {
            background: #667eea;
            color: white;
        }

        .builder-tab:hover:not(.active) {
            background: #e2e8f0;
        }

        .template-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .template-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: all 0.3s;
            cursor: pointer;
            border: 2px solid transparent;
        }

        .template-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            border-color: #667eea;
        }

        .template-card h3 {
            margin: 0 0 8px 0;
            color: #1e293b;
            font-size: 1.3rem;
        }

        .template-card p {
            color: #64748b;
            margin: 0 0 16px 0;
            line-height: 1.6;
        }

        .template-meta {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }

        .template-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }

        .badge-beginner { background: #dcfce7; color: #16a34a; }
        .badge-intermediate { background: #fef3c7; color: #d97706; }
        .badge-advanced { background: #fee2e2; color: #dc2626; }
        .badge-category { background: #ddd6fe; color: #7c3aed; }

        .form-container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .form-group {
            margin-bottom: 24px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #1e293b;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .form-group textarea {
            min-height: 100px;
            resize: vertical;
        }

        .phase-section {
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }

        .phase-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .phase-header h4 {
            margin: 0;
            color: #1e293b;
        }

        .btn {
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 1rem;
        }

        .btn-primary {
            background: #667eea;
            color: white;
        }

        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .btn-secondary {
            background: #64748b;
            color: white;
        }

        .btn-secondary:hover {
            background: #475569;
        }

        .btn-danger {
            background: #dc2626;
            color: white;
        }

        .btn-danger:hover {
            background: #b91c1c;
        }

        .btn-success {
            background: #16a34a;
            color: white;
        }

        .btn-outline {
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }

        .btn-outline:hover {
            background: #667eea;
            color: white;
        }

        .scenario-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }

        .scenario-item {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }

        .scenario-item:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }

        .scenario-item h3 {
            margin: 0 0 12px 0;
            color: #1e293b;
        }

        .scenario-actions {
            display: flex;
            gap: 10px;
            margin-top: 16px;
            flex-wrap: wrap;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 12px;
            max-width: 800px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }

        .modal-header h2 {
            margin: 0;
        }

        .close-modal {
            font-size: 2rem;
            cursor: pointer;
            color: #64748b;
            background: none;
            border: none;
            padding: 0;
            line-height: 1;
        }

        .close-modal:hover {
            color: #1e293b;
        }

        .array-input-group {
            margin-bottom: 16px;
        }

        .array-input-item {
            display: flex;
            gap: 10px;
            margin-bottom: 8px;
        }

        .array-input-item input {
            flex: 1;
        }

        .help-text {
            font-size: 0.875rem;
            color: #64748b;
            margin-top: 4px;
        }

        .error-message {
            background: #fee2e2;
            color: #dc2626;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 16px;
        }

        .success-message {
            background: #dcfce7;
            color: #16a34a;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 16px;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #64748b;
        }

        .empty-state h3 {
            margin: 0 0 12px 0;
            color: #1e293b;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #64748b;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        @media (max-width: 768px) {
            .template-grid,
            .scenario-list {
                grid-template-columns: 1fr;
            }

            .builder-tabs {
                flex-direction: column;
            }
        }
    """)


def scenario_builder_scripts():
    """JavaScript for dynamic scenario builder functionality"""
    return Script("""
        // Tab switching
        function switchTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(el => {
                el.classList.remove('active');
            });

            // Remove active class from all tabs
            document.querySelectorAll('.builder-tab').forEach(el => {
                el.classList.remove('active');
            });

            // Show selected tab content
            document.getElementById(tabName + '-tab').classList.add('active');
            document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        }

        // Phase management
        let phaseCount = 2;

        function addPhase() {
            phaseCount++;
            if (phaseCount > 6) {
                alert('Maximum 6 phases allowed');
                phaseCount = 6;
                return;
            }

            const phasesContainer = document.getElementById('phases-container');
            const phaseDiv = document.createElement('div');
            phaseDiv.className = 'phase-section';
            phaseDiv.id = `phase-${phaseCount}`;

            phaseDiv.innerHTML = `
                <div class="phase-header">
                    <h4>Phase ${phaseCount}</h4>
                    <button type="button" class="btn btn-danger" onclick="removePhase(${phaseCount})">Remove</button>
                </div>
                <div class="form-group">
                    <label>Phase Name</label>
                    <input type="text" name="phase_name_${phaseCount}" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="phase_description_${phaseCount}" required></textarea>
                </div>
                <div class="form-group">
                    <label>Expected Duration (minutes)</label>
                    <input type="number" name="phase_duration_${phaseCount}" min="1" max="30" value="5" required>
                </div>
                <div class="form-group">
                    <label>Key Vocabulary (comma-separated, min 3)</label>
                    <input type="text" name="phase_vocabulary_${phaseCount}" placeholder="word1, word2, word3" required>
                </div>
                <div class="form-group">
                    <label>Essential Phrases (comma-separated, min 3)</label>
                    <input type="text" name="phase_phrases_${phaseCount}" placeholder="phrase1, phrase2, phrase3" required>
                </div>
                <div class="form-group">
                    <label>Learning Objectives (comma-separated, min 1)</label>
                    <input type="text" name="phase_objectives_${phaseCount}" required>
                </div>
                <div class="form-group">
                    <label>Success Criteria (comma-separated, min 1)</label>
                    <input type="text" name="phase_criteria_${phaseCount}" required>
                </div>
                <div class="form-group">
                    <label>Cultural Notes (optional)</label>
                    <textarea name="phase_cultural_${phaseCount}"></textarea>
                </div>
            `;

            phasesContainer.appendChild(phaseDiv);
        }

        function removePhase(phaseNum) {
            if (phaseCount <= 2) {
                alert('Minimum 2 phases required');
                return;
            }

            const phaseDiv = document.getElementById(`phase-${phaseNum}`);
            if (phaseDiv) {
                phaseDiv.remove();
                phaseCount--;
                // Renumber remaining phases
                renumberPhases();
            }
        }

        function renumberPhases() {
            const phases = document.querySelectorAll('.phase-section');
            phases.forEach((phase, index) => {
                const num = index + 1;
                phase.querySelector('h4').textContent = `Phase ${num}`;
            });
            phaseCount = phases.length;
        }

        // Template selection
        async function selectTemplate(templateId) {
            try {
                const response = await fetch(`/api/v1/scenario-builder/templates`);
                const data = await response.json();
                const template = data.templates.find(t => t.template_id === templateId);

                if (template) {
                    // Show customization modal
                    showTemplateModal(template);
                }
            } catch (error) {
                console.error('Error loading template:', error);
                alert('Failed to load template');
            }
        }

        function showTemplateModal(template) {
            const modal = document.getElementById('template-modal');
            document.getElementById('template-title').textContent = template.title;
            document.getElementById('selected-template-id').value = template.template_id;
            document.getElementById('custom-title').value = template.title + ' (My Version)';
            modal.classList.add('active');
        }

        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('active');
        }

        // Create scenario from template
        async function createFromTemplate(event) {
            event.preventDefault();
            const formData = new FormData(event.target);

            const payload = {
                template_id: formData.get('template_id'),
                customization: {
                    title: formData.get('custom_title'),
                    description: formData.get('custom_description') || undefined,
                    difficulty: formData.get('custom_difficulty') || undefined
                }
            };

            try {
                const response = await fetch('/api/v1/scenario-builder/scenarios/from-template', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });

                const result = await response.json();

                if (response.ok) {
                    alert('Scenario created successfully!');
                    closeModal('template-modal');
                    switchTab('my-scenarios');
                    loadMyScenarios();
                } else {
                    alert('Error: ' + (result.detail || 'Failed to create scenario'));
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to create scenario');
            }
        }

        // Load my scenarios
        async function loadMyScenarios() {
            const container = document.getElementById('my-scenarios-list');
            container.innerHTML = '<div class="loading">Loading your scenarios...</div>';

            try {
                const response = await fetch('/api/v1/scenario-builder/my-scenarios');
                const data = await response.json();

                if (data.scenarios.length === 0) {
                    container.innerHTML = `
                        <div class="empty-state">
                            <h3>No scenarios yet</h3>
                            <p>Create your first scenario using a template or from scratch!</p>
                        </div>
                    `;
                } else {
                    container.innerHTML = data.scenarios.map(s => createScenarioCard(s)).join('');
                }
            } catch (error) {
                console.error('Error loading scenarios:', error);
                container.innerHTML = '<div class="error-message">Failed to load scenarios</div>';
            }
        }

        function createScenarioCard(scenario) {
            return `
                <div class="scenario-item">
                    <h3>${scenario.title}</h3>
                    <div class="template-meta">
                        <span class="template-badge badge-category">${scenario.category}</span>
                        <span class="template-badge badge-${scenario.difficulty}">${scenario.difficulty}</span>
                        <span class="template-badge">${scenario.estimated_duration} min</span>
                        <span class="template-badge">${scenario.phases.length} phases</span>
                    </div>
                    <p>${scenario.description || 'No description'}</p>
                    <div class="scenario-actions">
                        <button class="btn btn-primary" onclick="viewScenario('${scenario.scenario_id}')">View</button>
                        ${!scenario.is_system_scenario ? `
                            <button class="btn btn-secondary" onclick="editScenario('${scenario.scenario_id}')">Edit</button>
                            <button class="btn btn-outline" onclick="toggleVisibility('${scenario.scenario_id}', ${!scenario.is_public})">
                                ${scenario.is_public ? 'Make Private' : 'Make Public'}
                            </button>
                            <button class="btn btn-danger" onclick="deleteScenario('${scenario.scenario_id}')">Delete</button>
                        ` : ''}
                        <button class="btn btn-success" onclick="duplicateScenario('${scenario.scenario_id}')">Duplicate</button>
                    </div>
                </div>
            `;
        }

        async function deleteScenario(scenarioId) {
            if (!confirm('Are you sure you want to delete this scenario?')) return;

            try {
                const response = await fetch(`/api/v1/scenario-builder/scenarios/${scenarioId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    alert('Scenario deleted successfully');
                    loadMyScenarios();
                } else {
                    alert('Failed to delete scenario');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to delete scenario');
            }
        }

        async function toggleVisibility(scenarioId, makePublic) {
            try {
                const response = await fetch(`/api/v1/scenario-builder/scenarios/${scenarioId}/visibility`, {
                    method: 'PATCH',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({is_public: makePublic})
                });

                if (response.ok) {
                    alert(`Scenario is now ${makePublic ? 'public' : 'private'}`);
                    loadMyScenarios();
                } else {
                    alert('Failed to update visibility');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to update visibility');
            }
        }

        async function duplicateScenario(scenarioId) {
            const newTitle = prompt('Enter title for the duplicate:');
            if (!newTitle) return;

            try {
                const response = await fetch(`/api/v1/scenario-builder/scenarios/${scenarioId}/duplicate`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({new_title: newTitle})
                });

                if (response.ok) {
                    alert('Scenario duplicated successfully!');
                    loadMyScenarios();
                } else {
                    alert('Failed to duplicate scenario');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to duplicate scenario');
            }
        }

        // Load public scenarios
        async function loadPublicScenarios() {
            const container = document.getElementById('public-scenarios-list');
            container.innerHTML = '<div class="loading">Loading public scenarios...</div>';

            try {
                const response = await fetch('/api/v1/scenario-builder/public-scenarios');
                const data = await response.json();

                if (data.scenarios.length === 0) {
                    container.innerHTML = '<div class="empty-state"><h3>No public scenarios yet</h3></div>';
                } else {
                    container.innerHTML = data.scenarios.map(s => createScenarioCard(s)).join('');
                }
            } catch (error) {
                console.error('Error:', error);
                container.innerHTML = '<div class="error-message">Failed to load public scenarios</div>';
            }
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadMyScenarios();
        });
    """)


def create_scenario_builder_page(current_user: SimpleUser):
    """Create the main scenario builder page"""

    return Div(
        scenario_builder_styles(),
        # Header
        Div(
            H1("Scenario Builder"),
            P(
                "Create custom conversation scenarios or use our templates to get started quickly"
            ),
            cls="builder-header",
        ),
        # Tabs
        Div(
            Button(
                "Templates",
                cls="builder-tab active",
                **{"data-tab": "templates"},
                onclick="switchTab('templates')",
            ),
            Button(
                "Create from Scratch",
                cls="builder-tab",
                **{"data-tab": "create"},
                onclick="switchTab('create')",
            ),
            Button(
                "My Scenarios",
                cls="builder-tab",
                **{"data-tab": "my-scenarios"},
                onclick="switchTab('my-scenarios')",
            ),
            Button(
                "Browse Public",
                cls="builder-tab",
                **{"data-tab": "public"},
                onclick="switchTab('public')",
            ),
            cls="builder-tabs",
        ),
        # Tab Contents
        create_templates_tab(),
        create_from_scratch_tab(),
        create_my_scenarios_tab(),
        create_public_scenarios_tab(),
        # Modals
        create_template_modal(),
        cls="builder-container",
    )


def create_templates_tab():
    """Template selection grid"""
    return Div(
        H2("Choose a Template"),
        P(
            "Select a pre-built template and customize it to create your scenario quickly",
            style="color: #64748b; margin-bottom: 20px;",
        ),
        Div(
            id="templates-grid",
            hx_get="/api/v1/scenario-builder/templates",
            hx_trigger="load",
            hx_swap="innerHTML",
        ),
        cls="tab-content active",
        id="templates-tab",
    )


def create_from_scratch_tab():
    """Form for creating scenario from scratch"""
    return Div(
        H2("Create Custom Scenario"),
        P(
            "Build your own scenario from the ground up",
            style="color: #64748b; margin-bottom: 20px;",
        ),
        Div(
            Form(
                Div(
                    Div(
                        Label("Scenario Title"),
                        Input(
                            type="text",
                            name="title",
                            required=True,
                            placeholder="e.g., Coffee Shop Conversation",
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Label("Description"),
                        Textarea(
                            name="description",
                            placeholder="Brief description of your scenario",
                        ),
                        cls="form-group",
                    ),
                    style="display: grid; grid-template-columns: 2fr 3fr; gap: 20px;",
                ),
                Div(
                    Div(
                        Label("Category"),
                        Select(
                            Option("restaurant", value="restaurant"),
                            Option("travel", value="travel"),
                            Option("shopping", value="shopping"),
                            Option("business", value="business"),
                            Option("social", value="social"),
                            Option("healthcare", value="healthcare"),
                            Option("emergency", value="emergency"),
                            Option("daily_life", value="daily_life"),
                            Option("hobbies", value="hobbies"),
                            Option("education", value="education"),
                            name="category",
                            required=True,
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Label("Difficulty"),
                        Select(
                            Option("beginner", value="beginner"),
                            Option("intermediate", value="intermediate"),
                            Option("advanced", value="advanced"),
                            name="difficulty",
                            required=True,
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Label("Duration (minutes)"),
                        Input(
                            type="number",
                            name="estimated_duration",
                            min="5",
                            max="60",
                            value="15",
                            required=True,
                        ),
                        cls="form-group",
                    ),
                    style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;",
                ),
                H3("Phases (2-6 required)", style="margin-top: 30px;"),
                P(
                    "Each scenario should have 2-6 phases representing different stages of the conversation",
                    cls="help-text",
                    style="margin-bottom: 20px;",
                ),
                Div(id="phases-container"),
                Button(
                    "+ Add Phase",
                    type="button",
                    cls="btn btn-secondary",
                    onclick="addPhase()",
                    style="margin-top: 10px;",
                ),
                Button(
                    "Create Scenario",
                    type="submit",
                    cls="btn btn-primary",
                    style="margin-top: 30px; width: 100%;",
                ),
                hx_post="/api/v1/scenario-builder/scenarios",
                hx_swap="none",
            ),
            cls="form-container",
        ),
        cls="tab-content",
        id="create-tab",
    )


def create_my_scenarios_tab():
    """User's scenarios list"""
    return Div(
        H2("My Scenarios"),
        P(
            "Manage your created scenarios",
            style="color: #64748b; margin-bottom: 20px;",
        ),
        Div(id="my-scenarios-list", cls="scenario-list"),
        cls="tab-content",
        id="my-scenarios-tab",
    )


def create_public_scenarios_tab():
    """Public scenarios browser"""
    return Div(
        H2("Public Scenarios"),
        P(
            "Discover and duplicate scenarios created by the community",
            style="color: #64748b; margin-bottom: 20px;",
        ),
        Button(
            "Refresh",
            cls="btn btn-secondary",
            onclick="loadPublicScenarios()",
            style="margin-bottom: 20px;",
        ),
        Div(id="public-scenarios-list", cls="scenario-list"),
        cls="tab-content",
        id="public-tab",
    )


def create_template_modal():
    """Modal for customizing template"""
    return Div(
        Div(
            Div(
                H2(id="template-title"),
                Button("×", cls="close-modal", onclick="closeModal('template-modal')"),
                cls="modal-header",
            ),
            Form(
                Input(type="hidden", name="template_id", id="selected-template-id"),
                Div(
                    Label("Custom Title"),
                    Input(
                        type="text",
                        name="custom_title",
                        id="custom-title",
                        required=True,
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Custom Description (optional)"),
                    Textarea(name="custom_description", id="custom-description"),
                    cls="form-group",
                ),
                Div(
                    Label("Difficulty Level (optional override)"),
                    Select(
                        Option("Keep template default", value="", selected=True),
                        Option("beginner", value="beginner"),
                        Option("intermediate", value="intermediate"),
                        Option("advanced", value="advanced"),
                        name="custom_difficulty",
                    ),
                    cls="form-group",
                ),
                Button(
                    "Create from Template",
                    type="submit",
                    cls="btn btn-primary",
                    style="width: 100%;",
                ),
                onsubmit="createFromTemplate(event); return false;",
            ),
            cls="modal-content",
        ),
        cls="modal",
        id="template-modal",
        onclick="if (event.target === this) closeModal('template-modal')",
    )


# Route handler
def create_scenario_builder_route():
    """FastAPI/FastHTML route handler"""
    from fastapi import Depends

    from app.core.security import require_auth

    def scenario_builder_handler(current_user: SimpleUser = Depends(require_auth)):
        return create_scenario_builder_page(current_user)

    return scenario_builder_handler
