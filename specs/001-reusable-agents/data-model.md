# Data Model: Reusable AI Agents and Skills

**Feature**: 001-reusable-agents
**Date**: 2026-01-16
**Phase**: 1 - Data Model Design

## Overview

This document defines the data entities for the reusable AI agents system. All entities are persisted in Neon PostgreSQL using SQLModel ORM, following constitution principles IV (stateless backend) and V (database as source of truth).

---

## Entity Definitions

### 1. Conversation

Stores conversation history and metadata for multi-turn interactions (FR-012, FR-013).

**Purpose**: Enable Conversation Reasoning Agent to resolve implicit references and maintain context across messages.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique conversation identifier |
| user_id | String(255) | NOT NULL, Index | User who owns this conversation |
| application_domain | String(50) | NOT NULL | Application context (todo, crm, notes) |
| created_at | DateTime | NOT NULL, Default=now() | Conversation start timestamp |
| updated_at | DateTime | NOT NULL, Default=now() | Last message timestamp |
| status | Enum | NOT NULL, Default=active | active, archived, deleted |
| metadata | JSONB | NULL | Optional conversation metadata (tags, labels) |

**Relationships**:
- One-to-many with ConversationMessage (conversation has many messages)
- One-to-many with ConversationEntity (conversation tracks many entities)

**Indexes**:
- PRIMARY KEY (id)
- INDEX (user_id, created_at DESC) - For user conversation history lookup
- INDEX (application_domain) - For domain-specific analytics

**Validation Rules**:
- user_id must not be empty
- application_domain must match known domains or be "generic"
- status transitions: active → archived OR active → deleted (no reversals)

**State Transitions**:
```
[created] → active → archived
                  ↘ deleted
```

---

### 2. ConversationMessage

Stores individual messages within a conversation (implements sliding window context per research.md).

**Purpose**: Provide message history for context retrieval and conversation analysis.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique message identifier |
| conversation_id | UUID | FK, NOT NULL, Index | Parent conversation |
| role | Enum | NOT NULL | user, agent, system, tool |
| content | Text | NOT NULL | Message content (user input or agent response) |
| sequence_number | Integer | NOT NULL | Message order within conversation |
| timestamp | DateTime | NOT NULL, Default=now() | Message creation time |
| agent_type | String(50) | NULL | Which agent generated this (orchestrator, validation, etc.) |
| tool_calls | JSONB | NULL | Tools invoked during this message (for audit) |
| metadata | JSONB | NULL | Additional message metadata (confidence scores, reasoning traces) |

**Relationships**:
- Many-to-one with Conversation (message belongs to conversation)

**Indexes**:
- PRIMARY KEY (id)
- INDEX (conversation_id, sequence_number ASC) - For ordered message retrieval
- INDEX (conversation_id, timestamp DESC) - For sliding window queries

**Validation Rules**:
- sequence_number must be unique within conversation_id
- role must be one of: user, agent, system, tool
- content must not be empty
- agent_type required if role = agent

**Query Patterns**:
```sql
-- Retrieve sliding window (last 10 messages)
SELECT * FROM conversation_message
WHERE conversation_id = ?
ORDER BY sequence_number DESC
LIMIT 10;

-- Get full conversation history
SELECT * FROM conversation_message
WHERE conversation_id = ?
ORDER BY sequence_number ASC;
```

---

### 3. ConversationEntity

Stores key entities extracted from conversation for persistent reference resolution (FR-012).

**Purpose**: Enable "mark it done" references where "it" refers to entity mentioned earlier in conversation.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique entity reference identifier |
| conversation_id | UUID | FK, NOT NULL, Index | Parent conversation |
| entity_type | String(100) | NOT NULL | Entity type (task, customer, note, meeting, etc.) |
| entity_id | String(255) | NOT NULL | Application-specific entity identifier |
| entity_name | String(500) | NULL | Human-readable entity name/title |
| first_mentioned_at | DateTime | NOT NULL | When entity was first referenced |
| last_mentioned_at | DateTime | NOT NULL | Most recent mention timestamp |
| mention_count | Integer | NOT NULL, Default=1 | Number of times referenced |
| metadata | JSONB | NULL | Additional entity attributes extracted |

