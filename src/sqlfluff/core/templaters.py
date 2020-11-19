"""Defines the templaters."""

import os.path
import ast
from typing import Dict, Optional
from dataclasses import dataclass
from cached_property import cached_property
from functools import partial

from jinja2.sandbox import SandboxedEnvironment
from jinja2 import meta
import jinja2.nodes

from .errors import SQLTemplaterError
from .parser import FilePositionMarker

_templater_lookup: Dict[str, "RawTemplateInterface"] = {}


def templater_selector(s=None, **kwargs):
    """Instantitate a new templater by name."""
    s = s or "jinja"  # default to jinja
    try:
        cls = _templater_lookup[s]
        # Instantiate here, optionally with kwargs
        return cls(**kwargs)
    except KeyError:
        raise ValueError(
            "Requested templater {0!r} which is not currently available. Try one of {1}".format(
                s, ", ".join(_templater_lookup.keys())
            )
        )


def register_templater(cls):
    """Register a new templater by name.

    This is designed as a decorator for templaters.

    e.g.
    @register_templater()
    class RawTemplateInterface(BaseSegment):
        blah blah blah

    """
    n = cls.name
    _templater_lookup[n] = cls
    return cls


@register_templater
class RawTemplateInterface:
    """A templater which does nothing.

    This also acts as the base templating class.
    """

    name = "raw"
    templater_selector = "templater"

    def __init__(self, **kwargs):
        """Placeholder init function.

        Here we should load any initial config found in the root directory. The init
        function shouldn't take any arguments at this stage as we assume that it will load
        it's own config. Maybe at this stage we might allow override parameters to be passed
        to the linter at runtime from the cli - that would be the only time we would pass
        arguments in here.
        """

    @staticmethod
    def process(*, in_str, fname=None, config=None):
        """Process a string and return the new string.

        Args:
            in_str (:obj:`str`): The input string.
            fname (:obj:`str`, optional): The filename of this string. This is
                mostly for loading config files at runtime.
            config (:obj:`FluffConfig`): A specific config to use for this
                templating operation. Only necessary for some templaters.

        """
        return in_str, []

    def __eq__(self, other):
        """Return true if `other` is of the same class as this one.

        NB: This is useful in comparing configs.
        """
        return isinstance(other, self.__class__)


@register_templater
class PythonTemplateInterface(RawTemplateInterface):
    """A templater using python format strings.

    See: https://docs.python.org/3/library/string.html#format-string-syntax

    For the python templater we don't allow functions or macros because there isn't
    a good way of doing it securely. Use the jinja templater for this.
    """

    name = "python"

    def __init__(self, override_context=None, **kwargs):
        self.default_context = dict(test_value="__test__")
        self.override_context = override_context or {}

    @staticmethod
    def infer_type(s):
        """Infer a python type from a string ans convert.

        Given a string value, convert it to a more specific built-in Python type
        (e.g. int, float, list, dictionary) if possible.

        """
        try:
            return ast.literal_eval(s)
        except (SyntaxError, ValueError):
            return s

    def get_context(self, fname=None, config=None):
        """Get the templating context from the config."""
        # TODO: The config loading should be done outside the templater code. Here
        # is a silly place.
        if config:
            # This is now a nested section
            loaded_context = (
                config.get_section((self.templater_selector, self.name, "context"))
                or {}
            )
        else:
            loaded_context = {}
        live_context = {}
        live_context.update(self.default_context)
        live_context.update(loaded_context)
        live_context.update(self.override_context)

        # Infer types
        for k in loaded_context:
            live_context[k] = self.infer_type(live_context[k])
        return live_context

    def process(self, *, in_str, fname=None, config=None):
        """Process a string and return the new string.

        Args:
            in_str (:obj:`str`): The input string.
            fname (:obj:`str`, optional): The filename of this string. This is
                mostly for loading config files at runtime.
            config (:obj:`FluffConfig`): A specific config to use for this
                templating operation. Only necessary for some templaters.

        """
        live_context = self.get_context(fname=fname, config=config)
        try:
            return in_str.format(**live_context), []
        except KeyError as err:
            # TODO: Add a url here so people can get more help.
            raise SQLTemplaterError(
                "Failure in Python templating: {0}. Have you configured your variables?".format(
                    err
                )
            )


