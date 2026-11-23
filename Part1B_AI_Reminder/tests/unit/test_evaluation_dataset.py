import json

import pytest

from ai_reminder_agent.evaluation_dataset import DatasetLoadError, load_dataset


def test_loads_all_29_frozen_cases_with_baseline_context(dataset) -> None:
    assert len(dataset.cases) == 29
    assert dataset.cases[0].context.reference_datetime.isoformat() == (
        "2026-11-23T09:00:00+05:30"
    )
    assert dataset.cases[0].context.timezone == "Asia/Kolkata"


def test_duplicate_case_ids_are_rejected(tmp_path) -> None:
    document = {
        "dataset_version": "test",
        "default_context": {
            "reference_datetime": None,
            "timezone": None,
            "known_reminders": [],
        },
        "cases": [
            {
                "case_id": "EVAL-01",
                "kind": "request",
                "category": ["normal"],
                "request": "Remind me.",
                "expected": {"intent": "CLARIFY"},
            },
            {
                "case_id": "EVAL-01",
                "kind": "request",
                "category": ["normal"],
                "request": "Remind me.",
                "expected": {"intent": "CLARIFY"},
            },
        ],
    }
    path = tmp_path / "duplicate.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(DatasetLoadError, match="Duplicate evaluation case ID"):
        load_dataset(path)