**Relationships**:
- Many-to-one with Conversation (entities belong to conversation)

**Indexes**:
- PRIMARY KEY (id)
- INDEX (conversation_id, last_mentioned_at DESC) - For recency-based resolution
- INDEX (conversation_id, entity_type) - For type-specific lookups
- UNIQUE (conversation_id, entity_type, entity_id) - Prevent duplicate tracking

**Validation Rules**:
- entity_type must not be empty
- entity_id must not be empty
- mention_count must be positive integer
- last_mentioned_at >= first_mentioned_at

**Query Patterns**:
```sql
-- Get most recently mentioned entities
SELECT * FROM conversation_entity
WHERE conversation_id = ?
ORDER BY last_mentioned_at DESC
LIMIT 5;

-- Find entity by partial name match
SELECT * FROM conversation_entity
WHERE conversation_id = ?
  AND entity_name ILIKE ?
ORDER BY mention_count DESC, last_mentioned_at DESC;
```

---

### 4. AgentExecution

Stores agent execution logs for auditability and explainability (FR-025, FR-029).

**Purpose**: Provide execution traces showing agent reasoning, decisions, and confidence scores.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique execution identifier |
| conversation_id | UUID | FK, NULL | Associated conversation (null for stateless calls) |
| user_id | String(255) | NOT NULL, Index | User who triggered execution |
| agent_type | Enum | NOT NULL | orchestrator, validation, conversation, error_recovery |
| input_data | JSONB | NOT NULL | Agent input (user request, context, parameters) |
| output_data | JSONB | NOT NULL | Agent output (decisions, selected tools, responses) |
| execution_start | DateTime | NOT NULL | Execution start timestamp |
| execution_end | DateTime | NOT NULL | Execution completion timestamp |
| duration_ms | Integer | NOT NULL | Execution duration in milliseconds |
| status | Enum | NOT NULL | success, failure, partial |
| error_details | JSONB | NULL | Error information if status=failure |
| reasoning_trace | JSONB | NULL | Step-by-step reasoning log (for explainability) |
| confidence_scores | JSONB | NULL | Confidence metrics for decisions made |
| tools_invoked | JSONB | NULL | List of tools called during execution |

**Relationships**:
- Many-to-one with Conversation (execution may belong to conversation)

**Indexes**:
- PRIMARY KEY (id)
- INDEX (conversation_id, execution_start DESC) - For conversation history
- INDEX (user_id, execution_start DESC) - For user activity tracking
- INDEX (agent_type, status) - For agent performance analytics
- INDEX (execution_start DESC) - For time-based queries

**Validation Rules**:
- execution_end >= execution_start
- duration_ms = (execution_end - execution_start) in milliseconds
- status must be one of: success, failure, partial
- error_details required if status=failure or partial
- reasoning_trace should be array of step objects

**Query Patterns**:
```sql
-- Get execution history for debugging
SELECT * FROM agent_execution
WHERE conversation_id = ?
ORDER BY execution_start ASC;

-- Performance analytics
SELECT agent_type,
       AVG(duration_ms) as avg_duration,
       PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) as p95_duration
FROM agent_execution
WHERE execution_start > NOW() - INTERVAL '24 hours'
GROUP BY agent_type;
```

**Reasoning Trace Format** (JSONB example):
```json
{
  "steps": [
    {
      "step": 1,
      "action": "classify_intent",
      "input": "show my tasks",
      "output": "list",
      "confidence": 0.95,
      "timestamp": "2026-01-16T10:30:00Z"
    },
    {
      "step": 2,
      "action": "select_tool",
      "input": {"intent": "list", "entity_type": "task"},
      "output": "list_todos",
      "confidence": 0.92,
      "timestamp": "2026-01-16T10:30:00.150Z"
    }
  ]
}
```

---

### 5. ToolDefinition

Stores registered MCP tool definitions and metadata for dynamic discovery (FR-030).

