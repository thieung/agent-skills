"""QMD integration: index, search, and semantic vector search."""

import subprocess
import sys

from . import config_loader as cfg  # noqa


def cmd_index(args) -> int:
    """Re-index sessions in QMD."""
    config = cfg.load_config()
    output_dir = cfg.get_output_dir(config)
    qmd_path = cfg.find_qmd(config)

    if not qmd_path:
        print("ERROR: QMD not installed. Install: npm install -g @tobilu/qmd")
        return 1

    collection = config.get("collection_name", "claude-sessions")

    # Remove existing collection and re-add
    subprocess.run([qmd_path, "collection", "remove", collection], capture_output=True, text=True)

    print(f"Adding collection: {collection} from {output_dir}")
    result = subprocess.run(
        [qmd_path, "collection", "add", str(output_dir), "--name", collection],
        capture_output=True, text=True,
    )
    print(result.stdout)

    print("Generating embeddings...")
    result = subprocess.run([qmd_path, "embed"], capture_output=True, text=True)
    print(result.stdout)
    return 0


def cmd_search(args) -> int:
    """BM25 keyword search via QMD."""
    config = cfg.load_config()
    qmd_path = cfg.find_qmd(config)

    if not qmd_path:
        print("ERROR: QMD not installed")
        return 1

    collection = config.get("collection_name", "claude-sessions")
    result = subprocess.run(
        [qmd_path, "search", args.query, "-c", collection, "-n", str(args.n)],
        capture_output=True, text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def cmd_vsearch(args) -> int:
    """Semantic vector search via QMD."""
    config = cfg.load_config()
    qmd_path = cfg.find_qmd(config)

    if not qmd_path:
        print("ERROR: QMD not installed")
        return 1

    collection = config.get("collection_name", "claude-sessions")
    result = subprocess.run(
        [qmd_path, "vsearch", args.query, "-c", collection, "-n", str(args.n)],
        capture_output=True, text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode
