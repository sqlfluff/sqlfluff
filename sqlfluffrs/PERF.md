# Performance Gate

The Rust parser engine is under a **hard no-regression mandate**: a maintainability
refactor must not make parsing slower. This is the runbook for proving that.

There are two layers, because they catch different things:

| Layer | Script | What it measures | Status |
|-------|--------|------------------|--------|
| Criterion micro-benchmarks | `utils/perf_gate_rust.py` | pure-Rust parse time, fixed inputs, no FFI | **blocking** |
| End-to-end diff | `utils/perf_gate_e2e.py` | full Python↔Rust path over the fixture corpus | advisory |

The benches live in [`benches/`](benches/) and are registered in
[`Cargo.toml`](Cargo.toml) (`parser_bench`, `baseline_phase1`, `delimited_performance` —
note `autobenches = false`, so a new bench file must be added there or `cargo bench`
skips it).

## Layer 1 — Criterion gate (the one that blocks)

Criterion records each benchmark's change vs. a saved baseline as a point estimate plus a
bootstrap confidence interval. The gate flags a regression only when the **lower** bound of
that interval exceeds the threshold — i.e. we are statistically confident the regression is
real and worse than 5%. A single slow sample cannot trip it; improvements never fail.

```bash
# 1. On the comparison commit (main / merge-base), capture the baseline:
git checkout main
python utils/perf_gate_rust.py --save-baseline main        # or: tox -e perf-baseline-rust

# 2. On your refactor branch, gate against it:
git checkout my-refactor
python utils/perf_gate_rust.py --baseline main --threshold 0.05   # or: tox -e perf-gate-rust
```

The gate prints a per-benchmark table (change %, 95% CI, verdict) and **exits non-zero** if
any benchmark regressed beyond the threshold. Useful flags: `--benches parser_bench`
(subset for a fast inner loop), `--sample-size N` (default 200; lower = faster/noisier),
`--json out.json`.

## Layer 2 — End-to-end diff (advisory)

Diffs two JSON runs from `utils/benchmark_parsing.py` (which already separates lex/parse
time and filters FFI-dominated tiny files at `MIN_PARSE_TIME_MS = 5.0`):

```bash
git checkout main
python utils/benchmark_parsing.py --dialect ansi --limit 100 \
    --iterations 25 --warmup 5 --rust-only --output bench_main.json

git checkout my-refactor
python utils/benchmark_parsing.py --dialect ansi --limit 100 \
    --iterations 25 --warmup 5 --rust-only --output bench_branch.json

python utils/perf_gate_e2e.py --baseline bench_main.json --candidate bench_branch.json
# add --blocking to make it fail the build
```

It fails (when `--blocking`) if total parse time regresses > 8%, median per-file > 10%, or
any large file (≥ 20 ms baseline) regresses > 25%. Advisory by default because the Python
timing path is noisier than criterion; promote to blocking once you've characterised
variance on your machine. `tox -e perf-gate-e2e` wraps the branch run + diff (expects a
`bench_main.json` baseline at the repo root).

## Noise model — why the thresholds are what they are

- **Always compare baseline and candidate on the same machine, same session.** Never gate a
  laptop run against a CI baseline.
- Criterion auto-warms (3 s) and auto-sizes iterations; `--sample-size 200` keeps variance
  low. For the e2e layer use `--iterations 25 --warmup 5` (the tox bench default of 3 is a
  smoke setting, far too few to gate).
- Developer/CI machines drift ~2–5%. The 5% criterion / 8% aggregate thresholds sit above
  that band on purpose, and criterion's significance test guards single-sample outliers.
- `[profile.bench] debug = true` adds small constant overhead but cancels in a *relative*
  comparison, so it's left on (keeps flamegraphs usable). The gate measures deltas, not
  absolutes.

## Per-commit loop (during the engine refactor)

```bash
# once, on main:
tox -e perf-baseline-rust

# after each refactor commit:
tox -e perf-gate-rust                                   # hard gate (>5% fails)
cargo test --test yaml_compare --test fixture_tests     # parity must still hold
```

## CI

[`.github/workflows/ci-perf.yml`](../.github/workflows/ci-perf.yml) runs the criterion gate,
but is **manual-only** (`workflow_dispatch`) because hosted runners are too noisy to
auto-gate every PR. To make it blocking on PRs, add a paths-filtered `pull_request` trigger
(scoped to `sqlfluffrs/sqlfluffrs_parser/**` and `sqlfluffrs/benches/**`) — ideally on a
pinned/self-hosted runner with stable timings.
