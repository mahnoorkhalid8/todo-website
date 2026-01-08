# Data Model: Todo Web Application

## Overview
This document defines the data models for the Todo Web Application, including entities, their attributes, relationships, and validation rules.

## Entity Models

### User
**Description**: Represents a registered user in the system

**Attributes**:
- `id` (string): Unique identifier for the user (primary key)
- `email` (string): User's email address (required, unique, valid email format)
- `name` (string, optional): User's display name (nullable)
- `password_hash` (string): Hashed password for authentication (required)
- `created_at` (timestamp): Account creation timestamp (required, default: now)
- `updated_at` (timestamp): Last update timestamp (required, default: now, auto-update)

**Validation Rules**:
- Email must follow standard email format
- Email must be unique across all users
- Password must meet complexity requirements (8+ characters)
- Created timestamp automatically set on creation
- Updated timestamp automatically updated on any change

**Constraints**:
- Primary key: id
- Unique constraint: email

### Task
**Description**: Represents a user's task item

**Attributes**:
- `id` (integer): Unique identifier for the task (primary key, auto-increment)
- `user_id` (string): Foreign key referencing the user who owns this task (required)
- `title` (string): Task title (required, 1-200 characters)
- `description` (text, optional): Task description (nullable, max 1000 characters)
- `completed` (boolean): Completion status (required, default: false)
- `created_at` (timestamp): Task creation timestamp (required, default: now)
- `updated_at` (timestamp): Last update timestamp (required, default: now, auto-update)

**Validation Rules**:
- Title must be 1-200 characters
- Description must be max 1000 characters if provided
- User_id must reference an existing user
- Completed defaults to false
- Created timestamp automatically set on creation
- Updated timestamp automatically updated on any change

**Constraints**:
- Primary key: id
- Foreign key: user_id references users(id)
- Index: user_id for efficient user-based filtering
- Index: completed for status-based filtering

## Relationships

### User → Task (One-to-Many)
- One user can have many tasks
- Foreign key: tasks.user_id references users.id
- Cascade behavior: Tasks should be deleted when user is deleted (to be confirmed)

## State Transitions

### Task State Transitions
- **Created**: New task with `completed = false`
- **Updated**: Task details modified, `updated_at` timestamp updated
- **Completed**: `completed` status toggled to `true`
- **Reopened**: `completed` status toggled back to `false`
- **Deleted**: Task removed from user's list

## Database Indexes

### Required Indexes
1. **tasks.user_id**: For efficient filtering by user
2. **tasks.completed**: For efficient filtering by completion status
3. **composite index (user_id, completed)**: For optimized queries filtering by both user and status
4. **tasks.created_at**: For sorting tasks by creation date

## Data Integrity Rules

### User Data Isolation
- All task queries must be filtered by authenticated user's ID
- Users cannot access tasks belonging to other users
- Authentication required for all task operations

### Validation Enforcement
- All validation rules enforced at both application and database levels
- Database constraints prevent invalid data storage
- Application-level validation provides user-friendly error messages

## API Data Contracts

### Request/Response Schemas

**User Registration Request**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**User Registration Response**:
```json
{
  "success": true,
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "name": null
  },
  "token": "jwt-token-string"
}
```

**Task Creation Request**:
```json
{
  "title": "Complete project",
  "description": "Finish the todo application project"
}
```

**Task Response**:
```json
{
  "id": 123,
  "user_id": "user-uuid",
  "title": "Complete project",
  "description": "Finish the todo application project",
  "completed": false,
  "created_at": "2026-01-05T10:00:00Z",
  "updated_at": "2026-01-05T10:00:00Z"
}
```