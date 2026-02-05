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
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class DeletedTaskOutput(BaseModel):
    """Response for delete_task tool."""
    task_id: int
    deleted: bool = True
