# Data Model: AI Agent & Chat Orchestration

**Feature**: 002-ai-agent-orchestration
**Created**: 2026-01-23
**Purpose**: Document data entities and relationships for agent conversation management

## Overview

This feature does NOT introduce new database tables. All data operations use existing infrastructure:
- **Tasks**: Existing `Task` model from Phase I & II (no modifications)
- **Conversations**: Existing conversation storage (enhanced metadata only)
- **Agent State**: Ephemeral (stateless), no persistence

The agent layer is purely orchestration - it reads from and writes to existing entities via MCP tools.

---

## Existing Entities (No Modifications)

### Task Entity
**Location**: `backend/src/models/task.py`
**Status**: ✅ Complete, no changes needed

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending")  # "pending" or "completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
```

**Agent Access**: Read and modify ONLY through MCP tools (add_task, list_tasks, update_task, complete_task, delete_task)

**Validation Rules**:
- Title: Required, 1-255 characters
- Description: Optional, ≤1000 characters
- Status: Enum ("pending", "completed")
- Timestamps: Auto-generated (created_at on creation, completed_at on completion)

---

## Enhanced Entities (Metadata Changes Only)

### Conversation Metadata Extension

**Location**: Existing conversation storage (structure varies by implementation)
**Change Type**: Add/enhance metadata JSON field

#### Existing Conversation Structure (Assumed)
```python
class Conversation:
    id: str  # Unique conversation ID
    user_id: str
    messages: List[Message]  # Message history
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict] = Field(default=None)  # ← Enhanced field
```

#### Enhanced Metadata Schema
```json
{
  "task_references": {
    "1": 42,  // Position 1 → Task ID 42
    "2": 43,  // Position 2 → Task ID 43
    "3": 44   // Position 3 → Task ID 44
  },
  "referenced_at": "2026-01-23T10:30:00Z",  // When list was displayed
  "last_tool_used": "list_tasks",
  "last_tool_parameters": {
    "status": "pending"
  },
  "agent_context": {
    "application_domain": "task_management",
    "confidence_history": [0.92, 0.85, 0.78],  // Last 3 confidence scores
    "clarification_count": 0
  }
}
```

#### Metadata Fields

| Field | Type | Purpose | Lifespan |
|-------|------|---------|----------|
| `task_references` | Object | Maps display position to task ID for reference resolution | Until next list_tasks or end of conversation |
| `referenced_at` | ISO 8601 | Timestamp when task list was displayed | Same as task_references |
| `last_tool_used` | String | Name of most recent MCP tool invoked | Session |
| `last_tool_parameters` | Object | Parameters used for last tool invocation | Session |
| `agent_context` | Object | Agent-specific state variables | Session |
| `agent_context.application_domain` | String | Domain for semantic tool search | Session |
| `agent_context.confidence_history` | Array | Last N confidence scores for threshold tuning | Session |
| `agent_context.clarification_count` | Integer | Number of clarifications asked this session | Session |

#### Task Reference Resolution Logic

```python
def resolve_task_reference(conversation_metadata: dict, user_reference: str) -> Optional[int]:
    """
    Resolve user's task reference to actual task ID.

    Args:
        conversation_metadata: Conversation metadata dict
        user_reference: User's reference string (e.g., "task 2", "the first one", "2")

    Returns:
        Task ID if found, None otherwise

    Examples:
        - "task 2" → 43 (if task_references["2"] = 43)
        - "the first one" → 42 (if task_references["1"] = 42)
        - "#3" → 44 (if task_references["3"] = 44)
    """
    task_refs = conversation_metadata.get("task_references", {})

    if not task_refs:
        return None

    # Handle numeric references: "task 2", "2", "#2"
    numeric_match = re.search(r'\d+', user_reference)
    if numeric_match:
        position = numeric_match.group()
        return task_refs.get(position)

    # Handle ordinal references: "the first one", "first task", "second"
    ordinals = {
        "first": "1",
        "second": "2",
        "third": "3",
        "fourth": "4",
        "fifth": "5",
        "last": str(len(task_refs))  # Dynamic based on list length
    }

    user_lower = user_reference.lower()
    for word, position in ordinals.items():
        if word in user_lower:
            return task_refs.get(position)

    return None
