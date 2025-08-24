# API Documentation - AI Language Tutor App
## Document #5: API Specification & Integration Guide (Finalized)

---

### **Document Information**
- **Project**: Personal AI Language Tutor App (Family Educational Tool)
- **Document**: API Specification & Integration Guide
- **Version**: 2.0 (Finalized)
- **Date**: June 11, 2025
- **Author**: Development Team
- **Status**: Finalized Design

---

## **1. API Architecture Overview**

The AI Language Tutor App leverages a **Python-first backend with FastAPI**, providing a robust RESTful API and real-time WebSockets. This architecture intelligently routes requests to a **multi-AI system** and integrates with **specialized speech services**, all while prioritizing cost efficiency and supporting offline capabilities.

### **1.1 Service Integration Strategy**
* **Intelligent Routing**: A "mini router layer" dynamically selects the optimal AI model based on cost, performance, and online/offline status.
* **Hybrid Operation**: Seamlessly switches between cloud-based services (IBM Watson, Claude, Mistral, Qwen) and local models (Ollama/LM Studio) for offline resilience and budget control.
* **Budget Constraint**: Strict adherence to a **$30/month** total API cost across all services.

### **1.2 Authentication Strategy**
* **Token-Based Authentication**: Secure JWT (JSON Web Tokens) for user sessions.
* **API Key Management**: All external API keys are securely stored in server-side environment variables and never exposed client-side.
* **Rate Limiting**: Implemented on all endpoints to prevent abuse and manage costs.
* **Usage Monitoring**: Real-time tracking of API consumption to stay within budget.

---

## **2. External API Integrations**

### **2.1 AI Language Model APIs (LLMs)**
The LLM Router handles the intelligent selection and interaction with various models.

#### **2.1.1 Anthropic Claude (Primary Conversation Engine)**
* **Purpose**: Advanced dialogue, contextual understanding, and core conversational practice.
* **Endpoint**: `https://api.anthropic.com/v1/messages`
* **Authentication**: API Key in headers (`x-api-key`).
* **Request Format Example**:
    ```json
    {
      "model": "claude-3-haiku-20240307",
      "max_tokens": 2048,
      "messages": [
        {"role": "user", "content": "Let's discuss this article about space travel in French."}
      ],
      "system": "You are a French language tutor. Provide conversational practice and subtle corrections."
    }
    ```
* **Response Format Example**:
    ```json
    {
      "id": "msg_abc123",
      "content": [{"type": "text", "text": "Bien sûr! Commençons. Qu'est-ce qui vous intéresse le plus dans l'article?"}]
    }
    ```

#### **2.1.2 Mistral AI (Grammar & Quick Responses)**
* **Purpose**: Cost-effective for quick grammar checks, short responses, and focused linguistic feedback.
* **Endpoint**: `https://api.mistral.ai/v1/chat/completions`
* **Authentication**: API Key in headers (`Authorization: Bearer`).
* **Request Format Example**:
    ```json
    {
      "model": "mistral-tiny",
      "messages": [{"role": "user", "content": "Correct this sentence: 'I is going to the park.'"}]
    }
    ```

#### **2.1.3 Alibaba Qwen (Multilingual Support)**
* **Purpose**: Enhanced support for specific languages (e.g., Chinese) and diverse linguistic tasks.
* **Endpoint**: Varies by deployment (e.g., specific Alibaba Cloud endpoint or self-hosted).
* **Authentication**: API Key.
* **Request/Response Format**: Similar to other chat completion APIs.

#### **2.1.4 Ollama / LM Studio (Local Fallback LLM)**
* **Purpose**: Provides offline AI capabilities and acts as a budget overrun protection mechanism.
* **Endpoint (Local)**: `http://localhost:11434/api/chat` (Ollama default) or `http://localhost:1234/v1/chat/completions` (LM Studio default).
* **Authentication**: None (local).
* **Request/Response Format**: Follows OpenAI-compatible chat completion API standards. The LLM Router abstracts this.

### **2.2 Speech Services APIs**

#### **2.2.1 IBM Watson Speech-to-Text (STT)**
* **Purpose**: Highly accurate real-time speech recognition for converting user's spoken input into text.
* **Endpoint (WebSocket for Streaming)**: `wss://api.{region}.speech-to-text.watson.cloud.ibm.com/instances/{instance_id}/v1/recognize`
* **Authentication**: IAM API Key (via Bearer token or basic auth).
* **Request**: Audio stream (e.g., FLAC, Opus) with JSON parameters (language model, interim results).
* **Response**: JSON objects with transcription results, confidence scores, and potential word-level timestamps.

#### **2.2.2 IBM Watson Text-to-Speech (TTS)**
* **Purpose**: Generates natural-sounding audio from AI's text responses.
* **Endpoint**: `https://api.{region}.text-to-speech.watson.cloud.ibm.com/instances/{instance_id}/v1/synthesize`
* **Authentication**: IAM API Key.
* **Request**:
    ```json
    {
      "text": "Hello, how can I help you today?",
      "voice": "en-US_AllisonV3Voice",
      "accept": "audio/mp3"
    }
    ```
