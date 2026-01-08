"""
Task data model for the Todo application.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """
    Represents a task in the todo list.

    Attributes:
        id: Unique identifier for the task
        title: Title of the task (required)
        description: Optional description of the task
        completed: Boolean indicating if the task is completed
        created_at: Timestamp when the task was created
        updated_at: Timestamp when the task was last updated
    """
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate the task after initialization."""
        if not self.title.strip():
            raise ValueError("Task title cannot be empty")

    def update(self, title: Optional[str] = None, description: Optional[str] = None) -> None:
        """
        Update the task's title and/or description.

        Args:
            title: New title for the task (optional)
            description: New description for the task (optional)
        """
        if title is not None:
            if not title.strip():
                raise ValueError("Task title cannot be empty")
            self.title = title
        if description is not None:
            self.description = description

        self.updated_at = datetime.now()