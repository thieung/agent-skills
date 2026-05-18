"""Session lifecycle commands: resume, note, close, log, list."""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from . import config_loader as cfg  # noqa: relative import via kebab-case workaround handled in __init__
from . import markdown_renderer as renderer  # noqa


def _get_output_dir() -> Path:
    """Get output directory from config."""
    config = cfg.load_config()
    return cfg.get_output_dir(config)


def _get_session_files(output_dir: Path) -> list[tuple[Path, dict]]:
    """Get all session files with parsed frontmatter, sorted by last_activity desc."""
    sessions = []
    for f in output_dir.rglob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            fm = renderer.parse_frontmatter(content)
            if fm.get("type") == "claude-session":
                sessions.append((f, fm))
        except Exception:
            continue
    return sorted(sessions, key=lambda x: x[1].get("last_activity", x[1].get("date", "")), reverse=True)


def _find_session_file(output_dir: Path, session_id: str) -> Path | None:
    """Find markdown file by session_id prefix."""
    short_id = session_id[:8]
    for f in output_dir.rglob(f"*-{short_id}.md"):
        return f
    return None


def _resolve_session_id(args_session_id: str | None, output_dir: Path) -> tuple[str | None, Path | None]:
    """Resolve session_id from args, env, or most recent active session."""
    sid = args_session_id or os.environ.get("CLAUDE_SESSION_ID") or os.environ.get("CK_SESSION_ID")
    if sid:
        return sid, _find_session_file(output_dir, sid)

    # Fallback: most recent active session
    sessions = _get_session_files(output_dir)
    active = [(f, fm) for f, fm in sessions if fm.get("status") == "active"]
    if active:
        fm = active[0][1]
        return fm.get("session_id"), active[0][0]
    return None, None


def _update_frontmatter_field(file_path: Path, field: str, value: str) -> bool:
    """Update a single frontmatter field in-place via regex."""
    content = file_path.read_text(encoding="utf-8")
    pattern = rf"^{re.escape(field)}: .*$"
    new_content = re.sub(pattern, f"{field}: {value}", content, count=1, flags=re.MULTILINE)
    if new_content == content:
        return False
    file_path.write_text(new_content, encoding="utf-8")
    return True


def _update_tags(file_path: Path, tags: list[str]) -> bool:
    """Update tags array in frontmatter."""
    content = file_path.read_text(encoding="utf-8")
    if tags:
        tags_yaml = "tags:\n" + "\n".join(f"  - {t}" for t in tags)
    else:
        tags_yaml = "tags: []"

    # Replace existing tags block
    pattern = r"tags:(?:\s*\[\]|\n(?:  - .*\n)*)"
    new_content = re.sub(pattern, tags_yaml + "\n", content)
    if new_content == content:
        # Try inserting before rating
        new_content = content.replace("rating:", f"{tags_yaml}\nrating:")
    file_path.write_text(new_content, encoding="utf-8")
    return True


def _append_comment(file_path: Path, text: str) -> bool:
    """Append a timestamped comment to frontmatter comments field."""
    content = file_path.read_text(encoding="utf-8")
    fm = renderer.parse_frontmatter(content)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"[{ts}] {text}"

    existing = fm.get("comments", "")
    new_comments = f"{existing}\n{entry}" if existing else entry
    comments_yaml = "comments: |\n" + "\n".join(f"  {line}" for line in new_comments.split("\n"))

    if "comments: |" in content:
        pattern = r'comments: \|\n(?:  .*\n)*'
        new_content = re.sub(pattern, comments_yaml + "\n", content)
    elif 'comments: ""' in content:
        new_content = content.replace('comments: ""', comments_yaml)
    else:
        new_content = content.replace("---\n\n#", f"{comments_yaml}\n---\n\n#")

    file_path.write_text(new_content, encoding="utf-8")
    return True


# =============================================================================
# Commands
# =============================================================================

def cmd_list(args) -> int:
    """List exported sessions."""
    output_dir = _get_output_dir()
    sessions = _get_session_files(output_dir)

    if not getattr(args, "all", False):
        sessions = [(f, fm) for f, fm in sessions if fm.get("status") == "active"]
        title = "Active Sessions"
    else:
        title = "All Sessions"

    if getattr(args, "json", False):
        data = [{"path": str(p), **fm} for p, fm in sessions]
        print(json.dumps(data, indent=2))
        return 0

    print(f"\n{title}:")
    print("-" * 80)
    if not sessions:
        print("  No sessions found.")
        return 0

    for i, (path, fm) in enumerate(sessions[:20], 1):
        t = fm.get("title", "Untitled")[:50]
        s = fm.get("status", "?")
        m = fm.get("messages", "?")
        d = fm.get("date", "?")
        sid = fm.get("session_id", "?")[:8]
        print(f"  {i:2}. [{s:8}] {d} ({m:>3} msgs) {sid} {t}")

    if len(sessions) > 20:
        print(f"  ... and {len(sessions) - 20} more")
    return 0


