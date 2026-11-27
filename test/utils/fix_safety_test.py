"""Tests for the fix safety check, `utils/fix_safety.py`."""

import pytest
import yaml

from utils import fix_safety


def test_drop_keys_drops_only_what_the_predicate_says():
    """Positions go, everything else stays, at any depth."""
    tree = {"location": 3, "name": "a", "args": [{"location": 7, "location2": "x"}]}
    result = fix_safety._drop_keys(tree, lambda k, v: k == "location")
    assert result == {"name": "a", "args": [{"location2": "x"}]}


def test_fold_identifiers_keeps_constant_text():
    """Identifiers and aliases are folded; a constant's text isn't."""
    tree = {
        "class": "CONSTANT",
        "alias": "MyAlias",
        "literal": {"kind": "STRING", "text": "Keep Me"},
        "args": [{"class": "COLUMN_REF", "column_names": ["Col"]}],
    }
    assert fix_safety._fold_identifiers(tree) == {
        "class": "constant",
        "alias": "myalias",
        "literal": {"kind": "STRING", "text": "Keep Me"},
        "args": [{"class": "column_ref", "column_names": ["col"]}],
    }


@pytest.mark.parametrize(
    "first, second, same",
    [
        # DuckDB resolves identifiers case-insensitively, quoted or not.
        ("SELECT 42 AS col1", "SELECT 42 AS COL1", True),
        ('SELECT "A" FROM t', "SELECT a FROM t", True),
        ("SELECT {name: 'x'}", "SELECT {NAME: 'x'}", True),
        ("SELECT a,b FROM t", "SELECT\n    a,\n    b\nFROM t", True),
        # A string's text, a number and an operator matter.
        ("SELECT 'abc'", "SELECT 'ABC'", False),
        ("SELECT 'Abc' AS x", "SELECT 'abc' AS x", False),
        ("SELECT 1", "SELECT 2", False),
        ("SELECT a FROM t WHERE b > 1", "SELECT a FROM t WHERE b < 1", False),
    ],
)
def test_duckdb_oracle(first, second, same):
    """The DuckDB oracle tells meaning apart from layout and identifier case."""
    pytest.importorskip("duckdb")
    oracle = fix_safety.DuckDBOracle()
    assert (oracle.tree(first) == oracle.tree(second)) is same


def test_duckdb_oracle_cant_judge():
    """Statements DuckDB can't serialise aren't judged."""
    pytest.importorskip("duckdb")
    oracle = fix_safety.DuckDBOracle()
    assert oracle.tree("CREATE TABLE t (a INT)") is None
    assert oracle.tree("SELECT FROM WHERE") is None


@pytest.mark.parametrize(
    "first, second, same",
    [
        # Positions, including the IN-list ones added in PostgreSQL 18.
        ("SELECT 1 IN (1,2)", "SELECT 1 IN (1, 2)", True),
        ("SELECT ARRAY[1,2]", "SELECT ARRAY[1, 2]", True),
        ("SELECT A FROM T", "select a from t", True),
        # Quoting changes the case of an identifier in PostgreSQL.
        ('SELECT "A" FROM t', "SELECT a FROM t", False),
        # A `location` that's a string is part of the statement.
        (
            "CREATE TABLESPACE t LOCATION '/a'",
            "CREATE TABLESPACE t LOCATION '/b'",
            False,
        ),
    ],
)
def test_postgres_oracle(first, second, same):
    """The Postgres oracle ignores positions and keeps what PostgreSQL keeps."""
    pytest.importorskip("pglast")
    oracle = fix_safety.PostgresOracle()
    assert (oracle.tree(first) == oracle.tree(second)) is same


def test_postgres_oracle_cant_parse():
    """A statement PostgreSQL can't parse can't be judged."""
    pytest.importorskip("pglast")
    assert fix_safety.PostgresOracle().tree("SELECT FROM WHERE (") is None


def test_check_finds_and_names_the_rule(tmp_path, monkeypatch):
    """A rule whose fix changes the tree is found and named.

    ST07 is excluded from the default run because it replaces USING with ON on
    purpose, so asking for it on its own shows how a failure is reported.
    """
    pytest.importorskip("duckdb")
    monkeypatch.setattr(fix_safety, "KNOWN_FAILURES", tmp_path / "none.yml")
    report = tmp_path / "report.md"
    code = fix_safety.main(
        [
            "--dialect",
            "duckdb",
            "--filter",
            "anti_semi_join.sql",
            "--rules",
            "ST07",
            "--processes",
            "1",
            "--report",
            str(report),
        ]
    )
    assert code == 1
    text = report.read_text()
    assert "New failures: 2." in text
    assert "Rules: ST07." in text
    assert "ON cars.region_id = region.region_id" in text


