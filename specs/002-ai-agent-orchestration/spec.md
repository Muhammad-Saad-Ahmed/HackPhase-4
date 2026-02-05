# Feature Specification: AI Agent & Chat Orchestration

**Feature Branch**: `002-ai-agent-orchestration`
**Created**: 2026-01-23
**Status**: Draft
**Input**: User description: "Phase III-B – AI Agent & Chat Orchestration - Build an AI agent that understands natural language and manages todos exclusively via MCP tools. Scope: Agent intent recognition, Tool selection and invocation, Friendly confirmations and error messages. Agent Rules: Use OpenAI Agents SDK, Never modify data directly, Always act through MCP tools. Supported Intents: Create, list, update, complete, delete tasks. Success Criteria: Correct tool invoked per user intent, Multiple-step flows handled (list → delete), Clear confirmations after actions. Not Building: MCP server, Database schemas, Frontend UI. Precondition: Review existing API routes and task behaviors, Understand current task lifecycle and constraints, Align agent actions with existing backend behavior."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Creation (Priority: P1)

A user sends a casual message like "remind me to buy groceries" or "I need to call John tomorrow" and the AI agent recognizes the intent to create a task, invokes the add_task MCP tool, and responds with a friendly confirmation showing what was created.

**Why this priority**: This is the foundational capability - users must be able to create tasks through natural conversation. Without this, the agent provides no value. This is the core differentiator from direct API access.

**Independent Test**: Can be fully tested by sending various natural language messages expressing task creation intent (explicit and implicit), and verifying the agent correctly identifies the intent, invokes add_task with appropriate parameters, and responds with a user-friendly confirmation.

**Acceptance Scenarios**:

1. **Given** a user sends "remind me to buy groceries", **When** the agent processes this message, **Then** the agent invokes add_task with title "buy groceries", receives the created task details, and responds with "I've added 'buy groceries' to your tasks"
2. **Given** a user sends "I need to schedule a meeting with the team about Q1 planning", **When** the agent processes this message, **Then** the agent invokes add_task with title "schedule a meeting with the team" and description "about Q1 planning", and confirms the task creation
3. **Given** a user sends "add task: Review documentation", **When** the agent processes this explicit command, **Then** the agent invokes add_task with title "Review documentation" and responds with confirmation
4. **Given** a user sends an extremely long task description (over 1000 characters), **When** the agent attempts to create the task, **Then** the add_task tool returns a validation error, and the agent translates this into a friendly message like "That description is too long. Please keep it under 1000 characters."

---

### User Story 2 - Natural Language Task Retrieval (Priority: P1)

A user asks "what do I need to do?" or "show me my pending tasks" and the AI agent recognizes the intent to list tasks, invokes the list_tasks MCP tool with appropriate filters, and presents the results in a readable format.

**Why this priority**: Viewing tasks is equally critical as creating them - users need to understand what's on their plate. This enables the agent to provide context for follow-up actions like completing or deleting tasks.

**Independent Test**: Can be fully tested by creating tasks with different statuses, then sending various natural language queries requesting task lists (all, pending, completed), and verifying the agent invokes list_tasks correctly and formats responses clearly.

**Acceptance Scenarios**:

1. **Given** multiple tasks exist (some pending, some completed), **When** a user sends "what's on my todo list?", **Then** the agent invokes list_tasks without filters, receives all tasks, and presents them in a numbered, readable format
2. **Given** tasks exist with different statuses, **When** a user sends "show me what I still need to do", **Then** the agent invokes list_tasks with status="pending" filter and lists only incomplete tasks
3. **Given** tasks exist with different statuses, **When** a user sends "what have I completed?", **Then** the agent invokes list_tasks with status="completed" filter and shows completed tasks with completion timestamps
4. **Given** no tasks exist, **When** a user sends "show my tasks", **Then** the agent invokes list_tasks, receives an empty result, and responds with "You don't have any tasks yet. Would you like to create one?"

---

### User Story 3 - Natural Language Task Updates (Priority: P2)

A user references a task by number or description and requests a change like "change task 2 to 'Call Sarah instead of John'" and the AI agent recognizes the intent to update, identifies which task, invokes the update_task MCP tool, and confirms the modification.

**Why this priority**: While less critical than creating and viewing, updating tasks is important for keeping information accurate. However, users can work around this by deleting and recreating tasks if needed.

**Independent Test**: Can be fully tested by listing tasks to get their IDs/positions, then sending update requests referencing tasks by number or partial description, and verifying the agent correctly identifies the target task, invokes update_task with new values, and confirms the change.

**Acceptance Scenarios**:

