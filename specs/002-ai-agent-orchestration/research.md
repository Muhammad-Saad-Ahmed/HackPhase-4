# Research: AI Agent & Chat Orchestration

**Feature**: 002-ai-agent-orchestration
**Created**: 2026-01-23
**Purpose**: Document architectural decisions and design research for implementing natural language agent using OpenAI Agents SDK

## Overview

This document captures research findings and architectural decisions for building an AI agent that translates natural language into MCP tool invocations. The agent must:
- Parse user messages to identify task-related intents
- Select and invoke appropriate MCP tools
- Maintain conversation context across multiple turns
- Handle errors gracefully with user-friendly messages
- Ask clarifying questions when ambiguous

## Decision 1: System Prompt Architecture

### Decision
Use **structured three-tier system prompt** with explicit role definition, tool boundaries, and conditional reasoning instructions.

### Rationale
- OpenAI 2026 best practices emphasize high-quality instructions with clear role and objective definitions
- Structured prompts with policy variables enable template-based flexibility
- Reduces ambiguity in intent recognition and tool selection

### Alternatives Considered
1. **Single monolithic prompt**: Simpler but less maintainable, harder to debug confidence issues
2. **LLM-based intent classification only**: More flexible but slower and more expensive
3. **Hardcoded intent patterns**: Faster but inflexible and doesn't scale

### Implementation Pattern
```
# Role & Objective
You are a task-oriented AI assistant that helps users manage their todos.

# Available Tools
[Dynamic tool descriptions from MCP registry]

# Instructions
1. Parse user requests to identify:
   - Primary intent (create, read, update, delete, list)
   - Key entities (title, description, task ID)
   - Constraints or filters (status, date ranges)

2. Tool Selection Guidelines:
   - "show me" or "list" → list_tasks
   - "add" or "create" → add_task
   - "mark as done" or "complete" → complete_task
   - "remove" or "delete" → delete_task
   - "change" or "update" → update_task

3. Confidence Thresholds:
   - Intent confidence < 0.80 → ask clarifying question
   - Tool selection confidence < 0.75 → confirm before executing
   - Ambiguous entities → list options for user to choose

4. Error Handling:
   - Translate tool errors into plain language
   - Suggest alternative actions when possible
   - Never expose technical stack traces
```

### Key Considerations
- System prompt should be dynamic (load tool descriptions from MCP registry)
- Add tool boundaries for destructive operations (delete confirmation)
- Maintain conversational tone in all responses

---

## Decision 2: Tool Registry & Selection Strategy

### Decision
Use **OpenAI Agents SDK native MCP integration** (`MCPServerStreamableHttp`) with semantic tool descriptions for better matching.

### Rationale
- OpenAI officially adopted MCP in March 2025 across all products
- Native SDK support includes automatic retries (`max_retry_attempts`, `retry_backoff_seconds_base`)
- Semantic tool descriptions enable better intent-to-tool mapping
- Industry standard approach (Gartner predicts 40% of enterprise apps will use agents by end of 2026)

### Alternatives Considered
1. **OpenAI function calling only**: Simpler but requires hardcoding tool mappings, breaks reusability
2. **LangGraph/LangChain tool routing**: More complex framework, higher learning curve, vendor lock-in
3. **Custom tool registry without MCP**: Works but doesn't benefit from standardization

### Implementation Pattern
```python
from openai_agents import MCPServerStreamableHttp

# Initialize MCP client with retries
mcp_client = MCPServerStreamableHttp(
    server_url=settings.mcp_server_url,
    max_retry_attempts=3,
    retry_backoff_seconds_base=2
)

# List available tools dynamically
available_tools = await mcp_client.list_tools()

# Tool descriptions should be comprehensive
@server.tool(
    name="list_tasks",
    description="""Lists tasks for the current user.

WHEN TO USE:
- User wants to see their tasks
- User asks "what tasks do I have" or "show me my tasks"
- User wants to filter tasks by status

PARAMETERS:
- status: Filter by completion status (pending, completed, all)
- limit: Maximum tasks to return (default: 50)

RETURNS:
- List of task objects with id, title, status, created_at
"""
)
async def list_tasks(status: str = "all", limit: int = 50):
    # Implementation
```

