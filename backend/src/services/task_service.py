"""
Business logic for task operations.
"""
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List, Optional
from ..models.task import Task, TaskBase
from datetime import datetime


class TaskService:
    """
    Service class for task-related business logic.
    """

    def __init__(self):
        pass

    async def create_task(self, title: str, description: Optional[str] = None) -> Task:
        """
        Create a new task with the given title and optional description.
        """
        from ..core.database import engine

        async with AsyncSession(engine) as session:
            # Create a new task instance
            task = Task(
                title=title,
                description=description,
                status="pending",
                created_at=datetime.utcnow()
            )

            # Add the task to the session and commit
            session.add(task)
            await session.commit()
            await session.refresh(task)

            return task

    async def get_tasks(self, status: str = "all", limit: int = 50, offset: int = 0) -> List[Task]:
        """
        Retrieve a list of tasks with optional filtering.
        """
        from ..core.database import engine

        async with AsyncSession(engine) as session:
            # Build the query based on status filter
            query = select(Task)

            if status != "all":
                if status in ["pending", "completed"]:
                    query = query.where(Task.status == status)

            # Apply limit and offset
            query = query.offset(offset).limit(limit)

            # Execute the query
            result = await session.exec(query)
            tasks = result.all()

            return tasks

    async def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a specific task by ID.
        """
        from ..core.database import engine

        async with AsyncSession(engine) as session:
            query = select(Task).where(Task.id == task_id)
            result = await session.exec(query)
            task = result.first()
            return task

    async def complete_task(self, task_id: int) -> Task:
        """
        Mark a task as completed.
        """
        # Get the task
        task = await self.get_task(task_id)

        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        # Update the task status and completion time
        task.status = "completed"
        task.completed_at = datetime.utcnow()

        from ..core.database import engine
        async with AsyncSession(engine) as session:
            # Commit the changes
            session.add(task)
            await session.commit()
            await session.refresh(task)

            return task

    async def update_task(self, task_id: int, title: str = None, description: str = None) -> Task:
        """
        Update a task's title or description.
        """
        # Get the task
        task = await self.get_task(task_id)

        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        # Update the fields if provided
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        from ..core.database import engine
        async with AsyncSession(engine) as session:
            # Commit the changes
            session.add(task)
            await session.commit()
            await session.refresh(task)

            return task

    async def delete_task(self, task_id: int) -> bool:
        """
        Delete a task permanently.
        """
        # Get the task
        task = await self.get_task(task_id)

        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        from ..core.database import engine
        async with AsyncSession(engine) as session:
            # Delete the task
            await session.delete(task)
            await session.commit()

            return True