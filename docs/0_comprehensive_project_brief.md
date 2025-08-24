# AI Language Tutor App - Comprehensive Project Brief (Finalized)

## Personal Family Educational Platform - Consolidated Overview

---

### **Executive Summary & Project Declaration**

The AI Language Tutor App is a **personal family educational tool** developed exclusively for private, family use (Father + daughter + son, maximum 3 users). It is **NOT** intended for commercial distribution, public access, or third-party usage, as formally declared in Appendix A. This project is a self-funded initiative, prioritizing personal language learning, family educational enrichment, and exploration of AI technologies, all while adhering to a strict monthly operational budget of $30.

This document provides a consolidated, comprehensive overview of the AI Language Tutor App's functional description, conceptual design, technical architecture, and project goals, incorporating all critical corrections, clarifications, and finalized stack details from recent updates and implementation notes.

---

### **1. Vision & Core Objectives**

**Vision Statement**: To create an intelligent, intuitive language learning companion that bridges the gap between theoretical knowledge and real-world conversational confidence, enabling users to practice languages naturally through meaningful, context-driven interactions with immediate pronunciation and grammar feedback, fostering fluency and cultural appreciation within a private family setting.

**Primary Objectives**:
* Provide **real-time pronunciation and grammar feedback** with tone, timing, and accent analysis.
* Enable **content-driven learning** through document, image, or link upload processing, allowing users to customize learning experiences.
* Support **scenario-based conversations** for practical skill development.
* Deliver a **family-friendly multi-user experience** with individual progress tracking.
* Maintain **cost-effective operation** under a $30/month budget.

---

### **2. User Model & Access (Corrected)**

The AI Language Tutor App supports a user-autonomous model, allowing each family member full control over their learning journey.

* **Intended Users**:
    * **Primary User**: Developer (Parent) - For personal language learning (Chinese, French, German, Japanese) and professional development.
    * **Secondary Users**: Developer's Children (Daughter, Son) - For supervised, age-appropriate language learning and educational support.
* **User Autonomy & Dynamic Configuration (Crucial Correction)**:
    * **Dynamic Language Selection**: All users can dynamically choose any language, content, and topics at any time. There are no fixed language assignments per user.
    * **Full User Autonomy**: There are **no parental controls, oversight, or age-appropriate content filtering mechanisms** within the application itself. Each family member operates as an independent learner.
    * **Simplified Security Model**: Basic authentication is implemented without complex role-based access restrictions. All family members have identical capabilities and interface access.
    * **No Admin Approval for Sign-ups**: The initial concept of admin approval for new user sign-ups (`mcampos.cerda@tutanota.com`) is **removed**. All registered family members have equal access.
* **Authentication**: Simple login interface with email and password validation, including "remember me" and "forgot password" options.

---

### **3. Core Functional Requirements**

The application is designed for a seamless, intuitive, and engaging language learning experience, prioritizing a "local-first" approach for resilience and cost-effectiveness.

* **Home Screen & Navigation**: Upon login, users access a home screen with a top navigation bar for language selection, application mode, and logout. The application interface, menus, and controls will always be displayed in **English**.
* **Conversational Interface**:
    * A main chat panel allows for new conversations and access to conversation history.
    * **Contextual Conversations**: Engage in dialogues based on uploaded content or predefined scenarios.
* **Content Integration & Customization**:
    * Users can upload files (documents, images), or provide links to customize their learning experience.
    * When content is uploaded, the main chat screen must be split into two sections: one to allow for previewing options of the uploaded content and another for the conversation follow along or for grammar-syntax-orthography real-time feedback and correction checks.
    * Uploaded content is *not* saved persistently after user logout.
* **Speech Layer Integration**:
    * **Speech-to-Text (STT)**: Utilizes IBM Watson's speech-to-text API in WebSocket mode for live transcription; FastAPI can interface using an async WebSocket route. Browser-based Speech APIs serve as fallback for offline mode.
    * **Text-to-Speech (TTS)**: IBM Watson's text-to-speech API can return MP3 audio streams that can be embedded directly into the FastHTML components for playback. Browser-based Speech APIs are also used as fallback.
* **Pronunciation & Grammar Feedback**: Provides real-time analysis for improved speaking and writing. Feedback on learning and proficiency for custom topics is provided *only if explicitly requested* by the user.
* **Learning Tracking & Gamification**:
    * Promotes the "Don't break the chain" strategy as a streak-based learning system or a habit-building framework. Where the users engage in daily learning tasks and visually track their progress to maintain consistency.
    * Encouraging users to complete a learning activity daily and showing their streak on the app.
    * Using a calendar-like system to mark each day a user engages with the app.
    * Incentivizing users with badges or highlighting topics, words, scenarios, language proficiency for maintaining a long streak.
    * The application tracks topics and languages selected, along with progress feedback, but *not* full conversation histories.
