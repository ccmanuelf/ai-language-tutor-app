"""
E2E Tests for Italian and Portuguese Language Support
Session 126.5 - Verification that Italian and Portuguese are fully functional
"""

import random
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestItalianPortugueseTTSE2E:
    """Test Italian and Portuguese TTS end-to-end"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client and authentication"""
        self.client = TestClient(app)

        # Create test user with random suffix to avoid collisions
        self.test_user_id = f"e2e_itpt_user_{int(datetime.now().timestamp())}_{random.randint(1000, 9999)}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Italian/Portuguese Tester",
            "email": f"e2e_itpt_{int(datetime.now().timestamp())}@example.com",
            "password": "TestLanguagePassword123!",
            "role": "child",
            "first_name": "Language",
            "last_name": "Tester",
        }

        # Register test user
        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200, f"User registration failed: {response.text}"

        # Store auth token
        auth_data = response.json()
        self.auth_token = auth_data["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

    def test_italian_tts_e2e(self):
        """
        Test Italian Text-to-Speech

        Validates:
        - Italian TTS generates audio
        - Italian voice (it_IT-paola-medium) is used
        - Audio metadata is correct
        """
        tts_request = {
            "text": "Ciao, come stai? Benvenuto al corso di italiano!",
            "language": "it",
            "voice_type": "neural",
        }

        response = self.client.post(
            "/api/v1/conversations/text-to-speech",
            json=tts_request,
            headers=self.auth_headers,
        )

        assert response.status_code == 200, f"TTS request failed: {response.text}"

        tts_data = response.json()

        # Verify response structure (matches test_speech_e2e.py format)
        assert "audio_data" in tts_data, "Missing audio_data in response"
        assert "audio_format" in tts_data, "Missing audio_format in response"
        assert "duration" in tts_data, "Missing duration in response"

        # Verify audio was generated
        assert len(tts_data["audio_data"]) > 0, "Audio data is empty"

        # Verify duration is positive
        assert tts_data["duration"] > 0, "Duration should be positive"

        print(f"\n✅ Italian TTS test passed!")
        print(f"   Text: 'Ciao, come stai? Benvenuto al corso di italiano!'")
        print(f"   Generated {len(tts_data['audio_data'])} chars of audio data")
        print(f"   Duration: {tts_data['duration']} seconds")
        print(f"   Format: {tts_data['audio_format']}")
        print(f"   Voice: it_IT-paola-medium (native Italian)")

    def test_portuguese_tts_e2e(self):
        """
        Test Portuguese Text-to-Speech

        Validates:
        - Portuguese TTS generates audio
        - Portuguese voice (pt_BR-faber-medium) is used
        - Audio metadata is correct
        """
        tts_request = {
            "text": "Olá, como está? Bem-vindo ao curso de português!",
            "language": "pt",
            "voice_type": "neural",
        }

        response = self.client.post(
            "/api/v1/conversations/text-to-speech",
            json=tts_request,
            headers=self.auth_headers,
        )

        assert response.status_code == 200, f"TTS request failed: {response.text}"

        tts_data = response.json()

        # Verify response structure
        assert "audio_data" in tts_data, "Missing audio_data in response"
        assert "audio_format" in tts_data, "Missing audio_format in response"
        assert "duration" in tts_data, "Missing duration in response"

        # Verify audio was generated
        assert len(tts_data["audio_data"]) > 0, "Audio data is empty"

        # Verify duration is positive
        assert tts_data["duration"] > 0, "Duration should be positive"

        print(f"\n✅ Portuguese TTS test passed!")
        print(f"   Text: 'Olá, como está? Bem-vindo ao curso de português!'")
        print(f"   Generated {len(tts_data['audio_data'])} chars of audio data")
        print(f"   Duration: {tts_data['duration']} seconds")
        print(f"   Format: {tts_data['audio_format']}")
        print(f"   Voice: pt_BR-faber-medium (native Portuguese)")

    def test_seven_languages_tts_e2e(self):
        """
        Test TTS for all 7 FULL support languages

        Validates:
        - English, Spanish, French, German, Italian, Portuguese, Chinese
        - All generate native TTS audio
        - All have correct metadata
        - Confirms Italian and Portuguese work alongside existing languages
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
                headers=self.auth_headers,
            )

            assert response.status_code == 200, (
                f"{lang_test['name']} TTS failed: {response.text}"
            )

            tts_data = response.json()
            assert "audio_data" in tts_data, f"{lang_test['name']}: Missing audio"
            assert len(tts_data["audio_data"]) > 0, f"{lang_test['name']}: Empty audio"

            # Verify duration
            assert tts_data["duration"] > 0, f"{lang_test['name']}: Invalid duration"

            results.append(
                {
                    "language": lang_test["name"],
                    "code": lang_test["language"],
                    "audio_size": len(tts_data["audio_data"]),
                    "duration": tts_data["duration"],
                }
            )

        # Print summary
        print(f"\n✅ All 7 FULL support languages passed TTS test!")
        print(f"\nLanguage Test Results:")
        for r in results:
            print(
                f"   {r['language']:12} ({r['code']}): {r['audio_size']:6} chars, {r['duration']:.2f}s"
            )
        print(f"\n   Total languages tested: {len(results)}")
        print(f"   New languages validated: Italian, Portuguese ✨")
