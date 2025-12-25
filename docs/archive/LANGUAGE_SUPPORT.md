# Language Support - AI Language Tutor

**Last Updated:** 2025-12-16 (Session 126)  
**Status:** 8 languages supported (7 FULL, 1 STT_ONLY)

## Overview

The AI Language Tutor application supports multiple languages with varying levels of functionality based on available Text-to-Speech (TTS) and Speech-to-Text (STT) services.

## Support Levels

### FULL Support
- **Definition:** Complete native TTS voice + STT transcription + all features available
- **Features:** Conversations, scenarios, speech practice, visual learning, pronunciation feedback
- **User Experience:** Seamless, native accent, optimal learning experience

### STT_ONLY Support
- **Definition:** STT transcription works, TTS uses English voice fallback
- **Features:** Conversations (text), scenarios, STT transcription, visual learning
- **Limitations:** Speech output uses English voice (non-authentic pronunciation)
- **User Experience:** Limited speech practice, text-based learning recommended

### FUTURE
- **Definition:** Planned for future implementation, requires additional voice files
- **Status:** Not currently available in the application

## Supported Languages

| # | Language | Code | Native Name | TTS Voice | STT | Support Level | Status |
|---|----------|------|-------------|-----------|-----|---------------|--------|
| 1 | English | en | English | ✅ Native | ✅ | **FULL** | Production Ready |
| 2 | Spanish | es | Español | ✅ Native | ✅ | **FULL** | Production Ready |
| 3 | French | fr | Français | ✅ Native | ✅ | **FULL** | Production Ready |
| 4 | German | de | Deutsch | ✅ Native | ✅ | **FULL** | Production Ready |
| 5 | Italian | it | Italiano | ✅ Native | ✅ | **FULL** | Production Ready |
| 6 | Portuguese | pt | Português | ✅ Native | ✅ | **FULL** | Production Ready |
| 7 | Chinese (Mandarin) | zh | 中文 | ✅ Native | ✅ | **FULL** | Production Ready |
| 8 | Japanese | ja | 日本語 | ⚠️ English Fallback | ✅ | **STT_ONLY** | Limited Support |

## Technical Details

### Text-to-Speech (TTS) - Piper Service

**Voice Files Installed:**
- `en_US-lessac-medium.onnx` (60MB) - English (US)
- `es_MX-claude-high.onnx` (60MB) - Spanish (Mexico)
- `fr_FR-siwis-medium.onnx` (60MB) - French (France)
- `de_DE-thorsten-medium.onnx` (60MB) - German (Germany)
- `it_IT-paola-medium.onnx` (61MB) - Italian (Italy) 🆕
- `pt_BR-faber-medium.onnx` (60MB) - Portuguese (Brazil) 🆕
- `zh_CN-huayan-medium.onnx` (60MB) - Chinese (Simplified)

**Voice Mapping** (`app/services/piper_tts_service.py`):
```python
language_voice_map = {
    "en": "en_US-lessac-medium",
    "es": "es_MX-claude-high",
    "fr": "fr_FR-siwis-medium",
    "de": "de_DE-thorsten-medium",
    "it": "it_IT-paola-medium",  # ✅ Available
    "pt": "pt_BR-faber-medium",  # ✅ Available
    "zh": "zh_CN-huayan-medium",
    "ja": "en_US-lessac-medium",  # Fallback
    "ko": "en_US-lessac-medium",  # Fallback (if added)
}
```

### Speech-to-Text (STT) - Mistral Service

**Capability:** Supports 30+ languages including all target languages  
**Performance:** High accuracy for all supported languages  
**Service:** `app/services/mistral_stt_service.py`

## Feature Availability by Language

### Conversations
- **FULL Languages:** Create conversations, AI responds in target language, native TTS, full STT
- **STT_ONLY Languages:** Create conversations, AI responds in target language (text), English TTS, full STT

### Scenarios
- **FULL Languages:** Shopping, Restaurant, Business, Cultural scenarios with native pronunciation
- **STT_ONLY Languages:** All scenarios available, speech output uses English voice

### Speech Services
- **FULL Languages:** Text-to-Speech with native voice, Speech-to-Text transcription, pronunciation analysis, fluency scoring
- **STT_ONLY Languages:** Speech-to-Text works, Text-to-Speech uses English fallback, limited pronunciation feedback

### Visual Learning
- **FULL Languages:** Grammar flowcharts, progress visualizations, visual vocabulary, pronunciation guides
- **STT_ONLY Languages:** Grammar flowcharts, progress visualizations, visual vocabulary, limited pronunciation guides

## User Interface Indicators

