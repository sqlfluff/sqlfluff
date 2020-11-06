"""Defines the templaters."""

import ast

from ..errors import SQLTemplaterError

from .base import RawTemplateInterface, register_templater, TemplatedFile


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

    def process(self, in_str, fname=None, config=None):
        """Process a string and return a TemplatedFile.

        Args:
            in_str (:obj:`str`): The input string.
            fname (:obj:`str`, optional): The filename of this string. This is
                mostly for loading config files at runtime.
            config (:obj:`FluffConfig`): A specific config to use for this
                templating operation. Only necessary for some templaters.

        """
        live_context = self.get_context(fname=fname, config=config)
        try:
            new_str = in_str.format(**live_context)
        except KeyError as err:
            # TODO: Add a url here so people can get more help.
            raise SQLTemplaterError(
                "Failure in Python templating: {0}. Have you configured your variables?".format(
                    err
                )
            )
        return TemplatedFile(source_str=in_str, templated_str=new_str, fname=fname), []
