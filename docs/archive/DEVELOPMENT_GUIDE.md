# 🛠️ Development Guide - AI Language Tutor App

> **Developer Setup and Workflow Guide for Family Educational AI Platform**

*Last Updated: August 25, 2025*

## 🎯 Development Environment Setup

### **Prerequisites Checklist**
- [ ] Python 3.12+ installed
- [ ] Git configured with SSH keys
- [ ] API keys obtained (Claude, Mistral, Qwen, Watson)
- [ ] Audio system working (microphone + speakers)
- [ ] 10GB+ free disk space

### **Environment Configuration**

#### **1. Repository Setup**
```bash
# Clone and setup
git clone <repository-url>
cd ai-language-tutor-app

# Create development branch
git checkout -b dev-$(whoami)-$(date +%Y%m%d)

# Setup virtual environment
python -m venv ai-tutor-env
source ai-tutor-env/bin/activate  # Windows: ai-tutor-env\\Scripts\\activate
```

#### **2. Dependencies Installation**
```bash
# Core dependencies
pip install -r requirements.txt

# macOS audio dependencies
brew install portaudio
pip install pyaudio webrtcvad

# Linux audio dependencies (if needed)
# sudo apt-get install portaudio19-dev python3-pyaudio
# pip install pyaudio webrtcvad

# Windows audio dependencies (if needed)  
# Download and install PyAudio wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# pip install webrtcvad
```

#### **3. Environment Variables**
```bash
# Copy template and configure
cp .env.example .env

# Edit .env with your API keys
# See API_KEYS_SETUP_GUIDE.md for detailed instructions
vim .env  # or code .env
```

#### **4. Database Initialization**
```bash
# Initialize database and load sample data
python init_sample_data.py

# Verify database setup
python -c \"from app.database.config import db_manager; print('DB Health:', db_manager.get_health_summary())\"
```

## 🏗️ Architecture Overview for Developers

### **Project Structure**
```
ai-language-tutor-app/
├── app/                          # Main application package
│   ├── api/                      # FastAPI route definitions
│   ├── core/                     # Configuration and security
│   ├── database/                 # Database configuration and models
│   ├── frontend/                 # FastHTML frontend components
│   ├── models/                   # Pydantic data models
│   ├── services/                 # Business logic and AI integrations
│   ├── static/                   # Static assets (CSS, JS, images)
│   ├── templates/                # HTML templates (FastHTML)
│   └── utils/                    # Utility functions
├── alembic/                      # Database migration scripts
├── data/                         # Application data and databases
│   ├── ai_language_tutor.db      # SQLite primary database
│   ├── chromadb/                 # ChromaDB vector storage
│   └── local/                    # Local storage (DuckDB, uploads)
├── docs/                         # Auto-generated documentation
├── tasks/                        # Task planning and tracking
├── tests/                        # Test suite
└── scripts/                      # Development and deployment scripts
```

### **Key Modules and Responsibilities**

#### **Backend Core (`app/`)**
```python
# FastAPI application entry points
app/main.py              # Backend API server (port 8000)
app/frontend_main.py     # Frontend server (port 3000) [🚧 In Development]

# Configuration and security
app/core/config.py       # Environment variables and settings
app/core/security.py     # JWT authentication and authorization

# Database layer
app/database/config.py   # Multi-database connection manager
app/models/database.py   # SQLAlchemy ORM models
app/models/schemas.py    # Pydantic request/response models

# AI and service integrations
app/services/ai/router.py           # Multi-LLM routing logic
app/services/speech_processor.py    # Watson STT/TTS integration
app/services/cost_tracker.py        # Budget management
```

#### **Frontend Layer (FastHTML)**
```python
# 🚧 Frontend implementation in progress
app/frontend/            # FastHTML components and pages
app/templates/           # HTML templates
app/static/              # CSS, JavaScript, images
```

## 🚀 Development Workflow

