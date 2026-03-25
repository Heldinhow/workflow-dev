# AGENTS.md - Ralph Agent Configuration

This file configures how ralph-starter runs coding agents.

## OpenCode Agent

To use opencode directly (not the SDK), set the AGENT_CMD environment variable:

```bash
export AGENT_CMD="opencode run --"
```

Or create this agents.json:

```json
{
  "agents": {
    "opencode": {
      "command": "opencode run --",
      "description": "OpenCode CLI with -- separator"
    }
  }
}
```

## Alternative: Use Claude Code instead

If OpenCode continues to have issues, use Claude Code:

```bash
ralph-starter run --from github --project Heldinhow/workflow-dev --issue 21 --agent claude-code --commit
```

Claude Code is the recommended agent in ralph-starter and tends to work more reliably.
