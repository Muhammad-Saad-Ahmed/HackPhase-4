# Agent Reusability Validation Guide

## Purpose

This document provides a comprehensive validation framework to verify that agents can be reused across future projects without modification. Use these tests and checklists to ensure your agents follow the reusability principles.

## Validation Criteria

### ✅ Level 1: Code Analysis (Static Validation)

Run these checks on agent code to identify reusability violations:

#### 1.1 No Hardcoded Tool References

**Test**: Search for hardcoded tool names in agent code

```bash
# Should return NO matches in agent code
grep -r "list_todos\|create_todo\|list_customers" backend/src/agents/
grep -r "delete_note\|update_task" backend/src/agents/
```

**Expected Result**: Zero matches. Agents should only reference tools via variables or MCP discovery.

**Violation Example**:
```python
# ❌ BAD - Hardcoded tool name
if intent == "list":
    result = await invoke_tool("list_todos", params)
```

**Correct Implementation**:
```python
# ✅ GOOD - Tool discovered dynamically
tool = await select_tool_by_semantic_search(intent, entities, domain)
result = await invoke_tool(tool.name, params)
```

#### 1.2 No Application-Specific Logic

**Test**: Search for domain-specific keywords

```bash
# Should return NO matches in agent code (except in comments/docs)
grep -r "todo\|customer\|note\|task" backend/src/agents/*.py | grep -v "^#" | grep -v '"""'
```

**Expected Result**: Only generic references like "entity", "item", "record".

**Violation Example**:
```python
# ❌ BAD - Domain-specific logic
if entity_type == "task":
    # Special handling for tasks
    validate_task_status(entity)
```

**Correct Implementation**:
```python
# ✅ GOOD - Generic validation
validation_result = await validate_entity_via_tool(entity_type, entity_id)
```

#### 1.3 Configuration Injection

**Test**: Verify all environment-specific values come from config

```python
# Run this test
from backend.src.agents.orchestrator import OrchestratorAgent
import inspect

# Get all hardcoded strings in agent class
source = inspect.getsource(OrchestratorAgent)
hardcoded_urls = re.findall(r'"http[s]?://[^"]*"', source)
hardcoded_ports = re.findall(r':800[01]', source)

print("Hardcoded URLs:", hardcoded_urls)  # Should be empty
print("Hardcoded ports:", hardcoded_ports)  # Should be empty
```

**Expected Result**: All URLs, ports, and environment values from `settings` or injected parameters.

---

### ✅ Level 2: Cross-Domain Testing (Dynamic Validation)

Deploy agents against multiple application domains to verify they work identically:

#### 2.1 Multi-Domain Intent Classification

**Test Suite**:

```python
# tests/integration/test_cross_domain_reusability.py

import pytest
from backend.src.agents.orchestrator import OrchestratorAgent, OrchestratorInput

@pytest.mark.asyncio
@pytest.mark.parametrize("domain,request,expected_tool_prefix", [
    ("todo", "Show me my tasks", "list_"),
    ("crm", "Show me my customers", "list_"),
    ("notes", "Show me my notes", "list_"),
    ("inventory", "Show me inventory items", "list_"),
])
async def test_agent_works_across_domains(domain, request, expected_tool_prefix):
    """
    Verify Orchestrator Agent works identically across different domains.

    The agent should:
    1. Classify intent correctly (list)
    2. Extract entities correctly
    3. Find appropriate tool via semantic search
    4. Invoke tool successfully

    No agent code changes between domains.
    """
    agent = OrchestratorAgent()

    response = await agent.invoke(OrchestratorInput(
        request=request,
        user_id="test-user",
        application_domain=domain
    ))

    # Verify successful execution
    assert response.status == "success", f"Failed in {domain} domain: {response.clarification}"

    # Verify tool selection
    assert response.selected_tool is not None
    assert response.selected_tool.tool_name.startswith(expected_tool_prefix)
    assert response.selected_tool.confidence >= 0.75

    # Verify intent classification
    assert response.intent["type"] == "list"
    assert response.intent["confidence"] >= 0.8

    await agent.close()
```

**Expected Result**: All tests pass without agent modifications.

#### 2.2 Tool Discovery After New Registration

**Test**: Verify agent discovers newly registered tools automatically

```python
@pytest.mark.asyncio
async def test_agent_discovers_new_domain_automatically():
    """
    Verify agent adapts to new application domain without code changes.

    Steps:
    1. Register tools for a brand new domain
    2. Use existing agent with new domain
    3. Verify agent discovers and uses new tools
    """
    # Register new domain tools (simulated)
    new_domain = "project-management"
    await register_tool(
        name="list_projects",
        domain=new_domain,
        description="Lists all projects in the system. Use when user wants to see projects."
    )
    await register_tool(
        name="create_project",
        domain=new_domain,
        description="Creates a new project. Use when user wants to start or create a project."
    )

    # Use existing agent with new domain (NO agent code changes)
    agent = OrchestratorAgent()
    response = await agent.invoke(OrchestratorInput(
        request="Show me all projects",
        user_id="test-user",
        application_domain=new_domain
    ))

    # Agent should discover new tools automatically
    assert response.status == "success"
    assert response.selected_tool.tool_name == "list_projects"

    await agent.close()
```

