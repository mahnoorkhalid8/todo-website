# Todo Console App Constitution

## Core Principles

### I. Dependency Management with 'uv'
All project dependencies must be managed using 'uv'. The project will use pyproject.toml for dependency declarations, with all dependencies properly versioned and pinned as appropriate. Virtual environments will be created and managed exclusively through 'uv' commands.

### II. Project Structure - '/src' Organization
All source code must reside in the '/src' directory. The directory structure should be well-organized with clear separation of concerns. The main application entry point should be in a designated module within this structure.

### III. Strict Type Hinting Throughout
All code must include comprehensive type hints using Python's typing module. This includes function parameters, return types, and variable declarations. Type checking tools like mypy should be integrated into the development workflow.

### IV. Clean Code Principles (SOLID)
All code must adhere to SOLID principles:
- Single Responsibility Principle: Each class/module should have one reason to change
- Open/Closed Principle: Entities should be open for extension but closed for modification
- Liskov Substitution Principle: Objects should be replaceable with instances of their subtypes
- Interface Segregation Principle: Clients should not be forced to depend on interfaces they don't use
- Dependency Inversion Principle: Depend on abstractions, not concretions

### V. In-Memory Storage Only
The application must use in-memory storage only (Python lists, dictionaries, and other built-in data structures). No external databases, file storage, or persistent storage mechanisms should be used. Data persistence is not a requirement for this console application.

### VI. User-Friendly Error Handling
All error messages displayed to the console must be clear, informative, and user-friendly. Error handling should provide actionable feedback to users without exposing internal implementation details. Proper exception handling with appropriate error types should be implemented throughout the application.

## Additional Constraints

### Technology Stack
- Python 3.13+ required
- 'uv' for dependency management
- Standard library for data structures and console I/O
- Type checking tools (mypy, pyright) for static analysis
- Testing framework (pytest) for unit and integration tests

### Code Quality Standards
- All code must pass static type checking
- All functions and classes must have docstrings
- Test coverage should be comprehensive
- Code should follow PEP 8 style guidelines
- No external dependencies beyond what's necessary for core functionality

## Development Workflow

### Testing Approach
- Test-driven development (TDD) is encouraged
- Unit tests for all business logic
- Integration tests for command flows
- Error handling tests to ensure user-friendly messages

### Code Review Process
- All code changes must include type hints
- Adherence to SOLID principles will be verified
- Error handling and user experience will be evaluated
- Clean code practices will be validated

## Governance

This constitution supersedes all other practices for this project. All pull requests and code reviews must verify compliance with these principles. Any deviation from these principles must be documented with a clear justification and approved through the project's governance process.

**Version**: 1.0.0 | **Ratified**: 2026-01-01 | **Last Amended**: 2026-01-01