**Purpose**: Enable Orchestrator to discover available tools without hardcoded mappings; support tool versioning.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique tool identifier |
| tool_name | String(255) | NOT NULL, Unique | Tool name (e.g., list_todos, create_customer) |
| tool_version | String(50) | NOT NULL, Default=1.0.0 | Semantic version |
| application_domain | String(50) | NOT NULL, Index | Domain this tool belongs to (todo, crm, notes) |
| description | Text | NOT NULL | Human-readable tool description (used for semantic search) |
| description_embedding | Vector(1536) | NULL | Text embedding for semantic tool selection |
| parameter_schema | JSONB | NOT NULL | JSON Schema for tool parameters |
| return_schema | JSONB | NOT NULL | JSON Schema for tool return value |
| is_active | Boolean | NOT NULL, Default=true | Whether tool is available for use |
| requires_validation | Boolean | NOT NULL, Default=false | Whether Validation Agent should check entity existence |
| created_at | DateTime | NOT NULL, Default=now() | Tool registration timestamp |
| updated_at | DateTime | NOT NULL, Default=now() | Last tool metadata update |
| metadata | JSONB | NULL | Additional tool metadata (tags, categories, examples) |

**Relationships**:
- None (tools are self-contained definitions)

**Indexes**:
- PRIMARY KEY (id)
- UNIQUE INDEX (tool_name, tool_version) - Ensure unique tool+version combinations
- INDEX (application_domain, is_active) - For domain-specific tool discovery
- VECTOR INDEX (description_embedding) USING ivfflat - For semantic search (pgvector extension)

**Validation Rules**:
- tool_name must match pattern: ^[a-z][a-z0-9_]*$ (lowercase, underscores)
- tool_version must match semantic versioning: ^\\d+\\.\\d+\\.\\d+$
- description must be at least 50 characters (detailed enough for semantic search)
- parameter_schema and return_schema must be valid JSON Schema objects
- description_embedding must be 1536-dimensional vector (OpenAI text-embedding-3-small)

**Query Patterns**:
```sql
-- Find tools by semantic similarity
SELECT tool_name, description,
       (description_embedding <=> ?) as distance
FROM tool_definition
WHERE application_domain = ? AND is_active = true
ORDER BY distance ASC
LIMIT 5;

-- Get all active tools for a domain
SELECT * FROM tool_definition
WHERE application_domain = ? AND is_active = true
ORDER BY tool_name ASC;
```

**Parameter Schema Example** (JSONB):
```json
{
  "type": "object",
  "properties": {
    "title": {"type": "string", "description": "Task title"},
    "status": {"type": "string", "enum": ["todo", "done"], "description": "Task status"}
  },
  "required": ["title"]
}
```

---

### 6. ToolInvocation

Stores individual tool execution records for observability and analytics (FR-025).

**Purpose**: Audit trail of all tool calls; track tool performance and success rates.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique invocation identifier |
| agent_execution_id | UUID | FK, NULL | Parent agent execution (null for direct tool calls) |
| tool_definition_id | UUID | FK, NOT NULL | Tool that was invoked |
| input_parameters | JSONB | NOT NULL | Parameters passed to tool |
| output_result | JSONB | NULL | Tool return value (null if error) |
| invocation_start | DateTime | NOT NULL | Invocation start timestamp |
| invocation_end | DateTime | NOT NULL | Invocation completion timestamp |
| duration_ms | Integer | NOT NULL | Invocation duration in milliseconds |
| status | Enum | NOT NULL | success, failure, timeout |
| error_details | JSONB | NULL | Error information if status=failure/timeout |
| retry_count | Integer | NOT NULL, Default=0 | Number of retry attempts |

**Relationships**:
- Many-to-one with AgentExecution (invocation belongs to execution)
- Many-to-one with ToolDefinition (invocation uses specific tool)

**Indexes**:
- PRIMARY KEY (id)
- INDEX (agent_execution_id, invocation_start ASC) - For execution timeline
- INDEX (tool_definition_id, status) - For tool reliability analytics
- INDEX (invocation_start DESC) - For time-based queries

**Validation Rules**:
- invocation_end >= invocation_start
- duration_ms = (invocation_end - invocation_start) in milliseconds
- status must be one of: success, failure, timeout
- error_details required if status=failure or timeout
- retry_count must be non-negative

