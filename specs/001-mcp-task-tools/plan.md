# Implementation Plan: MCP Task Management Tools

**Branch**: `001-mcp-task-tools` | **Date**: 2026-01-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-mcp-task-tools/spec.md`

## Summary

Implement five stateless MCP tools (add_task, list_tasks, update_task, complete_task, delete_task) that expose task management operations to AI agents. Tools use the existing Task model and database infrastructure from Phase I & II, providing CRUD operations with structured responses. All state persists in Neon PostgreSQL via SQLModel. No AI logic is included in this layer - tools are pure interfaces between agents and the database.

**Key Technical Approach**: Direct SQLModel queries in async tool handlers registered with Official MCP SDK, leveraging existing database session management and response builders.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Official MCP SDK, FastAPI 0.100+, SQLModel 0.14+, Pydantic 2.x
**Storage**: Neon PostgreSQL (existing database, no schema changes)
**Testing**: pytest with async support, pytest-asyncio
**Target Platform**: Linux server (FastAPI backend)
**Project Type**: Web application (backend enhancement)
**Performance Goals**: <2s per tool operation, <1s list queries up to 10K tasks, <500ms error responses
**Constraints**: Stateless tools only, all state in database, no in-memory caching, reuse existing Task model
**Scale/Scope**: 5 MCP tools, ~600 LOC implementation, 10K tasks scale

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | spec.md complete with requirements, plan.md generated, tasks.md to follow |
| II. AI-Generated Code Only | ✅ PASS | All code will be AI-generated via /sp.implement |
| III. Reusable Intelligence | ✅ PASS | Tools designed as stateless, composable units for agent consumption |
| IV. Stateless Backend Architecture | ✅ PASS | Tools are completely stateless, no in-memory state |
| V. Database as Single Source of Truth | ✅ PASS | All task state persists in Neon PostgreSQL, no alternative storage |
| VI. MCP-Only Agent Interactions | ✅ PASS | All agent operations go through MCP tools, no direct API calls |
| VII. Official MCP SDK Mandate | ✅ PASS | Using Official MCP SDK for tool registration and handling |
| VIII. OpenAI Agents SDK Requirement | ⚠️ DEFERRED | Agent integration out of scope for this feature, tools prepare for it |
| IX. FastAPI Backend Framework | ✅ PASS | MCP server integrates with existing FastAPI application |
| X. SQLModel ORM Requirement | ✅ PASS | All database operations use SQLModel (existing Task model) |
| XI. ChatKit Frontend Framework | N/A | Frontend out of scope for this feature |
| XII. Better Auth Authentication | N/A | Authentication out of scope per specification |
| XIII. Tool Chaining Support | ✅ PASS | Tools return structured outputs suitable for chaining |
| XIV. Graceful Error Handling | ✅ PASS | All tools return structured errors with clear codes and messages |
| XV. Restart Resilience | ✅ PASS | Stateless tools survive restarts, all state in database |
| XVI. No Hardcoded Business Logic | ✅ PASS | Tools are configurable via inputs, no hardcoded task logic |

**Post-Phase 1 Re-check**: All principles remain PASS. No violations introduced during design phase.

## Project Structure

### Documentation (this feature)

```text
specs/001-mcp-task-tools/
├── spec.md              # Feature specification (completed by /sp.specify)
├── plan.md              # This file (completed by /sp.plan)
├── research.md          # Phase 0 output (design decisions)
├── data-model.md        # Phase 1 output (Task entity documentation)
├── quickstart.md        # Phase 1 output (developer guide)
├── contracts/           # Phase 1 output (JSON Schemas for each tool)
│   ├── add_task.json
│   ├── list_tasks.json
│   ├── update_task.json
│   ├── complete_task.json
│   ├── delete_task.json
│   └── README.md
├── checklists/          # Quality validation
│   └── requirements.md
└── tasks.md             # Phase 2 output (NOT created by /sp.plan - created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── mcp_tools/
│   │   ├── __init__.py           # Existing
│   │   ├── base.py               # Existing: BaseTool, ResponseBuilder
│   │   ├── schemas.py            # NEW: Pydantic models for tool I/O validation
│   │   ├── task_tools.py         # NEW: Tool handler implementations (add, list, update, complete, delete)
│   │   └── server.py             # NEW: MCP server initialization and tool registration
│   ├── models/
│   │   └── task.py               # Existing: Task SQLModel (NO CHANGES)
│   ├── core/
│   │   ├── database.py           # Existing: DB session management (NO CHANGES)
│   │   └── config.py             # Existing: Configuration (NO CHANGES)
│   └── main.py                   # Existing: FastAPI app (MINOR UPDATE to integrate MCP server)
└── tests/
    ├── mcp_tools/                 # NEW: Tool tests
    │   ├── test_add_task.py
    │   ├── test_list_tasks.py
    │   ├── test_update_task.py
    │   ├── test_complete_task.py
    │   └── test_delete_task.py
    └── conftest.py                # Existing: Test fixtures (MINOR UPDATE for async fixtures)

