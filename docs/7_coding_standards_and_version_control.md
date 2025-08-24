# Coding Standards & Version Control

## AI Language Tutor App - Development Guidelines & GitHub Workflow

### **Document Overview**

This document establishes comprehensive coding standards, development practices, and version control workflows for the AI Language Tutor App project. It provides guidelines for maintaining code quality, consistency, and collaborative development using GitHub as our primary platform.

### **1. Development Philosophy**

#### **1.1 Core Principles**

**Code Quality First**:

  - Write code that is readable, maintainable, and testable
  - Follow established patterns and conventions consistently
  - Prioritize clarity over cleverness
  - Document complex logic and architectural decisions

**Collaborative Development**:

  - Use clear, descriptive commit messages
  - Implement thorough code review processes
  - Maintain comprehensive documentation
  - Foster knowledge sharing through clear code structure

**Progressive Enhancement**:

  - Build features incrementally with proper testing
  - Maintain backward compatibility when possible
  - Use feature flags for experimental functionality
  - Plan for scalability from the beginning

#### **1.2 Technology Stack Standards**

**Frontend Stack**:

  - **FastHTML**: Server-rendered HTML for a Pythonic frontend
  - **MonsterUI**: Primary UI component library for consistent design
  - **Alpine.js**: Used minimally for specific, localized interactivity where absolutely necessary, aligning with the "full pythonic application" principle
  - **TypeScript**: Type-safe JavaScript development (for minimal Alpine.js where used)

**Backend Stack (Python)**:

  - **FastAPI**: High-performance Python web framework for APIs and backend logic
  - **SQLAlchemy**: ORM for database interactions
  - **Pydantic**: Data validation and settings management
  - **Celery**: Asynchronous task queue for background processing
  - **pytest**: Testing framework

**AI Libraries & Services**:

  - **Anthropic Claude**: Primary conversation engine for advanced dialogue and lesson planning
  - **Mistral AI**: For grammar checks and quick responses, chosen for cost-effectiveness and accuracy
  - **Alibaba Qwen**: For multilingual support, especially Chinese vocabulary and language processing
  - **Ollama**: Local AI fallback for offline mode and budget overrun protection
  - **IBM Cloud Speech-to-Text**: Accurate speech recognition
  - **IBM Cloud Text-to-Speech**: Natural voice synthesis
  - **Browser-based Speech APIs**: Fallback for offline Text-to-Speech functionality

**Database**:

  - **MariaDB**: Server-side permanent storage
  - **SQLite**: Local storage for development and offline mode
  - **ChromaDB**: Vector database for RAG (Retrieval Augmented Generation) capabilities with uploaded content

**LLM Orchestration**:

  - LLM orchestration, including multi-AI routing and RAG (Retrieval Augmented Generation) with ChromaDB, is handled directly by the Python backend services (FastAPI). This approach supports complex AI interactions within the "full pythonic application" paradigm, without relying on external JavaScript-based frameworks like LangChain.

### **2. Coding Standards**

#### **2.1 Python Backend (FastAPI + SQLAlchemy) Standards**

**2.1.1 Code Formatting**:

  - **Black**: Use `black` for uncompromising code formatting.
  - **Isort**: Use `isort` for sorting imports alphabetically and separating into sections.

