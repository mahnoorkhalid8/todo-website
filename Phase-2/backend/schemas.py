"""
Pydantic schemas for request/response validation in the Todo application.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TaskBase(BaseModel):
    """
    Base schema for Task with common fields.
    """
    title: str
    description: Optional[str] = None
    completed: bool = False


class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    """
    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskUpdateStatus(BaseModel):
    """
    Schema for updating task completion status only.
    """
    completed: bool


class TaskResponse(TaskBase):
    """
    Schema for reading a task with additional fields.
    """
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """
    Schema for returning a list of tasks.
    """
    tasks: List[TaskResponse]
    total: int