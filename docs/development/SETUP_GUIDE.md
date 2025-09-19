# 🚀 Complete Setup Guide - AI Language Tutor App

> **Comprehensive development environment setup for the AI Language Tutor App**  
> **Last Updated**: September 18, 2025  
> **Status**: All services operational and validated

## 📋 Quick Setup Checklist

### ✅ Prerequisites  
- [ ] Python 3.12+ installed and verified
- [ ] Git configured with SSH keys  
- [ ] 10GB+ free disk space available
- [ ] Audio system working (microphone + speakers)
- [ ] API keys obtained for all required services

### ✅ Setup Steps
- [ ] Clone repository and create virtual environment
- [ ] Install dependencies and audio libraries
- [ ] Configure environment variables with API keys
- [ ] Initialize databases and verify connections
- [ ] Run health checks and validate all systems
- [ ] Start servers and test application

---

## 🔧 1. Environment Setup

### **Repository and Virtual Environment**
```bash
# Clone repository
git clone <repository-url>
cd ai-language-tutor-app

# Create and activate virtual environment
python -m venv ai-tutor-env
source ai-tutor-env/bin/activate  # Windows: ai-tutor-env\\Scripts\\activate

# Verify Python version
python --version  # Should be 3.12+
```

### **Dependencies Installation**
```bash
# Install core Python dependencies
pip install -r requirements.txt

# Install audio processing libraries
# macOS
brew install portaudio
pip install pyaudio webrtcvad

# Linux (Ubuntu/Debian)
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio webrtcvad

# Windows
# Download PyAudio wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install webrtcvad
```

---

## 🔐 2. API Keys Configuration

### **Required API Services**

| Service | Purpose | Cost (Monthly) | Status |
|---------|---------|----------------|--------|
| **Claude API** | Primary AI conversations | $12-15 | ✅ Operational |
| **Mistral API** | French language optimization | $3-5 | ✅ Operational |
| **Qwen API** | Chinese language support | $2-3 | ✅ Operational |
| **Watson STT** | Speech-to-text processing | $5-8 | ✅ Operational |
| **Watson TTS** | Text-to-speech generation | $3-5 | ✅ Operational |
| **Total** | Combined services | **$25-36** | **Within $30 target** |

### **API Key Setup**

#### **1. Create Environment File**
```bash
cp .env.example .env
# Edit with your preferred editor
code .env  # or vim .env
```

#### **2. Configure API Keys**
```bash
# Anthropic Claude API (Primary AI)
# Get from: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_claude_api_key_here

# Mistral AI API (French optimization)  
# Get from: https://console.mistral.ai/
MISTRAL_API_KEY=your_mistral_api_key_here

# Qwen API (Chinese support)
# Get from: https://dashscope.aliyun.com/
QWEN_API_KEY=your_qwen_api_key_here

# IBM Watson Speech-to-Text
# Get from: https://cloud.ibm.com/catalog/services/speech-to-text
WATSON_STT_API_KEY=your_watson_stt_api_key_here
WATSON_STT_URL=your_watson_stt_service_url_here
WATSON_STT_INSTANCE_ID=your_watson_stt_instance_id_here

# IBM Watson Text-to-Speech
# Get from: https://cloud.ibm.com/catalog/services/text-to-speech
WATSON_TTS_API_KEY=your_watson_tts_api_key_here
WATSON_TTS_URL=your_watson_tts_service_url_here
WATSON_TTS_INSTANCE_ID=your_watson_tts_instance_id_here

# Database Configuration
DATABASE_URL=sqlite:///./data/ai_language_tutor.db
CHROMADB_PATH=./data/chromadb/
DUCKDB_PATH=./data/local/app.duckdb

# Security
SECRET_KEY=your_secret_key_here  # Generate with: openssl rand -hex 32
JWT_SECRET_KEY=your_jwt_secret_here  # Generate with: openssl rand -hex 32

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
```

#### **3. Generate Security Keys**
```bash
# Generate secure secret keys
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

---

## 🗄️ 3. Database Setup

### **Multi-Database Architecture**

The application uses three databases for different purposes:

```
✅ SQLite (Primary Database)
├── File: ./data/ai_language_tutor.db
├── Purpose: Main application data (users, conversations, vocabulary)
├── Advantages: Zero configuration, file-based, reliable
└── Production Path: Migrate to MariaDB when scaling needed

✅ ChromaDB (Vector Database)  
├── Path: ./data/chromadb/
├── Purpose: Embeddings for semantic search and RAG capabilities
├── Features: Multilingual embeddings, conversation history vectors
└── Collections: Learning content, conversation history, vocabulary

✅ DuckDB (Analytics Database)
├── File: ./data/local/app.duckdb
├── Purpose: Learning analytics and performance metrics
├── Features: Fast columnar analytics, learning progress tracking
└── Use Cases: Progress reports, learning insights, usage analytics
```

### **Database Initialization**
```bash
# Create data directories
mkdir -p data/chromadb data/local

# Initialize databases with sample data
python -c "
from app.database.config import init_database
init_database()
print('✅ Databases initialized successfully')
"

# Load sample data for development
python init_sample_data.py
```

### **Database Health Verification**
```bash
# Test all database connections
python -c "
from app.database.config import db_manager
health = db_manager.test_all_connections()

print('📊 Database Health Check:')
for db_name, status in health.items():
    emoji = '✅' if status['status'] == 'healthy' else '❌'
    time_ms = status.get('response_time_ms', 0)
    print(f'   {emoji} {db_name.upper()}: {status[\"status\"]} ({time_ms:.1f}ms)')

