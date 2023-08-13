"""Allows to provide deprecated options for click's command."""

from typing import Any, Callable

import click
from click import Context, OptionParser, echo, style
from click.parser import Option, ParsingState


class DeprecatedOption(click.Option):
    """Allows to provide deprecated options for click's command.

    Works with `DeprecatedOptionsCommand` (see below).
    Expects to be provided into standard `@click.option` with:
      * two parameter declarations arguments - old one (deprecated)
        and new one (preferred);
      * `cls` parameter (standard click Option) as `cls=DeprecatedOption`;
      * `deprecated` parameter - which says which ones are deprecated,
        like`deprecated=["--disable_progress_bar"]1.

    This is based on
      * https://stackoverflow.com/a/50402799/5172513

    It's somewhat hackish and may broke when click internals are changed, it is even
    mentioned in SO:
    > This code reaches into some private structures in the parser, but this is
    unlikely to be an issue. This parser code was last changed 4 years ago.
    The parser code is unlikely to undergo significant revisions.

    Hopefully will be removed when
      * https://github.com/pallets/click/issues/2263
    is finished.
    """

    def __init__(self, *args, **kwargs) -> None:
        self.deprecated = kwargs.pop("deprecated", ())
        self.preferred = args[0][-1]

        super().__init__(*args, **kwargs)


class DeprecatedOptionsCommand(click.Command):
    """Allows to provide deprecated options for click's command.

    Works with `DeprecatedOption` (see above).
    Expects to be provided into standard `@click.command` as:
      * `@cli.command(cls=DeprecatedOptionsCommand)`
    """

    def make_parser(self, ctx: Context) -> OptionParser:
        """Hook 'make_parser' and during processing check the name.

        Used to invoke the option to see if it is preferred.
        """
        parser: OptionParser = super().make_parser(ctx)

        # get the parser options
        options = set(parser._short_opt.values())
        options |= set(parser._long_opt.values())

        for option in options:
            if not isinstance(option.obj, DeprecatedOption):
                continue

            option.process = self._make_process(option)  # type: ignore

        return parser

    def _make_process(self, an_option: Option) -> Callable:
        """Construct a closure to the parser option processor."""
        orig_process: Callable = an_option.process
        deprecated = getattr(an_option.obj, "deprecated", None)
        preferred = getattr(an_option.obj, "preferred", None)

        if not deprecated:
            raise ValueError(
                f"Expected `deprecated` value for `{an_option.obj.name!r}`"
            )

        def process(value: Any, state: ParsingState) -> None:
            """Custom process method.

            The function above us on the stack used 'opt' to
            pick option from a dict, see if it is deprecated.
            """
            # reach up the stack and get 'opt'
            import inspect

            frame = inspect.currentframe()
            try:
                opt = frame.f_back.f_locals.get("opt")  # type: ignore
            finally:
                del frame

            assert deprecated
            if opt in deprecated:
                msg = (
                    f"DeprecationWarning: The option {opt!r} is deprecated, "
                    f"use {preferred!r}."
                )
                echo(style(msg, fg="red"), err=True)

            return orig_process(value, state)

        return process
