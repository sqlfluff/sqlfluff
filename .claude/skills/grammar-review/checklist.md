# Grammar review checklist

Recurring maintainer requests on dialect PRs. Report each item that applies at its
severity, with `file:line`. Item numbers match sources.md (precedent PRs and quotes),
but read that only when asked for a source.

**Severity:** **Blocking** = broken. **Required** = must change before merge; every
simplification is Required. **Suggestion** = can be a follow-up. **Question** = needs
the author's answer. **Nit** = cosmetic or process.

**Strictness:** parsing all valid SQL matters more than rejecting invalid SQL.
Accepting a superset is fine if it keeps the grammar simple. Flag only *structural*
over-acceptance: wrong clause order, syntax the dialect lacks, a widened shared grammar.
Never ask for negative tests.

## Simplifications (Required)

Required for grammar the PR adds or edits. In untouched code nearby, it's a **Suggestion** ("while you're here").

1. **Don't nest alternatives in a combinator that already chooses between them.** Flatten
   `Delimited(OneOf(a, b))` → `Delimited(a, b)`. The same goes for `AnyNumberOf` inside
   `Delimited`, and for `OneOf` inside `OneOf` or `AnyNumberOf`.
   Leave the inner wrapper alone when:
   - it has its own kwargs (`exclude`, `terminators`, `reset_terminators`, `parse_mode`, `min_times`/`max_times`);
   - it sits inside `AnySetOf` or `max_times_per_element`, which count per top-level
     element, so `AnySetOf(OneOf("A", "B"), "C")` deliberately allows only one of A or B;
   - it sits inside `Sequence`, `Bracketed` or `OptionallyBracketed`, whose args are a sequence.
2. **No pointless wrappers.**
   - Single-element `Sequence`/`OneOf` with no kwargs: remove. With only `optional=True`, move it onto the element
     (`OneOf("A", optional=True)` → `Ref.keyword("A", optional=True)`). Other kwargs (`exclude`, `terminators`,
     `parse_mode`) change matching, so keep the wrapper. Exception: keep it at the top level of a segment's `match_grammar`,
     which must be a grammar object, not a bare string (`match_grammar = Sequence("NULL")`).
   - A `Sequence` with no kwargs inside a `Sequence`: flatten.
   - `Ref.keyword("KW")` with no kwargs → `"KW"`. Exception: inside `.copy(insert=[...])` lists a bare
     string isn't resolved and fails at parse time (`'str' object has no attribute 'simple'`), so keep `Ref.keyword` there.
   - `Sequence(x, optional=True)` → `x` with `optional=True`.
3. **`optional=True` on a direct child of `OneOf`/`AnySetOf`/`AnyNumberOf`/`Delimited` does
   nothing.** Make the outer grammar optional.
4. **Merge branches with the same structure:** `OneOf(Sequence("A", x), Sequence("B", x))` →
   `Sequence(OneOf("A", "B"), x)`.
5. **Options that appear once each, in any order → `AnySetOf`.** Not `AnyNumberOf`
   (allows repeats), not `max_times_per_element=1`, not a `Sequence` of optionals.
6. **`OneOf(X, Bracketed(X))` → `OptionallyBracketed(X)`.** Note that
   `Bracketed(X, optional=True)` means (X) or nothing.
7. **A helper used by one statement → a private `_name` grammar in the class.** If it has
   no meaningful `type`, make it a `*Grammar`, not a segment.
8. **Reuse before writing.** Check the dialect, its parents and ANSI first
   (`OrReplaceGrammar`, `IfExistsGrammar`, `CollateGrammar`, `SignedSegmentGrammar`, …).
   Don't redefine a segment you haven't changed.

## Grammar correctness (Required)

9. Documented clause order → an ordered `Sequence`, not a flat `OneOf`/`Delimited`.
10. Use defined grammar instead of `Anything()` wherever it can be written. If `Anything()` is unavoidable,
    it needs a termination point, e.g. inside `Bracketed(...)`; unbounded, it swallows the next statement.
    Likewise, no `ExpressionSegment` where a narrower ref fits.
11. Don't bound a grammar with a terminator list copied from another dialect's statements, because it drifts
    from the parent. Bound it structurally instead (brackets, delimiters, the statement grammar). Scope
    terminators so they don't leak into nested constructs (`CASE … ELSE` inside an `IF`).
12. In a `OneOf`, a specific keyword comes before a generic ref that would also match it (`CURRENT_USER` before `RoleReferenceSegment`).
13. New lexer rules must not steal identifiers or operators. Anchor them, and run them after the word lexer where
    possible. A lexer regex change may also need the prefilter in `utils/build_lexers.py`. **Suggestion:** prefer
    `StringParser`/`MultiStringParser`/`TypedParser` over a new `RegexParser`, and keep regexes in the lexer.
