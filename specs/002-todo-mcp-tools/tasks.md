# Tasks: Todo MCP Tools

**Feature**: Todo MCP Tools  
**Branch**: `002-todo-mcp-tools`  
**Generated**: 2026-01-16  

## Implementation Strategy

Build the Todo MCP Tools server in phases, starting with the foundational components (setup, models, database), followed by user stories in priority order (P1-P4), and ending with polish and cross-cutting concerns. Each user story is designed to be independently testable and deliverable.

**MVP Scope**: User Story 1 (Create and View Tasks) - Implement the core functionality to add and list tasks, sufficient for basic agent interaction.

## Dependencies

- User Story 2 (Update Task Status) depends on User Story 1 (Create and View Tasks) - requires tasks to exist before they can be completed
- User Story 3 (Modify Task Details) depends on User Story 1 (Create and View Tasks) - requires tasks to exist before they can be updated
- User Story 4 (Remove Unwanted Tasks) depends on User Story 1 (Create and View Tasks) - requires tasks to exist before they can be deleted

## Parallel Execution Examples

Within each user story phase, many tasks can be executed in parallel:
- Multiple tool implementations (add_task, list_tasks, etc.) can be developed simultaneously
- Unit tests can be written in parallel with tool implementations
- Documentation can be updated alongside implementation

## Phase 1: Setup

Initialize the project structure and configure dependencies.

- [X] T001 Create backend directory structure per implementation plan
- [X] T002 Initialize Poetry project in backend directory with Python 3.11
- [X] T003 Add dependencies to pyproject.toml: FastAPI, SQLModel, Official MCP SDK, asyncpg, python-dotenv
- [X] T004 Create .env.example with required environment variables
- [X] T005 Create basic configuration module in backend/src/core/config.py
- [X] T006 Set up logging configuration in backend/src/core/logging.py
- [X] T007 Create entry point file backend/src/main.py

## Phase 2: Foundational Components

Build core infrastructure components that all user stories depend on.

- [X] T008 Define Task SQLModel in backend/src/models/task.py following data model specification
- [X] T009 Define ToolMetadata SQLModel in backend/src/models/tool_metadata.py following data model specification
- [X] T010 Define ToolInvocation SQLModel in backend/src/models/tool_invocation.py following data model specification
- [X] T011 Create database session management in backend/src/core/database.py
- [X] T012 Create base response models for success and error responses in backend/src/api/responses.py
- [X] T013 Implement database initialization and migration functions in backend/src/core/database.py
- [X] T014 Create base tool class for MCP tools in backend/src/mcp_tools/base.py

## Phase 3: User Story 1 - Create and View Tasks (Priority: P1)

An agent receives a user request like "Add a task to buy groceries" and needs to create a new task in the todo system, then confirm the action by retrieving the created task.

**Independent Test**: Can be fully tested by invoking `add_task` tool via MCP protocol, receiving a JSON response with task ID, then invoking `list_tasks` to verify the task appears in the list.

- [X] T015 [P] [US1] Create add_task MCP tool implementation in backend/src/mcp_tools/add_task_tool.py
- [X] T016 [P] [US1] Create list_tasks MCP tool implementation in backend/src/mcp_tools/list_tasks_tool.py
- [X] T017 [P] [US1] Create TaskService with add_task method in backend/src/services/task_service.py
- [X] T018 [P] [US1] Create TaskService with list_tasks method in backend/src/services/task_service.py
- [X] T019 [US1] Register add_task and list_tasks tools in tool registry
- [X] T020 [US1] Implement input validation for add_task tool according to contract
- [X] T021 [US1] Implement input validation for list_tasks tool according to contract
- [ ] T022 [US1] Test add_task functionality with valid inputs
- [ ] T023 [US1] Test list_tasks functionality with various filters
- [ ] T024 [US1] Test end-to-end workflow: add_task followed by list_tasks

## Phase 4: User Story 2 - Update Task Status (Priority: P2)

An agent receives a user request like "Mark task #3 as done" and needs to update the task's status to completed.

**Independent Test**: Can be fully tested by creating a task via `add_task`, invoking `complete_task` with the task ID, then verifying the task status changed to "completed" via `list_tasks`.

