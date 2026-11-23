from pathlib import Path

import pytest

from smart_todo.models import (
    DuplicateIdError,
    Status,
    TaskNotFoundError,
    ValidationError,
)
from smart_todo.service import TaskService
from smart_todo.storage import JsonTaskStorage


@pytest.fixture
def service(tmp_path: Path) -> TaskService:
    return TaskService(JsonTaskStorage(tmp_path / "tasks.json"))


def test_create_list_get_and_empty_tags(service: TaskService) -> None:
    task = service.create(42, "Review", "Review notes", "High", ["work"])
    assert task.status == Status.PENDING
    assert service.list_tasks() == [task]
    assert service.get(42) == task
    with pytest.raises(ValidationError):
        service.create(43, "Missing tags", "Description", "Low", [])


def test_duplicate_id(service: TaskService) -> None:
    service.create(42, "First", "Description", "Low", ["work"])
    with pytest.raises(DuplicateIdError):
        service.create(42, "Second", "Description", "Low", ["work"])


def test_update_is_immutable_and_noop_does_not_change(service: TaskService) -> None:
    task = service.create(42, "Review", "Review notes", "High", ["work"])
    updated = service.update(42, priority="Medium", tags=["personal"])
    assert updated.id == task.id
    assert (
        service.update(
            42, title="Review", description="Review notes", priority="Medium", tags=["personal"]
        )
        == updated
    )


def test_update_missing_and_delete_missing(service: TaskService) -> None:
    with pytest.raises(TaskNotFoundError):
        service.update(99, title="Missing")
    with pytest.raises(TaskNotFoundError):
        service.delete(99)


def test_delete(service: TaskService) -> None:
    service.create(42, "Review", "Review notes", "High", ["work"])
    service.delete(42)
    with pytest.raises(TaskNotFoundError):
        service.get(42)


def test_and_tag_filter_and_no_matches(service: TaskService) -> None:
    service.create(1, "One", "One", "Low", ["work"])
    service.create(2, "Two", "Two", "High", ["work", "urgent"])
    assert [task.id for task in service.filter_by_tags(["work", "urgent"])] == [2]
    assert service.filter_by_tags(["personal"]) == []


def test_stable_priority_sort(service: TaskService) -> None:
    service.create(1, "Low", "Low", "Low", ["work"])
    service.create(2, "High one", "High", "High", ["work"])
    service.create(3, "Medium", "Medium", "Medium", ["work"])
    service.create(4, "High two", "High", "High", ["work"])
    assert [task.id for task in service.sort_by_priority()] == [2, 4, 3, 1]


def test_all_status_transitions_and_invalid_status(service: TaskService) -> None:
    task = service.create(42, "Review", "Review notes", "High", ["work"])
    task = service.change_status(42, "In Progress")
    task = service.change_status(42, "Completed")
    task = service.change_status(42, "Pending")
    assert task.status == Status.PENDING
    with pytest.raises(ValidationError):
        service.change_status(42, "Done")
    with pytest.raises(TaskNotFoundError):
        service.change_status(99, "Pending")
