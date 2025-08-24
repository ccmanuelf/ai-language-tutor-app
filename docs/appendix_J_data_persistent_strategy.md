# Appendix J: Data Persistence Strategy - Session Management & Storage Architecture
## AI Language Tutor App - Comprehensive Data Management Implementation (Finalized)

---

### **Document Information**
- **Appendix**: J
- **Document**: Data Persistence Strategy - Session Management & Storage Architecture
- **Version**: 2.0 (Finalized)
- **Date**: June 11, 2025
- **Technology Stack**: FastAPI + FastHTML + SQLAlchemy + MariaDB + ChromaDB + DuckDB/SQLite
- **Purpose**: Define comprehensive data storage, session management, and privacy-conscious persistence strategy for the AI Language Tutor App.
- **Status**: Finalized Design

---

## **1. EXECUTIVE SUMMARY**

This appendix establishes the complete data persistence architecture for the AI Language Tutor family educational tool. The strategy balances functional requirements (session continuity, progress tracking) with **strict privacy considerations (minimal conversation storage)** while supporting both online and offline operational modes. It fully aligns with the **user-autonomous model**, eliminating any administrative oversight or parental controls over user content and language choices.

### **1.1 Core Data Persistence Principles**

✅ **Privacy-First**: **NO persistent storage of sensitive full conversation content**. Only high-level metadata and temporary session context are retained.
✅ **User Autonomy**: All family members have equal, independent control over their learning paths, content, and language selections. No data structures for parental controls or administrative user management are implemented.
✅ **Session Continuity**: Smart context preservation for "continue conversation" functionality through temporary, local storage.
✅ **Progress Tracking**: Comprehensive learning analytics based on metadata, not detailed conversation logs.
✅ **Hybrid Support**: Consistent data experience across online/offline modes, leveraging local and server-side databases.
✅ **Family Focus**: Personal data isolation and secure usage for family members.

### **1.2 Storage Architecture Overview**

The data persistence layers are designed to optimize for privacy, performance, and the hybrid online/offline operational model.

```mermaid
graph TD
    A[Application Frontend (PWA)] -- Reads/Writes Local --> B[DuckDB/SQLite (Local DB)]
    B -- Syncs/Requests --> C[FastAPI Backend]
    C -- Writes/Reads Persistent --> D[MariaDB (Persistent Metadata)]
    C -- Writes/Reads Ephemeral --> E[ChromaDB (Temporary Vector Store)]
    C -- Handles Temp Files --> F[Temporary Server Storage (Raw Uploads)]

    F -- Deletes Immediately After Processing --> G[🗑️]
    E -- Cleared on Logout/Session End --> H[🗑️]
```

**Key Data Persistence Layers:**

* **MariaDB**: The primary server-side relational database for **persistent, structured metadata**.
* **ChromaDB**: A dedicated vector database for **temporary vector embeddings** of user-uploaded content, enabling RAG.
* **DuckDB/SQLite**: Lightweight, embedded databases for **client-side local storage** (offline caching, temporary session context, user preferences).
* **Temporary Server Storage**: Used for raw user-uploaded files during processing, with **immediate deletion after embedding generation or user logout**.

---

## **2. DETAILED DATA PERSISTENCE LAYERS**

### **2.1 Persistent Data (MariaDB)**

MariaDB stores all non-sensitive, necessary data that needs to persist across sessions and user logins.

