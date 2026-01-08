"""
Main entry point for the Todo application.
"""
from src.cli import TodoCLI
from src.manager import TaskManager


def main() -> None:
    """Main entry point for the Todo application."""
    # Initialize the task manager
    task_manager = TaskManager()

    # Initialize the CLI interface
    cli = TodoCLI(task_manager)

    # Run the application
    cli.run()


if __name__ == "__main__":
    main()