### Key Considerations
- Tool descriptions are critical for accurate intent-to-tool mapping
- Use "WHEN TO USE" sections to guide LLM selection
- Keep tool signatures simple (avoid complex nested objects)
- Add retry logic for transient failures

---

## Decision 3: Context Management Strategy

### Decision
Implement **stateless agent with external PostgreSQL storage**, using existing `ConversationService` for state management.

### Rationale
- OpenAI Agents SDK uses stateless architecture by design ("does not retain information between calls")
- Existing `ConversationService` already implements recommended pattern: load → process → store
- Scales horizontally and survives server restarts (critical per Constitution Principle XV)
- Aligns with Constitution Principle IV (Stateless Backend Architecture)

### Alternatives Considered
1. **In-memory state with Redis**: Faster but requires sticky sessions, data loss risk, violates Constitution
2. **OpenAI Assistants API**: Being deprecated mid-2026, not recommended
3. **Stateful agents with persistent connections**: Doesn't scale horizontally

### Implementation Pattern
```python
class AgentRunner:
    async def run_conversation(self, user_id: str, message: str, conversation_id: Optional[str]):
        # 1. Load conversation history from database
        history = self.conversation_service.get_conversation_history(conversation_id)

        # 2. Build context variables for this turn
        context_variables = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "last_tool_used": self._extract_last_tool(history),
            "task_references": self._extract_task_references(history)  # For "task 2" resolution
        }

        # 3. Generate LLM response with context
        response = await self.llm_client.generate_response(
            messages=history + [{"role": "user", "content": message}],
            context_variables=context_variables
        )

        # 4. Execute tool calls if identified
        if response.get("tool_calls"):
            tool_results = await self.mcp_executor.execute_multiple_tools(response["tool_calls"])
            response["tool_calls"] = self._merge_results(response["tool_calls"], tool_results)

        # 5. Store conversation turn in database
        self.conversation_service.store_assistant_response(
            conversation_id=conversation_id,
            user_id=user_id,
            response=response["response"],
            tool_calls=response.get("tool_calls", [])
        )

        return response
```

### Key Considerations
- Conversation state is **only** in PostgreSQL (no in-memory state)
- Each request loads context, processes, stores result (stateless)
- Task references from previous "list" operations must be stored in conversation metadata
- Context window management: truncate old messages if conversation exceeds token limits
- Add TTL for old conversations (auto-cleanup after 30 days)

---

## Decision 4: Error Handling & Graceful Degradation

### Decision
Implement **circuit breaker pattern with automatic retries** and user-facing error translation following OpenAI 2026 guidance.

### Rationale
- OpenAI best practice: "When tool execution fails, provide error to model and it will figure out what to do"
- Circuit breakers prevent infinite loops and runaway costs
- User-friendly error messages improve trust and recovery success
- Aligns with Constitution Principle XIV (Graceful Error Handling)

### Alternatives Considered
1. **Simple try-catch with generic errors**: Easier but poor user experience
2. **No retries, fail fast**: Simpler but frustrates users with transient errors
3. **Unlimited retries**: Can cause infinite loops and cost overruns

