"""
ChatMessage SQLModel definition.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class ChatMessageBase(SQLModel):
    user_id: str = Field(max_length=100)
    message: str = Field(min_length=1, max_length=10000)
    conversation_id: Optional[str] = Field(default=None, max_length=100)


class ChatMessage(ChatMessageBase, table=True):
    id: int = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Indexes for common queries
    __table_args__ = (
        # Index on user_id for user-specific queries
        # Index on conversation_id for conversation retrieval
        # Index on timestamp for chronological ordering
    )