"""
Admin Feature Toggle Management Interface
Provides comprehensive UI for managing dynamic feature controls.
"""

from fasthtml.common import *


def create_feature_toggle_page():
    """Create the main feature toggle management page."""

    return Div(
        # Header
        Div(
            H1(
                "Feature Toggle Management", cls="text-3xl font-bold text-gray-900 mb-2"
            ),
            P(
                "Manage dynamic feature controls and user access permissions",
                cls="text-gray-600 mb-6",
            ),
            cls="mb-8",
        ),
        # Action Bar
        Div(
            Div(
                Button(
                    I(cls="fas fa-plus mr-2"),
                    "Create Feature",
                    cls="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors",
                    onclick="openCreateFeatureModal()",
                ),
                Button(
                    I(cls="fas fa-chart-bar mr-2"),
                    "View Statistics",
                    cls="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors ml-2",
                    onclick="openStatsModal()",
                ),
                Button(
                    I(cls="fas fa-sync mr-2"),
                    "Refresh",
                    cls="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors ml-2",
                    onclick="refreshFeatures()",
                ),
                cls="flex items-center",
            ),
            # Search and Filter
            Div(
                Input(
                    type="text",
                    placeholder="Search features...",
                    cls="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    oninput="filterFeatures(this.value)",
                ),
                Select(
                    Option("All Categories", value=""),
                    Option("Tutor Modes", value="tutor_modes"),
                    Option("Scenarios", value="scenarios"),
                    Option("Analysis", value="analysis"),
                    Option("Speech", value="speech"),
                    Option("UI Components", value="ui_components"),
                    Option("API Endpoints", value="api_endpoints"),
                    Option("Integrations", value="integrations"),
                    Option("Experimental", value="experimental"),
                    cls="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ml-2",
                    onchange="filterByCategory(this.value)",
                ),
                Select(
                    Option("All Statuses", value=""),
                    Option("Enabled", value="enabled"),
                    Option("Disabled", value="disabled"),
                    Option("Experimental", value="experimental"),
                    Option("Deprecated", value="deprecated"),
                    Option("Maintenance", value="maintenance"),
                    cls="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ml-2",
                    onchange="filterByStatus(this.value)",
                ),
                cls="flex items-center",
            ),
            cls="flex justify-between items-center mb-6",
        ),
        # Feature Toggles Table
        create_features_table(),
        # Modals
        create_feature_modal(),
        create_edit_feature_modal(),
        create_user_access_modal(),
        create_stats_modal(),
        # JavaScript
        Script(create_feature_toggle_js()),
        cls="max-w-7xl mx-auto p-6",
    )


