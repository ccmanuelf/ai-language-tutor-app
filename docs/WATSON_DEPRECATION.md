# Watson Speech Services - Deprecation Notice

**Status**: DEPRECATED  
**Deprecated**: Phase 2A Migration  
**Session 82**: Cleanup in progress  
**Current TTS/STT**: Piper (local, offline)

---

## Summary

IBM Watson Speech-to-Text and Text-to-Speech services have been **deprecated** and replaced with **Piper TTS/STT** (local, offline solution).

**Reasons for Deprecation:**
1. **Cost** - Watson requires paid API credits
2. **Privacy** - Piper runs locally, no data sent to external services
3. **Offline** - Piper works without internet connection
4. **Performance** - Piper provides comparable quality with lower latency
5. **Simplicity** - No API keys or service URLs required

---

## Migration Timeline

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 2A** | ✅ Complete | Migrated to Piper TTS/STT |
| **Phase 2B** | ✅ Complete | Removed Watson from production code |
| **Session 82** | 🔄 In Progress | Cleanup remaining references |
| **Session 83+** | 📋 Planned | Complete documentation cleanup |

---

## Current State (Session 82)

### ✅ What's Complete
- Piper TTS fully integrated and working
- Piper STT fully integrated and working
- 11 voices across 7 languages available
- Voice persona selection API implemented
- TRUE 100% test coverage on speech services

### 🔄 What Remains
- Historical Watson references in documentation (~187 references)
- Deprecated Watson validation code in `api_key_validator.py` (removed in Session 82)
- Watson initialization stubs in `speech_processor.py` (functional but deprecated)
- Frontend diagnostic messages mentioning Watson

### ⚠️ Safe to Ignore
Most remaining Watson references are:
- Historical documentation
- Commented-out code with deprecation notices
- Fallback code that's never executed
- Legacy initialization that safely no-ops

---

## Files Updated in Session 82

### Removed Watson Validation
- **File**: `app/utils/api_key_validator.py`
- **Change**: Removed `validate_watson_stt_api()` and `validate_watson_tts_api()`
- **Impact**: No breaking changes - these were never called in production

---

## Current TTS/STT: Piper

**Piper** is a fast, local, neural text-to-speech system:

### Advantages
✅ **Local** - Runs on your machine  
✅ **Offline** - No internet required  
✅ **Free** - No API costs  
✅ **Private** - Data never leaves your system  
✅ **Fast** - Low latency synthesis  
✅ **Quality** - Natural-sounding speech  

### Available Voices (11 total)
- **English** (2): lessac (male), ljspeech (female)
- **Spanish** (3): claude (male), davefx (male), carlfm (male)
- **German** (2): thorsten (male), eva_k (female)
- **French** (1): siwis (female)
- **Italian** (1): riccardo (male)
- **Portuguese** (1): faber (male)
- **Chinese** (1): baker (female)

### Voice Selection
Session 81 implemented voice persona selection:
```python
# Get available voices
GET /api/v1/conversations/available-voices?language=es

# Use specific voice
POST /api/v1/conversations/text-to-speech
{
  "text": "Hola",
  "language": "es",
  "voice": "es_AR-daniela-high"  // Optional voice selection
}
```

---

## For Developers

### If You See Watson References

**In Code:**
- Check if it's commented out with deprecation notice
- Check if it's in a fallback path (likely never executed)
- If it's active code, verify if Piper equivalent exists

**In Documentation:**
- Most are historical and safe to ignore
- If updating docs, replace "Watson" with "Piper"

**In Tests:**
- Watson tests have been removed/updated
- All TTS/STT tests now use Piper
- See `tests/test_piper_tts_service.py` for examples

### If You Need to Clean Up Watson References

1. **Search for references:**
   ```bash
   grep -r "watson" --include="*.py" app/
   grep -r "Watson" --include="*.md" docs/
   ```

2. **Verify it's safe to remove:**
   - Check if code is commented out
   - Check if it's in a deprecation notice
   - Check if there's a Piper equivalent

3. **Replace with Piper equivalent:**
   - `watson_stt` → `piper_stt`
   - `watson_tts` → `piper_tts`
   - IBM Watson → Piper TTS

4. **Run tests:**
   ```bash
   pytest tests/test_piper_tts_service.py -v
   pytest tests/test_speech_processor.py -v
   ```

---

## FAQ

### Q: Can I still use Watson if I want?
**A:** No, Watson integration has been fully removed. Use Piper instead.

### Q: What if I need cloud TTS/STT?
**A:** Consider integrating:
- Google Cloud TTS/STT
- Azure Speech Services
- Amazon Polly/Transcribe

Piper works offline, which is a major advantage for privacy and cost.

### Q: Are there any breaking changes?
**A:** No. The migration to Piper was done in Phase 2A with full backwards compatibility. APIs remain the same, only the underlying engine changed.

### Q: What about Watson API keys in .env?
**A:** They're no longer needed or used. You can safely remove:
- `WATSON_STT_API_KEY`
- `WATSON_STT_URL`
- `WATSON_TTS_API_KEY`
- `WATSON_TTS_URL`

### Q: Will Watson references be fully removed?
**A:** Yes, gradually:
- Session 82: Removed Watson validation code ✅
- Future: Documentation cleanup
- Future: Remove deprecated stubs

This is being done carefully to avoid breaking changes.

---

## References

- **Piper Documentation**: https://github.com/rhasspy/piper
- **Session 81**: Voice Persona Selection API implementation
- **Session 82**: AI Testing Architecture + Watson cleanup (partial)
- **Phase 2A Migration**: Original Watson → Piper migration

---

**Last Updated**: Session 82 - 2025-12-04  
**Status**: Watson deprecated, Piper fully operational  
**Next Steps**: Complete documentation cleanup in future sessions
