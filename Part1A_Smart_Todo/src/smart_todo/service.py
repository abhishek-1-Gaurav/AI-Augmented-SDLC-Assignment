from collections.abc import Iterable

from .models import (
    DuplicateIdError,
    Priority,
    Status,
    StorageError,
    Task,
    TaskNotFoundError,
)
from .storage import JsonTaskStorage
from .validation import (
    normalize_tags,
    validate_positive_id,
    validate_priority,
    validate_required_text,
    validate_status,
)


class TaskService:
    def __init__(self, storage: JsonTaskStorage) -> None:
        self.storage = storage
        loaded = storage.load()
        self.tasks: dict[int, Task] = {task.id: task for task in loaded.tasks}
        self.load_warning = loaded.warning

    def create(
        self,
        task_id: int,
        title: str,
        description: str,
        priority: Priority | str,
        tags: Iterable[str] | str,
    ) -> Task:
        checked_id = validate_positive_id(task_id)
        if checked_id in self.tasks:
            raise DuplicateIdError(f"Task ID {checked_id} is already in use.")
        checked_title = validate_required_text(title, "Title")
        checked_description = validate_required_text(description, "Description")
        checked_priority = (
            priority if isinstance(priority, Priority) else validate_priority(priority)
        )
        checked_tags = normalize_tags(tags)
        task = Task(
            id=checked_id,
            title=checked_title,
            description=checked_description,
            priority=checked_priority,
            tags=checked_tags,
            status=Status.PENDING,
        )
        self.tasks[task.id] = task
        try:
            self.storage.save(list(self.tasks.values()))
        except StorageError:
            del self.tasks[task.id]
            raise
        return task

    def list_tasks(self) -> list[Task]:
        return list(self.tasks.values())

    def get(self, task_id: int) -> Task:
        checked_id = validate_positive_id(task_id)
        try:
            return self.tasks[checked_id]
        except KeyError as exc:
            raise TaskNotFoundError(f"Task ID {checked_id} was not found.") from exc

    def update(
        self,
        task_id: int,
        *,
        title: str | None = None,
        description: str | None = None,
        priority: Priority | str | None = None,
        tags: Iterable[str] | str | None = None,
    ) -> Task:
        checked_id = validate_positive_id(task_id)
        current = self.tasks.get(checked_id)
        if current is None:
            raise TaskNotFoundError(f"Task ID {checked_id} was not found.")

        new_title = validate_required_text(title, "Title") if title is not None else current.title
        new_description = (
            validate_required_text(description, "Description")
            if description is not None
            else current.description
        )
        new_priority = (
            (priority if isinstance(priority, Priority) else validate_priority(priority))
            if priority is not None
            else current.priority
        )
        new_tags = normalize_tags(tags) if tags is not None else current.tags

        if (
            new_title == current.title
            and new_description == current.description
            and new_priority == current.priority
            and new_tags == current.tags
        ):
            return current

        updated = Task(
            id=current.id,
            title=new_title,
            description=new_description,
            priority=new_priority,
            tags=new_tags,
            status=current.status,
        )
        self.tasks[current.id] = updated
        try:
            self.storage.save(list(self.tasks.values()))
        except StorageError:
            self.tasks[current.id] = current
            raise
        return updated

    def delete(self, task_id: int) -> None:
        checked_id = validate_positive_id(task_id)
        if checked_id not in self.tasks:
            raise TaskNotFoundError(f"Task ID {checked_id} was not found.")
        removed = self.tasks.pop(checked_id)
        try:
            self.storage.save(list(self.tasks.values()))
        except StorageError:
            self.tasks[checked_id] = removed
            raise

    def filter_by_tags(self, tags: Iterable[str] | str) -> list[Task]:
        requested = normalize_tags(tags)
        requested_keys = {tag.casefold() for tag in requested}
        return [
            task
            for task in self.tasks.values()
            if requested_keys.issubset({tag.casefold() for tag in task.tags})
        ]

    def sort_by_priority(self) -> list[Task]:
        rank = {Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}
        return sorted(self.tasks.values(), key=lambda task: rank[task.priority], reverse=True)

    def change_status(self, task_id: int, status: Status | str) -> Task:
        checked_id = validate_positive_id(task_id)
        current = self.tasks.get(checked_id)
        if current is None:
            raise TaskNotFoundError(f"Task ID {checked_id} was not found.")
        checked_status = status if isinstance(status, Status) else validate_status(status)
        if checked_status == current.status:
            return current
        updated = Task(
            id=current.id,
            title=current.title,
            description=current.description,
            priority=current.priority,
            tags=current.tags,
            status=checked_status,
        )
        self.tasks[current.id] = updated
        try:
            self.storage.save(list(self.tasks.values()))
        except StorageError:
            self.tasks[current.id] = current
            raise
        return updated
