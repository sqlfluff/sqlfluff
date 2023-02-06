"""The Test suite for `DeprecatedOption` - extension for click options."""
from typing import List

import click
import pytest

from sqlfluff.cli.click_deprecated_option import (
    DeprecatedOption,
    DeprecatedOptionsCommand,
)
from test.cli.commands_test import invoke_assert_code


class TestClickDeprecatedOption:
    """Tests for custom click's option `DeprecatedOption`."""

    @pytest.mark.parametrize(
        "option, expected_output",
        [
            ([], "{'old_option': False}\n"),
            (
                ["--old_option"],
                "DeprecationWarning: The option '--old_option' is deprecated, "
                "use '--new_option'.\n{'old_option': True}\n",
            ),
            (["--new_option"], "{'old_option': True}\n"),
        ],
    )
    def test_cli_deprecated_option(
        self, option: List[str], expected_output: str
    ) -> None:
        """Prepares command with option which has deprecated version and checks it."""

        @click.command(cls=DeprecatedOptionsCommand)
        @click.option(
            "--old_option",
            "--new_option",
            is_flag=True,
            cls=DeprecatedOption,
            deprecated=["--old_option"],
        )
        def some_command(**kwargs):
            click.echo("{}".format(kwargs))

        result = invoke_assert_code(args=[some_command, option])
        raw_output = result.output

        assert raw_output == expected_output

    def test_cli_deprecated_option_should_fail_when_missing_attr(
        self,
    ) -> None:
        """The DeprecatedOption needs to have specified deprecated attr."""

        @click.command(cls=DeprecatedOptionsCommand)
        @click.option(
            "--old_option",
            "--new_option",
            is_flag=True,
            cls=DeprecatedOption,
        )
        def some_command(**kwargs):
            click.echo("{}".format(kwargs))

        with pytest.raises(ValueError) as exc:
            invoke_assert_code(args=[some_command, ["--old_option"]])

        assert str(exc.value) == "Expected `deprecated` value for `'old_option'`"
