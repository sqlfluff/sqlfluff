---
name: grammar-review
description: Review a SQLFluff dialect/grammar change (PR number, branch, or local diff touching src/sqlfluff/dialects/ or test/fixtures/dialects/). Checks the grammar against vendor docs, notes when a real database is available in Docker (runs the fixture SQL on it only if asked), and applies a checklist of recurring reviewer requests from past PRs. Use when asked to "review this dialect PR", "review grammar changes", "check this against the docs", or /grammar-review.
---

# Grammar review

Input: a PR number, a branch, or nothing (= the working-tree diff vs `main`).
Output: findings grouped as **Blocking / Required / Suggestion / Question / Nit**. Each one
gets a `file:line` and, where it applies, the doc link or DB output that backs it.
Never post to GitHub unless the user asks.

Supporting files (read them when you reach the step). `<skill-dir>` is the folder this file is in: Claude Code
prints it as "Base directory for this skill"; in the repo it's `.claude/skills/grammar-review/`.
- [checklist.md](checklist.md): recurring reviewer requests from past PRs, each tagged with its severity. Go through it line by line.
- [sources.md](sources.md): precedent PRs and quotes per checklist item. **Don't read it
  unless the user asks for a source**, or wants a precedent to cite against pushback.
- [dialects.md](dialects.md): docs roots per dialect, Docker images, run commands, syntax-error signatures.

## 1. Scope the change

```bash
gh pr view N -R sqlfluff/sqlfluff --json title,body,files,headRefName   # PR
gh pr diff N -R sqlfluff/sqlfluff   # branch: git diff main...BRANCH; no input: git diff main (includes uncommitted)
```

List each of these: dialect(s) touched, segments added or changed (class name +
`type`), `.replace()`/`.add()` calls, keyword-set edits, fixture `.sql`/`.yml`
pairs. Note the dialect's parent chain (`grep copy_as src/sqlfluff/dialects/dialect_<d>.py`).
A change to ansi or postgres reaches every child dialect that inherits the affected segment; children that
override it don't get the change.

To run anything, put the PR in its own worktree. Don't touch the user's checkout
and **don't use `git stash`**:

```bash
git fetch https://github.com/sqlfluff/sqlfluff.git pull/N/head && git worktree add <scratchpad>/pr-N FETCH_HEAD
```

## 2. Mechanical checks (run them, don't eyeball)

From the PR worktree:

```bash
tox -e generate-fixture-yml -- -d <dialect>     # then: git status --porcelain test/fixtures
tox -e py312 -- test/dialects/ -k <dialect> -n auto
grep -ln "unparsable" test/fixtures/dialects/<dialect>/<changed>.yml
```

- Any diff after regenerating means stale `.yml` or a bad `_hash`: **Blocking**.
- `unparsable` in a changed fixture: **Blocking**, unless it's a deliberate test of a failure.
- Use tox, not the dev venv. If `sqlfluffrs` is installed, `use_rust_parser = auto`
  parses with the Rust tables **compiled at build time**, which are the *old* grammar. That only
  affects your local runs. Never ask the PR author to regenerate Rust tables: they are gitignored
  and CI builds them. Local parity check: `tox -e build-rs`, then `tox -e rust -- test/dialects -k <dialect>`.
- If other dialects inherit the change, also regenerate their fixtures (one run per dialect: `-d` takes a single value and a repeated `-d` keeps only the last).

## 3. Compare against vendor docs

For each new or changed segment:
1. Find the docs: the segment docstring URL, then the PR body, then the root in
   dialects.md. Fetch the page (WebFetch or the web-fetch agent). Use the docs
   version matching what the dialect targets.
2. Build a clause matrix: each clause/option in the doc's syntax block →
   **covered / missing / differs**. Then check the reverse direction too: what
   does the grammar accept that the docs don't allow?
3. Things to look for:
   - **Over-acceptance**: `Ref("ExpressionSegment")` where the docs require a literal or identifier,
     `Delimited` where only one item is allowed, `Anything()`, `optional=True` on required parts.
   - **Ordering**: docs say options can come in any order, but the grammar is a fixed `Sequence`.
     Usually wants `AnySetOf(...)` (checklist item 5).
   - **Missing alternatives** the PR claims to support. Missing clauses the PR doesn't
     claim are only a Suggestion or Question. Partial support is fine if it's honest.
   - **Keyword placement**: check every new keyword against the vendor reserved list.
   - **Wrong dialect level**: syntax added to ansi/postgres that only one child supports.
