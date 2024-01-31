"""Defines the templaters."""

import copy
import importlib
import logging
import os.path
import pkgutil
import sys
from functools import reduce
from typing import Callable, Dict, Generator, Iterator, List, Optional, Set, Tuple, cast

import jinja2.nodes
from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateError,
    TemplateSyntaxError,
    meta,
)
from jinja2.exceptions import TemplateNotFound, UndefinedError
from jinja2.ext import Extension
from jinja2.sandbox import SandboxedEnvironment

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.errors import SQLBaseError, SQLFluffUserError, SQLTemplaterError
from sqlfluff.core.helpers.slice import is_zero_slice, slice_length
from sqlfluff.core.templaters.base import (
    RawFileSlice,
    TemplatedFile,
    TemplatedFileSlice,
    large_file_check,
)
from sqlfluff.core.templaters.python import PythonTemplater
from sqlfluff.core.templaters.slicers.tracer import JinjaAnalyzer, JinjaTrace

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")


class JinjaTemplater(PythonTemplater):
    """A templater using the jinja2 library.

    See: https://jinja.palletsprojects.com/
    """

    name = "jinja"

    class Libraries:
        """Mock namespace for user-defined Jinja library."""

        pass

    @staticmethod
    def _extract_macros_from_template(template, env, ctx):
        """Take a template string and extract any macros from it.

        Lovingly inspired by http://codyaray.com/2015/05/auto-load-jinja2-macros

        Raises:
            TemplateSyntaxError: If the macro we try to load has invalid
                syntax. We assume that outer functions will catch this
                exception and handle it appropriately.
        """
        from jinja2.runtime import Macro  # noqa

        # Iterate through keys exported from the loaded template string
        context = {}
        # NOTE: `env.from_string()` will raise TemplateSyntaxError if `template`
        # is invalid.
        macro_template = env.from_string(template, globals=ctx)

        # This is kind of low level and hacky but it works
        try:
            for k in macro_template.module.__dict__:
                attr = getattr(macro_template.module, k)
                # Is it a macro? If so install it at the name of the macro
                if isinstance(attr, Macro):
                    context[k] = attr
        except UndefinedError:
            # This occurs if any file in the macro path references an
            # undefined Jinja variable. It's safe to ignore this. Any
            # meaningful issues will surface later at linting time.
            pass
        # Return the context
        return context

    @classmethod
    def _extract_macros_from_path(
        cls, path: List[str], env: Environment, ctx: Dict
    ) -> dict:
        """Take a path and extract macros from it.

        Args:
            path (List[str]): A list of paths.
            env (Environment): The environment object.
            ctx (Dict): The context dictionary.

        Returns:
            dict: A dictionary containing the extracted macros.

        Raises:
            ValueError: If a path does not exist.
            SQLTemplaterError: If there is an error in the Jinja macro file.
        """
        macro_ctx = {}
        for path_entry in path:
            # Does it exist? It should as this check was done on config load.
            if not os.path.exists(path_entry):
                raise ValueError(f"Path does not exist: {path_entry}")

            if os.path.isfile(path_entry):
                # It's a file. Extract macros from it.
                with open(path_entry) as opened_file:
                    template = opened_file.read()
                # Update the context with macros from the file.
                try:
                    macro_ctx.update(
                        cls._extract_macros_from_template(template, env=env, ctx=ctx)
                    )
                except TemplateSyntaxError as err:
                    raise SQLTemplaterError(
                        f"Error in Jinja macro file {os.path.relpath(path_entry)}: "
                        f"{err.message}",
                        line_no=err.lineno,
                        line_pos=1,
                    ) from err
            else:
                # It's a directory. Iterate through files in it and extract from them.
                for dirpath, _, files in os.walk(path_entry):
                    for fname in files:
                        if fname.endswith(".sql"):
                            macro_ctx.update(
                                cls._extract_macros_from_path(
                                    [os.path.join(dirpath, fname)], env=env, ctx=ctx
                                )
                            )
        return macro_ctx

    def _extract_macros_from_config(self, config, env, ctx):
        """Take a config and load any macros from it.

        Args:
            config: The config to extract macros from.
            env: The environment.
            ctx: The context.

        Returns:
            dict: A dictionary containing the extracted macros.
        """
        if config:
            # This is now a nested section
            loaded_context = (
                config.get_section((self.templater_selector, self.name, "macros")) or {}
            )
        else:  # pragma: no cover TODO?
            loaded_context = {}

        # Iterate to load macros
        macro_ctx = {}
        for value in loaded_context.values():
            try:
                macro_ctx.update(
                    self._extract_macros_from_template(value, env=env, ctx=ctx)
                )
            except TemplateSyntaxError as err:
                raise SQLFluffUserError(
                    f"Error loading user provided macro:\n`{value}`\n> {err}."
                )
        return macro_ctx

    def _extract_libraries_from_config(self, config):
        """Extracts libraries from the given configuration.

        This function iterates over the modules in the library path and
        imports them dynamically. The imported modules are then added to a 'Libraries'
        object, which is returned as a dictionary excluding magic methods.

        Args:
            config: The configuration object.

        Returns:
            dict: A dictionary containing the extracted libraries.
        """
        # If a more global library_path is set, let that take precedence.
        library_path = config.get("library_path") or config.get_section(
            (self.templater_selector, self.name, "library_path")
        )
        if not library_path:
            return {}

        libraries = JinjaTemplater.Libraries()

        # If library_path has __init__.py we parse it as one module, else we parse it
        # a set of modules
        is_library_module = os.path.exists(os.path.join(library_path, "__init__.py"))
        library_module_name = os.path.basename(library_path)

        # Need to go one level up to parse as a module correctly
        walk_path = (
            os.path.join(library_path, "..") if is_library_module else library_path
        )

        for module_finder, module_name, _ in pkgutil.walk_packages([walk_path]):
            # skip other modules that can be near module_dir
            if is_library_module and not module_name.startswith(library_module_name):
                continue

            # import_module is deprecated as of python 3.4. This follows roughly
            # the guidance of the python docs:
            # https://docs.python.org/3/library/importlib.html#approximating-importlib-import-module
            spec = module_finder.find_spec(module_name)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            if "." in module_name:  # nested modules have `.` in module_name
                *module_path, last_module_name = module_name.split(".")
                # find parent module recursively
                parent_module = reduce(
                    lambda res, path_part: getattr(res, path_part),
                    module_path,
                    libraries,
                )

                # set attribute on module object to make jinja working correctly
                setattr(parent_module, last_module_name, module)
            else:
                # set attr on `libraries` obj to make it work in jinja nicely
                setattr(libraries, module_name, module)

        if is_library_module:
            # when library is module we have one more root module in hierarchy and we
            # remove it
            libraries = getattr(libraries, library_module_name)

        # remove magic methods from result
        return {k: v for k, v in libraries.__dict__.items() if not k.startswith("__")}

    @staticmethod
    def _generate_dbt_builtins():
        """Generate the dbt builtins which are injected in the context."""
        # This feels a bit wrong defining these here, they should probably
        # be configurable somewhere sensible. But for now they're not.
        # TODO: Come up with a better solution.

        class ThisEmulator:
            """A class which emulates the `this` class from dbt."""

            name = "this_model"
            schema = "this_schema"
            database = "this_database"

            def __str__(self) -> str:  # pragma: no cover TODO?
                return self.name

        dbt_builtins = {
            "ref": lambda *args: args[-1],
            # In case of a cross project ref in dbt, model_ref is the second
            # argument. Otherwise it is the only argument.
            "source": lambda source_name, table: f"{source_name}_{table}",
            "config": lambda **kwargs: "",
            "var": lambda variable, default="": "item",
            # `is_incremental()` renders as True, always in this case.
            # TODO: This means we'll never parse other parts of the query,
            # that are only reachable when `is_incremental()` returns False.
            # We should try to find a solution to that. Perhaps forcing the file
            # to be parsed TWICE if it uses this variable.
            "is_incremental": lambda: True,
            "this": ThisEmulator(),
        }
        return dbt_builtins

    @classmethod
    def _crawl_tree(
        cls, tree, variable_names, raw
    ) -> Generator[SQLTemplaterError, None, None]:
        """Crawl the tree looking for occurrences of the undeclared values."""
        # First iterate through children
        for elem in tree.iter_child_nodes():
            yield from cls._crawl_tree(elem, variable_names, raw)
        # Then assess self
        if (
            isinstance(tree, jinja2.nodes.Name)
            and getattr(tree, "name") in variable_names
        ):
            line_no: int = getattr(tree, "lineno")
            tree_name: str = getattr(tree, "name")
            line = raw.split("\n")[line_no - 1]
            pos = line.index(tree_name) + 1
            yield SQLTemplaterError(
                f"Undefined jinja template variable: {tree_name!r}",
                line_no=line_no,
                line_pos=pos,
            )

    def _get_jinja_env(self, config=None):
        """Get a properly configured jinja environment.

        This method returns a properly configured jinja environment. It
        first checks if the 'ignore' key is present in the config dictionary and
        if it contains the value 'templating'. If so, it creates a subclass of
        FileSystemLoader called SafeFileSystemLoader that overrides the
        get_source method to handle missing templates when templating is ignored.
        If 'ignore' is not present or does not contain 'templating', it uses the
        regular FileSystemLoader. It then sets the extensions to ['jinja2.ext.do']
        and adds the DBTTestExtension if the _apply_dbt_builtins method returns
        True. Finally, it returns a SandboxedEnvironment object with the
        specified settings.

        Args:
            config (dict, optional): A dictionary containing configuration settings.

        Returns:
            jinja2.Environment: A properly configured jinja environment.
        """
        # We explicitly want to preserve newlines.
        macros_path = self._get_macros_path(config)
        ignore_templating = config and "templating" in config.get("ignore")
        if ignore_templating:

            class SafeFileSystemLoader(FileSystemLoader):
                def get_source(self, environment, name, *args, **kwargs):
                    try:
                        if not isinstance(name, DummyUndefined):
                            return super().get_source(
                                environment, name, *args, **kwargs
                            )
                        raise TemplateNotFound(str(name))
                    except TemplateNotFound:
                        # When ignore=templating is set, treat missing files
                        # or attempts to load an "Undefined" file as the first
                        # 'base' part of the name / filename rather than failing.
                        templater_logger.debug(
                            "Providing dummy contents for Jinja macro file: %s", name
                        )
                        value = os.path.splitext(os.path.basename(str(name)))[0]
                        return value, f"{value}.sql", lambda: False

            loader = SafeFileSystemLoader(macros_path or [])
        else:
            loader = FileSystemLoader(macros_path) if macros_path else None
        extensions = ["jinja2.ext.do"]
        if self._apply_dbt_builtins(config):
            extensions.append(DBTTestExtension)

        return SandboxedEnvironment(
            keep_trailing_newline=True,
            # The do extension allows the "do" directive
            autoescape=False,
            extensions=extensions,
            loader=loader,
        )

    def _get_macros_path(self, config: FluffConfig) -> Optional[List[str]]:
        """Get the list of macros paths from the provided config object.

        This method searches for a config section specified by the
        templater_selector, name, and 'load_macros_from_path' keys. If the section is
        found, it retrieves the value associated with that section and splits it into
        a list of strings using a comma as the delimiter. The resulting list is
        stripped of whitespace and empty strings and returned. If the section is not
        found or the resulting list is empty, it returns None.

        Args:
            config (FluffConfig): The config object to search for the macros path
                section.

        Returns:
            Optional[List[str]]: The list of macros paths if found, None otherwise.
        """
        if config:
            macros_path = config.get_section(
                (self.templater_selector, self.name, "load_macros_from_path")
            )
            if macros_path:
                result = [s.strip() for s in macros_path.split(",") if s.strip()]
                if result:
                    return result
        return None

    def _get_jinja_analyzer(
        self, raw_str: str, env: Environment, config: Optional[FluffConfig] = None
    ) -> JinjaAnalyzer:
        """Creates a new object derived from JinjaAnalyzer.

        Derived classes can provide their own analyzers (e.g. to support custom Jinja
        tags).
        """
        return JinjaAnalyzer(raw_str, env)

    def _apply_dbt_builtins(self, config: FluffConfig) -> bool:
        """Check if dbt builtins should be applied from the provided config object.

        This method searches for a config section specified by the
        templater_selector, name, and 'apply_dbt_builtins' keys. If the section
        is found, it returns the value associated with that section. If the
        section is not found, it returns False.

        Args:
            config (FluffConfig): The config object to search for the apply_dbt_builtins
                section.

        Returns:
            bool: True if dbt builtins should be applied, False otherwise.
        """
        if config:
            return config.get_section(
                (self.templater_selector, self.name, "apply_dbt_builtins")
            )
        return False

    def get_context(self, fname=None, config=None, **kw) -> Dict:
        """Get the templating context from the config.

        Args:
            fname (str, optional): The name of the file.
            config (dict, optional): The configuration.
            **kw: Additional keyword arguments.

        Returns:
            dict: The templating context.
        """
        # Load the context
        env = kw.pop("env")
        live_context = super().get_context(fname=fname, config=config)
        # Apply dbt builtin functions if we're allowed.
        if config:
            # first make libraries available in the context
            # so they can be used by the macros too
            libraries = self._extract_libraries_from_config(config=config)
            live_context.update(libraries)

            if libraries.get("SQLFLUFF_JINJA_FILTERS"):
                env.filters.update(libraries.get("SQLFLUFF_JINJA_FILTERS"))

            if self._apply_dbt_builtins(config):
                # This feels a bit wrong defining these here, they should probably
                # be configurable somewhere sensible. But for now they're not.
                # TODO: Come up with a better solution.
                dbt_builtins = self._generate_dbt_builtins()
                for name in dbt_builtins:
                    # Only apply if it hasn't already been set at this stage.
                    if name not in live_context:
                        live_context[name] = dbt_builtins[name]

        # Load macros from path (if applicable)
        if config:
            macros_path = self._get_macros_path(config)
            if macros_path:
                live_context.update(
                    self._extract_macros_from_path(
                        macros_path, env=env, ctx=live_context
                    )
                )

            # Load config macros, these will take precedence over macros from the path
            live_context.update(
                self._extract_macros_from_config(
                    config=config, env=env, ctx=live_context
                )
            )

        return live_context

    def construct_render_func(
        self, fname=None, config=None
    ) -> Tuple[Environment, dict, Callable[[str], str]]:
        """Builds and returns objects needed to create and run templates.

        Args:
            fname (Optional[str]): The name of the file.
            config (Optional[dict]): The configuration settings.

        Returns:
            Tuple[Environment, dict, Callable[[str], str]]: A tuple
            containing the following:
                - env (Environment): An instance of the 'Environment' class.
                - live_context (dict): A dictionary containing the live context.
                - render_func (Callable[[str], str]): A callable function
                that is used to instantiate templates.
        """
        # Load the context
        env = self._get_jinja_env(config)
        live_context = self.get_context(fname=fname, config=config, env=env)

        def render_func(in_str: str) -> str:
            """Used by JinjaTracer to instantiate templates.

            This function is a closure capturing internal state from process().
            Note that creating templates involves quite a bit of state known to
            _this_ function but not to JinjaTracer.

            https://www.programiz.com/python-programming/closure
            """
            # Load the template, passing the global context.
            try:
                template = env.from_string(in_str, globals=live_context)
            except TemplateSyntaxError as err:  # pragma: no cover
                # Something in the template didn't parse, return the original
                # and a violation around what happened.
                # NOTE: Most parsing exceptions will be captured when we call
                # env.parse() in the .process() method. Hence this exception
                # handling should never be called.
                raise SQLTemplaterError(
                    f"Failure to parse jinja template: {err}.",
                    line_no=err.lineno,
                )
            return template.render()

        return env, live_context, render_func

    @large_file_check
    def process(
        self,
        *,
        in_str: str,
        fname: str,
        config: Optional[FluffConfig] = None,
        formatter=None,
    ) -> Tuple[Optional[TemplatedFile], list]:
        """Process a string and return the new string.

        Note that the arguments are enforced as keywords
        because Templaters can have differences in their `process`
        method signature. A Templater that only supports reading
        from a file would need the following signature:
            process(*, fname, in_str=None, config=None)
            (arguments are swapped)

        Args:
            in_str (str): The input string.
            fname (str, optional): The filename of this string. This is
                mostly for loading config files at runtime.
            config (FluffConfig): A specific config to use for this
                templating operation. Only necessary for some templaters.
            formatter (CallbackFormatter): Optional object for output.

        Raises:
            ValueError: If the 'config' argument is not provided.

        Returns:
            Tuple[Optional[TemplatedFile], list]: A tuple containing the
            templated file and a list of violations.
        """
        if not config:  # pragma: no cover
            raise ValueError(
                "For the jinja templater, the `process()` method requires a config "
                "object."
            )

        try:
            env, live_context, render_func = self.construct_render_func(
                fname=fname, config=config
            )
        except SQLTemplaterError as err:
            return None, [err]

        violations: List[SQLBaseError] = []

        # Attempt to identify any undeclared variables or syntax errors.
        # The majority of variables will be found during the _crawl_tree
        # step rather than this first Exception which serves only to catch
        # catastrophic errors.
        try:
            syntax_tree = env.parse(in_str)
            potentially_undefined_variables = meta.find_undeclared_variables(
                syntax_tree
            )
        except Exception as err:
            unrendered_out = TemplatedFile(
                source_str=in_str,
                fname=fname,
            )
            templater_error = SQLTemplaterError(
                "Failed to parse Jinja syntax. Correct the syntax or select an "
                "alternative templater."
            )
            # Capture a line number if we can.
            if isinstance(err, TemplateSyntaxError):
                templater_error.line_no = err.lineno
            return unrendered_out, [templater_error]

        undefined_variables = set()

        class UndefinedRecorder:
            """Similar to jinja2.StrictUndefined, but remembers, not fails."""

            # Tell Jinja this object is safe to call and does not alter data.
            # https://jinja.palletsprojects.com/en/2.9.x/sandbox/#jinja2.sandbox.SandboxedEnvironment.is_safe_callable
            unsafe_callable = False
            # https://jinja.palletsprojects.com/en/3.0.x/sandbox/#jinja2.sandbox.SandboxedEnvironment.is_safe_callable
            alters_data = False

            @classmethod
            def create(cls, name: str) -> "UndefinedRecorder":
                return UndefinedRecorder(name=name)

            def __init__(self, name: str) -> None:
                self.name = name

            def __str__(self) -> str:
                """Treat undefined vars as empty, but remember for later."""
                undefined_variables.add(self.name)
                return ""

            def __getattr__(self, item) -> "UndefinedRecorder":
                undefined_variables.add(self.name)
                return UndefinedRecorder(f"{self.name}.{item}")

            def __call__(self, *args, **kwargs) -> "UndefinedRecorder":
                return UndefinedRecorder(f"{self.name}()")

        Undefined = (
            UndefinedRecorder
            if "templating" not in config.get("ignore")
            else DummyUndefined
        )
        for val in potentially_undefined_variables:
            if val not in live_context:
                live_context[val] = Undefined.create(val)  # type: ignore

        try:
            # Slice the file once rendered.
            raw_sliced, sliced_file, out_str = self.slice_file(
                in_str,
                render_func=render_func,
                config=config,
            )
            if undefined_variables:
                # Lets go through and find out where they are:
                for template_err_val in self._crawl_tree(
                    syntax_tree, undefined_variables, in_str
                ):
                    violations.append(template_err_val)
            return (
                TemplatedFile(
                    source_str=in_str,
                    templated_str=out_str,
                    fname=fname,
                    sliced_file=sliced_file,
                    raw_sliced=raw_sliced,
                ),
                violations,
            )
        except (TemplateError, TypeError) as err:
            templater_logger.info("Unrecoverable Jinja Error: %s", err, exc_info=True)
            template_err: SQLBaseError = SQLTemplaterError(
                (
                    "Unrecoverable failure in Jinja templating: {}. Have you "
                    "configured your variables? "
                    "https://docs.sqlfluff.com/en/latest/configuration.html"
                ).format(err),
                # We don't have actual line number information, but specify
                # line 1 so users can ignore with "noqa" if they want. (The
                # default is line 0, which can't be ignored because it's not
                # a valid line number.)
                line_no=1,
                line_pos=1,
            )
            violations.append(template_err)
            return None, violations

    def slice_file(
        self, raw_str: str, render_func: Callable[[str], str], config=None, **kwargs
    ) -> Tuple[List[RawFileSlice], List[TemplatedFileSlice], str]:
        """Slice the file to determine regions where we can fix.

        Args:
            raw_str (str): The raw string to be sliced.
            render_func (Callable[[str], str]): The rendering function to be used.
            config (optional): Optional configuration.
            **kwargs: Additional keyword arguments.

        Returns:
            Tuple[List[RawFileSlice], List[TemplatedFileSlice], str]:
                A tuple containing a list of raw file slices, a list of
                templated file slices, and the templated string.
        """
        # The JinjaTracer slicing algorithm is more robust, but it requires
        # us to create and render a second template (not raw_str).

        templater_logger.info("Slicing File Template")
        templater_logger.debug("    Raw String: %r", raw_str[:80])
        analyzer = self._get_jinja_analyzer(raw_str, self._get_jinja_env(), config)
        tracer = analyzer.analyze(render_func)
        trace = tracer.trace(append_to_templated=kwargs.pop("append_to_templated", ""))
        return trace.raw_sliced, trace.sliced_file, trace.templated_str

    def _handle_unreached_code(
        self,
        in_str: str,
        render_func: Callable[[str], str],
        uncovered_slices: Set[int],
        append_to_templated="",
        config: Optional[FluffConfig] = None,
    ):
        """Address uncovered slices by tweaking the template to hit them.

        Args:
            in_str (:obj:`str`): The raw source file.
            render_func (:obj:`callable`): The render func for the templater.
            uncovered_slices (:obj:`set` of :obj:`int`): Indices of slices in the raw
                file which are not rendered in the original rendering. These are the
                slices we'll attempt to hit by modifying the template. NOTE: These are
                indices in the _sequence of slices_, not _character indices_ in the
                raw source file.
            append_to_templated (:obj:`str`, optional): Optional string to append
                to the templated file.
            config (:obj:`FluffConfig`, optional): Optional config object.
        """
        analyzer = self._get_jinja_analyzer(in_str, self._get_jinja_env(), config)
        tracer_copy = analyzer.analyze(render_func)

        max_variants_generated = 10
        max_variants_returned = 5
        variants: Dict[str, Tuple[int, JinjaTrace]] = {}

        # Create a mapping of the original source slices before modification so
        # we can adjust the positions post-modification.
        original_source_slices = {
            idx: raw_slice.source_slice()
            for idx, raw_slice in enumerate(tracer_copy.raw_sliced)
        }

        for uncovered_slice in sorted(uncovered_slices)[:max_variants_generated]:
            tracer_probe = copy.deepcopy(tracer_copy)
            tracer_trace = copy.deepcopy(tracer_copy)
            override_raw_slices = []
            # Find a path that takes us to 'uncovered_slice'.
            choices = tracer_probe.move_to_slice(uncovered_slice, 0)
            for branch, options in choices.items():
                tag = tracer_probe.raw_sliced[branch].tag
                if tag in ("if", "elif"):
                    # Replace the existing "if" of "elif" expression with a new,
                    # hardcoded value that hits the target slice in the template
                    # (here that is options[0]).
                    new_value = "True" if options[0] == branch + 1 else "False"
                    tracer_trace.raw_slice_info[
                        tracer_probe.raw_sliced[branch]
                    ].alternate_code = f"{{% {tag} {new_value} %}}"
                    override_raw_slices.append(branch)

            # Render and analyze the template with the overrides.
            variant_key = tuple(
                (
                    cast(str, tracer_trace.raw_slice_info[rs].alternate_code)
                    if idx in override_raw_slices
                    and tracer_trace.raw_slice_info[rs].alternate_code is not None
                    else rs.raw
                )
                for idx, rs in enumerate(tracer_trace.raw_sliced)
            )
            # In some cases (especially with nested if statements), we may
            # generate a variant that duplicates an existing variant. Skip
            # those.
            variant_raw_str = "".join(variant_key)
            if variant_raw_str not in variants:
                analyzer = self._get_jinja_analyzer(
                    variant_raw_str, self._get_jinja_env(), config
                )
                tracer_trace = analyzer.analyze(render_func)
                try:
                    trace = tracer_trace.trace(
                        append_to_templated=append_to_templated,
                    )
                except Exception:
                    # If we get an error tracing the variant, skip it. This may
                    # happen for a variety of reasons. Basically there's no
                    # guarantee that the variant will be valid Jinja.
                    continue
                else:
                    # Compute a score for the variant based on the size of initially
                    # uncovered literal slices it hits.
                    # NOTE: We need to map this back to the positions in the original
                    # file, and only have the positions in the modified file here.
                    # That means we go translate back via the slice index in raw file.

                    # First, work out the literal positions in the modified file which
                    # are now covered.
                    _covered_source_positions = {
                        tfs.source_slice.start
                        for tfs in trace.sliced_file
                        if tfs.slice_type == "literal"
                        and not is_zero_slice(tfs.templated_slice)
                    }
                    # Second, convert these back into indices so we can use them to
                    # refer to the unmodified source file.
                    _covered_raw_slice_idxs = [
                        idx
                        for idx, raw_slice in enumerate(trace.raw_sliced)
                        if raw_slice.source_idx in _covered_source_positions
                    ]

                    score = sum(
                        slice_length(original_source_slices[idx])
                        for idx in _covered_raw_slice_idxs
                        if idx in uncovered_slices
                    )

                    variants[variant_raw_str] = (score, trace)

        # Return the top-scoring variants.
        sorted_variants: List[Tuple[int, JinjaTrace]] = sorted(
            variants.values(), key=lambda v: v[0], reverse=True
        )
        for _, trace in sorted_variants[:max_variants_returned]:
            # :TRICKY: Yield variants that _look like_ they were rendered from
            # the original template, but actually were rendered from a modified
            # template. This should ensure that lint issues and fixes for the
            # variants are handled correctly and can be combined with those from
            # the original template.
            # To do this we run through modified slices and adjust their source
            # slices to correspond with the original version. We do this by referencing
            # their slice position in the original file, because we know we haven't
            # changed the number or ordering of slices, just their length/content.
            adjusted_slices: List[TemplatedFileSlice] = [
                tfs._replace(source_slice=original_source_slices[idx])
                for idx, tfs in enumerate(trace.sliced_file)
            ]
            yield (
                tracer_copy.raw_sliced,
                adjusted_slices,
                trace.templated_str,
            )

    @large_file_check
    def process_with_variants(
        self, *, in_str: str, fname: str, config=None, formatter=None
    ) -> Iterator[Tuple[Optional[TemplatedFile], List]]:
        """Process a string and return one or more variant renderings.

        Note that the arguments are enforced as keywords
        because Templaters can have differences in their
        `process` method signature.
        A Templater that only supports reading from a file
        would need the following signature:
            process(*, fname, in_str=None, config=None)
        (arguments are swapped)

        Args:
            in_str (:obj:`str`): The input string.
            fname (:obj:`str`, optional): The filename of this string. This is
                mostly for loading config files at runtime.
            config (:obj:`FluffConfig`): A specific config to use for this
                templating operation. Only necessary for some templaters.
            formatter (:obj:`CallbackFormatter`): Optional object for output.

        """
        templated_file, violations = self.process(
            in_str=in_str, fname=fname, config=config, formatter=formatter
        )
        yield templated_file, violations

        if not templated_file:
            return  # pragma: no cover

        # Find uncovered code (if any), tweak the template to hit that code.
        # First, identify the literals which _are_ covered.
        covered_literal_positions = {
            tfs.source_slice.start
            for tfs in templated_file.sliced_file
            # It's covered if it's rendered
            if not is_zero_slice(tfs.templated_slice)
        }
        templater_logger.debug(
            "Covered literal positions %s", covered_literal_positions
        )

        uncovered_literal_idxs = {
            idx
            for idx, raw_slice in enumerate(templated_file.raw_sliced)
            if raw_slice.slice_type == "literal"
            and raw_slice.source_idx not in covered_literal_positions
        }
        templater_logger.debug(
            "Uncovered literals correspond to slices %s", uncovered_literal_idxs
        )

        # NOTE: No validation required as all validation done in the `.process()`
        # call above.
        _, _, render_func = self.construct_render_func(fname=fname, config=config)

        for raw_sliced, sliced_file, templated_str in self._handle_unreached_code(
            in_str, render_func, uncovered_literal_idxs, config=config
        ):
            yield (
                TemplatedFile(
                    source_str=in_str,
                    templated_str=templated_str,
                    fname=fname,
                    sliced_file=sliced_file,
                    raw_sliced=raw_sliced,
                ),
                violations,
            )


