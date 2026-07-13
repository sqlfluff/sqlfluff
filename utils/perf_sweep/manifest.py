"""manifest.jsonl: an append-only index of every commit the sweep has touched.

Used both as a progress log and to make a sweep resumable - later entries
for the same sha win when the file is loaded.
"""

from __future__ import annotations

import json
from pathlib import Path


def load_manifest(path: Path) -> dict:
    """Load manifest.jsonl into {sha: entry}, last entry per sha winning."""
    if not path.exists():
        return {}
    entries: dict = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        entry = json.loads(line)
        entries[entry["sha"]] = entry
    return entries


def append(path: Path, entry: dict) -> None:
    """Append one JSON entry as a new line in manifest.jsonl."""
    with path.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def is_done(entry: dict, current_is_dry_run: bool) -> bool:
    """Whether a manifest entry means nothing more to do, for a run of the given dry-run-ness.

    A skip decision is dry-run-independent. A dry-run pass treats any prior
    visit (real or dry) as done, since it's just a cheap resumable scan. A
    real run only accepts a prior *real* measurement as done - a stale
    dry-run stub must never satisfy a real run and get left in place.
    """
    if entry.get("skipped"):
        return True
    if current_is_dry_run:
        return True
    return not entry.get("dry_run", False)
