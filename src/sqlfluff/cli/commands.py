"""Contains the CLI."""

import sys
import json
import logging

import oyaml as yaml

import click

# For the profiler
import pstats
from io import StringIO
from benchit import BenchIt

# To enable colour cross platform
import colorama

from sqlfluff.cli.formatters import (
    format_rules,
    format_violation,
    format_linting_result_header,
    format_linting_stats,
    colorize,
    format_dialect_warning,
    format_dialects,
    CallbackFormatter,
)
from sqlfluff.cli.helpers import cli_table, get_package_version

# Import from sqlfluff core.
from sqlfluff.core import (
    Linter,
    FluffConfig,
    SQLLintError,
    dialect_selector,
    dialect_readout,
)


class RedWarningsFilter(logging.Filter):
    """This filter makes all warnings or above red."""

    def filter(self, record):
        """Filter any warnings (or above) to turn them red."""
        if record.levelno >= logging.WARNING:
            record.msg = colorize(record.msg, "red") + " "
        return True


def set_logging_level(verbosity, logger=None):
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

    # Set up the log handler to log to stdout
    handler = logging.StreamHandler(stream=sys.stdout)
    # NB: the unicode character at the beginning is to squash any badly
    # tamed ANSI colour statements, and return us to normality.
    handler.setFormatter(logging.Formatter("\u001b[0m%(levelname)-10s %(message)s"))
    # Set up a handler to colour warnings red.
    handler.addFilter(RedWarningsFilter())
    if logger:
        focus_logger = logging.getLogger("sqlfluff.{0}".format(logger))
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


def common_options(f):
    """Add common options to commands via a decorator.

    These are applied to all of the cli commands.
    """
    f = click.version_option()(f)
    f = click.option(
        "-v",
        "--verbose",
        count=True,
        help=(
            "Verbosity, how detailed should the output be. This is *stackable*, so `-vv`"
            " is more verbose than `-v`. For the most verbose option try `-vvvv` or `-vvvvv`."
        ),
    )(f)
    f = click.option(
        "-n",
        "--nocolor",
        is_flag=True,
        help="No color - if this is set then the output will be without ANSI color codes.",
    )(f)
    return f


def core_options(f):
    """Add core operation options to commands via a decorator.

    These are applied to the main (but not all) cli commands like
    `parse`, `lint` and `fix`.
    """
    f = click.option(
        "--dialect", default=None, help="The dialect of SQL to lint (default=ansi)"
    )(f)
    f = click.option(
        "--templater", default=None, help="The templater to use (default=jinja)"
    )(f)
    f = click.option(
        "--rules",
        default=None,
        # short_help='Specify a particular rule, or comma separated rules, to check',
        help=(
            "Narrow the search to only specific rules. For example "
            "specifying `--rules L001` will only search for rule `L001` (Unnecessary "
            "trailing whitespace). Multiple rules can be specified with commas e.g. "
            "`--rules L001,L002` will specify only looking for violations of rule "
            "`L001` and rule `L002`."
        ),
    )(f)
    f = click.option(
        "--exclude-rules",
        default=None,
        # short_help='Specify a particular rule, or comma separated rules to exclude',
        help=(
            "Exclude specific rules. For example "
            "specifying `--exclude-rules L001` will remove rule `L001` (Unnecessary "
            "trailing whitespace) from the set of considered rules. This could either "
            "be the whitelist, or the general set if there is no specific whitelist. "
            "Multiple rules can be specified with commas e.g. "
            "`--exclude-rules L001,L002` will exclude violations of rule "
            "`L001` and rule `L002`."
        ),
    )(f)
    f = click.option(
        "--ignore",
        default=None,
        help=(
            "Ignore particular families of errors so that they don't cause a failed "
            "run. For example `--ignore parsing` would mean that any parsing errors "
            "are ignored and don't influence the success or fail of a run. Multiple "
            "options are possible if comma separated e.g. `--ignore parsing,templating`."
        ),
    )(f)
    f = click.option(
        "--bench",
        is_flag=True,
        help="Set this flag to engage the benchmarking tool output.",
    )(f)
    f = click.option(
        "--logger",
        type=click.Choice(["parser", "linter", "rules"], case_sensitive=False),
        help="Choose to limit the logging to one of the loggers.",
    )(f)
    return f


