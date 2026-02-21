"""
Unit Tests for Authentication Module
Tests JWT token generation, OTP verification, and auth flows
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt
from main import app
from database import get_database

client = TestClient(app)

# Test Data
VALID_PHONE = "+919876543210"
INVALID_PHONE = "invalid"
TEST_OTP = "123456"
JWT_SECRET = "your-secret-key"  # Should match main.py


class TestOTPGeneration:
    """Test OTP generation and storage"""
    
    def test_request_otp_valid_phone(self):
        """Test OTP request with valid phone number"""
        response = client.post(
            "/api/auth/request-otp",
            json={"phone": VALID_PHONE}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "OTP sent successfully"
        assert "otp" in data  # In test mode, OTP is returned
    
    def test_request_otp_invalid_phone(self):
        """Test OTP request with invalid phone format"""
        response = client.post(
            "/api/auth/request-otp",
            json={"phone": INVALID_PHONE}
        )
        assert response.status_code == 400
    
    def test_request_otp_missing_phone(self):
        """Test OTP request without phone number"""
        response = client.post("/api/auth/request-otp", json={})
        assert response.status_code == 422  # Validation error


class TestOTPVerification:
    """Test OTP verification and token generation"""
    
    def test_verify_otp_success(self):
        """Test successful OTP verification"""
        # First request OTP
        otp_response = client.post(
            "/api/auth/request-otp",
            json={"phone": VALID_PHONE}
        )
        otp = otp_response.json()["otp"]
        
        # Then verify it
        response = client.post(
            "/api/auth/verify-otp",
            json={"phone": VALID_PHONE, "otp": otp}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_verify_otp_wrong_code(self):
        """Test verification with wrong OTP"""
        client.post("/api/auth/request-otp", json={"phone": VALID_PHONE})
        
        response = client.post(
            "/api/auth/verify-otp",
            json={"phone": VALID_PHONE, "otp": "000000"}
        )
        assert response.status_code == 401
    
    def test_verify_otp_expired(self):
        """Test verification with expired OTP"""
        # This requires mocking time or waiting 10 minutes
        # Implementation depends on your OTP expiry logic
        pass


class TestJWTTokens:
    """Test JWT token generation and validation"""
    
    def test_token_structure(self):
        """Verify JWT token contains required claims"""
        # Get a valid token
        otp_response = client.post("/api/auth/request-otp", json={"phone": VALID_PHONE})
        otp = otp_response.json()["otp"]
        
        verify_response = client.post(
            "/api/auth/verify-otp",
            json={"phone": VALID_PHONE, "otp": otp}
        )
        token = verify_response.json()["access_token"]
        
        # Decode and verify claims
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        assert "user_id" in decoded
        assert "phone" in decoded
        assert "exp" in decoded
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/customers/list")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token"""
        # Get token
        otp_response = client.post("/api/auth/request-otp", json={"phone": VALID_PHONE})
        otp = otp_response.json()["otp"]
        verify_response = client.post(
            "/api/auth/verify-otp",
            json={"phone": VALID_PHONE, "otp": otp}
        )
        token = verify_response.json()["access_token"]
        
        # Use token
        response = client.get(
            "/api/customers/list",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 404]  # 404 if no customers yet


class TestRateLimiting:
    """Test rate limiting on OTP requests"""
    
    def test_otp_rate_limit(self):
        """Test that excessive OTP requests are blocked"""
        # Make 6 rapid requests (assuming limit is 5)
        for i in range(6):
            response = client.post(
                "/api/auth/request-otp",
                json={"phone": f"+9198765432{i:02d}"}
            )
            if i < 5:
                assert response.status_code == 200
            else:
                assert response.status_code == 429  # Too Many Requests


# Run with: pytest tests/test_auth.py -v
