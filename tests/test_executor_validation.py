"""
Tests for executor configuration validation.

Ensures the executor task is configured correctly to force actual file creation.
"""

import yaml
from pathlib import Path


def test_executor_task_has_no_output_file():
    """Executor task must NOT have output_file — it misleads the LLM into thinking task is done."""
    tasks_config = Path("src/dev_workflow/crews/executor/config/tasks.yaml")
    with open(tasks_config) as f:
        config = yaml.safe_load(f)
    task = config["coding_task"]
    assert "output_file" not in task, (
        "output_file causes CrewAI to write summary, not real code"
    )


def test_executor_task_forces_file_writer_usage():
    """Task description must explicitly require FileWriterTool for ALL code."""
    tasks_config = Path("src/dev_workflow/crews/executor/config/tasks.yaml")
    with open(tasks_config) as f:
        config = yaml.safe_load(f)
    desc = config["coding_task"]["description"]
    assert "FileWriterTool" in desc, "Task must mention FileWriterTool explicitly"


def test_executor_task_has_mandatory_language():
    """Task must use mandatory language (must, required) to force tool usage."""
    tasks_config = Path("src/dev_workflow/crews/executor/config/tasks.yaml")
    with open(tasks_config) as f:
        config = yaml.safe_load(f)
    desc = config["coding_task"]["description"]
    assert "must" in desc.lower() or "required" in desc.lower(), (
        "Task must use mandatory language"
    )


def test_executor_agent_emphasizes_file_creation():
    """Agent goal must emphasize that FileWriterTool must be used for actual file creation."""
    agents_config = Path("src/dev_workflow/crews/executor/config/agents.yaml")
    with open(agents_config) as f:
        config = yaml.safe_load(f)
    goal = config["executor"]["goal"]
    assert "FileWriterTool" in goal, "Agent goal must mention FileWriterTool"
    assert "must" in goal.lower(), "Agent goal must use mandatory language"
