# Data Model: MCP Task Management Tools

**Feature**: 001-mcp-task-tools
**Date**: 2026-01-23
**Phase**: 1 (Design & Contracts)

## Overview

This document defines the data model for MCP Task Management Tools. The feature reuses the existing Task entity from Phase I & II with no schema modifications required. This document serves to clarify the entity's role within the MCP tool context and document validation rules enforced at the tool layer.

## Entity: Task

**Purpose**: Represents an action item or to-do that can be managed by AI agents through MCP tools.

**Source**: Existing model defined in `backend/src/models/task.py`

**Database Table**: `task`

### Schema

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Generated | Unique identifier for the task |
| `title` | String | Required, 1-255 characters | None | Short description of the task |
| `description` | String | Optional, max 1000 characters | NULL | Detailed context or notes for the task |
| `status` | String | Required, enum: "pending" or "completed" | "pending" | Current state of the task |
| `created_at` | DateTime | Required, Auto-generated | `datetime.utcnow()` | UTC timestamp when task was created |
| `completed_at` | DateTime | Optional | NULL | UTC timestamp when task was marked complete |

### Validation Rules

**Tool-Layer Validation** (enforced by Pydantic schemas before database):

1. **Title** (FR-001):
   - Must not be empty (min_length=1)
   - Must not exceed 255 characters (max_length=255)
   - Leading/trailing whitespace should be trimmed

2. **Description** (FR-001):
   - Optional field (can be NULL)
   - If provided, must not exceed 1000 characters (max_length=1000)
   - Leading/trailing whitespace should be trimmed

3. **Status** (FR-002, FR-004):
   - Must be exactly "pending" or "completed"
   - Case-sensitive (lowercase only)
   - Used for filtering in list operations

4. **Task ID** (FR-003, FR-004, FR-005):
   - Must be positive integer
   - Validated before database lookup to prevent SQL errors

**Database-Layer Validation** (enforced by SQLModel):
- `id`: Primary key constraint ensures uniqueness
- `title`: NOT NULL constraint
- `status`: Regex validation `^(pending|completed)$` enforces allowed values
- `created_at`: NOT NULL constraint ensures all tasks have creation timestamp

### State Transitions

Tasks follow a simple two-state lifecycle:

```
┌─────────┐                          ┌───────────┐
│ pending │  ── complete_task() ──>  │ completed │
└─────────┘                          └───────────┘
     │                                      │
     │                                      │
     └──── Can be updated or deleted ───────┘
```

**Allowed Transitions**:
- `pending → completed`: Via `complete_task` tool (sets `completed_at`)
- `completed → completed`: Idempotent via `complete_task` tool (updates `completed_at`)

**No Transitions**:
- `completed → pending`: Not supported (tasks cannot be "un-completed")

**State-Independent Operations**:
- `update_task`: Modifies `title` or `description` regardless of status
- `delete_task`: Removes task regardless of status

### Indexes

**Existing Indexes** (from Phase I & II schema):
- Primary key index on `id` (automatic)

**Recommended Indexes** (for query performance):
- Index on `status` for efficient filtering in `list_tasks`
- Index on `created_at DESC` for efficient ordering in `list_tasks`

**Note**: Index creation is out of scope for this feature but recommended for production deployment.

### Relationships

**None**: The Task entity has no foreign key relationships in this feature. It is a standalone entity with no references to users, projects, or other entities.

**Future Considerations** (out of current scope):
- User assignment (e.g., `user_id` foreign key to User table)
- Project membership (e.g., `project_id` foreign key to Project table)
- Tags or categories (many-to-many relationship via junction table)

## Tool-to-Entity Mapping

| MCP Tool | Primary Entity | Operation | Affected Fields |
|----------|----------------|-----------|-----------------|
| `add_task` | Task | CREATE | Sets: `title`, `description`, `status="pending"`, `created_at` (auto) |
| `list_tasks` | Task | READ (query) | Filters on: `status` (optional). Returns all fields. Orders by: `created_at DESC` |
| `update_task` | Task | UPDATE | Modifies: `title` and/or `description`. Preserves: `id`, `status`, timestamps |
| `complete_task` | Task | UPDATE | Modifies: `status="completed"`, `completed_at` (set to now). Preserves: `id`, `title`, `description`, `created_at` |
| `delete_task` | Task | DELETE | Removes entire Task record |

## Data Integrity Constraints

### Application-Level Constraints (Enforced by Tools)

1. **Character Limits** (FR-001, FR-006):
   - Title: 1-255 characters (validated by Pydantic)
   - Description: 0-1000 characters (validated by Pydantic)

2. **Status Values** (FR-002, FR-004):
   - Only "pending" or "completed" allowed (validated by Pydantic and SQLModel regex)

