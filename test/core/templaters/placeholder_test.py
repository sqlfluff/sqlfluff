"""Tests for templaters."""

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff.core.templaters import PlaceholderTemplater


def test__templater_raw():
    """Test the templaters when nothing has to be replaced."""
    t = PlaceholderTemplater(override_context=dict(param_style="colon"))
    instr = "SELECT * FROM {{blah}} WHERE %(gnepr)s OR e~':'"
    outstr, _ = t.process(in_str=instr, fname="test")
    assert str(outstr) == instr


@pytest.mark.parametrize(
    "instr, param_style, expected_outstr, values",
    [
        (
            "SELECT * FROM f, o, o WHERE a < 10\n\n",
            "colon",
            "SELECT * FROM f, o, o WHERE a < 10\n\n",
            dict(
                unused=7777,
            ),
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE userid = :user_id AND date > :start_date
            """,
            "colon",
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE userid = 42 AND date > '2021-10-01'
            """,
            dict(
                user_id="42",
                start_date="'2021-10-01'",
                city_ids="(1, 2, 3, 45)",
            ),
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE userid = :user_id AND date > :start_date""",
            "colon",
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE userid = 42 AND date > '2021-10-01'""",
            dict(
                user_id="42",
                start_date="'2021-10-01'",
                city_ids="(1, 2, 3, 45)",
            ),
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN :city_ids
            AND date > '2020-10-01'
            """,
            "colon",
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN (1, 2, 3, 45)
            AND date > '2020-10-01'
            """,
            dict(
                user_id="42",
                start_date="'2021-10-01'",
                city_ids="(1, 2, 3, 45)",
            ),
        ),
        (
            """
            SELECT user_mail, city_id, :"custom_column"
            FROM users_data
            WHERE userid = :user_id AND date > :'start_date'
            """,
            "colon_optional_quotes",
            """
            SELECT user_mail, city_id, "PascalCaseColumn"
            FROM users_data
            WHERE userid = 42 AND date > '2021-10-01'
            """,
            dict(
                user_id="42",
                custom_column="PascalCaseColumn",
                start_date="2021-10-01",
            ),
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data:table_suffix
            """,
            "colon_nospaces",
            """
            SELECT user_mail, city_id
            FROM users_data42
            """,
            dict(
                table_suffix="42",
            ),
        ),
        (
            # Postgres uses double-colons for type casts , see
            # https://www.postgresql.org/docs/current/sql-expressions.html#SQL-SYNTAX-TYPE-CASTS
            # This test ensures we don't confuse them with colon placeholders.
            """
            SELECT user_mail, city_id, joined::date
            FROM users_data:table_suffix
            """,
            "colon_nospaces",
            """
            SELECT user_mail, city_id, joined::date
            FROM users_data42
            """,
            dict(
                table_suffix="42",
            ),
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN ?
            AND date > ?
            """,
            "question_mark",
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN (1, 2, 3, 45)
            AND date > '2020-10-01'
            """,
            {
                "1": "(1, 2, 3, 45)",
                "2": "'2020-10-01'",
            },
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN :1
            AND date > :45
            """,
            "numeric_colon",
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN (1, 2, 3, 45)
            AND date > '2020-10-01'
            """,
            {
                "1": "(1, 2, 3, 45)",
                "45": "'2020-10-01'",
            },
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN %(city_id)s
            AND date > %(date)s
            AND someflag = %(someflag)s
            LIMIT %(limit)s
            """,
            "pyformat",
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN (1, 2, 3, 45)
            AND date > '2020-10-01'
            AND someflag = False
            LIMIT 15
            """,
            dict(
                city_id="(1, 2, 3, 45)", date="'2020-10-01'", limit=15, someflag=False
            ),
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN $city_id
            AND date > $date
            OR date = ${date}
            """,
            "dollar",
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN (1, 2, 3, 45)
            AND date > '2020-10-01'
            OR date = '2020-10-01'
            """,
            dict(
                city_id="(1, 2, 3, 45)",
                date="'2020-10-01'",
            ),
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN $12
            AND date > $90
            """,
            "numeric_dollar",
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN (1, 2, 3, 45)
            AND date > '2020-10-01'
            """,
            {
                "12": "(1, 2, 3, 45)",
                "90": "'2020-10-01'",
            },
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN ${12}
            AND date > ${90}
            """,
            "numeric_dollar",
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN (1, 2, 3, 45)
            AND date > '2020-10-01'
            """,
            {
                "12": "(1, 2, 3, 45)",
                "90": "'2020-10-01'",
            },
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE user_mail = '${12}'
            AND date > ${90}
            """,
            "numeric_dollar",
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE user_mail = 'test@example.com'
            AND date > '2020-10-01'
            """,
            {
                "12": "test@example.com",
                "90": "'2020-10-01'",
            },
        ),
        (
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN %s
            AND date > %s
            """,
            "percent",
            """
            SELECT user_mail, city_id
            FROM users_data
            WHERE (city_id) IN (1, 2, 3, 45)
            AND date > '2020-10-01'
            """,
            {
                "1": "(1, 2, 3, 45)",
                "2": "'2020-10-01'",
            },
        ),
        (
            """
            USE DATABASE &{env}_MARKETING;
            USE SCHEMA &&EMEA;
            SELECT user_mail, city_id
            FROM users_data
            WHERE userid = &user_id AND date > &{start_date}
            """,
            "ampersand",
            """
            USE DATABASE PRD_MARKETING;
            USE SCHEMA &&EMEA;
            SELECT user_mail, city_id
            FROM users_data
            WHERE userid = 42 AND date > '2021-10-01'
            """,
            dict(
                env="PRD",
                user_id="42",
                start_date="'2021-10-01'",
            ),
        ),
        (
            "USE ${flyway:database}.test_schema;",
            "flyway_var",
            "USE test_db.test_schema;",
            {
                "flyway:database": "test_db",
            },
        ),
        (
            "SELECT metadata$filename, $1 FROM @stg_data_export_${env_name};",
            "flyway_var",
            "SELECT metadata$filename, $1 FROM @stg_data_export_staging;",
            {
                "env_name": "staging",
            },
        ),
        (
            "SELECT metadata$filename, $1 FROM @stg_data_export_${env_name};",
            "flyway_var",
            "SELECT metadata$filename, $1 FROM @stg_data_export_env_name;",
            {},
        ),
    ],
    ids=[
        "no_changes",
        "colon_simple_substitution",
        "colon_accept_block_at_end",
        "colon_tuple_substitution",
        "colon_quoted",
        "colon_nospaces",
        "colon_nospaces_double_colon_ignored",
        "question_mark",
        "numeric_colon",
        "pyformat",
        "dollar",
        "numeric_dollar",
        "numeric_dollar_with_braces",
        "numeric_dollar_with_braces_and_string",
        "percent",
        "ampersand",
        "flyway_var",
        "flyway_var",
        "params_not_specified",
    ],
)
def test__templater_param_style(instr, expected_outstr, param_style, values):
    """Test different param_style templating."""
    t = PlaceholderTemplater(override_context={**values, "param_style": param_style})
    outstr, _ = t.process(
        in_str=instr, fname="test", config=FluffConfig(overrides={"dialect": "ansi"})
    )
    assert str(outstr) == expected_outstr


