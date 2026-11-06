"""Run SQLFluff's real lexer, linter and fixer on upstream render provenance."""

import json
from pathlib import Path

import pytest
from sqlfluff_templater_dbt2.templater import Dbt2Templater
from sqlfluff_templater_dbt2.trace import normalize_newlines

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLTemplaterError


def make_config(**settings):
    """Select the real plugin entry point and a deterministic keyword policy."""
    return FluffConfig(
        configs={
            "core": {
                "dialect": "duckdb",
                "templater": "dbt2",
                "rules": "CP01",
                "use_rust_parser": False,
            },
            "templater": {"dbt2": settings},
            "rules": {"capitalisation.keywords": {"capitalisation_policy": "upper"}},
        }
    )


@pytest.mark.parametrize(
    "case,expected",
    [
        ("literal", "SELECT 1\n"),
        ("expression", "SELECT {{ var('value') }} AS x FROM t\n"),
        ("branch_false", "{% if var('flag') %}select 1{% else %}SELECT 1{% endif %}\n"),
        ("loop", "{% for n in [1,2,3] %}SELECT {{ n }} AS x;\n{% endfor %}"),
        ("capture", "{% set query %}select 1{% endset %}{{ query }}\n"),
        ("comment", "{# hidden #}select 1 -- noqa: CP01\n"),
        ("unicode_crlf", "SELECT 'é😀' AS {{ var('column') }}\nFROM t\n"),
        (
            "continued",
            "{% for n in [1, 2] %}{% if n > 0 %}SELECT {{ n }};{% continue %}{% endif %}{% endfor %}SELECT 9\n",
        ),
        (
            "broken",
            "{% for n in [1, 2] %}{% if n > 0 %}SELECT {{ n }};{% break %}{% endif %}{% else %}select 0{% endfor %}SELECT 9\n",
        ),
        ("returned", "select 0 {{ return('select 1') }}\n"),
        (
            "block_returned",
            "SELECT {% block columns %}0{{ return('1') }}{% endblock %} AS n\n",
        ),
        (
            "recursive",
            "{% for item in [{'n': 1, 'children': [{'n': 2, 'children': []}]}] recursive %}"
            "SELECT {{ item.n }};{{ loop(item.children) }}{% endfor %}\n",
        ),
        (
            "recursive_transformed",
            "{% for item in [{'n': 1, 'children': [{'n': 2, 'children': []}]}] recursive %}"
            "SELECT {{ item.n }};{{ loop(item.children) | upper }}{% endfor %}\n",
        ),
        (
            "recursive_else",
            "{% for item in [{'n': 1, 'children': []}] recursive %}"
            "SELECT {{ item.n }};{{ loop(item.children) }}{% else %}select 0{% endfor %}\n",
        ),
    ],
)
def test_fix_original_source(case, expected, traces, monkeypatch):
    """Fix literal source while preserving generated SQL, skipped branches and noqa."""
    trace = traces[case]
    monkeypatch.setattr(Dbt2Templater, "_runtime", lambda *_: trace)
    source = normalize_newlines(trace["source"])
    result = Linter(config=make_config()).lint_string(
        source, fname="model.sql", fix=True
    )
    assert not result.get_violations(types=SQLTemplaterError)
    assert result.fix_string()[0] == expected


def test_project_trace(traces, monkeypatch):
    """Use real config(), return(), ref() and repeated macro calls without Python dbt."""
    trace = traces["project"]
    monkeypatch.setattr(Dbt2Templater, "_runtime", lambda *_: trace)
    source = trace["source"]
    result = Linter(config=make_config()).lint_string(
        source, fname="model.sql", fix=True
    )
    assert result.templated_file.templated_str == trace["rendered"]
    assert "99 as base_value" not in trace["rendered"]
    expected = (
        source.replace("select ", "SELECT ")
        .replace(" as ", " AS ")
        .replace(" from ", " FROM ")
        .replace("union all", "UNION ALL")
    )
    assert result.fix_string()[0] == expected
    assert result.check_tuples()[0] == ("CP01", 3, 1)


def test_invalid_elif_layout_does_not_crash_linting(monkeypatch):
    """Surface invalid upstream provenance before lexer work is dispatched."""
    trace = json.loads(
        (Path(__file__).parent / "fixtures/elif_duplicate.json").read_text(
            encoding="utf-8"
        )
    )
    monkeypatch.setattr(Dbt2Templater, "_runtime", lambda *_: trace)
    result = Linter(config=make_config()).lint_string(
        trace["source"], fname="model.sql", fix=True
    )
    errors = result.get_violations(types=SQLTemplaterError)
    assert len(errors) == 1
    assert "unmatched block_end" in str(errors[0])


def test_trimmed_raw_block_preserves_whitespace(traces, monkeypatch):
    """A dropped Jinja2 lexical gap must not shift source fixes after raw output."""
    source = "{% raw -%} select 1 {%- endraw %}\n"
    start = source.index("select 1")
    trace = {
        **traces["literal"],
        "source": source,
        "events": [
            {
                "kind": "literal",
                "source_start": start,
                "source_end": start + len("select 1"),
                "rendered_start": 0,
                "rendered_end": len("select 1"),
            }
        ],
    }
    monkeypatch.setattr(Dbt2Templater, "_runtime", lambda *_: trace)
    result = Linter(config=make_config()).lint_string(
        source, fname="model.sql", fix=True
    )
    assert not result.get_violations(types=SQLTemplaterError)
    assert "".join(item.raw for item in result.templated_file.raw_sliced) == source
    assert result.fix_string()[0] == "{% raw -%} SELECT 1 {%- endraw %}\n"


def test_fix_after_skipped_expression_uses_exact_literal(traces, monkeypatch):
    """A skipped loop expression must not make an executed else fix unfixable."""
    source = "{% for x in [] %}select {{ x }};{% else %}select 0{% endfor %}\n"
    middle = source.index("{% else %}")
    literal = source.index("select 0")
    end = source.index("{% endfor %}")
    trace = {
        **traces["literal"],
        "source": source,
        "rendered": "select 0",
        "events": [
            {
                "kind": kind,
                "source_start": start,
                "source_end": stop,
                "rendered_start": rendered_start,
                "rendered_end": rendered_end,
            }
            for kind, start, stop, rendered_start, rendered_end in [
                ("block_start", 0, source.index("%}") + 2, 0, 0),
                ("block_mid", middle, literal, 0, 0),
                ("literal", literal, end, 0, 8),
                ("block_end", end, len(source) - 1, 8, 8),
            ]
        ],
    }
    monkeypatch.setattr(Dbt2Templater, "_runtime", lambda *_: trace)
    result = Linter(config=make_config()).lint_string(
        source, fname="model.sql", fix=True
    )
    assert not result.get_violations(types=SQLTemplaterError)
    assert result.fix_string()[0] == source.replace("select 0", "SELECT 0")