```

---

## Ephemeral Entities (Runtime Only, No Persistence)

### Agent Response
**Purpose**: Structure agent's output for consistent handling
**Lifespan**: Single request/response cycle

```python
class AgentResponse(BaseModel):
    conversation_id: str
    response: str  # Natural language response to user
    status: str  # "success", "clarification_needed", "confirmation_required", "error"
    tool_calls: List[ToolCall] = []  # MCP tools invoked
    reasoning_trace: Optional[str] = None  # For debugging/observability
```

#### Status Values

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `success` | Agent completed request successfully | Display response to user |
| `clarification_needed` | Agent needs more information | Display clarification question, wait for user answer |
| `confirmation_required` | Agent needs explicit yes/no confirmation | Display confirmation prompt, wait for user confirmation |
| `error` | Agent encountered unrecoverable error | Display user-friendly error message |

### Tool Call Record
**Purpose**: Track MCP tool invocations
**Lifespan**: Single request/response cycle (stored in conversation history)

```python
class ToolCall(BaseModel):
    tool_name: str  # e.g., "add_task", "list_tasks"
    parameters: dict  # Tool-specific parameters
    result: Optional[dict] = None  # Tool execution result
    error: Optional[str] = None  # Error message if tool failed
    invoked_at: datetime
```

### Intent Classification Result
**Purpose**: Capture LLM intent recognition output
**Lifespan**: Single request processing

```python
class IntentResult(BaseModel):
    intent_type: str  # "create", "list", "update", "complete", "delete"
    confidence: float  # 0.0 - 1.0
    entities: dict  # Extracted entities (e.g., {"title": "buy groceries"})
    alternatives: List[Tuple[str, float]] = []  # Alternative intents with confidence
    reasoning: Optional[str] = None  # LLM's reasoning (for debugging)
```

### Tool Selection Result
**Purpose**: Capture tool matching output
**Lifespan**: Single request processing

```python
class ToolSelectionResult(BaseModel):
    tool_name: str  # Selected MCP tool name
    confidence: float  # 0.0 - 1.0
    parameters: dict  # Extracted parameters for tool
    requires_confirmation: bool  # True for destructive operations
    alternatives: List[Tuple[str, float]] = []  # Alternative tools
```

---

## Data Flow

### 1. Task Creation Flow
```
User: "remind me to buy groceries"
  ↓
Intent Recognition → {intent: "create", confidence: 0.92, entities: {title: "buy groceries"}}
  ↓
Tool Selection → {tool: "add_task", parameters: {title: "buy groceries", description: null}}
  ↓
MCP Tool Invocation → add_task(title="buy groceries", description=null)
  ↓
Tool Result → {success: true, data: {id: 42, title: "buy groceries", status: "pending", ...}}
  ↓
Response Formatting → "I've added 'buy groceries' to your tasks. You got this!"
  ↓
Store in Conversation → messages.append({role: "assistant", content: "...", tool_calls: [...]})
```

### 2. Multi-Turn Flow (Task Reference Resolution)
```
User: "show my tasks"
  ↓
list_tasks() → Returns [task1{id:42}, task2{id:43}, task3{id:44}]
  ↓
Update Metadata → conversation.metadata.task_references = {"1": 42, "2": 43, "3": 44}
  ↓
Response → "Here are your tasks:\n1. Buy groceries\n2. Call John\n3. Review docs"
  ↓
Store in Conversation
___

User: "complete task 2"
  ↓
Resolve Reference → metadata.task_references["2"] = 43
  ↓
complete_task(task_id=43)
  ↓
Response → "Great! I've marked 'Call John' as completed ✓"
```

### 3. Clarification Flow
```
User: "update the meeting task"
  ↓
Intent Recognition → {intent: "update", confidence: 0.85, entities: {description: "meeting"}}
  ↓
Find Matching Tasks → Multiple tasks contain "meeting" (ambiguous)
  ↓
Generate Clarification → "I found 3 tasks about meetings. Which one did you mean?"
  ↓
Response → {status: "clarification_needed", clarification: {question: "...", options: [...]}}
___

User: "the first one"
  ↓
Resolve Selection → Option 1 selected
  ↓