def create_features_table():
    """Create the features table with sorting and filtering."""

    return Div(
        Div(
            Table(
                # Header
                Thead(
                    Tr(
                        Th(
                            "Name",
                            cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer",
                            onclick="sortTable('name')",
                        ),
                        Th(
                            "Category",
                            cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer",
                            onclick="sortTable('category')",
                        ),
                        Th(
                            "Status",
                            cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer",
                            onclick="sortTable('status')",
                        ),
                        Th(
                            "Scope",
                            cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer",
                            onclick="sortTable('scope')",
                        ),
                        Th(
                            "Created",
                            cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer",
                            onclick="sortTable('created')",
                        ),
                        Th(
                            "Actions",
                            cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        cls="bg-gray-50",
                    ),
                    cls="bg-gray-50",
                ),
                # Body (will be populated by JavaScript)
                Tbody(id="featuresTableBody", cls="bg-white divide-y divide-gray-200"),
                cls="min-w-full divide-y divide-gray-200",
            ),
            cls="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg",
        ),
        # Pagination
        Div(
            Div(
                P(id="paginationInfo", cls="text-sm text-gray-700"),
                cls="flex-1 flex justify-between sm:hidden",
            ),
            Div(
                Nav(
                    Div(
                        Button(
                            "Previous",
                            id="prevPageBtn",
                            cls="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50",
                            onclick="changePage(-1)",
                        ),
                        Div(id="pageNumbers", cls="hidden md:flex"),
                        Button(
                            "Next",
                            id="nextPageBtn",
                            cls="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50",
                            onclick="changePage(1)",
                        ),
                        cls="relative z-0 inline-flex rounded-md shadow-sm -space-x-px",
                    ),
                    cls="isolate inline-flex -space-x-px rounded-md shadow-sm",
                ),
                cls="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between",
            ),
            cls="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-4",
        ),
        cls="mt-8",
    )


def create_feature_modal():
    """Create the new feature creation modal."""

    return Div(
        Div(
            Div(
                Div(
                    # Modal Header
                    Div(
                        H3(
                            "Create New Feature Toggle",
                            cls="text-lg font-medium text-gray-900",
                        ),
                        Button(
                            I(cls="fas fa-times"),
                            cls="text-gray-400 hover:text-gray-600",
                            onclick="closeCreateFeatureModal()",
                        ),
                        cls="flex items-center justify-between p-6 border-b border-gray-200",
                    ),
                    # Modal Body
                    Div(
                        Form(
                            # Basic Information
                            Div(
                                H4(
                                    "Basic Information",
                                    cls="text-md font-medium text-gray-900 mb-4",
                                ),
                                Div(
                                    Label(
                                        "Feature Name",
                                        cls="block text-sm font-medium text-gray-700 mb-1",
                                    ),
                                    Input(
                                        type="text",
                                        id="createFeatureName",
                                        required=True,
                                        cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                                        placeholder="e.g., Advanced Speech Analysis",
                                    ),
                                    cls="mb-4",
                                ),
                                Div(
                                    Label(
                                        "Description",
                                        cls="block text-sm font-medium text-gray-700 mb-1",
                                    ),
                                    Textarea(
                                        id="createFeatureDescription",
                                        required=True,
                                        rows="3",
                                        cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                                        placeholder="Detailed description of what this feature does...",
                                    ),
                                    cls="mb-4",
                                ),
                                Div(
                                    Div(
                                        Label(
                                            "Category",
                                            cls="block text-sm font-medium text-gray-700 mb-1",
                                        ),
                                        Select(
                                            Option("Tutor Modes", value="tutor_modes"),
                                            Option("Scenarios", value="scenarios"),
                                            Option("Analysis", value="analysis"),
                                            Option("Speech", value="speech"),
                                            Option(
                                                "UI Components", value="ui_components"
                                            ),
                                            Option(
                                                "API Endpoints", value="api_endpoints"
                                            ),
                                            Option(
                                                "Integrations", value="integrations"
                                            ),
                                            Option(
                                                "Experimental", value="experimental"
                                            ),
                                            id="createFeatureCategory",
                                            required=True,
                                            cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                                        ),
                                        cls="flex-1 mr-2",
                                    ),
                                    Div(
                                        Label(
                                            "Scope",
                                            cls="block text-sm font-medium text-gray-700 mb-1",
                                        ),
                                        Select(
                                            Option("Global", value="global"),
                                            Option(
                                                "User Specific", value="user_specific"
                                            ),
                                            Option("Role Based", value="role_based"),
                                            Option(
                                                "Experimental", value="experimental"
                                            ),
                                            id="createFeatureScope",
                                            cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                                        ),
                                        cls="flex-1 ml-2",
                                    ),
                                    cls="flex mb-4",
                                ),
                                cls="mb-6",
                            ),
                            # Configuration
                            Div(
                                H4(
                                    "Configuration",
                                    cls="text-md font-medium text-gray-900 mb-4",
                                ),
                                Div(
                                    Div(
                                        Label(
                                            "Initial Status",
                                            cls="block text-sm font-medium text-gray-700 mb-1",
                                        ),
                                        Select(
                                            Option(
                                                "Disabled",
                                                value="disabled",
                                                selected=True,
                                            ),
                                            Option("Enabled", value="enabled"),
                                            Option(
                                                "Experimental", value="experimental"
                                            ),
                                            Option("Maintenance", value="maintenance"),
                                            id="createFeatureStatus",
                                            cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                                        ),
                                        cls="flex-1 mr-2",
                                    ),
                                    Div(
                                        Label(
                                            "Rollout Percentage",
                                            cls="block text-sm font-medium text-gray-700 mb-1",
                                        ),
                                        Input(
                                            type="number",
                                            id="createFeatureRollout",
                                            min="0",
                                            max="100",
                                            value="100",
                                            cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                                        ),
                                        cls="flex-1 ml-2",
                                    ),
                                    cls="flex mb-4",
                                ),
                                # Checkboxes
                                Div(
                                    Label(
                                        Input(
                                            type="checkbox",
                                            id="createFeatureDefaultEnabled",
                                            cls="mr-2",
                                        ),
                                        "Enabled by default for new users",
                                        cls="flex items-center text-sm text-gray-700 mb-2",
                                    ),
                                    Label(
                                        Input(
                                            type="checkbox",
                                            id="createFeatureRequiresAdmin",
                                            cls="mr-2",
                                        ),
                                        "Requires admin permission",
                                        cls="flex items-center text-sm text-gray-700 mb-2",
                                    ),
                                    Label(
                                        Input(
                                            type="checkbox",
                                            id="createFeatureExperimental",
                                            cls="mr-2",
                                        ),
                                        "Experimental feature",
                                        cls="flex items-center text-sm text-gray-700 mb-2",
                                    ),
                                    Label(
                                        Input(
                                            type="checkbox",
                                            id="createFeatureUsageTracking",
                                            checked=True,
                                            cls="mr-2",
                                        ),
                                        "Enable usage tracking",
                                        cls="flex items-center text-sm text-gray-700",
                                    ),
                                    cls="mb-4",
                                ),
                                cls="mb-6",
                            ),
                            # Environment Configuration
                            Div(
                                H4(
                                    "Environment Configuration",
                                    cls="text-md font-medium text-gray-900 mb-4",
                                ),
                                Div(
                                    Div(
                                        Label(
                                            Input(
                                                type="checkbox",
                                                id="createFeatureDevEnabled",
                                                checked=True,
                                                cls="mr-2",
                                            ),
                                            "Development",
                                            cls="flex items-center text-sm text-gray-700",
                                        ),
                                        cls="flex-1",
                                    ),
                                    Div(
                                        Label(
                                            Input(
                                                type="checkbox",
                                                id="createFeatureStagingEnabled",
                                                cls="mr-2",
                                            ),
                                            "Staging",
                                            cls="flex items-center text-sm text-gray-700",
                                        ),
                                        cls="flex-1",
                                    ),
                                    Div(
                                        Label(
                                            Input(
                                                type="checkbox",
                                                id="createFeatureProdEnabled",
                                                cls="mr-2",
                                            ),
                                            "Production",
                                            cls="flex items-center text-sm text-gray-700",
                                        ),
                                        cls="flex-1",
                                    ),
                                    cls="flex space-x-4",
                                ),
                                cls="mb-6",
                            ),
                            id="createFeatureForm",
                        ),
                        cls="p-6",
                    ),
                    # Modal Footer
                    Div(
                        Button(
                            "Cancel",
                            cls="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-lg font-medium transition-colors mr-2",
                            onclick="closeCreateFeatureModal()",
                        ),
                        Button(
                            "Create Feature",
                            cls="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors",
                            onclick="createFeature()",
                        ),
                        cls="flex justify-end p-6 border-t border-gray-200",
                    ),
                    cls="bg-white rounded-lg shadow-xl transform transition-all",
                ),
                cls="flex items-center justify-center min-h-screen p-4",
            ),
            cls="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50",
        ),
        id="createFeatureModal",
        style="display: none;",
    )


def create_edit_feature_modal():
    """Create the feature edit modal."""

    return Div(
        Div(
            Div(
                Div(
                    # Modal Header
                    Div(
                        H3(
                            "Edit Feature Toggle",
                            cls="text-lg font-medium text-gray-900",
                        ),
                        Button(
                            I(cls="fas fa-times"),
                            cls="text-gray-400 hover:text-gray-600",
                            onclick="closeEditFeatureModal()",
                        ),
                        cls="flex items-center justify-between p-6 border-b border-gray-200",
                    ),
                    # Modal Body
                    Div(Form(id="editFeatureForm", cls="space-y-4"), cls="p-6"),
                    # Modal Footer
                    Div(
                        Button(
                            "Cancel",
                            cls="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-lg font-medium transition-colors mr-2",
                            onclick="closeEditFeatureModal()",
                        ),
                        Button(
                            "Update Feature",
                            cls="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors",
                            onclick="updateFeature()",
                        ),
                        cls="flex justify-end p-6 border-t border-gray-200",
                    ),
                    cls="bg-white rounded-lg shadow-xl transform transition-all",
                ),
                cls="flex items-center justify-center min-h-screen p-4",
            ),
            cls="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50",
        ),
        id="editFeatureModal",
        style="display: none;",
    )


def create_user_access_modal():
    """Create the user access management modal."""

    return Div(
        Div(
            Div(
                Div(
                    # Modal Header
                    Div(
                        H3(
                            "Manage User Access",
                            cls="text-lg font-medium text-gray-900",
                        ),
                        Button(
                            I(cls="fas fa-times"),
                            cls="text-gray-400 hover:text-gray-600",
                            onclick="closeUserAccessModal()",
                        ),
                        cls="flex items-center justify-between p-6 border-b border-gray-200",
                    ),
                    # Modal Body
                    Div(Div(id="userAccessContent"), cls="p-6"),
                    # Modal Footer
                    Div(
                        Button(
                            "Close",
                            cls="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-lg font-medium transition-colors",
                            onclick="closeUserAccessModal()",
                        ),
                        cls="flex justify-end p-6 border-t border-gray-200",
                    ),
                    cls="bg-white rounded-lg shadow-xl transform transition-all max-w-2xl w-full",
                ),
                cls="flex items-center justify-center min-h-screen p-4",
            ),
            cls="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50",
        ),
        id="userAccessModal",
        style="display: none;",
    )


def create_stats_modal():
    """Create the statistics modal."""

    return Div(
        Div(
            Div(
                Div(
                    # Modal Header
                    Div(
                        H3(
                            "Feature Toggle Statistics",
                            cls="text-lg font-medium text-gray-900",
                        ),
                        Button(
                            I(cls="fas fa-times"),
                            cls="text-gray-400 hover:text-gray-600",
                            onclick="closeStatsModal()",
                        ),
                        cls="flex items-center justify-between p-6 border-b border-gray-200",
                    ),
                    # Modal Body
                    Div(Div(id="statsContent"), cls="p-6"),
                    # Modal Footer
                    Div(
                        Button(
                            "Close",
                            cls="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-lg font-medium transition-colors",
                            onclick="closeStatsModal()",
                        ),
                        cls="flex justify-end p-6 border-t border-gray-200",
                    ),
                    cls="bg-white rounded-lg shadow-xl transform transition-all max-w-4xl w-full",
                ),
                cls="flex items-center justify-center min-h-screen p-4",
            ),
            cls="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50",
        ),
        id="statsModal",
        style="display: none;",
    )


def create_feature_toggle_js():
    """Create JavaScript for feature toggle management."""

    return """
let features = [];
let filteredFeatures = [];
let currentPage = 1;
let pageSize = 10;
let sortColumn = 'created_at';
let sortDirection = 'desc';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadFeatures();
});

// Feature Loading
async function loadFeatures() {
    try {
        const response = await fetch('/api/admin/feature-toggles/features');
        const data = await response.json();
        features = data.features || [];
        filteredFeatures = [...features];
        renderFeatures();
    } catch (error) {
        console.error('Error loading features:', error);
        showNotification('Error loading features', 'error');
    }
}

async function refreshFeatures() {
    await loadFeatures();
    showNotification('Features refreshed', 'success');
}

// Feature Rendering
function renderFeatures() {
    const tbody = document.getElementById('featuresTableBody');
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const pageFeatures = filteredFeatures.slice(start, end);

    tbody.innerHTML = pageFeatures.map(feature => createFeatureRow(feature)).join('');
    updatePagination();
}

function createFeatureRow(feature) {
    const statusBadge = getStatusBadge(feature.status);
    const scopeBadge = getScopeBadge(feature.scope);
    const categoryBadge = getCategoryBadge(feature.category);

    return `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div>
                        <div class="text-sm font-medium text-gray-900">${feature.name}</div>
                        <div class="text-sm text-gray-500">${feature.description.substring(0, 60)}${feature.description.length > 60 ? '...' : ''}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${categoryBadge}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${statusBadge}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${scopeBadge}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatDate(feature.created_at)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                    <button onclick="editFeature('${feature.id}')" class="text-blue-600 hover:text-blue-900">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="toggleFeature('${feature.id}', '${feature.status === 'enabled' ? 'disable' : 'enable'}')"
                            class="text-${feature.status === 'enabled' ? 'red' : 'green'}-600 hover:text-${feature.status === 'enabled' ? 'red' : 'green'}-900">
                        <i class="fas fa-power-off"></i>
                    </button>
                    <button onclick="manageUserAccess('${feature.id}')" class="text-purple-600 hover:text-purple-900">
                        <i class="fas fa-users"></i>
                    </button>
                    <button onclick="deleteFeature('${feature.id}')" class="text-red-600 hover:text-red-900">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `;
}

function getStatusBadge(status) {
    const colors = {
        'enabled': 'bg-green-100 text-green-800',
        'disabled': 'bg-gray-100 text-gray-800',
        'experimental': 'bg-yellow-100 text-yellow-800',
        'deprecated': 'bg-red-100 text-red-800',
        'maintenance': 'bg-orange-100 text-orange-800'
    };

    return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${colors[status] || 'bg-gray-100 text-gray-800'}">${status}</span>`;
}

function getScopeBadge(scope) {
    const colors = {
        'global': 'bg-blue-100 text-blue-800',
        'user_specific': 'bg-purple-100 text-purple-800',
        'role_based': 'bg-indigo-100 text-indigo-800',
        'experimental': 'bg-yellow-100 text-yellow-800'
    };

    return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${colors[scope] || 'bg-gray-100 text-gray-800'}">${scope.replace('_', ' ')}</span>`;
}

function getCategoryBadge(category) {
    const colors = {
        'tutor_modes': 'bg-green-100 text-green-800',
        'scenarios': 'bg-blue-100 text-blue-800',
        'analysis': 'bg-purple-100 text-purple-800',
        'speech': 'bg-pink-100 text-pink-800',
        'ui_components': 'bg-indigo-100 text-indigo-800',
        'api_endpoints': 'bg-yellow-100 text-yellow-800',
        'integrations': 'bg-red-100 text-red-800',
        'experimental': 'bg-orange-100 text-orange-800'
    };

    return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${colors[category] || 'bg-gray-100 text-gray-800'}">${category.replace('_', ' ')}</span>`;
}

// Filtering and Sorting
function filterFeatures(searchTerm) {
    filteredFeatures = features.filter(feature =>
        feature.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        feature.description.toLowerCase().includes(searchTerm.toLowerCase())
    );
    currentPage = 1;
    renderFeatures();
}

function filterByCategory(category) {
    if (category === '') {
        filteredFeatures = [...features];
    } else {
        filteredFeatures = features.filter(feature => feature.category === category);
    }
    currentPage = 1;
    renderFeatures();
}

function filterByStatus(status) {
    if (status === '') {
        filteredFeatures = [...features];
    } else {
        filteredFeatures = features.filter(feature => feature.status === status);
    }
    currentPage = 1;
    renderFeatures();
}

function sortTable(column) {
    if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'asc';
    }

    filteredFeatures.sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];

        if (column === 'created_at') {
            aVal = new Date(aVal);
            bVal = new Date(bVal);
        }

        if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
        return 0;
    });

    renderFeatures();
}

// Pagination
function updatePagination() {
    const totalPages = Math.ceil(filteredFeatures.length / pageSize);
    const info = document.getElementById('paginationInfo');
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');

    info.textContent = `Showing ${((currentPage - 1) * pageSize) + 1} to ${Math.min(currentPage * pageSize, filteredFeatures.length)} of ${filteredFeatures.length} features`;

    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;

    if (prevBtn.disabled) {
        prevBtn.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        prevBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }

    if (nextBtn.disabled) {
        nextBtn.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        nextBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

function changePage(delta) {
    const totalPages = Math.ceil(filteredFeatures.length / pageSize);
    const newPage = currentPage + delta;

    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        renderFeatures();
    }
}

// Modal Management
function openCreateFeatureModal() {
    document.getElementById('createFeatureModal').style.display = 'block';
}

function closeCreateFeatureModal() {
    document.getElementById('createFeatureModal').style.display = 'none';
    document.getElementById('createFeatureForm').reset();
}

function openEditFeatureModal() {
    document.getElementById('editFeatureModal').style.display = 'block';
}

function closeEditFeatureModal() {
    document.getElementById('editFeatureModal').style.display = 'none';
}

function openUserAccessModal() {
    document.getElementById('userAccessModal').style.display = 'block';
}

function closeUserAccessModal() {
    document.getElementById('userAccessModal').style.display = 'none';
}

function openStatsModal() {
    document.getElementById('statsModal').style.display = 'block';
    loadStats();
}

function closeStatsModal() {
    document.getElementById('statsModal').style.display = 'none';
}

// Feature Operations
async function createFeature() {
    const form = document.getElementById('createFeatureForm');
    const formData = new FormData(form);

    const featureData = {
        name: document.getElementById('createFeatureName').value,
        description: document.getElementById('createFeatureDescription').value,
        category: document.getElementById('createFeatureCategory').value,
        scope: document.getElementById('createFeatureScope').value,
        status: document.getElementById('createFeatureStatus').value,
        enabled_by_default: document.getElementById('createFeatureDefaultEnabled').checked,
        requires_admin: document.getElementById('createFeatureRequiresAdmin').checked,
        experimental: document.getElementById('createFeatureExperimental').checked,
        usage_tracking: document.getElementById('createFeatureUsageTracking').checked,
        rollout_percentage: parseFloat(document.getElementById('createFeatureRollout').value),
        environments: {
            development: document.getElementById('createFeatureDevEnabled').checked,
            staging: document.getElementById('createFeatureStagingEnabled').checked,
            production: document.getElementById('createFeatureProdEnabled').checked
        }
    };

    try {
        const response = await fetch('/api/admin/feature-toggles/features', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(featureData)
        });

        if (response.ok) {
            closeCreateFeatureModal();
            await loadFeatures();
            showNotification('Feature created successfully', 'success');
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Error creating feature', 'error');
        }
    } catch (error) {
        console.error('Error creating feature:', error);
        showNotification('Error creating feature', 'error');
    }
}

async function editFeature(featureId) {
    const feature = features.find(f => f.id === featureId);
    if (!feature) return;

    // Populate edit form
    const form = document.getElementById('editFeatureForm');
    form.innerHTML = `
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Feature Name</label>
                <input type="text" id="editFeatureName" value="${feature.name}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea id="editFeatureDescription" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent">${feature.description}</textarea>
            </div>
            <div class="flex space-x-4">
                <div class="flex-1">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                    <select id="editFeatureStatus" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                        <option value="enabled" ${feature.status === 'enabled' ? 'selected' : ''}>Enabled</option>
                        <option value="disabled" ${feature.status === 'disabled' ? 'selected' : ''}>Disabled</option>
                        <option value="experimental" ${feature.status === 'experimental' ? 'selected' : ''}>Experimental</option>
                        <option value="maintenance" ${feature.status === 'maintenance' ? 'selected' : ''}>Maintenance</option>
                        <option value="deprecated" ${feature.status === 'deprecated' ? 'selected' : ''}>Deprecated</option>
                    </select>
                </div>
                <div class="flex-1">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Rollout %</label>
                    <input type="number" id="editFeatureRollout" min="0" max="100" value="${feature.rollout_percentage}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                </div>
            </div>
        </div>
    `;

    // Store feature ID for update
    form.dataset.featureId = featureId;

    openEditFeatureModal();
}

async function updateFeature() {
    const form = document.getElementById('editFeatureForm');
    const featureId = form.dataset.featureId;

    const updateData = {
        name: document.getElementById('editFeatureName').value,
        description: document.getElementById('editFeatureDescription').value,
        status: document.getElementById('editFeatureStatus').value,
        rollout_percentage: parseFloat(document.getElementById('editFeatureRollout').value)
    };

    try {
        const response = await fetch(`/api/admin/feature-toggles/features/${featureId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updateData)
        });

        if (response.ok) {
            closeEditFeatureModal();
            await loadFeatures();
            showNotification('Feature updated successfully', 'success');
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Error updating feature', 'error');
        }
    } catch (error) {
        console.error('Error updating feature:', error);
        showNotification('Error updating feature', 'error');
    }
}

async function toggleFeature(featureId, action) {
    try {
        const response = await fetch(`/api/admin/feature-toggles/features/${featureId}/${action}`, {
            method: 'POST'
        });

        if (response.ok) {
            await loadFeatures();
            showNotification(`Feature ${action}d successfully`, 'success');
        } else {
            const error = await response.json();
            showNotification(error.detail || `Error ${action}ing feature`, 'error');
        }
    } catch (error) {
        console.error(`Error ${action}ing feature:`, error);
        showNotification(`Error ${action}ing feature`, 'error');
    }
}

async function deleteFeature(featureId) {
    if (!confirm('Are you sure you want to delete this feature toggle? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/api/admin/feature-toggles/features/${featureId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            await loadFeatures();
            showNotification('Feature deleted successfully', 'success');
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Error deleting feature', 'error');
        }
    } catch (error) {
        console.error('Error deleting feature:', error);
        showNotification('Error deleting feature', 'error');
    }
}

async function manageUserAccess(featureId) {
    const feature = features.find(f => f.id === featureId);
    if (!feature) return;

    const content = document.getElementById('userAccessContent');
    content.innerHTML = `
        <div class="space-y-4">
            <h4 class="text-lg font-medium">Feature: ${feature.name}</h4>
            <div class="bg-blue-50 p-4 rounded-md">
                <p class="text-sm text-blue-800">Use this interface to grant or revoke feature access for specific users.</p>
            </div>
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">User ID</label>
                    <input type="text" id="userAccessUserId" placeholder="Enter user ID" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                </div>
                <div class="flex items-center space-x-4">
                    <label class="flex items-center">
                        <input type="radio" name="userAccessAction" value="grant" checked class="mr-2">
                        Grant Access
                    </label>
                    <label class="flex items-center">
                        <input type="radio" name="userAccessAction" value="revoke" class="mr-2">
                        Revoke Access
                    </label>
                </div>
                <div>
                    <label class="flex items-center">
                        <input type="checkbox" id="userAccessOverride" class="mr-2">
                        Override global setting
                    </label>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Reason (optional)</label>
                    <input type="text" id="userAccessReason" placeholder="Reason for access change" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                </div>
                <button onclick="setUserAccess('${featureId}')" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                    Apply Changes
                </button>
            </div>
        </div>
    `;

    openUserAccessModal();
}

async function setUserAccess(featureId) {
    const userId = document.getElementById('userAccessUserId').value;
    const action = document.querySelector('input[name="userAccessAction"]:checked').value;
    const override = document.getElementById('userAccessOverride').checked;
    const reason = document.getElementById('userAccessReason').value;

    if (!userId) {
        showNotification('Please enter a user ID', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/admin/feature-toggles/users/${userId}/features/${featureId}?enabled=${action === 'grant'}&override_global=${override}&override_reason=${encodeURIComponent(reason)}`, {
            method: 'POST'
        });

        if (response.ok) {
            closeUserAccessModal();
            showNotification(`User access ${action === 'grant' ? 'granted' : 'revoked'} successfully`, 'success');
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Error setting user access', 'error');
        }
    } catch (error) {
        console.error('Error setting user access:', error);
        showNotification('Error setting user access', 'error');
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/admin/feature-toggles/statistics');
        const stats = await response.json();

        const content = document.getElementById('statsContent');
        content.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div class="bg-blue-50 p-4 rounded-lg">
                    <h4 class="font-medium text-blue-900">Total Features</h4>
                    <p class="text-2xl font-bold text-blue-600">${stats.total_features}</p>
                </div>
                <div class="bg-green-50 p-4 rounded-lg">
                    <h4 class="font-medium text-green-900">Enabled</h4>
                    <p class="text-2xl font-bold text-green-600">${stats.enabled_features}</p>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="font-medium text-gray-900">Disabled</h4>
                    <p class="text-2xl font-bold text-gray-600">${stats.disabled_features}</p>
                </div>
                <div class="bg-yellow-50 p-4 rounded-lg">
                    <h4 class="font-medium text-yellow-900">Experimental</h4>
                    <p class="text-2xl font-bold text-yellow-600">${stats.experimental_features}</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h4 class="font-medium text-gray-900 mb-3">Features by Category</h4>
                    <div class="space-y-2">
                        ${Object.entries(stats.features_by_category).map(([category, count]) => `
                            <div class="flex justify-between">
                                <span class="text-sm text-gray-600">${category.replace('_', ' ')}</span>
                                <span class="text-sm font-medium">${count}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div>
                    <h4 class="font-medium text-gray-900 mb-3">Features by Scope</h4>
                    <div class="space-y-2">
                        ${Object.entries(stats.features_by_scope).map(([scope, count]) => `
                            <div class="flex justify-between">
                                <span class="text-sm text-gray-600">${scope.replace('_', ' ')}</span>
                                <span class="text-sm font-medium">${count}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading stats:', error);
        showNotification('Error loading statistics', 'error');
    }
}

// Utility Functions
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
}

function showNotification(message, type = 'info') {
    // Simple notification system
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg text-white z-50 ${
        type === 'success' ? 'bg-green-500' :
        type === 'error' ? 'bg-red-500' :
        type === 'warning' ? 'bg-yellow-500' :
        'bg-blue-500'
    }`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
    """


async def render_feature_toggles_page():
    """Render the complete feature toggle management page."""
    return create_feature_toggle_page()
