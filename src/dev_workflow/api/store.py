"""In-memory execution store with thread-safe access."""

import threading
from datetime import datetime
from typing import Optional

_lock = threading.Lock()
_executions: dict[str, dict] = {}

PHASES = [
    ("research",   "Research"),
    ("planning",   "Planning"),
    ("execution",  "Execution"),
    ("review",     "Review"),
    ("testing",    "Testing"),
    ("deployment", "Deployment"),
]


def _blank_phase(name: str, label: str) -> dict:
    return {
        "name": name,
        "label": label,
        "status": "pending",
        "started_at": None,
        "completed_at": None,
        "output": None,
    }


def create(execution_id: str, feature_request: str, project_path: str) -> dict:
    ex = {
        "id": execution_id,
        "feature_request": feature_request,
        "project_path": project_path,
        "status": "pending",
        "current_phase": None,
        "current_agent": None,
        "phases": [_blank_phase(n, l) for n, l in PHASES],
        "retry_count": 0,
        "max_retries": 3,
        "test_retry_count": 0,
        "max_test_retries": 3,
        "errors": [],
        "log": [],
        "created_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None,
    }
    with _lock:
        _executions[execution_id] = ex
    return ex


def get(execution_id: str) -> Optional[dict]:
    return _executions.get(execution_id)


def list_all() -> list[dict]:
    with _lock:
        return sorted(_executions.values(), key=lambda x: x["created_at"], reverse=True)


def update(execution_id: str, **kwargs) -> None:
    with _lock:
        if execution_id in _executions:
            _executions[execution_id].update(kwargs)


def update_phase(execution_id: str, phase_name: str, **kwargs) -> None:
    with _lock:
        if execution_id not in _executions:
            return
        for phase in _executions[execution_id]["phases"]:
            if phase["name"] == phase_name:
                phase.update(kwargs)
                break


def append_log(execution_id: str, entry: dict) -> None:
    with _lock:
        if execution_id in _executions:
            _executions[execution_id]["log"].append(entry)
