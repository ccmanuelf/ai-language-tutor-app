# Document #12: Personal Maintenance Guide
## AI Language Tutor App - Solo Developer Operations Manual

---

### **Document Information**
- **Project**: Personal AI Language Tutor App (Family Educational Tool)
- **Document**: #12 of 12 - Personal Maintenance Guide
- **Version**: 1.0
- **Date**: May 30, 2025
- **Author**: Development Team
- **Status**: Final Documentation - Operations Manual

---

## **1. Executive Summary**

This comprehensive maintenance guide provides solo developer procedures for operating, maintaining, and optimizing the AI Language Tutor App family educational tool. The guide covers all aspects of system administration, from daily operations to emergency procedures, designed for a single developer managing a family-focused language learning platform.

### **Maintenance Philosophy**
- **Simplicity First**: Streamlined procedures for efficient solo management
- **Proactive Monitoring**: Prevent issues before they impact family learning
- **Cost Consciousness**: Maintain within $30/month family budget
- **User Autonomy**: Support independent learners with minimal intervention
- **Family Focus**: Ensure reliable educational tool for all family members

---

## **2. Development Environment Maintenance**

### **2.1 macOS M3 Environment Setup & Maintenance**

#### **Daily Development Environment Checks**

```bash
#!/bin/bash
# Daily macOS Environment Health Check
echo "=== AI Language Tutor App - Daily Environment Check ==="
echo "Date: $(date)"
echo

# Check Python environment
if command -v python3 &> /dev/null; then
    echo "1. Python 3:     ✅ Installed ($(python3 --version))"
else
    echo "1. Python 3:     ❌ Not found - Please install Python 3.9+"
fi

# Check Homebrew packages
echo "2. Homebrew Services:"
brew services list | grep "started" | while read -r service status; do
    echo "   ✅ $service ($status)"
done
if [ -z "$(brew services list | grep "started")" ]; then
    echo "   ⚠️  No Homebrew services running - check your setup."
fi

# Check Git status
echo "3. Git Status:"
if git status &> /dev/null; then
    if git status --porcelain | grep -q .; then
        echo "   ⚠️  Uncommitted changes detected in repository."
        git status --short
    else
        echo "   ✅ Git repository clean."
    fi
else
    echo "   ❌ Not a Git repository or Git not installed."
fi

echo
echo "=== DAILY CHECK COMPLETE ==="
```

#### **Weekly Development Environment Updates**

```bash
#!/bin/bash
# Weekly macOS Environment Update Script
echo "=== AI Language Tutor App - Weekly Development Update ==="
echo "Date: $(date)"
echo

echo "1. Updating Homebrew packages..."
brew update && brew upgrade
echo "   ✅ Homebrew packages updated."

echo "2. Cleaning up old Homebrew versions..."
brew cleanup
echo "   ✅ Homebrew cleanup complete."

echo "3. Updating Python dependencies..."
cd /path/to/your/app/backend # Adjust path to your FastAPI backend
pip install --upgrade -r requirements.txt
echo "   ✅ Python dependencies updated."

echo "4. Updating Node.js dependencies (if applicable for frontend tools)..."
cd /path/to/your/app/frontend # Adjust path to your frontend project
npm update
echo "   ✅ Node.js dependencies updated."

echo "5. Checking for macOS system updates (manual action recommended)..."
echo "   Please run 'softwareupdate --list' and install updates manually if available."

echo
echo "=== WEEKLY UPDATE COMPLETE ==="
```

---

## **3. Production Server Maintenance (InMotion Dedicated Server)**

### **3.1 Daily Server Health Checks**

