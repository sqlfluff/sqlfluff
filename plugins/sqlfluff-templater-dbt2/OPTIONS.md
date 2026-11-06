# dbt v2 source-mapping options

The Python dbt templater obtains compiler context through dbt internals and
Python Jinja hooks. Rust dbt cannot expose that same interception point.
The replacement needs execution provenance as well as rendered SQL so that
SQLFluff can identify original source positions and safely apply fixes.

## Upstream render-trace export: implemented reference

[dbt-labs/dbt#16870](https://github.com/dbt-labs/dbt/pull/16870) exports ordered
events from the real render. This plugin consumes those events through a
versioned JSON artifact. It needs no patched runtime in the SQLFluff wheel.

Assumptions: the shipped runtime exposes the exporter; event and offset
semantics remain compatible; source/invocation identity is reliable; and the
trace describes the execution being linted. A stable public contract is still
an upstream design question.

Validation: recorded real traces cover ambiguous branches, repeated and skipped
loops, captures, macros, Unicode and newline handling. The opt-in live project
test exercises source fixes, idempotent recompilation and the CLI. Broad
warehouse/adapter, snapshot-rewrite and cross-platform testing remains necessary.

## Independently patched runtime: earlier proof of concept

A maintained dbt source patch can attach the same observer without waiting for
an upstream release. That worked in the earlier prototype, preserved on the
SQLFluff development checkpoint `48761108f`. This draft supersedes its
standalone MiniJinja helper and private runtime-export patches with the proposed
upstream interface.

Assumptions: licensing and build infrastructure permit distribution; maintained
patches follow runtime changes; the bundled compiler can compile each user's
project correctly. Validation must cover both provenance and project behavior
for every supported producer variant. Native packaging and version management
make this significantly more expensive than consuming a supported upstream API.

## Existing compiled SQL and coarse macro spans

Reading existing artifacts can avoid patching, but coarse macro spans do not
reliably distinguish identical output from different branches, or all repeated
literal regions. Uncertain output must remain nonliteral. Useful compiled-SQL
linting alone does not establish source-fixing parity.

Validation would need adversarial duplicate-output, loop, capture and macro
cases against the exact shipped artifact behavior. The detailed trace route
exists because these artifacts do not expose all the necessary provenance.

## Marker renders or compiler-context reconstruction

Injecting markers risks changing Jinja semantics, whitespace, captures, adapter
queries and macros that inspect SQL. Reconstructing context and rendering in
Python risks diverging from the actual Rust runtime.

Both would require extensive differential testing of real projects. Neither
currently has evidence sufficient to substitute for exact provenance from dbt's
own execution, so this reference implementation does not use either approach.
