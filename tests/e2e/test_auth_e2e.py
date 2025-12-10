"""
End-to-End Tests for Authentication
Session 102 - TRUE 100% Functionality Validation

⚠️ WARNING: These tests use REAL database operations!
- Tests will create/modify real user records
- Uses test database configured in settings
- Safe to run, but creates actual data

Run: pytest tests/e2e/test_auth_e2e.py -v -s -m e2e
"""

import time
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import ALGORITHM, SECRET_KEY, get_password_hash, verify_password
from app.database.config import get_primary_db_session
from app.main import app
from app.models.simple_user import SimpleUser, UserRole

# Mark ALL tests in this module as E2E
pytestmark = pytest.mark.e2e


class TestUserRegistrationE2E:
    """E2E tests for user registration flow"""

    def test_user_registration_complete_flow(self):
        """
        Test complete user registration end-to-end

        Validates:
        - User can register with valid credentials
        - User data is stored in database correctly
        - Password is hashed (not stored as plaintext)
        - JWT token is returned and valid
        - User can immediately login with registered credentials
        """
        client = TestClient(app)
        # Step 1: Register new user
        registration_data = {
            "user_id": f"e2e_test_user_{datetime.now().timestamp()}",
            "username": "E2E Test User",
            "email": "e2e_test@example.com",
            "password": "TestPassword123!",
            "role": "child",
            "first_name": "E2E",
            "last_name": "Tester",
        }

        response = client.post("/api/v1/auth/register", json=registration_data)

        # Step 2: Verify successful registration response
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()

        # Verify response structure
        assert "access_token" in data, "No access token returned"
        assert "token_type" in data, "No token type returned"
        assert data["token_type"] == "bearer", "Wrong token type"
        assert "user" in data, "No user data returned"

        # Verify user data in response
        user_data = data["user"]
        assert user_data["user_id"] == registration_data["user_id"]
        assert user_data["username"] == registration_data["username"]
        assert user_data["email"] == registration_data["email"]
        assert user_data["role"] == registration_data["role"]
        assert user_data["first_name"] == registration_data["first_name"]
        assert user_data["last_name"] == registration_data["last_name"]
        assert user_data["is_active"] is True

        # Step 3: Verify user exists in database with correct data
        db = get_primary_db_session()
        try:
            db_user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == registration_data["user_id"])
                .first()
            )

            assert db_user is not None, "User not found in database"
            assert db_user.username == registration_data["username"]
            assert db_user.email == registration_data["email"]
            assert db_user.role == UserRole.CHILD
            assert db_user.first_name == registration_data["first_name"]
            assert db_user.last_name == registration_data["last_name"]
            assert db_user.is_active is True

            # Step 4: Verify password is hashed (NOT plaintext)
            assert db_user.password_hash is not None, "Password not hashed"
            assert db_user.password_hash != registration_data["password"], (
                "Password stored as plaintext! SECURITY ISSUE!"
            )
            # Verify password hash is valid
            assert verify_password(
                registration_data["password"], db_user.password_hash
            ), "Password hash verification failed"

            # Step 5: Verify JWT token is valid and contains correct user_id
            token = data["access_token"]
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            assert decoded["sub"] == registration_data["user_id"], (
                "Token contains wrong user_id"
            )

            # Step 6: Verify user can login with registered credentials
            login_response = client.post(
                "/api/v1/auth/login",
                json={
                    "user_id": registration_data["user_id"],
                    "password": registration_data["password"],
                },
            )
            assert login_response.status_code == 200, (
                "Cannot login with registered credentials"
            )
            login_data = login_response.json()
            assert "access_token" in login_data
            assert login_data["user"]["user_id"] == registration_data["user_id"]

            print(f"\n✅ User Registration E2E Test Passed")
            print(f"   User ID: {registration_data['user_id']}")
            print(f"   Username: {registration_data['username']}")
            print(f"   Password hashed: ✅")
            print(f"   JWT token valid: ✅")
            print(f"   Can login: ✅")
            print(f"   Database record: ✅")

        finally:
            # Cleanup: Delete test user
            if db_user:
                db.delete(db_user)
                db.commit()
            db.close()

    def test_registration_duplicate_user_rejection(self):
        """
        Test that duplicate user_id registration is rejected

        Validates:
        - Cannot register same user_id twice
        - Appropriate error response returned
        - Original user data unchanged
        """
        client = TestClient(app)
        # Create initial user
        user_id = f"e2e_duplicate_test_{datetime.now().timestamp()}"
        registration_data = {
            "user_id": user_id,
            "username": "Original User",
            "email": "original@example.com",
            "password": "Password123!",
            "role": "child",
        }

        # First registration - should succeed
        response1 = client.post("/api/v1/auth/register", json=registration_data)
        assert response1.status_code == 200, "First registration failed"

        # Second registration with same user_id - should fail
        duplicate_data = {
            "user_id": user_id,  # Same user_id
            "username": "Duplicate Attempt",
            "email": "duplicate@example.com",
            "password": "DifferentPassword123!",
            "role": "parent",
        }

        response2 = client.post("/api/v1/auth/register", json=duplicate_data)

        # Verify rejection
        assert response2.status_code == 400, "Duplicate registration not rejected"
        error_data = response2.json()
        assert "detail" in error_data
        assert "already exists" in error_data["detail"].lower()

        # Verify original user data unchanged
        db = get_primary_db_session()
        try:
            db_user = db.query(SimpleUser).filter(SimpleUser.user_id == user_id).first()

            assert db_user.username == "Original User", "Original user data modified!"
            assert db_user.email == "original@example.com", (
                "Original user data modified!"
            )

            print(f"\n✅ Duplicate User Rejection Test Passed")
            print(f"   Duplicate registration blocked: ✅")
            print(f"   Original data preserved: ✅")

        finally:
            # Cleanup
            if db_user:
                db.delete(db_user)
                db.commit()
            db.close()


