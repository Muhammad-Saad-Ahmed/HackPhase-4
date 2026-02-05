# Agent-MCP Integration Guide

## Overview

This document explains how reusable AI agents consume MCP (Model Context Protocol) tools and how to ensure agents can be reused across future projects without modification.

## Architecture Principles

### 1. Tool-Driven Agent Design

Agents in this system are **tool-agnostic** - they discover and use tools dynamically without hardcoded knowledge of specific tools.

**Key Design Principle**: Agents know HOW to use tools (via MCP protocol), not WHICH tools exist (discovered at runtime).

```
┌─────────────────┐
│  Orchestrator   │
│     Agent       │  ← Stateless, reusable across projects
└────────┬────────┘
         │
         │ Discovers tools via MCP
         ▼
┌─────────────────┐
│   MCP Server    │
│  (Tool Registry)│  ← Project-specific tools registered here
└────────┬────────┘
         │
         │ Provides tools
         ▼
┌─────────────────────────────────────┐
│  Application Tools                  │
│  • list_todos, create_todo          │ ← Todo app
│  • list_customers, create_customer  │ ← CRM app
│  • list_notes, create_note          │ ← Notes app
└─────────────────────────────────────┘
```

### 2. MCP as the Abstraction Layer

The Model Context Protocol serves as the abstraction layer that enables agent reusability:

- **Agents**: Consume tools via standardized MCP interface
- **Tools**: Expose capabilities via MCP schemas
- **No Direct Coupling**: Agents never import or call application code directly

## How Agents Consume MCP Tools

### Step 1: Tool Discovery

When an agent needs to perform an action, it first discovers available tools:

```python
# Inside Orchestrator Agent
async def discover_tools(application_domain: str) -> List[ToolDefinition]:
    """
    Query MCP server for available tools in the application domain.

    This is done via HTTP request to the MCP server's /tools endpoint,
    NOT by importing application modules.
    """
    response = await httpx.get(
        f"{MCP_SERVER_URL}/tools",
        params={"application_domain": application_domain, "is_active": True}
    )
    return [ToolDefinition(**tool) for tool in response.json()["tools"]]
```

### Step 2: Semantic Tool Selection

Agents use **semantic similarity** to find the right tool for a user's intent:

```python
# Inside Tool Selection Skill
async def select_tool(
    intent: IntentType,
    entities: List[ExtractedEntity],
    application_domain: str
) -> SelectedTool:
    """
    Match intent and entities to best available tool using:
    1. Semantic similarity (embeddings)
    2. Parameter schema compatibility
    3. Confidence scoring

    No hardcoded tool mappings - purely semantic search.
    """
    # Generate embedding for search query
    query = f"{intent.value} {' '.join([e.type for e in entities])}"
    query_embedding = await generate_embedding(query)

    # Semantic search via MCP server
    response = await httpx.post(
        f"{MCP_SERVER_URL}/tools/search-similar",
        json={
            "query": query,
            "application_domain": application_domain,
            "limit": 5,
            "threshold": 0.75
        }
    )

    # Return best match with confidence
    tools = response.json()["tools"]
    return select_best_match(tools, entities)
```

**Why This Enables Reusability**: No agent code changes needed when adding new tools. The semantic search automatically finds relevant tools based on their descriptions.

### Step 3: Tool Invocation via MCP

Once a tool is selected, agents invoke it through the MCP protocol:

```python
# Inside Orchestrator Agent
async def invoke_tool(
    tool_name: str,
    parameters: Dict[str, Any],
    user_id: str,
    conversation_id: Optional[str] = None
) -> ToolResult:
    """
    Execute tool via MCP server's standardized invocation endpoint.

    The agent doesn't know what the tool does internally - it just
    passes parameters and receives structured results.
    """
    response = await httpx.post(
        f"{MCP_SERVER_URL}/tools/{tool_name}/invoke",
        json={
            "parameters": parameters,
            "user_id": user_id,
            "conversation_id": conversation_id
        }
    )
    return ToolResult(**response.json())
```

## Ensuring Agent Reusability

### Design Patterns for Reusable Agents

#### 1. Configuration-Driven Behavior

**BAD** (hardcoded, not reusable):
```python
class OrchestratorAgent:
    def __init__(self):
        self.mcp_url = "http://localhost:8001"  # ❌ Hardcoded
        self.allowed_intents = ["create", "list"]  # ❌ App-specific
```

**GOOD** (configurable, reusable):
```python
class OrchestratorAgent:
    def __init__(self, mcp_url: str, config: AgentConfig):
        self.mcp_url = mcp_url  # ✅ Injected
        self.config = config     # ✅ Flexible
```

#### 2. Schema-Driven Validation

Agents validate parameters using **tool schemas from MCP**, not hardcoded rules:

```python
async def validate_parameters(
    tool_name: str,
    parameters: Dict[str, Any]
) -> ValidationResult:
    """
    Fetch tool schema from MCP and validate parameters against it.
    No hardcoded validation rules.
    """
    # Get tool schema from MCP
    tool = await get_tool_definition(tool_name)

    # Validate using JSON Schema from tool
    validate(instance=parameters, schema=tool.parameter_schema)

    return ValidationResult(valid=True)
```

#### 3. Generic Error Handling

Error translation is **category-based**, not tool-specific:

```python
class ErrorRecoveryAgent:
    async def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> ErrorRecoveryResponse:
        """
        Categorize and translate errors generically.

        Categories:
        - user_fixable: Missing parameters, invalid values
        - retryable: Timeouts, temporary failures
        - system_level: Bugs, infrastructure issues

        No tool-specific error handling.
        """
        category = self.categorize_error(error)
        return self.generate_recovery_message(category, context)
```

