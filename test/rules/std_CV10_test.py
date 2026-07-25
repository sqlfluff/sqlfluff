"""Tests the python routines within CV10."""

import sqlfluff


def test__rules__std_CV10_quote_doubling_not_converted() -> None:
    """CV10 leaves literals that escape a quote by doubling it alone.

    Rewriting them would copy the doubled quotes into the other quote style,
    where they are not an escape, silently changing the value of the literal.
    The leading literal sets the consistent style, so the second one would
    otherwise be converted.
    """
    sql = "SELECT \"x\", 'O''Brien' FROM t\n"
    result = sqlfluff.fix(sql, rules=["CV10"], dialect="mysql")

    assert "'O''Brien'" in result


def test__rules__std_CV10_quote_doubling_not_converted_double_quotes() -> None:
    """The same holds in the double-quoted direction."""
    sql = 'SELECT \'x\', "say ""hi""" FROM t\n'
    result = sqlfluff.fix(sql, rules=["CV10"], dialect="mysql")

    assert '"say ""hi"""' in result
