# Database Design & Data Architecture
## AI Language Tutor App - Comprehensive Data Management Specification (Finalized)

---

### **Document Information**
- **Project**: Personal AI Language Tutor App (Family Educational Tool)
- **Document**: Database Design & Data Architecture
- **Version**: 2.0 (Finalized)
- **Date**: June 11, 2025
- **Author**: Development Team
- **Status**: Finalized Design

---

## **1. Database Strategy & Design Philosophy**

### **1.1 Design Principles**
The database design prioritizes data integrity, performance, security, and especially **privacy**, given the application's focus as a personal family educational tool.

* **Data Integrity First**: ACID compliance, referential integrity, consistent data types.
* **Performance Optimization**: Strategic indexing, optimized queries for real-time interactions.
* **Privacy & Security**: **Minimal data retention (no persistent full conversation logs)**, encrypted storage, secure access.
* **Scalability Considerations**: Designed for a small family user base (max 3 users), efficient migration pathways.
* **Maintainability**: Clear documentation, standardized naming.

### **1.2 Database Architecture Strategy**

The application employs a **hybrid data persistence strategy**, combining local and server-side databases.

* **Phase 1: Local Development & Offline Capability (DuckDB/SQLite)**
    ```mermaid
    graph TD
        A[Application Frontend] --> B[DuckDB/SQLite DB (Local)]
        B -- Synchronizes --> C[FastAPI Backend]
    ```
    * **DuckDB/SQLite**: Lightweight, embedded databases for client-side local storage. Used for:
        * Offline caching of essential learning data.
        * Temporary session context (discarded on logout).
        * "Don't break the chain" streak tracking for offline continuity.
        * Synchronizes with MariaDB when online.

* **Phase 2: Production Deployment (MariaDB + ChromaDB)**
    ```mermaid
    graph TD
        A[FastAPI Backend] --> B[MariaDB (Persistent Data)]
        A --> C[ChromaDB (Vector Store)]
        B -- Stores Metadata --> D[External Systems (LLMs, STT/TTS)]
        C -- Stores Embeddings --> D
    ```
    * **MariaDB**: The primary relational database on the InMotion dedicated server for persistent, structured metadata.
    * **ChromaDB**: A dedicated vector database for storing embeddings generated from user-uploaded content, enabling Retrieval Augmented Generation (RAG).

---

## **2. Data Models & Schema Design**

### **2.1 Logical Entity Relationship Diagram**

```mermaid
erDiagram
    USERS {
        UUID user_id PK
        VARCHAR username
        VARCHAR email
        VARCHAR hashed_password
        VARCHAR primary_language
        JSON target_languages
        TIMESTAMP created_at
        TIMESTAMP last_login
    }

    CONVERSATIONS {
        UUID session_id PK
        UUID user_id FK
        UUID scenario_id FK
        VARCHAR target_language
        TIMESTAMP start_time
        TIMESTAMP end_time
        INT total_ai_tokens_used
        DECIMAL(10,4) estimated_cost
    }

    FEEDBACK {
        UUID feedback_id PK
        UUID session_id FK
        UUID user_id FK
        TEXT text_analyzed
        VARCHAR feedback_type
        DECIMAL(3,2) score
        JSON suggestions
        TIMESTAMP created_at
    }

    UPLOADED_CONTENT_METADATA {
        UUID content_id PK
        UUID user_id FK
        VARCHAR filename
        VARCHAR file_type
        VARCHAR original_source_url
        TIMESTAMP upload_time
        VARCHAR processed_status
        TEXT brief_description
    }

    PROGRESS {
        UUID progress_id PK
        UUID user_id FK
        INT streak_count
        DATE last_activity_date
        INT lessons_completed
        JSON topics_covered
        JSON languages_practiced
        TIMESTAMP last_updated
    }

    LEARNING_SCENARIOS {
        UUID scenario_id PK
        VARCHAR name
        TEXT description
        VARCHAR language
        JSON difficulty_levels
    }

    API_USAGE_LOG {
        UUID log_id PK
        UUID user_id FK
        VARCHAR service_name
        INT tokens_used
        INT duration_ms
        DECIMAL(10,6) actual_cost
        TIMESTAMP timestamp
    }

    USERS ||--o{ CONVERSATIONS : "initiates"
    CONVERSATIONS ||--o{ FEEDBACK : "generates"
    USERS ||--o{ UPLOADED_CONTENT_METADATA : "uploads"
    USERS ||--o{ PROGRESS : "tracks"
    LEARNING_SCENARIOS ||--o{ CONVERSATIONS : "uses"
    USERS ||--o{ API_USAGE_LOG : "triggers"
```

### **2.2 Physical Schema (MariaDB)**

#### **`users` Table**
* **Purpose**: Stores individual user profiles.
* **Key Design Point**: Reflects user autonomy. **No roles, admin flags, or parental control fields.** All family members have equal access.
```sql
CREATE TABLE users (
    user_id CHAR(36) PRIMARY KEY, -- UUID
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    primary_language VARCHAR(50) NOT NULL,
    target_languages JSON DEFAULT '[]', -- JSON array of strings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email)
);
```

