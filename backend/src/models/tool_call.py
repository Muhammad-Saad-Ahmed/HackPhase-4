"""
ToolCall SQLModel definition.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Dict, Any, Optional
import json


class ToolCallBase(SQLModel):
    tool_name: str = Field(max_length=100)
    arguments: str = Field(default="{}")  # Store as JSON string
    execution_result: Optional[str] = Field(default=None)  # Store as JSON string
    conversation_id: str = Field(max_length=100)
    chat_response_id: int

    def set_arguments(self, args_dict: Dict[str, Any]):
        """Convert arguments dict to JSON string for storage."""
        self.arguments = json.dumps(args_dict)

    def get_arguments(self) -> Dict[str, Any]:
        """Convert stored JSON string back to arguments dict."""
        return json.loads(self.arguments)

    def set_execution_result(self, result: Optional[Dict[str, Any]]):
        """Convert execution_result dict to JSON string for storage."""
        self.execution_result = json.dumps(result) if result else None

    def get_execution_result(self) -> Optional[Dict[str, Any]]:
        """Convert stored JSON string back to execution_result dict."""
        return json.loads(self.execution_result) if self.execution_result else None


class ToolCall(ToolCallBase, table=True):
    id: int = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending", regex="^(pending|executing|completed|failed)$")

    # Indexes for common queries
    __table_args__ = (
        # Index on conversation_id for conversation retrieval
        # Index on chat_response_id for linking to responses
        # Index on status for filtering by execution status
        # Index on timestamp for chronological ordering
    )