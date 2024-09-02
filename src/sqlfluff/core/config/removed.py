"""Records of deprecated and removed config variables."""

from dataclasses import dataclass
from typing import Callable, Optional, Tuple


@dataclass
class _RemovedConfig:
    old_path: Tuple[str, ...]
    warning: str
    new_path: Optional[Tuple[str, ...]] = None
    translation_func: Optional[Callable[[str], str]] = None


REMOVED_CONFIGS = [
    _RemovedConfig(
        ("rules", "L003", "hanging_indents"),
        (
            "Hanging indents are no longer supported in SQLFluff "
            "from version 2.0.0 onwards. See "
            "https://docs.sqlfluff.com/en/stable/perma/hanging_indents.html"
        ),
    ),
    _RemovedConfig(
        ("rules", "max_line_length"),
        (
            "The max_line_length config has moved "
            "from sqlfluff:rules to the root sqlfluff level."
        ),
        ("max_line_length",),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L002", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L003", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L004", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L016", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "indent_unit"),
        (
            "The indent_unit config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "indent_unit"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "LT03", "operator_new_lines"),
        (
            "Use the line_position config in the appropriate "
            "sqlfluff:layout section (e.g. sqlfluff:layout:type"
            ":binary_operator)."
        ),
        ("layout", "type", "binary_operator", "line_position"),
        (lambda x: "trailing" if x == "before" else "leading"),
    ),
    _RemovedConfig(
        ("rules", "comma_style"),
        (
            "Use the line_position config in the appropriate "
            "sqlfluff:layout section (e.g. sqlfluff:layout:type"
            ":comma)."
        ),
        ("layout", "type", "comma", "line_position"),
        (lambda x: x),
    ),
    # LT04 used to have a more specific version of the same /config itself.
    _RemovedConfig(
        ("rules", "LT04", "comma_style"),
        (
            "Use the line_position config in the appropriate "
            "sqlfluff:layout section (e.g. sqlfluff:layout:type"
            ":comma)."
        ),
        ("layout", "type", "comma", "line_position"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L003", "lint_templated_tokens"),
        "No longer used.",
    ),
    _RemovedConfig(
        ("core", "recurse"),
        "Removed as unused in production and unnecessary for debugging.",
    ),
]
