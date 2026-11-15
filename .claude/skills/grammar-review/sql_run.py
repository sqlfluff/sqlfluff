#!/usr/bin/env python3
"""Run each statement of a fixture against a real database, from a fresh schema each time.

Usage: sql_run.py ENGINE FIXTURE.sql [SETUP.sql ...]
       sql_run.py selftest
  ENGINE: db2 | postgres | sqlite | duckdb. Container: $CONTAINER, default
    sqlfluff-review-<engine>. db2 database: $DB2_DBNAME, default review.
  SETUP*.sql: the schema the fixture needs. Pass several setups as variants for
    statements that need conflicting states (ADD COLUMN b vs ALTER COLUMN b).
    A statement PASSes if it succeeds under any variant. No setup = empty schema.
Server engines (db2, postgres) batch every statement of a variant into one client
call: BEGIN; setup; marker; statement; marker; ROLLBACK. Markers map output to
statements, so the marker must print in the same stream as errors. Ephemeral engines
(sqlite, duckdb) start a fresh in-memory database per statement instead, because
their errors and markers would race across stdout and stderr.
Output (TSV): n  verdict  first-error-per-variant  statement
  verdict: PASS | SYNTAX (invalid SQL) | SEMANTIC (parsed, failed to execute)
           | UNKNOWN (couldn't judge: no marker, setup failed mid-batch e.g. after a fixture
             COMMIT, client failed without a recognisable error, or sqlite -safe blocked it)
sqlite runs on the host with -safe, so fixture dot-commands (.shell, .system) and
ATTACH/writefile can't touch the machine; statements it blocks come back UNKNOWN.
"""

import os
import re
import sqlite3
import subprocess
import sys
import tempfile

DB2_DB = os.environ.get("DB2_DBNAME", "review")
ENGINES = {
    # A server engine needs: a client that reads stdin, transactional DDL, and a marker
    # command whose output lands in the same stream as its errors. An ephemeral engine
    # (no "mark") needs only a client that starts empty and writes errors to stderr.
    "db2": dict(
        cmd=lambda c: [
            "docker",
            "exec",
            "-i",
            c,
            "su",
            "-",
            "db2inst1",
            "-c",
            f"f=$(mktemp); cat >$f; db2 connect to {DB2_DB} >/dev/null;"
            " db2 +c -tf $f; rm -f $f",
        ],
        begin="",
        mark="ECHO {};",
        error=r"^SQL\d+[NC]",
        syntax=r"^SQL(0104|0007)N",
    ),
    "postgres": dict(
        # -o /dev/null: query results can't look like errors; \warn and ERRORs use stderr.
        cmd=lambda c: [
            "docker",
            "exec",
            "-i",
            c,
            "psql",
            "-X",
            "-q",
            "-o",
            "/dev/null",
            "-U",
            "postgres",
        ],
        begin="BEGIN;",
        mark="\\warn {}",
        error=r"ERROR:",
        syntax=r"syntax error|unterminated",  # unterminated quote/$$/identifier
    ),
    "sqlite": dict(  # host binary; -safe blocks .shell/.system, ATTACH and writefile()
        cmd=lambda c: ["sqlite3", "-safe", ":memory:"],
        error=r"[Ee]rror|in safe mode",
        syntax=r"syntax error|incomplete input|unrecognized token",  # last = unterminated quote
    ),
    "duckdb": dict(
        cmd=lambda c: ["docker", "run", "--rm", "-i", "duckdb/duckdb:latest"],
        error=r"Error:",
        syntax=r"Parser Error",
    ),
}


def split(sql: str) -> list[str]:
    """Split on ';' outside quotes and comments (sqlite's tokenizer via the stdlib)."""
    stmts, buf = [], ""
    for piece in re.split(r"(;)", sql):
        buf += piece
        # Odd number of $tag$ delimiters = still inside a dollar-quoted body.
        if (
            piece == ";"
            and sqlite3.complete_statement(buf)
            and len(re.findall(r"\$\w*\$", re.sub(r"'(?:[^']|'')*'", "", buf))) % 2 == 0
        ):
            stmts.append(buf.strip()[:-1].strip())
            buf = ""
    stmts.append(buf.strip())
    # ponytail: PL blocks (BEGIN ... END; with inner ';') still split wrongly, except sqlite triggers.
    return [
        s for s in stmts if re.sub(r"--[^\n]*|/\*.*?\*/", "", s, flags=re.S).strip()
    ]