def get_config(**kwargs):
    """Get a config object from kwargs."""
    if kwargs.get("dialect", None):
        try:
            # We're just making sure it exists at this stage - it will be fetched properly in the linter
            dialect_selector(kwargs["dialect"])
        except KeyError:
            click.echo("Error: Unknown dialect {0!r}".format(kwargs["dialect"]))
            sys.exit(66)
    # Instantiate a config object (filtering out the nulls)
    overrides = {k: kwargs[k] for k in kwargs if kwargs[k] is not None}
    return FluffConfig.from_root(overrides=overrides)


def get_linter_and_formatter(cfg, silent=False):
    """Get a linter object given a config."""
    try:
        # We're just making sure it exists at this stage - it will be fetched properly in the linter
        dialect_selector(cfg.get("dialect"))
    except KeyError:
        click.echo("Error: Unknown dialect {0!r}".format(cfg.get("dialect")))
        sys.exit(66)

    if not silent:
        # Instantiate the linter and return (with an output function)
        formatter = CallbackFormatter(
            callback=lambda m: click.echo(m, color=cfg.get("color")),
            verbosity=cfg.get("verbose"),
            output_line_length=cfg.get("output_line_length"),
        )
        return Linter(config=cfg, formatter=formatter), formatter
    else:
        # Instantiate the linter and return. NB: No formatter
        # in the Linter and a black formatter otherwise.
        formatter = CallbackFormatter(callback=lambda m: None, verbosity=0)
        return Linter(config=cfg), formatter


@click.group()
@click.version_option()
def cli():
    """Sqlfluff is a modular sql linter for humans."""


@cli.command()
@common_options
def version(**kwargs):
    """Show the version of sqlfluff."""
    c = get_config(**kwargs)
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
def rules(**kwargs):
    """Show the current rules in use."""
    c = get_config(**kwargs)
    lnt, _ = get_linter_and_formatter(c)
    click.echo(format_rules(lnt), color=c.get("color"))


@cli.command()
@common_options
def dialects(**kwargs):
    """Show the current dialects available."""
    c = get_config(**kwargs)
    click.echo(format_dialects(dialect_readout), color=c.get("color"))


@cli.command()
@common_options
@core_options
@click.option(
    "-f",
    "--format",
    "format",
    default="human",
    type=click.Choice(["human", "json", "yaml"], case_sensitive=False),
    help="What format to return the lint result in.",
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
    help=("Perform the operation regardless of .sqlfluffignore configurations"),
)
@click.argument("paths", nargs=-1)
def lint(paths, format, nofail, disregard_sqlfluffignores, logger=None, **kwargs):
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
    c = get_config(**kwargs)
    lnt, formatter = get_linter_and_formatter(c, silent=format in ("json", "yaml"))
    verbose = c.get("verbose")

    formatter.dispatch_config(lnt)

    # Set up logging.
    set_logging_level(verbosity=verbose, logger=logger)
    # add stdin if specified via lone '-'
    if ("-",) == paths:
        # TODO: Remove verbose
        result = lnt.lint_string_wrapped(sys.stdin.read(), fname="stdin")
    else:
        # Output the results as we go
        if verbose >= 1:
            click.echo(format_linting_result_header())
        try:
            # TODO: Remove verbose
            result = lnt.lint_paths(
                paths,
                ignore_non_existent_files=False,
                ignore_files=not disregard_sqlfluffignores,
            )
        except IOError:
            click.echo(
                colorize(
                    "The path(s) {0!r} could not be accessed. Check it/they exist(s).".format(
                        paths
                    ),
                    "red",
                )
            )
            sys.exit(1)
        # Output the final stats
        if verbose >= 1:
            click.echo(format_linting_stats(result, verbose=verbose))

    if format == "json":
        click.echo(json.dumps(result.as_records()))
    elif format == "yaml":
        click.echo(yaml.dump(result.as_records()))

    if not nofail:
        sys.exit(result.stats()["exit code"])
    else:
        sys.exit(0)


def do_fixes(lnt, result, formatter=None, **kwargs):
    """Actually do the fixes."""
    click.echo("Persisting Changes...")
    res = result.persist_changes(formatter=formatter, **kwargs)
    if all(res.values()):
        click.echo("Done. Please check your files to confirm.")
        return True
    # If some failed then return false
    click.echo("Done. Some operations failed. Please check your files to confirm.")
    click.echo("Some errors cannot be fixed or there is another error blocking it.")
    return False


