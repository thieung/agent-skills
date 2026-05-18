# Setup Procedure

Interactive onboarding for the session-sync skill.

## Pre-flight Check

Set the script path from the installed location:

```bash
SCRIPT="/path/to/session-sync/scripts/session-sync.py"
python3 "$SCRIPT" status
```

Parse output:
- Target folder set? Look for `Target folder:`
- Projects dir correct? Look for `Projects dir:`
- QMD installed? Look for `✓ QMD installed` or `✗ QMD not installed`
- Sessions exported? Look for `✓ Exported:` or `✗ No sessions`
- Hook configured? Look for `✓ Auto-sync hook` or `✗ Auto-sync hook`

## Step 1: Configure Paths

If defaults are acceptable, no config is needed:
- Claude home: `~/.claude`
- Projects dir: `~/.claude/projects`
- Target folder: `~/Documents`

For custom installs:

```bash
python3 "$SCRIPT" config --target-folder "/path/to/output-parent"
python3 "$SCRIPT" config --claude-home "/path/to/claude-home"
python3 "$SCRIPT" config --projects-dir "/path/to/claude/projects"
python3 "$SCRIPT" config --settings-file "/path/to/claude/settings.json"
```

Exports go to `{target_folder}/Claude-Sessions/{project}/`.

## Step 2: Install QMD

If QMD is not installed, inform the user:
> QMD enables keyword and semantic search across exported sessions. Install it?

If yes, see `procedures/install-qmd.md`.

If no, skip search features.

## Step 3: Export Sessions

Ask what to export:
> Export sessions from: all time, last 30 days, last 90 days, or a specific project?

Run the matching command:

```bash
python3 "$SCRIPT" export --all
python3 "$SCRIPT" export --days 30
python3 "$SCRIPT" list-projects
python3 "$SCRIPT" export --project PROJECT_NAME
```

## Step 4: Index in QMD

If QMD is installed and sessions were exported:

```bash
python3 "$SCRIPT" index
```

## Step 5: Setup Auto-Sync Hook

Ask:
> Enable auto-sync on session end?

If yes, see `procedures/setup-hook.md`.

## Step 6: Optional Lifecycle Commands

```bash
python3 "$SCRIPT" list --active
python3 "$SCRIPT" resume --pick
python3 "$SCRIPT" note "Follow-up note"
python3 "$SCRIPT" close "Done"
```

## Completion

Run final status check:

```bash
python3 "$SCRIPT" status
```