**2.1.2 Naming Conventions**:

  - **Variables**: `snake_case` (e.g., `user_name`, `api_key`).
  - **Functions/Methods**: `snake_case` (e.g., `get_user_profile`, `process_speech_input`).
  - **Classes**: `PascalCase` (e.g., `UserProfile`, `SpeechProcessor`).
  - **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_TOKENS`, `DEFAULT_LANGUAGE`).

**2.1.3 Docstrings and Comments**:

  - Use [Google Style Docstrings](https://www.google.com/search?q=https://google.github.io/styleguide/pyguide.html%23pyguide-documenting-functions-and-classes) for functions, methods, and classes.
  - Inline comments for complex logic, but prefer self-documenting code.

**2.1.4 Type Hinting**:

  - Use [Python type hints](https://docs.python.org/3/library/typing.html) extensively for clarity and maintainability.

**2.1.5 Error Handling**:

  - Use `try...except` blocks for handling expected errors gracefully.
  - Raise custom exceptions for application-specific error scenarios.
  - Log errors with appropriate severity levels.

**2.1.6 Security Practices**:

  - **Input Validation**: Validate all user inputs rigorously at the API level.
  - **Sensitive Data**: Never log sensitive user data.
  - **API Keys**: Store API keys securely (e.g., environment variables, not in code).
  - **Authentication**: Implement secure token-based authentication.

#### **2.2 Frontend (FastHTML + MonsterUI + Alpine.js) Standards**

**2.2.1 FastHTML & Pythonic Frontend**:

  - Structure FastHTML templates for modularity and reusability.
  - Prioritize server-side rendering to maintain a "Pythonic" application.
  - Use `htmx` attributes for dynamic content loading where appropriate, minimizing custom JavaScript.

**2.2.2 MonsterUI Guidelines**:

  - Utilize MonsterUI components for all standard UI elements (buttons, forms, navigation, modals, etc.) to ensure a consistent and modern look and feel.
  - Customize MonsterUI components primarily through their provided configuration options and CSS variables, rather than extensive custom CSS overrides.
  - Adhere to MonsterUI's best practices for component composition and accessibility.

**2.2.3 Alpine.js Best Practices (Minimal Usage)**:

  - Use Alpine.js only for specific, localized interactive elements that cannot be efficiently handled by FastHTML or `htmx` alone.
  - Keep Alpine.js directives (`x-data`, `x-bind`, `x-on`, etc.) contained within the smallest possible HTML scope.
  - Avoid complex state management or large JavaScript logic within Alpine.js. For more complex interactions, prefer server-side Python logic or dedicated backend endpoints.
  - Ensure Alpine.js enhances the user experience without introducing significant client-side complexity or violating the "full pythonic application" principle.

**2.2.4 JavaScript (TypeScript) Standards**:

  - For any necessary custom JavaScript (e.g., Alpine.js plugins or specific front-end logic):
      - **ESLint & Prettier**: Enforce consistent code style and formatting.
      - **TypeScript**: Use TypeScript for type safety and better tooling.
      - **Naming Conventions**: `camelCase` for variables and functions. `PascalCase` for classes.
      - **Modularity**: Organize JavaScript into small, single-purpose modules.

#### **2.3 Database (MariaDB + SQLite + ChromaDB) Standards**

**2.3.1 Schema Design**:

  - **Normalization**: Follow normalization principles (up to 3NF) to minimize data redundancy.
  - **Indexing**: Create indexes on frequently queried columns (e.g., foreign keys, search fields).
  - **Naming Conventions**: `snake_case` for table and column names.
  - **Primary Keys**: Use auto-incrementing integer primary keys.
  - **Foreign Keys**: Enforce referential integrity using foreign key constraints.

**2.3.2 Data Management**:

  - **Migrations**: Use SQLAlchemy-Alembic for database migrations.
  - **Backups**: Implement regular backup procedures for MariaDB.
  - **Privacy**: Adhere to data privacy principles (e.g., GDPR), minimizing storage of sensitive conversation content.
  - **ChromaDB**: Ensure efficient embedding generation and retrieval for RAG.

### **3. Version Control (GitHub Workflow)**

#### **3.1 Branching Strategy**

**GitFlow-like Hybrid Model**:

  - **`main`**: Production-ready code only. Protected branch, no direct commits.
  - **`develop`**: Integration branch for new features. All feature branches merge into `develop`.
  - **`feature/`**: New features. Branch off `develop`, merge into `develop`. (e.g., `feature/user-auth`)
  - **`bugfix/`**: Bug fixes. Branch off `main` or `develop` depending on urgency, merge back accordingly.
  - **`release/`**: Preparation for production releases. Branch off `develop`, merge into `main` and `develop`.

#### **3.2 Commit Message Guidelines**

**Conventional Commits**:

  - `type(scope): subject`
      - `type`: `feat` (new feature), `fix` (bug fix), `docs` (documentation), `style` (formatting), `refactor` (code refactoring), `test` (adding tests), `chore` (maintenance), `perf` (performance improvements).
      - `scope`: Optional, indicates the part of the codebase affected (e.g., `backend`, `frontend`, `db`, `auth`).
      - `subject`: Concise summary (under 50 chars), imperative mood, no period.
  - **Body**: More detailed explanation if necessary.
  - **Footer**: Reference to issues (e.g., `Closes #123`, `Refs #456`).

