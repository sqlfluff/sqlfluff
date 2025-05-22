"""Methods for validating config dicts."""

from sqlfluff.core.config.removed import validate_config_dict_for_removed
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.types import ConfigMappingType

ALLOWABLE_LAYOUT_CONFIG_KEYS = (
    "spacing_before",
    "spacing_after",
    "spacing_within",
    "line_position",
    "align_within",
    "align_scope",
    "keyword_line_position",
    "keyword_line_position_exclusions",
)


def _validate_layout_config(config: ConfigMappingType, logging_reference: str) -> None:
    """Validate the layout config section of the config.

    We check for valid key values and for the depth of the
    structure.

    NOTE: For now we don't check that the "type" is a valid one
    to reference, or that the values are valid. For the values,
    these are likely to be rejected by the layout routines at
    runtime. The last risk area is validating that the type is
    a valid one, but that should be handled by the same as the above.
    """
    layout_section = config.get("layout", {})
    if not layout_section:
        return None

    preamble = f"Config file {logging_reference!r} set an invalid `layout` option. "
    reference = (
        "See https://docs.sqlfluff.com/en/stable/perma/layout.html"
        "#configuring-layout for more details."
    )

    if not isinstance(layout_section, dict):
        raise SQLFluffUserError(
            preamble
            + f"Found value {layout_section!r} instead of a valid layout section. "
            + reference
        )

    # The sections within layout can only be "type" (currently).
    non_type_keys = set(layout_section.keys()) - {"type"}
    type_section = layout_section.get("type", {})
    if non_type_keys or not type_section or not isinstance(type_section, dict):
        raise SQLFluffUserError(
            preamble
            + "Only sections of the form `sqlfluff:layout:type:...` are valid. "
            + reference
        )

    for layout_type, layout_section in type_section.items():
        if not isinstance(layout_section, dict):
            raise SQLFluffUserError(
                preamble
                + f"Layout config for {layout_type!r} is invalid. Expected a section. "
                + reference
            )

        invalid_keys = set(layout_section.keys()) - set(ALLOWABLE_LAYOUT_CONFIG_KEYS)
        if invalid_keys:
            raise SQLFluffUserError(
                preamble
                + f"Layout config for type {layout_type!r} is invalid. "
                + f"Found the following invalid keys: {invalid_keys}. "
                + reference
            )

        for key in ALLOWABLE_LAYOUT_CONFIG_KEYS:
            if key in layout_section:
                if isinstance(layout_section[key], dict):
                    raise SQLFluffUserError(
                        preamble
                        + f"Layout config for type {layout_type!r} is invalid. "
                        + "Found the an unexpected section rather than "
                        + f"value for {key}. "
                        + reference
                    )


def validate_config_dict(config: ConfigMappingType, logging_reference: str) -> None:
    """Validate a config dict.

    Currently we validate:
    - Removed and deprecated values.
    - Layout configuration structure.

    Using this method ensures that any later validation will also be applied.

    NOTE: Some of these method may mutate the config object where they are
    able to correct issues.
    """
    # Validate the config for any removed values
    validate_config_dict_for_removed(config, logging_reference)
    # Validate layout section
    _validate_layout_config(config, logging_reference)
