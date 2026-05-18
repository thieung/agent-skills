"""Config loading, saving, and output directory resolution."""

import json
import os
import shutil
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent.parent
CONFIG_FILE = SKILL_DIR / "config.json"

DEFAULT_CONFIG = {
    "target_folder": str(Path.home() / "Documents"),
    "claude_home": "",
    "projects_dir": "",
    "settings_file": "",
    "qmd_path": "qmd",
    "collection_name": "claude-sessions",
    "auto_sync": False,
}


def load_config() -> dict:
    """Load config from file, merged with defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """Save config to file."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_output_dir(config: dict) -> Path:
    """Get output directory based on the reference layout."""
    target = config.get("target_folder") or str(Path.home() / "Documents")
    target = Path(target).expanduser()
    return target / "Claude-Sessions"


def get_claude_home(config: dict) -> Path:
    """Resolve Claude Code home directory."""
    configured = config.get("claude_home")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".claude"


def get_projects_dir(config: dict) -> Path:
    """Resolve Claude Code projects directory."""
    configured = config.get("projects_dir")
    if configured:
        return Path(configured).expanduser()
    return get_claude_home(config) / "projects"


def get_settings_file(config: dict) -> Path:
    """Resolve Claude Code settings file."""
    configured = config.get("settings_file")
    if configured:
        return Path(configured).expanduser()
    return get_claude_home(config) / "settings.json"


def find_qmd(config: dict) -> str | None:
    """Find QMD executable from config or system PATH."""
    configured = config.get("qmd_path")
    if configured and shutil.which(configured):
        return configured

    qmd_in_path = shutil.which("qmd")
    if qmd_in_path:
        return qmd_in_path

    # Check common install locations
    home = Path.home()
    candidates = [
        home / ".bun/bin/qmd",
        home / ".local/bin/qmd",
        Path("/usr/local/bin/qmd"),
    ]
    nvm_dir = home / ".nvm/versions/node"
    if nvm_dir.exists():
        for node_ver in nvm_dir.iterdir():
            qmd_path = node_ver / "bin/qmd"
            if qmd_path.exists():
                candidates.insert(0, qmd_path)

    for qmd in candidates:
        if qmd.exists():
            return str(qmd)
    return None
