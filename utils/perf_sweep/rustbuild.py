"""Real (non-dry-run) per-commit build.

The Rust side is always rebuilt fresh for the checked-out commit, but reuses
a single worktree + a shared CARGO_TARGET_DIR across the whole sweep so
cargo's own content-hash fingerprinting gives real incremental compilation -
unaffected crates (most of the dependency graph, and any workspace crate
this commit didn't touch) skip straight to cached artifacts. Dialect codegen
additionally skips re-running `rustify.py build` when dialect_cache says
nothing that can affect its output has changed since the last commit.

The Python side (the venv sqlfluff/sqlfluffrs get installed into) is the
opposite: every commit gets a brand-new environment in a directory that did
not exist before this call, built via `uv venv` + `uv pip install`, and the
caller discards it once that commit's measurements are done. There is
deliberately no reuse and no --force-reinstall trick here - a fresh
environment can't have stale state to force past, so a single plain install
is both simpler and correct.

maturin itself isn't a prerequisite the user has to `pip install` up front:
it's launched via `uvx maturin`, which uv fetches into its own tool cache on
first use and reuses from then on.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from . import dialect_cache, gitrange


def venv_python_path(venv_dir: Path) -> Path:
    r"""`uv venv`/stdlib venv lay out the interpreter differently per OS.

    Scripts\python.exe on Windows, bin/python everywhere else.
    """
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


class BuildError(RuntimeError):
    """Raised when a per-commit build step (venv/pip/maturin) fails."""


def _run(cmd: list, cwd: Path = None, env: dict = None) -> subprocess.CompletedProcess:
    """Run cmd, raising BuildError with captured stdout/stderr on failure."""
    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        raise BuildError(
            f"command failed ({result.returncode}): {' '.join(str(c) for c in cmd)}\n"
            f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
        )
    return result


def ensure_uv() -> str:
    """Return the path to `uv` on PATH, or raise BuildError if it's missing."""
    exe = shutil.which("uv")
    if not exe:
        raise BuildError(
            "uv not found on PATH. Install it (see https://docs.astral.sh/uv/) "
            "before running a real (non-dry-run) sweep."
        )
    return exe


def build_commit(
    repo_dir: Path,
    worktree_dir: Path,
    venv_dir: Path,
    cargo_target_dir: Path,
    state_dir: Path,
    sha: str,
) -> dict:
    """Build `sha` and install it into `venv_dir`.

    `venv_dir` must not already exist - the caller is expected to hand in a
    freshly created temporary directory per commit and remove it once done.
    """
    timings = {}

    t0 = time.monotonic()
    gitrange.checkout_commit(worktree_dir, sha)
    timings["checkout_seconds"] = time.monotonic() - t0

    t0 = time.monotonic()
    _run(["uv", "venv", str(venv_dir)])
    venv_python = venv_python_path(venv_dir)
    timings["venv_create_seconds"] = time.monotonic() - t0

    t0 = time.monotonic()
    _run(["uv", "pip", "install", "--python", str(venv_python), str(worktree_dir)])
    timings["pip_install_python_pkg_seconds"] = time.monotonic() - t0

    hash_file = state_dir / "dialect_hash.txt"
    new_hash = dialect_cache.compute_generation_hash(repo_dir, sha)
    previous_hash = hash_file.read_text().strip() if hash_file.exists() else None

    t0 = time.monotonic()
    dialect_regenerated = new_hash != previous_hash
    if dialect_regenerated:
        _run(
            [str(venv_python), str(worktree_dir / "utils" / "rustify.py"), "build"],
            cwd=worktree_dir,
        )
        hash_file.write_text(new_hash)
    timings["dialect_codegen_seconds"] = time.monotonic() - t0

    dist_dir = worktree_dir / "dist"
    env = dict(os.environ)
    env["CARGO_TARGET_DIR"] = str(cargo_target_dir)

    t0 = time.monotonic()
    _run(
        [
            "uvx",
            "maturin",
            "build",
            "--release",
            "--manifest-path",
            str(worktree_dir / "sqlfluffrs" / "Cargo.toml"),
            "--out",
            str(dist_dir),
        ],
        env=env,
    )
    timings["maturin_build_seconds"] = time.monotonic() - t0

    t0 = time.monotonic()
    _run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(venv_python),
            "--no-index",
            "--find-links",
            str(dist_dir),
            "sqlfluffrs",
        ]
    )
    timings["pip_install_rust_pkg_seconds"] = time.monotonic() - t0

    return {
        "dialect_regenerated": dialect_regenerated,
        "dialect_gen_hash": new_hash,
        "build_timings_seconds": timings,
    }
