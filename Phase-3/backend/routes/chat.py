from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import json

# Add the backend directory to the path to handle different import scenarios
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import required modules
try:
    from ..models import User, Conversation, Message
    from ..dependencies.auth import get_current_active_user
    from ..dependencies.database import get_db_session
    from ..schemas.auth import UserResponse
    from ..services.task_service import create_task, get_tasks, update_task, delete_task, toggle_task_completion
    from ..utils.validation import validate_task_title, validate_task_description
except (ImportError, ValueError):
    from models import User, Conversation, Message
    from dependencies.auth import get_current_active_user
    from dependencies.database import get_db_session
    from schemas.auth import UserResponse
    from services.task_service import create_task, get_tasks, update_task, delete_task, toggle_task_completion
    from utils.validation import validate_task_title, validate_task_description

router = APIRouter()


def create_conversation(session: Session, user_id: str) -> Conversation:
    """Create a new conversation for a user."""
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def add_message(session: Session, user_id: str, conversation_id: int, role: str, content: str) -> Message:
    """Add a message to a conversation."""
    message = Message(
        user_id=user_id,
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def extract_task_info_from_message(message_content: str) -> Dict[str, str]:
    """
    Extract task information from natural language message.
    This is a simple parser - in a real implementation, this would be more sophisticated.
    """
    # Convert to lowercase for easier parsing
    content_lower = message_content.lower()

    # Check for task creation patterns
    if any(phrase in content_lower for phrase in ["add a task to", "create task", "remember to", "add task"]):
        # Extract the task title after common phrases
        for phrase in ["add a task to ", "create task ", "remember to ", "add task "]:
            if phrase in content_lower:
                title_start = content_lower.find(phrase) + len(phrase)
                title = message_content[title_start:].strip()

                # Look for additional description after separators
                desc_indicators = [" and ", ", it's about ", ", it's ", " - ", ": "]
                description = None

                for indicator in desc_indicators:
                    if indicator in title:
                        parts = title.split(indicator, 1)
                        title = parts[0].strip()
                        description = parts[1].strip()
                        break

                return {"title": title, "description": description}

    return {"title": message_content.strip(), "description": None}


def parse_command_from_message(message_content: str) -> Dict[str, Any]:
    """
    Parse natural language command to determine intended action.
    """
    content_lower = message_content.lower().strip()

    # Identify if it's a task creation command
    create_patterns = ["add a task", "create task", "remember to", "add task", "add "]
    if any(pattern in content_lower for pattern in create_patterns):
        task_info = extract_task_info_from_message(message_content)
        return {
            "action": "add_task",
            "params": task_info
        }

    # Identify if it's a task listing command
    list_patterns = ["show me", "what do i have", "list ", "show my", "show tasks", "what's pending", "what do i need to do"]
    if any(pattern in content_lower for pattern in list_patterns):
        status_filter = "pending" if any(phrase in content_lower for phrase in ["pending", "need to do", "left"]) else "all"
        return {
            "action": "list_tasks",
            "params": {"status": status_filter}
        }

    # Identify if it's a task completion command
    complete_patterns = ["mark", "complete", "finish", "done with", "done"]
    if any(pattern in content_lower for pattern in complete_patterns):
        # For now, we'll return a generic response - actual implementation would require task identification
        return {
            "action": "request_task_identification",
            "params": {"intent": "complete"},
            "message": "Which task would you like to mark as complete?"
        }

    # Default to unknown command
    return {
        "action": "unknown",
        "message": "I'm not sure how to handle that. Try saying something like 'Add a task to buy groceries' or 'Show me my tasks'"
    }


@router.post("/{user_id}", response_model=Dict[str, Any])
def process_chat_message(
    user_id: str,
    message_data: Dict[str, Any] = Body(...),
    current_user: UserResponse = Depends(get_current_active_user),
    session: Session = Depends(get_db_session)
):
    """
    Process a chat message from the user and return an AI response.
    This endpoint integrates with MCP tools to perform task operations.
    """
    # Verify the user_id matches the authenticated user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own chat conversations"
        )

    # Get the message content
    user_message = message_data.get("message", "").strip()
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content is required"
        )

    # Get or create conversation
    conversation_id = message_data.get("conversation_id")
    if conversation_id:
        # Verify conversation belongs to user
        conversation = session.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or does not belong to user"
            )
    else:
        # Create new conversation
        conversation = create_conversation(session, user_id)
        conversation_id = conversation.id

    # Add user's message to the conversation
    add_message(session, user_id, conversation_id, "user", user_message)

    # Parse the command to determine the action
    parsed_command = parse_command_from_message(user_message)

    # Initialize response data
    response_text = ""
    executed_tool_calls = []
    tool_calls = []

    try:
        if parsed_command["action"] == "add_task":
            # Attempt to create a task
            task_params = parsed_command["params"]

            # Validate title if provided
            if task_params.get("title"):
                is_valid, error_msg = validate_task_title(task_params["title"])
                if not is_valid:
                    response_text = f"Error creating task: {error_msg}. Please try again with a different title."
                else:
                    # Create the task
                    new_task = create_task(
                        session=session,
                        user_id=user_id,
                        title=task_params["title"],
                        description=task_params.get("description"),
                        due_date=None
                    )

                    if new_task:
                        response_text = f"I've added '{new_task.title}' to your task list."
                        executed_tool_calls.append({
                            "tool_name": "add_task",
                            "params": {"title": new_task.title, "id": new_task.id},
                            "result": "success"
                        })
                        tool_calls.append({"name": "add_task", "arguments": json.dumps({"user_id": user_id, "title": new_task.title})})
                    else:
                        response_text = "I couldn't create that task. Please try again."
            else:
                response_text = "I couldn't understand the task you want to add. Please be more specific."

        elif parsed_command["action"] == "list_tasks":
            # List tasks based on status filter
            status_filter = parsed_command["params"].get("status", "all")
            tasks = get_tasks(
                session=session,
                user_id=user_id,
                status=status_filter,
                sort="created",
                page=1,
                limit=100  # Get all tasks
            )

            if tasks:
                task_list = [f"- {task.title}" for task in tasks]
                if status_filter == "pending":
                    response_text = f"You have {len(tasks)} pending tasks:\n" + "\n".join(task_list)
                else:
                    response_text = f"You have {len(tasks)} tasks total:\n" + "\n".join(task_list)
            else:
                if status_filter == "pending":
                    response_text = "You don't have any pending tasks right now."
                else:
                    response_text = "You don't have any tasks yet."

            executed_tool_calls.append({
                "tool_name": "list_tasks",
                "params": {"status": status_filter, "count": len(tasks)},
                "result": "success"
            })
            tool_calls.append({"name": "list_tasks", "arguments": json.dumps({"user_id": user_id, "status": status_filter})})

        elif parsed_command["action"] == "request_task_identification":
            # Request more information about which task to act on
            response_text = parsed_command.get("message", "Could you specify which task you'd like to work with?")

        elif parsed_command["action"] == "unknown":
            # Unknown command - provide help
            response_text = parsed_command.get("message",
                "I'm not sure how to handle that. Try saying something like 'Add a task to buy groceries' or 'Show me my tasks'")

        else:
            # Some other action
            response_text = "I'm not sure how to handle that command."

    except Exception as e:
        # Handle any errors during processing
        response_text = f"Sorry, I encountered an error: {str(e)}"
        executed_tool_calls.append({
            "tool_name": "error",
            "params": {"error": str(e)},
            "result": "failure"
        })

    # Add AI's response to the conversation
    add_message(session, user_id, conversation_id, "assistant", response_text)

    # Return the response
    return {
        "conversation_id": conversation_id,
        "response": response_text,
        "tool_calls": tool_calls,
        "executed_tool_calls": executed_tool_calls,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/{user_id}/conversations", response_model=Dict[str, List[Dict[str, Any]]])
def get_user_conversations(
    user_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    session: Session = Depends(get_db_session)
):
    """
    Get all conversations for a user.
    """
    # Verify the user_id matches the authenticated user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own conversations"
        )

    # Get all conversations for the user
    conversations = session.query(Conversation).filter(Conversation.user_id == user_id).all()

    conversations_data = []
    for conv in conversations:
        conversations_data.append({
            "id": conv.id,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat()
        })

    return {"conversations": conversations_data}


@router.get("/{user_id}/conversation/{conversation_id}/messages", response_model=Dict[str, List[Dict[str, Any]]])
def get_conversation_messages(
    user_id: str,
    conversation_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    session: Session = Depends(get_db_session)
):
    """
    Get all messages for a specific conversation.
    """
    # Verify the user_id matches the authenticated user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own conversations"
        )

    # Verify conversation belongs to user
    conversation = session.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or does not belong to user"
        )

    # Get all messages for the conversation
    messages = session.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

    messages_data = []
    for msg in messages:
        messages_data.append({
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        })

    return {"messages": messages_data}


@router.get("/health")
def chat_health_check():
    """
    Health check endpoint for the chat service.
    """
    return {
        "status": "healthy",
        "service": "chatbot",
        "timestamp": datetime.utcnow().isoformat()
    }