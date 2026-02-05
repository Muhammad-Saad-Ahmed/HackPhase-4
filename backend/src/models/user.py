"""
User model for authentication.
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User model with authentication credentials."""

    __tablename__ = "user"

    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique user identifier"
    )
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User email address (unique)"
    )
    hashed_password: str = Field(
        max_length=255,
        description="Bcrypt hashed password"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user account is active"
    )
