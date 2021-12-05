"""Defines the templaters."""
import logging
import os.path
import pkgutil
from functools import reduce
from typing import Callable, Dict, List, Optional, Tuple

import jinja2.nodes
from jinja2 import Environment, TemplateError, TemplateSyntaxError, meta
from jinja2.environment import Template
from jinja2.sandbox import SandboxedEnvironment

from sqlfluff.core.errors import SQLTemplaterError
from sqlfluff.core.templaters.base import (
    RawFileSlice,
    TemplatedFile,
    TemplatedFileSlice,
)
from sqlfluff.core.templaters.python import PythonTemplater
from sqlfluff.core.templaters.slicers.tracer import JinjaTracer


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
        """
        from jinja2.runtime import Macro  # noqa

        # Iterate through keys exported from the loaded template string
        context = {}
        macro_template = env.from_string(template, globals=ctx)
        # This is kind of low level and hacky but it works
        for k in macro_template.module.__dict__:
            attr = getattr(macro_template.module, k)
            # Is it a macro? If so install it at the name of the macro
            if isinstance(attr, Macro):
                context[k] = attr
        # Return the context
        return context

    @classmethod
    def _extract_macros_from_path(cls, path, env, ctx):
        """Take a path and extract macros from it."""
        # Does the path exist? It should as this check was done on config load.
        if not os.path.exists(path):  # pragma: no cover
            raise ValueError(f"Path does not exist: {path}")

        macro_ctx = {}
        if os.path.isfile(path):
            # It's a file. Extract macros from it.
            with open(path) as opened_file:
                template = opened_file.read()
            # Update the context with macros from the file.
            macro_ctx.update(
                cls._extract_macros_from_template(template, env=env, ctx=ctx)
            )
        else:
            # It's a directory. Iterate through files in it and extract from them.
            for dirpath, _, files in os.walk(path):
                for fname in files:
                    if fname.endswith(".sql"):
                        macro_ctx.update(
                            cls._extract_macros_from_path(
                                os.path.join(dirpath, fname), env=env, ctx=ctx
                            )
                        )
        return macro_ctx

    def _extract_macros_from_config(self, config, env, ctx):
        """Take a config and load any macros from it."""
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
            macro_ctx.update(
                self._extract_macros_from_template(value, env=env, ctx=ctx)
            )
        return macro_ctx

    def _extract_libraries_from_config(self, config):
        library_path = config.get_section(
            (self.templater_selector, self.name, "library_path")
        )
        if not library_path:
            return {}

        libraries = JinjaTemplater.Libraries()

        # If library_path hash __init__.py we parse it as a one module, else we parse it a set of modules
        is_library_module = os.path.exists(os.path.join(library_path, "__init__.py"))
        library_module_name = os.path.basename(library_path)

        # Need to go one level up to parse as a module correctly
        walk_path = (
            os.path.join(library_path, "..") if is_library_module else library_path
        )

        for loader, module_name, is_pkg in pkgutil.walk_packages([walk_path]):
            # skip other modules that can be near module_dir
            if is_library_module and not module_name.startswith(library_module_name):
                continue

            module = loader.find_module(module_name).load_module(module_name)

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
            # when library is module we have one more root module in hierarchy and we remove it
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

            def __str__(self):  # pragma: no cover TODO?
                return self.name

        dbt_builtins = {
            # `is_incremental()` renders as False, always in this case.
            # TODO: This means we'll never parse the other part of the query,
            # so we should find a solution to that. Perhaps forcing the file
            # to be parsed TWICE if it uses this variable.
            "is_incremental": lambda: False,
            "this": ThisEmulator(),
        }
        return dbt_builtins

    @classmethod
    def _crawl_tree(cls, tree, variable_names, raw):
        """Crawl the tree looking for occurrences of the undeclared values."""
        # First iterate through children
        for elem in tree.iter_child_nodes():
            yield from cls._crawl_tree(elem, variable_names, raw)
        # Then assess self
        if isinstance(tree, jinja2.nodes.Name) and tree.name in variable_names:
            line_no = tree.lineno
            line = raw.split("\n")[line_no - 1]
            pos = line.index(tree.name) + 1
            yield SQLTemplaterError(
                f"Undefined jinja template variable: {tree.name!r}",
                line_no=line_no,
                line_pos=pos,
            )

    @staticmethod
    def _get_jinja_env():
        """Get a properly configured jinja environment."""
        # We explicitly want to preserve newlines.
        return SandboxedEnvironment(
            keep_trailing_newline=True,
            # The do extension allows the "do" directive
            autoescape=False,
            extensions=["jinja2.ext.do"],
        )

    def get_context(self, fname=None, config=None) -> Dict:
        """Get the templating context from the config."""
        # Load the context
        live_context = super().get_context(fname=fname, config=config)
        # Apply dbt builtin functions if we're allowed.
        if config:
            apply_dbt_builtins = config.get_section(
                (self.templater_selector, self.name, "apply_dbt_builtins")
            )
            if apply_dbt_builtins:
                # This feels a bit wrong defining these here, they should probably
                # be configurable somewhere sensible. But for now they're not.
                # TODO: Come up with a better solution.
                dbt_builtins = self._generate_dbt_builtins()
                for name in dbt_builtins:
                    # Only apply if it hasn't already been set at this stage.
                    if name not in live_context:
                        live_context[name] = dbt_builtins[name]

        env = self._get_jinja_env()

        # Load macros from path (if applicable)
        if config:
            macros_path = config.get_section(
                (self.templater_selector, self.name, "load_macros_from_path")
            )
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

            live_context.update(self._extract_libraries_from_config(config=config))
        return live_context

    def template_builder(
        self, fname=None, config=None
    ) -> Tuple[Environment, dict, Callable[[str], Template]]:
        """Builds and returns objects needed to create and run templates."""
        # Load the context
        live_context = self.get_context(fname=fname, config=config)
        env = self._get_jinja_env()

        def make_template(in_str):
            """Used by JinjaTracer to instantiate templates.

            This function is a closure capturing internal state from process().
            Note that creating templates involves quite a bit of state known to
            _this_ function but not to JinjaTracer.

            https://www.programiz.com/python-programming/closure
            """
            return env.from_string(in_str, globals=live_context)

        return env, live_context, make_template

    def process(
        self, *, in_str: str, fname: str, config=None, formatter=None
    ) -> Tuple[Optional[TemplatedFile], list]:
        """Process a string and return the new string.

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
        if not config:  # pragma: no cover
            raise ValueError(
                "For the jinja templater, the `process()` method requires a config object."
            )

        env, live_context, make_template = self.template_builder(
            fname=fname, config=config
        )

        # Load the template, passing the global context.
        try:
            template = make_template(in_str)
        except TemplateSyntaxError as err:
            # Something in the template didn't parse, return the original
            # and a violation around what happened.
            return (
                TemplatedFile(source_str=in_str, fname=fname),
                [
                    SQLTemplaterError(
                        f"Failure to parse jinja template: {err}.",
                        line_no=err.lineno,
                    )
                ],
            )

        violations = []

        # Attempt to identify any undeclared variables. The majority
        # will be found during the _crawl_tree step rather than this
        # first Exception which serves only to catch catastrophic errors.
        try:
            syntax_tree = env.parse(in_str)
            undefined_variables = meta.find_undeclared_variables(syntax_tree)
        except Exception as err:  # pragma: no cover
            # TODO: Add a url here so people can get more help.
            raise SQLTemplaterError(f"Failure in identifying Jinja variables: {err}.")

        # Get rid of any that *are* actually defined.
        for val in live_context:
            if val in undefined_variables:
                undefined_variables.remove(val)

        if undefined_variables:
            # Lets go through and find out where they are:
            for val in self._crawl_tree(syntax_tree, undefined_variables, in_str):
                violations.append(val)

        try:
            # NB: Passing no context. Everything is loaded when the template is loaded.
            out_str = template.render()
            # Slice the file once rendered.
            raw_sliced, sliced_file, out_str = self.slice_file(
                in_str,
                out_str,
                config=config,
                make_template=make_template,
            )
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
            templater_logger.info("Unrecoverable Jinja Error: %s", err)
            violations.append(
                SQLTemplaterError(
                    (
                        "Unrecoverable failure in Jinja templating: {}. Have you configured "
                        "your variables? https://docs.sqlfluff.com/en/latest/configuration.html"
                    ).format(err)
                )
            )
            return None, violations

    @classmethod
    def slice_file(
        cls, raw_str: str, templated_str: str, config=None, **kwargs
    ) -> Tuple[List[RawFileSlice], List[TemplatedFileSlice], str]:
        """Slice the file to determine regions where we can fix."""
        # The JinjaTracer slicing algorithm is more robust, but it requires
        # us to create and render a second template (not raw_str) and is only
        # enabled if the caller passes a make_template() function. (For now,
        # the dbt templater does not.)
        make_template = kwargs.pop("make_template", None)
        if make_template is None:
            # make_template() was not provided. Use the base class
            # implementation instead.
            return super().slice_file(raw_str, templated_str, config, **kwargs)

        templater_logger.info("Slicing File Template")
        templater_logger.debug("    Raw String: %r", raw_str)
        templater_logger.debug("    Templated String: %r", templated_str)
        tracer = JinjaTracer(raw_str, cls._get_jinja_env(), make_template)
        trace = tracer.trace()
        return trace.raw_sliced, trace.sliced_file, trace.templated_str
