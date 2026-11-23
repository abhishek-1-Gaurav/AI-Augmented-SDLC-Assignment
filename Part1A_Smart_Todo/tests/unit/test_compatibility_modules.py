import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_flat_compatibility_modules_import() -> None:
    import models
    import storage
    import task_manager

    assert models.Task
    assert storage.JsonTaskStorage
    assert task_manager.TaskService
