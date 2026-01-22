from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import json
import pytz

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


def extract_task_identifier_from_message(message_content: str) -> str:
    """
    Extract task identifier (by number or title) from message.
    Improved to handle natural language better.
    """
    content_lower = message_content.lower()
    import re

    # Look for task number (e.g., "task 1", "task 3", "number 2")
    number_match = re.search(r'(?:task|number)\s*(\d+)', content_lower)
    if number_match:
        return number_match.group(1)

    # Look for phrases like "task called 'title'", "task named 'title'", "task 'title'"
    title_match = re.search(r'(?:task|called|named)\s*[\'"]([^\'"]+)[\'"]', content_lower)
    if title_match:
        return title_match.group(1).strip()

    # Look for tasks after action words (e.g., "delete 'buy groceries'", "update 'walk dog'")
    action_match = re.search(r'(?:delete|remove|update|edit|complete|finish|mark)\s+[\'"]([^\'"]+)[\'"]', content_lower)
    if action_match:
        return action_match.group(1).strip()

    # If no specific title found, try to extract the most relevant part of the message
    # Remove common action words and return the remaining text as potential title
    common_phrases = [
        r'delete\s+', r'remove\s+', r'update\s+', r'edit\s+', r'complete\s+',
        r'finish\s+', r'mark\s+', r'as\s+complete', r'task\s+', r'called\s+',
        r'named\s+', r'the\s+', r'a\s+', r'an\s+', r'to\s+'
    ]

    extracted_title = content_lower
    for phrase in common_phrases:
        extracted_title = re.sub(phrase, '', extracted_title, flags=re.IGNORECASE)

    extracted_title = extracted_title.strip()

    # If the extracted title is still too long or doesn't make sense, return original
    if len(extracted_title) > 5 and extracted_title.count(' ') <= 4:
        return extracted_title

    return message_content.strip()


def find_task_by_identifier(session: Session, user_id: str, task_identifier: str) -> Optional[dict]:
    """
    Find a task by its identifier (number or title).
    Improved to handle partial matches and exact title matches.
    """
    try:
        task_id = int(task_identifier)
        # If identifier is a number, look for that specific task
        from models import Task
        task = session.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()

        if task:
            return {"id": task.id, "title": task.title, "completed": task.completed}
    except ValueError:
        # If identifier is not a number, search by title/content
        from models import Task

        # First, try exact match
        exact_task = session.query(Task).filter(
            Task.user_id == user_id,
            Task.title == task_identifier
        ).first()

        if exact_task:
            return {"id": exact_task.id, "title": exact_task.title, "completed": exact_task.completed}

        # Then try partial match
        tasks = session.query(Task).filter(
            Task.user_id == user_id,
            Task.title.ilike(f'%{task_identifier}%')
        ).all()

        if tasks:
            # Return the first match (in a real implementation, might want to disambiguate)
            task = tasks[0]
            return {"id": task.id, "title": task.title, "completed": task.completed}

    return None


