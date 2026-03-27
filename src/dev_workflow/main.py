"""Entry point for the Dev Workflow."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent.parent / ".env")

from dev_workflow.flow import DevWorkflowFlow  # noqa: E402


def run(feature_request: str | None = None, project_path: str = "./output"):
    """
    Run the automated dev workflow.

    Args:
        feature_request: Description of the feature to implement.
                         If None, reads from CLI args or prompts the user.
        project_path:    Directory where the code will be written.
    """
    if not feature_request:
        if len(sys.argv) > 1:
            feature_request = " ".join(sys.argv[1:])
        else:
            feature_request = input("🤖 What feature should I implement?\n> ").strip()

    if not feature_request:
        print("ERROR: Feature request cannot be empty.")
        sys.exit(1)

    # Ensure output directory exists
    os.makedirs(project_path, exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    print("\n" + "=" * 60)
    print("🤖 AUTOMATED DEV WORKFLOW")
    print("=" * 60)
    print(f"Feature: {feature_request}")
    print(f"Output:  {project_path}")
    print(f"Model:   MiniMax {os.getenv('MINIMAX_MODEL', 'MiniMax-M2.1')}")
    print("=" * 60 + "\n")

    flow = DevWorkflowFlow()
    flow.kickoff(
        inputs={
            "feature_request": feature_request,
            "project_path": project_path,
        }
    )

    # Print final state summary
    state = flow.state
    print("\n" + "=" * 60)
    print("📊 WORKFLOW SUMMARY")
    print("=" * 60)
    print(f"Review iterations:  {state.review_iteration}")
    print(f"Test iterations:    {state.test_iteration}")
    print(f"Review passed:      {'✅' if state.review_passed else '❌'}")
    print(f"Tests passed:       {'✅' if state.tests_passed else '❌'}")
    print(f"Deployed:           {'✅' if state.deploy_succeeded else '❌'}")
    if state.errors:
        print("\nErrors encountered:")
        for err in state.errors:
            print(f"  - {err}")
    print("\nTimestamps:")
    for phase, ts in state.timestamps.items():
        print(f"  {phase}: {ts}")


if __name__ == "__main__":
    run()
