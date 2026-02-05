"""
ConversationMetadata SQLModel definition.
Stores metadata for conversations including task references for multi-turn flows.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import json


class ConversationMetadata(SQLModel, table=True):
    """Stores metadata for conversations."""

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(max_length=100, index=True, unique=True)
    metadata_json: str = Field(default="{}")  # Store metadata as JSON string
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def set_metadata(self, metadata: dict):
        """Convert metadata dict to JSON string for storage."""
        self.metadata_json = json.dumps(metadata)
        self.updated_at = datetime.utcnow()

    def get_metadata(self) -> dict:
        """Convert stored JSON string back to metadata dict."""
        try:
            return json.loads(self.metadata_json)
        except (json.JSONDecodeError, TypeError):
            return {}
