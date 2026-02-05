"""
Password hashing and validation utilities using bcrypt.
"""
import re
import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with 12 salt rounds.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hashed password string (60 characters, format: $2b$12$...)
    """
    # Bcrypt requires bytes input
    password_bytes = password.encode('utf-8')
    # Generate salt with 12 rounds
    salt = bcrypt.gensalt(rounds=12)
    # Hash the password
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password to verify against

    Returns:
        True if password matches hash, False otherwise
    """
    # Bcrypt requires bytes input
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    # Verify the password
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength against security requirements.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid: bool, error_message: str)
        If valid: (True, "")
        If invalid: (False, "error message")
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"

    return True, ""
