# AI Language Tutor - User Guide

> **Your Family's Personal Language Learning Assistant**

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [For Parents - Setting Up the Family](#for-parents---setting-up-the-family)
3. [For Learners - Using the Tutor](#for-learners---using-the-tutor)
4. [Features Guide](#features-guide)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### What is the AI Language Tutor?

The AI Language Tutor is your family's personal language learning companion that provides:

- **Natural Conversations** - Talk with AI tutors in 7 languages
- **Speech Practice** - Improve pronunciation with real-time feedback
- **Visual Learning** - Generate images to reinforce vocabulary
- **Personalized Progress** - Track improvement over time
- **Family-Friendly** - Safe, ad-free environment for all ages

### Supported Languages

| Language | Speech Recognition | Speech Synthesis | AI Conversation |
|----------|-------------------|------------------|-----------------|
| 🇺🇸 English | ✅ | ✅ | ✅ |
| 🇪🇸 Spanish | ✅ | ✅ | ✅ |
| 🇫🇷 French | ✅ | ✅ | ✅ |
| 🇩🇪 German | ✅ | ✅ | ✅ |
| 🇮🇹 Italian | ✅ | ✅ | ✅ |
| 🇵🇹 Portuguese | ✅ | ✅ | ✅ |
| 🇨🇳 Chinese (Mandarin) | ✅ | ✅ | ✅ |

---

## 👨‍👩‍👧‍👦 For Parents - Setting Up the Family

### Step 1: Initial System Setup

**Prerequisites:**
- Computer with Python 3.12+ installed
- Internet connection for AI services
- Microphone for speech practice (optional but recommended)

**Quick Start:**
```bash
# 1. Clone or download the application
cd ai-language-tutor-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment (see Step 2 below)
cp .env.example .env
nano .env  # Edit with your settings

# 4. Start the application
python run_backend.py  # In one terminal
python run_frontend.py  # In another terminal
```

### Step 2: Configure Your Account

**Create your `.env` file** (this is your private configuration):

```bash
# ==========================================
# ADMIN SETUP (Required for parent/admin)
# ==========================================

# Your admin email (for managing the family account)
ADMIN_EMAIL=your-email@example.com

# Your admin username
ADMIN_USERNAME=Mom

# Your admin password (choose a strong password!)
ADMIN_PASSWORD=YourSecurePassword123!

# ==========================================
# AI SERVICE KEYS (Mistral Primary - Cost-Conscious)
# ==========================================

# Get your API keys from these providers:

# Mistral AI (PRIMARY - REQUIRED for cost-effective AI + speech)
# https://console.mistral.ai
MISTRAL_API_KEY=your-mistral-key

# Anthropic Claude (SECONDARY - Optional for premium quality)
# https://console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# DeepSeek (OPTIONAL - Chinese language specialist)
# https://platform.deepseek.com
DEEPSEEK_API_KEY=sk-your-deepseek-key

# Ollama (LOCAL FALLBACK - Recommended for budget/offline/privacy)
# Free local LLM, zero API costs, automatic fallback
# Install: https://ollama.ai/ then run: ollama pull mistral
OLLAMA_HOST=http://localhost:11434

# ==========================================
# SPEECH SERVICES (Built-in - No API keys needed!)
# ==========================================

# Speech Recognition: Mistral STT (included)
# Text-to-Speech: Piper TTS (included)
# No additional configuration required!

# ==========================================
# OPTIONAL FEATURES
# ==========================================

# Visual learning (image generation)
ENABLE_VISUAL_LEARNING=true

# Budget limits (to control API costs)
ENABLE_BUDGET_MANAGEMENT=true
```

### Step 3: Create User Accounts for Family Members

**Access the Admin Dashboard:**

1. Open your browser to `http://localhost:3000`
2. Click **"Admin Dashboard"** in the navigation
3. Log in with your ADMIN_EMAIL and ADMIN_PASSWORD

**Add Family Members:**

1. In the Admin Dashboard, navigate to **"User Management"**
2. Click **"Create New User"**
3. Fill in the details:
   ```
   Username: Sofia
   Email: sofia@family.local  (or use real email)
   Password: SafePassword123!
   Is Admin: ☐ (unchecked for regular users)
   ```
4. Click **"Create User"**
5. Repeat for each family member (wife, kids, etc.)

**Example Family Setup:**
- **Mom** (you) - Admin account
- **Sofia** (daughter) - Regular user, learning Spanish
- **Lucas** (son) - Regular user, learning French
- **Maria** (wife) - Regular user, learning Italian

### Step 4: Configure Learning Preferences

**For Each User:**

1. Log in as the user
2. Go to **"Settings"** → **"Language Preferences"**
3. Select:
   - **Target Language** (e.g., Spanish)
   - **Proficiency Level** (Beginner, Intermediate, Advanced)
   - **Learning Goals** (Conversation, Travel, Business)
   - **Speech Settings** (Enable/disable voice features)

---

## 🎓 For Learners - Using the Tutor

### Starting a Conversation

**Option 1: Quick Start (Text Chat)**

1. Log in to your account
2. Select a language from the dropdown
3. Click **"Start Learning"**
4. Begin typing your messages!

**Option 2: Voice Conversation**

1. Log in and select your language
2. Click the **🎤 Microphone** icon
3. Speak naturally in your target language
4. The AI will respond with text and speech!

### Choosing a Learning Scenario

The tutor offers different conversation scenarios:

| Scenario | Best For | Description |
|----------|----------|-------------|
| 🍽️ **Restaurant Ordering** | Beginners | Practice ordering food and drinks |
| 🏨 **Hotel Check-in** | Travel | Learn hotel and accommodation vocabulary |
| 🛒 **Shopping** | Practical | Shopping conversations and negotiations |
| 🚕 **Directions** | Navigation | Asking for and giving directions |
| 👋 **Introductions** | Social | Meeting people and introductions |
| 📞 **Phone Calls** | Business | Professional phone conversations |
| 🏥 **Doctor Visit** | Essential | Medical and health vocabulary |

**How to Select:**
1. Click **"Choose Scenario"**
2. Pick from the list
3. The AI adapts to that context!

### Using Visual Learning

**Generate Images for Vocabulary:**

1. During conversation, type: *"Show me an image of [word]"*
2. Example: "Show me an image of 'la manzana'"
3. The system generates a visual to help remember!

**When to Use:**
- Learning new nouns (objects, animals, food)
- Understanding cultural concepts
- Visual memory reinforcement

### Tracking Your Progress

**View Your Progress:**

1. Click **"My Progress"** in the navigation
2. See your:
   - Total conversation time
   - Messages sent/received
   - Scenarios completed
   - Vocabulary learned
   - Pronunciation scores (if using speech)

**Weekly Goals:**
- Set daily/weekly practice goals
- Get reminders to practice
- Celebrate milestones!

---

## 🎯 Features Guide

### 1. AI Conversation Partners (Smart Cost-Conscious Routing)

**AI Models (Priority Order):**
- **Mistral** (PRIMARY) - Cost-effective for all languages, natural conversations
- **Claude (Anthropic)** (SECONDARY) - Premium quality when budget allows
- **Ollama** (LOCAL FALLBACK) - Free, offline-capable, privacy-focused
- **DeepSeek** (SPECIALIST) - Chinese language optimization, ultra-low-cost

**Conversation Modes:**
- **Beginner Mode** - Simple vocabulary, slow pace
- **Intermediate Mode** - Conversational flow
- **Advanced Mode** - Native-like complexity

### 2. Speech Recognition & Synthesis

**Voice Practice:**
- Speak naturally - no typing required!
- Real-time pronunciation feedback
- Native-quality voice responses

**Supported Features:**
- Accent detection
- Pronunciation scoring
- Intonation analysis
- Speed adjustment

### 3. Visual Learning System

**Image Generation:**
- Vocabulary illustration
- Cultural context images
- Scenario visualization

**How It Works:**
- Request an image during conversation
- AI generates educational illustration
- Image saved to your learning history

### 4. Budget Management (For Parents)

**Cost Control:**
- Set monthly spending limits
- Per-user budget allocation
- Real-time usage tracking
- Email alerts for budget thresholds

**Access Budget Dashboard:**
1. Admin Dashboard → Budget Management
2. View all family usage
3. Set limits and policies

---

## 🛠️ Troubleshooting

### Common Issues

**Problem: Cannot log in**
- **Solution**: Verify your email/password in the admin dashboard
- Check that user account is active

**Problem: No speech recognition**
- **Solution**: 
  - Check microphone permissions in browser
  - Verify Mistral API key in `.env`
  - Test microphone in browser settings
  - Ensure microphone is not being used by another app

**Problem: Slow AI responses**
- **Solution**:
  - Check internet connection
  - Verify API keys are valid
  - Try switching AI model (Claude → Mistral)

**Problem: Images not generating**
- **Solution**:
  - Ensure `ENABLE_VISUAL_LEARNING=true` in `.env`
  - Check API key for image provider
  - Verify sufficient budget remaining

### Getting Help

**Check the Documentation:**
- `docs/DEPLOYMENT_READINESS_ASSESSMENT.md` - Production setup
- `docs/PRODUCTION_CONFIGURATION_CHECKLIST.md` - Configuration guide
- `docs/API_KEYS_SETUP_GUIDE.md` - API key setup (in archive)

**For Parents:**
- Admin Dashboard has built-in help sections
- Check logs in `logs/backend.log` for errors

---

## 📊 Usage Best Practices

### For Maximum Learning

**Daily Practice:**
- 15-30 minutes per day is ideal
- Short sessions better than long, infrequent ones
- Use different scenarios to avoid monotony

**Speech Practice:**
- Start with text, gradually add voice
- Don't worry about perfection - practice makes progress!
- Use slow speech mode for difficult words

**Family Learning:**
- Practice together during meals
- Create friendly competitions
- Share interesting phrases you learned

### Cost Management Tips

**Optimize API Usage:**
- Set realistic budgets for each user
- Use text more than speech for budget control
- Monitor usage weekly in admin dashboard

**Free & Low-Cost Options:**
- **Ollama**: 100% free local LLM (runs on your computer)
- **Piper TTS**: Completely free (runs locally)
- **Mistral**: Cost-effective primary provider
- **Mistral STT**: Included with Mistral API
- Anthropic: Free tier available for testing

---

## 🎉 Fun Family Activities

### Weekly Challenges

**Challenge 1: Restaurant Night**
- Everyone practices restaurant scenario
- Order a real meal in target language
- Track who uses the most vocabulary!

**Challenge 2: Story Time**
- Create a story together in target language
- Each person adds one sentence
- Use visual learning for illustrations

**Challenge 3: Translation Race**
- Parents give phrases to translate
- Kids race to respond correctly
- Winner picks next week's scenario!

---

## 📞 Support & Updates

**Application Updates:**
- Check GitHub for latest version
- Follow `README.md` for update instructions

**Community:**
- Share your learning journey
- Contribute improvements
- Report bugs via GitHub Issues

---

**Happy Learning! 🎓📚🌍**

*Your family's journey to multilingual mastery starts here!*