### Implementation Pattern
```python
# Circuit Breaker
class CircuitBreaker:
    def __init__(self, max_failures=3, timeout_seconds=60):
        self.max_failures = max_failures
        self.timeout = timedelta(seconds=timeout_seconds)
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

# Error Humanizer
class ErrorHumanizer:
    ERROR_TEMPLATES = {
        "validation_error": "I need more information: {details}",
        "not_found": "I couldn't find what you're looking for. Could you be more specific?",
        "rate_limit": "Too many requests right now. Please wait a moment and try again.",
        "database_error": "I'm having trouble saving that right now. Let's try again in a moment."
    }

    @staticmethod
    def humanize(error: Exception) -> str:
        # Map technical errors to friendly messages
        error_type = type(error).__name__.lower()
        for key, template in ErrorHumanizer.ERROR_TEMPLATES.items():
            if key in error_type or key in str(error).lower():
                return template.format(details=str(error))
        return "Something went wrong. I'll try a different approach."

# Retry with exponential backoff
async def invoke_tool_with_retry(tool_name, parameters, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await mcp_client.call_tool(tool_name, parameters)
        except Exception as e:
            if attempt == max_retries - 1 or not is_retryable(e):
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Key Considerations
- Distinguish transient errors (retry) from permanent errors (fail fast)
- Translate all MCP tool errors to user-friendly messages
- Never expose: stack traces, error codes, database details
- Log technical details for debugging but show friendly messages to users
- Circuit breaker prevents cascading failures

---

## Decision 5: Confidence Scoring & Clarification Strategy

### Decision
Use **risk-adjusted confidence thresholds** with proactive clarification: Intent threshold 0.80, Tool selection threshold 0.75, elevated thresholds for destructive operations.

### Rationale
- OpenAI ChatGPT agent "proactively seeks additional details" when unclear
- Confidence-based clarification improves user trust and reduces incorrect actions
- Destructive operations (delete) need higher confidence to prevent accidents
- User studies show confidence thresholds improve task success rates

### Alternatives Considered
1. **No confidence scoring, always execute**: Fast but risky for destructive operations
2. **Always ask for confirmation**: Safe but frustrates users with obvious requests
3. **Fixed confidence threshold**: Doesn't account for action risk level

### Implementation Pattern
```python
class ConfidenceThresholds:
    """Risk-adjusted confidence thresholds."""
    DELETE = 0.90      # High-risk
    UPDATE = 0.85      # Medium-risk
    CREATE = 0.80      # Low-risk
    LIST = 0.70        # Very low-risk
    READ = 0.70        # Very low-risk

# Confidence checking
if intent_confidence < ConfidenceThresholds.get(intent_type):
    return {
        "status": "clarification_needed",
        "question": "I'm not entirely sure what you want to do. Did you mean to:\n" + suggestions,
        "options": alternative_intents
    }

# Confirmation for destructive operations
if is_destructive(tool_name) and not confirmed:
    return {
        "status": "confirmation_required",
        "question": f"⚠️ This will {tool_name} the task. Are you sure?",
        "expected_response": "yes/no",
        "pending_action": {"tool": tool_name, "parameters": parameters}
    }
```

### Clarification Templates
| Scenario | Template |
|----------|----------|
| Low intent confidence | "I'm not entirely sure what you want to do. Did you mean to: {suggestions}" |
| Low tool confidence | "I found a tool '{tool_name}' but I'm not very confident. Is this what you meant?" |
| Ambiguous entity | "I found multiple {entity_type}s. Which one did you mean? {options}" |
| Missing parameter | "To {action}, I need to know: {missing_params}" |
| Destructive operation | "⚠️ This will {action} {entity}. Are you sure? (yes/no)" |

### Key Considerations
- Use different thresholds based on action risk (delete needs 0.90, list only needs 0.70)
- Generate suggestions when confidence is low (show top 3 alternatives)
- Always confirm destructive operations even if confidence is high
- Track clarification success rates to tune thresholds over time

---

## Decision 6: Task Reference Resolution

### Decision
Store **task list context in conversation metadata** to enable positional references like "task 2" or "the first one".

### Rationale
- User Story 6 (P1): Multi-step flows are essential for natural conversation
- Users expect to say "complete task 2" after listing tasks
- Positional references only make sense within conversation context
- Aligns with natural language patterns in chat interfaces

### Alternatives Considered
1. **No positional references, require task IDs**: Breaks natural conversation flow
2. **Global task numbering**: Confusing when multiple conversations exist
3. **LLM-based resolution**: Too slow and unreliable for simple positional references

### Implementation Pattern
```python
# After list_tasks invocation
class ConversationService:
    def store_assistant_response(self, conversation_id, response, tool_calls):
        # ... existing storage ...

        # If tool was list_tasks, store task references
        if any(call["tool"] == "list_tasks" for call in tool_calls):
            task_list = self._extract_task_list(tool_calls)
            self.store_task_references(conversation_id, task_list)

    def store_task_references(self, conversation_id, task_list):
        """Store positional task references for conversation."""
        metadata = {
            "task_references": {
                str(index + 1): task["id"]
                for index, task in enumerate(task_list)
            },
            "referenced_at": datetime.utcnow().isoformat()
        }
        # Store in conversation_metadata JSON column
        self._update_conversation_metadata(conversation_id, metadata)

    def resolve_task_reference(self, conversation_id, reference: str) -> Optional[int]:
        """Resolve 'task 2' or 'the first one' to actual task ID."""
        metadata = self._get_conversation_metadata(conversation_id)
        task_refs = metadata.get("task_references", {})

        # Handle numeric references: "task 2", "2", "#2"
        numeric = re.search(r'\d+', reference)
        if numeric:
            position = numeric.group()
            return task_refs.get(position)

        # Handle ordinal references: "the first one", "first task"
        ordinals = {"first": "1", "second": "2", "third": "3"}
        for word, num in ordinals.items():
            if word in reference.lower():
                return task_refs.get(num)

        return None

