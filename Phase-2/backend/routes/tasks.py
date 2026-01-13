from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List

router = APIRouter()


@router.get("/")
def get_tasks(
    status_filter: str = Query("all", description="Filter tasks by status (all, pending, completed)"),
    sort: str = Query("created", description="Sort tasks by field (created, title)"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of tasks per page"),
    current_user = Depends(lambda: None),
    session: Session = Depends(lambda: None)
):
    # Import everything inside the function to avoid early initialization
    try:
        from ..dependencies.database import get_db_session
        from ..models import Task, User
        from ..schemas.tasks import TaskResponse
        from ..schemas.auth import UserResponse
        from ..utils.validation import validate_task_title, validate_task_description
        from ..dependencies.auth import get_current_active_user
        from ..services.task_service import get_tasks as get_tasks_service
    except (ImportError, ValueError):
        from dependencies.database import get_db_session
        from models import Task, User
        from schemas.tasks import TaskResponse
        from schemas.auth import UserResponse
        from utils.validation import validate_task_title, validate_task_description
        from dependencies.auth import get_current_active_user
        from services.task_service import get_tasks as get_tasks_service

    tasks = get_tasks_service(session, current_user.id, status_filter, sort, page, limit)
    return tasks


@router.post("/")
def create_task(task, current_user = Depends(lambda: None), session: Session = Depends(lambda: None)):
    # Import everything inside the function to avoid early initialization
    try:
        from ..dependencies.database import get_db_session
        from ..models import Task, User
        from ..schemas.tasks import TaskCreate, TaskResponse
        from ..schemas.auth import UserResponse
        from ..utils.validation import validate_task_title, validate_task_description
        from ..dependencies.auth import get_current_active_user
        from ..services.task_service import create_task as create_task_service
    except (ImportError, ValueError):
        from dependencies.database import get_db_session
        from models import Task, User
        from schemas.tasks import TaskCreate, TaskResponse
        from schemas.auth import UserResponse
        from utils.validation import validate_task_title, validate_task_description
        from dependencies.auth import get_current_active_user
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


@router.get("/{task_id}")
def get_task(task_id: int, current_user = Depends(lambda: None), session: Session = Depends(lambda: None)):
    # Import everything inside the function to avoid early initialization
    try:
        from ..dependencies.database import get_db_session
        from ..models import Task, User
        from ..schemas.tasks import TaskResponse
        from ..schemas.auth import UserResponse
        from ..utils.validation import validate_task_title, validate_task_description
        from ..dependencies.auth import get_current_active_user
        from ..services.task_service import get_task_by_id
    except (ImportError, ValueError):
        from dependencies.database import get_db_session
        from models import Task, User
        from schemas.tasks import TaskResponse
        from schemas.auth import UserResponse
        from utils.validation import validate_task_title, validate_task_description
        from dependencies.auth import get_current_active_user
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


@router.put("/{task_id}")
def update_task(task_id: int, task_update, current_user = Depends(lambda: None), session: Session = Depends(lambda: None)):
    # Import everything inside the function to avoid early initialization
    try:
        from ..dependencies.database import get_db_session
        from ..models import Task, User
        from ..schemas.tasks import TaskUpdate, TaskResponse
        from ..schemas.auth import UserResponse
        from ..utils.validation import validate_task_title, validate_task_description
        from ..dependencies.auth import get_current_active_user
        from ..services.task_service import update_task
    except (ImportError, ValueError):
        from dependencies.database import get_db_session
        from models import Task, User
        from schemas.tasks import TaskUpdate, TaskResponse
        from schemas.auth import UserResponse
        from utils.validation import validate_task_title, validate_task_description
        from dependencies.auth import get_current_active_user
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
def delete_task(task_id: int, current_user = Depends(lambda: None), session: Session = Depends(lambda: None)):
    # Import everything inside the function to avoid early initialization
    try:
        from ..dependencies.database import get_db_session
        from ..models import Task, User
        from ..schemas.auth import UserResponse
        from ..dependencies.auth import get_current_active_user
        from ..services.task_service import delete_task
    except (ImportError, ValueError):
        from dependencies.database import get_db_session
        from models import Task, User
        from schemas.auth import UserResponse
        from dependencies.auth import get_current_active_user
        from services.task_service import delete_task

    success = delete_task(session, task_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {"success": True}


@router.patch("/{task_id}/complete")
def toggle_task_completion(task_id: int, completion_data, current_user = Depends(lambda: None), session: Session = Depends(lambda: None)):
    # Import everything inside the function to avoid early initialization
    try:
        from ..dependencies.database import get_db_session
        from ..models import Task, User
        from ..schemas.tasks import TaskToggleComplete, TaskResponse
        from ..schemas.auth import UserResponse
        from ..dependencies.auth import get_current_active_user
        from ..services.task_service import toggle_task_completion
    except (ImportError, ValueError):
        from dependencies.database import get_db_session
        from models import Task, User
        from schemas.tasks import TaskToggleComplete, TaskResponse
        from schemas.auth import UserResponse
        from dependencies.auth import get_current_active_user
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


# Update response models after imports are resolved
try:
    from ..schemas.tasks import TaskCreate, TaskUpdate, TaskResponse, TaskToggleComplete
    from ..schemas.auth import UserResponse
    from ..dependencies.database import get_db_session
    from ..dependencies.auth import get_current_active_user

    # Apply proper type annotations
    get_tasks.__annotations__ = {
        'status_filter': str,
        'sort': str,
        'page': int,
        'limit': int,
        'current_user': UserResponse,
        'session': Session,
        'return': List[TaskResponse]
    }

    create_task.__annotations__ = {
        'task': TaskCreate,
        'current_user': UserResponse,
        'session': Session,
        'return': TaskResponse
    }

    get_task.__annotations__ = {
        'task_id': int,
        'current_user': UserResponse,
        'session': Session,
        'return': TaskResponse
    }

    update_task.__annotations__ = {
        'task_id': int,
        'task_update': TaskUpdate,
        'current_user': UserResponse,
        'session': Session,
        'return': TaskResponse
    }

    delete_task.__annotations__ = {
        'task_id': int,
        'current_user': UserResponse,
        'session': Session,
        'return': dict
    }

    toggle_task_completion.__annotations__ = {
        'task_id': int,
        'completion_data': TaskToggleComplete,
        'current_user': UserResponse,
        'session': Session,
        'return': TaskResponse
    }

    # Update response models for routes
    for route in router.routes:
        if route.path == "/":
            if "POST" in route.methods:
                route.response_model = TaskResponse
            elif "GET" in route.methods:
                route.response_model = List[TaskResponse]
        elif "/{task_id}" in route.path and "GET" in route.methods:
            route.response_model = TaskResponse
        elif "/{task_id}" in route.path and "PUT" in route.methods:
            route.response_model = TaskResponse
        elif "/{task_id}" in route.path and "PATCH" in route.path:
            route.response_model = TaskResponse

except:
    # If type annotation fails, continue without it
    pass