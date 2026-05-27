import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("jwt_handler")

# Fallback development variables (production loads these from secure environment profiles)
SECRET_KEY = "antigravity_cybersecurity_forensic_platform_key_signature"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

class JWTHandler:
    """
    Manages session serialization, token encryption, and claims integrity validation
    for access tokens and refresh tokens.
    """
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Generates a short-lived access JWT containing user identities and access roles.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Generates a long-lived refresh JWT used to re-validate access credentials without login prompts.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str, expected_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Decodes a JWT string and validates its signatures, types, and expiration dates.
        
        Returns:
            Decoded claims dictionary if token is valid and matches expected type, else None.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Verify token usage type to prevent access token swapping exploits
            if payload.get("type") != expected_type:
                logger.warning(f"Swapped token type detected: Expected {expected_type}, got {payload.get('type')}")
                return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.debug("Decryption match failed: Token claims signature has expired.")
            return None
        except jwt.InvalidTokenError as e:
            logger.debug(f"Invalid token credentials parsed: {e}")
            return None
