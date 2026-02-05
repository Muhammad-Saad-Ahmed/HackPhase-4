"""
Authentication middleware for protecting endpoints with JWT validation.
"""
from typing import Optional
from fastapi import Depends, HTTPException, Header
from jose import JWTError
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_db_session
from ..models.user import User
from ..utils.jwt import decode_access_token
from ..services.auth_service import get_user_by_id


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Validates JWT signature, extracts user_id, and queries the database.

    Args:
        authorization: Authorization header value (format: "Bearer {token}")
        db: Database async session

    Returns:
        User object for the authenticated user

    Raises:
        HTTPException 401: If token is missing, invalid, or expired
        HTTPException 403: If user is inactive
    """
    # Check if Authorization header is present
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

    # Decode and validate JWT
    try:
        payload = decode_access_token(token)
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid token", "message": f"Token validation failed: {str(e)}"}
        )

    # Extract user_id from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid token", "message": "Token does not contain user ID"}
        )

    # Query user from database
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail={"error": "User not found", "message": "The user associated with this token does not exist"}
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail={"error": "Account inactive", "message": "Your account has been deactivated"}
        )

    return user
