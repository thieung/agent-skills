# Handoff Skill

Preserve and restore compact cross-session work context in a repo-local handoff file.

## What It Does

- Reads `.handoff/handoff.md` when starting or resuming work.
- Writes a compact handoff when wrapping up, checkpointing, or preparing the next session.
- Keeps next steps concrete enough for a fresh agent to continue quickly.

## Install

```bash
cp -r skills/handoff ~/.claude/skills/handoff
```

Or project-local:

```bash
cp -r skills/handoff /path/to/project/.claude/skills/handoff
```

## Default Handoff Path

```text
.handoff/handoff.md
```

The path is relative to the active project/repo, not the skill folder.

## Optional Config

```yaml
handoff:
  mode: ask # ask | yolo
  include_git_diff: true
  max_key_files: 20
```

Default mode is `ask`: draft first, save after approval. `yolo` writes directly.

## Optional: `/ck:watzup` Integration

Handoff is self-sufficient — it gathers git state on its own. If you happen to use `/ck:watzup` (a ClaudeKit paid skill that analyzes recent branch activity), and ran it earlier in the same conversation, handoff will reuse its summary instead of re-collecting facts. No requirement to install or run it.

## Optional SessionStart Hook

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "if [ -f .handoff/handoff.md ]; then echo '--- PRIOR HANDOFF ---'; cat .handoff/handoff.md; echo '--- END PRIOR HANDOFF ---'; else echo 'No prior handoff.'; fi"
      }
    ]
  }
}
```
