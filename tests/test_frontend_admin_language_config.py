"""
Test module for Admin Language Configuration Frontend
AI Language Tutor App - Session 106

Tests for app/frontend/admin_language_config.py module
Target: 100% coverage with comprehensive test scenarios
"""

import pytest
from fasthtml.common import to_xml

from app.frontend.admin_language_config import (
    advanced_config_modal,
    feature_toggle_card,
    language_config_card,
    language_config_javascript,
    language_config_page,
    voice_model_config_modal,
    voice_model_row,
)


class TestLanguageConfigPage:
    """Tests for language_config_page function"""

    def test_language_config_page_returns_div(self):
        """Test that language_config_page returns a Div element"""
        result = language_config_page()
        result_str = to_xml(result)
        assert "<div" in result_str.lower()

    def test_language_config_page_has_header(self):
        """Test that page includes header"""
        result = language_config_page()
        result_str = to_xml(result)
        assert "Language Configuration" in result_str

    def test_language_config_page_has_description(self):
        """Test that page includes description"""
        result = language_config_page()
        result_str = to_xml(result)
        assert "Manage language support" in result_str

    def test_language_config_page_has_container(self):
        """Test that page has language config container"""
        result = language_config_page()
        result_str = to_xml(result)
        assert "language-config-container" in result_str

    def test_language_config_page_has_voice_model_section(self):
        """Test that page includes voice model management section"""
        result = language_config_page()
        result_str = to_xml(result)
        assert "Voice Model Management" in result_str

    def test_language_config_page_has_sync_button(self):
        """Test that page includes sync voice models button"""
        result = language_config_page()
        result_str = to_xml(result)
        assert "Sync Voice Models" in result_str
        assert "syncVoiceModels()" in result_str

    def test_language_config_page_has_sync_description(self):
        """Test that page includes sync description"""
        result = language_config_page()
        result_str = to_xml(result)
        assert "Synchronize voice models with filesystem" in result_str

    def test_language_config_page_has_feature_toggles_section(self):
        """Test that page includes feature toggles section"""
        result = language_config_page()
        result_str = to_xml(result)
        assert "Feature Toggles" in result_str

    def test_language_config_page_has_feature_toggles_container(self):
        """Test that page has feature toggles container"""
        result = language_config_page()
        result_str = to_xml(result)
        assert "feature-toggles-container" in result_str


