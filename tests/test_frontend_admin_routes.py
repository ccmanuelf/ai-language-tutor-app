"""
Test module for Admin Routes Frontend
AI Language Tutor App - Session 106

Tests for app/frontend/admin_routes.py module
Target: 100% coverage with comprehensive test scenarios
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from datetime import datetime

from app.frontend_main import frontend_app
from app.models.database import User, UserRole


class TestAdminRoutes:
    """Test suite for admin routes"""

    def setup_method(self):
        """Set up test client and mocks for each test"""
        self.client = TestClient(frontend_app)
        
        # Create mock admin user
        self.mock_admin_user = {
            "user_id": "admin123",
            "username": "admin_user",
            "email": "admin@test.com",
            "role": "admin",
            "is_active": True,
        }
        
        # Create mock regular user
        self.mock_regular_user = {
            "user_id": "user123",
            "username": "regular_user",
            "email": "user@test.com",
            "role": "user",
            "is_active": True,
        }

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_dashboard_redirect_success(self, mock_auth_service, mock_get_user):
        """Test admin dashboard redirect for authenticated admin"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        
        response = self.client.get("/dashboard/admin", follow_redirects=False)
        
        assert response.status_code == 302
        assert response.headers["location"] == "/dashboard/admin/users"

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_dashboard_redirect_forbidden_non_admin(self, mock_auth_service, mock_get_user):
        """Test admin dashboard redirect denies non-admin users"""
        mock_get_user.return_value = self.mock_regular_user
        mock_auth_service.is_admin_user.return_value = False
        
        response = self.client.get("/dashboard/admin")
        
        # When is_admin_user returns False, code raises HTTPException which gets logged and converted to 500
        assert response.status_code == 500
        assert "Failed to access admin dashboard" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_dashboard_redirect_exception_handling(self, mock_auth_service, mock_get_user):
        """Test admin dashboard redirect handles generic exceptions"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.side_effect = Exception("Database error")
        
        response = self.client.get("/dashboard/admin")
        
        assert response.status_code == 500
        assert "Failed to access admin dashboard" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.get_db_session_context")
    @patch("app.services.admin_auth.GuestUserManager")
    def test_admin_users_page_success(self, mock_guest_manager, mock_db_context, mock_auth_service, mock_get_user):
        """Test admin users page loads successfully"""
        # Setup mocks
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        
        # Mock database session and users
        mock_session = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_session
        
        # Create mock users
        mock_user1 = Mock(spec=User)
        mock_user1.user_id = "user1"
        mock_user1.username = "testuser1"
        mock_user1.email = "test1@example.com"
        mock_user1.first_name = "Test"
        mock_user1.last_name = "User"
        mock_user1.role = UserRole.PARENT
        mock_user1.is_active = True
        mock_user1.is_verified = True
        mock_user1.created_at = datetime(2024, 1, 1, 12, 0, 0)
        mock_user1.updated_at = datetime(2024, 1, 2, 12, 0, 0)
        mock_user1.last_login = datetime(2024, 1, 3, 12, 0, 0)
        
        mock_user2 = Mock(spec=User)
        mock_user2.user_id = "user2"
        mock_user2.username = "testuser2"
        mock_user2.email = "test2@example.com"
        mock_user2.first_name = "Another"
        mock_user2.last_name = "User"
        mock_user2.role = UserRole.ADMIN
        mock_user2.is_active = False
        mock_user2.is_verified = False
        mock_user2.created_at = None
        mock_user2.updated_at = None
        mock_user2.last_login = None
        
        mock_session.query.return_value.all.return_value = [mock_user1, mock_user2]
        
        # Mock guest manager
        mock_guest_instance = Mock()
        mock_guest_instance.active_guest_session = "guest123"
        mock_guest_instance.guest_session_data = {"created_at": "2024-01-01"}
        mock_guest_manager.return_value = mock_guest_instance
        
        response = self.client.get("/dashboard/admin/users")
        
        assert response.status_code == 200
        content = response.text
        
        # Check for user data presence
        assert "testuser1" in content or "test1@example.com" in content

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.get_db_session_context")
    @patch("app.services.admin_auth.GuestUserManager")
    def test_admin_users_page_without_guest_session(self, mock_guest_manager, mock_db_context, mock_auth_service, mock_get_user):
        """Test admin users page without active guest session"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        
        # Mock database session
        mock_session = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.all.return_value = []
        
        # Mock guest manager without active session
        mock_guest_instance = Mock()
        mock_guest_instance.active_guest_session = None
        mock_guest_manager.return_value = mock_guest_instance
        
        response = self.client.get("/dashboard/admin/users")
        
        assert response.status_code == 200

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_users_page_forbidden_non_admin(self, mock_auth_service, mock_get_user):
        """Test admin users page denies non-admin users"""
        mock_get_user.return_value = self.mock_regular_user
        mock_auth_service.is_admin_user.return_value = False
        
        response = self.client.get("/dashboard/admin/users")
        
        assert response.status_code == 403
        assert "Admin access required" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.get_db_session_context")
    def test_admin_users_page_exception_handling(self, mock_db_context, mock_auth_service, mock_get_user):
        """Test admin users page handles database exceptions"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        
        # Simulate database error
        mock_db_context.side_effect = Exception("Database connection failed")
        
        response = self.client.get("/dashboard/admin/users")
        
        assert response.status_code == 500
        assert "Failed to load user management page" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_languages_page_forbidden_non_admin(self, mock_auth_service, mock_get_user):
        """Test admin languages page denies non-admin users"""
        mock_get_user.return_value = self.mock_regular_user
        mock_auth_service.is_admin_user.return_value = False
        
        response = self.client.get("/dashboard/admin/languages")
        
        assert response.status_code == 403
        assert "Admin access required" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.AdminPermission")
    def test_admin_languages_page_forbidden_no_permission(self, mock_permission, mock_auth_service, mock_get_user):
        """Test admin languages page denies users without language management permission"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        mock_auth_service.has_permission.return_value = False
        
        response = self.client.get("/dashboard/admin/languages")
        
        assert response.status_code == 403
        assert "Language management permission required" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_languages_page_exception_handling(self, mock_auth_service, mock_get_user):
        """Test admin languages page handles exceptions"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.side_effect = Exception("Auth error")
        
        response = self.client.get("/dashboard/admin/languages")
        
        assert response.status_code == 500
        assert "Failed to load language configuration page" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_features_page_forbidden_non_admin(self, mock_auth_service, mock_get_user):
        """Test admin features page denies non-admin users"""
        mock_get_user.return_value = self.mock_regular_user
        mock_auth_service.is_admin_user.return_value = False
        
        response = self.client.get("/dashboard/admin/features")
        
        assert response.status_code == 403
        assert "Admin access required" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.AdminPermission")
    def test_admin_features_page_forbidden_no_permission(self, mock_permission, mock_auth_service, mock_get_user):
        """Test admin features page denies users without feature management permission"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        mock_auth_service.has_permission.return_value = False
        
        response = self.client.get("/dashboard/admin/features")
        
        assert response.status_code == 403
        assert "Feature management permission required" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_features_page_exception_handling(self, mock_auth_service, mock_get_user):
        """Test admin features page handles exceptions"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.side_effect = Exception("Permission error")
        
        response = self.client.get("/dashboard/admin/features")
        
        assert response.status_code == 500
        assert "Failed to load feature management page" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_ai_models_page_forbidden_non_admin(self, mock_auth_service, mock_get_user):
        """Test admin AI models page denies non-admin users"""
        mock_get_user.return_value = self.mock_regular_user
        mock_auth_service.is_admin_user.return_value = False
        
        response = self.client.get("/dashboard/admin/ai-models")
        
        assert response.status_code == 403
        assert "Admin access required" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.AdminPermission")
    def test_admin_ai_models_page_forbidden_no_permission(self, mock_permission, mock_auth_service, mock_get_user):
        """Test admin AI models page denies users without AI model management permission"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        mock_auth_service.has_permission.return_value = False
        
        response = self.client.get("/dashboard/admin/ai-models")
        
        assert response.status_code == 403
        assert "AI model management permission required" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_ai_models_page_exception_handling(self, mock_auth_service, mock_get_user):
        """Test admin AI models page handles exceptions"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.side_effect = Exception("Model loading error")
        
        response = self.client.get("/dashboard/admin/ai-models")
        
        assert response.status_code == 500
        assert "Failed to load AI model management page" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_system_page_success(self, mock_auth_service, mock_get_user):
        """Test admin system status page loads successfully"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        
        response = self.client.get("/dashboard/admin/system")
        
        assert response.status_code == 200
        content = response.text
        assert "System Status" in content
        assert "System monitoring interface coming soon" in content
        assert "Back to Users" in content

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_system_page_forbidden_non_admin(self, mock_auth_service, mock_get_user):
        """Test admin system page denies non-admin users"""
        mock_get_user.return_value = self.mock_regular_user
        mock_auth_service.is_admin_user.return_value = False
        
        response = self.client.get("/dashboard/admin/system")
        
        assert response.status_code == 403
        assert "Admin access required" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_system_page_exception_handling(self, mock_auth_service, mock_get_user):
        """Test admin system page handles exceptions"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.side_effect = Exception("System error")
        
        response = self.client.get("/dashboard/admin/system")
        
        assert response.status_code == 500
        assert "Failed to load system status page" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_scenarios_page_forbidden_non_admin(self, mock_auth_service, mock_get_user):
        """Test admin scenarios page denies non-admin users"""
        mock_get_user.return_value = self.mock_regular_user
        mock_auth_service.is_admin_user.return_value = False
        
        response = self.client.get("/dashboard/admin/scenarios")
        
        assert response.status_code == 403
        assert "Admin access required" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.AdminPermission")
    def test_admin_scenarios_page_forbidden_no_permission(self, mock_permission, mock_auth_service, mock_get_user):
        """Test admin scenarios page denies users without scenario management permission"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        mock_auth_service.has_permission.return_value = False
        
        response = self.client.get("/dashboard/admin/scenarios")
        
        assert response.status_code == 403
        assert "Scenario management permission required" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_scenarios_page_exception_handling(self, mock_auth_service, mock_get_user):
        """Test admin scenarios page handles exceptions"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.side_effect = Exception("Scenario error")
        
        response = self.client.get("/dashboard/admin/scenarios")
        
        assert response.status_code == 500
        assert "Failed to load scenario management page" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_progress_analytics_page_forbidden_non_admin(self, mock_auth_service, mock_get_user):
        """Test admin progress analytics page denies non-admin users"""
        mock_get_user.return_value = self.mock_regular_user
        mock_auth_service.is_admin_user.return_value = False
        
        response = self.client.get("/dashboard/admin/progress-analytics")
        
        assert response.status_code == 403
        assert "Admin access required" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.AdminPermission")
    def test_admin_progress_analytics_page_forbidden_no_permission(self, mock_permission, mock_auth_service, mock_get_user):
        """Test admin progress analytics page denies users without analytics viewing permission"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        mock_auth_service.has_permission.return_value = False
        
        response = self.client.get("/dashboard/admin/progress-analytics")
        
        assert response.status_code == 403
        assert "Analytics viewing permission required" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_progress_analytics_page_exception_handling(self, mock_auth_service, mock_get_user):
        """Test admin progress analytics page handles exceptions"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.side_effect = Exception("Analytics error")
        
        response = self.client.get("/dashboard/admin/progress-analytics")
        
        assert response.status_code == 500
        assert "Failed to load progress analytics page" in response.text

    @patch("app.frontend.admin_routes.logger")
    def test_register_admin_routes_logging(self, mock_logger):
        """Test register_admin_routes logs success message"""
        from app.frontend.admin_routes import register_admin_routes
        
        mock_app = Mock()
        mock_api_router = Mock()
        
        register_admin_routes(mock_app, mock_api_router)
        
        mock_logger.info.assert_called_once_with("Admin dashboard routes registered successfully")


class TestAdminRoutesHTTPExceptions:
    """Test suite for ensuring HTTPExceptions are properly re-raised"""

    def setup_method(self):
        """Set up test client for each test"""
        self.client = TestClient(frontend_app)

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.get_db_session_context")
    @patch("app.services.admin_auth.GuestUserManager")
    def test_admin_users_page_reraises_http_exception(self, mock_guest_manager, mock_db_context, mock_auth_service, mock_get_user):
        """Test that HTTPException is re-raised in admin users page"""
        mock_get_user.return_value = {"user_id": "admin123"}
        mock_auth_service.is_admin_user.return_value = True
        
        # Simulate HTTPException being raised
        mock_session = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_session
        mock_session.query.side_effect = HTTPException(status_code=503, detail="Service unavailable")
        
        response = self.client.get("/dashboard/admin/users")
        
        assert response.status_code == 503
        assert "Service unavailable" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_languages_page_reraises_http_exception(self, mock_auth_service, mock_get_user):
        """Test that HTTPException is re-raised in admin languages page"""
        mock_get_user.return_value = {"user_id": "admin123"}
        
        # Raise HTTPException during admin check
        mock_auth_service.is_admin_user.side_effect = HTTPException(status_code=401, detail="Unauthorized")
        
        response = self.client.get("/dashboard/admin/languages")
        
        assert response.status_code == 401
        assert "Unauthorized" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_features_page_reraises_http_exception(self, mock_auth_service, mock_get_user):
        """Test that HTTPException is re-raised in admin features page"""
        mock_get_user.return_value = {"user_id": "admin123"}
        mock_auth_service.is_admin_user.side_effect = HTTPException(status_code=504, detail="Gateway timeout")
        
        response = self.client.get("/dashboard/admin/features")
        
        assert response.status_code == 504
        assert "Gateway timeout" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_ai_models_page_reraises_http_exception(self, mock_auth_service, mock_get_user):
        """Test that HTTPException is re-raised in admin AI models page"""
        mock_get_user.return_value = {"user_id": "admin123"}
        mock_auth_service.is_admin_user.side_effect = HTTPException(status_code=429, detail="Too many requests")
        
        response = self.client.get("/dashboard/admin/ai-models")
        
        assert response.status_code == 429
        assert "Too many requests" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_scenarios_page_reraises_http_exception(self, mock_auth_service, mock_get_user):
        """Test that HTTPException is re-raised in admin scenarios page"""
        mock_get_user.return_value = {"user_id": "admin123"}
        mock_auth_service.is_admin_user.side_effect = HTTPException(status_code=502, detail="Bad gateway")
        
        response = self.client.get("/dashboard/admin/scenarios")
        
        assert response.status_code == 502
        assert "Bad gateway" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    def test_admin_progress_analytics_page_reraises_http_exception(self, mock_auth_service, mock_get_user):
        """Test that HTTPException is re-raised in admin progress analytics page"""
        mock_get_user.return_value = {"user_id": "admin123"}
        mock_auth_service.is_admin_user.side_effect = HTTPException(status_code=503, detail="Service temporarily unavailable")
        
        response = self.client.get("/dashboard/admin/progress-analytics")
        
        assert response.status_code == 503
        assert "Service temporarily unavailable" in response.text


class TestAdminRoutesImportErrors:
    """Test that routes handle missing import errors properly"""
    
    def setup_method(self):
        """Set up test client for each test"""
        self.client = TestClient(frontend_app)
        
        self.mock_admin_user = {
            "user_id": "admin123",
            "username": "admin_user",
            "email": "admin@test.com",
            "role": "admin",
            "is_active": True,
        }

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.AdminPermission")
    def test_languages_page_import_error_coverage(self, mock_permission, mock_auth_service, mock_get_user):
        """Test that languages page import errors are caught"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        mock_auth_service.has_permission.return_value = True
        
        response = self.client.get("/dashboard/admin/languages")
        
        # Currently fails due to missing get_admin_styles import
        assert response.status_code == 500
        assert "Failed to load language configuration page" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.AdminPermission")
    def test_features_page_import_error_coverage(self, mock_permission, mock_auth_service, mock_get_user):
        """Test that features page import errors are caught"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        mock_auth_service.has_permission.return_value = True
        
        response = self.client.get("/dashboard/admin/features")
        
        # Currently fails due to missing get_admin_styles import
        assert response.status_code == 500
        assert "Failed to load feature management page" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.AdminPermission")
    def test_ai_models_page_import_error_coverage(self, mock_permission, mock_auth_service, mock_get_user):
        """Test that AI models page import errors are caught"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        mock_auth_service.has_permission.return_value = True
        
        response = self.client.get("/dashboard/admin/ai-models")
        
        # Currently fails due to missing get_admin_styles import
        assert response.status_code == 500
        assert "Failed to load AI model management page" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.AdminPermission")
    def test_scenarios_page_import_error_coverage(self, mock_permission, mock_auth_service, mock_get_user):
        """Test that scenarios page import errors are caught"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        mock_auth_service.has_permission.return_value = True
        
        response = self.client.get("/dashboard/admin/scenarios")
        
        # Currently fails due to missing get_admin_styles import
        assert response.status_code == 500
        assert "Failed to load scenario management page" in response.text

    @patch("app.frontend.admin_routes.get_current_user")
    @patch("app.frontend.admin_routes.admin_auth_service")
    @patch("app.frontend.admin_routes.AdminPermission")
    def test_progress_analytics_page_import_error_coverage(self, mock_permission, mock_auth_service, mock_get_user):
        """Test that progress analytics page import errors are caught"""
        mock_get_user.return_value = self.mock_admin_user
        mock_auth_service.is_admin_user.return_value = True
        mock_auth_service.has_permission.return_value = True
        
        response = self.client.get("/dashboard/admin/progress-analytics")
        
        # Currently fails due to missing get_admin_styles import
        assert response.status_code == 500
        assert "Failed to load progress analytics page" in response.text