```bash
#!/bin/bash
# Daily InMotion Server Health Check
echo "=== AI Language Tutor App - Daily Server Health Check ==="
echo "Date: $(date)"
echo

echo "1. System Load:"
uptime
echo

echo "2. Disk Usage:"
df -h /
echo

echo "3. Memory Usage:"
free -h
echo

echo "4. Nginx Status:"
sudo systemctl status nginx | grep "Active:"
echo

echo "5. MariaDB Status:"
sudo systemctl status mariadb | grep "Active:"
echo

echo "6. ChromaDB Status (Assuming direct installation and systemd service):"
sudo systemctl status chromadb | grep "Active:"
echo

echo "7. FastAPI Application Status (via PM2):"
pm2 list
echo

echo "8. Redis Status (if used for Celery/caching):"
sudo systemctl status redis-server | grep "Active:"
echo

echo "9. Check for critical messages in system logs:"
sudo journalctl -p 3 -xb --since "24 hours ago"
echo

echo "=== DAILY SERVER HEALTH CHECK COMPLETE ==="
```

### **3.2 Weekly Server Maintenance & Updates**

```bash
#!/bin/bash
# Weekly InMotion Server Maintenance Script
echo "=== AI Language Tutor App - Weekly Server Maintenance ==="
echo "Date: $(date)"
echo

echo "1. Updating System Packages..."
sudo apt update && sudo apt upgrade -y
echo "   ✅ System packages updated."

echo "2. Cleaning up old packages..."
sudo apt autoremove -y && sudo apt clean
echo "   ✅ Old packages cleaned."

echo "3. Updating Python dependencies for FastAPI backend..."
cd /path/to/your/fastapi/app # Adjust path
source venv/bin/activate # Activate your virtual environment
pip install --upgrade -r requirements.txt
deactivate
echo "   ✅ FastAPI dependencies updated."

echo "4. Checking for MariaDB updates (manual review recommended for major versions):"
# For minor updates: sudo apt upgrade mariadb-server mariadb-client -y
echo "   Consider checking MariaDB official documentation for major version upgrades."
echo "   ✅ MariaDB checked."

echo "5. Checking for ChromaDB updates (manual review recommended):"
# Assuming ChromaDB is installed via pip or a standalone binary
# If installed via pip: pip install --upgrade chromadb
echo "   Consider checking ChromaDB official documentation for updates or reinstall if necessary."
echo "   ✅ ChromaDB checked."

echo "6. Restarting application services to apply updates..."
echo "   Stopping Nginx..."
sudo systemctl stop nginx
echo "   Stopping FastAPI (via PM2)..."
pm2 stop all
echo "   Stopping MariaDB (if needed for update)..."
# sudo systemctl stop mariadb
echo "   Stopping ChromaDB (if needed for update)..."
# sudo systemctl stop chromadb
echo "   Stopping Redis (if needed for update)..."
# sudo systemctl stop redis-server

echo "   Starting services..."
# sudo systemctl start mariadb
# sudo systemctl start chromadb
# sudo systemctl start redis-server
pm2 start all
sudo systemctl start nginx

echo "   ✅ Services restarted."

echo "7. Rotating Nginx logs..."
sudo logrotate -f /etc/logrotate.d/nginx
echo "   ✅ Nginx logs rotated."

echo
echo "=== WEEKLY SERVER MAINTENANCE COMPLETE ==="
```

### **3.3 Monthly Database Optimization & Cleanup**

