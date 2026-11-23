import argparse
import sys
from pathlib import Path

from .models import SmartTodoError, Status, Task
from .service import TaskService
from .storage import JsonTaskStorage


def default_storage_path() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    return project_root / "data" / "tasks.json"


def format_task(task: Task) -> str:
    return (
        f"ID: {task.id}\n"
        f"Title: {task.title}\n"
        f"Description: {task.description}\n"
        f"Priority: {task.priority.value}\n"
        f"Tags: {', '.join(task.tags)}\n"
        f"Status: {task.status.value}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="smart-todo",
        description="Manage tasks stored in a local JSON file.",
    )
    parser.add_argument(
        "--storage",
        type=Path,
        help="JSON storage path (defaults to data/tasks.json relative to the project root)",
    )
    subparsers = parser.add_subparsers(dest="operation", required=True)

    create = subparsers.add_parser("create", help="Create a task")
    create.add_argument("--id", required=True, type=int)
    create.add_argument("--title", required=True)
    create.add_argument("--description", required=True)
    create.add_argument("--priority", required=True)
    create.add_argument("--tags", required=True)

    subparsers.add_parser("list", help="List all tasks")

    get = subparsers.add_parser("get", help="View one task")
    get.add_argument("--id", required=True, type=int)

    update = subparsers.add_parser("update", help="Update mutable task fields")
    update.add_argument("--id", required=True, type=int)
    update.add_argument("--title")
    update.add_argument("--description")
    update.add_argument("--priority")
    update.add_argument("--tags")

    delete = subparsers.add_parser("delete", help="Delete a task")
    delete.add_argument("--id", required=True, type=int)

    filter_parser = subparsers.add_parser("filter", help="Filter tasks by tags")
    filter_parser.add_argument("--tags", required=True)

    sort_parser = subparsers.add_parser("sort", help="Sort tasks")
    sort_parser.add_argument("--priority", action="store_true")

    status_parser = subparsers.add_parser("status", help="Change task status")
    status_parser.add_argument("--id", required=True, type=int)
    status_parser.add_argument(
        "--status",
        required=True,
        choices=[Status.PENDING.value, Status.IN_PROGRESS.value, Status.COMPLETED.value],
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    storage_path = args.storage or default_storage_path()
    service = TaskService(JsonTaskStorage(storage_path))

    if service.load_warning:
        print(f"Warning: {service.load_warning}", file=sys.stderr)

    try:
        if args.operation == "create":
            task = service.create(
                args.id,
                args.title,
                args.description,
                args.priority,
                args.tags,
            )
            print(f"Task {task.id} created.")
        elif args.operation == "list":
            tasks = service.list_tasks()
            print("\n\n".join(format_task(task) for task in tasks) if tasks else "No tasks found.")
        elif args.operation == "get":
            print(format_task(service.get(args.id)))
        elif args.operation == "update":
            task = service.update(
                args.id,
                title=args.title,
                description=args.description,
                priority=args.priority,
                tags=args.tags,
            )
            print(f"Task {task.id} updated.")
        elif args.operation == "delete":
            service.delete(args.id)
            print(f"Task {args.id} deleted.")
        elif args.operation == "filter":
            tasks = service.filter_by_tags(args.tags)
            print(
                "\n\n".join(format_task(task) for task in tasks)
                if tasks
                else "No tasks match the requested tags."
            )
        elif args.operation == "sort":
            tasks = service.sort_by_priority()
            print("\n\n".join(format_task(task) for task in tasks) if tasks else "No tasks found.")
        elif args.operation == "status":
            task = service.change_status(args.id, args.status)
            print(f"Task {task.id} status changed to {task.status.value}.")
        else:
            parser.error("Unknown operation")
    except SmartTodoError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0
