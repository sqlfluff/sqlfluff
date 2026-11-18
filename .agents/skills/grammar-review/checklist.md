# Grammar review checklist

Distilled from past maintainer reviews of dialect PRs. Root `AGENTS.md` overrides it: historical
requests are evidence of preferences, not permanent rules. Item numbers match
[sources.md](sources.md), which holds provenance only.

**Severity.** **Blocking** = broken (stale fixtures, `unparsable`, wrong tree). **Required** = a
correctness problem or an explicit current convention. **Suggestion** = semantics-preserving
improvement, including simplifications. **Question** = needs the author's answer. **Nit** =
cosmetic or process. Apply items to code the PR adds or edits; omit unrelated pre-existing issues.
Valid SQL parsing into the wrong tree is **Blocking**, whichever item finds it. Report one finding
per root cause, with its fix in the same bullet.

**Permissiveness.** A grammar-correctness finding needs valid SQL that fails to parse or parses
into the wrong tree. Accepting another clause order, repeats, or SQL the vendor would reject is
not a finding, and neither is a child dialect now accepting a statement its vendor lacks (don't ask
to add it to a `remove` list). Never ask for negative tests.

Contents: Simplifications (1–8) · Grammar correctness (9–14) · Inheritance and scope (15–19a) ·
Naming, types, rules (20–23) · Keywords (24–25) · Docs and fixtures (27–33) · Docstrings and
process (34–38) · Don't flag.

## Simplifications (Suggestion unless noted)

1. **Don't nest alternatives in a combinator that already chooses between them.** Flatten
   `Delimited(OneOf(a, b))` → `Delimited(a, b)`; likewise `AnyNumberOf` inside `Delimited`, and
   `OneOf` inside `OneOf` or `AnyNumberOf`. Keep the inner wrapper when:
   - it has its own kwargs (`exclude`, `terminators`, `reset_terminators`, `parse_mode`, `min_times`/`max_times`);
   - it sits inside `AnySetOf` or `max_times_per_element`, which count per top-level element, so
     `AnySetOf(OneOf("A", "B"), "C")` deliberately allows only one of A or B;
   - it sits inside `Sequence`, `Bracketed` or `OptionallyBracketed`, whose args are a sequence.
2. **No pointless wrappers.**
   - Single-element `Sequence`/`OneOf` with no kwargs: remove. With only `optional=True`, move it onto
     the element (`OneOf("A", optional=True)` → `Ref.keyword("A", optional=True)`). Keep wrappers whose
     other kwargs change matching. Keep it at the top level of a segment's `match_grammar`, which must
     be a grammar object (`match_grammar = Sequence("NULL")`).
   - A `Sequence` with no kwargs inside a `Sequence`: flatten.
   - `Ref.keyword("KW")` with no kwargs → `"KW"`, except inside `.copy(insert=[...])` lists, where a
     bare string isn't resolved.
   - `Sequence(x, optional=True)` → `x` with `optional=True`.
3. **Required:** `optional=True` on a direct child of `OneOf`/`AnySetOf`/`AnyNumberOf`/`Delimited`
   does nothing, so the intended optional form fails. Make the outer grammar optional.
4. **Merge branches with the same structure:** `OneOf(Sequence("A", x), Sequence("B", x))` →
   `Sequence(OneOf("A", "B"), x)`.
5. **Required when valid orders fail:** options that appear at most once each, in any order, need
   `AnySetOf`, not a `Sequence` of optionals. `AnyNumberOf(max_times_per_element=1)` is `AnySetOf`.
   If options may repeat, use `AnyNumberOf`; `AnySetOf` would reject valid repeats.
6. **`OneOf(X, Bracketed(X))` → `OptionallyBracketed(X)`.** `Bracketed(X, optional=True)` means (X) or nothing.
7. **Single-segment helpers.** Check whether a new helper belongs only to one enclosing segment. Prefer
   a private class-local grammar when it needs neither a meaningful AST node nor dialect-level
   reuse/override. Check inherited usage and rule consumers before moving or removing a segment.
8. **Reuse before writing.** Check the dialect, its parents and ANSI first (`OrReplaceGrammar`,
   `IfExistsGrammar`, `CollateGrammar`, `SignedSegmentGrammar`, …). Don't redefine an unchanged segment.

## Grammar correctness (Required; Blocking if valid SQL gets the wrong tree)

9. Use an ordered `Sequence` for documented clause order only when a flat `OneOf`/`Delimited`
   mis-parses valid SQL or gives the wrong tree.
10. Use defined grammar instead of `Anything()` wherever it can be written. If `Anything()` is
    unavoidable, it needs a termination point (e.g. inside `Bracketed(...)`); unbounded, it swallows
    the next statement. **Suggestion:** a narrower ref instead of `ExpressionSegment`.
11. Don't bound a grammar with a terminator list copied from another dialect's statements; it drifts
    from the parent. Bound it structurally, and prefer `exclude=` on the ref that steals a keyword over
    adding terminators. When a change adds terminators or closes a block, probe the nested constructs
    the body allows (`CASE … ELSE … END`, sub-blocks, nested statements) inside each statement form it
    accepts (SELECT/DML, not just assignment), on base and head. Base parses, head doesn't: **Blocking**.
12. In a `OneOf`, a specific keyword comes before a generic ref that would also match it
    (`CURRENT_USER` before `RoleReferenceSegment`).
