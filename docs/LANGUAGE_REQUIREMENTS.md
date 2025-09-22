# Language Requirements Specification
**AI Language Tutor App - Core Functionality Requirements**

**Last Updated**: September 22, 2025  
**Status**: MANDATORY - Core Functionality Requirements  
**Priority**: CRITICAL - Must be validated in all tasks  

---

## 🎯 **CORE LANGUAGE REQUIREMENTS (MANDATORY)**

These languages MUST be validated and confirmed working as part of expected CORE functionality:

### **1. English (REQUIRED)**
**Primary Variant**: American US English (`en-US`)
- **Code**: `en`, `en-US`
- **Voice Models**: `en_US-lessac-medium` (primary)
- **Status**: ✅ IMPLEMENTED
- **Validation**: REQUIRED in all speech tests

**Secondary Variants**: British UK English
- **Code**: `en-GB` 
- **Voice Models**: TBD (optional enhancement)
- **Status**: Optional - not required for core functionality
- **Note**: Canadian (`en-CA`) and Australian (`en-AU`) are optional

### **2. Spanish (REQUIRED)**
**Primary Variant**: Mexican Latin American Spanish ONLY
- **Code**: `es`, `es-MX`
- **Voice Models**: `es_MX-claude-high` (primary), `es_MX-ald-medium` (secondary)
- **Status**: ✅ IMPLEMENTED
- **Validation**: REQUIRED in all speech tests
- **Note**: European Spanish (`es-ES`) available but not required for core

### **3. French (REQUIRED)**
**Primary Variant**: European French
- **Code**: `fr`, `fr-FR`
- **Voice Models**: `fr_FR-siwis-medium` (primary)
- **Status**: ✅ IMPLEMENTED
- **Validation**: REQUIRED in all speech tests

**Secondary Variant**: Canadian French
- **Code**: `fr-CA`
- **Voice Models**: TBD (optional enhancement)
- **Status**: Optional - encouraged but not required for core

### **4. German (REQUIRED)**
**Variant**: Standard German
- **Code**: `de`, `de-DE`
- **Voice Models**: `de_DE-thorsten-medium` (primary)
- **Status**: ✅ IMPLEMENTED
- **Validation**: REQUIRED in all speech tests
- **Note**: Austrian (`de-AT`) and Swiss (`de-CH`) are optional

### **5. Chinese (REQUIRED)**
**Variant**: Simplified Chinese with standard accent
- **Code**: `zh`, `zh-CN`
- **Voice Models**: `zh_CN-huayan-medium` (primary)
- **Status**: ✅ IMPLEMENTED
- **Validation**: REQUIRED in all speech tests
- **Note**: Traditional Chinese (`zh-TW`) and Hong Kong (`zh-HK`) are optional

---

## 🔄 **OPTIONAL LANGUAGES (ENCOURAGED)**

### **6. Portuguese (OPTIONAL)**
**Primary Variant**: Brazilian Portuguese
- **Code**: `pt`, `pt-BR`
- **Voice Models**: `pt_BR-faber-medium` (available)
- **Status**: ✅ AVAILABLE
- **Validation**: Optional - test when convenient

**Secondary Variant**: European Portuguese
- **Code**: `pt-PT`
- **Voice Models**: TBD (future enhancement)
- **Status**: Not implemented - optional enhancement

### **7. Italian (OPTIONAL)**
**Variant**: Standard Italian
- **Code**: `it`, `it-IT`
- **Voice Models**: `it_IT-paola-medium` (primary), `it_IT-riccardo-x_low` (backup)
- **Status**: ✅ AVAILABLE
- **Validation**: Optional - test when convenient

### **8. Japanese (OPTIONAL - ENCOURAGED)**
**Variant**: Standard Japanese
- **Code**: `ja`, `ja-JP`
- **Voice Models**: TBD (currently falls back to English)
- **Status**: NOT IMPLEMENTED - encouraged future enhancement
- **Priority**: High optional - large user base potential

### **9. Korean (OPTIONAL - ENCOURAGED)**
**Variant**: Standard Korean
- **Code**: `ko`, `ko-KR`
- **Voice Models**: TBD (currently falls back to English)
- **Status**: NOT IMPLEMENTED - encouraged future enhancement
- **Priority**: High optional - growing user base

---

## ✅ **CURRENT IMPLEMENTATION STATUS**

### **✅ FULLY IMPLEMENTED (Core Requirements)**
1. **English** (`en-US`): `en_US-lessac-medium` ✅
2. **Spanish** (`es-MX`): `es_MX-claude-high`, `es_MX-ald-medium` ✅
3. **French** (`fr-FR`): `fr_FR-siwis-medium` ✅
4. **German** (`de-DE`): `de_DE-thorsten-medium` ✅
5. **Chinese** (`zh-CN`): `zh_CN-huayan-medium` ✅

