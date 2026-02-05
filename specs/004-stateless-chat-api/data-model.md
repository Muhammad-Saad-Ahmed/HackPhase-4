# Data Model: Stateless Chat API & UI

**Feature**: 004-stateless-chat-api
**Date**: 2026-01-26
**Status**: Design Complete

## Overview

This document defines the data entities, relationships, and validation rules for the stateless chat API. All entities use SQLModel (Pydantic + SQLAlchemy) for type safety and database mapping.

## Entity Diagram

```
┌─────────────────────┐
│   User              │
│  (External)         │
│─────────────────────│
│ user_id: str (PK)   │
└──────────┬──────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────────────┐
│   Conversation                  │
│  (Implicit - no table)          │
│─────────────────────────────────│
│ conversation_id: str (PK)       │
│ user_id: str (FK)               │
│ created_at: datetime            │
└────────┬─────────────────┬──────┘
         │ 1:N             │ 1:1
         ▼                 ▼
┌────────────────────┐  ┌──────────────────────────┐
│  ChatMessage       │  │ ConversationMetadata     │
│────────────────────│  │──────────────────────────│
│ id: int (PK)       │  │ id: int (PK)             │
│ conversation_id:str│  │ conversation_id: str     │
│ user_id: str       │  │ metadata_json: str (JSON)│
│ message: str       │  │ updated_at: datetime     │
│ timestamp: datetime│  └──────────────────────────┘
└────────────────────┘
         │
         │ 1:1
         ▼
┌────────────────────┐
│  ChatResponse      │
│────────────────────│
│ id: int (PK)       │
│ conversation_id:str│
│ user_id: str       │
│ response: str      │
│ tool_calls: str    │
│ timestamp: datetime│
└────────────────────┘
```

## Entities

### 1. User (External Entity)

**Description**: Represents a user of the chat system. Managed externally; user_id is provided by caller.

**Note**: No User table exists in this feature. user_id is treated as an external identifier passed in API requests.

**Attributes**:
- `user_id` (string, 1-100 characters): Unique identifier for the user

**Validation Rules**:
- MUST be between 1 and 100 characters
- MUST NOT be empty or null

---

### 2. Conversation (Implicit Entity)

**Description**: Logical grouping of messages between a user and the AI assistant. Not a physical table; identified by conversation_id.

**Attributes**:
- `conversation_id` (string, 13 characters): Unique identifier, format: `conv_xxxxxxxx`
- `user_id` (string): Owner of the conversation
- `created_at` (datetime): Timestamp of first message

**Generation**:
```python
import uuid
from datetime import datetime

conversation_id = f"conv_{str(uuid.uuid4())[:8]}"
created_at = datetime.utcnow()
```

**Validation Rules**:
- conversation_id MUST match pattern: `^conv_[a-f0-9]{8}$`
- conversation_id MUST be unique across all conversations
- user_id MUST be associated with the conversation

**Relationships**:
- Has many ChatMessage (1:N)
- Has many ChatResponse (1:N)
- Has one ConversationMetadata (1:1)

---

### 3. ChatMessage (Existing Entity from Phase III-B)

**Description**: Represents a single user message in a conversation.

**Table**: `chat_message`

**Attributes**:
- `id` (int, Primary Key, Auto-increment): Unique identifier
- `conversation_id` (string, 100 chars, Indexed): Foreign key to conversation
- `user_id` (string, 100 chars): User who sent the message
- `message` (string, 1-10,000 chars): Message content
- `timestamp` (datetime, Auto-generated): When message was created

**SQLModel Definition** (Existing):
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class ChatMessage(SQLModel, table=True):
    id: int = Field(primary_key=True)
    conversation_id: str = Field(max_length=100, index=True)
    user_id: str = Field(max_length=100)
    message: str = Field(min_length=1, max_length=10000)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

