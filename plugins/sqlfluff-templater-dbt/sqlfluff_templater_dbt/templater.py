"""Defines the dbt templater.

NOTE: The dbt python package adds a significant overhead to import.
This module is also loaded on every run of SQLFluff regardless of
whether the dbt templater is selected in the configuration.

The templater is however only _instantiated_ when selected, and as
such, all imports of the dbt libraries are contained within the
DbtTemplater class and so are only imported when necessary.
"""

import logging
import os
import os.path
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Deque,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)

from jinja2 import Environment
from jinja2_simple_tags import StandaloneTag

from sqlfluff.core.errors import SQLFluffSkipFile, SQLFluffUserError, SQLTemplaterError
from sqlfluff.core.templaters.base import TemplatedFile, large_file_check
from sqlfluff.core.templaters.jinja import JinjaTemplater

if TYPE_CHECKING:  # pragma: no cover
    from dbt.semver import VersionSpecifier

    from sqlfluff.cli.formatters import OutputStreamFormatter
    from sqlfluff.core import FluffConfig

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")


@dataclass
class DbtConfigArgs:
    """Arguments to load dbt runtime config."""

    project_dir: Optional[str] = None
    profiles_dir: Optional[str] = None
    profile: Optional[str] = None
    target: Optional[str] = None
    threads: int = 1
    single_threaded: bool = False
    # dict in 1.5.x onwards, json string before.
    # NOTE: We always set this value when instantiating this
    # class. If we rely on defaults, this should default to
    # an empty string pre 1.5.x
    vars: Optional[Union[Dict, str]] = None
    # NOTE: The `which` argument here isn't covered in tests, but many
    # dbt packages assume that it will have been set.
    # https://github.com/sqlfluff/sqlfluff/issues/4861
    # https://github.com/sqlfluff/sqlfluff/issues/4965
    which: Optional[str] = "compile"


