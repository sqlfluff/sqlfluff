# perf_sweep

Local, laptop-run historical performance sweep for `Linter.parse_string`
across the TPC-H/TPC-DS query suites, over every non-dialect-only commit in
a git range. Not wired into CI - this is meant to run on your own machine
where you can control (and mitigate) measurement noise.

## What it measures

For each non-skipped commit, in 3 parser modes:

- `python` - the pure-Python parser (`use_rust_parser=False`)
- `rust_legacy` - the Rust parser, legacy convert+apply path (`use_rust_parser=True`,
  `native_ast=False`)
- `rust_native_ast` - the Rust parser, fused single-pass builder
  (`use_rust_parser=True`, `native_ast=True`)

`native_ast` only exists from upstream PR #7983 onward. On commits before it,
`rust_native_ast` is recorded as **not applicable**, not measured as a
duplicate of `rust_legacy`.

Each (commit x mode x suite) gets two measurements:

- **callgrind**: a single valgrind-instrumented run - deterministic
  instruction count, immune to system noise, the primary regression signal.
- **walltime**: adaptive-round wall-clock timing (2 unmeasured warmup rounds,
  then batches of 10, floor 10, until the 95% relative margin of error is
  <=2% or 100 rounds is hit) - real-world context, more affected by noise.

## Commit selection

- Default range is `4.2.2..upstream/main`, inclusive of `4.2.2` - set up an `upstream` remote
  pointing at `https://github.com/sqlfluff/sqlfluff` (`git remote add upstream
  https://github.com/sqlfluff/sqlfluff`) before running, or pass `--start-ref`
  /`--end-ref` explicitly.
- A commit is **skipped** (no build, no measurement) only if every file it
  touches falls under `src/sqlfluff/dialects/`, `src/sqlfluff/rules/`,
  `src/sqlfluff/core/rules/`, `src/sqlfluff/core/templaters/`, `test/`,
  `CHANGELOG.md`, `docs/`, `docsv/`, `plugins/`, `utils/`, `.github/`,
  `pyproject.toml`, `sqlfluffrs/sqlfluffrs_benchmarks/`, `sqlfluffrs/tests/`,
  or any `AGENTS.md`.
- Everything else in this range is benchmarked, including "trivial-looking"
  refactors - the whole point is to catch things a diff wouldn't tell you.

## Usage

```sh
# One-time: point at the real upstream project, not just your fork.
git remote add upstream https://github.com/sqlfluff/sqlfluff

# Cheap sanity pass first - no builds, no measurement, just the plan:
python -m utils.perf_sweep.cli --dry-run --output bench-results-dry

# The real thing. This is slow (a release build per non-skipped commit,
# plus callgrind + adaptive walltime x 3 modes x 2 suites). Use --max-commits
# or --time-budget-seconds to bound a single invocation; it's resumable -
# rerun the same command later and it picks up where it left off.
python -m utils.perf_sweep.cli --output bench-results \
    --max-commits 20 --time-budget-seconds 21600
```

Requires (on the machine actually running the sweep): `git`, `cargo`+`rustc`,
`uv` (https://docs.astral.sh/uv/ - `maturin` itself isn't a separate
prerequisite, it's launched via `uvx maturin` and fetched into uv's tool
cache on first use), `valgrind`, Python 3. Noise mitigation
(`powercfg.exe`/`powershell.exe` via WSL2's Win32 interop) is Windows/WSL2
specific and degrades to warnings-only elsewhere; `taskset`/`nice` are used
if present.

## Output layout

```
<output>/
  manifest.jsonl       # append-only index; also drives resume
  _state/dialect_hash.txt
  _worktree/           # single persistent git worktree, reused across commits
  _cargo-target/       # shared CARGO_TARGET_DIR for real incremental builds
  _venv_tmp/           # scratch parent dir for per-commit venvs (see below)
  _fixtures/tpc/       # downloaded TPC-H/TPC-DS query cache (fetched once)
  <sha>/
    meta.json                              # commit info, build timings, env readings
    <mode>-<suite>-callgrind.out           # raw valgrind callgrind output
    <mode>-<suite>-callgrind-run.json      # marker file from bench_runner.py
    <mode>-<suite>-walltime.json           # raw round timings + achieved RME
```

Unlike the Rust side, the Python environment a commit gets installed into is
**not** reused: each commit gets a brand-new `uv venv` in a directory that
did not exist before (`_venv_tmp/<sha>-XXXXXXXX/`, via `tempfile.mkdtemp`),
built with `uv venv` + `uv pip install`, and discarded the moment that
commit's 12 measurements are done - win or lose. `_venv_tmp/` itself is
wiped at the start of every real run, since a hard-killed previous run can
leave one behind (Python doesn't unwind `finally` blocks on a plain SIGTERM)
and none of them are ever a resume source of truth - only `manifest.jsonl` is.

Skipped commits get a `meta.json` stub (`skipped: true`, with a reason) and
no other files, so the manifest has full provenance for the whole range even
though most commits in it were never built.

A secondary analysis script should read `manifest.jsonl` to know which
commits exist and in what order, then load each `<sha>/meta.json` and the
raw `callgrind.out`/`walltime.json` files directly - nothing here is
pre-aggregated across commits.

## Design notes / known limitations

- **Dialect-codegen caching**: skips `utils/rustify.py build` only when a
  hash over the generation scripts themselves (`utils/rustify.py`,
  `utils/build_{dialect,dialects,lexers,parsers}.py`) *and* everything they
  introspect (`src/sqlfluff/core/dialects/**`, `src/sqlfluff/core/parser/**`,
  `src/sqlfluff/dialects/**`) is unchanged since the last commit. Narrower
  hashing (e.g. dialect files alone) would go silently stale on a commit that
  changes grammar/segment internals without touching a single `dialect_*.py`
  file - there's no CI check that would catch that for us, so this errs
  wide on purpose.
- **Build is always fresh per commit**, cheapened by cargo's own incremental
  compilation (shared `CARGO_TARGET_DIR`, one persistent worktree so paths
  stay stable) - not by skipping the rebuild itself.
- **Sequential by design**: build and measurement never overlap, even though
  pipelining the next commit's build during the current commit's measurement
  would hide latency - on a small core count that risks bleeding compile-job
  noise into the walltime pass.
- **A commit that fails to build is recorded, not fatal** - `meta.json` gets
  `build_failed: true` and the sweep continues to the next commit.
- **Resume semantics**: a dry-run pass treats any prior visit (real or dry)
  as done. A real run only accepts a prior *real* measurement as done - it
  will never treat a dry-run stub as sufficient and silently skip a commit
  that was never actually measured.