# Agent prompt includes task reference resolution
system_prompt = """
When user references tasks by position (e.g., "task 2", "the first one"):
1. Check conversation context for recent list_tasks results
2. Map position to actual task ID
3. Use that ID for the operation

If no recent task list exists, ask user to list tasks first.
"""
```

### Key Considerations
- Task references expire after conversation ends (session-scoped only)
- Store references in conversation metadata (JSON column)
- Support multiple reference formats: "task 2", "2", "#2", "the first one"
- Clear references when new list_tasks is invoked (refresh context)
- If reference is stale (>10 messages ago), ask user to re-list tasks

---

## Decision 7: Agent Response Formatting

### Decision
Use **template-based response generation** with personality variables to maintain conversational tone.

### Rationale
- User Story requirements emphasize "friendly confirmations" and "encouraging messages"
- Success Criterion SC-009: "Agent maintains conversational tone (not robotic)"
- Templates ensure consistency while allowing customization
- LLM generates response content, templates add personality

### Alternatives Considered
1. **Pure LLM generation**: Inconsistent tone, hard to control, expensive
2. **Hardcoded responses**: Not conversational, can't adapt to context
3. **No formatting**: Technical responses frustrate users

### Implementation Pattern
```python
class ResponseFormatter:
    """Formats agent responses with consistent tone."""

    TEMPLATES = {
        "task_created": "I've added '{title}' to your tasks. {encouragement}",
        "task_completed": "{celebration} I've marked '{title}' as completed ✓",
        "task_deleted": "I've deleted task {position}: '{title}'",
        "task_listed_empty": "You don't have any tasks yet. Would you like to create one?",
        "task_listed": "Here are your {filter_name} tasks:\n{task_list}",
        "error_not_found": "I couldn't find task {reference}. {suggestion}",
        "error_validation": "That {field} is too long. Please keep it under {limit} characters.",
    }

    PERSONALITY = {
        "encouragement": ["You got this!", "Let's make it happen!", "On it!"],
        "celebration": ["Great!", "Awesome!", "Nice!", "Way to go!"],
        "suggestion": ["Would you like to see your current tasks?", "Try 'show my tasks' to see what's available."]
    }

    @staticmethod
    def format(template_key: str, **kwargs) -> str:
        template = ResponseFormatter.TEMPLATES.get(template_key, "Done!")

        # Add personality variations
        for key, options in ResponseFormatter.PERSONALITY.items():
            if f"{{{key}}}" in template:
                kwargs[key] = random.choice(options)

        return template.format(**kwargs)

# Usage in agent
async def handle_create_task(user_message, tool_result):
    if tool_result["success"]:
        return ResponseFormatter.format(
            "task_created",
            title=tool_result["data"]["title"]
        )
    else:
        return ResponseFormatter.format(
            "error_validation",
            field="description",
            limit=1000
        )
