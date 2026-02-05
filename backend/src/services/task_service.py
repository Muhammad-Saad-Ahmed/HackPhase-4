"""
Business logic for task operations.
"""
from sqlmodel import Session, select
from typing import List, Optional
from ..models.task import Task, TaskBase
from datetime import datetime


class TaskService:
    """
    Service class for task-related business logic.
    """
    
    def __init__(self, engine):
        self.engine = engine
    
    def create_task(self, title: str, description: Optional[str] = None) -> Task:
        """
        Create a new task with the given title and optional description.
        """
        with Session(self.engine) as session:
            # Create a new task instance
            task = Task(
                title=title,
                description=description,
                status="pending",
                created_at=datetime.utcnow()
            )
            
            # Add the task to the session and commit
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return task
    
    def get_tasks(self, status: str = "all", limit: int = 50, offset: int = 0) -> List[Task]:
        """
        Retrieve a list of tasks with optional filtering.
        """
        with Session(self.engine) as session:
            # Build the query based on status filter
            query = select(Task)
            
            if status != "all":
                if status in ["pending", "completed"]:
                    query = query.where(Task.status == status)
            
            # Apply limit and offset
            query = query.offset(offset).limit(limit)
            
            # Execute the query
            tasks = session.exec(query).all()
            
            return tasks
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a specific task by ID.
        """
        with Session(self.engine) as session:
            query = select(Task).where(Task.id == task_id)
            task = session.exec(query).first()
            return task
    
    def complete_task(self, task_id: int) -> Task:
        """
        Mark a task as completed.
        """
        with Session(self.engine) as session:
            # Get the task
            task = self.get_task(task_id)
            
            if not task:
                raise ValueError(f"Task with ID {task_id} not found")
            
            # Update the task status and completion time
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            
            # Commit the changes
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return task
    
    def update_task(self, task_id: int, title: str = None, description: str = None) -> Task:
        """
        Update a task's title or description.
        """
        with Session(self.engine) as session:
            # Get the task
            task = self.get_task(task_id)
            
            if not task:
                raise ValueError(f"Task with ID {task_id} not found")
            
            # Update the fields if provided
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            
            # Commit the changes
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return task
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task permanently.
        """
        with Session(self.engine) as session:
            # Get the task
            task = self.get_task(task_id)
            
            if not task:
                raise ValueError(f"Task with ID {task_id} not found")
            
            # Delete the task
            session.delete(task)
            session.commit()
            
            return True