def find_and_perform_task_operation(session: Session, user_id: str, task_identifier: str, operation: str, new_title: str = None, new_description: str = None, new_due_date: str = None) -> Dict[str, Any]:
    """
    Find a task and perform the specified operation on it.
    """
    task = find_task_by_identifier(session, user_id, task_identifier)

    if not task:
        return {"success": False, "message": f"Could not find a task matching '{task_identifier}'"}

    from models import Task
    from services.task_service import update_task, delete_task, toggle_task_completion
    from datetime import datetime

    if operation == "complete":
        # Toggle task completion
        updated_task = toggle_task_completion(session, task["id"], user_id, not task["completed"])
        if updated_task:
            status = "completed" if updated_task.completed else "incomplete"
            return {
                "success": True,
                "message": f"Task '{updated_task.title}' has been marked as {status}",
                "task": {"id": updated_task.id, "title": updated_task.title, "completed": updated_task.completed}
            }
    elif operation == "delete":
        # Delete the task
        success = delete_task(session, task["id"], user_id)
        if success:
            return {
                "success": True,
                "message": f"Task '{task['title']}' has been deleted",
                "task": {"id": task["id"], "title": task["title"]}
            }
    elif operation == "update":
        # Update the task
        title_to_use = new_title if new_title else task["title"]
        description_to_use = new_description if new_description else None

        # Convert due date string to datetime if provided
        due_date_obj = None
        if new_due_date:
            try:
                due_date_obj = datetime.fromisoformat(new_due_date.replace('Z', '+00:00'))
            except ValueError:
                # If fromisoformat fails, try parsing as YYYY-MM-DD
                try:
                    due_date_obj = datetime.strptime(new_due_date, '%Y-%m-%d')
                except ValueError:
                    # If all parsing fails, try parsing as DD-MM-YYYY or DD/MM/YYYY
                    try:
                        due_date_obj = datetime.strptime(new_due_date, '%d-%m-%Y')
                    except ValueError:
                        try:
                            due_date_obj = datetime.strptime(new_due_date, '%d/%m/%Y')
                        except ValueError:
                            # If all parsing fails, keep as None
                            due_date_obj = None

        updated_task = update_task(session, task["id"], user_id, title_to_use, description_to_use, due_date_obj)
        if updated_task:
            return {
                "success": True,
                "message": f"Task '{task['title']}' has been updated to '{updated_task.title}'",
                "task": {"id": updated_task.id, "title": updated_task.title, "description": updated_task.description, "due_date": updated_task.due_date.isoformat() if updated_task.due_date else None}
            }

    return {"success": False, "message": f"Failed to {operation} task '{task['title']}'"}


def convert_utc_to_pakistani_time(utc_datetime_str: str) -> str:
    """
    Convert UTC datetime string to Pakistani time (GMT+5) in 12-hour format with AM/PM.
    """
    try:
        # Parse the UTC datetime string
        if utc_datetime_str.endswith('Z'):
            utc_datetime = datetime.fromisoformat(utc_datetime_str.replace('Z', '+00:00'))
        else:
            utc_datetime = datetime.fromisoformat(utc_datetime_str)

        # Define UTC and Pakistan timezones
        utc_tz = pytz.UTC
        pakistan_tz = pytz.timezone('Asia/Karachi')

        # Make the datetime timezone-aware if it isn't already
        if utc_datetime.tzinfo is None:
            utc_datetime = utc_tz.localize(utc_datetime)
        else:
            utc_datetime = utc_datetime.astimezone(utc_tz)

        # Convert to Pakistan time
        pakistan_time = utc_datetime.astimezone(pakistan_tz)

        # Format to 12-hour format with AM/PM
        return pakistan_time.strftime('%Y-%m-%d %I:%M:%S %p %Z')
    except Exception as e:
        # If conversion fails, return original string with error info
        return f"{utc_datetime_str} (Timezone conversion error: {str(e)})"


