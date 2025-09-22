# Environment Fix Instructions - Watson Deprecation

**Task**: 2A.4 - Watson Deprecation & Cleanup  
**Issue**: Watson API keys in .env file are no longer accepted  
**Solution**: Remove Watson configuration from your personal .env file  

---

## 🚨 **IMMEDIATE ACTION REQUIRED**

Your environment validation is failing because Watson services have been deprecated in Phase 2A. You need to remove Watson configuration from your personal `.env` file.

### **Current Error**:
```
ValidationError: 4 validation errors for Settings
IBM_WATSON_STT_API_KEY: Extra inputs are not permitted
IBM_WATSON_TTS_API_KEY: Extra inputs are not permitted  
IBM_WATSON_STT_URL: Extra inputs are not permitted
IBM_WATSON_TTS_URL: Extra inputs are not permitted
```

---

## 🔧 **STEP-BY-STEP FIX**

### **Step 1: Open Your .env File**
```bash
cd ai-language-tutor-app
nano .env  # or use your preferred editor
```

### **Step 2: Remove These Lines**
Delete or comment out these lines from your `.env` file:
```bash
# Remove these lines:
IBM_WATSON_STT_API_KEY=***REMOVED***
IBM_WATSON_TTS_API_KEY=***REMOVED***
IBM_WATSON_STT_URL=https://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/...
IBM_WATSON_TTS_URL=https://api.au-syd.text-to-speech.watson.cloud.ibm.com/instances/...
```

### **Step 3: Verify Mistral Key Exists**
Ensure this line exists in your `.env` file (required for new STT service):
```bash
MISTRAL_API_KEY=your_mistral_api_key_here
```

### **Step 4: Save and Test**
```bash
# Save the file and test
python scripts/validate_environment.py
```

---

## ✅ **EXPECTED RESULT**

After removing Watson keys, you should see:
```
🎯 VALIDATION SUMMARY
=========================
✅ PASS Python Environment: /path/to/ai-tutor-env/bin/python
✅ PASS Dependencies: 5/5 available
✅ PASS Working Directory: /path/to/ai-language-tutor-app  
✅ PASS Voice Models: 12 models
✅ PASS Service Availability: 4/4 services

Overall: 5/5 checks passed

🎉 ENVIRONMENT VALIDATION: PASSED
🎉 Safe to proceed with testing and validation
```

---

## 🎯 **WHY THIS CHANGE?**

### **Phase 2A Migration Benefits**:
- **99.8% Cost Reduction**: $0.000033 vs $0.020667 per operation
- **Better Performance**: 11x faster than real-time processing
- **Offline Capability**: Piper TTS works without internet
- **Higher Quality**: 22.05kHz audio vs Watson's defaults

### **New Speech Architecture**:
- **STT**: Mistral Voxtral (uses your existing Mistral API key)
- **TTS**: Piper (local processing, no API keys needed)
- **Languages**: All supported (en, es, fr, zh, de, it)

---

## 🛡️ **SECURITY NOTE**

Watson API keys are no longer needed and should be removed for security:

1. **Remove from .env**: Done with steps above
2. **Deactivate Keys**: Consider deactivating Watson keys in IBM Cloud Console
3. **Update Documentation**: Your local setup now uses Mistral + Piper only

---

## 🆘 **TROUBLESHOOTING**

### **If Still Getting Errors**:

1. **Check for .env.local or other env files**:
   ```bash
   find . -name "*.env*" -type f
   ```

2. **Verify virtual environment**:
   ```bash
   which python  # Should show ai-tutor-env path
   source ai-tutor-env/bin/activate  # If not active
   ```

3. **Check environment variables**:
   ```bash
   env | grep WATSON  # Should show nothing
   ```

### **If Missing Mistral Key**:
```bash
# Add to .env file:
MISTRAL_API_KEY=your_mistral_api_key_from_console_mistral_ai
```

### **If Voice Models Missing**:
```bash
pip install piper-tts
# Models should auto-download (12 models, ~150MB)
```

---

## 📞 **NEED HELP?**

If you continue to have issues:

1. **Check validation logs**: `validation_results/last_environment_validation.json`
2. **Review this report**: `validation_artifacts/2A.4/WATSON_DEPRECATION_VALIDATION_REPORT.md`
3. **Run deprecation test**: `python validation_artifacts/2A.4/test_watson_deprecation.py`

---

## 🎉 **SUCCESS CONFIRMATION**

Once the fix is complete, you'll have:
- ✅ No Watson dependencies
- ✅ Mistral STT working  
- ✅ Piper TTS working
- ✅ 99.8% cost reduction active
- ✅ All speech features preserved

**You're ready to continue with the next phase of development!**

---

**Last Updated**: September 22, 2025  
**Phase**: 2A - Speech Architecture Migration  
**Status**: User action required - remove Watson keys from .env