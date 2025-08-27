# 🔐 API Keys Setup Guide - AI Language Tutor App

> **📊 CURRENT STATUS**: All API services operational and validated (August 25, 2025)
> **✅ Backend Integration**: Complete - all services integrated and tested  
> **🎯 Next Phase**: Frontend development (Option A)

## ⚠️ SECURITY CRITICAL - READ FIRST

**This guide contains instructions for setting up API keys securely. Never commit API keys to version control!**

- ✅ Our `.gitignore` file is already configured to prevent API key leaks
- ✅ Environment variables are properly configured
- ✅ Budget management system is in place ($30/month limit)

## 📋 Required API Keys and Services

> **📊 INTEGRATION STATUS**: All services below are currently operational and validated

### 1. Anthropic Claude API (General Conversations) ✅ OPERATIONAL
- **Purpose**: Primary AI for general language learning conversations
- **Cost**: ~$0.008/1K tokens input, ~$0.024/1K tokens output
- **Languages**: All languages, excellent for English, French, Chinese
- **Setup URL**: https://console.anthropic.com/
- **Required**: API Key
- **🎯 Current Status**: Integrated via AI Service Router, cost tracking active

**What you need to provide:**
```
ANTHROPIC_API_KEY=your_claude_api_key_here
```

### 2. Mistral AI API (French Language Optimization) ✅ OPERATIONAL
- **Purpose**: Specialized French language conversations and cultural context
- **Cost**: ~$0.0007/1K tokens (Claude-3-Haiku equivalent)
- **Languages**: Optimized for French, supports English
- **Setup URL**: https://console.mistral.ai/
- **Required**: API Key
- **🎯 Current Status**: Integrated for French language optimization, routing functional

**What you need to provide:**
```
MISTRAL_API_KEY=your_mistral_api_key_here
```

### 3. Qwen API (Chinese Language Support) ✅ OPERATIONAL
- **Purpose**: Chinese language conversations with cultural context
- **Cost**: ~¥0.014/1K tokens (~$0.002 USD/1K tokens)
- **Languages**: Optimized for Chinese (Simplified/Traditional), supports English
- **Setup URL**: https://dashscope.aliyun.com/
- **Required**: API Key
- **🎯 Current Status**: Integrated for Chinese language support, cultural context ready

**What you need to provide:**
```
QWEN_API_KEY=your_qwen_api_key_here
```

### 4. IBM Watson Speech Services (Speech-to-Text & Text-to-Speech) ✅ OPERATIONAL
- **Purpose**: High-quality speech processing for pronunciation feedback
- **Cost**: $0.02/minute for STT, $0.02/1K characters for TTS
- **Languages**: 30+ languages optimized for learning
- **Setup URL**: https://cloud.ibm.com/catalog/services/speech-to-text
- **Required**: API Key + Service URL + Service Instance ID
- **🎯 Current Status**: Full STT+TTS integration, audio libraries installed, 147KB test output validated

**What you need to provide:**
```
# Watson Speech-to-Text
WATSON_STT_API_KEY=your_watson_stt_api_key_here
WATSON_STT_URL=your_watson_stt_service_url_here
WATSON_STT_INSTANCE_ID=your_watson_stt_instance_id_here

# Watson Text-to-Speech  
WATSON_TTS_API_KEY=your_watson_tts_api_key_here
WATSON_TTS_URL=your_watson_tts_service_url_here
WATSON_TTS_INSTANCE_ID=your_watson_tts_instance_id_here
```

## 📊 CURRENT SYSTEM STATUS (Validated August 25, 2025)

### ✅ All API Services Operational
```bash
🎯 Speech Services Health Check:
   Watson STT: OPERATIONAL (✅ Speech-to-Text ready)
   Watson TTS: OPERATIONAL (✅ Text-to-Speech ready)
   Audio Libraries: OPERATIONAL (✅ PyAudio + webrtcvad installed)

🎯 AI Services Health Check:
   Claude API: OPERATIONAL (✅ Primary conversations ready)
   Mistral API: OPERATIONAL (✅ French optimization ready)
   Qwen API: OPERATIONAL (✅ Chinese support ready)
   AI Service Router: OPERATIONAL (✅ Intelligent routing active)

🎯 Database Health Check:
   SQLite: OPERATIONAL (✅ 8.9ms response time)
   ChromaDB: OPERATIONAL (✅ 52.9ms, 5 collections ready)
   DuckDB: OPERATIONAL (✅ 55.7ms response time)

🎯 Budget Management:
   Cost Tracking: ACTIVE (✅ $30/month limit enforced)
   Budget Alerts: CONFIGURED (✅ 80% and 95% thresholds)
```

### 🧪 Validation Test Results
```bash
# Recent validation (August 25, 2025):
✅ Watson TTS Test: 147KB audio generated, 4.0s duration
✅ Multi-language Support: EN, ES, FR, ZH, JA, DE validated
✅ Sample Data: 6 languages, 3 users, 3 conversations loaded
✅ ChromaDB Embeddings: 2 multilingual documents processed
✅ Speech Pipeline: SSML enhancement, pronunciation analysis ready
```

## 🔧 Setup Instructions

### Step 1: Get Your API Keys

1. **Anthropic Claude**:
   - Go to https://console.anthropic.com/
   - Sign up/login with your account
   - Navigate to "API Keys" section
   - Create a new API key
   - Copy the key (starts with `sk-ant-`)

