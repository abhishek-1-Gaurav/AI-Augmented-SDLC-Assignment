import subprocess
import sys
from pathlib import Path


def run_cli(storage: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "smart_todo", "--storage", str(storage), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_update_filter_sort_and_status_cli(tmp_path: Path) -> None:
    storage = tmp_path / "tasks.json"
    for task_id, priority in ((1, "Low"), (2, "High"), (3, "High")):
        tags = "work,urgent" if task_id == 2 else "work"
        result = run_cli(
            storage,
            "create",
            "--id",
            str(task_id),
            "--title",
            f"Task {task_id}",
            "--description",
            "Description",
            "--priority",
            priority,
            "--tags",
            tags,
        )
        assert result.returncode == 0

    updated = run_cli(
        storage,
        "update",
        "--id",
        "1",
        "--priority",
        "High",
        "--tags",
        "work,urgent",
    )
    assert updated.returncode == 0

    filtered = run_cli(storage, "filter", "--tags", "work,urgent")
    assert filtered.returncode == 0
    assert "Task 1" in filtered.stdout
    assert "Task 2" in filtered.stdout
    assert "Task 3" not in filtered.stdout

    sorted_result = run_cli(storage, "sort", "--priority")
    assert sorted_result.returncode == 0
    assert sorted_result.stdout.find("Task 1") < sorted_result.stdout.find("Task 2")

    status = run_cli(
        storage,
        "status",
        "--id",
        "2",
        "--status",
        "In Progress",
    )
    assert status.returncode == 0

    completed = run_cli(
        storage,
        "status",
        "--id",
        "2",
        "--status",
        "Completed",
    )
    assert completed.returncode == 0

    pending = run_cli(
        storage,
        "status",
        "--id",
        "2",
        "--status",
        "Pending",
    )
    assert pending.returncode == 0
