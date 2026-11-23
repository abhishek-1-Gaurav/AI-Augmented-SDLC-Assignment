import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .models import StorageError, Task, ValidationError, task_to_dict
from .validation import (
    normalize_tags,
    validate_positive_id,
    validate_priority,
    validate_required_text,
    validate_status,
)


@dataclass(frozen=True)
class LoadResult:
    tasks: list[Task]
    warning: str | None
    can_save: bool


class JsonTaskStorage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._blocked = False

    def load(self) -> LoadResult:
        if not self.path.exists():
            self._blocked = False
            return LoadResult([], f"Task file is missing: {self.path}", True)

        try:
            text = self.path.read_text(encoding="utf-8")
        except OSError:
            self._blocked = True
            return LoadResult(
                [],
                f"Task file is unreadable: {self.path}. Back it up before recovery.",
                False,
            )

        try:
            raw = json.loads(text)
        except json.JSONDecodeError:
            self._blocked = True
            return LoadResult(
                [],
                f"Task file contains malformed JSON: {self.path}. Back it up before recovery.",
                False,
            )

        if not isinstance(raw, list):
            self._blocked = True
            return LoadResult([], f"Task file has an invalid structure: {self.path}", False)

        tasks: list[Task] = []
        ids: set[int] = set()
        try:
            for item in raw:
                if not isinstance(item, dict):
                    raise TypeError("Task record must be an object")
                required = {"id", "title", "description", "priority", "tags", "status"}
                if set(item) != required:
                    raise ValueError("Task record has missing or unknown fields")

                task_id = validate_positive_id(item["id"])
                if task_id in ids:
                    raise ValueError("Task IDs must be unique")
                ids.add(task_id)
                title = validate_required_text(item["title"], "Title")
                description = validate_required_text(item["description"], "Description")
                priority = validate_priority(item["priority"])
                status = validate_status(item["status"])
                tags = normalize_tags(item["tags"])
                tasks.append(
                    Task(
                        id=task_id,
                        title=title,
                        description=description,
                        priority=priority,
                        tags=tags,
                        status=status,
                    )
                )
        except (KeyError, TypeError, ValueError, ValidationError):
            self._blocked = True
            return LoadResult(
                [],
                f"Task file has invalid task data: {self.path}. Back it up before recovery.",
                False,
            )

        self._blocked = False
        return LoadResult(tasks, None, True)

    def save(self, tasks: list[Task]) -> None:
        if self._blocked:
            raise StorageError(
                "Storage is blocked because the original JSON is malformed, unreadable, "
                "or structurally invalid. Back up and recover it before saving."
            )

        try:
            serialized = json.dumps(
                [task_to_dict(task) for task in tasks],
                ensure_ascii=False,
                indent=2,
            )
        except (TypeError, ValueError) as exc:
            raise StorageError("Tasks could not be serialized to JSON.") from exc

        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = -1
        temporary_path: Path | None = None
        try:
            fd, temp_name = tempfile.mkstemp(
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                text=True,
            )
            temporary_path = Path(temp_name)
            handle = os.fdopen(fd, "w", encoding="utf-8")
            fd = -1
            with handle:
                handle.write(serialized)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, self.path)
            temporary_path = None
        except (OSError, TypeError, ValueError) as exc:
            if fd >= 0:
                os.close(fd)
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass
            raise StorageError(
                f"Tasks could not be saved safely to {self.path}. "
                "The original file was not intentionally replaced."
            ) from exc
