# MariaDB Setup Guide - Collaborative Steps

> **📊 CURRENT STATUS (August 25, 2025)**: Database setup is **COMPLETE** and **OPERATIONAL**
> 
> **✅ Active Configuration**: SQLite (development) + ChromaDB (vectors) + DuckDB (analytics)  
> **🎯 Production Path**: SQLite → MariaDB migration ready when needed  
> **🔧 Health Status**: All databases operational (SQLite: 8.9ms, ChromaDB: 52.9ms, DuckDB: 55.7ms)

## 🏗️ Current Architecture (Operational)

### **Multi-Database Setup (Implemented)**
```
✅ PRIMARY DATABASE: SQLite
├── File: ./data/ai_language_tutor.db
├── Usage: Main application data (users, conversations, vocabulary)
├── Status: Operational with 6 languages, 3 users, 3 conversations
└── Migration Path: → MariaDB for production scaling

✅ VECTOR DATABASE: ChromaDB  
├── Path: ./data/chromadb/
├── Usage: Embeddings for semantic search and RAG
├── Status: 5 collections ready, 2 sample document embeddings
└── Features: Multilingual embeddings, conversation history vectors

✅ ANALYTICS DATABASE: DuckDB
├── File: ./data/local/app.duckdb  
├── Usage: Learning analytics and performance metrics
├── Status: Operational, ready for analytics queries
└── Features: Fast columnar analytics, learning progress tracking
```

## 🔍 Verification Commands

### **Health Check (All Systems)**
```bash
# Complete database health verification
python -c "
from app.database.config import db_manager
health = db_manager.test_all_connections()
for db_name, status in health.items():
    emoji = '✅' if status['status'] == 'healthy' else '❌'
    print(f'{emoji} {db_name.upper()}: {status["status"]} ({status.get("response_time_ms", 0):.1f}ms)')

overall = db_manager.get_health_summary()
print(f'\n🎯 OVERALL STATUS: {overall["overall"].upper()}')
"
```

### **Sample Data Verification**
```bash
# Check populated data
python -c "
from app.database.config import db_manager
from sqlalchemy import text

session = db_manager.get_sqlite_session()
print('📊 Database Contents:')
for table in ['languages', 'users', 'conversations', 'vocabulary_items']:
    count = session.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
    print(f'   {table}: {count} records')
session.close()

# Check ChromaDB collections
chroma = db_manager.chromadb_client
collections = chroma.list_collections()
embeddings_total = sum(c.count() for c in collections)
print(f'   ChromaDB: {embeddings_total} embeddings across {len(collections)} collections')
"
```

## 📜 Original MariaDB Setup (Reference)

> **📝 NOTE**: The steps below were the original plan for MariaDB setup. We evolved to SQLite for development efficiency, but these steps remain valid for production deployment.

### **MariaDB Production Migration (Future)**

## Step 1: Check MariaDB Status
Run this command to confirm MariaDB is running:
```bash
brew services list | grep mariadb
```

## Step 2: Connect to MariaDB as Root
Try connecting as root (fresh installation usually has no password):
```bash
sudo mysql -u root
```

If that doesn't work, try:
```bash
mysql -u root
```

## Step 3: Execute Database Setup SQL
Once connected, run these SQL commands one by one:

```sql
-- Create the database
CREATE DATABASE IF NOT EXISTS ai_language_tutor
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Create the application user
CREATE USER IF NOT EXISTS 'ai_tutor_user'@'localhost' IDENTIFIED BY 'ai_tutor_pass_2024';

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON ai_language_tutor.* TO 'ai_tutor_user'@'localhost';

-- Flush privileges
FLUSH PRIVILEGES;

-- Show databases to confirm creation
SHOW DATABASES;

-- Show users to confirm user creation
SELECT User, Host FROM mysql.user WHERE User = 'ai_tutor_user';
```

## Step 4: Test Application User Connection
Exit MySQL and test the new user:
```bash
mysql -u ai_tutor_user -p ai_language_tutor
```
Password: `ai_tutor_pass_2024`

## Step 5: Update Environment Configuration
If successful, we'll update the .env file with the correct database URL.

## Alternative Simple Approach
If the above has issues, we can use a simpler SQLite approach for development:
```bash
# Just update .env to use SQLite instead
DATABASE_URL=sqlite:///./data/ai_language_tutor.db
```

Please run **Step 1** first and let me know the output!