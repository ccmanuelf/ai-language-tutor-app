"""
Admin Language Configuration UI Components

This module provides the user interface components for managing language
configurations, voice models, and feature toggles in the admin dashboard.

Task 3.1.3 - Language Configuration Panel
"""

from fasthtml.common import *
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


def language_config_page():
    """Main language configuration page"""
    return Div(
        # Page Header
        Div(
            H2("Language Configuration", cls="text-2xl font-bold text-white mb-6"),
            P(
                "Manage language support, voice models, and language-specific features",
                cls="text-gray-300 mb-6",
            ),
            cls="mb-8",
        ),
        # Language Configuration Cards Container
        Div(id="language-config-container", cls="space-y-6"),
        # Voice Model Sync Section
        Div(
            H3("Voice Model Management", cls="text-xl font-semibold text-white mb-4"),
            Div(
                Button(
                    "🔄 Sync Voice Models",
                    cls="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors",
                    onclick="syncVoiceModels()",
                ),
                P(
                    "Synchronize voice models with filesystem and update database",
                    cls="text-gray-400 text-sm mt-2",
                ),
                cls="bg-gray-800 p-4 rounded-lg",
            ),
            cls="mt-8",
        ),
        # Feature Toggles Section
        Div(
            H3("Feature Toggles", cls="text-xl font-semibold text-white mb-4"),
            Div(
                id="feature-toggles-container",
                cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",
            ),
            cls="mt-8",
        ),
        cls="max-w-7xl mx-auto",
    )


def language_config_card(
    language_code: str,
    language_name: str,
    native_name: str,
    config: Dict[str, Any],
    voice_models: List[Dict[str, Any]],
):
    """Individual language configuration card"""

    # Status indicators
    status_badges = []
    if config.get("is_enabled_globally", True):
        status_badges.append(
            Span("🟢 Enabled", cls="bg-green-600 text-white px-2 py-1 rounded text-xs")
        )
    else:
        status_badges.append(
            Span("🔴 Disabled", cls="bg-red-600 text-white px-2 py-1 rounded text-xs")
        )

    # Voice model info
    default_voice = config.get("default_voice_model", "None")
    active_models = [vm for vm in voice_models if vm.get("is_active", True)]

    # Feature status
    features = [
        ("STT", config.get("speech_recognition_enabled", True)),
        ("TTS", config.get("text_to_speech_enabled", True)),
        ("Pronunciation", config.get("pronunciation_analysis_enabled", True)),
        ("Tutor Modes", config.get("tutor_mode_enabled", True)),
        ("Scenarios", config.get("scenario_mode_enabled", True)),
        ("Real-time", config.get("realtime_analysis_enabled", True)),
    ]

    return Div(
        # Card Header
        Div(
            Div(
                H4(f"{language_name}", cls="text-lg font-semibold text-white"),
                P(
                    f"{native_name} ({language_code.upper()})",
                    cls="text-gray-400 text-sm",
                ),
                cls="flex-1",
            ),
            Div(*status_badges, cls="flex gap-2"),
            cls="flex items-start justify-between mb-4",
        ),
        # Configuration Sections
        Div(
            # Voice Models Section
            Div(
                H5("Voice Models", cls="text-md font-semibold text-white mb-2"),
                Div(
                    P(f"Default: {default_voice}", cls="text-gray-300 text-sm"),
                    P(
                        f"Available: {len(active_models)} models",
                        cls="text-gray-400 text-sm",
                    ),
                    cls="mb-3",
                ),
                Button(
                    "🎤 Configure Voices",
                    cls="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition-colors",
                    onclick=f"openVoiceConfig('{language_code}')",
                ),
                cls="mb-4",
            ),
            # Feature Toggles Section
            Div(
                H5("Features", cls="text-md font-semibold text-white mb-2"),
                Div(
                    *[
                        Div(
                            Label(
                                Input(
                                    type="checkbox",
                                    checked=enabled,
                                    onchange=f"toggleLanguageFeature('{language_code}', '{feature.lower().replace(' ', '_').replace('-', '_')}', this.checked)",
                                    cls="mr-2",
                                ),
                                feature,
                                cls="text-gray-300 text-sm flex items-center",
                            ),
                            cls="mb-1",
                        )
                        for feature, enabled in features
                    ],
                    cls="grid grid-cols-2 gap-2",
                ),
                cls="mb-4",
            ),
            # Quick Actions
            Div(
                Button(
                    "⚙️ Advanced Config",
                    cls="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm transition-colors mr-2",
                    onclick=f"openAdvancedConfig('{language_code}')",
                ),
                Button(
                    "🔄" if config.get("is_enabled_globally", True) else "✅",
                    cls=f"{'bg-red-600 hover:bg-red-700' if config.get('is_enabled_globally', True) else 'bg-green-600 hover:bg-green-700'} text-white px-3 py-1 rounded text-sm transition-colors",
                    onclick=f"toggleLanguage('{language_code}', {not config.get('is_enabled_globally', True)})",
                    title="Toggle language enable/disable",
                ),
                cls="flex gap-2",
            ),
            cls="space-y-3",
        ),
        cls="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors",
        id=f"language-card-{language_code}",
    )