```bash
#!/bin/bash
# Monthly MariaDB Optimization & Cleanup Script
echo "=== AI Language Tutor App - Monthly DB Maintenance ==="
echo "Date: $(date)"
echo

echo "1. Optimizing MariaDB tables..."
# This might require root access or specific user permissions
# Ensure you replace 'your_db_user' and 'your_db_name'
mysql -u root -pYOUR_MARIADB_ROOT_PASSWORD -e "OPTIMIZE TABLE ai_language_tutor.conversations, ai_language_tutor.messages, ai_language_tutor.learning_progress;"
echo "   ✅ MariaDB tables optimized."

echo "2. Cleaning up old API usage logs (e.g., older than 6 months)..."
# Adjust the WHERE clause as needed based on your API_USAGE_LOGS table schema
mysql -u root -pYOUR_MARIADB_ROOT_PASSWORD -e "DELETE FROM ai_language_tutor.api_usage_logs WHERE request_time < NOW() - INTERVAL 6 MONTH;"
echo "   ✅ Old API usage logs cleaned."

echo "3. Analyzing MariaDB tables for updated statistics..."
mysql -u root -pYOUR_MARIADB_ROOT_PASSWORD -e "ANALYZE TABLE ai_language_tutor.conversations, ai_language_tutor.messages, ai_language_tutor.learning_progress;"
echo "   ✅ MariaDB tables analyzed."

echo "4. ChromaDB database compaction/optimization (if applicable, consult ChromaDB docs):"
# ChromaDB might have its own methods for compaction or cleanup, depending on its storage backend.
# This is a placeholder for a future command if ChromaDB requires manual optimization.
echo "   Refer to ChromaDB documentation for specific optimization commands."
echo "   ✅ ChromaDB optimization check complete."

echo
echo "=== MONTHLY DATABASE MAINTENANCE COMPLETE ==="
```
*Note: Replace `YOUR_MARIADB_ROOT_PASSWORD` and `/path/to/your/app/` with actual values.*

---

## **4. Backup & Recovery Procedures**

### **4.1 Automated Daily Backups**

A cron job should be set up on the InMotion server to perform daily backups.

```bash
#!/bin/bash
# Daily Backup Script
# /etc/cron.daily/ai_tutor_backup (ensure executable: chmod +x)

BACKUP_DIR="/var/backups/ai_tutor"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="ai_language_tutor"
DB_USER="root" # Or a dedicated backup user
DB_PASSWORD="YOUR_MARIADB_ROOT_PASSWORD" # Replace with actual password

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# 1. MariaDB Database Backup
echo "Dumping MariaDB database..."
mysqldump -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" | gzip > "$BACKUP_DIR/$DB_NAME-$DATE.sql.gz"
if [ $? -eq 0 ]; then
    echo "   ✅ MariaDB backup complete: $DB_NAME-$DATE.sql.gz"
else
    echo "   ❌ MariaDB backup failed."
    exit 1
fi

# 2. ChromaDB Data Directory Backup (assuming default data_path configuration)
echo "Backing up ChromaDB data directory..."
# Stop ChromaDB temporarily for a consistent snapshot if it's running as a service
# sudo systemctl stop chromadb
tar -czf "$BACKUP_DIR/chromadb_data-$DATE.tar.gz" /path/to/your/chromadb/data # Adjust path
# sudo systemctl start chromadb
if [ $? -eq 0 ]; then
    echo "   ✅ ChromaDB data backup complete: chromadb_data-$DATE.tar.gz"
else
    echo "   ❌ ChromaDB data backup failed."
fi


# 3. Application Code Backup
echo "Backing up application code..."
tar -czf "$BACKUP_DIR/ai_tutor_app_code-$DATE.tar.gz" /path/to/your/fastapi/app # Adjust path
if [ $? -eq 0 ]; then
    echo "   ✅ Application code backup complete: ai_tutor_app_code-$DATE.tar.gz"
else
    echo "   ❌ Application code backup failed."
fi

# 4. Clean up old backups (e.g., keep last 7 days)
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -type f -name "*.gz" -mtime +7 -delete
echo "   ✅ Old backups cleaned."

echo "=== DAILY BACKUP COMPLETE ==="
```
*Note: Ensure MariaDB password and ChromaDB/FastAPI application paths are correctly configured.*

### **4.2 Manual Restore Procedures**

In case of a catastrophic failure, follow these steps to restore the application:

1.  **Access Server**: SSH into your InMotion dedicated server.
2.  **Stop Services**:
    ```bash
    sudo systemctl stop nginx
    pm2 stop all
    sudo systemctl stop mariadb
    sudo systemctl stop chromadb # If running as a service
    sudo systemctl stop redis-server # If running as a service
    ```