* **Response**: Audio file (e.g., `audio/mp3`).

#### **2.2.3 Browser-based Speech APIs (Fallback)**
* **Purpose**: Provides basic STT/TTS functionality when offline or if IBM Watson services are unavailable.
* **Implementation**: Utilizes `SpeechRecognition` and `SpeechSynthesis` interfaces directly in the browser.
* **No specific API endpoint**: Handled client-side.

---

## **3. Internal API Endpoints (FastAPI)**

The FastAPI backend exposes the following endpoints for the client-side PWA.

### **3.1 User Management**
* **`POST /api/auth/register`**
    * **Description**: Registers a new user. **No admin approval required** for new registrations in this personal family tool; all family users have equal and autonomous access.
    * **Request Body**: `{"username": "string", "email": "string", "password": "string", "primary_language": "string"}`
    * **Response**: `{"message": "User registered successfully", "user_id": "uuid"}` or error.
* **`POST /api/auth/login`**
    * **Description**: Authenticates a user and returns a JWT.
    * **Request Body**: `{"email": "string", "password": "string"}`
    * **Response**: `{"access_token": "string", "token_type": "bearer", "user_id": "uuid", "username": "string"}` or error.
* **`POST /api/auth/logout`**
    * **Description**: Invalidates the current user session.
    * **Request Body**: (None, token in headers)
    * **Response**: `{"message": "Logged out successfully"}`.
* **`GET /api/user/profiles`**
    * **Description**: Retrieves a list of available user profiles for selection.
    * **Response**: `[{"user_id": "uuid", "username": "string", "primary_language": "string"}, ...]`
* **`PUT /api/user/profile/{user_id}`**
    * **Description**: Updates the current user's profile information (e.g., target languages).
    * **Request Body**: `{"username": "string", "target_languages": ["string"]}` (partial updates allowed)
    * **Response**: `{"message": "Profile updated successfully"}`.

### **3.2 Conversation & Learning**
* **`POST /api/conversation/start`**
    * **Description**: Initiates a new conversation session.
    * **Request Body**: `{"language": "string", "scenario_id": "uuid"}` (optional)
    * **Response**: `{"session_id": "uuid", "initial_ai_prompt": "string"}`.
* **`POST /api/conversation/message`**
    * **Description**: Sends a text message to the AI and receives a response.
    * **Request Body**: `{"session_id": "uuid", "user_message": "string"}`
    * **Response**: `{"ai_response": "string", "feedback": {"pronunciation": "object", "grammar": "object"}}` (feedback optional).
* **`GET /api/conversation/stream/{session_id}`** (WebSocket)
    * **Description**: Establishes a WebSocket connection for real-time speech input/output and live feedback.
    * **Client Sends**: Audio chunks, text inputs.
    * **Server Sends**: AI text responses, audio responses (TTS), real-time pronunciation/grammar feedback.
* **`POST /api/conversation/feedback`**
    * **Description**: Requests specific feedback on a phrase or word (e.g., pronunciation re-check).
    * **Request Body**: `{"session_id": "uuid", "text_to_analyze": "string", "feedback_type": "pronunciation | grammar"}`
    * **Response**: `{"analysis": "object", "suggestions": ["string"]}`.

### **3.3 Content Management**
* **`POST /api/content/upload`**
    * **Description**: Uploads a file (document, image) or a link for AI processing. **Uploaded content is not persistently saved after logout.**
    * **Request Body**: `multipart/form-data` for files, `{"url": "string"}` for links.
    * **Response**: `{"content_id": "uuid", "message": "Content uploaded for processing"}`.
* **`GET /api/content/preview/{content_id}`**
    * **Description**: Retrieves a preview of the uploaded content.
    * **Response**: Content appropriate for `fileMimeType` (e.g., image, text, PDF snippet).
* **`POST /api/content/process/{content_id}`**
    * **Description**: Triggers AI processing (embedding into ChromaDB) for RAG.
    * **Response**: `{"message": "Content processed successfully", "status": "completed"}`.
* **`GET /api/scenarios`**
    * **Description**: Retrieves a list of predefined learning scenarios.
    * **Response**: `[{"scenario_id": "uuid", "name": "string", "description": "string", "language": "string"}, ...]`

### **3.4 Progress Tracking**
* **`GET /api/progress/summary/{user_id}`**
    * **Description**: Retrieves high-level learning progress (streaks, languages practiced, topics engaged). **Does not include full conversation history.**
    * **Response**: `{"streak": "integer", "languages_mastered": ["string"], "topics_covered": ["string"], "last_activity": "datetime"}`.
* **`POST /api/progress/update/{user_id}`**
    * **Description**: Updates user's progress based on session activity (e.g., daily streak).
    * **Request Body**: `{"activity_type": "string", "value": "integer"}` (e.g., "completed_lesson", 1).
    * **Response**: `{"message": "Progress updated", "new_streak": "integer"}`.

