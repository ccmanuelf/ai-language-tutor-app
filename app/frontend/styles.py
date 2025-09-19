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
    /* AI Language Tutor - Modern UI Styles */
    :root {
        --primary-color: #2563eb;
        --primary-dark: #1d4ed8;
        --secondary-color: #10b981;
        --accent-color: #f59e0b;
        --danger-color: #ef4444;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --border-color: #e5e7eb;
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.6;
        color: var(--text-primary);
        background-color: var(--bg-secondary);
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem;
    }

    .header {
        background: var(--bg-primary);
        border-bottom: 1px solid var(--border-color);
        padding: 1rem 0;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
    }

    .nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .logo {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-color);
        text-decoration: none;
    }

    .nav-links {
        display: flex;
        gap: 2rem;
        list-style: none;
    }

    .nav-links a {
        color: var(--text-secondary);
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s;
    }

    .nav-links a:hover {
        color: var(--primary-color);
    }

    .btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: 0.5rem;
        font-weight: 500;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: var(--shadow);
    }

    .btn-primary {
        background: var(--primary-color);
        color: white;
    }

    .btn-primary:hover {
        background: var(--primary-dark);
        box-shadow: var(--shadow-lg);
    }

    .btn-secondary {
        background: var(--bg-primary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }

    .btn-secondary:hover {
        background: var(--bg-secondary);
    }

    .card {
        background: var(--bg-primary);
        border-radius: 0.75rem;
        padding: 2rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        margin-bottom: 2rem;
    }

    .grid {
        display: grid;
        gap: 2rem;
    }

    .grid-2 {
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }

    .grid-3 {
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    }

    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .status-success {
        background: #dcfce7;
        color: #166534;
    }

    .status-warning {
        background: #fef3c7;
        color: #92400e;
    }

    .status-error {
        background: #fee2e2;
        color: #dc2626;
    }

    .form-group {
        margin-bottom: 1.5rem;
    }

    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: var(--text-primary);
    }

    .form-input {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        font-size: 1rem;
        transition: border-color 0.2s;
    }

    .form-input:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }

    .form-select {
        width: 100%;
        padding: 0.75rem;
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
