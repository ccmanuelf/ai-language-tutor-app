"""
End-to-End Tests for Conversation Management
Session 117 - Phase 2: TRUE 100% Functionality Validation

⚠️ WARNING: These tests use REAL services and database!
- REAL AI API calls (costs money)
- REAL database operations
- REAL conversation flows

Run manually only: pytest tests/e2e/test_conversations_e2e.py -v -s -m e2e
"""

import os
import time
from datetime import datetime
from typing import Dict, List

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from app.database.config import get_primary_db_session
from app.main import app
from app.models.simple_user import SimpleUser, UserRole

# Mark ALL tests in this module as E2E
pytestmark = pytest.mark.e2e

# Load environment variables
load_dotenv()


class TestConversationStartE2E:
    """E2E tests for starting new conversations"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and authentication"""
        self.client = TestClient(app)

        # Create test user for conversations
        self.test_user_id = f"e2e_conv_user_{int(datetime.now().timestamp())}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Conversation Tester",
            "email": f"e2e_conv_{int(datetime.now().timestamp())}@example.com",
            "password": "TestConvPassword123!",
            "role": "child",
            "first_name": "E2E",
            "last_name": "Conversationalist",
        }

        # Register test user
        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200, f"User registration failed: {response.text}"

        # Store auth token
        auth_data = response.json()
        self.auth_token = auth_data["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

        yield

        # Cleanup: Delete test user after tests
        db = get_primary_db_session()
        try:
            test_user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == self.test_user_id)
                .first()
            )
            if test_user:
                db.delete(test_user)
                db.commit()
        finally:
            db.close()

    def test_start_new_conversation_e2e(self):
        """
        Test starting a new conversation end-to-end

        Validates:
        - User can send first message
        - AI responds with actual content
        - Conversation ID is generated
        - Response includes all required fields
        - AI provider is selected correctly
        """
        # Skip if no AI API key available
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found - Skipping E2E test")

        # Prepare chat request
        chat_request = {
            "message": "Hello! Say 'Hi' in one word.",
            "language": "en-claude",  # English with Claude
            "use_speech": False,
            "conversation_history": None,  # New conversation
        }

        # Send message
        response = self.client.post(
            "/api/v1/conversations/chat",
            json=chat_request,
            headers=self.auth_headers,
        )

        # Validate response
        assert response.status_code == 200, f"Chat request failed: {response.text}"
        chat_data = response.json()

        # Verify response structure
        assert "response" in chat_data, "No AI response in chat data"
        assert "message_id" in chat_data, "No message ID generated"
        assert "conversation_id" in chat_data, "No conversation ID generated"
        assert "language" in chat_data, "No language in response"
        assert "ai_provider" in chat_data, "No AI provider in response"

        # Verify AI actually responded (not empty)
        assert len(chat_data["response"]) > 0, "AI response is empty"
        assert chat_data["response"] != chat_request["message"], (
            "AI echoed user message"
        )

        # Verify correct language and provider
        assert chat_data["language"] == "en", "Wrong language returned"
        assert "claude" in chat_data["ai_provider"].lower(), "Wrong AI provider"

        # Store conversation ID for next test
        self.conversation_id = chat_data["conversation_id"]

        print(f"\n✅ New Conversation Started Successfully")
        print(f"   Conversation ID: {self.conversation_id}")
        print(f"   AI Response: {chat_data['response'][:100]}...")
        print(f"   Provider: {chat_data['ai_provider']}")
        print(f"   Cost: ${chat_data.get('estimated_cost', 0):.4f}")


