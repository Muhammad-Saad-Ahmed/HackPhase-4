"""
JWT token creation and validation utilities using python-jose.
"""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from ..core.config import settings


def create_access_token(user_id: str, email: str, session_id: str) -> str:
    """
    Create a JWT access token signed with BETTER_AUTH_SECRET.

    Args:
        user_id: User ID to embed in token
        email: User email to embed in token
        session_id: Session ID to use as JTI (JWT ID) for revocation

    Returns:
        JWT token string signed with HS256
    """
    expires_delta = timedelta(days=settings.jwt_expiry_days)
    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": user_id,  # Subject (user ID)
        "email": email,
        "iat": datetime.utcnow(),  # Issued at
        "exp": expire,  # Expiration
        "jti": session_id,  # JWT ID for revocation
    }

    token = jwt.encode(
        payload,
        settings.better_auth_secret,
        algorithm=settings.jwt_algorithm
    )
    return token


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token using BETTER_AUTH_SECRET.

    Args:
        token: JWT token string to decode

    Returns:
        Decoded token payload as dict with keys: sub, email, iat, exp, jti

    Raises:
        JWTError: If token is invalid, expired, or signature verification fails
    """
    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        # Re-raise JWTError for caller to handle (401 Unauthorized)
        raise e
