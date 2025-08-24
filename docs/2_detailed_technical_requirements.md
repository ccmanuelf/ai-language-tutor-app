# Software Requirements Specification (SRS)
## AI Language Tutor App - Detailed Technical Requirements (Finalized)

---

### **Document Information**
- **Project**: Personal AI Language Tutor App (Family Educational Tool)
- **Document**: Software Requirements Specification (SRS)
- **Version**: 2.0 (Finalized)
- **Date**: June 11, 2025
- **Author**: Development Team
- **Status**: Finalized Requirements

---

## **1. Introduction**

### **1.1 Purpose**
This document specifies the comprehensive functional and non-functional requirements for the AI Language Tutor App, a Progressive Web Application focused on conversational language learning with real-time pronunciation and grammar feedback. It formalizes the requirements based on the finalized Product Requirements Document (PRD) and subsequent architectural decisions, including the user autonomy model.

### **1.2 Scope**
The system enables a small group of family users (maximum 3) to practice language skills through AI-powered conversations based on user-uploaded content or predefined scenarios. Key emphasis is placed on immediate pronunciation analysis, grammar correction, contextual learning, and cost-effective operation within a personal family environment. The application is developed exclusively for **personal and family use only** and is not intended for commercial use or public distribution.

### **1.3 Definitions and Abbreviations**
- **PWA**: Progressive Web Application
- **STT**: Speech-to-Text
- **TTS**: Text-to-Speech
- **AI**: Artificial Intelligence
- **LLM**: Large Language Model
- **MVP**: Minimum Viable Product
- **API**: Application Programming Interface
- **RAG**: Retrieval Augmented Generation

---

## **2. System Overview**

### **2.1 System Context**
The AI Language Tutor App operates as a Python-first, Python-driven hybrid multi-service platform. It features a FastAPI backend and FastHTML frontend, integrating with cloud-based AI and speech services, and robust local LLM capabilities for offline operation. Data persistence utilizes a hybrid approach with MariaDB (server-side for metadata), ChromaDB (vector store), and DuckDB/SQLite (local/offline storage).

### **2.2 User Classes**
The application is designed for a maximum of three family users (Father, Daughter, Son). All users have identical capabilities and full autonomy within the application.

* **Primary User**: Developer (Parent) - Engages in personal language learning and utilizes the app for professional development and technical skill advancement.
* **Secondary Users**: Developer's Children - Utilize the app for language learning and educational support.

**Note on User Autonomy**: There is **no "System Administrator" role within the application's user management** for approving accounts or managing user details. All registered family members have equal access and control over their learning experience.

---

## **3. Functional Requirements (FRs)**

### **3.1 User Management & Authentication**

* **FR-001 User Authentication**:
    * The system shall provide a simple login interface with email and password validation.
    * The system shall include a "remember me" checkbox.
    * The system shall include a "forgot password" link.
    * The system shall include a "sign up" link.
    * The system shall allow new users to register without requiring admin approval.
    * The system shall not include any in-app user management features (e.g., adding/editing/deleting users by an admin).
    * The system shall not enforce specific "primary languages" per user. Users can dynamically select languages.

* **FR-002 User Profile Management**:
    * The system shall allow users to select and dynamically change their target language(s) for learning at any time.
    * The system shall maintain individual learning progress for each user profile.

### **3.2 Main Interface & Content Interaction**

* **FR-003 Main User Interface**:
    * The system shall present a top navigation bar with options for language selection, application mode (online/offline), and logout.
    * The system shall provide a main chat panel for new and historical conversations.
    * When content is uploaded, the main chat screen shall split into two sections: one for previewing the uploaded content and another for conversation/feedback.

* **FR-004 Content Upload & Processing**:
    * The system shall allow users to upload documents (PDF, TXT, MD), images (JPG, PNG), or provide external links for learning customization.
    * The system shall process uploaded text content by chunking and embedding it for Retrieval Augmented Generation (RAG).
    * The system shall perform MIME type validation and sanitization for all uploaded files.
    * **Crucially, uploaded content shall not be saved persistently after the user logs out**.

### **3.3 Conversational AI & Speech Integration**

* **FR-005 Conversational AI**:
    * The system shall generate context-aware conversations based on user input, uploaded content, or selected scenarios.
    * The system shall dynamically route requests to appropriate LLM providers (Anthropic Claude, Mistral, Alibaba Qwen) based on context, language, and cost.
    * The system shall utilize local LLMs (Ollama / LM Studio) for offline mode and budget protection, with a "mini router layer" and "prompt adapters."
    * The system shall ensure LLM outputs are validated (e.g., markdown, MermaidJS diagrams) to prevent injection risks.

* **FR-006 Speech Layer Integration**:
    * **Speech-to-Text (STT)**: The system shall use IBM Watson's speech-to-text API in WebSocket mode for real-time transcription. Browser-based Speech APIs shall serve as fallback.
    * **Text-to-Speech (TTS)**: The system shall use IBM Watson's text-to-speech API to generate MP3 audio streams for AI responses. Browser-based Speech APIs shall serve as fallback.
    * The system shall provide real-time pronunciation, grammar, tone, timing, and accent feedback on user speech.

### **3.4 Learning Tracking & Offline Capability**

