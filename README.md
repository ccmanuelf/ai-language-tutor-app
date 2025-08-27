# 🌟 AI Language Tutor App - Personal Family Educational Tool

> **A sophisticated AI-powered language learning platform designed for family use with enterprise-grade speech processing, multi-LLM integration, and comprehensive cost management.**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Watson](https://img.shields.io/badge/IBM%20Watson-Speech-blue.svg)](https://www.ibm.com/watson)
[![Status](https://img.shields.io/badge/Status-Backend%20Complete-brightgreen.svg)](#)
[![License](https://img.shields.io/badge/License-Family%20Use-orange.svg)](#)

## 🎯 Project Overview

### **Mission**
Provide AI-powered, real-time language learning with pronunciation feedback for family education, maintaining a $30/month operational budget with enterprise-grade quality.

### **Current Status (August 25, 2025)**
```
🚀 PHASE 1: BACKEND & INFRASTRUCTURE ✅ COMPLETE
├── Database Architecture     ✅ SQLite + ChromaDB + DuckDB operational
├── AI Service Integration    ✅ Claude + Mistral + Qwen operational  
├── Speech Processing         ✅ Watson STT/TTS fully functional
├── Cost Management          ✅ $30/month budget tracking active
└── Security Framework       ✅ JWT authentication ready

📋 PHASE 2: FRONTEND & UI (NEXT)
├── FastHTML Server          🚧 Ready for implementation
├── User Interface           🚧 MonsterUI components planned
├── Conversation Interface   🚧 AI chat with speech integration
└── Profile Management       🚧 Multi-user with child protections
```

## 🏗️ Architecture Overview

### **Technology Stack**
```mermaid
graph TB
    subgraph \"Frontend (Port 3000)\"
        FH[FastHTML Server]
        UI[User Interface]
        MU[MonsterUI Components]
    end
    
    subgraph \"Backend (Port 8000)\"
        API[FastAPI Server]
        AUTH[JWT Authentication]
        ROUTER[AI Service Router]
    end
    
    subgraph \"AI Services\"
        CLAUDE[Claude API - General]
        MISTRAL[Mistral API - French]
        QWEN[Qwen API - Chinese]
        WATSON[Watson STT/TTS]
    end
    
    subgraph \"Database Layer\"
        SQLITE[SQLite - Primary]
        CHROMADB[ChromaDB - Vectors]
        DUCKDB[DuckDB - Analytics]
    end
    
    FH --> API
    API --> ROUTER
    ROUTER --> CLAUDE
    ROUTER --> MISTRAL
    ROUTER --> QWEN
    ROUTER --> WATSON
    API --> SQLITE
    API --> CHROMADB
    API --> DUCKDB
```

### **Key Features**
- 🤖 **Multi-LLM Intelligence**: Claude (general), Mistral (French), Qwen (Chinese)
- 🎤 **Enterprise Speech**: IBM Watson STT/TTS with pronunciation analysis
- 🗄️ **Multi-Database**: SQLite + ChromaDB vectors + DuckDB analytics
- 💰 **Cost Control**: $30/month budget with automatic tracking
- 👨‍👩‍👧‍👦 **Family Safe**: Child data protections and GDPR compliance
- 🌐 **Multi-Language**: English, Spanish, French, Chinese, Japanese, German+

## 🚀 Quick Start

### **Prerequisites**
- Python 3.12+
- API keys for Claude, Mistral, Qwen, Watson (see setup guide)
- macOS/Linux/Windows with audio support

### **Installation**
```bash
# Clone the repository
git clone https://github.com/your-repo/ai-language-tutor-app.git
cd ai-language-tutor-app

# Create virtual environment
python -m venv ai-tutor-env
source ai-tutor-env/bin/activate  # On Windows: ai-tutor-env\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Install audio processing libraries
brew install portaudio  # macOS
pip install pyaudio webrtcvad

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys (see API_KEYS_SETUP_GUIDE.md)
```

### **Database Setup**
```bash
# Initialize database and sample data
python init_sample_data.py

# Verify database health
python -c \"from app.database.config import db_manager; print('Status:', db_manager.get_health_summary())\"
```

### **Run the Application**
```bash
# Start backend server (Port 8000)
python run_backend.py

# In another terminal, start frontend server (Port 3000)
python run_frontend.py  # 🚧 Frontend implementation in progress

# Verify services
curl http://localhost:8000/health
curl http://localhost:3000/health  # 🚧 Coming soon
```

## 📊 System Validation

### **Health Check Commands**
```bash
# Complete system health verification
python -c \"
import asyncio
from app.database.config import db_manager
from app.services.speech_processor import speech_processor

# Database health
health = db_manager.test_all_connections()
print('Database Status:', {k: v['status'] for k, v in health.items()})

# Speech services validation  
async def check_speech():
    status = await speech_processor.get_speech_pipeline_status()
    print('Speech Status:', status['status'])

asyncio.run(check_speech())
\"
```

### **Expected Output**
```
✅ Database Status: {'chromadb': 'healthy', 'duckdb': 'healthy', 'sqlite': 'healthy'}
✅ Speech Status: operational
```

## 📚 Documentation

### **Setup Guides**
- 📘 **[API Keys Setup Guide](API_KEYS_SETUP_GUIDE.md)** - Complete API configuration
- 🏗️ **[Project Status & Architecture](PROJECT_STATUS_AND_ARCHITECTURE.md)** - Current status and technical details
- 🗄️ **[Database Setup Guide](database_setup_guide.md)** - Database configuration steps

### **Development Documentation**
- 📋 **[Task Planning](tasks/tasks.json)** - Original planning and progress tracking
- 🧪 **[Testing Scripts](quick_watson_validation.py)** - Validation and testing tools
- 📁 **[Generated Docs](docs/)** - Auto-generated project documentation

## 🔧 Development Status

### **✅ Completed Systems**
| Component | Status | Details |
|-----------|---------|----------|
| **Backend API** | ✅ Operational | FastAPI server with OpenAPI docs |
| **Database** | ✅ Operational | SQLite + ChromaDB + DuckDB multi-DB |
| **AI Services** | ✅ Operational | Claude + Mistral + Qwen routing |
| **Speech Processing** | ✅ Operational | Watson STT/TTS with audio libraries |
| **Cost Tracking** | ✅ Operational | $30/month budget enforcement |
| **Authentication** | ✅ Ready | JWT framework implemented |
| **Sample Data** | ✅ Loaded | 6 languages, 3 users, test conversations |

### **🚧 In Development**
| Component | Status | Priority |
|-----------|---------|----------|
| **Frontend UI** | 📋 Planned | High - FastHTML implementation |
| **User Profiles** | 📋 Planned | High - Multi-user management |
| **Conversation UI** | 📋 Planned | High - AI chat interface |
| **Document Upload** | 📋 Planned | Medium - PDF/DOCX processing |
| **GDPR Compliance** | 📋 Planned | High - Child data protections |

## 💰 Cost Management

### **Monthly Budget Breakdown ($30 limit)**
```
Service          | Est. Cost | Purpose                    | Usage %
-----------------|-----------|----------------------------|--------
Claude API       | $12-15    | Primary conversations      | 60%
Mistral API      | $3-5      | French optimization        | 15%  
Qwen API         | $2-3      | Chinese support            | 15%
Watson STT/TTS   | $8-12     | Speech processing          | 10%
-----------------|-----------|----------------------------|--------
Total            | ~$25-30   | Within budget target       | 100%
```

### **Budget Monitoring**
- ⚠️ **80% threshold**: Warning alerts
- 🚨 **95% threshold**: Critical alerts
- 🛡️ **100% limit**: Automatic service suspension
- 🔄 **Fallback**: Local Ollama LLM when budget exceeded

## 🔒 Security & Privacy

### **Data Protection**
- 🔐 API keys stored in `.env` (git-ignored)
- 🛡️ JWT authentication with secure tokens
- 👶 Child account protections planned
- 🇪🇺 GDPR compliance framework ready
- 🏠 Local data storage (family privacy)

### **Security Validation**
```bash
# Check API key security
python -c \"from app.core.config import get_settings; print('Keys configured:', bool(get_settings().ANTHROPIC_API_KEY))\"

# Verify JWT framework
python -c \"from app.core.security import create_access_token; print('JWT ready:', bool(create_access_token))\"
```

## 🧪 Testing & Validation

### **Quick System Test**
```bash
# Run comprehensive system validation
python quick_watson_validation.py

# Expected output:
# ✅ Watson Speech Services integration validated successfully!
# ✅ Speech processing pipeline ready for use!
```

### **Database Validation**
```bash
# Verify sample data loaded correctly
python -c \"
from app.database.config import db_manager
from sqlalchemy import text
session = db_manager.get_sqlite_session()
result = session.execute(text('SELECT COUNT(*) FROM languages')).scalar()
print(f'Languages loaded: {result}')
session.close()
\"
```

## 🚀 Next Development Phase

### **Phase 2A: Frontend Foundation (Priority: High)**
1. **FastHTML Server Setup**
   - Initialize server on port 3000
   - Basic routing and health endpoints
   - MonsterUI component integration

2. **User Interface Framework**
   - Responsive layout foundation
   - Navigation and authentication flows
   - API integration patterns

3. **Core User Features**
   - Profile management (multi-user)
   - Basic conversation interface
   - Speech input/output controls

### **Getting Started with Frontend Development**
```bash
# Development workflow (coming soon)
git checkout -b frontend-implementation
# Implement FastHTML server
# Test user interface components  
# Integrate with backend APIs
```

## 📞 Support & Contributing

### **Development Resources**
- 🏗️ **Architecture**: See [PROJECT_STATUS_AND_ARCHITECTURE.md](PROJECT_STATUS_AND_ARCHITECTURE.md)
- 🔑 **API Setup**: See [API_KEYS_SETUP_GUIDE.md](API_KEYS_SETUP_GUIDE.md)
- 📋 **Task Planning**: See [tasks/tasks.json](tasks/tasks.json)

### **Common Issues**
```bash
# Database connection issues
python -c \"from app.database.config import db_manager; print(db_manager.test_all_connections())\"

# Speech processing issues  
brew install portaudio && pip install pyaudio webrtcvad

# API key issues
# Check .env file configuration and API_KEYS_SETUP_GUIDE.md
```

## 📈 Project Roadmap

### **Completed Phases ✅**
- [x] Backend infrastructure and API framework
- [x] Multi-database architecture (SQLite + ChromaDB + DuckDB)
- [x] AI service integration (Claude + Mistral + Qwen)
- [x] Enterprise speech processing (Watson STT/TTS)
- [x] Cost management and budget tracking
- [x] Security and authentication framework

### **Current Focus 🎯**
- [ ] FastHTML frontend implementation
- [ ] User profile and authentication UI
- [ ] AI conversation interface with speech
- [ ] Multi-user family management

### **Future Enhancements 🔮**
- [ ] Document processing (PDF, DOCX, PPTX)
- [ ] YouTube video integration
- [ ] Advanced pronunciation analysis
- [ ] Learning analytics and progress tracking
- [ ] Offline mode with local Ollama LLMs

---

## 📄 License

**Personal Family Educational Tool** - This project is designed for personal family use with educational purposes. See project documentation for usage guidelines.

---

**🌟 Ready to revolutionize family language learning with AI!**

*For setup instructions, see [API_KEYS_SETUP_GUIDE.md](API_KEYS_SETUP_GUIDE.md)*  
*For technical details, see [PROJECT_STATUS_AND_ARCHITECTURE.md](PROJECT_STATUS_AND_ARCHITECTURE.md)*