def voice_model_config_modal(language_code: str, voice_models: List[Dict[str, Any]]):
    """Voice model configuration modal"""

    return Div(
        # Modal Overlay
        Div(
            cls="fixed inset-0 bg-black bg-opacity-50 z-40",
            onclick="closeVoiceConfig()",
        ),
        # Modal Content
        Div(
            # Modal Header
            Div(
                H3(
                    f"Voice Models - {language_code.upper()}",
                    cls="text-xl font-semibold text-white",
                ),
                Button(
                    "✕",
                    cls="text-gray-400 hover:text-white text-xl",
                    onclick="closeVoiceConfig()",
                ),
                cls="flex items-center justify-between mb-6",
            ),
            # Voice Models List
            Div(
                *[voice_model_row(vm, i) for i, vm in enumerate(voice_models)],
                cls="space-y-4 max-h-96 overflow-y-auto",
            ),
            # Modal Footer
            Div(
                Button(
                    "Save Changes",
                    cls="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors mr-3",
                    onclick="saveVoiceModelChanges()",
                ),
                Button(
                    "Cancel",
                    cls="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors",
                    onclick="closeVoiceConfig()",
                ),
                cls="flex justify-end mt-6",
            ),
            cls="bg-gray-900 p-6 rounded-lg max-w-4xl w-full mx-auto my-8 border border-gray-700",
        ),
        cls="fixed inset-0 flex items-center justify-center z-50",
        id="voice-config-modal",
        style="display: none;",
    )


def voice_model_row(voice_model: Dict[str, Any], index: int):
    """Individual voice model configuration row"""

    model_name = voice_model.get("model_name", "Unknown")
    quality = voice_model.get("quality_level", "medium")
    file_size = voice_model.get("file_size_mb", 0)
    is_active = voice_model.get("is_active", True)
    is_default = voice_model.get("is_default", False)
    sample_rate = voice_model.get("sample_rate", 22050)

    # Quality color coding
    quality_colors = {
        "high": "bg-green-600",
        "medium": "bg-blue-600",
        "low": "bg-yellow-600",
        "x_low": "bg-red-600",
    }

    return Div(
        # Model Info
        Div(
            Div(
                H5(model_name, cls="text-white font-semibold"),
                Div(
                    Span(
                        quality.title(),
                        cls=f"text-white px-2 py-1 rounded text-xs {quality_colors.get(quality, 'bg-gray-600')}",
                    ),
                    Span(f"{file_size:.1f}MB", cls="text-gray-400 text-sm ml-2"),
                    Span(f"{sample_rate}Hz", cls="text-gray-400 text-sm ml-2"),
                    cls="flex items-center gap-2 mt-1",
                ),
                cls="flex-1",
            ),
            # Controls
            Div(
                Label(
                    Input(
                        type="checkbox",
                        checked=is_active,
                        onchange=f"toggleVoiceModel({voice_model.get('id', index)}, this.checked)",
                        cls="mr-2",
                    ),
                    "Active",
                    cls="text-gray-300 text-sm flex items-center mr-4",
                ),
                Label(
                    Input(
                        type="radio",
                        name=f"default-voice-{voice_model.get('language_code', 'unknown')}",
                        checked=is_default,
                        onchange=f"setDefaultVoice({voice_model.get('id', index)})",
                        cls="mr-2",
                    ),
                    "Default",
                    cls="text-gray-300 text-sm flex items-center",
                ),
                cls="flex items-center",
            ),
            cls="flex items-center justify-between",
        ),
        cls="bg-gray-800 p-3 rounded border border-gray-700",
    )


