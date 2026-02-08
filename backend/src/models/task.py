"""
SQLModel definitions for the Todo application.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending", regex="^(pending|completed)$")


class Task(TaskBase, table=True):
    __table_args__ = {'extend_existing': True}

    id: int = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)


# Tool Metadata and Tool Invocation models would go here as well
# But for now, let's focus on the Task model for the MVP