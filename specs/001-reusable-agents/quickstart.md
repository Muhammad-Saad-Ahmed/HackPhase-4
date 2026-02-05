# Quickstart Guide: Reusable AI Agents and Skills

**Feature**: 001-reusable-agents
**Date**: 2026-01-16
**Audience**: Developers implementing or using the agent system

## Overview

This guide provides step-by-step instructions for setting up, using, and extending the reusable AI agents and skills system. Follow this guide to:

1. Set up the development environment
2. Run the agent system locally
3. Invoke agents via API
4. Register new tools for your application domain
5. Test and debug agent behavior

---

## Prerequisites

Before starting, ensure you have:

- Python 3.11 or higher
- PostgreSQL 15+ (or Neon account for managed PostgreSQL)
- OpenAI API key with access to GPT-4 models
- Docker and Docker Compose (for local development)
- Git

---

## 1. Environment Setup

### Clone the Repository

```bash
git clone <repository-url>
cd <repository-root>
git checkout 001-reusable-agents
```

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Key Dependencies**:
- `openai-agents-sdk`: Agent framework
- `mcp-sdk`: Official MCP SDK
- `fastapi`: REST API framework
- `sqlmodel`: Database ORM
- `pydantic`: Data validation
- `asyncpg`: Async PostgreSQL driver
- `pgvector`: Vector similarity search extension
- `alembic`: Database migrations
- `pytest`: Testing framework

### Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/agents_db

# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0

# MCP Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8001

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Performance
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
REQUEST_TIMEOUT_SECONDS=30

# Feature Flags
ENABLE_AGENT_TRACING=true
ENABLE_TOOL_CACHING=true
```

### Start Local Services with Docker Compose

```bash
cd backend
docker-compose up -d
```

This starts:
- PostgreSQL database with pgvector extension
- Redis (for tool definition caching)
- PGAdmin (for database management)

### Run Database Migrations

```bash
cd backend
alembic upgrade head
```

This creates all required tables (conversation, agent_execution, tool_definition, etc.) and indexes.

---

## 2. Starting the Agent System

### Start FastAPI Server

```bash
cd backend
uvicorn src.api.routes:app --reload --host 0.0.0.0 --port 8000
```

FastAPI server starts with:
- REST API: `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`

### Start MCP Server

```bash
cd backend
python -m src.mcp.server
```

MCP server starts on `http://localhost:8001` with tool registry.

### Verify Services are Running

```bash
# Check FastAPI health
curl http://localhost:8000/health

# Check MCP server
curl http://localhost:8001/tools
```

Expected responses:
```json
// FastAPI health
{"status": "healthy", "timestamp": "2026-01-16T10:30:00Z"}

// MCP tools (initially empty)
{"tools": [], "total_count": 0}
```

---

## 3. Registering Your First Tool

Tools are the interface between agents and your application logic. Let's register a simple "list_todos" tool.

### Create Tool Definition

```python
# backend/src/mcp/tools/todo_tools.py

from mcp.server import Server
from pydantic import BaseModel, Field

server = Server("todo-app")

class ListTodosParams(BaseModel):
    """Parameters for listing todos"""
    status: str = Field(
        default="all",
        description="Filter by status: todo, done, or all"
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of todos to return"
    )

class TodoItem(BaseModel):
    """A todo item"""
    id: str
    title: str
    status: str
    created_at: str

class ListTodosResponse(BaseModel):
    """Response from listing todos"""
    tasks: list[TodoItem]
    total_count: int

@server.tool(
    name="list_todos",
    description="Lists all todos for the current user. Can filter by status (todo/done) and limit results. Use this when user asks to see, show, or list their tasks.",
)
async def list_todos(params: ListTodosParams) -> ListTodosResponse:
    """
    Implementation of list_todos tool.

    In production, this would query your application's database.
    For this example, we return mock data.
    """
    # Mock implementation
    mock_todos = [
        TodoItem(
            id="1",
            title="Buy groceries",
            status="todo",
            created_at="2026-01-15T10:00:00Z"
        ),
        TodoItem(
            id="2",
            title="Write documentation",
            status="done",
            created_at="2026-01-15T11:00:00Z"
        )
    ]

    # Filter by status
    if params.status != "all":
        mock_todos = [t for t in mock_todos if t.status == params.status]

    # Apply limit
    mock_todos = mock_todos[:params.limit]

    return ListTodosResponse(
        tasks=mock_todos,
        total_count=len(mock_todos)
    )
```