def feature_toggle_card(feature: Dict[str, Any]):
    """Feature toggle configuration card"""

    feature_name = feature.get("feature_name", "Unknown")
    display_name = feature_name.replace("_", " ").title()
    is_enabled = feature.get("is_enabled", True)
    description = feature.get("description", "")
    category = feature.get("category", "general")
    requires_restart = feature.get("requires_restart", False)

    # Category colors
    category_colors = {
        "learning": "bg-blue-600",
        "speech": "bg-green-600",
        "admin": "bg-purple-600",
        "access": "bg-yellow-600",
        "performance": "bg-orange-600",
        "general": "bg-gray-600",
    }

    return Div(
        # Feature Header
        Div(
            H5(display_name, cls="text-white font-semibold"),
            Div(
                Span(
                    category.title(),
                    cls=f"text-white px-2 py-1 rounded text-xs {category_colors.get(category, 'bg-gray-600')}",
                ),
                Span(
                    "🔄 Restart Required",
                    cls="text-orange-400 px-2 py-1 rounded text-xs bg-orange-600 bg-opacity-20 ml-2",
                )
                if requires_restart
                else None,
                cls="flex items-center gap-2",
            ),
            cls="mb-3",
        ),
        # Feature Description
        P(description, cls="text-gray-400 text-sm mb-4 line-clamp-2"),
        # Feature Toggle
        Div(
            Label(
                Input(
                    type="checkbox",
                    checked=is_enabled,
                    onchange=f"toggleFeature('{feature_name}', this.checked)",
                    cls="mr-3",
                ),
                "Enabled" if is_enabled else "Disabled",
                cls=f"text-{'green' if is_enabled else 'red'}-400 font-semibold flex items-center",
            ),
            cls="flex items-center justify-between",
        ),
        cls="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors",
        id=f"feature-{feature_name}",
    )


