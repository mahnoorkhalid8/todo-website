# Todo Application Implementation Tasks

## Overview
This document breaks down the Todo application implementation into atomic, verifiable tasks. The tasks follow the order: environment configuration, data model, CRUD functions, and CLI implementation.

## Phase 1: Environment Configuration

### Task 1.1: Set up project structure
- Create src/ directory
- Set up pyproject.toml with uv configuration
- Add dependencies: rich (optional), typing extensions
- Verify: Run `uv sync` successfully

### Task 1.2: Configure development tools
- Set up mypy configuration for type checking
- Set up pytest configuration for testing
- Set up pre-commit hooks if needed
- Verify: Run `mypy src/` without errors

## Phase 2: Data Model Implementation

### Task 2.1: Create Task data class
- Implement Task class in `src/models.py`
- Include id, title, description, completed, created_at, updated_at fields
- Add proper type hints for all properties
- Verify: Task can be instantiated with required parameters

### Task 2.2: Add Task validation
- Implement validation for required fields (title cannot be empty)
- Add validation methods to ensure data integrity
- Verify: Attempting to create a Task with empty title raises appropriate error

### Task 2.3: Add Task factory methods
- Create factory method for creating new tasks with auto-generated timestamps
- Implement method to update task fields
- Verify: Factory methods work correctly and update timestamps properly

## Phase 3: Manager Implementation (CRUD Operations)

### Task 3.1: Create TaskManager class
- Implement TaskManager in `src/manager.py`
- Add in-memory storage (dictionary) for tasks
- Implement unique ID generation mechanism with counter
- Verify: TaskManager can be instantiated and maintains internal state

### Task 3.2: Implement add_task method
- Create method to add new tasks to storage
- Generate unique ID for each new task
- Update created_at and updated_at timestamps
- Verify: Adding a task returns the task with a unique ID

### Task 3.3: Implement list_tasks method
- Create method to return all tasks
- Return tasks in a consistent order (e.g., by ID)
- Verify: Method returns all added tasks in correct order

### Task 3.4: Implement get_task method
- Create method to retrieve a single task by ID
- Handle case where task doesn't exist
- Verify: Method returns correct task for valid ID, appropriate error for invalid ID

### Task 3.5: Implement update_task method
- Create method to update existing task's title/description
- Update updated_at timestamp when task is modified
- Verify: Task fields are updated correctly and timestamp is updated

### Task 3.6: Implement delete_task method
- Create method to remove task by ID
- Handle case where task doesn't exist
- Verify: Task is removed from storage and method returns appropriate confirmation

### Task 3.7: Implement toggle_task_status method
- Create method to toggle completed status of a task
- Update updated_at timestamp when status changes
- Verify: Task completion status toggles correctly and timestamp is updated

### Task 3.8: Add error handling to manager
- Implement proper exception handling for all operations
- Create custom exception classes for different error types
- Verify: Appropriate errors are raised for invalid operations

## Phase 4: CLI Implementation

### Task 4.1: Set up CLI framework
- Implement basic CLI structure in `src/cli.py`
- Set up argument parsing with argparse
- Create command routing mechanism
- Verify: CLI accepts commands and routes them appropriately

### Task 4.2: Implement add command
- Create CLI command to add new tasks
- Parse title and optional description from arguments
- Call manager's add_task method
- Format and display success/error messages
- Verify: Adding task via CLI works and displays appropriate message

### Task 4.3: Implement list command
- Create CLI command to list all tasks
- Format tasks in a readable table (ID, Status, Title)
- Handle case where no tasks exist
- Verify: Task list displays correctly in table format

### Task 4.4: Implement update command
- Create CLI command to update existing tasks
- Parse task ID and new title/description from arguments
- Call manager's update_task method
- Format and display success/error messages
- Verify: Updating task via CLI works and displays appropriate message

### Task 4.5: Implement delete command
- Create CLI command to delete tasks by ID
- Parse task ID from arguments
- Call manager's delete_task method
- Format and display success/error messages
- Verify: Deleting task via CLI works and displays appropriate message

### Task 4.6: Implement toggle command
- Create CLI command to toggle task status
- Parse task ID from arguments
- Call manager's toggle_task_status method
- Format and display success/error messages
- Verify: Toggling task status via CLI works and displays appropriate message

### Task 4.7: Add help and error messages
- Implement comprehensive help text for all commands
- Add user-friendly error messages for invalid inputs
- Verify: Help text is displayed correctly and errors are user-friendly

## Phase 5: Main Application and Integration

### Task 5.1: Create main entry point
- Implement main function in `src/main.py`
- Initialize TaskManager instance
- Parse command-line arguments
- Route commands to CLI handler
- Verify: Application starts and processes commands correctly

### Task 5.2: Implement CLI loop
- Create interactive mode if desired (optional)
- Handle command execution flow
- Implement graceful shutdown
- Verify: CLI processes commands in sequence without crashing

### Task 5.3: Add rich formatting (optional)
- Integrate Rich library for enhanced console output
- Format tables and messages with Rich
- Add color coding for different statuses
- Verify: Output is formatted nicely with Rich enhancements

## Phase 6: Testing and Verification

### Task 6.1: Write unit tests for models
- Test Task class instantiation and validation
- Test factory methods
- Verify: All model tests pass with 100% coverage

### Task 6.2: Write unit tests for manager
- Test all CRUD operations
- Test error handling
- Test unique ID generation
- Verify: All manager tests pass with 100% coverage

### Task 6.3: Write integration tests
- Test full workflow from CLI to manager to models
- Test command flows
- Verify: All integration tests pass

### Task 6.4: End-to-end testing
- Test complete application functionality
- Verify all commands work as specified in the requirements
- Verify: All end-to-end tests pass

## Verification Checklist
- [ ] All type hints are correct and pass mypy validation
- [ ] All functions have appropriate docstrings
- [ ] Error handling is implemented throughout
- [ ] Unique ID generation works correctly
- [ ] In-memory storage persists data during session
- [ ] CLI commands work as specified
- [ ] User-friendly error messages are displayed
- [ ] All tests pass
- [ ] Application follows SOLID principles