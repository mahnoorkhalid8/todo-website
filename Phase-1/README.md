# Todo Console Application

A Python 3.13+ console-based todo application with in-memory storage.

## Features

- Add tasks with title and description
- List all tasks with ID, status, and title
- Update existing tasks
- Delete tasks by ID
- Toggle task completion status
- User-friendly console interface

## Prerequisites

- Python 3.13+
- uv (for dependency management)

## Installation

1. Clone the repository
2. Navigate to the project directory
3. Install dependencies using uv:

```bash
uv sync
```

## Usage

### Add a Task

```bash
python -m src.main add "Task Title" "Task Description (optional)"
```

### List All Tasks

```bash
python -m src.main list
```

### Update a Task

```bash
python -m src.main update 1 --title "New Title" --description "New Description"
```

Or update just the title:

```bash
python -m src.main update 1 --title "New Title"
```

Or update just the description:

```bash
python -m src.main update 1 --description "New Description"
```

### Delete a Task

```bash
python -m src.main delete 1
```

### Toggle Task Status

```bash
python -m src.main toggle 1
```

### Get Help

```bash
python -m src.main --help
```

Or get help for specific commands:

```bash
python -m src.main add --help
python -m src.main update --help
```

## Example Workflow

```bash
# Add tasks
python -m src.main add "Buy groceries" "Milk, bread, eggs"
python -m src.main add "Complete project" "Finish the todo app implementation"

# List tasks
python -m src.main list

# Toggle task status
python -m src.main toggle 1

# Update a task
python -m src.main update 2 --title "Complete project" --description "Finish the todo app implementation and test it"

# Delete a task
python -m src.main delete 1

# List tasks again to see changes
python -m src.main list
```

## Project Structure

- `src/models.py` - Task data model
- `src/manager.py` - Task management logic
- `src/cli.py` - Command-line interface
- `src/main.py` - Application entry point