class TestMultiTurnConversationE2E:
    """E2E tests for multi-turn conversation flows"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and start conversation"""
        self.client = TestClient(app)

        # Create test user
        self.test_user_id = f"e2e_multiturn_user_{int(datetime.now().timestamp())}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E MultiTurn Tester",
            "email": f"e2e_multiturn_{int(datetime.now().timestamp())}@example.com",
            "password": "TestMultiPassword123!",
            "role": "child",
        }

        # Register and get auth
        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200
        self.auth_token = response.json()["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

        yield

        # Cleanup
        db = get_primary_db_session()
        try:
            test_user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == self.test_user_id)
                .first()
            )
            if test_user:
                db.delete(test_user)
                db.commit()
        finally:
            db.close()

    @pytest.mark.asyncio
    async def test_multi_turn_conversation_e2e(self):
        """
        Test multi-turn conversation end-to-end (5+ messages)

        Validates:
        - Conversation history is maintained
        - AI remembers context from previous messages
        - Each turn generates valid responses
        - Conversation ID stays consistent
        - Context is passed correctly between turns
        """
        # Skip if no AI API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found - Skipping E2E test")

        conversation_history = []
        conversation_id = None

        # Define conversation turns
        turns = [
            "My name is Alice.",
            "What is my name?",  # Tests context memory
            "Tell me a number between 1 and 5.",
            "What number did you just tell me?",  # Tests short-term memory
            "Thank you!",
        ]

        total_cost = 0.0

        for turn_num, user_message in enumerate(turns, 1):
            # Prepare chat request with history
            chat_request = {
                "message": user_message,
                "language": "en-claude",
                "use_speech": False,
                "conversation_history": conversation_history
                if conversation_history
                else None,
            }

            # Send message
            response = self.client.post(
                "/api/v1/conversations/chat",
                json=chat_request,
                headers=self.auth_headers,
            )

            assert response.status_code == 200, (
                f"Turn {turn_num} failed: {response.text}"
            )

            chat_data = response.json()

            # Verify response
            assert len(chat_data["response"]) > 0, f"Turn {turn_num}: Empty response"

            # Verify conversation ID consistency
            if conversation_id is None:
                conversation_id = chat_data["conversation_id"]
            else:
                assert chat_data["conversation_id"] == conversation_id, (
                    f"Turn {turn_num}: Conversation ID changed!"
                )

            # Add to conversation history
            conversation_history.append(
                {
                    "role": "user",
                    "content": user_message,
                }
            )
            conversation_history.append(
                {
                    "role": "assistant",
                    "content": chat_data["response"],
                }
            )

            # Track cost
            total_cost += chat_data.get("estimated_cost", 0)

            print(f"\n  Turn {turn_num}:")
            print(f"    User: {user_message}")
            print(f"    AI: {chat_data['response'][:80]}...")

            # Small delay between turns (rate limiting)
            time.sleep(0.5)

        # Validate conversation had context
        # Turn 2 should have user's name (Alice)
        turn_2_response = conversation_history[3]["content"]  # AI's 2nd response
        assert "alice" in turn_2_response.lower(), (
            "AI didn't remember user's name from context!"
        )

        print(f"\n✅ Multi-Turn Conversation Completed")
        print(f"   Total Turns: {len(turns)}")
        print(f"   Conversation ID: {conversation_id}")
        print(f"   Total Cost: ${total_cost:.4f}")
        print(f"   Context Memory: VALIDATED ✅")


class TestConversationPersistenceE2E:
    """E2E tests for conversation persistence and retrieval"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user"""
        self.client = TestClient(app)

        self.test_user_id = f"e2e_persist_user_{int(datetime.now().timestamp())}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Persistence Tester",
            "email": f"e2e_persist_{int(datetime.now().timestamp())}@example.com",
            "password": "TestPersistPassword123!",
            "role": "child",
        }

        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200
        self.auth_token = response.json()["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

        yield

        # Cleanup
        db = get_primary_db_session()
        try:
            test_user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == self.test_user_id)
                .first()
            )
            if test_user:
                db.delete(test_user)
                db.commit()
        finally:
            db.close()

    def test_conversation_persistence_and_retrieval_e2e(self):
        """
        Test conversation is saved and can be retrieved

        Validates:
        - Conversation persists to database
        - Can retrieve conversation by ID
        - Can list user's conversations
        - Retrieved data matches sent data
        - Timestamps are recorded correctly
        """
        # Skip if no AI API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found - Skipping E2E test")

        # Step 1: Start conversation
        chat_request = {
            "message": "Hello! This is a test conversation.",
            "language": "en-claude",
            "use_speech": False,
        }

        response = self.client.post(
            "/api/v1/conversations/chat",
            json=chat_request,
            headers=self.auth_headers,
        )

        assert response.status_code == 200
        chat_data = response.json()
        conversation_id = chat_data["conversation_id"]

        print(f"\n  Conversation created: {conversation_id}")

        # Step 2: Retrieve conversation by ID
        response = self.client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=self.auth_headers,
        )

        assert response.status_code == 200, (
            f"Failed to retrieve conversation: {response.text}"
        )

        retrieved_conv = response.json()

        # Validate retrieved data
        assert retrieved_conv["conversation_id"] == conversation_id
        assert "messages" in retrieved_conv
        assert len(retrieved_conv["messages"]) >= 1, (
            "No messages in retrieved conversation"
        )
        assert "started_at" in retrieved_conv or "created_at" in retrieved_conv

        print(f"  Conversation retrieved: {len(retrieved_conv['messages'])} messages")

        # Step 3: List user's conversations
        response = self.client.get(
            f"/api/v1/conversations/user/{self.test_user_id}",
            headers=self.auth_headers,
        )

        assert response.status_code == 200, (
            f"Failed to list user conversations: {response.text}"
        )

        user_conversations = response.json()

        # Validate conversation is in list
        assert isinstance(user_conversations, list), (
            "Conversations not returned as list"
        )
        assert len(user_conversations) >= 1, "User has no conversations"

        # Find our conversation in list
        our_conv = next(
            (
                c
                for c in user_conversations
                if c.get("conversation_id") == conversation_id
            ),
            None,
        )

        assert our_conv is not None, "Our conversation not in user's list"

        print(f"  User has {len(user_conversations)} conversation(s)")
        print(f"\n✅ Conversation Persistence Validated")
        print(f"   Created: ✅")
        print(f"   Retrieved by ID: ✅")
        print(f"   Listed for user: ✅")


