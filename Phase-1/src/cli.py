"""
CLI interface for the Todo application.
Uses standard input/output for console interaction.
"""
import argparse
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich import print
from rich.panel import Panel

from src.manager import TaskManager


class TodoCLI:
    """
    Command-line interface for the Todo application.
    """
    def __init__(self, task_manager: TaskManager) -> None:
        """
        Initialize the CLI with a task manager.

        Args:
            task_manager: TaskManager instance to use
        """
        self.task_manager = task_manager

    def add_task(self, title: str, description: str = "") -> None:
        """
        Add a new task.

        Args:
            title: Title of the task
            description: Description of the task (optional)
        """
        try:
            task = self.task_manager.add_task(title, description)
            print(f"[green]Task added successfully with ID: {task.id}[/green]")
        except ValueError as e:
            print(f"[red]Error: {e}[/red]")

    def list_tasks(self) -> None:
        """List all tasks in a formatted table using Rich."""
        tasks = self.task_manager.list_tasks()

        if not tasks:
            print("[yellow]No tasks found.[/yellow]")
            return

        # Create a rich table
        table = Table(title="Todo List", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=5)
        table.add_column("Status", min_width=10)
        table.add_column("Title", min_width=30)
        table.add_column("Description", min_width=30)

        # Add each task to the table
        for task in tasks:
            status = "[green]Complete[/green]" if task.completed else "[red]Incomplete[/red]"
            title = task.title if len(task.title) <= 30 else task.title[:27] + "..."
            description = task.description if len(task.description) <= 30 else task.description[:27] + "..."
            table.add_row(str(task.id), status, title, description)

        # Print the table
        console = Console()
        console.print(table)

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> None:
        """
        Update an existing task.

        Args:
            task_id: ID of the task to update
            title: New title for the task (optional)
            description: New description for the task (optional)
        """
        if title is None and description is None:
            print("[red]Error: Must provide at least one field to update (title or description)[/red]")
            return

        task = self.task_manager.update_task(task_id, title, description)
        if task:
            print(f"[green]Task {task_id} updated successfully[/green]")
        else:
            print(f"[red]Error: Task with ID {task_id} not found[/red]")

    def delete_task(self, task_id: int) -> None:
        """
        Delete a task by ID.

        Args:
            task_id: ID of the task to delete
        """
        success = self.task_manager.delete_task(task_id)
        if success:
            print(f"[green]Task {task_id} deleted successfully[/green]")
        else:
            print(f"[red]Error: Task with ID {task_id} not found[/red]")

    def toggle_task_status(self, task_id: int) -> None:
        """
        Toggle the completion status of a task.

        Args:
            task_id: ID of the task to toggle
        """
        task = self.task_manager.toggle_task_status(task_id)
        if task:
            status = "Complete" if task.completed else "Incomplete"
            print(f"[green]Task {task_id} marked as {status}[/green]")
        else:
            print(f"[red]Error: Task with ID {task_id} not found[/red]")

    def interactive_mode(self) -> None:
        """Run the application in interactive mode."""
        print("[bold blue]Welcome to the Todo Console Application![/bold blue]")
        print("[green]Available commands:[/green] [cyan]add, list, update, delete, toggle, quit[/cyan]")
        print("[yellow]Type 'help' for more information on each command.[/yellow]\n")

        while True:
            try:
                command = Prompt.ask("[bold]Enter command[/bold]", choices=["add", "list", "update", "delete", "toggle", "help", "quit", "exit"], default="list").strip().lower()

                if command == "quit" or command == "exit":
                    print("[bold red]Goodbye![/bold red]")
                    break
                elif command == "help":
                    self.show_interactive_help()
                elif command == "add":
                    self.interactive_add()
                elif command == "list":
                    self.list_tasks()
                elif command == "update":
                    self.interactive_update()
                elif command == "delete":
                    self.interactive_delete()
                elif command == "toggle":
                    self.interactive_toggle()
                else:
                    print(f"[red]Unknown command: {command}. Type 'help' for available commands.[/red]")
            except KeyboardInterrupt:
                print("\n[bold red]Goodbye![/bold red]")
                break
            except EOFError:
                print("\n[bold red]Goodbye![/bold red]")
                break

    def show_interactive_help(self) -> None:
        """Display help information for interactive mode."""
        help_text = """[bold]Available commands:[/bold]
  [cyan]add[/cyan]     - Add a new task
  [cyan]list[/cyan]    - List all tasks
  [cyan]update[/cyan]  - Update an existing task
  [cyan]delete[/cyan]  - Delete a task
  [cyan]toggle[/cyan]  - Toggle task completion status
  [cyan]help[/cyan]    - Show this help message
  [cyan]quit[/cyan]    - Exit the application

[bold]Examples:[/bold]
  add
  list
  update
  delete 1
  toggle 1"""

        print(Panel(help_text, title="[bold]Help[/bold]", border_style="blue"))

    def interactive_add(self) -> None:
        """Interactive task addition."""
        try:
            title = Prompt.ask("[bold]Enter task title[/bold]").strip()
            if not title:
                print("[red]Error: Title cannot be empty[/red]")
                return

            description = Prompt.ask("[bold]Enter task description (optional)[/bold]", default="")
            self.add_task(title, description)
        except KeyboardInterrupt:
            print("\n[red]Add operation cancelled.[/red]")

    def interactive_update(self) -> None:
        """Interactive task update."""
        try:
            task_id = IntPrompt.ask("[bold]Enter task ID to update[/bold]")

            title_input = Prompt.ask("[bold]Enter new title (leave blank to keep current)[/bold]", default="")
            description_input = Prompt.ask("[bold]Enter new description (leave blank to keep current)[/bold]", default="")

            title = title_input if title_input else None
            description = description_input if description_input else None

            if title is None and description is None:
                print("[red]Error: Must provide at least one field to update (title or description)[/red]")
                return

            self.update_task(task_id, title, description)
        except KeyboardInterrupt:
            print("\n[red]Update operation cancelled.[/red]")

    def interactive_delete(self) -> None:
        """Interactive task deletion."""
        try:
            task_id = IntPrompt.ask("[bold]Enter task ID to delete[/bold]")
            self.delete_task(task_id)
        except KeyboardInterrupt:
            print("\n[red]Delete operation cancelled.[/red]")

    def interactive_toggle(self) -> None:
        """Interactive task status toggle."""
        try:
            task_id = IntPrompt.ask("[bold]Enter task ID to toggle[/bold]")
            self.toggle_task_status(task_id)
        except KeyboardInterrupt:
            print("\n[red]Toggle operation cancelled.[/red]")

    def run(self, args: Optional[List[str]] = None) -> None:
        """
        Run the CLI application with the given arguments.

        Args:
            args: Command-line arguments (for testing)
        """
        if args is None or len(args) == 0:
            # Run in interactive mode if no arguments provided
            self.interactive_mode()
            return

        parser = argparse.ArgumentParser(description="Todo Application")
        parser.add_argument("--version", action="version", version="Todo App 1.0.0")

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Add command
        add_parser = subparsers.add_parser("add", help="Add a new task")
        add_parser.add_argument("title", help="Title of the task")
        add_parser.add_argument("description", nargs="?", default="", help="Description of the task")

        # List command
        list_parser = subparsers.add_parser("list", help="List all tasks")

        # Update command
        update_parser = subparsers.add_parser("update", help="Update a task")
        update_parser.add_argument("id", type=int, help="ID of the task to update")
        update_parser.add_argument("--title", help="New title for the task")
        update_parser.add_argument("--description", help="New description for the task")

        # Delete command
        delete_parser = subparsers.add_parser("delete", help="Delete a task")
        delete_parser.add_argument("id", type=int, help="ID of the task to delete")

        # Toggle command
        toggle_parser = subparsers.add_parser("toggle", help="Toggle task status")
        toggle_parser.add_argument("id", type=int, help="ID of the task to toggle")

        # Parse arguments
        parsed_args = parser.parse_args(args)

        # Execute command based on parsed arguments
        if parsed_args.command == "add":
            self.add_task(parsed_args.title, parsed_args.description)
        elif parsed_args.command == "list":
            self.list_tasks()
        elif parsed_args.command == "update":
            self.update_task(parsed_args.id, parsed_args.title, parsed_args.description)
        elif parsed_args.command == "delete":
            self.delete_task(parsed_args.id)
        elif parsed_args.command == "toggle":
            self.toggle_task_status(parsed_args.id)
        elif parsed_args.command is None:
            # If no arguments provided, run in interactive mode
            self.interactive_mode()
        else:
            print(f"Unknown command: {parsed_args.command}")
            parser.print_help()