1. **Given** tasks are listed with numbers (1. Buy groceries, 2. Call John), **When** a user sends "change task 2 to 'Call Sarah'", **Then** the agent invokes update_task with the correct task ID and new title, and confirms "I've updated task 2 to 'Call Sarah'"
2. **Given** tasks exist in the system, **When** a user sends "update the groceries task to include milk and eggs", **Then** the agent invokes update_task with the matching task ID and new description, and confirms the update
3. **Given** a user references a non-existent task, **When** the user sends "update task 99 to something", **Then** the update_task tool returns NOT_FOUND, and the agent responds with "I couldn't find task 99. Would you like to see your current tasks?"
4. **Given** a user's update request is ambiguous (matches multiple tasks), **When** the user sends "update the meeting task", **Then** the agent asks for clarification: "I found 3 tasks about meetings. Which one did you mean? 1. Schedule meeting, 2. Prepare meeting agenda, 3. Send meeting notes"

---

### User Story 4 - Natural Language Task Completion (Priority: P2)

A user indicates they finished something like "I bought the groceries" or "mark task 3 as done" and the AI agent recognizes the completion intent, invokes the complete_task MCP tool, and celebrates the accomplishment with a friendly confirmation.

**Why this priority**: Completing tasks is a natural part of task management and provides satisfaction to users. However, it's slightly less critical than basic CRUD operations since incomplete tasks don't prevent system usage.

**Independent Test**: Can be fully tested by creating pending tasks, sending completion messages referencing tasks by number or description, and verifying the agent invokes complete_task with the correct task ID and responds with encouraging confirmation.

**Acceptance Scenarios**:

1. **Given** tasks are listed with numbers (1. Buy groceries, 2. Call John), **When** a user sends "I finished task 1", **Then** the agent invokes complete_task with the correct ID and responds "Great! I've marked 'Buy groceries' as completed ✓"
2. **Given** tasks exist, **When** a user sends "I bought the groceries", **Then** the agent infers the task from context, invokes complete_task, and confirms with encouragement
3. **Given** a task is already completed, **When** a user tries to complete it again, **Then** the complete_task tool succeeds idempotently, and the agent responds "That task was already completed on [timestamp]"
4. **Given** a user references a non-existent task, **When** the user sends "complete task 99", **Then** the complete_task tool returns NOT_FOUND, and the agent responds "I couldn't find task 99. Would you like to see your current tasks?"

---

### User Story 5 - Natural Language Task Deletion (Priority: P3)

A user decides a task is no longer needed and says "delete the groceries task" or "remove task 4" and the AI agent recognizes the deletion intent, invokes the delete_task MCP tool, and confirms the removal.

**Why this priority**: While useful for cleanup, deletion is the lowest priority since users can simply ignore unwanted tasks or mark them complete. It's a convenience feature rather than a necessity.

**Independent Test**: Can be fully tested by creating tasks, sending deletion requests referencing tasks by number or description, and verifying the agent invokes delete_task with the correct ID, confirms the deletion, and the task no longer appears in subsequent lists.

**Acceptance Scenarios**:

1. **Given** tasks are listed with numbers, **When** a user sends "delete task 2", **Then** the agent invokes delete_task with the correct ID and confirms "I've deleted task 2: 'Call John'"
2. **Given** tasks exist, **When** a user sends "remove the meeting task", **Then** the agent identifies the matching task, invokes delete_task, and confirms the deletion
3. **Given** a user references a non-existent task, **When** the user sends "delete task 99", **Then** the delete_task tool returns NOT_FOUND, and the agent responds "I couldn't find task 99 to delete"
4. **Given** multiple tasks match a description, **When** a user sends "delete the meeting task", **Then** the agent asks for clarification before invoking delete_task

---

### User Story 6 - Multi-Step Conversational Flows (Priority: P1)

A user engages in a multi-turn conversation like "show my tasks" followed by "complete task 2" and the AI agent maintains context across messages, correctly referencing tasks from previous responses.

**Why this priority**: Multi-step flows are essential for natural conversation. Without this, users must repeat context in every message, making the experience frustrating and unnatural.

**Independent Test**: Can be fully tested by conducting multi-turn conversations where the agent first lists tasks, then the user references tasks from that list by position/number, and verifying the agent correctly maps references to task IDs across conversation turns.

**Acceptance Scenarios**:

1. **Given** a user sends "show my tasks" and receives a numbered list, **When** the user follows up with "complete task 2", **Then** the agent remembers which task was #2 in the previous response and invokes complete_task with the correct ID
2. **Given** a user sends "what do I need to do?" and receives tasks, **When** the user follows up with "delete the first one", **Then** the agent identifies task #1 from the previous list and invokes delete_task correctly
3. **Given** a user engages in unrelated conversation between task commands, **When** the user later references "task 2", **Then** the agent either retrieves the latest task list context or asks for clarification if context is stale
4. **Given** a user starts a new conversation session, **When** the user references "task 1" without first listing tasks, **Then** the agent recognizes the missing context and either lists tasks first or asks for clarification