@cli.command()
@common_options
@core_options
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help=(
        "skip the confirmation prompt and go straight to applying "
        "fixes. **Use this with caution.**"
    ),
)
@click.option(
    "--fixed-suffix", default=None, help="An optional suffix to add to fixed files."
)
@click.argument("paths", nargs=-1)
def fix(force, paths, bench=False, fixed_suffix="", logger=None, **kwargs):
    """Fix SQL files.

    PATH is the path to a sql file or directory to lint. This can be either a
    file ('path/to/file.sql'), a path ('directory/of/sql/files'), a single ('-')
    character to indicate reading from *stdin* or a dot/blank ('.'/' ') which will
    be interpreted like passing the current working directory as a path argument.
    """
    # some quick checks
    fixing_stdin = ("-",) == paths

    c = get_config(**kwargs)
    lnt, formatter = get_linter_and_formatter(c, silent=fixing_stdin)
    verbose = c.get("verbose")

    bencher = BenchIt()

    formatter.dispatch_config(lnt)

    # Set up logging.
    set_logging_level(verbosity=verbose, logger=logger)

    # handle stdin case. should output formatted sql to stdout and nothing else.
    if fixing_stdin:
        stdin = sys.stdin.read()
        # TODO: Remove verbose
        result = lnt.lint_string_wrapped(stdin, fname="stdin", fix=True)
        stdout = result.paths[0].files[0].fix_string()[0]
        click.echo(stdout, nl=False)
        sys.exit()

    # Lint the paths (not with the fix argument at this stage), outputting as we go.
    click.echo("==== finding fixable violations ====")
    try:
        result = lnt.lint_paths(paths, fix=True, ignore_non_existent_files=False)
    except IOError:
        click.echo(
            colorize(
                "The path(s) {0!r} could not be accessed. Check it/they exist(s).".format(
                    paths
                ),
                "red",
            )
        )
        sys.exit(1)

    # NB: We filter to linting violations here, because they're
    # the only ones which can be potentially fixed.
    if result.num_violations(types=SQLLintError, fixable=True) > 0:
        click.echo("==== fixing violations ====")
        click.echo(
            "{0} fixable linting violations found".format(
                result.num_violations(types=SQLLintError, fixable=True)
            )
        )
        if force:
            click.echo(colorize("FORCE MODE", "red") + ": Attempting fixes...")
            # TODO: Remove verbose
            success = do_fixes(
                lnt,
                result,
                formatter,
                types=SQLLintError,
                fixed_file_suffix=fixed_suffix,
            )
            if not success:
                sys.exit(1)
        else:
            click.echo(
                "Are you sure you wish to attempt to fix these? [Y/n] ", nl=False
            )
            c = click.getchar().lower()
            click.echo("...")
            if c in ("y", "\r", "\n"):
                click.echo("Attempting fixes...")
                # TODO: Remove verbose
                success = do_fixes(
                    lnt,
                    result,
                    formatter,
                    types=SQLLintError,
                    fixed_file_suffix=fixed_suffix,
                )
                if not success:
                    sys.exit(1)
            elif c == "n":
                click.echo("Aborting...")
            else:
                click.echo("Invalid input, please enter 'Y' or 'N'")
                click.echo("Aborting...")
    else:
        click.echo("==== no fixable linting violations found ====")
        if result.num_violations(types=SQLLintError, fixable=False) > 0:
            click.echo(
                "  [{0} unfixable linting violations found]".format(
                    result.num_violations(types=SQLLintError, fixable=False)
                )
            )

    if bench:
        click.echo("\n\n==== bencher stats ====")
        bencher.display()

    sys.exit(0)


def quoted_presenter(dumper, data):
    """Re-presenter which always double quotes string values needing escapes."""
    if "\n" in data or "\t" in data or "'" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
    else:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="")


