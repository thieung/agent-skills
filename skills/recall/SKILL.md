---
name: recall
description: Load context from Claude Code session history. Temporal queries use native JSONL timelines, topic queries use QMD BM25 search, and "recall graph" creates an interactive session-file graph. Use when users say "recall", "what did we work on", "load context about", "remember when we", "prime context", "yesterday", "what was I doing", "last week", "session history", "recall graph", "session graph", or ask to visualize session relationships.
version: 1.0.0
license: MIT
argument-hint: [yesterday|today|last week|this week|TOPIC|graph DATE_EXPR]
allowed-tools:
  - Bash
---

# Recall

Recall has three modes:

- **Temporal**: date-based session timeline from Claude Code JSONL files.
- **Topic**: BM25 search across QMD collections.
- **Graph**: interactive HTML graph of sessions and files touched.

Every recall response should end with **One Thing** when there is enough signal: the single highest-leverage next action synthesized from the results.

## Script Paths

Do not assume cwd is the skill directory. Resolve the installed skill path first:

```bash
RECALL_DIR="/path/to/recall"
python3 "$RECALL_DIR/scripts/recall-day.py" list yesterday
```

Common installed paths:

- Global Claude Code skill: `~/.claude/skills/recall`
- Project skill: `.claude/skills/recall`
- This repository: `skills/recall`

## Configuration

Defaults work for standard Claude Code installs:

| Variable | Default | Purpose |
|----------|---------|---------|
| `CLAUDE_HOME` | `~/.claude` | Claude Code home |
| `CLAUDE_PROJECTS_DIR` | `$CLAUDE_HOME/projects` | JSONL session directory |
| `VAULT_DIR` | detected from cwd if `.obsidian` exists | Obsidian vault root, used by graph mode to normalize file paths |

Topic search uses the QMD collection `claude-sessions` maintained by the `session-sync` skill. Install and index session-sync first (see "QMD Index" below).

Graph mode requires Python packages in `requirements.txt`:

```bash
python3 -m pip install -r "$RECALL_DIR/requirements.txt"
```

## Temporal Recall

```bash
python3 "$RECALL_DIR/scripts/recall-day.py" list yesterday
python3 "$RECALL_DIR/scripts/recall-day.py" list "last week"
python3 "$RECALL_DIR/scripts/recall-day.py" list 2026-02-25
python3 "$RECALL_DIR/scripts/recall-day.py" expand SESSION_ID
```

Options:

- `--min-msgs N`: filter short/noisy sessions.
- `--all-projects`: scan all projects.
- `--project PATH`: scan one project directory or source path.

## Topic Recall

Use QMD BM25 search. Expand the user query into 3-4 keyword variants because BM25 needs exact-ish terms.

```bash
qmd search "VARIANT_1" -c sessions -n 5
qmd search "VARIANT_2" -c sessions -n 5
qmd search "VARIANT_1" -c notes -n 5
qmd search "VARIANT_1" -c daily -n 3
qmd get "qmd://collection/path/to/file.md" -l 50
```

Deduplicate by document path and present the top unique results.

## Graph Recall

```bash
python3 "$RECALL_DIR/scripts/session-graph.py" yesterday --no-open
python3 "$RECALL_DIR/scripts/session-graph.py" "last week" --min-files 5 --no-open -o "$RECALL_DIR/output/session-graph.html"
```

Tell the user the output path, node/edge counts, and what clusters/shared files indicate.

## QMD Index

The QMD collection `claude-sessions` is owned by `session-sync`. Run once:

```bash
SS="$HOME/.claude/skills/session-sync/scripts/session-sync.py"
python3 "$SS" export --all
python3 "$SS" index
```

The `Stop` hook (see `session-sync/procedures/setup-hook.md`) keeps the collection fresh automatically.

## Workflow

Read `workflows/recall.md` for routing logic and response shape.
