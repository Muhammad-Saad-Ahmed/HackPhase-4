"""
Task REST API endpoint implementation.
Provides CRUD operations for tasks via traditional REST API (in addition to chat-based MCP tools).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from ..services.task_service import TaskService
from ..core.database import get_db_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
from ..models.task import Task
from ..core.logging import logger


router = APIRouter()


# Request/Response Models
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Helper function to get task service
def get_task_service():
    """Dependency injection for TaskService."""
    return TaskService()


@router.get("/v1/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = Query(default="all", regex="^(all|pending|completed)$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Get list of tasks with optional filtering.

    Query Parameters:
    - status: Filter by task status (all, pending, completed)
    - limit: Maximum number of tasks to return (1-100)
    - offset: Number of tasks to skip for pagination
    """
    try:
        tasks = await task_service.get_tasks(status=status, limit=limit, offset=offset)
        logger.info(
            "Tasks retrieved",
            user_id=current_user.id,
            status=status,
            count=len(tasks)
        )
        return tasks
    except Exception as e:
        logger.error("Error retrieving tasks", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tasks"
        )


@router.post("/v1/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Create a new task.

    Request Body:
    - title: Task title (required, 1-255 characters)
    - description: Task description (optional, max 1000 characters)
    """
    try:
        new_task = await task_service.create_task(
            title=task_data.title,
            description=task_data.description
        )
        logger.info(
            "Task created",
            user_id=current_user.id,
            task_id=new_task.id,
            title=new_task.title
        )
        return new_task
    except Exception as e:
        logger.error("Error creating task", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
        )


@router.get("/v1/tasks/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Get a specific task by ID.

    Path Parameters:
    - task_id: ID of the task to retrieve
    """
    try:
        task = await task_service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving task", error=str(e), task_id=task_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task"
        )


@router.put("/v1/tasks/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Update a task's title or description.

    Path Parameters:
    - task_id: ID of the task to update

    Request Body:
    - title: New task title (optional)
    - description: New task description (optional)
    """
    try:
        updated_task = await task_service.update_task(
            task_id=task_id,
            title=task_data.title,
            description=task_data.description
        )
        logger.info(
            "Task updated",
            user_id=current_user.id,
            task_id=task_id
        )
        return updated_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error updating task", error=str(e), task_id=task_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )


@router.patch("/v1/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task_endpoint(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Mark a task as completed.

    Path Parameters:
    - task_id: ID of the task to complete
    """
    try:
        completed_task = await task_service.complete_task(task_id)
        logger.info(
            "Task completed",
            user_id=current_user.id,
            task_id=task_id
        )
        return completed_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error completing task", error=str(e), task_id=task_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete task"
        )


@router.delete("/v1/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_endpoint(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Delete a task permanently.

    Path Parameters:
    - task_id: ID of the task to delete
    """
    try:
        await task_service.delete_task(task_id)
        logger.info(
            "Task deleted",
            user_id=current_user.id,
            task_id=task_id
        )
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error deleting task", error=str(e), task_id=task_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )
