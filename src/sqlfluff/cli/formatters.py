"""Defines the formatters for the CLI."""


from io import StringIO
from typing import Callable, List, Union

from sqlfluff.cli.helpers import (
    colorize,
    cli_table,
    get_package_version,
    get_python_version,
    get_python_implementation,
    pad_line,
)
from sqlfluff.core import SQLBaseError, FluffConfig, Linter
from sqlfluff.core.enums import Color
from sqlfluff.core.linter import LintedFile


def format_filename(
    filename: str, success: Union[str, bool] = False, success_text: str = "PASS"
) -> str:
    """Format filenames."""
    if isinstance(success, str):
        status_string = success
    else:
        status_string = colorize(
            success_text if success else "FAIL",
            Color.green if success else Color.red,
        )
    return f"== [{colorize(filename, Color.lightgrey)}] {status_string}"


def split_string_on_spaces(s: str, line_length: int = 100) -> List[str]:
    """Split a string into lines based on whitespace."""
    line_buff = []
    str_buff = ""
    for token in s.split():
        # Can we put this token on this line without going over?
        if str_buff:
            if len(str_buff) + len(token) > line_length:
                line_buff.append(str_buff)
                str_buff = token
            else:
                str_buff += " " + token
        else:
            # In the case that the buffer is already empty, add it without checking,
            # otherwise there might be things that we might never.
            str_buff = token
    # If we have left over buff, add it in
    if str_buff:
        line_buff.append(str_buff)
    return line_buff


def format_violation(violation: SQLBaseError, max_line_length: int = 90) -> str:
    """Format a violation."""
    if isinstance(violation, SQLBaseError):
        desc = violation.desc()
        if violation.line_no is not None:
            line_elem = f"{violation.line_no:4d}"
        else:
            line_elem = "   -"  # pragma: no cover
        if violation.line_pos is not None:
            pos_elem = f"{violation.line_pos:4d}"
        else:
            pos_elem = "   -"  # pragma: no cover
    else:  # pragma: no cover
        raise ValueError(f"Unexpected violation format: {violation}")

    if violation.ignore:
        desc = "IGNORE: " + desc  # pragma: no cover

    split_desc = split_string_on_spaces(desc, line_length=max_line_length - 25)

    out_buff = ""
    for idx, line in enumerate(split_desc):
        if idx == 0:
            out_buff += colorize(
                f"L:{line_elem} | P:{pos_elem} | {violation.rule_code().rjust(4)} | ",
                # Grey out the violation if we're ignoring it.
                Color.lightgrey if violation.ignore else Color.blue,
            )
        else:
            out_buff += (
                "\n"
                + (" " * 23)
                + colorize(
                    "| ",
                    Color.lightgrey if violation.ignore else Color.blue,
                )
            )
        out_buff += line
    return out_buff


def format_linting_stats(result, verbose=0):
    """Format a set of stats given a `LintingResult`."""
    text_buffer = StringIO()
    all_stats = result.stats()
    text_buffer.write("==== summary ====\n")
    if verbose >= 2:
        output_fields = [
            "files",
            "violations",
            "clean files",
            "unclean files",
            "avg per file",
            "unclean rate",
            "status",
        ]
        special_formats = {"unclean rate": "{0:.0%}"}
    else:
        output_fields = ["violations", "status"]
        special_formats = {}
    # Generate content tuples, applying special formats for some fields
    summary_content = [
        (
            key,
            special_formats[key].format(all_stats[key])
            if key in special_formats
            else all_stats[key],
        )
        for key in output_fields
    ]
    # Render it all as a table
    text_buffer.write(cli_table(summary_content, max_label_width=14))
    return text_buffer.getvalue()


def format_linting_result_header():
    """Format the header of a linting result output."""
    text_buffer = StringIO()
    text_buffer.write("==== readout ====\n")
    return text_buffer.getvalue()


def format_config_vals(config_vals):
    """Format an iterable of config values from a config object."""
    text_buffer = StringIO()
    for i, k, v in config_vals:
        val = "" if v is None else str(v)
        text_buffer.write(
            ("    " * i)
            + colorize(pad_line(str(k) + ":", 20, "left"), color=Color.lightgrey)
            + pad_line(val, 20, "left")
            + "\n"
        )
    return text_buffer.getvalue()


def format_rules(linter: Linter, verbose: int = 0) -> str:
    """Format the a set of rules given a `Linter`."""
    text_buffer = StringIO()
    text_buffer.write("==== sqlfluff - rules ====\n")
    text_buffer.write(
        cli_table(
            linter.rule_tuples(),
            col_width=80,
            cols=1,
            label_color=Color.blue,
            val_align="left",
        )
    )
    return text_buffer.getvalue()


def format_dialects(dialect_readout, verbose=0):
    """Format the dialects yielded by `dialect_readout`."""
    text_buffer = StringIO()
    text_buffer.write("==== sqlfluff - dialects ====\n")
    readouts = [
        (
            dialect.label,
            f"{dialect.name} dialect [inherits from '{dialect.inherits_from}']",
        )
        for dialect in dialect_readout()
    ]
    text_buffer.write(
        cli_table(
            readouts,
            col_width=60,
            cols=1,
            label_color=Color.blue,
            val_align="right",
        )
    )
    return text_buffer.getvalue()


def format_dialect_warning():  # pragma: no cover
    """Output a warning for parsing errors found on the ansi dialect."""
    return colorize(
        (
            "WARNING: Parsing errors found and dialect is set to "
            "'ansi'. Have you configured your dialect?"
        ),
        Color.lightgrey,
    )