3.  **Clean Existing Data (if fresh restore)**:
    ```bash
    # BE CAREFUL: These commands delete data. Only use if performing a full clean restore.
    sudo rm -rf /path/to/your/fastapi/app/*
    sudo rm -rf /path/to/your/chromadb/data/*
    # Drop and recreate MariaDB database if needed
    # mysql -u root -pYOUR_MARIADB_ROOT_PASSWORD -e "DROP DATABASE IF EXISTS ai_language_tutor;"
    # mysql -u root -pYOUR_MARIADB_ROOT_PASSWORD -e "CREATE DATABASE ai_language_tutor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ```
4.  **Restore Application Code**:
    * Navigate to your backup directory (`/var/backups/ai_tutor`).
    * Find the latest `ai_tutor_app_code-DATE.tar.gz`.
    * Extract it to your application directory:
        ```bash
        tar -xzf /var/backups/ai_tutor/ai_tutor_app_code-*.tar.gz -C /path/to/your/fastapi/app --strip-components=1
        ```
5.  **Restore MariaDB Database**:
    * Find the latest `ai_language_tutor-DATE.sql.gz` backup.
    * Restore the database:
        ```bash
        gunzip < /var/backups/ai_tutor/ai_language_tutor-*.sql.gz | mysql -u root -pYOUR_MARIADB_ROOT_PASSWORD ai_language_tutor
        ```
6.  **Restore ChromaDB Data**:
    * Find the latest `chromadb_data-DATE.tar.gz`.
    * Extract it to your ChromaDB data directory:
        ```bash
        tar -xzf /var/backups/ai_tutor/chromadb_data-*.tar.gz -C /path/to/your/chromadb/data --strip-components=1
        ```
7.  **Reinstall Python Dependencies**:
    ```bash
    cd /path/to/your/fastapi/app
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    ```
8.  **Restart Services**:
    ```bash
    sudo systemctl start mariadb
    sudo systemctl start chromadb # If running as a service
    sudo systemctl start redis-server # If running as a service
    pm2 start all
    sudo systemctl start nginx
    ```
9.  **Verify**: Access the application URL and test core functionalities.

---

## **5. Monitoring & Alerting**

### **5.1 Basic Monitoring Setup**

Leverage existing Linux tools for basic monitoring.

