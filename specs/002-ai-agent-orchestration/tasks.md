# Tasks: AI Agent & Chat Orchestration

**Input**: Design documents from `/specs/002-ai-agent-orchestration/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

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

**Purpose**: Install dependencies and prepare agent infrastructure

**Duration Estimate**: ~20 minutes

- [x] T001 Install OpenAI Agents SDK dependency using UV: `cd backend && uv add openai-agents`
- [x] T002 Verify existing MCP server from Phase III-A is running and all 5 tools are functional
- [x] T003 Verify existing chat endpoint at backend/src/api/chat_endpoint.py is functional
- [x] T004 Verify existing AgentRunner at backend/src/services/agent_runner.py structure exists
- [x] T005 Verify existing LLMClient at backend/src/services/llm_client.py is functional
- [x] T006 Verify existing MCPTaskExecutor at backend/src/services/mcp_client.py is functional
- [x] T007 Verify existing ConversationService at backend/src/services/conversation_service.py is functional

**Checkpoint**: Foundation verified - all existing infrastructure confirmed working

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create shared services needed by ALL user stories

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete

- [x] T008 [P] Create response formatter service at backend/src/services/response_formatter.py with template-based response generation
- [x] T009 [P] Create error humanizer service at backend/src/services/error_humanizer.py with error translation functionality
- [x] T010 [P] Create task reference resolver service at backend/src/services/task_reference_resolver.py with reference resolution logic
- [x] T011 [P] Update conversation service at backend/src/services/conversation_service.py with metadata management methods (get_metadata, update_metadata)
- [x] T012 Update backend/src/core/config.py to add OpenAI API key setting
- [x] T013 Create circuit breaker utility at backend/src/utils/circuit_breaker.py with automatic retry functionality

**Checkpoint**: Shared services ready - user story implementations can now proceed in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks through natural conversation like "remind me to buy groceries" → invokes add_task with friendly confirmation

**Independent Test**: Send various natural language messages expressing task creation intent (explicit and implicit), verify agent correctly identifies intent, invokes add_task with appropriate parameters, and responds with user-friendly confirmation

### Implementation for User Story 1

- [x] T014 [P] [US1] Update LLM client in backend/src/services/llm_client.py with OpenAI Agents SDK integration
- [x] T015 [P] [US1] Add MCP client update in backend/src/services/mcp_client.py to use MCPServerStreamableHttp with automatic retries
- [x] T016 [P] [US1] Implement intent recognition logic in backend/src/services/agent_runner.py for CREATE intent
- [x] T017 [P] [US1] Add tool selection logic in backend/src/services/agent_runner.py to map CREATE intent to add_task tool
- [x] T018 [P] [US1] Add parameter extraction logic in backend/src/services/agent_runner.py to extract title/description from natural language
- [x] T019 [US1] Add response formatting in backend/src/services/agent_runner.py to generate friendly creation confirmation
- [x] T020 [US1] Add error handling in backend/src/services/agent_runner.py for validation errors during creation
- [x] T021 [US1] Register add_task tool invocation in backend/src/services/agent_runner.py with MCP client
- [x] T022 [US1] Add confidence scoring for CREATE intent in backend/src/services/agent_runner.py with 0.80 threshold
- [x] T023 [US1] Update chat endpoint in backend/src/api/chat_endpoint.py to return formatted responses with tool calls

**Acceptance Validation**:
- Create task with title only → Returns task with ID, status="pending", created_at timestamp, description=null
- Create task with title and description → Returns task with both fields populated
- Create task with empty title → Returns VALIDATION_ERROR with friendly message
- Create task with title exceeding 255 chars → Returns VALIDATION_ERROR with friendly message
- Create task with description exceeding 1000 chars → Returns VALIDATION_ERROR with friendly message
- Natural language "remind me to buy groceries" → Invokes add_task with title="buy groceries"
- Explicit command "add task: Review docs" → Invokes add_task with title="Review docs"

**Checkpoint**: Natural language task creation fully functional - users can create tasks and receive confirmation

---

## Phase 4: User Story 2 - Natural Language Task Retrieval (Priority: P1) 🎯 MVP

**Goal**: Enable users to query all tasks or filter by status through natural conversation like "what do I need to do?" → invokes list_tasks with readable format

**Independent Test**: Create multiple tasks with different statuses, invoke list_tasks with and without status filter via natural language, verify correct tasks returned in DESC order with readable format

### Implementation for User Story 2

- [x] T024 [P] [US2] Implement intent recognition logic in backend/src/services/agent_runner.py for LIST intent
- [x] T025 [P] [US2] Add tool selection logic in backend/src/services/agent_runner.py to map LIST intent to list_tasks tool
- [x] T026 [P] [US2] Add parameter extraction logic in backend/src/services/agent_runner.py to extract status filters from natural language
- [x] T027 [P] [US2] Add task list formatting in backend/src/services/agent_runner.py to generate readable numbered format
- [x] T028 [US2] Add response formatting in backend/src/services/agent_runner.py to handle empty list scenarios
- [x] T029 [US2] Register list_tasks tool invocation in backend/src/services/agent_runner.py with MCP client
- [x] T030 [US2] Add confidence scoring for LIST intent in backend/src/services/agent_runner.py with 0.70 threshold
- [x] T031 [US2] Update conversation metadata in backend/src/services/agent_runner.py to store task_references after list_tasks
- [x] T032 [US2] Add error handling in backend/src/services/agent_runner.py for list_tasks errors
- [x] T033 [US2] Add status filter recognition in backend/src/services/agent_runner.py to detect "pending", "completed", "all" from natural language

**Acceptance Validation**:
- List all tasks without filter → Returns all tasks ordered by created_at DESC in numbered format
- List tasks with "pending" filter → Returns only pending tasks in readable format
- List tasks with "completed" filter → Returns only completed tasks with completion timestamps
- List tasks when database is empty → Returns friendly message "You don't have any tasks yet..."
- List tasks with invalid status value → Returns VALIDATION_ERROR with friendly message
- Natural language "what do I need to do?" → Invokes list_tasks with status="pending"
- Natural language "show me what's completed" → Invokes list_tasks with status="completed"

**Checkpoint**: Natural language task retrieval fully functional - users can query and filter tasks

---

## Phase 5: User Story 6 - Multi-Step Conversational Flows (Priority: P1)

**Goal**: Enable users to engage in multi-turn conversations like "show my tasks" followed by "complete task 2" with proper context maintenance

**Independent Test**: Conduct multi-turn conversations where agent first lists tasks, then user references tasks from that list by position/number, verify agent correctly maps references to task IDs across conversation turns

### Implementation for User Story 6

- [x] T034 [P] [US6] Update conversation service in backend/src/services/conversation_service.py to store task_references in metadata after list_tasks
- [x] T035 [P] [US6] Implement task reference resolution logic in backend/src/services/task_reference_resolver.py to map position strings to task IDs
- [x] T036 [P] [US6] Add reference resolution in backend/src/services/agent_runner.py to handle "task 2", "the first one", "#3" patterns
- [x] T037 [US6] Add context loading in backend/src/services/agent_runner.py to retrieve task_references from conversation metadata
- [x] T038 [US6] Update metadata management in backend/src/services/agent_runner.py to refresh task_references when new list_tasks occurs
- [x] T039 [US6] Add context staleness handling in backend/src/services/agent_runner.py to detect when references are too old
- [x] T040 [US6] Add missing context detection in backend/src/services/agent_runner.py to prompt for listing tasks when no recent references exist
- [x] T041 [US6] Add multi-turn flow validation in backend/src/services/agent_runner.py to verify context before using task references
- [x] T042 [US6] Add conversation history management in backend/src/services/conversation_service.py to maintain context across turns

**Acceptance Validation**:
- Show tasks then complete task 2 → Shows numbered list then completes correct task by position
- Show tasks then delete first one → Shows numbered list then deletes first task by position reference
- Engage in unrelated conversation then reference "task 2" → Either retrieves fresh context or asks for clarification
- Start new conversation and reference "task 1" without listing → Asks user to list tasks first
- Context remains valid across at least 5 conversation turns
- Task references expire when new list_tasks is invoked (refresh context)

**Checkpoint**: Multi-step conversational flows fully functional - users can reference tasks by position after listing

---

## Phase 6: User Story 3 - Natural Language Task Updates (Priority: P2)

**Goal**: Enable users to modify task title and/or description by reference through natural conversation like "change task 2 to 'Call Sarah instead of John'" → invokes update_task with confirmation

**Independent Test**: List tasks to get their IDs/positions, send update requests referencing tasks by number or partial description, verify agent correctly identifies target task, invokes update_task with new values, and confirms the change

### Implementation for User Story 3

- [x] T043 [P] [US3] Implement intent recognition logic in backend/src/services/agent_runner.py for UPDATE intent
- [x] T044 [P] [US3] Add tool selection logic in backend/src/services/agent_runner.py to map UPDATE intent to update_task tool
- [x] T045 [P] [US3] Add parameter extraction logic in backend/src/services/agent_runner.py to extract new title/description and task reference from natural language
- [x] T046 [P] [US3] Add confidence scoring for UPDATE intent in backend/src/services/agent_runner.py with 0.85 threshold
- [x] T047 [US3] Add task reference resolution in backend/src/services/agent_runner.py to handle description-based references like "the groceries task"
- [x] T048 [US3] Add response formatting in backend/src/services/agent_runner.py to generate update confirmation messages
- [x] T049 [US3] Register update_task tool invocation in backend/src/services/agent_runner.py with MCP client
- [x] T050 [US3] Add error handling in backend/src/services/agent_runner.py for NOT_FOUND and validation errors during updates
- [x] T051 [US3] Add ambiguous reference detection in backend/src/services/agent_runner.py to handle multiple matching tasks
- [x] T052 [US3] Add clarification logic in backend/src/services/agent_runner.py to ask for task selection when multiple matches exist

**Acceptance Validation**:
- Update task by position "change task 2 to 'Call Sarah'" → Updates correct task by position reference
- Update task by description "update the groceries task to include milk" → Updates matching task by description
- Update non-existent task → Returns NOT_FOUND error with friendly message
- Update with ambiguous reference (multiple matches) → Asks for clarification with options
- Natural language "update the meeting task" → Handles appropriately when multiple meeting tasks exist
- Update with confidence below threshold → Asks for confirmation before proceeding

**Checkpoint**: Natural language task updates fully functional - users can modify task details by reference

---

## Phase 7: User Story 4 - Natural Language Task Completion (Priority: P2)

**Goal**: Enable users to mark tasks as completed through natural conversation like "I bought the groceries" or "mark task 3 as done" → invokes complete_task with encouraging confirmation

**Independent Test**: Create pending tasks, send completion messages referencing tasks by number or description, verify agent invokes complete_task with correct task ID and responds with encouraging confirmation

### Implementation for User Story 4

- [x] T053 [P] [US4] Implement intent recognition logic in backend/src/services/agent_runner.py for COMPLETE intent
- [x] T054 [P] [US4] Add tool selection logic in backend/src/services/agent_runner.py to map COMPLETE intent to complete_task tool
- [x] T055 [P] [US4] Add parameter extraction logic in backend/src/services/agent_runner.py to extract task reference from completion language
- [x] T056 [P] [US4] Add confidence scoring for COMPLETE intent in backend/src/services/agent_runner.py with 0.80 threshold
- [x] T057 [US4] Add task reference resolution in backend/src/services/agent_runner.py to handle inferred completions like "I bought groceries"
- [x] T058 [US4] Add encouraging response formatting in backend/src/services/agent_runner.py with personality variations
- [x] T059 [US4] Register complete_task tool invocation in backend/src/services/agent_runner.py with MCP client
- [x] T060 [US4] Add error handling in backend/src/services/agent_runner.py for NOT_FOUND and validation errors during completion
- [x] T061 [US4] Add idempotency handling in backend/src/services/agent_runner.py to handle already-completed tasks gracefully
- [x] T062 [US4] Add completion celebration logic in backend/src/services/response_formatter.py with "Great!", "Awesome!" variations

**Acceptance Validation**:
- Complete task by position "complete task 1" → Marks correct task as completed with timestamp
- Complete task by inference "I bought the groceries" → Identifies and completes matching task
- Complete already-completed task → Succeeds idempotently with appropriate message
- Complete non-existent task → Returns NOT_FOUND error with friendly message
- Natural language "I finished task 2" → Completes correct task by position
- Completion returns encouraging response with ✓ emoji

**Checkpoint**: Natural language task completion fully functional - users can mark tasks complete with positive reinforcement

---

## Phase 8: User Story 5 - Natural Language Task Deletion (Priority: P3)

**Goal**: Enable users to permanently delete tasks by reference through natural conversation like "delete the groceries task" or "remove task 4" → invokes delete_task with confirmation

**Independent Test**: Create tasks, send deletion requests referencing tasks by number or description, verify agent invokes delete_task with correct ID, confirms deletion, and task no longer appears in subsequent lists

### Implementation for User Story 5

- [x] T063 [P] [US5] Implement intent recognition logic in backend/src/services/agent_runner.py for DELETE intent
- [x] T064 [P] [US5] Add tool selection logic in backend/src/services/agent_runner.py to map DELETE intent to delete_task tool
- [x] T065 [P] [US5] Add parameter extraction logic in backend/src/services/agent_runner.py to extract task reference from deletion language
- [x] T066 [P] [US5] Add confidence scoring for DELETE intent in backend/src/services/agent_runner.py with 0.90 threshold
- [x] T067 [US5] Add confirmation logic in backend/src/services/agent_runner.py to always confirm before deletion regardless of confidence
- [x] T068 [US5] Add response formatting in backend/src/services/agent_runner.py to generate deletion confirmation messages
- [x] T069 [US5] Register delete_task tool invocation in backend/src/services/agent_runner.py with MCP client
- [x] T070 [US5] Add error handling in backend/src/services/agent_runner.py for NOT_FOUND and validation errors during deletion
- [x] T071 [US5] Add ambiguous reference detection in backend/src/services/agent_runner.py to handle multiple matching tasks
- [x] T072 [US5] Add destructive operation warnings in backend/src/services/agent_runner.py with ⚠️ emoji and clear confirmation

**Acceptance Validation**:
- Delete task by position "delete task 2" → Asks for confirmation then deletes correct task
- Delete task by description "remove the meeting task" → Identifies and asks to confirm deletion of matching task
- Delete non-existent task → Returns NOT_FOUND error with friendly message
- Delete with multiple matching tasks → Asks for clarification before confirmation
- Natural language "remove task 3" → Asks for confirmation then deletes correct task
- Delete operation always requires confirmation regardless of confidence level

**Checkpoint**: Natural language task deletion fully functional - users can remove obsolete tasks with confirmation

---

## Phase 9: Integration & Polish

**Purpose**: Integrate all components and add cross-cutting concerns

- [x] T073 Update system prompt loading in backend/src/services/agent_runner.py to inject task_references and conversation context
- [x] T074 Add comprehensive error handling in backend/src/services/agent_runner.py with circuit breaker patterns
- [x] T075 Add logging statements for all agent operations in backend/src/services/agent_runner.py (import logging, log intent recognition, tool selection, execution results)
- [x] T076 Verify all error messages do not leak sensitive information in backend/src/services/agent_runner.py (review error detail fields)
- [x] T077 Add input sanitization in backend/src/services/agent_runner.py for title and description fields (strip leading/trailing whitespace)
- [ ] T078 Run manual integration test: Start FastAPI server and verify agent processes natural language requests without errors
- [ ] T079 Run manual end-to-end test: Invoke each user story flow via chat endpoint and verify structured responses
- [x] T080 Add docstrings to all agent functions in backend/src/services/agent_runner.py with parameter descriptions and return types
- [x] T081 Update backend/src/mcp_tools/__init__.py to export any new agent-related utilities
- [x] T082 Add performance monitoring to agent operations in backend/src/services/agent_runner.py (response time tracking)
- [x] T083 Add confidence threshold adjustment mechanism in backend/src/services/agent_runner.py (for tuning based on usage)
- [x] T084 Update chat endpoint response format in backend/src/api/chat_endpoint.py to include reasoning_trace for debugging

**Checkpoint**: AI agent integrated and polished - all user stories functional with proper error handling and logging

---

## Dependencies Between User Stories

**Visualization**:
```
Setup (Phase 1)
  ↓
