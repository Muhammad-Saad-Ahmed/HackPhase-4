# Research & Design Decisions: MCP Task Management Tools

**Feature**: 001-mcp-task-tools
**Date**: 2026-01-23
**Phase**: 0 (Research)

## Executive Summary

This document captures all architectural and design decisions for implementing stateless MCP tools that expose task management operations to AI agents. All decisions align with project constitution requirements and build upon existing Phase I & II infrastructure.

## Research Areas & Decisions

### 1. MCP Tool Contract Design

**Decision**: Use JSON Schema-based tool definitions with typed input/output schemas

**Rationale**:
- Official MCP SDK requires JSON Schema for tool registration
- Provides automatic validation of tool inputs by the MCP runtime
- Enables AI agents to understand tool capabilities through schema introspection
- Type safety ensures consistent data exchange between agents and tools
- JSON Schema is widely supported and well-documented

**Alternatives Considered**:
- **Pydantic models only**: Rejected because MCP SDK expects JSON Schema format, not Python-specific types
- **Free-form dictionary responses**: Rejected due to lack of type safety and poor agent comprehension
- **Protocol Buffers**: Rejected as MCP SDK doesn't natively support protobuf schemas

**Implementation Approach**:
- Define Pydantic models for each tool's input and output
- Use `model_json_schema()` to generate JSON Schemas from Pydantic models
- Register schemas with MCP SDK during server initialization
- Maintain schema definitions in `backend/src/mcp_tools/schemas.py`

### 2. Error Signaling Format for MCP Tools

**Decision**: Use structured error objects with error codes, messages, and optional details

**Rationale**:
- AI agents need machine-readable error codes to make intelligent retry decisions
- Human-readable messages support debugging and logging
- Optional details field allows context-specific error information (e.g., which validation rule failed)
- Consistent error format across all tools reduces agent confusion
- Aligns with existing `ResponseBuilder.error()` pattern in codebase

**Alternatives Considered**:
- **Exception throwing**: Rejected because MCP tools must return responses, not raise exceptions to the agent
- **HTTP status codes only**: Rejected as MCP operates at a higher abstraction than HTTP
- **String error messages only**: Rejected due to lack of structure for programmatic handling

**Error Format**:
```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "details": {
    "field": "title",
    "constraint": "max_length",
    "limit": 255
  }
}
```

**Error Code Taxonomy**:
- `VALIDATION_ERROR`: Input validation failures (missing fields, format errors, constraint violations)
- `NOT_FOUND`: Requested task ID does not exist
- `DATABASE_ERROR`: Database connection or query failures
- `INTERNAL_ERROR`: Unexpected server errors

### 3. Tool Naming and Parameter Consistency

**Decision**: Use snake_case tool names with consistent parameter patterns across all operations

**Rationale**:
- Python conventions favor snake_case for function names
- Consistency reduces cognitive load for AI agents
- Common parameters (e.g., `task_id`) use identical names across tools
- Predictable naming enables agents to infer tool capabilities

**Naming Convention**:
- Tool names: `add_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`
- ID parameter: Always named `task_id` (never `id`, `taskId`, or `task_identifier`)
- Status filter: Always named `status` with allowed values `["pending", "completed", null]`
- Text fields: `title` and `description` (consistent with database schema)

**Alternatives Considered**:
- **CamelCase**: Rejected as it conflicts with Python naming conventions
- **Verbose names**: Rejected (e.g., `create_new_task` vs `add_task`) as brevity aids agent invocation
- **REST-style naming**: Rejected (e.g., `POST /tasks`) as MCP uses tool names, not HTTP verbs

### 4. MCP Server Initialization Pattern

**Decision**: Use async initialization with dependency injection for database session

**Rationale**:
- MCP SDK supports async tool handlers (essential for async database operations)
- Dependency injection of database session ensures proper connection lifecycle
- Stateless tool design requires database session to be created per-request
- Aligns with existing FastAPI patterns in the codebase
- Enables proper error handling and transaction management

**Initialization Flow**:
1. Import MCP SDK and register server instance
2. Define tool schemas using Pydantic models
3. Register each tool with its schema and async handler function
4. In each handler, acquire database session via `get_db_session()` dependency
5. Execute database operation within try-except block
6. Return structured success or error response

