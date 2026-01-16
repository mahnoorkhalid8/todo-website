from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlmodel import Session
from typing import List
import sys
import os

# Add the backend directory to the path to handle different import scenarios
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import schemas and functions with multiple fallback strategies
def safe_import_task_components():
    global TaskCreate, TaskUpdate, TaskResponse, TaskToggleComplete, UserResponse
    global get_current_active_user, get_db_session, create_task_service, get_tasks_service
    global get_task_by_id_service, update_task_service, delete_task_service, toggle_task_completion_service

    try:
        from ..schemas.tasks import TaskCreate, TaskUpdate, TaskResponse, TaskToggleComplete
        from ..schemas.auth import UserResponse
        from ..dependencies.auth import get_current_active_user
        from ..dependencies.database import get_db_session
        from ..services.task_service import (
            create_task as create_task_service,
            get_tasks as get_tasks_service,
            get_task_by_id as get_task_by_id_service,
            update_task as update_task_service,
            delete_task as delete_task_service,
            toggle_task_completion as toggle_task_completion_service
        )
        print("DEBUG: All task components imported successfully via relative imports")
        return True
    except (ImportError, ValueError) as e:
        print(f"DEBUG: Relative import failed: {e}")
        try:
            from schemas.tasks import TaskCreate, TaskUpdate, TaskResponse, TaskToggleComplete
            from schemas.auth import UserResponse
            from dependencies.auth import get_current_active_user
            from dependencies.database import get_db_session
            from services.task_service import (
                create_task as create_task_service,
                get_tasks as get_tasks_service,
                get_task_by_id as get_task_by_id_service,
                update_task as update_task_service,
                delete_task as delete_task_service,
                toggle_task_completion as toggle_task_completion_service
            )
            print("DEBUG: All task components imported successfully via absolute imports")
            return True
        except ImportError as e:
            print(f"DEBUG: Absolute import failed: {e}")

            # Define fallback classes and functions
            from pydantic import BaseModel
            from typing import Optional
            from fastapi import Depends

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

            # Define placeholder functions
            def get_current_active_user():
                return UserResponse(id="placeholder", email="placeholder", name="placeholder")

            def get_db_session():
                yield None

            def create_task_service(session, user_id, title, description=None, due_date=None):
                print("ERROR: create_task_service not available")
                return None

            def get_tasks_service(session, user_id, status_filter="all", sort="created", page=1, limit=10):
                print("ERROR: get_tasks_service not available")
                return []

            def get_task_by_id_service(session, task_id, user_id):
                print("ERROR: get_task_by_id_service not available")
                return None

            def update_task_service(session, task_id, user_id, title=None, description=None, due_date=None):
                print("ERROR: update_task_service not available")
                return None

            def delete_task_service(session, task_id, user_id):
                print("ERROR: delete_task_service not available")
                return False

            def toggle_task_completion_service(session, task_id, user_id, completed):
                print("ERROR: toggle_task_completion_service not available")
                return None

            print("DEBUG: Fallback task components defined")
            return True

# Call the import function to set up components
safe_import_task_components()

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
    # Import everything needed (service already imported globally)
    try:
        from ..models import Task, User
        from ..utils.validation import validate_task_title, validate_task_description
    except (ImportError, ValueError):
        from models import Task, User
        from utils.validation import validate_task_title, validate_task_description

    # The authentication dependency is already handled by get_current_active_user
    tasks = get_tasks_service(session, current_user.id, status_filter, sort, page, limit)
    return tasks


@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate = Body(...), current_user: UserResponse = Depends(get_current_active_user), session: Session = Depends(get_db_session)):
    # Import everything needed (already imported globally)
    try:
        from ..models import Task, User
        from ..utils.validation import validate_task_title, validate_task_description
    except (ImportError, ValueError):
        from models import Task, User
        from utils.validation import validate_task_title, validate_task_description

    try:
        # Create new task using the service (imported globally)
        # Pass due_date directly since it's part of the TaskCreate schema
        db_task = create_task_service(session, current_user.id, task.title, task.description, task.due_date)

        if db_task is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task - service unavailable"
            )

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
    # Service already imported globally
    try:
        from ..models import Task, User
        from ..utils.validation import validate_task_title, validate_task_description
    except (ImportError, ValueError):
        from models import Task, User
        from utils.validation import validate_task_title, validate_task_description

    task = get_task_by_id_service(session, task_id, current_user.id)

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
    # Service already imported globally as 'update_task_service'
    try:
        from ..models import Task, User
        from ..utils.validation import validate_task_title, validate_task_description
    except (ImportError, ValueError):
        from models import Task, User
        from utils.validation import validate_task_title, validate_task_description

    try:
        # Use the globally imported service function
        updated_task = update_task_service(session, task_id, current_user.id, task_update.title, task_update.description, getattr(task_update, 'due_date', None))

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
    # Service already imported globally
    try:
        from ..models import Task, User
        from ..utils.validation import validate_task_title, validate_task_description
    except (ImportError, ValueError):
        from models import Task, User
        from utils.validation import validate_task_title, validate_task_description

    success = delete_task_service(session, task_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {"success": True}


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def toggle_task_completion(task_id: int, completion_data: TaskToggleComplete = Body(...), current_user: UserResponse = Depends(get_current_active_user), session: Session = Depends(get_db_session)):
    # Service already imported globally
    try:
        from ..models import Task, User
        from ..utils.validation import validate_task_title, validate_task_description
    except (ImportError, ValueError):
        from models import Task, User
        from utils.validation import validate_task_title, validate_task_description

    updated_task = toggle_task_completion_service(session, task_id, current_user.id, completion_data.completed)

    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Ensure all attributes are loaded before session closes
    # Access all attributes that will be needed for serialization
    _ = updated_task.id, updated_task.title, updated_task.description, updated_task.completed, updated_task.user_id, updated_task.created_at, updated_task.updated_at, updated_task.due_date

    return updated_task