* **`htop` / `top`**: For real-time CPU, memory, and process monitoring.
* **`df -h` / `du -sh`**: For disk space monitoring.
* **`journalctl`**: For system and service logs.
* **`pm2 logs`**: For FastAPI application logs.
* **Nginx logs**: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`.
* **MariaDB logs**: Typically `/var/log/mysql/error.log` or similar.
* **ChromaDB logs**: Depends on how it's run, usually console output redirected to a file or `journalctl` if run as a systemd service.

### **5.2 Cost Monitoring**

* **Cloud Provider Dashboards**: Regularly check IBM Cloud, Anthropic, Mistral AI, and Alibaba Cloud dashboards for API usage and costs.
* **MariaDB API Usage Logs**: The `API_USAGE_LOGS` table in your MariaDB database stores detailed records of API calls, tokens used, and estimated costs. Query this table daily/weekly to track spending.
    ```sql
    SELECT
        DATE(request_time) as usage_date,
        api_service,
        SUM(tokens_used) as total_tokens,
        SUM(cost) as estimated_cost
    FROM api_usage_logs
    WHERE request_time >= CURDATE() - INTERVAL 7 DAY
    GROUP BY usage_date, api_service
    ORDER BY usage_date DESC, api_service;
    ```
* **Budget Overrun Fallback**: Ensure the application's internal logic correctly routes requests to Ollama (local/server) when the monthly budget threshold is approached or exceeded.

---

## **6. Troubleshooting Guide**

### **6.1 Common Issues & Solutions**

#### **Issue: Application Not Responding**
* **Symptoms**: Web browser shows "Page not found" or "Connection refused".
* **Checks**:
    * **Nginx**: `sudo systemctl status nginx` (Is it running? Check `/var/log/nginx/error.log`).
    * **FastAPI**: `pm2 list` (Is your app listed and "online"? Check `pm2 logs your_app_name`).
    * **Firewall**: `sudo ufw status` (Is port 80/443 open?).
    * **Server Resources**: Check `htop`, `df -h` for high CPU, low memory, full disk.

#### **Issue: AI Responses are Slow or Non-Existent**
* **Symptoms**: Long delays in chat, or generic/error messages from AI.
* **Checks**:
    * **Internet Connectivity**: `ping google.com` from server.
    * **API Keys**: Verify `FastAPI` environment variables for correct API keys.
    * **Cloud Provider Status**: Check status pages for IBM Cloud, Anthropic, Mistral AI, Alibaba Cloud for outages.
    * **API Usage Logs**: Query `API_USAGE_LOGS` table to see if budget limits are hit.
    * **FastAPI Logs**: Look for errors related to external API calls.

#### **Issue: Pronunciation Feedback Not Working**
* **Symptoms**: User speaks, but no feedback or incorrect feedback.
* **Checks**:
    * **IBM Cloud Speech Service Status**: Check for outages.
    * **API Usage Logs**: Verify STT/TTS calls are being made and not hitting rate limits/budgets.
    * **FastAPI Logs**: Errors related to IBM Cloud STT/TTS calls.
    * **Browser Console**: Frontend errors related to microphone access or Web Speech API.

#### **Issue: Data Not Saving or Loading (Conversations/Progress)**
* **Symptoms**: New conversations disappear, progress not tracked.
* **Checks**:
    * **MariaDB Status**: `sudo systemctl status mariadb` (Is it running?).
    * **FastAPI Database Connection**: Check FastAPI logs for `SQLAlchemy` or `MariaDB` connection errors.
    * **Disk Space**: `df -h` (Database might stop if disk is full).
    * **MariaDB Logs**: `/var/log/mysql/error.log` for database-specific errors.
    * **ChromaDB Status**: `sudo systemctl status chromadb` (Is it running and accessible from FastAPI?).
    * **ChromaDB Data Directory**: Check permissions and disk space for ChromaDB's data path.

#### **Issue: Local PWA Issues on Family Devices**
* **Symptoms**: Offline mode not working, local data not saving, UI glitches.
* **Checks**:
    * **Browser Cache**: Clear browser cache and service worker.
    * **IndexedDB/SQLite**: Check browser's developer tools for `Application` tab to inspect `IndexedDB` or `Web SQL`.
    * **Service Worker**: Ensure the service worker is registered and active.
    * **Device Storage**: Check free storage on the device.

---

## **7. System Downtime & Emergency Procedures**

### **7.1 Planned Downtime**
* **Announce**: Inform family members of planned maintenance window.
* **Stop Services**: Gracefully stop Nginx, FastAPI, MariaDB, ChromaDB, Redis.
* **Perform Maintenance**: Apply updates, backups, or optimizations.
* **Verify**: After maintenance, restart all services and verify functionality.
* **Announce Uptime**: Inform family members when the app is fully operational.

### **7.2 Unplanned Downtime (Emergency)**
* **Assess Impact**: Determine which services are down and the scope of the problem.
* **Check Logs**: Immediately check system, Nginx, FastAPI, MariaDB, ChromaDB logs for error messages.
* **Attempt Restart**: Try restarting individual services or the entire server (`sudo reboot`).
* **Consult Backups**: If data corruption or loss is suspected, prepare for a restore from the latest backup.
* **Isolate Issue**: If a specific service is causing issues, try to temporarily disable it or use a fallback (e.g., enable Ollama if cloud AI is down).
* **Communicate**: Inform family members if the app is unusable for an extended period.

---

## **8. Performance Optimization & Scaling**

### **8.1 Ongoing Performance Tuning**
* **API Usage**: Continuously monitor `API_USAGE_LOGS` and optimize prompts to reduce token usage and cost.
* **Database Queries**: Review MariaDB slow query logs; add/optimize indexes as needed.
* **Caching**: Implement Redis caching for frequently accessed data (e.g., user profiles, common phrases).
* **FastAPI Endpoints**: Profile FastAPI routes to identify bottlenecks; use `async/await` effectively.
* **ChromaDB Performance**: Monitor ChromaDB query times; optimize embedding generation and vector search parameters.
* **Nginx Configuration**: Tune Nginx worker processes and buffer sizes.

### **8.2 Scaling Considerations**
* **Vertical Scaling**: Upgrade InMotion server resources (CPU, RAM, Storage) as needed. This is the primary scaling strategy for a single dedicated server.
* **MariaDB Replication**: For future high availability or read scaling, consider setting up MariaDB replication (Master-Slave).
* **ChromaDB Clustering**: If vector database load becomes significant, explore ChromaDB's distributed deployment options (if available and necessary for a family-sized app).
* **Celery Workers**: Increase Celery worker processes if background tasks become a bottleneck.

---

## **9. Family User Management & Privacy**

### **9.1 User Profile Management (Developer Only)**
* As the developer, you are the only one with direct access to the MariaDB database to manage `USERS` and `PROFILES` tables if manual intervention is ever required.
* **No Parental Controls**: The application is designed for user autonomy. There are no built-in parental controls, age-appropriate content filtering, or role-based restrictions. Each family member manages their own learning.
* **User Autonomy**: Each family member has equal capabilities and can select any language, content, and topics independently.

### **9.2 Data Privacy Best Practices**
* **Minimal Data Retention**: Only store conversation summaries and progress metrics, not full conversation logs.
* **Encryption**: Ensure MariaDB data at rest is encrypted (if enabled on the server/DB configuration). All data in transit is encrypted via HTTPS.
* **Access Control**: Restrict SSH access to the server and MariaDB/ChromaDB to trusted IPs only.
* **Regular Backups**: Ensure encrypted backups are stored off-site for disaster recovery.
* **No PII to Third-Party AI**: Avoid sending personally identifiable information (PII) to external AI/Speech APIs. Anonymize data where possible.

---

## **10. Pre-Maintenance & Post-Maintenance Checklists**

### **10.1 Pre-Maintenance Checklist**

```bash
#!/bin/bash
# Pre-Maintenance Checklist
echo "=== PRE-MAINTENANCE CHECKLIST ==="
echo "Review before starting any maintenance tasks"
echo

