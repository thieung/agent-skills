---
name: session-sync
description: Export Claude Code JSONL sessions to searchable markdown with lifecycle management and optional QMD indexing. Use when users ask to sync, export, browse, resume, search, back up, or annotate Claude Code session history.
version: 1.0.0
license: MIT
allowed-tools:
  - Bash
---

# Session Sync

Export Claude Code sessions to project-organized markdown under `{target_folder}/Claude-Sessions/{project}/`. The script supports full conversation export, QMD keyword/semantic search, lifecycle annotations, resume helpers, skills detection, artifacts, and re-sync preservation.

## Script Path

Do not assume the agent's cwd is the skill directory. Resolve the script path from the installed skill location:

```bash
SCRIPT="/path/to/session-sync/scripts/session-sync.py"
python3 "$SCRIPT" status
```

Common installed paths:

- Global Claude Code skill: `~/.claude/skills/session-sync/scripts/session-sync.py`
- Project skill: `.claude/skills/session-sync/scripts/session-sync.py`
- This repository: `skills/session-sync/scripts/session-sync.py`

## Commands

| Command | Description |
|---------|-------------|
| `setup` | Print setup steps for the current script path |
| `status` | Show target folder, Claude projects dir, QMD status, exports, hook status |
| `sync` | Sync current session from Stop hook stdin or `CK_SESSION_ID` / `CLAUDE_SESSION_ID` |
| `export` | Export sessions. Filters: `--all`, `--days N`, `--project NAME`, `--since YYYY-MM-DD` |
| `config` | Set `--target-folder`, `--claude-home`, `--projects-dir`, `--settings-file`, `--auto-sync`, `--collection-name` |
| `list-projects` | List available Claude Code project directories and session counts |
| `list` | Browse exported sessions. `--active` default, `--all`, `--json` |
| `resume` | Resume in Claude Code. Use `--pick`, `--active`, `--fork`, `--all`, or pass a markdown file path |
| `note TEXT` | Append timestamped note to a session. Supports `--session-id` |
| `close [TEXT]` | Mark a session `done` with optional closing note. Supports `--session-id` |
| `log [TEXT]` | Update lifecycle fields. Supports `--status`, `--tags`, `--rating`, `--session-id` |
| `index` | Re-index exported sessions in QMD |
| `search QUERY` | BM25 keyword search via QMD. Use `-n` for result count |
| `vsearch QUERY` | Semantic vector search via QMD. Use `-n` for result count |

## Generic Configuration

Config lives beside the skill at `config.json`.

| Key | Default | Description |
|-----|---------|-------------|
| `target_folder` | `~/Documents` when empty | Parent folder for `Claude-Sessions/` |
| `claude_home` | `~/.claude` when empty | Claude Code home directory |
| `projects_dir` | `{claude_home}/projects` when empty | JSONL transcript directory |
| `settings_file` | `{claude_home}/settings.json` when empty | Settings file used to detect hook status |
| `qmd_path` | `qmd` when empty | QMD executable name/path |
| `collection_name` | `claude-sessions` | QMD collection name |
| `auto_sync` | `false` | Declarative flag updated after hook setup |

Examples:

```bash
python3 "$SCRIPT" config --target-folder "$HOME/Documents"
python3 "$SCRIPT" config --claude-home "$HOME/.claude"
python3 "$SCRIPT" config --projects-dir "/custom/claude/projects"
python3 "$SCRIPT" config --settings-file "/custom/claude/settings.json"
```

## Core Procedures

Use `procedures/setup.md` for first-time setup, `procedures/setup-hook.md` for Stop hook setup, and `procedures/install-qmd.md` for QMD installation.

### Export

```bash
python3 "$SCRIPT" export --all
python3 "$SCRIPT" export --days 30
python3 "$SCRIPT" list-projects
python3 "$SCRIPT" export --project my-project
python3 "$SCRIPT" export --since 2026-04-01
```

### Browse, Resume, Annotate

```bash
python3 "$SCRIPT" list --active
python3 "$SCRIPT" list --all
python3 "$SCRIPT" resume --pick
python3 "$SCRIPT" resume --active
python3 "$SCRIPT" note "Follow-up context"
python3 "$SCRIPT" log --status blocked --tags "handoff,debugging" "Waiting for access"
python3 "$SCRIPT" close "Done"
```

Status values: `active`, `done`, `blocked`, `handoff`.

### Search

```bash
python3 "$SCRIPT" index
python3 "$SCRIPT" search "authentication" -n 10
python3 "$SCRIPT" vsearch "how did we fix the database issue" -n 5
```

## Output

Markdown files are written to:

```text
{target_folder}/Claude-Sessions/{project-name}/YYYY-MM-DD-HHMM-{session_id_prefix}.md
```

Re-export preserves `title`, `status`, `tags`, `rating`, `comments`, and `## My Notes`. Fresh extraction updates messages, timestamps, conversation, summary, skills, and artifacts. Conversation content is not truncated.

## References

- `procedures/setup.md` - First-time setup
- `procedures/setup-hook.md` - Stop hook configuration
- `procedures/install-qmd.md` - QMD installation
- `references/schema.md` - Exported markdown schema
- `schema/tags.yaml` - Suggested lifecycle tags
