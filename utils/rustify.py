"""Checker for rust rebuild."""

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

from sqlfluff.core.dialects import dialect_readout


def check_generated_output(
    build_path: Path, output_path: Path, build_arg: list[str]
) -> bool:
    """Check output matches file."""
    with open(output_path, "rb") as f:
        output_bytes = f.read()
    output_hash = hashlib.sha256(output_bytes).hexdigest()
    result = subprocess.run(
        [sys.executable, build_path, *build_arg], capture_output=True, check=True
    )
    process_hash = hashlib.sha256(result.stdout).hexdigest()
    output_answer = "✅" if output_hash == process_hash else "❌"
    print(f"Matching output of {build_path} to {output_path}: {output_answer}")
    return output_hash == process_hash


def build_generated_output(build_path: Path, output_path: Path, build_arg: list[str]):
    """Builds rust output from python."""
    result = subprocess.run(
        [sys.executable, build_path, *build_arg], capture_output=True, check=True
    )
    if not output_path.parent.exists():
        output_path.parent.mkdir(0o755, parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        f.write(result.stdout)


if __name__ == "__main__":
    dialects_list = [
        (
            f"utils/{builder}.py",
            f"sqlfluffrs/src/dialect/{dialect.label.lower()}/{file}.rs",
            args,
        )
        for dialect in dialect_readout()
        for builder, file, args in [
            ("build_dialect", "mod", []),
            ("build_lexers", "matcher", [dialect.label.lower()]),
        ]
    ]

    file_pair_list = [
        ("utils/build_dialects.py", "sqlfluffrs/src/dialect/mod.rs", []),
        *dialects_list,
        # ("utils/build_lexers.py", "sqlfluffrs/src/dialect/matcher.rs", []),
    ]
    parser = argparse.ArgumentParser(
        description="Check or build generated Rust output."
    )
    parser.add_argument(
        "action",
        choices=["build", "check"],
        help="Action to perform: 'build' to generate output, 'check' to verify output.",
    )
    args = parser.parse_args()

    file_pair_list = [
        (Path(build), Path(output), build_args)
        for build, output, build_args in file_pair_list
    ]

    if args.action == "build":
        for build_path, output_path, build_arg in file_pair_list:
            build_generated_output(build_path, output_path, build_arg)
        sys.exit(0)
    elif args.action == "check":
        mismatch_count = sum(
            not check_generated_output(build_path, output_path, build_args)
            for build_path, output_path, build_args in file_pair_list
        )
        sys.exit(mismatch_count != 0)
    sys.exit(1)