* **FR-007 Learning Tracking**:
    * The system shall implement the "Don't break the chain" strategy for streak-based learning.
    * The system shall track topics, languages engaged, and progress feedback for each user.
    * **The system shall not retain full conversation histories**.

* **FR-008 Offline Functionality**:
    * The system shall detect online/offline status and provide visual cues (e.g., banner "powered by Ollama • offline").
    * The system shall seamlessly transition to offline mode, utilizing local LLMs and local data storage (DuckDB/SQLite).
    * The system shall synchronize relevant learning progress data when connectivity is restored.

### **3.5 Budget Management**

* **FR-009 Budget Management**:
    * The system shall implement real-time API cost tracking.
    * The system shall automatically fallback to local LLMs (Ollama/LM Studio) when predefined budget thresholds are approached or exceeded, ensuring monthly costs remain under $30.

---

## **4. Non-Functional Requirements (NFRs)**

### **4.1 Performance**

* **NFR-P-001 Response Times**:
    * Speech-to-Text latency shall be less than 500ms for continuous speech.
    * Text-to-Speech audio generation shall begin within 500ms of AI response.
    * AI conversational response times shall be less than 2 seconds (online) and within 5 seconds (offline).
* **NFR-P-002 Scalability**: The system shall efficiently support up to 3 concurrent family users without performance degradation.
* **NFR-P-003 Resource Usage**: The system shall optimize CPU and memory usage to run efficiently on a macOS M3 development environment and an InMotion dedicated server.

### **4.2 Security**

* **NFR-S-001 Data Privacy**:
    * The system shall implement a privacy-first approach with minimal storage of sensitive conversation content.
    * Personal data shall be isolated for each user.
    * Uploaded content will be processed in-session and not stored persistently after logout.
* **NFR-S-002 Authentication Security**: User credentials shall be securely stored and transmitted using industry best practices.
* **NFR-S-003 Input Validation**: The system shall perform robust input validation for all user-provided data and API inputs to prevent injection attacks (e.g., prompt injection, code injection from LLM output).

### **4.3 Usability**

* **NFR-U-001 Intuitive Interface**: The user interface shall be intuitive and easy to navigate for all family members.
* **NFR-U-002 Accessibility**: The application shall adhere to basic accessibility guidelines for web applications.
* **NFR-U-003 Multimodal Interaction**: The system shall support seamless transitions between text, speech, and content-based interactions.

### **4.4 Reliability**

* **NFR-R-001 Uptime**: The online components of the application shall maintain 99%+ uptime.
* **NFR-R-002 Error Handling**: The system shall gracefully handle API errors, network disconnections, and other exceptions, providing informative feedback to the user.
* **NFR-R-003 Data Integrity**: The hybrid data persistence strategy shall ensure data consistency and integrity across online and offline modes.

### **4.5 Maintainability**

* **NFR-M-001 Code Quality**: The codebase shall adhere to established Python coding standards (e.g., PEP 8).
* **NFR-M-002 Documentation**: Comprehensive technical and user documentation shall be maintained.
* **NFR-M-003 Modularity**: The system architecture shall promote modularity for ease of updates and feature additions.

### **4.6 Cost Efficiency**

* **NFR-C-001 Budget Adherence**: The total monthly operational cost for cloud services (AI, Speech, Database) shall not exceed $30/month.
* **NFR-C-002 Cost Optimization**: The system shall prioritize cost-effective API usage, including intelligent routing and fallback mechanisms to local models.

---

## **5. Project Constraints and Assumptions**

### **5.1 Schedule Constraints**
* **Continuous Development**: The project follows a continuous development model with milestone-based progress rather than fixed delivery dates.
* **MVP Priority**: Core functionality (conversational AI, speech, content integration, progress tracking, budget management, user autonomy) shall be prioritized for the Minimum Viable Product.
* **Iterative Approach**: Development will be iterative with regular testing and refinement cycles.

### **5.2 Assumptions**
* **Development Environment**: The primary development environment is macOS M3 with Python 3.12.4 and pip 25.0.1 (Anaconda 'base' environment).
* **Production Environment**: The production environment is an InMotion dedicated server.
* **User Environment**: Users will have access to modern devices with working microphones and audio output for optimal experience.
* **Basic Computer Literacy**: Users are assumed to have basic computer literacy for navigation and file uploads.
* **Content Availability**: Users will provide relevant documents or utilize predefined scenarios for their learning.
* **Internet Connectivity (for online mode)**: A stable internet connection is assumed for access to cloud AI and speech services when operating in online mode.
* **User Autonomy**: All family users will exercise their autonomy responsibly within the educational context of the application.

---

## **6. Approval and Change Management**

### **6.1 Requirements Validation**
* Requirements shall be validated through iterative prototype testing and user feedback.
* Technical feasibility shall be confirmed through proof-of-concept development.

### **6.2 Change Control**
* All requirement changes shall be documented and their impact assessed.
* Changes in priority shall consider budget and technical constraints.
* Scope modifications shall maintain MVP viability and adherence to the personal family use declaration.

---

### **Document Completion Status**

**Software Requirements Specification (SRS) - Detailed Technical Requirements** - ✅ **COMPLETE (Finalized)**

**Next Step**: Proceed with **UX/UI Documentation** (`ux_ui_documentation.md`) to align the user experience and interface design with these finalized requirements.