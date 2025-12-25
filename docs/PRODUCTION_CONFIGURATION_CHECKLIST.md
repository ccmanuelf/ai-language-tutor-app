# Production Configuration Checklist - Phase 7

**Date**: December 25, 2025  
**Phase**: Phase 7 - Production Certification  
**Status**: IN PROGRESS

---

## Overview

This checklist validates all production configuration requirements for deploying the AI Language Tutor App to a production environment.

---

## 1. Environment Variables Configuration

### Required Environment Variables (CRITICAL)

#### Security Keys (MUST GENERATE NEW FOR PRODUCTION)
- [ ] **SECRET_KEY**: Session signing key
  - Current: `dev-secret-key-change-in-production` (DEFAULT - INSECURE)
  - Production: Generate with `openssl rand -hex 32`
  - Status: ⚠️ **MUST CHANGE**
  
- [ ] **JWT_SECRET_KEY**: JWT token signing key
  - Current: `jwt-secret-key-change-in-production` (DEFAULT - INSECURE)
  - Production: Generate with `openssl rand -hex 32`
  - Status: ⚠️ **MUST CHANGE**

#### Admin Credentials (REQUIRED)
- [x] **ADMIN_EMAIL**: Admin user email
  - Example: `admin@yourdomain.com`
  - Status: ✅ Environment variable required (no default)
  
- [x] **ADMIN_USERNAME**: Admin display name
  - Example: `System Administrator`
  - Status: ✅ Environment variable supported
  
- [x] **ADMIN_PASSWORD**: Admin initial password
  - Security: Must be strong, change after first login
  - Status: ✅ Environment variable required (no default, fail-safe)

#### AI Service API Keys (AT LEAST ONE REQUIRED)
- [ ] **ANTHROPIC_API_KEY**: Claude API (Primary AI service)
  - Source: https://console.anthropic.com/
  - Status: ⚠️ Required for AI functionality
  
- [ ] **MISTRAL_API_KEY**: Mistral AI (Optional - French optimization, STT)
  - Source: https://console.mistral.ai/
  - Status: ⚙️ Optional but recommended
  
- [ ] **DEEPSEEK_API_KEY**: DeepSeek AI (Optional - Chinese optimization)
  - Source: https://platform.deepseek.com/
  - Status: ⚙️ Optional but recommended

### Optional Environment Variables

#### Application Settings
- [ ] **DEBUG**: Debug mode (default: true)
  - Production: `false`
  - Impact: Disables API docs, enables security features
  - Status: ⚠️ **MUST SET TO FALSE**
  
- [ ] **HOST**: Bind host (default: localhost)
  - Production: `0.0.0.0` or specific IP
  - Status: ⚙️ Optional
  
- [ ] **PORT**: Backend port (default: 8000)
  - Production: Your production port
  - Status: ⚙️ Optional
  
- [ ] **FRONTEND_PORT**: Frontend port (default: 3000)
  - Production: Your production frontend port
  - Status: ⚙️ Optional

#### Database Configuration
- [ ] **DATABASE_URL**: Database connection string
  - Default: `sqlite:///./data/local/app.db`
  - Production: MariaDB recommended `mysql+pymysql://user:pass@host/db`
  - Status: ⚙️ SQLite OK for small deployments, MariaDB for production scale
  
- [ ] **CHROMADB_PATH**: Vector database path (default: ./data/chromadb)
  - Status: ⚙️ Optional
  
- [ ] **DUCKDB_PATH**: Analytics database path (default: ./data/local/app.duckdb)
  - Status: ⚙️ Optional

#### CORS Configuration
- [ ] **CORS_ORIGINS**: Allowed origins for CORS
  - Current: Hardcoded `["http://localhost:3000", "http://localhost:8000"]`
  - Production: Environment variable with production URLs
  - Status: ⚠️ **NEEDS IMPLEMENTATION** (see recommendations)

#### Budget Management
- [ ] **MONTHLY_BUDGET_USD**: API cost budget (default: 30.0)
  - Status: ⚙️ Optional
  
- [ ] **COST_TRACKING_ENABLED**: Enable cost tracking (default: true)
  - Status: ⚙️ Optional

#### File Uploads
- [ ] **MAX_UPLOAD_SIZE**: Max file size in bytes (default: 52428800 = 50MB)
  - Status: ⚙️ Optional
  
- [ ] **UPLOAD_DIR**: Upload directory (default: ./data/uploads)
  - Status: ⚙️ Optional

#### JWT Settings
- [ ] **JWT_ALGORITHM**: JWT algorithm (default: HS256)
  - Status: ✅ Default is secure
  
- [ ] **ACCESS_TOKEN_EXPIRE_MINUTES**: Token expiration (default: 30)
  - Status: ✅ Default is secure

