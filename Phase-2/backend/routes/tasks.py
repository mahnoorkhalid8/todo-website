from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlmodel import Session
from typing import List

# Import schemas at module level for proper type hints
import sys
import os

# Add the backend directory to the path to handle different import scenarios
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from ..schemas.tasks import TaskCreate, TaskUpdate, TaskResponse, TaskToggleComplete
    from ..schemas.auth import UserResponse
    from ..dependencies.auth import get_current_active_user
    from ..dependencies.database import get_db_session
except (ImportError, ValueError):
    try:
        from schemas.tasks import TaskCreate, TaskUpdate, TaskResponse, TaskToggleComplete
        from schemas.auth import UserResponse
        from dependencies.auth import get_current_active_user
        from dependencies.database import get_db_session
    except ImportError:
        print("Warning: Could not import task dependencies")

        # Define placeholder classes for graceful degradation
        from pydantic import BaseModel
        from typing import Optional

        class TaskCreate(BaseModel):
            title: str
            description: Optional[str] = None

        class TaskUpdate(BaseModel):
            title: Optional[str] = None
            description: Optional[str] = None

        class TaskResponse(BaseModel):
            id: int
            title: str
            description: Optional[str] = None
            completed: bool = False

        class TaskToggleComplete(BaseModel):
            completed: bool

        class UserResponse(BaseModel):
            id: str
            email: str
            name: str

router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    status_filter: str = Query("all", description="Filter tasks by status (all, pending, completed)"),
    sort: str = Query("created", description="Sort tasks by field (created, title)"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of tasks per page"),
    current_user: UserResponse = Depends(get_current_active_user),
    session: Session = Depends(get_db_session)
):
    # Import everything inside the function to avoid early initialization
    try:
        from ..models import Task, User
        from ..utils.validation import validate_task_title, validate_task_description
        from ..services.task_service import get_tasks as get_tasks_service
    except (ImportError, ValueError):
        from models import Task, User
        from utils.validation import validate_task_title, validate_task_description
        from services.task_service import get_tasks as get_tasks_service

    # The authentication dependency is already handled by get_current_active_user
    tasks = get_tasks_service(session, current_user.id, status_filter, sort, page, limit)
    return tasks


@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate = Body(...), current_user: UserResponse = Depends(get_current_active_user), session: Session = Depends(get_db_session)):
    # Import everything inside the function to avoid early initialization
    try:
        from ..models import Task, User
        from ..schemas.tasks import TaskResponse
        from ..schemas.auth import UserResponse
        from ..utils.validation import validate_task_title, validate_task_description
        from ..services.task_service import create_task as create_task_service
    except (ImportError, ValueError):
        from models import Task, User
        from schemas.tasks import TaskResponse
        from schemas.auth import UserResponse
        from utils.validation import validate_task_title, validate_task_description
        from services.task_service import create_task as create_task_service

    try:
        # Create new task using the service
        db_task = create_task_service(session, current_user.id, task.title, task.description, task.due_date)

        # Ensure all attributes are loaded before session closes
        # Access all attributes that will be needed for serialization
        _ = db_task.id, db_task.title, db_task.description, db_task.completed, db_task.user_id, db_task.created_at, db_task.updated_at, db_task.due_date

        return db_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, current_user: UserResponse = Depends(get_current_active_user), session: Session = Depends(get_db_session)):
    # Import everything inside the function to avoid early initialization
    try:
        from ..models import Task, User
        from ..schemas.tasks import TaskResponse
        from ..utils.validation import validate_task_title, validate_task_description
        from ..services.task_service import get_task_by_id
    except (ImportError, ValueError):
        from models import Task, User
        from schemas.tasks import TaskResponse
        from utils.validation import validate_task_title, validate_task_description
        from services.task_service import get_task_by_id

    task = get_task_by_id(session, task_id, current_user.id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Ensure all attributes are loaded before session closes
    # Access all attributes that will be needed for serialization
    _ = task.id, task.title, task.description, task.completed, task.user_id, task.created_at, task.updated_at, task.due_date

    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate = Body(...), current_user: UserResponse = Depends(get_current_active_user), session: Session = Depends(get_db_session)):
    # Import everything inside the function to avoid early initialization
    try:
        from ..models import Task, User
        from ..schemas.tasks import TaskResponse
        from ..utils.validation import validate_task_title, validate_task_description
        from ..services.task_service import update_task
    except (ImportError, ValueError):
        from models import Task, User
        from schemas.tasks import TaskResponse
        from utils.validation import validate_task_title, validate_task_description
        from services.task_service import update_task

    try:
        updated_task = update_task(session, task_id, current_user.id, task_update.title, task_update.description, task_update.due_date)

        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Ensure all attributes are loaded before session closes
        # Access all attributes that will be needed for serialization
        _ = updated_task.id, updated_task.title, updated_task.description, updated_task.completed, updated_task.user_id, updated_task.created_at, updated_task.updated_at, updated_task.due_date

        return updated_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{task_id}")
def delete_task(task_id: int, current_user: UserResponse = Depends(get_current_active_user), session: Session = Depends(get_db_session)):
    # Import everything inside the function to avoid early initialization
    try:
        from ..models import Task, User
        from ..schemas.auth import UserResponse
        from ..services.task_service import delete_task
    except (ImportError, ValueError):
        from models import Task, User
        from schemas.auth import UserResponse
        from services.task_service import delete_task

    success = delete_task(session, task_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {"success": True}


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def toggle_task_completion(task_id: int, completion_data: TaskToggleComplete = Body(...), current_user: UserResponse = Depends(get_current_active_user), session: Session = Depends(get_db_session)):
    # Import everything inside the function to avoid early initialization
    try:
        from ..models import Task, User
        from ..schemas.tasks import TaskResponse
        from ..services.task_service import toggle_task_completion
    except (ImportError, ValueError):
        from models import Task, User
        from schemas.tasks import TaskResponse
        from services.task_service import toggle_task_completion

    updated_task = toggle_task_completion(session, task_id, current_user.id, completion_data.completed)

    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Ensure all attributes are loaded before session closes
    # Access all attributes that will be needed for serialization
    _ = updated_task.id, updated_task.title, updated_task.description, updated_task.completed, updated_task.user_id, updated_task.created_at, updated_task.updated_at, updated_task.due_date

    return updated_task


                                                                                                                                                                                                                                                                                                                                     