* **Offline UX**: Provides visual cues that distinguish between online/offline mode—something like a "powered by Ollama • offline" banner when cloud fallback is unavailable. This ensures a seamless and informed user experience regardless of connectivity.

---

### **4. Technical Architecture Overview**

The AI Language Tutor App is a **Python-first and Python-driven hybrid multi-service platform**, with **minimal JavaScript for client-side rendering** (charts, mind maps), only embedding it where needed. It is designed as a local-first, multimodal, LLM-agnostic tool, balancing cloud-savviness with offline-awareness to offer an elegant visual storytelling and conversational flow.

* **Frontend UI**: FastHTML + MonsterUI
* **Backend Framework**: FastAPI
* **Document Upload + Chunking**: FastAPI + LangChain (or custom implementation)
* **Vector Search**: ChromaDB (vector store), MariaDB (metadata), DuckDB/SQLite (offline)
* **Database**: Hybrid approach utilizing **MariaDB** for persistent session data, document references, and user metadata on the server. **SQLite** and **DuckDB** are used for local/offline storage. Documents and their embedding metadata will be modeled separately from vectors stored in ChromaDB.
* **Hosting**: InMotion dedicated server with full administrative control.
* **Development Environment**: macOS M3 environment with **Python 3.12.4 and pip 25.0.1** (managed via Anaconda 'base' environment).

#### **4.1 AI Service Integration (Multi-AI System with Intelligent Routing)**

A "mini router layer" will dynamically adapt prompts and responses based on the LLM's context length, formatting preferences, and capabilities. **Prompt adapters** per model will help tweak temperature, format, and token budget per target (especially Qwen vs. Claude or local LLaMA derivatives).

* **LLM Providers (Cloud)**:
    * Anthropic Claude API (Primary conversation engine and content processing).
    * Mistral API (Grammar correction and quick responses).
    * Alibaba Qwen API (Multilingual support, especially for Chinese language learning).
* **LLM Providers (Offline)**:
    * Ollama / LM Studio (Offline mode and budget overrun protection). For Ollama or LM Studio, a lightweight selector panel will read available models from the system (e.g., from a JSON config or local folder scan), then route the conversation accordingly. This panel can also tag their max context/precision for user preview.
* **Routing/Prompt Adapter**: LangChain LCEL or custom adapter.

#### **4.2 Other Integrations & Features**

* **Speech-to-Text / TTS**: IBM Watson Speech APIs (WebSocket for STT + MP3 playback for TTS).
* **Markdown + Diagrams**: MonsterUI (Markdown + MermaidJS), markmap-lib for visual rendering.
* **Background Processing**: FastAPI BackgroundTasks, with Celery as an optional consideration for more complex asynchronous tasks.
* **Permissions**: Read-only local model catalog (no install/delete from UI) to simplify user interaction and prevent unintended changes.

#### **4.3 Security & Data Handling**

* **File Uploads**: Include MIME validation and document sanitization to prevent injection.
* **LLM Output**: Validate structure of markdown or diagram output from LLMs to prevent injection.
* **Privacy-First**: Minimal storage of sensitive conversation content.
* **Session Continuity**: Smart context preservation for "continue conversation" functionality.

---

### **5. Budget Management**

The project is committed to maintaining a strict **$30/month** operational budget. This is achieved through:
* Prioritizing **offline capabilities** via local LLMs (Ollama).
* Strategic selection of cost-effective cloud AI services.
* Real-time cost tracking with automatic fallbacks to local models upon budget thresholds.

---

### **6. Success Metrics for Family Use**

**Learning Outcomes**:
* **Individual Progress**: Measurable improvement in target languages for each family member.
* **Engagement**: Consistent daily usage and maintained learning streaks.
* **Family Interaction**: Shared learning experiences and cross-family language practice.
* **Cultural Appreciation**: Enhanced understanding of target language cultures.

**Technical Performance**:
* **Reliability**: 99%+ uptime for family learning sessions.
* **Responsiveness**: <2-second response times for AI interactions.
* **Budget Compliance**: Monthly costs maintained within $30 allocation.
* **User Satisfaction**: High family satisfaction with interface and features.

**Long-term Family Impact**:
* **Sustainable Learning**: Continued engagement over months and years.
* **Educational Value**: Demonstrable language skill advancement.
* **Technology Integration**: Successful introduction of AI tools for educational purposes.
* **Family Bonding**: Enhanced family communication through shared language learning.

---

### **7. Project Status**

The AI Language Tutor App project is in an advanced documentation phase, with foundational and architectural documents largely complete and corrected. This consolidated and updated brief serves as the definitive guide for ongoing development and implementation.

---

**Document Status**: ✅ **COMPLETE** - Finalized comprehensive application brief.
**Next Step**: Please provide your next request.