def advanced_config_modal(language_code: str, config: Dict[str, Any]):
    """Advanced language configuration modal"""

    voice_settings = config.get("voice_settings", {})
    difficulty_levels = config.get(
        "difficulty_levels", ["beginner", "intermediate", "advanced"]
    )

    return Div(
        # Modal Overlay
        Div(
            cls="fixed inset-0 bg-black bg-opacity-50 z-40",
            onclick="closeAdvancedConfig()",
        ),
        # Modal Content
        Div(
            # Modal Header
            Div(
                H3(
                    f"Advanced Configuration - {language_code.upper()}",
                    cls="text-xl font-semibold text-white",
                ),
                Button(
                    "✕",
                    cls="text-gray-400 hover:text-white text-xl",
                    onclick="closeAdvancedConfig()",
                ),
                cls="flex items-center justify-between mb-6",
            ),
            # Configuration Sections
            Div(
                # Difficulty Levels
                Div(
                    H4(
                        "Difficulty Levels", cls="text-lg font-semibold text-white mb-3"
                    ),
                    Div(
                        *[
                            Div(
                                Input(
                                    value=level,
                                    cls="bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 flex-1",
                                    onchange=f"updateDifficultyLevel({i}, this.value)",
                                ),
                                Button(
                                    "✕",
                                    cls="bg-red-600 hover:bg-red-700 text-white px-2 py-2 rounded ml-2",
                                    onclick=f"removeDifficultyLevel({i})",
                                ),
                                cls="flex items-center mb-2",
                            )
                            for i, level in enumerate(difficulty_levels)
                        ],
                        Button(
                            "+ Add Level",
                            cls="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded text-sm",
                            onclick="addDifficultyLevel()",
                        ),
                        cls="mb-6",
                    ),
                    cls="mb-6",
                ),
                # Voice Settings
                Div(
                    H4("Voice Settings", cls="text-lg font-semibold text-white mb-3"),
                    Div(
                        Div(
                            Label(
                                "Speaking Rate", cls="text-gray-300 text-sm block mb-1"
                            ),
                            Input(
                                type="range",
                                min="0.5",
                                max="2.0",
                                step="0.1",
                                value=str(voice_settings.get("speaking_rate", 1.0)),
                                cls="w-full",
                                oninput="updateVoiceSetting('speaking_rate', this.value)",
                            ),
                            P(
                                f"{voice_settings.get('speaking_rate', 1.0)}",
                                cls="text-gray-400 text-sm",
                                id="speaking-rate-value",
                            ),
                            cls="mb-4",
                        ),
                        Div(
                            Label(
                                "Noise Scale", cls="text-gray-300 text-sm block mb-1"
                            ),
                            Input(
                                type="range",
                                min="0.0",
                                max="1.0",
                                step="0.1",
                                value=str(voice_settings.get("noise_scale", 0.667)),
                                cls="w-full",
                                oninput="updateVoiceSetting('noise_scale', this.value)",
                            ),
                            P(
                                f"{voice_settings.get('noise_scale', 0.667)}",
                                cls="text-gray-400 text-sm",
                                id="noise-scale-value",
                            ),
                            cls="mb-4",
                        ),
                        Div(
                            Label(
                                "Length Scale", cls="text-gray-300 text-sm block mb-1"
                            ),
                            Input(
                                type="range",
                                min="0.5",
                                max="2.0",
                                step="0.1",
                                value=str(voice_settings.get("length_scale", 1.0)),
                                cls="w-full",
                                oninput="updateVoiceSetting('length_scale', this.value)",
                            ),
                            P(
                                f"{voice_settings.get('length_scale', 1.0)}",
                                cls="text-gray-400 text-sm",
                                id="length-scale-value",
                            ),
                            cls="mb-4",
                        ),
                        cls="grid grid-cols-1 md:grid-cols-2 gap-4",
                    ),
                    cls="mb-6",
                ),
                cls="max-h-96 overflow-y-auto",
            ),
            # Modal Footer
            Div(
                Button(
                    "Save Advanced Settings",
                    cls="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors mr-3",
                    onclick="saveAdvancedConfig()",
                ),
                Button(
                    "Reset to Defaults",
                    cls="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg transition-colors mr-3",
                    onclick="resetAdvancedConfig()",
                ),
                Button(
                    "Cancel",
                    cls="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors",
                    onclick="closeAdvancedConfig()",
                ),
                cls="flex justify-end mt-6",
            ),
            cls="bg-gray-900 p-6 rounded-lg max-w-4xl w-full mx-auto my-8 border border-gray-700",
        ),
        cls="fixed inset-0 flex items-center justify-center z-50",
        id="advanced-config-modal",
        style="display: none;",
    )