### **✅ AVAILABLE (Optional)**
6. **Portuguese** (`pt-BR`): `pt_BR-faber-medium` ✅
7. **Italian** (`it-IT`): `it_IT-paola-medium`, `it_IT-riccardo-x_low` ✅

### **❌ NOT IMPLEMENTED (Optional - Encouraged)**
8. **Japanese** (`ja-JP`): No native voice (falls back to English) ❌
9. **Korean** (`ko-KR`): No native voice (falls back to English) ❌

### **❌ NOT IMPLEMENTED (Optional Variants)**
- British English (`en-GB`)
- Canadian French (`fr-CA`)
- European Portuguese (`pt-PT`)

---

## 🧪 **VALIDATION REQUIREMENTS**

### **🔊 CRITICAL AUDIO PLAYBACK REQUIREMENT**
**🚨 MANDATORY: All language validation MUST include actual audio playback testing**

**File generation alone is INSUFFICIENT for validation. Each language MUST:**
- ✅ Generate valid audio file (WAV format, ≥16kHz, >0.5s duration)
- 🔊 **PLAY audio through system speakers for auditory verification**
- 👂 **Confirm audio is audible, clear, and correctly pronounced**
- ⏭️ **Sequential playback (one by one) to prevent system timeouts**

**Audio playback failures are considered CRITICAL validation failures that block task completion.**

### **Mandatory Language Testing**
ALL core functionality tests MUST include validation of these 5 languages:

```python
CORE_LANGUAGES = [
    ("en", "Hello world"),           # English (US)
    ("es", "Hola mundo"),           # Spanish (Mexican)
    ("fr", "Bonjour le monde"),     # French (European)
    ("de", "Hallo Welt"),           # German (Standard)
    ("zh", "你好世界")               # Chinese (Simplified)
]
```

**🎵 AUDIO PLAYBACK PROTOCOL:**
```python
# MANDATORY: Each language must be played sequentially
for lang, text in CORE_LANGUAGES:
    audio_file = generate_tts(text, lang)
    play_audio_file(audio_file)  # REQUIRED - must hear through speakers
    verify_audible_output()      # REQUIRED - human verification
    time.sleep(1)               # Prevent system conflicts
```

### **Optional Language Testing**
When time permits, include these optional languages:

```python
OPTIONAL_LANGUAGES = [
    ("pt", "Olá mundo"),            # Portuguese (Brazilian)
    ("it", "Ciao mondo"),           # Italian (Standard)
    ("ja", "こんにちは世界"),         # Japanese (fallback to English)
    ("ko", "안녕 세상")              # Korean (fallback to English)
]
```

### **Quality Gates Language Requirements**
**Gate 4 (Language Validation)** must validate:
- ✅ All 5 core languages produce valid audio output
- 🔊 **All 5 core languages play successfully through speakers**
- ✅ Audio duration >0.5s for each core language
- ✅ Sample rate ≥16kHz for each core language
- ✅ No errors or fallbacks for core languages
- ⏭️ Sequential playback without system timeouts

---

## 📊 **LANGUAGE PRIORITY MATRIX**

| Language | Code | Status | Priority | Voice Quality | Validation |
|----------|------|---------|-----------|---------------|------------|
| English (US) | en-US | ✅ CORE | CRITICAL | High | MANDATORY |
| Spanish (MX) | es-MX | ✅ CORE | CRITICAL | High | MANDATORY |
| French (EU) | fr-FR | ✅ CORE | CRITICAL | Medium | MANDATORY |
| German | de-DE | ✅ CORE | CRITICAL | Medium | MANDATORY |
| Chinese | zh-CN | ✅ CORE | CRITICAL | Medium | MANDATORY |
| Portuguese (BR) | pt-BR | ✅ Optional | Medium | Medium | OPTIONAL |
| Italian | it-IT | ✅ Optional | Medium | Medium | OPTIONAL |
| Japanese | ja-JP | ❌ Missing | High Optional | N/A | FUTURE |
| Korean | ko-KR | ❌ Missing | High Optional | N/A | FUTURE |

---

## 🎯 **IMPLEMENTATION ROADMAP**

### **Phase 1: Core Language Validation (CURRENT)**
- ✅ Validate all 5 core languages working correctly
- ✅ Ensure quality gates test all core languages
- ✅ Document voice model assignments
- ✅ Test STT and TTS for all core languages

