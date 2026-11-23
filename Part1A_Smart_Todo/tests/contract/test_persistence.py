from pathlib import Path

from smart_todo.service import TaskService
from smart_todo.storage import JsonTaskStorage


def test_task_survives_repeated_service_instances(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    first = TaskService(JsonTaskStorage(path))
    first.create(42, "Review", "Review notes", "High", ["work"])

    second = TaskService(JsonTaskStorage(path))
    assert second.get(42).title == "Review"
