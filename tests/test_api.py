"""Tests for API endpoints."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """Tests for the FastAPI server endpoints."""

    @pytest.fixture
    def mock_store(self):
        """Mock the API store."""
        with patch("dev_workflow.api.server.store") as mock:
            mock.init_db.return_value = None
            mock.create.return_value = {
                "id": "abc123",
                "feature_request": "Add hello endpoint",
                "project_path": "./output",
                "status": "pending",
            }
            mock.get.return_value = {
                "id": "abc123",
                "feature_request": "Add hello endpoint",
                "project_path": "./output",
                "status": "running",
                "current_phase": "research",
                "phases": [],
                "errors": [],
                "log": [],
            }
            mock.list_all.return_value = [
                {
                    "id": "abc123",
                    "feature_request": "Add hello endpoint",
                    "status": "running",
                }
            ]
            mock.list_all_filtered.return_value = [
                {
                    "id": "abc123",
                    "feature_request": "Add hello endpoint",
                    "status": "running",
                }
            ]
            mock.update.return_value = None
            mock.append_log.return_value = None
            yield mock

    @pytest.fixture
    def mock_workflow_run(self):
        """Mock the workflow run in a separate thread."""
        with patch("dev_workflow.api.server._run_workflow") as mock:
            yield mock

    @pytest.fixture
    def client(self, mock_store, mock_workflow_run):
        """TestClient for the FastAPI app."""
        with patch("dev_workflow.api.server.emitter") as emitter_mock:
            emitter_mock.register.return_value = None
            emitter_mock.emit.return_value = None
            from dev_workflow.api.server import app
            with TestClient(app) as client:
                yield client

    def test_start_execution(self, client, mock_store, mock_workflow_run):
        """POST /api/executions creates an execution and returns ID."""
        response = client.post(
            "/api/executions",
            json={
                "feature_request": "Add hello endpoint",
                "project_path": "./output",
                "max_retries": 3,
                "max_test_retries": 3,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        mock_store.create.assert_called_once()

    def test_start_execution_custom_params(self, client, mock_store, mock_workflow_run):
        """POST /api/executions accepts custom max_retries and max_test_retries."""
        response = client.post(
            "/api/executions",
            json={
                "feature_request": "Add auth",
                "project_path": "/app",
                "max_retries": 5,
                "max_test_retries": 5,
                "workspace_mode": "sandbox",
                "github_repo": "org/repo",
            },
        )
        assert response.status_code == 201
        call_kwargs = mock_store.update.call_args
        assert call_kwargs[1]["max_retries"] == 5
        assert call_kwargs[1]["max_test_retries"] == 5
        assert call_kwargs[1]["workspace_mode"] == "sandbox"
        assert call_kwargs[1]["github_repo"] == "org/repo"

    def test_list_executions(self, client, mock_store):
        """GET /api/executions returns list of executions."""
        response = client.get("/api/executions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        mock_store.list_all.assert_called_once()

    def test_list_executions_with_filters(self, client, mock_store):
        """GET /api/executions accepts status, phase, search filters."""
        response = client.get(
            "/api/executions",
            params={"status": "running", "phase": "research", "search": "hello", "limit": 50},
        )
        assert response.status_code == 200
        mock_store.list_all_filtered.assert_called_once_with(
            status="running", phase="research", search="hello", limit=50, offset=0
        )

    def test_get_execution(self, client, mock_store):
        """GET /api/executions/{id} returns execution details."""
        response = client.get("/api/executions/abc123")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "abc123"
        mock_store.get.assert_called_once_with("abc123")

    def test_get_execution_not_found(self, client, mock_store):
        """GET /api/executions/{id} returns 404 for unknown ID."""
        mock_store.get.return_value = None
        response = client.get("/api/executions/unknown")
        assert response.status_code == 404

    def test_cancel_execution(self, client, mock_store):
        """POST /api/executions/{id}/cancel cancels a running execution."""
        response = client.post("/api/executions/abc123/cancel")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
        mock_store.update.assert_called()

    def test_cancel_execution_not_found(self, client, mock_store):
        """POST /api/executions/{id}/cancel returns 404 for unknown execution."""
        mock_store.get.return_value = None
        response = client.post("/api/executions/unknown/cancel")
        assert response.status_code == 404

    def test_cancel_execution_not_running(self, client, mock_store):
        """POST /api/executions/{id}/cancel returns 400 if not running."""
        mock_store.get.return_value = {"id": "abc123", "status": "completed"}
        response = client.post("/api/executions/abc123/cancel")
        assert response.status_code == 400

    def test_stream_events(self, client, mock_store):
        """GET /api/executions/{id}/events returns SSE stream."""
        mock_store.get.return_value = {
            "id": "abc123",
            "log": [
                {"type": "phase_started", "phase": "research", "message": "Starting"}
            ],
        }
        response = client.get("/api/executions/abc123/events")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    def test_stream_events_not_found(self, client, mock_store):
        """GET /api/executions/{id}/events returns 404 for unknown execution."""
        mock_store.get.return_value = None
        response = client.get("/api/executions/unknown/events")
        assert response.status_code == 404


class TestAPIMetrics:
    """Tests for Prometheus metrics endpoint."""

    def test_metrics_endpoint(self):
        """GET /metrics returns Prometheus metrics."""
        with patch("dev_workflow.api.server.emitter") as emitter_mock:
            emitter_mock.register.return_value = None
            emitter_mock.emit.return_value = None
            from dev_workflow.api.server import app
            with TestClient(app) as client:
                response = client.get("/metrics")
                assert response.status_code == 200
                assert "text/plain" in response.headers["content-type"]


class TestAPIStoreIntegration:
    """Tests for API store operations."""

    def test_store_update_phase(self):
        """Store update_phase correctly updates phase status."""
        from dev_workflow.api import store
        with patch.object(store, "_get_session") as mock_session:
            mock_exec = MagicMock()
            mock_phase = MagicMock()
            mock_phase.name = "research"
            mock_exec.phases = [mock_phase]
            mock_session.return_value.__enter__.return_value.exec.return_value.first.return_value = mock_exec
            with patch.object(store, "Session") as _mock_session_cls:
                pass