```

### Response Formatting Guidelines
| Event | Tone | Example |
|-------|------|---------|
| Task created | Affirming | "I've added 'buy groceries' to your tasks. You got this!" |
| Task completed | Celebrating | "Great! I've marked 'buy groceries' as completed ✓" |
| Task deleted | Confirming | "I've deleted task 2: 'Call John'" |
| Empty list | Helpful | "You don't have any tasks yet. Would you like to create one?" |
| Error | Guiding | "I couldn't find task 99. Try 'show my tasks' to see what's available." |

### Key Considerations
- Use varied language (rotate encouragements: "You got this!", "Let's make it happen!")
- Include emoji sparingly for emphasis (✓ for completions, ⚠️ for warnings)
- Always suggest next action when errors occur
- Format lists with numbers for easy reference (1. Task, 2. Task)
- Preserve user's original language when confirming ("buy groceries" not "Buy Groceries")

---

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Agent SDK | OpenAI Agents SDK | Constitution Principle VIII mandate, industry standard |
| MCP Client | MCPServerStreamableHttp (official) | Constitution Principle VII mandate, automatic retries |
| Backend Framework | FastAPI | Constitution Principle IX mandate, existing infrastructure |
| ORM | SQLModel | Constitution Principle X mandate, existing infrastructure |
| Database | Neon PostgreSQL | Constitution Principle V mandate, single source of truth |
| State Management | Stateless (DB-backed) | Constitution Principle IV mandate, restart resilience |
| LLM Provider | OpenAI API | Required for OpenAI Agents SDK |

---

## Integration with Existing Services

### Existing Services (Keep As-Is)
- ✅ **ConversationService**: Already implements stateless pattern with DB storage
- ✅ **Chat Endpoint**: Good request validation and error handling structure
- ✅ **Task Model**: Complete, no modifications needed
- ✅ **MCP Tools**: All 5 tools operational from Phase III-A

### Services Requiring Updates
- 🔄 **AgentRunner**: Integrate OpenAI Agents SDK for LLM calls
- 🔄 **LLMClient**: Migrate from generic OpenAI API to Agents SDK
- 🔄 **MCPTaskExecutor**: Replace custom HTTP client with `MCPServerStreamableHttp`

### New Components to Build
- ➕ **ResponseFormatter**: Template-based response generation with personality
- ➕ **ErrorHumanizer**: Translate technical errors to user-friendly messages
- ➕ **ConfidenceThresholds**: Risk-adjusted confidence scoring
- ➕ **TaskReferenceResolver**: Map positional references to task IDs
- ➕ **CircuitBreaker**: Prevent infinite loops and cascading failures

---

## Constitution Compliance

All decisions comply with project constitution:

| Principle | Compliance | Notes |
|-----------|------------|-------|
| I. Spec-Driven Development | ✅ | Following spec.md → plan.md → tasks.md workflow |
| II. AI-Generated Code Only | ✅ | All code will be generated via /sp.implement |
| III. Reusable Intelligence | ✅ | Agent designed for cross-domain reusability |
| IV. Stateless Backend | ✅ | Agent instances stateless, state in PostgreSQL |
| V. Database as Source of Truth | ✅ | All conversation state persisted in PostgreSQL |
| VI. MCP-Only Interactions | ✅ | Agent uses only MCP tools for data operations |
| VII. Official MCP SDK | ✅ | Using MCPServerStreamableHttp from official SDK |
| VIII. OpenAI Agents SDK | ✅ | Required by user spec and constitution |
| IX. FastAPI Backend | ✅ | Existing infrastructure, no changes |
| X. SQLModel ORM | ✅ | Existing infrastructure, no changes |
| XI. ChatKit Frontend | N/A | Not building frontend in this phase |
| XII. Better Auth | N/A | Auth handled by existing endpoint |
| XIII. Tool Chaining | ✅ | Agent can invoke multiple tools in sequence |
| XIV. Graceful Error Handling | ✅ | Circuit breaker, retries, error humanization |
| XV. Restart Resilience | ✅ | Stateless design survives server restarts |
| XVI. No Hardcoded Logic | ✅ | Agent uses LLM for intent, no hardcoded rules |

---

## Next Steps

1. **Phase 1**: Generate `data-model.md` (conversation entities and task reference schema)
2. **Phase 1**: Generate `quickstart.md` (agent integration examples)
3. **Phase 1**: Generate `contracts/` (agent API contracts and MCP tool schemas)
4. **Phase 2**: Generate `tasks.md` via `/sp.tasks` command
5. **Phase 3**: Implement via `/sp.implement` command

---

**Research Complete**: All architectural decisions documented. Ready to proceed to Phase 1 (Design & Contracts).
