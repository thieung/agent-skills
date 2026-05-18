# Recall Skill

Recall Claude Code session history by date, topic, or session-file graph.

## Install

```bash
cp -r skills/recall ~/.claude/skills/recall
```

Set a script directory helper:

```bash
RECALL_DIR="$HOME/.claude/skills/recall"
```

## Temporal Recall

```bash
python3 "$RECALL_DIR/scripts/recall-day.py" list yesterday
python3 "$RECALL_DIR/scripts/recall-day.py" list "last week"
python3 "$RECALL_DIR/scripts/recall-day.py" expand SESSION_ID
```

## Topic Recall

Use QMD:

```bash
qmd search "authentication" -c sessions -n 5
qmd get "qmd://sessions/path/to/file.md" -l 50
```

## Graph Recall

Install graph dependencies:

```bash
python3 -m pip install -r "$RECALL_DIR/requirements.txt"
```

Generate graph:

```bash
python3 "$RECALL_DIR/scripts/session-graph.py" yesterday --no-open -o /tmp/session-graph.html
```

## Custom Paths

`recall` aligns with the `session-sync` skill. The QMD output dir defaults to `{target_folder}/Claude-Sessions/_recall/`, where `target_folder` resolves in this order:

1. `$CLAUDE_SESSIONS_TARGET_FOLDER`
2. `~/.claude/skills/session-sync/config.json` → `target_folder`
3. `$VAULT_DIR` (Obsidian vault)
4. `.obsidian/` walking up from CWD
5. `~/Documents` (matches session-sync default)

Variables:

| Variable | Default | Purpose |
|---|---|---|
| `CLAUDE_HOME` | `~/.claude` | Claude Code home |
| `CLAUDE_PROJECTS_DIR` | `$CLAUDE_HOME/projects` | Raw JSONL transcripts |
| `CLAUDE_SESSIONS_TARGET_FOLDER` | resolved chain above | Parent of `Claude-Sessions/` |
| `VAULT_DIR` | detected `.obsidian` walking up CWD | Obsidian vault root |
| `RECALL_OUTPUT_DIR` | `{target_folder}/Claude-Sessions/_recall` | Explicit override |

Override when needed:

```bash
export CLAUDE_SESSIONS_TARGET_FOLDER="$HOME/MyVault"
export CLAUDE_PROJECTS_DIR="/custom/claude/projects"
```

QMD collection name is `claude-sessions` (matches session-sync). After first extract:

```bash
qmd collection add "$RECALL_OUTPUT_DIR" --name claude-sessions
qmd update && qmd embed
```
