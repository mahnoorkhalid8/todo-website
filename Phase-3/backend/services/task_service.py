from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

# Handle imports for both local development and Hugging Face deployment
try:
    # Try relative imports first (works when running as a package)
    from ..models import Task, User
    from ..utils.validation import validate_task_title, validate_task_description
except (ImportError, ValueError):
    # Fall back to absolute imports (works when running directly)
    from models import Task, User
    from utils.validation import validate_task_title, validate_task_description


def create_task(session: Session, user_id: str, title: str, description: Optional[str] = None, due_date: Optional[datetime] = None) -> Task:
    """
    Create a new task for the user
    """
    # Validate title
    is_valid, error_msg = validate_task_title(title)
    if not is_valid:
        raise ValueError(error_msg)

    # Validate description
    if description:
        is_valid, error_msg = validate_task_description(description)
        if not is_valid:
            raise ValueError(error_msg)

    # Create new task
    db_task = Task(
        title=title,
        description=description,
        due_date=due_date,
        completed=False,
        user_id=user_id
    )

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task


def get_tasks(session: Session, user_id: str, status: str = "all", sort: str = "created",
              page: int = 1, limit: int = 10) -> List[Task]:
    """
    Get tasks for a user with filtering and pagination
    """
    query = select(Task).where(Task.user_id == user_id)

    # Apply status filter
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    # Apply sorting
    if sort == "title":
        query = query.order_by(Task.title)
    else:  # Default to created date
        query = query.order_by(Task.created_at.desc())

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    tasks = session.exec(query).all()
    return tasks


def get_task_by_id(session: Session, task_id: int, user_id: str) -> Task | None:
    """
    Get a specific task by ID for the user
    """
    task = session.get(Task, task_id)
    if task and task.user_id == user_id:
        return task
    return None


def update_task(session: Session, task_id: int, user_id: str, title: Optional[str] = None,
                description: Optional[str] = None, due_date: Optional[datetime] = None) -> Task | None:
    """
    Update a task for the user
    """
    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        return None

    # Validate title if provided
    if title is not None:
        is_valid, error_msg = validate_task_title(title)
        if not is_valid:
            raise ValueError(error_msg)

    # Validate description if provided
    if description is not None:
        is_valid, error_msg = validate_task_description(description)
        if not is_valid:
            raise ValueError(error_msg)

    # Update task
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if due_date is not None:
        task.due_date = due_date

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def toggle_task_completion(session: Session, task_id: int, user_id: str, completed: bool) -> Task | None:
    """
    Toggle task completion status
    """
    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        return None

    task.completed = completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def delete_task(session: Session, task_id: int, user_id: str) -> bool:
    """
    Delete a task for the user
    """
    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        return False

    session.delete(task)
    session.commit()

    return True


def get_user_task_count(session: Session, user_id: str, status: str = "all") -> int:
    """
    Get count of tasks for a user with optional status filter
    """
    query = select(Task).where(Task.user_id == user_id)

    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    return session.exec(query).count()