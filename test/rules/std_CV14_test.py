"""Tests the python routines within CV14."""

import sqlfluff
from sqlfluff.core import FluffConfig, Linter

SQL = """\
SELECT
    SUM(x) OVER (PARTITION BY a ORDER BY b) AS implicit_frame,
    SUM(x) OVER (PARTITION BY a ORDER BY b ROWS UNBOUNDED PRECEDING) AS explicit,
    ROW_NUMBER() OVER (ORDER BY b) AS rn,
    SUM(x) OVER w AS named,
    SUM(x) OVER (w ORDER BY c) AS extended,
    LAST_VALUE(x) OVER w2 AS last_x
FROM t
WINDOW w AS (PARTITION BY a ORDER BY b), w2 AS (ORDER BY z);
"""


def _lint(sql: str, force_enable: bool) -> list[dict]:
    config = FluffConfig(
        overrides={"dialect": "ansi", "rules": "CV14"},
        configs={"rules": {"convention.window_frame": {"force_enable": force_enable}}},
    )
    linted = Linter(config=config).lint_string(sql)
    return [violation.to_dict() for violation in linted.get_violations()]


def test__rules__std_CV14_reports_each_implicit_frame() -> None:
    """Every window with an ORDER BY and no frame is reported once."""
    violations = _lint(SQL, force_enable=True)
    assert [(v["start_line_no"], v["start_line_pos"]) for v in violations] == [
        (2, 18),
        (6, 18),
        (9, 14),
        (9, 49),
    ]
    assert {v["code"] for v in violations} == {"CV14"}
    assert violations[0]["description"] == (
        "Window definition has an ORDER BY but no explicit frame clause "
        "(ROWS, RANGE or GROUPS)."
    )


def test__rules__std_CV14_disabled_by_default() -> None:
    """The rule is opt in, even when it is selected explicitly."""
    assert _lint(SQL, force_enable=False) == []
    results = sqlfluff.lint(SQL, dialect="ansi", rules=["CV14"])
    assert results == []


def test__rules__std_CV14_not_in_default_rule_set() -> None:
    """Enabling all rules still doesn't make the opt in rule fire."""
    results = sqlfluff.lint(SQL, dialect="ansi")
    assert "CV14" not in {result["code"] for result in results}


def test__rules__std_CV14_noqa() -> None:
    """The rule can be silenced inline like any other."""
    sql = "SELECT SUM(x) OVER (ORDER BY b) AS s FROM t  -- noqa: CV14\n"
    assert _lint(sql, force_enable=True) == []
