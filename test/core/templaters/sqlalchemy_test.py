"""Tests for templaters."""
import pytest

from sqlfluff.core import FluffConfig
from sqlfluff.core.templaters import SqlalchemyTemplater
from sqlfluff.core.errors import SQLTemplaterError


def test__templater_raw():
    """Test the templaters when nothing has to be replaced."""
    t = SqlalchemyTemplater()
    instr = "SELECT * FROM {{blah}} WHERE %(gnepr)s OR e~':'"
    outstr, _ = t.process(in_str=instr, fname="test")
    assert str(outstr) == instr


@pytest.mark.parametrize(
    "instr, expected_outstr",
    [
        (
            "SELECT * FROM f, o, o WHERE a < 10\n\n",
            "SELECT * FROM f, o, o WHERE a < 10\n\n",
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE userid = :user_id AND date > :start_date
            """,
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE userid = 42 AND date > '2021-10-01'
            """,
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE userid = :user_id AND date > :start_date""",
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE userid = 42 AND date > '2021-10-01'""",
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN :city_ids
            AND date > '2020-10-01'
            """,
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN (1, 2, 3, 45)
            AND date > '2020-10-01'
            """,
        ),
    ],
    ids=[
        "no_changes",
        "simple_substitution",
        "accept_block_at_end",
        "tuple_substitution",
    ],
)
def test__templater_sqlalchemy(instr, expected_outstr):
    """Test sqlalchemy templating."""
    t = SqlalchemyTemplater(
        override_context=dict(
            user_id="42", start_date="'2021-10-01'", city_ids="(1, 2, 3, 45)"
        )
    )
    outstr, _ = t.process(in_str=instr, fname="test", config=FluffConfig())
    assert str(outstr) == expected_outstr


def test__templater_exception():
    """Test the exception raised when variables are missing."""
    t = SqlalchemyTemplater(override_context=dict(name="'john'"))
    instr = "SELECT name FROM table WHERE user_id = :user_id"
    with pytest.raises(
        SQLTemplaterError, match=r"Failure in SQLAlchemy templating: 'user_id'"
    ):
        t.process(in_str=instr, fname="test")