def parse_command_from_message(message_content: str) -> Dict[str, Any]:
    """
    Parse natural language command to determine intended action.
    """
    import re  # Move import to beginning of function to avoid UnboundLocalError
    content_lower = message_content.lower().strip()

    # FIRST: Handle specific update patterns before any general patterns

    # Handle "add task cooking" format
    add_task_pattern = r'^add task\s+(.+)$'
    add_task_match = re.search(add_task_pattern, content_lower)
    if add_task_match:
        task_title = add_task_match.group(1).strip()
        return {
            "action": "add_task",
            "params": {
                "title": task_title,
                "description": None
            }
        }

    # Handle "add task description in task 40 Biryani" format
    add_desc_pattern = r'add task description in task (\d+)\s+(.+)$'
    add_desc_match = re.search(add_desc_pattern, content_lower)
    if add_desc_match:
        task_id = add_desc_match.group(1)
        description = add_desc_match.group(2).strip()
        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_id,
                "new_title": None,  # Don't change the title
                "new_description": description,
                "new_due_date": None
            }
        }

    # Handle "add task due date in task 40 29-01-2026" format
    add_due_date_pattern = r'add task due date in task (\d+)\s+(.+)$'
    add_due_date_match = re.search(add_due_date_pattern, content_lower)
    if add_due_date_match:
        task_id = add_due_date_match.group(1)
        due_date_str = add_due_date_match.group(2).strip()

        # Normalize date format to YYYY-MM-DD
        # Handle DD/MM/YYYY or DD-MM-YYYY format and convert to YYYY-MM-DD
        date_parts = due_date_str.split(r'[-/]')
        if len(date_parts) == 3:
            day, month, year = date_parts
            # Handle 2-digit vs 4-digit years
            if len(year) == 2:
                year = '20' + year
            if len(day) == 1:
                day = '0' + day
            if len(month) == 1:
                month = '0' + month
            due_date_str = f"{year}-{month}-{day}"
        else:
            # If the date doesn't have 3 parts, try another approach for common formats
            # Try to match DD/MM/YY or DD-MM-YY format
            import re as re_module  # Use different name to avoid conflict
            date_match = re_module.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', due_date_str)
            if date_match:
                day, month, year = date_match.groups()
                if len(year) == 2:
                    year = '20' + year
                if len(day) == 1:
                    day = '0' + day
                if len(month) == 1:
                    month = '0' + month
                due_date_str = f"{year}-{month}-{day}"

        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_id,
                "new_title": None,  # Don't change the title
                "new_description": None,  # Don't change description
                "new_due_date": due_date_str
            }
        }

    # Handle "update task title of task 40 cook dinner" format
    update_task_title_pattern = r'update task title of task (\d+)\s+(.+)$'
    update_task_title_match = re.search(update_task_title_pattern, content_lower)
    if update_task_title_match:
        task_id = update_task_title_match.group(1)
        # Extract the original title from the original message to preserve case
        original_match = re.search(r'update task title of task (\d+)\s+(.+)$', message_content, re.IGNORECASE)
        new_title = original_match.group(2).strip() if original_match else update_task_title_match.group(2).strip()
        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_id,
                "new_title": new_title,
                "new_description": None,  # Don't change description
                "new_due_date": None
            }
        }

    # Handle "update task description of task 40 Biryani for dinner" format
    update_task_description_pattern = r'update task description of task (\d+)\s+(.+)$'
    update_task_description_match = re.search(update_task_description_pattern, content_lower)
    if update_task_description_match:
        task_id = update_task_description_match.group(1)
        new_description = update_task_description_match.group(2).strip()
        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_id,
                "new_title": None,  # Don't change the title
                "new_description": new_description,
                "new_due_date": None
            }
        }

    # Handle "update task due date of task 40 02-02-2026" format
    update_task_due_date_pattern = r'update task due date of task (\d+)\s+(.+)$'
    update_task_due_date_match = re.search(update_task_due_date_pattern, content_lower)
    if update_task_due_date_match:
        task_id = update_task_due_date_match.group(1)
        due_date_str = update_task_due_date_match.group(2).strip()

        # Normalize date format to YYYY-MM-DD
        # Handle DD/MM/YYYY or DD-MM-YYYY format and convert to YYYY-MM-DD
        date_parts = due_date_str.split(r'[-/]')
        if len(date_parts) == 3:
            day, month, year = date_parts
            # Handle 2-digit vs 4-digit years
            if len(year) == 2:
                year = '20' + year
            if len(day) == 1:
                day = '0' + day
            if len(month) == 1:
                month = '0' + month
            due_date_str = f"{year}-{month}-{day}"
        else:
            # If the date doesn't have 3 parts, try another approach for common formats
            # Try to match DD/MM/YY or DD-MM-YY format
            import re as re_module  # Use different name to avoid conflict
            date_match = re_module.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', due_date_str)
            if date_match:
                day, month, year = date_match.groups()
                if len(year) == 2:
                    year = '20' + year
                if len(day) == 1:
                    day = '0' + day
                if len(month) == 1:
                    month = '0' + month
                due_date_str = f"{year}-{month}-{day}"

        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_id,
                "new_title": None,  # Don't change the title
                "new_description": None,  # Don't change description
                "new_due_date": due_date_str
            }
        }

    # Handle "update task title in task 44 cooking" format (existing pattern)
    update_task_title_pattern_alt = r'update task title in task (\d+)\s+(.+)$'
    update_task_title_match_alt = re.search(update_task_title_pattern_alt, content_lower)
    if update_task_title_match_alt:
        task_id = update_task_title_match_alt.group(1)
        # Extract the original title from the original message to preserve case
        original_match = re.search(r'update task title in task (\d+)\s+(.+)$', message_content, re.IGNORECASE)
        new_title = original_match.group(2).strip() if original_match else update_task_title_match_alt.group(2).strip()
        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_id,
                "new_title": new_title,
                "new_description": None,  # Don't change description
                "new_due_date": None
            }
        }

    # Handle "update task description in task 44 something" format (existing pattern)
    update_task_description_pattern_alt = r'update task description in task (\d+)\s+(.+)$'
    update_task_description_match_alt = re.search(update_task_description_pattern_alt, content_lower)
    if update_task_description_match_alt:
        task_id = update_task_description_match_alt.group(1)
        new_description = update_task_description_match_alt.group(2).strip()
        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_id,
                "new_title": None,  # Don't change the title
                "new_description": new_description,
                "new_due_date": None
            }
        }

    # Handle "update title in task 44 cooking" format (existing pattern)
    update_title_pattern = r'update title in task (\d+)\s+(.+)$'
    update_title_match = re.search(update_title_pattern, content_lower)
    if update_title_match:
        task_id = update_title_match.group(1)
        # Extract the original title from the original message to preserve case
        original_match = re.search(r'update title in task (\d+)\s+(.+)$', message_content, re.IGNORECASE)
        new_title = original_match.group(2).strip() if original_match else update_title_match.group(2).strip()
        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_id,
                "new_title": new_title,
                "new_description": None,  # Don't change description
                "new_due_date": None
            }
        }

    # Handle "update description in task 44 something" format (existing pattern)
    update_description_pattern = r'update description in task (\d+)\s+(.+)$'
    update_description_match = re.search(update_description_pattern, content_lower)
    if update_description_match:
        task_id = update_description_match.group(1)
        new_description = update_description_match.group(2).strip()
        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_id,
                "new_title": None,  # Don't change the title
                "new_description": new_description,
                "new_due_date": None
            }
        }

    # Handle "update task due date in task 44 26-01-2026" format (existing pattern)
    update_task_due_date_pattern_alt = r'update task due date in task (\d+)\s+(.+)$'
    update_task_due_date_match_alt = re.search(update_task_due_date_pattern_alt, content_lower)
    if update_task_due_date_match_alt:
        task_id = update_task_due_date_match_alt.group(1)
        due_date_str = update_task_due_date_match_alt.group(2).strip()

        # Normalize date format to YYYY-MM-DD
        # Handle DD/MM/YYYY or DD-MM-YYYY format and convert to YYYY-MM-DD
        date_parts = due_date_str.split(r'[-/]')
        if len(date_parts) == 3:
            day, month, year = date_parts
            # Handle 2-digit vs 4-digit years
            if len(year) == 2:
                year = '20' + year
            if len(day) == 1:
                day = '0' + day
            if len(month) == 1:
                month = '0' + month
            due_date_str = f"{year}-{month}-{day}"
        else:
            # If the date doesn't have 3 parts, try another approach for common formats
            # Try to match DD/MM/YY or DD-MM-YY format
            import re as re_module  # Use different name to avoid conflict
            date_match = re_module.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', due_date_str)
            if date_match:
                day, month, year = date_match.groups()
                if len(year) == 2:
                    year = '20' + year
                if len(day) == 1:
                    day = '0' + day
                if len(month) == 1:
                    month = '0' + month
                due_date_str = f"{year}-{month}-{day}"

        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_id,
                "new_title": None,  # Don't change the title
                "new_description": None,  # Don't change description
                "new_due_date": due_date_str
            }
        }

    # Handle "update due date in task 44 26-01-2026" format (existing pattern)
    update_due_date_pattern_alt = r'update due date in task (\d+)\s+(.+)$'
    update_due_date_match_alt = re.search(update_due_date_pattern_alt, content_lower)
    if update_due_date_match_alt:
        task_id = update_due_date_match_alt.group(1)
        due_date_str = update_due_date_match_alt.group(2).strip()

        # Normalize date format to YYYY-MM-DD
        # Handle DD/MM/YYYY or DD-MM-YYYY format and convert to YYYY-MM-DD
        date_parts = due_date_str.split(r'[-/]')
        if len(date_parts) == 3:
            day, month, year = date_parts
            # Handle 2-digit vs 4-digit years
            if len(year) == 2:
                year = '20' + year
            if len(day) == 1:
                day = '0' + day
            if len(month) == 1:
                month = '0' + month
            due_date_str = f"{year}-{month}-{day}"
        else:
            # If the date doesn't have 3 parts, try another approach for common formats
            # Try to match DD/MM/YY or DD-MM-YY format
            import re as re_module  # Use different name to avoid conflict
            date_match = re_module.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', due_date_str)
            if date_match:
                day, month, year = date_match.groups()
                if len(year) == 2:
                    year = '20' + year
                if len(day) == 1:
                    day = '0' + day
                if len(month) == 1:
                    month = '0' + month
                due_date_str = f"{year}-{month}-{day}"

        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_id,
                "new_title": None,  # Don't change the title
                "new_description": None,  # Don't change description
                "new_due_date": due_date_str
            }
        }

    # Handle "add description in task 44 something" format (existing pattern)
    add_desc_pattern_alt = r'add description in task (\d+)\s+(.+)$'
    add_desc_match_alt = re.search(add_desc_pattern_alt, content_lower)
    if add_desc_match_alt:
        task_id = add_desc_match_alt.group(1)
        description = add_desc_match_alt.group(2).strip()
        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_id,
                "new_title": None,  # Don't change the title
                "new_description": description,
                "new_due_date": None
            }
        }

    # Handle "add due date in task 44 26-01-2026" format (existing pattern)
    add_due_date_pattern_alt = r'add due date in task (\d+)\s+(.+)$'
    add_due_date_match_alt = re.search(add_due_date_pattern_alt, content_lower)
    if add_due_date_match_alt:
        task_id = add_due_date_match_alt.group(1)
        due_date_str = add_due_date_match_alt.group(2).strip()

        # Normalize date format to YYYY-MM-DD
        # Handle DD/MM/YYYY or DD-MM-YYYY format and convert to YYYY-MM-DD
        date_parts = due_date_str.split(r'[-/]')
        if len(date_parts) == 3:
            day, month, year = date_parts
            # Handle 2-digit vs 4-digit years
            if len(year) == 2:
                year = '20' + year
            if len(day) == 1:
                day = '0' + day
            if len(month) == 1:
                month = '0' + month
            due_date_str = f"{year}-{month}-{day}"
        else:
            # If the date doesn't have 3 parts, try another approach for common formats
            # Try to match DD/MM/YY or DD-MM-YY format
            import re as re_module  # Use different name to avoid conflict
            date_match = re_module.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', due_date_str)
            if date_match:
                day, month, year = date_match.groups()
                if len(year) == 2:
                    year = '20' + year
                if len(day) == 1:
                    day = '0' + day
                if len(month) == 1:
                    month = '0' + month
                due_date_str = f"{year}-{month}-{day}"

        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_id,
                "new_title": None,  # Don't change the title
                "new_description": None,  # Don't change description
                "new_due_date": due_date_str
            }
        }

    # Identify if it's a task creation command
    create_patterns = ["add a task", "create task", "remember to", "add task", "add "]
    # Exclude patterns that are meant for updating descriptions
    exclude_patterns = ["add description in task", "add due date in task", "update task", "update title in task", "update description in task", "update due date in task"]
    if any(pattern in content_lower for pattern in create_patterns) and not any(exclude_pattern in content_lower for exclude_pattern in exclude_patterns):
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
    complete_patterns = ["mark", "complete", "finish", "done with", "done", "mark as complete"]
    if any(pattern in content_lower for pattern in complete_patterns):
        # Try to extract task identifier from the message
        import re as re_module
        task_identifier = extract_task_identifier_from_message(message_content)
        return {
            "action": "complete_task",
            "params": {"task_identifier": task_identifier}
        }

    # Identify if it's a task deletion command
    delete_patterns = ["delete", "remove", "cancel", "get rid of", "eliminate", "erase"]
    if any(pattern in content_lower for pattern in delete_patterns):
        task_identifier = extract_task_identifier_from_message(message_content)
        return {
            "action": "delete_task",
            "params": {"task_identifier": task_identifier}
        }

    # Identify if it's a task update command
    update_patterns = ["update", "change", "modify", "edit", "rename"]
    if any(pattern in content_lower for pattern in update_patterns):
        task_identifier = extract_task_identifier_from_message(message_content)
        new_details = extract_task_info_from_message(message_content)
        return {
            "action": "update_task",
            "params": {
                "task_identifier": task_identifier,
                "new_title": new_details.get("title"),
                "new_description": new_details.get("description")
            }
        }

    # Default to unknown command
    return {
        "action": "unknown",
        "message": "I'm not sure how to handle that. Try saying something like 'Add a task to buy groceries', 'Show me my tasks', 'Mark task 1 as complete', 'Delete task 2', or 'Update task 3 to new title'"
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

        elif parsed_command["action"] == "complete_task":
            # Complete a task
            task_identifier = parsed_command["params"]["task_identifier"]
            result = find_and_perform_task_operation(session, user_id, task_identifier, "complete")
            response_text = result["message"]

            if result["success"]:
                executed_tool_calls.append({
                    "tool_name": "complete_task",
                    "params": {"task_id": result["task"]["id"], "title": result["task"]["title"], "completed": result["task"]["completed"]},
                    "result": "success"
                })
                tool_calls.append({"name": "complete_task", "arguments": json.dumps({"user_id": user_id, "task_id": result["task"]["id"], "title": result["task"]["title"], "completed": result["task"]["completed"]})})
            else:
                executed_tool_calls.append({
                    "tool_name": "complete_task",
                    "params": {"task_identifier": task_identifier},
                    "result": "failure"
                })

        elif parsed_command["action"] == "delete_task":
            # Delete a task
            task_identifier = parsed_command["params"]["task_identifier"]
            result = find_and_perform_task_operation(session, user_id, task_identifier, "delete")
            response_text = result["message"]

            if result["success"]:
                executed_tool_calls.append({
                    "tool_name": "delete_task",
                    "params": {"task_id": result["task"]["id"], "title": result["task"]["title"]},
                    "result": "success"
                })
                tool_calls.append({"name": "delete_task", "arguments": json.dumps({"user_id": user_id, "task_id": result["task"]["id"], "title": result["task"]["title"]})})
            else:
                executed_tool_calls.append({
                    "tool_name": "delete_task",
                    "params": {"task_identifier": task_identifier},
                    "result": "failure"
                })

        elif parsed_command["action"] == "update_task":
            # Update a task
            task_identifier = parsed_command["params"]["task_identifier"]
            new_title = parsed_command["params"].get("new_title")
            new_description = parsed_command["params"].get("new_description")
            new_due_date = parsed_command["params"].get("new_due_date")

            result = find_and_perform_task_operation(session, user_id, task_identifier, "update", new_title, new_description, new_due_date)
            response_text = result["message"]

            if result["success"]:
                executed_tool_calls.append({
                    "tool_name": "update_task",
                    "params": {"task_id": result["task"]["id"], "title": result["task"]["title"]},
                    "result": "success"
                })
                tool_calls.append({"name": "update_task", "arguments": json.dumps({"user_id": user_id, "task_id": result["task"]["id"], "title": result["task"]["title"], "description": result["task"]["description"], "due_date": result["task"].get("due_date")})})
            else:
                executed_tool_calls.append({
                    "tool_name": "update_task",
                    "params": {"task_identifier": task_identifier},
                    "result": "failure"
                })

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

    # Get current UTC time and convert to Pakistani time
    utc_now = datetime.utcnow()
    pakistani_time_str = convert_utc_to_pakistani_time(utc_now.isoformat() + "Z")

    # Return the response
    return {
        "conversation_id": conversation_id,
        "response": response_text,
        "tool_calls": tool_calls,
        "executed_tool_calls": executed_tool_calls,
        "timestamp": datetime.utcnow().isoformat(),
        "pakistani_timestamp": pakistani_time_str
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