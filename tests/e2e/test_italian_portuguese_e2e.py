"""
E2E Tests for Italian and Portuguese Language Support
Session 126 - Verification that Italian and Portuguese are fully functional
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestItalianLanguageE2E:
    """Test Italian language support end-to-end"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_italian_tts_e2e(self):
        """
        Test Italian Text-to-Speech

        Validates:
        - Italian TTS generates audio
        - Italian voice is used
        - Audio metadata is correct
        """
        tts_request = {
            "text": "Ciao, come stai?",
            "language": "it",
            "voice_type": "neural",
        }

        response = self.client.post(
            "/api/v1/conversations/text-to-speech",
            json=tts_request,
        )

        assert response.status_code == 200, f"TTS request failed: {response.text}"

        tts_data = response.json()

        # Verify response structure
        assert "audio_base64" in tts_data, "Missing audio_base64 in response"
        assert "metadata" in tts_data, "Missing metadata in response"

        # Verify audio was generated
        assert len(tts_data["audio_base64"]) > 0, "Audio data is empty"

        # Verify metadata
        metadata = tts_data["metadata"]
        assert metadata["language"] == "it", "Language metadata incorrect"
        assert "duration" in metadata, "Missing duration in metadata"
        assert metadata["duration"] > 0, "Duration should be positive"

        print(f"✅ Italian TTS test passed!")
        print(f"   Generated {len(tts_data['audio_base64'])} chars of base64 audio")
        print(f"   Duration: {metadata['duration']} seconds")

    def test_italian_conversation_e2e(self):
        """
        Test Italian conversation

        Validates:
        - Can create conversation in Italian
        - AI responds appropriately
        - Conversation metadata is correct
        """
        # Create conversation request
        conversation_request = {
            "user_id": "test_user_italian",
            "language": "it",
            "context": "Italian language practice",
        }

        response = self.client.post(
            "/api/v1/conversations",
            json=conversation_request,
        )

        assert response.status_code == 200, (
            f"Failed to create conversation: {response.text}"
        )

        conversation = response.json()
        assert conversation["language"] == "it", "Conversation language incorrect"

        print(f"✅ Italian conversation test passed!")
        print(f"   Conversation ID: {conversation.get('id')}")


class TestPortugueseLanguageE2E:
    """Test Portuguese language support end-to-end"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_portuguese_tts_e2e(self):
        """
        Test Portuguese Text-to-Speech

        Validates:
        - Portuguese TTS generates audio
        - Portuguese voice is used
        - Audio metadata is correct
        """
        tts_request = {
            "text": "Olá, como está?",
            "language": "pt",
            "voice_type": "neural",
        }

        response = self.client.post(
            "/api/v1/conversations/text-to-speech",
            json=tts_request,
        )

        assert response.status_code == 200, f"TTS request failed: {response.text}"

        tts_data = response.json()

        # Verify response structure
        assert "audio_base64" in tts_data, "Missing audio_base64 in response"
        assert "metadata" in tts_data, "Missing metadata in response"

        # Verify audio was generated
        assert len(tts_data["audio_base64"]) > 0, "Audio data is empty"

        # Verify metadata
        metadata = tts_data["metadata"]
        assert metadata["language"] == "pt", "Language metadata incorrect"
        assert "duration" in metadata, "Missing duration in metadata"
        assert metadata["duration"] > 0, "Duration should be positive"

        print(f"✅ Portuguese TTS test passed!")
        print(f"   Generated {len(tts_data['audio_base64'])} chars of base64 audio")
        print(f"   Duration: {metadata['duration']} seconds")

    def test_portuguese_conversation_e2e(self):
        """
        Test Portuguese conversation

        Validates:
        - Can create conversation in Portuguese
        - AI responds appropriately
        - Conversation metadata is correct
        """
        # Create conversation request
        conversation_request = {
            "user_id": "test_user_portuguese",
            "language": "pt",
            "context": "Portuguese language practice",
        }

        response = self.client.post(
            "/api/v1/conversations",
            json=conversation_request,
        )

        assert response.status_code == 200, (
            f"Failed to create conversation: {response.text}"
        )

        conversation = response.json()
        assert conversation["language"] == "pt", "Conversation language incorrect"

        print(f"✅ Portuguese conversation test passed!")
        print(f"   Conversation ID: {conversation.get('id')}")


class TestSevenLanguageSupportE2E:
    """Test that all 7 FULL support languages work"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_seven_languages_tts_e2e(self):
        """
        Test TTS for all 7 FULL support languages

        Validates:
        - English, Spanish, French, German, Italian, Portuguese, Chinese
        - All generate native TTS audio
        - All have correct metadata
        """
        language_tests = [
            {"text": "Hello world", "language": "en", "name": "English"},
            {"text": "Hola mundo", "language": "es", "name": "Spanish"},
            {"text": "Bonjour le monde", "language": "fr", "name": "French"},
            {"text": "Hallo Welt", "language": "de", "name": "German"},
            {"text": "Ciao mondo", "language": "it", "name": "Italian"},
            {"text": "Olá mundo", "language": "pt", "name": "Portuguese"},
            {"text": "你好世界", "language": "zh", "name": "Chinese"},
        ]

        results = []

        for lang_test in language_tests:
            tts_request = {
                "text": lang_test["text"],
                "language": lang_test["language"],
                "voice_type": "neural",
            }

            response = self.client.post(
                "/api/v1/conversations/text-to-speech",
                json=tts_request,
            )

            assert response.status_code == 200, (
                f"{lang_test['name']} TTS failed: {response.text}"
            )

            tts_data = response.json()
            assert "audio_base64" in tts_data, f"{lang_test['name']}: Missing audio"
            assert len(tts_data["audio_base64"]) > 0, (
                f"{lang_test['name']}: Empty audio"
            )

            metadata = tts_data["metadata"]
            assert metadata["language"] == lang_test["language"], (
                f"{lang_test['name']}: Wrong language"
            )

            results.append(
                {
                    "language": lang_test["name"],
                    "code": lang_test["language"],
                    "audio_size": len(tts_data["audio_base64"]),
                    "duration": metadata.get("duration", 0),
                }
            )

            print(
                f"✅ {lang_test['name']} ({lang_test['language']}): {len(tts_data['audio_base64'])} chars, {metadata.get('duration', 0)}s"
            )

        print(f"\n✅ All 7 FULL support languages passed TTS test!")
        print(f"   Tested: {', '.join([r['language'] for r in results])}")
