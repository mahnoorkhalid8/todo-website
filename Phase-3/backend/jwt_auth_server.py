from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
from typing import Union

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Configuration
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET") or "default_secret_key_for_development"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = timedelta(hours=24)  # 24 hours

# Models for request/response
class UserLogin(BaseModel):
    email: str
    password: str

class UserSignup(BaseModel):
    email: str
    password: str
    name: str

class Task(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# Mock database - in memory storage
users_db = {}
tasks_db = {}

# JWT Utility Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + JWT_EXPIRATION_DELTA
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = None):
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    return verify_token(token)

# Authentication endpoints
@app.post("/api/auth/login")
def login(user_credentials: UserLogin):
    # Mock user validation - in real app, check against database
    user_id = f"mock_user_{hash(user_credentials.email) % 10000}"
    token = create_access_token(data={"sub": user_id, "email": user_credentials.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": user_credentials.email
        }
    }

@app.post("/api/auth/signup")
def signup(user_data: UserSignup):
    # Mock user creation - in real app, create in database
    user_id = f"mock_user_{hash(user_data.email) % 10000}"
    token = create_access_token(data={"sub": user_id, "email": user_data.email})

    # Store user in mock database
    users_db[user_id] = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name
        }
    }

# Task endpoints with user isolation
@app.get("/api/{user_id}/tasks")
def get_tasks(user_id: str, current_user: str = Depends(get_current_user)):
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's tasks")

    # Get tasks for this user from mock database
    user_tasks = tasks_db.get(user_id, [])
    return {"tasks": user_tasks}

@app.post("/api/{user_id}/tasks")
def create_task(user_id: str, task: TaskCreate, current_user: str = Depends(get_current_user)):
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's tasks")

    # Create new task in mock database
    task_id = len(tasks_db.get(user_id, [])) + 1
    new_task = Task(
        id=task_id,
        title=task.title,
        description=task.description,
        completed=False,
        created_at=datetime.utcnow().isoformat()
    )

    if user_id not in tasks_db:
        tasks_db[user_id] = []
    tasks_db[user_id].append(new_task)

    return new_task

@app.get("/api/{user_id}/tasks/{task_id}")
def get_task(user_id: str, task_id: int, current_user: str = Depends(get_current_user)):
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's tasks")

    user_tasks = tasks_db.get(user_id, [])
    for task in user_tasks:
        if task.id == task_id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/api/{user_id}/tasks/{task_id}")
def update_task(user_id: str, task_id: int, task_update: TaskUpdate, current_user: str = Depends(get_current_user)):
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's tasks")

    user_tasks = tasks_db.get(user_id, [])
    for i, task in enumerate(user_tasks):
        if task.id == task_id:
            updated_task = task.copy(update=task_update.dict(exclude_unset=True))
            user_tasks[i] = updated_task
            return updated_task

    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/api/{user_id}/tasks/{task_id}")
def delete_task(user_id: str, task_id: int, current_user: str = Depends(get_current_user)):
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's tasks")

    user_tasks = tasks_db.get(user_id, [])
    for i, task in enumerate(user_tasks):
        if task.id == task_id:
            deleted_task = user_tasks.pop(i)
            return {"message": "Task deleted successfully", "task": deleted_task}

    raise HTTPException(status_code=404, detail="Task not found")

@app.patch("/api/{user_id}/tasks/{task_id}/complete")
def toggle_task_completion(user_id: str, task_id: int, current_user: str = Depends(get_current_user)):
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's tasks")

    user_tasks = tasks_db.get(user_id, [])
    for i, task in enumerate(user_tasks):
        if task.id == task_id:
            task.completed = not task.completed
            return task

    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/")
def read_root():
    return {"message": "Todo API with JWT authentication is running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running with JWT authentication"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)