#### **3.3 Pull Request (PR) Workflow**

1.  **Create a Branch**: Always work on a new `feature/` or `bugfix/` branch.
2.  **Commit Changes**: Follow commit message guidelines.
3.  **Push Branch**: Push your branch to GitHub.
4.  **Create PR**: Open a pull request from your feature branch to `develop`.
5.  **Code Review**:
      - Require at least one reviewer approval.
      - Address all comments and make necessary changes.
      - Avoid direct pushes to PR branches after review comments; prefer new commits for clarity.
6.  **Merge**: Once approved, merge the PR into `develop`. Use "Squash and Merge" for clean history on `develop`.

### **4. Documentation Standards**

#### **4.1 In-Code Documentation**

  - **Comments**: Explain "why" not "what" for complex logic.
  - **Docstrings**: Document all public classes, methods, and functions.
  - **Type Hints**: Essential for Python code clarity.

#### **4.2 Project Documentation**

  - **README.md**: High-level overview, setup instructions, and quick start guide.
  - **API Documentation**: Use FastAPI's auto-generated OpenAPI (Swagger UI) for API endpoints. Supplement with custom documentation for external integrations.
  - **Architecture Decisions Records (ADRs)**: Document significant architectural decisions.
  - **User Guide**: Provide a simple guide for family members using the app.
  - **Maintenance Guide**: For solo developer operations.

### **5. Quality Assurance**

#### **5.1 Testing Strategy**

  - **Unit Tests**: For individual functions/components (pytest).
  - **Integration Tests**: For interactions between components/services.
  - **End-to-End Tests**: Simulate user flows (e.g., Playwright for frontend).
  - **Performance Tests**: Evaluate response times, throughput, and API costs.
  - **Security Tests**: Vulnerability scanning, penetration testing basics.

#### **5.2 CI/CD (Continuous Integration/Continuous Deployment)**

  - **GitHub Actions**: Automate testing, linting, and deployment workflows.
  - **Automated Checks**:
      - Linting (Black, Isort, ESLint)
      - Type checking (mypy, TypeScript compiler)
      - Unit and integration tests
      - Security scans (basic checks)

### **Conclusion**

By adhering to these coding standards and version control guidelines, we ensure:

### **Key Benefits**

**Code Quality**:

  - Consistent formatting and style across the entire codebase
  - Comprehensive type safety with TypeScript (for minimal JS) and Python type hints
  - Thorough testing coverage and quality assurance
  - Clear documentation and maintainable code structure

**Team Collaboration**:

  - Streamlined GitHub workflow with clear branch strategies
  - Efficient code review processes with standardized templates
  - Automated CI/CD pipelines for quality assurance
  - Comprehensive issue tracking and project management

**Security & Performance**:

  - Robust security practices and input validation
  - Performance monitoring and optimization guidelines
  - Secure handling of sensitive data and API keys
  - Regular security audits and vulnerability assessments

**Maintainability**:

  - Clear project structure and organization
  - Comprehensive documentation standards
  - Automated quality checks and enforcement
  - Scalable development practices for team growth

### **Next Steps**

With these standards in place, the development team can:

1.  Set up development environments consistently
2.  Begin implementing features with confidence
3.  Maintain high code quality throughout development
4.  Scale the team effectively as the project grows

This document serves as the definitive guide for all development activities and should be regularly updated as the project evolves and new best practices emerge.

**Document Status**: Complete - Ready for implementation
**Next Document**: \#8 - Task Lists & Project Management