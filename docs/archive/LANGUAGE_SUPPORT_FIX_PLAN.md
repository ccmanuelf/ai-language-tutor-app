# Language Support Fix Plan - Session 126 Priority 1

## Executive Summary

**CRITICAL GAP IDENTIFIED**: The application currently supports only 5-6 hardcoded languages (English, Spanish, French, German, Chinese, Japanese) but should support learning ANY available language, including English itself.

**GOOD NEWS**: Italian and Portuguese TTS voices ARE ALREADY INSTALLED but not exposed to users!

**FIX SCOPE**: Add 2 fully-supported languages (Italian, Portuguese) immediately, document 3 STT-only languages (Japanese, Korean, Russian/Hindi/Arabic as future enhancements), and make the system extensible for future language additions without code changes.

## Language Capability Assessment (COMPLETED)

### TTS Service (Piper) - Voice Files Available

✅ **FULLY SUPPORTED (Native TTS + STT)**:
1. English (en) - `en_US-lessac-medium.onnx`
2. Spanish (es) - `es_MX-claude-high.onnx` (+ 3 other variants)
3. French (fr) - `fr_FR-siwis-medium.onnx`
4. German (de) - `de_DE-thorsten-medium.onnx`
5. **Italian (it)** - `it_IT-paola-medium.onnx` ✨ ALREADY INSTALLED!
6. **Portuguese (pt)** - `pt_BR-faber-medium.onnx` ✨ ALREADY INSTALLED!
7. Chinese (zh) - `zh_CN-huayan-medium.onnx`

⚠️ **LIMITED SUPPORT (STT Only, TTS Fallback to English)**:
8. Japanese (ja) - STT works, TTS uses English voice
9. Korean (ko) - STT works, TTS uses English voice

❌ **NOT AVAILABLE (Future Enhancement)**:
10. Russian (ru) - No TTS voice files, STT available
11. Hindi (hi) - No TTS voice files, STT available
12. Arabic (ar) - No TTS voice files, STT available

### STT Service (Mistral)

✅ All 12 target languages supported (30+ languages total)

## 6 CORE Languages Status

**User Requirement**: "It is REALLY important that at least the 6 CORE languages (English, Spanish, French, German, Chinese, Japanese) are FULLY functional and FULLY validated."

| Language | TTS | STT | Status |
|----------|-----|-----|--------|
| English | ✅ Native | ✅ | FULL SUPPORT |
| Spanish | ✅ Native | ✅ | FULL SUPPORT |
| French | ✅ Native | ✅ | FULL SUPPORT |
| German | ✅ Native | ✅ | FULL SUPPORT |
| Chinese | ✅ Native | ✅ | FULL SUPPORT |
| Japanese | ⚠️ Fallback | ✅ | LIMITED (STT only) |

**Issue**: Japanese does NOT have native TTS. User must be informed and accept this limitation.

## Implementation Plan

### Phase 1: Quick Wins - Expose Italian & Portuguese (1-2 hours)

**These languages are ALREADY WORKING in code but hidden from users!**

1. ✅ Update `init_sample_data.py`:
   - Add Italian: `("it", "Italian", "Italiano", True, True, True)`
   - Add Portuguese: `("pt", "Portuguese", "Português", True, True, True)`

2. ✅ Update `app/models/database.py`:
   - Add `ITALIAN = "it"` to LanguageCode enum
   - Add `PORTUGUESE = "pt"` to LanguageCode enum

3. ✅ Update `app/models/schemas.py`:
   - Add `it = "it"` to LanguageEnum
   - Add `pt = "pt"` to LanguageEnum

4. ✅ Verify Piper TTS service mapping (already exists):
   ```python
   "it": "it_IT-paola-medium",
   "pt": "pt_BR-faber-medium",
   ```

### Phase 2: Add Support Level Field (2-3 hours)

**Make language capabilities transparent to users and the system.**

1. ✅ Update Language model in `app/models/database.py`:
   ```python
   support_level = Column(Enum("FULL", "STT_ONLY", "FUTURE", name="support_level"), nullable=False, default="FULL")
   ```

2. ✅ Create migration to add support_level column

3. ✅ Update `init_sample_data.py` with support levels:
   - FULL: en, es, fr, de, it, pt, zh
   - STT_ONLY: ja, ko
   - FUTURE: (not in database yet, but documented)

4. ✅ Update API responses to include support_level

### Phase 3: Make System Extensible (3-4 hours)

**Remove hardcoded validation, make dynamic based on database.**

1. ✅ Update `app/models/database.py`:
   - Keep LanguageCode enum for backwards compatibility
   - Add validation that checks database instead of enum
   - Add comment: "# Note: New languages can be added via database without code changes"

