---
name: handoff
description: "Preserve and restore cross-session work context via a compact repo-local `.handoff/handoff.md`. Use when the user says: hand off, wrap up, checkpoint, save progress, save where we are, continue later, continue from previous session, resume from handoff, pick up where we left off, what did we leave off, where we left off, read the prior handoff, read prior context, load handoff, load previous context, check the handoff file, last session, prepare the next session. Skill writes a handoff on end-of-session and reads it on start-of-session so a fresh agent can continue without re-discovery."
argument-hint: "[what the next session should focus on]"
version: 1.0.0
license: MIT
allowed-tools:
  - Bash
  - Read
  - Write
---

# Handoff

Create or consume a compact handoff document so another agent, another session, or future-you can continue the work quickly.

Use this skill only when continuity is the goal. Do not use it for ordinary implementation, code review, or debugging unless the user asks to checkpoint or resume state.

## Paths

Default handoff path:

```text
.handoff/handoff.md
```

When reading or writing handoff state, use `.handoff/handoff.md` unless the user explicitly specifies another path.

Optional config:

```yaml
handoff:
  mode: ask # ask | yolo
  include_git_diff: true
  max_key_files: 20
```

Default mode is `ask`: show the draft first, then write after approval. If config says `yolo`, write directly and report the path.

For reusable installs, keep the handoff file repo-local. Do not write to the skill directory itself.

## Start Session

Trigger phrases (non-exhaustive): "resume", "continue", "continue from previous session", "pick up where we left off", "where we left off", "what did we leave off", "read the prior handoff", "check the handoff file", "load handoff", "load previous context", "what happened before", "last session".

When the user uses any of these or a close variant:

1. Read `.handoff/handoff.md` if it exists.
2. If it does not exist, say no handoff file was found and start fresh unless the user provides another path.
3. Summarize the handoff in 3-6 bullets: branch, goal, in-progress state, blockers, next steps.
4. Check alignment with the current user request. If the handoff is about a different task, ask whether to use it or start fresh.
5. Verify before trusting: run lightweight checks such as current branch, `git status --short`, and spot-check 1-2 Key Files.
6. If aligned and current, continue from `Next Steps`. Do not re-explore files already listed unless the handoff says they are uncertain or stale.
7. If stale or branch/files do not match, say what is stale and do targeted rediscovery only for the mismatched areas.

## End Session

Trigger phrases (non-exhaustive): "hand off", "wrap up", "checkpoint", "save progress", "save where we are", "I'll continue later", "prepare the next session", "context is heavy". Also auto-suggest when context pressure is high without an explicit user trigger.

When any of these apply:

1. Gather facts (handoff is self-sufficient — collect directly):
   - Current branch and recent git state.
   - `git status --short`.
   - `git diff --stat` when useful.
   - Files read, created, edited, or important for the next session.
   - Decisions, blockers, gotchas, failed attempts worth preserving.
   - The user's original goal and any later scope changes.
   - **Optional shortcut**: if `/ck:watzup` (ClaudeKit paid skill) happens to have been run earlier in this conversation, reuse its summary as input for `Done`, `In Progress`, `Next Steps`, `Decisions`, `Key Files`, and `Verification` — distill, do not paste. Refresh missing/stale parts with targeted git checks. Do not require or invoke `/ck:watzup` if it was not already run.
2. If the user supplied arguments, treat them as the next session's intended focus and tailor `Next Steps` around that.
3. Draft a compact handoff using the template below.
4. Do not duplicate content already captured in plans, PRDs, ADRs, issues, commits, or reports. Reference those artifacts by path or URL.
5. In `ask` mode, show the draft and ask whether to save or adjust it. In `yolo` mode, write `.handoff/handoff.md` directly.

## Template

```markdown
# Handoff - [project or task name]

**Updated:** [real ISO 8601 timestamp]
**Branch:** [current branch]
**Focus:** [what the next session should continue]
**Context Pressure:** [low | medium | high]

## Goal
[One short paragraph. What outcome are we working toward?]

## In Progress
- [Current partial state, if any. Include exact file refs where useful.]

## Done
- [Completed work with file:line refs where useful.]

## Next Steps
1. [Most important next action, concrete enough to execute.]
2. [Second action.]
3. [Third action.]

## Blockers
- [External dependency, failing test, missing decision, or "None".]

## Decisions
- [Non-obvious choice and why.]

## Key Files
- `path/to/file` - why it matters; line ref if useful.

## Verification
- [Command/check run and result, or "Not run".]

## Open Questions
- [Unresolved question, or "None".]
```

## Quality Bar

- Target 30-80 lines, under roughly 1k tokens.
- Favor file paths and line references over pasted code.
- Do not include full file contents, long code snippets, tool transcripts, or verbose logs.
- Include only dead ends that prevent repeated mistakes.
- `Next Steps` must be executable without reading the old chat.
- A fresh agent should be able to start productive work within 2-3 tool calls after reading the handoff.

## Optional SessionStart Hook

For automatic context injection in Claude Code, add a SessionStart hook that prints the handoff if present.

macOS / Linux (bash):

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

Windows (PowerShell):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "powershell -NoProfile -Command \"if (Test-Path .handoff/handoff.md) { Write-Host '--- PRIOR HANDOFF ---'; Get-Content .handoff/handoff.md; Write-Host '--- END PRIOR HANDOFF ---' } else { Write-Host 'No prior handoff.' }\""
      }
    ]
  }
}
```

For project-local hooks, add this to the project settings file. For global hooks, only use it if you are comfortable exposing the current repo's handoff at every new session start.
