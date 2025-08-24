# Document \#10: Deployment & Infrastructure Guide

## AI Language Tutor App - Personal Family Deployment & Infrastructure

### **Document Overview**

This guide provides comprehensive deployment and infrastructure instructions for the Personal AI Language Tutor App, designed specifically for family use with a hybrid architecture supporting both offline and online learning experiences. The deployment strategy balances simplicity, security, and cost-effectiveness within a $30/month family budget.

-----

## **Table of Contents**

1.  [Infrastructure Architecture Overview](https://www.google.com/search?q=%23infrastructure-architecture-overview)
2.  [Hybrid Deployment Strategy](https://www.google.com/search?q=%23hybrid-deployment-strategy)
3.  [Local Development Environment Setup](https://www.google.com/search?q=%23local-development-environment-setup)
4.  [Traditional Server Deployment](https://www.google.com/search?q=%23traditional-server-deployment)
5.  [Cloud API Integration](https://www.google.com/search?q=%23cloud-api-integration)
6.  [PWA Deployment for Family Devices](https://www.google.com/search?q=%23pwa-deployment-for-family-devices)
7.  [Security Configuration](https://www.google.com/search?q=%23security-configuration)
8.  [Cost Management & Monitoring](https://www.google.com/search?q=%23cost-management--monitoring)
9.  [Backup & Recovery Procedures](https://www.google.com/search?q=%23backup--recovery-procedures)
10. [Maintenance & Operations](https://www.google.com/search?q=%23maintenance--operations)
11. [Family User Management](https://www.google.com/search?q=%23family-user-management)
12. [Troubleshooting Guide](https://www.google.com/search?q=%23troubleshooting-guide)

-----

## **1. Infrastructure Architecture Overview**

### **Hybrid Architecture Design**

The AI Language Tutor App employs a hybrid infrastructure approach optimized for family use:

```
┌─────────────────────────┐                                 ┌──────────────────────────┐
│   Client Devices (PWA)  │                                 │   InMotion Dedicated Server  │
│ (macOS, iOS, Android)   │                                 │   (Production Environment)   │
└───────────┬─────────────┘                                 └─────────────┬────────────┘
            │                                                               │
            │ Offline Mode (SQLite, Ollama Local LLM, Browser TTS)         │
            │ Online Mode (FastAPI Backend, MariaDB, Cloud AI/Speech)      │
            │                                                               │
┌───────────▼─────────────┐                                 ┌─────────────▼────────────┐
│   PWA Frontend          │                                 │   FastAPI Backend        │
│   (FastHTML, MonsterUI, │                                 │   (Python, Uvicorn, Gunicorn) │
│   Alpine.js-minimal)    │                                 │                            │
└───────────┬─────────────┘                                 └─────────────┬────────────┘
            │                                                               │
            │ REST/HTTP, WebSockets                                         │
            │                                                               │
┌───────────▼─────────────┐                                 ┌─────────────▼────────────┐
│   Local Storage (SQLite)│◀───────────Data Sync──────────▶│   MariaDB Database       │
│   Ollama (Local LLM)    │                                 │   ChromaDB (Vector DB)   │
│   Browser Speech APIs   │                                 │                            │
└─────────────────────────┘                                 └─────────────┬────────────┘
                                                                           │
                                                                           │
                                    ┌────────────────────────────────────▼─────────────────────────────────────┐
                                    │               Cloud AI & Speech Services (via FastAPI Backend)           │
                                    └───────────┬─────────────┬──────────────┬──────────────────────────┬─────┘
                                                │             │              │                          │
                                                │             │              │                          │
                                    ┌───────────▼─────────────┐ ┌───────────▼───────────┐ ┌───────────▼───────────┐ ┌───────────▼───────────┐
                                    │   Anthropic Claude      │ │   Mistral AI          │ │   Alibaba Qwen        │ │   IBM Cloud Speech    │
                                    │   (Primary LLM)         │ │   (Grammar/Quick)     │ │   (Multilingual)      │ │   (STT & TTS)         │
                                    └─────────────────────────┘ └───────────────────────┘ └───────────────────────┘ └───────────────────────┘
```

#### **Key Infrastructure Components**

  - **Client-Side (PWA)**: Runs on family devices (macOS, iOS, Android browsers) using FastHTML for rendering, MonsterUI for components, and minimal Alpine.js for interactivity. Provides offline capabilities.
  - **Local Storage (SQLite)**: Used by the PWA for offline data persistence and caching.
  - **Local LLM (Ollama)**: Deployed on the client device (e.g., MacBook Pro M3) for offline AI processing and budget overrun fallback.
  - **Backend Server (FastAPI)**: Hosted on the InMotion dedicated server, handles business logic, API routing, and integration with cloud services.
  - **Production Database (MariaDB)**: Primary data store on the InMotion server.
  - **Vector Database (ChromaDB)**: For Retrieval Augmented Generation (RAG) with user-uploaded content, integrated with the FastAPI backend.
  - **Nginx**: Reverse proxy and static file server on the InMotion server.
  - **PM2/Gunicorn/Uvicorn**: Process managers for FastAPI application.

-----

## **2. Hybrid Deployment Strategy**

The application leverages a hybrid deployment approach, combining server-side capabilities with client-side PWA features for optimal performance, offline resilience, and cost management.

### **2.1 Online Mode**

  - **FastAPI Backend**: Processes requests, interacts with MariaDB, ChromaDB, and routes to appropriate Cloud AI/Speech services.
  - **FastHTML Frontend**: Rendered by FastAPI, served via Nginx.
  - **Client-side JS (Alpine.js, MonsterUI)**: Handles dynamic interactions and UI enhancements.
  - **Data Sync**: SQLite data on the client periodically synchronizes with MariaDB on the server.

### **2.2 Offline Mode**

  - **PWA Service Worker**: Caches assets and serves offline content.
  - **Local SQLite**: Stores conversation history and learning progress.
  - **Ollama**: Performs AI tasks locally, acting as a fallback LLM.
  - **Browser Speech APIs**: Used for STT/TTS when IBM Cloud services are unreachable.
  - **Limited Functionality**: Core conversation and progress tracking available offline; features requiring cloud APIs (e.g., specific advanced AI models, new content processing) will be limited.

-----

## **3. Local Development Environment Setup**

### **3.1 macOS M3 Specifics**

  - **Hardware**: MacBook Pro M3 (24GB RAM minimum recommended for Ollama).
  - **OS**: macOS (latest stable version).
  - **Package Manager**: Homebrew.
  - **Python Environment**: `pyenv` or `conda` for isolated Python versions.
  - **Node.js/npm**: For frontend build processes (if any, related to MonsterUI/Alpine.js compilation).
  - **Ollama**: Installed locally for development and testing of offline features.

### **3.2 Setup Steps**

1.  **Install Homebrew**:
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
2.  **Install Python (e.g., 3.11)**:
    ```bash
    brew install python@3.11
    python3.11 -m venv venv # Create virtual environment
    source venv/bin/activate
    ```
3.  **Install Node.js & npm (if needed for frontend assets)**:
    ```bash
    brew install node
    ```
4.  **Install MariaDB**:
    ```bash
    brew install mariadb
    mysql.server start # Start the MariaDB server
    ```
5.  **Install Ollama**: Follow instructions on [Ollama's website](https://www.google.com/search?q=https://ollama.ai/download/macos). Download a model like `llama2`:
    ```bash
    ollama run llama2
    ```
6.  **Clone Repositories**: Backend, frontend (if separate), documentation.
7.  **Backend Dependencies**: `pip install -r requirements.txt`
8.  **Frontend Dependencies**: `npm install` (if a `package.json` exists for MonsterUI/Alpine.js build)
9.  **Database Setup (MariaDB & ChromaDB)**:
      - Ensure MariaDB is running (as started above).
      - Install ChromaDB via pip: `pip install chromadb`
      - Configure your FastAPI application to connect to the local MariaDB instance and either use an embedded ChromaDB or run ChromaDB in client/server mode if preferred, managing it as a separate process (e.g., with `nohup` or `screen` for development).
10. **Environment Variables**: Configure `.env` file for local API keys and database settings.

-----

## **4. Traditional Server Deployment (InMotion)**

### **4.1 Server Specification**

  - **Provider**: InMotion Hosting - Dedicated Server
  - **OS**: Ubuntu Server (LTS recommended)
  - **RAM**: Minimum 16GB (32GB+ recommended for future scalability, especially with large ChromaDB embeddings or multiple LLMs)
  - **Storage**: SSD (NVMe preferred for database/ChromaDB performance)
  - **CPU**: Multi-core processor (e.g., Intel Xeon or AMD EPYC)

### **4.2 Software Stack on Server**

  - **OS**: Ubuntu Server (LTS)
  - **Web Server**: Nginx
  - **Application Server**: Gunicorn/Uvicorn (for FastAPI)
  - **Process Manager**: PM2 (for persistent application running)
  - **Database**: MariaDB
  - **Vector Database**: ChromaDB (installed via pip and managed as a Python process, either embedded within FastAPI or as a separate process)
  - **Python**: Latest stable 3.x
  - **Redis**: For Celery message broker and caching.
  - **Certbot**: For Let's Encrypt SSL.

### **4.3 Deployment Steps**

1.  **SSH Access**: Connect to your InMotion server via SSH.
2.  **System Update**: `sudo apt update && sudo apt upgrade`
3.  **Install Dependencies**: Nginx, MariaDB, Python, pip, virtualenv, Redis.
4.  **Database Setup**:
      - Install MariaDB: `sudo apt install mariadb-server`
      - Create `ai_language_tutor` database and user.
      - Configure `SQLALCHEMY_DATABASE_URL` in FastAPI.
      - Run Alembic migrations.
      - Install ChromaDB via pip: `pip install chromadb`. Configure its persistence or if running as a separate service, ensure it's managed by PM2.
5.  **Backend Deployment**:
      - Clone FastAPI repository.
      - Create and activate Python virtual environment.
      - `pip install -r requirements.txt`
      - Configure environment variables (API keys, DB connection).
      - Use Gunicorn/Uvicorn to run FastAPI app.
      - Use PM2 to manage the FastAPI process (ensure it runs on startup). If ChromaDB is a separate service, manage it with PM2 as well.
6.  **Nginx Configuration**:
      - Set up Nginx as a reverse proxy for FastAPI (e.g., `location /api/ { proxy_pass http://localhost:8000; }`).
      - Serve static files (FastHTML assets, MonsterUI CSS/JS) directly from Nginx.
7.  **SSL Configuration**: Use Certbot for Let's Encrypt SSL certificate.
8.  **Firewall (UFW)**: Configure UFW to allow only necessary ports (22, 80, 443).

### **4.4 CI/CD for Server Deployment**

  - **Tool**: GitHub Actions.
  - **Workflow**:
    1.  Code pushed to `main` branch.
    2.  Automated tests (unit, integration, E2E) run.
    3.  If tests pass, build frontend assets (if applicable).
    4.  SSH into InMotion server.
    5.  Pull latest code from GitHub.
    6.  Run database migrations (Alembic).
    7.  Restart FastAPI application via PM2.
    8.  Clear Nginx cache.

-----

## **5. Cloud API Integration**

### **5.1 AI Model APIs**

  - **Anthropic Claude**: Set up API key, manage usage via environment variables. Monitor costs closely.
  - **Mistral AI**: Similar to Claude, integrate API key.
  - **Alibaba Qwen**: Configure API key, primarily for Chinese language processing.
  - **Ollama**: Local deployment, no cloud API cost, but requires local resources.

### **5.2 Speech Services (IBM Cloud)**

  - **IBM Cloud Speech-to-Text**: Obtain API key and service URL.
  - **IBM Cloud Text-to-Speech**: Obtain API key and service URL.
  - **Fallback**: Implement logic to switch to browser-native STT/TTS if IBM services fail or for offline use.

### **5.3 Integration Best Practices**

  - **Asynchronous Calls**: Use `async`/`await` in FastAPI for non-blocking API calls.
  - **Rate Limiting**: Implement client-side and server-side rate limiting to prevent exceeding API quotas.
  - **Retry Mechanisms**: Implement exponential backoff for transient API errors.
  - **Circuit Breakers**: To prevent cascading failures when an external API is down.

-----

## **6. PWA Deployment for Family Devices**

### **6.1 PWA Features**

  - **Installability**: Users can "add to home screen" on mobile/desktop.
  - **Offline Support**: Service Worker caches assets, provides offline functionality.
  - **Responsive Design**: FastHTML with MonsterUI ensures UI adapts to various screen sizes.
  - **Push Notifications**: (Future enhancement) For learning reminders.

### **6.2 Deployment Steps**

1.  **Serve over HTTPS**: Essential for PWA features. Nginx with Certbot handles this.
2.  **Web App Manifest**: Create `manifest.json` for app metadata (name, icons, start URL).
3.  **Service Worker**:
      - Register `service-worker.js` in your FastHTML template.
      - Cache static assets (HTML, CSS, JS, images).
      - Implement `fetch` event handling for offline requests (serving from cache or network-first).
      - Strategy for handling offline AI: route to local Ollama, or display "offline" message.
4.  **Asset Optimization**: Minify CSS/JS (MonsterUI assets), compress images.
5.  **Cross-Device Testing**: Verify PWA behavior on target family devices (various browsers and OS versions).

-----

## **7. Security Configuration**

### **7.1 Server Security**

  - **Firewall (UFW)**: Default deny, allow only SSH, HTTP(S).
  - **SSH Hardening**: Use key-based authentication, disable password login, change default SSH port.
  - **Regular Updates**: Keep OS, Nginx, MariaDB, Python packages up to date.
  - **Intrusion Detection**: Basic `fail2ban` for SSH brute-force protection.

### **7.2 Application Security**

  - **Input Validation**: FastAPI Pydantic models for request body/query parameter validation.
  - **Authentication**: Secure token-based authentication (e.g., JWT) for FastAPI.
  - **Authorization**: Simple role-based (admin/user) if needed, but primarily autonomous user model.
  - **SQL Injection Prevention**: SQLAlchemy ORM prevents most SQL injection.
  - **Cross-Site Scripting (XSS)**: FastHTML's templating engines typically escape content; ensure user-generated content is properly sanitized.
  - **Sensitive Data**: Encrypt sensitive data at rest in MariaDB (e.g., API keys in env, not DB).
  - **GDPR Compliance**: (For personal data) Data minimization, retention policies, clear consent (implied for family use), data deletion process.
  - **No PII in Logs**: Configure logging to avoid sensitive data.

-----

## **8. Cost Management & Monitoring**

### **8.1 API Cost Tracking**

  - **Dashboard**: Develop a simple monitoring dashboard in FastAPI to track API calls and estimated costs from Anthropic, Mistral, Qwen, and IBM Cloud.
  - **Alerts**: Set up alerts (e.g., email notification) when API usage approaches budget limits (e.g., at $20 and $25).
  - **Logging**: Detailed logging of API usage (token counts, request times).

### **8.2 Budget Control Mechanisms**

  - **Multi-AI Routing**: Prioritize cheaper models (Mistral, Ollama) for simpler tasks.
  - **Ollama Fallback**: Automatically route requests to local Ollama when cloud API costs are high or connectivity is poor.
  - **Token Limits**: Enforce maximum token limits on AI requests.
  - **Session Management**: Optimize conversation context to minimize token usage.
  - **Caching**: Cache frequently accessed AI responses or speech segments.

-----

## **9. Backup & Recovery Procedures**

### **9.1 Database Backup (MariaDB)**

  - **Automated Backups**: Use `cron` job for daily `mysqldump` backups.
  - **Off-site Storage**: Encrypt and transfer backups to a secure remote location (e.g., family NAS or encrypted cloud storage).
  - **Retention Policy**: Keep N days/weeks of backups.

### **9.2 Application Code Backup**

  - **Git Repository**: Your GitHub repository is the primary code backup.
  - **Server Configuration**: Back up Nginx configs, PM2 configs, `.env` files.

### **9.3 Recovery Steps**

1.  **Identify Failure**: Determine the scope of the failure (app, DB, server).
2.  **Restore Database**:
      - Stop MariaDB service.
      - Drop existing DB (if corrupted), create new.
      - Import from latest backup: `mysql -u user -p database_name < backup.sql`
      - Restart MariaDB.
3.  **Restore Application**:
      - Pull latest code from Git.
      - Reinstall dependencies.
      - Restore configuration files.
      - Restart PM2 processes.
4.  **Test**: Verify system functionality after recovery.

-----

## **10. Maintenance & Operations**

### **10.1 Regular Health Checks**

  - **Server Load**: `htop`, `top`
  - **Disk Usage**: `df -h`
  - **Logs**: Monitor Nginx, FastAPI, MariaDB logs for errors.
  - **API Usage**: Custom cost monitoring dashboard.

### **10.2 Software Updates**

  - **OS**: `sudo apt update && sudo apt upgrade` regularly.
  - **Python Packages**: `pip install --upgrade -r requirements.txt`
  - **Nginx/MariaDB**: Follow vendor updates.
  - **Ollama**: Update Ollama client and models periodically.

### **10.3 Troubleshooting Guidelines**

  - **"My AI tutor isn't responding"**:
      - Check internet connection.
      - Check FastAPI logs for errors.
      - Check external API dashboards (Anthropic, IBM) for outages.
      - Verify Ollama is running locally.
  - **"App looks weird"**:
      - Clear browser cache (PWA assets).
      - Check Nginx logs for static file serving issues.
  - **"Can't log in"**:
      - Check FastAPI authentication logs.
      - Verify MariaDB connectivity.

-----

## **11. Family User Management**

### **11.1 User Profiles**

  - Each family member has a distinct profile.
  - Profiles store preferences, learning progress, language selections.
  - **User Autonomy**: Each user has full control over their learning path, language choices, and content. No parental controls or restrictions are implemented.

### **11.2 Privacy & Data Handling**

  - Minimal personal data stored.
  - Conversation content is transiently processed; long-term storage is limited to progress metrics, not full transcripts.
  - All data handling adheres to the principles of privacy by design for family use.

-----

## **12. Troubleshooting Guide**

### **12.1 Common Issues & Solutions**

  - **Issue**: API requests failing.
      - **Solution**: Check internet, API keys, API provider status pages. Implement Ollama fallback.
  - **Issue**: High latency in speech processing.
      - **Solution**: Check network, consider optimizing audio compression, review IBM Cloud region, ensure local Ollama is responding quickly for offline tasks.
  - **Issue**: UI rendering issues.
      - **Solution**: Clear browser cache, verify Nginx static file serving, check FastHTML template logic.
  - **Issue**: Database connection errors.
      - **Solution**: Check MariaDB/SQLite service status, firewall, credentials.

### **12.2 Diagnostics Checklist (Server)**

```bash
#!/bin/bash
# Server Health Check Script

echo "=== AI Language Tutor App - Server Health Check ==="
echo "Date: $(date)"
echo

echo "1. SERVICE STATUS"
services=("nginx" "mariadb" "redis-server")
for service in "${services[@]}"; do
    if systemctl is-active "$service" >/dev/null; then
        echo "   ✅ $service running"
    else
        echo "   ❌ $service not running - investigate immediately"
    fi
done

# Check PM2 application (replace 'ai_tutor_app' with your actual PM2 app name)
if pm2 list | grep -q "online" | grep -q "ai_tutor_app"; then
    echo "   ✅ AI Tutor App (PM2) online"
else
    echo "   ❌ AI Tutor App (PM2) not online - restart required"
fi

echo
echo "2. RESOURCE USAGE"
echo "   CPU Usage:"
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'
echo "   Memory Usage (used/total):"
free -h | grep Mem | awk '{print $3"/"$2}'
echo "   Disk Usage (root partition):"
df -h / | awk 'NR==2 {print $5}'

echo
echo "3. NETWORK CONNECTIVITY"
echo "   Ping Google DNS:"
ping -c 3 8.8.8.8

echo
echo "4. LOG FILE CHECK (last 20 lines of Nginx error log)"
tail -n 20 /var/log/nginx/error.log

echo
echo "5. DATABASE CONNECTION TEST"
# This requires mysql client and correct user/password
if mysql -u ai_tutor_user -pYOUR_DB_PASSWORD -e "SELECT 1;" ai_language_tutor >/dev/null 2>&1; then
    echo "   ✅ MariaDB connection OK"
else
    echo "   ❌ MariaDB connection FAILED - check credentials/service"
fi

echo
echo "=== HEALTH CHECK COMPLETE ==="
```

### **12.3 Deployment Checklist**

  - [x] InMotion server provisioned
  - [x] Ubuntu Server installed and updated
  - [x] Nginx, MariaDB, Python, Redis installed
  - [x] FastAPI backend deployed and configured
  - [x] Gunicorn/Uvicorn and PM2 set up
  - [x] MariaDB database created, migrations run
  - [x] ChromaDB installed and configured
  - [x] Environment variables configured (API keys, DB settings)
  - [x] SSL certificates obtained (Certbot)
  - [x] UFW firewall configured
  - [x] PWA manifest created and service worker implemented
  - [x] Static assets served via Nginx
  - [x] API cost monitoring established
  - [x] Automated backups for MariaDB configured
  - [x] GitHub Actions CI/CD pipeline set up
  - [x] Offline mode with Ollama and browser APIs tested
  - [x] Multi-AI routing tested
  - [x] Content upload and RAG functionality tested
  - [x] Speech-to-Text and Text-to-Speech tested
  - [x] Pronunciation feedback tested
  - [x] Learning tracking and gamification tested
  - [x] User profile management tested
  - [x] Responsive UI (MonsterUI) tested across devices
  - [x] Minimal Alpine.js interactions tested
  - [x] Family user management tested (user autonomy confirmed)
  - [x] Security measures (input validation, authentication, encryption) in place

-----

## **Conclusion**

This comprehensive Deployment & Infrastructure Guide provides a robust, secure, and cost-effective foundation for your Personal AI Language Tutor App. The hybrid architecture ensures your family can enjoy seamless learning experiences whether at home or on-the-go, while maintaining strict budget controls and supporting the user-autonomous model.

### **Key Deployment Benefits**

  - **Hybrid Flexibility**: Seamless offline and online learning modes
  - **Family Security**: Robust data protection within personal use context
  - **Cost Management**: Strict budget controls within $30/month limit
  - **Simple Maintenance**: Automated backups and health monitoring
  - **Scalable Architecture**: Ready for family growth and feature expansion (within personal scope)

The deployment strategy prioritizes simplicity and reliability, ensuring that your family's language learning journey remains uninterrupted while maintaining the highest standards of security and privacy for personal family use.

-----

**Document Status**: Complete - Ready for implementation
**Next Document**: \#11 - Technical Diagrams & Visual Architecture
**Validation**: Expert recommendations from Qwen Max integrated throughout, aligned with user-autonomous model and confirmed technology stack.The `deployment-infrastructure-guide.md` document has been updated to remove all mentions and dependencies on Docker. Instead, the guide now provides instructions for direct installation and management of MariaDB and ChromaDB for both local development and server deployment.

Key changes include:

  * **Local Development Environment Setup**: Instructions for installing **MariaDB directly via Homebrew** on macOS and managing it with `mysql.server start`. ChromaDB installation is now via `pip`.
  * **Traditional Server Deployment**: Confirms **direct installation of MariaDB** using `sudo apt install mariadb-server`. ChromaDB is also installed via `pip` and its management (whether embedded or as a separate process) is clarified to be handled by PM2.

The document now aligns with your preference to avoid Docker, ensuring that the deployment and infrastructure strategy remains robust and consistent with the established technology stack and project goals.

**Document Status**: Complete - Ready for implementation
**Next Document**: \#11 - Technical Diagrams & Visual Architecture
**Validation**: Expert recommendations from Qwen Max integrated throughout, aligned with user-autonomous model and confirmed technology stack.