"""
ChatResponse SQLModel definition.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import List, Dict, Any
import json


class ChatResponseBase(SQLModel):
    conversation_id: str = Field(max_length=100)
    response: str = Field(min_length=1, max_length=10000)
    tool_calls: str = Field(default="[]")  # Store as JSON string
    user_id: str = Field(max_length=100)


class ChatResponse(ChatResponseBase, table=True):
    id: int = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Indexes for common queries
    __table_args__ = (
        # Index on conversation_id for conversation retrieval
        # Index on user_id for user-specific queries
        # Index on timestamp for chronological ordering
    )

    def set_tool_calls(self, tool_calls_list: List[Dict[str, Any]]):
        """Convert tool_calls list to JSON string for storage."""
        self.tool_calls = json.dumps(tool_calls_list)

    def get_tool_calls(self) -> List[Dict[str, Any]]:
        """Convert stored JSON string back to tool_calls list."""
        import json
        return json.loads(self.tool_calls)