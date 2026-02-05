# Feature Specification: Todo MCP Tools

**Feature Branch**: `002-todo-mcp-tools`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Expose Todo application capabilities as MCP tools consumable by reusable agents. Tools: add_task, list_tasks, complete_task, update_task, delete_task. Rules: One tool = one DB operation, No chaining inside tools, JSON-only responses"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and View Tasks (Priority: P1)

An agent receives a user request like "Add a task to buy groceries" and needs to create a new task in the todo system, then confirm the action by retrieving the created task.

**Why this priority**: This is the foundational capability - users must be able to add tasks and see their task list. Without this, the todo system is non-functional.

**Independent Test**: Can be fully tested by invoking `add_task` tool via MCP protocol, receiving a JSON response with task ID, then invoking `list_tasks` to verify the task appears in the list.

**Acceptance Scenarios**:

1. **Given** MCP server is running, **When** agent invokes `add_task` with title "Buy groceries", **Then** system returns JSON with new task ID and status "pending"
2. **Given** tasks exist in database, **When** agent invokes `list_tasks`, **Then** system returns JSON array of all tasks with id, title, status, created_at
3. **Given** task with id=5 exists, **When** agent invokes `list_tasks` with filter status="completed", **Then** system returns only completed tasks in JSON array

---

### User Story 2 - Update Task Status (Priority: P2)

An agent receives a user request like "Mark task #3 as done" and needs to update the task's status to completed.

**Why this priority**: Completing tasks is the primary workflow after creation. This delivers the core value proposition of a todo system (tracking completion).

**Independent Test**: Can be fully tested by creating a task via `add_task`, invoking `complete_task` with the task ID, then verifying the task status changed to "completed" via `list_tasks`.

**Acceptance Scenarios**:

1. **Given** pending task with id=3 exists, **When** agent invokes `complete_task` with task_id=3, **Then** system returns JSON with updated task showing status="completed" and completed_at timestamp
2. **Given** task with id=10 does not exist, **When** agent invokes `complete_task` with task_id=10, **Then** system returns JSON error with message "Task not found" and error code

---

### User Story 3 - Modify Task Details (Priority: P3)

An agent receives a user request like "Change task #2 title to 'Buy organic groceries'" and needs to update the task's attributes.

**Why this priority**: Users frequently need to edit task details after creation. This enhances usability but isn't critical for MVP.

**Independent Test**: Can be fully tested by creating a task via `add_task`, invoking `update_task` with new title/description, then verifying changes via `list_tasks`.

**Acceptance Scenarios**:

1. **Given** task with id=2 exists with title "Buy groceries", **When** agent invokes `update_task` with task_id=2 and title="Buy organic groceries", **Then** system returns JSON with updated task showing new title
2. **Given** task with id=7 exists, **When** agent invokes `update_task` with task_id=7 and description="New description", **Then** system returns JSON with updated task preserving original title and status

---

### User Story 4 - Remove Unwanted Tasks (Priority: P4)

An agent receives a user request like "Delete task #5" and needs to permanently remove the task from the system.

**Why this priority**: Task deletion is useful but not critical for MVP. Users can simply mark tasks as completed instead.

**Independent Test**: Can be fully tested by creating a task via `add_task`, invoking `delete_task` with the task ID, then verifying task no longer appears in `list_tasks` response.

**Acceptance Scenarios**:

1. **Given** task with id=5 exists, **When** agent invokes `delete_task` with task_id=5, **Then** system returns JSON success message and task is removed from database
2. **Given** task with id=5 does not exist, **When** agent invokes `delete_task` with task_id=5, **Then** system returns JSON error with message "Task not found"

---

### Edge Cases