---

### Edge Cases

- What happens when a user's natural language request is ambiguous (e.g., "do the thing")?
- How does the agent handle messages that don't express any task-related intent?
- What happens when the MCP tools return errors (validation, database, not found)?
- How does the agent handle malformed tool responses from the MCP server?
- What happens when a user references a task by description that matches multiple tasks?
- How does the agent handle extremely long messages (approaching 10000 character limit)?
- What happens when conversation_id is invalid or corrupted?
- How does the agent handle rapid-fire requests that might cause race conditions?
- What happens when a user tries to reference a task from a different conversation?
- How does the agent distinguish between "list tasks" intent and casual mentions of tasks in conversation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Agent MUST parse user messages to identify task-related intents (create, list, update, complete, delete)
- **FR-002**: Agent MUST invoke the appropriate MCP tool (add_task, list_tasks, update_task, complete_task, delete_task) based on identified intent
- **FR-003**: Agent MUST translate MCP tool responses into natural, friendly language for users
- **FR-004**: Agent MUST handle MCP tool errors gracefully and provide helpful error messages to users (never expose technical error codes directly)
- **FR-005**: Agent MUST extract task details (title, description, status) from natural language messages
- **FR-006**: Agent MUST maintain conversation context to support multi-turn interactions (remembering task IDs from previous list responses)
- **FR-007**: Agent MUST format task lists in a numbered, readable format when presenting to users
- **FR-008**: Agent MUST ask clarifying questions when user requests are ambiguous or match multiple tasks
- **FR-009**: Agent MUST provide encouraging confirmations after successful task operations (especially completions)
- **FR-010**: Agent MUST never directly modify the database - all data operations MUST go through MCP tools
- **FR-011**: Agent MUST handle cases where users reference tasks by position/number from previous lists
- **FR-012**: Agent MUST recognize both explicit commands (e.g., "add task: X") and implicit intents (e.g., "I need to X")
- **FR-013**: Agent MUST preserve user's original language and tone when confirming task details
- **FR-014**: Agent MUST handle multiple intents in a single message (e.g., "show my tasks and add one for groceries")
- **FR-015**: Agent MUST integrate with OpenAI Agents SDK for LLM-powered natural language understanding
- **FR-016**: Agent MUST respect character limits from MCP tools (title ≤255, description ≤1000) and warn users before exceeding them
- **FR-017**: Agent MUST distinguish between requests for pending vs completed tasks and apply appropriate filters
- **FR-018**: Agent MUST provide fallback responses when intent recognition confidence is low

### Key Entities

- **Agent Response**: Represents the agent's natural language reply to the user, including tool call results formatted for human consumption
- **Intent**: The classified user request type (CREATE_TASK, LIST_TASKS, UPDATE_TASK, COMPLETE_TASK, DELETE_TASK, UNCLEAR, OFF_TOPIC)
- **Tool Invocation**: A record of which MCP tool was called, with what parameters, and what result was returned
- **Conversation Context**: Session-scoped memory containing recent task lists with their IDs for reference resolution
- **Task Reference**: A user's way of identifying a task (by ID, by position from last list, or by partial description match)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of clear task-related messages result in the correct MCP tool being invoked
- **SC-002**: Users can complete a full task lifecycle (create → list → complete) within a natural 3-message conversation
- **SC-003**: Agent correctly maintains context for task references across at least 5 conversation turns
- **SC-004**: All MCP tool errors are translated into user-friendly messages (no raw error codes exposed to users)
- **SC-005**: Agent response time is under 2 seconds for simple operations (create, list with few tasks)
- **SC-006**: Agent correctly handles multi-step flows (list → complete/delete) without requiring users to specify task IDs manually
- **SC-007**: 90% of ambiguous requests trigger appropriate clarifying questions before tool invocation
- **SC-008**: Users successfully create tasks using implicit intent ("I need to X") at least 80% of the time without explicit commands
- **SC-009**: Agent maintains conversational tone (not robotic) across all responses based on user feedback
- **SC-010**: Zero direct database modifications - 100% of data operations route through MCP tools

## Constraints & Assumptions *(optional)*

### Constraints