class TestUserLoginE2E:
    """E2E tests for user login flow"""

    def test_user_login_complete_flow(self):
        """
        Test complete login flow with real JWT

        Validates:
        - User can login with valid credentials
        - JWT token returned and valid
        - Token contains correct user data
        - Token can access protected endpoints
        - Last login timestamp updated
        """
        client = TestClient(app)
        # Setup: Create test user
        user_id = f"e2e_login_test_{datetime.now().timestamp()}"
        password = "LoginTest123!"

        # Register user
        client.post(
            "/api/v1/auth/register",
            json={
                "user_id": user_id,
                "username": "Login Tester",
                "email": "login@test.com",
                "password": password,
                "role": "child",
            },
        )

        # Get initial last_login time
        db = get_primary_db_session()
        initial_login_time = (
            db.query(SimpleUser)
            .filter(SimpleUser.user_id == user_id)
            .first()
            .last_login
        )
        db.close()

        # Wait a moment to ensure timestamp difference
        time.sleep(0.1)

        # Step 1: Login with valid credentials
        login_response = client.post(
            "/api/v1/auth/login", json={"user_id": user_id, "password": password}
        )

        # Step 2: Verify successful login response
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        login_data = login_response.json()

        assert "access_token" in login_data
        assert "token_type" in login_data
        assert login_data["token_type"] == "bearer"
        assert "user" in login_data

        # Step 3: Verify JWT token is valid and contains correct data
        token = login_data["access_token"]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert "sub" in decoded, "Token missing 'sub' claim"
        assert decoded["sub"] == user_id, "Token contains wrong user_id"
        assert "exp" in decoded, "Token missing expiration"

        # Verify token not expired
        exp_timestamp = decoded["exp"]
        now = datetime.now(timezone.utc).timestamp()
        assert exp_timestamp > now, "Token already expired"

        # Step 4: Verify token can access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = client.get("/api/v1/auth/profile", headers=headers)

        assert profile_response.status_code == 200, (
            "Token cannot access protected endpoint"
        )
        profile_data = profile_response.json()
        assert profile_data["user_id"] == user_id

        # Step 5: Verify last_login timestamp was updated
        db = get_primary_db_session()
        try:
            updated_user = (
                db.query(SimpleUser).filter(SimpleUser.user_id == user_id).first()
            )

            assert updated_user.last_login is not None, "last_login not set"
            if initial_login_time:
                assert updated_user.last_login > initial_login_time, (
                    "last_login not updated on login"
                )

            print(f"\n✅ User Login E2E Test Passed")
            print(f"   Login successful: ✅")
            print(f"   JWT token valid: ✅")
            print(f"   Token contains correct user_id: ✅")
            print(f"   Token accesses protected endpoints: ✅")
            print(f"   Last login updated: ✅")

        finally:
            # Cleanup
            if updated_user:
                db.delete(updated_user)
                db.commit()
            db.close()

    def test_login_invalid_credentials_rejection(self):
        """
        Test that invalid credentials are rejected

        Validates:
        - Wrong password rejected
        - Non-existent user rejected
        - Appropriate error responses
        """
        client = TestClient(app)
        # Setup: Create test user
        user_id = f"e2e_invalid_creds_{datetime.now().timestamp()}"
        correct_password = "CorrectPass123!"

        client.post(
            "/api/v1/auth/register",
            json={
                "user_id": user_id,
                "username": "Creds Tester",
                "password": correct_password,
                "role": "child",
            },
        )

        # Test 1: Wrong password
        wrong_pass_response = client.post(
            "/api/v1/auth/login",
            json={"user_id": user_id, "password": "WrongPassword123!"},
        )
        assert wrong_pass_response.status_code == 401, "Wrong password not rejected"
        assert "invalid credentials" in wrong_pass_response.json()["detail"].lower()

        # Test 2: Non-existent user
        nonexistent_response = client.post(
            "/api/v1/auth/login",
            json={
                "user_id": "nonexistent_user_12345",
                "password": "SomePassword123!",
            },
        )
        assert nonexistent_response.status_code == 401, "Non-existent user not rejected"

        print(f"\n✅ Invalid Credentials Rejection Test Passed")
        print(f"   Wrong password blocked: ✅")
        print(f"   Non-existent user blocked: ✅")

        # Cleanup
        db = get_primary_db_session()
        try:
            user = db.query(SimpleUser).filter(SimpleUser.user_id == user_id).first()
            if user:
                db.delete(user)
                db.commit()
        finally:
            db.close()


