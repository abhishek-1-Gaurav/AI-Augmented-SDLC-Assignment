from pathlib import Path

import pytest


@pytest.fixture
def temporary_json(tmp_path: Path) -> Path:
    return tmp_path / "tasks.json"