**Expected Result**: Agent works with new domain immediately after tool registration.

#### 2.3 Parameter Mapping Across Schemas

**Test**: Verify agent maps entities to tool parameters correctly for different schemas

```python
@pytest.mark.asyncio
@pytest.mark.parametrize("domain,request,tool_name,expected_params", [
    (
        "todo",
        "Show tasks with status done",
        "list_todos",
        {"status": "done"}
    ),
    (
        "crm",
        "Show customers at Acme Corp",
        "list_customers",
        {"company": "Acme Corp"}
    ),
    (
        "inventory",
        "Show items with low stock",
        "list_inventory",
        {"stock_level": "low"}
    ),
])
async def test_agent_maps_parameters_correctly(domain, request, tool_name, expected_params):
    """
    Verify agent maps extracted entities to tool parameters correctly
    across different tool schemas without hardcoded mapping rules.
    """
    agent = OrchestratorAgent()

    response = await agent.invoke(OrchestratorInput(
        request=request,
        user_id="test-user",
        application_domain=domain
    ))

    assert response.status == "success"
    assert response.selected_tool.tool_name == tool_name

    # Verify parameter mapping
    for key, expected_value in expected_params.items():
        assert key in response.selected_tool.parameters
        assert response.selected_tool.parameters[key] == expected_value

    await agent.close()
```

**Expected Result**: Agent correctly maps entities to parameters for all domains.

---

### ✅ Level 3: Configuration Portability

Test that agents work in different deployment environments:

#### 3.1 MCP Server URL Configuration

**Test**: Verify agent accepts MCP server URL injection

```python
@pytest.mark.asyncio
async def test_agent_accepts_mcp_url_configuration():
    """Verify agent works with different MCP server URLs."""

    # Test with different URLs
    urls = [
        "http://localhost:8001",
        "http://mcp-server:8001",
        "https://mcp.example.com",
    ]

    for url in urls:
        agent = OrchestratorAgent(mcp_url=url)
        assert agent.mcp_url == url
        await agent.close()
```

**Expected Result**: Agent accepts any MCP URL without code changes.

#### 3.2 Confidence Threshold Configuration

**Test**: Verify agent respects configurable thresholds

```python
@pytest.mark.asyncio
async def test_agent_respects_confidence_thresholds():
    """Verify agent clarification behavior is configurable."""

    from backend.src.core.config import settings

    # Test with different thresholds (would normally be env var)
    original_threshold = settings.intent_confidence_threshold  # If this existed

    # Low threshold - accepts lower confidence
    settings.intent_confidence_threshold = 0.5
    agent = OrchestratorAgent()
    # ... test with low-confidence request ...

    # High threshold - requires high confidence
    settings.intent_confidence_threshold = 0.9
    agent = OrchestratorAgent()
    # ... test with medium-confidence request ...

    await agent.close()
```

**Expected Result**: Agent behavior adapts to configuration without code changes.

---

### ✅ Level 4: Reusability Metrics

Quantify agent reusability:

#### 4.1 Code Coupling Score

```python
def calculate_agent_coupling_score(agent_file_path: str) -> float:
    """
    Calculate coupling score for agent code.

    Score components:
    - Hardcoded tool names: -10 points each
    - Domain-specific keywords: -5 points each
    - Hardcoded URLs/ports: -5 points each
    - Config injection: +10 points
    - MCP-only communication: +10 points

    Score >= 80: Highly reusable
    Score 60-79: Moderately reusable
    Score < 60: Poorly reusable
    """
    with open(agent_file_path, 'r') as f:
        code = f.read()

    score = 100

    # Penalties
    tool_references = len(re.findall(r'"(list|create|update|delete)_[a-z_]+"\s*\(', code))
    score -= tool_references * 10

    domain_keywords = len(re.findall(r'\b(todo|task|customer|note|inventory)\b', code, re.IGNORECASE))
    score -= domain_keywords * 5

    hardcoded_urls = len(re.findall(r'"http[s]?://[^"]*"', code))
    score -= hardcoded_urls * 5

    # Bonuses
    if 'from ..core.config import settings' in code:
        score += 10

    if 'self.http_client.post' in code and 'mcp' in code.lower():
        score += 10

    return max(0, min(100, score))

# Run for all agents
orchestrator_score = calculate_agent_coupling_score('backend/src/agents/orchestrator.py')
print(f"Orchestrator Agent Coupling Score: {orchestrator_score}/100")
```

**Target**: >= 80 for all agents

