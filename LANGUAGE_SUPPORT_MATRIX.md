# Language Support Matrix - Current Status

**Last Updated**: 2025-12-16
**Session**: 126 (Priority 1 - Critical Gap Fix)

## Overview

This document provides a comprehensive overview of language support capabilities in the AI Language Tutor application based on available TTS (Text-to-Speech) and STT (Speech-to-Text) services.

## Support Level Definitions

- **FULL**: Native TTS voice + STT transcription + All features available
- **STT_ONLY**: STT transcription works, TTS falls back to English voice
- **FUTURE**: Not currently implemented, requires additional voice files

## Language Capabilities Matrix

| # | Language | Code | TTS Voice | STT | Support Level | Features Available |
|---|----------|------|-----------|-----|---------------|-------------------|
| 1 | English | en | ✅ en_US-lessac-medium | ✅ | **FULL** | Conversations, Scenarios, Speech, Visual Learning |
| 2 | Spanish | es | ✅ es_MX-claude-high | ✅ | **FULL** | Conversations, Scenarios, Speech, Visual Learning |
| 3 | French | fr | ✅ fr_FR-siwis-medium | ✅ | **FULL** | Conversations, Scenarios, Speech, Visual Learning |
| 4 | German | de | ✅ de_DE-thorsten-medium | ✅ | **FULL** | Conversations, Scenarios, Speech, Visual Learning |
| 5 | Italian | it | ✅ it_IT-paola-medium | ✅ | **FULL** | Conversations, Scenarios, Speech, Visual Learning |
| 6 | Portuguese | pt | ✅ pt_BR-faber-medium | ✅ | **FULL** | Conversations, Scenarios, Speech, Visual Learning |
| 7 | Chinese | zh | ✅ zh_CN-huayan-medium | ✅ | **FULL** | Conversations, Scenarios, Speech, Visual Learning |
| 8 | Japanese | ja | ⚠️ English fallback | ✅ | **STT_ONLY** | Conversations, Scenarios, STT only |
| 9 | Korean | ko | ⚠️ English fallback | ✅ | **STT_ONLY** | Conversations, Scenarios, STT only |
| 10 | Russian | ru | ❌ Not available | ✅ | **FUTURE** | Would require voice file download |
| 11 | Hindi | hi | ❌ Not available | ✅ | **FUTURE** | Would require voice file download |
| 12 | Arabic | ar | ❌ Not available | ✅ | **FUTURE** | Would require voice file download |

## Current Status (Before Fix)

**Exposed to Users**: 6 languages (en, es, fr, de, zh, ja)

**Hidden but Working**: 2 languages (it, pt) - TTS voices installed but not in database!

**Total Available Now**: 8 languages could be FULL support (7 FULL + 2 STT_ONLY)

## 6 CORE Languages Validation Status

Per user requirement: "It is REALLY important that at least the 6 CORE languages (English, Spanish, French, German, Chinese, Japanese) are FULLY functional and FULLY validated."

| Language | TTS Status | STT Status | Overall Status | Notes |
|----------|------------|------------|----------------|-------|
| English | ✅ Native | ✅ Works | ✅ FULL | No issues |
| Spanish | ✅ Native | ✅ Works | ✅ FULL | No issues |
| French | ✅ Native | ✅ Works | ✅ FULL | No issues |
| German | ✅ Native | ✅ Works | ✅ FULL | No issues |
| Chinese | ✅ Native | ✅ Works | ✅ FULL | No issues |
| Japanese | ⚠️ Fallback | ✅ Works | ⚠️ LIMITED | **TTS uses English voice** |

**CRITICAL NOTE**: Japanese does NOT have native TTS. Users will hear English pronunciation when using speech features. This must be clearly communicated in the UI.

## Additional TTS Voice Files Available

The following voice variants exist but are not currently configured:

**Spanish Variants**:
- es_ES-davefx-medium (Spain Spanish)
- es_AR-daniela-high (Argentina Spanish)
- es_MX-ald-medium (Mexico Spanish, alternative)

**Italian Variants**:
- it_IT-riccardo-x_low (Alternative Italian voice, lower quality)

These could be exposed as voice options in future versions.

## Feature Support by Language Type

### FULL Support Languages (en, es, fr, de, it, pt, zh)

✅ **Conversations**:
- Create conversations in target language
- AI responds in target language
- Full native TTS for speech output
- Full STT for speech input

✅ **Scenarios**:
- Shopping, Restaurant, Business, Cultural scenarios
- Native language interactions
- Pronunciation feedback in native accent

✅ **Speech Services**:
- Text-to-Speech with native voice
- Speech-to-Text transcription
- Pronunciation analysis
- Fluency scoring

✅ **Visual Learning**:
- Grammar flowcharts
- Progress visualizations
- Visual vocabulary
- Pronunciation guides

### STT_ONLY Languages (ja, ko)

✅ **Conversations**:
- Create conversations in target language
- AI responds in target language (text)
- ⚠️ TTS uses English voice (pronunciation not authentic)
- ✅ STT for speech input works