class DbtTemplater(JinjaTemplater):
    """A templater using dbt."""

    name = "dbt"
    sequential_fail_limit = 3
    adapters = {}

    def __init__(self, **kwargs):
        self.sqlfluff_config = None
        self.formatter = None
        self.project_dir = None
        self.profiles_dir = None
        self.working_dir = os.getcwd()
        self._sequential_fails = 0
        super().__init__(**kwargs)

    def config_pairs(self):
        """Returns info about the given templater for output by the cli."""
        return [("templater", self.name), ("dbt", self.dbt_version)]

    @cached_property
    def _dbt_version(self) -> "VersionSpecifier":
        """Fetches the installed dbt version.

        This is cached in the raw dbt format.

        NOTE: We do this only on demand to reduce the amount of loading
        required to discover the templater.
        """
        from dbt.version import get_installed_version

        return get_installed_version()

    @cached_property
    def dbt_version(self):
        """Gets the dbt version."""
        return self._dbt_version.to_version_string()

    @cached_property
    def dbt_version_tuple(self):
        """Gets the dbt version."""
        return int(self._dbt_version.major), int(self._dbt_version.minor)

    def try_silence_dbt_logs(self) -> None:
        """Attempt to silence dbt logs.

        During normal operation dbt is likely to log output such as:

        .. code-block::

           14:13:10  Registered adapter: snowflake=1.6.0

        This is emitted by dbt directly to stdout/stderr, and so for us
        to silence it (e.g. when outputting to json or yaml) we need to
        reach into the internals of dbt and silence it directly.

        https://github.com/sqlfluff/sqlfluff/issues/5054

        NOTE: We wrap this in a try clause so that if the API changes
        within dbt that we don't get a direct fail. This was tested on
        dbt-code==1.6.0.
        """
        # First check whether we need to silence the logs. If a formatter
        # is present then assume that it's not a problem
        if not self.formatter:
            try:
                from dbt.events.functions import cleanup_event_logger

                cleanup_event_logger()
            except ImportError:
                pass

    @cached_property
    def dbt_config(self):
        """Loads the dbt config."""
        from dbt import flags
        from dbt.adapters.factory import register_adapter
        from dbt.config import read_user_config
        from dbt.config.runtime import RuntimeConfig as DbtRuntimeConfig

        # Attempt to silence internal logging at this point.
        # https://github.com/sqlfluff/sqlfluff/issues/5054
        self.try_silence_dbt_logs()

        if self.dbt_version_tuple >= (1, 5):
            user_config = None
            # 1.5.x+ this is a dict.
            cli_vars = self._get_cli_vars()
        else:
            # Here, we read flags.PROFILE_DIR directly, prior to calling
            # set_from_args(). Apparently, set_from_args() sets PROFILES_DIR
            # to a lowercase version of the value, and the profile wouldn't be
            # found if the directory name contained uppercase letters. This fix
            # was suggested and described here:
            # https://github.com/sqlfluff/sqlfluff/issues/2253#issuecomment-1018722979
            user_config = read_user_config(flags.PROFILES_DIR)
            # Pre 1.5.x this is a string.
            cli_vars = str(self._get_cli_vars())

        flags.set_from_args(
            DbtConfigArgs(
                project_dir=self.project_dir,
                profiles_dir=self.profiles_dir,
                profile=self._get_profile(),
                vars=cli_vars,
                threads=1,
            ),
            user_config,
        )
        self.dbt_config = DbtRuntimeConfig.from_args(
            DbtConfigArgs(
                project_dir=self.project_dir,
                profiles_dir=self.profiles_dir,
                profile=self._get_profile(),
                target=self._get_target(),
                vars=cli_vars,
                threads=1,
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
        from dbt.exceptions import DbtProjectError

        # NOTE: The uninstalled packages error only exists from around
        # dbt 1.4 onwards. Before that we'll just get a slightly uglier
        # error - not a breaking issue.
        try:
            from dbt.exceptions import UninstalledPackagesFoundError

            summary_errors = (DbtProjectError, UninstalledPackagesFoundError)
        except ImportError:
            summary_errors = (DbtProjectError,)

        # Set dbt not to run tracking. We don't load
        # a full project and so some tracking routines
        # may fail.
        from dbt.tracking import do_not_track

        do_not_track()

        # dbt 0.20.* and onward
        from dbt.parser.manifest import ManifestLoader

        old_cwd = os.getcwd()
        try:
            # Changing cwd temporarily as dbt is not using project_dir to
            # read/write `target/partial_parse.msgpack`. This can be undone when
            # https://github.com/dbt-labs/dbt-core/issues/6055 is solved.
            # For dbt 1.4+ this isn't necessary, but it is required for 1.3
            # and before.
            if self.dbt_version_tuple < (1, 4):
                os.chdir(self.project_dir)
            self.dbt_manifest = ManifestLoader.get_full_manifest(self.dbt_config)
        except summary_errors as err:  # pragma: no cover
            raise SQLFluffUserError(f"{err.__class__.__name__}: {err}")
        finally:
            if self.dbt_version_tuple < (1, 4):
                os.chdir(old_cwd)

        return self.dbt_manifest

    @cached_property
    def dbt_selector_method(self):
        """Loads the dbt selector method."""
        if self.formatter:  # pragma: no cover TODO?
            self.formatter.dispatch_compilation_header(
                "dbt templater", "Compiling dbt project..."
            )

        from dbt.graph.selector_methods import (
            MethodManager as DbtSelectorMethodManager,
        )
        from dbt.graph.selector_methods import (
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

        The default is `~/.dbt` but we use the
        default_profiles_dir from the dbt library to
        support a change of default in the future, as well
        as to support the same overwriting mechanism as
        dbt (currently an environment variable).
        """
        # Where default_profiles_dir is available, use it. For dbt 1.2 and
        # earlier, it is not, so fall back to the flags option which should
        # still be available in those versions.

        from dbt import flags

        # From dbt 1.3 onwards, the default_profiles_dir resolver is
        # available. Before that version we use the flags module
        try:
            from dbt.cli.resolvers import default_profiles_dir
        except ImportError:
            default_profiles_dir = None

        default_dir = (
            default_profiles_dir()
            if default_profiles_dir is not None
            else flags.PROFILES_DIR
        )

        dbt_profiles_dir = os.path.abspath(
            os.path.expanduser(
                self.sqlfluff_config.get_section(
                    (self.templater_selector, self.name, "profiles_dir")
                )
                or (os.getenv("DBT_PROFILES_DIR") or default_dir)
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

    def _get_cli_vars(self) -> dict:
        cli_vars = self.sqlfluff_config.get_section(
            (self.templater_selector, self.name, "context")
        )

        return cli_vars if cli_vars else {}

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

        # Populate full paths for selected files
        full_paths: Dict[str, str] = {}
        selected_files = set()
        for fname in fnames:
            fpath = os.path.join(self.working_dir, fname)
            full_paths[fpath] = fname
            selected_files.add(fpath)

        ephemeral_nodes: Dict[str, Tuple[str, Any]] = {}

        # Extract the ephemeral models
        for key, node in self.dbt_manifest.nodes.items():
            if node.config.materialized == "ephemeral":
                # The key is the full filepath.
                # The value tuple, with the filepath and a list of dependent keys
                ephemeral_nodes[key] = (
                    os.path.join(self.project_dir, node.original_file_path),
                    node.depends_on.nodes,
                )

        # Yield ephemeral nodes first. We use a deque for efficient re-queuing.
        # We iterate through the deque, yielding any nodes without dependents,
        # or where those dependents have already yielded, first. The original
        # mapping is still used to hold the metadata on each key.
        already_yielded = set()
        ephemeral_buffer: Deque[str] = deque(ephemeral_nodes.keys())
        while ephemeral_buffer:
            key = ephemeral_buffer.popleft()
            fpath, dependents = ephemeral_nodes[key]

            # If it's not in our selection, skip it
            if fpath not in selected_files:
                templater_logger.debug("- Purging unselected ephemeral: %r", fpath)
            # If there are dependent nodes in the set, don't process it yet.
            elif any(
                dependent in ephemeral_buffer for dependent in dependents
            ):  # pragma: no cover
                templater_logger.debug(
                    "- Requeuing ephemeral with dependents: %r", fpath
                )
                # Requeue it for later
                ephemeral_buffer.append(key)
            # Otherwise yield it.
            else:
                templater_logger.debug("- Yielding Ephemeral: %r", fpath)
                yield full_paths[fpath]
                already_yielded.add(full_paths[fpath])

        for fname in fnames:
            if fname not in already_yielded:
                yield fname
                # Dedupe here so we don't yield twice
                already_yielded.add(fname)
            else:
                templater_logger.debug(
                    "- Skipping yield of previously sequenced file: %r", fname
                )

    @large_file_check
    def process(
        self,
        *,
        fname: str,
        in_str: Optional[str] = None,
        config: Optional["FluffConfig"] = None,
        formatter: Optional["OutputStreamFormatter"] = None,
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
        self.project_dir = self._get_project_dir()
        self.profiles_dir = self._get_profiles_dir()
        fname_absolute_path = os.path.abspath(fname)

        try:
            # These are the names in dbt-core 1.4.1+
            # https://github.com/dbt-labs/dbt-core/pull/6539
            from dbt.exceptions import CompilationError, FailedToConnectError
        except ImportError:
            # These are the historic names for older dbt-core versions
            from dbt.exceptions import CompilationException as CompilationError
            from dbt.exceptions import (
                FailedToConnectException as FailedToConnectError,
            )

        try:
            os.chdir(self.project_dir)
            processed_result = self._unsafe_process(fname_absolute_path, in_str, config)
            # Reset the fail counter
            self._sequential_fails = 0
            return processed_result
        except FailedToConnectError as e:
            return None, [
                SQLTemplaterError(
                    "dbt tried to connect to the database and failed: you could use "
                    "'execute' to skip the database calls. See "
                    "https://docs.getdbt.com/reference/dbt-jinja-functions/execute/ "
                    f"Error: {e.msg}",
                    fatal=True,
                )
            ]
        except CompilationError as e:
            # Increment the counter
            self._sequential_fails += 1
            if e.node:
                _msg = (
                    f"dbt compilation error on file '{e.node.original_file_path}'"
                    f", {e.msg}"
                )
            else:
                _msg = f"dbt compilation error: {e.msg}"
            return None, [
                SQLTemplaterError(
                    _msg,
                    # It's fatal if we're over the limit
                    fatal=self._sequential_fails > self.sequential_fail_limit,
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
                "For the dbt templater, the `process()` method "
                "requires a config object."
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
            skip_reason = self._find_skip_reason(fname)
            if skip_reason:
                raise SQLFluffSkipFile(
                    f"Skipped file {fname} because it is {skip_reason}"
                )
            raise SQLFluffSkipFile(
                "File %s was not found in dbt project" % fname
            )  # pragma: no cover
        return results[0]

    def _find_skip_reason(self, fname) -> Optional[str]:
        """Return string reason if model okay to skip, otherwise None."""
        # Scan macros.
        abspath = os.path.abspath(fname)
        for macro in self.dbt_manifest.macros.values():
            if os.path.abspath(macro.original_file_path) == abspath:
                return "a macro"

        # Scan disabled nodes.
        for nodes in self.dbt_manifest.disabled.values():
            for node in nodes:
                if os.path.abspath(node.original_file_path) == abspath:
                    return "disabled"
        return None  # pragma: no cover

    def _unsafe_process(self, fname, in_str=None, config=None):
        original_file_path = os.path.relpath(fname, start=os.getcwd())

        # Below, we monkeypatch Environment.from_string() to intercept when dbt
        # compiles (i.e. runs Jinja) to expand the "node" corresponding to fname.
        # We do this to capture the Jinja context at the time of compilation, i.e.:
        # - Jinja Environment object
        # - Jinja "globals" dictionary
        #
        # This info is captured by the "make_template()" function, which in
        # turn is used by our parent class' (JinjaTemplater) slice_file()
        # function.
        old_from_string = Environment.from_string
        # Start with render_func undefined. We need to know whether it has been
        # overwritten.
        render_func: Optional[Callable[[str], str]] = None

        if self.dbt_version_tuple >= (1, 3):
            compiled_sql_attribute = "compiled_code"
            raw_sql_attribute = "raw_code"
        else:  # pragma: no cover
            compiled_sql_attribute = "compiled_sql"
            raw_sql_attribute = "raw_sql"

        def from_string(*args, **kwargs):
            """Replaces (via monkeypatch) the jinja2.Environment function."""
            nonlocal render_func
            # Is it processing the node corresponding to fname?
            globals = kwargs.get("globals")
            if globals:
                model = globals.get("model")
                if model:
                    if model.get("original_file_path") == original_file_path:
                        # Yes. Capture the important arguments and create
                        # a render_func() closure with overwrites the variable
                        # from within _unsafe_process when from_string is run.
                        env = args[0]
                        globals = args[2] if len(args) >= 3 else kwargs["globals"]

                        # Overwrite the outer render_func
                        def render_func(in_str):
                            env.add_extension(SnapshotExtension)
                            template = env.from_string(in_str, globals=globals)
                            return template.render()

            return old_from_string(*args, **kwargs)

        # NOTE: We need to inject the project root here in reaction to the
        # breaking change upstream with dbt. Coverage works in 1.5.2, but
        # appears to no longer be covered in 1.5.3.
        # This change was backported and so exists in some versions
        # but not others. When not present, no additional action is needed.
        # https://github.com/dbt-labs/dbt-core/pull/7949
        # On the 1.5.x branch this was between 1.5.1 and 1.5.2
        try:
            from dbt.task.contextvars import cv_project_root

            cv_project_root.set(self.project_dir)  # pragma: no cover
        except ImportError:
            cv_project_root = None

        # NOTE: _find_node will raise a compilation exception if the project
        # fails to compile, and we catch that in the outer `.process()` method.
        node = self._find_node(fname, config)

        templater_logger.debug(
            "_find_node for path %r returned object of type %s.", fname, type(node)
        )

        save_ephemeral_nodes = dict(
            (k, v)
            for k, v in self.dbt_manifest.nodes.items()
            if v.config.materialized == "ephemeral"
            and not getattr(v, "compiled", False)
        )

        try:
            # These are the names in dbt-core 1.4.1+
            # https://github.com/dbt-labs/dbt-core/pull/6539
            from dbt.exceptions import UndefinedMacroError
        except ImportError:
            # These are the historic names for older dbt-core versions
            from dbt.exceptions import UndefinedMacroException as UndefinedMacroError

        with self.connection():
            # Apply the monkeypatch.
            Environment.from_string = from_string
            try:
                node = self.dbt_compiler.compile_node(
                    node=node,
                    manifest=self.dbt_manifest,
                )
            except UndefinedMacroError as err:
                # The explanation on the undefined macro error is already fairly
                # explanatory, so just pass it straight through.
                raise SQLTemplaterError(str(err))
            except Exception as err:  # pragma: no cover
                # NOTE: We use .error() here rather than .exception() because
                # for most users, the trace which accompanies the latter isn't
                # particularly helpful.
                templater_logger.error(
                    "Fatal dbt compilation error on %s. This occurs most often "
                    "during incorrect sorting of ephemeral models before linting. "
                    "Please report this error on github at "
                    "https://github.com/sqlfluff/sqlfluff/issues, including "
                    "both the raw and compiled sql for the model affected.",
                    fname,
                )
                # Additional error logging in case we get a fatal dbt error.
                raise SQLFluffSkipFile(  # pragma: no cover
                    f"Skipped file {fname} because dbt raised a fatal "
                    f"exception during compilation: {err!s}"
                )
                # NOTE: We don't do a `raise ... from err` here because the
                # full trace is not useful for most users. In debugging
                # issues here it may be valuable to add the `from err` part
                # after the above `raise` statement.
            finally:
                # Undo the monkeypatch.
                Environment.from_string = old_from_string

            if hasattr(node, "injected_sql"):
                # If injected SQL is present, it contains a better picture
                # of what will actually hit the database (e.g. with tests).
                # However it's not always present.
                compiled_sql = node.injected_sql  # pragma: no cover
            else:
                compiled_sql = getattr(node, compiled_sql_attribute)

            raw_sql = getattr(node, raw_sql_attribute)

            if not compiled_sql:  # pragma: no cover
                raise SQLTemplaterError(
                    "dbt templater compilation failed silently, check your "
                    "configuration by running `dbt compile` directly."
                )
            source_dbt_sql = in_str
            if not source_dbt_sql.rstrip().endswith("-%}"):
                n_trailing_newlines = len(source_dbt_sql) - len(
                    source_dbt_sql.rstrip("\n")
                )
            else:
                # Source file ends with right whitespace stripping, so there's
                # no need to preserve/restore trailing newlines, as they would
                # have been removed regardless of dbt's
                # keep_trailing_newlines=False behavior.
                n_trailing_newlines = 0

            templater_logger.debug(
                "    Trailing newline count in source dbt model: %r",
                n_trailing_newlines,
            )
            templater_logger.debug("    Raw SQL before compile: %r", source_dbt_sql)
            templater_logger.debug("    Node raw SQL: %r", raw_sql)
            templater_logger.debug("    Node compiled SQL: %r", compiled_sql)

            # When using dbt-templater, trailing newlines are ALWAYS REMOVED during
            # compiling. Unless fixed (like below), this will cause:
            #    1. Assertion errors in TemplatedFile, when it sanity checks the
            #       contents of the sliced_file array.
            #    2. LT12 linting errors when running "sqlfluff lint foo_bar.sql"
            #       since the linter will use the compiled code with the newlines
            #       removed.
            #    3. "No newline at end of file" warnings in Git/GitHub since
            #       sqlfluff uses the compiled SQL to write fixes back to the
            #       source SQL in the dbt model.
            #
            # The solution is (note that both the raw and compiled files have
            # had trailing newline(s) removed by the dbt-templater.
            #    1. Check for trailing newlines before compiling by looking at the
            #       raw SQL in the source dbt file. Remember the count of trailing
            #       newlines.
            #    2. Set node.raw_sql/node.raw_code to the original source file contents.
            #    3. Append the count from #1 above to compiled_sql. (In
            #       production, slice_file() does not usually use this string,
            #       but some test scenarios do.
            setattr(node, raw_sql_attribute, source_dbt_sql)

            # So for files that have no templated elements in them, render_func
            # will still be null at this point. If so, we replace it with a lambda
            # which just directly returns the input , but _also_ reset the trailing
            # newlines counter because they also won't have been stripped.
            if render_func is None:
                # NOTE: In this case, we shouldn't re-add newlines, because they
                # were never taken away.
                n_trailing_newlines = 0

                # Overwrite the render_func placeholder.
                def render_func(in_str):
                    """A render function which just returns the input."""
                    return in_str

            # At this point assert that we _have_ a render_func
            assert render_func is not None

            # TRICKY: dbt configures Jinja2 with keep_trailing_newline=False.
            # As documented (https://jinja.palletsprojects.com/en/3.0.x/api/),
            # this flag's behavior is: "Preserve the trailing newline when
            # rendering templates. The default is False, which causes a single
            # newline, if present, to be stripped from the end of the template."
            #
            # Below, we use "append_to_templated" to effectively "undo" this.
            raw_sliced, sliced_file, templated_sql = self.slice_file(
                source_dbt_sql,
                render_func=render_func,
                config=config,
                append_to_templated="\n" if n_trailing_newlines else "",
            )
        # :HACK: If calling compile_node() compiled any ephemeral nodes,
        # restore them to their earlier state. This prevents a runtime error
        # in the dbt "_inject_ctes_into_sql()" function that occurs with
        # 2nd-level ephemeral model dependencies (e.g. A -> B -> C, where
        # both B and C are ephemeral). Perhaps there is a better way to do
        # this, but this seems good enough for now.
        for k, v in save_ephemeral_nodes.items():
            if getattr(self.dbt_manifest.nodes[k], "compiled", False):
                self.dbt_manifest.nodes[k] = v
        return (
            TemplatedFile(
                source_str=source_dbt_sql,
                templated_str=templated_sql,
                fname=fname,
                sliced_file=sliced_file,
                raw_sliced=raw_sliced,
            ),
            # No violations returned in this way.
            [],
        )

    @contextmanager
    def connection(self):
        """Context manager that manages a dbt connection, if needed."""
        from dbt.adapters.factory import get_adapter

        # We have to register the connection in dbt >= 1.0.0 ourselves
        # In previous versions, we relied on the functionality removed in
        # https://github.com/dbt-labs/dbt-core/pull/4062.
        adapter = self.adapters.get(self.project_dir)
        if adapter is None:
            adapter = get_adapter(self.dbt_config)
            self.adapters[self.project_dir] = adapter
            adapter.acquire_connection("master")
            adapter.set_relations_cache(self.dbt_manifest)

        yield
        # :TRICKY: Once connected, we never disconnect. Making multiple
        # connections during linting has proven to cause major performance
        # issues.


class SnapshotExtension(StandaloneTag):
    """Dummy "snapshot" tags so raw dbt templates will parse.

    Context: dbt snapshots
    (https://docs.getdbt.com/docs/building-a-dbt-project/snapshots/#example)
    use custom Jinja "snapshot" and "endsnapshot" tags. However, dbt does not
    actually register those tags with Jinja. Instead, it finds and removes these
    tags during a preprocessing step. However, DbtTemplater needs those tags to
    actually parse, because JinjaTracer creates and uses Jinja to process
    another template similar to the original one.
    """

    tags = {"snapshot", "endsnapshot"}

    def render(self, format_string=None):
        """Dummy method that renders the tag."""
        return ""
