"""session-sync lib — importlib shim for kebab-case module filenames."""

import importlib.util
import sys
from pathlib import Path

_LIB_DIR = Path(__file__).parent

# Map importable names to kebab-case filenames
_MODULES = {
    "config_loader": "config-loader.py",
    "session_extractor": "session-extractor.py",
    "markdown_renderer": "markdown-renderer.py",
    "session_lifecycle": "session-lifecycle.py",
    "qmd_search": "qmd-search.py",
}


def _load(name: str):
    """Dynamically load a kebab-case module and cache it in sys.modules."""
    full_name = f"{__name__}.{name}"
    if full_name in sys.modules:
        return sys.modules[full_name]

    filename = _MODULES.get(name)
    if not filename:
        raise ImportError(f"No module named '{full_name}'")

    spec = importlib.util.spec_from_file_location(full_name, _LIB_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = mod
    spec.loader.exec_module(mod)
    return mod


def __getattr__(name: str):
    if name in _MODULES:
        return _load(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
