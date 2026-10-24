"""Run SQLFluff's real lexer, linter and fixer on upstream render provenance."""

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
        ("expression", "SELECT {{ var('value') }} AS x FROM t\n"),
        ("branch_false", "{% if var('flag') %}select 1{% else %}SELECT 1{% endif %}\n"),
        ("loop", "{% for n in [1,2,3] %}SELECT {{ n }} AS x;\n{% endfor %}"),
        ("capture", "{% set query %}select 1{% endset %}{{ query }}\n"),
        ("comment", "{# hidden #}select 1 -- noqa: CP01\n"),
        ("unicode_crlf", "SELECT 'é😀' AS {{ var('column') }}\nFROM t\n"),
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