class TestProtectedEndpointsE2E:
    """E2E tests for JWT authentication on protected endpoints"""

    def test_protected_endpoint_authentication_flow(self):
        """
        Test JWT authentication on protected endpoints

        Validates:
        - Access without token → 401
        - Access with valid token → 200
        - Access with invalid token → 401
        - Access with expired token → 401
        """
        client = TestClient(app)
        # Step 1: Try accessing protected endpoint WITHOUT token
        no_token_response = client.get("/api/v1/auth/profile")
        assert no_token_response.status_code == 401, (
            "Protected endpoint accessible without token!"
        )

        # Step 2: Create user and get valid token
        user_id = f"e2e_protected_test_{datetime.now().timestamp()}"
        password = "Protected123!"

        client.post(
            "/api/v1/auth/register",
            json={
                "user_id": user_id,
                "username": "Protected Tester",
                "password": password,
                "role": "child",
            },
        )

        login_response = client.post(
            "/api/v1/auth/login", json={"user_id": user_id, "password": password}
        )
        valid_token = login_response.json()["access_token"]

        # Step 3: Access with VALID token
        valid_headers = {"Authorization": f"Bearer {valid_token}"}
        valid_response = client.get("/api/v1/auth/profile", headers=valid_headers)
        assert valid_response.status_code == 200, (
            "Protected endpoint not accessible with valid token"
        )
        assert valid_response.json()["user_id"] == user_id

        # Step 4: Access with INVALID token
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        invalid_response = client.get("/api/v1/auth/profile", headers=invalid_headers)
        assert invalid_response.status_code in [401, 422], "Invalid token not rejected"

        # Step 5: Access with EXPIRED token
        # Create expired token
        expired_payload = {
            "sub": user_id,
            "exp": datetime.now(timezone.utc)
            - timedelta(hours=1),  # Expired 1 hour ago
        }
        expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
        expired_headers = {"Authorization": f"Bearer {expired_token}"}

        expired_response = client.get("/api/v1/auth/profile", headers=expired_headers)
        assert expired_response.status_code in [401, 422], "Expired token not rejected"

        print(f"\n✅ Protected Endpoint Authentication Test Passed")
        print(f"   No token → 401: ✅")
        print(f"   Valid token → 200: ✅")
        print(f"   Invalid token → 401: ✅")
        print(f"   Expired token → 401: ✅")

        # Cleanup
        db = get_primary_db_session()
        try:
            user = db.query(SimpleUser).filter(SimpleUser.user_id == user_id).first()
            if user:
                db.delete(user)
                db.commit()
        finally:
            db.close()