✅ **Scenarios**:
- All scenarios available
- ⚠️ Speech output uses English voice
- ⚠️ Pronunciation feedback limited (English accent)

⚠️ **Speech Services**:
- ⚠️ Text-to-Speech uses English voice (fallback)
- ✅ Speech-to-Text transcription works
- ⚠️ Pronunciation analysis limited
- ⚠️ Fluency scoring based on transcription only

✅ **Visual Learning**:
- Grammar flowcharts (text-based, works fine)
- Progress visualizations (works fine)
- Visual vocabulary (works fine)
- ⚠️ Pronunciation guides (limited without native TTS)

### FUTURE Languages (ru, hi, ar)

❌ Not currently available. Would require:
1. Downloading appropriate Piper voice files
2. Adding to voice mapping in `app/services/piper_tts_service.py`
3. Adding to database initialization
4. Testing and validation

## Technical Details

### TTS Service: Piper

**Location**: `app/services/piper_tts_service.py`

**Voice Mapping**:
```python
self.language_voice_map = {
    "en": "en_US-lessac-medium",
    "es": "es_MX-claude-high",
    "fr": "fr_FR-siwis-medium",
    "de": "de_DE-thorsten-medium",
    "it": "it_IT-paola-medium",  # ← AVAILABLE but not exposed!
    "pt": "pt_BR-faber-medium",  # ← AVAILABLE but not exposed!
    "zh": "zh_CN-huayan-medium",
    "ja": "en_US-lessac-medium",  # Fallback
    "ko": "en_US-lessac-medium",  # Fallback
}
```

**Voice Files Directory**: `app/data/piper_voices/`

**File Format**: ONNX models with JSON config (e.g., `en_US-lessac-medium.onnx`)

### STT Service: Mistral

**Location**: `app/services/mistral_stt_service.py`

**Capability**: Supports 30+ languages including all 12 target languages

**Performance**: High accuracy for all supported languages

## Limitations & Known Issues

### Japanese & Korean
- No native TTS voice files available in Piper repository
- Current workaround: Use English voice (not ideal for learning)
- STT works perfectly
- **Recommendation**: Clearly label as "Limited Support" in UI

### Russian, Hindi, Arabic
- No TTS voice files installed
- Would require downloading from Piper repository
- Must verify voice quality before implementation
- **Status**: Future enhancement (documented for roadmap)

### Learning English
- Currently, users cannot select English as the LEARNING language
- This is a gap identified by the user
- Fix required: Allow English as a learning language (native speakers learning formal English, non-natives learning English, etc.)

## User Experience Implications

### For FULL Support Languages
- Seamless experience
- Native pronunciation
- Complete feature access
- No warnings needed

### For STT_ONLY Languages
- Must display clear warning:
  - "Note: Japanese uses English voice for text-to-speech. Speech recognition is available."
- Consider disabling certain speech-focused features
- Alternative: Offer text-only mode

### For FUTURE Languages
- Not selectable in UI
- Could be shown as "Coming Soon" with explanation
- Allow users to request priority languages

## Recommendations for Implementation

### Immediate (Session 126)
1. Expose Italian and Portuguese (voices already available)
2. Add `support_level` field to database
3. Update UI to show support level badges
4. Add warning messages for LIMITED languages

### Short-term (Session 127-128)
1. Re-validate all features with 7 FULL languages
2. Test Japanese/Korean LIMITED support
3. Document user experience for each support level
4. Create language selection UI with clear indicators

### Medium-term (Future Sessions)
1. Research Russian, Hindi, Arabic voice availability
2. Download and test voice files if available
3. Consider multiple voice options per language (male/female, regional)
4. Implement voice selection feature

### Long-term (Roadmap)
1. Periodic check for new Piper voices
2. User voting for next language priority
3. Custom voice upload (advanced feature)
4. Community-contributed language support

## Testing Requirements

### Per Language Testing (7 FULL Languages)
- [ ] Conversation creation and interaction
- [ ] All 4 scenario types (Shopping, Restaurant, Business, Cultural)
- [ ] TTS audio generation and quality
- [ ] STT transcription accuracy
- [ ] Pronunciation feedback
- [ ] Visual learning features
- [ ] Progress tracking

### Cross-Language Testing
- [ ] Switch languages mid-session
- [ ] Multiple conversations in different languages
- [ ] Language preference persistence
- [ ] API response consistency

### Regression Testing
- [ ] All 61 existing E2E tests must pass
- [ ] No existing functionality broken
- [ ] Performance not degraded

## Success Metrics

- **7 FULL languages** available to users
- **2 STT_ONLY languages** available with clear warnings
- **3 FUTURE languages** documented for roadmap
- **100% E2E test pass rate** maintained
- **System extensibility** proven (can add languages via database only)
- **User clarity** on what each language supports

---

**Status**: Assessment Complete - Ready for Implementation
**Next**: Begin Phase 1 implementation (expose Italian & Portuguese)