class DummyUndefined(jinja2.Undefined):
    """Acts as a dummy value to try and avoid template failures.

    Inherits from jinja2.Undefined so Jinja's default() filter will
    treat it as a missing value, even though it has a non-empty value
    in normal contexts.
    """

    # Tell Jinja this object is safe to call and does not alter data.
    # https://jinja.palletsprojects.com/en/2.9.x/sandbox/#jinja2.sandbox.SandboxedEnvironment.is_safe_callable
    unsafe_callable = False
    # https://jinja.palletsprojects.com/en/3.0.x/sandbox/#jinja2.sandbox.SandboxedEnvironment.is_safe_callable
    alters_data = False

    def __init__(self, name) -> None:
        super().__init__()
        self.name = name

    def __str__(self) -> str:
        return self.name.replace(".", "_")

    @classmethod
    def create(cls, name) -> "DummyUndefined":
        """Factory method.

        When ignoring=templating is configured, use 'name' as the value for
        undefined variables. We deliberately avoid recording and reporting
        undefined variables as errors. Using 'name' as the value won't always
        work, but using 'name', combined with implementing the magic methods
        (such as __eq__, see above), works well in most cases.
        """
        templater_logger.debug(
            "Providing dummy value for undefined Jinja variable: %s", name
        )
        result = DummyUndefined(name)
        return result

    def __getattr__(self, item):
        """Intercept any calls to undefined attributes.

        Args:
            item (str): The name of the attribute.

        Returns:
            object: A dynamically created instance of this class.
        """
        return self.create(f"{self.name}.{item}")

    # Implement the most common magic methods. This helps avoid
    # templating errors for undefined variables.
    # https://www.tutorialsteacher.com/python/magic-methods-in-python
    def _self_impl(self, *args, **kwargs) -> "DummyUndefined":
        """Return an instance of the class itself.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            object: An instance of the class itself.
        """
        return self

    def _bool_impl(self, *args, **kwargs) -> bool:
        """Return a boolean value.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            bool: A boolean value.
        """
        return True

    __add__ = _self_impl
    __sub__ = _self_impl
    __mul__ = _self_impl
    __floordiv__ = _self_impl
    __truediv__ = _self_impl
    __mod__ = _self_impl
    __pow__ = _self_impl
    __pos__ = _self_impl
    __neg__ = _self_impl
    __lshift__ = _self_impl
    __rshift__ = _self_impl
    __getitem__ = _self_impl
    __invert__ = _self_impl
    __call__ = _self_impl
    __and__ = _bool_impl
    __or__ = _bool_impl
    __xor__ = _bool_impl
    __bool__ = _bool_impl
    __lt__ = _bool_impl
    __le__ = _bool_impl
    __eq__ = _bool_impl
    __ne__ = _bool_impl
    __ge__ = _bool_impl
    __gt__ = _bool_impl

    def __hash__(self) -> int:  # pragma: no cov
        """Return a constant hash value.

        Returns:
            int: A constant hash value.
        """
        # This is called by the "in" operator, among other things.
        return 0

    def __iter__(self):
        """Return an iterator that contains only the instance of the class itself.

        Returns:
            iterator: An iterator.
        """
        return [self].__iter__()


class DBTTestExtension(Extension):
    """Jinja extension to handle the dbt test tag."""

    tags = {"test"}

    def parse(self, parser) -> jinja2.nodes.Macro:
        """Parses out the contents of the test tag."""
        node = jinja2.nodes.Macro(lineno=next(parser.stream).lineno)
        test_name = parser.parse_assign_target(name_only=True).name

        parser.parse_signature(node)
        node.name = f"test_{test_name}"
        node.body = parser.parse_statements(("name:endtest",), drop_needle=True)
        return node