* **`users` Table**: Stores basic user profiles including `user_id`, `username`, `email`, `hashed_password`, `primary_language`, and `target_languages`. **Crucially, there are no fields for roles, admin status, parental controls, or approval status, upholding user autonomy.**
* **`conversations` Table**: Stores **only high-level metadata about conversation sessions**, such as `session_id`, `user_id`, `scenario_id`, `target_language`, `start_time`, `end_time`, `total_ai_tokens_used`, and `estimated_cost`. **It explicitly does NOT store full conversation transcripts or individual messages.**
* **`feedback` Table**: Stores specific feedback instances (e.g., pronunciation scores, grammar suggestions) linked to a `session_id` and `user_id`.
* **`uploaded_content_metadata` Table**: Stores metadata about user-uploaded files or links (`content_id`, `user_id`, `filename`, `file_type`, `upload_time`, `processed_status`). **The actual content of the files is NOT stored in MariaDB; only its metadata is kept.**
* **`progress` Table**: Tracks aggregate learning progress, including `streak_count`, `last_activity_date`, `lessons_completed`, `topics_covered`, and `languages_practiced`.
* **`learning_scenarios` Table**: Stores predefined learning scenarios and their associated metadata.
* **`api_usage_log` Table**: Records API calls to external services (`service_name`, `tokens_used`, `cost`) for budget management.

### **2.2 Ephemeral Data (ChromaDB)**

ChromaDB serves as a dedicated vector store for **temporary, session-bound embeddings** generated from user-uploaded content.

* **Purpose**: To enable Retrieval Augmented Generation (RAG) by quickly retrieving relevant content snippets based on semantic similarity.
* **Data Stored**: Only vector embeddings and minimal metadata (e.g., `content_id` linked to MariaDB, `user_id`, `chunk_id`, small text snippets for context).
* **Privacy & Lifecycle**: **The actual raw content of uploaded files is NEVER stored persistently in ChromaDB or on the server.** The embeddings and their associated metadata in ChromaDB are **designed to be ephemeral**. They are ingested only when a user uploads content for a session and are **automatically cleared upon user logout, session expiry, or app close** to ensure privacy. This prevents long-term retention of potentially sensitive user-provided data.

### **2.3 Local/Offline Data (DuckDB/SQLite)**

DuckDB/SQLite provides a robust local data store on the user's device, enabling offline functionality and temporary data persistence.

* **`user_preferences`**: Stores user-specific settings, UI preferences, and current target language selections.
* **`offline_progress_cache`**: Temporarily stores `streak_count` and `last_activity_date` to ensure "Don't break the chain" continuity even when offline. This cache synchronizes with the `progress` table in MariaDB when the device comes online.
* **`current_session_context`**: Stores the **immediate conversational turns for the active session only**. This allows for conversational continuity within a single session. **This data is strictly ephemeral and is cleared from the local database upon app close or user logout.** This design avoids persistent storage of detailed conversation logs while enabling seamless session experience.

---

## **3. SESSION MANAGEMENT & CONTEXT PRESERVATION**

The system employs a sophisticated session management strategy that prioritizes privacy while maintaining conversational flow.

* **Authentication**: Standard session management (e.g., JWT-based or secure cookies) ensures user authentication without storing sensitive session details server-side long-term.
* **Short-Term Context**: For an active conversation, the last few turns and relevant RAG snippets are held in the client's local `current_session_context` (DuckDB/SQLite) and in the backend's ephemeral memory. This allows the AI to maintain context for follow-up questions and conversational flow.
* **Long-Term Context (Metadata)**: Persistent `conversations` metadata (in MariaDB) provides high-level summaries. This allows the application to display a list of past "sessions" (e.g., "Practice: French - Travel Scenario - 15 min") without revealing the actual dialogue content.
* **"Continue Conversation" Functionality**: When a user selects a past session from their history (based on metadata), the backend dynamically reconstructs a limited context for the AI by retrieving relevant `uploaded_content_metadata` and potentially using summaries from past `feedback` entries. No full past dialogue is reloaded; the focus is on the scenario and topic.

---

## **4. FILE HANDLING & CONTENT PROCESSING LIFECYCLE**

User-uploaded content (documents, images, links) is handled with a strong emphasis on privacy and temporary storage.

1.  **Upload**: User uploads a file/link via the frontend. The raw file is sent to the FastAPI backend.
2.  **Temporary Storage**: The raw file is temporarily stored on the FastAPI server in a designated, secure temporary directory (e.g., `/tmp/uploads`).
3.  **Processing**:
    * The backend processes the raw file: extracts text, converts images to text (OCR), or fetches content from links.
    * This extracted content is then chunked and converted into vector embeddings using a chosen embedding model.
    * Metadata about the uploaded content (filename, type, etc.) is stored in the `uploaded_content_metadata` table in MariaDB.
