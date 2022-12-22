"""Replaces .tox/ paths in the lcov file with paths relative to repo root."""
import re
from pathlib import Path

path = Path("coverage.lcov")
if path.exists():
    lines = path.read_text().splitlines()
    modified_lines = []
    for line in lines:
        if line.startswith("SF:"):
            m = re.search(r"^(SF:).*(sqlfluff/.*)", line)
            if m:
                modified_lines.append(f"{m.group(1)}src/{m.group(2)}")
            else:
                print(f"Could not patch line: {line}")
                modified_lines.append(line)
        else:
            modified_lines.append(line)
    path.write_text("\n".join(modified_lines))