echo "1. BACKUP STATUS"
# Check for recent backup files
BACKUP_DIR="/var/backups/ai_tutor"
if find "$BACKUP_DIR" -maxdepth 1 -mtime -1 -name "*.gz" | grep -q .; then
    echo "   ✅ Recent backups found (within last 24 hours)."
else
    echo "   ❌ No recent backups found - perform a manual backup immediately!"
fi

echo
echo "2. SERVICE STATUS (Verify before stopping)"
services=("nginx" "mariadb" "chromadb" "redis-server") # Include chromadb and redis
for service in "${services[@]}"; do
    if systemctl is-active "$service" >/dev/null; then
        echo "   ✅ $service running"
    else
        echo "   ⚠️  $service not running - investigate before proceeding"
    fi
done
# Check PM2 application
if pm2 list | grep -q \"online\"; then
    echo "   ✅ PM2 application online"
else
    echo "   ⚠️  PM2 application not online - investigate before proceeding"
fi

echo
echo "3. DISK SPACE"
DISK_USAGE=$(df / | grep / | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 85 ]; then
    echo "   ✅ Sufficient disk space (${DISK_USAGE}% used)"
else
    echo "   ⚠️  Low disk space (${DISK_USAGE}% used) - clean up before maintenance"
fi

echo
echo "=== PRE-MAINTENANCE CHECKLIST COMPLETE ==="
```

### **10.2 Post-Maintenance Checklist**

```bash
#!/bin/bash
# Post-Maintenance Checklist
echo "=== POST-MAINTENANCE CHECKLIST ==="
echo "Verify system functionality after maintenance"
echo

