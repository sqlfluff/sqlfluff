"""Tests specific to the MariaDB dialect."""

import pytest

from sqlfluff.core import Linter


@pytest.mark.parametrize(
    "raw",
    [
        "CREATE PROCEDURE p(IN OUT a INT) SET a = a + 1",
        "CREATE FUNCTION f(IN OUT a INT) RETURNS INT RETURN a",
    ],
)
def test_mariadb_in_out_is_oracle_mode_only(raw: str) -> None:
    """Test that the two-word IN OUT parameter mode does not parse.

    MariaDB accepts it only with sql_mode=ORACLE, and there after the
    parameter name; in the default mode, which this dialect follows, it is a
    syntax error. Accepting it would need an Oracle-mode dialect, which
    sqlfluff does not have.
    """
    parsed = Linter(dialect="mariadb").parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors


@pytest.mark.parametrize(
    "raw",
    [
        # OR REPLACE after DEFINER, instead of straight after CREATE.
        "CREATE DEFINER = CURRENT_USER OR REPLACE FUNCTION f() RETURNS INT RETURN 1",
        "CREATE DEFINER = CURRENT_USER() OR REPLACE PROCEDURE p() SELECT 1",
        "CREATE DEFINER = 'u'@'%' OR REPLACE EVENT e "
        "ON SCHEDULE EVERY 1 DAY DO SELECT 1",
        # AGGREGATE before DEFINER, instead of just before FUNCTION.
        "CREATE AGGREGATE DEFINER = CURRENT_USER FUNCTION f(x INT) RETURNS INT "
        "RETURN x",
    ],
)
def test_mariadb_routine_header_order_is_fixed(raw: str) -> None:
    """Test that MariaDB's routine and event header order is enforced.

    The order is CREATE [OR REPLACE] [DEFINER = user] [AGGREGATE] FUNCTION,
    and likewise for PROCEDURE and EVENT. Each of these moves one part, and
    each is a syntax error on the server.
    """
    parsed = Linter(dialect="mariadb").parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors


@pytest.mark.parametrize(
    "raw",
    [
        "CREATE USER CURRENT_ROLE",
        "DROP USER CURRENT_ROLE",
        "KILL USER CURRENT_ROLE",
    ],
)
def test_mariadb_current_role_only_where_a_role_fits(raw: str) -> None:
    """Test that CURRENT_ROLE is not accepted where only a user makes sense.

    It belongs in DEFINER and role positions (`user_or_role` in the server's
    grammar), not where a statement names a specific user account. None of
    these can work on the server: DROP USER is a syntax error, CREATE USER
    fails (1396), and KILL USER does not read it as a user (1054).
    """
    parsed = Linter(dialect="mariadb").parse_string(raw)
    parsing_errors = [v for v in parsed.violations if v.rule_code() == "PRS"]

    assert parsing_errors