14. **Suggestion:** model nested parens recursively, not to a fixed depth.

## Inheritance and scope (Required unless noted)

15. Hook into the grammar ladders (`Expression_A..D_Grammar`, `SelectableGrammar`,
    `NonWithSelectableGrammar`) instead of overriding whole segments. Cover the `UNION` path too.
16. **Suggestion:** prefer a `Nothing()` placeholder in the parent, overridden in the child, over a positional
    `.copy(insert=…, at=/before=)`. Positional inserts break when the parent changes. Fine when there's no clean hook point.
17. Check the blast radius:
    - Children inherit the change: postgres → redshift/duckdb/greenplum/materialize, sparksql → databricks,
      mysql → mariadb/doris/starrocks, hive → impala.
    - Siblings that override the same segment don't get the fix.
    - Databricks-only syntax goes in databricks.
18. Only widen a shared grammar with syntax that's valid everywhere it's used. One statement's syntax added to a
    grammar other statements use (`FunctionParameterGrammar`, access-object grammars) makes them accept it too,
    so scope it to that statement.
19. **Suggestion:** syntax valid in many dialects goes in ANSI once, instead of an override in each dialect.
    ANSI may be a little looser than individual dialects.
19a. A new *selectable* node type (anything added to `SelectableGrammar`/`NonSetSelectableGrammar`): run
    AM04/AM07/ST03/RF01 on a CTE + set-expression sample. `utils/analysis/query.py` hard-codes
    `select_statement`/`values_clause`. **Blocking** if a rule throws, Required if a rule silently misses.

## Naming, types, rules

20. **Required:** classes end in `…Segment`, statements in `…StatementSegment`, grammars in `…Grammar`.
    An override keeps the parent's name with no dialect prefix. Statements are segments.
21. **Required:** use the token types rules expect (`data_type_identifier`, boolean literal), and reuse existing `type` names.
22. **Required:** check rule impact (RF01/02, LT01/02, CP0x, CV11, ST05/09) by running `sqlfluff lint` on the fixture.
    If behaviour changes, add rule YAML cases.
23. **Blocking:** read the `.yml` tree for the right shape, not just "no unparsable".

## Keywords (Required)

24. Keywords are unreserved unless the vendor reserves them in the versions the dialect targets.
25. Edit keyword lists in `dialect_<x>_keywords.py`, in uppercase. Add only keywords the grammar uses, and drop newly unused ones.
26. No keywords for syntax the dialect lacks; remove the statement instead.

## Docs

27. **Suggestion** (**Required** if the PR claims the form): cover the documented syntax completely for the touched
    statement. That includes optional clauses, abbreviations, aliases, empty forms and quoted identifiers.
28. **Question:** if the syntax isn't in the vendor docs, ask "where is this documented?". If it runs on the real DB, keep it.

## Tests and fixtures

29. **Blocking:** `.yml` files must be regenerated, never hand-edited. A parent/ANSI change → regenerate every inheriting dialect.
30. **Required:** a fixture for every new branch and every modified grammar. If the change adds a keyword, the
    fixture must use it. Keep the old case, and test repeated forms where the syntax allows repeats.
31. **Required:** test with SQL/YAML fixtures. Python tests in `test/dialects/*_test.py` only for what a fixture
    can't express.
32. **Required:** put the fixture in the most specific dialect and the right `<statement>.sql`. Extend that file rather than duplicating it.
33. **Nit:** files end with a trailing newline.

## Docstrings and process

34. **Suggestion:** docstrings link to current, non-versioned vendor docs (check for 404s) and say why a segment overrides its parent.
35. **Suggestion:** one dialect and one statement per PR. Gaps outside the PR's scope that turn up in review go to
    a follow-up PR, not a blocker. A dialect fix shouldn't pull in core parser changes; if it needs them, they
    get their own PR.
36. **Required:** a new dialect also needs entries in `pyproject.toml` keywords, the README, `.github/labeler.yml` and `src/sqlfluff/core/dialects/__init__.py`.
37. **Question:** for AI-assisted PRs, has the author reviewed the code and answered cubic's comments?
38. **Nit:** if CI lint fails, run pre-commit (`tox -e pre-commit -- run --all`). If the branch is stale or CI fails
    for unrelated reasons, merge or rebase on `main`. Avoid force-pushing once review has started. Title format:
    `<Dialect>: <short description>`.

## Don't flag

- Rust table regeneration. CI does it; a stale local `sqlfluffrs` only affects your own test runs.
- Keyword alphabetical order, `StatementSegment` list order, missing negative tests.
- Comments cubic or a maintainer already raised that have been resolved.
