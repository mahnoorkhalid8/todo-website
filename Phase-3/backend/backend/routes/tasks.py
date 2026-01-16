from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List
# Handle imports for both local development and Hugging Face deployment
try:
    # Try relative imports first (works when running as a package)
    from ..dependencies.database import get_db_session
    from ..models import Task, User
    from ..schemas.tasks import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, TaskToggleComplete, TaskFilter
    from ..schemas.auth import UserResponse
    from ..utils.validation import validate_task_title, validate_task_description
    from ..dependencies.auth import get_current_active_user
    from ..services.task_service import get_tasks as get_tasks_service, create_task as create_task_service
except (ImportError, ValueError):
    # Fall back to absolute imports (works when running directly)
    from dependencies.database import get_db_session
    from models import Task, User
    from schemas.tasks import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, TaskToggleComplete, TaskFilter
    from schemas.auth import UserResponse
    from utils.validation import validate_task_title, validate_task_description
    from dependencies.auth import get_current_active_user
    from services.task_service import get_tasks as get_tasks_service, create_task as create_task_service


router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    status_filter: str = Query("all", description="Filter tasks by status (all, pending, completed)"),
    sort: str = Query("created", description="Sort tasks by field (created, title)"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of tasks per page"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db_session)
):
    tasks = get_tasks_service(session, current_user.id, status_filter, sort, page, limit)
    return tasks


@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db_session)
):
    try:
        # Create new task using the service
        db_task = create_task_service(session, current_user.id, task.title, task.description, task.due_date)
        return db_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db_session)
):
    from services.task_service import get_task_by_id

    task = get_task_by_id(session, task_id, current_user.id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db_session)
):
    from services.task_service import update_task

    try:
        updated_task = update_task(session, task_id, current_user.id, task_update.title, task_update.description, task_update.due_date)

        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return updated_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db_session)
):
    from services.task_service import delete_task

    success = delete_task(session, task_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {"success": True}


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def toggle_task_completion(
    task_id: int,
    completion_data: TaskToggleComplete,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db_session)
):
    from services.task_service import toggle_task_completion

    updated_task = toggle_task_completion(session, task_id, current_user.id, completion_data.completed)

    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return updated_task