class CallbackFormatter:
    """Formatter which uses a callback to output information.

    On instantiation, this formatter accepts a function to
    dispatch messages. Each public method accepts an object
    or data in a common format, with this class handling the
    formatting and output.

    This class is designed to be subclassed if we eventually
    want to provide other methods of surfacing output.


    Args:
        callback (:obj:`callable`): A callable which can be
            be called with a string to be output.
        verbosity (:obj:`int`): An integer specifying how
            verbose the output should be.
        filter_empty (:obj:`bool`): If True, empty messages
            will not be dispatched.

    """

    def __init__(
        self,
        callback: Callable,
        verbosity: int = 0,
        filter_empty: bool = True,
        output_line_length: int = 80,
    ):
        self._callback = callback
        self._verbosity = verbosity
        self._filter_empty = filter_empty
        self.output_line_length = output_line_length

    def _dispatch(self, s: str) -> None:
        """Dispatch a string to the callback.

        This method is designed as a point for subclassing.
        """
        # The strip here is to filter out any empty messages
        if (not self._filter_empty) or s.strip(" \n\t"):
            self._callback(s)

    def _format_config(self, linter: Linter) -> str:
        """Format the config of a `Linter`."""
        text_buffer = StringIO()
        # Only show version information if verbosity is high enough
        if self._verbosity > 0:
            text_buffer.write("==== sqlfluff ====\n")
            config_content = [
                ("sqlfluff", get_package_version()),
                ("python", get_python_version()),
                ("implementation", get_python_implementation()),
                ("dialect", linter.dialect.name),
                ("verbosity", self._verbosity),
            ] + linter.templater.config_pairs()
            text_buffer.write(
                cli_table(config_content, col_width=30, max_label_width=15)
            )
            text_buffer.write("\n")
            if linter.config.get("rule_allowlist"):
                text_buffer.write(
                    cli_table(
                        [("rules", ", ".join(linter.config.get("rule_allowlist")))],
                        col_width=41,
                    )
                )
            if self._verbosity > 1:
                text_buffer.write("\n== Raw Config:\n")
                text_buffer.write(format_config_vals(linter.config.iter_vals()))
        return text_buffer.getvalue()

    def dispatch_config(self, linter: Linter) -> None:
        """Dispatch configuration output appropriately."""
        self._dispatch(self._format_config(linter))

    def dispatch_persist_filename(self, filename, result):
        """Dispatch filenames during a persist operation."""
        # Only show the skip records at higher levels of verbosity
        if self._verbosity >= 2 or result != "SKIP":
            self._dispatch(format_filename(filename=filename, success=result))

    @staticmethod
    def _format_path(path: str) -> str:
        """Format paths."""
        return f"=== [ path: {colorize(path, Color.lightgrey)} ] ===\n"

    def dispatch_path(self, path: str) -> None:
        """Dispatch paths for display."""
        if self._verbosity > 0:
            self._dispatch(self._format_path(path))

    def dispatch_template_header(
        self, fname: str, linter_config: FluffConfig, file_config: FluffConfig
    ) -> None:
        """Dispatch the header displayed before templating."""
        if self._verbosity > 1:
            self._dispatch(format_filename(filename=fname, success="TEMPLATING"))
            # This is where we output config diffs if they exist.
            if file_config:
                # Only output config diffs if there is a config to diff to.
                config_diff = file_config.diff_to(linter_config)
                if config_diff:  # pragma: no cover
                    self._dispatch("   Config Diff:")
                    self._dispatch(
                        format_config_vals(linter_config.iter_vals(cfg=config_diff))
                    )

    def dispatch_parse_header(self, fname: str) -> None:
        """Dispatch the header displayed before parsing."""
        if self._verbosity > 1:
            self._dispatch(format_filename(filename=fname, success="PARSING"))

    def dispatch_lint_header(self, fname: str) -> None:
        """Dispatch the header displayed before linting."""
        if self._verbosity > 1:
            self._dispatch(format_filename(filename=fname, success="LINTING"))

    def dispatch_compilation_header(self, templater, message):
        """Dispatch the header displayed before linting."""
        self._dispatch(
            f"=== [{colorize(templater, Color.lightgrey)}] {message}"
        )  # pragma: no cover

    def dispatch_dialect_warning(self) -> None:
        """Dispatch a warning for dialects."""
        self._dispatch(format_dialect_warning())  # pragma: no cover

    def _format_file_violations(
        self, fname: str, violations: List[SQLBaseError]
    ) -> str:
        """Format a set of violations in a `LintingResult`."""
        text_buffer = StringIO()
        # Success is having no violations (which aren't ignored)
        success = sum(int(not violation.ignore) for violation in violations) == 0

        # Only print the filename if it's either a failure or verbosity > 1
        if self._verbosity > 0 or not success:
            text_buffer.write(format_filename(fname, success=success))
            text_buffer.write("\n")

        # If we have violations, print them
        if not success:
            # sort by position in file (using line number and position)
            s = sorted(violations, key=lambda v: (v.line_no, v.line_pos))
            for violation in s:
                text_buffer.write(
                    format_violation(violation, max_line_length=self.output_line_length)
                )
                text_buffer.write("\n")
        str_buffer = text_buffer.getvalue()
        # Remove the trailing newline if there is one
        if len(str_buffer) > 0 and str_buffer[-1] == "\n":
            str_buffer = str_buffer[:-1]
        return str_buffer

    def dispatch_file_violations(
        self, fname: str, linted_file: LintedFile, only_fixable: bool
    ) -> None:
        """Dispatch any violations found in a file."""
        s = self._format_file_violations(
            fname, linted_file.get_violations(fixable=True if only_fixable else None)
        )
        self._dispatch(s)
