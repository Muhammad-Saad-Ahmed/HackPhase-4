# Research: Reusable AI Agents and Skills

**Feature**: 001-reusable-agents
**Date**: 2026-01-16
**Phase**: 0 - Technology Research and Decision Making

## Overview

This document consolidates research findings for technology choices, architectural patterns, and best practices for implementing reusable AI agents and skills that operate via MCP tools across multiple application domains.

## Technology Stack Decisions

### 1. Agent Framework: OpenAI Agents SDK

**Decision**: Use OpenAI Agents SDK for agent implementation

**Rationale**:
- **Constitution Mandate**: Principle VIII requires OpenAI Agents SDK
- **Native Tool Support**: Built-in support for function calling and tool orchestration
- **Structured Output**: Supports JSON schema-based responses for deterministic outputs (FR-026)
- **Streaming Support**: Enables real-time agent reasoning visibility (FR-025, FR-029)
- **Production-Ready**: Battle-tested in production environments with strong error handling

**Alternatives Considered**:
- LangChain/LangGraph: More flexibility but introduces complexity; custom agent frameworks violate constitution
- Anthropic SDK: Not mandated by constitution; less standardized for multi-model scenarios
- Custom Framework: Violates Principle VIII and increases maintenance burden

**Implementation Notes**:
- Use Agents SDK's `Agent` class for each agent type (Orchestrator, Validation, Conversation, Error Recovery)
- Leverage `@tool` decorators for skill functions to make them agent-invocable
- Use `Agent.run()` with streaming enabled for explainable outputs (FR-025)

---

### 2. MCP Implementation: Official MCP SDK (Python)

**Decision**: Use Official MCP SDK for Python to implement MCP server

**Rationale**:
- **Constitution Mandate**: Principle VII requires Official MCP SDK
- **Protocol Compliance**: Ensures compatibility with MCP clients and ecosystem tools
- **Type Safety**: Provides Pydantic models for tool schemas and messages
- **Server Lifecycle Management**: Handles connection management, tool registration, and request routing
- **Security**: Built-in security features and protocol-level error handling

**Alternatives Considered**:
- Custom MCP Implementation: Violates Principle VII; high risk of protocol incompatibility
- Third-party MCP wrappers: Not officially supported; potential breaking changes

**Implementation Notes**:
- Create MCP server in `backend/src/mcp/server.py` using `mcp.server.Server`
- Define tools as async functions decorated with `@server.tool()`
- Use `Tool` schema objects to provide rich metadata (description, parameter types, examples) for agent discovery
- Implement dynamic tool registry for runtime tool addition (FR-030)

**Best Practices**:
- Tool descriptions should be verbose and include examples (helps intent classification)
- Use JSON Schema for parameter validation to catch errors at MCP layer before agent execution
- Implement tool versioning in metadata to support backward compatibility

---

### 3. Backend Framework: FastAPI

**Decision**: Use FastAPI for REST API layer and MCP server hosting

**Rationale**:
- **Constitution Mandate**: Principle IX requires FastAPI
- **Async Native**: Full async/await support for concurrent agent requests
- **Type Safety**: Pydantic integration provides request/response validation
- **OpenAPI Auto-generation**: Automatic API documentation for agent endpoints
- **Performance**: Uvicorn/ASGI provides high-throughput request handling (supports 100+ concurrent requests per spec)

**Implementation Notes**:
- Main FastAPI app in `backend/src/api/routes.py`
- Agent invocation endpoint: `POST /agents/{agent_type}/invoke`
- Health check and tool introspection endpoints for observability
- Middleware for request logging and agent execution tracing (FR-025)

**Best Practices**:
- Use FastAPI dependency injection for database sessions and agent instances
- Implement rate limiting middleware to prevent abuse
- Use Pydantic models for all request/response bodies to ensure type safety

---

### 4. Database: Neon PostgreSQL + SQLModel ORM

**Decision**: Use Neon PostgreSQL for persistence with SQLModel as ORM

**Rationale**:
- **Constitution Mandate**: Principle V requires Neon PostgreSQL; Principle X requires SQLModel
- **Managed Service**: Neon provides serverless PostgreSQL with branching and auto-scaling
- **Type Safety**: SQLModel combines Pydantic and SQLAlchemy for type-safe database operations
- **Migration Support**: Alembic integration for schema versioning
- **JSON Support**: Native JSONB type for flexible conversation context storage