### **3.5 System Status**
* **`GET /api/health`**
    * **Description**: General application health check.
    * **Response**: `{"status": "ok", "version": "string"}`.
* **`GET /api/health/db`**
    * **Description**: Database connectivity status.
    * **Response**: `{"status": "ok", "database": "MariaDB/ChromaDB"}`.
* **`GET /api/health/services`**
    * **Description**: Status of external AI and Speech APIs.
    * **Response**: `{"status": "ok", "services": {"ibm_watson": "up", "claude": "up", "mistral": "up", "ollama_local": "up"}}`

---

## **4. Data Models (Request/Response Examples)**

Detailed Pydantic models will be defined in FastAPI for request body validation and response serialization.

### **4.1 User Model (Internal Representation)**
```python
class User(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    hashed_password: str
    primary_language: str
    target_languages: List[str] = []
    # No roles or administrative flags due to user autonomy model
```

### **4.2 Conversation Message Model**
```json
// Example User Message Request
{
  "session_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "user_message": "Can you tell me more about the Louvre Museum?",
  "message_type": "text" // or "audio_transcription"
}

// Example AI Response
{
  "ai_response": "The Louvre Museum is the world's largest art museum and a historic monument in Paris, France.",
  "feedback": {
    "pronunciation": {
      "word": "Louvre",
      "score": 0.85,
      "issues": ["intonation"],
      "suggestions": ["Try stressing the first syllable more."]
    },
    "grammar": {
      "original_sentence": "I go to the Louvre yesterday.",
      "corrected_sentence": "I went to the Louvre yesterday.",
      "explanation": "Use past tense for past actions."
    }
  }
}
```

---

## **5. Error Handling**

FastAPI provides excellent error handling capabilities.
* **Standard HTTP Status Codes**: (e.g., 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error).
* **JSON Error Responses**:
    ```json
    {
      "detail": "Error description or specific validation message"
    }
    ```
* **Detailed Logging**: Errors will be logged server-side for debugging and monitoring.

---

## **6. Environment Configuration**

Configuration will be managed via environment variables for different deployment environments.

**Development (`.env.development`)**:
```env
APP_ENV=development
DATABASE_URL=sqlite:///./dev.db
CHROMA_DB_PATH=./chroma_dev_data
IBM_WATSON_API_KEY=dev_key_watson
IBM_WATSON_REGION=us-south
CLAUDE_API_KEY=dev_key_claude
MISTRAL_API_KEY=dev_key_mistral
QWEN_API_KEY=dev_key_qwen
OLLAMA_LOCAL_URL=http://localhost:11434
```

**Production (`.env.production`)**:
```env
APP_ENV=production
DATABASE_URL=mysql+pymysql://user:pass@host/ai_tutor_db
CHROMA_DB_PATH=/mnt/data/chroma_prod_data
IBM_WATSON_API_KEY=prod_key_watson
IBM_WATSON_REGION=us-south
CLAUDE_API_KEY=prod_key_claude
MISTRAL_API_KEY=prod_key_mistral
QWEN_API_KEY=prod_key_qwen
OLLAMA_LOCAL_URL=http://localhost:11434 # Only if local LLM is on server or client supports it
```

---

## **7. Monitoring & Logging**

* **Health Checks**:
    * `/api/health`: Overall application status.
    * `/api/health/db`: Database connectivity (MariaDB, ChromaDB).
    * `/api/health/services`: Connectivity to external AI/Speech APIs.
* **Logging Strategy**:
    * Structured JSON logging for easy parsing and analysis.
    * Includes request/response details (sanitized), error traces, and performance metrics.
    * Integrated with monitoring tools for real-time dashboards and alerts.

---

## **8. Implementation Priority**

This API documentation guides the development, aligning with the project's phased approach.

### **Phase 1 - MVP (Core Functionality)**
1.  User Authentication (`register`, `login`, `logout`, `profiles`).
2.  Basic Conversation API (`start`, `message` - text only initially, routing to Claude).
3.  Content Upload (`upload`) and basic processing.
4.  Simple Progress Tracking (`update`).
5.  Health Checks (`health`).

### **Phase 2 - Enhancement (Advanced Features)**
1.  Real-time WebSocket for `conversation/stream` (integrating IBM Watson STT/TTS).
2.  Multi-AI Routing for `conversation/message` (adding Mistral, Qwen, Ollama/LM Studio fallback).
3.  Enhanced Content Processing (`process`) with RAG.
4.  Detailed Progress Summary (`summary`).
5.  Specific Feedback API (`feedback`).

### **Phase 3 - Optimization & Hardening**
1.  Performance optimizations across all endpoints.
2.  Advanced error handling and graceful degradation.
3.  Comprehensive security hardening (e.g., detailed input validation, rate limiting).
4.  Scalability refinements for family user base.

---

### **Document Completion Status**

**API Documentation - API Specification & Integration Guide** - ✅ **COMPLETE (Finalized)**

**Next Step**: Proceed with **Database Design & Data Architecture** (`database-design.md`) as part of the technical deep dive.