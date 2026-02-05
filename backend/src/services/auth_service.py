"""
Authentication service layer for user registration, login, and session management.
"""
import re
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException

from ..models.user import User
from ..models.session import Session
from ..utils.password import hash_password, verify_password, validate_password_strength
from ..utils.jwt import create_access_token
from ..core.config import settings


class EmailAlreadyExistsException(Exception):
    """Raised when attempting to register with an already registered email."""
    pass


def validate_email_format(email: str) -> bool:
    """
    Validate email format using regex.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


async def register_user(email: str, password: str, db: AsyncSession) -> User:
    """
    Register a new user with email and password.

    Args:
        email: User email address
        password: Plain text password
        db: Database async session

    Returns:
        Created User object

    Raises:
        EmailAlreadyExistsException: If email is already registered
        HTTPException: If email format is invalid or password is weak
    """
    # Validate email format
    if not validate_email_format(email):
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid email format", "message": "Please provide a valid email address"}
        )

    # Validate password strength
    is_valid, error_msg = validate_password_strength(password)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail={"error": "Weak password", "message": error_msg}
        )

    # Check if email already exists
    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise EmailAlreadyExistsException(f"Email {email} is already registered")

    # Hash password
    hashed = hash_password(password)

    # Create user record
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        hashed_password=hashed,
        created_at=datetime.utcnow(),
        is_active=True
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[User]:
    """
    Authenticate user by email and password.

    Args:
        email: User email address
        password: Plain text password

    Returns:
        User object if authentication succeeds, None otherwise
    """
    # Query user by email
    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        return None

    # Verify password
    if not verify_password(password, user.hashed_password):
        return None

    return user


async def create_session(user_id: str, email: str, db: AsyncSession) -> tuple[str, Session]:
    """
    Create a new session and generate JWT token.

    Args:
        user_id: User ID to create session for
        email: User email to embed in JWT
        db: Database async session

    Returns:
        Tuple of (jwt_token, session_object)
    """
    # Generate session ID (will be used as JTI in JWT)
    session_id = str(uuid.uuid4())

    # Create JWT token
    token = create_access_token(user_id, email, session_id)

    # Calculate expiration
    expires_at = datetime.utcnow() + timedelta(days=settings.jwt_expiry_days)

    # Create session record
    session = Session(
        id=session_id,
        user_id=user_id,
        token_jti=session_id,
        expires_at=expires_at,
        created_at=datetime.utcnow(),
        revoked=False
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return token, session


async def revoke_session(token_jti: str, db: AsyncSession) -> bool:
    """
    Revoke a session by marking it as revoked.

    Args:
        token_jti: JWT ID (jti claim) to revoke
        db: Database async session

    Returns:
        True if session was revoked, False if not found
    """
    statement = select(Session).where(Session.token_jti == token_jti)
    result = await db.execute(statement)
    session = result.scalar_one_or_none()

    if not session:
        return False

    session.revoked = True
    await db.commit()

    return True


async def get_user_by_id(user_id: str, db: AsyncSession) -> Optional[User]:
    """
    Get user by ID.

    Args:
        user_id: User ID to query
        db: Database async session

    Returns:
        User object if found, None otherwise
    """
    statement = select(User).where(User.id == user_id)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    return user


async def check_session_revoked(token_jti: str, db: AsyncSession) -> bool:
    """
    Check if a session has been revoked.

    Args:
        token_jti: JWT ID (jti claim) to check
        db: Database async session

    Returns:
        True if session is revoked, False otherwise
    """
    statement = select(Session).where(Session.token_jti == token_jti)
    result = await db.execute(statement)
    session = result.scalar_one_or_none()

    if not session:
        return False

    return session.revoked