### Register Tool with MCP Server

```python
# backend/src/mcp/server.py

from src.mcp.tools import todo_tools

# Server auto-registers tools defined with @server.tool decorator
# Just import the module to register
```

### Sync Tool to Database

```bash
# This script reads registered MCP tools and creates entries in tool_definition table
python -m src.mcp.sync_tools --domain todo
```

The sync script:
1. Discovers all `@server.tool` decorated functions
2. Generates embeddings for tool descriptions
3. Inserts/updates tool_definition table entries
4. Sets `is_active=true` for synced tools

---

## 4. Invoking Agents via API

### Example 1: Simple Request with Orchestrator

```bash
curl -X POST http://localhost:8000/api/v1/agents/orchestrator/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Show me my tasks that are not done yet",
    "user_id": "user-123",
    "application_domain": "todo"
  }'
```

**Response**:
```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "intent": {
    "type": "list",
    "confidence": 0.95
  },
  "entities": [
    {
      "type": "task",
      "value": "all",
      "attributes": {"status_filter": "todo"}
    }
  ],
  "selected_tool": {
    "tool_name": "list_todos",
    "confidence": 0.92,
    "parameters": {
      "status": "todo",
      "limit": 10
    }
  },
  "tool_result": {
    "tasks": [
      {
        "id": "1",
        "title": "Buy groceries",
        "status": "todo",
        "created_at": "2026-01-15T10:00:00Z"
      }
    ],
    "total_count": 1
  },
  "reasoning_trace": [
    {
      "step": 1,
      "action": "classify_intent",
      "input": "Show me my tasks that are not done yet",
      "output": "list",
      "confidence": 0.95,
      "timestamp": "2026-01-16T10:30:00Z"
    },
    {
      "step": 2,
      "action": "extract_entities",
      "input": "Show me my tasks that are not done yet",
      "output": [{"type": "task", "attributes": {"status_filter": "todo"}}],
      "confidence": 0.93,
      "timestamp": "2026-01-16T10:30:00.150Z"
    },
    {
      "step": 3,
      "action": "select_tool",
      "input": {"intent": "list", "entities": [...]},
      "output": "list_todos",
      "confidence": 0.92,
      "timestamp": "2026-01-16T10:30:00.300Z"
    }
  ],
  "status": "success"
}
```

### Example 2: Request Requiring Validation

```bash
curl -X POST http://localhost:8000/api/v1/agents/orchestrator/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Delete task #42",
    "user_id": "user-123",
    "application_domain": "todo"
  }'
```

If task #42 doesn't exist, Validation Agent will intercept:

```json
{
  "execution_id": "...",
  "intent": {"type": "delete", "confidence": 0.96},
  "entities": [{"type": "task", "value": "42"}],
  "selected_tool": {
    "tool_name": "delete_todo",
    "confidence": 0.94,
    "parameters": {"task_id": "42"}
  },
  "validation_status": "rejected",
  "validation_issues": [
    {
      "issue_type": "entity_not_found",
      "message": "Task #42 not found. Use 'show tasks' to see available tasks.",
      "recovery_actions": [
        "List your tasks with: show tasks",
        "Check the task ID is correct",
        "The task may have already been deleted"
      ]
    }
  ],
  "status": "failure"
}
```

### Example 3: Conversation with Context

**First message**:
```bash
curl -X POST http://localhost:8000/api/v1/agents/orchestrator/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Show task #5",
    "user_id": "user-123",
    "application_domain": "todo"
  }'
```

Response includes `conversation_id`: `"abc-123-def-456"`

**Follow-up message** (using conversation context):
```bash
curl -X POST http://localhost:8000/api/v1/agents/orchestrator/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Mark it done",
    "conversation_id": "abc-123-def-456",
    "user_id": "user-123",
    "application_domain": "todo"
  }'
```

Conversation Reasoning Agent resolves "it" → task #5:

```json
{
  "execution_id": "...",
  "intent": {"type": "update", "confidence": 0.94},
  "entities": [
    {
      "type": "task",
      "value": "5",
      "attributes": {"status": "done"},
      "resolved_from": "implicit_reference"
    }
  ],
  "conversation_context_used": {
    "messages_retrieved": 2,
    "entities_resolved": 1,
    "resolution_details": {
      "reference": "it",
      "resolved_to": "task #5",
      "confidence": 0.91
    }
  },
  "selected_tool": {
    "tool_name": "update_todo",
    "confidence": 0.93,
    "parameters": {"task_id": "5", "status": "done"}
  },
  "status": "success"
}
```

