---
title: Reusable AI Agents and Skills
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
python_version: "3.11"
app_file: app.py
pinned: false
---

# Reusable AI Agents and Skills

A framework for building application-agnostic AI agents that work across multiple domains (Todo, CRM, Notes, Inventory, etc.) without modification. Agents discover and invoke tools dynamically via the Model Context Protocol (MCP).

## 🎯 Key Features

- **Reusable Agents**: Work identically across todo, CRM, notes, and any other domain
- **Dynamic Tool Discovery**: Agents find tools via semantic search, not hardcoded mappings
- **MCP Protocol**: Standardized tool communication via Model Context Protocol
- **Explainable AI**: Full reasoning traces with confidence scores for all decisions
- **Stateless Architecture**: Agents survive restarts, scale horizontally
- **Production Ready**: Structured logging, metrics export, OpenTelemetry tracing

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Request                             │
│            "Show me my tasks that are done"                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │    Orchestrator Agent             │
        │  (Reusable, domain-agnostic)     │
        └───────────┬───────────────────────┘
                    │
        ┌───────────┴────────────┬──────────────┬─────────────┐
        │                        │              │             │
        ▼                        ▼              ▼             ▼
┌──────────────┐    ┌────────────────┐  ┌──────────┐  ┌──────────┐
│   Intent     │    │    Entity      │  │   Tool   │  │  Tool    │
│ Classifier   │    │   Extractor    │  │ Selector │  │ Invoker  │
│  (Skill)     │    │    (Skill)     │  │ (Skill)  │  │  (MCP)   │
└──────┬───────┘    └────────┬───────┘  └────┬─────┘  └────┬─────┘
       │                     │               │             │
       │  "list"             │  "task",      │  Search     │ Invoke
       │  confidence=0.95    │  status=done  │  tools      │  via MCP
       │                     │               │             │
       └─────────────────────┴───────────────┴─────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │      MCP Server               │
            │   (Tool Registry)             │
            └───────────┬───────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │  Application-Specific Tools           │
        │  • list_todos (Todo app)              │
        │  • list_customers (CRM app)           │
        │  • list_notes (Notes app)             │
        └───────────────────────────────────────┘
```

## 🚀 Quick Start

### TL;DR - Run Locally

```bash
# 1. Install dependencies (first time only)
pip install -e ".[dev]"

# 2. Setup environment (first time only)
cp .env.example .env
# Edit .env with your database and API credentials

# 3. Run database migrations (first time only)
alembic upgrade head

# 4. Start the server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Server will be available at:
# http://localhost:8000 (API)
# http://localhost:8000/docs (Swagger Documentation)
```

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or Neon account)
- OpenAI API key

### Installation

```bash
# Clone repository
cd backend

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# - DATABASE_URL: Your PostgreSQL connection string
# - OPENAI_API_KEY: Your OpenAI API key
```

### Database Setup

```bash
# Run migrations
alembic upgrade head
```

### Start Backend Server

```bash
# Method 1: Using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using Python module (recommended)
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Method 3: Using Python script
python -m src.main
```

The server will start on:
- **Local**: http://localhost:8000
- **Network**: http://0.0.0.0:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Register Example Tools

```bash
# Register todo app tools
python -m src.mcp.sync_tools --domain todo
```

### Test the Agent

```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/agents/orchestrator/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Show me my tasks",
    "user_id": "user-123",
    "application_domain": "todo"
  }'
```

Expected response:
```json
{
  "execution_id": "...",
  "intent": {"type": "list", "confidence": 0.95},
  "entities": [{"type": "task", "value": "all"}],
  "selected_tool": {
    "tool_name": "list_todos",
    "confidence": 0.92,
    "parameters": {"status": "all"}
  },
  "tool_result": {
    "tasks": [...]
  },
  "reasoning_trace": [
    {"step": 1, "action": "classify_intent", ...},
    {"step": 2, "action": "extract_entities", ...},
    {"step": 3, "action": "select_tool", ...}
  ],
  "status": "success"
}
```

## 📚 Core Components

### Agents

- **Orchestrator Agent** (`src/agents/orchestrator.py`): Main entry point, coordinates skills and tools
- **Validation Agent**: Entity existence checks, operation approval
- **Conversation Agent**: Implicit reference resolution, context management
- **Error Recovery Agent**: Error translation, retry logic

### Skills

- **Intent Classifier** (`src/skills/intent_classifier.py`): Categorizes requests (create/read/update/delete/list/search/analyze)
- **Entity Extractor** (`src/skills/entity_extractor.py`): Identifies entities and attributes from text
- **Tool Selector**: Semantic search for best matching tool
- **Confirmation Generator**: User-friendly confirmation messages
- **Error Humanizer**: Technical error → plain language translation

### MCP Integration

- **MCP Server** (`src/mcp/server.py`): Tool registry and invocation
- **Tool Sync** (`src/mcp/sync_tools.py`): Discovers tools, generates embeddings, registers in database
- **Tool Registry**: Dynamic tool discovery with semantic search

## 🔄 Reusability

This framework is designed for **zero-modification reusability** across projects. To add a new application domain:

```python
# 1. Define your tools with @server.tool decorator
from mcp.server import Server

server = Server("crm-app")

@server.tool(
    name="list_customers",
    description="Lists all customers in CRM. Use when user wants to see customers."
)
async def list_customers(company: str = "") -> List[Customer]:
    return get_customers_from_database(company)
