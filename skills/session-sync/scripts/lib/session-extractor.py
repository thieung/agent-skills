"""JSONL parsing with skills detection, artifact tracking, and summary extraction."""

import json
import re
from datetime import datetime
from pathlib import Path

# Patterns to skip for title extraction
SKIP_PATTERNS = ["<command-name>", "<local-command", "/clear", "/help", "/exit"]

# System tag patterns to filter from conversation
SYSTEM_TAG_PATTERNS = ["<local-command", "<system-reminder", "<command-name>"]


def parse_jsonl(jsonl_path: Path) -> list[dict] | None:
    """Parse a JSONL file into a list of records."""
    try:
        records = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return records if records else None
    except Exception:
        return None


def parse_project_name(cwd: str) -> str:
    """Extract clean project name from CWD path."""
    if not cwd:
        return "unknown"
    path = Path(cwd)
    name = path.name if path.name else cwd
    name = name.lstrip("-")
    parts = name.split("-")
    common_segments = {"Applications", "Users", "MAMP", "htdocs", "home", "projects", "code", "dev", "src", "repos"}
    start_idx = 0
    for i, part in enumerate(parts):
        if part in common_segments or (len(part) <= 2 and part.isalpha()):
            start_idx = i + 1
        else:
            break
    if 0 < start_idx < len(parts):
        name = "-".join(parts[start_idx:])
    return name or "unknown"


def _extract_skills(contents: list) -> list[str]:
    """Extract skill names from assistant message content blocks."""
    skills = []
    if not isinstance(contents, list):
        return skills
    for item in contents:
        if isinstance(item, dict) and item.get("name") == "Skill":
            skill_name = item.get("input", {}).get("skill", "")
            if skill_name and skill_name not in skills:
                skills.append(skill_name)
    return skills


def _extract_artifacts(records: list[dict]) -> dict:
    """Extract files created/modified from tool use records."""
    created = []
    modified = set()

    for record in records:
        # Check toolUseResult records (from global approach)
        result = record.get("toolUseResult", {})
        if isinstance(result, dict) and result.get("filePath"):
            fp = result["filePath"]
            if result.get("type") == "create":
                if fp not in created:
                    created.append(fp)
            elif result.get("structuredPatch") or result.get("oldString"):
                modified.add(fp)

        # Check tool_use in assistant messages (Write/Edit/MultiEdit)
        if record.get("type") == "assistant":
            msg = record.get("message", {})
            contents = msg.get("content", [])
            if isinstance(contents, list):
                for item in contents:
                    if isinstance(item, dict) and item.get("type") == "tool_use":
                        name = item.get("name", "")
                        inp = item.get("input", {})
                        fp = inp.get("file_path", "")
                        if not fp:
                            continue
                        if name == "Write" and fp not in created:
                            created.append(fp)
                        elif name in ("Edit", "MultiEdit"):
                            modified.add(fp)

    modified = modified - set(created)
    return {"created": created, "modified": sorted(modified)}


def extract_session_data(jsonl_path: Path) -> dict | None:
    """Extract full session metadata and conversation from JSONL file.

    Returns dict with: session_id, date, title, summary, skills, messages,
    conversation, cwd, git_branch, first_timestamp, last_timestamp,
    files_created, files_modified.
    """
    records = parse_jsonl(jsonl_path)
    if not records:
        return None

    data = {
        "session_id": None,
        "date": None,
        "title": None,
        "summary": None,
        "skills": [],
        "messages": 0,
        "first_timestamp": None,
        "last_timestamp": None,
        "conversation": [],
        "cwd": None,
        "git_branch": None,
        "files_created": [],
        "files_modified": [],
    }

    all_skills = []

    for record in records:
        if record.get("sessionId") and not data["session_id"]:
            data["session_id"] = record["sessionId"]

        record_type = record.get("type")

        if record_type == "user":
            timestamp = record.get("timestamp", "")
            if timestamp:
                if not data["date"]:
                    data["date"] = timestamp.split("T")[0]
                if not data["first_timestamp"]:
                    data["first_timestamp"] = timestamp
                data["last_timestamp"] = timestamp

            data["messages"] += 1

            if record.get("cwd") and not data["cwd"]:
                data["cwd"] = record["cwd"]
            if record.get("gitBranch") and not data["git_branch"]:
                data["git_branch"] = record["gitBranch"]

            # Extract user message text
            msg = record.get("message", {})
            content = msg.get("content", "")
            text = ""
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = item.get("text", "")
                        break

            if text and not record.get("isMeta"):
                if not any(p in text for p in SYSTEM_TAG_PATTERNS):
                    data["conversation"].append({"role": "user", "content": text})

        elif record_type == "assistant":
            msg = record.get("message", {})
            contents = msg.get("content", [])
            text_parts = []
            tool_uses = []

            # Detect skills used
            skills_found = _extract_skills(contents)
            for s in skills_found:
                if s not in all_skills:
                    all_skills.append(s)

            if isinstance(contents, list):
                for item in contents:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                        elif item.get("type") == "tool_use":
                            tool_uses.append(item.get("name", "unknown"))

            output_parts = text_parts.copy()
            if tool_uses:
                output_parts.append(f"*[Used: {', '.join(tool_uses)}]*")

            if output_parts:
                data["conversation"].append({"role": "assistant", "content": "\n".join(output_parts)})

        elif record_type == "custom-title":
            custom_title = record.get("customTitle", "")
            if custom_title:
                data["title"] = custom_title.split("\n")[0].strip()[:100]

        elif record_type == "summary":
            summary = record.get("summary", "")
            if summary:
                data["summary"] = summary
                if not data["title"]:
                    data["title"] = summary.split("\n")[0].strip()[:100]

    # Fallback title from first meaningful user message
    if not data["title"] and data["conversation"]:
        for msg in data["conversation"]:
            if msg["role"] == "user":
                content = msg["content"]
                if any(p in content for p in SKIP_PATTERNS):
                    continue
                clean = content.replace("\n", " ").strip()
                if len(clean) > 10:
                    data["title"] = clean[:80]
                    break

    if not data["title"]:
        data["title"] = "Untitled Session"
    if not data["date"]:
        data["date"] = datetime.now().strftime("%Y-%m-%d")

    data["skills"] = all_skills
    artifacts = _extract_artifacts(records)
    data["files_created"] = artifacts["created"]
    data["files_modified"] = artifacts["modified"]

    return data
