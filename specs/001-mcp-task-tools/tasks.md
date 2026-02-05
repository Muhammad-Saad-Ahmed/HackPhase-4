# Tasks: MCP Task Management Tools

**Input**: Design documents from `/specs/001-mcp-task-tools/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not explicitly requested in specification. This is an implementation-focused task list.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story (MVP-first approach).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project type**: Web application (backend enhancement)
- **Backend root**: `backend/src/`
- **Tests root**: `backend/tests/`
- All tasks use absolute paths from repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and prepare MCP tool infrastructure

**Duration Estimate**: ~15 minutes

- [x] T001 Install Official MCP SDK dependency using UV: `cd backend && uv add mcp`
- [x] T002 Verify existing Task model at backend/src/models/task.py matches specification requirements (no modifications needed)
- [x] T003 Verify existing database session management at backend/src/core/database.py is functional
- [x] T004 Verify existing ResponseBuilder at backend/src/mcp_tools/base.py supports success and error responses

**Checkpoint**: Foundation verified - all existing infrastructure confirmed working

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create shared schemas and server infrastructure needed by ALL tools

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete

- [x] T005 Create Pydantic input/output schemas file at backend/src/mcp_tools/schemas.py with AddTaskInput, ListTasksInput, UpdateTaskInput, CompleteTaskInput, DeleteTaskInput, TaskOutput, DeletedTaskOutput classes
- [x] T006 Initialize MCP server file at backend/src/mcp_tools/server.py with Server instance creation and exports
- [x] T007 Create task tools module at backend/src/mcp_tools/task_tools.py with placeholder functions for add_task, list_tasks, update_task, complete_task, delete_task

**Checkpoint**: Schemas and server structure ready - tool implementations can now proceed in parallel

---

## Phase 3: User Story 1 - AI Agent Creates New Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable AI agents to create new tasks with title and optional description, returning created task with ID and timestamps

**Independent Test**: Invoke add_task tool with valid title and description, verify task is created in database with status="pending" and auto-generated ID and created_at timestamp

### Implementation for User Story 1

- [x] T008 [P] [US1] Implement add_task function in backend/src/mcp_tools/task_tools.py with input validation using AddTaskInput schema
- [x] T009 [P] [US1] Add database session acquisition using get_db_session() in add_task function
- [x] T010 [P] [US1] Implement Task creation logic in add_task with title, description, and status="pending"
- [x] T011 [P] [US1] Add session.add(), commit(), and refresh() calls in add_task function
- [x] T012 [P] [US1] Add ResponseBuilder.success() call returning TaskOutput in add_task function
- [x] T013 [P] [US1] Add try-except error handling with ResponseBuilder.error() for VALIDATION_ERROR and DATABASE_ERROR in add_task
- [x] T014 [US1] Register add_task tool with MCP server in backend/src/mcp_tools/server.py using @mcp_server.tool decorator
- [x] T015 [US1] Add add_task import and tool registration to server.py exports

**Acceptance Validation**:
- Create task with title only → Returns task with ID, status="pending", created_at timestamp, description=null
- Create task with title and description → Returns task with both fields populated
- Create task with empty title → Returns VALIDATION_ERROR
- Create task with title exceeding 255 chars → Returns VALIDATION_ERROR
- Create task with description exceeding 1000 chars → Returns VALIDATION_ERROR

**Checkpoint**: add_task tool fully functional - agents can create tasks and receive confirmation

---

## Phase 4: User Story 2 - AI Agent Retrieves Task Lists (Priority: P1) 🎯 MVP

**Goal**: Enable AI agents to query all tasks or filter by status, receiving tasks ordered by creation date (newest first)

**Independent Test**: Create multiple tasks with different statuses, invoke list_tasks with and without status filter, verify correct tasks returned in DESC order

### Implementation for User Story 2

- [x] T016 [P] [US2] Implement list_tasks function in backend/src/mcp_tools/task_tools.py with input validation using ListTasksInput schema
- [x] T017 [P] [US2] Add database session acquisition using get_db_session() in list_tasks function
- [x] T018 [P] [US2] Implement SQLModel select query with order_by(Task.created_at.desc()) in list_tasks
- [x] T019 [P] [US2] Add optional status filter using .where(Task.status == status) when status parameter provided
- [x] T020 [P] [US2] Execute query with await session.execute() and extract results with .scalars().all()
- [x] T021 [P] [US2] Convert task list to TaskOutput dictionaries in list_tasks function
- [x] T022 [P] [US2] Add ResponseBuilder.success() with task list and count message in list_tasks
- [x] T023 [P] [US2] Add try-except error handling with ResponseBuilder.error() for VALIDATION_ERROR (invalid status) and DATABASE_ERROR
- [x] T024 [US2] Register list_tasks tool with MCP server in backend/src/mcp_tools/server.py using @mcp_server.tool decorator
- [x] T025 [US2] Add list_tasks import and tool registration to server.py exports

**Acceptance Validation**:
- List all tasks without filter → Returns all tasks ordered by created_at DESC
- List tasks with status="pending" → Returns only pending tasks
- List tasks with status="completed" → Returns only completed tasks with completed_at timestamps
- List tasks when database is empty → Returns empty array with success=true
- List tasks with invalid status value → Returns VALIDATION_ERROR

**Checkpoint**: list_tasks tool fully functional - agents can query and filter tasks

---

## Phase 5: User Story 3 - AI Agent Updates Task Details (Priority: P2)

**Goal**: Enable AI agents to modify task title and/or description by ID, receiving updated task details

**Independent Test**: Create a task, invoke update_task with new title or description, verify changes persisted in database

### Implementation for User Story 3

- [x] T026 [P] [US3] Implement update_task function in backend/src/mcp_tools/task_tools.py with input validation using UpdateTaskInput schema
- [x] T027 [P] [US3] Add validation requiring at least one of title or description in update_task function
- [x] T028 [P] [US3] Add database session acquisition using get_db_session() in update_task function
- [x] T029 [P] [US3] Implement task lookup by ID using select(Task).where(Task.id == task_id) in update_task
- [x] T030 [P] [US3] Add NOT_FOUND error response when task does not exist in update_task
- [x] T031 [P] [US3] Update task.title and/or task.description fields when provided in update_task
- [x] T032 [P] [US3] Add session.commit() and refresh() calls in update_task function
- [x] T033 [P] [US3] Add ResponseBuilder.success() returning updated TaskOutput in update_task
- [x] T034 [P] [US3] Add try-except error handling for VALIDATION_ERROR, NOT_FOUND, and DATABASE_ERROR in update_task
- [x] T035 [US3] Register update_task tool with MCP server in backend/src/mcp_tools/server.py using @mcp_server.tool decorator
- [x] T036 [US3] Add update_task import and tool registration to server.py exports

**Acceptance Validation**:
- Update task title only → Title changes, description unchanged
- Update task description only → Description changes, title unchanged
- Update both title and description → Both fields change
- Update non-existent task ID → Returns NOT_FOUND error
- Update with empty title → Returns VALIDATION_ERROR
- Update with no title or description provided → Returns VALIDATION_ERROR

**Checkpoint**: update_task tool fully functional - agents can modify task details

---

## Phase 6: User Story 4 - AI Agent Marks Tasks Complete (Priority: P2)

**Goal**: Enable AI agents to mark tasks as completed, recording completion timestamp (idempotent operation)

**Independent Test**: Create pending task, invoke complete_task with ID, verify status changes to "completed" and completed_at timestamp is set

### Implementation for User Story 4

- [x] T037 [P] [US4] Implement complete_task function in backend/src/mcp_tools/task_tools.py with input validation using CompleteTaskInput schema
- [x] T038 [P] [US4] Add database session acquisition using get_db_session() in complete_task function
- [x] T039 [P] [US4] Implement task lookup by ID using select(Task).where(Task.id == task_id) in complete_task
- [x] T040 [P] [US4] Add NOT_FOUND error response when task does not exist in complete_task
- [x] T041 [P] [US4] Check if task.status is already "completed" and set appropriate message flag in complete_task
- [x] T042 [P] [US4] Set task.status = "completed" and task.completed_at = datetime.utcnow() in complete_task
- [x] T043 [P] [US4] Add session.commit() and refresh() calls in complete_task function
- [x] T044 [P] [US4] Add ResponseBuilder.success() with message indicating if task was already completed in complete_task
- [x] T045 [P] [US4] Add try-except error handling for VALIDATION_ERROR, NOT_FOUND, and DATABASE_ERROR in complete_task
- [x] T046 [US4] Register complete_task tool with MCP server in backend/src/mcp_tools/server.py using @mcp_server.tool decorator
- [x] T047 [US4] Add complete_task import and tool registration to server.py exports

**Acceptance Validation**:
- Complete pending task → Status becomes "completed", completed_at timestamp recorded
- Complete already-completed task → Operation succeeds idempotently with message "Task was already completed"
- Complete non-existent task ID → Returns NOT_FOUND error
- Verify completed_at is UTC timestamp in ISO 8601 format

**Checkpoint**: complete_task tool fully functional - agents can mark tasks complete

---

## Phase 7: User Story 5 - AI Agent Removes Obsolete Tasks (Priority: P3)

**Goal**: Enable AI agents to permanently delete tasks by ID, receiving deletion confirmation

**Independent Test**: Create a task, invoke delete_task with ID, verify task no longer exists in database via list_tasks

### Implementation for User Story 5

- [x] T048 [P] [US5] Implement delete_task function in backend/src/mcp_tools/task_tools.py with input validation using DeleteTaskInput schema
- [x] T049 [P] [US5] Add database session acquisition using get_db_session() in delete_task function
- [x] T050 [P] [US5] Implement task lookup by ID using select(Task).where(Task.id == task_id) in delete_task
- [x] T051 [P] [US5] Add NOT_FOUND error response when task does not exist in delete_task
- [x] T052 [P] [US5] Add session.delete(task) call in delete_task function
- [x] T053 [P] [US5] Add session.commit() call in delete_task function
- [x] T054 [P] [US5] Add ResponseBuilder.success() returning DeletedTaskOutput with task_id and deleted=True in delete_task
- [x] T055 [P] [US5] Add try-except error handling for VALIDATION_ERROR, NOT_FOUND, and DATABASE_ERROR in delete_task
- [x] T056 [US5] Register delete_task tool with MCP server in backend/src/mcp_tools/server.py using @mcp_server.tool decorator
- [x] T057 [US5] Add delete_task import and tool registration to server.py exports

**Acceptance Validation**:
- Delete existing task → Task removed from database, returns success with task_id and deleted=true
- Delete non-existent task → Returns NOT_FOUND error
- Verify deleted task does not appear in list_tasks results
- Verify attempting to update/complete/delete already-deleted task returns NOT_FOUND

**Checkpoint**: delete_task tool fully functional - agents can remove obsolete tasks

---

## Phase 8: Integration & Polish

**Purpose**: Integrate MCP server with FastAPI and add cross-cutting concerns

- [x] T058 Update backend/src/main.py to import mcp_server from backend/src/mcp_tools/server.py
- [x] T059 Add MCP server initialization to FastAPI startup event in backend/src/main.py
- [x] T060 [P] Add logging statements for tool invocations in backend/src/mcp_tools/task_tools.py (import logging, log tool name and inputs)
- [x] T061 [P] Verify all error messages do not leak sensitive information (review error detail fields)
- [x] T062 [P] Add input sanitization for title and description fields (strip leading/trailing whitespace) in schemas.py
- [x] T063 Run manual integration test: Start FastAPI server and verify MCP server is initialized without errors
- [x] T064 Run manual tool invocation test: Invoke each tool via MCP client or HTTP endpoint and verify structured responses
- [x] T065 [P] Add docstrings to all tool functions in backend/src/mcp_tools/task_tools.py with parameter descriptions and return types
- [x] T066 [P] Update backend/src/mcp_tools/__init__.py to export mcp_server and all tool functions

**Checkpoint**: MCP server integrated with FastAPI, all tools registered and functional

---

## Dependencies Between User Stories

**Visualization**:
```
Setup (Phase 1)
  ↓
