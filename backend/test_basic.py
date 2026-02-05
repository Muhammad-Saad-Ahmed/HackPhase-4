"""
Basic test to verify the Todo MCP Tools implementation.
"""
import asyncio
from src.models.task import Task
from src.services.task_service import TaskService
from src.core.database import engine
from sqlmodel import Session, select


def test_basic_functionality():
    """
    Test basic functionality of the task service.
    """
    # Create a task service instance
    task_service = TaskService(engine=engine)
    
    # Test creating a task
    print("Creating a task...")
    task = task_service.create_task(
        title="Test task",
        description="This is a test task"
    )
    print(f"Created task: {task.title} (ID: {task.id})")
    
    # Test getting tasks
    print("\nGetting all tasks...")
    tasks = task_service.get_tasks()
    print(f"Found {len(tasks)} tasks")
    
    # Test getting a specific task
    print(f"\nGetting task with ID {task.id}...")
    retrieved_task = task_service.get_task(task.id)
    print(f"Retrieved task: {retrieved_task.title}")
    
    # Test updating a task
    print(f"\nUpdating task with ID {task.id}...")
    updated_task = task_service.update_task(
        task_id=task.id,
        title="Updated test task",
        description="This is an updated test task"
    )
    print(f"Updated task: {updated_task.title}")
    
    # Test completing a task
    print(f"\nCompleting task with ID {task.id}...")
    completed_task = task_service.complete_task(task.id)
    print(f"Completed task: {completed_task.title} (Status: {completed_task.status})")
    
    # Test completing the same task again (idempotent operation)
    print(f"\nCompleting task with ID {task.id} again (idempotent test)...")
    completed_task_again = task_service.complete_task(task.id)
    print(f"Completed task again: {completed_task_again.title} (Status: {completed_task_again.status})")
    
    # Test listing tasks with filter
    print(f"\nGetting completed tasks...")
    completed_tasks = task_service.get_tasks(status="completed")
    print(f"Found {len(completed_tasks)} completed tasks")
    
    # Test deleting a task
    print(f"\nDeleting task with ID {task.id}...")
    result = task_service.delete_task(task.id)
    print(f"Deletion result: {result}")
    
    # Verify the task is gone
    print(f"\nVerifying task with ID {task.id} is deleted...")
    deleted_task = task_service.get_task(task.id)
    print(f"Task after deletion: {deleted_task}")


if __name__ == "__main__":
    test_basic_functionality()