### **Phase 2: Japanese Voice Implementation (FUTURE)**
- [ ] Research and acquire Japanese voice models for Piper TTS
- [ ] Implement `ja-JP` language support
- [ ] Validate Japanese STT with Mistral Voxtral
- [ ] Add Japanese to core testing suite

### **Phase 3: Korean Voice Implementation (FUTURE)**
- [ ] Research and acquire Korean voice models for Piper TTS
- [ ] Implement `ko-KR` language support
- [ ] Validate Korean STT with Mistral Voxtral
- [ ] Add Korean to core testing suite

### **Phase 4: Language Variant Expansion (FUTURE)**
- [ ] British English (`en-GB`)
- [ ] Canadian French (`fr-CA`)
- [ ] European Portuguese (`pt-PT`)

---

## 🔧 **VOICE MODEL SPECIFICATIONS**

### **Current Voice Model Inventory**
```
CORE LANGUAGES (MANDATORY):
- en_US-lessac-medium.onnx (63.2MB) - English (US)
- es_MX-claude-high.onnx (63.1MB) - Spanish (Mexican) - Primary
- es_MX-ald-medium.onnx (63.2MB) - Spanish (Mexican) - Secondary
- fr_FR-siwis-medium.onnx (63.2MB) - French (European)
- de_DE-thorsten-medium.onnx (63.2MB) - German (Standard)
- zh_CN-huayan-medium.onnx (63.2MB) - Chinese (Simplified)

OPTIONAL LANGUAGES (AVAILABLE):
- pt_BR-faber-medium.onnx (63.2MB) - Portuguese (Brazilian)
- it_IT-paola-medium.onnx (63.5MB) - Italian (Standard) - Primary
- it_IT-riccardo-x_low.onnx (28.1MB) - Italian (Standard) - Backup

ADDITIONAL MODELS:
- es_ES-davefx-medium.onnx (63.2MB) - Spanish (European) - Available but not core
- es_AR-daniela-high.onnx (114.2MB) - Spanish (Argentinian) - Available but not core
```

### **Missing Voice Models (Future Enhancement)**
- Japanese (`ja-JP`) - High priority optional
- Korean (`ko-KR`) - High priority optional
- British English (`en-GB`) - Medium priority optional
- Canadian French (`fr-CA`) - Medium priority optional
- European Portuguese (`pt-PT`) - Low priority optional

---

## 📋 **TESTING PROTOCOL**

### **Core Language Validation Test**
```python
# This MUST pass for any task completion
def test_core_languages():
    core_tests = [
        ("en", "Hello, this is a test of English speech synthesis."),
        ("es", "Hola, esta es una prueba de síntesis de voz en español mexicano."),
        ("fr", "Bonjour, ceci est un test de synthèse vocale française."),
        ("de", "Hallo, dies ist ein Test der deutschen Sprachsynthese."),
        ("zh", "你好，这是中文语音合成的测试。")
    ]
    
    for lang, text in core_tests:
        result = await tts_service.synthesize(text, lang)
        assert result.success, f"Core language {lang} failed"
        assert len(result.audio_data) > 1024, f"Core language {lang} insufficient output"
        assert result.duration_seconds > 0.5, f"Core language {lang} too short"
```

### **Optional Language Validation Test**
```python
# This is optional but encouraged
def test_optional_languages():
    optional_tests = [
        ("pt", "Olá, este é um teste de síntese de voz em português brasileiro."),
        ("it", "Ciao, questo è un test di sintesi vocale italiana."),
        ("ja", "Hello, Japanese voice model not available yet."),  # Fallback
        ("ko", "Hello, Korean voice model not available yet.")     # Fallback
    ]
    
    for lang, text in optional_tests:
        try:
            result = await tts_service.synthesize(text, lang)
            print(f"Optional language {lang}: {'SUCCESS' if result.success else 'FALLBACK'}")
        except Exception as e:
            print(f"Optional language {lang}: ERROR - {e}")
```

---

## 🏆 **SUCCESS CRITERIA**

### **Core Functionality Requirements**
✅ **All 5 core languages must work correctly**  
✅ **Audio output quality must be consistent across core languages**  
✅ **STT and TTS must function for all core languages**  
✅ **No fallbacks or errors for core languages**  
✅ **Performance must be consistent across core languages**

### **Quality Metrics**
- Audio duration: >0.5s per language
- Sample rate: ≥16kHz per language
- File size: >1KB per language output
- Processing time: <2s per language
- Success rate: 100% for core languages

---

**This specification ensures that the AI Language Tutor App delivers on its core promise of multilingual language learning support with the specific language variants that are most valuable to the target user base.**