4. Every fixture statement should be valid per the docs. Invalid SQL that only
   "works" because the grammar is loose is **Required**.
5. Calibrate severity to the maintainers' line (top of checklist.md). Missing valid
   syntax matters more than accepting invalid syntax. Flag over-acceptance only when
   it is *structural*: clause order, syntax the dialect lacks, a widened shared grammar.
   Never ask for negative tests. Syntax you can't find in any doc → a **Question**
   ("where is this documented?"). If a DB is runnable, say step 4 could settle it.

## 4. Live database check (optional, only on request)

This step is never part of the default review. Don't prompt for it or start
anything. If dialects.md lists a runnable database for the dialect, add one line
to the report header, for example:
`DB: postgres:17 available, ask me to run the fixtures against it`.
Leave that line out for dialects that aren't runnable.

Run it only when the user asks, either now or as a follow-up. Before starting:
`docker ps -a --filter name=sqlfluff-review-`, and look for a running container
from the same image (offer to reuse it). Mention any license/EULA the image
accepts, plus the startup tier.

Then:
1. Start it, then wait for readiness by polling the client in an until-loop (Monitor), not with sleeps.
2. Write sample tables the fixture references (setup `.sql` in the scratchpad), so
   statements *execute* instead of stopping at "undefined name". Run each statement
   against a fresh copy: setup, statement, rollback (transactional DDL: db2, postgres,
   sqlite, duckdb) or drop/recreate (mysql/mariadb/oracle). When statements need
   conflicting states (`ADD COLUMN b` vs `ALTER COLUMN b`), write setup *variants*; a
   statement passes if it succeeds under any variant. For db2, postgres, sqlite and duckdb, use
   `<skill-dir>/sql_run.py ENGINE FIXTURE.sql [SETUP1.sql ...]`. It
   does all of this and prints TSV verdicts (PASS/SYNTAX/SEMANTIC/UNKNOWN). Treat UNKNOWN
   as unchecked. For other engines, use the commands in dialects.md. Strip `{{ }}`/Jinja first if present.
3. Classify each statement with the signature column. **Syntax error** = the DB
   rejects it, so the fixture is invalid SQL (**Required**, or **Blocking** if the
   grammar exists only to accept it). **Success** = pass. **Semantic error** = parsed;
   then decide whether it's a setup gap (fix the setup and rerun: e.g. `DROP DEFAULT`
   on a column with no default) or a real fixture problem (e.g. the same column in two
   clauses of one statement). Report only the real ones. Name the setup variants in the report.
4. Optionally probe the edges: hand-write 2–5 near-miss statements the grammar
   accepts (or rejects) and see whether the DB agrees. This is the quickest way to
   show over- or under-acceptance.
5. When done, offer to stop and remove only `sqlfluff-review-*` containers you started.
   Never touch other containers.

## 5. Apply the checklist

Go through [checklist.md](checklist.md) against the diff. Report each item that applies
at the severity it's tagged with, with its `file:line`. Grammar simplifications are
**Required**, not optional polish. Don't pad the review with items that don't apply. For a PR, also read the existing
cubic-dev-ai and maintainer comments
(`gh api repos/sqlfluff/sqlfluff/pulls/N/comments --paginate`) and skip anything
already raised and resolved.

## 6. Report

```
## Grammar review: <PR title> (<dialect>)
Docs: <links used>   DB: <"<image> available on request" / results if it was run / omit if not runnable>

### Blocking
- path:line: what, why (doc quote or DB error)
### Required
### Suggestion
### Question
### Nit
### Verified OK
- one line each: fixtures regen clean, tests pass, N/N statements accepted by <db>
```

If the user asks to post: one review via `gh api repos/sqlfluff/sqlfluff/pulls/N/reviews --input review.json`,
where the JSON has `"event": "COMMENT"`, the summary as `body`, and inline suggestions (only where the fix
is certain) in `comments` (each `path`, `line`, `side: "RIGHT"`, `body`). `gh pr review --comment` can't post
inline comments. Never approve or request changes on
their behalf unless told to.

When a review turns up a new recurring request, or fixes a wrong command in dialects.md,
update those files in place.
