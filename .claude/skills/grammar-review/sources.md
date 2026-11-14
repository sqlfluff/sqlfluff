# Checklist sources

Evidence behind each item in checklist.md, keyed by the same numbers. **Read this
only when asked for a source**, or when a PR author pushes back on an item and a
precedent would help.

Method: the human, non-author review comments on ~1,000 merged PRs touching
`src/sqlfluff/dialects/` (#3800–#9124), mined 2026-11-13. About 419 of those PRs had
substantive review. `~N` = roughly how many PRs a maintainer raised the item in. PR
links are `https://github.com/sqlfluff/sqlfluff/pull/<n>`.

| # | Freq | PRs and quotes |
|---|---|---|
| 1 | ~12 (top request) | [8252](https://github.com/sqlfluff/sqlfluff/pull/8252) "the `OneOf` can be removed as `Delimited` is a type of `OneOf`"; [7279](https://github.com/sqlfluff/sqlfluff/pull/7279), [4642](https://github.com/sqlfluff/sqlfluff/pull/4642) "You don't need this AnyNumberOf inside Delimited". AnySetOf exception: `option_counter` in `src/sqlfluff/core/parser/grammar/anyof.py` |
| 2 | ~10 | [7046](https://github.com/sqlfluff/sqlfluff/pull/7046) "These Sequence wrappers aren't needed… just write it as `"COMPILE"`"; [8126](https://github.com/sqlfluff/sqlfluff/pull/8126) "plain "NOT" is just as good"; [4616](https://github.com/sqlfluff/sqlfluff/pull/4616); top-level `match_grammar` exception: WittierDinosaur on [9166](https://github.com/sqlfluff/sqlfluff/pull/9166) "A wrapper is needed at the top level of a match grammar - it's rare, but worth calling out" |
| 3 | ~6 | [5995](https://github.com/sqlfluff/sqlfluff/pull/5995) "remove the optional=True from all of these nested sequences, and move it to the AnySetOf"; [6063](https://github.com/sqlfluff/sqlfluff/pull/6063) "setting… `optional` within a `OneOf` has no effect" |
| 4 | ~5 | [4358](https://github.com/sqlfluff/sqlfluff/pull/4358) "These 4 are the same structurally… wrap the keywords in a OneOf()"; [4381](https://github.com/sqlfluff/sqlfluff/pull/4381), [6953](https://github.com/sqlfluff/sqlfluff/pull/6953) |
| 5 | ~7 | [4721](https://github.com/sqlfluff/sqlfluff/pull/4721) "Rather than `AnyNumberOf(..., max_times_per_element=1)` you can just use `AnySetOf`"; [8890](https://github.com/sqlfluff/sqlfluff/pull/8890), [8124](https://github.com/sqlfluff/sqlfluff/pull/8124), [7393](https://github.com/sqlfluff/sqlfluff/pull/7393) |
| 6 | ~6 | [6063](https://github.com/sqlfluff/sqlfluff/pull/6063) "`OptionallyBracketed("FOO")` would match `FOO` and `(FOO)`"; [7515](https://github.com/sqlfluff/sqlfluff/pull/7515), [6461](https://github.com/sqlfluff/sqlfluff/pull/6461) |
| 7 | ~5 | [8025](https://github.com/sqlfluff/sqlfluff/pull/8025) "define the grammar elements which are used _only_ inside a specific structure… locally"; [9049](https://github.com/sqlfluff/sqlfluff/pull/9049) "A number of these don't appear to really need the `type`. Can these be Grammars"; [7513](https://github.com/sqlfluff/sqlfluff/pull/7513) |
| 8 | ~15 | [6377](https://github.com/sqlfluff/sqlfluff/pull/6377) "I can't see any edits vs the classes created in the ansi dialect, so no need to redefine"; [7501](https://github.com/sqlfluff/sqlfluff/pull/7501); [7943](https://github.com/sqlfluff/sqlfluff/pull/7943) "should be using the new… `CollateGrammar`" |
| 9 | ~12 (cubic's #3 theme) | [8212](https://github.com/sqlfluff/sqlfluff/pull/8212) "should be modeled with an ordered sequence rather than an unconstrained alternation" |
| 10 | ~7 | [8187](https://github.com/sqlfluff/sqlfluff/pull/8187) "`Anything()` fallback… consumes the following statement whole, and the file then lints clean"; [4690](https://github.com/sqlfluff/sqlfluff/pull/4690); [4854](https://github.com/sqlfluff/sqlfluff/pull/4854) "`ExpressionSegment` is a very broad segment, and doesn't perform well" |
| 11 | ~6 | [8380](https://github.com/sqlfluff/sqlfluff/pull/8380) "A `CASE` expression within the `IF` body has its own `ELSE`… treated as a terminator"; [8187](https://github.com/sqlfluff/sqlfluff/pull/8187) "hand-coded terminator list is the wrong shape"; [8468](https://github.com/sqlfluff/sqlfluff/pull/8468), [8270](https://github.com/sqlfluff/sqlfluff/pull/8270) |
| 12 | 1 | [9032](https://github.com/sqlfluff/sqlfluff/pull/9032) "`CURRENT_USER` will need to come before `RoleReferenceSegment`" |
| 13 | 5 | Lexer: [8067](https://github.com/sqlfluff/sqlfluff/pull/8067) "overmatch valid Oracle code… they steal ordinary identifiers at line start"; [8011](https://github.com/sqlfluff/sqlfluff/pull/8011) "I think this breaks the modulo operator" / "just a bit overly greedy". RegexParser (Suggestion; one 2023 comment, and dialects still use it ~100×): [4725](https://github.com/sqlfluff/sqlfluff/pull/4725) "we're actively trying to deprecate the RegexParser… `TypedParser` may be able to achieve what you're after"; [7875](https://github.com/sqlfluff/sqlfluff/pull/7875) "using the `MultiStringParser` instead of this custom function would be the preferred approach". Prefilter: [7471](https://github.com/sqlfluff/sqlfluff/pull/7471) |
| 14 | 2 | [8393](https://github.com/sqlfluff/sqlfluff/pull/8393) "a third redundant layer… remains unparsable. Could we model this recursively"; [9031](https://github.com/sqlfluff/sqlfluff/pull/9031) |
| 15 | ~6 | [8016](https://github.com/sqlfluff/sqlfluff/pull/8016) "Prefer extending `Expression_A_Grammar` over subclassing `ExpressionSegment`"; [7895](https://github.com/sqlfluff/sqlfluff/pull/7895) "should we use `SelectableGrammar` instead?"; [8229](https://github.com/sqlfluff/sqlfluff/pull/8229) |
| 16 | ~8 | [7897](https://github.com/sqlfluff/sqlfluff/pull/7897) "brittle as based on position in a parent grammar… look for `AddDropSystemVersioningGrammar=Nothing()`"; [8601](https://github.com/sqlfluff/sqlfluff/pull/8601) "Avoid the hard-coded at=3 insert"; [8101](https://github.com/sqlfluff/sqlfluff/pull/8101) "`copy()` appends at the end… outside the inherited `Indent`/`Dedent`"; counterpoint, [8402](https://github.com/sqlfluff/sqlfluff/pull/8402) "a full replacement would duplicate a substantial ANSI grammar merely to add two standalone privileges… The small inheritance delta is the better tradeoff here"; [8130](https://github.com/sqlfluff/sqlfluff/pull/8130), [6018](https://github.com/sqlfluff/sqlfluff/pull/6018) |
| 17 | ~7 | [8216](https://github.com/sqlfluff/sqlfluff/pull/8216) "appears to widen Postgres 17 MERGE syntax into Redshift through dialect inheritance"; [8393](https://github.com/sqlfluff/sqlfluff/pull/8393) "ClickHouse, Hive, Snowflake, and SparkSQL override… so they will not inherit this fix"; [4568](https://github.com/sqlfluff/sqlfluff/pull/4568) |
| 18 | 2 cited | [8402](https://github.com/sqlfluff/sqlfluff/pull/8402) "Adding it to the shared access-object grammar makes SQLFluff accept… `GRANT ALL ON COPY JOBS`"; [8352](https://github.com/sqlfluff/sqlfluff/pull/8352) "The `TABLE(...)` grammar change leaks into other function signatures" |
| 19 | ~5 | [4127](https://github.com/sqlfluff/sqlfluff/pull/4127) "ok to make the ANSI file a little looser… better than copying the segment"; [4209](https://github.com/sqlfluff/sqlfluff/pull/4209), [7398](https://github.com/sqlfluff/sqlfluff/pull/7398) |
| 19a | 1 | [8924](https://github.com/sqlfluff/sqlfluff/pull/8924) peterbud (changes requested): "The new `table_statement` nodes are not recognized by query analysis. A TABLE-only set expression inside a CTE can trigger an AM07 `IndexError`, and unused TABLE-bodied CTEs are missed by ST03." |
| 20 | ~5 | [8601](https://github.com/sqlfluff/sqlfluff/pull/8601) "Follow the class naming pattern and end in `...StatementSegment`"; [6985](https://github.com/sqlfluff/sqlfluff/pull/6985) "can we drop the Flink from these?"; [8762](https://github.com/sqlfluff/sqlfluff/pull/8762) |
| 21 | ~12 | [6060](https://github.com/sqlfluff/sqlfluff/pull/6060) "get `DateTime64` to parse as a `data_type_identifier`… handled appropriately by the capitalisation rules"; [4129](https://github.com/sqlfluff/sqlfluff/pull/4129) "This already exists in BigQuery but with a different type. Let's keep them consistent"; [8197](https://github.com/sqlfluff/sqlfluff/pull/8197) |
| 22 | ~12 | [7927](https://github.com/sqlfluff/sqlfluff/pull/7927) "introducing a new operator would lead to a regression with rule CV11"; [8620](https://github.com/sqlfluff/sqlfluff/pull/8620); [7802](https://github.com/sqlfluff/sqlfluff/pull/7802) "is there an unintended impact related to the different rules?" |
| 23 | ~10 | [8761](https://github.com/sqlfluff/sqlfluff/pull/8761) "for Databricks it's an incorrect parse tree"; [8484](https://github.com/sqlfluff/sqlfluff/pull/8484) "The tree is inconsistent"; [8124](https://github.com/sqlfluff/sqlfluff/pull/8124) |
| 24 | ~7 | [7077](https://github.com/sqlfluff/sqlfluff/pull/7077) "`BULK` and `COLLECT` don't appear to be reserved words"; [8812](https://github.com/sqlfluff/sqlfluff/pull/8812) "put LIBRARY in as an unreserved keyword… only reserved in MySQL 9.x"; [5918](https://github.com/sqlfluff/sqlfluff/pull/5918) |
| 25 | ~6 | [8050](https://github.com/sqlfluff/sqlfluff/pull/8050) "The lists themselves should be changed under `dialect_sparksql_keywords.py`"; [7835](https://github.com/sqlfluff/sqlfluff/pull/7835) "a bunch of unreserved keywords, but they are NOT used"; [4620](https://github.com/sqlfluff/sqlfluff/pull/4620) |
| 26 | ~4 | [8902](https://github.com/sqlfluff/sqlfluff/pull/8902) "we should be removing it from the grammar, not adding incorrect keywords"; [8862](https://github.com/sqlfluff/sqlfluff/pull/8862) "going out of our way to add an invalid path" |
| 27 | ~15 | [8577](https://github.com/sqlfluff/sqlfluff/pull/8577) "Please add `TRU`… The docs list `TRU[NCATED]`"; [8701](https://github.com/sqlfluff/sqlfluff/pull/8701) "`PATTERN (())`… unparsable. The docs list 'empty pattern ()'"; [8585](https://github.com/sqlfluff/sqlfluff/pull/8585) |
| 28 | — | [7509](https://github.com/sqlfluff/sqlfluff/pull/7509) "where did you get this 'RUNTIME = ONNX'?"; [8701](https://github.com/sqlfluff/sqlfluff/pull/8701) "I can't find that example, can you please point me at it?"; [8312](https://github.com/sqlfluff/sqlfluff/pull/8312) "I don't have a MariaDB to confirm myself. Is that actually supported"; [5726](https://github.com/sqlfluff/sqlfluff/pull/5726) "If it runs - I think we keep it" |
| 29 | ~12 | [4879](https://github.com/sqlfluff/sqlfluff/pull/4879) "Did you generate this manually?… update the hash"; [7398](https://github.com/sqlfluff/sqlfluff/pull/7398) "When you change ANSI… all fixtures should be re-generated"; [7163](https://github.com/sqlfluff/sqlfluff/pull/7163) |
| 30 | ~15 | [8146](https://github.com/sqlfluff/sqlfluff/pull/8146) "you modified the `CREATE FOREIGN TABLE` grammar, but… not added matching regression cases"; [3898](https://github.com/sqlfluff/sqlfluff/pull/3898) "This file doesn't appear to use the new `ORCFILE` keyword"; [8702](https://github.com/sqlfluff/sqlfluff/pull/8702), [8380](https://github.com/sqlfluff/sqlfluff/pull/8380) |
| 31 | ~12 | [8908](https://github.com/sqlfluff/sqlfluff/pull/8908) "The yaml tests cover this, please remove these ones"; [4279](https://github.com/sqlfluff/sqlfluff/pull/4279) "We try to avoid python tests unless really necessary"; [8920](https://github.com/sqlfluff/sqlfluff/pull/8920), [8516](https://github.com/sqlfluff/sqlfluff/pull/8516) |
| 32 | ~10 | [4307](https://github.com/sqlfluff/sqlfluff/pull/4307) "separate this out into a different file? It's not the same statement type"; [4127](https://github.com/sqlfluff/sqlfluff/pull/4127) |
| 33 | — | [6862](https://github.com/sqlfluff/sqlfluff/pull/6862) "All the .sql files… are missing a final newline" |
| 34 | ~7 | [4661](https://github.com/sqlfluff/sqlfluff/pull/4661) "Is there a Greenplum URL… better to explain why overriding"; [7919](https://github.com/sqlfluff/sqlfluff/pull/7919) "that link 404s now"; [6153](https://github.com/sqlfluff/sqlfluff/pull/6153), [8451](https://github.com/sqlfluff/sqlfluff/pull/8451) |
| 35 | 3 direct + 7 follow-ups | [8305](https://github.com/sqlfluff/sqlfluff/pull/8305) "Smaller PRs are much easier to review… focussed on changes to a specific statement"; [4340](https://github.com/sqlfluff/sqlfluff/pull/4340) "Next time, break two logical changes into two PRs" (merged anyway); [8187](https://github.com/sqlfluff/sqlfluff/pull/8187) "drifted too far from the original SparkSQL grammar fix… shared parser behavior, serializer changes, and Rust parser plumbing". Merged with gaps deferred to a follow-up: [9031](https://github.com/sqlfluff/sqlfluff/pull/9031), [8633](https://github.com/sqlfluff/sqlfluff/pull/8633), [8575](https://github.com/sqlfluff/sqlfluff/pull/8575), [8403](https://github.com/sqlfluff/sqlfluff/pull/8403), [8386](https://github.com/sqlfluff/sqlfluff/pull/8386), [8191](https://github.com/sqlfluff/sqlfluff/pull/8191), [3991](https://github.com/sqlfluff/sqlfluff/pull/3991) |
| 36 | 3 | [6415](https://github.com/sqlfluff/sqlfluff/pull/6415), [6985](https://github.com/sqlfluff/sqlfluff/pull/6985) |
| 37 | ~6 (recent) | [8818](https://github.com/sqlfluff/sqlfluff/pull/8818) "we expect submitters to personally review and understand the changes"; [8890](https://github.com/sqlfluff/sqlfluff/pull/8890) "your task is much more than just prompting your agent" |
| 38 | see parts | Pre-commit/black (~10, always after CI lint failed): [6979](https://github.com/sqlfluff/sqlfluff/pull/6979) "Would you mind running the pre-commit hooks… `tox -e pre-commit -- run --all`"; [3972](https://github.com/sqlfluff/sqlfluff/pull/3972), [4112](https://github.com/sqlfluff/sqlfluff/pull/4112), [4340](https://github.com/sqlfluff/sqlfluff/pull/4340), [4642](https://github.com/sqlfluff/sqlfluff/pull/4642), [6018](https://github.com/sqlfluff/sqlfluff/pull/6018), [6059](https://github.com/sqlfluff/sqlfluff/pull/6059), [7163](https://github.com/sqlfluff/sqlfluff/pull/7163), [7370](https://github.com/sqlfluff/sqlfluff/pull/7370), [7387](https://github.com/sqlfluff/sqlfluff/pull/7387). Update from main (~6, mostly to pick up CI fixes; rebase accepted): [7338](https://github.com/sqlfluff/sqlfluff/pull/7338) "Could you merge/rebase your branch onto the `main`?"; [7786](https://github.com/sqlfluff/sqlfluff/pull/7786), [8146](https://github.com/sqlfluff/sqlfluff/pull/8146), [8210](https://github.com/sqlfluff/sqlfluff/pull/8210), [8920](https://github.com/sqlfluff/sqlfluff/pull/8920). Force-push (3): [8515](https://github.com/sqlfluff/sqlfluff/pull/8515) "please don't force push in the future to simplify reviews for us"; [3986](https://github.com/sqlfluff/sqlfluff/pull/3986) "just merge in main… easier to review instead of force-pushes. We squash on PR merges anyways"; [4073](https://github.com/sqlfluff/sqlfluff/pull/4073). Title (1): [4344](https://github.com/sqlfluff/sqlfluff/pull/4344) "usually best to write '<Dialect>: <some short description of the change>'". Dropped: maintainer edits (only [4073](https://github.com/sqlfluff/sqlfluff/pull/4073), 2022), `closes #N` (no source). |

## Strictness line

[8695](https://github.com/sqlfluff/sqlfluff/pull/8695) "drop the negative tests… sqlfluff isn't a validator";
[8520](https://github.com/sqlfluff/sqlfluff/pull/8520) "we generally over-index on the parser accepting all valid sql";
[7329](https://github.com/sqlfluff/sqlfluff/pull/7329), [6112](https://github.com/sqlfluff/sqlfluff/pull/6112).

## Simplification scope

Required on touched lines, Suggestion elsewhere:
[8252](https://github.com/sqlfluff/sqlfluff/pull/8252) "one small nit that was pre-existing then we should be good to merge" (on a line the PR touched);
[7393](https://github.com/sqlfluff/sqlfluff/pull/7393) "I know it was in the original, but maybe we can use this opportunity to make it a bit better";
[6953](https://github.com/sqlfluff/sqlfluff/pull/6953) "nit, this could be cleaner as one sequence".

## Don't flag

- Rust regeneration: keraion in [8658](https://github.com/sqlfluff/sqlfluff/pull/8658), "grammar changes are always generated and tested in CI".
- Alphabetical keyword order: no human reviewer has raised it (only greptile).
- `StatementSegment` ordering: only placement scope was raised ([8081](https://github.com/sqlfluff/sqlfluff/pull/8081)).

## Reviewers asking to verify against docs or a real DB

[8312](https://github.com/sqlfluff/sqlfluff/pull/8312), [7509](https://github.com/sqlfluff/sqlfluff/pull/7509),
[8701](https://github.com/sqlfluff/sqlfluff/pull/8701), [8472](https://github.com/sqlfluff/sqlfluff/pull/8472),
[8221](https://github.com/sqlfluff/sqlfluff/pull/8221), [3997](https://github.com/sqlfluff/sqlfluff/pull/3997),
[5726](https://github.com/sqlfluff/sqlfluff/pull/5726), [4773](https://github.com/sqlfluff/sqlfluff/pull/4773),
[6167](https://github.com/sqlfluff/sqlfluff/pull/6167), [5881](https://github.com/sqlfluff/sqlfluff/pull/5881),
[5727](https://github.com/sqlfluff/sqlfluff/pull/5727), [7491](https://github.com/sqlfluff/sqlfluff/pull/7491),
[8090](https://github.com/sqlfluff/sqlfluff/pull/8090), [8365](https://github.com/sqlfluff/sqlfluff/pull/8365),
[9065](https://github.com/sqlfluff/sqlfluff/pull/9065) (cites the MySQL yacc file in the docstring).

## cubic-dev-ai themes

359 inline comments across 162 PRs:
- over-acceptance: ~82 PRs
- missing fixture coverage or a misparse locked in: ~68
- wrong clause order: ~65
- documented form still unparsable: ~50
- `.yml` not regenerated: ~32
- leaking into child dialects: ~16
- terminators: ~15
- "AI slop / fabricated" syntax: recurring
- redundant `OneOf` in `Delimited`: recurring

Maintainers often reply "agree with cubic" (8177, 8862, 8113, 8065, 8516, 8146). keraion pushed back on local Rust-regen requests ([8658](https://github.com/sqlfluff/sqlfluff/pull/8658)) and on a misread of `optional` scope ([8126](https://github.com/sqlfluff/sqlfluff/pull/8126)).