**Validation Rules**:
- message MUST be between 1 and 10,000 characters
- conversation_id MUST be a valid conversation identifier
- user_id MUST match the conversation owner
- timestamp MUST be auto-generated (no manual override)

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` for efficient conversation retrieval
- Composite index on `(conversation_id, timestamp)` for ordered queries

---

### 4. ChatResponse (Existing Entity from Phase III-B)

**Description**: Represents an AI assistant response in a conversation.

**Table**: `chat_response`

**Attributes**:
- `id` (int, Primary Key, Auto-increment): Unique identifier
- `conversation_id` (string, 100 chars, Indexed): Foreign key to conversation
- `user_id` (string, 100 chars): User who received the response
- `response` (string, 1-10,000 chars): AI-generated response text
- `tool_calls` (string, JSON): Serialized list of tool calls made by agent
- `timestamp` (datetime, Auto-generated): When response was created

**SQLModel Definition** (Existing):
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import List, Dict, Any
import json

class ChatResponse(SQLModel, table=True):
    id: int = Field(primary_key=True)
    conversation_id: str = Field(max_length=100, index=True)
    response: str = Field(min_length=1, max_length=10000)
    tool_calls: str = Field(default="[]")  # JSON string
    user_id: str = Field(max_length=100)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def set_tool_calls(self, tool_calls_list: List[Dict[str, Any]]):
        self.tool_calls = json.dumps(tool_calls_list)

    def get_tool_calls(self) -> List[Dict[str, Any]]:
        return json.loads(self.tool_calls)
```

**Validation Rules**:
- response MUST be between 1 and 10,000 characters
- tool_calls MUST be valid JSON string
- conversation_id MUST be a valid conversation identifier
- user_id MUST match the conversation owner
- timestamp MUST be auto-generated

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` for efficient conversation retrieval
- Composite index on `(conversation_id, timestamp)` for ordered queries

---

### 5. ConversationMetadata (Existing Entity from Phase III-B)

**Description**: Stores metadata for conversations including task references for multi-turn flows.

**Table**: `conversation_metadata`

**Attributes**:
- `id` (int, Primary Key, Auto-increment): Unique identifier
- `conversation_id` (string, 100 chars, Unique Index): Foreign key to conversation
- `metadata_json` (string, JSON): Serialized metadata dictionary
- `updated_at` (datetime, Auto-updated): Last update timestamp

**SQLModel Definition** (Existing):
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import json

class ConversationMetadata(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(max_length=100, index=True, unique=True)
    metadata_json: str = Field(default="{}")
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def set_metadata(self, metadata: dict):
        self.metadata_json = json.dumps(metadata)
        self.updated_at = datetime.utcnow()

    def get_metadata(self) -> dict:
        try:
            return json.loads(self.metadata_json)
        except (json.JSONDecodeError, TypeError):
            return {}
```

**Metadata Structure** (JSON content):
```json
{
  "task_references": {
    "1": 42,
    "2": 43,
    "3": 44
  },
  "task_details": [
    {"position": "1", "id": 42, "title": "Buy groceries"},
    {"position": "2", "id": 43, "title": "Call dentist"}
  ],
  "referenced_at": "2026-01-26T10:30:00Z"
}
```

**Validation Rules**:
- conversation_id MUST be unique
- metadata_json MUST be valid JSON
- updated_at MUST be auto-updated on each metadata change

**Indexes**:
- Primary key on `id`
- Unique index on `conversation_id`

---

## Validation Rules Summary

### Cross-Entity Validation

1. **Conversation Integrity**:
   - All ChatMessage and ChatResponse rows for a conversation_id MUST have the same user_id
   - ConversationMetadata row MUST exist before storing metadata

2. **Ordering Constraints**:
   - Messages and responses MUST be retrievable in chronological order (timestamp ASC)
   - No gaps or out-of-order timestamps within a conversation

3. **Atomicity**:
   - User message + AI response MUST be stored atomically (database transaction)
   - Metadata updates MUST be atomic with tool execution results

### Field-Level Validation

| Field | Type | Min | Max | Required | Pattern |
|-------|------|-----|-----|----------|---------|
| user_id | string | 1 | 100 | Yes | Any non-empty string |
| conversation_id | string | 13 | 13 | Yes | `^conv_[a-f0-9]{8}$` |
| message | string | 1 | 10,000 | Yes | Any text |
| response | string | 1 | 10,000 | Yes | Any text |
| tool_calls | string (JSON) | 2 | ∞ | No | Valid JSON array |
| metadata_json | string (JSON) | 2 | ∞ | No | Valid JSON object |
| timestamp | datetime | - | - | Auto | ISO 8601 |