**Data Storage Requirements**:
- **Conversation Context** (FR-012): Store message history, referenced entities, active topics
- **Agent Execution Logs** (FR-025): Store agent decisions, confidence scores, reasoning traces
- **Tool Metadata**: Store tool schemas, descriptions, and versioning for dynamic discovery

**Implementation Notes**:
- Define SQLModel entities in `backend/src/models/`
- Use Alembic for migrations in `backend/migrations/`
- Implement repository pattern for database access with context managers
- Use PostgreSQL's JSONB for conversation context to support flexible schema evolution

**Best Practices**:
- Index conversation_id and user_id columns for fast context retrieval
- Use database transactions for multi-step operations to ensure atomicity
- Implement soft deletes for audit trail compliance
- Set up connection pooling for concurrent request handling

---

### 5. Intent Classification & Entity Extraction: OpenAI Function Calling

**Decision**: Use OpenAI's function calling with structured outputs for intent and entity extraction

**Rationale**:
- **Accuracy**: OpenAI models excel at understanding intent from natural language
- **Structured Output**: JSON schema enforcement ensures deterministic outputs (FR-026)
- **No Training Required**: Zero-shot classification works across domains (FR-001, FR-020)
- **Confidence Scores**: Log probabilities provide confidence metrics (FR-029)

**Implementation Approach**:
- Define intent classification as a function with enum of intent types (create, read, update, delete, list, search, analyze)
- Define entity extraction as a function that returns structured entity objects with type and attributes
- Use OpenAI SDK's `response_format` parameter for JSON schema enforcement

**Alternative Considered**:
- Traditional NLP (spaCy, NLTK): Requires domain-specific training; doesn't meet app-agnostic requirement
- Fine-tuned models: Violates reusability principle; requires per-domain training

**Best Practices**:
- Provide rich examples in system prompts to guide classification
- Use temperature=0 for deterministic outputs
- Implement fallback logic for low-confidence predictions (threshold: 0.8 per spec assumptions)
- Cache common intent patterns to reduce API costs

---

### 6. Tool Selection: Semantic Similarity + Schema Matching

**Decision**: Use embedding-based semantic similarity combined with parameter schema matching for tool selection

**Rationale**:
- **Scalability**: Works with 50+ tools per domain without hardcoded mappings (FR-003)
- **Accuracy**: Semantic search finds best tool match based on intent and tool descriptions
- **Schema Validation**: Parameter matching ensures selected tool can fulfill request
- **Extensibility**: New tools automatically available without code changes (FR-030)

**Implementation Approach**:
1. Generate embeddings for tool descriptions using OpenAI's text-embedding-3-small model
2. Store embeddings in PostgreSQL using pgvector extension
3. At runtime: Generate embedding for user intent + extracted entities
4. Find top-K similar tools via cosine similarity
5. Filter by parameter schema compatibility
6. Return best match with confidence score

**Alternative Considered**:
- Keyword matching: Too rigid; fails on paraphrasing
- LLM tool selection: More expensive; adds latency; semantic similarity is sufficient

**Best Practices**:
- Update embeddings when tool descriptions change
- Use hybrid search (semantic + keyword) for better recall
- Implement tool usage tracking to learn from successful selections
- Set similarity threshold (0.75) to trigger clarification when no confident match exists

---

### 7. Conversation Context Management: Sliding Window with Key Entity Persistence

**Decision**: Use sliding window (last 10 messages) with persistent key entity tracking

**Rationale**:
- **Predictable Performance**: Fixed context size prevents unbounded token growth (addresses spec clarification needed)
- **Critical Context Preservation**: Key entities (referenced IDs, names) stored separately and always available
- **Simplicity**: Easier to implement and reason about than AI summarization
- **Cost-Effective**: No additional API calls for summarization

**Implementation Approach**:
- Store full conversation history in database (conversation_messages table)
- On context retrieval: Fetch last 10 messages + all key entities from session
- Key entities extracted via entity extraction skill and stored in conversation_entities table
- Use PostgreSQL window functions for efficient message retrieval