### **Daily Development Process**

#### **1. Start Development Session**
```bash
# Activate environment and update
source ai-tutor-env/bin/activate
git pull origin main

# Start backend server
python run_backend.py &  # Runs on http://localhost:8000

# Start frontend server (when implemented)
# python run_frontend.py &  # Will run on http://localhost:3000

# Monitor logs
tail -f logs/app.log
```

#### **2. System Health Check**
```bash
# Verify all systems operational
python quick_watson_validation.py

# Expected output:
# ✅ All systems operational!
# ✅ Database: SQLite + ChromaDB + DuckDB healthy
# ✅ Speech: Watson STT + TTS operational
# ✅ AI Services: Claude + Mistral + Qwen ready
```

#### **3. Development Testing**
```bash
# Backend API testing
curl http://localhost:8000/health
# Expected: {\"status\":\"healthy\",\"service\":\"ai-language-tutor-api\"}

# Database queries
python -c \"from app.database.config import db_manager; session = db_manager.get_sqlite_session(); print('Connected to DB')\"

# AI service testing
python -c \"from app.services.ai.router import ai_router; print('AI Router ready:', ai_router.get_status())\"
```

### **Feature Development Process**

#### **Backend Feature Development**
```bash
# 1. Create feature branch
git checkout -b feature/new-feature-name

# 2. Implement in appropriate module
# - API endpoints: app/api/
# - Business logic: app/services/
# - Data models: app/models/
# - Database changes: alembic/versions/

# 3. Test implementation
python -m pytest tests/ -v

# 4. Update documentation
# Edit relevant .md files in docs/
```

#### **Frontend Feature Development (FastHTML)**
```bash
# 🚧 Coming in Phase 2 - Frontend Implementation
# 
# Planned workflow:
# 1. Create FastHTML components in app/frontend/
# 2. Add routes to app/frontend_main.py
# 3. Style with MonsterUI components
# 4. Test user interactions
# 5. Integrate with backend APIs
```

## 🧪 Testing and Validation

### **Automated Testing**
```bash
# Run comprehensive test suite
python -m pytest tests/ -v --cov=app --cov-report=html

# Run specific test categories
python -m pytest tests/test_database.py -v      # Database tests
python -m pytest tests/test_ai_services.py -v   # AI integration tests
python -m pytest tests/test_speech.py -v        # Speech processing tests

# Performance testing
python -m pytest tests/test_performance.py -v
```

### **Manual Testing Procedures**

#### **Database Testing**
```bash
# Test all database connections
python -c \"
from app.database.config import db_manager
health = db_manager.test_all_connections()
for db, status in health.items():
    print(f'{db}: {status[\"status\"]} ({status.get(\"response_time_ms\", 0):.1f}ms)')
\"
```

#### **AI Services Testing**
```bash
# Test Claude API
python -c \"
import asyncio
from app.services.ai.providers.claude_service import ClaudeService

async def test_claude():
    service = ClaudeService()
    response = await service.generate_response('Hello, test message')
    print('Claude response:', response[:100] + '...')

asyncio.run(test_claude())
\"
```

#### **Speech Services Testing**
```bash
# Test Watson TTS
python -c \"
import asyncio
from app.services.speech_processor import speech_processor

async def test_tts():
    result = await speech_processor.process_text_to_speech(
        'Hello, this is a test', 'en', 'neural'
    )
    print(f'TTS Result: {len(result.audio_data)} bytes, {result.duration_seconds}s')

asyncio.run(test_tts())
\"
```

## 🛠️ Debugging and Troubleshooting

### **Common Issues and Solutions**

#### **Database Connection Issues**
```bash
# Check database file permissions
ls -la data/ai_language_tutor.db

# Verify ChromaDB directory
ls -la data/chromadb/

# Test database connections
python -c \"from app.database.config import db_manager; print(db_manager.test_all_connections())\"
```

