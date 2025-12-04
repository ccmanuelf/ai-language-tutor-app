"""
API Key Validation Utility for AI Language Tutor App
Session 82 - Removed deprecated Watson references

This utility helps validate API keys for all integrated services:
- Anthropic Claude
- Mistral AI
- Qwen

Current TTS/STT: Piper TTS (local, offline, no API key required)

Usage:
    python -m app.utils.api_key_validator

Security:
- Never logs actual API keys
- Only validates connectivity and permissions
- Reports validation results safely
"""

import asyncio
import logging
import os
from typing import Any, Dict

from dotenv import load_dotenv

# Suppress HTTP request logs for cleaner output
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("anthropic").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class APIKeyValidator:
    """Validates API keys for all integrated services"""

    def __init__(self):
        load_dotenv()
        self.results = {}

    async def validate_anthropic_api(self) -> Dict[str, Any]:
        """Validate Anthropic Claude API key"""
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key or api_key == "your_anthropic_api_key_here":
                return {
                    "status": "not_configured",
                    "message": "API key not provided",
                    "service": "Anthropic Claude",
                }

            # Test with minimal request
            from anthropic import Anthropic

            client = Anthropic(api_key=api_key)

            # Simple test message
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )

            return {
                "status": "valid",
                "message": "API key is valid and working",
                "service": "Anthropic Claude",
                "model": "claude-3-haiku-20240307",
                "test_response_length": len(response.content[0].text),
            }

        except Exception as e:
            error_msg = str(e)
            # Don't expose the actual API key in error messages
            if "api_key" in error_msg.lower():
                error_msg = "Authentication failed - check API key"

            return {
                "status": "invalid",
                "message": f"Validation failed: {error_msg}",
                "service": "Anthropic Claude",
            }

    async def validate_mistral_api(self) -> Dict[str, Any]:
        """Validate Mistral AI API key"""
        try:
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key or api_key == "your_mistral_api_key_here":
                return {
                    "status": "not_configured",
                    "message": "API key not provided",
                    "service": "Mistral AI",
                }

            from mistralai.client import MistralClient

            client = MistralClient(api_key=api_key)

            # Test with minimal request
            response = client.chat(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10,
            )

            return {
                "status": "valid",
                "message": "API key is valid and working",
                "service": "Mistral AI",
                "model": "mistral-small-latest",
                "test_response_length": len(response.choices[0].message.content),
            }

        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                error_msg = "Authentication failed - check API key"

            return {
                "status": "invalid",
                "message": f"Validation failed: {error_msg}",
                "service": "Mistral AI",
            }

    async def validate_qwen_api(self) -> Dict[str, Any]:
        """Validate Qwen API key"""
        try:
            api_key = os.getenv("QWEN_API_KEY")
            if not api_key or api_key == "your_qwen_api_key_here":
                return {
                    "status": "not_configured",
                    "message": "API key not provided",
                    "service": "Qwen (Alibaba Cloud)",
                }

            # For Qwen, we'll implement a basic HTTP test
            import httpx

            _headers = {  # noqa: F841 - Intentional placeholder
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            # Test endpoint (this is a simplified test)
            async with httpx.AsyncClient() as _client:  # noqa: F841 - Intentional placeholder
                # Note: This is a placeholder - actual Qwen API validation
                # would require specific endpoint and format
                return {
                    "status": "configured",
                    "message": "API key configured (validation requires specific endpoint setup)",
                    "service": "Qwen (Alibaba Cloud)",
                    "note": "Full validation will be implemented with service integration",
                }

        except Exception as e:
            return {
                "status": "invalid",
                "message": f"Validation failed: {str(e)}",
                "service": "Qwen (Alibaba Cloud)",
            }

    async def validate_all_apis(self) -> Dict[str, Dict[str, Any]]:
        """Validate all API keys"""
        print("🔍 Validating API Keys for AI Language Tutor App...")
        print("=" * 60)

        validators = [
            ("anthropic", self.validate_anthropic_api),
            ("mistral", self.validate_mistral_api),
            ("qwen", self.validate_qwen_api),
        ]

        results = {}

        for service_name, validator in validators:
            print(f"🔍 Testing {service_name}...")
            try:
                result = await validator()
                results[service_name] = result

                status_emoji = {
                    "valid": "✅",
                    "configured": "🟡",
                    "not_configured": "⚪",
                    "misconfigured": "🟠",
                    "invalid": "❌",
                }.get(result["status"], "❓")

                print(f"{status_emoji} {result['service']}: {result['message']}")

            except Exception as e:
                results[service_name] = {
                    "status": "error",
                    "message": f"Validation error: {str(e)}",
                    "service": service_name,
                }
                print(f"❌ {service_name}: Validation error")

        print("=" * 60)
        self._print_summary(results)
        return results

    def _calculate_validation_stats(
        self, results: Dict[str, Dict[str, Any]]
    ) -> tuple[int, int, int]:
        """Calculate validation statistics"""
        valid_count = sum(1 for r in results.values() if r["status"] == "valid")
        configured_count = sum(
            1 for r in results.values() if r["status"] in ["valid", "configured"]
        )
        total_count = len(results)
        return valid_count, configured_count, total_count

    def _print_validation_counts(
        self, valid_count: int, configured_count: int, total_count: int
    ):
        """Print validation count summary"""
        print("📊 VALIDATION SUMMARY")
        print(f"✅ Fully Working: {valid_count}/{total_count}")
        print(f"🟡 Configured: {configured_count}/{total_count}")
        print(f"⚪ Not Configured: {total_count - configured_count}/{total_count}")

    def _print_status_message(
        self, valid_count: int, configured_count: int, total_count: int
    ):
        """Print overall status message"""
        if valid_count == total_count:
            print("🎉 ALL SERVICES READY - Your AI Language Tutor is fully configured!")
        elif configured_count > 0:
            print("🚀 PARTIAL SETUP - Some services are ready, others need API keys")
        else:
            print("📝 SETUP NEEDED - Please provide API keys to continue")

    def _print_next_steps(self, results: Dict[str, Dict[str, Any]]):
        """Print next steps guidance"""
        print("\n💡 Next Steps:")
        not_configured = [
            r for r in results.values() if r["status"] == "not_configured"
        ]
        if not_configured:
            print(
                "   1. Get API keys for:",
                ", ".join([r["service"] for r in not_configured]),
            )
            print("   2. Add them to your .env file")
            print("   3. Run this validator again")
        else:
            print("   1. All APIs configured! Ready to proceed with development")

        print("\n📝 Note: TTS/STT now uses Piper (local, offline, no API key required)")

    def _print_summary(self, results: Dict[str, Dict[str, Any]]):
        """Print validation summary"""
        valid_count, configured_count, total_count = self._calculate_validation_stats(
            results
        )

        self._print_validation_counts(valid_count, configured_count, total_count)
        self._print_status_message(valid_count, configured_count, total_count)
        self._print_next_steps(results)

    def get_validation_status(self) -> str:
        """Get overall validation status"""
        if not self.results:
            return "not_tested"

        valid_count = sum(1 for r in self.results.values() if r["status"] == "valid")
        total_count = len(self.results)

        if valid_count == total_count:
            return "all_valid"
        elif valid_count > 0:
            return "partial_valid"
        else:
            return "none_valid"


async def main():
    """Main validation function"""
    validator = APIKeyValidator()
    results = await validator.validate_all_apis()
    return results


if __name__ == "__main__":
    # Run the validation
    asyncio.run(main())