update_task(task_id=selected_id, ...)
```

---

## Database Schema Impact

**No new tables required.**

**Migrations needed**:
- ❌ None (no schema changes)

**Metadata changes only**:
- ✅ Ensure conversation table has `metadata: JSONB` column (likely already exists)
- ✅ Add index on `metadata->>'task_references'` if query performance is concern (optional)

---

## Validation Rules

### Conversation Metadata Validation
```python
class ConversationMetadata(BaseModel):
    """Validation schema for conversation metadata."""

    task_references: Optional[Dict[str, int]] = Field(default=None)
    referenced_at: Optional[datetime] = Field(default=None)
    last_tool_used: Optional[str] = Field(default=None)
    last_tool_parameters: Optional[dict] = Field(default=None)
    agent_context: Optional[Dict[str, Any]] = Field(default=None)

    @validator('task_references')
    def validate_task_references(cls, v):
        if v is not None:
            # Keys must be numeric strings ("1", "2", "3", ...)
            for key, value in v.items():
                if not key.isdigit():
                    raise ValueError(f"Task reference key must be numeric string: {key}")
                if not isinstance(value, int):
                    raise ValueError(f"Task reference value must be integer: {value}")
        return v

    @validator('referenced_at')
    def validate_timestamp(cls, v, values):
        if v is not None and 'task_references' in values and values['task_references']:
            # Ensure timestamp exists if task_references exist
            if v is None:
                raise ValueError("referenced_at required when task_references present")
        return v
```

---

## State Management Rules

### Agent State (Ephemeral)
- ✅ **Never persist**: Agent instances are stateless
- ✅ **Load per request**: Context loaded from DB at request start
- ✅ **Store per response**: Results written to DB at request end
- ❌ **No in-memory state**: All state must be in PostgreSQL

### Conversation State (Persistent)
- ✅ **Store in database**: All conversation history in PostgreSQL
- ✅ **Include metadata**: Task references, context, tool history
- ✅ **TTL policy**: Auto-delete conversations >30 days old
- ✅ **Session-scoped**: Task references valid only within conversation

### Task State (Persistent)
- ✅ **MCP tools only**: Agent modifies tasks only via MCP tools
- ✅ **No direct access**: Agent never touches Task table directly
- ✅ **Audit trail**: All modifications logged via MCP tool invocations

---

## Performance Considerations

### Task Reference Lookup
- **Query**: `SELECT metadata FROM conversations WHERE id = ?`
- **Index**: Existing primary key index on `id` is sufficient
- **Cost**: O(1) lookup, negligible performance impact

### Conversation History Retrieval
- **Query**: `SELECT * FROM conversation_messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT 50`
- **Index**: Composite index on `(conversation_id, created_at)` recommended
- **Cost**: O(log n) with index, returns recent messages only

### Metadata Staleness
- **Problem**: Task references become invalid if tasks deleted outside conversation
- **Solution**: Verify task still exists before using referenced ID
- **Fallback**: If task not found, return NOT_FOUND error with helpful message

---

## Examples

### Example 1: Task Reference Storage
```python
# After list_tasks returns results
tasks = [
    {"id": 42, "title": "Buy groceries", "status": "pending"},
    {"id": 43, "title": "Call John", "status": "pending"},
    {"id": 44, "title": "Review docs", "status": "pending"}
]

# Store references in metadata
metadata = {
    "task_references": {
        "1": 42,
        "2": 43,
        "3": 44
    },
    "referenced_at": "2026-01-23T10:30:00Z",
    "last_tool_used": "list_tasks",
    "last_tool_parameters": {"status": "pending"}
}

# Update conversation
conversation_service.update_metadata(conversation_id, metadata)
```

### Example 2: Task Reference Resolution
```python
# User says "complete task 2"
conversation = conversation_service.get_conversation(conversation_id)
task_id = resolve_task_reference(conversation.metadata, "complete task 2")
# task_id = 43

# Invoke MCP tool with resolved ID
await mcp_client.call_tool("complete_task", {"task_id": task_id})
```

### Example 3: Stale Reference Handling
```python
# User says "update task 1" but task was deleted
conversation = conversation_service.get_conversation(conversation_id)
task_id = resolve_task_reference(conversation.metadata, "task 1")  # Returns 42

# Verify task still exists before using
try:
    result = await mcp_client.call_tool("update_task", {"task_id": task_id, ...})
except NotFoundError:
    return "I couldn't find task 1. It may have been deleted. Try 'show my tasks' to see what's current."
```

---

## Constitution Compliance

| Principle | Compliance | Implementation |
|-----------|------------|----------------|
| IV. Stateless Backend | ✅ | Agent instances are ephemeral, no in-memory state |
| V. Database as Source of Truth | ✅ | All conversation state in PostgreSQL |
| VI. MCP-Only Interactions | ✅ | Agent modifies tasks only via MCP tools |
| XV. Restart Resilience | ✅ | Stateless design survives server restarts |

---

**Data Model Complete**: No new tables, metadata enhancements only. Ready for contract generation.