#### **`conversations` Table**
* **Purpose**: Stores high-level metadata about each conversation session.
* **Key Design Point**: **Crucially, does NOT store full conversation history/messages.** This ensures privacy and compliance with project brief. Only aggregate data and session context for continuity.
```sql
CREATE TABLE conversations (
    session_id CHAR(36) PRIMARY KEY, -- UUID
    user_id CHAR(36) NOT NULL,
    scenario_id CHAR(36), -- NULLable if free-form conversation
    target_language VARCHAR(50) NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_ai_tokens_used INT DEFAULT 0,
    estimated_cost DECIMAL(10,4) DEFAULT 0.0000, -- Based on token usage and model rates
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id) REFERENCES learning_scenarios(scenario_id) ON DELETE SET NULL,
    INDEX idx_conv_user_lang (user_id, target_language)
);
```

#### **`feedback` Table**
* **Purpose**: Stores specific pronunciation and grammar feedback instances provided to the user.
```sql
CREATE TABLE feedback (
    feedback_id CHAR(36) PRIMARY KEY, -- UUID
    session_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    text_analyzed TEXT NOT NULL,
    feedback_type VARCHAR(50) NOT NULL, -- e.g., 'pronunciation', 'grammar'
    score DECIMAL(3,2), -- e.g., 0.85 for pronunciation
    suggestions JSON, -- JSON array of strings or object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES conversations(session_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_feedback_session (session_id)
);
```

#### **`uploaded_content_metadata` Table**
* **Purpose**: Stores metadata about user-uploaded documents, images, or links used for RAG.
* **Key Design Point**: **Does NOT store the actual file content.** The content is processed into embeddings for ChromaDB, and the original raw file is only stored temporarily (e.g., in a temporary server directory) and deleted after processing or user logout for privacy.
```sql
CREATE TABLE uploaded_content_metadata (
    content_id CHAR(36) PRIMARY KEY, -- UUID
    user_id CHAR(36) NOT NULL,
    filename VARCHAR(255), -- For files
    file_type VARCHAR(100), -- MIME type
    original_source_url TEXT, -- For links
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_status VARCHAR(50) NOT NULL, -- e.g., 'pending', 'processing', 'completed', 'failed'
    brief_description TEXT, -- AI-generated summary or user-provided
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_content_user (user_id)
);
```