13. New lexer rules must not steal identifiers or operators: anchor them, and run them after the word
    lexer where possible. A lexer regex change may need the prefilter in `utils/build_lexers.py`.
    **Suggestion:** prefer `StringParser`/`MultiStringParser`/`TypedParser` over a new `RegexParser`.
14. **Suggestion:** model nested parens recursively, not to a fixed depth.

## Inheritance and scope

15. **Required:** hook into the grammar ladders (`Expression_A..D_Grammar`, `SelectableGrammar`,
    `NonWithSelectableGrammar`) instead of overriding whole segments; cover the `UNION` path too.
16. **Suggestion:** prefer a `Nothing()` placeholder in the parent, overridden in the child, over a
    positional `.copy(insert=…, at=/before=)`. Fine when there's no clean hook point.
17. **Required:** check the blast radius. Children inherit the change (postgres → redshift/duckdb/
    greenplum/materialize, sparksql → databricks, mysql → mariadb/doris/starrocks, hive → impala);
    siblings that override the segment don't get the fix. **Suggestion:** dialect-only syntax belongs
    in that dialect.
18. Widening a shared grammar (`FunctionParameterGrammar`, access-object grammars) for one statement:
    **Required** to scope locally if other statements' valid SQL now parses differently; otherwise a
    **Suggestion**.
19. **Suggestion:** syntax valid in many dialects goes in ANSI once, instead of an override in each.
19a. **Required:** a new *selectable* node type (added to `SelectableGrammar`/`NonSetSelectableGrammar`):
    run AM04/AM07/ST03/RF01 on a CTE + set-expression sample. `src/sqlfluff/utils/analysis/query.py`
    hard-codes `select_statement`/`values_clause`. **Blocking** if a rule throws.

## Naming, types, rules

20. **Required:** classes end in `…Segment`, statements in `…StatementSegment`, grammars in
    `…Grammar`. An override keeps the parent's name with no dialect prefix. Statements are segments.
21. **Required — cross-dialect AST consistency.** Before introducing a segment, grammar or type,
    compare equivalent constructs in ANSI, the parent and other relevant dialects. Prefer established
    names, semantic types (`data_type_identifier`, boolean literals) and compatible tree shapes, so
    existing rules and query-analysis helpers work without dialect-specific exceptions. Introduce
    differences only when the SQL semantics require them; explain why and test affected rule behaviour.
22. **Required:** check rule impact (RF01/02, LT01/02, CP0x, CV11, ST05/09). Lint only the new or
    changed statements and compare with the base; for a new clause, compare with the same SQL minus
    that clause; lint a wholly new statement on its own. Skip it when the change only adds tokens to
    an existing node shape. Fixtures aren't lint-clean, so layout, capitalisation and CV11 hits aren't
    findings. A rule result the new tree causes (e.g. CP02 on a keyword parsed as an identifier) is
    evidence for the tree finding. If behaviour changes, add rule YAML cases.
23. **Blocking:** read the `.yml` tree for the right shape, not just "no unparsable".

## Keywords (Required)

24. Keywords are unreserved unless the vendor reserves them in the versions the dialect targets.
25. Edit keyword lists in `dialect_<x>_keywords.py`, in uppercase. Add only keywords the grammar
    uses, and drop newly unused ones.

## Docs and fixtures

27. Cover the documented syntax the PR claims (optional clauses, abbreviations, aliases, empty forms,
    quoted identifiers): **Required** for claimed forms, **Suggestion** otherwise.
28. **Question:** syntax not in the vendor docs → "where is this documented?" If it runs on the
    real database, keep it.
29. **Blocking:** `.yml` files are regenerated, never hand-edited. A parent/ANSI change → the author
    regenerates every inheriting dialect (CI checks it). Reviewers regenerate a child locally only when
    the change reaches a segment it inherits and one of its fixtures uses that construct.
30. **Required:** a positive fixture for every new branch and modified grammar, using any new keyword.
    Keep the old case; test repeated forms where the syntax allows repeats.
31. **Required:** test with SQL/YAML fixtures; Python tests in `test/dialects/*_test.py` only for what
    a fixture can't express.
32. **Required:** put the fixture in the most specific dialect and the right `<statement>.sql`.
33. **Nit:** files end with a trailing newline.

## Docstrings and process

34. **Suggestion:** docstrings link to current, non-versioned vendor docs and say why a segment
    overrides its parent.
35. **Suggestion:** one dialect and one statement per PR. Out-of-scope gaps go to a follow-up PR; a
    dialect fix that needs core parser changes gets a separate PR for them.
36. **Required:** a new dialect also needs entries in `pyproject.toml` keywords, the README,
    `.github/labeler.yml` and `src/sqlfluff/core/dialects/__init__.py`.
37. **Question:** for AI-assisted PRs, has the author reviewed the code and answered bot comments?
38. **Nit:** if CI lint fails, run pre-commit (`tox -e pre-commit -- run --all-files`). Merge or rebase
    on `main` for a stale branch. Avoid force-pushing once review has started. Title:
    `<Dialect>: <short description>`.

## Don't flag

- Rust table regeneration (CI does it), keyword alphabetical order, `StatementSegment` list order,
  missing negative tests, and unrelated pre-existing issues.
- Points already raised and resolved in review comments.