- What happens when `add_task` is invoked with empty title?
- What happens when `list_tasks` is invoked on empty database?
- What happens when `complete_task` is invoked on already completed task?
- What happens when `update_task` is invoked with no fields to update?
- How does system handle concurrent updates to the same task?
- What happens when agent sends malformed JSON to a tool?
- How does system handle database connection failures during tool invocation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose `add_task` tool that accepts title (required) and description (optional) parameters and returns JSON with created task object containing id, title, description, status, created_at
- **FR-002**: System MUST expose `list_tasks` tool that returns JSON array of all tasks, with optional filtering by status parameter (pending/completed/all)
- **FR-003**: System MUST expose `complete_task` tool that accepts task_id parameter and updates task status to "completed" with completed_at timestamp, returning JSON with updated task object
- **FR-004**: System MUST expose `update_task` tool that accepts task_id (required) and optional fields (title, description) and returns JSON with updated task object
- **FR-005**: System MUST expose `delete_task` tool that accepts task_id parameter and permanently removes task from database, returning JSON success confirmation
- **FR-006**: Each tool MUST perform exactly one database operation (no chaining or multiple operations)
- **FR-007**: All tool responses MUST be valid JSON format with no HTML, plain text, or other formats
- **FR-008**: All tools MUST return error responses in JSON format with structure: `{"error": "message", "code": "ERROR_CODE"}`
- **FR-009**: System MUST validate all required parameters before database operations and return JSON error if missing
- **FR-010**: System MUST return appropriate error codes for: task not found (404), validation failures (400), database errors (500)
- **FR-011**: `add_task` MUST create tasks with default status "pending" and auto-generated created_at timestamp
- **FR-012**: `complete_task` MUST be idempotent - calling multiple times on same task returns success
- **FR-013**: Tool descriptions MUST include semantic keywords to enable agent discovery via semantic search (e.g., "create", "add", "new" for add_task)
- **FR-014**: Each tool MUST be registered in MCP tool registry with name, description, parameter schema
- **FR-015**: System MUST generate embeddings for tool descriptions to enable semantic similarity search
- **FR-016**: `list_tasks` MUST support pagination parameters (limit, offset) for large task lists
- **FR-017**: All tools MUST execute within 2 seconds for single-task operations
- **FR-018**: System MUST log all tool invocations with timestamp, tool_name, parameters, user_id, execution_time
- **FR-019**: Each tool MUST validate parameter types (e.g., task_id must be integer, title must be string)
- **FR-020**: System MUST persist all task data to database before returning success response

### Key Entities

- **Task**: Represents a todo item with attributes: id (unique identifier), title (task name, required), description (optional details), status (pending/completed), created_at (timestamp), completed_at (timestamp, null if pending)
- **Tool Metadata**: Represents MCP tool registration with attributes: tool_name (unique identifier), description (semantic-rich text for discovery), parameter_schema (JSON schema), application_domain ("todo"), embedding (vector for semantic search), is_active (boolean)
- **Tool Invocation**: Represents execution log with attributes: invocation_id, tool_name, parameters, user_id, execution_time_ms, result, error, timestamp

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Agents can successfully create tasks via `add_task` and receive task ID in under 1 second
- **SC-002**: Agents can retrieve task lists via `list_tasks` with 100+ tasks in under 2 seconds
- **SC-003**: All tool invocations return valid JSON responses (0% plain text or HTML responses)
- **SC-004**: Tool discovery via semantic search returns correct tool with confidence ≥0.85 for standard requests (e.g., "add a task" → `add_task`)
- **SC-005**: 100% of error scenarios return structured JSON error responses with appropriate error codes
- **SC-006**: System handles 50 concurrent tool invocations without failures or timeouts
- **SC-007**: Task completion workflow (add → complete → list) succeeds end-to-end with 100% consistency

## Dependencies *(mandatory)*

- Requires database schema for Task entity (id, title, description, status, created_at, completed_at)
- Requires MCP server implementation from 001-reusable-agents feature
- Requires tool registry with semantic search capability (pgvector embeddings)
- Requires SQLModel models and database session management
- Requires OpenAI API for embedding generation

## Assumptions *(mandatory)*

- Database connection is configured and available before tool registration
- MCP server is running and accessible at configured host:port
- OpenAI API key is configured for embedding generation
- Task IDs are auto-generated by database (sequence/auto-increment)
- Default status for new tasks is "pending"
- Task deletion is permanent (no soft delete or trash functionality)
- No user authentication required at tool level (handled by agent layer)
- Task ownership is managed via user_id parameter passed to tools
- Single-tenant design (no multi-organization support in this feature)
- Concurrent updates follow last-write-wins strategy (no optimistic locking)

## Out of Scope *(mandatory)*

- Task prioritization or ordering (high/medium/low priority)
- Task due dates or reminders
- Task categories or tags
- Task assignment to multiple users or teams
- Task comments or attachments
- Recurring tasks or templates
- Task dependencies or subtasks
- Bulk operations (delete multiple tasks, batch updates)
- Task history or audit trail
- Soft delete or task archive functionality
- Task search by text content (only status filtering)
- Task sharing or collaboration features
- Undo/redo operations
- Task import/export functionality