#### **`progress` Table**
* **Purpose**: Tracks high-level learning progress and gamification elements (e.g., streaks).
```sql
CREATE TABLE progress (
    progress_id CHAR(36) PRIMARY KEY, -- UUID
    user_id CHAR(36) UNIQUE NOT NULL, -- One-to-one with users
    streak_count INT DEFAULT 0,
    last_activity_date DATE,
    lessons_completed INT DEFAULT 0,
    topics_covered JSON DEFAULT '[]', -- JSON array of strings
    languages_practiced JSON DEFAULT '[]', -- JSON array of strings
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

#### **`learning_scenarios` Table**
* **Purpose**: Stores predefined learning scenarios and topics.
```sql
CREATE TABLE learning_scenarios (
    scenario_id CHAR(36) PRIMARY KEY, -- UUID
    name VARCHAR(255) NOT NULL,
    description TEXT,
    language VARCHAR(50) NOT NULL,
    difficulty_levels JSON DEFAULT '[]', -- JSON array of strings, e.g., ['beginner', 'intermediate']
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_scenario_language (language)
);
```

#### **`api_usage_log` Table**
* **Purpose**: Records API calls to external services for budget tracking and monitoring.
```sql
CREATE TABLE api_usage_log (
    log_id CHAR(36) PRIMARY KEY, -- UUID
    user_id CHAR(36), -- NULLable for system-level calls not tied to a specific user
    service_name VARCHAR(100) NOT NULL, -- e.g., 'Claude', 'Mistral', 'Watson STT', 'Watson TTS', 'Ollama'
    tokens_used INT DEFAULT 0, -- For LLMs
    duration_ms INT DEFAULT 0, -- For speech services or processing time
    actual_cost DECIMAL(10,6) DEFAULT 0.000000, -- Actual cost incurred for the call
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_usage_timestamp (timestamp),
    INDEX idx_usage_user_service (user_id, service_name)
);
```

### **2.3 ChromaDB (Vector Database)**
* **Purpose**: Stores vector embeddings generated from user-uploaded content for Retrieval Augmented Generation (RAG).
* **Structure**: ChromaDB manages collections of embeddings. Each embedding will be associated with metadata linking back to the `content_id` in the `uploaded_content_metadata` table in MariaDB.
* **Key Design Point**: **No direct storage of raw text/image data in ChromaDB, only its vector representation.** This vector store is ephemeral for privacy; data is only there as long as the user is logged in or for a very limited session time, then it's cleared.
* **Example (Conceptual)**:
    ```json
    // ChromaDB Document Entry
    {
      "id": "embedding_uuid_123",
      "embedding": [0.1, 0.2, ..., 0.9], // The vector embedding
      "metadata": {
        "content_id": "uuid_from_uploaded_content_metadata",
        "user_id": "user_id_from_maria_db",
        "chunk_id": "chunk_001",
        "text_snippet": "Actual text snippet from the document chunk (short)" // For context on retrieval
      }
    }
    ```

### **2.4 DuckDB/SQLite (Local Database)**
* **Purpose**: Client-side storage for offline functionality and temporary data.
* **Structure**: A subset of the server-side schema, optimized for local persistence.
* **Key Tables (Conceptual)**:
    * `local_user_settings`: User preferences, current target language.
    * `offline_progress_cache`: Cached `streak_count`, `last_activity_date` to be synchronized with `progress` table on server.
    * `session_context_cache`: Temporary storage for conversational turns within an active session. **Cleared on app close/logout.**

---

## **3. Data Storage & File Handling**

* **MariaDB**: Used for structured, persistent metadata like user profiles, progress summaries, and API usage logs.
* **ChromaDB**: Used for dynamic, session-based storage of content embeddings for RAG.
* **DuckDB/SQLite**: Used for local, offline data caching and temporary session context.
* **Temporary File Storage**: When a user uploads a document or image, the raw file is temporarily stored on the server (e.g., in a designated `/tmp` directory). After processing the content into embeddings for ChromaDB, and certainly upon user logout, **the original raw file is immediately and irrevocably deleted from the server.** This aligns with the privacy principles of not retaining user-uploaded content long-term.

---

## **4. Security & Privacy Considerations**

* **Data Minimization**: Adheres strictly to storing only necessary metadata and no full conversation histories.
* **No Parental Controls/Oversight**: The database schema explicitly avoids fields or structures that would support any form of administrative oversight, parental controls, or age-based content filtering, as per the `document_11_5_user_autonomy_corrections.md`. All users are equal and autonomous.
* **Encryption**:
    * **Data in Transit**: All communication between client and server, and between backend and external APIs, uses TLS/SSL (HTTPS/WSS).
    * **Data at Rest**: MariaDB will be configured with encryption for data at rest. Hashed passwords.
* **Access Control**: Database access is restricted to the FastAPI backend service only. No direct client access.
* **Auditing**: The `api_usage_log` table provides an audit trail for API costs, contributing to budget compliance.

---

## **5. Performance & Optimization**

* **Indexing**: Strategic indexing on frequently queried columns (e.g., `user_id`, `email`, `timestamp`, `session_id`).
* **Query Optimization**: Optimized SQL queries, leveraging ORM (SQLAlchemy) effectively in FastAPI.
* **Caching**: In-memory caching for frequently accessed data (e.g., learning scenarios).
* **Efficient Embeddings**: ChromaDB is optimized for fast similarity searches on vector embeddings.

---

## **6. Scalability & Migration**

* **Vertical Scaling**: MariaDB server resources (CPU, RAM) can be scaled up on the InMotion dedicated server.
* **Horizontal Scaling (Future Consideration)**: The relational schema is designed with partitioning potential, though not strictly required for a small family user base.
* **Local to Server Sync**: DuckDB/SQLite data is synchronized to MariaDB as appropriate (e.g., progress updates).
* **Database Migrations**: Alembic (or similar) for managing schema changes in MariaDB.

---

## **7. Backup & Recovery Procedures**

* **Automated Backups**: Regular automated backups of the MariaDB database to a secure off-site location on the InMotion server.
* **Recovery Plan**: Documented procedures for restoring the database from backups in case of data loss or corruption.
* **Data Retention Policy**: Backups will align with the privacy-first data retention policy (e.g., no retention of temporary content data).

---

## **8. Implementation Plan**

This database design guides the implementation phases for the AI Language Tutor App.

### **Phase 1: Database Setup & Core Models**
* MariaDB installation and initial schema setup.
* DuckDB/SQLite integration for local development.
* Implement `users`, `progress`, and `learning_scenarios` tables.
* Basic authentication and user profile management via FastAPI.

### **Phase 2: Conversation & Content Integration**
* Implement `conversations` (metadata only) and `feedback` tables.
* Develop `uploaded_content_metadata` table.
* Integrate ChromaDB for vector embeddings and RAG.
* Implement temporary file storage and deletion logic.

### **Phase 3: Monitoring & Optimization**
* Implement `api_usage_log` for cost tracking.
* Performance tuning and indexing for all tables.
* Set up database monitoring and alerting.
* Implement backup and recovery procedures.

---

### **Document Completion Status**

**Database Design & Data Architecture - Comprehensive Data Management Specification** - ✅ **COMPLETE (Finalized)**

**Next Step**: Proceed with **Appendix J: Data Persistence Strategy** (`appendix-j-data-persistence-strategy.md`) which further elaborates on session management and storage architecture.