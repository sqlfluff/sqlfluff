"""Contains the CLI."""

import json
import logging
import os
import sys
import time
from itertools import chain
from logging import LogRecord
from typing import Callable, Optional, Tuple

import click

# To enable colour cross platform
import colorama
import yaml
from tqdm import tqdm

from sqlfluff.cli import EXIT_ERROR, EXIT_FAIL, EXIT_SUCCESS
from sqlfluff.cli.autocomplete import dialect_shell_complete, shell_completion_enabled
from sqlfluff.cli.formatters import (
    OutputStreamFormatter,
    format_linting_result_header,
)
from sqlfluff.cli.helpers import LazySequence, get_package_version
from sqlfluff.cli.outputstream import OutputStream, make_output_stream

# Import from sqlfluff core.
from sqlfluff.core import (
    FluffConfig,
    Linter,
    SQLFluffUserError,
    SQLLintError,
    SQLTemplaterError,
    dialect_readout,
    dialect_selector,
)
from sqlfluff.core.config import progress_bar_configuration
from sqlfluff.core.enums import Color, FormatType
from sqlfluff.core.linter import LintingResult
from sqlfluff.core.plugin.host import get_plugin_manager


class StreamHandlerTqdm(logging.StreamHandler):
    """Modified StreamHandler which takes care of writing within `tqdm` context.

    It uses `tqdm` write which takes care of conflicting prints with progressbar.
    Without it, there were left artifacts in DEBUG mode (not sure about another ones,
    but probably would happen somewhere).
    """

    def emit(self, record: LogRecord) -> None:
        """Behaves like original one except uses `tqdm` to write."""
        try:
            msg = self.format(record)
            tqdm.write(msg, file=self.stream)
            self.flush()
        except Exception:  # pragma: no cover
            self.handleError(record)


def set_logging_level(
    verbosity: int,
    formatter: OutputStreamFormatter,
    logger: Optional[logging.Logger] = None,
    stderr_output: bool = False,
) -> None:
    """Set up logging for the CLI.

    We either set up global logging based on the verbosity
    or, if `logger` is specified, we only limit to a single
    sqlfluff logger. Verbosity is applied in the same way.

    Implementation: If `logger` is not specified, the handler
    is attached to the `sqlfluff` logger. If it is specified
    then it attaches the the logger in question. In addition
    if `logger` is specified, then that logger will also
    not propagate.
    """
    fluff_logger = logging.getLogger("sqlfluff")
    # Don't propagate logging
    fluff_logger.propagate = False

    # Enable colorama
    colorama.init()

    # Set up the log handler which is able to print messages without overlapping
    # with progressbars.
    handler = StreamHandlerTqdm(stream=sys.stderr if stderr_output else sys.stdout)
    # NB: the unicode character at the beginning is to squash any badly
    # tamed ANSI colour statements, and return us to normality.
    handler.setFormatter(logging.Formatter("\u001b[0m%(levelname)-10s %(message)s"))

    # Set up a handler to colour warnings red.
    # See: https://docs.python.org/3/library/logging.html#filter-objects
    def red_log_filter(record: logging.LogRecord) -> bool:
        if record.levelno >= logging.WARNING:
            record.msg = f"{formatter.colorize(record.msg, Color.red)} "
        return True

    handler.addFilter(red_log_filter)

    if logger:
        focus_logger = logging.getLogger(f"sqlfluff.{logger}")
        focus_logger.addHandler(handler)
    else:
        fluff_logger.addHandler(handler)

    # NB: We treat the parser logger slightly differently because it's noisier.
    # It's important that we set levels for all each time so
    # that we don't break tests by changing the granularity
    # between tests.
    parser_logger = logging.getLogger("sqlfluff.parser")
    if verbosity < 3:
        fluff_logger.setLevel(logging.WARNING)
        parser_logger.setLevel(logging.NOTSET)
    elif verbosity == 3:
        fluff_logger.setLevel(logging.INFO)
        parser_logger.setLevel(logging.WARNING)
    elif verbosity == 4:
        fluff_logger.setLevel(logging.DEBUG)
        parser_logger.setLevel(logging.INFO)
    elif verbosity > 4:
        fluff_logger.setLevel(logging.DEBUG)
        parser_logger.setLevel(logging.DEBUG)


class PathAndUserErrorHandler:
    """Make an API call but with error handling for the CLI."""

    def __init__(self, formatter: OutputStreamFormatter) -> None:
        self.formatter = formatter

    def __enter__(self) -> "PathAndUserErrorHandler":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is SQLFluffUserError:
            click.echo(
                "\nUser Error: "
                + self.formatter.colorize(
                    str(exc_val),
                    Color.red,
                )
            )
            sys.exit(EXIT_ERROR)


def common_options(f: Callable) -> Callable:
    """Add common options to commands via a decorator.

    These are applied to all of the cli commands.
    """
    f = click.version_option()(f)
    f = click.option(
        "-v",
        "--verbose",
        count=True,
        default=None,
        help=(
            "Verbosity, how detailed should the output be. This is *stackable*, so "
            "`-vv` is more verbose than `-v`. For the most verbose option try `-vvvv` "
            "or `-vvvvv`."
        ),
    )(f)
    f = click.option(
        "-n",
        "--nocolor",
        is_flag=True,
        default=None,
        help="No color - output will be without ANSI color codes.",
    )(f)

    return f


def core_options(f: Callable) -> Callable:
    """Add core operation options to commands via a decorator.

    These are applied to the main (but not all) cli commands like
    `parse`, `lint` and `fix`.
    """
    # Only enable dialect completion if on version of click
    # that supports it
    if shell_completion_enabled:
        f = click.option(
            "-d",
            "--dialect",
            default=None,
            help="The dialect of SQL to lint",
            shell_complete=dialect_shell_complete,
        )(f)
    else:  # pragma: no cover
        f = click.option(
            "-d",
            "--dialect",
            default=None,
            help="The dialect of SQL to lint",
        )(f)
    f = click.option(
        "-t",
        "--templater",
        default=None,
        help="The templater to use (default=jinja)",
        type=click.Choice(
            # Use LazySequence so that we don't load templaters until required.
            LazySequence(
                lambda: [
                    templater.name
                    for templater in chain.from_iterable(
                        get_plugin_manager().hook.get_templaters()
                    )
                ]
            )
        ),
    )(f)
    f = click.option(
        "-r",
        "--rules",
        default=None,
        help=(
            "Narrow the search to only specific rules. For example "
            "specifying `--rules LT01` will only search for rule `LT01` (Unnecessary "
            "trailing whitespace). Multiple rules can be specified with commas e.g. "
            "`--rules LT01,LT02` will specify only looking for violations of rule "
            "`LT01` and rule `LT02`."
        ),
    )(f)
    f = click.option(
        "-e",
        "--exclude-rules",
        default=None,
        help=(
            "Exclude specific rules. For example "
            "specifying `--exclude-rules LT01` will remove rule `LT01` (Unnecessary "
            "trailing whitespace) from the set of considered rules. This could either "
            "be the allowlist, or the general set if there is no specific allowlist. "
            "Multiple rules can be specified with commas e.g. "
            "`--exclude-rules LT01,LT02` will exclude violations of rule "
            "`LT01` and rule `LT02`."
        ),
    )(f)
    f = click.option(
        "--config",
        "extra_config_path",
        default=None,
        help=(
            "Include additional config file. By default the config is generated "
            "from the standard configuration files described in the documentation. "
            "This argument allows you to specify an additional configuration file that "
            "overrides the standard configuration files. N.B. cfg format is required."
        ),
        type=click.Path(),
    )(f)
    f = click.option(
        "--ignore-local-config",
        is_flag=True,
        help=(
            "Ignore config files in default search path locations. "
            "This option allows the user to lint with the default config "
            "or can be used in conjunction with --config to only "
            "reference the custom config file."
        ),
    )(f)
    f = click.option(
        "--encoding",
        default=None,
        help=(
            "Specify encoding to use when reading and writing files. Defaults to "
            "autodetect."
        ),
    )(f)
    f = click.option(
        "-i",
        "--ignore",
        default=None,
        help=(
            "Ignore particular families of errors so that they don't cause a failed "
            "run. For example `--ignore parsing` would mean that any parsing errors "
            "are ignored and don't influence the success or fail of a run. "
            "`--ignore` behaves somewhat like `noqa` comments, except it "
            "applies globally. Multiple options are possible if comma separated: "
            "e.g. `--ignore parsing,templating`."
        ),
    )(f)
    f = click.option(
        "--bench",
        is_flag=True,
        help="Set this flag to engage the benchmarking tool output.",
    )(f)
    f = click.option(
        "--logger",
        type=click.Choice(
            ["templater", "lexer", "parser", "linter", "rules", "config"],
            case_sensitive=False,
        ),
        help="Choose to limit the logging to one of the loggers.",
    )(f)
    f = click.option(
        "--disable-noqa",
        is_flag=True,
        default=None,
        help="Set this flag to ignore inline noqa comments.",
    )(f)
    f = click.option(
        "--library-path",
        default=None,
        help=(
            "Override the `library_path` value from the [sqlfluff:templater:jinja]"
            " configuration value. Set this to 'none' to disable entirely."
            " This overrides any values set by users in configuration files or"
            " inline directives."
        ),
    )(f)
    return f


def lint_options(f: Callable) -> Callable:
    """Add lint operation options to commands via a decorator.

    These are cli commands that do linting, i.e. `lint` and `fix`.
    """
    f = click.option(
        "-p",
        "--processes",
        type=int,
        default=None,
        help=(
            "The number of parallel processes to run. Positive numbers work as "
            "expected. Zero and negative numbers will work as number_of_cpus - "
            "number. e.g  -1 means all cpus except one. 0 means all cpus."
        ),
    )(f)
    f = click.option(
        "--disable-progress-bar",
        is_flag=True,
        help="Disables progress bars.",
    )(f)
    f = click.option(
        "--persist-timing",
        default=None,
        help=(
            "A filename to persist the timing information for a linting run to "
            "in csv format for external analysis. NOTE: This feature should be "
            "treated as beta, and the format of the csv file may change in "
            "future releases without warning."
        ),
    )(f)
    f = click.option(
        "--warn-unused-ignores",
        is_flag=True,
        default=False,
        help="Warn about unneeded '-- noqa:' comments.",
    )(f)
    return f


def get_config(
    extra_config_path: Optional[str] = None,
    ignore_local_config: bool = False,
    **kwargs,
) -> FluffConfig:
    """Get a config object from kwargs."""
    plain_output = OutputStreamFormatter.should_produce_plain_output(kwargs["nocolor"])
    if kwargs.get("dialect"):
        try:
            # We're just making sure it exists at this stage.
            # It will be fetched properly in the linter.
            dialect_selector(kwargs["dialect"])
        except SQLFluffUserError as err:
            click.echo(
                OutputStreamFormatter.colorize_helper(
                    plain_output,
                    f"Error loading dialect '{kwargs['dialect']}': {str(err)}",
                    color=Color.red,
                )
            )
            sys.exit(EXIT_ERROR)
        except KeyError:
            click.echo(
                OutputStreamFormatter.colorize_helper(
                    plain_output,
                    f"Error: Unknown dialect '{kwargs['dialect']}'",
                    color=Color.red,
                )
            )
            sys.exit(EXIT_ERROR)

    from_root_kwargs = {}
    if "require_dialect" in kwargs:
        from_root_kwargs["require_dialect"] = kwargs.pop("require_dialect")

    library_path = kwargs.pop("library_path", None)

    if not kwargs.get("warn_unused_ignores", True):
        # If it's present AND True, then keep it, otherwise remove this so
        # that we default to the root config.
        del kwargs["warn_unused_ignores"]

    # Instantiate a config object (filtering out the nulls)
    overrides = {k: kwargs[k] for k in kwargs if kwargs[k] is not None}
    if library_path is not None:
        # Check for a null value
        if library_path.lower() == "none":
            library_path = None  # Set an explicit None value.
        # Set the global override
        overrides["library_path"] = library_path
    try:
        return FluffConfig.from_root(
            extra_config_path=extra_config_path,
            ignore_local_config=ignore_local_config,
            overrides=overrides,
            **from_root_kwargs,
        )
    except SQLFluffUserError as err:  # pragma: no cover
        click.echo(
            OutputStreamFormatter.colorize_helper(
                plain_output,
                f"Error loading config: {str(err)}",
                color=Color.red,
            )
        )
        sys.exit(EXIT_ERROR)


def get_linter_and_formatter(
    cfg: FluffConfig, output_stream: Optional[OutputStream] = None
) -> Tuple[Linter, OutputStreamFormatter]:
    """Get a linter object given a config."""
    try:
        # We're just making sure it exists at this stage.
        # It will be fetched properly in the linter.
        dialect = cfg.get("dialect")
        if dialect:
            dialect_selector(dialect)
    except KeyError:  # pragma: no cover
        click.echo(f"Error: Unknown dialect '{cfg.get('dialect')}'")
        sys.exit(EXIT_ERROR)
    formatter = OutputStreamFormatter(
        output_stream=output_stream or make_output_stream(cfg),
        nocolor=cfg.get("nocolor"),
        verbosity=cfg.get("verbose"),
        output_line_length=cfg.get("output_line_length"),
    )
    return Linter(config=cfg, formatter=formatter), formatter


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="""\b\bExamples:\n
  sqlfluff lint --dialect postgres .\n
  sqlfluff lint --dialect postgres --rules ST05 .\n
  sqlfluff fix --dialect sqlite --rules LT10,ST05 src/queries\n
  sqlfluff parse --dialect sqlite --templater jinja src/queries/common.sql
""",
)
@click.version_option()
def cli() -> None:
    """SQLFluff is a modular SQL linter for humans."""  # noqa D403


@cli.command()
@common_options
def version(**kwargs) -> None:
    """Show the version of sqlfluff."""
    c = get_config(**kwargs, require_dialect=False)
    if c.get("verbose") > 0:
        # Instantiate the linter
        lnt, formatter = get_linter_and_formatter(c)
        # Dispatch the detailed config from the linter.
        formatter.dispatch_config(lnt)
    else:
        # Otherwise just output the package version.
        click.echo(get_package_version(), color=c.get("color"))


@cli.command()
@common_options
def rules(**kwargs) -> None:
    """Show the current rules in use."""
    c = get_config(**kwargs, dialect="ansi")
    lnt, formatter = get_linter_and_formatter(c)
    try:
        click.echo(formatter.format_rules(lnt), color=c.get("color"))
    # No cover for clause covering poorly formatted rules.
    # Without creating a poorly formed plugin, these are hard to
    # test.
    except (SQLFluffUserError, AssertionError) as err:  # pragma: no cover
        click.echo(
            OutputStreamFormatter.colorize_helper(
                c.get("color"),
                f"Error loading rules: {str(err)}",
                color=Color.red,
            )
        )
        sys.exit(EXIT_ERROR)


@cli.command()
@common_options
def dialects(**kwargs) -> None:
    """Show the current dialects available."""
    c = get_config(**kwargs, require_dialect=False)
    _, formatter = get_linter_and_formatter(c)
    click.echo(formatter.format_dialects(dialect_readout), color=c.get("color"))


def dump_file_payload(filename: Optional[str], payload: str) -> None:
    """Write the output file content to stdout or file."""
    # If there's a file specified to write to, write to it.
    if filename:
        with open(filename, "w") as out_file:
            out_file.write(payload)
    # Otherwise write to stdout
    else:
        click.echo(payload)


@cli.command()
@common_options
@core_options
@lint_options
@click.option(
    "-f",
    "--format",
    "format",
    default="human",
    type=click.Choice([ft.value for ft in FormatType], case_sensitive=False),
    help="What format to return the lint result in (default=human).",
)
@click.option(
    "--write-output",
    help=(
        "Optionally provide a filename to write the results to, mostly used in "
        "tandem with --format. NB: Setting an output file re-enables normal "
        "stdout logging."
    ),
)
@click.option(
    "--annotation-level",
    default="warning",
    type=click.Choice(["notice", "warning", "failure", "error"], case_sensitive=False),
    help=(
        'When format is set to "github-annotation" or "github-annotation-native", '
        'default annotation level (default="warning"). "failure" and "error" '
        "are equivalent. Any rules configured only as warnings will always come "
        'through with type "notice" regardless of this option.'
    ),
)
@click.option(
    "--nofail",
    is_flag=True,
    help=(
        "If set, the exit code will always be zero, regardless of violations "
        "found. This is potentially useful during rollout."
    ),
)
@click.option(
    "--disregard-sqlfluffignores",
    is_flag=True,
    help="Perform the operation regardless of .sqlfluffignore configurations",
)
@click.argument("paths", nargs=-1, type=click.Path(allow_dash=True))
def lint(
    paths: Tuple[str],
    format: str,
    write_output: Optional[str],
    annotation_level: str,
    nofail: bool,
    disregard_sqlfluffignores: bool,
    logger: Optional[logging.Logger] = None,
    bench: bool = False,
    processes: Optional[int] = None,
    disable_progress_bar: Optional[bool] = False,
    persist_timing: Optional[str] = None,
    extra_config_path: Optional[str] = None,
    ignore_local_config: bool = False,
    **kwargs,
) -> None:
    """Lint SQL files via passing a list of files or using stdin.

    PATH is the path to a sql file or directory to lint. This can be either a
    file ('path/to/file.sql'), a path ('directory/of/sql/files'), a single ('-')
    character to indicate reading from *stdin* or a dot/blank ('.'/' ') which will
    be interpreted like passing the current working directory as a path argument.

    Linting SQL files:

        sqlfluff lint path/to/file.sql
        sqlfluff lint directory/of/sql/files

    Linting a file via stdin (note the lone '-' character):

        cat path/to/file.sql | sqlfluff lint -
        echo 'select col from tbl' | sqlfluff lint -

    """
    config = get_config(
        extra_config_path, ignore_local_config, require_dialect=False, **kwargs
    )
    non_human_output = (format != FormatType.human.value) or (write_output is not None)
    file_output = None
    output_stream = make_output_stream(config, format, write_output)
    lnt, formatter = get_linter_and_formatter(config, output_stream)

    verbose = config.get("verbose")
    progress_bar_configuration.disable_progress_bar = disable_progress_bar

    formatter.dispatch_config(lnt)

    # Set up logging.
    set_logging_level(
        verbosity=verbose,
        formatter=formatter,
        logger=logger,
        stderr_output=non_human_output,
    )

    # Output the results as we go
    if verbose >= 1 and not non_human_output:
        click.echo(format_linting_result_header())

    with PathAndUserErrorHandler(formatter):
        # add stdin if specified via lone '-'
        if ("-",) == paths:
            result = lnt.lint_string_wrapped(sys.stdin.read(), fname="stdin")
        else:
            result = lnt.lint_paths(
                paths,
                ignore_non_existent_files=False,
                ignore_files=not disregard_sqlfluffignores,
                processes=processes,
                # If we're just linting in the CLI, we don't need to retain the
                # raw file content. This allows us to reduce memory overhead.
                retain_files=False,
            )

    # Output the final stats
    if verbose >= 1 and not non_human_output:
        click.echo(formatter.format_linting_stats(result, verbose=verbose))

    if format == FormatType.json.value:
        file_output = json.dumps(result.as_records())
    elif format == FormatType.yaml.value:
        file_output = yaml.dump(result.as_records(), sort_keys=False)
    elif format == FormatType.none.value:
        file_output = ""
    elif format == FormatType.github_annotation.value:
        if annotation_level == "error":
            annotation_level = "failure"

        github_result = []
        for record in result.as_records():
            filepath = record["filepath"]
            for violation in record["violations"]:
                # NOTE: The output format is designed for this GitHub action:
                # https://github.com/yuzutech/annotations-action
                # It is similar, but not identical, to the native GitHub format:
                # https://docs.github.com/en/rest/reference/checks#annotations-items
                github_result.append(
                    {
                        "file": filepath,
                        "start_line": violation["start_line_no"],
                        "start_column": violation["start_line_pos"],
                        # NOTE: There should always be a start, there _may_ not be an
                        # end, so in that case we default back to just re-using
                        # the start.
                        "end_line": violation.get(
                            "end_line_no", violation["start_line_no"]
                        ),
                        "end_column": violation.get(
                            "end_line_pos", violation["start_line_pos"]
                        ),
                        "title": "SQLFluff",
                        "message": f"{violation['code']}: {violation['description']}",
                        # The annotation_level is configurable, but will only apply
                        # to any SQLFluff rules which have not been downgraded
                        # to warnings using the `warnings` config value. Any which have
                        # been set to warn rather than fail will always be given the
                        # `notice` annotation level in the serialised result.
                        "annotation_level": (
                            annotation_level if not violation["warning"] else "notice"
                        ),
                    }
                )
        file_output = json.dumps(github_result)
    elif format == FormatType.github_annotation_native.value:
        if annotation_level == "failure":
            annotation_level = "error"

        github_result_native = []
        for record in result.as_records():
            filepath = record["filepath"]
            for violation in record["violations"]:
                # NOTE: The output format is designed for GitHub action:
                # https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-a-notice-message

                # The annotation_level is configurable, but will only apply
                # to any SQLFluff rules which have not been downgraded
                # to warnings using the `warnings` config value. Any which have
                # been set to warn rather than fail will always be given the
                # `notice` annotation level in the serialised result.
                line = "::notice " if violation["warning"] else f"::{annotation_level} "

                line += "title=SQLFluff,"
                line += f"file={filepath},"
                line += f"line={violation['start_line_no']},"
                line += f"col={violation['start_line_pos']}"
                if "end_line_no" in violation:
                    line += f",endLine={violation['end_line_no']}"
                if "end_line_pos" in violation:
                    line += f",endColumn={violation['end_line_pos']}"
                line += "::"
                line += f"{violation['code']}: {violation['description']}"
                if violation["name"]:
                    line += f" [{violation['name']}]"

                github_result_native.append(line)

        file_output = "\n".join(github_result_native)

    if file_output:
        dump_file_payload(write_output, file_output)

    if persist_timing:
        result.persist_timing_records(persist_timing)

    output_stream.close()
    if bench:
        click.echo("==== overall timings ====")
        click.echo(formatter.cli_table([("Clock time", result.total_time)]))
        timing_summary = result.timing_summary()
        for step in timing_summary:
            click.echo(f"=== {step} ===")
            click.echo(
                formatter.cli_table(timing_summary[step].items(), cols=3, col_width=20)
            )

    if not nofail:
        if not non_human_output:
            formatter.completion_message()
        sys.exit(result.stats(EXIT_FAIL, EXIT_SUCCESS)["exit code"])
    else:
        sys.exit(EXIT_SUCCESS)


