"""
Authentication endpoints with real JWT-based authentication.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_db_session
from ..services.auth_service import (
    register_user,
    authenticate_user,
    create_session,
    revoke_session,
    EmailAlreadyExistsException
)
from ..utils.jwt import decode_access_token
from jose import JWTError
from fastapi import Header

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    user: dict
    session_token: str
    expires_at: str


@router.post("/v1/auth/signup", response_model=AuthResponse, status_code=201)
async def signup(request: SignupRequest, db: AsyncSession = Depends(get_db_session)):
    """
    Register a new user with email and password.

    Returns:
        201 Created with JWT token and user info

    Raises:
        400 Bad Request: Weak password or invalid email
        409 Conflict: Email already registered
    """
    try:
        # Register user (validates email format and password strength)
        user = await register_user(request.email, request.password, db)

        # Create session and generate JWT
        token, session = await create_session(user.id, user.email, db)

        # Return response
        return AuthResponse(
            user={
                "user_id": user.id,
                "email": user.email,
            },
            session_token=token,
            expires_at=session.expires_at.isoformat(),
        )

    except EmailAlreadyExistsException:
        raise HTTPException(
            status_code=409,
            detail={"error": "Email already registered", "message": "An account with this email already exists"}
        )


@router.post("/v1/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db_session)):
    """
    Authenticate user with email and password.

    Returns:
        200 OK with JWT token and user info

    Raises:
        401 Unauthorized: Invalid credentials
        403 Forbidden: Account is inactive
    """
    # Authenticate user
    user = await authenticate_user(request.email, request.password, db)

    if not user:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid credentials", "message": "Invalid email or password"}
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail={"error": "Account inactive", "message": "Your account has been deactivated"}
        )

    # Create session and generate JWT
    token, session = await create_session(user.id, user.email, db)

    return AuthResponse(
        user={
            "user_id": user.id,
            "email": user.email,
        },
        session_token=token,
        expires_at=session.expires_at.isoformat(),
    )


@router.post("/v1/auth/logout")
async def logout(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Logout user by revoking their session.

    Requires valid JWT token in Authorization header.

    Returns:
        200 OK with success message

    Raises:
        401 Unauthorized: Invalid or missing token
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={"error": "Authentication required", "message": "No authorization header provided"}
        )

    # Extract Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid authorization header", "message": "Format must be: Bearer {token}"}
        )

    token = parts[1]

    # Decode token to get JTI
    try:
        payload = decode_access_token(token)
        token_jti = payload.get("jti")

        if token_jti:
            # Revoke session in database
            await revoke_session(token_jti, db)

    except JWTError:
        # Token invalid or expired - that's fine for logout
        pass

    return {"status": "success", "message": "Logged out successfully"}
