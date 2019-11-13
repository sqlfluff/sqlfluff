""" Defines the templaters """

_templater_lookup = {}


def templater_selector(s=None, **kwargs):
    s = s or 'raw'
    cls = _templater_lookup[s]
    # Instantiate here, optionally with kwargs
    return cls(**kwargs)


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

    def __init__(self, **kwargs):
        """ here we should load any initial config found in the root directory. The init
        function shouldn't take any arguments at this stage as we assume that it will load
        it's own config. Maybe at this stage we might allow override parameters to be passed
        to the linter at runtime from the cli - that would be the only time we would pass
        arguments in here. """
        pass

    def process(self, in_str, fname=None):
        """ fname is so that we can load any config files in the FILE directory, or in the file
        itself """
        return in_str


@register_templater
class JinjaTemplateInterface(RawTemplateInterface):
    name = 'jinja'

    def __init__(self, override_context=None, **kwargs):
        """ here we should load any initial config found in the root directory. The init
        function shouldn't take any arguments at this stage as we assume that it will load
        it's own config. Maybe at this stage we might allow override parameters to be passed
        to the linter at runtime from the cli - that would be the only time we would pass
        arguments in here. """
        self.default_context = dict(test_value='__test__')
        self.override_context = override_context or {}
        pass

    def process(self, in_str, fname=None):
        """ fname is so that we can load any config files in the FILE directory, or in the
        file itself """
        # No need to import this unless we're using this templater
        from jinja2 import Template  # noqa
        template = Template(in_str)
        loaded_context = {}
        live_context = {}
        live_context.update(self.default_context)
        live_context.update(loaded_context)
        live_context.update(self.override_context)
        return template.render(**live_context)