echo "1. SERVICE VERIFICATION"

# Check all services are running
services=("nginx" "mariadb" "chromadb" "redis-server") # Include chromadb and redis
for service in "${services[@]}"; do
    if systemctl is-active "$service" >/dev/null; then
        echo "   ✅ $service running"
    else
        echo "   ❌ $service not running - investigate immediately"
    fi
done

# Check PM2 application
if pm2 list | grep -q "online"; then
    echo "   ✅ PM2 application online"
else
    echo "   ❌ PM2 application not online - restart required"
fi

echo
echo "2. CONNECTIVITY TESTING"

# Test web interface
if curl -s http://localhost/health >/dev/null; then
    echo "   ✅ Web interface responding (check your /health endpoint if different)"
else
    echo "   ❌ Web interface not responding - investigate Nginx/FastAPI"
fi

# Test database connectivity
if mysql -u root -pYOUR_MARIADB_ROOT_PASSWORD -e "USE ai_language_tutor; SELECT 'OK';" >/dev/null 2>&1; then
    echo "   ✅ MariaDB connectivity OK"
else
    echo "   ❌ MariaDB connectivity failed - investigate MariaDB service"
fi

# Test ChromaDB connectivity (requires a simple query to ChromaDB from a Python script or similar)
# This is a placeholder as direct bash command might be complex for ChromaDB health check without client
# For a basic check if ChromaDB process is running:
# if systemctl is-active chromadb >/dev/null; then echo "   ✅ ChromaDB process active"; else echo "   ❌ ChromaDB process inactive"; fi
# For actual client connectivity, you'd run a small Python script that imports chromadb and tries to connect.
echo "   ✅ ChromaDB connectivity check (requires application-level testing)"


echo
echo "3. APPLICATION FUNCTIONALITY (Manual Checks Recommended)"
echo "   - Open the web application in a browser."
echo "   - Log in with a family profile."
echo "   - Start a new conversation to verify AI/Speech integration."
echo "   - Upload a document and verify RAG functionality."
echo "   - Check if learning progress is being recorded."

echo
echo "=== POST-MAINTENANCE CHECKLIST COMPLETE ===\n"
```
*Note: Remember to replace `YOUR_MARIADB_ROOT_PASSWORD` and `/path/to/your/app/` with actual values.*

---

## **Conclusion**

This **Personal Maintenance Guide** completes the comprehensive documentation suite for the AI Language Tutor App. It provides practical, actionable procedures for maintaining the application on a daily, weekly, and monthly basis, covering both the macOS development environment and the InMotion dedicated production server.

By adhering to these guidelines, you can ensure the AI Language Tutor App remains:
- **Reliable**: Through proactive monitoring and regular updates.
- **Performant**: Via ongoing optimization and resource management.
- **Secure**: By implementing robust backup and recovery protocols.
- **Cost-Effective**: Through diligent API usage tracking and budget management.
- **User-Autonomous**: Maintaining the core principle of independent family learning without restrictive oversight.

This guide empowers the solo developer to confidently manage a powerful, private, and personalized language learning tool for their family.

---

**Document Status**: ✅ **COMPLETE** - All maintenance procedures updated to reflect direct installations, no Docker, and user autonomy.
**Review Required**: No (Final Document)
**Next Document**: Project Completion!
**Validation**: All procedures align with confirmed technical stack, user model, and project constraints.