#### **Audio Processing Issues**
```bash
# Check audio libraries
python -c \"import pyaudio; print('PyAudio version:', pyaudio.__version__)\"
python -c \"import webrtcvad; print('WebRTCVAD available')\"

# Test audio device access
python -c \"
import pyaudio
p = pyaudio.PyAudio()
print('Audio devices:', p.get_device_count())
p.terminate()
\"
```

#### **API Key Issues**
```bash
# Verify API keys loaded
python -c \"
from app.core.config import get_settings
s = get_settings()
print('Claude key configured:', bool(s.ANTHROPIC_API_KEY))
print('Watson STT configured:', bool(s.IBM_WATSON_STT_API_KEY))
print('Watson TTS configured:', bool(s.IBM_WATSON_TTS_API_KEY))
\"
```

#### **Cost Tracking Issues**
```bash
# Check budget status
python -c \"
from app.services.cost_tracker import cost_tracker
status = cost_tracker.get_budget_status()
print('Budget status:', status)
\"
```

### **Logging and Monitoring**

#### **Log Files**
```bash
# Application logs
tail -f logs/app.log

# Database logs (if enabled)
tail -f logs/database.log

# Error logs
tail -f logs/error.log
```

#### **Performance Monitoring**
```bash
# Check response times
python -c \"
from app.database.config import db_manager
import time

start = time.time()
health = db_manager.test_all_connections()
print(f'Health check took: {(time.time() - start)*1000:.1f}ms')
\"

# Monitor resource usage
ps aux | grep python
df -h  # Disk usage
```

## 📊 Code Quality and Standards

### **Code Formatting and Linting**
```bash
# Install development tools
pip install black isort flake8 mypy

# Format code
black app/ tests/
isort app/ tests/

# Check code quality
flake8 app/ tests/
mypy app/
```

### **Pre-commit Hooks**
```bash
# Setup pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### **Documentation Standards**
- Use docstrings for all functions and classes
- Update README.md for major changes
- Keep API_KEYS_SETUP_GUIDE.md current
- Document configuration changes in PROJECT_STATUS_AND_ARCHITECTURE.md

## 🚀 Deployment and Production

### **Environment-Specific Configuration**

#### **Development Environment**
```bash
# Current setup (SQLite + local services)
DATABASE_URL=sqlite:///./data/ai_language_tutor.db
DEBUG=True
```

#### **Production Environment (Future)**
```bash
# Production setup (MariaDB + scaled services)
DATABASE_URL=mysql+pymysql://user:pass@host/db
DEBUG=False
CHROMADB_HOST=production-chromadb-host
```

### **Database Migration Path**
```bash
# Development to Production migration
# 1. Export SQLite data
# 2. Setup MariaDB instance
# 3. Run Alembic migrations
# 4. Import data to MariaDB
# 5. Update configuration
```

## 📚 Additional Resources

### **Documentation**
- [API Keys Setup Guide](API_KEYS_SETUP_GUIDE.md) - Complete API configuration
- [Project Status & Architecture](PROJECT_STATUS_AND_ARCHITECTURE.md) - Technical overview
- [Task Planning](tasks/tasks.json) - Development roadmap

### **External Documentation**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastHTML Documentation](https://fastht.ml/)
- [IBM Watson Speech Services](https://cloud.ibm.com/docs/speech-to-text)
- [ChromaDB Documentation](https://docs.trychroma.com/)

### **Development Tools**
```bash
# Useful development commands
alias ll='ls -la'
alias activate='source ai-tutor-env/bin/activate'
alias runback='python run_backend.py'
alias runfront='python run_frontend.py'  # When implemented
alias health='python quick_watson_validation.py'
alias dbtest='python -c \"from app.database.config import db_manager; print(db_manager.get_health_summary())\"'
```

---

**🎯 Happy Coding! Building the future of AI-powered family language learning!**

*For questions or issues, refer to the troubleshooting section above or check the project documentation.*