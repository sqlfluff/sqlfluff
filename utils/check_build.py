"""Checker for rust rebuild."""

import hashlib
import subprocess
import sys
from pathlib import Path


def check_generated_output(build_path: Path, output_path: Path) -> bool:
    """Check output matches file."""
    with open(output_path, "rb") as f:
        output_bytes = f.read()
    output_hash = hashlib.sha256(output_bytes).hexdigest()
    result = subprocess.run(
        [sys.executable, build_path], capture_output=True, check=True
    )
    process_hash = hashlib.sha256(result.stdout).hexdigest()
    output_answer = "✅" if output_hash == process_hash else "❌"
    print(f"Matching output of {build_path} to {output_path}: {output_answer}")
    return output_hash == process_hash


if __name__ == "__main__":
    mismatch_count = sum(
        not check_generated_output(build_path, output_path)
        for build_path, output_path in [
            ("utils/build_lexers.py", "rsqlfluff/src/dialect/matcher.rs"),
        ]
    )
    sys.exit(mismatch_count != 0)
