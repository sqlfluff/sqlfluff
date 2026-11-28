"""Tests for the fix safety check, `utils/fix_safety.py`."""

import signal
import sys
import time

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
    trees = oracle.tree(first), oracle.tree(second)
    assert None not in trees
    assert (trees[0] == trees[1]) is same


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
    trees = oracle.tree(first), oracle.tree(second)
    assert None not in trees
    assert (trees[0] == trees[1]) is same


def test_postgres_oracle_cant_parse():
    """A statement PostgreSQL can't parse can't be judged."""
    pytest.importorskip("pglast")
    assert fix_safety.PostgresOracle().tree("SELECT FROM WHERE (") is None


@pytest.fixture
def no_known_failures(tmp_path, monkeypatch):
    """An empty list of known failures."""
    known = tmp_path / "known.yml"
    known.write_text("[]\n", encoding="utf-8")
    monkeypatch.setattr(fix_safety, "KNOWN_FAILURES", known)
    return known


def _run(capsys, *args):
    """Run the check in this process; return the exit code, stdout and stderr."""
    if "--processes" not in args:
        args = (*args, "--processes", "1")
    code = fix_safety.main(list(args))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


ANTI_SEMI_JOIN = ("--dialect", "duckdb", "--filter", "anti_semi_join.sql")
# A fixture where no fix is flagged.
ASOF_JOIN = ("--dialect", "duckdb", "--filter", "asof_join.sql")


def test_check_finds_and_names_the_rule(capsys, no_known_failures):
    """A rule whose fix changes the tree is found and named.

    ST07 replaces USING with ON, which changes the tree, so asking for it on its
    own shows how a flagged fix is reported.
    """
    pytest.importorskip("duckdb")
    code, out, _ = _run(capsys, *ANTI_SEMI_JOIN, "--rules", "ST07")
    assert code == 1
    assert "Flagged fixes that aren't listed: 2." in out
    assert "#### `duckdb/anti_semi_join.sql`, statement 3" in out
    assert "Rules: ST07." in out
    assert "ON cars.region_id = region.region_id" in out


def _listed(statement_start):
    return (
        "- dialect: duckdb\n"
        "  fixture: duckdb/anti_semi_join.sql\n"
        f'  starts_with: "SELECT cars.name, cars.manufacturer\\nFROM {statement_start}"\n'
        "  reason: A reason.\n"
    )


def test_known_failures(capsys, tmp_path, monkeypatch):
    """In a default run, listed fixes don't fail the check, and stale ones do.

    ST07 replaces USING with ON in the last two statements of the fixture.
    """
    pytest.importorskip("duckdb")
    known = tmp_path / "known.yml"
    monkeypatch.setattr(fix_safety, "KNOWN_FAILURES", known)
    # Both flagged fixes listed: a pass, which shows the reason.
    known.write_text(
        _listed("cars SEMI JOIN region\\nUSING") + _listed("cars ANTI JOIN region"),
        encoding="utf-8",
    )
    code, out, _ = _run(capsys, *ANTI_SEMI_JOIN)
    assert code == 0
    assert "Flagged fixes that aren't listed: 0. Listed: 2." in out
    assert "- `duckdb/anti_semi_join.sql`, statement 3 (ST07): A reason." in out
    # One not listed: it fails.
    known.write_text(_listed("cars ANTI JOIN region"), encoding="utf-8")
    code, out, _ = _run(capsys, *ANTI_SEMI_JOIN)
    assert code == 1
    assert "Flagged fixes that aren't listed: 1. Listed: 1." in out
    # A listed statement that passes is stale, and fails.
    known.write_text(
        _listed("cars SEMI JOIN region\\nUSING")
        + _listed("cars ANTI JOIN region")
        + _listed("cars SEMI JOIN region\\nON"),
        encoding="utf-8",
    )
    code, out, _ = _run(capsys, *ANTI_SEMI_JOIN)
    assert code == 1
    assert "Listed statements that pass: 1." in out
    # With `--rules`, the list isn't used.
    code, out, _ = _run(capsys, *ANTI_SEMI_JOIN, "--rules", "ST07")
    assert code == 1
    assert "Flagged fixes that aren't listed: 2. Listed: 0." in out
    assert "The known failures aren't used" in out


