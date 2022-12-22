"""Defines the dbt templater (aka 'sqlfluff-templater-dbt' package).

Parts of this file are based on dbt-osmosis' dbt templater.
(https://github.com/z3z1ma/dbt-osmosis/blob/main/src/dbt_osmosis/dbt_templater/templater.py)
That project uses the Apache 2.0 license: https://www.apache.org/licenses/LICENSE-2.0
"""
import logging
import os.path
from pathlib import Path
from typing import Iterator, List, Optional

from dbt.clients import jinja
from dbt.exceptions import (
    RuntimeException as DbtRuntimeException,
)
from dbt.flags import PROFILES_DIR
from dbt.version import get_installed_version
from jinja2_simple_tags import StandaloneTag

from sqlfluff.cli.formatters import OutputStreamFormatter
from sqlfluff.core import FluffConfig
from sqlfluff.core.errors import SQLTemplaterError, SQLFluffSkipFile
from sqlfluff.core.templaters.base import TemplatedFile, large_file_check
from sqlfluff.core.templaters.jinja import JinjaTemplater

from sqlfluff_templater_dbt.osmosis import DbtProjectContainer

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")

DBT_VERSION = get_installed_version()
DBT_VERSION_STRING = DBT_VERSION.to_version_string()
DBT_VERSION_TUPLE = (int(DBT_VERSION.major), int(DBT_VERSION.minor))

COMPILED_SQL_ATTRIBUTE = (
    "compiled_code" if DBT_VERSION_TUPLE >= (1, 3) else "compiled_sql"
)
RAW_SQL_ATTRIBUTE = "raw_code" if DBT_VERSION_TUPLE >= (1, 3) else "raw_sql"