def do_fixes(
    result: LintingResult,
    formatter: Optional[OutputStreamFormatter] = None,
    fixed_file_suffix: str = "",
) -> bool:
    """Actually do the fixes."""
    if formatter and formatter.verbosity >= 0:
        click.echo("Persisting Changes...")
    res = result.persist_changes(
        formatter=formatter, fixed_file_suffix=fixed_file_suffix
    )
    if all(res.values()):
        if formatter and formatter.verbosity >= 0:
            click.echo("Done. Please check your files to confirm.")
        return True
    # If some failed then return false
    click.echo(
        "Done. Some operations failed. Please check your files to confirm."
    )  # pragma: no cover
    click.echo(
        "Some errors cannot be fixed or there is another error blocking it."
    )  # pragma: no cover
    return False  # pragma: no cover


def _handle_unparsable(
    fix_even_unparsable: bool,
    initial_exit_code: int,
    linting_result: LintingResult,
    formatter: OutputStreamFormatter,
):
    """Handles the treatment of files with templating and parsing issues.

    By default, any files with templating or parsing errors shouldn't have
    fixes attempted - because we can't guarantee the validity of the fixes.

    This method returns 1 if there are any files with templating or parse errors after
    filtering, else 0 (Intended as a process exit code). If `fix_even_unparsable` is
    set then it just returns whatever the pre-existing exit code was.

    NOTE: This method mutates the LintingResult so that future use of the object
    has updated violation counts which can be used for other exit code calcs.
    """
    if fix_even_unparsable:
        # If we're fixing even when unparsable, don't perform any filtering.
        return initial_exit_code
    total_errors, num_filtered_errors = linting_result.count_tmp_prs_errors()
    linting_result.discard_fixes_for_lint_errors_in_files_with_tmp_or_prs_errors()
    formatter.print_out_residual_error_counts(
        total_errors, num_filtered_errors, force_stderr=True
    )
    return EXIT_FAIL if num_filtered_errors else EXIT_SUCCESS


def _stdin_fix(
    linter: Linter, formatter: OutputStreamFormatter, fix_even_unparsable: bool
) -> None:
    """Handle fixing from stdin."""
    exit_code = EXIT_SUCCESS
    stdin = sys.stdin.read()

    result = linter.lint_string_wrapped(stdin, fname="stdin", fix=True)
    templater_error = result.num_violations(types=SQLTemplaterError) > 0
    unfixable_error = result.num_violations(types=SQLLintError, fixable=False) > 0

    exit_code = _handle_unparsable(fix_even_unparsable, exit_code, result, formatter)

    if result.num_violations(types=SQLLintError, fixable=True) > 0:
        stdout = result.paths[0].files[0].fix_string()[0]
    else:
        stdout = stdin

    if templater_error:
        click.echo(
            formatter.colorize(
                "Fix aborted due to unparsable template variables.",
                Color.red,
            ),
            err=True,
        )
        click.echo(
            formatter.colorize(
                "Use --FIX-EVEN-UNPARSABLE' to attempt to fix the SQL anyway.",
                Color.red,
            ),
            err=True,
        )

    if unfixable_error:
        click.echo(
            formatter.colorize("Unfixable violations detected.", Color.red),
            err=True,
        )

    click.echo(stdout, nl=False)
    sys.exit(EXIT_FAIL if templater_error or unfixable_error else exit_code)


