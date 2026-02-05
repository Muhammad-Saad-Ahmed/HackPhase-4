---
id: 2
title: MCP Task Tools Implementation Plan
stage: plan
date: 2026-01-23
surface: agent
model: claude-sonnet-4-5
feature: 001-mcp-task-tools
branch: 001-mcp-task-tools
user: user
command: /sp.plan
labels: ["plan", "mcp", "task-tools", "architecture", "phase3"]
links:
  spec: specs/001-mcp-task-tools/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-mcp-task-tools/plan.md
  - specs/001-mcp-task-tools/research.md
  - specs/001-mcp-task-tools/data-model.md
  - specs/001-mcp-task-tools/quickstart.md
  - specs/001-mcp-task-tools/contracts/add_task.json
  - specs/001-mcp-task-tools/contracts/list_tasks.json
  - specs/001-mcp-task-tools/contracts/update_task.json
  - specs/001-mcp-task-tools/contracts/complete_task.json
  - specs/001-mcp-task-tools/contracts/delete_task.json
  - specs/001-mcp-task-tools/contracts/README.md
tests:
  - none (planning phase)
---

## Prompt

/sp.plan Phase III-A Plan

Create:
- MCP tool contracts (input/output schemas)
- MCP server initialization
- DB access layer using SQLModel

Decisions:
- Error signaling format for MCP tools
- Tool naming and parameter consistency

Validation:
- Direct tool invocation tests
- Database state verification after each tool call

## Response snapshot

Successfully completed comprehensive implementation plan for MCP Task Management Tools.

**Planning Phase Completed**:
- Phase 0: Research & Design Decisions (10 major decisions documented)
- Phase 1: Design & Contracts (data model, contracts, quickstart guide)
- Constitutional compliance verified (15/16 principles PASS, 1 deferred)

**Key Architectural Decisions**:
1. JSON Schema-based MCP tools with Pydantic validation
2. Structured error responses (success/error/code/details format)
3. snake_case tool naming with consistent parameters
4. Async initialization with database session dependency injection
5. Direct SQLModel queries (no repository abstraction layer)

**Artifacts Generated** (9 files):
- `plan.md` - Complete implementation plan (450 lines)
- `research.md` - 10 design decisions with rationale
- `data-model.md` - Task entity documentation with validation rules
- `quickstart.md` - Developer implementation guide with code examples
- `contracts/*.json` - 5 tool JSON Schemas (add, list, update, complete, delete)
- `contracts/README.md` - Contract documentation and usage guide

**Tool Contracts Defined**:
- `add_task` - Create tasks with title and optional description
- `list_tasks` - Query with optional status filter
- `update_task` - Modify title/description by ID
- `complete_task` - Mark as completed with timestamp
- `delete_task` - Permanent removal by ID

**Error Handling Strategy**:
- 4 error codes: VALIDATION_ERROR, NOT_FOUND, DATABASE_ERROR, INTERNAL_ERROR
- Structured responses with human-readable messages and machine-readable codes
- Optional details field for context-specific error information

**Implementation Blueprint**:
- Files to create: 4 (schemas.py, task_tools.py, server.py, test files)
- Files to modify: 2 (main.py, conftest.py)
- Lines of code: ~600 LOC implementation + ~500 LOC tests
- Dependencies to add: Official MCP SDK via UV

**Constitution Check Results**:
- 15 principles PASS
- 1 principle DEFERRED (OpenAI Agents SDK - agent integration out of scope)
- 0 violations
- Stateless architecture confirmed
- Database as single source of truth confirmed
- No hardcoded business logic confirmed

## Outcome

- ✅ Impact: Complete architectural plan with all design decisions documented. Ready for task generation (/sp.tasks) and implementation. Zero blockers identified.
- 🧪 Tests: No tests created (planning phase). Test strategy defined: unit tests (tool isolation), integration tests (E2E workflows), contract tests (schema validation), performance tests (success criteria verification).
- 📁 Files: 9 files created - plan.md (450 lines), research.md (350 lines), data-model.md (400 lines), quickstart.md (650 lines), 5 JSON Schema contracts, contracts README
- 🔁 Next prompts: `/sp.tasks` (generate detailed implementation tasks with test-first approach)
- 🧠 Reflection: Successfully balanced architectural rigor with pragmatism. Chose direct SQLModel queries over repository pattern (simpler for stateless CRUD). Designed idempotent complete_task operation while keeping other operations fail-fast for clarity. All design decisions aligned with constitution principles.

## Evaluation notes (flywheel)

- Failure modes observed: None. Agent context update script found placeholder values in plan.md but completed successfully after plan was filled with concrete technical details.
- Graders run and results (PASS/FAIL):
  - Constitution Check: PASS (15/16 principles, 1 deferred appropriately)
  - Phase 0 Research: PASS (10 decisions with rationale and alternatives)
  - Phase 1 Contracts: PASS (5 tools, complete I/O schemas, unified response format)
  - Documentation Quality: PASS (plan, research, data-model, quickstart all complete)
- Prompt variant (if applicable): Standard /sp.plan workflow with user-specified focus areas (contracts, error format, validation)
- Next experiment (smallest change to try): Consider adding example curl commands to quickstart.md for manual testing. Consider adding performance benchmarking section to plan.md with specific measurement strategies.