## State Transitions

### Conversation Lifecycle

```
[New Request] → conversation_id=null
    ↓
[Generate ID] → conversation_id=conv_xxxxxxxx
    ↓
[Store User Message] → ChatMessage row created
    ↓
[Process with Agent] → AgentRunner executes
    ↓
[Store AI Response] → ChatResponse row created
    ↓
[Update Metadata] → ConversationMetadata updated (if needed)
    ↓
[Return Response] → conversation_id returned to caller

[Existing Conversation] → conversation_id provided
    ↓
[Load History] → Query ChatMessage + ChatResponse WHERE conversation_id
    ↓
[Load Metadata] → Query ConversationMetadata WHERE conversation_id
    ↓
[Rebuild Context] → Combine history + metadata
    ↓
[Store User Message] → New ChatMessage row
    ↓
[Process with Agent] → AgentRunner executes with full context
    ↓
[Store AI Response] → New ChatResponse row
    ↓
[Update Metadata] → ConversationMetadata updated (if needed)
    ↓
[Return Response] → conversation_id returned to caller
```

### Message States

Messages do not have explicit state transitions - they are immutable once created. The conversation evolves by appending new messages and responses.

## Database Schema Compatibility

**Existing Schema**: All entities already exist from Phase III-A and Phase III-B
- ChatMessage: ✅ Deployed
- ChatResponse: ✅ Deployed
- ConversationMetadata: ✅ Deployed

**Changes Required**: NONE - all required tables and fields already exist

**Indexes Required**:
- ✅ `chat_message(conversation_id)` - Already exists
- ✅ `chat_response(conversation_id)` - Already exists
- ✅ `conversation_metadata(conversation_id)` - Already exists
- ⚠️ Recommended: Composite index on `(conversation_id, timestamp)` for both message tables (performance optimization)

## Frontend Data Types (TypeScript)

```typescript
// API Request/Response Types
export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: ToolCall[];
  reasoning_trace?: ReasoningTrace;
}

export interface ToolCall {
  tool_name: string;
  parameters: Record<string, any>;
  result: any;
}

export interface ReasoningTrace {
  intent: string;
  confidence: number;
  tool_selected: string | null;
  response_time_ms: number;
}

// Frontend Display Types
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string; // ISO 8601
  tool_calls?: ToolCall[];
}

export interface Conversation {
  conversation_id: string;
  messages: Message[];
}
```

## Migration Plan

**No migrations required** - all database schema already exists from previous phases.

**Verification Steps**:
1. Confirm `chat_message` table exists with all required columns
2. Confirm `chat_response` table exists with all required columns
3. Confirm `conversation_metadata` table exists with all required columns
4. Verify indexes on `conversation_id` columns
5. Test conversation_id generation and uniqueness

## Performance Considerations

### Query Optimization

1. **Conversation History Retrieval** (most frequent query):
   ```sql
   SELECT * FROM chat_message
   WHERE conversation_id = 'conv_abc12345'
   ORDER BY timestamp ASC
   LIMIT 50;

   SELECT * FROM chat_response
   WHERE conversation_id = 'conv_abc12345'
   ORDER BY timestamp ASC
   LIMIT 50;
   ```
   - Uses index on `conversation_id`
   - Expected: <100ms for 50 messages
   - Target: <1s for 1000 messages

2. **Metadata Retrieval**:
   ```sql
   SELECT * FROM conversation_metadata
   WHERE conversation_id = 'conv_abc12345'
   LIMIT 1;
   ```
   - Uses unique index on `conversation_id`
   - Expected: <10ms

### Scalability Targets

- Support 10,000+ conversations per day
- Handle conversations with 1000+ messages
- Maintain <1s query time for history retrieval
- Support 100+ concurrent requests without degradation

## References

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Validation](https://docs.pydantic.dev/latest/)
- [PostgreSQL Indexing Best Practices](https://www.postgresql.org/docs/current/indexes.html)
- Phase III-B Implementation: `backend/src/models/`
