# Software Architecture Design
## AI Language Tutor App - Technical Architecture & System Design (Finalized)

---

### **Document Information**
- **Project**: Personal AI Language Tutor App (Family Educational Tool)
- **Document**: Software Architecture Design
- **Version**: 2.0 (Finalized)
- **Date**: June 11, 2025
- **Author**: Development Team
- **Status**: Finalized Design

---

## **1. Architecture Overview**

### **1.1 Design Principles**
The architecture adheres to robust design principles, prioritizing performance, cost efficiency, and maintainability for a personalized family educational tool.

* **DRY (Don't Repeat Yourself)**: Centralized configuration, reusable components, single source of truth for data models.
* **KISS (Keep It Simple, Stupid)**: Minimal external dependencies, clear separation of concerns, straightforward data flow.
* **Performance First**: Optimized for real-time speech processing and quick AI responses.
* **Cost Conscious**: Efficient API usage patterns to stay within the $30/month budget.
* **Progressive Enhancement**: Iterative development, starting with core features and adding complexity gradually.
* **Offline Resilience**: Graceful degradation and seamless operation using local resources when online services are unavailable.
* **User Autonomy**: The system design supports full user autonomy and equal access for all family members, with no internal role-based restrictions or parental controls.

### **1.2 Architecture Style**
The AI Language Tutor App employs a **Python-first, Hybrid Multi-Service Platform** architecture.

* **Frontend**: **FastHTML** (Python-based server-side rendering for robust PWA foundation) combined with **MonsterUI** (CSS/JS components for interactive elements).
* **Backend**: **FastAPI** (Python-based RESTful API for core logic and WebSockets for real-time communication).
* **Data Layer**: **Hybrid approach**:
    * **MariaDB** (server-side, for persistent metadata and user profiles).
    * **ChromaDB** (vector store for Retrieval Augmented Generation (RAG) based on uploaded content).
    * **DuckDB/SQLite** (local storage for offline data, progress tracking, and temporary session data).
* **AI/LLM Integration**: **Multi-AI Routing** intelligently leveraging cloud-based LLMs (Anthropic Claude, Mistral AI, Alibaba Qwen) and local LLMs (Ollama / LM Studio) for offline capability and budget control.
* **Speech Services**: **IBM Watson Speech-to-Text (STT)** and **Text-to-Speech (TTS)** for primary real-time speech processing, with browser-based Speech APIs as fallback.
* **Hosting**: **InMotion dedicated server** for backend services.

---

## **2. System Architecture**

### **2.1 High-Level Architecture Diagram**
```mermaid
graph TD
    subgraph "Client (PWA on User Device)"
        UI[User Interface<br/>FastHTML + MonsterUI]
        SW[Service Worker<br/>Offline Capabilities]
        LOCAL_DB[(DuckDB/SQLite<br/>Local Data)]
        UI -- HTTP/WS --> Backend_API
        SW -- Data Sync --> Backend_API
        LOCAL_DB -- Local Storage --> UI
    end

    subgraph "Backend (InMotion Dedicated Server)"
        Backend_API[FastAPI Server<br/>REST + WebSockets]
        DB_MariaDB[(MariaDB<br/>Persistent Data)]
        DB_ChromaDB[(ChromaDB<br/>Vector Store)]
        LLM_Router[LLM Router<br/>(Mini Router Layer)]
        Speech_API_Proxy[Speech API Proxy]

        Backend_API -- Data Query --> DB_MariaDB
        Backend_API -- Embeddings & RAG --> DB_ChromaDB
        Backend_API -- LLM Calls --> LLM_Router
        Backend_API -- Speech Calls --> Speech_API_Proxy
    end

    subgraph "External Services (Cloud)"
        IBM_Watson[IBM Watson<br/>STT/TTS]
        Claude[Anthropic Claude]
        Mistral[Mistral AI]
        Qwen[Alibaba Qwen]

        Speech_API_Proxy -- API Calls --> IBM_Watson
        LLM_Router -- API Calls (Online) --> Claude
        LLM_Router -- API Calls (Online) --> Mistral
        LLM_Router -- API Calls (Online) --> Qwen
    end

    subgraph "Local LLMs (Offline/Fallback)"
        Ollama_LM_Studio[Ollama / LM Studio<br/>(on User Device)]
        LLM_Router -- API Calls (Offline/Fallback) --> Ollama_LM_Studio
    end
```

### **2.2 Component Breakdown**

#### **2.2.1 Frontend Layer**
* **FastHTML**: Responsible for server-side rendering of HTML pages, providing a robust, Python-native foundation for the PWA. This ensures initial page loads are fast and search-engine friendly.
* **MonsterUI**: A lightweight, modern CSS/JavaScript framework used for interactive UI components (e.g., buttons, modals, chat bubbles, feedback displays). It will integrate seamlessly with FastHTML's rendered content.
* **Service Worker**: Enables core PWA functionalities like offline access, caching of static assets, and background data synchronization. It manages the local DuckDB/SQLite instance for offline data persistence.

#### **2.2.2 Backend Layer (FastAPI)**
* **RESTful API Endpoints**: Handles user authentication, content upload processing, progress tracking updates, and core conversational requests.
* **WebSockets**: Provides real-time, bidirectional communication for continuous speech input, instant AI responses, and live pronunciation/grammar feedback.
* **Business Logic**: Orchestrates interactions between different modules, including data persistence, AI models, and speech services.
* **Security & Validation**: Implements input validation, authentication, and output sanitization, especially critical for LLM interactions.

#### **2.2.3 Data Layer**
* **MariaDB**: The primary relational database for persistent server-side data such as user profiles, learning progress summaries (not full conversation logs), and application configuration. Hosted on the InMotion dedicated server.
* **ChromaDB**: An in-memory or persistent vector database used for storing embeddings of uploaded content (documents, images, links). This enables efficient Retrieval Augmented Generation (RAG) for context-aware conversations.
* **DuckDB/SQLite**: Lightweight, embedded databases for local storage on the client-side. DuckDB is preferred for its analytical capabilities and performance, with SQLite as a fallback. Used for offline caching of learning data, temporary session context, and 'Don't break the chain' streak tracking.

#### **2.2.4 AI/LLM Integration**
* **LLM Router (Mini Router Layer)**: An intelligent routing module that directs AI requests to the most appropriate LLM based on various factors:
    * **Cost Efficiency**: Prioritizes cheaper models when budget allows.
    * **Performance**: Selects faster models for real-time interactions.
    * **Capability**: Routes to specialized models for specific languages or tasks (e.g., Qwen for Chinese, Mistral for quick grammar checks).
    * **Online/Offline Status**: Automatically falls back to local LLMs (Ollama/LM Studio) when offline or nearing budget limits.
* **Cloud LLMs**: Anthropic Claude (primary for complex dialogue), Mistral AI (for quick responses and grammar), Alibaba Qwen (for enhanced multilingual support, especially Chinese).
* **Local LLMs (Ollama / LM Studio)**: Running locally on the user's device, these provide a robust offline capability and act as a crucial budget protection mechanism.
* **Prompt Adapters**: Ensure consistent prompting across different LLMs despite their varying API interfaces and optimal prompt formats.

#### **2.2.5 Speech Services Integration**
* **IBM Watson STT/TTS**: The primary cloud-based solution for high-accuracy Speech-to-Text (WebSocket streaming for real-time transcription) and natural-sounding Text-to-Speech (MP3 audio generation).
* **Browser-based Speech APIs**: Fallback for STT/TTS in offline mode or if IBM Watson services are unavailable, ensuring basic speech functionality remains.

#### **2.2.6 Offline Module**
* **Connectivity Detection**: Monitors network status to seamlessly switch between online and offline modes.
* **Local Data Management**: Utilizes DuckDB/SQLite to store essential conversational context, user preferences, and 'Don't break the chain' progress locally.
* **Local LLM Interface**: Routes AI queries to Ollama/LM Studio running on the user's device for offline AI interaction.
* **Synchronization Logic**: Manages periodic synchronization of local progress data with the server-side MariaDB when online.

### **2.3 API Interactions**
* **Client-Server Communication**: Primarily via RESTful HTTP requests for data exchange and WebSockets for real-time conversational flow.
* **Backend-External API Communication**: Server-to-server API calls (HTTP/HTTPS) for LLM and speech service integrations.
* **Data Exchange Formats**: JSON for REST APIs, binary/text streams for WebSockets (e.g., for audio data).

---

## **3. Data Flow and Management**

### **3.1 High-Level Data Flow**
```mermaid
graph TD
    User[User] --> UI[User Interface (FastHTML/MonsterUI)]
    UI -- Speech Input --> SW[Service Worker]
    SW -- Audio Stream (WebSocket) --> Backend_API[FastAPI Backend]
    Backend_API -- STT Call --> IBM_Watson[IBM Watson STT]
    IBM_Watson -- Transcription --> Backend_API
    
    User -- Text Input / Content Upload --> UI
    UI -- HTTP Request --> Backend_API
    
    Backend_API -- RAG (Content Embeddings) --> ChromaDB[(ChromaDB)]
    Backend_API -- Contextual Prompting --> LLM_Router[LLM Router]
    
    LLM_Router -- Cloud Call (Claude/Mistral/Qwen) --> Cloud_LLMs[Cloud LLMs]
    LLM_Router -- Local Call (Ollama/LM Studio) --> Local_LLMs[Local LLMs]
    
    Cloud_LLMs --> LLM_Router
    Local_LLMs --> LLM_Router
    LLM_Router -- AI Response --> Backend_API
    
    Backend_API -- TTS Call --> IBM_Watson_TTS[IBM Watson TTS]
    IBM_Watson_TTS -- Audio Stream --> Backend_API
    Backend_API -- Text/Audio Response (WebSocket/HTTP) --> UI
    
    Backend_API -- Store Progress/Profile --> MariaDB[(MariaDB)]
    UI -- Offline Store --> DuckDB_SQLite[(DuckDB/SQLite)]
    DuckDB_SQLite -- Sync --> MariaDB
```

### **3.2 Data Persistence Strategy**
Adhering to a privacy-first approach:
* **Minimal Conversation Storage**: Full conversation histories are **not persistently stored** on the server. Only high-level learning progress (topics, languages, streak) is saved in MariaDB.
* **Session Context**: A temporary, in-memory session context is maintained by FastAPI for ongoing conversations to provide continuity, but this is discarded after logout or session timeout.
* **Uploaded Content**: User-uploaded documents, images, and links are processed for RAG and embedded into ChromaDB, but **the original content is not persistently saved after logout**.
* **Local Data**: DuckDB/SQLite stores essential data for offline functionality and progress tracking, with periodic synchronization to MariaDB.
* For complete details on data persistence, refer to `Appendix J: Data Persistence Strategy`.

### **3.3 Session Management**
User sessions are managed securely, with tokens for authentication and context held temporarily to facilitate seamless conversation continuity within a single session. No long-term retention of conversational data.

---

## **4. Security Considerations**

* **Authentication**: Standard secure login procedures with hashed passwords for user authentication.
* **Authorization**: All family users have **equal capabilities and full autonomy**. The system does not implement internal role-based access control (RBAC) or administrative panels for user management.
* **Data Encryption**: Data in transit (TLS/SSL) and at rest (database encryption) will be encrypted.
* **Input/Output Sanitization**: Robust validation and sanitization of all user inputs and LLM outputs are crucial to prevent prompt injection, XSS, and other vulnerabilities.
* **API Key Management**: API keys for external services are securely stored (e.g., environment variables, secret management) and never exposed client-side.
* **Personal Use Declaration**: The project strictly adheres to its declaration as a "personal family educational tool," which simplifies some security requirements by removing public-facing vulnerabilities, but maintains high standards for family data privacy.

---

## **5. Performance and Scalability**

* **Response Times**: Strict targets for speech processing (<500ms) and AI responses (<2s online, <5s offline) will be met through optimized API calls, efficient data handling, and local LLM fallback.
* **Cost Optimization**: The intelligent LLM router and automatic fallback to local models are key to maintaining the $30/month budget.
* **Scalability**: The architecture is designed to efficiently support up to 3 concurrent family users, optimizing resource usage for this specific scope rather than public scaling.
* **Resource Management**: Efficient use of server and client resources to minimize latency and operational costs.

---

## **6. Error Handling and Monitoring**

* **Logging and Monitoring**: Comprehensive logging (structured JSON) and monitoring of application health, API usage, errors, and performance metrics (e.g., response times, budget burn rate).
* **Graceful Degradation**: The system is designed to degrade gracefully during network interruptions or API failures, automatically switching to offline mode and local resources.
* **Alerting**: Automated alerts for critical errors or budget threshold warnings.

---

## **7. Development and Deployment Strategy**

* **Development Environment**: macOS M3, Python 3.12.4, pip 25.0.1 (Anaconda 'base' environment), Homebrew for dependencies, Ollama/LM Studio for local LLM testing.
* **Production Environment**: InMotion dedicated server, managed via standard Linux system administration tools (Nginx, Gunicorn/Uvicorn, PM2/Systemd).
* **Continuous Integration/Continuous Deployment (CI/CD)**: Automated pipelines for testing, building, and deploying updates to ensure rapid and reliable delivery.
* **Version Control**: Git and GitHub for collaborative development and code management.

---

## **8. Compliance and Legal (for personal use)**

* The architecture and its implementation strictly adhere to the `Personal Use Declaration` (Appendix A), ensuring the application remains exclusively for personal and family educational use. This context influences decisions regarding data retention, user management, and external service integrations.

---

### **Document Completion Status**

**Software Architecture Design - Technical Architecture & System Design** - ✅ **COMPLETE (Finalized)**

**Next Step**: Proceed with **API Documentation** (`api-documentation.md`) as part of the technical deep dive.