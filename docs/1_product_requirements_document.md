# Product Requirements Document (PRD)
## AI Language Tutor App - Executive Summary & Vision (Finalized)

---

### **Document Information**
- **Project**: Personal AI Language Tutor App (Family Educational Tool)
- **Document**: Product Requirements Document (PRD) - Executive Summary & Vision
- **Version**: 2.0 (Finalized)
- **Date**: June 11, 2025
- **Author**: Development Team
- **Status**: Finalized Requirements

---

## **1. Executive Summary**

The AI Language Tutor App is a **personal family educational tool** designed as a Progressive Web Application. It provides personalized, real-time language learning through conversational practice with advanced pronunciation and grammar feedback. Unlike traditional gamified language apps, this solution focuses on practical fluency development through context-driven interactions based on user-uploaded content or specific scenarios, all within a private, family-only environment.

### **1.1 Vision Statement**

To create an intelligent, intuitive language learning companion that bridges the gap between theoretical knowledge and real-world conversational confidence, enabling users to practice languages naturally through meaningful, context-driven interactions with immediate pronunciation and grammar feedback, fostering fluency and cultural appreciation within a private family setting.

### **1.2 Primary Objectives**

* Provide **real-time pronunciation and grammar feedback** with tone, timing, and accent analysis.
* Enable **content-driven learning** through document, image, or link upload processing, allowing users to customize learning experiences.
* Support **scenario-based conversations** for practical skill development.
* Deliver a **family-friendly multi-user experience** with individual progress tracking, emphasizing **full user autonomy** for language and content selection.
* Maintain **cost-effective operation** under a **strict $30/month budget**.

---

## **2. Target Users & User Autonomy**

The AI Language Tutor App is developed exclusively for a maximum of three family users (Father, Daughter, Son).

### **2.1 Intended Users**

* **Primary User**: Developer (Parent) - For personal language learning (Chinese, French, German, Japanese) and professional development.
* **Secondary Users**: Developer's Children (Daughter, Son) - For supervised, age-appropriate language learning and educational support.

### **2.2 User Autonomy & Dynamic Configuration**

Crucially, all users have **full autonomy** within the application. This means:
* Users can **dynamically choose any language, content, and topics** at any time. There are no fixed language assignments per user.
* There are **no parental controls, oversight, or age-appropriate content filtering mechanisms** within the application itself. Each family member operates as an independent learner.
* Authentication is simplified; all registered family members have **identical capabilities and interface access**, and there is no admin approval for sign-ups.

---

## **3. Core Functional Requirements**

The application is designed for a seamless, intuitive, and engaging language learning experience.

* **Conversational Interface**: Main chat panel for new and historical conversations, with contextual dialogues based on uploaded content or scenarios.
* **Content Integration & Customization**: Users can upload files (documents, images), or provide links. The main chat screen splits into a preview section and a conversation/feedback section when content is uploaded. Uploaded content is **not saved persistently** after user logout.
* **Speech Layer Integration**:
    * **Speech-to-Text (STT)**: IBM Watson's speech-to-text API in WebSocket mode for live transcription; browser-based Speech APIs as fallback.
    * **Text-to-Speech (TTS)**: IBM Watson's text-to-speech API (MP3 audio streams); browser-based Speech APIs as fallback.
* **Pronunciation & Grammar Feedback**: Provides real-time analysis for improved speaking and writing. Feedback on learning and proficiency for custom topics is provided *only if explicitly requested* by the user.
* **Learning Tracking & Gamification**: Implements the "Don't break the chain" strategy for streak-based learning, tracking topics, languages, and progress feedback without storing full conversation histories.
* **Offline UX**: Visual cues indicate online/offline mode, such as a "powered by Ollama • offline" banner.

---

## **4. Technical Architecture Overview (Finalized)**

The AI Language Tutor App is a **Python-first and Python-driven hybrid multi-service platform**, with minimal JavaScript for client-side rendering. It's designed as a local-first, multimodal, LLM-agnostic tool.

* **Frontend UI**: FastHTML + MonsterUI.
* **Backend Framework**: FastAPI.
* **Document Processing**: FastAPI + LangChain (or custom).
* **Vector Search**: ChromaDB (vector store), MariaDB (metadata), DuckDB/SQLite (offline).
* **Database**: Hybrid using **MariaDB** (server-side, persistent data) and **SQLite/DuckDB** (local/offline storage).
* **Hosting**: InMotion dedicated server with full administrative control.
* **Development Environment**: **macOS M3 environment with Python 3.12.4 and pip 25.0.1 (managed via Anaconda 'base' environment)**.
* **LLM Providers**:
    * **Cloud**: Anthropic Claude API, Mistral API, Alibaba Qwen API.
    * **Offline**: Ollama / LM Studio (with a mini router layer and prompt adapters for dynamic routing).
* **Speech Services**: IBM Watson Speech APIs.

---

## **5. Business Model & Budget Management**

### **5.1 Cost Structure**

The project is self-funded with a **strict operational budget of $30/month**. This includes API costs (speech services, AI model usage) and infrastructure (database hosting, server maintenance).

### **5.2 Value Proposition**

* **Personal ROI**: Enhanced language skills for professional and personal advancement.
* **Family Value**: Cost-effective, private educational tool for children's language development.
* **Long-term Benefits**: Maintained fluency through consistent, engaging practice.

---

## **6. Risk Assessment & Mitigation**

### **6.1 Technical Risks**

* **Speech Recognition Accuracy**: Variability across accents/languages.
    * *Mitigation*: Implement fallback browser-based speech services; continuous evaluation and optimization of IBM Watson integration.
* **Real-time Processing Latency**: Potential impact on user experience, especially with cloud AI/speech.
    * *Mitigation*: Optimize API calls; implement efficient data chunking; prioritize local LLMs (Ollama) for offline/low-latency needs; use FastHTML for minimal frontend overhead.
* **API Cost Overruns**: Exceeding the $30/month budget with increased usage.
    * *Mitigation*: Implement real-time usage monitoring; automatic fallback to local Ollama models upon budget thresholds; strategic selection of cost-effective cloud AI services.
* **Offline Synchronization Complexity**: Ensuring consistent data across hybrid local/server storage.
    * *Mitigation*: Design robust synchronization mechanisms for MariaDB, ChromaDB, and DuckDB/SQLite; prioritize data integrity.

### **6.2 Project Risks**

* **Scope Creep**: Expanding features beyond the core MVP.
    * *Mitigation*: Strict MVP feature prioritization and adherence to documented requirements.
* **Technical Complexity**: Exceeding available development time.
    * *Mitigation*: Adopt an iterative, continuous development approach with regular milestone assessments.

---

## **7. Project Status**

The AI Language Tutor App project is in an **advanced documentation phase**, with its foundational and architectural documents finalized. This comprehensive PRD now serves as the **definitive guide for product direction and core requirements**, fully aligned with the finalized technical stack and user autonomy principles.

---

### **Document Completion Status**

**Product Requirements Document (PRD) - Executive Summary & Vision** - ✅ **COMPLETE (Finalized)**

**Next Step**: Proceed with **Software Requirements Specification (SRS)** (`srs_software_requirements.md`) to detail functional and non-functional requirements based on this finalized PRD.