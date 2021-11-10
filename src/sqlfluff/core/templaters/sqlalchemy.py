"""Defines the templaters."""

import logging
import re
from typing import Dict, Optional, Tuple


from sqlfluff.core.errors import SQLTemplaterError

from sqlfluff.core.templaters.base import (
    RawFileSlice,
    TemplatedFile,
    TemplatedFileSlice,
)

from sqlfluff.core.templaters.base import RawTemplater

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")

# from https://github.com/sqlalchemy/sqlalchemy/blob/cf404d840c15fe167518dd884b295dc99ee26178/lib/sqlalchemy/sql/elements.py#L1756 # noqa
BIND_PARAM_REGEX = re.compile(r"(?<![:\w\x5c]):(?P<bind_param>\w+)(?!:)", re.UNICODE)


class SqlalchemyTemplater(RawTemplater):
    """A templater for sqlalchemy."""

    name = "sqlalchemy"

    def __init__(self, override_context=None, **kwargs):
        self.default_context = dict(test_value="__test__")
        self.override_context = override_context or {}

    # copy of the Python templater
    def get_context(self, config) -> Dict:
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
        # TODO here everything is a string, it's not possible to guess the
        # type and if it needs quoting, only assume the original string has proper escape

        return live_context

    def process(
        self, *, in_str: str, fname: str, config=None, formatter=None
    ) -> Tuple[Optional[TemplatedFile], list]:
        """Process a string and return a TemplatedFile.

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
        context = self.get_context(config)
        template_slices = []
        raw_slices = []
        last_pos_raw, last_pos_templated = 0, 0
        out_str = ""

        for found_param in BIND_PARAM_REGEX.finditer(in_str):
            span = found_param.span()
            param_name = found_param["bind_param"]
            last_literal_length = span[0] - last_pos_raw
            try:
                replacement = context[param_name]
            except KeyError as err:
                # TODO: Add a url here so people can get more help.
                raise SQLTemplaterError(
                    "Failure in SQLAlchemy templating: {}. Have you configured your variables?".format(
                        err
                    )
                )
            # add the literal to the slices
            template_slices.append(
                TemplatedFileSlice(
                    slice_type="literal",
                    source_slice=slice(last_pos_raw, span[0], None),
                    templated_slice=slice(
                        last_pos_templated,
                        last_pos_templated + last_literal_length,
                        None,
                    ),
                )
            )
            raw_slices.append(
                RawFileSlice(
                    raw=in_str[last_pos_raw : span[0]],
                    slice_type="literal",
                    source_idx=last_pos_raw,
                )
            )
            out_str += in_str[last_pos_raw : span[0]]
            # add the current replaced element
            start_teplate_pos = last_pos_templated + last_literal_length
            template_slices.append(
                TemplatedFileSlice(
                    slice_type="block_start",
                    source_slice=slice(span[0], span[1], None),
                    templated_slice=slice(
                        start_teplate_pos, start_teplate_pos + len(replacement), None
                    ),
                )
            )
            raw_slices.append(
                RawFileSlice(
                    raw=in_str[span[0] : span[1]],
                    slice_type="block_start",
                    source_idx=span[0],
                )
            )
            out_str += replacement
            # update the indexes
            last_pos_raw = span[1]
            last_pos_templated = start_teplate_pos + len(replacement)
        # add the last literal, if any
        if len(in_str) > last_pos_raw:
            template_slices.append(
                TemplatedFileSlice(
                    slice_type="literal",
                    source_slice=slice(last_pos_raw, len(in_str), None),
                    templated_slice=slice(
                        last_pos_templated,
                        last_pos_templated + (len(in_str) - last_pos_raw),
                        None,
                    ),
                )
            )
            raw_slices.append(
                RawFileSlice(
                    raw=in_str[last_pos_raw:],
                    slice_type="literal",
                    source_idx=last_pos_raw,
                )
            )
            out_str += in_str[last_pos_raw:]
        return (
            TemplatedFile(
                # original string
                source_str=in_str,
                # string after all replacements
                templated_str=out_str,
                # filename
                fname=fname,
                # list of TemplatedFileSlice
                sliced_file=template_slices,
                # list of RawFileSlice, same size
                raw_sliced=raw_slices,
            ),
            [],  # violations, always empty
        )