#### Ollama Local LLM
- [ ] **OLLAMA_HOST**: Ollama server URL (default: http://localhost:11434)
  - Status: ⚙️ Optional (if using local LLMs)

---

## 2. Application Configuration Review

### Debug Mode
- **Current**: `DEBUG: bool = Field(default=True)`
- **Production Requirement**: Must be `False`
- **Impact**:
  - Debug mode exposes API documentation
  - Debug mode may expose stack traces
  - Debug mode disables some security features
- **Action**: ⚠️ Set `DEBUG=false` in production environment

### API Documentation
- **Current**: Conditionally disabled when `DEBUG=False`
  ```python
  docs_url="/api/docs" if settings.DEBUG else None,
  redoc_url="/api/redoc" if settings.DEBUG else None,
  ```
- **Status**: ✅ Properly configured to disable in production

### CORS Configuration
- **Current**: Hardcoded in `app/main.py`
  ```python
  allow_origins=["http://localhost:3000", "http://localhost:8000"]
  ```
- **Production Requirement**: Should be environment-based
- **Recommendation**: 
  ```python
  allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
  ```
- **Action**: ⚠️ Implement environment-based CORS (see recommendations)

### Security Headers
- **Current**: SecurityHeadersMiddleware active
- **Headers Set**:
  - X-Content-Type-Options: nosniff ✅
  - X-Frame-Options: DENY ✅
  - X-XSS-Protection: 1; mode=block ✅
  - Strict-Transport-Security: max-age=31536000 ✅
  - Referrer-Policy: strict-origin-when-cross-origin ✅
  - Permissions-Policy: geolocation=(), microphone=(), camera=() ✅
- **Status**: ✅ Fully configured

---

## 3. Database Configuration

### SQLite (Development/Small Deployment)
- **Default**: `sqlite:///./data/local/app.db`
- **Pros**: No additional setup, file-based
- **Cons**: Limited concurrency, not suitable for high traffic
- **Recommendation**: ✅ OK for personal/family use, small deployments

### MariaDB (Production Scale)
- **Connection**: `mysql+pymysql://username:password@localhost/ai_language_tutor`
- **Pros**: Better concurrency, scalability, backups
- **Cons**: Requires separate server setup
- **Recommendation**: Use for production with >10 concurrent users

### Required Database Directories
- `./data` ✅ Auto-created
- `./data/local` ✅ Auto-created
- `./data/uploads` ✅ Auto-created
- `./data/chromadb` ✅ Auto-created
- `./logs` ✅ Auto-created

---

## 4. File System Permissions

### Required Directories (Write Access)
- [ ] `./data/` - Database and app data
- [ ] `./data/local/` - SQLite and DuckDB files
- [ ] `./data/uploads/` - User uploads
- [ ] `./data/chromadb/` - Vector database
- [ ] `./logs/` - Application logs

### Static Files (Read Access)
- [ ] `./app/static/` - Static assets
- [ ] `./app/frontend/` - Frontend code

---

## 5. Security Configuration Validation

### Secrets Management
- [x] ✅ No hardcoded passwords in source code
- [x] ✅ No hardcoded API keys in source code
- [x] ✅ Admin credentials via environment variables
- [x] ✅ API keys via environment variables
- [x] ✅ Secret keys via environment variables (with insecure defaults flagged)

### Authentication & Authorization
- [x] ✅ JWT-based authentication
- [x] ✅ Role-based access control (CHILD, PARENT, ADMIN)
- [x] ✅ Permission-based authorization
- [x] ✅ Token expiration configured (30 minutes)
- [x] ✅ Password hashing (bcrypt/scrypt)

### Network Security
- [x] ✅ HTTPS enforcement (HSTS header)
- [x] ✅ Security headers configured
- [x] ✅ CORS restrictions in place
- [ ] ⚠️ Rate limiting recommended (not implemented)

---

## 6. Production Environment File Template

### .env.production (EXAMPLE - DO NOT COMMIT)

```bash
# ===== PRODUCTION CONFIGURATION =====
# AI Language Tutor App

# ===== APPLICATION SETTINGS =====
DEBUG=false
HOST=0.0.0.0
PORT=8000
FRONTEND_PORT=3000

# ===== SECURITY KEYS (GENERATE NEW!) =====
SECRET_KEY=<GENERATE_WITH: openssl rand -hex 32>
JWT_SECRET_KEY=<GENERATE_WITH: openssl rand -hex 32>

# ===== ADMIN CREDENTIALS =====
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_USERNAME=System Administrator
ADMIN_PASSWORD=<STRONG_PASSWORD_CHANGE_AFTER_FIRST_LOGIN>

# ===== AI SERVICE API KEYS =====
ANTHROPIC_API_KEY=sk-ant-api03-XXXXX
MISTRAL_API_KEY=XXXXX
DEEPSEEK_API_KEY=XXXXX

# ===== DATABASE CONFIGURATION =====
# Production with MariaDB
DATABASE_URL=mysql+pymysql://username:password@dbhost/ai_language_tutor

# Or SQLite for small deployment
# DATABASE_URL=sqlite:///./data/local/app.db

CHROMADB_PATH=./data/chromadb
DUCKDB_PATH=./data/local/app.duckdb

# ===== CORS CONFIGURATION (IF IMPLEMENTED) =====
# CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ===== OPTIONAL SETTINGS =====
OLLAMA_HOST=http://localhost:11434
MONTHLY_BUDGET_USD=100.0
COST_TRACKING_ENABLED=true
MAX_UPLOAD_SIZE=52428800
UPLOAD_DIR=./data/uploads
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 7. Pre-Production Checklist

### Configuration
- [ ] All required environment variables set
- [ ] DEBUG=false in production
- [ ] SECRET_KEY generated and set
- [ ] JWT_SECRET_KEY generated and set
- [ ] ADMIN_PASSWORD strong and secure
- [ ] API keys obtained and configured
- [ ] Database connection tested
- [ ] File system permissions verified

### Security
- [x] Security audit completed
- [x] No hardcoded credentials
- [x] Security headers active
- [x] HTTPS enforcement configured
- [ ] SSL/TLS certificate installed
- [ ] Firewall configured
- [ ] Rate limiting (recommended)

### Testing
- [x] All 5,737 tests passing
- [x] Security tests passing
- [ ] Load testing completed
- [ ] Production environment smoke test

### Documentation
- [x] .env.example updated
- [x] Security audit report created
- [ ] Deployment guide created
- [ ] Admin documentation created

---

## 8. Configuration Recommendations

### Priority: HIGH - Environment-Based CORS

**Current Issue**: CORS origins hardcoded in `app/main.py`

**Current Code**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    ...
)
```

**Recommended Fix**:
```python
import os

cors_origins = os.getenv(
    "CORS_ORIGINS", 
    "http://localhost:3000,http://localhost:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    ...
)
```

**Benefits**:
- Production URLs without code changes
- Different origins per environment
- Easier deployment

### Priority: MEDIUM - Rate Limiting

**Recommendation**: Add rate limiting to prevent abuse

**Example Implementation**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(...):
    ...
```

### Priority: LOW - Logging Configuration

**Recommendation**: Configure structured logging for production

**Example**:
```python
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file'],
    },
}
```

---

## 9. Deployment Validation Steps

### Step 1: Environment Setup
```bash
# Copy production environment template
cp .env.example .env.production

