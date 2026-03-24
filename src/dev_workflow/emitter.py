"""
Module-level event emitter — zero dependency on the API layer.
The flow emits events here; the API registers a handler to forward them.
"""

from datetime import datetime
from typing import Callable

_handlers: list[Callable] = []


def register(handler: Callable) -> None:
    _handlers.append(handler)


def unregister(handler: Callable) -> None:
    if handler in _handlers:
        _handlers.remove(handler)


def emit(
    execution_id: str,
    event_type: str,
    phase: str,
    message: str,
    data: dict | None = None,
) -> None:
    if not _handlers or not execution_id:
        return
    event = {
        "execution_id": execution_id,
        "type": event_type,
        "phase": phase,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now().isoformat(),
    }
    for handler in _handlers:
        try:
            handler(event)
        except Exception:
            pass
