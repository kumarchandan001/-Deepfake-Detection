import unittest
import os
import sys
from datetime import timedelta

# Ensure workspace path imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.auth.password import PasswordHasher
from backend.auth.jwt import JWTHandler
from backend.auth.schemas import UserRole

class TestEnterpriseAuth(unittest.TestCase):
    """
    Validates password encryption, matching, JWT lifetimes, and claims structure checks.
    """
    def test_password_encryption(self):
        """
        Passwords should be successfully encrypted and validated.
        """
        raw_pwd = "security_platform_secret_123"
        hashed_pwd = PasswordHasher.hash_password(raw_pwd)
        
        # Verify hash matches plain text
        self.assertTrue(PasswordHasher.verify_password(raw_pwd, hashed_pwd))
        # Verify invalid mismatch
        self.assertFalse(PasswordHasher.verify_password("wrong_password", hashed_pwd))

    def test_jwt_generation_and_decryption(self):
        """
        JWTHandler should encode and decode access tokens and refresh tokens safely.
        """
        claims = {
            "sub": "usr_998877",
            "email": "analyst@antigravity.ai",
            "role": UserRole.ANALYST.value
        }
        
        # Generate Access Token
        access_token = JWTHandler.create_access_token(data=claims, expires_delta=timedelta(minutes=5))
        
        # Decode and assert claims
        decoded = JWTHandler.decode_token(access_token, expected_type="access")
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["sub"], "usr_998877")
        self.assertEqual(decoded["role"], "analyst")
        self.assertEqual(decoded["type"], "access")

        # Generate Refresh Token
        refresh_token = JWTHandler.create_refresh_token(data=claims)
        
        # Decode and assert type matching
        decoded_refresh = JWTHandler.decode_token(refresh_token, expected_type="refresh")
        self.assertIsNotNone(decoded_refresh)
        self.assertEqual(decoded_refresh["type"], "refresh")

        # Swapping Token types should return None (Exploit protection check)
        bad_swap = JWTHandler.decode_token(access_token, expected_type="refresh")
        self.assertIsNone(bad_swap)

if __name__ == "__main__":
    unittest.main()