**Alternatives Considered**:
- **Singleton database connection**: Rejected as it violates stateless requirement and creates connection pooling issues
- **Synchronous tools**: Rejected because SQLModel with async SQLAlchemy requires async/await
- **Global session**: Rejected as it creates state between tool invocations

### 5. Database Access Layer Design

**Decision**: Direct SQLModel queries in tool handlers with no additional repository layer

**Rationale**:
- Constitution mandates SQLModel as ORM
- Tools are simple CRUD operations that don't justify repository abstraction
- Direct queries reduce complexity and indirection
- Existing codebase (Phase I & II) uses direct SQLModel queries successfully
- Repository pattern adds cognitive overhead without providing value for stateless tools

**Query Patterns**:
- **Create**: `session.add(task)`, `await session.commit()`, `await session.refresh(task)`
- **Read**: `await session.exec(select(Task).where(...))` with filters
- **Update**: Fetch task, modify attributes, `await session.commit()`
- **Delete**: `await session.delete(task)`, `await session.commit()`

**Alternatives Considered**:
- **Repository pattern**: Rejected as unnecessary abstraction for simple CRUD (would violate complexity principle)
- **Service layer**: Rejected as tools are already the service boundary for agents
- **Raw SQL**: Rejected as constitution requires SQLModel usage

### 6. Tool Response Schema Structure

**Decision**: Unified response structure with success flag and conditional data/error fields

**Rationale**:
- Consistent structure enables predictable agent parsing
- Success flag allows quick determination of operation outcome
- Conditional fields reduce response size (either `data` or `error`, not both)
- Aligns with existing `ResponseBuilder` pattern in codebase

**Success Response**:
```json
{
  "success": true,
  "data": {
    "id": 42,
    "title": "Review documentation",
    "description": "Check for completeness",
    "status": "pending",
    "created_at": "2026-01-23T12:00:00Z",
    "completed_at": null
  },
  "message": "Task created successfully"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Task not found",
  "code": "NOT_FOUND",
  "details": {"task_id": 99}
}
```

### 7. Input Validation Strategy

**Decision**: Pydantic model validation at tool boundary with immediate error responses

**Rationale**:
- Pydantic provides declarative validation rules matching database constraints
- Early validation prevents database errors and provides clear feedback
- Validation rules centralized in schema definitions
- Automatic JSON Schema generation from Pydantic models

**Validation Rules** (matching Task model constraints):
- `title`: Required, 1-255 characters
- `description`: Optional, max 1000 characters
- `status`: Must be "pending" or "completed" (for filters)
- `task_id`: Must be positive integer

**Alternatives Considered**:
- **Database-only validation**: Rejected as it produces cryptic constraint violation errors
- **Manual validation**: Rejected as Pydantic provides better ergonomics and maintainability
- **Separate validation layer**: Rejected as unnecessary - Pydantic handles it at the schema level

### 8. Timestamp Management

**Decision**: Automatic timestamp generation using database defaults and tool-level logic

**Rationale**:
- `created_at` handled by database default (`Field(default_factory=datetime.utcnow)`)
- `completed_at` set explicitly in `complete_task` tool when status changes
- Automatic timestamps prevent inconsistencies from manual management
- UTC timestamps ensure timezone consistency

**Implementation**:
- Create: Database sets `created_at` automatically
- Complete: Tool sets `completed_at = datetime.utcnow()` when marking complete
- Update: Timestamps remain unchanged (only title/description modified)

**Alternatives Considered**:
- **Client-provided timestamps**: Rejected as stateless tools shouldn't trust client time
- **Trigger-based timestamps**: Rejected as SQLModel doesn't natively support DB triggers
- **Separate timestamp update tool**: Rejected as overly granular and violates YAGNI principle

### 9. List Query Filtering and Ordering

**Decision**: Optional status filter with default created_at DESC ordering

**Rationale**:
- Most recent tasks typically most relevant to agents and users
- Status filter enables focused queries (pending vs completed tasks)
- Descending order (newest first) is standard for activity streams
- Single optional filter parameter keeps tool interface simple

