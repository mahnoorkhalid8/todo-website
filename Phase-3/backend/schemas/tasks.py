from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskToggleComplete(BaseModel):
    completed: bool


class TaskInDB(TaskBase):
    id: int
    user_id: str
    completed: bool
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskResponse(TaskInDB):
    pass


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    pagination: dict


class TaskFilter(BaseModel):
    status: Optional[str] = "all"  # all, pending, completed
    sort: Optional[str] = "created"  # created, title, due_date
    page: Optional[int] = 1
    limit: Optional[int] = 10