def _paths_fix(
    linter: Linter,
    formatter: OutputStreamFormatter,
    paths,
    processes,
    fix_even_unparsable,
    fixed_suffix,
    bench,
    show_lint_violations,
    check: bool = False,
    persist_timing: Optional[str] = None,
) -> None:
    """Handle fixing from paths."""
    # Lint the paths (not with the fix argument at this stage), outputting as we go.
    if formatter.verbosity >= 0:
        click.echo("==== finding fixable violations ====")
    exit_code = EXIT_SUCCESS

    with PathAndUserErrorHandler(formatter):
        result: LintingResult = linter.lint_paths(
            paths,
            fix=True,
            ignore_non_existent_files=False,
            processes=processes,
            # If --check is set, then don't apply any fixes until the end.
            apply_fixes=not check,
            fixed_file_suffix=fixed_suffix,
            fix_even_unparsable=fix_even_unparsable,
            # If --check is not set, then don't apply any fixes until the end.
            # NOTE: This should enable us to limit the memory overhead of keeping
            # a large parsed project in memory unless necessary.
            retain_files=check,
        )

    exit_code = _handle_unparsable(fix_even_unparsable, exit_code, result, formatter)

    # NB: We filter to linting violations here, because they're
    # the only ones which can be potentially fixed.
    violation_records = result.as_records()
    num_fixable = sum(
        # Coerce to boolean so that we effectively count the ones which have fixes.
        bool(v.get("fixes", []))
        for rec in violation_records
        for v in rec["violations"]
    )

    if num_fixable > 0:
        if check and formatter.verbosity >= 0:
            click.echo("==== fixing violations ====")

        click.echo(f"{num_fixable} " "fixable linting violations found")

        if check:
            click.echo(
                "Are you sure you wish to attempt to fix these? [Y/n] ", nl=False
            )
            c = click.getchar().lower()
            click.echo("...")
            if c in ("y", "\r", "\n"):
                if formatter.verbosity >= 0:
                    click.echo("Attempting fixes...")
                success = do_fixes(
                    result,
                    formatter,
                    fixed_file_suffix=fixed_suffix,
                )
                if not success:
                    sys.exit(EXIT_FAIL)  # pragma: no cover
                else:
                    formatter.completion_message()
            elif c == "n":
                click.echo("Aborting...")
                exit_code = EXIT_FAIL
            else:  # pragma: no cover
                click.echo("Invalid input, please enter 'Y' or 'N'")
                click.echo("Aborting...")
                exit_code = EXIT_FAIL
    else:
        if formatter.verbosity >= 0:
            click.echo("==== no fixable linting violations found ====")
            formatter.completion_message()

    num_unfixable = sum(p.num_unfixable_lint_errors for p in result.paths)
    if num_unfixable > 0 and formatter.verbosity >= 0:
        click.echo("  [{} unfixable linting violations found]".format(num_unfixable))
        exit_code = max(exit_code, EXIT_FAIL)

    if bench:
        click.echo("==== overall timings ====")
        click.echo(formatter.cli_table([("Clock time", result.total_time)]))
        timing_summary = result.timing_summary()
        for step in timing_summary:
            click.echo(f"=== {step} ===")
            click.echo(
                formatter.cli_table(timing_summary[step].items(), cols=3, col_width=20)
            )

    if show_lint_violations:
        click.echo("==== lint for unfixable violations ====")
        for record in result.as_records():
            # Non fixable linting errors _have_ a `fixes` value, but it's an empty list.
            non_fixable = [
                v for v in record["violations"] if v.get("fixes", None) == []
            ]
            click.echo(
                formatter.format_filename(record["filepath"], success=(not non_fixable))
            )
            for violation in non_fixable:
                click.echo(formatter.format_violation(violation))

    if persist_timing:
        result.persist_timing_records(persist_timing)

    sys.exit(exit_code)


@cli.command()
@common_options
@core_options
@lint_options
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help=(
        "[DEPRECATED - From 3.0 onward this is the default behaviour] "
        "Apply fixes will also be applied file by file, during the "
        "linting process, rather than waiting until all files are "
        "linted before fixing."
    ),
)
@click.option(
    "--check",
    is_flag=True,
    help=(
        "Analyse all files and ask for confirmation before applying "
        "any fixes. Fixes will be applied all together at the end of "
        "the operation."
    ),
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help=(
        "Reduces the amount of output to stdout to a minimal level. "
        "This is effectively the opposite of -v. NOTE: It will only "
        "take effect if -f/--force is also set."
    ),
)
@click.option(
    "-x",
    "--fixed-suffix",
    default=None,
    help="An optional suffix to add to fixed files.",
)
@click.option(
    "--FIX-EVEN-UNPARSABLE",
    is_flag=True,
    default=None,
    help=(
        "Enables fixing of files that have templating or parse errors. "
        "Note that the similar-sounding '--ignore' or 'noqa' features merely "
        "prevent errors from being *displayed*. For safety reasons, the 'fix'"
        "command will not make any fixes in files that have templating or parse "
        "errors unless '--FIX-EVEN-UNPARSABLE' is enabled on the command line"
        "or in the .sqlfluff config file."
    ),
)
@click.option(
    "--show-lint-violations",
    is_flag=True,
    help="Show lint violations",
)
@click.argument("paths", nargs=-1, type=click.Path(allow_dash=True))
def fix(
    force: bool,
    paths: Tuple[str],
    check: bool = False,
    bench: bool = False,
    quiet: bool = False,
    fixed_suffix: str = "",
    logger: Optional[logging.Logger] = None,
    processes: Optional[int] = None,
    disable_progress_bar: Optional[bool] = False,
    persist_timing: Optional[str] = None,
    extra_config_path: Optional[str] = None,
    ignore_local_config: bool = False,
    show_lint_violations: bool = False,
    **kwargs,
) -> None:
    """Fix SQL files.

    PATH is the path to a sql file or directory to lint. This can be either a
    file ('path/to/file.sql'), a path ('directory/of/sql/files'), a single ('-')
    character to indicate reading from *stdin* or a dot/blank ('.'/' ') which will
    be interpreted like passing the current working directory as a path argument.
    """
    # some quick checks
    fixing_stdin = ("-",) == paths
    if quiet:
        if kwargs["verbose"]:
            click.echo(
                "ERROR: The --quiet flag can only be used if --verbose is not set.",
            )
            sys.exit(EXIT_ERROR)
        kwargs["verbose"] = -1

    config = get_config(
        extra_config_path, ignore_local_config, require_dialect=False, **kwargs
    )
    fix_even_unparsable = config.get("fix_even_unparsable")
    output_stream = make_output_stream(
        config, None, os.devnull if fixing_stdin else None
    )
    lnt, formatter = get_linter_and_formatter(config, output_stream)

    verbose = config.get("verbose")
    progress_bar_configuration.disable_progress_bar = disable_progress_bar

    formatter.dispatch_config(lnt)

    # Set up logging.
    set_logging_level(
        verbosity=verbose,
        formatter=formatter,
        logger=logger,
        stderr_output=fixing_stdin,
    )

    if force:
        click.echo(
            formatter.colorize(
                "The -f/--force option is deprecated as it is now the "
                "default behaviour.",
                Color.red,
            )
        )

    # handle stdin case. should output formatted sql to stdout and nothing else.
    if fixing_stdin:
        _stdin_fix(lnt, formatter, fix_even_unparsable)
    else:
        _paths_fix(
            lnt,
            formatter,
            paths,
            processes,
            fix_even_unparsable,
            fixed_suffix,
            bench,
            show_lint_violations,
            check=check,
            persist_timing=persist_timing,
        )