frontend/                          # OUT OF SCOPE (no changes)
```

**Structure Decision**: Web application structure selected. This feature adds MCP tools to the existing backend without modifying frontend. All new code resides in `backend/src/mcp_tools/` with corresponding tests in `backend/tests/mcp_tools/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. This table is empty.

## Phase 0: Research & Design Decisions

✅ **Completed**: See [research.md](./research.md)

**Key Decisions Made**:
1. **MCP Tool Contract Design**: JSON Schema-based with Pydantic model generation
2. **Error Signaling Format**: Structured error objects (success flag, error message, code, details)
3. **Tool Naming Convention**: snake_case with consistent parameters (task_id, status, title, description)
4. **MCP Server Initialization**: Async with database session dependency injection
5. **Database Access Layer**: Direct SQLModel queries (no repository abstraction)
6. **Tool Response Structure**: Unified success/error format via ResponseBuilder
7. **Input Validation Strategy**: Pydantic validation at tool boundary
8. **Timestamp Management**: Automatic via database defaults and tool logic
9. **List Query Behavior**: Optional status filter, created_at DESC ordering
10. **Idempotency**: complete_task is idempotent, others fail on constraint violations

All research questions resolved. No blockers to implementation.

## Phase 1: Design & Contracts

✅ **Completed**

### Artifacts Generated

1. **Data Model Documentation**: [data-model.md](./data-model.md)
   - Existing Task entity documented with validation rules
   - State transitions defined (pending ↔ completed)
   - Tool-to-entity mapping clarified
   - No schema changes required

2. **Tool Contracts**: [contracts/](./contracts/)
   - `add_task.json` - Create task schema
   - `list_tasks.json` - Query tasks schema
   - `update_task.json` - Modify task schema
   - `complete_task.json` - Complete task schema
   - `delete_task.json` - Delete task schema
   - `README.md` - Contract documentation

3. **Developer Quickstart**: [quickstart.md](./quickstart.md)
   - Step-by-step implementation guide
   - Code examples for all tools
   - Test templates
   - Common issues and solutions

### Agent Context Updated

✅ Claude Code context file updated with:
- Language: Python 3.11+
- Framework: FastAPI + Official MCP SDK
- Database: Neon PostgreSQL via SQLModel

## Key Architectural Decisions

### 1. Tool Interface Design

**Decision**: Use JSON Schema-based MCP tools with structured I/O

**Rationale**:
- Official MCP SDK requires JSON Schemas
- Enables AI agent introspection of tool capabilities
- Provides automatic input validation
- Type safety through Pydantic models

**Trade-offs**:
- Pro: Clear contracts, automatic validation, good agent UX
- Con: Additional schema maintenance overhead
- **Chosen**: Pros outweigh cons; schemas are essential for MCP

### 2. Error Handling Strategy

**Decision**: Structured error responses with machine-readable codes

**Format**:
```json
{
  "success": false,
  "error": "Task not found",
  "code": "NOT_FOUND",
  "details": {"task_id": 42}
}
```

**Rationale**:
- Agents need codes for intelligent error handling
- Details provide context for debugging
- Consistent format across all tools reduces complexity

**Error Code Taxonomy**:
- `VALIDATION_ERROR` - Input validation failures
- `NOT_FOUND` - Non-existent task IDs
- `DATABASE_ERROR` - Database operation failures
- `INTERNAL_ERROR` - Unexpected errors

### 3. Database Access Pattern

**Decision**: Direct SQLModel queries in tool handlers (no repository layer)

**Rationale**:
- Tools are simple CRUD operations
- Repository pattern adds unnecessary indirection
- Constitution requires SQLModel usage
- Existing codebase uses direct queries successfully

**Trade-offs**:
- Pro: Simple, direct, easy to maintain
- Con: Less abstraction for future changes
- **Chosen**: Simplicity wins for stateless tools

### 4. Stateless Design Implementation

**Decision**: Tools receive database session via dependency injection, no global state

**Implementation**:
```python
async for session in get_db_session():
    # Perform database operation
    # Session automatically closed after block
```

**Rationale**:
- Constitution mandates stateless backend
- Session-per-request ensures proper lifecycle
- Survives server restarts
- Horizontally scalable

### 5. Tool Response Format

**Decision**: Unified success/error structure using existing ResponseBuilder

**Success Structure**:
```json
{
  "success": true,
  "data": { /* tool-specific */ },
  "message": "Operation completed successfully"
}
```

**Rationale**:
- Consistent agent experience across tools
- Reuses existing ResponseBuilder class
- Clear success/failure distinction
- Human-readable messages for debugging

## Implementation Blueprint

### Files to Create

1. `backend/src/mcp_tools/schemas.py` (~150 LOC)
   - Pydantic models for all tool inputs and outputs
   - Validation rules matching database constraints

2. `backend/src/mcp_tools/task_tools.py` (~300 LOC)
   - Five async tool handler functions
   - Database operations using SQLModel
   - Error handling and response building

3. `backend/src/mcp_tools/server.py` (~80 LOC)
   - MCP server initialization
   - Tool registration with schemas
   - Integration with FastAPI lifecycle