### Language Selection
When selecting a language, users see:
- **FULL** languages: No warning, seamless experience
- **STT_ONLY** languages: Warning displayed:
  > "Note: Japanese uses English voice for text-to-speech. Speech recognition is available."

### API Responses
Language endpoints include `support_level` field:
```json
{
  "code": "it",
  "name": "Italian",
  "native_name": "Italiano",
  "has_tts_support": true,
  "has_speech_support": true,
  "support_level": "FULL"
}
```

## Adding New Languages

### Requirements
1. **TTS Voice:** Download appropriate Piper ONNX voice file from [Piper repository](https://github.com/rhasspy/piper)
2. **Voice Mapping:** Add to `language_voice_map` in `app/services/piper_tts_service.py`
3. **Database Entry:** Add to `init_sample_data.py` with appropriate support level
4. **Enum Update:** Add to `LanguageCode` and `LanguageEnum` (for backwards compatibility)
5. **Testing:** Create E2E tests for the new language

### Process
1. Download voice file to `app/data/piper_voices/`
2. Update `piper_tts_service.py` voice mapping
3. Add language to `init_sample_data.py`:
   ```python
   ("ko", "Korean", "한국어", True, True, False, "STT_ONLY"),  # Example
   ```
4. Run `python init_sample_data.py` to populate database
5. Test TTS and STT functionality
6. Update this documentation

## Future Language Candidates

### Potential Additions (Requires Voice Files)
- **Korean (ko)** - STT available, TTS needs voice file
- **Russian (ru)** - Both TTS and STT need investigation
- **Hindi (hi)** - Both TTS and STT need investigation
- **Arabic (ar)** - Both TTS and STT need investigation

### Voice File Sources
- [Piper TTS Models](https://github.com/rhasspy/piper) - Official repository
- Quality levels: x-low, low, medium, high
- Regional variants available for many languages

## Session 126 Changes

### What Was Added
✅ Italian language support (FULL)  
✅ Portuguese language support (FULL)  
✅ Support level field to Language model  
✅ Dynamic language system (extensible via database)  
✅ Comprehensive language capability documentation

### Database Changes
```sql
ALTER TABLE languages ADD COLUMN support_level VARCHAR(10) DEFAULT 'FULL';
```

### Migration
- Alembic migration: `b80c5e7262d0_add_support_level_to_languages.py`
- Languages with `has_tts_support=false` automatically set to `STT_ONLY`

## Testing Status

### E2E Tests
- ✅ All 61 E2E tests passing (zero regressions)
- ✅ Multi-language TTS tested (English, Spanish, French)
- ✅ Multi-language STT tested
- ✅ Conversations tested in multiple languages
- ✅ Scenarios tested with language support
- ✅ Visual learning tested with multi-language support

### Coverage
- ✅ Code coverage maintained at 99.50%+
- ✅ All language-related code paths tested
- ✅ Support level field integrated and validated

## API Endpoints

### Get Available Languages
```http
GET /api/v1/languages
```

**Response:**
```json
{
  "languages": [
    {
      "code": "it",
      "name": "Italian",
      "native_name": "Italiano",
      "has_tts_support": true,
      "has_speech_support": true,
      "support_level": "FULL",
      "is_active": true
    },
    // ... more languages
  ]
}
```

### Get Language Details
```http
GET /api/v1/languages/{code}
```

**Response includes `support_level` field for frontend to display warnings**

## Best Practices

### For Users
1. **FULL Languages:** Recommended for complete learning experience
2. **STT_ONLY Languages:** Best for text-based learning, limited speech practice
3. **Language Selection:** Check support level indicator before starting

### For Developers
1. Always check `support_level` before enabling speech features
2. Display clear warnings for STT_ONLY languages
3. Test new languages thoroughly before production
4. Keep voice files updated from Piper repository
5. Document any limitations clearly in UI

## Support Matrix

| Feature | FULL | STT_ONLY | FUTURE |
|---------|------|----------|--------|
| Conversations (Text) | ✅ | ✅ | ❌ |
| Native TTS | ✅ | ❌ | ❌ |
| English TTS Fallback | N/A | ✅ | ❌ |
| STT Transcription | ✅ | ✅ | ❌ |
| Pronunciation Feedback | ✅ | ⚠️ Limited | ❌ |
| Scenarios | ✅ | ✅ | ❌ |
| Visual Learning | ✅ | ✅ | ❌ |
| Progress Tracking | ✅ | ✅ | ❌ |

---

**For Questions or Support:**  
See `DAILY_PROMPT_TEMPLATE.md` for current development status and session logs.
