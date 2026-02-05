"""
Session model for JWT token management and revocation.
"""
import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel


class Session(SQLModel, table=True):
    """Session model for tracking JWT tokens and enabling revocation."""

    __tablename__ = "session"

    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique session identifier"
    )
    user_id: str = Field(
        foreign_key="user.id",
        index=True,
        description="User ID (foreign key to user table)"
    )
    token_jti: str = Field(
        unique=True,
        index=True,
        max_length=100,
        description="JWT ID (jti claim) for revocation support"
    )
    expires_at: datetime = Field(
        description="Token expiration timestamp"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Session creation timestamp"
    )
    revoked: bool = Field(
        default=False,
        description="Whether this session has been revoked"
    )
