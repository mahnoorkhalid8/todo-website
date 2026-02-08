# Todo Application Specification

## Overview
This document defines the functional requirements for a Python 3.13+ Todo Console Application. The application will allow users to manage their tasks through a command-line interface with persistent in-memory storage.

## Functional Requirements

### 1. Add Task
**Feature**: Add a new task to the todo list
- **Input**: Title (required), Description (optional)
- **Validation**: Title must not be empty
- **Output**: Success message with assigned task ID
- **Error Handling**: Display user-friendly error if title is missing

### 2. List Tasks
**Feature**: Display all tasks in the todo list
- **Output Format**: ID, Status (Complete/Incomplete), Title
- **Display**: Show all tasks in a tabular format
- **Empty State**: Display message if no tasks exist

### 3. Update Task
**Feature**: Modify existing task's title and/or description
- **Input**: Task ID, new Title (optional), new Description (optional)
- **Validation**: Task ID must exist, at least one field to update
- **Output**: Success message confirming update
- **Error Handling**: Display user-friendly error if task ID doesn't exist

### 4. Delete Task
**Feature**: Remove a task by its ID
- **Input**: Task ID
- **Validation**: Task ID must exist
- **Output**: Success message confirming deletion
- **Error Handling**: Display user-friendly error if task ID doesn't exist

### 5. Toggle Status
**Feature**: Mark a task as Complete or Incomplete
- **Input**: Task ID
- **Validation**: Task ID must exist
- **Behavior**: Toggle current status (Complete ↔ Incomplete)
- **Output**: Success message with new status
- **Error Handling**: Display user-friendly error if task ID doesn't exist

## Data Model

### Task
The Task entity will have the following properties:

```
Task {
    id: int          # Unique identifier (auto-generated)
    title: str       # Task title (required, non-empty)
    description: str # Task description (optional, can be empty)
    completed: bool  # Completion status (default: False)
    created_at: datetime  # Timestamp of creation (auto-generated)
    updated_at: datetime  # Timestamp of last update (auto-generated)
}
```

## CLI Interaction Flow

### Command Structure
The application will follow this command pattern:
```
todo [command] [arguments]
```

### Available Commands
- `todo add "Title" ["Description"]` - Add a new task
- `todo list` - List all tasks
- `todo update [ID] ["New Title"] ["New Description"]` - Update a task
- `todo delete [ID]` - Delete a task by ID
- `todo toggle [ID]` - Toggle task completion status
- `todo help` - Show help information
- `todo --version` - Show application version

### Expected User Flow
1. User runs the application with a command
2. Application validates input parameters
3. Application performs requested operation
4. Application displays appropriate output or error message
5. Application returns to ready state for next command

### Error Handling
- All errors must be displayed to stderr
- Error messages must be user-friendly and actionable
- The application should not crash on invalid input
- Invalid commands should show help text

## Non-Functional Requirements

### Performance
- Operations should complete in under 100ms for up to 1000 tasks
- Application startup time should be under 500ms

### Usability
- Command interface must be intuitive
- Help text must be available for all commands
- Error messages must clearly indicate what went wrong and how to fix it

### Reliability
- In-memory storage must persist data for the duration of the application session
- Proper validation must prevent invalid data from being stored
- Graceful handling of edge cases (empty lists, invalid IDs, etc.)

## Acceptance Criteria

### Add Task
- [ ] Can add a task with title and optional description
- [ ] Prevents adding a task without a title
- [ ] Assigns a unique ID to each task
- [ ] Sets completion status to 'Incomplete' by default

### List Tasks
- [ ] Displays all tasks with ID, Status, and Title
- [ ] Shows appropriate message when no tasks exist
- [ ] Formats output in a readable table format

### Update Task
- [ ] Can update task title and/or description
- [ ] Prevents updating non-existent tasks
- [ ] Allows partial updates (only title or only description)

### Delete Task
- [ ] Can delete a task by ID
- [ ] Prevents deleting non-existent tasks
- [ ] Confirms successful deletion

### Toggle Status
- [ ] Can toggle task completion status
- [ ] Prevents toggling non-existent tasks
- [ ] Shows new status after toggle

## Example Usage
```
$ todo add "Buy groceries" "Milk, bread, eggs"
Task added successfully with ID: 1

$ todo add "Complete project"
Task added successfully with ID: 2

$ todo list
ID  | Status      | Title
----|-------------|------------------
1   | Incomplete  | Buy groceries
2   | Incomplete  | Complete project

$ todo toggle 1
Task 1 marked as Complete

$ todo update 2 "Complete project" "Finish the todo app implementation"
Task 2 updated successfully

$ todo list
ID  | Status      | Title
----|-------------|------------------
1   | Complete    | Buy groceries
2   | Incomplete  | Complete project

$ todo delete 1
Task 1 deleted successfully
```