4.  **ChromaDB Ingestion**: The generated vector embeddings are ingested into ChromaDB, linked by the `content_id` from MariaDB.
5.  **Immediate Deletion of Raw File**: **Crucially, immediately after processing and ingestion into ChromaDB, the original raw file is irrevocably deleted from the temporary server storage.** This ensures no long-term retention of user-provided raw content.
6.  **Ephemeral Embeddings**: The embeddings in ChromaDB are themselves ephemeral, designed to be cleared upon user logout or session expiry to maintain privacy.

---

## **5. PRIVACY & SECURITY MEASURES**

The data persistence strategy is underpinned by robust privacy and security measures:

* **Data Minimization**: Adherence to the principle of collecting and storing only the absolute minimum data required for the application's functionality. This specifically means **no persistent storage of detailed conversation content**.
* **No Parental Controls/Oversight**: The absence of any data structures or logic for administrative or parental oversight of user activities or content choices reinforces user autonomy as per the latest architectural corrections.
* **Ephemeral Data Handling**: Temporary storage mechanisms for sensitive data (raw uploads, conversation turns, RAG embeddings) ensure that data is deleted as soon as its immediate utility ends.
* **Encryption**:
    * **Data in Transit**: All data exchanged between client, server, and external APIs is encrypted using TLS/SSL (HTTPS/WSS).
    * **Data at Rest**: MariaDB will be configured for encryption at rest on the InMotion dedicated server. Passwords are stored as hashes.
* **Access Control**: Database access is strictly limited to the FastAPI backend.
* **Audit Trails**: The `api_usage_log` table provides a transparent record of external service consumption, contributing to both budget management and basic auditing.

---

## **6. PERFORMANCE & ANALYTICS**

* **Optimized Queries**: SQLAlchemy ORM with MariaDB for efficient data retrieval.
* **Strategic Indexing**: Ensures fast access to frequently queried data points in MariaDB.
* **Ephemeral Vector Search**: ChromaDB is optimized for fast similarity search on embeddings, crucial for real-time RAG.
* **Analytics based on Metadata**: Learning analytics (e.g., streak progression, topics covered, API costs) are derived from the aggregate metadata stored in MariaDB, not from detailed conversation transcripts. This maintains privacy while providing valuable insights into learning patterns.

---

## **7. SEAMLESS TRANSITIONS & IMPLEMENTATION READINESS**

* **Automatic Mode Detection**: The application intelligently detects online/offline status and routes data persistence operations accordingly.
* **Offline Data Sync**: DuckDB/SQLite handles offline data capture, with automatic synchronization to MariaDB once network connectivity is restored (e.g., updating progress streaks).
* **Consistent User Experience**: Users experience continuous learning, whether online or offline, with data handled appropriately in the background.
* **Implementation Readiness**: The data persistence architecture is fully specified and ready for Python implementation with FastAPI + SQLAlchemy, leveraging MariaDB, ChromaDB, and DuckDB/SQLite.

---

## **8. Next Steps**

With Appendix J completed, the project is ready to proceed with the next prioritized documentation. Given the user autonomy model, the previous "Administrative User Management" document is no longer relevant in its original form.

The next critical steps in documentation are:

1.  **Appendix C**: File Upload & Content Integration (FastAPI implementation for processing user-uploaded content, focusing on the temporary storage and deletion lifecycle).
2.  **Appendix D**: Gamification & Learning Tracking (detailed implementation of streak tracking and progress analytics based on the `progress` table and conversation metadata).
3.  **Appendix E**: AI Tutor Personalization Engine (voice and personality systems, integrating with the chosen AI models).

The data persistence foundation established in this appendix will support all subsequent features while maintaining the privacy-first, family-focused approach that defines this personal educational tool.

---

**Document Status**: ✅ **COMPLETE**
**Review Required**: Yes
**Next Appendix**: C - File Upload & Content Integration