overall = db_manager.get_health_summary()
print(f'\\n🎯 Overall Status: {overall[\"overall\"].upper()}')
"
```

**Expected Output:**
```
📊 Database Health Check:
   ✅ SQLITE: healthy (8.9ms)
   ✅ CHROMADB: healthy (52.9ms)  
   ✅ DUCKDB: healthy (55.7ms)

🎯 Overall Status: HEALTHY
```

---

## ⚡ 4. Application Startup

### **Start Backend Server**
```bash
# Activate environment
source ai-tutor-env/bin/activate

# Start backend API server (port 8000)
python run_backend.py

# Backend available at: http://localhost:8000
# API documentation: http://localhost:8000/docs
```

### **Start Frontend Server** (When Available)
```bash
# In separate terminal
source ai-tutor-env/bin/activate

# Start frontend server (port 3000)
python run_frontend.py

# Frontend available at: http://localhost:3000
```

### **System Health Check**
```bash
# Run comprehensive system validation
python test_basic_functionality.py

# Expected output:
# ✅ Database connectivity: PASS
# ✅ AI service routing: PASS  
# ✅ Speech processing: PASS
# ✅ Authentication: PASS
# ✅ Cost tracking: PASS
```

---

## 🧪 5. Testing and Validation

### **Basic Functionality Tests**
```bash
# Core system tests
python test_basic_functionality.py

# Speech processing validation
python test_watson_stt.py

# AI service routing tests
python -c "
from app.services.ai_router import route_ai_request
result = route_ai_request('Hello, test message', 'english', 'claude')
print('✅ AI routing test:', 'PASS' if result else 'FAIL')
"
```

### **Comprehensive Testing Suite**
```bash
# Run all tests
python test_comprehensive_functionality.py

# Frontend integration tests (when available)
python comprehensive_frontend_test.py

# Performance and load tests
python test_performance_benchmarks.py
```

---

## 🏗️ 6. Development Workflow

### **Daily Development Process**
```bash
# 1. Start development session
source ai-tutor-env/bin/activate
git pull origin main

# 2. Check current task status
cat docs/project-management/TASK_TRACKER.json | jq '.project_info.current_task'

# 3. Start servers
python run_backend.py &  # Background process
python run_frontend.py   # Foreground (when available)

# 4. Monitor application logs
tail -f logs/app.log
```

### **Code Quality and Testing**
```bash
# Before committing changes
python -m pytest tests/
python -m black app/  # Code formatting
python -m flake8 app/  # Linting

# Database migrations (if needed)
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

---

## 🛠️ 7. Troubleshooting

### **Common Issues and Solutions**

#### **Audio Processing Issues**
```bash
# macOS audio permissions
# Go to System Preferences > Security & Privacy > Microphone
# Enable permission for Terminal/IDE

# Test microphone access
python -c "
import pyaudio
p = pyaudio.PyAudio()
print('Audio devices:', p.get_device_count())
p.terminate()
"
```

#### **Database Connection Issues**
```bash
# Reset databases
rm -rf data/
python -c "from app.database.config import init_database; init_database()"
python init_sample_data.py
```

#### **API Key Issues**
```bash
# Verify environment variables loaded
python -c "
import os
keys = ['ANTHROPIC_API_KEY', 'WATSON_STT_API_KEY', 'WATSON_TTS_API_KEY']
for key in keys:
    status = '✅ SET' if os.getenv(key) else '❌ MISSING'
    print(f'{key}: {status}')
"
```

#### **Port Conflicts**
```bash
# Check if ports are in use
lsof -i :8000  # Backend port
lsof -i :3000  # Frontend port

# Kill processes if needed
kill -9 $(lsof -t -i:8000)
kill -9 $(lsof -t -i:3000)
```

### **Getting Help**
1. **Check Documentation**: Review relevant docs in `docs/` directory
2. **Run Diagnostics**: Use provided test scripts to identify issues
3. **Check Logs**: Monitor `logs/app.log` for error details
4. **Verify Configuration**: Ensure all API keys and environment variables are correct

---

## 📊 8. Production Considerations

### **Database Migration (Future)**
When scaling beyond development, migrate to MariaDB:

```sql
-- MariaDB production setup
CREATE DATABASE ai_language_tutor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ai_tutor_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON ai_language_tutor.* TO 'ai_tutor_user'@'localhost';
FLUSH PRIVILEGES;
```

Update environment:
```bash
DATABASE_URL=mysql+pymysql://ai_tutor_user:secure_password@localhost/ai_language_tutor
```

### **Security Hardening**
```bash
# Generate strong production keys
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Set production configuration
DEBUG=false
LOG_LEVEL=WARNING
```

### **Cost Monitoring**
The application includes automatic cost tracking for the $30/month budget:
- Real-time API usage monitoring
- Automatic alerts when approaching limits
- Monthly usage reports and optimization suggestions

---

## ✅ Setup Completion Checklist

Verify your setup is complete:

- [ ] **Environment**: Python 3.12+ virtual environment activated
- [ ] **Dependencies**: All packages installed including audio libraries
- [ ] **API Keys**: All required API keys configured in `.env`
- [ ] **Databases**: SQLite, ChromaDB, and DuckDB operational
- [ ] **Servers**: Backend API server starts successfully
- [ ] **Tests**: Basic functionality tests pass
- [ ] **Audio**: Microphone and speakers working
- [ ] **Cost Tracking**: Budget monitoring active

**Ready for Development!** 🎉

For ongoing development, see:
- [Project Management](../project-management/TASK_TRACKER.json) - Current tasks and progress
- [Architecture Documentation](../architecture/) - Technical specifications
- [Quality Gates](../project-management/QUALITY_GATES.md) - Testing and validation requirements