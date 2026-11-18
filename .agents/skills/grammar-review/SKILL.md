---
name: grammar-review
description: Reviews SQLFluff dialect grammar PRs, branches or local changes (segments, keywords, fixtures) against vendor documentation, parse-tree expectations, inheritance and fixture coverage. Use for dialect/grammar reviews. Runs live database checks only when explicitly requested.
---

# Grammar review

Input: a PR number, a branch, or local changes. Output: findings grouped as
**Blocking / Required / Suggestion / Question / Nit**, each with `file:line` and the evidence
behind it, plus an evidence ledger (step 7). Never post to GitHub unless asked.

**Policy.** Root `AGENTS.md` ("Grammar is Permissive, Not a Validator" and "Review Scope") is the
authority. Current repository policy overrides historical review comments and this skill.

Files in this skill's folder:
- [checklist.md](checklist.md): the review standards. Read it in full for every review.
- [dialects.md](dialects.md): vendor docs and reserved-word lists per dialect.
- [databases.md](databases.md): candidate live-check backends. Read only when a live check is requested.
- [sources.md](sources.md): optional provenance for checklist items. Read only when asked for a source.

## 1. Scope

- Identify the exact revision under review and its comparison base.
- For local changes, include staged, unstaged and relevant untracked files.
- Preserve the user's checkout. If running anything needs another revision, use a separate worktree.
- List the dialects touched, segments added or changed (class name and `type`), `.replace()`/`.add()`
  calls, keyword-set edits, and fixture `.sql`/`.yml` pairs.
- Note the parent chain (`copy_as`). A change reaches child dialects that inherit the segment;
  children that override it don't get it.

## 2. Mechanical evidence

- Consult CI at the reviewed commit first. Run focused local checks only to answer what CI leaves open.
  With no CI run (local changes, an unpushed branch), run them yourself and record
  `Verified by CI: none (local)`. Keep them focused: the changed fixtures and the tests for the
  touched dialect, not the whole suite.
- Running tox executes the reviewed code (`tox.ini`, `conftest.py`, tests). For code the user didn't
  write, check the changed paths first. If anything outside `src/sqlfluff/dialects/` and
  `test/fixtures/dialects/` changed, ask before running.
- A diff after regenerating fixtures means a stale `.yml` or bad `_hash`: **Blocking**. `git diff`
  can't show this for an untracked `.yml`, so note its `_hash` before regenerating and compare.
  `unparsable` in a changed fixture: **Blocking**.
- Keep scratch files (probe SQL, backups) inside the review worktree.
- Read the `.yml` node for each new or changed statement: check the segment type and its children,
  not just that it parsed.

Project-specific traps:
- If `sqlfluffrs` is installed, `use_rust_parser = auto` parses with Rust tables compiled at build
  time, i.e. the *old* grammar. Use a tox env without it. To check, run
  `cd /tmp && <review env python> -c 'import sqlfluffrs'`: `ModuleNotFoundError` means it isn't
  installed.
  (Inside the repo root it always imports, as an empty namespace package.) Never ask authors to
  regenerate Rust tables: they're gitignored and CI builds them.
- `test/generate_parse_fixture_yml.py -d` takes one dialect; a repeated `-d` keeps only the last.
  `-f` is an anchored glob (`'name*'`): a bare name matches nothing yet still succeeds, so check the
  `Found N file(s)` line. A new top-level statement needs only its own fixture regenerated.

## 3. Compare against vendor docs

For each new or changed segment:
1. Find the docs: the segment docstring URL, then the PR body, then [dialects.md](dialects.md).
   Check syntax against the version-specific page the dialect targets (docstrings still link the
   current, non-versioned page).
2. Build a clause matrix from the doc's syntax: **covered / missing / differs**.
3. A grammar finding must name **valid SQL that fails to parse or parses into the wrong tree**.
   Accepting SQL the vendor would reject is not a finding, and never ask for negative tests.
4. Missing forms the PR claims to support are **Required**; other missing forms are a Suggestion
   or Question. If the PR explicitly defers documented forms, mention them once as a Suggestion
   and check they still fail to parse rather than mis-parse. Syntax you can't find in any doc is a
   **Question**.
5. New fixtures must contain valid SQL. That's about the fixtures; it doesn't justify tightening
   the parser.

## 4. Live database check (only on explicit request)

Never part of the default review. When asked: use an available compatible playground or
disposable local database from [databases.md](databases.md). Check the engine, version and
supported operations first. Never upload sensitive SQL or data. If nothing suitable is
available, report the check as not performed. A listed backend is a candidate, not proof it's
available here.

Run each changed statement from a fresh state (setup, statement, then rollback or recreate),
with setup tables the fixture needs, and several setups when statements need conflicting
states. Only syntax errors count against the grammar: "table does not exist" and similar mean
the database parsed it. Report anything you couldn't classify as not checked. Only stop or
remove containers you started.

## 5. Apply the checklist

Go through [checklist.md](checklist.md) against the diff and report each item that applies at
its severity. Don't pad the review. For a PR, skip points already raised and resolved in
existing review comments.

## 6. Re-check findings

Before reporting, re-check each Blocking and Required finding against the code. It must cite the
valid SQL that fails or the wrong tree, a CI job, or a doc quote. Before reporting a form as
missing, parse it on the reviewed code: it may already be covered. Drop or downgrade to a Question
anything you can't back, and repeat until every remaining finding has its evidence.

## 7. Report

```
## Grammar review: <title> (<dialect>) @ <reviewed sha>
Docs: <links used>

### Blocking
- path:line: what, why (doc quote, CI job or DB output), and the fix
### Required
### Suggestion
### Question
### Nit

Not flagged: <optional, one line>

### Evidence
- Verified locally: <checks and results>
- Verified by CI at <sha>: <jobs>
- Not checked: <and why>
- Inconclusive: <and why>
```

Under the severity headings, list only findings; write `None` under an empty heading. Anything
you wouldn't ask the author to act on is not a finding: put it in the `Not flagged:` line, or
leave it out. Don't list checks that passed outside the Evidence section. For example, not
"### Question: is the extra `OPTIONS` order intended? No action needed." but
"Not flagged: `OPTIONS` accepts any order (permissive, nothing valid mis-parses)."

If asked to post, post one `COMMENT` review with inline comments only where the fix is certain.
Never approve or request changes unless told to.

If the review shows a gap in this skill, list it after the report as a proposed change.
