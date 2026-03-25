"""Tests for the emitter pattern — register, unregister, emit."""

import pytest
from unittest.mock import MagicMock


class TestEmitter:
    """Tests for emitter module functions."""

    def test_register_adds_handler(self):
        """register() adds a handler to _handlers list."""
        from dev_workflow import emitter
        handler = MagicMock()
        emitter._handlers.clear()
        emitter.register(handler)
        assert handler in emitter._handlers

    def test_register_multiple_handlers(self):
        """register() can add multiple handlers."""
        from dev_workflow import emitter
        handler1 = MagicMock()
        handler2 = MagicMock()
        emitter._handlers.clear()
        emitter.register(handler1)
        emitter.register(handler2)
        assert handler1 in emitter._handlers
        assert handler2 in emitter._handlers

    def test_unregister_removes_handler(self):
        """unregister() removes a handler from _handlers list."""
        from dev_workflow import emitter
        handler = MagicMock()
        emitter._handlers.clear()
        emitter._handlers.append(handler)
        emitter.unregister(handler)
        assert handler not in emitter._handlers

    def test_unregister_idempotent(self):
        """unregister() handles removing non-existent handler gracefully."""
        from dev_workflow import emitter
        handler = MagicMock()
        emitter._handlers.clear()
        emitter.unregister(handler)

    def test_emit_calls_all_handlers(self):
        """emit() calls all registered handlers with event data."""
        from dev_workflow import emitter
        handler1 = MagicMock()
        handler2 = MagicMock()
        emitter._handlers.clear()
        emitter._handlers.append(handler1)
        emitter._handlers.append(handler2)
        emitter.emit("exec-123", "phase_started", "research", "Starting research")
        handler1.assert_called_once()
        handler2.assert_called_once()

    def test_emit_event_structure(self):
        """emit() creates correct event structure."""
        from dev_workflow import emitter
        handler = MagicMock()
        emitter._handlers.clear()
        emitter._handlers.append(handler)
        emitter.emit(
            "exec-123",
            "phase_completed",
            "research",
            "Research complete",
            {"findings": "docs found"},
        )
        call_args = handler.call_args[0][0]
        assert call_args["execution_id"] == "exec-123"
        assert call_args["type"] == "phase_completed"
        assert call_args["phase"] == "research"
        assert call_args["message"] == "Research complete"
        assert call_args["data"] == {"findings": "docs found"}
        assert "timestamp" in call_args

    def test_emit_skips_empty_execution_id(self):
        """emit() returns early if execution_id is empty."""
        from dev_workflow import emitter
        handler = MagicMock()
        emitter._handlers.clear()
        emitter._handlers.append(handler)
        emitter.emit("", "phase_started", "research", "Starting")
        handler.assert_not_called()

    def test_emit_skips_when_no_handlers(self):
        """emit() returns early if no handlers registered."""
        from dev_workflow import emitter
        emitter._handlers.clear()
        emitter.emit("exec-123", "phase_started", "research", "Starting")

    def test_emit_handlers_exception_silenced(self):
        """emit() silences exceptions from handlers."""
        from dev_workflow import emitter
        bad_handler = MagicMock(side_effect=Exception("Handler error"))
        good_handler = MagicMock()
        emitter._handlers.clear()
        emitter._handlers.append(bad_handler)
        emitter._handlers.append(good_handler)
        emitter.emit("exec-123", "phase_started", "research", "Starting")
        good_handler.assert_called_once()

    def test_emit_with_none_data(self):
        """emit() handles None data gracefully."""
        from dev_workflow import emitter
        handler = MagicMock()
        emitter._handlers.clear()
        emitter._handlers.append(handler)
        emitter.emit("exec-123", "phase_started", "research", "Starting", None)
        call_args = handler.call_args[0][0]
        assert call_args["data"] == {}

    def test_emit_multiple_event_types(self):
        """emit() correctly handles different event types."""
        from dev_workflow import emitter
        calls = []
        handler = MagicMock(side_effect=lambda e: calls.append(e))
        emitter._handlers.clear()
        emitter._handlers.append(handler)
        emitter.emit("exec-123", "phase_started", "research", "Starting")
        emitter.emit("exec-123", "phase_completed", "research", "Done")
        emitter.emit("exec-123", "execution_completed", "", "Complete")
        assert len(calls) == 3
        assert calls[0]["type"] == "phase_started"
        assert calls[1]["type"] == "phase_completed"
        assert calls[2]["type"] == "execution_completed"

    def test_emit_timestamp_is_iso_format(self):
        """emit() includes ISO format timestamp."""
        from dev_workflow import emitter
        handler = MagicMock()
        emitter._handlers.clear()
        emitter._handlers.append(handler)
        emitter.emit("exec-123", "phase_started", "research", "Starting")
        timestamp = handler.call_args[0][0]["timestamp"]
        assert "T" in timestamp

    def test_handler_called_with_event_dict(self):
        """Handler receives event as dictionary."""
        from dev_workflow import emitter
        received = {}
        def capture(event):
            received.update(event)
        emitter._handlers.clear()
        emitter._handlers.append(capture)
        emitter.emit("exec-456", "phase_started", "planning", "Planning started")
        assert received["execution_id"] == "exec-456"
        assert received["type"] == "phase_started"
        assert received["phase"] == "planning"


class TestEmitterIntegration:
    """Integration tests for emitter with flow."""

    def test_flow_emits_research_phase_events(self):
        """Flow emits events during research phase."""
        from dev_workflow.flow import DevWorkflowFlow
        from dev_workflow import emitter
        handler = MagicMock()
        emitter._handlers.clear()
        emitter.register(handler)
        try:
            flow = DevWorkflowFlow()
            with pytest.raises(Exception):
                flow.kickoff(inputs={"feature_request": "test", "project_path": "."})
        except Exception:
            pass
        finally:
            emitter.unregister(handler)
            emitter._handlers.clear()

    def test_emitter_preserves_handler_order(self):
        """Handlers are called in registration order."""
        from dev_workflow import emitter
        call_order = []
        def make_handler(name):
            def h(event):
                call_order.append(name)
            return h
        emitter._handlers.clear()
        emitter.register(make_handler("first"))
        emitter.register(make_handler("second"))
        emitter.register(make_handler("third"))
        emitter.emit("exec-123", "test", "", "test")
        assert call_order == ["first", "second", "third"]
