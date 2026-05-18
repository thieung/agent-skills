# Recall Workflow

Load context from Claude Code memory. Temporal queries use native JSONL files, topic queries use QMD search, and graph queries generate an interactive session-file graph.

## Step 1: Resolve Paths

Set the installed skill directory:

```bash
RECALL_DIR="/path/to/recall"
```

Optional environment overrides:

```bash
export CLAUDE_HOME="$HOME/.claude"
export CLAUDE_PROJECTS_DIR="$CLAUDE_HOME/projects"
export CLAUDE_SESSIONS_TARGET_FOLDER="$HOME/Documents"   # parent of Claude-Sessions/
export VAULT_DIR="/path/to/obsidian-vault"               # used if target_folder unset
export RECALL_OUTPUT_DIR=""                              # explicit override for extract-sessions output
```

Path resolution for `{target_folder}/Claude-Sessions/` (aligned with `session-sync`):

1. `$CLAUDE_SESSIONS_TARGET_FOLDER`
2. `~/.claude/skills/session-sync/config.json` → `target_folder`
3. `$VAULT_DIR`
4. `.obsidian/` walking up from CWD
5. `~/Documents` (default)

## Step 2: Classify Query

- **Graph**: starts with `graph`, e.g. `graph last week` -> Step 3C
- **Temporal**: mentions a date/range, e.g. `yesterday`, `last week`, `session history` -> Step 3A
- **Topic**: mentions a subject, e.g. `authentication`, `QMD video` -> Step 3B
- **Both**: temporal + topic, e.g. `what did I do with QMD yesterday` -> Step 3A, then scan/filter for topic

## Step 3A: Temporal Recall

```bash
python3 "$RECALL_DIR/scripts/recall-day.py" list DATE_EXPR
```

Supported date expressions:
- `today`, `yesterday`
- `YYYY-MM-DD`
- `last monday` .. `last sunday`
- `this week`, `last week`
- `N days ago`, `last N days`

Options:
- `--min-msgs N`
- `--all-projects`
- `--project PATH`

If the user picks a session:

```bash
python3 "$RECALL_DIR/scripts/recall-day.py" expand SESSION_ID
```

## Step 3B: Topic Recall

BM25 is keyword-based. Expand the query into 3-4 variants before searching.

Example:
- User says `disk clean up`
- Variants: `disk cleanup free space`, `large files storage`, `delete cache bloat GB`, `free up computer space`

Run variants across likely QMD collections:

```bash
qmd search "VARIANT_1" -c claude-sessions -n 5
qmd search "VARIANT_2" -c claude-sessions -n 5
qmd search "VARIANT_3" -c claude-sessions -n 5
qmd search "VARIANT_1" -c notes -n 5
qmd search "VARIANT_2" -c notes -n 5
qmd search "VARIANT_1" -c daily -n 3
```

Deduplicate by document path and keep highest score. Fetch the top documents:

```bash
qmd get "qmd://collection/path/to/file.md" -l 50
```

## Step 3C: Graph Recall

Strip the `graph` prefix and run:

```bash
python3 "$RECALL_DIR/scripts/session-graph.py" DATE_EXPR --no-open
```

Options:
- `--min-files N`
- `--min-msgs N`
- `--all-projects`
- `-o PATH`
- `--no-open`

If dependencies are missing:

```bash
python3 -m pip install -r "$RECALL_DIR/requirements.txt"
```

## Step 4: Present Results

Temporal:
- Show the session table.
- Offer to expand a session if useful.

Topic:
- Group by collection: sessions, notes, daily.
- Summarize dates, decisions, current state, and next steps.

Graph:
- Give output path.
- Report node/edge counts.
- Explain clusters and shared files.

## Step 5: One Thing

End with:

> **One Thing: [specific, concrete next action]**

Pick it from momentum, blockers, closeness to done, and urgency. If results are too thin to infer a useful action, skip One Thing and ask what to inspect next.