---

## 5. Adding a New Application Domain

To add support for a new application (e.g., CRM), follow these steps:

### Step 1: Define Your Tools

```python
# backend/src/mcp/tools/crm_tools.py

from mcp.server import Server
from pydantic import BaseModel, Field

server = Server("crm-app")

class CreateCustomerParams(BaseModel):
    name: str = Field(description="Customer name")
    email: str = Field(description="Customer email address")
    company: str = Field(default="", description="Company name (optional)")

class Customer(BaseModel):
    id: str
    name: str
    email: str
    company: str
    created_at: str

@server.tool(
    name="create_customer",
    description="Creates a new customer record in the CRM system. Use this when user wants to add, create, or register a new customer. Requires customer name and email address.",
)
async def create_customer(params: CreateCustomerParams) -> Customer:
    # Implementation: Save to your CRM database
    # For now, return mock data
    return Customer(
        id="cust-001",
        name=params.name,
        email=params.email,
        company=params.company,
        created_at="2026-01-16T10:30:00Z"
    )

@server.tool(
    name="list_customers",
    description="Lists all customers in the CRM system. Can filter by company name. Use this when user asks to see, show, or list customers.",
)
async def list_customers(company: str = "") -> list[Customer]:
    # Implementation
    return []
```

### Step 2: Sync Tools to Database

```bash
python -m src.mcp.sync_tools --domain crm
```

### Step 3: Test with Orchestrator

```bash
curl -X POST http://localhost:8000/api/v1/agents/orchestrator/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Add a new customer named John Doe with email john@example.com",
    "user_id": "user-123",
    "application_domain": "crm"
  }'
```

The Orchestrator will:
1. Classify intent → `create`
2. Extract entities → `{name: "John Doe", email: "john@example.com"}`
3. Search tool_definition table for CRM domain tools
4. Find `create_customer` via semantic similarity
5. Map entities to tool parameters
6. Invoke tool and return result

**No agent code changes required!** The agents automatically discover and use your new tools.

---

## 6. Testing Agent Behavior

### Unit Tests for Skills

```bash
cd backend
pytest tests/unit/test_skills/
```

Example test:

```python
# tests/unit/test_skills/test_intent_classifier.py

import pytest
from src.skills.intent_classifier import classify_intent

@pytest.mark.asyncio
async def test_classify_intent_list():
    result = await classify_intent({
        "text": "Show me my tasks"
    })

    assert result["intent_type"] == "list"
    assert result["confidence"] >= 0.8

@pytest.mark.asyncio
async def test_classify_intent_determinism():
    """Verify same input produces identical output (FR-026)"""
    input_data = {"text": "Delete the customer"}

    results = [await classify_intent(input_data) for _ in range(5)]

    # All results should be identical
    assert all(r["intent_type"] == results[0]["intent_type"] for r in results)
    assert all(r["confidence"] == results[0]["confidence"] for r in results)
```

### Integration Tests for Agents

```bash
pytest tests/integration/test_orchestration.py
```

Example test:

```python
# tests/integration/test_orchestration.py

import pytest
from httpx import AsyncClient
from src.api.routes import app

@pytest.mark.asyncio
async def test_orchestrator_end_to_end():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/agents/orchestrator/invoke",
            json={
                "request": "Show my todos that are not done",
                "user_id": "test-user",
                "application_domain": "todo"
            }
        )

    assert response.status_code == 200
    data = response.json()

    assert data["intent"]["type"] == "list"
    assert data["selected_tool"]["tool_name"] == "list_todos"
    assert "tool_result" in data
    assert data["status"] == "success"
```

### Contract Tests for MCP Tools

```bash
pytest tests/contract/test_mcp_tools.py
```

Validates that all registered tools conform to MCP schema specifications.

---

## 7. Debugging and Troubleshooting

### Enable Debug Logging

```bash
# In .env file
LOG_LEVEL=DEBUG
ENABLE_AGENT_TRACING=true
```

Restart servers to see detailed logs including:
- Intent classification confidence scores
- Entity extraction details
- Tool selection reasoning
- Database queries
- API call latencies