Foundational (Phase 2: Shared Services)
  ↓
  ├─→ User Story 1 (Natural Language Creation) ──────┐
  ├─→ User Story 2 (Natural Language Retrieval) ─────┤
  └─→ User Story 6 (Multi-Step Flows) ───────────────┤
       ↓                                             ├─→ Can execute in parallel (independent)
       ├─→ User Story 3 (Task Updates) ──────────────┤
       ├─→ User Story 4 (Task Completion) ───────────┤
       └─→ User Story 5 (Task Deletion) ─────────────┘
            ↓
       Integration & Polish (Phase 9)
```

**Story Dependencies**:
- **User Story 1** (Creation): No dependencies on other stories. Can be implemented and tested first.
- **User Story 2** (Retrieval): No dependencies on other stories. Can run in parallel with US1.
- **User Story 6** (Multi-Step): Depends on US2 (needs task listing to establish references). Can run after US2.
- **User Story 3** (Updates): Depends on US6 (needs reference resolution). Can run after US6.
- **User Story 4** (Completion): Depends on US6 (needs reference resolution). Can run after US6.
- **User Story 5** (Deletion): Depends on US6 (needs reference resolution). Can run after US6.

**Implementation Order**: US1/US2 (parallel) → US6 → US3/US4/US5 (parallel)

---

## Parallel Execution Examples

### Scenario 1: Single Developer (Sequential MVP)
1. Complete Phase 1-2 (Setup + Foundational)
2. Implement User Story 1 (Natural Language Creation) - **MVP READY** ✅
3. Implement User Story 2 (Natural Language Retrieval) - **Core functionality complete** ✅
4. Implement User Story 6 (Multi-Step Flows) - **Natural conversation ready** ✅
5. Implement User Stories 3-5 as enhancements
6. Complete Phase 9 (Integration & Polish)

### Scenario 2: Team of 6 Developers (Parallel)
After Phase 2 completes:
- Dev 1: User Story 1 (T014-T023) - Natural Language Creation
- Dev 2: User Story 2 (T024-T033) - Natural Language Retrieval
- Dev 3: User Story 6 (T034-T042) - Multi-Step Flows
- Dev 4: User Story 3 (T043-T052) - Task Updates
- Dev 5: User Story 4 (T053-T062) - Task Completion
- Dev 6: User Story 5 (T063-T072) - Task Deletion

Stories 1, 2 run in parallel → Story 6 after 2 → Stories 3, 4, 5 after 6. All merge independently, then Phase 9 integration by any developer.

### Scenario 3: Two-Phase Delivery
**Phase A (P1 Stories)**: Implement US1 + US2 + US6 → Deploy as MVP
**Phase B (P2-P3 Stories)**: Add US3 + US4 + US5 later → Deploy as enhancement

---

## Implementation Strategy

### MVP-First Approach (Recommended)

**MVP Definition**: User Story 1 (Natural Language Creation) + User Story 2 (Natural Language Retrieval) + User Story 6 (Multi-Step Flows)

**Rationale**:
- US1 enables task creation (essential)
- US2 enables task querying (essential)
- US6 enables natural multi-turn conversations (essential for good UX)
- Updates, completion, deletion are enhancements
- Together they provide complete task management value

**MVP Task Sequence**:
1. Phase 1: Setup (T001-T007)
2. Phase 2: Foundational (T008-T013)
3. Phase 3: User Story 1 (T014-T023) - Natural Language Creation
4. Phase 4: User Story 2 (T024-T033) - Natural Language Retrieval
5. Phase 5: User Story 6 (T034-T042) - Multi-Step Conversational Flows
6. Phase 9: Integration (T073-T084)

**Total MVP Tasks**: 42 tasks
**Estimated MVP Duration**: 4-6 hours for experienced developer

### Incremental Delivery

After MVP deployment, add remaining stories incrementally:
- **Iteration 2**: Add User Story 3 (Task Updates) for task editing
- **Iteration 3**: Add User Story 4 (Task Completion) for task completion tracking
- **Iteration 4**: Add User Story 5 (Task Deletion) for task cleanup

Each iteration is independently testable and deployable.

---

## Task Summary

**Total Tasks**: 84 tasks
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (User Story 1 - P1): 10 tasks
- Phase 4 (User Story 2 - P1): 10 tasks
- Phase 5 (User Story 6 - P1): 9 tasks
- Phase 6 (User Story 3 - P2): 10 tasks
- Phase 7 (User Story 4 - P2): 10 tasks
- Phase 8 (User Story 5 - P3): 10 tasks
- Phase 9 (Integration & Polish): 12 tasks

**Parallel Opportunities**: 65 tasks marked with [P] can run in parallel

**Story Distribution**:
- User Story 1 (Natural Language Creation): 10 implementation tasks
- User Story 2 (Natural Language Retrieval): 10 implementation tasks
- User Story 3 (Natural Language Updates): 10 implementation tasks
- User Story 4 (Natural Language Completion): 10 implementation tasks
- User Story 5 (Natural Language Deletion): 10 implementation tasks
- User Story 6 (Multi-Step Flows): 9 implementation tasks

**Independent Test Criteria** (per story):
- US1: Create task via natural language, verify in database with correct status and timestamps
- US2: Query tasks via natural language with/without filters, verify correct results and ordering
- US3: Update task via natural language, verify changes persisted
- US4: Complete task via natural language, verify status and timestamp changes (idempotent)
- US5: Delete task via natural language, verify removal from database
- US6: List tasks then reference by position, verify correct task identification across turns

**MVP Scope**: User Story 1 + User Story 2 + User Story 6 (30 implementation tasks + 13 setup/foundational + 12 integration = 55 tasks total)

---

## Validation Checklist

Before marking feature complete, verify:

- [ ] All 5 MCP tools from Phase III-A are functional and accessible
- [ ] Each user story returns structured responses (success/error format)
- [ ] All error codes implemented (VALIDATION_ERROR, NOT_FOUND, DATABASE_ERROR, INTERNAL_ERROR)
- [ ] Input validation enforces character limits (title ≤255, description ≤1000)
- [ ] Database session properly acquired and closed in all tool invocations
- [ ] Timestamps auto-generated correctly (created_at, completed_at)
- [ ] list_tasks returns results ordered by created_at DESC in readable format
- [ ] complete_task is idempotent (no error on re-completion)
- [ ] All agent operations are stateless (no memory between invocations)
- [ ] MCP server integrates with agent operations
- [ ] Logging added for all agent operations
- [ ] No sensitive data in error messages
- [ ] All agent functions have docstrings
- [ ] All imports and exports in __init__.py are correct
- [ ] Task reference resolution works for position-based references
- [ ] Multi-turn context maintained across conversation turns
- [ ] Confidence thresholds applied correctly (DELETE: 0.90, UPDATE: 0.85, CREATE: 0.80, LIST: 0.70)
- [ ] Error humanization translates technical errors to user-friendly messages
- [ ] Response formatting uses templates with personality variations
- [ ] Destructive operations (delete) always require confirmation

---

## Notes

- **No tests required**: Specification does not explicitly request automated tests
- **Existing infrastructure reused**: MCP server, Task model, database config all from Phase I & II
- **No schema changes**: Task model remains unchanged, only conversation metadata enhanced
- **Stateless design**: All agent operations use conversation state dependency injection
- **Error handling**: Consistent error codes and friendly messages across all user stories
- **Performance**: Direct MCP tool invocations, no additional overhead beyond existing infrastructure
- **Idempotency**: complete_task operation is idempotent per specification
- **Natural language focus**: All user stories accessed through conversational interfaces

---

**Generated**: 2026-01-23
**Branch**: `002-ai-agent-orchestration`
**Ready for**: `/sp.implement` (task execution)