**Alternative Considered**:
- AI Summarization (spec option A): More expensive; adds latency; risk of losing important details
- Unlimited context (spec option C): Unsustainable; will hit token limits and degrade performance

**Rationale for Choice**:
- Balances context preservation with performance/cost constraints
- 10 messages typically cover 5-10 conversational turns, sufficient for most reference resolution
- Key entities persist indefinitely, enabling "earlier you said X" references

**Best Practices**:
- Implement context compression for very long messages (>500 tokens)
- Provide users with command to "clear context" for new conversation threads
- Log context retrieval patterns to tune window size empirically

---

### 8. Error Handling Strategy: Categorized Errors with Recovery Actions

**Decision**: Implement 3-tier error classification with mapped recovery strategies

**Rationale**:
- **User-Friendly**: Clear categorization helps users understand what went wrong (FR-016)
- **Actionable**: Each category has specific recovery steps (FR-017)
- **Agent-Friendly**: Structured errors enable Error Agent to reason about recovery (FR-018)

**Error Categories**:

1. **User-Fixable Errors** (validation, missing parameters):
   - Examples: Missing required field, invalid entity ID, ambiguous reference
   - Recovery: Explain what's needed with clear examples
   - Template: "{Error context}. {Required action}. {Example if applicable}"

2. **Retryable Errors** (transient failures):
   - Examples: Network timeout, database connection lost, rate limit
   - Recovery: Automatic retry with exponential backoff (3 attempts)
   - Template: "Unable to {action} due to temporary issue. Retrying... [{attempt}/3]"

3. **System-Level Errors** (bugs, infrastructure failures):
   - Examples: Tool unavailable, unexpected error, data corruption
   - Recovery: Log for debugging, escalate to human support
   - Template: "An unexpected error occurred. Our team has been notified. Reference ID: {trace_id}"

**Implementation Approach**:
- Create error taxonomy in `backend/src/core/errors.py`
- Error Recovery Agent maps exceptions to categories using pattern matching
- Use Pydantic models for structured error responses
- Include trace_id in all errors for debugging

**Best Practices**:
- Never expose raw technical error messages to users
- Include context about what the user was trying to do
- Provide specific next steps, not generic "try again later" messages
- Log all errors with full stack traces for debugging (FR-025)

---

### 9. Agent Determinism: Seed-Based Execution with Fixed Parameters

**Decision**: Use temperature=0, fixed seeds, and deterministic tool selection for reproducible agent behavior

**Rationale**:
- **Constitutional Requirement**: FR-026 mandates deterministic agent behavior
- **Debuggability**: Same input produces same output, critical for testing and debugging
- **Predictability**: Users can rely on consistent agent responses for similar requests

**Implementation Approach**:
- Set `temperature=0` for all LLM calls
- Use deterministic seed values for tool selection when multiple tools match (e.g., sort by alphabetical order)
- Cache intent/entity classifications to avoid non-deterministic variations
- Disable randomness in skill functions (no `random.choice`, use reproducible sorting)

**Testing Strategy**:
- Create determinism test suite that runs identical requests multiple times
- Assert that agent outputs (intent, entities, tool selection, responses) are identical
- Use snapshot testing for regression detection

**Edge Cases**:
- When multiple tools have identical semantic similarity scores, use alphabetical ordering as tiebreaker
- For time-sensitive operations, pass explicit timestamps rather than using `datetime.now()`

---

### 10. Performance Optimization: Async Operations and Connection Pooling

**Decision**: Use asynchronous I/O throughout and implement connection pooling for database and API calls

**Rationale**:
- **Concurrency**: Support 100+ concurrent agent requests per spec
- **Latency**: Meet <500ms p95 latency target
- **Resource Efficiency**: Async I/O prevents thread blocking during network/database operations

**Implementation Approach**:
- Use `async def` for all agents, skills, and tool functions
- Implement async database session management with SQLAlchemy async engine
- Use `asyncio.gather()` for parallel tool calls in multi-step requests
- Set up connection pooling for PostgreSQL (pool size: 20 connections)
- Use OpenAI SDK's async client for concurrent LLM calls

