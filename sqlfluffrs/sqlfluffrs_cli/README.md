# sqlfluffrs_cli — `sqlfluff-rs`

A Rust command entry point for SQLFluff's **templating → lexing → parsing**
pipeline. It owns argument parsing, config resolution and file discovery
natively in Rust, reuses the existing `sqlfluffrs_lexer` / `sqlfluffrs_parser`
crates, and *reverse-dispatches templating* to the existing Python templaters.

## Commands

```
sqlfluff-rs render <paths...>   # show the templated SQL
sqlfluff-rs lex    <paths...>   # show the token stream
sqlfluff-rs parse  <paths...>   # show the parse tree
```

`-` reads from stdin. Common options mirror the Python CLI: `--dialect/-d`,
`--templater/-t`, `--config`, `--ignore-local-config`, `--encoding`,
`--library-path`, `--stdin-filename`, and per-command `--format/-f`
(`human|json|yaml|none`), plus `parse`'s `--code-only/-c` and `--include-meta/-m`.

Exit codes match Python: `0` success, `1` lint/template/parse failure, `2` error.

## Building

Pure-Rust build (only the `raw` templater is available; no Python needed):

```bash
cargo build -p sqlfluffrs_cli
```

With templating (Jinja, python, placeholder, dbt) via the embedded interpreter:

```bash
PYO3_PYTHON=/path/to/venv/bin/python \
  cargo build -p sqlfluffrs_cli --features embed-python
```

## Runtime requirement (embed-python)

The `embed-python` build links libpython and dispatches templating to the
Python `sqlfluff` package. At runtime that package (and its templater
dependencies — jinja2, optionally dbt) must be importable:

- If a virtualenv is **activated** (`VIRTUAL_ENV` set), its `site-packages` is
  added automatically (including `.pth`/editable installs).
- Otherwise set `PYTHONPATH` to where `sqlfluff` and its deps live.

## Architecture notes

- Config resolution mirrors `FluffConfig` layering (embedded `default_config.cfg`
  → ancestor config files → `--config` → CLI overrides → inline `-- sqlfluff:`
  directives) and produces the nested map handed to the Python `FluffConfig`
  for templating.
- Templating selects the templater generically via `FluffConfig.get_templater()`,
  so the dbt plugin works automatically when installed.
- `parse -f json|yaml` uses `Node::as_record`, matching `sqlfluff parse`'s record
  format (a `[{filepath, segments}]` envelope). The `human` tree is readable but
  not byte-identical to Python's `stringify`.
- The Rust `Node` tree is at parity with Python's AST for the large majority of
  fixtures; a small number of constructs still differ (the `_rs_node` tree is
  not yet consumed by Python) and will converge as the parser does.
