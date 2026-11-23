import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from smart_todo.storage import JsonTaskStorage, LoadResult

__all__ = ["JsonTaskStorage", "LoadResult"]