2. ✅ Update `app/models/schemas.py`:
   - Make LanguageEnum dynamic or deprecate strict validation
   - Allow any 2-letter ISO 639-1 code that exists in database

3. ✅ Update language validation in API endpoints:
   - Change from: `if language not in LanguageCode`
   - Change to: `if not language_exists_in_db(language)`

4. ✅ Create utility function `get_supported_languages()` that queries database

### Phase 4: Documentation & User Communication (1 hour)

1. ✅ Create `LANGUAGE_SUPPORT.md` with:
   - Full matrix of what each language supports
   - Clear explanation of FULL vs STT_ONLY vs FUTURE
   - Instructions for adding new languages in future

2. ✅ Update API documentation to reflect language support levels

3. ✅ Add UI message for LIMITED languages:
   - "Japanese: Speech recognition available, text-to-speech uses English voice"

### Phase 5: Comprehensive Re-validation (4-6 hours)

**User Requirement**: "If this correction requires to re-assess and re-test all previous features, let's do it as it cannot be assumed to be covered if the languages were not available at that time."

1. ✅ Re-run ALL 61 existing E2E tests (baseline: must remain passing)

2. ✅ Test conversations with Italian:
   - Create new conversation
   - Send messages
   - Verify AI responses

3. ✅ Test conversations with Portuguese:
   - Same as Italian

4. ✅ Test scenarios in 7 FULL languages (en, es, fr, de, it, pt, zh):
   - Shopping scenario
   - Restaurant scenario
   - Business scenario
   - Cultural scenario

5. ✅ Test speech services in 7 FULL languages:
   - TTS generation (verify correct voice)
   - STT transcription
   - Pronunciation feedback

6. ✅ Test visual learning in 7 FULL languages:
   - Grammar flowcharts
   - Progress visualizations
   - Visual vocabulary
   - Pronunciation guides

7. ✅ Test Japanese LIMITED support:
   - STT works
   - TTS uses English fallback (document behavior)
   - User sees appropriate warning

### Phase 6: Update Session Planning (30 minutes)

1. ✅ Update `DAILY_PROMPT_TEMPLATE.md`:
   - Move language fix to Priority 1 (COMPLETED)
   - Add new section: "Language Support Matrix"
   - Keep Priority 2 features as next phase

2. ✅ Create Session 126 focus:
   - Language support fix and validation
   - Do NOT proceed to Priority 2 until complete

## Success Criteria

### Must Have (Blocking)
- [ ] Italian fully functional (TTS + STT)
- [ ] Portuguese fully functional (TTS + STT)
- [ ] All 61 E2E tests passing
- [ ] 6 CORE languages validated (English, Spanish, French, German, Chinese, Japanese*)
  - *Japanese documented as STT_ONLY with user warning
- [ ] System extensible (can add languages via database only)
- [ ] Support level field implemented and working

### Should Have (High Priority)
- [ ] Conversations tested in Italian and Portuguese
- [ ] Scenarios tested in 7 FULL languages
- [ ] Speech services tested in 7 FULL languages
- [ ] Visual learning tested in 7 FULL languages
- [ ] Documentation complete (LANGUAGE_SUPPORT.md)

### Nice to Have (Documentation)
- [ ] Korean documented as STT_ONLY (if time permits)
- [ ] Future enhancement notes for Russian, Hindi, Arabic

## Rollback Plan

If issues arise:
1. Revert `init_sample_data.py` changes
2. Remove Italian/Portuguese from enums
3. Keep existing 6 languages
4. User data will NOT be affected (backwards compatible)

## Estimated Timeline

- **Phase 1**: 1-2 hours (Quick wins)
- **Phase 2**: 2-3 hours (Support level field)
- **Phase 3**: 3-4 hours (Extensibility)
- **Phase 4**: 1 hour (Documentation)
- **Phase 5**: 4-6 hours (Re-validation)
- **Phase 6**: 30 minutes (Planning)

**Total**: 11.5-16.5 hours (2 work days)

## Next Immediate Steps

1. Start with Phase 1 (Italian & Portuguese exposure)
2. Run database initialization
3. Test basic functionality
4. Proceed to Phase 2 if no issues

## Notes

- **DO NOT over-engineer**: Focus on the 7 FULL + 2 LIMITED languages
- **DO NOT add Russian/Hindi/Arabic**: No TTS voices available (future enhancement only)
- **DO implement support_level**: Critical for transparency
- **DO make extensible**: Per user requirement
- **DO re-validate everything**: Per user requirement

---

**Created**: 2025-12-16
**Status**: READY TO IMPLEMENT
**Priority**: P1 (BLOCKS all Priority 2 work)