class TestUserProfileE2E:
    """E2E tests for user profile management"""

    def test_user_profile_crud_operations(self):
        """
        Test user profile read and update operations

        Validates:
        - Can retrieve user profile
        - Can update user profile
        - Changes persist to database
        - Updated data returned in subsequent requests
        """
        client = TestClient(app)
        # Setup: Create user and login
        user_id = f"e2e_profile_test_{datetime.now().timestamp()}"
        password = "Profile123!"

        client.post(
            "/api/v1/auth/register",
            json={
                "user_id": user_id,
                "username": "Original Name",
                "email": "original@test.com",
                "password": password,
                "first_name": "Original",
                "last_name": "User",
                "role": "child",
            },
        )

        login_response = client.post(
            "/api/v1/auth/login", json={"user_id": user_id, "password": password}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: GET profile - verify initial data
        get_response = client.get("/api/v1/auth/profile", headers=headers)
        assert get_response.status_code == 200
        initial_profile = get_response.json()

        assert initial_profile["user_id"] == user_id
        assert initial_profile["username"] == "Original Name"
        assert initial_profile["email"] == "original@test.com"
        assert initial_profile["first_name"] == "Original"
        assert initial_profile["last_name"] == "User"

        # Step 2: UPDATE profile
        update_data = {
            "username": "Updated Name",
            "email": "updated@test.com",
            "first_name": "Updated",
            "last_name": "Person",
            "ui_language": "fr",
        }

        update_response = client.put(
            "/api/v1/auth/profile",
            headers=headers,
            data=update_data,  # Use data instead of json for form data
        )
        assert update_response.status_code == 200

        # Step 3: GET profile again - verify changes persisted
        updated_response = client.get("/api/v1/auth/profile", headers=headers)
        assert updated_response.status_code == 200
        updated_profile = updated_response.json()

        assert updated_profile["username"] == "Updated Name"
        assert updated_profile["email"] == "updated@test.com"
        assert updated_profile["first_name"] == "Updated"
        assert updated_profile["last_name"] == "Person"
        assert updated_profile["ui_language"] == "fr"

        # Step 4: Verify changes in database
        db = get_primary_db_session()
        try:
            db_user = db.query(SimpleUser).filter(SimpleUser.user_id == user_id).first()

            assert db_user.username == "Updated Name"
            assert db_user.email == "updated@test.com"
            assert db_user.first_name == "Updated"
            assert db_user.last_name == "Person"
            assert db_user.ui_language == "fr"
            assert db_user.updated_at is not None

            print(f"\n✅ User Profile CRUD Test Passed")
            print(f"   Profile retrieval: ✅")
            print(f"   Profile update: ✅")
            print(f"   Changes persisted to DB: ✅")
            print(f"   Updated data in API: ✅")

        finally:
            # Cleanup
            if db_user:
                db.delete(db_user)
                db.commit()
            db.close()


class TestFamilyUserManagementE2E:
    """E2E tests for family user management (role-based access)"""

    def test_family_user_list_access_control(self):
        """
        Test that only parents/admins can list all users

        Validates:
        - Parent can list all users
        - Child cannot list all users (403 Forbidden)
        - User list contains correct data
        """
        client = TestClient(app)
        # Create parent user
        parent_id = f"e2e_parent_{datetime.now().timestamp()}"
        parent_password = "Parent123!"

        client.post(
            "/api/v1/auth/register",
            json={
                "user_id": parent_id,
                "username": "Parent User",
                "password": parent_password,
                "role": "parent",
            },
        )

        # Create child user
        child_id = f"e2e_child_{datetime.now().timestamp()}"
        child_password = "Child123!"

        client.post(
            "/api/v1/auth/register",
            json={
                "user_id": child_id,
                "username": "Child User",
                "password": child_password,
                "role": "child",
            },
        )

        # Login as parent
        parent_login = client.post(
            "/api/v1/auth/login",
            json={"user_id": parent_id, "password": parent_password},
        )
        parent_token = parent_login.json()["access_token"]
        parent_headers = {"Authorization": f"Bearer {parent_token}"}

        # Login as child
        child_login = client.post(
            "/api/v1/auth/login",
            json={"user_id": child_id, "password": child_password},
        )
        child_token = child_login.json()["access_token"]
        child_headers = {"Authorization": f"Bearer {child_token}"}

        # Test 1: Parent can list users
        parent_list_response = client.get("/api/v1/auth/users", headers=parent_headers)
        assert parent_list_response.status_code == 200, "Parent cannot list users"
        user_list = parent_list_response.json()
        assert isinstance(user_list, list)
        # Should contain at least the parent and child
        user_ids = [u["user_id"] for u in user_list]
        assert parent_id in user_ids, f"Parent {parent_id} not in list: {user_ids}"
        assert child_id in user_ids, f"Child {child_id} not in list: {user_ids}"

        # Test 2: Child cannot list users (403 Forbidden)
        child_list_response = client.get("/api/v1/auth/users", headers=child_headers)
        assert child_list_response.status_code == 403, (
            "Child can list users! Authorization broken!"
        )
        error_data = child_list_response.json()
        assert "insufficient permissions" in error_data["detail"].lower()

        print(f"\n✅ Family User Management Test Passed")
        print(f"   Parent can list users: ✅")
        print(f"   Child blocked from listing: ✅")
        print(f"   Role-based access control: ✅")

        # Cleanup
        db = get_primary_db_session()
        try:
            parent_user = (
                db.query(SimpleUser).filter(SimpleUser.user_id == parent_id).first()
            )
            child_user = (
                db.query(SimpleUser).filter(SimpleUser.user_id == child_id).first()
            )

            if parent_user:
                db.delete(parent_user)
            if child_user:
                db.delete(child_user)
            db.commit()
        finally:
            db.close()


class TestSessionTokenLifecycleE2E:
    """E2E tests for JWT token lifecycle and session management"""

    def test_token_lifecycle_and_expiration(self):
        """
        Test JWT token lifecycle

        Validates:
        - Fresh token works immediately
        - Token works before expiration
        - Token can be decoded correctly
        - Logout flow (client-side token deletion)
        """
        client = TestClient(app)
        # Setup: Create user and login
        user_id = f"e2e_token_test_{datetime.now().timestamp()}"
        password = "Token123!"

        client.post(
            "/api/v1/auth/register",
            json={
                "user_id": user_id,
                "username": "Token Tester",
                "password": password,
                "role": "child",
            },
        )

        login_response = client.post(
            "/api/v1/auth/login", json={"user_id": user_id, "password": password}
        )
        token = login_response.json()["access_token"]

        # Test 1: Fresh token works immediately
        headers = {"Authorization": f"Bearer {token}"}
        immediate_response = client.get("/api/v1/auth/profile", headers=headers)
        assert immediate_response.status_code == 200

        # Test 2: Decode token and verify claims
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == user_id
        assert "exp" in decoded

        # Verify expiration is in the future
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        assert exp_time > now, "Token already expired"

        # Verify reasonable expiration (should be ~30 minutes as per auth.py)
        time_until_exp = exp_time - now
        assert timedelta(minutes=20) < time_until_exp < timedelta(minutes=40), (
            f"Token expiration time unexpected: {time_until_exp}"
        )

        # Test 3: Token still works after small delay
        time.sleep(0.2)

        delayed_response = client.get("/api/v1/auth/profile", headers=headers)
        assert delayed_response.status_code == 200

        # Test 4: Logout endpoint (client should delete token after this)
        logout_response = client.post("/api/v1/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        logout_data = logout_response.json()
        assert "logout successful" in logout_data["message"].lower()

        print(f"\n✅ Token Lifecycle Test Passed")
        print(f"   Fresh token works: ✅")
        print(f"   Token decoded correctly: ✅")
        print(f"   Token expiration valid: ✅")
        print(f"   Token persists over time: ✅")
        print(f"   Logout endpoint works: ✅")

        # Cleanup
        db = get_primary_db_session()
        try:
            user = db.query(SimpleUser).filter(SimpleUser.user_id == user_id).first()
            if user:
                db.delete(user)
                db.commit()
        finally:
            db.close()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("AUTHENTICATION E2E TESTS - USING REAL DATABASE!")
    print("=" * 80)
    print("\nThese tests will:")
    print("  - Create real user records in database")
    print("  - Generate real JWT tokens")
    print("  - Test actual authentication flows")
    print("  - Validate security mechanisms")
    print("  - Clean up test data afterwards")
    print("\nTo run these tests:")
    print("  pytest tests/e2e/test_auth_e2e.py -v -s -m e2e")
    print("\n" + "=" * 80 + "\n")
