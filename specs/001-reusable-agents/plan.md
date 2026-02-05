# Implementation Plan: Reusable AI Agents and Skills

**Branch**: `001-reusable-agents` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-reusable-agents/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Design and implement reusable, application-agnostic AI agents (Orchestrator, Validation, Conversation Reasoning, Error & Recovery) and skills (intent classification, entity extraction, tool selection, confirmation generation, error humanization) that can be deployed across multiple application domains (Todo, CRM, Notes) without modification. Agents communicate exclusively through MCP tools and operate without hardcoded business logic, enabling extensibility through tool definition alone.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: OpenAI Agents SDK, Official MCP SDK, FastAPI, SQLModel, Pydantic
**Storage**: Neon PostgreSQL (for conversation context, agent execution logs, tool metadata)
**Testing**: pytest (unit, integration, contract tests)
**Target Platform**: Linux server (Docker containers, cloud-deployable)
**Project Type**: Single backend project (agents + skills library with MCP server)
**Performance Goals**: <200ms p95 latency for intent classification and tool selection; <500ms p95 for full request-to-response cycle
**Constraints**: Stateless agent architecture; all context passed explicitly or retrieved from database; no in-memory caching of state; MCP-only tool communication
**Scale/Scope**: Support 3+ application domains initially (Todo, CRM, Notes); handle 100+ concurrent agent requests; 50+ tools per domain

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Status

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Spec-Driven Development** | ✅ PASS | Feature has complete spec.md, this plan.md will be followed by tasks.md |
| **II. AI-Generated Code Only** | ✅ PASS | All implementation will be AI-generated following SDD workflow |
| **III. Reusable Intelligence** | ✅ PASS | Core feature objective - agents/skills designed for cross-domain reuse |
| **IV. Stateless Backend** | ✅ PASS | Agents are stateless; context retrieved from DB per FR-028 |
| **V. Database as Source of Truth** | ✅ PASS | Conversation context and agent logs persisted in Neon PostgreSQL |
| **VI. MCP-Only Agent Interactions** | ✅ PASS | FR-027 mandates tool-only communication; no direct function calls |
| **VII. Official MCP SDK** | ✅ PASS | Specified in Technical Context dependencies |
| **VIII. OpenAI Agents SDK** | ✅ PASS | Specified in Technical Context dependencies |
| **IX. FastAPI Backend** | ✅ PASS | Specified for MCP server implementation |
| **X. SQLModel ORM** | ✅ PASS | Specified for database operations |
| **XI. ChatKit Frontend** | ⚠️ DEFERRED | Not applicable to this feature - agents/backend only. Frontend integration is separate feature |
| **XII. Better Auth** | ⚠️ DEFERRED | Authentication not in scope for agent framework. Will be added in application layer |
| **XIII. Tool Chaining** | ✅ PASS | FR-004 requires multi-step reasoning and tool chaining support |
| **XIV. Graceful Error Handling** | ✅ PASS | User Story 4 and FR-016 to FR-019 mandate error translation and recovery |
| **XV. Restart Resilience** | ✅ PASS | Stateless architecture ensures restart safety; no runtime-only state |
| **XVI. No Hardcoded Business Logic** | ✅ PASS | FR-030 mandates new domains add tools only, not agent code modifications |

### Gate Decision

**PASS** - All applicable principles satisfied. Principles XI (ChatKit) and XII (Better Auth) are deferred as they apply to application layer, not agent framework. This feature establishes the agent foundation that applications will build upon.

## Project Structure

### Documentation (this feature)

```text
specs/001-reusable-agents/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - technology decisions and best practices
├── data-model.md        # Phase 1 output - agent/skill/tool entity definitions
├── quickstart.md        # Phase 1 output - developer guide for using agents
├── contracts/           # Phase 1 output - MCP tool schemas and agent interfaces
│   ├── mcp-tools.yaml   # MCP tool interface definitions
│   ├── agent-api.yaml   # Agent invocation APIs
│   └── skill-api.yaml   # Skill function signatures
├── checklists/          # Quality validation artifacts
│   └── requirements.md  # Spec quality checklist (already created)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

This is a single backend project following Option 1 structure:

```text
backend/
├── src/
│   ├── agents/                   # Agent implementations
│   │   ├── __init__.py
│   │   ├── orchestrator.py       # Orchestrator Agent (FR-001 to FR-006)
│   │   ├── validation.py         # Validation Agent (FR-007 to FR-011)
│   │   ├── conversation.py       # Conversation Reasoning Agent (FR-012 to FR-015)
│   │   └── error_recovery.py     # Error & Recovery Agent (FR-016 to FR-019)
│   ├── skills/                   # Reusable skill functions
│   │   ├── __init__.py
│   │   ├── intent_classifier.py  # Intent Classification (FR-020)
│   │   ├── entity_extractor.py   # Entity Extraction (FR-021)
│   │   ├── tool_selector.py      # Tool Selection (FR-022)
│   │   ├── confirmation_gen.py   # Confirmation Generation (FR-023)
│   │   └── error_humanizer.py    # Error Humanization (FR-024)
│   ├── mcp/                      # MCP server implementation
│   │   ├── __init__.py
│   │   ├── server.py             # MCP server using Official MCP SDK
│   │   ├── tool_registry.py      # Dynamic tool discovery and registration
│   │   └── schemas.py            # Tool schema definitions
│   ├── models/                   # SQLModel entities
│   │   ├── __init__.py
│   │   ├── conversation.py       # Conversation Context entity
│   │   ├── agent_execution.py    # Agent execution logs
│   │   └── tool_metadata.py      # Tool definitions and metadata
│   ├── api/                      # FastAPI endpoints
│   │   ├── __init__.py
│   │   ├── routes.py             # Agent invocation endpoints
│   │   └── middleware.py         # Request/response handling
│   └── core/                     # Shared utilities
│       ├── __init__.py
│       ├── config.py             # Configuration management
│       ├── database.py           # Database connection (SQLModel + PostgreSQL)
│       └── logging.py            # Structured logging setup
├── tests/
│   ├── contract/                 # Tool contract tests
│   │   ├── test_mcp_tools.py
│   │   └── test_agent_interfaces.py
│   ├── integration/              # Multi-agent workflow tests
│   │   ├── test_orchestration.py
│   │   ├── test_validation_flow.py
│   │   └── test_error_handling.py
│   └── unit/                     # Individual component tests
│       ├── test_agents/
│       ├── test_skills/
│       └── test_mcp/
├── migrations/                   # Database migrations (Alembic)
│   └── versions/
├── pyproject.toml                # Python dependencies and project metadata
├── Dockerfile                    # Container definition
└── docker-compose.yml            # Local development environment

```

**Structure Decision**: Selected Option 1 (Single project) because this feature is purely backend/agent framework with no frontend components. The backend directory contains the complete agent system with clear separation between agents (orchestration logic), skills (reusable functions), MCP (tool communication), models (data persistence), and API (invocation layer).

## Complexity Tracking

> No constitution violations - all principles satisfied or appropriately deferred for application-layer features.
