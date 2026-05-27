from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from backend.auth.schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, UserProfileResponse, UserRole
from backend.auth.password import PasswordHasher
from backend.auth.jwt import JWTHandler
from backend.auth.dependencies import get_current_user_claims
from ai_engine.utils.logger import setup_logger

logger = setup_logger("auth_routes")
router = APIRouter(prefix="/api/v1/auth", tags=["User Authentication"])

# Mock database dictionary to support local test environments when SQL engine is detached
MOCK_DB_USERS = {}

# Simple registration
@router.post("/register", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: UserRegisterRequest):
    email = request.email.lower()
    if email in MOCK_DB_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account with this email signature is already registered."
        )

    # Hash the password using bcrypt
    hashed_pwd = PasswordHasher.hash_password(request.password)
    
    # Store registration info in mock database
    user_id = f"usr_{int(request.email.encode().hex()[:8], 16) % 10000000}"
    user_record = {
        "id": user_id,
        "email": email,
        "password": hashed_pwd,
        "full_name": request.full_name,
        "role": request.role,
        "is_active": True
    }
    
    MOCK_DB_USERS[email] = user_record
    logger.info(f"New user registered: {email} as role {request.role.value}")
    
    return UserProfileResponse(
        id=user_id,
        email=email,
        full_name=request.full_name,
        role=request.role,
        is_active=True
    )

# Login
@router.post("/login", response_model=TokenResponse)
async def login_user(request: UserLoginRequest):
    email = request.email.lower()
    user = MOCK_DB_USERS.get(email)
    
    # Verify account exists and password matches
    if not user or not PasswordHasher.verify_password(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password credentials provided."
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is currently suspended."
        )

    # Generate JWT pair
    token_claims = {"sub": user["id"], "email": user["email"], "role": user["role"].value}
    
    access = JWTHandler.create_access_token(data=token_claims)
    refresh = JWTHandler.create_refresh_token(data=token_claims)
    
    logger.info(f"User session successfully authenticated: {email}")
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        role=user["role"].value
    )

# Refresh Token
@router.post("/refresh", response_model=TokenResponse)
async def refresh_session(refresh_token: str):
    claims = JWTHandler.decode_token(refresh_token, expected_type="refresh")
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired or invalid signature."
        )
        
    # Generate new access + refresh pair
    token_claims = {"sub": claims["sub"], "email": claims["email"], "role": claims["role"]}
    
    access = JWTHandler.create_access_token(data=token_claims)
    new_refresh = JWTHandler.create_refresh_token(data=token_claims)
    
    return TokenResponse(
        access_token=access,
        refresh_token=new_refresh,
        role=claims["role"]
    )

# Current Profile
@router.get("/me", response_model=UserProfileResponse)
async def get_current_profile(claims: dict = Depends(get_current_user_claims)):
    email = claims.get("email").lower()
    user = MOCK_DB_USERS.get(email)
    
    if not user:
        # Fallback profile extraction straight from token claims if DB connection is hot-swapped
        return UserProfileResponse(
            id=claims.get("sub"),
            email=email,
            full_name=claims.get("email").split("@")[0].capitalize(),
            role=UserRole(claims.get("role")),
            is_active=True
        )
        
    return UserProfileResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        is_active=user["is_active"]
    )