@pytest.mark.parametrize(
    "content",
    [
        "- dialect: duckdb\n  fixture: duckdb/x.sql\n  starts_with: SELECT\n",
        "dialect: duckdb\n",
    ],
)
def test_bad_known_failures_file(capsys, tmp_path, monkeypatch, content):
    """A malformed list of known failures is an error, not a pass or a flag."""
    pytest.importorskip("duckdb")
    known = tmp_path / "known.yml"
    known.write_text(content, encoding="utf-8")
    monkeypatch.setattr(fix_safety, "KNOWN_FAILURES", known)
    code, _, err = _run(capsys, *ANTI_SEMI_JOIN)
    assert code == 2
    assert "needs a dialect, a fixture, a starts_with and a reason" in err


def test_no_oracle_for_dialect(capsys):
    """A dialect without an oracle is an error, not a pass."""
    code, _, err = _run(capsys, "--dialect", "tsql")
    assert code == 2
    assert "No oracle" in err


def test_unjudged_known_failure_isnt_stale(capsys, tmp_path, monkeypatch):
    """A listed statement the oracle can't judge isn't reported as passing."""
    pytest.importorskip("duckdb")
    known = tmp_path / "known.yml"
    # DuckDB's json_serialize_sql only handles SELECTs.
    known.write_text(
        "- dialect: duckdb\n"
        "  fixture: duckdb/create_type.sql\n"
        "  starts_with: CREATE TYPE mood\n"
        "  reason: A reason.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(fix_safety, "KNOWN_FAILURES", known)
    code, out, _ = _run(capsys, "--dialect", "duckdb", "--filter", "create_type.sql")
    # Nothing in the file is judged, so the run is incomplete.
    assert code == 2
    assert "Listed statements that pass: 0." in out


def test_several_dialects(capsys):
    """Each dialect gets its own section of one report.

    `duckdb/select.sql` has a listed fix, so this also checks the real list.
    """
    pytest.importorskip("duckdb")
    pytest.importorskip("pglast")
    code, out, _ = _run(
        capsys, "--dialect", "duckdb", "--dialect", "postgres", "--filter", "select.sql"
    )
    assert code == 0
    assert "## duckdb, judged by the duckdb parser" in out
    assert "## postgres, judged by the postgres parser" in out


def test_default_run_names_the_rule(capsys, no_known_failures):
    """Without `--rules`, the rules with a fix are tried one at a time.

    RF06 removes the quotes from "time" in a RETURNS TABLE column, which
    PostgreSQL can't parse: the known failure, unlisted here.
    """
    pytest.importorskip("pglast")
    code, out, _ = _run(
        capsys, "--dialect", "postgres", "--filter", "create_function.sql"
    )
    assert code == 1
    assert "Flagged fixes that aren't listed: 1." in out
    assert "The postgres parser can't parse the fixed statement. Rules: RF06." in out


def test_fixing_raises(capsys, monkeypatch, no_known_failures):
    """Statements that couldn't be fixed make the run incomplete."""
    pytest.importorskip("duckdb")

    def failing_fix(sql, dialect, rules, config_path):
        raise ValueError("can't fix")

    monkeypatch.setattr(fix_safety, "_fix", failing_fix)
    code, out, _ = _run(capsys, *ANTI_SEMI_JOIN)
    assert code == 2
    assert "Not all was judged: fixing 4 statements raised an error" in out


def test_timed_out(capsys, monkeypatch, no_known_failures):
    """Statements that time out make the run incomplete."""
    pytest.importorskip("duckdb")

    def slow_fix(sql, dialect, rules, config_path):
        raise fix_safety._Timeout()

    monkeypatch.setattr(fix_safety, "_fix", slow_fix)
    code, out, _ = _run(capsys, *ANTI_SEMI_JOIN)
    assert code == 2
    assert "Not all was judged: 4 statements timed out" in out


@pytest.mark.skipif(not hasattr(signal, "SIGALRM"), reason="needs SIGALRM")
def test_time_limit(monkeypatch):
    """The time limit stops a slow statement, and puts the old handler back."""
    pytest.importorskip("duckdb")
    monkeypatch.setattr(fix_safety, "STATEMENT_TIMEOUT", 1)

    def slow_fix(sql, dialect, rules, config_path):
        time.sleep(5)

    monkeypatch.setattr(fix_safety, "_fix", slow_fix)
    before = signal.getsignal(signal.SIGALRM)
    path = fix_safety.FIXTURES / "duckdb" / "anti_semi_join.sql"
    started = time.monotonic()
    _, stats, _ = fix_safety._check_fixture((str(path), "duckdb", "duckdb", None, None))
    assert stats.timeouts == 4
    assert time.monotonic() - started < 20
    assert signal.getsignal(signal.SIGALRM) == before


def test_no_fixtures_selected(capsys):
    """Selecting no fixture files is an error, not a pass."""
    pytest.importorskip("duckdb")
    code, _, err = _run(capsys, "--dialect", "duckdb", "--filter", "no_such*.sql")
    assert code == 2
    assert "No fixture files to check" in err


def test_unknown_cpu_count(capsys, monkeypatch, no_known_failures):
    """Without a CPU count, the check runs in one process."""
    pytest.importorskip("duckdb")
    monkeypatch.setattr(fix_safety.os, "cpu_count", lambda: None)
    assert fix_safety.main([*ANTI_SEMI_JOIN, "--rules", "ST07"]) == 1


def test_report_without_sigalrm(capsys, monkeypatch):
    """Where there's no SIGALRM, the report says there was no time limit."""
    pytest.importorskip("duckdb")
    monkeypatch.delattr(fix_safety.signal, "SIGALRM", raising=False)
    code, out, _ = _run(capsys, *ANTI_SEMI_JOIN)
    assert code == 0
    assert "There's no SIGALRM on this platform" in out


def test_unparsable_fixture(capsys, monkeypatch, no_known_failures):
    """A fixture file that doesn't parse isn't judged, so the run is incomplete."""
    pytest.importorskip("duckdb")
    monkeypatch.setattr(fix_safety, "_statements", lambda sql, dialect: None)
    code, out, _ = _run(capsys, *ANTI_SEMI_JOIN)
    assert code == 2
    assert "Not all was judged: 1 fixture files couldn't be parsed" in out


def test_fixture_that_raises(capsys, monkeypatch, no_known_failures):
    """A fixture file that raises while being split counts as unparsable."""
    pytest.importorskip("duckdb")

    def broken(sql, dialect):
        raise ValueError("can't lex")

    monkeypatch.setattr(fix_safety, "_statements", broken)
    code, out, _ = _run(capsys, *ANTI_SEMI_JOIN)
    assert code == 2
    assert "1 fixture files couldn't be parsed" in out


def test_flagged_and_incomplete(capsys, monkeypatch, no_known_failures):
    """When a fix is flagged and the run is also incomplete, the code is 1."""
    pytest.importorskip("duckdb")
    statements = fix_safety._statements
    monkeypatch.setattr(
        fix_safety,
        "_statements",
        lambda sql, dialect: None if "CHECKPOINT" in sql else statements(sql, dialect),
    )
    args = ["--dialect", "duckdb", "--filter", "[a-c]*.sql", "--rules", "ST07"]
    code, out, _ = _run(capsys, *args)
    assert code == 1
    assert "couldn't be parsed" in out


def test_nothing_judged(capsys, no_known_failures):
    """A run where the oracle can judge no statement isn't a pass.

    DuckDB's oracle only judges SELECTs, and `checkpoint.sql` has none.
    """
    pytest.importorskip("duckdb")
    code, out, _ = _run(capsys, "--dialect", "duckdb", "--filter", "checkpoint.sql")
    assert code == 2
    assert "the oracle could judge none of the statements" in out


def test_unexpected_error(capsys, monkeypatch, no_known_failures):
    """An unexpected error exits with 2, not 1, which means a fix was flagged."""
    pytest.importorskip("duckdb")

    def broken(*args):
        raise RuntimeError("a bug")

    monkeypatch.setattr(fix_safety, "_check_dialect", broken)
    code, _, err = _run(capsys, *ANTI_SEMI_JOIN)
    assert code == 2
    assert "RuntimeError: a bug" in err


@pytest.mark.parametrize(
    "options",
    [
        ["--processes", "0"],
        ["--rules", "CV11,XX99"],
        ["--rules", " , "],
        ["--config", "no_such_file.sqlfluff"],
        ["--config", "BAD"],
        ["--config", "TYPO_RULES"],
        ["--config", "TYPO_EXCLUDE"],
    ],
)
def test_usage_errors(tmp_path, options):
    """Options that can't be right are usage errors, before anything is checked.

    An unknown rule would otherwise pass, as sqlfluff only warns about it.
    """
    files = {
        "BAD": "[sqlfluff\nrules =\n",
        "TYPO_RULES": "[sqlfluff]\nrules = CV11,XX99\n",
        "TYPO_EXCLUDE": "[sqlfluff]\nexclude_rules = XX99\n",
    }
    for name, content in files.items():
        (tmp_path / f"{name}.sqlfluff").write_text(content, encoding="utf-8")
    options = [
        str(tmp_path / f"{option}.sqlfluff") if option in files else option
        for option in options
    ]
    with pytest.raises(SystemExit) as excinfo:
        fix_safety.main(["--dialect", "duckdb", *options])
    assert excinfo.value.code == 2


@pytest.mark.parametrize("rules", ["LT01, ST07", "st07"])
def test_rules_spaces_and_case(capsys, no_known_failures, rules):
    """`--rules` takes spaces around the rules, and any case, as sqlfluff does."""
    pytest.importorskip("duckdb")
    code, out, _ = _run(capsys, *ANTI_SEMI_JOIN, "--rules", rules)
    assert code == 1
    assert "Rules: ST07." in out.replace("st07", "ST07")


def test_parallel_run_matches_sequential_run(capsys, no_known_failures):
    """Worker processes give the same report and exit code as one process."""
    pytest.importorskip("duckdb")
    args = ["--dialect", "duckdb", "--filter", "[a-c]*.sql", "--rules", "ST07"]
    first = _run(capsys, *args, "--processes", "1")
    second = _run(capsys, *args, "--processes", "2")
    assert first[0] == second[0] == 1
    assert first[1] == second[1]


def _cast_style(path, extra=""):
    path.write_text(
        f"[sqlfluff]\n{extra}"
        "[sqlfluff:rules:convention.casting_style]\n"
        "preferred_type_casting_style = cast\n",
        encoding="utf-8",
    )
    return str(path)


SELECT_SQL = ("--dialect", "postgres", "--filter", "select.sql")


def test_config_file_changes_the_verdict(capsys, tmp_path, no_known_failures):
    """The rule settings of `--config` are used to fix, and to name the rule.

    CV11 is fine with its default style, but with the `cast` style it turns
    `'...'::TIMESTAMP AT TIME ZONE 'UTC'` into SQL PostgreSQL can't parse.
    """
    pytest.importorskip("pglast")
    config = _cast_style(tmp_path / "cast.sqlfluff")
    assert _run(capsys, *SELECT_SQL, "--rules", "CV11")[0] == 0
    code, out, _ = _run(capsys, *SELECT_SQL, "--rules", "CV11", "--config", config)
    assert code == 1
    assert "can't parse the fixed statement. Rules: CV11." in out


def test_config_file_selects_rules(capsys, tmp_path, no_known_failures):
    """A `--config` file's `rules` and `exclude_rules` select the rules.

    Unless `--rules` is given, which selects exactly its rules.
    """
    pytest.importorskip("pglast")
    only_cv11 = _cast_style(tmp_path / "only.sqlfluff", "rules = CV11\n")
    code, out, _ = _run(capsys, *SELECT_SQL, "--config", only_cv11)
    assert code == 1
    assert "Rules: CV11." in out
    assert "Rules: CV11, " not in out and ", CV11." not in out

    no_cv11 = _cast_style(
        tmp_path / "no.sqlfluff", "rules = CV11,ST06\nexclude_rules = CV11\n"
    )
    selection = fix_safety._selection(None, no_cv11)
    assert selection["rules"] == "CV11,ST06"
    assert selection["exclude_rules"] == "CV11"
    assert _run(capsys, *SELECT_SQL, "--config", no_cv11)[0] == 0
    # `--rules` gives exactly the rules to fix with.
    assert _run(capsys, *SELECT_SQL, "--config", no_cv11, "--rules", "CV11")[0] == 1


def test_only_the_config_file_is_read(capsys, tmp_path, no_known_failures):
    """A `.sqlfluff` next to the `--config` file isn't read."""
    pytest.importorskip("pglast")
    _cast_style(tmp_path / ".sqlfluff")
    empty = tmp_path / "empty.sqlfluff"
    empty.write_text("[sqlfluff]\n", encoding="utf-8")
    args = (*SELECT_SQL, "--rules", "CV11", "--config", str(empty))
    assert _run(capsys, *args)[0] == 0


def test_config_with_tilde(capsys, tmp_path, monkeypatch, no_known_failures):
    """`--config "~/..."` is expanded, as the shell would."""
    pytest.importorskip("duckdb")
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / "my.sqlfluff").write_text("[sqlfluff]\n", encoding="utf-8")
    code, out, _ = _run(capsys, *ASOF_JOIN, "--config", "~/my.sqlfluff")
    assert code == 0
    assert "The known failures aren't used" in out