Foundational (Phase 2: Schemas + Server)
  ↓
  ├─→ User Story 1 (add_task) ────────┐
  ├─→ User Story 2 (list_tasks) ──────┼─→ Can execute in parallel (independent)
  ├─→ User Story 3 (update_task) ─────┤
  ├─→ User Story 4 (complete_task) ───┤
  └─→ User Story 5 (delete_task) ─────┘
       ↓
  Integration & Polish (Phase 8)
```

**Story Independence**:
- **User Story 1** (add_task): No dependencies on other stories. Can be implemented and tested first.
- **User Story 2** (list_tasks): No dependencies on other stories. Can run in parallel with US1.
- **User Story 3** (update_task): No dependencies on other stories. Can run in parallel with US1, US2.
- **User Story 4** (complete_task): No dependencies on other stories. Can run in parallel with US1, US2, US3.
- **User Story 5** (delete_task): No dependencies on other stories. Can run in parallel with US1, US2, US3, US4.

**All user stories are independent and can be implemented in parallel after Phase 2 is complete.**

---

## Parallel Execution Examples

### Scenario 1: Single Developer (Sequential MVP)
1. Complete Phase 1-2 (Setup + Foundational)
2. Implement User Story 1 (add_task) - **MVP READY** ✅
3. Implement User Story 2 (list_tasks) - **Core functionality complete** ✅
4. Implement User Stories 3-5 as enhancements
5. Complete Phase 8 (Integration & Polish)

### Scenario 2: Team of 5 Developers (Parallel)
After Phase 2 completes:
- Dev 1: User Story 1 (T008-T015) - add_task
- Dev 2: User Story 2 (T016-T025) - list_tasks
- Dev 3: User Story 3 (T026-T036) - update_task
- Dev 4: User Story 4 (T037-T047) - complete_task
- Dev 5: User Story 5 (T048-T057) - delete_task

All stories merge independently, then Phase 8 integration by any developer.

### Scenario 3: Two-Phase Delivery
**Phase A (P1 Stories)**: Implement US1 + US2 first → Deploy as MVP
**Phase B (P2-P3 Stories)**: Add US3 + US4 + US5 later → Deploy as enhancement

---

## Implementation Strategy

### MVP-First Approach (Recommended)

**MVP Definition**: User Story 1 (add_task) + User Story 2 (list_tasks)

**Rationale**:
- US1 enables task creation (essential)
- US2 enables task querying (essential)
- Together they provide core task management value
- Update, complete, and delete are enhancements

**MVP Task Sequence**:
1. Phase 1: Setup (T001-T004)
2. Phase 2: Foundational (T005-T007)
3. Phase 3: User Story 1 (T008-T015) - add_task
4. Phase 4: User Story 2 (T016-T025) - list_tasks
5. Phase 8: Integration (T058-T066)

**Total MVP Tasks**: 42 tasks
**Estimated MVP Duration**: 2-3 hours for experienced developer

### Incremental Delivery

After MVP deployment, add remaining stories incrementally:
- **Iteration 2**: Add User Story 3 (update_task) for task editing
- **Iteration 3**: Add User Story 4 (complete_task) for task completion tracking
- **Iteration 4**: Add User Story 5 (delete_task) for task cleanup

Each iteration is independently testable and deployable.

---

## Task Summary

**Total Tasks**: 66 tasks
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 3 tasks
- Phase 3 (User Story 1 - P1): 8 tasks
- Phase 4 (User Story 2 - P1): 10 tasks
- Phase 5 (User Story 3 - P2): 11 tasks
- Phase 6 (User Story 4 - P2): 11 tasks
- Phase 7 (User Story 5 - P3): 10 tasks
- Phase 8 (Integration & Polish): 9 tasks

**Parallel Opportunities**: 52 tasks marked with [P] can run in parallel

**Story Distribution**:
- User Story 1 (add_task): 8 implementation tasks
- User Story 2 (list_tasks): 10 implementation tasks
- User Story 3 (update_task): 11 implementation tasks
- User Story 4 (complete_task): 11 implementation tasks
- User Story 5 (delete_task): 10 implementation tasks

**Independent Test Criteria** (per story):
- US1: Create task, verify in database with correct status and timestamps
- US2: Query tasks with/without filters, verify correct results and ordering
- US3: Update task, verify changes persisted
- US4: Complete task, verify status and timestamp changes (idempotent)
- US5: Delete task, verify removal from database

**MVP Scope**: User Story 1 + User Story 2 (18 implementation tasks + 7 setup/foundational + 9 integration = 34 tasks total)

---

## Validation Checklist

Before marking feature complete, verify:

- [x] All 5 tools registered with MCP server
- [x] Each tool returns structured responses (success/error format)
- [x] All error codes implemented (VALIDATION_ERROR, NOT_FOUND, DATABASE_ERROR, INTERNAL_ERROR)
- [x] Input validation enforces character limits (title ≤ 255, description ≤ 1000)
- [x] Database session properly acquired and closed in all tools
- [x] Timestamps auto-generated correctly (created_at, completed_at)
- [x] list_tasks returns results ordered by created_at DESC
- [x] complete_task is idempotent (no error on re-completion)
- [x] All tools are stateless (no memory between invocations)
- [x] MCP server integrates with FastAPI startup
- [x] Logging added for all tool invocations
- [x] No sensitive data in error messages
- [x] All tool functions have docstrings
- [x] All imports and exports in __init__.py are correct

---

## Notes

- **No tests required**: Specification does not explicitly request automated tests
- **Existing infrastructure reused**: Task model, database config, ResponseBuilder all from Phase I & II
- **No schema changes**: Task model remains unchanged
- **Stateless design**: All tools use database session dependency injection
- **Error handling**: Consistent error codes and structured responses across all tools
- **Performance**: Direct SQLModel queries, no ORM overhead beyond existing infrastructure
- **Idempotency**: complete_task operation is idempotent per specification

---

**Generated**: 2026-01-23
**Branch**: `001-mcp-task-tools`
**Ready for**: `/sp.implement` (task execution)