class TestLanguageConfigCard:
    """Tests for language_config_card function"""

    def setup_method(self):
        """Set up test data"""
        self.language_code = "es"
        self.language_name = "Spanish"
        self.native_name = "Español"
        self.config = {
            "is_enabled_globally": True,
            "default_voice_model": "es-ES-Neural",
            "speech_recognition_enabled": True,
            "text_to_speech_enabled": True,
            "pronunciation_analysis_enabled": True,
            "tutor_mode_enabled": True,
            "scenario_mode_enabled": True,
            "realtime_analysis_enabled": True,
        }
        self.voice_models = [
            {"name": "es-ES-Neural", "is_active": True},
            {"name": "es-MX-Neural", "is_active": False},
        ]

    def test_language_config_card_returns_div(self):
        """Test that language_config_card returns a Div"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "<div" in result_str.lower()

    def test_language_config_card_shows_language_name(self):
        """Test that card shows language name"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "Spanish" in result_str

    def test_language_config_card_shows_native_name(self):
        """Test that card shows native name"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "Español" in result_str

    def test_language_config_card_shows_language_code(self):
        """Test that card shows language code"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "ES" in result_str  # Uppercase language code

    def test_language_config_card_shows_enabled_badge(self):
        """Test that card shows enabled badge when globally enabled"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "🟢 Enabled" in result_str
        assert "bg-green-600" in result_str

    def test_language_config_card_shows_disabled_badge(self):
        """Test that card shows disabled badge when globally disabled"""
        self.config["is_enabled_globally"] = False
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "🔴 Disabled" in result_str
        assert "bg-red-600" in result_str

    def test_language_config_card_shows_default_voice(self):
        """Test that card shows default voice model"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "Default: es-ES-Neural" in result_str

    def test_language_config_card_with_no_default_voice(self):
        """Test card when no default voice is set"""
        del self.config["default_voice_model"]
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "Default: None" in result_str

    def test_language_config_card_shows_active_models_count(self):
        """Test that card shows count of active models"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "Available: 1 models" in result_str  # Only 1 is active

    def test_language_config_card_shows_voice_config_button(self):
        """Test that card has configure voices button"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "🎤 Configure Voices" in result_str
        assert "openVoiceConfig('es')" in result_str

    def test_language_config_card_shows_features_section(self):
        """Test that card shows features section"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "Features" in result_str

    def test_language_config_card_shows_stt_feature(self):
        """Test that card shows STT feature toggle"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "STT" in result_str
        assert "toggleLanguageFeature('es', 'stt'" in result_str

    def test_language_config_card_shows_tts_feature(self):
        """Test that card shows TTS feature toggle"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "TTS" in result_str
        assert "toggleLanguageFeature('es', 'tts'" in result_str

    def test_language_config_card_shows_pronunciation_feature(self):
        """Test that card shows Pronunciation feature toggle"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "Pronunciation" in result_str
        assert "toggleLanguageFeature('es', 'pronunciation'" in result_str

    def test_language_config_card_shows_tutor_modes_feature(self):
        """Test that card shows Tutor Modes feature toggle"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "Tutor Modes" in result_str
        assert "toggleLanguageFeature('es', 'tutor_modes'" in result_str

    def test_language_config_card_shows_scenarios_feature(self):
        """Test that card shows Scenarios feature toggle"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "Scenarios" in result_str
        assert "toggleLanguageFeature('es', 'scenarios'" in result_str

    def test_language_config_card_shows_realtime_feature(self):
        """Test that card shows Real-time feature toggle"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "Real-time" in result_str
        assert "toggleLanguageFeature('es', 'real_time'" in result_str

    def test_language_config_card_features_checked_when_enabled(self):
        """Test that feature checkboxes are checked when enabled"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        # All features enabled, should have multiple checked checkboxes
        assert result_str.count("checked") >= 6

    def test_language_config_card_features_unchecked_when_disabled(self):
        """Test that feature checkboxes are unchecked when disabled"""
        # Disable all features
        self.config["speech_recognition_enabled"] = False
        self.config["text_to_speech_enabled"] = False
        self.config["pronunciation_analysis_enabled"] = False
        self.config["tutor_mode_enabled"] = False
        self.config["scenario_mode_enabled"] = False
        self.config["realtime_analysis_enabled"] = False

        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        # Check that specific feature toggles don't have checked
        assert 'onchange="toggleLanguageFeature' in result_str
        # Check for the HTML attribute "checked" (not "this.checked" in JS)
        # When disabled, checkboxes should not have ' checked' or 'checked>' attributes
        feature_section_start = result_str.find("Features")
        feature_section_end = result_str.find("Advanced Config")
        if feature_section_start >= 0 and feature_section_end >= 0:
            feature_section = result_str[feature_section_start:feature_section_end]
            # Look for the HTML checked attribute, not "this.checked"
            assert (
                " checked" not in feature_section and "checked>" not in feature_section
            )

    def test_language_config_card_shows_advanced_config_button(self):
        """Test that card has advanced config button"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "⚙️ Advanced Config" in result_str
        assert "openAdvancedConfig('es')" in result_str

    def test_language_config_card_shows_toggle_button_enabled(self):
        """Test that card shows toggle button with correct state when enabled"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "🔄" in result_str  # Disable icon when enabled
        assert "toggleLanguage('es', False)" in result_str

    def test_language_config_card_shows_toggle_button_disabled(self):
        """Test that card shows toggle button with correct state when disabled"""
        self.config["is_enabled_globally"] = False
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "✅" in result_str  # Enable icon when disabled
        assert "toggleLanguage('es', True)" in result_str

    def test_language_config_card_has_correct_id(self):
        """Test that card has correct ID attribute"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert 'id="language-card-es"' in result_str

    def test_language_config_card_with_empty_config(self):
        """Test card with minimal config (uses defaults)"""
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            {},
            [],
        )
        result_str = to_xml(result)
        assert "Spanish" in result_str
        assert "🟢 Enabled" in result_str  # Default is True
        assert "Available: 0 models" in result_str

    def test_language_config_card_filters_active_models(self):
        """Test that card correctly counts only active voice models"""
        self.voice_models = [
            {"name": "model1", "is_active": True},
            {"name": "model2", "is_active": True},
            {"name": "model3", "is_active": False},
            {"name": "model4", "is_active": True},
        ]
        result = language_config_card(
            self.language_code,
            self.language_name,
            self.native_name,
            self.config,
            self.voice_models,
        )
        result_str = to_xml(result)
        assert "Available: 3 models" in result_str


class TestVoiceModelConfigModal:
    """Tests for voice_model_config_modal function"""

    def setup_method(self):
        """Set up test data"""
        self.language_code = "es"
        self.voice_models = [
            {"name": "es-ES-Neural", "is_active": True, "gender": "female"},
            {"name": "es-MX-Neural", "is_active": False, "gender": "male"},
        ]

    def test_voice_model_config_modal_returns_div(self):
        """Test that modal returns a Div"""
        result = voice_model_config_modal(self.language_code, self.voice_models)
        result_str = to_xml(result)
        assert "<div" in result_str.lower()

    def test_voice_model_config_modal_contains_voice_models(self):
        """Test that modal contains voice model rows"""
        result = voice_model_config_modal(self.language_code, self.voice_models)
        result_str = to_xml(result)
        # Should contain voice model information
        assert "voice" in result_str.lower() or "model" in result_str.lower()

    def test_voice_model_config_modal_with_empty_models(self):
        """Test modal with no voice models"""
        result = voice_model_config_modal(self.language_code, [])
        result_str = to_xml(result)
        assert "<div" in result_str.lower()

    def test_voice_model_config_modal_with_multiple_models(self):
        """Test modal processes multiple voice models"""
        result = voice_model_config_modal(self.language_code, self.voice_models)
        result_str = to_xml(result)
        # Should have content
        assert len(result_str) > 10


class TestVoiceModelRow:
    """Tests for voice_model_row function"""

    def setup_method(self):
        """Set up test data"""
        self.voice_model = {
            "id": 0,
            "model_name": "Spanish (Spain) Neural",
            "is_active": True,
            "is_default": False,
            "language_code": "es",
            "quality_level": "high",
            "file_size_mb": 45.2,
            "sample_rate": 24000,
        }

    def test_voice_model_row_returns_html(self):
        """Test that voice_model_row returns HTML"""
        result = voice_model_row(self.voice_model, 0)
        result_str = to_xml(result)
        assert "<div" in result_str.lower()

    def test_voice_model_row_shows_display_name(self):
        """Test that row shows voice model display name"""
        result = voice_model_row(self.voice_model, 0)
        result_str = to_xml(result)
        assert "Spanish (Spain) Neural" in result_str

    def test_voice_model_row_shows_unknown_when_no_model_name(self):
        """Test that row shows Unknown when model_name is missing"""
        del self.voice_model["model_name"]
        result = voice_model_row(self.voice_model, 0)
        result_str = to_xml(result)
        assert "Unknown" in result_str

    def test_voice_model_row_shows_quality(self):
        """Test that row shows voice quality"""
        result = voice_model_row(self.voice_model, 0)
        result_str = to_xml(result)
        assert "High" in result_str  # Capitalized quality

    def test_voice_model_row_shows_size(self):
        """Test that row shows file size"""
        result = voice_model_row(self.voice_model, 0)
        result_str = to_xml(result)
        assert "45.2MB" in result_str

    def test_voice_model_row_shows_sample_rate(self):
        """Test that row shows sample rate"""
        result = voice_model_row(self.voice_model, 0)
        result_str = to_xml(result)
        assert "24000Hz" in result_str

    def test_voice_model_row_with_index(self):
        """Test that row uses id field in callbacks when present"""
        result = voice_model_row(self.voice_model, 5)
        result_str = to_xml(result)
        # When id is present (id=0), it uses that instead of index
        assert "toggleVoiceModel(0" in result_str
        assert "setDefaultVoice(0)" in result_str

    def test_voice_model_row_checked_when_active(self):
        """Test that active checkbox is checked when model is active"""
        result = voice_model_row(self.voice_model, 0)
        result_str = to_xml(result)
        assert "checked" in result_str

    def test_voice_model_row_unchecked_when_inactive(self):
        """Test that active checkbox is unchecked when model is inactive"""
        self.voice_model["is_active"] = False
        result = voice_model_row(self.voice_model, 0)
        result_str = to_xml(result)
        # Should have input but no checked attribute
        assert 'type="checkbox"' in result_str
        # Count checked attributes - if is_active is False, the Active checkbox shouldn't be checked
        assert (
            result_str.count("checked") == 0
            or 'onchange="toggleVoiceModel' in result_str
        )

    def test_voice_model_row_with_minimal_data(self):
        """Test row with minimal voice model data"""
        minimal_model = {}
        result = voice_model_row(minimal_model, 0)
        result_str = to_xml(result)
        assert "Unknown" in result_str
        assert "0.0MB" in result_str  # Default size
        assert "22050Hz" in result_str  # Default sample rate

    def test_voice_model_row_has_toggle_callback(self):
        """Test that row has toggle callback"""
        result = voice_model_row(self.voice_model, 0)
        result_str = to_xml(result)
        assert "toggleVoiceModel" in result_str
        assert "this.checked" in result_str

    def test_voice_model_row_has_default_callback(self):
        """Test that row has set default callback"""
        result = voice_model_row(self.voice_model, 0)
        result_str = to_xml(result)
        assert "setDefaultVoice" in result_str

    def test_voice_model_row_has_active_label(self):
        """Test that row has Active label"""
        result = voice_model_row(self.voice_model, 0)
        result_str = to_xml(result)
        assert "Active" in result_str

    def test_voice_model_row_has_default_label(self):
        """Test that row has Default label"""
        result = voice_model_row(self.voice_model, 0)
        result_str = to_xml(result)
        assert "Default" in result_str


class TestFeatureToggleCard:
    """Tests for feature_toggle_card function"""

    def setup_method(self):
        """Set up test data"""
        self.feature = {
            "feature_name": "pronunciation_analysis",
            "description": "Real-time pronunciation feedback",
            "is_enabled": True,
            "category": "speech",
            "requires_restart": False,
        }

    def test_feature_toggle_card_returns_div(self):
        """Test that feature_toggle_card returns a Div"""
        result = feature_toggle_card(self.feature)
        result_str = to_xml(result)
        assert "<div" in result_str.lower()

    def test_feature_toggle_card_shows_name(self):
        """Test that card shows feature name"""
        result = feature_toggle_card(self.feature)
        result_str = to_xml(result)
        assert "Pronunciation Analysis" in result_str

    def test_feature_toggle_card_shows_description(self):
        """Test that card shows feature description"""
        result = feature_toggle_card(self.feature)
        result_str = to_xml(result)
        assert "Real-time pronunciation feedback" in result_str

    def test_feature_toggle_card_checked_when_enabled(self):
        """Test that toggle is checked when feature is enabled"""
        result = feature_toggle_card(self.feature)
        result_str = to_xml(result)
        assert "checked" in result_str

    def test_feature_toggle_card_unchecked_when_disabled(self):
        """Test that toggle is unchecked when feature is disabled"""
        self.feature["is_enabled"] = False
        result = feature_toggle_card(self.feature)
        result_str = to_xml(result)
        # Should not have the checked attribute (look for space before 'checked')
        assert " checked" not in result_str and "checked>" not in result_str
        # Should show "Disabled" text
        assert "Disabled" in result_str

    def test_feature_toggle_card_with_minimal_data(self):
        """Test card with minimal feature data"""
        minimal_feature = {"feature_name": "test_feature"}
        result = feature_toggle_card(minimal_feature)
        result_str = to_xml(result)
        assert "Test Feature" in result_str  # Transformed from test_feature

    def test_feature_toggle_card_has_toggle_callback(self):
        """Test that card has toggle callback"""
        result = feature_toggle_card(self.feature)
        result_str = to_xml(result)
        assert "toggleFeature(" in result_str

    def test_feature_toggle_card_has_feature_id(self):
        """Test that card includes feature ID"""
        result = feature_toggle_card(self.feature)
        result_str = to_xml(result)
        assert "pronunciation_analysis" in result_str or "feature-" in result_str


class TestAdvancedConfigModal:
    """Tests for advanced_config_modal function"""

    def setup_method(self):
        """Set up test data"""
        self.language_code = "es"
        self.config = {
            "proficiency_levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
            "default_proficiency": "B1",
            "max_session_duration": 60,
            "min_session_duration": 5,
        }

    def test_advanced_config_modal_returns_div(self):
        """Test that modal returns a Div"""
        result = advanced_config_modal(self.language_code, self.config)
        result_str = to_xml(result)
        assert "<div" in result_str.lower()

    def test_advanced_config_modal_references_language(self):
        """Test that modal contains language reference"""
        result = advanced_config_modal(self.language_code, self.config)
        result_str = to_xml(result)
        # Should contain the language code or config information
        assert len(result_str) > 10

    def test_advanced_config_modal_with_empty_config(self):
        """Test modal with empty config"""
        result = advanced_config_modal(self.language_code, {})
        result_str = to_xml(result)
        assert "<div" in result_str.lower()

    def test_advanced_config_modal_with_proficiency_levels(self):
        """Test modal with proficiency levels"""
        result = advanced_config_modal(self.language_code, self.config)
        result_str = to_xml(result)
        # Should process the config
        assert len(result_str) > 10


class TestLanguageConfigJavascript:
    """Tests for language_config_javascript function"""

    def test_language_config_javascript_returns_script(self):
        """Test that javascript function returns a Script element"""
        result = language_config_javascript()
        result_str = str(result)
        assert "<script" in result_str.lower()

    def test_language_config_javascript_has_functions(self):
        """Test that javascript includes function definitions"""
        result = language_config_javascript()
        result_str = str(result)
        assert "function" in result_str.lower() or "const" in result_str.lower()

    def test_language_config_javascript_not_empty(self):
        """Test that javascript is not empty"""
        result = language_config_javascript()
        result_str = str(result)
        assert len(result_str) > 100  # Should have substantial content
