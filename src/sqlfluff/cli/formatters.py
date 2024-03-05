"""Defines the formatters for the CLI."""

import sys
from io import StringIO
from typing import List, Optional, Tuple, Union

import click
from colorama import Style

from sqlfluff.cli import EXIT_FAIL, EXIT_SUCCESS
from sqlfluff.cli.helpers import (
    get_package_version,
    get_python_implementation,
    get_python_version,
    pad_line,
    wrap_field,
)
from sqlfluff.cli.outputstream import OutputStream
from sqlfluff.core import FluffConfig, Linter, SQLBaseError, TimingSummary
from sqlfluff.core.enums import Color
from sqlfluff.core.linter import LintedFile, ParsedString


def split_string_on_spaces(s: str, line_length: int = 100) -> List[str]:
    """Split a string into lines based on whitespace.

    For short strings the functionality is trivial.
    >>> split_string_on_spaces("abc")
    ['abc']

    For longer sections it will split at an appropriate point.
    >>> split_string_on_spaces("abc def ghi", line_length=7)
    ['abc def', 'ghi']

    After splitting, multi-space sections should be intact.
    >>> split_string_on_spaces("a '   ' b c d e f", line_length=11)
    ["a '   ' b c", 'd e f']
    """
    line_buff = []
    str_buff = ""
    # NOTE: We *specify* the single space split, so that on reconstruction
    # we can accurately represent multi space strings.
    for token in s.split(" "):
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


def format_linting_result_header() -> str:
    """Format the header of a linting result output."""
    text_buffer = StringIO()
    text_buffer.write("==== readout ====\n")
    return text_buffer.getvalue()