#### 4.2 Domain Compatibility Matrix

Test agents against N domains and measure success rate:

```python
async def generate_compatibility_matrix():
    """
    Test agents against multiple domains and generate compatibility report.

    Returns:
        Matrix showing which agents work with which domains.
    """
    agents = [
        ("Orchestrator", OrchestratorAgent),
        ("Validation", ValidationAgent),
        ("Conversation", ConversationAgent),
    ]

    domains = ["todo", "crm", "notes", "inventory", "calendar"]

    results = {}

    for agent_name, AgentClass in agents:
        results[agent_name] = {}
        for domain in domains:
            try:
                agent = AgentClass()
                # Test basic operation in domain
                success = await test_agent_in_domain(agent, domain)
                results[agent_name][domain] = "✅" if success else "❌"
            except Exception as e:
                results[agent_name][domain] = f"❌ {str(e)}"

    return results

# Expected output:
#                 | todo | crm | notes | inventory | calendar |
# ----------------|------|-----|-------|-----------|----------|
# Orchestrator    |  ✅  | ✅  |  ✅   |    ✅     |    ✅    |
# Validation      |  ✅  | ✅  |  ✅   |    ✅     |    ✅    |
# Conversation    |  ✅  | ✅  |  ✅   |    ✅     |    ✅    |
```

**Target**: 100% compatibility across all tested domains

---

## Validation Checklist

Use this checklist before deploying agents to a new project:

### Code Review Checklist

- [ ] **No hardcoded tool names** in agent code
- [ ] **No domain-specific logic** (todo, crm, notes, etc.)
- [ ] **All URLs/ports from config**, not hardcoded
- [ ] **MCP-only tool invocation**, no direct imports
- [ ] **Schema-driven validation**, not hardcoded rules
- [ ] **Generic error handling**, not tool-specific
- [ ] **Stateless implementation**, context via database/parameters
- [ ] **Configuration injection** for environment-specific values

### Testing Checklist

- [ ] **Cross-domain tests pass** for ≥3 different domains
- [ ] **New domain test passes** (agent discovers new tools automatically)
- [ ] **Parameter mapping tests pass** across different schemas
- [ ] **Confidence threshold tests pass** (configurable behavior)
- [ ] **MCP URL configuration test passes**
- [ ] **Coupling score ≥80** for all agents
- [ ] **Domain compatibility 100%** across tested domains

### Documentation Checklist

- [ ] **Agent purpose documented** without domain-specific examples
- [ ] **MCP integration explained** with generic examples
- [ ] **Reusability principles documented**
- [ ] **Configuration options listed**
- [ ] **Cross-domain usage examples provided**

---

## Certification Process

To certify an agent as "Reusable Across Projects":

1. **Pass all Level 1-3 tests** with 100% success rate
2. **Achieve coupling score ≥80**
3. **Demonstrate 100% domain compatibility** across ≥3 domains
4. **Document reusability contract** (inputs, outputs, assumptions)
5. **Provide cross-domain usage examples**

### Certification Badge

Once certified, add this badge to agent documentation:

```markdown
## 🔄 Reusability Certified

This agent has been validated for cross-project reusability:
- ✅ Zero hardcoded tool references
- ✅ 100% domain compatibility (tested: todo, crm, notes, inventory, calendar)
- ✅ Coupling score: 95/100
- ✅ MCP-only tool communication
- ✅ Configuration-driven behavior

Safe to use across any application domain without modification.
```

---

## Troubleshooting Common Reusability Issues

### Issue 1: Agent fails in new domain

**Symptom**: Agent works in todo domain but fails in crm domain

**Diagnosis**:
```python
# Check for hardcoded domain assumptions
grep -r "todo\|task" backend/src/agents/
```

**Fix**: Replace domain-specific logic with generic entity handling

### Issue 2: Low tool selection confidence

**Symptom**: Agent always requests clarification in new domain

**Diagnosis**:
```python
# Check tool descriptions are detailed enough for semantic search
print(tool.description)  # Should be ≥50 characters with examples
```

**Fix**: Improve tool descriptions with more context and examples

### Issue 3: Parameter mapping failures

**Symptom**: Tool invocation fails due to missing/incorrect parameters

**Diagnosis**:
```python
# Verify parameter mapping uses schema, not hardcoded rules
# Look for code like:
params = {"task_id": entity.value}  # ❌ Hardcoded mapping
```

**Fix**: Implement schema-driven parameter mapping

---

## Summary

An agent is reusable if:

1. **It works identically across ≥3 application domains**
2. **It discovers new domains automatically** (no code changes)
3. **It has zero hardcoded tool/domain references**
4. **It communicates exclusively via MCP protocol**
5. **Its coupling score is ≥80/100**
6. **It accepts configuration injection** for environment values
7. **It passes all validation tests** in this guide

**Follow this validation framework to ensure your agents can be deployed to any future project without modification.**
