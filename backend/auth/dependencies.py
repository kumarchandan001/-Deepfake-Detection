from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from backend.auth.jwt import JWTHandler
from backend.auth.schemas import UserRole

# Standard Bearer auth header injection scheme
security_scheme = HTTPBearer()

async def get_current_user_claims(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> dict:
    """
    Extracts Bearer token from authorization header and decodes token claims.
    """
    token = credentials.credentials
    claims = JWTHandler.decode_token(token, expected_type="access")
    
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or authorization signature is invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return claims

class RoleChecker:
    """
    FastAPI dependency factory enforcing role requirements on routed endpoints.
    """
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, claims: dict = Depends(get_current_user_claims)) -> dict:
        user_role = claims.get("role")
        
        # Admin bypasses standard role checks as superuser privilege
        if user_role == UserRole.ADMIN:
            return claims
            
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Insufficient role authorization."
            )
            
        return claims
