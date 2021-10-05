"""Defines the templaters."""

import os
import os.path
import logging
from pathlib import Path
from typing import List, Optional

from dataclasses import dataclass
from cached_property import cached_property
from functools import partial

from dbt.version import get_installed_version
from dbt.config.profile import PROFILES_DIR
from dbt.config.runtime import RuntimeConfig as DbtRuntimeConfig
from dbt.adapters.factory import register_adapter
from dbt.compilation import Compiler as DbtCompiler
from dbt.exceptions import (
    CompilationException as DbtCompilationException,
    FailedToConnectException as DbtFailedToConnectException,
)

from sqlfluff.core.errors import SQLTemplaterError, SQLTemplaterSkipFile

from sqlfluff.core.templaters.base import TemplatedFile
from sqlfluff.core.templaters.jinja import JinjaTemplater

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")


DBT_VERSION = get_installed_version()
DBT_VERSION_STRING = DBT_VERSION.to_version_string()
DBT_VERSION_TUPLE = (int(DBT_VERSION.major), int(DBT_VERSION.minor))


@dataclass
class DbtConfigArgs:
    """Arguments to load dbt runtime config."""

    project_dir: Optional[str] = None
    profiles_dir: Optional[str] = None
    profile: Optional[str] = None


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

    @property
    def dbt_version(self):
        """Gets the dbt version."""
        return DBT_VERSION_STRING

    @property
    def dbt_version_tuple(self):
        """Gets the dbt version as a tuple on (major, minor)."""
        return DBT_VERSION_TUPLE

    @cached_property
    def dbt_config(self):
        """Loads the dbt config."""
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

        if self.dbt_version_tuple == (0, 17):  # pragma: no cover TODO?
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

    def sequence_files(self, fnames: List[str], config=None, formatter=None):
        """Reorder fnames to process dependent files first.

        This avoids errors when an ephemeral model is processed before use.
        """
        # Stash the formatter if provided to use in cached methods.
        self.formatter = formatter
        result_fnames = []
        model_fqns = set()
        for fname in fnames:
            # "fqn" is either a tuple or None. If a tuple, it's a dbt "fully
            # qualified name" for the model. If an fqn is available (not None),
            # we use it here to try and avoid confusion with multiple versions
            # of a relative path to the same underlying file:
            # - Most models: Relative to the working directory
            # - Dependent/ephemeral models: Relative to the dbt project directory
            for fqn, dependent in self._walk_dependents(
                fname, fnames, self.working_dir, config=config
            ):
                add = False
                if fqn:
                    # We have a fully-qualified name. Use it to avoid
                    # duplicate filenames.
                    if fqn not in model_fqns:
                        model_fqns.add(fqn)
                        add = True
                else:
                    # Fully-qualified name not available. Assume we need to add it.
                    add = True
                if add and dependent not in result_fnames:
                    result_fnames.append(dependent)
        return result_fnames

    def _walk_dependents(self, fname, fnames, relative_to, config=None):
        self.sqlfluff_config = config
        if not self.project_dir:
            self.project_dir = self._get_project_dir()
        if not self.profiles_dir:
            self.profiles_dir = self._get_profiles_dir()
        node = None
        try:
            os.chdir(self.project_dir)
            fname_absolute_path = os.path.join(relative_to, fname)
            try:
                node = self._find_node(fname_absolute_path, config)
                if node.depends_on.nodes:
                    templater_logger.info(
                        "%s depends on %s", fname, node.depends_on.nodes
                    )
                for dependent in node.depends_on.nodes:
                    if dependent in self.dbt_manifest.nodes:
                        # Note that we don't check here whether the file is in
                        # "fnames". It's okay to *walk through these files* as
                        # long as we don't *return* them.
                        yield from self._walk_dependents(
                            self.dbt_manifest.nodes[dependent].original_file_path,
                            fnames,
                            self.project_dir,
                            config=config,
                        )
            except SQLTemplaterSkipFile:
                pass
            finally:
                # Traversing dependencies may lead us to files that are "out of
                # scope". It's okay to traverse them, but only return files
                # seen in the original list. This avoids having SQLFluff look
                # at things it's not supposed to (e.g. directories that weren't
                # passed to the "lint" command, files excluded by
                # .sqlfluffignore, etc.
                if os.path.relpath(
                    fname, self.working_dir
                ) in fnames or os.path.relpath(
                    os.path.join(self.working_dir, fname), self.working_dir
                ):
                    if node:
                        # If we have a node object, use it to clean up the
                        # path we return, i.e. return a path relative to the
                        # working directory.
                        yield tuple(node.fqn), str(
                            (
                                Path(node.root_path) / node.original_file_path
                            ).relative_to(Path(self.working_dir))
                        ),
                    else:
                        # If we don't have a node object, just return fname "as is"
                        # and let the caller deal with this the best it can.
                        yield None, fname
        finally:
            os.chdir(self.working_dir)

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

    def _find_node(self, fname, config=None):
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
        return results[0]

    def _unsafe_process(self, fname, in_str=None, config=None):
        node = self._find_node(fname, config)

        node = self.dbt_compiler.compile_node(
            node=node,
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
