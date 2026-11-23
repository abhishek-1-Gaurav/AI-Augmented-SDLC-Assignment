from dataclasses import dataclass
from enum import Enum
from typing import Any


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Status(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    description: str
    priority: Priority
    tags: tuple[str, ...]
    status: Status = Status.PENDING


class SmartTodoError(Exception):
    """Base class for domain-facing errors."""


class ValidationError(SmartTodoError):
    pass


class DuplicateIdError(SmartTodoError):
    pass


class TaskNotFoundError(SmartTodoError):
    pass


class StorageError(SmartTodoError):
    pass


class StorageStateError(StorageError):
    pass


def task_to_dict(task: Task) -> dict[str, Any]:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority.value,
        "tags": list(task.tags),
        "status": task.status.value,
    }