# Generate secret keys
openssl rand -hex 32  # For SECRET_KEY
openssl rand -hex 32  # For JWT_SECRET_KEY

# Edit .env.production with actual values
nano .env.production
```

### Step 2: Configuration Validation
```bash
# Test configuration loading
python3 -c "from app.core.config import get_settings; print(get_settings())"

# Verify DEBUG is false
python3 -c "from app.core.config import get_settings; assert not get_settings().DEBUG"

# Verify secrets are not defaults
python3 -c "from app.core.config import get_settings; s = get_settings(); assert 'dev-secret' not in s.SECRET_KEY"
```

### Step 3: Database Migration
```bash
# If using MariaDB, create database
mysql -u root -p -e "CREATE DATABASE ai_language_tutor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run migrations (if applicable)
# alembic upgrade head
```

### Step 4: Smoke Test
```bash
# Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test health endpoint
curl http://localhost:8000/health

# Expected: {"status":"healthy","service":"ai-language-tutor-api"}
```

---

## 10. Configuration Status Summary

### Critical Issues (MUST FIX)
1. ⚠️ **SECRET_KEY**: Default value must be changed
2. ⚠️ **JWT_SECRET_KEY**: Default value must be changed
3. ⚠️ **DEBUG**: Must be set to false in production

### High Priority Recommendations
1. ⚠️ **CORS_ORIGINS**: Implement environment-based configuration
2. ⚠️ **API Keys**: Obtain production API keys
3. ⚠️ **ADMIN_PASSWORD**: Set strong initial password

### Medium Priority Recommendations
1. ⚙️ **Database**: Consider MariaDB for production scale
2. ⚙️ **Rate Limiting**: Implement to prevent abuse
3. ⚙️ **Logging**: Configure structured logging

### Configuration Readiness
- **Security**: ⚠️ Needs production secret keys
- **Environment**: ⚠️ Needs production environment file
- **Database**: ✅ Ready (SQLite) or ⚙️ MariaDB setup needed
- **API Services**: ⚠️ Needs API keys
- **Code**: ✅ Production ready
- **Tests**: ✅ 5,737/5,737 passing

---

## Conclusion

### Production Configuration Status: READY WITH REQUIRED CHANGES

The application configuration is **production-ready** after completing the following required actions:

**MUST DO (Critical)**:
1. Generate and set `SECRET_KEY`
2. Generate and set `JWT_SECRET_KEY`
3. Set `DEBUG=false`
4. Set `ADMIN_PASSWORD`
5. Obtain and set AI service API keys

**SHOULD DO (High Priority)**:
1. Implement environment-based CORS configuration
2. Set up production database (MariaDB recommended for scale)
3. Configure SSL/TLS certificate

**RECOMMENDED**:
1. Implement rate limiting
2. Configure structured logging
3. Set up monitoring and alerting

All configuration infrastructure is in place. The application will fail safely if required environment variables are not provided.

---

**Checklist Completed**: December 25, 2025  
**Next Step**: Implement CORS environment configuration, then proceed to Deployment Readiness Assessment  
**Status**: AWAITING PRODUCTION ENVIRONMENT SETUP