@register_templater
class JinjaTemplateInterface(PythonTemplateInterface):
    """A templater using the jinja2 library.

    See: https://jinja.palletsprojects.com/
    """

    name = "jinja"

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
        if not os.path.exists(path):
            raise ValueError("Path does not exist: {0}".format(path))

        macro_ctx = {}
        if os.path.isfile(path):
            # It's a file. Extract macros from it.
            with open(path, "r") as opened_file:
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
        else:
            loaded_context = {}

        # Iterate to load macros
        macro_ctx = {}
        for value in loaded_context.values():
            macro_ctx.update(
                self._extract_macros_from_template(value, env=env, ctx=ctx)
            )
        return macro_ctx

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

            def __str__(self):
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
        """Crawl the tree looking for occurances of the undeclared values."""
        # First iterate through children
        for elem in tree.iter_child_nodes():
            yield from cls._crawl_tree(elem, variable_names, raw)
        # Then assess self
        if isinstance(tree, jinja2.nodes.Name) and tree.name in variable_names:
            line_no = tree.lineno
            line = raw.split("\n")[line_no - 1]
            pos = line.index(tree.name) + 1
            # Generate the charpos. +1 is for the newline characters themselves
            charpos = (
                sum(len(raw_line) + 1 for raw_line in raw.split("\n")[: line_no - 1])
                + pos
            )
            # NB: The positions returned here will be *inconsistent* with those
            # from the linter at the moment, because these are references to the
            # structure of the file *before* templating.
            yield SQLTemplaterError(
                "Undefined jinja template variable: {0!r}".format(tree.name),
                pos=FilePositionMarker(None, line_no, pos, charpos),
            )

    def process(self, *, in_str, fname=None, config=None):
        """Process a string and return the new string.

        Args:
            in_str (:obj:`str`): The input string.
            fname (:obj:`str`, optional): The filename of this string. This is
                mostly for loading config files at runtime.
            config (:obj:`FluffConfig`): A specific config to use for this
                templating operation. Only necessary for some templaters.

        """
        # We explicitly want to preserve newlines.
        env = SandboxedEnvironment(
            keep_trailing_newline=True,
            # The do extension allows the "do" directive
            autoescape=False,
            extensions=["jinja2.ext.do"],
        )

        if not config:
            raise ValueError(
                "For the jinja templater, the `process()` method requires a config object."
            )

        # Load the context
        live_context = self.get_context(fname=fname, config=config)
        # Apply dbt builtin functions if we're allowed.
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

        # Load config macros
        ctx = self._extract_macros_from_config(config=config, env=env, ctx=live_context)
        # Load macros from path (if applicable)
        macros_path = config.get_section(
            (self.templater_selector, self.name, "load_macros_from_path")
        )
        if macros_path:
            ctx.update(
                self._extract_macros_from_path(macros_path, env=env, ctx=live_context)
            )
        live_context.update(ctx)

        # Load the template, passing the global context.
        template = env.from_string(in_str, globals=live_context)
        violations = []

        # Attempt to identify any undeclared variables
        try:
            ast = env.parse(in_str)
            undefined_variables = meta.find_undeclared_variables(ast)
        except Exception as err:
            # TODO: Add a url here so people can get more help.
            raise SQLTemplaterError(
                "Failure in identifying Jinja variables: {0}.".format(err)
            )

        # Get rid of any that *are* actually defined.
        for val in live_context:
            if val in undefined_variables:
                undefined_variables.remove(val)

        if undefined_variables:
            # Lets go through and find out where they are:
            for val in self._crawl_tree(ast, undefined_variables, in_str):
                violations.append(val)

        try:
            # NB: Passing no context. Everything is loaded when the template is loaded.
            out_str = template.render()
            return out_str, violations
        except Exception as err:
            # TODO: Add a url here so people can get more help.
            violations.append(
                SQLTemplaterError(
                    (
                        "Unrecoverable failure in Jinja templating: {0}. Have you configured "
                        "your variables? https://docs.sqlfluff.com/en/latest/configuration.html"
                    ).format(err)
                )
            )
            return None, violations


@dataclass
class DbtConfigArgs:
    """Arguments to load dbt runtime config."""

    project_dir: Optional[str] = None
    profiles_dir: Optional[str] = None
    profile: Optional[str] = None


@register_templater
class DbtTemplateInterface(PythonTemplateInterface):
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
        return node.injected_sql, []