def test_known_failures_file():
    """Each known failure names exactly one statement of its fixture."""
    for entry in fix_safety._load_known_failures():
        fixture = fix_safety.FIXTURES / entry["fixture"]
        statements = fix_safety._statements(
            fixture.read_text(encoding="utf-8"), entry["dialect"]
        )
        assert statements is not None, entry
        matches = [s for s in statements if s.startswith(entry["starts_with"])]
        assert len(matches) == 1, entry


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


def test_duckdb_oracle_non_ascii_case():
    """DuckDB tells `ä` and `Ä` apart, so the oracle must too.

    The fixed query returns 2 instead of 1.
    """
    pytest.importorskip("duckdb")
    oracle = fix_safety.DuckDBOracle()
    before = 'SELECT ä FROM (SELECT 1 AS "ä", 2 AS "Ä") t'
    after = 'SELECT Ä FROM (SELECT 1 AS "ä", 2 AS "Ä") T'
    trees = oracle.tree(before), oracle.tree(after)
    assert None not in trees
    assert trees[0] != trees[1]


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


def _historical_corruptions():
    path = fix_safety.ROOT / "test/fixtures/fix_safety/historical_corruptions.yml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


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


@pytest.mark.parametrize(
    "oracle_name, package", [("duckdb", "duckdb"), ("postgres", "pglast")]
)
def test_oracle_not_installed(capsys, monkeypatch, oracle_name, package):
    """Without its package, an oracle isn't available, and the run is an error."""
    monkeypatch.setitem(sys.modules, package, None)
    assert not fix_safety.ORACLES[oracle_name].available()
    code, _, err = _run(capsys, "--dialect", oracle_name)
    assert code == 2
    assert f"The {oracle_name} oracle isn't installed" in err


def test_statements_of_sql_that_doesnt_parse():
    """SQL that doesn't parse has no statements to check."""
    assert fix_safety._statements("SELECT (", "ansi") is None
    assert fix_safety._statements("SELECT 1; SELECT 2", "ansi") == [
        "SELECT 1",
        "SELECT 2",
    ]