- Must use OpenAI Agents SDK (cannot use alternative agent frameworks)
- Cannot modify database directly (all operations through MCP tools)
- Must work with existing MCP server from Phase III-A (no changes to tool signatures)
- Must use existing chat endpoint structure (AgentRunner, LLMClient, MCPTaskExecutor)
- Agent logic must be stateless at the instance level (conversation state stored via ConversationService)
- Must respect existing error codes and response formats from MCP tools
- Cannot introduce new database tables or schemas for agent-specific data
- Must maintain backward compatibility with existing chat endpoint API contract

### Assumptions

- OpenAI Agents SDK is installed and configured with valid API credentials
- MCP server from Phase III-A is running and all 5 tools are functional
- Users understand basic task management concepts (create, complete, delete)
- Users will provide feedback in natural language (not expecting command syntax)
- Conversations are in English (no multi-language support required in MVP)
- Task references by position are only valid within the same conversation session
- Users accept that very old context (>10 messages ago) may not be retained for task references
- Network latency to OpenAI API is reasonable (<1 second for typical requests)

## Dependencies & Integrations *(optional)*

### Internal Dependencies

- **Phase III-A MCP Server**: All 5 MCP tools (add_task, list_tasks, update_task, complete_task, delete_task) must be operational
- **LLMClient**: Existing LLM client interface for generating responses (backend/src/services/llm_client.py)
- **MCPTaskExecutor**: Existing MCP client for invoking tools (backend/src/services/mcp_client.py)
- **ConversationService**: Existing service for storing conversation history (backend/src/services/conversation_service.py)
- **Chat Endpoint**: Existing FastAPI endpoint that orchestrates agent flow (backend/src/api/chat_endpoint.py)
- **Task Model**: Existing SQLModel Task entity (backend/src/models/task.py)

### External Dependencies

- **OpenAI Agents SDK**: LLM provider for natural language understanding and intent recognition
- **OpenAI API**: Cloud service for model inference (requires API key and billing)

## Out of Scope *(optional)*

### Explicitly Excluded

- Building or modifying the MCP server (that's Phase III-A)
- Creating new MCP tools beyond the 5 existing ones
- Modifying database schemas or the Task model
- Building a frontend UI (agent is backend-only)
- Multi-language support (English only for MVP)
- Voice or audio input/output
- Task scheduling or reminders (time-based triggers)
- Task prioritization or categorization (beyond pending/completed status)
- Multi-user task sharing or collaboration
- Authentication or authorization logic (handled by existing endpoint)
- Real-time notifications or push updates
- Task attachments or file uploads
- Integration with external calendar or productivity tools
- Custom LLM model training or fine-tuning
- Conversational memory beyond current session (no cross-session learning)

## Testing Strategy *(optional)*

### Test Scenarios

**Intent Recognition Tests**:
1. Verify agent recognizes explicit commands ("add task: X", "list tasks", "complete task N")
2. Verify agent recognizes implicit intents ("I need to X", "remind me to X")
3. Verify agent distinguishes pending vs completed list requests
4. Verify agent handles ambiguous messages appropriately
5. Verify agent ignores off-topic messages gracefully

**Tool Invocation Tests**:
1. Verify agent invokes add_task with correct parameters from natural language
2. Verify agent invokes list_tasks with correct status filters
3. Verify agent invokes update_task with correct task ID and new values
4. Verify agent invokes complete_task with correct task ID
5. Verify agent invokes delete_task with correct task ID

**Error Handling Tests**:
1. Verify agent translates VALIDATION_ERROR into user-friendly messages
2. Verify agent translates NOT_FOUND into helpful responses
3. Verify agent handles DATABASE_ERROR gracefully
4. Verify agent handles malformed tool responses

**Multi-Turn Conversation Tests**:
1. Verify agent remembers task IDs from list_tasks responses
2. Verify agent correctly maps "task 2" references to actual task IDs
3. Verify agent maintains context across at least 5 turns
4. Verify agent handles context staleness appropriately

**Response Formatting Tests**:
1. Verify agent formats task lists with numbers and readability
2. Verify agent provides encouraging confirmations for completions
3. Verify agent maintains conversational tone
4. Verify agent preserves user's original task details in confirmations

## Notes *(optional)*

- The agent is the "brain" that connects natural language to structured tool calls
- All intelligence for parsing intent and formatting responses lives in the agent layer
- The MCP tools remain dumb, stateless functions - they only validate and execute
- Conversation context is critical for usability (users expect to say "complete task 2" after listing tasks)
- OpenAI Agents SDK will handle the heavy lifting of LLM interactions and tool orchestration
- The agent must balance helpfulness with avoiding assumptions (ask clarifying questions when needed)
- Response tone matters: friendly, encouraging, helpful (not robotic or terse)
- Error messages should guide users toward success ("Task 99 not found. Try 'show my tasks' to see what's available")
