"""
MCP (Model Context Protocol) Server Implementation for AI Chatbot

This module implements an MCP server that exposes Todo operations as tools
that can be called by AI agents. The server follows the MCP specification
and provides standardized interfaces for task management operations.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import secrets
from sqlmodel import Session, select
from fastapi import HTTPException, status

import sys
import os
# Add the backend directory to the path to resolve absolute imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from models import Task, Conversation, Message
from services.task_service import (
    create_task as service_create_task,
    get_tasks as service_get_tasks,
    get_task_by_id as service_get_task_by_id,
    update_task as service_update_task,
    toggle_task_completion as service_toggle_task_completion,
    delete_task as service_delete_task
)
from db import get_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result returned by MCP tools"""
    task_id: Optional[int] = None
    status: str = ""
    title: str = ""
    message: str = ""


class MCPServer:
    """
    MCP Server that exposes Todo operations as callable tools
    """

    def __init__(self, db_session: Session, user_id: str):
        self.db_session = db_session
        self.user_id = user_id
        self.tools = {
            "add_task": self.add_task,
            "list_tasks": self.list_tasks,
            "complete_task": self.complete_task,
            "delete_task": self.delete_task,
            "update_task": self.update_task,
        }

    def validate_user_access(self, task_id: int) -> bool:
        """
        Validate that the user has access to the specified task
        """
        task = self.db_session.get(Task, task_id)
        return task and task.user_id == self.user_id

    def add_task(self, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new task to the user's list

        Args:
            title: Title of the task (required)
            description: Description of the task (optional)

        Returns:
            Dict with task_id, status, and title
        """
        try:
            # Validate inputs
            if not title or len(title) < 1 or len(title) > 200:
                raise ValueError("Title must be between 1 and 200 characters")

            if description and len(description) > 1000:
                raise ValueError("Description must be less than 1000 characters")

            # Create the task using the service
            task = service_create_task(
                session=self.db_session,
                user_id=self.user_id,
                title=title,
                description=description
            )

            logger.info(f"Task created: {task.id} for user {self.user_id}")

            return {
                "task_id": task.id,
                "status": "created",
                "title": task.title
            }

        except ValueError as e:
            logger.error(f"Validation error in add_task: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error in add_task: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )

    def list_tasks(self, status_filter: Optional[str] = "all") -> List[Dict[str, Any]]:
        """
        List tasks with optional filtering

        Args:
            status_filter: Filter by status ("all", "pending", "completed")

        Returns:
            List of task objects
        """
        try:
            # Validate status filter
            valid_filters = ["all", "pending", "completed"]
            if status_filter and status_filter not in valid_filters:
                status_filter = "all"

            # Get tasks using the service
            tasks = service_get_tasks(
                session=self.db_session,
                user_id=self.user_id,
                status=status_filter
            )

            # Format tasks for response
            formatted_tasks = []
            for task in tasks:
                formatted_tasks.append({
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "description": task.description,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                })

            logger.info(f"Retrieved {len(formatted_tasks)} tasks for user {self.user_id}")

            return formatted_tasks

        except Exception as e:
            logger.error(f"Error in list_tasks: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve tasks"
            )

    def complete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Mark a task as complete

        Args:
            task_id: ID of the task to complete

        Returns:
            Dict with task_id, status, and title
        """
        try:
            # Validate user access to task
            if not self.validate_user_access(task_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or access denied"
                )

            # Complete the task using the service
            task = service_toggle_task_completion(
                session=self.db_session,
                task_id=task_id,
                user_id=self.user_id,
                completed=True
            )

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )

            logger.info(f"Task completed: {task.id} for user {self.user_id}")

            return {
                "task_id": task.id,
                "status": "completed",
                "title": task.title
            }

        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Error in complete_task: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete task"
            )

    def delete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Delete a task

        Args:
            task_id: ID of the task to delete

        Returns:
            Dict with task_id, status, and title
        """
        try:
            # Validate user access to task
            if not self.validate_user_access(task_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or access denied"
                )

            # Get task for response before deletion
            task = service_get_task_by_id(
                session=self.db_session,
                task_id=task_id,
                user_id=self.user_id
            )

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )

            # Delete the task using the service
            success = service_delete_task(
                session=self.db_session,
                task_id=task_id,
                user_id=self.user_id
            )

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete task"
                )

            logger.info(f"Task deleted: {task_id} for user {self.user_id}")

            return {
                "task_id": task.id,
                "status": "deleted",
                "title": task.title
            }

        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Error in delete_task: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task"
            )

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Update task title or description

        Args:
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)

        Returns:
            Dict with task_id, status, and title
        """
        try:
            # Validate user access to task
            if not self.validate_user_access(task_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or access denied"
                )

            # Validate inputs if provided
            if title is not None:
                if len(title) < 1 or len(title) > 200:
                    raise ValueError("Title must be between 1 and 200 characters")

            if description is not None and len(description) > 1000:
                raise ValueError("Description must be less than 1000 characters")

            # Update the task using the service
            task = service_update_task(
                session=self.db_session,
                task_id=task_id,
                user_id=self.user_id,
                title=title,
                description=description
            )

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )

            logger.info(f"Task updated: {task.id} for user {self.user_id}")

            return {
                "task_id": task.id,
                "status": "updated",
                "title": task.title
            }

        except ValueError as e:
            logger.error(f"Validation error in update_task: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Error in update_task: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task"
            )

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute the specified tool with the given parameters

        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool

        Returns:
            Result of the tool execution
        """
        if tool_name not in self.tools:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tool '{tool_name}' not found"
            )

        tool_func = self.tools[tool_name]

        try:
            # Execute the tool with the provided parameters
            result = tool_func(**parameters)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            raise


import asyncio
from concurrent.futures import ThreadPoolExecutor

async def run_mcp_tool(user_id: str, tool_name: str, parameters: Dict[str, Any]) -> Any:
    """
    Execute an MCP tool with the given parameters

    Args:
        user_id: ID of the user executing the tool
        tool_name: Name of the tool to execute
        parameters: Parameters for the tool

    Returns:
        Result of the tool execution
    """
    from sqlmodel import Session

    # Import engine at module level to ensure it's available in thread
    try:
        from ..db import engine
    except ImportError:
        import sys
        import os
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        from db import engine

    def _run_tool_sync():
        # Create a completely isolated session from the engine
        session = Session(engine)

        try:
            # Create MCP server with the isolated session
            mcp_server = MCPServer(session, user_id)

            # Check if tool exists
            if tool_name not in mcp_server.tools:
                from fastapi import HTTPException
                from fastapi import status
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tool '{tool_name}' not found"
                )

            # Execute the tool function
            tool_func = mcp_server.tools[tool_name]
            result = tool_func(**parameters)
            session.commit()  # Commit any changes
            return result
        except Exception as e:
            session.rollback()  # Rollback on error
            raise
        finally:
            session.close()  # Always close the session

    # Run the synchronous function in a thread pool
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _run_tool_sync)