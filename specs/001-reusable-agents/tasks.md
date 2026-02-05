# Tasks: Reusable AI Agents and Skills

**Input**: Design documents from `/specs/001-reusable-agents/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not explicitly requested in feature specification - tests are OPTIONAL for this implementation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single backend project**: `backend/src/`, `backend/tests/` at repository root
- Paths shown below follow single project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend project directory structure per plan.md (backend/src/ with agents/, skills/, mcp/, models/, api/, core/ subdirectories)
- [ ] T002 Initialize Python project with pyproject.toml in backend/ (dependencies: openai-agents-sdk, mcp-sdk, fastapi, sqlmodel, pydantic, asyncpg, pgvector, alembic, pytest)
- [ ] T003 [P] Create .env.example file in backend/ with required environment variables (DATABASE_URL, OPENAI_API_KEY, MCP_HOST, API_HOST, etc.)
- [ ] T004 [P] Create Dockerfile in backend/ for containerized deployment (multi-stage build with Python 3.11+)
- [ ] T005 [P] Create docker-compose.yml in backend/ for local development (PostgreSQL with pgvector, Redis, PGAdmin services)
- [ ] T006 [P] Create .gitignore in backend/ (Python-specific: __pycache__, .env, .pytest_cache, etc.)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create database configuration in backend/src/core/database.py (SQLModel async engine with connection pooling, pool_size=20)
- [ ] T008 [P] Create logging configuration in backend/src/core/logging.py (structured JSON logging, log levels, trace IDs)
- [ ] T009 [P] Create application config management in backend/src/core/config.py (Pydantic settings from environment variables)
- [ ] T010 Create Alembic migration setup in backend/migrations/ (initialize alembic, create alembic.ini)
- [ ] T011 Create initial database migration 001_initial_schema in backend/migrations/versions/ (create conversation, conversation_message, conversation_entity, agent_execution, tool_definition, tool_invocation tables per data-model.md)
- [ ] T012 [P] Enable pgvector extension in migration 001_initial_schema (CREATE EXTENSION IF NOT EXISTS vector)
- [ ] T013 [P] Create all indexes from data-model.md in migration 001_initial_schema (conversation_id indexes, user_id indexes, vector index on tool_definition.description_embedding)
- [ ] T014 [P] Create SQLModel entity for Conversation in backend/src/models/conversation.py (id, user_id, application_domain, created_at, updated_at, status, metadata fields)
- [ ] T015 [P] Create SQLModel entity for ConversationMessage in backend/src/models/conversation.py (id, conversation_id, role, content, sequence_number, timestamp, agent_type, tool_calls, metadata)
- [ ] T016 [P] Create SQLModel entity for ConversationEntity in backend/src/models/conversation.py (id, conversation_id, entity_type, entity_id, entity_name, first_mentioned_at, last_mentioned_at, mention_count, metadata)
- [ ] T017 [P] Create SQLModel entity for AgentExecution in backend/src/models/agent_execution.py (id, conversation_id, user_id, agent_type, input_data, output_data, execution_start, execution_end, duration_ms, status, error_details, reasoning_trace, confidence_scores, tools_invoked)
- [ ] T018 [P] Create SQLModel entity for ToolDefinition in backend/src/models/tool_metadata.py (id, tool_name, tool_version, application_domain, description, description_embedding, parameter_schema, return_schema, is_active, requires_validation, created_at, updated_at, metadata)
- [ ] T019 [P] Create SQLModel entity for ToolInvocation in backend/src/models/tool_metadata.py (id, agent_execution_id, tool_definition_id, input_parameters, output_result, invocation_start, invocation_end, duration_ms, status, error_details, retry_count)
- [ ] T020 Create FastAPI application instance in backend/src/api/routes.py (app = FastAPI with metadata, CORS middleware, exception handlers)
- [ ] T021 [P] Create health check endpoint GET /health in backend/src/api/routes.py (returns status and timestamp)
- [ ] T022 [P] Create readiness check endpoint GET /ready in backend/src/api/routes.py (checks database connection)
- [ ] T023 [P] Create request logging middleware in backend/src/api/middleware.py (log all requests with trace_id, user_id, duration)
- [ ] T024 Create MCP server instance in backend/src/mcp/server.py (initialize with Official MCP SDK, configure host/port from config)
- [ ] T025 [P] Create tool registry for dynamic tool discovery in backend/src/mcp/tool_registry.py (load tools from database, cache in memory, refresh mechanism)
- [ ] T026 [P] Create tool schema validation utilities in backend/src/mcp/schemas.py (validate parameter_schema and return_schema are valid JSON Schema)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Intent Understanding and Action Execution (Priority: P1) 🎯 MVP

**Goal**: Enable Orchestrator Agent to process natural language requests through intent classification, entity extraction, and tool selection, then execute the selected tool

**Independent Test**: Send various natural language requests across different application contexts (Todo, CRM, Notes) and verify Orchestrator correctly identifies intent, extracts entities, selects appropriate tools, and executes them without app-specific code

### Implementation for User Story 1

- [ ] T027 [P] [US1] Create intent classification skill in backend/src/skills/intent_classifier.py (async function using OpenAI function calling with temperature=0, returns intent_type enum [create/read/update/delete/list/search/analyze] and confidence score)
- [ ] T028 [P] [US1] Create entity extraction skill in backend/src/skills/entity_extractor.py (async function using OpenAI function calling, extracts entities with type/value/attributes, returns confidence score)
- [ ] T029 [P] [US1] Create tool selection skill in backend/src/skills/tool_selector.py (async function for semantic similarity search using pgvector, queries tool_definition table, filters by parameter schema compatibility, returns selected tool with confidence and parameter mapping)
- [ ] T030 [P] [US1] Create confirmation generation skill in backend/src/skills/confirmation_gen.py (async function to generate user-friendly confirmation messages with checkmark and entity details)
- [ ] T031 [US1] Implement Orchestrator Agent in backend/src/agents/orchestrator.py (uses OpenAI Agents SDK Agent class, invokes intent_classifier → entity_extractor → tool_selector skills in sequence, coordinates tool execution via MCP, returns structured response with reasoning_trace)
- [ ] T032 [US1] Create POST /api/v1/agents/orchestrator/invoke endpoint in backend/src/api/routes.py (accepts request/user_id/application_domain, invokes Orchestrator Agent, saves AgentExecution to database, returns OrchestratorResponse per agent-api.yaml contract)
- [ ] T033 [US1] Implement agent execution logging in Orchestrator (create AgentExecution record with input_data, output_data, reasoning_trace, confidence_scores before returning response)
- [ ] T034 [US1] Add explainability output to Orchestrator response (populate reasoning_trace with step-by-step decisions: classify_intent, extract_entities, select_tool with inputs/outputs/confidence/timestamp per step)
- [ ] T035 [US1] Create tool invocation endpoint POST /tools/{tool_name}/invoke in backend/src/mcp/server.py (validates parameters against tool schema, executes tool via MCP SDK, logs to tool_invocation table, returns result with invocation_id and duration_ms)
- [ ] T036 [US1] Implement multi-step tool chaining in Orchestrator (detect multi-intent requests like "show my tasks and mark the first one done", execute tools sequentially, aggregate results)

**Checkpoint**: At this point, User Story 1 should be fully functional - Orchestrator can classify intent, extract entities, select tools, and execute single or multi-step requests

---

## Phase 4: User Story 2 - Validation and Error Prevention (Priority: P2)

**Goal**: Enable Validation Agent to check entity existence and operation validity before execution, preventing errors like "delete task #999" when task doesn't exist

**Independent Test**: Attempt operations on non-existent entities and verify clear, actionable error messages are returned before execution, without requiring Orchestrator to be fully functional

### Implementation for User Story 2

- [ ] T037 [P] [US2] Create Validation Agent in backend/src/agents/validation.py (uses OpenAI Agents SDK Agent class, verifies entity existence by calling lookup tools via MCP, detects ambiguous references, validates operation parameters against tool schema)
- [ ] T038 [US2] Create POST /api/v1/agents/validation/check endpoint in backend/src/api/routes.py (accepts entity_references/operation/tool_name/parameters/user_id/application_domain, invokes Validation Agent, returns ValidationResponse per agent-api.yaml contract)
- [ ] T039 [US2] Implement entity existence verification in Validation Agent (for each entity_reference, invoke appropriate lookup tool via MCP, return validation_results with exists boolean and details if found)
- [ ] T040 [US2] Implement ambiguity detection in Validation Agent (when multiple entities match reference, return validation_status=ambiguous with possible_entities list and clarification question)
- [ ] T041 [US2] Implement dependency checking for delete operations in Validation Agent (query tool metadata to detect if entity has dependencies, based on user context from research.md: warn user and require explicit confirmation)
- [ ] T042 [US2] Implement parameter validation in Validation Agent (validate parameters against tool's parameter_schema using JSON Schema validation, catch type mismatches and missing required fields)
- [ ] T043 [US2] Integrate Validation Agent into Orchestrator workflow in backend/src/agents/orchestrator.py (after tool selection, before tool execution: invoke Validation Agent, only proceed if validation_status=approved, return validation errors to user if rejected)
- [ ] T044 [US2] Create user-friendly validation error messages in Validation Agent (for entity_not_found: "Entity #{id} not found. Use 'list {entities}' to see available {entity_type}s.", for ambiguous_reference: list options with details)

**Checkpoint**: At this point, User Story 2 should work independently - Validation Agent prevents invalid operations and provides actionable guidance

---

## Phase 5: User Story 3 - Conversation Context Awareness (Priority: P3)

**Goal**: Enable Conversation Reasoning Agent to maintain conversation history and resolve implicit references like "mark it done" after "show task #5"

**Independent Test**: Conduct multi-turn conversations and verify pronouns and implicit references are correctly resolved using conversation history, independent of other agent functionality

### Implementation for User Story 3

- [ ] T045 [P] [US3] Create Conversation Reasoning Agent in backend/src/agents/conversation.py (uses OpenAI Agents SDK Agent class, retrieves sliding window context from database, resolves pronouns and implicit references, detects when clarification is needed)
- [ ] T046 [US3] Create POST /api/v1/agents/conversation/resolve-references endpoint in backend/src/api/routes.py (accepts current_request/conversation_id/user_id, invokes Conversation Agent, returns ConversationResponse per agent-api.yaml contract)
- [ ] T047 [US3] Implement sliding window context retrieval in Conversation Agent (query conversation_message table for last 10 messages WHERE conversation_id=? ORDER BY sequence_number DESC LIMIT 10)
- [ ] T048 [US3] Implement key entity retrieval in Conversation Agent (query conversation_entity table for all entities WHERE conversation_id=? ORDER BY last_mentioned_at DESC)
- [ ] T049 [US3] Implement reference resolution in Conversation Agent (use OpenAI function calling with conversation context to resolve "it", "that", "the task" to specific entity_type/entity_id/entity_name, return confidence score)
- [ ] T050 [US3] Implement entity tracking in Conversation Agent (after entity extraction by Orchestrator, upsert to conversation_entity table: increment mention_count, update last_mentioned_at for existing entities, insert new entities)
- [ ] T051 [US3] Implement ambiguity detection for references in Conversation Agent (when multiple entities could match reference, return status=clarification_needed with possible_entities and question)
- [ ] T052 [US3] Create conversation creation endpoint POST /api/v1/conversations in backend/src/api/routes.py (creates new Conversation record with user_id/application_domain, returns conversation_id)
- [ ] T053 [US3] Implement conversation message logging (in Orchestrator endpoint, after processing request: insert ConversationMessage record with role=user for input, role=agent for output, increment sequence_number)
- [ ] T054 [US3] Integrate Conversation Agent into Orchestrator workflow in backend/src/agents/orchestrator.py (if conversation_id provided: invoke Conversation Agent before intent classification to resolve references, use resolved_request for subsequent steps)

**Checkpoint**: All user stories 1-3 should now be independently functional - Conversation context enables natural follow-up commands

---

## Phase 6: User Story 4 - Graceful Error Recovery (Priority: P4)

**Goal**: Translate technical errors into user-friendly messages with concrete recovery steps when operations fail

**Independent Test**: Simulate various failure scenarios (timeouts, invalid states, tool errors) and verify friendly messages with actionable suggestions are returned, independent of other agent logic

### Implementation for User Story 4

- [ ] T055 [P] [US4] Create error humanization skill in backend/src/skills/error_humanizer.py (async function to translate error_type/error_message/error_code to user-friendly message, categorize as user_fixable/retryable/system_level, generate recovery_actions list)
- [ ] T056 [P] [US4] Create Error & Recovery Agent in backend/src/agents/error_recovery.py (uses OpenAI Agents SDK Agent class, invokes error_humanizer skill, implements retry logic with exponential backoff for retryable errors, logs errors with trace_id)
- [ ] T057 [US4] Create POST /api/v1/agents/error-recovery/handle endpoint in backend/src/api/routes.py (accepts error/context/user_id, invokes Error Agent, returns ErrorRecoveryResponse per agent-api.yaml contract)
- [ ] T058 [US4] Implement error categorization in Error Agent (pattern match common errors: timeout→retryable, not_found→user_fixable, validation_failed→user_fixable, unexpected→system_level)
- [ ] T059 [US4] Implement retry logic in Error Agent (for retryable errors: attempt up to 3 times with exponential backoff [1s, 2s, 4s], track retry_count in ToolInvocation, if all attempts fail: escalate to system_level)
- [ ] T060 [US4] Implement partial failure handling in Error Agent (for multi-step operations: track which steps succeeded, explain what completed and what failed, suggest how to complete remaining steps or rollback)
- [ ] T061 [US4] Create error taxonomy mapping in backend/src/core/errors.py (define error categories, map exception types to categories, include templates for common error messages)
- [ ] T062 [US4] Integrate Error Agent into Orchestrator workflow in backend/src/agents/orchestrator.py (wrap tool execution in try/except, on exception: invoke Error Agent, return error recovery response to user, never expose raw technical errors)
- [ ] T063 [US4] Add trace_id generation and logging (generate UUID trace_id at request start, include in all logs and error responses, store in AgentExecution.id for correlation)

**Checkpoint**: All 4 user stories should now be complete and independently testable - Error handling ensures graceful degradation

---

## Phase 7: Additional Requirements (From User Context)

**Purpose**: Implement additional governance and reusability requirements specified by user

- [ ] T064 [P] Define agent roles and authority document in specs/001-reusable-agents/agent-roles.md (specify decision-making authority for each agent: Orchestrator [tool selection, chaining], Validation [approve/reject operations], Conversation [reference resolution], Error Recovery [retry attempts, escalation]; define escalation boundaries: low confidence <0.8 → clarification, validation rejection → user, system errors → support)
- [ ] T065 [P] Define decision vs escalation boundaries document in specs/001-reusable-agents/escalation-boundaries.md (specify when agents decide autonomously vs ask user: high confidence ≥0.8 → decide, medium 0.6-0.8 → show confidence and ask, low <0.6 → clarify; define escalation triggers: ambiguous entity → user clarification, validation failure → user with options, repeated retry failures → system support)
- [ ] T066 [P] Define skill input/output contracts document in specs/001-reusable-agents/skill-contracts.md (formalize contracts already in skill-api.yaml: IntentClassificationInput/Output, EntityExtractionInput/Output, ToolSelectionInput/Output, ConfirmationGenerationInput/Output, ErrorHumanizationInput/Output; add versioning strategy, backward compatibility policy)
- [ ] T067 [P] Define reporting formats document in specs/001-reusable-agents/reporting-formats.md (specify structured output formats: agent responses include reasoning_trace array with step/action/input/output/confidence/timestamp, all responses include execution_id for tracking, errors include trace_id and error_category, tool invocations logged with duration and status)
- [ ] T068 [P] Define reuse guidelines document in specs/001-reusable-agents/reuse-guidelines.md (best practices for adding new domains: write clear tool descriptions ≥50 chars with examples, follow tool naming convention ^[a-z][a-z0-9_]*$, provide parameter_schema with descriptions, test tool selection accuracy, generate embeddings via sync_tools script; guidelines for extending agents: don't modify agent code for new domains, add logic as tools not hardcoded rules, use metadata field for domain-specific customization)

---

## Phase 8: Tool Infrastructure and Sync

**Purpose**: Enable dynamic tool registration and semantic search for tool discovery

- [ ] T069 Create tool sync script in backend/src/mcp/sync_tools.py (discovers all @server.tool decorated functions, extracts metadata, generates embeddings for descriptions using OpenAI text-embedding-3-small, upserts to tool_definition table with is_active=true)
- [ ] T070 [P] Create embedding generation utility in backend/src/mcp/sync_tools.py (async function to generate embeddings batch, cache results, handle rate limits)
- [ ] T071 [P] Create tool definition cache in backend/src/mcp/tool_registry.py (Redis cache for active tools, TTL=1 hour, cache invalidation on tool updates, fallback to database if cache miss)
- [ ] T072 Create GET /tools endpoint in backend/src/mcp/server.py (implements MCP tools interface from mcp-tools.yaml: list all active tools filtered by application_domain, return ToolDefinition schemas)
- [ ] T073 [P] Create GET /tools/{tool_name} endpoint in backend/src/mcp/server.py (retrieve specific tool definition by name, return 404 if not found)
- [ ] T074 [P] Create POST /tools/{tool_name}/search-similar endpoint in backend/src/mcp/server.py (implements semantic search from mcp-tools.yaml: generate embedding for query, perform pgvector cosine similarity search, return top-K tools with similarity scores above threshold)
- [ ] T075 Create example tool implementation for testing in backend/src/mcp/tools/example_tools.py (create list_todos, create_todo, update_todo tools using @server.tool decorator with detailed descriptions and parameter schemas per quickstart.md examples)

---

## Phase 9: Observability and Debugging

**Purpose**: Enable execution trace retrieval and debugging capabilities

- [ ] T076 Create GET /api/v1/agents/executions/{execution_id} endpoint in backend/src/api/routes.py (retrieves AgentExecution record by id, returns full execution trace with reasoning steps, confidence scores, tool invocations, timing data per agent-api.yaml)
- [ ] T077 [P] Create GET /api/v1/agents/executions endpoint in backend/src/api/routes.py (list agent executions with filters: user_id, agent_type, status, date_range; pagination support; returns summary view without full traces)
- [ ] T078 [P] Create metrics export endpoint GET /metrics in backend/src/api/routes.py (Prometheus format metrics: agent execution counts by type/status, tool invocation success rates, p95/p99 latencies, conversation context retrieval times)
- [ ] T079 [P] Implement structured logging throughout (use logging config from T008, include trace_id/user_id/agent_type in all log entries, log at INFO for decisions, DEBUG for detailed steps, ERROR for failures with full context)
- [ ] T080 [P] Create OpenTelemetry tracing integration in backend/src/core/tracing.py (optional, configure tracer, instrument FastAPI app, add spans for agent execution, skill invocation, tool calls, database queries)

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, documentation, and validation

- [ ] T081 [P] Create README.md in backend/ (project overview, architecture diagram, quick start instructions reference to quickstart.md, link to API docs at /docs endpoint)
- [ ] T082 [P] Update CLAUDE.md with implementation notes (document any deviations from plan, note performance optimizations made, record troubleshooting tips discovered during implementation)
- [ ] T083 [P] Create API documentation in backend/docs/ (copy contracts from specs/001-reusable-agents/contracts/ to backend/docs/, add examples for each endpoint, include curl commands and expected responses)
- [ ] T084 Run database migration (execute: alembic upgrade head in backend/ to create all tables and indexes)
- [ ] T085 Run tool sync for example tools (execute: python -m src.mcp.sync_tools --domain todo to register example_tools with embeddings)
- [ ] T086 Validate all endpoints return responses matching contracts (manually test or write validation script: invoke each endpoint from agent-api.yaml and mcp-tools.yaml, compare response schemas)
- [ ] T087 [P] Performance optimization pass (review database queries for N+1 issues, add connection pooling configuration, enable query result caching for tool definitions, optimize embedding generation batch sizes)
- [ ] T088 [P] Security hardening (validate all user inputs via Pydantic models, add rate limiting middleware for agent endpoints, sanitize error messages to prevent information leakage, ensure row-level security policies if multi-tenant)
- [ ] T089 Run quickstart validation (follow quickstart.md step-by-step, verify all examples work: environment setup, tool registration, agent invocation, conversation context, adding new domain)
- [ ] T090 Create deployment documentation in backend/docs/deployment.md (Docker build instructions, environment variable reference, database migration steps, health check configuration, monitoring setup, scaling considerations)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) completion - Can run in parallel with US1 after foundation
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) completion - Can run in parallel with US1/US2 after foundation
- **User Story 4 (Phase 6)**: Depends on Foundational (Phase 2) completion - Can run in parallel with US1/US2/US3 after foundation
- **Additional Requirements (Phase 7)**: Can run in parallel with user stories - these are documentation tasks
- **Tool Infrastructure (Phase 8)**: Depends on Foundational (Phase 2) completion - Can run in parallel with user stories
- **Observability (Phase 9)**: Depends on User Story 1 completion (needs agent execution to observe)
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories - Can start after Foundational
- **User Story 2 (P2)**: Integrates with User Story 1 (T043) but independently testable - Can start after Foundational
- **User Story 3 (P3)**: Integrates with User Story 1 (T054) but independently testable - Can start after Foundational
- **User Story 4 (P4)**: Integrates with User Story 1 (T062) but independently testable - Can start after Foundational

**Critical Path**: Setup → Foundational → User Story 1 → Integration → Observability → Polish

**Parallel Opportunities**: After Foundational, US1/US2/US3/US4 can proceed in parallel (if team capacity allows)

### Within Each User Story

**User Story 1**:
- T027, T028, T029, T030 can run in parallel (different skill files)
- T031 depends on T027-T030 (Orchestrator needs skills)
- T032-T034 depend on T031 (endpoint needs Orchestrator)
- T035 can run in parallel with T031-T034 (tool invocation independent)
- T036 depends on T031-T035 (multi-step chaining needs base orchestration)

**User Story 2**:
- T037 can start immediately after Foundational
- T038-T042 depend on T037 (endpoint and features need Validation Agent)
- T043-T044 integrate with Orchestrator (requires US1 T031)

**User Story 3**:
- T045, T046, T052 can start in parallel after Foundational
- T047-T051 depend on T045 (context features need Conversation Agent)
- T053 can run in parallel with T047-T051 (message logging independent)
- T054 integrates with Orchestrator (requires US1 T031)

**User Story 4**:
- T055, T056, T061 can start in parallel after Foundational
- T057-T060 depend on T055-T056 (endpoint and features need Error Agent and skill)
- T062-T063 integrate with Orchestrator (requires US1 T031)

---

## Parallel Execution Examples

### Parallel Example: Setup Phase (Phase 1)

All Setup tasks can run in parallel:
```bash
Task T001: Create backend project directory structure
Task T002: Initialize Python project with pyproject.toml
Task T003: Create .env.example file
Task T004: Create Dockerfile
Task T005: Create docker-compose.yml
Task T006: Create .gitignore
```

### Parallel Example: Foundational Phase (Phase 2)

After T007 completes, many foundational tasks can run in parallel:
```bash
# Database models (all independent)
Task T014: Create Conversation model
Task T015: Create ConversationMessage model
Task T016: Create ConversationEntity model
Task T017: Create AgentExecution model
Task T018: Create ToolDefinition model
Task T019: Create ToolInvocation model