def test_known_failures(tmp_path, monkeypatch):
    """Known failures don't fail the run, and stale ones do."""
    pytest.importorskip("duckdb")
    known = tmp_path / "known.yml"
    known.write_text(
        "- dialect: duckdb\n"
        "  fixture: duckdb/anti_semi_join.sql\n"
        '  starts_with: "SELECT cars.name, cars.manufacturer\\nFROM cars SEMI"\n'
        "- dialect: duckdb\n"
        "  fixture: duckdb/anti_semi_join.sql\n"
        '  starts_with: "SELECT cars.name, cars.manufacturer\\nFROM cars ANTI"\n'
    )
    monkeypatch.setattr(fix_safety, "KNOWN_FAILURES", known)
    args = ["--dialect", "duckdb", "--filter", "anti_semi_join.sql"]
    # With ST07 both statements fail, as listed.
    assert fix_safety.main([*args, "--rules", "ST07", "--processes", "1"]) == 0
    # By default neither fails, so both entries are stale.
    assert fix_safety.main([*args, "--processes", "1"]) == 1


def test_no_oracle_for_dialect(capsys):
    """A dialect without an oracle is an error, not a pass."""
    assert fix_safety.main(["--dialect", "tsql"]) == 2
    assert "No oracle" in capsys.readouterr().err


def test_known_failures_file():
    """Each known failure names exactly one statement of its fixture."""
    for entry in fix_safety._load_known_failures():
        fixture = fix_safety.FIXTURES / entry["fixture"]
        statements = fix_safety._statements(fixture.read_text(), entry["dialect"])
        assert statements is not None, entry
        matches = [s for s in statements if s.startswith(entry["starts_with"])]
        assert len(matches) == 1, entry


def test_unjudged_known_failure_isnt_stale(tmp_path, monkeypatch):
    """A listed statement the oracle can't judge isn't reported as passing."""
    pytest.importorskip("duckdb")
    known = tmp_path / "known.yml"
    # DuckDB's json_serialize_sql only handles SELECTs.
    known.write_text(
        "- dialect: duckdb\n"
        "  fixture: duckdb/create_type.sql\n"
        "  starts_with: CREATE TYPE mood\n"
    )
    monkeypatch.setattr(fix_safety, "KNOWN_FAILURES", known)
    args = ["--dialect", "duckdb", "--filter", "create_type.sql", "--processes", "1"]
    assert fix_safety.main(args) == 0


def test_each_rule_is_tried_alone(monkeypatch):
    """A rule that can't fix the statement alone doesn't hide later rules."""
    pytest.importorskip("duckdb")
    statement = "SELECT 'a'"

    def fake_fix(sql, dialect, rules, config_path):
        if rules == ["AA01"]:
            raise ValueError("can't fix this alone")
        return "SELECT 'b'\n"

    monkeypatch.setattr(fix_safety, "_fix", fake_fix)
    _, reason, rules = fix_safety._check_statement(
        statement,
        "duckdb",
        fix_safety.DuckDBOracle(),
        "duckdb",
        ["AA01", "BB02"],
        None,
    )
    assert reason == "The fix changes the syntax tree"
    assert rules == ["BB02"]


def test_several_dialects(tmp_path, monkeypatch):
    """Each dialect gets its own section of one report."""
    pytest.importorskip("duckdb")
    pytest.importorskip("pglast")
    monkeypatch.setattr(fix_safety, "KNOWN_FAILURES", tmp_path / "none.yml")
    report = tmp_path / "report.md"
    args = ["--dialect", "duckdb", "--dialect", "postgres", "--filter", "select.sql"]
    assert fix_safety.main([*args, "--processes", "1", "--report", str(report)]) == 0
    text = report.read_text()
    assert "## duckdb, judged by the duckdb parser" in text
    assert "## postgres, judged by the postgres parser" in text


def test_default_run_names_the_rule(tmp_path, monkeypatch):
    """Without `--rules`, the rules with a fix are tried one at a time.

    RF06 removes the quotes from "time" in a RETURNS TABLE column, which
    PostgreSQL can't parse: the known failure, unlisted here.
    """
    pytest.importorskip("pglast")
    monkeypatch.setattr(fix_safety, "KNOWN_FAILURES", tmp_path / "none.yml")
    report = tmp_path / "report.md"
    args = ["--dialect", "postgres", "--filter", "create_function.sql"]
    assert fix_safety.main([*args, "--processes", "1", "--report", str(report)]) == 1
    text = report.read_text()
    assert "New failures: 1." in text
    assert "The postgres parser can't parse the fixed statement. Rules: RF06." in text


