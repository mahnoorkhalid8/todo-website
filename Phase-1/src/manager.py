"""
Task manager for the Todo application.
Handles all CRUD operations and business logic.
"""
from datetime import datetime
from typing import Dict, List, Optional

from src.models import Task


class TaskManager:
    """
    Manages tasks in memory with CRUD operations.
    """
    def __init__(self) -> None:
        """Initialize the task manager with empty storage."""
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def _get_next_id(self) -> int:
        """
        Generate the next unique ID for a task.

        Returns:
            The next unique ID
        """
        current_id = self._next_id
        self._next_id += 1
        return current_id

    def add_task(self, title: str, description: str = "") -> Task:
        """
        Add a new task to the manager.

        Args:
            title: Title of the task
            description: Description of the task (optional)

        Returns:
            The created Task object
        """
        task_id = self._get_next_id()
        task = Task(
            id=task_id,
            title=title,
            description=description,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._tasks[task_id] = task
        return task

    def list_tasks(self) -> List[Task]:
        """
        Get all tasks.

        Returns:
            List of all Task objects
        """
        return list(self._tasks.values())

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Get a specific task by ID.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task object if found, None otherwise
        """
        return self._tasks.get(task_id)

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Optional[Task]:
        """
        Update an existing task.

        Args:
            task_id: ID of the task to update
            title: New title for the task (optional)
            description: New description for the task (optional)

        Returns:
            Updated Task object if successful, None if task doesn't exist
        """
        task = self.get_task(task_id)
        if task is None:
            return None

        task.update(title=title, description=description)
        return task

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if task was deleted, False if task doesn't exist
        """
        if task_id not in self._tasks:
            return False

        del self._tasks[task_id]
        return True

    def toggle_task_status(self, task_id: int) -> Optional[Task]:
        """
        Toggle the completion status of a task.

        Args:
            task_id: ID of the task to toggle

        Returns:
            Updated Task object if successful, None if task doesn't exist
        """
        task = self.get_task(task_id)
        if task is None:
            return None

        task.completed = not task.completed
        task.updated_at = datetime.now()
        return task