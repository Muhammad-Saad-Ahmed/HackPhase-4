# Data Model: Todo MCP Tools

## Core Entities

### Task Entity
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending", regex="^(pending|completed)$")

class Task(TaskBase, table=True):
    id: int = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Indexes for common queries
    __table_args__ = (
        # Index on status for list_tasks filtering
        # Index on created_at for chronological sorting
    )
```

**Validation Rules**:
- `title` is required (1-255 characters)
- `description` is optional (up to 1000 characters)
- `status` must be either "pending" or "completed"
- `created_at` is auto-generated on creation
- `completed_at` is set when status changes to "completed"

### Tool Metadata Entity
```python
from sqlmodel import SQLModel, Field
from typing import Dict, Any, Optional

class ToolMetadataBase(SQLModel):
    tool_name: str = Field(unique=True, max_length=100)
    description: str = Field(max_length=500)
    parameter_schema: Dict[str, Any]
    application_domain: str = Field(default="todo")
    is_active: bool = Field(default=True)

class ToolMetadata(ToolMetadataBase, table=True):
    id: int = Field(primary_key=True)
    embedding: Optional[str] = Field(default=None)  # Vector embedding for semantic search
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Validation Rules**:
- `tool_name` must be unique
- `description` is required (up to 500 characters)
- `parameter_schema` must be valid JSON Schema
- `application_domain` defaults to "todo"
- `is_active` defaults to true
- `embedding` is optional (for semantic search)

### Tool Invocation Log Entity
```python
from sqlmodel import SQLModel, Field
from typing import Dict, Any, Optional

class ToolInvocationBase(SQLModel):
    tool_name: str = Field(max_length=100)
    parameters: Dict[str, Any]
    user_id: Optional[str] = Field(default=None, max_length=100)
    execution_time_ms: int
    result: Optional[Dict[str, Any]]
    error: Optional[str] = Field(default=None, max_length=1000)

class ToolInvocation(ToolInvocationBase, table=True):
    id: int = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

**Validation Rules**:
- `tool_name` is required (up to 100 characters)
- `parameters` must be valid JSON
- `execution_time_ms` must be non-negative
- `result` and `error` are mutually exclusive (both can be null for successful operations with no return data)

## Relationships

### Task Relationships
- No direct relationships required for the core Task entity

### Tool Metadata Relationships
- No direct relationships required for Tool Metadata entity

### Tool Invocation Relationships
- No direct relationships required for Tool Invocation entity

## State Transitions

### Task State Transitions
- `pending` → `completed` (via complete_task operation)
- Once `completed`, status remains `completed` (idempotent completion per FR-012)

## Indexing Strategy

### Task Table Indexes
- Primary index on `id`
- Secondary index on `status` for efficient filtering in `list_tasks`
- Secondary index on `created_at` for chronological ordering

### ToolMetadata Table Indexes
- Primary index on `id`
- Unique index on `tool_name`
- Index on `application_domain` and `is_active` for efficient tool discovery

### ToolInvocation Table Indexes
- Primary index on `id`
- Index on `tool_name` and `timestamp` for analytics
- Index on `user_id` for user-specific queries