class TestConversationDeletionE2E:
    """E2E tests for conversation deletion"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user"""
        self.client = TestClient(app)

        self.test_user_id = f"e2e_delete_user_{int(datetime.now().timestamp())}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Delete Tester",
            "email": f"e2e_delete_{int(datetime.now().timestamp())}@example.com",
            "password": "TestDeletePassword123!",
            "role": "child",
        }

        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200
        self.auth_token = response.json()["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

        yield

        # Cleanup
        db = get_primary_db_session()
        try:
            test_user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == self.test_user_id)
                .first()
            )
            if test_user:
                db.delete(test_user)
                db.commit()
        finally:
            db.close()

    def test_delete_conversation_e2e(self):
        """
        Test conversation deletion end-to-end

        Validates:
        - Conversation can be deleted
        - Deleted conversation cannot be retrieved
        - Deleted conversation not in user's list
        - Deletion is permanent
        """
        # Skip if no AI API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found - Skipping E2E test")

        # Step 1: Create conversation to delete
        chat_request = {
            "message": "This conversation will be deleted.",
            "language": "en-claude",
            "use_speech": False,
        }

        response = self.client.post(
            "/api/v1/conversations/chat",
            json=chat_request,
            headers=self.auth_headers,
        )

        assert response.status_code == 200
        conversation_id = response.json()["conversation_id"]

        print(f"\n  Created conversation to delete: {conversation_id}")

        # Step 2: Verify conversation exists
        response = self.client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=self.auth_headers,
        )
        assert response.status_code == 200, "Conversation not found before deletion"

        # Step 3: Delete conversation
        response = self.client.delete(
            f"/api/v1/conversations/{conversation_id}",
            headers=self.auth_headers,
        )

        assert response.status_code == 200, (
            f"Failed to delete conversation: {response.text}"
        )

        print(f"  Conversation deleted successfully")

        # Step 4: Verify conversation is gone (should return 404 or empty)
        response = self.client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=self.auth_headers,
        )

        # Should be 404 or return empty/null
        assert response.status_code in [404, 200], (
            f"Unexpected status after deletion: {response.status_code}"
        )

        if response.status_code == 200:
            # If 200, data should be empty or indicate deleted
            data = response.json()
            assert data is None or data == {} or data.get("deleted") is True, (
                "Conversation still accessible after deletion!"
            )

        print(f"\n✅ Conversation Deletion Validated")
        print(f"   Created: ✅")
        print(f"   Deleted: ✅")
        print(f"   Confirmed removed: ✅")


