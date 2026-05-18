# Session Sync Skill

Export Claude Code JSONL sessions to searchable markdown with lifecycle metadata.

## Install

Copy this skill into a Claude Code skills directory:

```bash
cp -r skills/session-sync ~/.claude/skills/session-sync
```

Or keep it in a project-local skills folder:

```bash
cp -r skills/session-sync /path/to/project/.claude/skills/session-sync
```

## Configure

Set the script path for your install:

```bash
SCRIPT="$HOME/.claude/skills/session-sync/scripts/session-sync.py"
```

Default paths:
- Claude home: `~/.claude`
- Claude projects: `~/.claude/projects`
- Output parent: `~/Documents`
- Output files: `~/Documents/Claude-Sessions/{project}/`

For custom paths:

```bash
python3 "$SCRIPT" config --target-folder "$HOME/Documents"
python3 "$SCRIPT" config --projects-dir "/path/to/claude/projects"
python3 "$SCRIPT" config --settings-file "/path/to/claude/settings.json"
```

## Use

```bash
python3 "$SCRIPT" status
python3 "$SCRIPT" export --days 30
python3 "$SCRIPT" list --active
python3 "$SCRIPT" resume --pick
python3 "$SCRIPT" note "Important follow-up"
python3 "$SCRIPT" index
python3 "$SCRIPT" search "authentication" -n 10
```

## Auto-sync

See `procedures/setup-hook.md` to add a Claude Code Stop hook.

## Optional QMD Search

Install QMD for keyword and semantic search:

```bash
npm install -g @tobilu/qmd
```

Then:

```bash
python3 "$SCRIPT" index
python3 "$SCRIPT" search "query"
python3 "$SCRIPT" vsearch "semantic query"
```