@cli.command(name="format")
@common_options
@core_options
@lint_options
@click.option(
    "-x",
    "--fixed-suffix",
    default=None,
    help="An optional suffix to add to fixed files.",
)
@click.argument("paths", nargs=-1, type=click.Path(allow_dash=True))
def cli_format(
    paths: Tuple[str],
    bench: bool = False,
    fixed_suffix: str = "",
    logger: Optional[logging.Logger] = None,
    processes: Optional[int] = None,
    disable_progress_bar: Optional[bool] = False,
    persist_timing: Optional[str] = None,
    extra_config_path: Optional[str] = None,
    ignore_local_config: bool = False,
    **kwargs,
) -> None:
    """Autoformat SQL files.

    This effectively force applies `sqlfluff fix` with a known subset of fairly
    stable rules. Enabled rules are ignored, but rule exclusions (via CLI) or
    config are still respected.

    PATH is the path to a sql file or directory to lint. This can be either a
    file ('path/to/file.sql'), a path ('directory/of/sql/files'), a single ('-')
    character to indicate reading from *stdin* or a dot/blank ('.'/' ') which will
    be interpreted like passing the current working directory as a path argument.
    """
    # some quick checks
    fixing_stdin = ("-",) == paths

    if kwargs.get("rules"):
        click.echo(
            "Specifying rules is not supported for sqlfluff format.",
        )
        sys.exit(EXIT_ERROR)

    # Override rules for sqlfluff format
    kwargs["rules"] = (
        # All of the capitalisation rules
        "capitalisation,"
        # All of the layout rules
        "layout,"
        # Safe rules from other groups
        "ambiguous.union,"
        "convention.not_equal,"
        "convention.coalesce,"
        "convention.select_trailing_comma,"
        "convention.is_null,"
        "jinja.padding,"
        "structure.distinct,"
    )

    config = get_config(
        extra_config_path, ignore_local_config, require_dialect=False, **kwargs
    )
    output_stream = make_output_stream(
        config, None, os.devnull if fixing_stdin else None
    )
    lnt, formatter = get_linter_and_formatter(config, output_stream)

    verbose = config.get("verbose")
    progress_bar_configuration.disable_progress_bar = disable_progress_bar

    formatter.dispatch_config(lnt)

    # Set up logging.
    set_logging_level(
        verbosity=verbose,
        formatter=formatter,
        logger=logger,
        stderr_output=fixing_stdin,
    )

    # handle stdin case. should output formatted sql to stdout and nothing else.
    if fixing_stdin:
        _stdin_fix(lnt, formatter, fix_even_unparsable=False)
    else:
        _paths_fix(
            lnt,
            formatter,
            paths,
            processes,
            fix_even_unparsable=False,
            fixed_suffix=fixed_suffix,
            bench=bench,
            show_lint_violations=False,
            persist_timing=persist_timing,
        )


def quoted_presenter(dumper, data):
    """Re-presenter which always double quotes string values needing escapes."""
    if "\n" in data or "\t" in data or "'" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
    else:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="")