```

```bash
# 2. Sync tools to registry
python -m src.mcp.sync_tools --domain crm
```

```python
# 3. Use existing agents (no code changes!)
response = await orchestrator.invoke(
    request="Show me customers at Acme Corp",
    user_id="user-123",
    application_domain="crm"  # ← Only difference
)
```

**That's it!** The Orchestrator Agent will:
1. Discover your new tools via semantic search
2. Match them to user intent
3. Invoke them via MCP
4. Return structured results

**See full reusability guide**: [docs/AGENT_MCP_INTEGRATION.md](docs/AGENT_MCP_INTEGRATION.md)

**Validate reusability**: [docs/REUSABILITY_VALIDATION.md](docs/REUSABILITY_VALIDATION.md)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run integration tests only
pytest tests/integration/

# Run reusability validation
pytest tests/integration/test_cross_domain_reusability.py
```

## 📊 Observability

### Structured Logging

All logs include:
- `trace_id`: Unique identifier for request correlation
- `user_id`: User attribution
- `agent_type`: Which agent processed the request
- `confidence`: Decision confidence scores
- `duration_ms`: Timing information

```python
# Example log entry (JSON format)
{
  "event": "intent_classified",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "intent_type": "list",
  "confidence": 0.95,
  "timestamp": "2026-01-16T10:30:00Z"
}
```

### Metrics

Prometheus metrics at `/metrics`:
- `agent_execution_total{agent_type, status}`: Execution counts
- `agent_execution_duration_seconds{agent_type}`: Latency percentiles
- `tool_invocation_total{tool_name, status}`: Tool usage
- `intent_classification_confidence`: Confidence distribution

### Tracing

OpenTelemetry spans for:
- Agent execution (orchestrator, validation, conversation, error recovery)
- Skill invocation (intent classification, entity extraction, tool selection)
- Tool execution via MCP
- Database queries

## 🛡️ Security

- **Input Validation**: All inputs validated via Pydantic models
- **No Direct Database Access from Agents**: Agents use tools, not direct queries
- **Audit Logging**: All agent executions logged with user attribution
- **Rate Limiting**: FastAPI middleware prevents abuse
- **Environment Variables**: Sensitive data (API keys, DB credentials) never committed

## 📖 Documentation

- **[Agent-MCP Integration Guide](docs/AGENT_MCP_INTEGRATION.md)**: How agents consume MCP tools
- **[Reusability Validation](docs/REUSABILITY_VALIDATION.md)**: Validate agents work across projects
- **[API Contracts](../specs/001-reusable-agents/contracts/)**: OpenAPI specs for all endpoints
- **[Architecture Decisions](../specs/001-reusable-agents/research.md)**: Technology choices and rationale
- **[Quick Start Guide](../specs/001-reusable-agents/quickstart.md)**: Developer guide with examples

## 🏛️ Project Structure

```
backend/
├── src/
│   ├── agents/          # Agent implementations
│   │   ├── orchestrator.py      # Main orchestrator
│   │   ├── validation.py        # Entity validation
│   │   ├── conversation.py      # Context management
│   │   └── error_recovery.py   # Error handling
│   ├── skills/          # Reusable skill functions
│   │   ├── intent_classifier.py
│   │   ├── entity_extractor.py
│   │   ├── tool_selector.py
│   │   ├── confirmation_gen.py
│   │   └── error_humanizer.py
│   ├── mcp/             # MCP server and tools
│   │   ├── server.py
│   │   ├── tool_registry.py
│   │   └── sync_tools.py
│   ├── models/          # SQLModel entities
│   │   ├── conversation.py
│   │   ├── agent_execution.py
│   │   └── tool_metadata.py
│   ├── api/             # FastAPI endpoints
│   │   ├── routes.py
│   │   └── middleware.py
│   └── core/            # Configuration & utilities
│       ├── config.py
│       ├── database.py
│       └── logging.py
├── tests/              # Test suites
│   ├── contract/       # API contract tests
│   ├── integration/    # Multi-component tests
│   └── unit/           # Component tests
├── migrations/         # Database migrations (Alembic)
├── docs/              # Documentation
└── pyproject.toml     # Dependencies and config
```

## 📜 License

MIT

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## 🆘 Support

- **Issues**: File at [repository issues](../../issues)
- **Discussions**: Join [community discussions](../../discussions)
- **Documentation**: [Full documentation](../specs/001-reusable-agents/)

---

## 🚀 Deploy to Hugging Face Spaces

This backend can be deployed to Hugging Face Spaces using Docker.

### Deployment Steps

1. **Prepare Your Repository**
   - Create a new repository on Hugging Face Hub
   - Add the files from the backend directory to your repository

2. **Configure Your Space**
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Select **Container** as the Space SDK
   - Choose your hardware specifications
   - Link your repository

3. **Environment Variables**
   Add these secrets in your Space settings:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DATABASE_URL`: PostgreSQL database URL (consider using an external service)
   - `JWT_SECRET_KEY`: Secret key for JWT tokens
   - Any other environment variables required by your application

4. **Application Port**
   - The application is configured to run on port 7860, which is the standard for Hugging Face Spaces
   - The Dockerfile automatically sets the PORT environment variable

### API Endpoints

Once deployed, your API will be available at:
- Health check: `https://YOUR_SPACE_NAME.hf.space/health`
- Chat endpoint: `https://YOUR_SPACE_NAME.hf.space/api/{user_id}/chat`
- Authentication: `https://YOUR_SPACE_NAME.hf.space/api/auth/login`

### Notes

- Make sure your database connection is configured for external access if you're using persistent storage
- Hugging Face Spaces have resource limitations; consider this when choosing your hardware
- For production deployments, consider using a managed database service

**Built with ❤️ following Spec-Driven Development principles**