**Query Behavior**:
- No filter: Return all tasks ordered by `created_at DESC`
- `status="pending"`: Return only pending tasks ordered by `created_at DESC`
- `status="completed"`: Return only completed tasks ordered by `created_at DESC`

**Alternatives Considered**:
- **Multiple filters** (date range, text search): Rejected as out of scope per spec
- **Configurable ordering**: Rejected as unnecessary complexity for MVP
- **Pagination**: Rejected as not required by success criteria (1 second for 10K tasks)

### 10. Idempotency Considerations

**Decision**: Complete operation is idempotent; other operations fail on constraint violations

**Rationale**:
- Completing an already-completed task is safe and aligns with user intent
- Creating duplicate tasks should fail (no unique constraint, but intentional)
- Update and delete operations naturally idempotent through ID-based targeting
- Clear failure on non-idempotent operations prevents silent data corruption

**Idempotency Behavior**:
- `complete_task`: Re-completing a completed task succeeds (updates `completed_at` to current time)
- `add_task`: Always creates new task (no uniqueness constraint on title)
- `update_task`: Fails with NOT_FOUND if task doesn't exist
- `delete_task`: Fails with NOT_FOUND if task doesn't exist (could be made idempotent, but explicit failure aids debugging)

**Alternatives Considered**:
- **All operations idempotent**: Rejected as delete/update idempotency can mask errors
- **Upsert pattern for updates**: Rejected as spec doesn't require it
- **Title-based deduplication**: Rejected as spec doesn't require uniqueness

## Technology Stack Validation

### Required by Constitution

✅ **Official MCP SDK**: Used for tool registration and request handling
✅ **SQLModel ORM**: Used for all database operations
✅ **Neon PostgreSQL**: Existing database (no changes required)
✅ **FastAPI**: Existing backend framework (tools integrate with it)
✅ **Stateless architecture**: Tools have no memory between invocations

### Performance Expectations

- **Tool execution time**: <2 seconds per operation (per success criteria SC-004)
- **List query performance**: <1 second for up to 10,000 tasks (per success criteria SC-003)
- **Error response time**: <500ms (per success criteria SC-002)
- **Database connection**: Reuse existing async connection pool (no new config)

### Integration Points

- **Existing Task model**: `backend/src/models/task.py` - No modifications required
- **Existing database config**: `backend/src/core/database.py` - Reuse `get_db_session()`
- **Existing MCP base classes**: `backend/src/mcp_tools/base.py` - Extend `BaseTool` and use `ResponseBuilder`

## Open Questions Resolved

1. **Q**: Should tools support batch operations (e.g., delete multiple tasks)?
   **A**: No - Out of scope per specification. Single-operation tools sufficient for MVP.

2. **Q**: How should concurrent updates to the same task be handled?
   **A**: Database-level pessimistic locking not required. Last-write-wins acceptable for MVP. Edge case documented in spec.

3. **Q**: Should list_tasks support pagination?
   **A**: No - Success criteria specifies <1 second for 10K tasks. Pagination unnecessary for MVP scale.

4. **Q**: Should task IDs be UUIDs or integers?
   **A**: Integers - Existing Task model uses `id: int = Field(primary_key=True)`. No change required.

5. **Q**: Should tools support undo/redo operations?
   **A**: No - Out of scope. Task history/audit logging explicitly excluded from specification.

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| MCP SDK API changes | High | Pin SDK version in dependencies; monitor changelog |
| Database connection pool exhaustion | Medium | Reuse existing pool config; tools properly close sessions |
| Large result sets causing memory issues | Low | Success criteria caps at 10K tasks; acceptable for RAM |
| Concurrent task updates causing inconsistencies | Low | Documented edge case; acceptable for MVP; can add optimistic locking later |
| Validation bypass via direct DB access | Low | Tools are only agent interface; backend API has separate validation |

## Next Steps

With all research complete, proceed to **Phase 1: Design & Contracts**:
1. Generate `data-model.md` (reuse existing Task model, document relationships)
2. Generate tool contract schemas in `contracts/` directory
3. Create `quickstart.md` for developer onboarding
4. Update agent context with MCP SDK and tool patterns