def cmd_note(args) -> int:
    """Add timestamped note to a session."""
    output_dir = _get_output_dir()
    sid, session_file = _resolve_session_id(getattr(args, "session_id", None), output_dir)

    if not session_file or not session_file.exists():
        print(f"Error: Session file not found for {sid or 'current'}", file=sys.stderr)
        return 1

    text = " ".join(args.text)
    if not text:
        print("Error: No note text provided", file=sys.stderr)
        return 2

    _append_comment(session_file, text)
    print(f"Added note to {sid[:8] if sid else 'session'}: {text}")
    return 0


def cmd_close(args) -> int:
    """Mark session done with optional closing note."""
    output_dir = _get_output_dir()
    sid, session_file = _resolve_session_id(getattr(args, "session_id", None), output_dir)

    if not session_file or not session_file.exists():
        print(f"Error: Session file not found", file=sys.stderr)
        return 1

    text = " ".join(args.text) if args.text else None
    if text:
        _append_comment(session_file, f"[CLOSED] {text}")
    else:
        _append_comment(session_file, "[CLOSED]")

    _update_frontmatter_field(session_file, "status", "done")
    print(f"Session {sid[:8] if sid else ''} marked as done")
    return 0


def cmd_log(args) -> int:
    """Annotate session with status, tags, rating, comment."""
    output_dir = _get_output_dir()
    sid, session_file = _resolve_session_id(getattr(args, "session_id", None), output_dir)

    if not session_file or not session_file.exists():
        print(f"Error: Session file not found", file=sys.stderr)
        return 1

    if args.status:
        valid = ["active", "done", "blocked", "handoff"]
        if args.status not in valid:
            print(f"Error: Invalid status '{args.status}'. Use: {', '.join(valid)}", file=sys.stderr)
            return 1
        _update_frontmatter_field(session_file, "status", args.status)
        print(f"Status: {args.status}")

    if args.tags:
        tags = [t.strip() for t in args.tags.split(",")]
        _update_tags(session_file, tags)
        print(f"Tags: {', '.join(tags)}")

    if args.rating is not None:
        if not 1 <= args.rating <= 10:
            print(f"Error: Rating must be 1-10", file=sys.stderr)
            return 1
        _update_frontmatter_field(session_file, "rating", str(args.rating))
        print(f"Rating: {args.rating}/10")

    if args.text:
        text = " ".join(args.text)
        _append_comment(session_file, text)

    print(f"Session {sid[:8] if sid else ''} updated")
    return 0


def cmd_resume(args) -> int:
    """Resume a session in Claude Code."""
    output_dir = _get_output_dir()

    if getattr(args, "file", None):
        target = Path(args.file).expanduser()
        if not target.exists():
            print(f"Error: File not found: {target}", file=sys.stderr)
            return 1
        content = target.read_text(encoding="utf-8")
        fm = renderer.parse_frontmatter(content)
        sid = fm.get("session_id")
    elif getattr(args, "active", False):
        sessions = [(f, fm) for f, fm in _get_session_files(output_dir) if fm.get("status") == "active"]
        if not sessions:
            print("No active sessions found.")
            return 1
        sid = sessions[0][1].get("session_id")
        print(f"Most recent active: {sessions[0][0].name}")
    elif getattr(args, "pick", False):
        sessions = _get_session_files(output_dir) if getattr(args, "all", False) else \
            [(f, fm) for f, fm in _get_session_files(output_dir) if fm.get("status") == "active"]
        sid = _interactive_pick(sessions)
    else:
        print("Error: Specify --pick, --active, or a file", file=sys.stderr)
        return 2

    if not sid:
        print("No session selected.")
        return 0

    cmd = ["claude", "--resume", sid]
    if getattr(args, "fork", False):
        cmd.append("--fork-session")

    print(f"Resuming: {sid}")
    os.execvp("claude", cmd)


def _interactive_pick(sessions: list[tuple[Path, dict]]) -> str | None:
    """Interactive session picker via fzf or numbered fallback."""
    if not sessions:
        print("No sessions to pick from.")
        return None

    # Try fzf
    if shutil.which("fzf"):
        lines = []
        for path, fm in sessions:
            t = fm.get("title", "Untitled")[:60]
            s = fm.get("status", "?")
            d = fm.get("date", "?")
            m = fm.get("messages", "?")
            sid = fm.get("session_id", "")
            lines.append(f"{sid}\t[{s}] {d} ({m} msgs) {t}")

        try:
            result = subprocess.run(
                ["fzf", "--delimiter=\t", "--with-nth=2"],
                input="\n".join(lines), capture_output=True, text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split("\t")[0]
        except Exception:
            pass

    # Fallback: numbered list
    print("\nSessions:")
    print("-" * 70)
    for i, (path, fm) in enumerate(sessions[:15], 1):
        t = fm.get("title", "Untitled")[:50]
        s = fm.get("status", "?")
        d = fm.get("date", "?")
        print(f"  {i:2}. [{s:8}] {d} {t}")

    try:
        choice = input("\nEnter number (q to quit): ").strip()
        if choice.lower() == "q":
            return None
        idx = int(choice) - 1
        if 0 <= idx < len(sessions):
            return sessions[idx][1].get("session_id")
    except (ValueError, KeyboardInterrupt, EOFError):
        pass
    return None
