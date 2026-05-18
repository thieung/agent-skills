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

## Modes

| Mode | Needs session-sync? | Source |
|---|---|---|
| Temporal | No | JSONL at `~/.claude/projects/` |
| Topic    | **Yes** (for QMD index) | QMD collection `claude-sessions` |
| Graph    | No | JSONL at `~/.claude/projects/` |

Temporal and Graph read JSONL directly. Topic search reuses the QMD index maintained by `session-sync`.

## Temporal Recall

```bash
python3 "$RECALL_DIR/scripts/recall-day.py" list yesterday
python3 "$RECALL_DIR/scripts/recall-day.py" list "last week"
python3 "$RECALL_DIR/scripts/recall-day.py" expand SESSION_ID
```

## Topic Recall

Topic mode requires the `session-sync` skill installed and indexed. Setup once:

```bash
SS="$HOME/.claude/skills/session-sync/scripts/session-sync.py"
python3 "$SS" export --all
python3 "$SS" index
```

Then search via QMD:

```bash
qmd search "authentication" -c claude-sessions -n 5
qmd get "qmd://claude-sessions/path/to/file.md" -l 50
```

Workflow rule: agent expands the user query into 3-4 keyword variants before searching (BM25 needs exact-ish terms), then dedupes results by path.

## Graph Recall

Install graph dependencies:

```bash
python3 -m pip install -r "$RECALL_DIR/requirements.txt"
```

Generate graph:

```bash
python3 "$RECALL_DIR/scripts/session-graph.py" yesterday --no-open
```

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `CLAUDE_HOME` | `~/.claude` | Claude Code home |
| `CLAUDE_PROJECTS_DIR` | `$CLAUDE_HOME/projects` | Raw JSONL transcripts |
| `VAULT_DIR` | detected `.obsidian` walking up CWD | Obsidian vault root, used by graph mode to normalize file paths |

```bash
export CLAUDE_PROJECTS_DIR="/custom/claude/projects"
export VAULT_DIR="$HOME/MyVault"
```

## Semantic Search

When BM25 keyword search returns weak results, fall back to vector search via session-sync:

```bash
python3 "$SS" vsearch "how did we fix the database issue" -n 5
```