**Query Patterns**:
```sql
-- Tool success rate analytics
SELECT td.tool_name,
       COUNT(*) as total_invocations,
       SUM(CASE WHEN ti.status = 'success' THEN 1 ELSE 0 END) as successes,
       AVG(ti.duration_ms) as avg_duration_ms
FROM tool_invocation ti
JOIN tool_definition td ON ti.tool_definition_id = td.id
WHERE ti.invocation_start > NOW() - INTERVAL '24 hours'
GROUP BY td.tool_name;
```

---

## Entity Relationship Diagram

```
Conversation (1) ─────< ConversationMessage (N)
     │
     └──────< ConversationEntity (N)
     │
     └──────< AgentExecution (N)
                   │
                   └──────< ToolInvocation (N)
                                 │
                                 └──────> ToolDefinition (1)
```

---

## Database Schema Migrations

### Migration 001: Initial Schema

**File**: `backend/migrations/versions/001_initial_schema.py`

**Operations**:
1. Create `conversation` table
2. Create `conversation_message` table with FK to conversation
3. Create `conversation_entity` table with FK to conversation
4. Create `agent_execution` table with FK to conversation
5. Create `tool_definition` table
6. Create `tool_invocation` table with FKs to agent_execution and tool_definition
7. Create all indexes
8. Enable pgvector extension for vector similarity search
9. Create vector index on `tool_definition.description_embedding`

**Rollback**: Drop all tables in reverse order

---

## Data Retention Policy

| Entity | Retention Period | Rationale |
|--------|------------------|-----------|
| Conversation | 90 days (active), then archive | Balance user privacy with useful conversation history |
| ConversationMessage | Same as parent conversation | Messages meaningless without conversation context |
| ConversationEntity | Same as parent conversation | Entities tracked for conversation duration only |
| AgentExecution | 30 days | Debugging and analytics; older data less valuable |
| ToolInvocation | 30 days | Performance analytics; aggregate then purge details |
| ToolDefinition | Indefinite (soft delete) | Tool registry must persist for system operation |

**Implementation**: Background job runs daily to archive/purge expired records.

---

## Performance Considerations

1. **Connection Pooling**: SQLAlchemy async engine with pool_size=20, max_overflow=10
2. **Query Optimization**: All foreign keys indexed; composite indexes for common query patterns
3. **Partitioning**: Consider table partitioning by time for `agent_execution` and `tool_invocation` if volume exceeds 10M rows
4. **Caching**: Tool definitions cached in-memory (Redis) to avoid repeated database lookups
5. **Batch Operations**: Use bulk insert for agent execution logging to reduce database roundtrips

---

## Security Considerations

1. **Row-Level Security**: PostgreSQL RLS policies enforce user_id-based access control
2. **Sensitive Data**: No PII stored in metadata fields; user_id is opaque identifier
3. **Audit Trail**: All agent executions and tool invocations logged with user attribution
4. **Data Encryption**: Database encrypted at rest (Neon provides this by default)
5. **SQL Injection Prevention**: SQLModel parameterized queries prevent injection attacks

---

## Testing Strategy

### Schema Validation Tests
- Verify all SQLModel models match database schema
- Test constraint violations (e.g., null required fields, invalid enum values)
- Validate foreign key cascades and referential integrity

### Query Performance Tests
- Benchmark sliding window query (<50ms for 10 messages)
- Test semantic similarity search (<100ms for top-5 tools)
- Verify index usage with EXPLAIN ANALYZE

### Data Integrity Tests
- Test conversation state transitions (active → archived → deleted)
- Verify entity uniqueness constraints (no duplicate entity tracking)
- Test cascading deletes (conversation deletion removes all messages/entities)

---

## Future Enhancements

1. **Tool Usage Learning**: Track tool selection patterns to improve semantic search ranking
2. **Conversation Summarization**: Add `conversation_summary` table for long-term context compression
3. **Multi-tenancy**: Add `tenant_id` column for SaaS deployment
4. **Tool Marketplace**: Extend ToolDefinition with pricing, ratings, and usage metrics
