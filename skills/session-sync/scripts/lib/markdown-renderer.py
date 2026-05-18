"""Markdown generation with re-sync preservation for session files."""

import re
from datetime import datetime, timezone
from pathlib import Path

# Fields preserved across re-syncs (not overwritten by fresh extraction)
PRESERVED_FIELDS = {"title", "status", "tags", "rating", "comments"}
PRESERVED_SECTION = "## My Notes"
MY_NOTES_PATTERN = re.compile(r"(## My Notes\n)(.*?)(?=\n## |\Z)", re.DOTALL)


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown content."""
    fm = {}
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        return fm

    current_key = None
    current_array = None
    multiline_lines = []
    in_multiline = False

    for line in match.group(1).split("\n"):
        if in_multiline:
            if line.startswith("  ") or line == "":
                multiline_lines.append(line[2:] if line.startswith("  ") else "")
                continue
            else:
                fm[current_key] = "\n".join(multiline_lines).rstrip()
                in_multiline = False
                multiline_lines = []

        if line.startswith("  - ") and current_array:
            if current_array not in fm or not isinstance(fm[current_array], list):
                fm[current_array] = []
            fm[current_array].append(line[4:].strip())
            continue

        if ":" in line and not line.startswith("  "):
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_key = key

            if value == "|":
                in_multiline = True
                multiline_lines = []
                current_array = None
            elif value in ("", "[]"):
                current_array = key
                fm[key] = [] if value == "[]" else value
            else:
                current_array = None
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                fm[key] = value

    if in_multiline:
        fm[current_key] = "\n".join(multiline_lines).rstrip()

    return fm


def extract_my_notes(content: str) -> str | None:
    """Extract the ## My Notes section body from existing markdown."""
    if PRESERVED_SECTION not in content:
        return None
    match = MY_NOTES_PATTERN.search(content)
    return match.group(0).rstrip() if match else None


def read_preserved(output_path: Path) -> tuple[dict, str | None]:
    """Read preserved fields and My Notes section from existing file.
    Returns (preserved_fm_dict, my_notes_str_or_none).
    """
    if not output_path.exists():
        return {}, None
    content = output_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)
    preserved = {k: fm[k] for k in PRESERVED_FIELDS if k in fm}
    my_notes = extract_my_notes(content)
    return preserved, my_notes


def _format_file_path(file_path: str) -> str:
    """Format a file path for the artifacts section."""
    return f"`{file_path}`"


def generate_markdown(data: dict, project_name: str,
                      preserved_fm: dict | None = None,
                      my_notes: str | None = None) -> str:
    """Generate full markdown with merged frontmatter schema."""
    pfm = preserved_fm or {}
    lines = []

    # --- Frontmatter ---
    lines.append("---")
    lines.append("type: claude-session")
    lines.append(f"project: {project_name}")
    lines.append(f"date: {data['date']}")
    lines.append(f"session_id: {data['session_id']}")

    # Title: preserved > detected > fallback
    title = pfm.get("title") if pfm.get("title") and pfm["title"] != "Untitled Session" else None
    title = title or data.get("title") or "Untitled Session"
    lines.append(f'title: "{title.replace(chr(34), chr(92)+chr(34))}"')

    lines.append(f"messages: {data['messages']}")

    if data.get("first_timestamp"):
        lines.append(f"created: {data['first_timestamp']}")
    if data.get("last_timestamp"):
        lines.append(f"last_activity: {data['last_timestamp']}")
    if data.get("cwd"):
        lines.append(f"cwd: {data['cwd']}")
    if data.get("git_branch"):
        lines.append(f"git_branch: {data['git_branch']}")

    # Status: preserved > default
    status = pfm.get("status", "active")
    lines.append(f"status: {status}")

    # Tags: preserved > empty
    tags = pfm.get("tags", [])
    if isinstance(tags, list) and tags:
        lines.append("tags:")
        for tag in tags:
            lines.append(f"  - {tag}")
    else:
        lines.append("tags: []")

    # Rating: preserved > null
    rating = pfm.get("rating")
    if rating is not None and str(rating) != "null":
        lines.append(f"rating: {rating}")
    else:
        lines.append("rating: null")

    # Skills: always from fresh extraction
    if data.get("skills"):
        lines.append("skills:")
        for skill in sorted(data["skills"]):
            lines.append(f"  - {skill}")
    else:
        lines.append("skills: []")

    # Summary: from extraction
    if data.get("summary"):
        summary_escaped = data["summary"].replace('"', '\\"').replace("\n", " ")
        lines.append(f'summary: "{summary_escaped}"')

    # Comments: preserved > empty
    comments = pfm.get("comments", "")
    if comments:
        lines.append("comments: |")
        for cl in str(comments).split("\n"):
            lines.append(f"  {cl}")
    else:
        lines.append('comments: ""')

    lines.append("---")
    lines.append("")

    # --- Body ---
    lines.append(f"# {title}")
    lines.append("")

    # Summary section
    if data.get("summary"):
        lines.append("## Summary")
        lines.append("")
        lines.append(data["summary"])
        lines.append("")

    # Skills Used section
    if data.get("skills"):
        lines.append("## Skills Used")
        lines.append("")
        for skill in sorted(data["skills"]):
            lines.append(f"- {skill}")
        lines.append("")

    # Artifacts section
    created = data.get("files_created", [])
    modified = data.get("files_modified", [])
    if created or modified:
        lines.append("## Artifacts")
        lines.append("")
        if created:
            lines.append("**Created:**")
            for fp in created:
                lines.append(f"- {_format_file_path(fp)}")
            lines.append("")
        if modified:
            lines.append("**Modified:**")
            for fp in modified:
                lines.append(f"- {_format_file_path(fp)}")
            lines.append("")

    # Conversation
    lines.append("## Conversation")
    lines.append("")
    for msg in data.get("conversation", []):
        role = "**User:**" if msg["role"] == "user" else "**Assistant:**"
        content = msg["content"]
        lines.append(role)
        lines.append("")
        lines.append(content)
        lines.append("")
        lines.append("---")
        lines.append("")

    # My Notes section (preserved or fresh template)
    if my_notes:
        lines.append(my_notes)
    else:
        lines.append("## My Notes")
        lines.append("")
        lines.append("<!-- Add your notes here. This section is preserved across syncs. -->")
    lines.append("")

    return "\n".join(lines)
