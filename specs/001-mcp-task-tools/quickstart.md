# Quickstart Guide: MCP Task Management Tools

**Feature**: 001-mcp-task-tools
**Audience**: Developers implementing the MCP tools
**Prerequisites**: Familiarity with Python, FastAPI, SQLModel, and async/await

## Overview

This guide walks through implementing five stateless MCP tools for task management:
- `add_task` - Create tasks
- `list_tasks` - Query tasks with optional filtering
- `update_task` - Modify task details
- `complete_task` - Mark tasks as completed
- `delete_task` - Remove tasks permanently

All tools are stateless, use the existing Task model, and return structured responses.

## Architecture at a Glance

```
AI Agent
    ↓
MCP SDK (Tool Invocation)
    ↓
Tool Handler (Validation + Business Logic)
    ↓
SQLModel (Database ORM)
    ↓
Neon PostgreSQL (Persistent Storage)
```

**Key Principles**:
- Tools are stateless (no memory between invocations)
- All state persists in database
- Input validated before database operations
- Responses follow consistent structure (success/error)

## Project Structure

```
backend/
├── src/
│   ├── mcp_tools/
│   │   ├── __init__.py
│   │   ├── base.py                    # Existing: BaseTool, ResponseBuilder
│   │   ├── schemas.py                 # NEW: Pydantic models for tool I/O
│   │   ├── task_tools.py              # NEW: Tool handler implementations
│   │   └── server.py                  # NEW: MCP server initialization
│   ├── models/
│   │   └── task.py                    # Existing: Task SQLModel definition
│   ├── core/
│   │   ├── database.py                # Existing: DB session management
│   │   └── config.py                  # Existing: Configuration
│   └── main.py                        # Existing: FastAPI app (integrate MCP server)
└── tests/
    ├── mcp_tools/
    │   ├── test_add_task.py           # NEW: Tool tests
    │   ├── test_list_tasks.py
    │   ├── test_update_task.py
    │   ├── test_complete_task.py
    │   └── test_delete_task.py
    └── conftest.py                     # Existing: Test fixtures

specs/001-mcp-task-tools/
├── spec.md                             # Requirements
├── plan.md                             # This implementation plan
├── research.md                         # Design decisions
├── data-model.md                       # Task entity documentation
├── quickstart.md                       # This file
└── contracts/                          # JSON Schemas for each tool
    ├── add_task.json
    ├── list_tasks.json
    ├── update_task.json
    ├── complete_task.json
    └── delete_task.json
```

## Step 1: Install Dependencies

Add MCP SDK to your project (using UV package manager per constitution):

```bash
cd backend
uv add mcp
```

Verify existing dependencies are present:
- `sqlmodel` - ORM (already installed)
- `fastapi` - Web framework (already installed)
- `asyncpg` - PostgreSQL async driver (already installed)

## Step 2: Define Pydantic Schemas

Create `backend/src/mcp_tools/schemas.py`:

```python
"""
Pydantic schemas for MCP tool input validation and response serialization.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Input Schemas

class AddTaskInput(BaseModel):
    """Input for add_task tool."""
    title: str = Field(min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(default=None, max_length=1000, description="Task description")


class ListTasksInput(BaseModel):
    """Input for list_tasks tool."""
    status: Optional[str] = Field(default=None, pattern="^(pending|completed)$", description="Filter by status")


class UpdateTaskInput(BaseModel):
    """Input for update_task tool."""
    task_id: int = Field(ge=1, description="Task ID to update")
    title: Optional[str] = Field(default=None, min_length=1, max_length=255, description="New title")
    description: Optional[str] = Field(default=None, max_length=1000, description="New description")


class CompleteTaskInput(BaseModel):
    """Input for complete_task tool."""
    task_id: int = Field(ge=1, description="Task ID to complete")


class DeleteTaskInput(BaseModel):
    """Input for delete_task tool."""
    task_id: int = Field(ge=1, description="Task ID to delete")


# Output Schemas

class TaskOutput(BaseModel):
    """Standard task representation in responses."""
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel


class DeletedTaskOutput(BaseModel):
    """Response for delete_task tool."""
    task_id: int
    deleted: bool = True
```

## Step 3: Implement Tool Handlers

Create `backend/src/mcp_tools/task_tools.py`:

```python
"""
MCP tool implementations for task management.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.task import Task
from ..core.database import get_db_session
from .base import ResponseBuilder
from .schemas import (
    AddTaskInput, ListTasksInput, UpdateTaskInput,
    CompleteTaskInput, DeleteTaskInput, TaskOutput
)


async def add_task(title: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new task.

    Args:
        title: Task title (1-255 characters)
        description: Optional task description (max 1000 characters)

    Returns:
        Success response with created task or error response
    """
    try:
        # Validate input
        input_data = AddTaskInput(title=title, description=description)

        # Create task
        async for session in get_db_session():
            task = Task(
                title=input_data.title,
                description=input_data.description,
                status="pending"
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

            return ResponseBuilder.success(
                data=TaskOutput.from_orm(task).dict(),
                message="Task created successfully"
            )

    except ValueError as e:
        return ResponseBuilder.error(
            error_msg=str(e),
            code="VALIDATION_ERROR",
            details={"field": "title or description"}
        )
    except Exception as e:
        return ResponseBuilder.error(
            error_msg=f"Failed to create task: {str(e)}",
            code="DATABASE_ERROR"
        )


async def list_tasks(status: Optional[str] = None) -> Dict[str, Any]:
    """
    List all tasks or filter by status.

    Args:
        status: Optional filter - "pending" or "completed"

    Returns:
        Success response with task list or error response
    """
    try:
        # Validate input
        input_data = ListTasksInput(status=status)

        async for session in get_db_session():
            # Build query
            query = select(Task).order_by(Task.created_at.desc())
            if input_data.status:
                query = query.where(Task.status == input_data.status)

            # Execute query
            result = await session.execute(query)
            tasks = result.scalars().all()

            # Build response
            task_list = [TaskOutput.from_orm(task).dict() for task in tasks]
            count = len(task_list)
            filter_msg = f" {input_data.status}" if input_data.status else ""
            message = f"Found {count}{filter_msg} task{'s' if count != 1 else ''}" if count > 0 else "No tasks found"

            return ResponseBuilder.success(
                data=task_list,
                message=message
            )

    except ValueError as e:
        return ResponseBuilder.error(
            error_msg=str(e),
            code="VALIDATION_ERROR",
            details={"field": "status", "allowed_values": ["pending", "completed", None]}
        )
    except Exception as e:
        return ResponseBuilder.error(
            error_msg=f"Failed to list tasks: {str(e)}",
            code="DATABASE_ERROR"
        )


async def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update task title and/or description.

    Args:
        task_id: ID of task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Success response with updated task or error response
    """
    try:
        # Validate input
        input_data = UpdateTaskInput(task_id=task_id, title=title, description=description)

        if not input_data.title and not input_data.description:
            return ResponseBuilder.error(
                error_msg="At least one of title or description must be provided",
                code="VALIDATION_ERROR"
            )

        async for session in get_db_session():
            # Fetch task
            result = await session.execute(select(Task).where(Task.id == input_data.task_id))
            task = result.scalar_one_or_none()

            if not task:
                return ResponseBuilder.error(
                    error_msg="Task not found",
                    code="NOT_FOUND",
                    details={"task_id": input_data.task_id}
                )

            # Update fields
            if input_data.title is not None:
                task.title = input_data.title
            if input_data.description is not None:
                task.description = input_data.description

            await session.commit()
            await session.refresh(task)

            return ResponseBuilder.success(
                data=TaskOutput.from_orm(task).dict(),
                message="Task updated successfully"
            )

    except ValueError as e:
        return ResponseBuilder.error(
            error_msg=str(e),
            code="VALIDATION_ERROR"
        )
    except Exception as e:
        return ResponseBuilder.error(
            error_msg=f"Failed to update task: {str(e)}",
            code="DATABASE_ERROR"
        )


async def complete_task(task_id: int) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        task_id: ID of task to complete

    Returns:
        Success response with completed task or error response
    """
    try:
        # Validate input
        input_data = CompleteTaskInput(task_id=task_id)

        async for session in get_db_session():
            # Fetch task
            result = await session.execute(select(Task).where(Task.id == input_data.task_id))
            task = result.scalar_one_or_none()

            if not task:
                return ResponseBuilder.error(
                    error_msg="Task not found",
                    code="NOT_FOUND",
                    details={"task_id": input_data.task_id}
                )

            # Mark completed (idempotent)
            was_already_completed = task.status == "completed"
            task.status = "completed"
            task.completed_at = datetime.utcnow()

            await session.commit()
            await session.refresh(task)

            message = "Task was already completed" if was_already_completed else "Task marked as completed"
            return ResponseBuilder.success(
                data=TaskOutput.from_orm(task).dict(),
                message=message
            )

    except ValueError as e:
        return ResponseBuilder.error(
            error_msg=str(e),
            code="VALIDATION_ERROR"
        )
    except Exception as e:
        return ResponseBuilder.error(
            error_msg=f"Failed to complete task: {str(e)}",
            code="DATABASE_ERROR"
        )


async def delete_task(task_id: int) -> Dict[str, Any]:
    """
    Permanently delete a task.

    Args:
        task_id: ID of task to delete

    Returns:
        Success response with deletion confirmation or error response
    """
    try:
        # Validate input
        input_data = DeleteTaskInput(task_id=task_id)

        async for session in get_db_session():
            # Fetch task
            result = await session.execute(select(Task).where(Task.id == input_data.task_id))
            task = result.scalar_one_or_none()

            if not task:
                return ResponseBuilder.error(
                    error_msg="Task not found",
                    code="NOT_FOUND",
                    details={"task_id": input_data.task_id}
                )

            # Delete task
            await session.delete(task)
            await session.commit()

            return ResponseBuilder.success(
                data={"task_id": input_data.task_id, "deleted": True},
                message="Task deleted successfully"
            )

    except ValueError as e:
        return ResponseBuilder.error(
            error_msg=str(e),
            code="VALIDATION_ERROR"
        )
    except Exception as e:
        return ResponseBuilder.error(
            error_msg=f"Failed to delete task: {str(e)}",
            code="DATABASE_ERROR"
        )
```