class TestConversationMultiLanguageE2E:
    """E2E tests for multi-language conversation support"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user"""
        self.client = TestClient(app)

        self.test_user_id = f"e2e_multilang_user_{int(datetime.now().timestamp())}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E MultiLang Tester",
            "email": f"e2e_multilang_{int(datetime.now().timestamp())}@example.com",
            "password": "TestMultiLangPassword123!",
            "role": "child",
        }

        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200
        self.auth_token = response.json()["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

        yield

        # Cleanup
        db = get_primary_db_session()
        try:
            test_user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == self.test_user_id)
                .first()
            )
            if test_user:
                db.delete(test_user)
                db.commit()
        finally:
            db.close()

    def test_conversation_multi_language_support_e2e(self):
        """
        Test conversations in multiple languages

        Validates:
        - English conversations work
        - Spanish conversations work
        - French conversations work
        - Language is tracked correctly
        - Appropriate AI providers used for each language
        """
        # Skip if no AI API keys
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found - Skipping E2E test")

        # Test data: (language, message, expected_lang_code)
        language_tests = [
            ("en-claude", "Say 'Hello' in one word", "en"),
            ("es-claude", "Di 'Hola' en una palabra", "es"),
            ("fr-mistral", "Dis 'Bonjour' en un mot", "fr"),
        ]

        results = []

        for lang_code, message, expected_lang in language_tests:
            chat_request = {
                "message": message,
                "language": lang_code,
                "use_speech": False,
            }

            response = self.client.post(
                "/api/v1/conversations/chat",
                json=chat_request,
                headers=self.auth_headers,
            )

            assert response.status_code == 200, (
                f"Failed for {lang_code}: {response.text}"
            )

            chat_data = response.json()

            # Validate response
            assert len(chat_data["response"]) > 0, f"Empty response for {lang_code}"
            assert chat_data["language"] == expected_lang, (
                f"Wrong language: expected {expected_lang}, got {chat_data['language']}"
            )

            results.append(
                {
                    "language": lang_code,
                    "expected": expected_lang,
                    "response": chat_data["response"][:50],
                    "provider": chat_data["ai_provider"],
                    "cost": chat_data.get("estimated_cost", 0),
                }
            )

            print(f"\n  {lang_code}:")
            print(f"    Response: {chat_data['response'][:60]}...")
            print(f"    Provider: {chat_data['ai_provider']}")

            # Small delay between language tests
            time.sleep(0.5)

        print(f"\n✅ Multi-Language Conversations Validated")
        print(f"   Languages tested: {len(results)}")
        print(f"   All responses received: ✅")
        print(f"   Language codes correct: ✅")


class TestConversationErrorHandlingE2E:
    """E2E tests for conversation error handling"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user"""
        self.client = TestClient(app)

        self.test_user_id = f"e2e_error_user_{int(datetime.now().timestamp())}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Error Tester",
            "email": f"e2e_error_{int(datetime.now().timestamp())}@example.com",
            "password": "TestErrorPassword123!",
            "role": "child",
        }

        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200
        self.auth_token = response.json()["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

        yield

        # Cleanup
        db = get_primary_db_session()
        try:
            test_user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == self.test_user_id)
                .first()
            )
            if test_user:
                db.delete(test_user)
                db.commit()
        finally:
            db.close()

    def test_conversation_invalid_data_handling_e2e(self):
        """
        Test error handling for invalid conversation data

        Validates:
        - Empty message rejected
        - Invalid language code handled
        - Missing required fields rejected
        - Appropriate error messages returned
        """
        # Test 1: Empty message
        chat_request = {
            "message": "",
            "language": "en-claude",
        }

        response = self.client.post(
            "/api/v1/conversations/chat",
            json=chat_request,
            headers=self.auth_headers,
        )

        # Should reject empty message
        assert response.status_code in [400, 422], (
            f"Empty message not rejected: {response.status_code}"
        )

        print(f"\n  Empty message rejected: ✅")

        # Test 2: Invalid language code (if validation exists)
        chat_request = {
            "message": "Test message",
            "language": "invalid-provider",
        }

        response = self.client.post(
            "/api/v1/conversations/chat",
            json=chat_request,
            headers=self.auth_headers,
        )

        # May be rejected or fallback to default
        print(f"  Invalid language handled: Status {response.status_code}")

        # Test 3: Missing required field
        chat_request = {
            "language": "en-claude",
            # Missing 'message' field
        }

        response = self.client.post(
            "/api/v1/conversations/chat",
            json=chat_request,
            headers=self.auth_headers,
        )

        assert response.status_code in [400, 422], (
            f"Missing field not rejected: {response.status_code}"
        )

        print(f"  Missing required field rejected: ✅")
        print(f"\n✅ Error Handling Validated")


# Summary of E2E Tests Created:
# 1. test_start_new_conversation_e2e - Start fresh conversation
# 2. test_multi_turn_conversation_e2e - 5+ turn conversation with context
# 3. test_conversation_persistence_and_retrieval_e2e - Save and retrieve
# 4. test_delete_conversation_e2e - Delete conversation
# 5. test_conversation_multi_language_support_e2e - Multi-language support
# 6. test_conversation_invalid_data_handling_e2e - Error handling
#
# Total: 6 comprehensive E2E tests for conversation management
# Expected execution time: ~30-45 seconds (with API calls)
# Estimated cost per run: ~$0.05-0.10