@cli.command()
@common_options
@core_options
@click.argument("path", nargs=1)
@click.option(
    "--recurse", default=0, help="The depth to recursively parse to (0 for unlimited)"
)
@click.option(
    "-c",
    "--code-only",
    is_flag=True,
    help="Output only the code elements of the parse tree.",
)
@click.option(
    "-f",
    "--format",
    default="human",
    type=click.Choice(["human", "json", "yaml"], case_sensitive=False),
    help="What format to return the parse result in.",
)
@click.option(
    "--profiler", is_flag=True, help="Set this flag to engage the python profiler."
)
@click.option(
    "--nofail",
    is_flag=True,
    help=(
        "If set, the exit code will always be zero, regardless of violations "
        "found. This is potentially useful during rollout."
    ),
)
def parse(path, code_only, format, profiler, bench, nofail, logger=None, **kwargs):
    """Parse SQL files and just spit out the result.

    PATH is the path to a sql file or directory to lint. This can be either a
    file ('path/to/file.sql'), a path ('directory/of/sql/files'), a single ('-')
    character to indicate reading from *stdin* or a dot/blank ('.'/' ') which will
    be interpreted like passing the current working directory as a path argument.
    """
    # Initialise the benchmarker
    bencher = BenchIt()  # starts the timer
    c = get_config(**kwargs)
    # We don't want anything else to be logged if we want a yaml output
    lnt, formatter = get_linter_and_formatter(c, silent=format in ("json", "yaml"))
    verbose = c.get("verbose")
    recurse = c.get("recurse")

    formatter.dispatch_config(lnt)

    # Set up logging.
    set_logging_level(verbosity=verbose, logger=logger)

    # TODO: do this better
    nv = 0
    if profiler:
        # Set up the profiler if required
        try:
            import cProfile
        except ImportError:
            click.echo("The cProfiler is not available on your platform.")
            sys.exit(1)
        pr = cProfile.Profile()
        pr.enable()

    bencher("Parse setup")
    try:
        # handle stdin if specified via lone '-'
        if "-" == path:
            # put the parser result in a list to iterate later
            result = [
                lnt.parse_string(
                    sys.stdin.read(), "stdin", recurse=recurse, config=lnt.config
                ),
            ]
        else:
            # A single path must be specified for this command
            # TODO: Remove verbose
            result = lnt.parse_path(path, recurse=recurse)

        # iterative print for human readout
        if format == "human":
            for parsed_string in result:
                if parsed_string.tree:
                    click.echo(parsed_string.tree.stringify(code_only=code_only))
                else:
                    # TODO: Make this prettier
                    click.echo("...Failed to Parse...")
                nv += len(parsed_string.violations)
                if parsed_string.violations:
                    click.echo("==== parsing violations ====")
                for v in parsed_string.violations:
                    click.echo(format_violation(v))
                if (
                    parsed_string.violations
                    and parsed_string.config.get("dialect") == "ansi"
                ):
                    click.echo(format_dialect_warning())
                if verbose >= 2:
                    click.echo("==== timings ====")
                    click.echo(cli_table(parsed_string.time_dict.items()))
                bencher("Output details for file")
        else:
            # collect result and print as single payload
            # will need to zip in the file paths
            filepaths = ["stdin"] if "-" == path else lnt.paths_from_path(path)
            result = [
                dict(
                    filepath=filepath,
                    segments=parsed.as_record(code_only=code_only, show_raw=True)
                    if parsed
                    else None,
                )
                for filepath, (parsed, _, _, _, _) in zip(filepaths, result)
            ]

            if format == "yaml":
                # For yaml dumping always dump double quoted strings if they contain tabs or newlines.
                yaml.add_representer(str, quoted_presenter)

                click.echo(yaml.dump(result))
            elif format == "json":
                click.echo(json.dumps(result))
    except IOError:
        click.echo(
            colorize(
                "The path {0!r} could not be accessed. Check it exists.".format(path),
                "red",
            )
        )
        sys.exit(1)

    if profiler:
        pr.disable()
        profiler_buffer = StringIO()
        ps = pstats.Stats(pr, stream=profiler_buffer).sort_stats("cumulative")
        ps.print_stats()
        click.echo("==== profiler stats ====")
        # Only print the first 50 lines of it
        click.echo("\n".join(profiler_buffer.getvalue().split("\n")[:50]))

    if bench:
        click.echo("\n\n==== bencher stats ====")
        bencher.display()

    if nv > 0 and not nofail:
        sys.exit(66)
    else:
        sys.exit(0)