- [X] T025 [P] [US2] Create complete_task MCP tool implementation in backend/src/mcp_tools/complete_task_tool.py
- [X] T026 [P] [US2] Add complete_task method to TaskService in backend/src/services/task_service.py
- [X] T027 [US2] Register complete_task tool in tool registry
- [X] T028 [US2] Implement input validation for complete_task tool according to contract
- [X] T029 [US2] Ensure complete_task operation is idempotent as specified
- [ ] T030 [US2] Test complete_task functionality with valid task ID
- [ ] T031 [US2] Test complete_task with non-existent task ID (should return error)
- [ ] T032 [US2] Test complete_task on already completed task (should return success)
- [ ] T033 [US2] Test end-to-end workflow: add_task → complete_task → list_tasks

## Phase 5: User Story 3 - Modify Task Details (Priority: P3)

An agent receives a user request like "Change task #2 title to 'Buy organic groceries'" and needs to update the task's attributes.

**Independent Test**: Can be fully tested by creating a task via `add_task`, invoking `update_task` with new title/description, then verifying changes via `list_tasks`.

- [X] T034 [P] [US3] Create update_task MCP tool implementation in backend/src/mcp_tools/update_task_tool.py
- [X] T035 [P] [US3] Add update_task method to TaskService in backend/src/services/task_service.py
- [X] T036 [US3] Register update_task tool in tool registry
- [X] T037 [US3] Implement input validation for update_task tool according to contract
- [X] T038 [US3] Ensure update_task preserves unchanged fields as specified
- [ ] T039 [US3] Test update_task with title change only
- [ ] T040 [US3] Test update_task with description change only
- [ ] T041 [US3] Test update_task with both title and description changes
- [ ] T042 [US3] Test update_task with no fields to update (should return error)
- [ ] T043 [US3] Test update_task with non-existent task ID (should return error)
- [ ] T044 [US3] Test end-to-end workflow: add_task → update_task → list_tasks

## Phase 6: User Story 4 - Remove Unwanted Tasks (Priority: P4)

An agent receives a user request like "Delete task #5" and needs to permanently remove the task from the system.

**Independent Test**: Can be fully tested by creating a task via `add_task`, invoking `delete_task` with the task ID, then verifying task no longer appears in `list_tasks` response.

- [X] T045 [P] [US4] Create delete_task MCP tool implementation in backend/src/mcp_tools/delete_task_tool.py
- [X] T046 [P] [US4] Add delete_task method to TaskService in backend/src/services/task_service.py
- [X] T047 [US4] Register delete_task tool in tool registry
- [X] T048 [US4] Implement input validation for delete_task tool according to contract
- [X] T049 [US4] Ensure delete_task performs permanent deletion as specified
- [ ] T050 [US4] Test delete_task with valid task ID
- [ ] T051 [US4] Test delete_task with non-existent task ID (should return error)
- [ ] T052 [US4] Test end-to-end workflow: add_task → delete_task → list_tasks (task should not appear)

## Phase 7: Polish & Cross-Cutting Concerns

Finalize the implementation with logging, error handling, documentation, and tool discoverability features.

- [ ] T053 Implement logging for all tool invocations per requirement FR-018
- [ ] T054 Create tool invocation logging in backend/src/core/logging.py
- [ ] T055 Implement semantic search capability for tool discovery (requirements FR-013, FR-014, FR-015)
- [ ] T056 Add embeddings generation for tool descriptions using OpenAI API
- [ ] T057 Create tool registry with semantic search functionality
- [ ] T058 Implement comprehensive error handling with proper error codes per requirement FR-010
- [ ] T059 Add database connection error handling per edge case requirements
- [ ] T060 Add input validation for all edge cases mentioned in spec
- [ ] T061 Create comprehensive API documentation
- [ ] T062 Add performance monitoring to ensure 2-second execution limits per requirement FR-017
- [ ] T063 Write integration tests covering all user stories
- [ ] T064 Conduct end-to-end testing of all tool workflows
- [ ] T065 Update quickstart guide with new implementation details