class DbtTemplater(JinjaTemplater):
    """A templater using dbt."""

    name = "dbt"
    sequential_fail_limit = 3

    def __init__(self, **kwargs):
        self.sqlfluff_config = None
        self.formatter = None
        self.project_dir = None
        self.profiles_dir = None
        self._sequential_fails = 0
        self.dbt_project_container: DbtProjectContainer = kwargs.pop(
            "dbt_project_container"
        )
        super().__init__(**kwargs)

    def _get_profiles_dir(self):
        """Get the dbt profiles directory from the configuration.

        The default is `~/.dbt` in 0.17 but we use the
        PROFILES_DIR variable from the dbt library to
        support a change of default in the future, as well
        as to support the same overwriting mechanism as
        dbt (currently an environment variable).
        """
        dbt_profiles_dir = os.path.abspath(
            os.path.expanduser(
                self.sqlfluff_config.get_section(
                    (self.templater_selector, self.name, "profiles_dir")
                )
                or PROFILES_DIR
            )
        )

        if not os.path.exists(dbt_profiles_dir):
            templater_logger.error(
                f"dbt_profiles_dir: {dbt_profiles_dir} could not be accessed. "
                "Check it exists."
            )

        return dbt_profiles_dir

    def _get_project_dir(self):
        """Get the dbt project directory from the configuration.

        Defaults to the working directory.
        """
        dbt_project_dir = os.path.abspath(
            os.path.expanduser(
                self.sqlfluff_config.get_section(
                    (self.templater_selector, self.name, "project_dir")
                )
                or os.getcwd()
            )
        )
        if not os.path.exists(dbt_project_dir):
            templater_logger.error(
                f"dbt_project_dir: {dbt_project_dir} could not be accessed. "
                "Check it exists."
            )

        return dbt_project_dir

    def _get_profile(self):
        """Get a dbt profile name from the configuration."""
        return self.sqlfluff_config.get_section(
            (self.templater_selector, self.name, "profile")
        )

    def _get_target(self):
        """Get a dbt target name from the configuration."""
        return self.sqlfluff_config.get_section(
            (self.templater_selector, self.name, "target")
        )

    def _get_cli_vars(self) -> str:
        cli_vars = self.sqlfluff_config.get_section(
            (self.templater_selector, self.name, "context")
        )

        return str(cli_vars) if cli_vars else "{}"

    def sequence_files(
        self, fnames: List[str], config=None, formatter=None
    ) -> Iterator[str]:
        """Reorder fnames to process dependent files first.

        This avoids errors when an ephemeral model is processed before use.
        """
        if formatter:  # pragma: no cover
            formatter.dispatch_compilation_header("dbt templater", "Sorting Nodes...")

        # Initialise config if not already done
        self.sqlfluff_config = config
        if not self.project_dir:
            self.project_dir = self._get_project_dir()
        if not self.profiles_dir:
            self.profiles_dir = self._get_profiles_dir()
        yield from super().sequence_files(fnames, config, formatter)

    def config_pairs(self):  # pragma: no cover
        """Returns info about the given templater for output by the cli."""
        return [
            ("templater", self.name),
            ("dbt", get_installed_version().to_version_string()),
        ]

    def _find_node(self, project, fname):
        expected_node_path = os.path.relpath(
            fname, start=os.path.abspath(project.args.project_dir)
        )
        node = project.get_node_by_path(expected_node_path)
        if node:
            return node
        skip_reason = self._find_skip_reason(project, expected_node_path)
        if skip_reason:
            raise SQLFluffSkipFile(f"Skipped file {fname} because it is {skip_reason}")
        raise SQLFluffSkipFile(
            f"File {fname} was not found in dbt project"
        )  # pragma: no cover

    @large_file_check
    def process(
        self,
        *,
        in_str: Optional[str] = None,
        fname: str,
        config: Optional[FluffConfig] = None,
        formatter: Optional[OutputStreamFormatter] = None,
        **kwargs,
    ):
        """Compile a dbt model and return the compiled SQL.

        Args:
            fname: Path to dbt model(s)
            in_str: fname contents using configured encoding
            config: A specific config to use for this
                templating operation. Only necessary for some templaters.
            formatter: Optional object for output.
        """
        # Stash the formatter if provided to use in cached methods.
        self.formatter = formatter
        self.sqlfluff_config = config
        try:
            processsed_result = self._unsafe_process(
                os.path.abspath(fname) if fname else None, in_str, config
            )
            # Reset the fail counter
            self._sequential_fails = 0
            return processsed_result
        except DbtRuntimeException as e:
            # Increment the counter
            self._sequential_fails += 1
            message = (
                f"dbt error on file '{e.node.original_file_path}', " f"{e.msg}"
                if e.node
                else f"dbt error: {e.msg}"
            )
            return None, [
                SQLTemplaterError(
                    message,
                    # It's fatal if we're over the limit
                    fatal=self._sequential_fails > self.sequential_fail_limit,
                )
            ]
        # If a SQLFluff error is raised, just pass it through
        except SQLTemplaterError as e:  # pragma: no cover
            return None, [e]

    def _find_skip_reason(self, project, expected_node_path) -> Optional[str]:
        """Return string reason if model okay to skip, otherwise None."""
        # Scan macros.
        for macro in project.dbt.macros.values():
            if macro.original_file_path == expected_node_path:
                return "a macro"

        # Scan disabled nodes.
        for nodes in project.dbt.disabled.values():
            for node in nodes:
                if node.original_file_path == expected_node_path:
                    return "disabled"
        return None  # pragma: no cover

    def _unsafe_process(
        self, fname: Optional[str], in_str: str, config: FluffConfig = None
    ):
        # Get project_dir from '.sqlfluff' config file
        self.project_dir = (
            config.get_section((self.templater_selector, self.name, "project_dir"))
            or os.getcwd()
        )
        # Get project
        osmosis_dbt_project = self.dbt_project_container.get_project_by_root_dir(
            self.project_dir
        )
        if not osmosis_dbt_project:
            if not self.profiles_dir:
                self.profiles_dir = self._get_profiles_dir()
            assert self.project_dir
            assert self.profiles_dir
            osmosis_dbt_project = self.dbt_project_container.add_project(
                project_dir=self.project_dir,
                profiles_dir=self.profiles_dir,
                vars=self._get_cli_vars(),
            )

        # If in_str not provided, use path if file is present.
        fpath = Path(fname)
        if fpath.exists() and not in_str:
            in_str = fpath.read_text()

        self.dbt_config = osmosis_dbt_project.config
        node = self._find_node(osmosis_dbt_project, fname)
        node = osmosis_dbt_project.compile_node(node).node
        # Generate context
        ctx = osmosis_dbt_project.generate_runtime_model_context(node)
        env = jinja.get_environment(node)
        env.add_extension(SnapshotExtension)
        if hasattr(node, "injected_sql"):
            # If injected SQL is present, it contains a better picture
            # of what will actually hit the database (e.g. with tests).
            # However it's not always present.
            compiled_sql = node.injected_sql  # pragma: no cover
        else:
            compiled_sql = getattr(node, COMPILED_SQL_ATTRIBUTE)

        def make_template(_in_str):
            return env.from_string(_in_str, globals=ctx)

        # Need compiled
        if not compiled_sql:  # pragma: no cover
            raise SQLTemplaterError(
                "dbt templater compilation failed silently, check your "
                "configuration by running `dbt compile` directly."
            )

        # Whitespace
        if not in_str.rstrip().endswith("-%}"):
            n_trailing_newlines = len(in_str) - len(in_str.rstrip("\n"))
        else:
            # Source file ends with right whitespace stripping, so there's
            # no need to preserve/restore trailing newlines.
            n_trailing_newlines = 0

        # LOG
        templater_logger.debug(
            "    Trailing newline count in source dbt model: %r",
            n_trailing_newlines,
        )
        templater_logger.debug("    Raw SQL before compile: %r", in_str)
        templater_logger.debug("    Node raw SQL: %r", in_str)
        templater_logger.debug("    Node compiled SQL: %r", compiled_sql)

        # SLICE
        raw_sliced, sliced_file, templated_sql = self.slice_file(
            raw_str=in_str,
            templated_str=compiled_sql + "\n" * n_trailing_newlines,
            config=config,
            make_template=make_template,
            append_to_templated="\n" if n_trailing_newlines else "",
        )

        return (
            TemplatedFile(
                source_str=in_str,
                templated_str=templated_sql,
                fname=fname,
                sliced_file=sliced_file,
                raw_sliced=raw_sliced,
            ),
            # No violations returned in this way.
            [],
        )


class SnapshotExtension(StandaloneTag):
    """Dummy "snapshot" tags so raw dbt templates will parse.

    For more context, see sqlfluff-templater-dbt.
    """

    tags = {"snapshot", "endsnapshot"}

    def render(self, format_string=None):
        """Dummy method that renders the tag."""
        return ""
