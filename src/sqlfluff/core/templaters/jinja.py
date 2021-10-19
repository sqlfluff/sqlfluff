"""Defines the templaters."""

import ast
import os.path
import logging
import importlib.util
import re
import uuid
from itertools import chain
from typing import List, Tuple, Optional

from jinja2.sandbox import SandboxedEnvironment
from jinja2 import meta, TemplateSyntaxError, TemplateError
import jinja2.nodes

from sqlfluff.core.errors import SQLTemplaterError

from sqlfluff.core.templaters.base import (
    TemplatedFile,
    RawFileSlice,
    TemplatedFileSlice,
)
from sqlfluff.core.templaters.python import PythonTemplater

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")


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
    def get_jinja_env():
        """Get a properly configured jinja environment."""
        # We explicitly want to preserve newlines.
        return SandboxedEnvironment(
            keep_trailing_newline=True,
            # The do extension allows the "do" directive
            autoescape=False,
            extensions=["jinja2.ext.do"],
        )

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

        env = self.get_jinja_env()

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

        def make_template(in_str):
            return env.from_string(in_str, globals=live_context)

        # Load the template, passing the global context.
        try:
            template = make_template(in_str)
        except TemplateSyntaxError as err:
            # Something in the template didn't parse, return the original
            # and a violation around what happened.
            (len(line) for line in in_str.split("\n")[: err.lineno])
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
        make_template = kwargs.pop("make_template", None)
        if make_template is None:
            return super().slice_file(raw_str, templated_str, config, **kwargs)

        templater_logger.info("Slicing File Template")
        templater_logger.debug("    Raw String: %r", raw_str)
        templater_logger.debug("    Templated String: %r", templated_str)
        tracer = TemplateTracer(raw_str, templated_str, make_template)
        tracer.process()
        # for ts in tracer.sliced_file:
        #     print(
        #         f"{ts.slice_type} templated:{templated_str[ts.templated_slice]!r} raw:{raw_str[ts.source_slice]!r}"
        #     )
        return tracer.raw_sliced, tracer.sliced_file, templated_str


