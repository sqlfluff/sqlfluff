"""Defines the templaters."""

import os.path
import logging
from typing import Optional

from dataclasses import dataclass
from cached_property import cached_property
from functools import partial

from sqlfluff.core.errors import SQLTemplaterError, SQLTemplaterSkipFile

from sqlfluff.core.templaters.base import register_templater, TemplatedFile
from sqlfluff.core.templaters.jinja import JinjaTemplater

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")


@dataclass
class DbtConfigArgs:
    """Arguments to load dbt runtime config."""

    project_dir: Optional[str] = None
    profiles_dir: Optional[str] = None
    profile: Optional[str] = None


@register_templater
class DbtTemplater(JinjaTemplater):
    """A templater using dbt."""

    name = "dbt"
    sequential_fail_limit = 3

    def __init__(self, **kwargs):
        self.sqlfluff_config = None
        self.formatter = None
        self.project_dir = None
        self.profiles_dir = None
        self.working_dir = os.getcwd()
        self._sequential_fails = 0
        super().__init__(**kwargs)

    def config_pairs(self):  # pragma: no cover TODO?
        """Returns info about the given templater for output by the cli."""
        return [("templater", self.name), ("dbt", self.dbt_version)]

    @cached_property
    def dbt_version(self):
        """Gets the dbt version."""
        from dbt.version import get_installed_version

        self.dbt_version = get_installed_version().to_version_string()
        return self.dbt_version

    @cached_property
    def dbt_version_tuple(self):
        """Gets the dbt version as a tuple on (major, minor)."""
        from dbt.version import get_installed_version

        version = get_installed_version()

        self.dbt_version_tuple = (int(version.major), int(version.minor))
        return self.dbt_version_tuple

    @cached_property
    def dbt_config(self):
        """Loads the dbt config."""
        from dbt.config.runtime import RuntimeConfig as DbtRuntimeConfig
        from dbt.adapters.factory import register_adapter

        self.dbt_config = DbtRuntimeConfig.from_args(
            DbtConfigArgs(
                project_dir=self.project_dir,
                profiles_dir=self.profiles_dir,
                profile=self._get_profile(),
            )
        )
        register_adapter(self.dbt_config)
        return self.dbt_config

    @cached_property
    def dbt_compiler(self):
        """Loads the dbt compiler."""
        from dbt.compilation import Compiler as DbtCompiler

        self.dbt_compiler = DbtCompiler(self.dbt_config)
        return self.dbt_compiler

    @cached_property
    def dbt_manifest(self):
        """Loads the dbt manifest."""
        # Identity function used for macro hooks
        def identity(x):
            return x

        # Set dbt not to run tracking. We don't load
        # a dull project and so some tracking routines
        # may fail.
        from dbt.tracking import do_not_track

        do_not_track()

        if self.dbt_version_tuple <= (0, 19):

            if self.dbt_version_tuple == (0, 17):  # pragma: no cover TODO?
                # dbt version 0.17.*
                from dbt.parser.manifest import (
                    load_internal_manifest as load_macro_manifest,
                )
            else:
                # dbt version 0.18.* & # 0.19.*
                from dbt.parser.manifest import load_macro_manifest

                load_macro_manifest = partial(load_macro_manifest, macro_hook=identity)

            from dbt.parser.manifest import load_manifest

            dbt_macros_manifest = load_macro_manifest(self.dbt_config)
            self.dbt_manifest = load_manifest(
                self.dbt_config, dbt_macros_manifest, macro_hook=identity
            )
        else:
            # dbt 0.20.* and onward
            from dbt.parser.manifest import ManifestLoader

            projects = self.dbt_config.load_dependencies()
            loader = ManifestLoader(self.dbt_config, projects, macro_hook=identity)
            self.dbt_manifest = loader.load()

        return self.dbt_manifest

    @cached_property
    def dbt_selector_method(self):
        """Loads the dbt selector method."""
        if self.formatter:  # pragma: no cover TODO?
            self.formatter.dispatch_compilation_header(
                "dbt templater", "Compiling dbt project..."
            )

        if "0.17" in self.dbt_version:  # pragma: no cover TODO?
            from dbt.graph.selector import PathSelector

            self.dbt_selector_method = PathSelector(self.dbt_manifest)
        else:
            from dbt.graph.selector_methods import (
                MethodManager as DbtSelectorMethodManager,
                MethodName as DbtMethodName,
            )

            selector_methods_manager = DbtSelectorMethodManager(
                self.dbt_manifest, previous_state=None
            )
            self.dbt_selector_method = selector_methods_manager.get_method(
                DbtMethodName.Path, method_arguments=[]
            )

        if self.formatter:  # pragma: no cover TODO?
            self.formatter.dispatch_compilation_header(
                "dbt templater", "Project Compiled."
            )

        return self.dbt_selector_method

    def _get_profiles_dir(self):
        """Get the dbt profiles directory from the configuration.

        The default is `~/.dbt` in 0.17 but we use the
        PROFILES_DIR variable from the dbt library to
        support a change of default in the future, as well
        as to support the same overwriting mechanism as
        dbt (currently an environment variable).
        """
        from dbt.config.profile import PROFILES_DIR

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
                f"dbt_profiles_dir: {dbt_profiles_dir} could not be accessed. Check it exists."
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
                f"dbt_project_dir: {dbt_project_dir} could not be accessed. Check it exists."
            )

        return dbt_project_dir

    def _get_profile(self):
        """Get a dbt profile name from the configuration."""
        return self.sqlfluff_config.get_section(
            (self.templater_selector, self.name, "profile")
        )

    @staticmethod
    def _check_dbt_installed():
        try:
            import dbt  # noqa: F401
        except ModuleNotFoundError as e:  # pragma: no cover TODO?
            raise ModuleNotFoundError(
                "Module dbt was not found while trying to use dbt templating, "
                "please install dbt dependencies through `pip install sqlfluff[dbt]`"
            ) from e

    def process(self, *, fname, in_str=None, config=None, formatter=None):
        """Compile a dbt model and return the compiled SQL.

        Args:
            fname (:obj:`str`): Path to dbt model(s)
            in_str (:obj:`str`, optional): This is ignored for dbt
            config (:obj:`FluffConfig`, optional): A specific config to use for this
                templating operation. Only necessary for some templaters.
            formatter (:obj:`CallbackFormatter`): Optional object for output.
        """
        # Stash the formatter if provided to use in cached methods.
        self.formatter = formatter

        self._check_dbt_installed()
        from dbt.exceptions import (
            CompilationException as DbtCompilationException,
            FailedToConnectException as DbtFailedToConnectException,
        )

        self.sqlfluff_config = config
        self.project_dir = self._get_project_dir()
        self.profiles_dir = self._get_profiles_dir()
        fname_absolute_path = os.path.abspath(fname)

        try:
            os.chdir(self.project_dir)
            processed_result = self._unsafe_process(fname_absolute_path, in_str, config)
            # Reset the fail counter
            self._sequential_fails = 0
            return processed_result
        except DbtCompilationException as e:
            # Increment the counter
            self._sequential_fails += 1
            if e.node:
                return None, [
                    SQLTemplaterError(
                        f"dbt compilation error on file '{e.node.original_file_path}', {e.msg}",
                        # It's fatal if we're over the limit
                        fatal=self._sequential_fails > self.sequential_fail_limit,
                    )
                ]
            else:
                raise  # pragma: no cover
        except DbtFailedToConnectException as e:
            return None, [
                SQLTemplaterError(
                    "dbt tried to connect to the database and failed: "
                    "you could use 'execute' https://docs.getdbt.com/reference/dbt-jinja-functions/execute/ "
                    f"to skip the database calls. Error: {e.msg}",
                    fatal=True,
                )
            ]
        # If a SQLFluff error is raised, just pass it through
        except SQLTemplaterError as e:  # pragma: no cover
            return None, [e]
        finally:
            os.chdir(self.working_dir)

    def _unsafe_process(self, fname, in_str=None, config=None):
        if not config:  # pragma: no cover
            raise ValueError(
                "For the dbt templater, the `process()` method requires a config object."
            )
        if not fname:  # pragma: no cover
            raise ValueError(
                "For the dbt templater, the `process()` method requires a file name"
            )
        elif fname == "stdin":  # pragma: no cover
            raise ValueError(
                "The dbt templater does not support stdin input, provide a path instead"
            )
        selected = self.dbt_selector_method.search(
            included_nodes=self.dbt_manifest.nodes,
            # Selector needs to be a relative path
            selector=os.path.relpath(fname, start=os.getcwd()),
        )
        results = [self.dbt_manifest.expect(uid) for uid in selected]

        if not results:
            model_name = os.path.splitext(os.path.basename(fname))[0]
            disabled_model = self.dbt_manifest.find_disabled_by_name(name=model_name)
            if disabled_model and os.path.abspath(
                disabled_model.original_file_path
            ) == os.path.abspath(fname):
                raise SQLTemplaterSkipFile(
                    f"Skipped file {fname} because the model was disabled"
                )
            raise RuntimeError(
                "File %s was not found in dbt project" % fname
            )  # pragma: no cover

        node = self.dbt_compiler.compile_node(
            node=results[0],
            manifest=self.dbt_manifest,
        )

        if hasattr(node, "injected_sql"):
            # If injected SQL is present, it contains a better picture
            # of what will actually hit the database (e.g. with tests).
            # However it's not always present.
            compiled_sql = node.injected_sql
        else:
            compiled_sql = node.compiled_sql

        if not compiled_sql:  # pragma: no cover
            raise SQLTemplaterError(
                "dbt templater compilation failed silently, check your configuration "
                "by running `dbt compile` directly."
            )

        with open(fname) as source_dbt_model:
            source_dbt_sql = source_dbt_model.read()

        n_trailing_newlines = len(source_dbt_sql) - len(source_dbt_sql.rstrip("\n"))

        templater_logger.debug(
            "    Trailing newline count in source dbt model: %r", n_trailing_newlines
        )
        templater_logger.debug("    Raw SQL before compile: %r", source_dbt_sql)
        templater_logger.debug("    Node raw SQL: %r", node.raw_sql)
        templater_logger.debug("    Node compiled SQL: %r", compiled_sql)

        # When using dbt-templater, trailing newlines are ALWAYS REMOVED during
        # compiling. Unless fixed (like below), this will cause:
        #    1. L009 linting errors when running "sqlfluff lint foo_bar.sql"
        #       since the linter will use the compiled code with the newlines
        #       removed.
        #    2. "No newline at end of file" warnings in Git/GitHub since
        #       sqlfluff uses the compiled SQL to write fixes back to the
        #       source SQL in the dbt model.
        # The solution is:
        #    1. Check for trailing newlines before compiling by looking at the
        #       raw SQL in the source dbt file, store the count of trailing newlines.
        #    2. Append the count from #1 above to the node.raw_sql and
        #       compiled_sql objects, both of which have had the trailing
        #       newlines removed by the dbt-templater.
        node.raw_sql = node.raw_sql + "\n" * n_trailing_newlines
        compiled_sql = compiled_sql + "\n" * n_trailing_newlines

        raw_sliced, sliced_file, templated_sql = self.slice_file(
            node.raw_sql,
            compiled_sql,
            config=config,
        )

        return (
            TemplatedFile(
                source_str=node.raw_sql,
                templated_str=templated_sql,
                fname=fname,
                sliced_file=sliced_file,
                raw_sliced=raw_sliced,
            ),
            # No violations returned in this way.
            [],
        )

    @classmethod
    def _preprocess_template(cls, in_str: str) -> str:
        return in_str