def test_duckdb_oracle_non_ascii_case():
    """DuckDB tells `ä` and `Ä` apart, so the oracle must too.

    The fixed query returns 2 instead of 1.
    """
    pytest.importorskip("duckdb")
    oracle = fix_safety.DuckDBOracle()
    before = 'SELECT ä FROM (SELECT 1 AS "ä", 2 AS "Ä") t'
    after = 'SELECT Ä FROM (SELECT 1 AS "ä", 2 AS "Ä") T'
    assert oracle.tree(before) != oracle.tree(after)


def test_timeout_isnt_swallowed_while_naming_rules(monkeypatch):
    """A timeout while naming the rules stops the statement, not just one rule."""
    pytest.importorskip("duckdb")
    calls = []

    def fake_fix(sql, dialect, rules, config_path):
        calls.append(rules)
        if rules == ["AA01"]:
            raise fix_safety._Timeout()
        return "SELECT 'b'\n"

    monkeypatch.setattr(fix_safety, "_fix", fake_fix)
    with pytest.raises(fix_safety._Timeout):
        fix_safety._check_statement(
            "SELECT 'a'",
            "duckdb",
            fix_safety.DuckDBOracle(),
            "duckdb",
            ["AA01", "BB02"],
            None,
        )
    assert ["BB02"] not in calls


def test_incomplete_run_exit_code(tmp_path, monkeypatch):
    """A run where statements couldn't be fixed isn't reported as a pass."""
    pytest.importorskip("duckdb")

    def failing_fix(sql, dialect, rules, config_path):
        raise ValueError("can't fix")

    monkeypatch.setattr(fix_safety, "_fix", failing_fix)
    monkeypatch.setattr(fix_safety, "KNOWN_FAILURES", tmp_path / "none.yml")
    report = tmp_path / "report.md"
    args = ["--dialect", "duckdb", "--filter", "anti_semi_join.sql"]
    assert fix_safety.main([*args, "--processes", "1", "--report", str(report)]) == 3
    assert "The run is incomplete" in report.read_text()


def _historical_corruptions():
    path = fix_safety.ROOT / "test/fixtures/fix_safety/historical_corruptions.yml"
    return yaml.safe_load(path.read_text())


@pytest.mark.parametrize(
    "case", _historical_corruptions(), ids=lambda case: f"issue{case['issue']}"
)
@pytest.mark.parametrize("oracle_name", ["postgres", "duckdb"])
def test_historical_corruptions(case, oracle_name):
    """Each oracle's verdict on the corrupted fixes of past issues.

    This records what the check can and can't see, misses included, so a change
    to an oracle that changes a verdict shows up here.
    """
    pytest.importorskip({"postgres": "pglast", "duckdb": "duckdb"}[oracle_name])
    oracle = fix_safety.ORACLES[oracle_name]()
    before = oracle.tree(case["input"])
    if before is None:
        verdict = "not_judged"
    else:
        after = oracle.tree(case["bad_output"])
        verdict = "detected" if after is None or after != before else "missed"
    assert verdict == case[oracle_name]


def test_timed_out_run_exit_code(tmp_path, monkeypatch):
    """A statement that times out makes the run incomplete."""
    pytest.importorskip("duckdb")

    def slow_fix(sql, dialect, rules, config_path):
        raise fix_safety._Timeout()

    monkeypatch.setattr(fix_safety, "_fix", slow_fix)
    monkeypatch.setattr(fix_safety, "KNOWN_FAILURES", tmp_path / "none.yml")
    report = tmp_path / "report.md"
    args = ["--dialect", "duckdb", "--filter", "anti_semi_join.sql"]
    assert fix_safety.main([*args, "--processes", "1", "--report", str(report)]) == 3
    text = report.read_text()
    assert "were judged. The fix changed 0 of those. 4 timed out" in text
    assert "The run is incomplete" in text


@pytest.mark.parametrize(
    "selection",
    [["--filter", "no_such_fixture*.sql"], ["--fixtures", "no_such_dialect"]],
)
def test_no_fixtures_selected(selection, capsys):
    """Selecting no fixture files is an error, not a pass."""
    pytest.importorskip("duckdb")
    args = ["--dialect", "duckdb", *selection, "--processes", "1"]
    assert fix_safety.main(args) == 2
    assert "No fixture files to check" in capsys.readouterr().err


def test_processes_must_be_positive():
    """`--processes 0` is a usage error."""
    with pytest.raises(SystemExit):
        fix_safety.main(["--dialect", "duckdb", "--processes", "0"])