def run(engine: str, setup: str, stmts: list[str], cwd: str) -> dict[int, str]:
    """Return {statement index: first error line} for one setup variant."""
    e = ENGINES[engine]
    cmd = e["cmd"](os.environ.get("CONTAINER", f"sqlfluff-review-{engine}"))
    if "mark" not in e:  # ephemeral: one fresh process per statement, errors on stderr
        errs = {}
        for i, s in enumerate(stmts):
            r = subprocess.run(
                cmd,
                input=f"{setup}\n{s}\n;\n",
                cwd=cwd,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            lines = r.stderr.splitlines()
            hit = next((ln for ln in lines if re.search(e["error"], ln)), None)
            if hit and "in safe mode" in hit:
                errs[i] = f"?? blocked by sqlite -safe: {hit.strip()}"
            elif hit:
                errs[i] = hit.strip()
            elif r.returncode:  # e.g. docker itself failed: never report that as PASS
                why = next((ln for ln in lines if "rror" in ln), (lines or [""])[-1])
                errs[i] = f"?? client exited {r.returncode}: {why.strip()}"
        return errs
    script = []
    for i, s in enumerate(stmts):
        script += [
            e["begin"],
            setup,
            e["mark"].format(f"@@S {i}"),
            s + "\n;",  # own line: a trailing -- comment must not eat it
            e["mark"].format("@@E"),
            "ROLLBACK;",
        ]
    out = subprocess.run(
        cmd,
        input="\n".join(script),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout
    return parse_batch(out, len(stmts), e["error"])


def parse_batch(out: str, n: int, error: str) -> dict[int, str]:
    """Map batched client output to {statement index: first error line}.

    A statement counts only once its @@E end marker appears; without it (client
    crashed or stopped mid-statement) it's UNKNOWN, never a silent PASS. Exit
    codes can't stand in for this: db2's CLP exits non-zero whenever any
    statement fails, and psql exits 0 despite script errors.
    """
    errs, cur, setup_err, ended = {}, None, None, set()
    for line in out.splitlines():
        if m := re.match(r"@@S (\d+)", line):
            cur = int(m[1])
            if setup_err:  # the state is not what the setup describes, so don't judge
                errs[cur], setup_err = f"?? setup failed in batch: {setup_err}", None
        elif line.startswith("@@E"):
            if cur is not None:
                ended.add(cur)
            cur = None
        elif re.search(error, line):
            if cur is None:
                setup_err = setup_err or line.strip()
            elif cur not in errs:
                errs[cur] = line.strip()
    for i in range(n):
        if i not in ended and i not in errs:
            errs[i] = "?? no end marker in output (client stopped early?)"
    return errs


def main(engine: str, fixture: str, setups: list[str]) -> list[tuple]:
    """Run every fixture statement under each setup variant; return TSV rows."""
    # Re-terminate every setup statement on its own line, so a setup missing its final ";"
    # (or ending in a -- comment) can't merge into the first fixture statement.
    texts = ["".join(f"{s}\n;\n" for s in split(open(p).read())) for p in setups] or [
        ""
    ]
    stmts = split(open(fixture).read())
    with tempfile.TemporaryDirectory() as cwd:  # sqlite fixtures ATTACH files
        for path, text in zip(setups, texts):
            # A broken setup makes every result meaningless, so fail loudly.
            if err := run(engine, "", [text.strip().rstrip(";")], cwd).get(0):
                sys.exit(f"setup {path} failed: {err}")
        results = [run(engine, t, stmts, cwd) for t in texts]
    rows = []
    for i, s in enumerate(stmts):
        codes = [r.get(i) for r in results]
        judged = [c for c in codes if c and not c.startswith("??")]
        if None in codes:
            verdict = "PASS"
        elif any(re.search(ENGINES[engine]["syntax"], c) for c in judged):
            verdict = "SYNTAX"  # a syntax error doesn't depend on the setup state
        elif len(judged) < len(codes):
            verdict = "UNKNOWN"  # some variant couldn't be judged and might have passed
        else:
            verdict = "SEMANTIC"
        shown = " | ".join((c or "ok")[:90] for c in codes)
        rows.append((i + 1, verdict, shown, " ".join(s.split())))
    return rows


def selftest() -> None:
    """Check splitting and verdicts end to end on the host sqlite3 (no Docker)."""
    with tempfile.TemporaryDirectory() as d:
        fx, st = os.path.join(d, "f.sql"), os.path.join(d, "s.sql")
        open(st, "w").write("CREATE TABLE t (a INT);")
        open(fx, "w").write(
            "-- comment only;\nSELECT 'x;y' FROM t;\nINSERT INTO t VALUES (1);\n"
            "SELECT * FROM nope;\nSELEC 1;\nCREATE TABLE t (b INT);\n"
            "CREATE TRIGGER tr AFTER INSERT ON t BEGIN SELECT 1; END;\nCOMMIT;\nSELECT 2;\n"
            f".shell touch {os.path.join(d, 'pwned')}\nSELECT 3"
        )
        got = [r[1] for r in main("sqlite", fx, [st])]
        assert not os.path.exists(os.path.join(d, "pwned")), "sqlite ran a host command"
    # COMMIT fails with no open transaction; real errors only, nothing leaks between statements.
    assert got == [
        "PASS",
        "PASS",
        "SEMANTIC",
        "SYNTAX",
        "SEMANTIC",
        "PASS",
        "SEMANTIC",
        "PASS",
        "UNKNOWN",
    ], got
    assert split("CREATE FUNCTION f() AS $$ SELECT 1; $$;\nSELECT 1") == [
        "CREATE FUNCTION f() AS $$ SELECT 1; $$",
        "SELECT 1",
    ]
    assert split("SELECT '$x$';\nSELECT 1") == ["SELECT '$x$'", "SELECT 1"]
    with (
        tempfile.TemporaryDirectory() as d
    ):  # setup with no final ";", ending in a comment
        fx, st = os.path.join(d, "f.sql"), os.path.join(d, "s.sql")
        open(st, "w").write("CREATE TABLE t (a INT)\n-- trailing comment")
        open(fx, "w").write("SELECT a FROM t;\nSELECT 'unterminated;")
        got = [r[1] for r in main("sqlite", fx, [st])]
    assert got == ["PASS", "SYNTAX"], got
    # Batched engines: a statement whose end marker never arrives is UNKNOWN, not PASS.
    got = parse_batch("@@S 0\n@@E\n@@S 1\nERROR: boom\n@@E\n@@S 2\n", 4, r"ERROR:")
    assert got == {
        1: "ERROR: boom",
        2: "?? no end marker in output (client stopped early?)",
        3: "?? no end marker in output (client stopped early?)",
    }, got
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        selftest()
    elif len(sys.argv) < 3 or sys.argv[1] not in ENGINES:
        sys.exit(__doc__)
    else:
        for row in main(sys.argv[1], sys.argv[2], sys.argv[3:]):
            print(*row, sep="\t")
