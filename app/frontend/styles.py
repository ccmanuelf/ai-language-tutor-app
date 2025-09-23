"""
Frontend Styles Component
AI Language Tutor App - CSS Framework and Theming

Modern MonsterUI-inspired styling system with:
- CSS custom properties for theming
- Responsive design utilities
- Component-specific styles
- Mobile-first approach
"""

from fasthtml.common import Style


def load_styles():
    """Load comprehensive CSS styles for the AI Language Tutor frontend"""
    return Style("""
    /* AI Language Tutor - YouLearn-Inspired Modern UI */
    :root {
        /* YouLearn-inspired color palette */
        --primary-color: #6366f1;
        --primary-light: #a5b4fc;
        --primary-dark: #4338ca;
        --secondary-color: #0891b2;
        --accent-color: #f59e0b;
        --success-color: #10b981;
        --danger-color: #ef4444;
        --warning-color: #f59e0b;

        /* Text colors */
        --text-primary: #0f172a;
        --text-secondary: #64748b;
        --text-muted: #94a3b8;

        /* Background colors */
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        --bg-accent: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

        /* Border and shadow */
        --border-color: #e2e8f0;
        --border-light: #f1f5f9;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 8px 25px -5px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

        /* Radius */
        --radius-sm: 0.375rem;
        --radius: 0.5rem;
        --radius-md: 0.75rem;
        --radius-lg: 1rem;
        --radius-xl: 1.5rem;

        /* Spacing */
        --space-xs: 0.25rem;
        --space-sm: 0.5rem;
        --space: 1rem;
        --space-lg: 1.5rem;
        --space-xl: 2rem;
        --space-2xl: 3rem;
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, sans-serif;
        line-height: 1.7;
        color: var(--text-primary);
        background-color: var(--bg-secondary);
        font-size: 0.95rem;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: var(--space-lg);
    }

    .container-sm {
        max-width: 768px;
        margin: 0 auto;
        padding: var(--space-lg);
    }

    .container-lg {
        max-width: 1400px;
        margin: 0 auto;
        padding: var(--space-lg);
    }

    .header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--border-light);
        padding: var(--space-lg) 0;
        margin-bottom: var(--space-xl);
        box-shadow: var(--shadow-sm);
        position: sticky;
        top: 0;
        z-index: 50;
    }

    .nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .logo {
        font-size: 1.75rem;
        font-weight: 800;
        background: var(--bg-accent);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-decoration: none;
        letter-spacing: -0.025em;
    }

    .nav-links {
        display: flex;
        gap: var(--space-xl);
        list-style: none;
        align-items: center;
    }

    .nav-links a {
        color: var(--text-secondary);
        text-decoration: none;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        position: relative;
        padding: var(--space-sm) var(--space);
        border-radius: var(--radius);
    }

    .nav-links a:hover {
        color: var(--primary-color);
        background: var(--bg-tertiary);
    }

    .nav-links a.active {
        color: var(--primary-color);
        background: var(--bg-tertiary);
        font-weight: 600;
    }

    .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-sm);
        padding: var(--space) var(--space-xl);
        border: none;
        border-radius: var(--radius-md);
        font-weight: 600;
        font-size: 0.9rem;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .btn-sm {
        padding: var(--space-sm) var(--space-lg);
        font-size: 0.875rem;
    }

    .btn-lg {
        padding: var(--space-lg) var(--space-2xl);
        font-size: 1rem;
    }

    .btn-primary {
        background: var(--primary-color);
        color: white;
        box-shadow: var(--shadow);
    }

    .btn-primary:hover {
        background: var(--primary-dark);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }

    .btn-primary:active {
        transform: translateY(0);
        box-shadow: var(--shadow);
    }

    .btn-secondary {
        background: var(--bg-primary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }

    .btn-secondary:hover {
        background: var(--bg-tertiary);
        border-color: var(--primary-color);
        color: var(--primary-color);
    }

    .btn-ghost {
        background: transparent;
        color: var(--text-secondary);
        border: 1px solid transparent;
    }

    .btn-ghost:hover {
        background: var(--bg-tertiary);
        color: var(--primary-color);
    }

    .card {
        background: var(--bg-primary);
        border-radius: var(--radius-lg);
        padding: var(--space-xl);
        box-shadow: var(--shadow);
        border: 1px solid var(--border-light);
        margin-bottom: var(--space-xl);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
        border-color: var(--border-color);
    }

    .card-header {
        margin-bottom: var(--space-lg);
        padding-bottom: var(--space-lg);
        border-bottom: 1px solid var(--border-light);
    }

    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--space-sm);
        line-height: 1.3;
    }

    .card-description {
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.6;
    }

    .card-compact {
        padding: var(--space-lg);
        margin-bottom: var(--space-lg);
    }

    .card-featured {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-tertiary) 100%);
        border: 2px solid var(--primary-light);
        position: relative;
    }

    .card-featured::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--bg-accent);
    }

    .grid {
        display: grid;
        gap: var(--space-xl);
    }

    .grid-2 {
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    }

    .grid-3 {
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }

    .grid-4 {
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    }

    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: var(--space-sm);
        padding: var(--space-sm) var(--space-lg);
        border-radius: var(--radius-xl);
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }

    .status-success {
        background: rgba(16, 185, 129, 0.1);
        color: #065f46;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }

    .status-warning {
        background: rgba(245, 158, 11, 0.1);
        color: #92400e;
        border: 1px solid rgba(245, 158, 11, 0.2);
    }

    .status-error {
        background: rgba(239, 68, 68, 0.1);
        color: #dc2626;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }

    .status-info {
        background: rgba(99, 102, 241, 0.1);
        color: var(--primary-dark);
        border: 1px solid rgba(99, 102, 241, 0.2);
    }

    .form-group {
        margin-bottom: var(--space-xl);
    }

    .form-label {
        display: block;
        margin-bottom: var(--space-sm);
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.9rem;
        letter-spacing: 0.025em;
    }

    .form-input,
    .form-textarea,
    .form-select {
        width: 100%;
        padding: var(--space) var(--space-lg);
        border: 2px solid var(--border-color);
        border-radius: var(--radius);
        font-size: 0.95rem;
        background: var(--bg-primary);
        color: var(--text-primary);
        transition: all 0.2s ease;
        font-family: inherit;
    }

    .form-input:focus,
    .form-textarea:focus,
    .form-select:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        background: var(--bg-primary);
    }

    .form-input::placeholder,
    .form-textarea::placeholder {
        color: var(--text-muted);
        font-size: 0.9rem;
    }

    .form-textarea {
        resize: vertical;
        min-height: 120px;
    }

    .form-select {
        cursor: pointer;
        background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6,9 12,15 18,9'%3e%3c/polyline%3e%3c/svg%3e");
        background-repeat: no-repeat;
        background-position: right var(--space) center;
        background-size: 16px;
        appearance: none;
        padding-right: var(--space-2xl);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        background: var(--bg-primary);
        font-size: 1rem;
    }

    .alert {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid;
    }

    .alert-success {
        background: #dcfce7;
        border-color: #bbf7d0;
        color: #166534;
    }

    .alert-warning {
        background: #fef3c7;
        border-color: #fde68a;
        color: #92400e;
    }

    .alert-error {
        background: #fee2e2;
        border-color: #fecaca;
        color: #dc2626;
    }

    .speech-controls {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.5rem;
        background: var(--bg-primary);
        border-radius: 0.75rem;
        border: 1px solid var(--border-color);
        margin-bottom: 2rem;
    }

    .mic-button {
        position: relative;
        width: 4rem;
        height: 4rem;
        border-radius: 50%;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        transition: all 0.3s ease;
    }

    .mic-button.inactive {
        background: var(--border-color);
        color: var(--text-secondary);
    }

    .mic-button.active {
        background: var(--danger-color);
        color: white;
        animation: pulse 1.5s ease-in-out infinite;
    }

    @keyframes pulse {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            transform: scale(1);
        }
    }

    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid var(--border-color);
        border-radius: 0.75rem;
        background: var(--bg-primary);
        margin-bottom: 1rem;
    }

    .message {
        margin-bottom: 1rem;
        padding: 1rem;
        border-radius: 0.75rem;
        max-width: 80%;
    }

    .message.user {
        background: var(--primary-color);
        color: white;
        margin-left: auto;
    }

    .message.assistant {
        background: var(--bg-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }

    .message-content {
        margin-bottom: 0.5rem;
    }

    .message-time {
        font-size: 0.75rem;
        opacity: 0.7;
    }

    .loading-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem;
        background: var(--bg-secondary);
        border-radius: 0.75rem;
        border: 1px solid var(--border-color);
        max-width: 80%;
    }

    .loading-dots {
        display: flex;
        gap: 0.25rem;
    }

    .loading-dot {
        width: 0.5rem;
        height: 0.5rem;
        border-radius: 50%;
        background: var(--text-secondary);
        animation: loading 1.4s ease-in-out infinite both;
    }

    .loading-dot:nth-child(1) { animation-delay: -0.32s; }
    .loading-dot:nth-child(2) { animation-delay: -0.16s; }

    @keyframes loading {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .container {
            padding: 0.5rem;
        }

        .nav {
            flex-direction: column;
            gap: 1rem;
        }

        .nav-links {
            gap: 1rem;
        }

        .card {
            padding: 1rem;
        }

        .grid-2,
        .grid-3 {
            grid-template-columns: 1fr;
        }

        .message {
            max-width: 95%;
        }

        .speech-controls {
            flex-wrap: wrap;
        }
    }

    /* Typography System */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: var(--space-lg);
        letter-spacing: -0.025em;
    }

    h1 {
        font-size: 2.5rem;
        font-weight: 800;
        background: var(--bg-accent);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    h2 {
        font-size: 2rem;
    }

    h3 {
        font-size: 1.5rem;
    }

    h4 {
        font-size: 1.25rem;
    }

    p {
        margin-bottom: var(--space-lg);
        line-height: 1.7;
        color: var(--text-secondary);
    }

    /* Modern Utility Classes */
    .flex {
        display: flex;
    }

    .flex-col {
        flex-direction: column;
    }

    .items-center {
        align-items: center;
    }

    .justify-between {
        justify-content: space-between;
    }

    .gap-sm {
        gap: var(--space-sm);
    }

    .gap-lg {
        gap: var(--space-lg);
    }

    .text-center {
        text-align: center;
    }

    .rounded-lg {
        border-radius: var(--radius-lg);
    }

    /* Loading States */
    .loading {
        opacity: 0.6;
        pointer-events: none;
        position: relative;
    }

    .loading::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        margin: -10px 0 0 -10px;
        border: 2px solid var(--border-color);
        border-top-color: var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    /* Enhanced Responsive Design */
    @media (max-width: 768px) {
        .container {
            padding: var(--space);
        }

        .nav-links {
            gap: var(--space);
        }

        .grid-2,
        .grid-3,
        .grid-4 {
            grid-template-columns: 1fr;
        }

        .card {
            padding: var(--space-lg);
        }

        h1 {
            font-size: 2rem;
        }

        h2 {
            font-size: 1.75rem;
        }

        .btn {
            padding: var(--space-sm) var(--space-lg);
            font-size: 0.875rem;
        }
    }

    @media (max-width: 480px) {
        .container {
            padding: var(--space-sm);
        }

        .nav {
            flex-direction: column;
            gap: var(--space);
        }

        .card {
            padding: var(--space);
        }

        h1 {
            font-size: 1.75rem;
        }
    }

    /* Modal Styles */
    .modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
    }

    .modal-dialog {
        background: var(--bg-primary);
        border-radius: var(--radius);
        box-shadow: var(--shadow-lg);
        max-width: 600px;
        width: 100%;
        max-height: 80vh;
        overflow-y: auto;
    }

    .modal-content {
        padding: 2rem;
    }

    /* Scenario-specific styles */
    .scenario-info {
        line-height: 1.6;
    }

    .scenario-info h4 {
        color: var(--primary-color);
        margin-bottom: 1rem;
    }

    .scenario-info h5 {
        color: var(--text-primary);
        margin: 1.5rem 0 0.5rem 0;
        font-size: 1rem;
        font-weight: 600;
    }

    .scenario-info p {
        margin-bottom: 0.75rem;
    }

    .scenario-info ul, .scenario-info ol {
        margin-bottom: 1rem;
        padding-left: 1.5rem;
    }

    .scenario-info li {
        margin-bottom: 0.5rem;
    }

    .vocabulary-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    .vocab-tag {
        display: inline-block;
        background: var(--primary-light);
        color: var(--primary-dark);
        padding: 0.25rem 0.75rem;
        border-radius: var(--radius-sm);
        font-size: 0.875rem;
        font-weight: 500;
    }

    /* Scenario progress indicators */
    .scenario-progress {
        background: var(--bg-secondary);
        padding: 1rem;
        border-radius: var(--radius);
        margin: 1rem 0;
        border-left: 4px solid var(--primary-color);
    }

    .scenario-progress h4 {
        margin: 0 0 0.5rem 0;
        color: var(--primary-color);
        font-size: 1rem;
    }

    .scenario-progress p {
        margin: 0;
        color: var(--text-secondary);
        font-size: 0.875rem;
    }

    .phase-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }

    .phase-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--border-color);
    }

    .phase-dot.active {
        background: var(--primary-color);
    }

    .phase-dot.completed {
        background: var(--success-color);
    }

    /* Enhanced conversation area for scenarios */
    .conversation-area {
        position: relative;
    }

    .scenario-context {
        background: linear-gradient(135deg, var(--primary-light), var(--secondary-color));
        color: white;
        padding: 1rem;
        border-radius: var(--radius);
        margin-bottom: 1rem;
        text-align: center;
    }

    .scenario-context h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
    }

    .scenario-context p {
        margin: 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }

    /* Message enhancements for scenarios */
    .message.scenario-feedback {
        background: var(--bg-tertiary);
        border-left: 4px solid var(--accent-color);
        color: var(--text-primary);
        font-style: italic;
    }

    .message.phase-transition {
        background: linear-gradient(135deg, var(--success-color), var(--primary-color));
        color: white;
        text-align: center;
        font-weight: 600;
    }

    /* Responsive modal */
    @media (max-width: 640px) {
        .modal {
            padding: 0.5rem;
        }

        .modal-dialog {
            max-height: 90vh;
        }

        .modal-content {
            padding: 1rem;
        }

        .vocabulary-tags {
            gap: 0.25rem;
        }

        .vocab-tag {
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
        }
    }
    """)


# Additional utility functions for styling
def get_status_class(status: str) -> str:
    """Get appropriate CSS class for status indicators"""
    status_map = {
        "success": "status-success",
        "warning": "status-warning",
        "error": "status-error",
        "connected": "status-success",
        "disconnected": "status-error",
        "ready": "status-success",
        "loading": "status-warning",
    }
    return status_map.get(status.lower(), "status-warning")


def get_alert_class(alert_type: str) -> str:
    """Get appropriate CSS class for alert messages"""
    alert_map = {
        "success": "alert-success",
        "warning": "alert-warning",
        "error": "alert-error",
        "info": "alert-warning",
    }
    return alert_map.get(alert_type.lower(), "alert-warning")
