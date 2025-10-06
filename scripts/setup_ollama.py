#!/usr/bin/env python3
"""
Ollama Setup Script for AI Language Tutor App

This script helps set up Ollama for local LLM fallback functionality.
It handles installation verification, model downloads, and configuration.

Usage:
    python scripts/setup_ollama.py [command]

Commands:
    check       - Check Ollama installation status
    install     - Guide through Ollama installation
    setup       - Download recommended models for language learning
    test        - Test Ollama functionality
    status      - Show current status and models
"""

import asyncio
import sys
import platform
import subprocess
from pathlib import Path
from typing import Dict, Any

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.ollama_service import ollama_manager, ollama_service


class OllamaSetupScript:
    """Ollama setup and management script"""

    def __init__(self):
        self.system = platform.system().lower()
        self.architecture = platform.machine().lower()

    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"🤖 {title}")
        print("=" * 60)

    def print_step(self, step: str, status: str = ""):
        """Print formatted step"""
        status_emoji = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "pending": "⏳"
        }
        emoji = status_emoji.get(status, "📋")
        print(f"{emoji} {step}")

    async def check_ollama_installation(self) -> Dict[str, Any]:
        """Check if Ollama is installed and running"""
        self.print_header("Checking Ollama Installation")

        # Check if ollama command exists
        try:
            result = subprocess.run(["ollama", "--version"],
                                  capture_output=True, text=True, timeout=10)
            ollama_installed = result.returncode == 0
            version = result.stdout.strip() if ollama_installed else None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            ollama_installed = False
            version = None

        # Check if server is running
        server_running = await ollama_service.check_availability()

        # Get installation status
        install_status = await ollama_manager.check_installation()

        status = {
            "ollama_installed": ollama_installed,
            "version": version,
            "server_running": server_running,
            "models_installed": install_status.get("models", 0),
            "setup_required": install_status.get("setup_required", True)
        }

        # Print status
        self.print_step(f"Ollama CLI installed: {version if version else 'Not found'}",
                       "success" if ollama_installed else "error")
        self.print_step(f"Ollama server running: {server_running}",
                       "success" if server_running else "warning")
        self.print_step(f"Models installed: {status['models_installed']}",
                       "success" if status['models_installed'] > 0 else "warning")

        return status

    def print_installation_guide(self):
        """Print OS-specific installation guide"""
        self.print_header("Ollama Installation Guide")

        if self.system == "darwin":  # macOS
            self.print_step("macOS Installation Options:", "info")
            print("   Option 1 - Download installer:")
            print("     1. Visit https://ollama.ai/download")
            print("     2. Download 'Download for macOS'")
            print("     3. Run the installer")
            print("   Option 2 - Using Homebrew:")
            print("     brew install ollama")

        elif self.system == "linux":
            self.print_step("Linux Installation:", "info")
            print("   Install with curl:")
            print("     curl -fsSL https://ollama.ai/install.sh | sh")
            print("   Or download from https://ollama.ai/download")

        elif self.system == "windows":
            self.print_step("Windows Installation:", "info")
            print("   1. Visit https://ollama.ai/download")
            print("   2. Download 'Download for Windows'")
            print("   3. Run the installer")
            print("   4. Restart your terminal/IDE")

        print("\n📖 After installation:")
        print("   1. Start Ollama: 'ollama serve'")
        print("   2. Run this script again: 'python scripts/setup_ollama.py check'")

    async def setup_language_learning_models(self) -> Dict[str, Any]:
        """Setup recommended models for language learning"""
        self.print_header("Setting Up Language Learning Models")

        if not await ollama_service.check_availability():
            self.print_step("Ollama server not running!", "error")
            print("Please start Ollama server first: 'ollama serve'")
            return {"success": False}

        # Check available system memory
        self.print_step("Checking system requirements...", "pending")

        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            self.print_step(f"Available RAM: {memory_gb:.1f} GB", "info")
        except ImportError:
            memory_gb = 8  # Assume 8GB if psutil not available
            self.print_step("RAM check skipped (install psutil for memory detection)", "warning")

        # Recommend models based on available memory
        recommended_models = []

        if memory_gb >= 4:
            recommended_models.append({
                "name": "llama2:7b",
                "size": "3.8GB",
                "purpose": "General conversations, English learning",
                "priority": "essential"
            })

        if memory_gb >= 6:
            recommended_models.append({
                "name": "mistral:7b",
                "size": "4.1GB",
                "purpose": "French language optimization",
                "priority": "recommended"
            })

        if memory_gb >= 8:
            recommended_models.append({
                "name": "neural-chat:7b",
                "size": "3.8GB",
                "purpose": "Conversational practice",
                "priority": "recommended"
            })

        if memory_gb >= 12:
            recommended_models.append({
                "name": "llama2:13b",
                "size": "7.3GB",
                "purpose": "Advanced grammar correction",
                "priority": "optional"
            })

        if not recommended_models:
            self.print_step("Insufficient RAM for local models (need at least 4GB)", "error")
            return {"success": False, "reason": "insufficient_memory"}

        # Show recommendations
        print("📦 Recommended models for your system:")
        for model in recommended_models:
            priority_emoji = {"essential": "🔥", "recommended": "⭐", "optional": "💡"}
            emoji = priority_emoji.get(model["priority"], "📦")
            print(f"   {emoji} {model['name']} ({model['size']}) - {model['purpose']}")

        # Ask for confirmation
        print(f"\n⚠️  This will download ~{sum(float(m['size'].replace('GB', '')) for m in recommended_models):.1f}GB of models")
        response = input("Continue with model setup? (y/N): ").strip().lower()

        if response not in ['y', 'yes']:
            print("Setup cancelled by user")
            return {"success": False, "reason": "user_cancelled"}

        # Download models
        self.print_step("Downloading language learning models...", "pending")
        setup_result = await ollama_manager.setup_for_language_learning()

        if setup_result["success"]:
            self.print_step(f"Successfully set up {len(setup_result['models_setup'])} models", "success")
            for model in setup_result['models_setup']:
                self.print_step(f"✓ {model}", "success")
        else:
            self.print_step("Model setup failed", "error")
            print(f"Error: {setup_result.get('message', 'Unknown error')}")

        return setup_result

    async def test_ollama_functionality(self) -> Dict[str, Any]:
        """Test Ollama functionality with a simple conversation"""
        self.print_header("Testing Ollama Functionality")

        if not await ollama_service.check_availability():
            self.print_step("Ollama server not available", "error")
            return {"success": False}

        # List available models
        models = await ollama_service.list_models()
        if not models:
            self.print_step("No models available for testing", "error")
            print("Please run: python scripts/setup_ollama.py setup")
            return {"success": False}

        self.print_step(f"Found {len(models)} installed models", "success")

        # Test with a simple conversation
        test_model = models[0]["name"]
        self.print_step(f"Testing with model: {test_model}", "pending")

        try:
            messages = [
                {"role": "user", "content": "Hello! Can you help me learn English?"}
            ]

            response = await ollama_service.generate_response(
                messages=messages,
                language="en",
                model=test_model
            )

            self.print_step("Test conversation successful!", "success")
            print(f"   Model: {response.model}")
            print(f"   Response time: {response.processing_time:.2f}s")
            print(f"   Response preview: {response.content[:100]}...")

            return {
                "success": True,
                "model": response.model,
                "response_time": response.processing_time,
                "cost": response.cost
            }

        except Exception as e:
            self.print_step(f"Test failed: {str(e)}", "error")
            return {"success": False, "error": str(e)}

    async def show_status(self) -> Dict[str, Any]:
        """Show comprehensive Ollama status"""
        self.print_header("Ollama Status Report")

        # Installation check
        install_status = await self.check_ollama_installation()

        if not install_status["server_running"]:
            self.print_step("Server not running - limited information available", "warning")
            return install_status

        # Service health
        health = await ollama_service.get_health_status()

        if health["status"] == "healthy":
            self.print_step("Service health: Healthy", "success")
            print(f"   Server URL: {health['server_url']}")
            print(f"   Models installed: {health['models_installed']}")
            print(f"   Privacy: {health['privacy']}")

            # List models with details
            if health["available_models"]:
                print("\n📦 Installed Models:")
                for model in health["available_models"]:
                    model_info = ollama_service.available_models.get(model, {})
                    if hasattr(model_info, 'description'):
                        print(f"   ✓ {model} - {model_info.description}")
                    else:
                        print(f"   ✓ {model}")

            # Show recommendations
            missing_models = set(health["recommended_models"]) - set(health["available_models"])
            if missing_models:
                print("\n💡 Recommended additional models:")
                for model in missing_models:
                    model_info = ollama_service.available_models.get(model, {})
                    if hasattr(model_info, 'description'):
                        print(f"   📦 {model} - {model_info.description}")
                    else:
                        print(f"   📦 {model}")
                print("   Run: python scripts/setup_ollama.py setup")

        return {**install_status, **health}

    async def run_command(self, command: str):
        """Run a specific command"""
        commands = {
            "check": self.check_ollama_installation,
            "install": lambda: self.print_installation_guide(),
            "setup": self.setup_language_learning_models,
            "test": self.test_ollama_functionality,
            "status": self.show_status
        }

        if command not in commands:
            print(f"❌ Unknown command: {command}")
            print(f"Available commands: {', '.join(commands.keys())}")
            return

        try:
            if asyncio.iscoroutinefunction(commands[command]):
                result = await commands[command]()
            else:
                result = commands[command]()

            return result

        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
        except Exception as e:
            print(f"❌ Error executing command '{command}': {str(e)}")


async def main():
    """Main script entry point"""
    script = OllamaSetupScript()

    # Parse command line arguments
    if len(sys.argv) < 2:
        command = "status"  # Default command
    else:
        command = sys.argv[1].lower()

    print("🤖 AI Language Tutor - Ollama Setup Script")
    print("Local LLM Fallback System")

    await script.run_command(command)

    # Cleanup
    await ollama_service.close()


if __name__ == "__main__":
    asyncio.run(main())