4. `backend/tests/mcp_tools/test_*.py` (~500 LOC total)
   - Comprehensive tests for all tools
   - Edge case coverage
   - Database state verification

### Files to Modify

1. `backend/src/main.py` (~10 LOC added)
   - Import MCP server
   - Initialize on FastAPI startup
   - No breaking changes to existing routes

2. `backend/tests/conftest.py` (~20 LOC added)
   - Async test fixtures
   - Test database setup
   - MCP tool test helpers

### Dependencies to Add

```toml
[tool.uv.dependencies]
mcp = "^1.0.0"  # Official MCP SDK
```

All other dependencies (FastAPI, SQLModel, pytest, etc.) already present.

## Testing Strategy

### Unit Tests

**Scope**: Each tool tested independently with mocked database

**Coverage**:
- Valid inputs → Success responses
- Invalid inputs → Validation errors
- Non-existent IDs → NOT_FOUND errors
- Database errors → DATABASE_ERROR responses
- Edge cases (empty lists, idempotency, etc.)

### Integration Tests

**Scope**: End-to-end tool invocation with real database

**Coverage**:
- Create → List → Update → Complete → Delete workflow
- Concurrent tool invocations
- Database constraint enforcement
- Transaction rollback on errors

### Contract Tests

**Scope**: Verify tool responses match JSON Schemas

**Coverage**:
- Success response structure validation
- Error response structure validation
- Input schema adherence

### Performance Tests

**Scope**: Verify success criteria metrics

**Coverage**:
- List 10K tasks in <1 second (SC-003)
- Tool operations complete in <2 seconds (SC-004)
- Error responses in <500ms (SC-002)

## Performance & Scale Considerations

### Expected Load

- **Task Volume**: Up to 10,000 tasks
- **Concurrent Operations**: Moderate (standard FastAPI async capacity)
- **Query Frequency**: Typical AI agent interaction rates

### Optimization Strategies

1. **Database Indexing**:
   - Index on `status` for filtered queries
   - Index on `created_at DESC` for ordering
   - Note: Index creation out of scope but recommended for production

2. **Connection Pooling**:
   - Reuse existing async SQLAlchemy pool
   - No changes required

3. **Query Efficiency**:
   - Direct queries (no N+1 problems)
   - Minimal data transfer (<10K tasks × 600 bytes = ~6MB)

## Security Considerations

### Out of Scope (per specification)

- Authentication (no user identity)
- Authorization (no permission checks)
- Audit logging (no modification tracking)

### In Scope

- Input validation (SQL injection prevention)
- Error message safety (no sensitive data leakage)
- Database constraint enforcement

### Future Enhancements (when auth added)

- Add `user_id` foreign key to Task model
- Filter queries by authenticated user
- Prevent cross-user task access

## Deployment Considerations

### Requirements

- Python 3.11+ runtime
- Neon PostgreSQL accessible
- FastAPI server with async support
- MCP SDK installed via UV

### Configuration

- Database URL in environment variables (existing)
- No new configuration required
- MCP server runs within FastAPI process

### Monitoring

- Tool invocation logging (existing FastAPI logging)
- Error rate tracking (via structured error responses)
- Performance metrics (response times)

## Risk Analysis

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| MCP SDK API changes | High | Low | Pin SDK version, monitor changelog |
| Database connection exhaustion | Medium | Low | Reuse existing pool, proper session cleanup |
| Large result sets causing memory issues | Low | Very Low | Success criteria caps at 10K tasks (~6MB) |
| Concurrent updates causing inconsistencies | Low | Low | Documented edge case, acceptable for MVP |
| Tool registration failures on startup | Medium | Low | Comprehensive startup tests, error logging |

## Phase 2: Task Generation (Next Step)

**Command**: `/sp.tasks`

**Expected Output**: `tasks.md` with detailed implementation tasks including:
- Test-first approach for each tool
- Step-by-step implementation instructions
- Database state verification steps
- Acceptance criteria per task

**Prerequisites**: ✅ All met (spec, plan, research, data-model, contracts complete)

## Success Metrics (from Specification)

- **SC-001**: ✓ Tools designed for 100% success rate on valid inputs
- **SC-002**: ✓ Clear error messages with <500ms response time
- **SC-003**: ✓ List queries optimized for <1 second (10K tasks)
- **SC-004**: ✓ Tool operations designed for <2 second completion
- **SC-005**: ✓ Error handling covers all database constraint violations
- **SC-006**: ✓ Stateless design ensures zero data loss
- **SC-007**: ✓ All five tools specified and designed
- **SC-008**: ✓ Unified response format for predictable parsing

## References

- [Feature Specification](./spec.md) - Requirements and success criteria
- [Research & Decisions](./research.md) - Architectural choices and rationale
- [Data Model Documentation](./data-model.md) - Task entity and validation rules
- [Tool Contracts](./contracts/) - JSON Schemas for all tools
- [Developer Quickstart](./quickstart.md) - Implementation guide
- [Project Constitution](../../.specify/memory/constitution.md) - Governing principles
- [MCP SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

---

**Plan Status**: ✅ Complete
**Ready for**: `/sp.tasks` (task generation)
**Blockers**: None
