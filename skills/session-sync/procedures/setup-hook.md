# Setup Auto-Sync Hook Procedure

Configure Claude Code to auto-sync sessions on Stop events.

## Inputs

Set these paths first:

```bash
SCRIPT="/path/to/session-sync/scripts/session-sync.py"
SETTINGS="/path/to/claude/settings.json"
```

Common settings paths:
- Global Claude Code: `~/.claude/settings.json`
- Project-local: `.claude/settings.local.json`

## Check Current State

```bash
grep -A5 '"Stop"' "$SETTINGS"
```

If output contains `session-sync.py sync`, the hook is already configured.

## Add Hook

Edit the chosen settings file and add:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /absolute/path/to/session-sync/scripts/session-sync.py sync",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

If `hooks.Stop` already exists, append the hook object instead of replacing other hooks.

**Windows note:** Replace `python3` with `python` (or the absolute path to `python.exe`). The `py -3` launcher also works. Verify with `python --version` first.

Validate JSON:

```bash
python3 -c "import json, os; json.load(open(os.path.expanduser('$SETTINGS')))"
```

## Update Config

```bash
python3 "$SCRIPT" config --settings-file "$SETTINGS" --auto-sync true
```

## Verify

```bash
python3 "$SCRIPT" status
```

Expected marker: `✓ Auto-sync hook: enabled`

## How It Works

On Stop, Claude Code passes `{"session_id": "...", "transcript_path": "..."}` via stdin. The script reads the JSONL transcript and exports/updates markdown under `{target_folder}/Claude-Sessions/{project}/`, preserving lifecycle fields and `## My Notes`.

## Disable Hook

Remove the hook entry from the settings file, then run:

```bash
python3 "$SCRIPT" config --auto-sync false
```