### Validation Checklist: Is Your Agent Reusable?

Use this checklist to verify agent reusability:

- [ ] **No Hardcoded Tool Names**: Agent doesn't import or reference specific tool functions
- [ ] **No Application Logic**: Agent doesn't contain domain-specific business rules
- [ ] **Configuration Injection**: All environment-specific values injected via config
- [ ] **Schema-Driven**: Uses tool schemas from MCP for validation and parameter mapping
- [ ] **Semantic Discovery**: Finds tools via semantic search, not name matching
- [ ] **Generic Error Handling**: Error categories, not tool-specific error codes
- [ ] **Stateless**: All context passed explicitly or retrieved from database
- [ ] **MCP-Only Communication**: Tools invoked via MCP protocol, never direct function calls

## Reusability Example: Adding a CRM Application

To demonstrate reusability, let's add CRM support to an existing Todo system:

### Step 1: Register CRM Tools (No Agent Changes)

```python
# In your CRM application code
from mcp.server import Server

server = Server("crm-app")

@server.tool(
    name="list_customers",
    description="Lists all customers in the CRM. Can filter by company name. Use this when user asks to see, show, or list customers."
)
async def list_customers(company: str = "") -> List[Customer]:
    # Your CRM-specific implementation
    return get_customers_from_database(company)

@server.tool(
    name="create_customer",
    description="Creates a new customer record. Use when user wants to add, create, or register a customer. Requires name and email."
)
async def create_customer(name: str, email: str, company: str = "") -> Customer:
    # Your CRM-specific implementation
    return save_customer_to_database(name, email, company)
```

### Step 2: Sync Tools to MCP Registry

```bash
# Generate embeddings and register tools
python -m src.mcp.sync_tools --domain crm
```

### Step 3: Use Existing Agents (No Code Changes)

```python
# The SAME Orchestrator Agent now works with CRM
response = await orchestrator.invoke(
    request="Show me all customers at Acme Corp",
    user_id="user-123",
    application_domain="crm"  # ← Only difference
)

# Agent will:
# 1. Classify intent → "list"
# 2. Extract entities → {type: "customer", attributes: {company: "Acme Corp"}}
# 3. Search tools in "crm" domain
# 4. Find "list_customers" via semantic similarity
# 5. Map entities to parameters → {company: "Acme Corp"}
# 6. Invoke tool via MCP
# 7. Return results
```

**Result**: CRM support added without modifying any agent code. The agents discovered and used the new tools automatically.

## Advanced: Multi-Domain Agent Orchestration

For applications that span multiple domains (e.g., "Show my todos and upcoming customer meetings"), agents can orchestrate tools from different domains:

```python
async def handle_multi_domain_request(request: str) -> Response:
    # 1. Classify as multi-domain request
    domains = detect_domains(request)  # ["todo", "crm"]

    # 2. For each domain, discover relevant tools
    all_tools = []
    for domain in domains:
        tools = await discover_tools(domain)
        all_tools.extend(tools)

    # 3. Select best tools from all domains
    todo_tool = select_tool(intent="list", entities=["task"], tools=all_tools)
    crm_tool = select_tool(intent="list", entities=["meeting"], tools=all_tools)

    # 4. Execute in parallel and aggregate
    results = await asyncio.gather(
        invoke_tool(todo_tool),
        invoke_tool(crm_tool)
    )

    return combine_results(results)
```

## Testing Agent Reusability

To validate that your agents are truly reusable, test them against multiple application domains:

```python
# tests/integration/test_agent_reusability.py

import pytest

@pytest.mark.asyncio
async def test_orchestrator_works_across_domains():
    """Verify Orchestrator Agent works with todo, crm, and notes domains."""

    domains = ["todo", "crm", "notes"]

    for domain in domains:
        response = await orchestrator.invoke(
            request="Show me the list",
            user_id="test-user",
            application_domain=domain
        )

        # Agent should successfully find and invoke appropriate list tool
        assert response.status == "success"
        assert response.selected_tool.tool_name.startswith("list_")
        assert response.selected_tool.confidence >= 0.8

@pytest.mark.asyncio
async def test_agent_discovers_new_tools_automatically():
    """Verify agent finds newly registered tools without code changes."""

    # Register a new tool for "inventory" domain
    await register_tool(
        name="list_inventory",
        domain="inventory",
        description="Lists all inventory items"
    )

    # Agent should discover it immediately
    response = await orchestrator.invoke(
        request="Show me inventory",
        user_id="test-user",
        application_domain="inventory"
    )

    assert response.selected_tool.tool_name == "list_inventory"
```

## Summary: The Reusability Contract

For agents to remain reusable across projects, they must adhere to this contract:

1. **Discover, Don't Hardcode**: Tools discovered at runtime via MCP, never imported
2. **Schemas Are Truth**: Validation and parameters driven by tool schemas from MCP
3. **Semantic Not Literal**: Tool selection via semantic similarity, not name matching
4. **Stateless Always**: Context explicit or database-backed, never in-memory
5. **Generic Categories**: Error handling, intent types, entity types are domain-agnostic
6. **Configuration Over Code**: Environment-specific values injected, never hardcoded
7. **MCP Only**: Tool invocation exclusively through MCP protocol

**Follow these principles, and your agents will work unchanged across todo, CRM, notes, inventory, calendar, and any other application domain you add in the future.**

## Additional Resources

- [MCP Protocol Specification](contracts/mcp-tools.yaml)
- [Agent API Contract](contracts/agent-api.yaml)
- [Skill API Contract](contracts/skill-api.yaml)
- [Quick Start Guide](../specs/001-reusable-agents/quickstart.md)
- [Research Decisions](../specs/001-reusable-agents/research.md)
