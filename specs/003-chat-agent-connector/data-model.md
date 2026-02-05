# Data Model: Chat Agent Connector

## Core Entities

### ChatMessage Entity
```python
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
```

**Validation Rules**:
- `user_id` is required (up to 100 characters)
- `message` is required (1-10000 characters)
- `conversation_id` is optional (up to 100 characters)
- `timestamp` is auto-generated on creation

### ChatResponse Entity
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional

class ChatResponseBase(SQLModel):
    conversation_id: str = Field(max_length=100)
    response: str = Field(min_length=1, max_length=10000)
    tool_calls: List[Dict[str, Any]] = Field(default=[])
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
```

**Validation Rules**:
- `conversation_id` is required (up to 100 characters)
- `response` is required (1-10000 characters)
- `tool_calls` is a list of dictionaries representing MCP tool calls
- `user_id` is required (up to 100 characters)
- `timestamp` is auto-generated on creation

### ToolCall Entity
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Dict, Any, Optional

class ToolCallBase(SQLModel):
    tool_name: str = Field(max_length=100)
    arguments: Dict[str, Any] = Field(default={})
    execution_result: Optional[Dict[str, Any]] = Field(default=None)
    conversation_id: str = Field(max_length=100)
    chat_response_id: int

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
```

**Validation Rules**:
- `tool_name` is required (up to 100 characters)
- `arguments` is a dictionary of tool arguments (default empty)
- `execution_result` is optional (for storing results after execution)
- `conversation_id` is required (up to 100 characters)
- `chat_response_id` is required (foreign key reference)
- `status` must be one of "pending", "executing", "completed", "failed"
- `timestamp` is auto-generated on creation

## Relationships

### ChatMessage Relationships
- No direct relationships required for the ChatMessage entity

### ChatResponse Relationships
- No direct relationships required for the ChatResponse entity

### ToolCall Relationships
- Links to ChatResponse via `chat_response_id` foreign key

## State Transitions

### ToolCall State Transitions
- `pending` → `executing` (when tool execution starts)
- `executing` → `completed` (when tool execution succeeds)
- `executing` → `failed` (when tool execution fails)
- Once `completed` or `failed`, status remains unchanged

## Indexing Strategy

### ChatMessage Table Indexes
- Primary index on `id`
- Index on `user_id` for user-specific queries
- Index on `conversation_id` for conversation retrieval
- Index on `timestamp` for chronological ordering

### ChatResponse Table Indexes
- Primary index on `id`
- Index on `conversation_id` for conversation retrieval
- Index on `user_id` for user-specific queries
- Index on `timestamp` for chronological ordering

### ToolCall Table Indexes
- Primary index on `id`
- Index on `conversation_id` for conversation retrieval
- Index on `chat_response_id` for linking to responses
- Index on `status` for filtering by execution status
- Index on `timestamp` for chronological ordering