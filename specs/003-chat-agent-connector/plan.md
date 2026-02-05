# Implementation Plan: Chat Agent Connector

**Branch**: `003-chat-agent-connector` | **Date**: 2026-01-16 | **Spec**: [link]
**Input**: Feature specification from `/specs/003-chat-agent-connector/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a stateless chat backend that connects reusable agents to MCP tools using an external LLM provider. The system will follow a conversation flow: load conversation, store user message, run agent, execute MCP tools, store assistant response, and return result. Built with FastAPI, using SQLModel for persistence, and integrating with the Official MCP SDK.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, SQLModel, Official MCP SDK, httpx, pydantic, asyncpg
**Storage**: Neon PostgreSQL (managed PostgreSQL)
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: Backend service
**Performance Goals**: Respond to 95% of requests within 5 seconds, handle 100 concurrent users
**Constraints**: Stateless architecture (no server-side session storage), all state in database, <500ms p95 response time for LLM calls
**Scale/Scope**: Support 10,000+ conversations, 100 concurrent users, 1M+ messages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Spec-Driven Development**: ✅ Complete feature spec exists at `/specs/003-chat-agent-connector/spec.md`
- **II. AI-Generated Code Only**: ✅ Plan specifies AI-generated implementation approach
- **III. Reusable Intelligence**: ✅ System designed to work with reusable agents and MCP tools
- **IV. Stateless Backend Architecture**: ✅ System will be stateless, all state in Neon PostgreSQL
- **V. Database as Single Source of Truth**: ✅ All conversation data persists in Neon PostgreSQL
- **VI. MCP-Only Agent Interactions**: ✅ System will execute MCP tools as specified
- **VII. Official MCP SDK Mandate**: ✅ Plan specifies using Official MCP SDK for tool execution
- **VIII. OpenAI Agents SDK Requirement**: N/A - System connects to reusable agents but doesn't implement with OpenAI Agents SDK
- **IX. FastAPI Backend Framework**: ✅ System will use FastAPI framework
- **X. SQLModel ORM Requirement**: ✅ All database interactions will use SQLModel
- **XI. ChatKit Frontend Framework**: N/A - Backend service only
- **XII. Better Auth Authentication**: N/A - Authentication handled at API level per spec
- **XIII. Tool Chaining Support**: ✅ System will support tool chaining through MCP integration
- **XIV. Graceful Error Handling**: ✅ Plan includes error handling for LLM and tool execution failures
- **XV. Restart Resilience**: ✅ Stateless design ensures restart resilience
- **XVI. No Hardcoded Business Logic**: ✅ Agent logic will be driven by LLM responses and tool calls

## Project Structure

### Documentation (this feature)

```text
specs/003-chat-agent-connector/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat_message.py          # ChatMessage SQLModel definition
│   │   ├── chat_response.py         # ChatResponse SQLModel definition
│   │   └── tool_call.py             # ToolCall SQLModel definition
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_client.py            # Provider-agnostic LLM client
│   │   ├── mcp_client.py            # MCP client integration
│   │   ├── conversation_service.py  # Conversation management logic
│   │   └── agent_runner.py          # AgentRunner abstraction
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat_endpoint.py         # Main chat API endpoint
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration settings
│   │   ├── database.py              # Database session management
│   │   └── logging.py               # Logging configuration
│   └── main.py                      # Application entry point
└── tests/
    ├── unit/
    │   ├── test_llm_client.py
    │   ├── test_conversation_service.py
    │   └── test_agent_runner.py
    ├── integration/
    │   ├── test_chat_endpoint.py
    │   └── test_mcp_integration.py
    └── contract/
        └── test_api_contracts.py
```

**Structure Decision**: Selected Option 2: Web application structure with backend/ directory since this is a backend service. The structure follows the project's FastAPI and SQLModel requirements while organizing code into logical modules for models, services (LLM client, MCP client, conversation service, agent runner), API, and core utilities.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
|           |            |                                     |