# Configuration files (all independent)
Task T008: Create logging configuration
Task T009: Create application config
Task T023: Create request logging middleware

# API setup (can run in parallel)
Task T021: Create /health endpoint
Task T022: Create /ready endpoint
```

### Parallel Example: User Story 1 (Phase 3)

Skills can be implemented in parallel:
```bash
Task T027: Create intent classification skill
Task T028: Create entity extraction skill
Task T029: Create tool selection skill
Task T030: Create confirmation generation skill
# All 4 skills are in different files with no dependencies
```

### Parallel Example: After Foundational

Once Foundational is complete, all user stories can start in parallel:
```bash
# Team Member 1: User Story 1
Task T027: Start implementing intent classification skill

# Team Member 2: User Story 2
Task T037: Start implementing Validation Agent

# Team Member 3: User Story 3
Task T045: Start implementing Conversation Reasoning Agent

# Team Member 4: User Story 4
Task T055: Start implementing error humanization skill

# Team Member 5: Documentation
Task T064: Define agent roles and authority document
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (6 tasks)
2. Complete Phase 2: Foundational (20 tasks) - CRITICAL checkpoint
3. Complete Phase 3: User Story 1 (10 tasks)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Send natural language requests across domains (todo/crm/notes)
   - Verify intent classification accuracy
   - Verify tool selection works
   - Verify tool execution succeeds
   - Check reasoning traces are complete
