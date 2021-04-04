"""Defines the templaters."""

import os.path
import logging
import importlib.util
from typing import Iterator, Tuple, Optional

from jinja2.sandbox import SandboxedEnvironment
from jinja2 import meta, TemplateSyntaxError, TemplateError
import jinja2.nodes

from sqlfluff.core.errors import SQLTemplaterError
from sqlfluff.core.parser import FilePositionMarker

from sqlfluff.core.templaters.base import (
    register_templater,
    TemplatedFile,
    RawFileSlice,
)
from sqlfluff.core.templaters.python import PythonTemplater

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")


@register_templater
class JinjaTemplater(PythonTemplater):
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

    def _extract_libraries_from_config(self, config):
        library_path = config.get_section(
            (self.templater_selector, self.name, "library_path")
        )
        if not library_path:
            return {}

        libraries = {}
        for file_name in os.listdir(library_path):
            file_path = os.path.join(library_path, file_name)
            if not os.path.isfile(file_path) or not file_name.endswith(".py"):
                continue

            module_name = os.path.splitext(file_name)[0]
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            lib = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lib)
            libraries[module_name] = lib

        return libraries

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
        """Crawl the tree looking for occurrences of the undeclared values."""
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

    def process(
        self, *, in_str: str, fname: Optional[str] = None, config=None
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

        """
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

        env = self._get_jinja_env()

        # Load macros from path (if applicable)
        macros_path = config.get_section(
            (self.templater_selector, self.name, "load_macros_from_path")
        )
        if macros_path:
            live_context.update(
                self._extract_macros_from_path(macros_path, env=env, ctx=live_context)
            )

        # Load config macros, these will take precedence over macros from the path
        live_context.update(
            self._extract_macros_from_config(config=config, env=env, ctx=live_context)
        )

        live_context.update(self._extract_libraries_from_config(config=config))

        # Load the template, passing the global context.
        try:
            template = env.from_string(in_str, globals=live_context)
        except TemplateSyntaxError as err:
            # Something in the template didn't parse, return the original
            # and a violation around what happened.
            (len(line) for line in in_str.split("\n")[: err.lineno])
            return (
                TemplatedFile(source_str=in_str, fname=fname),
                [
                    SQLTemplaterError(
                        "Failure to parse jinja template: {0}.".format(err),
                        pos=FilePositionMarker(
                            None,
                            err.lineno,
                            None,
                            # Calculate the charpos for sorting.
                            sum(
                                len(line)
                                for line in in_str.split("\n")[: err.lineno - 1]
                            ),
                        ),
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
            for val in self._crawl_tree(syntax_tree, undefined_variables, in_str):
                violations.append(val)

        try:
            # NB: Passing no context. Everything is loaded when the template is loaded.
            out_str = template.render()
            # Slice the file once rendered.
            raw_sliced, sliced_file, out_str = self.slice_file(
                in_str, out_str, config=config
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
                        "Unrecoverable failure in Jinja templating: {0}. Have you configured "
                        "your variables? https://docs.sqlfluff.com/en/latest/configuration.html"
                    ).format(err)
                )
            )
            return None, violations

    @classmethod
    def _slice_template(cls, in_str: str) -> Iterator[RawFileSlice]:
        """Slice template in jinja.

        NB: Starts and ends of blocks are not distinguished.
        """
        env = cls._get_jinja_env()
        str_buff = ""
        idx = 0
        # We decide the "kind" of element we're dealing with
        # using it's _closing_ tag rather than it's opening
        # tag. The types here map back to similar types of
        # sections in the python slicer.
        block_types = {
            "variable_end": "templated",
            "block_end": "block",
            "comment_end": "comment",
            # Raw tags should behave like blocks. Note that
            # raw_end and raw_begin are whole tags rather
            # than blocks and comments where we get partial
            # tags.
            "raw_end": "block",
            "raw_begin": "block",
        }
        # https://jinja.palletsprojects.com/en/2.11.x/api/#jinja2.Environment.lex
        for _, elem_type, raw in env.lex(in_str):
            if elem_type == "data":
                yield RawFileSlice(raw, "literal", idx)
                idx += len(raw)
                continue
            str_buff += raw
            # raw_end and raw_begin behave a little differently in
            # that the whole tag shows up in one go rather than getting
            # parts of the tag at a time.
            if elem_type.endswith("_end") or elem_type == "raw_begin":
                block_type = block_types[elem_type]
                # Handle starts and ends of blocks
                if block_type == "block":
                    # Trim off the brackets and then the whitespace
                    trimmed_content = str_buff[2:-2].strip()
                    if trimmed_content.startswith("end"):
                        block_type = "block_end"
                    elif trimmed_content.startswith("el"):
                        # else, elif
                        block_type = "block_mid"
                    else:
                        block_type = "block_start"
                yield RawFileSlice(str_buff, block_type, idx)
                idx += len(str_buff)
                str_buff = ""
