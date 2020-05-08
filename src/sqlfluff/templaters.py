"""Defines the templaters."""

import os.path
import ast

from .errors import SQLTemplaterError
from .parser import FilePositionMarker

_templater_lookup = {}


def templater_selector(s=None, **kwargs):
    """Instantitate a new templater by name."""
    s = s or 'jinja'  # default to jinja
    try:
        cls = _templater_lookup[s]
        # Instantiate here, optionally with kwargs
        return cls(**kwargs)
    except KeyError:
        raise ValueError(
            "Requested templater {0!r} which is not currently available. Try one of {1}".format(
                s, ', '.join(_templater_lookup.keys())
            ))


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

    name = 'raw'
    templater_selector = 'templater'

    def __init__(self, **kwargs):
        """Placeholder init function.

        Here we should load any initial config found in the root directory. The init
        function shouldn't take any arguments at this stage as we assume that it will load
        it's own config. Maybe at this stage we might allow override parameters to be passed
        to the linter at runtime from the cli - that would be the only time we would pass
        arguments in here.
        """

    @staticmethod
    def process(in_str, fname=None, config=None):
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

    name = 'python'

    def __init__(self, override_context=None, **kwargs):
        self.default_context = dict(test_value='__test__')
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
            loaded_context = config.get_section((self.templater_selector, self.name, 'context')) or {}
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

    def process(self, in_str, fname=None, config=None):
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
                "Failure in Python templating: {0}. Have you configured your variables?".format(err))


@register_templater
class JinjaTemplateInterface(PythonTemplateInterface):
    """A templater using the jinja2 library.

    See: https://jinja.palletsprojects.com/
    """

    name = 'jinja'

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
            with open(path, 'r') as opened_file:
                template = opened_file.read()
            # Update the context with macros from the file.
            macro_ctx.update(
                cls._extract_macros_from_template(
                    template, env=env, ctx=ctx
                )
            )
        else:
            # It's a directory. Iterate through files in it and extract from them.
            for dirpath, _, files in os.walk(path):
                for fname in files:
                    if fname.endswith('.sql'):
                        macro_ctx.update(cls._extract_macros_from_path(
                            os.path.join(dirpath, fname),
                            env=env, ctx=ctx
                        ))
        return macro_ctx

    def _extract_macros_from_config(self, config, env, ctx):
        """Take a config and load any macros from it."""
        if config:
            # This is now a nested section
            loaded_context = config.get_section((self.templater_selector, self.name, 'macros')) or {}
        else:
            loaded_context = {}

        # Iterate to load macros
        macro_ctx = {}
        for value in loaded_context.values():
            macro_ctx.update(
                self._extract_macros_from_template(
                    value, env=env, ctx=ctx
                )
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
            name = 'this_model'
            schema = 'this_schema'
            database = 'this_database'

            def __str__(self):
                return self.name

        dbt_builtins = {
            # `is_incremental()` renders as False, always in this case.
            # TODO: This means we'll never parse the other part of the query,
            # so we should find a solution to that. Perhaps forcing the file
            # to be parsed TWICE if it uses this variable.
            'is_incremental': lambda: False,
            'this': ThisEmulator()
        }
        return dbt_builtins

    def process(self, in_str, fname=None, config=None):
        """Process a string and return the new string.

        Args:
            in_str (:obj:`str`): The input string.
            fname (:obj:`str`, optional): The filename of this string. This is
                mostly for loading config files at runtime.
            config (:obj:`FluffConfig`): A specific config to use for this
                templating operation. Only necessary for some templaters.

        """
        # No need to import this unless we're using this templater
        from jinja2.sandbox import SandboxedEnvironment  # noqa
        from jinja2 import meta  # noqa
        import jinja2.nodes  # noqa 
        # We explicitly want to preserve newlines.
        env = SandboxedEnvironment(
            keep_trailing_newline=True,
            # The do extension allows the "do" directive
            autoescape=False, extensions=['jinja2.ext.do']
        )

        if not config:
            raise ValueError("For the jinja templater, the `process()` method requires a config object.")

        # Load the context
        live_context = self.get_context(fname=fname, config=config)
        # Apply dbt builtin functions if we're allowed.
        apply_dbt_builtins = config.get_section((self.templater_selector, self.name, 'apply_dbt_builtins'))
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
        macros_path = config.get_section((self.templater_selector, self.name, 'load_macros_from_path'))
        if macros_path:
            ctx.update(self._extract_macros_from_path(macros_path, env=env, ctx=live_context))
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
                "Failure in identifying Jinja variables: {0}.".format(err))

        # Get rid of any that *are* actually defined.
        for val in live_context:
            if val in undefined_variables:
                undefined_variables.remove(val)

        if undefined_variables:
            # Lets go through and find out where they are:
            def _crawl_tree(tree, variable_names, raw):
                """Crawl the tree looking for occurances of the undeclared values."""
                for elem in tree.iter_child_nodes():
                    yield from _crawl_tree(elem, variable_names, raw)
                else:
                    if isinstance(tree, jinja2.nodes.Name) and tree.name in variable_names:
                        line_no = tree.lineno
                        line = raw.split('\n')[line_no - 1]
                        pos = line.index(tree.name) + 1
                        # Generate the charpos. +1 is for the newline characters themselves
                        charpos = sum(len(raw_line) + 1 for raw_line in raw.split('\n')[:line_no - 1]) + pos
                        # NB: The positions returned here will be *inconsistent* with those
                        # from the linter at the moment, because these are references to the
                        # structure of the file *before* templating.
                        yield SQLTemplaterError(
                            "Undefined jinja template variable: {0!r}".format(tree.name),
                            pos=FilePositionMarker(None, line_no, pos, charpos)
                        )
            for val in _crawl_tree(ast, undefined_variables, in_str):
                violations.append(val)

        try:
            # NB: Passing no context. Everything is loaded when the template is loaded.
            out_str = template.render()
            return out_str, violations
        except Exception as err:
            # TODO: Add a url here so people can get more help.
            violations.append(
                SQLTemplaterError(
                    ("Unrecoverable failure in Jinja templating: {0}. Have you configured "
                     "your variables? https://docs.sqlfluff.com/en/latest/configuration.html").format(err))
            )
            return None, violations