@cli.command()
@common_options
@core_options
@click.argument("path", nargs=1, type=click.Path(allow_dash=True))
@click.option(
    "-c",
    "--code-only",
    is_flag=True,
    help="Output only the code elements of the parse tree.",
)
@click.option(
    "-m",
    "--include-meta",
    is_flag=True,
    help=(
        "Include meta segments (indents, dedents and placeholders) in the output. "
        "This only applies when outputting json or yaml."
    ),
)
@click.option(
    "-f",
    "--format",
    default=FormatType.human.value,
    type=click.Choice(
        [
            FormatType.human.value,
            FormatType.json.value,
            FormatType.yaml.value,
            FormatType.none.value,
        ],
        case_sensitive=False,
    ),
    help="What format to return the parse result in.",
)
@click.option(
    "--write-output",
    help=(
        "Optionally provide a filename to write the results to, mostly used in "
        "tandem with --format. NB: Setting an output file re-enables normal "
        "stdout logging."
    ),
)
@click.option(
    "--parse-statistics",
    is_flag=True,
    help=(
        "Set this flag to enabled detailed debugging readout "
        "on the use of terminators in the parser."
    ),
)
@click.option(
    "--nofail",
    is_flag=True,
    help=(
        "If set, the exit code will always be zero, regardless of violations "
        "found. This is potentially useful during rollout."
    ),
)
def parse(
    path: str,
    code_only: bool,
    include_meta: bool,
    format: str,
    write_output: Optional[str],
    bench: bool,
    nofail: bool,
    logger: Optional[logging.Logger] = None,
    extra_config_path: Optional[str] = None,
    ignore_local_config: bool = False,
    parse_statistics: bool = False,
    **kwargs,
) -> None:
    """Parse SQL files and just spit out the result.

    PATH is the path to a sql file or directory to lint. This can be either a
    file ('path/to/file.sql'), a path ('directory/of/sql/files'), a single ('-')
    character to indicate reading from *stdin* or a dot/blank ('.'/' ') which will
    be interpreted like passing the current working directory as a path argument.
    """
    c = get_config(
        extra_config_path, ignore_local_config, require_dialect=False, **kwargs
    )
    # We don't want anything else to be logged if we want json or yaml output
    # unless we're writing to a file.
    non_human_output = (format != FormatType.human.value) or (write_output is not None)
    output_stream = make_output_stream(c, format, write_output)
    lnt, formatter = get_linter_and_formatter(c, output_stream)
    verbose = c.get("verbose")

    progress_bar_configuration.disable_progress_bar = True

    formatter.dispatch_config(lnt)

    # Set up logging.
    set_logging_level(
        verbosity=verbose,
        formatter=formatter,
        logger=logger,
        stderr_output=non_human_output,
    )

    t0 = time.monotonic()

    # handle stdin if specified via lone '-'
    with PathAndUserErrorHandler(formatter):
        if "-" == path:
            parsed_strings = [
                lnt.parse_string(
                    sys.stdin.read(),
                    "stdin",
                    config=lnt.config,
                    parse_statistics=parse_statistics,
                ),
            ]
        else:
            # A single path must be specified for this command
            parsed_strings = list(
                lnt.parse_path(
                    path=path,
                    parse_statistics=parse_statistics,
                )
            )

    total_time = time.monotonic() - t0
    violations_count = 0

    # iterative print for human readout
    if format == FormatType.human.value:
        violations_count = formatter.print_out_violations_and_timing(
            output_stream, bench, code_only, total_time, verbose, parsed_strings
        )
    else:
        parsed_strings_dict = [
            dict(
                filepath=linted_result.fname,
                segments=(
                    linted_result.tree.as_record(
                        code_only=code_only, show_raw=True, include_meta=include_meta
                    )
                    if linted_result.tree
                    else None
                ),
            )
            for linted_result in parsed_strings
        ]

        if format == FormatType.yaml.value:
            # For yaml dumping always dump double quoted strings if they contain
            # tabs or newlines.
            yaml.add_representer(str, quoted_presenter)
            file_output = yaml.dump(parsed_strings_dict, sort_keys=False)
        elif format == FormatType.json.value:
            file_output = json.dumps(parsed_strings_dict)
        elif format == FormatType.none.value:
            file_output = ""

        # Dump the output to stdout or to file as appropriate.
        dump_file_payload(write_output, file_output)

    if violations_count > 0 and not nofail:
        sys.exit(EXIT_FAIL)  # pragma: no cover
    else:
        sys.exit(EXIT_SUCCESS)


@cli.command()
@common_options
@core_options
@click.argument("path", nargs=1, type=click.Path(allow_dash=True))
def render(
    path: str,
    bench: bool,
    logger: Optional[logging.Logger] = None,
    extra_config_path: Optional[str] = None,
    ignore_local_config: bool = False,
    **kwargs,
) -> None:
    """Render SQL files and just spit out the result.

    PATH is the path to a sql file. This should be either a single file
    file ('path/to/file.sql') or a single ('-') character to indicate reading
    from *stdin*.
    """
    c = get_config(
        extra_config_path, ignore_local_config, require_dialect=False, **kwargs
    )
    # We don't want anything else to be logged if we want json or yaml output
    # unless we're writing to a file.
    output_stream = make_output_stream(c, None, None)
    lnt, formatter = get_linter_and_formatter(c, output_stream)
    verbose = c.get("verbose")

    progress_bar_configuration.disable_progress_bar = True

    formatter.dispatch_config(lnt)

    # Set up logging.
    set_logging_level(
        verbosity=verbose,
        formatter=formatter,
        logger=logger,
        stderr_output=False,
    )

    # handle stdin if specified via lone '-'
    with PathAndUserErrorHandler(formatter):
        if "-" == path:
            raw_sql = sys.stdin.read()
            fname = "stdin"
            file_config = lnt.config
        else:
            raw_sql, file_config, _ = lnt.load_raw_file_and_config(path, lnt.config)
            fname = path

    # Get file specific config
    file_config.process_raw_file_for_config(raw_sql, fname)
    rendered = lnt.render_string(raw_sql, fname, file_config, "utf8")

    if rendered.templater_violations:
        for v in rendered.templater_violations:
            click.echo(formatter.format_violation(v))
        sys.exit(EXIT_FAIL)
    else:
        click.echo(rendered.templated_file.templated_str)
        sys.exit(EXIT_SUCCESS)


# This "__main__" handler allows invoking SQLFluff using "python -m", which
# simplifies the use of cProfile, e.g.:
# python -m cProfile -s cumtime -m sqlfluff.cli.commands lint slow_file.sql
if __name__ == "__main__":
    cli.main(sys.argv[1:])  # pragma: no cover
