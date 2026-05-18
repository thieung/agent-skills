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

Defaults:
- `CLAUDE_HOME=$HOME/.claude`
- `CLAUDE_PROJECTS_DIR=$CLAUDE_HOME/projects`

Override when needed:

```bash
export CLAUDE_PROJECTS_DIR="/path/to/claude/projects"
export VAULT_DIR="/path/to/vault-or-repo"
```
