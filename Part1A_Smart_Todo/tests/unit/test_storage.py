import json
from pathlib import Path
from unittest.mock import patch

import pytest

from smart_todo.models import StorageError
from smart_todo.storage import JsonTaskStorage


def test_missing_file_loads_empty_and_allows_first_save(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    storage = JsonTaskStorage(path)
    result = storage.load()
    assert result.tasks == []
    assert result.warning
    assert result.can_save


def test_malformed_json_is_preserved_and_save_is_blocked(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    original = b"{not-json"
    path.write_bytes(original)
    storage = JsonTaskStorage(path)
    result = storage.load()
    assert result.tasks == []
    assert result.warning
    assert not result.can_save
    with pytest.raises(StorageError):
        storage.save([])
    assert path.read_bytes() == original


def test_structurally_invalid_json_is_preserved(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    original = json.dumps([{"id": 1, "title": "", "status": "Unknown"}]).encode()
    path.write_bytes(original)
    storage = JsonTaskStorage(path)
    result = storage.load()
    assert result.tasks == []
    assert not result.can_save
    assert result.warning
    with pytest.raises(StorageError):
        storage.save([])
    assert path.read_bytes() == original


def test_unreadable_file_is_preserved_and_save_is_blocked(
    tmp_path: Path,
) -> None:
    path = tmp_path / "tasks.json"
    path.write_text("[]", encoding="utf-8")
    storage = JsonTaskStorage(path)
    with patch.object(Path, "read_text", side_effect=PermissionError("unreadable")):
        result = storage.load()
    assert result.tasks == []
    assert not result.can_save
    assert result.warning
    with pytest.raises(StorageError):
        storage.save([])
    assert path.read_text(encoding="utf-8") == "[]"


def test_failed_atomic_write_preserves_original_and_cleans_temporary(
    tmp_path: Path,
) -> None:
    path = tmp_path / "tasks.json"
    path.write_text("[]", encoding="utf-8")
    storage = JsonTaskStorage(path)
    storage.load()
    with (
        patch("smart_todo.storage.os.replace", side_effect=OSError("replace failed")),
        pytest.raises(StorageError),
    ):
        storage.save([])
    assert path.read_text(encoding="utf-8") == "[]"
    assert list(tmp_path.iterdir()) == [path]


def test_failed_temporary_write_preserves_original(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    original = '[{"id":1}]'
    path.write_text(original, encoding="utf-8")
    storage = JsonTaskStorage(path)
    with (
        patch("smart_todo.storage.os.fdopen", side_effect=OSError("write failed")),
        pytest.raises(StorageError),
    ):
        storage.save([])
    assert path.read_text(encoding="utf-8") == original


def test_successful_atomic_save_and_reload(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    storage = JsonTaskStorage(path)
    from smart_todo.models import Priority, Status, Task

    task = Task(
        id=42,
        title="Review",
        description="Review notes",
        priority=Priority.HIGH,
        tags=("work",),
        status=Status.PENDING,
    )
    storage.save([task])
    assert storage.load().tasks == [task]
    assert not list(tmp_path.glob("*.tmp"))
