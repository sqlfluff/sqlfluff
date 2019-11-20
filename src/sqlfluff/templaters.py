""" Defines the templaters """

from .errors import SQLTemplaterError

_templater_lookup = {}


def templater_selector(s=None, **kwargs):
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
    """
    This is the decorator for templaters (so they register)

    e.g.
    @register_templater()
    class RawTemplateInterface(BaseSegment):
        blah blah blah

    """
    n = cls.name
    _templater_lookup[n] = cls
    return cls


@register_templater
class RawTemplateInterface(object):
    name = 'raw'
    templater_selector = 'templater'

    def __init__(self, **kwargs):
        """ here we should load any initial config found in the root directory. The init
        function shouldn't take any arguments at this stage as we assume that it will load
        it's own config. Maybe at this stage we might allow override parameters to be passed
        to the linter at runtime from the cli - that would be the only time we would pass
        arguments in here. """
        pass

    def process(self, in_str, fname=None, config=None):
        """ fname is so that we can load any config files in the FILE directory, or in the file
        itself """
        return in_str


@register_templater
class PythonTemplateInterface(RawTemplateInterface):
    name = 'python'

    def __init__(self, override_context=None, **kwargs):
        """ here we should load any initial config found in the root directory. The init
        function shouldn't take any arguments at this stage as we assume that it will load
        it's own config. Maybe at this stage we might allow override parameters to be passed
        to the linter at runtime from the cli - that would be the only time we would pass
        arguments in here. """
        self.default_context = dict(test_value='__test__')
        self.override_context = override_context or {}
        # TODO: Load variables from file.
        # TODO: Have a way of loading functions from file. Python is unsecure,
        # suggest that we use the option of lua scripts or just them defaulting
        # to literals. Even better might be to force people to define them as jinja
        # macros. Like this: http://codyaray.com/2015/05/auto-load-jinja2-macros
        pass

    def get_context(self, fname=None, config=None):
        """ NB: fname is used for loading the config """
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
        return live_context

    def process(self, in_str, fname=None, config=None):
        """ fname is so that we can load any config files in the FILE directory, or in the
        file itself """
        live_context = self.get_context(fname=fname, config=config)
        return in_str.format(**live_context)


@register_templater
class JinjaTemplateInterface(PythonTemplateInterface):
    name = 'jinja'

    def _extract_macros_from_template(self, template, env):
        """
        Take a template string and extract any macros from it.

        Lovingly inspired by http://codyaray.com/2015/05/auto-load-jinja2-macros
        """
        from jinja2.runtime import Macro  # noqa

        # Iterate through keys exported from the loaded template string
        context = {}
        macro_template = env.from_string(template)
        # This is kind of low level and hacky but it works
        for k in macro_template.module.__dict__:
            attr = getattr(macro_template.module, k)
            # Is it a macro? If so install it at the name of the macro
            if isinstance(attr, Macro):
                context[k] = attr
        # Return the context
        return context

    def _extract_macros_from_config(self, config, env):
        """Take a config and load any macros from it."""
        if config:
            # This is now a nested section
            loaded_context = config.get_section((self.templater_selector, self.name, 'macros')) or {}
        else:
            loaded_context = {}

        # Iterate to load macros
        macro_ctx = {}
        for key in loaded_context:
            macro_ctx.update(
                self._extract_macros_from_template(
                    loaded_context[key], env=env
                )
            )
        return macro_ctx

    def process(self, in_str, fname=None, config=None):
        """
        fname is so that we can load any config files in the FILE directory, or in the
        file itself
        """
        # No need to import this unless we're using this templater
        from jinja2 import Environment, StrictUndefined  # noqa
        # We explicitly want to preserve newlines.
        env = Environment(keep_trailing_newline=True, undefined=StrictUndefined)

        ctx = self._extract_macros_from_config(config=config, env=env)
        # Apply to globals
        env.globals.update(ctx)

        template = env.from_string(in_str)
        live_context = self.get_context(fname=fname, config=config)
        try:
            out_str = template.render(**live_context)
            return out_str
        except Exception as err:
            # TODO: Add a url here so people can get more help.
            raise SQLTemplaterError(
                "Failure in Jinja templating: {0}. Have you configured your variables?".format(err))
