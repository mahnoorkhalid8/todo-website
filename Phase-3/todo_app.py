#!/usr/bin/env python3
"""
Console script for the Todo application.
"""
import sys
import os

# Add the current directory to the Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli import TodoCLI
from src.manager import TaskManager


def main():
    """Main entry point for the Todo application when run as a script."""
    # Initialize the task manager
    task_manager = TaskManager()

    # Initialize the CLI interface
    cli = TodoCLI(task_manager)

    # Run the application with command line arguments
    cli.run(sys.argv[1:] if len(sys.argv) > 1 else None)


if __name__ == "__main__":
    main()