def test__templater_custom_regex():
    """Test custom regex templating."""
    t = PlaceholderTemplater(
        override_context=dict(param_regex="__(?P<param_name>[\\w_]+)__", my_name="john")
    )
    outstr, _ = t.process(
        in_str="SELECT bla FROM blob WHERE id = __my_name__",
        fname="test",
        config=FluffConfig(overrides={"dialect": "ansi"}),
    )
    assert str(outstr) == "SELECT bla FROM blob WHERE id = john"


def test__templater_setup():
    """Test the exception raised when config is incomplete or ambiguous."""
    t = PlaceholderTemplater(override_context=dict(name="'john'"))
    with pytest.raises(
        ValueError,
        match=(
            "No param_regex nor param_style was provided to the placeholder templater"
        ),
    ):
        t.process(in_str="SELECT 2+2", fname="test")

    t = PlaceholderTemplater(
        override_context=dict(param_style="bla", param_regex="bli")
    )
    with pytest.raises(
        ValueError,
        match=r"Either param_style or param_regex must be provided, not both",
    ):
        t.process(in_str="SELECT 2+2", fname="test")


def test__templater_styles():
    """Test the exception raised when parameter style is unknown."""
    t = PlaceholderTemplater(override_context=dict(param_style="pperccent"))
    with pytest.raises(ValueError, match=r"Unknown param_style"):
        t.process(in_str="SELECT 2+2", fname="test")