class OutputStreamFormatter:
    """Formatter which writes to an OutputStream.

    On instantiation, this formatter accepts a function to
    dispatch messages. Each public method accepts an object
    or data in a common format, with this class handling the
    formatting and output.

    This class is designed to be subclassed if we eventually
    want to provide other methods of surfacing output.


    Args:
        output_stream: Output is sent here
        verbosity: Specifies how verbose output should be
        filter_empty: If True, empty messages will not be dispatched
        output_line_length: Maximum line length
    """

    def __init__(
        self,
        output_stream: OutputStream,
        nocolor: bool,
        verbosity: int = 0,
        filter_empty: bool = True,
        output_line_length: int = 80,
    ):
        self._output_stream = output_stream
        self.plain_output = self.should_produce_plain_output(nocolor)
        self.verbosity = verbosity
        self._filter_empty = filter_empty
        self.output_line_length = output_line_length

    @staticmethod
    def should_produce_plain_output(nocolor: bool) -> bool:
        """Returns True if text output should be plain (not colored)."""
        return nocolor or not sys.stdout.isatty()

    def _dispatch(self, s: str) -> None:
        """Dispatch a string to the callback.

        This method is designed as a point for subclassing.
        """
        # The strip here is to filter out any empty messages
        if (not self._filter_empty) or s.strip(" \n\t"):
            self._output_stream.write(s)

    def _format_config(self, linter: Linter) -> str:
        """Format the config of a `Linter`."""
        text_buffer = StringIO()
        # Only show version information if verbosity is high enough
        if self.verbosity > 0:
            text_buffer.write("==== sqlfluff ====\n")
            config_content = [
                ("sqlfluff", get_package_version()),
                ("python", get_python_version()),
                ("implementation", get_python_implementation()),
                ("verbosity", self.verbosity),
            ]
            if linter.dialect:
                config_content.append(("dialect", linter.dialect.name))
            config_content += linter.templater.config_pairs()
            text_buffer.write(
                self.cli_table(config_content, col_width=30, max_label_width=15)
            )
            text_buffer.write("\n")
            if linter.config.get("rule_allowlist"):
                text_buffer.write(
                    self.cli_table(
                        [("rules", ", ".join(linter.config.get("rule_allowlist")))],
                        col_width=41,
                    )
                )
            if self.verbosity > 1:
                text_buffer.write("\n== Raw Config:\n")
                text_buffer.write(self.format_config_vals(linter.config.iter_vals()))
        return text_buffer.getvalue()

    def dispatch_config(self, linter: Linter) -> None:
        """Dispatch configuration output appropriately."""
        self._dispatch(self._format_config(linter))

    def dispatch_persist_filename(self, filename: str, result: str) -> None:
        """Dispatch filenames during a persist operation."""
        # Only show the skip records at higher levels of verbosity
        if self.verbosity >= 2 or result != "SKIP":
            self._dispatch(self.format_filename(filename=filename, success=result))

    def _format_path(self, path: str) -> str:
        """Format paths."""
        return f"=== [ path: {self.colorize(path, Color.lightgrey)} ] ===\n"

    def dispatch_path(self, path: str) -> None:
        """Dispatch paths for display."""
        if self.verbosity > 0:
            self._dispatch(self._format_path(path))

    def dispatch_template_header(
        self, fname: str, linter_config: FluffConfig, file_config: FluffConfig
    ) -> None:
        """Dispatch the header displayed before templating."""
        if self.verbosity > 1:
            self._dispatch(self.format_filename(filename=fname, success="TEMPLATING"))
            # This is where we output config diffs if they exist.
            if file_config:
                # Only output config diffs if there is a config to diff to.
                config_diff = file_config.diff_to(linter_config)
                if config_diff:  # pragma: no cover
                    self._dispatch("   Config Diff:")
                    self._dispatch(
                        self.format_config_vals(
                            linter_config.iter_vals(cfg=config_diff)
                        )
                    )

    def dispatch_parse_header(self, fname: str) -> None:
        """Dispatch the header displayed before parsing."""
        if self.verbosity > 1:
            self._dispatch(self.format_filename(filename=fname, success="PARSING"))

    def dispatch_lint_header(self, fname: str, rules: List[str]) -> None:
        """Dispatch the header displayed before linting."""
        if self.verbosity > 1:
            self._dispatch(
                self.format_filename(
                    filename=fname, success=f"LINTING ({', '.join(rules)})"
                )
            )

    def dispatch_compilation_header(self, templater: str, message: str) -> None:
        """Dispatch the header displayed before linting."""
        self._dispatch(
            f"=== [{self.colorize(templater, Color.lightgrey)}] {message}"
        )  # pragma: no cover

    def dispatch_processing_header(self, processes: int) -> None:
        """Dispatch the header displayed before linting."""
        if self.verbosity > 0:
            self._dispatch(  # pragma: no cover
                f"{self.colorize('effective configured processes: ', Color.lightgrey)} "
                f"{processes}"
            )

    def dispatch_dialect_warning(self, dialect) -> None:
        """Dispatch a warning for dialects."""
        self._dispatch(self.format_dialect_warning(dialect))  # pragma: no cover

    def _format_file_violations(
        self, fname: str, violations: List[SQLBaseError]
    ) -> str:
        """Format a set of violations in a `LintingResult`."""
        text_buffer = StringIO()
        # Success is based on there being no fails, but we still
        # want to show the results if there are warnings (even
        # if no fails).
        fails = sum(
            int(not violation.ignore and not violation.warning)
            for violation in violations
        )
        warns = sum(int(violation.warning) for violation in violations)
        show = fails + warns > 0

        # Only print the filename if it's either a failure or verbosity > 1
        if self.verbosity > 0 or show:
            text_buffer.write(self.format_filename(fname, success=fails == 0))
            text_buffer.write("\n")

        # If we have violations, print them
        if show:
            # sort by position in file (using line number and position)
            s = sorted(violations, key=lambda v: (v.line_no, v.line_pos))
            for violation in s:
                text_buffer.write(
                    self.format_violation(
                        violation, max_line_length=self.output_line_length
                    )
                )
                text_buffer.write("\n")
        str_buffer = text_buffer.getvalue()
        # Remove the trailing newline if there is one
        if len(str_buffer) > 0 and str_buffer[-1] == "\n":
            str_buffer = str_buffer[:-1]
        return str_buffer

    def dispatch_file_violations(
        self,
        fname: str,
        linted_file: LintedFile,
        only_fixable: bool,
        warn_unused_ignores: bool,
    ) -> None:
        """Dispatch any violations found in a file."""
        if self.verbosity < 0:
            return
        s = self._format_file_violations(
            fname,
            linted_file.get_violations(
                fixable=True if only_fixable else None,
                filter_warning=False,
                warn_unused_ignores=warn_unused_ignores,
            ),
        )
        self._dispatch(s)

    def colorize(self, s: str, color: Optional[Color] = None) -> str:
        """Optionally use ANSI colour codes to colour a string."""
        return self.colorize_helper(self.plain_output, s, color)

    @staticmethod
    def colorize_helper(
        plain_output: bool, s: str, color: Optional[Color] = None
    ) -> str:
        """Static version of colorize() method."""
        if not color or plain_output:
            return s
        else:
            return f"{color.value}{s}{Style.RESET_ALL}"

    def cli_table_row(
        self,
        fields: List[Tuple[str, str]],
        col_width,
        max_label_width=10,
        sep_char=": ",
        divider_char=" ",
        label_color=Color.lightgrey,
        val_align="right",
    ) -> str:
        """Make a row of a CLI table, using wrapped values."""
        # Do some intel first
        cols = len(fields)
        last_col_idx = cols - 1
        wrapped_fields = [
            wrap_field(
                field[0],
                field[1],
                width=col_width,
                max_label_width=max_label_width,
                sep_char=sep_char,
            )
            for field in fields
        ]
        max_lines = max(fld["lines"] for fld in wrapped_fields)
        last_line_idx = max_lines - 1
        # Make some text
        buff = StringIO()
        for line_idx in range(max_lines):
            for col_idx in range(cols):
                # Assume we pad labels left and values right
                fld = wrapped_fields[col_idx]
                ll = fld["label_list"]
                vl = fld["val_list"]
                buff.write(
                    self.colorize(
                        pad_line(
                            ll[line_idx] if line_idx < len(ll) else "",
                            width=fld["label_width"],
                        ),
                        color=label_color,
                    )
                )
                if line_idx == 0:
                    buff.write(sep_char)
                else:
                    buff.write(" " * len(sep_char))
                buff.write(
                    pad_line(
                        vl[line_idx] if line_idx < len(vl) else "",
                        width=fld["val_width"],
                        align=val_align,
                    )
                )
                if col_idx != last_col_idx:
                    buff.write(divider_char)
                elif line_idx != last_line_idx:
                    buff.write("\n")
        return buff.getvalue()

    def cli_table(
        self,
        fields,
        col_width=20,
        cols=2,
        divider_char=" ",
        sep_char=": ",
        label_color=Color.lightgrey,
        float_format="{0:.2f}",
        max_label_width=10,
        val_align="right",
    ) -> str:
        """Make a crude ascii table.

        Assume that `fields` is an iterable of (label, value) pairs.
        """
        # First format all the values into strings
        formatted_fields = []
        for label, value in fields:
            label = str(label)
            if isinstance(value, float):
                value = float_format.format(value)
            else:
                value = str(value)
            formatted_fields.append((label, value))

        # Set up a buffer to hold the whole table
        buff = StringIO()
        while len(formatted_fields) > 0:
            row_buff: List[Tuple[str, str]] = []
            while len(row_buff) < cols and len(formatted_fields) > 0:
                row_buff.append(formatted_fields.pop(0))
            buff.write(
                self.cli_table_row(
                    row_buff,
                    col_width=col_width,
                    max_label_width=max_label_width,
                    sep_char=sep_char,
                    divider_char=divider_char,
                    label_color=label_color,
                    val_align=val_align,
                )
            )
            if len(formatted_fields) > 0:
                buff.write("\n")
        return buff.getvalue()

    def format_filename(
        self,
        filename: str,
        success: Union[str, bool] = False,
        success_text: str = "PASS",
    ) -> str:
        """Format filenames."""
        if isinstance(success, str):
            status_string = success
        else:
            status_string = success_text if success else "FAIL"

        if status_string in ("PASS", "FIXED", success_text):
            status_string = self.colorize(status_string, Color.green)
        elif status_string in ("FAIL", "ERROR"):
            status_string = self.colorize(status_string, Color.red)

        return f"== [{self.colorize(filename, Color.lightgrey)}] {status_string}"

    def format_violation(
        self,
        violation: Union[SQLBaseError, dict],
        max_line_length: int = 90,
    ) -> str:
        """Format a violation.

        NOTE: This method accepts both SQLBaseError objects and the serialised
        dict representation. If the former is passed, then the conversion is
        done within the method so we can work with a common representation.
        """
        if isinstance(violation, dict):
            v_dict: dict = violation
        elif isinstance(violation, SQLBaseError):
            v_dict = violation.to_dict()
        elif not isinstance(violation, dict):  # pragma: no cover
            raise ValueError(f"Unexpected violation format: {violation}")

        desc: str = v_dict["description"]
        code: str = v_dict["code"]
        name: str = v_dict["name"]
        line_no: int = v_dict["start_line_no"]
        line_pos: int = v_dict["start_line_pos"]
        warning: bool = v_dict["warning"]
        line_elem = "   -" if line_no is None else f"{line_no:4d}"
        pos_elem = "   -" if line_pos is None else f"{line_pos:4d}"

        if warning:
            desc = "WARNING: " + desc  # pragma: no cover

        # If the rule has a name, add that the description.
        if name:
            desc += f" [{self.colorize(name, Color.lightgrey)}]"

        split_desc = split_string_on_spaces(desc, line_length=max_line_length - 25)

        out_buff = ""
        # Grey out the violation if we're ignoring or warning it.
        section_color: Color
        if warning:
            section_color = Color.lightgrey
        else:
            section_color = Color.blue

        for idx, line in enumerate(split_desc):
            if idx == 0:
                rule_code = code.rjust(4)
                if "PRS" in rule_code:
                    section_color = Color.red
                out_buff += self.colorize(
                    f"L:{line_elem} | P:{pos_elem} | {rule_code} | ",
                    section_color,
                )
            else:
                out_buff += (
                    "\n"
                    + (" " * 23)
                    + self.colorize(
                        "| ",
                        section_color,
                    )
                )
            out_buff += line
        return out_buff

    def format_linting_stats(self, result, verbose=0) -> str:
        """Format a set of stats given a `LintingResult`."""
        text_buffer = StringIO()
        all_stats = result.stats(EXIT_FAIL, EXIT_SUCCESS)
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
                (
                    special_formats[key].format(all_stats[key])
                    if key in special_formats
                    else all_stats[key]
                ),
            )
            for key in output_fields
        ]
        # Render it all as a table
        text_buffer.write(self.cli_table(summary_content, max_label_width=14))
        return text_buffer.getvalue()

    def format_config_vals(self, config_vals) -> str:
        """Format an iterable of config values from a config object."""
        text_buffer = StringIO()
        for i, k, v in config_vals:
            val = "" if v is None else str(v)
            text_buffer.write(
                ("    " * i)
                + self.colorize(
                    pad_line(str(k) + ":", 20, "left"), color=Color.lightgrey
                )
                + pad_line(val, 20, "left")
                + "\n"
            )
        return text_buffer.getvalue()

    def _format_rule_description(self, rule) -> str:
        """Format individual rule.

        This is a helper function in .format_rules().
        """
        if rule.name:
            name = self.colorize(rule.name, Color.blue)
            description = f"[{name}] {rule.description}"
        else:
            description = rule.description

        if rule.groups:
            groups = self.colorize(", ".join(rule.groups), Color.lightgrey)
            description += f"\ngroups: {groups}"
        if rule.aliases:
            aliases = self.colorize(", ".join(rule.aliases), Color.lightgrey)
            description += f" aliases: {aliases}"
        return description

    def format_rules(self, linter: Linter, verbose: int = 0) -> str:
        """Format the a set of rules given a `Linter`."""
        text_buffer = StringIO()
        text_buffer.write("==== sqlfluff - rules ====\n")
        text_buffer.write(
            self.cli_table(
                [
                    (
                        t.code,
                        self._format_rule_description(t),
                    )
                    for t in linter.rule_tuples()
                ],
                col_width=80,
                cols=1,
                label_color=Color.blue,
                val_align="left",
            )
        )
        return text_buffer.getvalue()

    def format_dialects(self, dialect_readout, verbose=0) -> str:
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
            self.cli_table(
                readouts,
                col_width=60,
                cols=1,
                label_color=Color.blue,
                val_align="right",
            )
        )
        return text_buffer.getvalue()

    def format_dialect_warning(self, dialect) -> str:
        """Output a warning for parsing errors."""
        return self.colorize(
            (
                "WARNING: Parsing errors found and dialect is set to "
                f"'{dialect}'. Have you configured your dialect correctly?"
            ),
            Color.lightgrey,
        )

    def print_out_residual_error_counts(
        self, total_errors: int, num_filtered_errors: int, force_stderr: bool = False
    ) -> None:
        """Output the residual error totals for the file.

        Args:
            total_errors (int): The total number of templating & parsing errors.
            num_filtered_errors (int): The number of templating & parsing errors
                which remain after any noqa and filters applied.
            force_stderr (bool): Whether to force the output onto stderr. By default
                the output is on stdout if there are no errors, otherwise stderr.
        """
        if total_errors:
            click.echo(
                message=self.colorize(
                    f"  [{total_errors} templating/parsing errors found]", Color.red
                ),
                color=self.plain_output,
                err=True,
            )
            if num_filtered_errors < total_errors:
                color = Color.red if num_filtered_errors else Color.green
                click.echo(
                    message=self.colorize(
                        f"  [{num_filtered_errors} templating/parsing errors "
                        f'remaining after "ignore" & "warning"]',
                        color=color,
                    ),
                    color=not self.plain_output,
                    err=force_stderr or num_filtered_errors > 0,
                )

    def print_out_violations_and_timing(
        self,
        output_stream: OutputStream,
        bench: bool,
        code_only: bool,
        total_time: float,
        verbose: int,
        parsed_strings: List[ParsedString],
    ) -> int:
        """Used by human formatting during the parse."""
        violations_count = 0
        timing = TimingSummary()

        for parsed_string in parsed_strings:
            timing.add(parsed_string.time_dict)

            if parsed_string.tree:
                output_stream.write(parsed_string.tree.stringify(code_only=code_only))
            else:
                # TODO: Make this prettier
                output_stream.write("...Failed to Parse...")  # pragma: no cover

            violations_count += len(parsed_string.violations)
            if parsed_string.violations:
                output_stream.write("==== parsing violations ====")  # pragma: no cover
            for v in parsed_string.violations:
                output_stream.write(self.format_violation(v))  # pragma: no cover
            if parsed_string.violations:
                output_stream.write(
                    self.format_dialect_warning(parsed_string.config.get("dialect"))
                )

            if verbose >= 2:
                output_stream.write("==== timings ====")
                output_stream.write(self.cli_table(parsed_string.time_dict.items()))

        if verbose >= 2 or bench:
            output_stream.write("==== overall timings ====")
            output_stream.write(self.cli_table([("Clock time", total_time)]))
            timing_summary = timing.summary()
            for step in timing_summary:
                output_stream.write(f"=== {step} ===")
                output_stream.write(self.cli_table(timing_summary[step].items()))

        return violations_count

    def completion_message(self) -> None:
        """Prints message when SQLFluff is finished."""
        click.echo("All Finished" f"{'' if self.plain_output else ' 📜 🎉'}!")
