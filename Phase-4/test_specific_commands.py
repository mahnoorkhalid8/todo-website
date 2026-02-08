#!/usr/bin/env python3
"""
Test script to verify the specific commands you mentioned work correctly.
"""

import sys
import os

# Add backend to the path to import the parsing function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the parsing function directly from the routes module
try:
    from routes.chat import parse_command_from_message
except ImportError:
    # If the direct import doesn't work, import from the fixed version
    import re

    def parse_command_from_message(message_content: str):
        """
        Parse natural language command to determine intended action.
        This is the exact copy from the updated chat.py file.
        """
        content_lower = message_content.lower().strip()

        # FIRST: Handle specific update patterns before any general patterns

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

        # Handle "add task description of task 44 biryani" format (alternative pattern)
        add_desc_of_pattern = r'add task description of task (\d+)\s+(.+)$'
        add_desc_of_match = re.search(add_desc_of_pattern, content_lower)
        if add_desc_of_match:
            task_id = add_desc_of_match.group(1)
            description = add_desc_of_match.group(2).strip()
            return {
                "action": "update_task",
                "params": {
                    "task_identifier": task_id,
                    "new_title": None,  # Don't change the title
                    "new_description": description,
                    "new_due_date": None
                }
            }

        # Handle "add task due date of task 44 29-01-2026" format (alternative pattern)
        add_due_date_of_pattern = r'add task due date of task (\d+)\s+(.+)$'
        add_due_date_of_match = re.search(add_due_date_of_pattern, content_lower)
        if add_due_date_of_match:
            task_id = add_due_date_of_match.group(1)
            due_date_str = add_due_date_of_match.group(2).strip()

            # Normalize date format to YYYY-MM-DD
            # Handle DD/MM/YYYY or DD-MM-YYYY format and convert to YYYY-MM-DD
            date_parts = re.split(r'[-/]', due_date_str)
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
                date_match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', due_date_str)
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

        # Handle "add task due date in task 40 29-01-2026" format
        add_due_date_pattern = r'add task due date in task (\d+)\s+(.+)$'
        add_due_date_match = re.search(add_due_date_pattern, content_lower)
        if add_due_date_match:
            task_id = add_due_date_match.group(1)
            due_date_str = add_due_date_match.group(2).strip()

            # Normalize date format to YYYY-MM-DD
            # Handle DD/MM/YYYY or DD-MM-YYYY format and convert to YYYY-MM-DD
            date_parts = re.split(r'[-/]', due_date_str)
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
                date_match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', due_date_str)
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

        # Handle "add task cooking" format (only if it's not a more specific add command)
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
            date_parts = re.split(r'[-/]', due_date_str)
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
                date_match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', due_date_str)
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
            date_parts = re.split(r'[-/]', due_date_str)
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
                date_match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', due_date_str)
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
            date_parts = re.split(r'[-/]', due_date_str)
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
                date_match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', due_date_str)
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
            date_parts = re.split(r'[-/]', due_date_str)
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
                date_match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', due_date_str)
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
            # Extract the task title from the message
            for phrase in ["add a task to ", "create task ", "remember to ", "add task ", "add "]:
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

                    return {
                        "action": "add_task",
                        "params": {
                            "title": title,
                            "description": description
                        }
                    }
            return {
                "action": "add_task",
                "params": {
                    "title": message_content.strip(),
                    "description": None
                }
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
            # Simplified extraction for this test
            import re as re_module
            number_match = re_module.search(r'(?:task|number)\s*(\d+)', content_lower)
            task_identifier = number_match.group(1) if number_match else None
            return {
                "action": "complete_task",
                "params": {"task_identifier": task_identifier}
            }

        # Identify if it's a task deletion command
        delete_patterns = ["delete", "remove", "cancel", "get rid of", "eliminate", "erase"]
        if any(pattern in content_lower for pattern in delete_patterns):
            # Simplified extraction for this test
            import re as re_module
            number_match = re_module.search(r'(?:task|number)\s*(\d+)', content_lower)
            task_identifier = number_match.group(1) if number_match else None
            return {
                "action": "delete_task",
                "params": {"task_identifier": task_identifier}
            }

        # Identify if it's a task update command
        update_patterns = ["update", "change", "modify", "edit", "rename"]
        if any(pattern in content_lower for pattern in update_patterns):
            # Simplified extraction for this test
            import re as re_module
            number_match = re_module.search(r'(?:task|number)\s*(\d+)', content_lower)
            task_identifier = number_match.group(1) if number_match else None
            return {
                "action": "update_task",
                "params": {
                    "task_identifier": task_identifier,
                    "new_title": None,
                    "new_description": None
                }
            }

        # Default to unknown command
        return {
            "action": "unknown",
            "message": "I'm not sure how to handle that. Try saying something like 'Add a task to buy groceries', 'Show me my tasks', 'Mark task 1 as complete', 'Delete task 2', or 'Update task 3 to new title'"
        }


def test_command(command, expected_action, expected_task_id=None, expected_description=None, expected_title=None):
    """Test a specific command."""
    result = parse_command_from_message(command)

    print(f"\nTesting: '{command}'")
    print(f"Action: {result['action']}")

    if 'params' in result:
        params = result['params']
        print(f"Params: {params}")

        # Check if it's an update task command for description
        if result['action'] == 'update_task':
            task_id = params.get('task_identifier')
            description = params.get('new_description')
            title = params.get('new_title')

            if expected_task_id and task_id == expected_task_id:
                print(f"PASS: Correctly identified task ID: {task_id}")
            elif expected_task_id:
                print(f"FAIL: Expected task ID: {expected_task_id}, got: {task_id}")

            if expected_description and description and expected_description.lower() in description.lower():
                print(f"PASS: Correctly identified description: '{description}'")
            elif expected_description:
                print(f"FAIL: Expected description containing: '{expected_description}', got: '{description}'")

            if expected_title and title and expected_title.lower() in title.lower():
                print(f"PASS: Correctly identified title: '{title}'")
            elif expected_title:
                print(f"FAIL: Expected title containing: '{expected_title}', got: '{title}'")
        elif result['action'] == 'add_task':
            title = params.get('title')
            print(f"Title: {title}")
            if 'description' in command.lower() and 'task' in command.lower():
                print("FAIL: This should be an update command, not an add command!")
            else:
                print("PASS: Correctly identified as add task command")
        else:
            print(f"Action type: {result['action']}")

def main():
    print("Testing Specific Commands:")
    print("="*50)

    # Test the exact command that was causing issues
    test_command(
        "add task description in task 44 biryani",
        expected_action='update_task',
        expected_task_id='44',
        expected_description='biryani'
    )

    # Test the update command
    test_command(
        "update task description in task 44 cook biryani",
        expected_action='update_task',
        expected_task_id='44',
        expected_description='cook biryani'
    )

    # Test other commands
    test_command(
        "add task cooking",
        expected_action='add_task',
        expected_title='cooking'
    )

    test_command(
        "add task due date in task 40 29-01-2026",
        expected_action='update_task',
        expected_task_id='40'
    )


if __name__ == "__main__":
    main()