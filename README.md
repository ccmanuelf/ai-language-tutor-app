# 🌟 AI Language Tutor App - Personal Family Educational Tool

> **A comprehensive AI-powered language learning platform combining YouLearn AI, Pingo AI, Fluently AI, and Airlearn features for family use with enterprise-grade speech processing and multi-LLM integration.**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)](https://fastapi.tiangolo.com/)
[![FastHTML](https://img.shields.io/badge/FastHTML-Frontend-blue.svg)](https://fasthtml.dev/)
[![Watson](https://img.shields.io/badge/IBM%20Watson-Speech-blue.svg)](https://www.ibm.com/watson)
[![Status](https://img.shields.io/badge/Status-Foundation%20Complete-brightgreen.svg)](#current-status)
[![License](https://img.shields.io/badge/License-Personal%20Family%20Use-orange.svg)](#)

## 🎯 Project Overview

### Mission Statement
Create a **comprehensive AI-powered learning platform** that functions as an interactive learning companion, blending conversational tutoring, real-time research, and multimedia teaching tools to help users master any topic with personalized guidance.

**Core Vision**: An AI learning assistant that combines conversational tutoring, real-time research, user-provided content, spoken interaction, and visual mind-mapping to deliver engaging, personalized, and feedback-driven education on any topic.

### Platform Capabilities
- **YouLearn AI**: Transform any content into structured learning materials in under 2 minutes
- **Pingo AI**: Scenario-based conversation practice with real-time feedback  
- **Fluently AI**: Live pronunciation analysis and accent coaching
- **Airlearn**: Spaced repetition and adaptive learning paths

**Target**: Family-safe, educational tool maintaining $30/month operational budget with enterprise-grade quality.

### Key Features Summary
- **Custom Learning Content**: Users choose any subject or upload materials (PDFs, websites, videos, notes)
- **Conversational Interface**: Natural, voice-first dialogue with spoken explanations and visual aids
- **Adaptive Research**: On-demand internet lookups to expand knowledge beyond provided materials
- **Visual Learning Tools**: Auto-generated flowcharts, diagrams, and mind maps for better comprehension
- **Engaging Interactions**: Questions, prompts, and interactive exercises rather than static explanations
- **Continuous Feedback**: Real-time monitoring, corrections, and tailored guidance for progress tracking

## 📊 Current Status

### Phase 0: Foundation & Repository Setup ✅ 25% Complete
```
Task 0.1: Documentation & Repository Cleanup    [████░░░░░░] 25% - IN_PROGRESS
Task 0.2: Database Configuration Cleanup        [░░░░░░░░░░]  0% - BLOCKED  
Task 0.3: GitHub Integration Setup               [░░░░░░░░░░]  0% - BLOCKED
```

### Overall Project Progress (5% of 10-12 weeks estimated)
```
Phase 0: Foundation & Repository Setup           [██░░░░░░░░] 25% - IN_PROGRESS
Phase 1: Frontend Architecture Restructuring    [░░░░░░░░░░]  0% - BLOCKED
Phase 2: Core Learning Engine Implementation    [░░░░░░░░░░]  0% - BLOCKED  
Phase 3: Structured Learning System             [░░░░░░░░░░]  0% - BLOCKED
Phase 4: Integration & Polish                   [░░░░░░░░░░]  0% - BLOCKED
```

## 🏗️ Current Implementation Status

### ✅ **Completed Infrastructure (Backend Foundation)**
- **Database Architecture**: SQLite + ChromaDB + DuckDB operational
- **AI Service Integration**: Claude + Mistral + Qwen APIs functional
- **Speech Processing**: IBM Watson STT/TTS fully operational  
- **Authentication**: JWT-based user authentication system
- **Cost Management**: $30/month budget tracking active
- **Project Management**: Comprehensive task tracking and quality gates established

### 🚧 **In Progress**
- **Documentation Consolidation**: 47+ files being organized into structured hierarchy
- **Repository Organization**: GitHub setup and sync workflow establishment
- **Database Cleanup**: Removing MariaDB references, standardizing on SQLite/ChromaDB/DuckDB

### ⏸️ **Planned (Phase 1+)**
- **Frontend Restructuring**: Break down 2,086-line monolithic frontend into <10 focused components
- **YouLearn Integration**: YouTube videos → learning materials in <2 minutes  
- **Pingo Conversations**: Scenario-based conversation practice with AI
- **Fluently Feedback**: Real-time pronunciation analysis and coaching
- **Airlearn Progression**: Spaced repetition and adaptive learning paths

## 🏛️ Technical Architecture

### **Current Stack**
```
Frontend (Port 3000)          Backend (Port 8000)           External Services
├── FastHTML Server          ├── FastAPI Server            ├── Claude API (General)
├── User Interface           ├── JWT Authentication        ├── Mistral API (French)
├── Conversation Interface   ├── AI Service Router         ├── Qwen API (Chinese)  
└── Speech Integration       └── Speech Processor          └── IBM Watson (Speech)

Data Layer                   Development Tools              Project Management
├── SQLite (Primary DB)      ├── Python 3.12+             ├── TASK_TRACKER.json
├── ChromaDB (Vectors)       ├── Git Repository            ├── Quality Gates Framework
└── DuckDB (Analytics)       └── Comprehensive Testing     └── Daily Workflow Templates
```

### **Database Schema (Current)**
- **Users**: 3 family members with role-based access
- **Conversations**: 3 active learning sessions
- **Vocabulary**: 9 items across 6 languages  
- **Vector Collections**: 5 collections with multilingual embeddings
- **Performance**: SQLite (8.9ms), ChromaDB (52.9ms) response times

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.12+ required
python --version  # Should be 3.12+

# Virtual environment recommended
python -m venv ai-tutor-env
source ai-tutor-env/bin/activate  # On Windows: ai-tutor-env\\Scripts\\activate
```

### Installation & Setup
```bash
# Clone and setup
git clone <repository-url>
cd ai-language-tutor-app

# Install dependencies
pip install -r requirements.txt

# Configure environment (see docs/development/SETUP_GUIDE.md for details)
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from app.database.config import init_database; init_database()"
```

### Running the Application
```bash
# Start backend server (Terminal 1)
python run_backend.py
# Backend available at: http://localhost:8000

# Start frontend server (Terminal 2)  
python run_frontend.py
# Frontend available at: http://localhost:3000

# Access the application
open http://localhost:3000/chat
```

### Health Check
```bash
# Verify all systems operational
python test_basic_functionality.py

# Expected output:
# ✅ Database connectivity: PASS
# ✅ AI service routing: PASS  
# ✅ Speech processing: PASS
# ✅ Authentication: PASS
```

## 📁 Project Structure

```
ai-language-tutor-app/
├── app/                          # Application source code
│   ├── api/                      # FastAPI routes and authentication
│   ├── database/                 # Database configuration and models
│   ├── models/                   # Data models and schemas
│   └── services/                 # AI routing and speech processing
├── docs/                         # Documentation (organized structure)
│   ├── project-management/       # Task tracking, status, quality gates
│   ├── development/              # Setup guides and development docs
│   ├── architecture/             # Technical specifications and design
│   ├── implementation-history/   # Historical fixes and implementation notes
│   └── resources/                # Reference materials and PDFs
├── requirements.txt              # Python dependencies
├── run_backend.py               # Backend server launcher
├── run_frontend.py              # Frontend server launcher
└── README.md                    # This file
```

## 🎓 Reference Applications Integration Plan

The platform is designed to combine and exceed the capabilities of these reference applications:

### **YouLearn AI** → Phase 2.1: Content Processing Pipeline
- **Input**: YouTube videos, articles, documents
- **Output**: Structured learning materials with exercises and assessments
- **Timeline**: 3-4 weeks (Phase 2)

### **Pingo AI** → Phase 2.2: Conversation System Enhancement  
- **Features**: Scenario-based conversations, cultural context, real-world situations
- **Integration**: AI-powered conversation partners with personality profiles
- **Timeline**: Following content processing completion

### **Fluently AI** → Phase 2.3: Real-Time Analysis Engine
- **Capabilities**: Live pronunciation feedback, accent coaching, speaking confidence building
- **Technology**: Advanced speech analysis with Watson STT/TTS integration
- **Timeline**: Following conversation system completion

### **Airlearn** → Phase 3.1: Structured Learning System
- **Features**: Spaced repetition, progress analytics, adaptive learning paths
- **Data**: Learning analytics with DuckDB for insights and optimization
- **Timeline**: 2-3 weeks (Phase 3)

## 🛠️ Development Workflow

### **Daily Development Process**
1. **Resume Session**: Use standardized daily prompt template
2. **Check Status**: Load current task from TASK_TRACKER.json  
3. **Validate Progress**: Ensure previous work passes quality gates
4. **Execute Tasks**: Work on current phase with systematic approach
5. **Document Changes**: Update tracking files and commit progress

### **Quality Standards**
- **No Advancement Rule**: Cannot proceed to next task until current task passes ALL quality gates
- **100% Acceptance Criteria**: Every criterion must be fully met with validation evidence
- **Comprehensive Testing**: All functionality tested before completion  
- **Change Documentation**: All modifications require rationale and impact analysis

### **Testing Strategy**
```bash
# Basic functionality tests
python test_basic_functionality.py

# Comprehensive system tests  
python test_comprehensive_functionality.py

# Speech system validation
python test_watson_stt.py

# Frontend integration tests
python comprehensive_frontend_test.py
```

## 💰 Cost Management

### **Current Budget Tracking**
- **Target**: $30/month operational cost
- **Current**: $0/month (development phase)
- **Monitoring**: Automatic API usage tracking with alerts
- **Optimization**: Multi-LLM routing based on cost and capability

### **Cost Breakdown (Projected)**
```
Service                 Monthly Cost    Usage
├── Claude API         $12-15          Primary conversations
├── Mistral API        $3-5            French language optimization  
├── Qwen API          $2-3            Chinese language support
├── IBM Watson STT     $5-8            Speech-to-text processing
├── IBM Watson TTS     $3-5            Text-to-speech generation
└── Infrastructure     $0              Local hosting
                      ─────────────────
Total                 $25-36/month    Within target range
```

## 🔒 Security & Privacy

### **Family-Safe Features**
- **Child Protection**: Age-appropriate content filtering and usage monitoring
- **Privacy First**: All personal data stored locally, no third-party data sharing
- **Secure Authentication**: JWT-based access control with role-based permissions
- **Content Moderation**: AI-powered inappropriate content detection and filtering

### **Data Handling**
- **Local Storage**: Primary data stored in local SQLite database
- **Vector Embeddings**: Multilingual learning content in ChromaDB
- **Analytics**: Learning progress and insights in DuckDB
- **API Security**: Encrypted API key management and secure communication

## 📖 Documentation

### **Available Documentation**
- **[Task Tracker](docs/project-management/TASK_TRACKER.json)**: Current project status and task management
- **[Setup Guide](docs/development/)**: Complete development environment setup
- **[Architecture Docs](docs/architecture/)**: Technical specifications and system design  
- **[Quality Gates](docs/project-management/QUALITY_GATES.md)**: Validation framework and testing requirements
- **[Daily Workflow](docs/project-management/DAILY_PROMPT_TEMPLATE.md)**: Standardized development process

### **Getting Help**
- **Issues**: Check existing documentation first, then create detailed issue reports
- **Development**: Follow daily workflow templates for consistent progress
- **Testing**: Use provided test scripts to validate functionality
- **Contributions**: Follow quality gate requirements for all changes

## 🎯 Success Metrics

### **Phase 0 Success Criteria (Current)**
- [x] Project management infrastructure established
- [x] Task tracking system operational  
- [x] Quality gate framework implemented
- [ ] Documentation consolidated into organized structure (75% complete)
- [ ] GitHub repository setup and sync workflow operational
- [ ] Database configuration cleaned up (MariaDB references removed)

### **Overall Project Goals**
- **Platform Superiority**: Surpass individual reference apps through integrated experience
- **Family Experience**: Safe, educational, and engaging for all family members
- **Cost Efficiency**: Maintain operational costs under $30/month
- **Educational Impact**: Measurable improvement in language learning outcomes

---

**Project Status**: Active development, Phase 0 (Foundation) 25% complete  
**Last Updated**: September 18, 2025  
**Next Milestone**: Complete documentation consolidation and GitHub integration  
**Estimated Completion**: December 18, 2025 (3 months remaining)

For detailed daily status and task tracking, see [docs/project-management/PROJECT_STATUS.md](docs/project-management/PROJECT_STATUS.md)