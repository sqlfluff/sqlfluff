"""Defines the templaters."""

import os.path
import logging
from typing import Optional

from dataclasses import dataclass
from cached_property import cached_property
from functools import partial

from sqlfluff.core.errors import SQLTemplaterError

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

    def __init__(self, **kwargs):
        self.sqlfluff_config = None
        super().__init__(**kwargs)

    @cached_property
    def dbt_version(self):
        """Gets the dbt version."""
        from dbt.version import get_installed_version

        self.dbt_version = get_installed_version().to_version_string()
        return self.dbt_version

    @cached_property
    def dbt_config(self):
        """Loads the dbt config."""
        from dbt.config.runtime import RuntimeConfig as DbtRuntimeConfig
        from dbt.adapters.factory import register_adapter

        self.dbt_config = DbtRuntimeConfig.from_args(
            DbtConfigArgs(
                project_dir=self._get_project_dir(),
                profiles_dir=self._get_profiles_dir(),
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

        if "0.17" in self.dbt_version:
            from dbt.parser.manifest import (
                load_internal_manifest as load_macro_manifest,
                load_manifest,
            )
        else:
            from dbt.parser.manifest import (
                load_macro_manifest,
                load_manifest,
            )

            load_macro_manifest = partial(load_macro_manifest, macro_hook=identity)

        dbt_macros_manifest = load_macro_manifest(self.dbt_config)
        self.dbt_manifest = load_manifest(
            self.dbt_config, dbt_macros_manifest, macro_hook=identity
        )
        return self.dbt_manifest

    @cached_property
    def dbt_selector_method(self):
        """Loads the dbt selector method."""
        if "0.17" in self.dbt_version:
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

        return os.path.expanduser(
            self.sqlfluff_config.get_section(
                (self.templater_selector, self.name, "profiles_dir")
            )
            or PROFILES_DIR
        )

    def _get_project_dir(self):
        """Get the dbt project directory from the configuration.

        Defaults to the working directory.
        """
        return os.path.expanduser(
            self.sqlfluff_config.get_section(
                (self.templater_selector, self.name, "project_dir")
            )
            or os.getcwd()
        )

    def _get_profile(self):
        """Get a dbt profile name from the configuration."""
        return self.sqlfluff_config.get_section(
            (self.templater_selector, self.name, "profile")
        )

    @staticmethod
    def _check_dbt_installed():
        try:
            import dbt  # noqa: F401
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Module dbt was not found while trying to use dbt templating, "
                "please install dbt dependencies through `pip install sqlfluff[dbt]`"
            ) from e

    def process(self, *, fname, in_str=None, config=None):
        """Compile a dbt model and return the compiled SQL.

        Args:
            fname (:obj:`str`): Path to dbt model(s)
            in_str (:obj:`str`, optional): This is ignored for dbt
            config (:obj:`FluffConfig`, optional): A specific config to use for this
                templating operation. Only necessary for some templaters.
        """
        self._check_dbt_installed()
        from dbt.exceptions import (
            CompilationException as DbtCompilationException,
            FailedToConnectException as DbtFailedToConnectException,
        )

        try:
            return self._unsafe_process(fname, in_str, config)
        except DbtCompilationException as e:
            return None, [
                SQLTemplaterError(
                    f"dbt compilation error on file '{e.node.original_file_path}', {e.msg}"
                )
            ]
        except DbtFailedToConnectException as e:
            return None, [
                SQLTemplaterError(
                    "dbt tried to connect to the database and failed: "
                    "you could use 'execute' https://docs.getdbt.com/reference/dbt-jinja-functions/execute/ "
                    f"to skip the database calls. Error: {e.msg}"
                )
            ]
        # If a SQLFluff error is raised, just pass it through
        except SQLTemplaterError as e:
            return None, [e]

    def _unsafe_process(self, fname, in_str=None, config=None):
        if not config:
            raise ValueError(
                "For the dbt templater, the `process()` method requires a config object."
            )
        if not fname:
            raise ValueError(
                "For the dbt templater, the `process()` method requires a file name"
            )
        elif fname == "stdin":
            raise ValueError(
                "The dbt templater does not support stdin input, provide a path instead"
            )
        self.sqlfluff_config = config

        selected = self.dbt_selector_method.search(
            included_nodes=self.dbt_manifest.nodes,
            # Selector needs to be a relative path
            selector=os.path.relpath(fname, start=os.getcwd()),
        )
        results = [self.dbt_manifest.expect(uid) for uid in selected]

        if not results:
            raise RuntimeError("File %s was not found in dbt project" % fname)

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

        if not compiled_sql:
            raise SQLTemplaterError(
                "dbt templater compilation failed silently, check your configuration "
                "by running `dbt compile` directly."
            )

        raw_sliced, sliced_file, templated_sql = self.slice_file(
            node.raw_sql, compiled_sql, config=config
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
