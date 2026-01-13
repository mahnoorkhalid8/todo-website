
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime


def create_task(session: Session, user_id: str, title: str, description: Optional[str] = None, due_date: Optional[datetime] = None):
    """
    Create a new task for the user
    """
    # Import inside the function to avoid early initialization
    try:
        # Try relative imports first (works when running as a package)
        from ..models import Task, User
        from ..utils.validation import validate_task_title, validate_task_description
    except (ImportError, ValueError):
        # Fall back to absolute imports (works when running directly)
        from models import Task, User
        from utils.validation import validate_task_title, validate_task_description

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
    # Refresh to load the task with its ID after commit
    session.refresh(db_task)

    # Ensure all required fields are loaded before session closes
    # Access all attributes that will be needed for serialization
    _ = db_task.id, db_task.title, db_task.description, db_task.completed, db_task.user_id, db_task.created_at, db_task.updated_at, db_task.due_date

    return db_task


def get_tasks(session: Session, user_id: str, status: str = "all", sort: str = "created",
              page: int = 1, limit: int = 10):
    """
    Get tasks for a user with filtering and pagination
    """
    # Import inside the function to avoid early initialization
    try:
        # Try relative imports first (works when running as a package)
        from ..models import Task, User
    except (ImportError, ValueError):
        # Fall back to absolute imports (works when running directly)
        from models import Task, User

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

    # Ensure all required fields are loaded before session closes
    # Access all attributes that will be needed for serialization
    for task in tasks:
        _ = task.id, task.title, task.description, task.completed, task.user_id, task.created_at, task.updated_at, task.due_date

    return tasks


def get_task_by_id(session: Session, task_id: int, user_id: str):
    """
    Get a specific task by ID for the user
    """
    # Import inside the function to avoid early initialization
    try:
        # Try relative imports first (works when running as a package)
        from ..models import Task, User
    except (ImportError, ValueError):
        # Fall back to absolute imports (works when running directly)
        from models import Task, User

    task = session.get(Task, task_id)
    if task and task.user_id == user_id:
        # Ensure all required fields are loaded before session closes
        # Access all attributes that will be needed for serialization
        _ = task.id, task.title, task.description, task.completed, task.user_id, task.created_at, task.updated_at, task.due_date
        return task
    return None


def update_task(session: Session, task_id: int, user_id: str, title: Optional[str] = None,
                description: Optional[str] = None, due_date: Optional[datetime] = None):
    """
    Update a task for the user
    """
    # Import inside the function to avoid early initialization
    try:
        # Try relative imports first (works when running as a package)
        from ..models import Task, User
        from ..utils.validation import validate_task_title, validate_task_description
    except (ImportError, ValueError):
        # Fall back to absolute imports (works when running directly)
        from models import Task, User
        from utils.validation import validate_task_title, validate_task_description

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

    # Ensure all required fields are loaded before session closes
    # Access all attributes that will be needed for serialization
    _ = task.id, task.title, task.description, task.completed, task.user_id, task.created_at, task.updated_at, task.due_date

    return task


def toggle_task_completion(session: Session, task_id: int, user_id: str, completed: bool):
    """
    Toggle task completion status
    """
    # Import inside the function to avoid early initialization
    try:
        # Try relative imports first (works when running as a package)
        from ..models import Task, User
    except (ImportError, ValueError):
        # Fall back to absolute imports (works when running directly)
        from models import Task, User

    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        return None

    task.completed = completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    # Ensure all required fields are loaded before session closes
    # Access all attributes that will be needed for serialization
    _ = task.id, task.title, task.description, task.completed, task.user_id, task.created_at, task.updated_at, task.due_date

    return task


def delete_task(session: Session, task_id: int, user_id: str) -> bool:
    """
    Delete a task for the user
    """
    # Import inside the function to avoid early initialization
    try:
        # Try relative imports first (works when running as a package)
        from ..models import Task, User
    except (ImportError, ValueError):
        # Fall back to absolute imports (works when running directly)
        from models import Task, User

    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        return False

    session.delete(task)
    session.commit()

    return True


def get_user_task_count(session: Session, user_id: str, status: str = "all"):
    """
    Get count of tasks for a user with optional status filter
    """
    # Import inside the function to avoid early initialization
    try:
        # Try relative imports first (works when running as a package)
        from ..models import Task, User
    except (ImportError, ValueError):
        # Fall back to absolute imports (works when running directly)
        from models import Task, User

    query = select(Task).where(Task.user_id == user_id)

    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    return session.exec(query).count()


# Apply type annotations after imports are resolved
try:
    from ..models import Task, User
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        # Only for type checking purposes
        def create_task(session: Session, user_id: str, title: str, description: Optional[str] = None, due_date: Optional[datetime] = None) -> Task:
            pass

        def get_tasks(session: Session, user_id: str, status: str = "all", sort: str = "created",
                      page: int = 1, limit: int = 10) -> List[Task]:
            pass

        def get_task_by_id(session: Session, task_id: int, user_id: str) -> Task | None:
            pass

        def update_task(session: Session, task_id: int, user_id: str, title: Optional[str] = None,
                        description: Optional[str] = None, due_date: Optional[datetime] = None) -> Task | None:
            pass

        def toggle_task_completion(session: Session, task_id: int, user_id: str, completed: bool) -> Task | None:
            pass

        def delete_task(session: Session, task_id: int, user_id: str) -> bool:
            pass

        def get_user_task_count(session: Session, user_id: str, status: str = "all") -> int:
            pass
except:
    pass