3. **Task ID Validation** (FR-009):
   - Must exist before update/complete/delete operations
   - Non-existent IDs return clear NOT_FOUND error

4. **Timestamp Consistency** (FR-010, FR-011):
   - `created_at` always set on creation (database default)
   - `completed_at` only set when status becomes "completed"
   - `completed_at` is NULL for pending tasks

### Database-Level Constraints (Enforced by PostgreSQL)

1. **Primary Key**: `id` must be unique and NOT NULL
2. **NOT NULL**: `title`, `status`, `created_at` must have values
3. **Check Constraint**: `status` must match regex `^(pending|completed)$`

## Data Flow Example

### Creating a Task

```
Agent Request:
{
  "title": "Review documentation",
  "description": "Check API docs for completeness"
}

Tool Validation:
- title length: 20 chars ✓
- description length: 36 chars ✓

Database Insert:
INSERT INTO task (title, description, status, created_at)
VALUES ('Review documentation', 'Check API docs...', 'pending', NOW())
RETURNING id, title, description, status, created_at, completed_at

Tool Response:
{
  "success": true,
  "data": {
    "id": 42,
    "title": "Review documentation",
    "description": "Check API docs for completeness",
    "status": "pending",
    "created_at": "2026-01-23T14:30:00Z",
    "completed_at": null
  },
  "message": "Task created successfully"
}
```

### Completing a Task

```
Agent Request:
{
  "task_id": 42
}

Database Query:
SELECT * FROM task WHERE id = 42

Database Update:
UPDATE task
SET status = 'completed', completed_at = NOW()
WHERE id = 42
RETURNING id, title, description, status, created_at, completed_at

Tool Response:
{
  "success": true,
  "data": {
    "id": 42,
    "title": "Review documentation",
    "description": "Check API docs for completeness",
    "status": "completed",
    "created_at": "2026-01-23T14:30:00Z",
    "completed_at": "2026-01-23T15:45:00Z"
  },
  "message": "Task marked as completed"
}
```

### Listing Tasks with Filter

```
Agent Request:
{
  "status": "pending"
}

Database Query:
SELECT * FROM task
WHERE status = 'pending'
ORDER BY created_at DESC

Tool Response:
{
  "success": true,
  "data": [
    {
      "id": 43,
      "title": "Update tests",
      "description": null,
      "status": "pending",
      "created_at": "2026-01-23T16:00:00Z",
      "completed_at": null
    },
    {
      "id": 41,
      "title": "Fix bug in parser",
      "description": "Handle edge case with empty strings",
      "status": "pending",
      "created_at": "2026-01-23T12:00:00Z",
      "completed_at": null
    }
  ],
  "message": "Found 2 pending tasks"
}
```

## Performance Considerations

### Query Performance

**Expected Load** (from Success Criteria):
- List queries should complete in <1 second for up to 10,000 tasks (SC-003)
- Individual operations should complete in <2 seconds (SC-004)

**Optimization Strategies**:
1. **Indexing**: Status and created_at indexes crucial for list performance
2. **Connection Pooling**: Reuse existing async SQLAlchemy pool
3. **Minimal Projections**: Return all fields (no SELECT * optimization needed for <10K scale)
4. **Eager Loading**: Not applicable (no relationships)

### Storage Estimates

**Per-Task Storage**:
- `id`: 4 bytes (integer)
- `title`: 1-255 bytes (variable)
- `description`: 0-1000 bytes (variable)
- `status`: ~8 bytes (VARCHAR(10))
- `created_at`: 8 bytes (timestamp)
- `completed_at`: 8 bytes (timestamp, nullable)

**Average**: ~600 bytes per task (assuming 100-char title, 200-char description)

**10,000 Tasks**: ~6 MB (well within PostgreSQL's efficient range)

## Security Considerations

**Out of Scope for This Feature** (per specification):
- Authentication: No user identity verification
- Authorization: No permission checks
- Audit Logging: No record of who modified what

**Data Validation Security**:
- Input length limits prevent buffer overflow and DOS attacks
- SQL injection prevented by SQLModel parameter binding
- No user-provided SQL or dynamic queries

**Future Enhancements** (when authentication added):
- Add `user_id` foreign key to Task model
- Filter list queries by authenticated user
- Prevent users from modifying others' tasks

## Migration Strategy

**No Migration Required**: This feature reuses the existing Task model without modifications.

**Verification Steps**:
1. Confirm Task table exists in database
2. Verify schema matches model definition
3. Test that existing task records are accessible via tools
4. Confirm no data migration or schema changes needed

## Summary

The Task entity is simple, well-defined, and requires no modifications for MCP tool integration. All validation rules, state transitions, and data flows are clear and testable. The model's simplicity aligns with the stateless tool design and constitution principles.