class TemplateTracer:
    re_open_tag = re.compile(r"^\s*{[{%][\+\-]?\s*")
    re_close_tag = re.compile(r"\s*[\+\-]?[}%]}\s*$")

    def __init__(self, raw_str, templated_str, make_template):
        self.raw_str = raw_str
        self.templated_str = templated_str
        self.make_template = make_template
        self.program_counter = 0
        self.raw_sliced = self._slice_template(self.raw_str)
        self.sliced_file = []
        self.source_idx = 0

    def process(self):
        alternate_template = "".join(
            rs.alternate_code or rs.raw for rs in self.raw_sliced
        )
        # print(alternate_template)
        unique_alternate = self.make_template(alternate_template)
        template = self.make_template(self.raw_str)
        for s1, s2 in zip(template.generate(), unique_alternate.generate()):
            # print(f"actual:           {s1!r}")
            # print(f"unique alternate: {s2}")
            parts = []
            for p in s2.split("|"):
                if p:
                    try:
                        value = ast.literal_eval(p)
                    except ValueError:
                        # HACK: This typically means the template has an
                        # undefined value. We'll have a string like this:
                        # "['8ec52833861446cda98a030cac45badd', Undefined"
                        # where "Undefined" comes from Jinja. In this case, we
                        # extract the first value from the string and provide
                        # None as the second value. There may be a better way to
                        # do this, but at least this avoids a runtime crash.
                        value = ast.literal_eval(f"{p.split(',', 1)[0]}]") + [None]
                    if isinstance(value, str):
                        # E.g. "2e8577c1d045439ba8d3b9bf47561de3_83"
                        value = [value.split("_")[0], int(value.split("_")[1]), True]
                    else:
                        value.append(False)
                    parts.append(value)
            for alt_id, content_info, literal in parts:
                target_slice_idx = self.find_slice_index(alt_id)
                # s1_part = self.raw_sliced[target_slice_idx].raw
                # steps.append(self.raw_sliced[target_slice_idx])
                if literal:
                    self.move_to_slice(target_slice_idx, content_info)
                else:
                    self.move_to_slice(target_slice_idx, len(str(content_info)))
                # Sanity check that the template slices we're recording match up
                # precisely with templated_str.
                templated_slice = self.templated_str[
                    self.sliced_file[-1].templated_slice
                ]
                if templated_slice != s1:
                    raise ValueError(
                        f"Internal error: Templated slice string mismatch: {templated_slice} != {s1}"
                    )

    def find_slice_index(self, slice_identifier) -> int:
        raw_slices_search_result = [
            idx
            for idx, rs in enumerate(self.raw_sliced)
            if rs.unique_alternate_id == slice_identifier
        ]
        if len(raw_slices_search_result) != 1:
            raise ValueError(
                f"Internal error. Unable to locate slice for {slice_identifier}."
            )
        return raw_slices_search_result[0]

    def move_to_slice(self, target_slice_idx, target_slice_length):
        while self.program_counter < len(self.raw_sliced):
            self.record_trace(
                target_slice_length if self.program_counter == target_slice_idx else 0
            )
            current_raw_slice = self.raw_sliced[self.program_counter]
            if self.program_counter == target_slice_idx:
                # Reached the target slice. Go to next location and stop.
                self.program_counter += 1
                break
            elif not current_raw_slice.next_slice_indices:
                # No choice available. Go to next location.
                self.program_counter += 1
            else:
                # We have choices. Which to choose?
                candidates = []
                for next_slice_idx in chain(
                    current_raw_slice.next_slice_indices, [self.program_counter + 1]
                ):
                    if next_slice_idx > target_slice_idx:
                        # Takes us past the target. No good.
                        continue
                    candidates.append(next_slice_idx)
                candidates.sort(key=lambda c: abs(target_slice_idx - c))
                self.program_counter = candidates[0]
        # if self.program_counter == len(self.raw_sliced) and self.program_counter == target_slice_idx:
        #     # Reached the end of the template without finding target_slice_idx.
        #     import pdb; pdb.set_trace()
        #     pass

    def record_trace(self, target_slice_length):
        slice_type = self.raw_sliced[self.program_counter].slice_type
        self.sliced_file.append(
            TemplatedFileSlice(
                slice_type,
                slice(
                    self.raw_sliced[self.program_counter].source_idx,
                    self.raw_sliced[self.program_counter + 1].source_idx
                    if self.program_counter + 1 < len(self.raw_sliced)
                    else len(self.raw_str),
                ),
                slice(
                    self.source_idx,
                    self.source_idx + target_slice_length
                    # if slice_type not in ("literal", "templated")
                    # else self.source_idx + target_slice_length,
                ),
            )
        )
        if slice_type in ("literal", "templated"):
            self.source_idx += target_slice_length

    @classmethod
    def _slice_template(cls, in_str: str) -> List[RawFileSlice]:
        """Slice template in jinja.

        NB: Starts and ends of blocks are not distinguished.
        """
        env = JinjaTemplater.get_jinja_env()
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
        stack = []
        result = []
        set_idx = None
        for _, elem_type, raw in env.lex(in_str):
            # Replace literal text with a unique ID, except for "set"
            # statements, which don't emit output and thus don't need this
            # treatment.
            if elem_type == "data":
                if set_idx is None:
                    unique_alternate_id = uuid.uuid4().hex
                    alternate_code = f"'{unique_alternate_id}_{len(raw)}'|"
                else:
                    unique_alternate_id = None
                    alternate_code = None
                result.append(
                    RawFileSlice(
                        raw,
                        "literal",
                        idx,
                        unique_alternate_id=unique_alternate_id,
                        alternate_code=alternate_code,
                    )
                )
                idx += len(raw)
                continue
            str_buff += raw

            if elem_type.endswith("_begin"):
                # When a "begin" tag (whether block, comment, or data) uses
                # whitespace stripping
                # (https://jinja.palletsprojects.com/en/3.0.x/templates/#whitespace-control),
                # the Jinja lex() function handles this by discarding adjacent
                # whitespace from in_str. For more insight, see the tokeniter()
                # function in this file:
                # https://github.com/pallets/jinja/blob/main/src/jinja2/lexer.py
                # We want to detect and correct for this in order to:
                # - Correctly update "idx" (if this is wrong, that's a
                #   potential DISASTER because lint fixes use this info to
                #   update the source file, and incorrect values often result in
                #   CORRUPTING the user's file so it's no longer valid SQL. :-O
                # - Guarantee that the slices we return fully "cover" the
                #   contents of in_str.
                #
                # We detect skipped characters by looking ahead in in_str for
                # the token just returned from lex(). The token text will either
                # be at the current 'idx' position (if whitespace stripping did
                # not occur) OR it'll be farther along in in_str, but we're
                # GUARANTEED that lex() only skips over WHITESPACE; nothing else.

                # Find the token returned. Did lex() skip over any characters?
                num_chars_skipped = in_str.index(raw, idx) - idx
                if num_chars_skipped:
                    # Yes. It skipped over some characters. Compute a string
                    # containing the skipped characters.
                    skipped_str = in_str[idx : idx + num_chars_skipped]

                    # Sanity check: Verify that Jinja only skips over
                    # WHITESPACE, never anything else.
                    if not skipped_str.isspace():  # pragma: no cover
                        templater_logger.warning(
                            "Jinja lex() skipped non-whitespace: %s", skipped_str
                        )
                    # Treat the skipped whitespace as a literal.
                    result.append(RawFileSlice(skipped_str, "literal", idx))
                    idx += num_chars_skipped

            # raw_end and raw_begin behave a little differently in
            # that the whole tag shows up in one go rather than getting
            # parts of the tag at a time.
            unique_alternate_id = None
            alternate_code = None
            if elem_type.endswith("_end") or elem_type == "raw_begin":
                block_type = block_types[elem_type]
                block_subtype = None
                # Handle starts and ends of blocks
                if block_type in ("block", "templated"):
                    # Trim off the brackets and then the whitespace
                    m_open = cls.re_open_tag.search(str_buff)
                    m_close = cls.re_close_tag.search(str_buff)
                    trimmed_content = ""
                    if m_open and m_close:
                        trimmed_content = str_buff[
                            len(m_open.group(0)) : -len(m_close.group(0))
                        ]
                    if block_type == "block":
                        if trimmed_content.startswith("end"):
                            block_type = "block_end"
                        elif trimmed_content.startswith("el"):
                            # else, elif
                            block_type = "block_mid"
                        else:
                            block_type = "block_start"
                            if trimmed_content.split()[0] == "for":
                                block_subtype = "loop"
                    else:
                        # For "templated", evaluate the content in case of side
                        # effects, but return a UUID.
                        if trimmed_content:
                            unique_id = uuid.uuid4().hex
                            unique_alternate_id = unique_id
                            alternate_code = f"{m_open.group(0)}[{unique_id!r}, {trimmed_content}]{m_close.group(0)}|"
                if block_type == "block_start" and trimmed_content.split()[0] == "set":
                    set_idx = len(result)
                elif block_type == "block_end" and set_idx is not None:
                    set_idx = None
                m = re.search(r"\s+$", raw, re.MULTILINE | re.DOTALL)
                if raw.startswith("-") and m:
                    # Right whitespace was stripped. Split off the trailing
                    # whitespace into a separate slice. The desired behavior is
                    # to behave similarly as the left stripping case above.
                    # Note that the stakes are a bit different, because lex()
                    # hasn't *omitted* any characters from the strings it
                    # returns, it has simply grouped them differently than we
                    # want.
                    trailing_chars = len(m.group(0))
                    result.append(
                        RawFileSlice(
                            str_buff[:-trailing_chars],
                            block_type,
                            idx,
                            block_subtype,
                            unique_alternate_id=unique_alternate_id,
                            alternate_code=alternate_code,
                        )
                    )
                    block_idx = len(result) - 1
                    idx += len(str_buff) - trailing_chars
                    result.append(
                        RawFileSlice(str_buff[-trailing_chars:], "literal", idx)
                    )
                    idx += trailing_chars
                else:
                    result.append(
                        RawFileSlice(
                            str_buff,
                            block_type,
                            idx,
                            block_subtype,
                            unique_alternate_id=unique_alternate_id,
                            alternate_code=alternate_code,
                        )
                    )
                    block_idx = len(result) - 1
                    idx += len(str_buff)
                if block_type == "block_start" and trimmed_content.split()[0] in (
                    "for",
                    "if",
                ):
                    stack.append(block_idx)
                elif block_type == "block_mid":
                    # Record potential forward jump over this block.
                    result[stack[-1]].next_slice_indices.append(block_idx)
                    stack.pop()
                    stack.append(block_idx)
                elif block_type == "block_end" and trimmed_content.split()[0] in (
                    "endfor",
                    "endif",
                ):
                    # Record potential forward jump over this block.
                    result[stack[-1]].next_slice_indices.append(block_idx)
                    if result[stack[-1]].slice_subtype == "loop":
                        # Record potential backward jump to the loop beginning.
                        result[block_idx].next_slice_indices.append(stack[-1])
                    stack.pop()
                str_buff = ""
        return result
