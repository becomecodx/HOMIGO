"""
Tests for authentication API endpoints.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_firebase_token():
    """Mock Firebase ID token for testing."""
    return "mock_firebase_token_12345"


@pytest.fixture
def mock_firebase_claims():
    """Mock Firebase token claims."""
    return {
        "uid": "firebase_uid_test_123",
        "email": "test@example.com",
        "email_verified": True
    }


@pytest.fixture
def sample_signup_data():
    """Sample signup request data."""
    return {
        "firebase_id": "firebase_uid_test_123",
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "user_type": "tenant",
        "profile_photo_url": "https://example.com/photo.jpg"
    }


@pytest.fixture
def sample_login_data(mock_firebase_token):
    """Sample login request data."""
    return {
        "firebase_token": mock_firebase_token,
        "fcm_token": "fcm_token_test_123"
    }


# ============================================================================
# Signup Tests
# ============================================================================

@pytest.mark.asyncio
class TestSignup:
    """Test cases for signup endpoint."""
    
    async def test_signup_success(self, sample_signup_data):
        """Test successful user signup."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/signup",
                json=sample_signup_data
            )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User registered successfully"
        assert "user" in data
        assert data["user"]["email"] == sample_signup_data["email"]
        assert data["user"]["full_name"] == sample_signup_data["full_name"]
        assert data["user"]["user_type"] == sample_signup_data["user_type"]
    
    async def test_signup_duplicate_firebase_id(self, sample_signup_data):
        """Test signup with duplicate firebase_id."""
        # First signup
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/v1/auth/signup", json=sample_signup_data)
            
            # Try to signup again with same firebase_id
            response = await client.post(
                "/api/v1/auth/signup",
                json=sample_signup_data
            )
        
        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert "Firebase ID already exists" in data["message"]
    
    async def test_signup_duplicate_email(self, sample_signup_data):
        """Test signup with duplicate email."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First signup
            await client.post("/api/v1/auth/signup", json=sample_signup_data)
            
            # Try to signup with different firebase_id but same email
            duplicate_data = sample_signup_data.copy()
            duplicate_data["firebase_id"] = "different_firebase_id"
            response = await client.post(
                "/api/v1/auth/signup",
                json=duplicate_data
            )
        
        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert "email already exists" in data["message"]
    
    async def test_signup_duplicate_phone(self, sample_signup_data):
        """Test signup with duplicate phone number."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First signup
            await client.post("/api/v1/auth/signup", json=sample_signup_data)
            
            # Try to signup with different firebase_id and email but same phone
            duplicate_data = sample_signup_data.copy()
            duplicate_data["firebase_id"] = "different_firebase_id"
            duplicate_data["email"] = "different@example.com"
            response = await client.post(
                "/api/v1/auth/signup",
                json=duplicate_data
            )
        
        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert "phone number already exists" in data["message"]
    
    async def test_signup_invalid_user_type(self, sample_signup_data):
        """Test signup with invalid user_type."""
        invalid_data = sample_signup_data.copy()
        invalid_data["user_type"] = "invalid_type"
        invalid_data["firebase_id"] = "unique_firebase_id"
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/signup",
                json=invalid_data
            )
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "user_type must be" in data["message"]
    
    async def test_signup_missing_required_fields(self):
        """Test signup with missing required fields."""
        incomplete_data = {
            "firebase_id": "test_firebase_id",
            "email": "test@example.com"
            # Missing: full_name, phone, user_type
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/signup",
                json=incomplete_data
            )
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "Validation error" in data["message"]


# ============================================================================
# Login Tests
# ============================================================================

@pytest.mark.asyncio
class TestLogin:
    """Test cases for login endpoint."""
    
    @patch('app.core.firebase.verify_firebase_token')
    async def test_login_success(
        self, 
        mock_verify, 
        sample_signup_data, 
        sample_login_data,
        mock_firebase_claims
    ):
        """Test successful login with Firebase token."""
        # Mock Firebase token verification
        mock_verify.return_value = mock_firebase_claims
        
        # First create a user
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/v1/auth/signup", json=sample_signup_data)
            
            # Now login
            response = await client.post(
                "/api/v1/auth/login",
                json=sample_login_data
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Login successful"
        assert "user" in data
        assert data["user"]["email"] == sample_signup_data["email"]
        
        # Verify Firebase token verification was called
        mock_verify.assert_called_once()
    
    @patch('app.core.firebase.verify_firebase_token')
    async def test_login_user_not_found(
        self, 
        mock_verify, 
        sample_login_data,
        mock_firebase_claims
    ):
        """Test login with valid token but user not in database."""
        # Mock Firebase token verification
        mock_verify.return_value = {
            "uid": "non_existent_firebase_id",
            "email": "nonexistent@example.com"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/login",
                json=sample_login_data
            )
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "User not found" in data["message"]
    
    @patch('app.core.firebase.verify_firebase_token')
    async def test_login_invalid_token(self, mock_verify, sample_login_data):
        """Test login with invalid Firebase token."""
        from fastapi import HTTPException, status
        
        # Mock Firebase token verification to raise exception
        mock_verify.side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase ID token"
        )
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/login",
                json=sample_login_data
            )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
    
    @patch('app.core.firebase.verify_firebase_token')
    async def test_login_updates_last_login(
        self, 
        mock_verify, 
        sample_signup_data, 
        sample_login_data,
        mock_firebase_claims
    ):
        """Test that login updates last_login_at timestamp."""
        mock_verify.return_value = mock_firebase_claims
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create user
            signup_response = await client.post(
                "/api/v1/auth/signup", 
                json=sample_signup_data
            )
            initial_login = signup_response.json()["user"]["last_login_at"]
            
            # Wait a moment and login again
            import asyncio
            await asyncio.sleep(0.1)
            
            login_response = await client.post(
                "/api/v1/auth/login",
                json=sample_login_data
            )
            updated_login = login_response.json()["user"]["last_login_at"]
            
            # Verify last_login_at was updated
            assert updated_login != initial_login


# ============================================================================
# Protected Endpoint Tests
# ============================================================================

@pytest.mark.asyncio
class TestProtectedEndpoints:
    """Test cases for protected endpoints requiring authentication."""
    
    @patch('app.core.firebase.verify_firebase_token')
    async def test_get_me_success(
        self, 
        mock_verify, 
        sample_signup_data,
        mock_firebase_claims,
        mock_firebase_token
    ):
        """Test GET /me with valid authentication."""
        mock_verify.return_value = mock_firebase_claims
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create user
            await client.post("/api/v1/auth/signup", json=sample_signup_data)
            
            # Access protected endpoint
            response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {mock_firebase_token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_signup_data["email"]
        assert data["full_name"] == sample_signup_data["full_name"]
    
    async def test_get_me_no_auth(self):
        """Test GET /me without authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 403
    
    @patch('app.core.firebase.verify_firebase_token')
    async def test_get_me_invalid_token(self, mock_verify, mock_firebase_token):
        """Test GET /me with invalid token."""
        from fastapi import HTTPException, status
        
        mock_verify.side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase ID token"
        )
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {mock_firebase_token}"}
            )
        
        assert response.status_code == 401


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