### View Agent Execution Traces

```bash
# Get execution details by ID
curl http://localhost:8000/api/v1/agents/executions/{execution_id}
```

Returns full execution trace with reasoning steps, confidence scores, and timing information.

### Query Database Directly

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d agents_db

# View recent agent executions
SELECT agent_type, status, duration_ms, execution_start
FROM agent_execution
ORDER BY execution_start DESC
LIMIT 10;

# View tool invocation success rates
SELECT td.tool_name,
       COUNT(*) as total_calls,
       SUM(CASE WHEN ti.status = 'success' THEN 1 ELSE 0 END) as successes,
       AVG(ti.duration_ms) as avg_duration
FROM tool_invocation ti
JOIN tool_definition td ON ti.tool_definition_id = td.id
WHERE ti.invocation_start > NOW() - INTERVAL '1 hour'
GROUP BY td.tool_name;
```

### Common Issues and Solutions

**Issue**: Agent always returns "clarification_needed"
- **Cause**: Low confidence in intent classification or tool selection
- **Solution**: Improve tool descriptions to be more specific and include examples. Check OpenAI API key is valid.

**Issue**: Tools not found by semantic search
- **Cause**: Tool embeddings not generated or pgvector extension not enabled
- **Solution**: Run `python -m src.mcp.sync_tools --regenerate-embeddings`

**Issue**: Conversation context not working
- **Cause**: Missing conversation_id in follow-up requests
- **Solution**: Ensure you pass the conversation_id from previous response

**Issue**: Slow response times (>1 second)
- **Cause**: Database connection pool exhausted or OpenAI API latency
- **Solution**: Increase `DATABASE_POOL_SIZE` in .env. Monitor with `SELECT * FROM pg_stat_activity`

---

## 8. Production Deployment

### Environment Configuration

For production, update `.env`:

```bash
# Production database (Neon)
DATABASE_URL=postgresql+asyncpg://user:password@neon-host/agents_db

# Disable debug features
API_RELOAD=false
LOG_LEVEL=INFO
ENABLE_AGENT_TRACING=false  # or use sampling

# Security
CORS_ORIGINS=https://your-app.com
API_KEY_REQUIRED=true
```

### Docker Build

```bash
cd backend
docker build -t reusable-agents:latest .
```

### Run Migrations Before Deployment

```bash
# In your CI/CD pipeline
alembic upgrade head
```

### Health Checks

Configure your orchestration platform (Kubernetes, ECS, etc.) to use:
- Health endpoint: `GET /health`
- Readiness check: `GET /ready` (checks database connection)

### Monitoring

Set up observability:
- **Logs**: Structured JSON logs to stdout (captured by log aggregator)
- **Metrics**: Prometheus metrics at `/metrics` endpoint
- **Tracing**: OpenTelemetry traces for distributed tracing
- **Alerts**: Alert on high error rates, slow p95 latency, low confidence scores

---

## 9. Best Practices

### Tool Description Guidelines

Good tool descriptions:
- Are 50+ characters
- Include examples of when to use the tool
- Mention key parameters
- Use natural language, not technical jargon

**Good**:
```
"Lists all todos for the current user. Can filter by status (todo/done) and limit results. Use this when user asks to see, show, or list their tasks. Useful for getting an overview of pending work."
```

**Bad**:
```
"Lists todos"  # Too short, no context
```

### Conversation Management

- Create new conversation for each distinct user session
- Archive conversations after 30 days of inactivity
- Use conversation_id consistently across all messages in a session

### Error Handling

- Always use Error & Recovery Agent to translate errors before showing to users
- Include trace_id in all error responses for debugging
- Log all errors with full context (user_id, request, stack trace)

### Performance Optimization

- Cache tool definitions in Redis (TTL: 1 hour)
- Use connection pooling for database
- Enable async I/O throughout (no blocking calls)
- Monitor p95 latency and optimize slow paths

---

## 10. Next Steps

- Read [data-model.md](./data-model.md) for database schema details
- Review [contracts/](./contracts/) for API specifications
- Explore [research.md](./research.md) for technology decisions and best practices
- See `/sp.tasks` command to generate implementation tasks

---

## Support

For issues or questions:
- Check troubleshooting section above
- Review agent execution traces for debugging
- Consult API documentation at `/docs` endpoint
- File issues in project repository
