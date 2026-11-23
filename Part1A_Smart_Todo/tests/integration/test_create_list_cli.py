import subprocess
import sys
from pathlib import Path


def test_create_list_get_delete_status_round_trip(tmp_path: Path) -> None:
    env_file = tmp_path / "tasks.json"
    base = [
        sys.executable,
        "-m",
        "smart_todo",
        "--storage",
        str(env_file),
    ]
    created = subprocess.run(
        base
        + [
            "create",
            "--id",
            "42",
            "--title",
            "Review",
            "--description",
            "Review notes",
            "--priority",
            "High",
            "--tags",
            "work,urgent",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert created.returncode == 0
    assert "Task 42 created" in created.stdout

    listed = subprocess.run(base + ["list"], check=False, capture_output=True, text=True)
    assert listed.returncode == 0
    assert "Review" in listed.stdout

    got = subprocess.run(base + ["get", "--id", "42"], check=False, capture_output=True, text=True)
    assert got.returncode == 0
    assert "Review" in got.stdout

    status = subprocess.run(
        base + ["status", "--id", "42", "--status", "Completed"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert status.returncode == 0

    deleted = subprocess.run(
        base + ["delete", "--id", "42"], check=False, capture_output=True, text=True
    )
    assert deleted.returncode == 0