## Step 4: Initialize MCP Server

Create `backend/src/mcp_tools/server.py`:

```python
"""
MCP server initialization and tool registration.
"""
from mcp import Server
from .task_tools import add_task, list_tasks, update_task, complete_task, delete_task


# Initialize MCP server
mcp_server = Server("task-manager")


# Register tools
@mcp_server.tool("add_task", description="Create a new task")
async def add_task_tool(title: str, description: str | None = None):
    return await add_task(title, description)


@mcp_server.tool("list_tasks", description="List all tasks or filter by status")
async def list_tasks_tool(status: str | None = None):
    return await list_tasks(status)


@mcp_server.tool("update_task", description="Update task title and/or description")
async def update_task_tool(task_id: int, title: str | None = None, description: str | None = None):
    return await update_task(task_id, title, description)


@mcp_server.tool("complete_task", description="Mark a task as completed")
async def complete_task_tool(task_id: int):
    return await complete_task(task_id)


@mcp_server.tool("delete_task", description="Delete a task permanently")
async def delete_task_tool(task_id: int):
    return await delete_task(task_id)
```

## Step 5: Integrate with FastAPI

Update `backend/src/main.py` to include MCP server:

```python
from fastapi import FastAPI
from .mcp_tools.server import mcp_server
from .core.database import init_db

app = FastAPI(title="Todo AI Chatbot")

@app.on_event("startup")
async def startup():
    """Initialize database and MCP server on startup."""
    await init_db()
    # MCP server is already initialized in server.py

@app.get("/")
async def root():
    return {"message": "Todo AI Chatbot API"}

# Mount MCP server (endpoint depends on MCP SDK implementation)
# Typically: app.mount("/mcp", mcp_server.asgi_app())
```

## Step 6: Write Tests

Create `backend/tests/mcp_tools/test_add_task.py`:

```python
"""
Tests for add_task MCP tool.
"""
import pytest
from backend.src.mcp_tools.task_tools import add_task


@pytest.mark.asyncio
async def test_add_task_success():
    """Test creating a task with title only."""
    result = await add_task("Test task")

    assert result["success"] is True
    assert result["data"]["title"] == "Test task"
    assert result["data"]["status"] == "pending"
    assert result["data"]["description"] is None
    assert result["data"]["id"] > 0


@pytest.mark.asyncio
async def test_add_task_with_description():
    """Test creating a task with title and description."""
    result = await add_task("Test task", "Test description")

    assert result["success"] is True
    assert result["data"]["title"] == "Test task"
    assert result["data"]["description"] == "Test description"


@pytest.mark.asyncio
async def test_add_task_title_too_long():
    """Test validation error for title exceeding 255 characters."""
    long_title = "x" * 256
    result = await add_task(long_title)

    assert result["success"] is False
    assert result["code"] == "VALIDATION_ERROR"
```

## Step 7: Run and Test

```bash
# Start development server
cd backend
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest tests/mcp_tools/ -v

# Test tool invocation manually (via MCP client or HTTP endpoint)
curl -X POST http://localhost:8000/mcp/tool/add_task \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Test description"}'
```

## Next Steps

1. **Task Generation**: Run `/sp.tasks` to generate detailed implementation tasks
2. **Implementation**: Follow tasks to build each tool incrementally
3. **Testing**: Write comprehensive tests for all tools and edge cases
4. **Integration**: Connect MCP server to AI agents (OpenAI Agents SDK)
5. **Deployment**: Configure for production (connection pooling, error monitoring)

## Common Issues

### Issue: Database session not closing
**Solution**: Use `async for session in get_db_session()` pattern to ensure proper cleanup

### Issue: Validation errors not clear
**Solution**: Include field names and constraints in error details

### Issue: Tool not registered
**Solution**: Verify `@mcp_server.tool()` decorator is applied and server is imported in main.py

### Issue: Tests fail with database errors
**Solution**: Use test database fixtures and ensure proper async context management

## References

- [Feature Specification](./spec.md)
- [Research & Decisions](./research.md)
- [Data Model](./data-model.md)
- [Tool Contracts](./contracts/)
- [MCP SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