**Connection Pool Configuration**:
```python
DATABASE_URL = "postgresql+asyncpg://..."
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600     # Recycle connections hourly
)
```

**Best Practices**:
- Use `async with` context managers for database sessions
- Implement request timeouts to prevent hanging requests
- Monitor connection pool utilization and adjust sizing based on load
- Use APM tools (e.g., DataDog, New Relic) to track async task performance

---

## Architectural Patterns

### Agent Orchestration Flow

```
User Request
    ↓
FastAPI Endpoint
    ↓
Orchestrator Agent
    ↓
[Intent Classification] → [Entity Extraction] → [Tool Selection]
    ↓
Validation Agent (checks entity existence, validates parameters)
    ↓
MCP Tool Execution (via MCP SDK)
    ↓
Confirmation Generation
    ↓
Response to User
```

### Error Handling Flow

```
Tool Execution Error
    ↓
Error & Recovery Agent
    ↓
Categorize Error (user-fixable / retryable / system-level)
    ↓
If retryable: Retry with backoff (max 3 attempts)
If user-fixable: Generate actionable message
If system-level: Log + escalate + user-friendly message
    ↓
Return Structured Error Response
```

### Conversation Context Flow

```
New Message Arrives
    ↓
Retrieve Sliding Window (last 10 messages + key entities)
    ↓
Conversation Reasoning Agent
    ↓
Resolve Pronouns/References using context
    ↓
If ambiguous: Request clarification
If resolved: Update context with new entities
    ↓
Pass resolved request to Orchestrator
```

---

## Security Considerations

1. **Input Validation**: All user inputs validated via Pydantic models before agent processing
2. **Tool Authorization**: MCP server validates that requested tool exists and is accessible
3. **SQL Injection Prevention**: SQLModel's parameterized queries prevent SQL injection
4. **Rate Limiting**: FastAPI middleware limits requests per user to prevent abuse
5. **Audit Logging**: All agent executions logged with user_id, timestamp, and trace_id (FR-025)
6. **Secrets Management**: Database credentials and API keys stored in environment variables, never in code

---

## Testing Strategy

### Unit Tests
- Individual skill functions (intent classification, entity extraction, etc.)
- Agent decision logic with mocked tool calls
- Error categorization and message generation

### Integration Tests
- Full agent workflows (request → orchestrator → validation → tool execution → response)
- Multi-step tool chaining scenarios
- Error handling and retry logic

### Contract Tests
- MCP tool interface validation (schema compliance)
- Agent API endpoint contracts (request/response formats)
- Database model validation (SQLModel schema checks)

### Performance Tests
- Load testing for 100+ concurrent requests
- Latency benchmarking for p95 <500ms target
- Database connection pool stress testing

---

## Deployment Considerations

1. **Containerization**: Dockerfile for backend with multi-stage builds (dev/prod)
2. **Database Migrations**: Alembic migrations run automatically on deployment
3. **Environment Configuration**: 12-factor app principles with environment-specific configs
4. **Health Checks**: `/health` endpoint for orchestration platforms (Kubernetes, ECS)
5. **Observability**: Structured logging, metrics export (Prometheus), and distributed tracing (OpenTelemetry)
6. **Scaling Strategy**: Horizontal scaling of backend containers; vertical scaling of PostgreSQL

---

## Open Questions Resolved

1. **Deletion behavior for entities with dependencies** (from spec clarification):
   - **Decision**: Option C - Warn user and require explicit confirmation
   - **Rationale**: Balances safety with user autonomy; prevents accidental data loss while allowing intentional cascades
   - **Implementation**: Validation Agent detects dependencies via tool metadata and generates confirmation request

2. **Conversation context retention policy** (from spec clarification):
   - **Decision**: Sliding window (last 10 messages) with persistent key entities
   - **Rationale**: See section 7 above - balances performance, cost, and context preservation

---

## References

- OpenAI Agents SDK Documentation: https://platform.openai.com/docs/agents
- Official MCP SDK (Python): https://github.com/modelcontextprotocol/python-sdk
- FastAPI Best Practices: https://fastapi.tiangolo.com/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- Neon PostgreSQL: https://neon.tech/docs
- Agent Design Patterns: Industry best practices for stateless, tool-driven agent architectures
