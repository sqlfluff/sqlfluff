"""Defines the templaters."""

from collections import deque
from contextlib import contextmanager
import os
import os.path
import logging
from typing import List, Optional, Iterator, Tuple, Any, Dict, Deque

from dataclasses import dataclass

from dbt.version import get_installed_version
from dbt.config import read_user_config
from dbt.config.runtime import RuntimeConfig as DbtRuntimeConfig
from dbt.adapters.factory import register_adapter, get_adapter
from dbt.compilation import Compiler as DbtCompiler
from dbt.exceptions import (
    CompilationException as DbtCompilationException,
    FailedToConnectException as DbtFailedToConnectException,
)
from dbt import flags
from jinja2 import Environment
from jinja2_simple_tags import StandaloneTag

from sqlfluff.core.cached_property import cached_property
from sqlfluff.core.errors import SQLTemplaterError, SQLFluffSkipFile

from sqlfluff.core.templaters.base import TemplatedFile, large_file_check

from sqlfluff.core.templaters.jinja import JinjaTemplater

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")


DBT_VERSION = get_installed_version()
DBT_VERSION_STRING = DBT_VERSION.to_version_string()
DBT_VERSION_TUPLE = (int(DBT_VERSION.major), int(DBT_VERSION.minor))

if DBT_VERSION_TUPLE >= (1, 0):
    from dbt.flags import PROFILES_DIR
else:
    from dbt.config.profile import PROFILES_DIR

if DBT_VERSION_TUPLE >= (1, 3):
    COMPILED_SQL_ATTRIBUTE = "compiled_code"
    RAW_SQL_ATTRIBUTE = "raw_code"
else:
    COMPILED_SQL_ATTRIBUTE = "compiled_sql"
    RAW_SQL_ATTRIBUTE = "raw_sql"


@dataclass
class DbtConfigArgs:
    """Arguments to load dbt runtime config."""

    project_dir: Optional[str] = None
    profiles_dir: Optional[str] = None
    profile: Optional[str] = None
    target: Optional[str] = None
    single_threaded: bool = False
    vars: str = ""


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
        self.connection_acquired = False
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
        if self.dbt_version_tuple >= (1, 0):
            # Here, we read flags.PROFILE_DIR directly, prior to calling
            # set_from_args(). Apparently, set_from_args() sets PROFILES_DIR
            # to a lowercase version of the value, and the profile wouldn't be
            # found if the directory name contained uppercase letters. This fix
            # was suggested and described here:
            # https://github.com/sqlfluff/sqlfluff/issues/2253#issuecomment-1018722979
            user_config = read_user_config(flags.PROFILES_DIR)
            flags.set_from_args(
                DbtConfigArgs(
                    project_dir=self.project_dir,
                    profiles_dir=self.profiles_dir,
                    profile=self._get_profile(),
                    vars=self._get_cli_vars(),
                ),
                user_config,
            )
        self.dbt_config = DbtRuntimeConfig.from_args(
            DbtConfigArgs(
                project_dir=self.project_dir,
                profiles_dir=self.profiles_dir,
                profile=self._get_profile(),
                target=self._get_target(),
                vars=self._get_cli_vars(),
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
        # a full project and so some tracking routines
        # may fail.
        from dbt.tracking import do_not_track

        do_not_track()

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
                        f"dbt compilation error on file '{e.node.original_file_path}', "
                        f"{e.msg}",
                        # It's fatal if we're over the limit
                        fatal=self._sequential_fails > self.sequential_fail_limit,
                    )
                ]
            else:
                raise  # pragma: no cover
        except DbtFailedToConnectException as e:
            return None, [
                SQLTemplaterError(
                    "dbt tried to connect to the database and failed: you could use "
                    "'execute' to skip the database calls. See"
                    "https://docs.getdbt.com/reference/dbt-jinja-functions/execute/ "
                    f"Error: {e.msg}",
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

        if DBT_VERSION_TUPLE >= (1, 0):
            # Scan disabled nodes.
            for nodes in self.dbt_manifest.disabled.values():
                for node in nodes:
                    if os.path.abspath(node.original_file_path) == abspath:
                        return "disabled"
        else:
            model_name = os.path.splitext(os.path.basename(fname))[0]
            if self.dbt_manifest.find_disabled_by_name(name=model_name):
                return "disabled"
        return None

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
        make_template = None

        def from_string(*args, **kwargs):
            """Replaces (via monkeypatch) the jinja2.Environment function."""
            nonlocal make_template
            # Is it processing the node corresponding to fname?
            globals = kwargs.get("globals")
            if globals:
                model = globals.get("model")
                if model:
                    if model.get("original_file_path") == original_file_path:
                        # Yes. Capture the important arguments and create
                        # a make_template() function.
                        env = args[0]
                        globals = args[2] if len(args) >= 3 else kwargs["globals"]

                        def make_template(in_str):
                            env.add_extension(SnapshotExtension)
                            return env.from_string(in_str, globals=globals)

            return old_from_string(*args, **kwargs)

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
        with self.connection():
            # Apply the monkeypatch.
            Environment.from_string = from_string
            try:
                node = self.dbt_compiler.compile_node(
                    node=node,
                    manifest=self.dbt_manifest,
                )
            except Exception as err:
                templater_logger.exception(
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
                ) from err
            finally:
                # Undo the monkeypatch.
                Environment.from_string = old_from_string

            if hasattr(node, "injected_sql"):
                # If injected SQL is present, it contains a better picture
                # of what will actually hit the database (e.g. with tests).
                # However it's not always present.
                compiled_sql = node.injected_sql
            else:
                compiled_sql = getattr(node, COMPILED_SQL_ATTRIBUTE)

            raw_sql = getattr(node, RAW_SQL_ATTRIBUTE)

            if not compiled_sql:  # pragma: no cover
                raise SQLTemplaterError(
                    "dbt templater compilation failed silently, check your "
                    "configuration by running `dbt compile` directly."
                )

            with open(fname) as source_dbt_model:
                source_dbt_sql = source_dbt_model.read()

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
            #    2. L009 linting errors when running "sqlfluff lint foo_bar.sql"
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
            setattr(node, RAW_SQL_ATTRIBUTE, source_dbt_sql)
            compiled_sql = compiled_sql + "\n" * n_trailing_newlines

            # TRICKY: dbt configures Jinja2 with keep_trailing_newline=False.
            # As documented (https://jinja.palletsprojects.com/en/3.0.x/api/),
            # this flag's behavior is: "Preserve the trailing newline when
            # rendering templates. The default is False, which causes a single
            # newline, if present, to be stripped from the end of the template."
            #
            # Below, we use "append_to_templated" to effectively "undo" this.
            raw_sliced, sliced_file, templated_sql = self.slice_file(
                source_dbt_sql,
                compiled_sql,
                config=config,
                make_template=make_template,
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
        # We have to register the connection in dbt >= 1.0.0 ourselves
        # In previous versions, we relied on the functionality removed in
        # https://github.com/dbt-labs/dbt-core/pull/4062.
        if DBT_VERSION_TUPLE >= (1, 0):
            if not self.connection_acquired:
                adapter = get_adapter(self.dbt_config)
                adapter.acquire_connection("master")
                adapter.set_relations_cache(self.dbt_manifest)
                self.connection_acquired = True
            yield
            # :TRICKY: Once connected, we never disconnect. Making multiple
            # connections during linting has proven to cause major performance
            # issues.
        else:
            yield


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