def language_config_javascript():
    """JavaScript functions for language configuration management"""

    return Script("""
        // Global variables for language configuration
        let currentLanguageCode = '';
        let currentLanguageConfig = {};
        let currentVoiceModels = [];
        let modifiedVoiceSettings = {};
        let modifiedDifficultyLevels = [];

        // Load language configurations
        async function loadLanguageConfigurations() {
            try {
                const response = await fetch('/api/admin/languages/', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to load language configurations');
                }

                const languages = await response.json();
                displayLanguageConfigurations(languages);

            } catch (error) {
                console.error('Error loading language configurations:', error);
                showNotification('Failed to load language configurations', 'error');
            }
        }

        // Display language configuration cards
        function displayLanguageConfigurations(languages) {
            const container = document.getElementById('language-config-container');
            container.innerHTML = '';

            languages.forEach(lang => {
                const card = createLanguageConfigCard(lang);
                container.appendChild(card);
            });
        }

        // Create language configuration card (simplified version)
        function createLanguageConfigCard(lang) {
            const card = document.createElement('div');
            card.className = 'bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors';
            card.id = `language-card-${lang.language_code}`;

            // This would be replaced with the actual HTML structure
            card.innerHTML = `
                <div class="flex items-start justify-between mb-4">
                    <div class="flex-1">
                        <h4 class="text-lg font-semibold text-white">${lang.language_name}</h4>
                        <p class="text-gray-400 text-sm">${lang.native_name} (${lang.language_code.toUpperCase()})</p>
                    </div>
                    <div class="flex gap-2">
                        <span class="px-2 py-1 rounded text-xs ${lang.is_enabled_globally ? 'bg-green-600' : 'bg-red-600'} text-white">
                            ${lang.is_enabled_globally ? '🟢 Enabled' : '🔴 Disabled'}
                        </span>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <h5 class="text-md font-semibold text-white mb-2">Voice Models</h5>
                        <p class="text-gray-300 text-sm">Default: ${lang.default_voice_model || 'None'}</p>
                        <p class="text-gray-400 text-sm">Available: ${lang.available_voice_models.length} models</p>
                        <button onclick="openVoiceConfig('${lang.language_code}')"
                                class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm mt-2">
                            🎤 Configure Voices
                        </button>
                    </div>
                    <div>
                        <h5 class="text-md font-semibold text-white mb-2">Quick Actions</h5>
                        <button onclick="openAdvancedConfig('${lang.language_code}')"
                                class="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm mr-2">
                            ⚙️ Advanced Config
                        </button>
                        <button onclick="toggleLanguage('${lang.language_code}', ${!lang.is_enabled_globally})"
                                class="${lang.is_enabled_globally ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'} text-white px-3 py-1 rounded text-sm">
                            ${lang.is_enabled_globally ? '🔄' : '✅'}
                        </button>
                    </div>
                </div>
            `;

            return card;
        }

        // Toggle language enable/disable
        async function toggleLanguage(languageCode, enabled) {
            try {
                const response = await fetch(`/api/admin/languages/${languageCode}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                    },
                    body: JSON.stringify({ is_enabled_globally: enabled })
                });

                if (!response.ok) {
                    throw new Error('Failed to update language configuration');
                }

                showNotification(`Language ${languageCode} ${enabled ? 'enabled' : 'disabled'}`, 'success');
                loadLanguageConfigurations(); // Reload to reflect changes

            } catch (error) {
                console.error('Error toggling language:', error);
                showNotification('Failed to update language configuration', 'error');
            }
        }

        // Toggle language feature
        async function toggleLanguageFeature(languageCode, feature, enabled) {
            try {
                const updateData = {};
                updateData[feature + '_enabled'] = enabled;

                const response = await fetch(`/api/admin/languages/${languageCode}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                    },
                    body: JSON.stringify(updateData)
                });

                if (!response.ok) {
                    throw new Error('Failed to update feature');
                }

                showNotification(`${feature.replace('_', ' ')} ${enabled ? 'enabled' : 'disabled'} for ${languageCode}`, 'success');

            } catch (error) {
                console.error('Error toggling feature:', error);
                showNotification('Failed to update feature', 'error');
            }
        }

        // Open voice configuration modal
        async function openVoiceConfig(languageCode) {
            try {
                const response = await fetch(`/api/admin/languages/${languageCode}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to load language data');
                }

                const langData = await response.json();
                currentLanguageCode = languageCode;
                currentVoiceModels = langData.available_voice_models;

                // Show modal (simplified)
                document.getElementById('voice-config-modal').style.display = 'flex';

            } catch (error) {
                console.error('Error opening voice config:', error);
                showNotification('Failed to load voice configuration', 'error');
            }
        }

        // Close voice configuration modal
        function closeVoiceConfig() {
            document.getElementById('voice-config-modal').style.display = 'none';
            currentLanguageCode = '';
            currentVoiceModels = [];
        }

        // Open advanced configuration modal
        async function openAdvancedConfig(languageCode) {
            try {
                const response = await fetch(`/api/admin/languages/${languageCode}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to load language data');
                }

                const langData = await response.json();
                currentLanguageCode = languageCode;
                currentLanguageConfig = langData;
                modifiedVoiceSettings = { ...langData.voice_settings };
                modifiedDifficultyLevels = [...langData.difficulty_levels];

                // Show modal (simplified)
                document.getElementById('advanced-config-modal').style.display = 'flex';

            } catch (error) {
                console.error('Error opening advanced config:', error);
                showNotification('Failed to load advanced configuration', 'error');
            }
        }

        // Close advanced configuration modal
        function closeAdvancedConfig() {
            document.getElementById('advanced-config-modal').style.display = 'none';
            currentLanguageCode = '';
            currentLanguageConfig = {};
            modifiedVoiceSettings = {};
            modifiedDifficultyLevels = [];
        }

        // Sync voice models
        async function syncVoiceModels() {
            try {
                const response = await fetch('/api/admin/languages/sync-voice-models', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to sync voice models');
                }

                const result = await response.json();
                showNotification(`Voice models synchronized: ${result.new_models} new, ${result.existing_models} existing`, 'success');
                loadLanguageConfigurations(); // Reload to show updated models

            } catch (error) {
                console.error('Error syncing voice models:', error);
                showNotification('Failed to sync voice models', 'error');
            }
        }

        // Load feature toggles
        async function loadFeatureToggles() {
            try {
                const response = await fetch('/api/admin/languages/feature-toggles/', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to load feature toggles');
                }

                const features = await response.json();
                displayFeatureToggles(features);

            } catch (error) {
                console.error('Error loading feature toggles:', error);
                showNotification('Failed to load feature toggles', 'error');
            }
        }

        // Display feature toggles
        function displayFeatureToggles(features) {
            const container = document.getElementById('feature-toggles-container');
            container.innerHTML = '';

            features.forEach(feature => {
                const card = createFeatureToggleCard(feature);
                container.appendChild(card);
            });
        }

        // Create feature toggle card (simplified)
        function createFeatureToggleCard(feature) {
            const card = document.createElement('div');
            card.className = 'bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors';
            card.id = `feature-${feature.feature_name}`;

            const categoryColors = {
                'learning': 'bg-blue-600',
                'speech': 'bg-green-600',
                'admin': 'bg-purple-600',
                'access': 'bg-yellow-600',
                'performance': 'bg-orange-600',
                'general': 'bg-gray-600'
            };

            card.innerHTML = `
                <h5 class="text-white font-semibold">${feature.feature_name.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase())}</h5>
                <div class="flex items-center gap-2 mb-3">
                    <span class="text-white px-2 py-1 rounded text-xs ${categoryColors[feature.category] || 'bg-gray-600'}">
                        ${feature.category.charAt(0).toUpperCase() + feature.category.slice(1)}
                    </span>
                    ${feature.requires_restart ? '<span class="text-orange-400 px-2 py-1 rounded text-xs bg-orange-600 bg-opacity-20">🔄 Restart Required</span>' : ''}
                </div>
                <p class="text-gray-400 text-sm mb-4">${feature.description}</p>
                <label class="flex items-center">
                    <input type="checkbox" ${feature.is_enabled ? 'checked' : ''}
                           onchange="toggleFeature('${feature.feature_name}', this.checked)" class="mr-3">
                    <span class="text-${feature.is_enabled ? 'green' : 'red'}-400 font-semibold">
                        ${feature.is_enabled ? 'Enabled' : 'Disabled'}
                    </span>
                </label>
            `;

            return card;
        }

        // Toggle feature
        async function toggleFeature(featureName, enabled) {
            try {
                const response = await fetch(`/api/admin/languages/feature-toggles/${featureName}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                    },
                    body: JSON.stringify({ is_enabled: enabled })
                });

                if (!response.ok) {
                    throw new Error('Failed to update feature toggle');
                }

                showNotification(`Feature ${featureName.replace('_', ' ')} ${enabled ? 'enabled' : 'disabled'}`, 'success');
                loadFeatureToggles(); // Reload to reflect changes

            } catch (error) {
                console.error('Error toggling feature:', error);
                showNotification('Failed to update feature toggle', 'error');
            }
        }

        // Show notification
        function showNotification(message, type = 'info') {
            // This would be implemented to show toast notifications
            console.log(`${type.toUpperCase()}: ${message}`);
        }

        // Initialize language configuration page
        document.addEventListener('DOMContentLoaded', function() {
            loadLanguageConfigurations();
            loadFeatureToggles();
        });
    """)


# Export the main components that will be used in admin routes
__all__ = [
    "language_config_page",
    "language_config_card",
    "voice_model_config_modal",
    "feature_toggle_card",
    "advanced_config_modal",
    "language_config_javascript",
]