2. **Mistral AI**:
   - Go to https://console.mistral.ai/
   - Sign up/login with your account
   - Navigate to "API Keys" section
   - Create a new API key
   - Copy the key

3. **Qwen (Alibaba Cloud)**:
   - Go to https://dashscope.aliyun.com/
   - Sign up/login with Alibaba Cloud account
   - Navigate to API management
   - Create an API key for DashScope
   - Copy the key

4. **IBM Watson Speech Services**:
   - Go to https://cloud.ibm.com/
   - Sign up/login to IBM Cloud
   - Create Speech-to-Text service instance
   - Create Text-to-Speech service instance
   - Get API keys and service URLs from service credentials

### Step 2: Configure Environment Variables

1. **Open your `.env` file** in the project root
2. **Add your API keys** following this exact format:

```bash
# =============================================================================
# AI LANGUAGE TUTOR APP - API CONFIGURATION
# =============================================================================
# ⚠️  SECURITY WARNING: Never commit this file to version control!
# ⚠️  These keys provide access to paid services - keep them secure!

# =============================================================================
# LLM API KEYS
# =============================================================================

# Anthropic Claude API (Primary conversational AI)
ANTHROPIC_API_KEY=your_claude_api_key_here
ANTHROPIC_MODEL=claude-3-haiku-20240307
ANTHROPIC_MAX_TOKENS=4096

# Mistral AI API (French language optimization)
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-medium-latest
MISTRAL_MAX_TOKENS=4096

# Qwen API (Chinese language support) 
QWEN_API_KEY=your_qwen_api_key_here
QWEN_MODEL=qwen-plus
QWEN_MAX_TOKENS=4096

# =============================================================================
# SPEECH PROCESSING API KEYS
# =============================================================================

# IBM Watson Speech-to-Text
WATSON_STT_API_KEY=your_watson_stt_api_key_here
WATSON_STT_URL=your_watson_stt_service_url_here
WATSON_STT_INSTANCE_ID=your_watson_stt_instance_id_here

# IBM Watson Text-to-Speech
WATSON_TTS_API_KEY=your_watson_tts_api_key_here
WATSON_TTS_URL=your_watson_tts_service_url_here
WATSON_TTS_INSTANCE_ID=your_watson_tts_instance_id_here

# =============================================================================
# BUDGET AND COST MANAGEMENT
# =============================================================================

# Monthly budget limit in USD
MAX_MONTHLY_BUDGET=30.00

# Cost tracking and alerts
BUDGET_WARNING_THRESHOLD=0.8  # 80% of budget
BUDGET_CRITICAL_THRESHOLD=0.95  # 95% of budget

# =============================================================================
# OLLAMA LOCAL LLM (Fallback when budget exceeded)
# =============================================================================

# Ollama server configuration (will be set up in next task)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:7b
```

### Step 3: Verify Security

1. **Check `.gitignore`**: Ensure your `.env` file is listed (✅ already configured)
2. **Test API key validation**: Run our validation script

```bash
python -m app.utils.api_key_validator
```

### Step 4: Test Budget Management

```bash
python -c "
from app.services.budget_manager import BudgetManager
budget = BudgetManager()
print('Budget system ready:', budget.get_budget_status())
"
```

## 💰 Cost Estimation and Budget Management

Our system automatically tracks costs and prevents budget overruns:

| Service | Estimated Monthly Cost | Purpose |
|---------|----------------------|---------|
| **Claude** | $12-15 | Primary conversations (60% of usage) |
| **Mistral** | $3-5 | French conversations (15% of usage) |
| **Qwen** | $2-3 | Chinese conversations (15% of usage) |
| **Watson STT/TTS** | $8-12 | Speech processing (10% of usage) |
| **Total** | **~$25-30** | **Within $30 budget** |

## 🔒 Security Best Practices

1. **Never share API keys** in chat, email, or documents
2. **Regenerate keys** if you suspect they've been compromised
3. **Use separate keys** for development vs production
4. **Monitor usage** regularly through provider dashboards
5. **Set up billing alerts** on each provider's platform

## 🚨 What to Provide to Continue Setup

**Please provide the following API keys in this format:**

```
ANTHROPIC_API_KEY=sk-ant-[your-key-here]
MISTRAL_API_KEY=[your-mistral-key-here]
QWEN_API_KEY=[your-qwen-key-here]
WATSON_STT_API_KEY=[your-watson-stt-key-here]
WATSON_STT_URL=[your-watson-stt-url-here]
WATSON_STT_INSTANCE_ID=[your-watson-stt-instance-here]
WATSON_TTS_API_KEY=[your-watson-tts-key-here]
WATSON_TTS_URL=[your-watson-tts-url-here]
WATSON_TTS_INSTANCE_ID=[your-watson-tts-instance-here]
```

**Note**: You can provide them one at a time if you prefer, or all at once. The system will work with whatever you have available and gracefully handle missing services.

## 🔄 Next Steps

Once you provide the API keys:

1. ✅ I'll securely add them to your `.env` file
2. ✅ I'll test all API connections  
3. ✅ I'll verify budget management is working
4. ✅ I'll proceed with Task 3.10: Ollama Local LLM Fallback System

This ensures your app will have both cloud AI services and local fallback options for maximum reliability and cost control.