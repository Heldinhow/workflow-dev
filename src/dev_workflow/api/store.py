"""SQLite-backed execution store with thread-safe access."""

import os
import threading
import json
from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Session, create_engine, select
from dev_workflow.models import Execution, ExecutionPhase


_lock = threading.Lock()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./workflow.db")
RETENTION_DAYS = 90

engine = create_engine(
    DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)


def _get_session():
    return Session(engine)


def init_db():
    """Create tables if they don't exist."""
    from dev_workflow.models import Execution, ExecutionPhase
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)


def _blank_phase(name: str, label: str) -> dict:
    return {
        "name": name,
        "label": label,
        "status": "pending",
        "started_at": None,
        "completed_at": None,
        "output": None,
    }


PHASES = [
    ("research", "Research"),
    ("planning", "Planning"),
    ("execution", "Execution"),
    ("review", "Review"),
    ("testing", "Testing"),
    ("deployment", "Deployment"),
]


def create(execution_id: str, feature_request: str, project_path: str) -> dict:
    with _lock:
        session = _get_session()
        try:
            execution = Execution(
                id=execution_id,
                feature_request=feature_request,
                project_path=project_path,
                status="pending",
            )
            session.add(execution)
            session.flush()

            for name, label in PHASES:
                phase = ExecutionPhase(
                    execution_id=execution_id,
                    name=name,
                    label=label,
                    status="pending",
                )
                session.add(phase)

            session.commit()

            result = session.exec(
                select(Execution).where(Execution.id == execution_id)
            ).first()
            return _execution_to_dict(result)
        finally:
            session.close()


def get(execution_id: str) -> Optional[dict]:
    with _lock:
        session = _get_session()
        try:
            result = session.exec(
                select(Execution).where(Execution.id == execution_id)
            ).first()
            return _execution_to_dict(result) if result else None
        finally:
            session.close()


def list_all() -> list[dict]:
    with _lock:
        session = _get_session()
        try:
            results = session.exec(
                select(Execution).order_by(Execution.created_at.desc())
            ).all()
            return [_execution_to_dict(ex) for ex in results]
        finally:
            session.close()


def list_all_filtered(
    status: str = None,
    phase: str = None,
    search: str = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    with _lock:
        session = _get_session()
        try:
            query = select(Execution)

            if status:
                query = query.where(Execution.status == status)
            if search:
                query = query.where(Execution.feature_request.contains(search))

            query = (
                query.order_by(Execution.created_at.desc()).offset(offset).limit(limit)
            )
            results = session.exec(query).all()
            return [_execution_to_dict(ex) for ex in results]
        finally:
            session.close()


def update(execution_id: str, **kwargs) -> None:
    with _lock:
        session = _get_session()
        try:
            execution = session.exec(
                select(Execution).where(Execution.id == execution_id)
            ).first()
            if not execution:
                return

            for key, value in kwargs.items():
                if hasattr(execution, key):
                    setattr(execution, key, value)

            session.add(execution)
            session.commit()
        finally:
            session.close()


def update_phase(execution_id: str, phase_name: str, **kwargs) -> None:
    with _lock:
        session = _get_session()
        try:
            execution = session.exec(
                select(Execution).where(Execution.id == execution_id)
            ).first()
            if not execution:
                return

            if execution.phases:
                phases = execution.phases
                for phase in phases:
                    if phase.name == phase_name:
                        for key, value in kwargs.items():
                            if hasattr(phase, key):
                                setattr(phase, key, value)
                        break
                session.add(execution)
                session.commit()
        finally:
            session.close()


def append_log(execution_id: str, entry: dict) -> None:
    with _lock:
        session = _get_session()
        try:
            execution = session.exec(
                select(Execution).where(Execution.id == execution_id)
            ).first()
            if not execution:
                return

            log = json.loads(execution.log) if execution.log else []
            log.append(entry)
            execution.log = json.dumps(log)

            session.add(execution)
            session.commit()
        finally:
            session.close()


def cleanup_old_executions() -> int:
    """Delete executions older than RETENTION_DAYS. Returns count of deleted."""
    with _lock:
        session = _get_session()
        try:
            cutoff = (datetime.now() - timedelta(days=RETENTION_DAYS)).isoformat()
            old_executions = session.exec(
                select(Execution).where(Execution.created_at < cutoff)
            ).all()

            count = len(old_executions)
            for ex in old_executions:
                session.delete(ex)
            session.commit()
            return count
        finally:
            session.close()


def _execution_to_dict(execution: Execution) -> dict:
    if not execution:
        return None

    return {
        "id": execution.id,
        "feature_request": execution.feature_request,
        "project_path": execution.project_path,
        "status": execution.status,
        "current_phase": execution.current_phase,
        "current_agent": execution.current_agent,
        "phases": [
            {
                "name": p.name,
                "label": p.label,
                "status": p.status,
                "started_at": p.started_at,
                "completed_at": p.completed_at,
                "output": p.output,
            }
            for p in execution.phases
        ]
        if execution.phases
        else [],
        "retry_count": execution.retry_count,
        "max_retries": execution.max_retries,
        "test_retry_count": execution.test_retry_count,
        "max_test_retries": execution.max_test_retries,
        "errors": json.loads(execution.errors) if execution.errors else [],
        "log": json.loads(execution.log) if execution.log else [],
        "token_usage": json.loads(execution.token_usage)
        if execution.token_usage
        else {},
        "cancelled_at": execution.cancelled_at,
        "github_pr_url": execution.github_pr_url,
        "github_branch": execution.github_branch,
        "linear_issue_id": execution.linear_issue_id,
        "linear_issue_url": execution.linear_issue_url,
        "workspace_mode": execution.workspace_mode,
        "github_repo": execution.github_repo,
        "created_at": execution.created_at,
        "started_at": execution.started_at,
        "completed_at": execution.completed_at,
    }
