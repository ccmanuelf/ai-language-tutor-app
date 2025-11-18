# 🌟 AI Language Tutor App

> **A comprehensive AI-powered language learning platform with enterprise-grade speech processing, multi-LLM integration, and adaptive learning features for personalized education.**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)](https://fastapi.tiangolo.com/)
[![FastHTML](https://img.shields.io/badge/FastHTML-Frontend-red.svg)](https://fastht.ml/)
[![Testing](https://img.shields.io/badge/Test_Coverage-64%25-yellow.svg)](#testing)
[![Status](https://img.shields.io/badge/Status-Active_Development-brightgreen.svg)](#project-status)

## 🎯 Project Overview

### Mission Statement
Create a **comprehensive AI-powered learning platform** that functions as an interactive learning companion, combining conversational tutoring, real-time content processing, multimedia teaching tools, and adaptive learning paths to help users master any topic with personalized guidance.

### Core Capabilities
- **📚 Content-Based Learning**: Transform any content (videos, articles, documents) into structured learning materials
- **💬 Conversational Practice**: Scenario-based conversation practice with real-time feedback and cultural context
- **🎤 Speech Analysis**: Live pronunciation feedback, accent coaching, and speaking confidence building
- **🔁 Adaptive Learning**: Spaced repetition system with progress analytics and personalized learning paths
- **🧠 Visual Learning**: Auto-generated mind maps, diagrams, and visual aids for better comprehension
- **🌍 Multi-Language Support**: Specialized AI models for English, French, Spanish, Italian, Portuguese, German, and Chinese

## 📊 Current Status

### Phase 3A: Comprehensive Testing - TRUE 100% Validation ✅ **COMPLETE!**

**Achievement**: 17/17 critical modules at **TRUE 100% coverage** (100% statement + 100% branch)

```
✅ 1,930 tests passing
✅ 64.37% overall project coverage
✅ 0 warnings, 0 technical debt
✅ 51 branch coverage patterns documented
✅ Production-ready speech processing (STT/TTS)
✅ All 11 voice models validated
```

**Latest Milestones**:
- **Session 43** (2025-11-16): mistral_stt_service.py → TRUE 100% - Initiative complete! 🎊
- **Sessions 27-42**: Systematic validation of 16 critical modules
- **Audio Initiative**: Complete STT/TTS/speech processing validation with real audio

**Next Phase**: Expanding TRUE 100% validation to 90+ modules (see [Expansion Plan](docs/TRUE_100_PERCENT_EXPANSION_PLAN.md))

### Overall Project Progress
```
Phase 1: Foundation Infrastructure          ✅ COMPLETE
Phase 2: Core Services & Features          ✅ COMPLETE  
Phase 3A: Comprehensive Testing            ✅ COMPLETE
Phase 3B: Coverage Expansion               🚀 PLANNED (90+ modules)
Phase 4: Production Deployment             📋 FUTURE
```

## 🏛️ Technical Architecture

### Technology Stack

**Frontend Layer**:
- **FastHTML**: Python-based, server-side rendering framework
- **Port**: 3000
- **Features**: Chat interface, progress tracking, admin dashboards, visual learning tools
- **Architecture**: Modular component structure

**Backend Layer**:
- **FastAPI**: High-performance async API server
- **Port**: 8000
- **Services**: AI routing, speech processing, authentication, content analysis

**AI Services**:
- **Claude (Anthropic)**: Primary conversational AI and content analysis
- **Mistral**: Specialized for French language optimization and speech-to-text
- **Qwen**: Chinese language support and specialized tasks
- **DeepSeek**: Cost-effective alternative for specific use cases
- **Ollama**: Local AI model support (optional)

**Speech Processing**:
- **STT**: Mistral-based speech-to-text with enterprise-grade accuracy
- **TTS**: Piper TTS with 11 validated voice models across 7 languages
- **Real-time Analysis**: Pronunciation feedback and accent coaching

**Data Layer**:
- **SQLite**: Primary relational database for user data and progress
- **ChromaDB**: Vector database for semantic search and embeddings
- **DuckDB**: Analytics database for learning insights and reporting

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend Layer (FastHTML)                   │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Chat UI     │  │ Progress UI  │  │ Admin Dashboards       │ │
│  └─────────────┘  └──────────────┘  └────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP (CORS enabled)
┌───────────────────────────┴─────────────────────────────────────┐
│                    Backend Layer (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │ AI Router    │  │ Speech Proc. │  │ Content Processor   │  │
│  │ Multi-LLM    │  │ STT/TTS      │  │ Learning Materials  │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │ Auth Service │  │ SR Manager   │  │ Analytics Engine    │  │
│  │ JWT Tokens   │  │ Spaced Rep.  │  │ Progress Tracking   │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                        Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │ SQLite       │  │ ChromaDB     │  │ DuckDB              │  │
│  │ User/State   │  │ Vectors      │  │ Analytics           │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.12+ required
python --version  # Should be 3.12+

# Virtual environment (recommended)
python -m venv ai-tutor-env
```

### Installation
```bash
# Clone repository
git clone <repository-url>
cd ai-language-tutor-app

# Activate virtual environment
source ai-tutor-env/bin/activate  # On Windows: ai-tutor-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys (Claude, Mistral, Qwen)
```

### Running the Application

**Backend Server** (Terminal 1):
```bash
cd /path/to/ai-language-tutor-app
source ai-tutor-env/bin/activate
python run_backend.py
# Or directly: uvicorn app.main:app --reload --host localhost --port 8000
```

**Frontend Server** (Terminal 2):
```bash
cd /path/to/ai-language-tutor-app
source ai-tutor-env/bin/activate
python run_frontend.py
# Or directly: uvicorn app.frontend_main:frontend_app --reload --host localhost --port 3000
```

**Access Application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## 🧪 Testing

### Test Suite Overview
```bash
# Activate virtual environment first!
source ai-tutor-env/bin/activate

# Run all tests with coverage
pytest tests/ --cov=app --cov-report=term-missing -v

# Run specific test modules
pytest tests/test_conversation_persistence.py -v
pytest tests/test_mistral_stt_service.py -v

# Run with branch coverage
pytest tests/ --cov=app --cov-branch --cov-report=term-missing -v
```

### Current Test Metrics
- **Total Tests**: 1,930 tests passing
- **Overall Coverage**: 64.37% (statement)
- **TRUE 100% Modules**: 17 critical modules (100% statement + 100% branch)
- **Test Execution Time**: ~100 seconds (full suite with coverage)
- **Warnings**: 0
- **Technical Debt**: 0

### Quality Standards
- **TRUE 100% Coverage**: 100% statement + 100% branch coverage
- **Zero Warnings**: Clean test output required
- **Zero Technical Debt**: No TODOs or FIXMEs in production code
- **Real Data Testing**: No mocked core logic, actual validation
- **Pattern Documentation**: All coverage patterns documented

## 📁 Project Structure

```
ai-language-tutor-app/
├── app/
│   ├── api/                    # FastAPI routes and endpoints
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── conversations.py   # Conversation management
│   │   ├── scenarios.py       # Scenario-based learning
│   │   └── visual_learning.py # Visual learning tools
│   ├── services/              # Business logic services
│   │   ├── ai_router.py       # Multi-LLM routing and fallback
│   │   ├── mistral_stt_service.py  # Speech-to-text
│   │   ├── piper_tts_service.py    # Text-to-speech
│   │   ├── speech_processor.py     # Audio processing
│   │   ├── content_processor.py    # Content analysis
│   │   ├── scenario_manager.py     # Scenario generation
│   │   └── sr_algorithm.py         # Spaced repetition
│   ├── database/              # Database configuration
│   │   ├── config.py          # Database setup
│   │   └── migrations.py      # Schema migrations
│   ├── models/                # Data models and schemas
│   │   ├── database.py        # ORM models
│   │   └── schemas.py         # Pydantic schemas
│   ├── core/                  # Core utilities
│   │   ├── config.py          # Application config
│   │   └── security.py        # Security utilities
│   ├── frontend/              # FastHTML UI components
│   │   ├── main.py            # Frontend app factory
│   │   ├── chat.py            # Chat interface
│   │   ├── progress.py        # Progress tracking
│   │   ├── home.py            # Landing page
│   │   └── admin_dashboard.py # Admin tools
│   ├── main.py                # Backend entry point
│   └── frontend_main.py       # Frontend entry point
├── tests/                     # Test suite (1,930 tests)
├── docs/                      # Documentation
│   ├── TRUE_100_PERCENT_VALIDATION.md  # Testing initiative
│   ├── TRUE_100_PERCENT_EXPANSION_PLAN.md  # Coverage expansion
│   ├── DAILY_PROMPT_TEMPLATE.md       # Development workflow
│   └── SESSION_*_SUMMARY.md           # Session summaries
├── requirements.txt           # Python dependencies
├── pytest.ini                # Pytest configuration
└── README.md                 # This file
```

## 🎓 Core Features

### 1. Content-Based Learning
- **Input Sources**: YouTube videos, PDFs, websites, articles, user notes
- **Processing**: AI-powered content analysis and structure extraction
- **Output**: Structured learning materials with exercises and assessments
- **Languages**: Support for 7+ languages with specialized AI models

### 2. Conversational Practice
- **Scenario System**: Real-world conversation scenarios with cultural context
- **AI Tutors**: Multiple AI personalities for diverse learning experiences
- **Real-time Feedback**: Instant corrections and guidance during conversations
- **Voice Integration**: Full voice support with STT/TTS for immersive practice

### 3. Speech Analysis & Coaching
- **Pronunciation Feedback**: Real-time analysis of pronunciation accuracy
- **Accent Coaching**: Personalized guidance for accent improvement
- **Confidence Building**: Progressive difficulty levels and positive reinforcement
- **Multi-language**: 11 validated voice models across 7 languages

### 4. Adaptive Learning System
- **Spaced Repetition**: Scientific scheduling algorithm for optimal retention
- **Progress Analytics**: Detailed insights into learning patterns and progress
- **Personalized Paths**: AI-driven curriculum adaptation based on performance
- **Visual Progress**: Charts, graphs, and visual feedback on achievements

### 5. Visual Learning Tools
- **Mind Maps**: Auto-generated visual concept maps
- **Diagrams**: Relationship diagrams for complex topics
- **Flowcharts**: Process visualization for step-by-step learning
- **Integration**: Seamless integration with all learning modes

## 🔒 Security & Privacy

### Authentication & Authorization
- **JWT-based Authentication**: Secure token-based auth system
- **Role-based Access Control**: User, Admin, and Teacher roles
- **Session Management**: Secure session handling and timeout policies

### Data Protection
- **Local Storage**: All personal data stored locally (SQLite)
- **Encrypted Credentials**: Secure API key management with environment variables
- **Privacy First**: No third-party data sharing or tracking
- **Content Moderation**: AI-powered inappropriate content filtering

### API Security
- **Rate Limiting**: Protection against abuse and excessive usage
- **Input Validation**: Comprehensive request validation using Pydantic
- **CORS Configuration**: Secure cross-origin resource sharing policies
- **Error Handling**: No sensitive data exposure in error messages

## 💰 Cost Efficiency

### Multi-LLM Strategy
The platform uses multiple AI providers to optimize for both cost and quality:

- **Claude (Anthropic)**: Primary model for general conversations and content analysis
- **Mistral**: Cost-effective for French optimization and speech-to-text
- **Qwen**: Specialized for Chinese language support
- **DeepSeek**: Ultra-low-cost alternative for specific use cases
- **Ollama**: Optional local models for zero-cost operation

### Intelligent Routing
- **Provider Selection**: Automatic selection based on language, task type, and cost
- **Fallback System**: Graceful degradation to alternative providers on failure
- **Usage Tracking**: Real-time monitoring of API costs and usage patterns
- **Budget Alerts**: Automatic notifications when approaching cost thresholds

## 📖 Documentation

### Developer Documentation
- **[Development Setup](docs/DAILY_PROMPT_TEMPLATE.md)**: Complete setup and workflow guide
- **[Testing Guide](docs/TRUE_100_PERCENT_VALIDATION.md)**: TRUE 100% validation methodology
- **[Expansion Plan](docs/TRUE_100_PERCENT_EXPANSION_PLAN.md)**: Coverage expansion strategy
- **[Session Summaries](docs/)**: Detailed summaries of each development session

### Testing Documentation
- **[Phase 3A Progress](docs/PHASE_3A_PROGRESS.md)**: Comprehensive testing initiative progress
- **[Session Reports](docs/SESSION_*_SUMMARY.md)**: Individual session achievements and patterns
- **[Voice Validation](docs/VOICE_VALIDATION_REPORT.md)**: TTS voice model validation results

### Architecture Documentation
- **[API Documentation](http://localhost:8000/docs)**: Interactive API documentation (when running)
- **Project Structure**: See [Project Structure](#-project-structure) section above

## 🛠️ Development

### Development Workflow
1. **Environment Setup**: Activate virtual environment before any work
2. **Run Tests**: Validate existing functionality before changes
3. **Implement Changes**: Follow TRUE 100% testing methodology
4. **Validate Coverage**: Ensure 100% statement + 100% branch coverage
5. **Document Patterns**: Capture new patterns discovered
6. **Commit Progress**: Detailed commit messages with context

### Quality Standards
✅ **Zero Technical Debt**: No TODOs, FIXMEs, or warnings allowed  
✅ **TRUE 100% Coverage**: 100% statement + 100% branch for critical modules  
✅ **Real Testing**: No mocked core logic, actual data validation  
✅ **Pattern Documentation**: All coverage patterns documented for reuse  
✅ **Comprehensive Validation**: Every edge case, every defensive pattern tested

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow quality standards and testing requirements
4. Commit changes with detailed messages
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request with comprehensive description

## 🎯 Roadmap

### Current Focus (2025 Q1)
- ✅ **TRUE 100% Validation**: 17/17 critical modules complete
- 🚀 **Coverage Expansion**: Targeting 90+ modules for TRUE 100%
- 📊 **Critical Infrastructure**: Database, models, security (Phase 3B)

### Future Phases
- **Phase 3B**: Critical Infrastructure (12 modules, ~30-40 hours)
- **Phase 4**: Extended Services (13 modules, ~55-70 hours)
- **Phase 5**: API Layer (14+ modules, ~60-80 hours)
- **Phase 6**: Frontend Layer (13+ modules, ~25-35 hours)
- **Phase 7**: Specialized Features (21+ modules, ~30-40 hours)

**Total Expansion**: 90+ modules, ~200-265 hours, 3-6 months

### Long-term Vision
- **Production Deployment**: Docker containerization and cloud deployment
- **Mobile Support**: Progressive Web App (PWA) for mobile access
- **Offline Mode**: Local AI models for offline learning
- **Multi-tenant**: Support for multiple organizations/families
- **Marketplace**: Community-contributed learning scenarios and content

## 📊 Project Metrics

### Test Coverage Evolution
```
Phase 1: Foundation (Sessions 1-26)
├── Initial Coverage: ~45%
└── Achievement: 6 AI services at 100%

Phase 2: Core Services (Sessions 27-29)  
├── Progress: 3 modules → TRUE 100%
└── Patterns: 21 branches covered

Phase 3A: Comprehensive Testing (Sessions 30-43)
├── Progress: 14 modules → TRUE 100%
└── Final: 17/17 modules, 51/51 branches, 1,930 tests ✅

Phase 3B: Expansion (Sessions 44+)
├── Target: 90+ modules → TRUE 100%
├── Progress: 0/90 modules
└── Estimated: 200-265 hours, 3-6 months
```

### Recent Achievements (Last 30 Days)
- ✅ Completed TRUE 100% validation for 17 critical modules
- ✅ Documented 51 branch coverage patterns
- ✅ Validated all 11 TTS voice models across 7 languages
- ✅ Achieved zero warnings and zero technical debt
- ✅ Created comprehensive expansion plan for 90+ modules

---

**Project Status**: Active Development, Phase 3A Complete  
**Last Updated**: 2025-11-18  
**Next Milestone**: Phase 3B - Critical Infrastructure (models/database.py)  
**Test Suite**: 1,930 tests passing, 0 warnings, 64.37% overall coverage

For detailed session-by-session progress, see the [documentation folder](docs/).