5. Deploy/demo if ready - **Working MVP with basic agent orchestration!**

### Incremental Delivery

1. Complete Setup + Foundational → **Foundation ready** (26 tasks)
2. Add User Story 1 → Test independently → Deploy/Demo → **MVP** (36 tasks total)
3. Add User Story 2 → Test independently → Deploy/Demo → **Validation added** (44 tasks total)
4. Add User Story 3 → Test independently → Deploy/Demo → **Conversation context added** (54 tasks total)
5. Add User Story 4 → Test independently → Deploy/Demo → **Error handling added** (63 tasks total)
6. Add Tool Infrastructure → **Dynamic tool discovery** (70 tasks total)
7. Add Observability → **Production-ready monitoring** (75 tasks total)
8. Polish → **Complete system** (90 tasks total)

Each increment adds value without breaking previous functionality

### Parallel Team Strategy

With multiple developers after Foundational completes:

1. **Team completes Setup + Foundational together** (26 tasks)
2. **Once Foundational done, split work**:
   - **Developer A**: User Story 1 (T027-T036) - 10 tasks
   - **Developer B**: User Story 2 (T037-T044) - 8 tasks
   - **Developer C**: User Story 3 (T045-T054) - 10 tasks
   - **Developer D**: User Story 4 (T055-T063) - 9 tasks
   - **Developer E**: Tool Infrastructure + Docs (T064-T075) - 12 tasks
3. Stories complete and integrate independently
4. Final integration testing when all stories done
5. Observability + Polish together (T076-T090) - 15 tasks

**Total: 90 tasks**

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable per spec.md acceptance scenarios
- User Story 1 is the MVP - basic orchestration works end-to-end
- User Stories 2-4 enhance User Story 1 with validation, context, and error handling
- Stop at any checkpoint to validate story independently
- All tasks have explicit file paths for implementation
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
