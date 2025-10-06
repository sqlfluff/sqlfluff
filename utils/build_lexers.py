"""For autogenerating rust lexers."""

import argparse
import re
from collections.abc import Callable
from typing import Optional, Union

from sqlfluff.core.dialects import dialect_selector
from sqlfluff.core.parser.lexer import LexerType


def generate_use():
    """Generates the `use` statements."""
    print("use once_cell::sync::Lazy;")
    print("use uuid::Uuid;")
    print("use crate::matcher::{LexMatcher, extract_nested_block_comment};")
    print("use crate::token::Token;")
    print("use crate::regex::RegexModeGroup;")
    print("use crate::dialect::Dialect;")


def segment_to_token_name(s: str):
    """Convert a segment class name to a token name."""
    return re.sub("([A-Z])", r"_\1", s).strip("_").lower().replace("segment", "token")


def generate_lexer(dialect: str):
    """Generate the lexers for all dialects."""
    loaded_dialect = dialect_selector(dialect)
    print(
        f"pub static {dialect.upper()}_LEXERS:"
        " Lazy<Vec<LexMatcher>> = Lazy::new(|| {"
        " vec!["
    )
    for matcher in loaded_dialect.get_lexer_matchers():
        print(f"{_as_rust_lexer_matcher(matcher, dialect.capitalize())},")
    print("]});")


def generate_reserved_keyword_list(dialect: str):
    """Generate the keywords for a dialects."""
    loaded_dialect = dialect_selector(dialect)
    print(
        f"pub static {dialect.upper()}_KEYWORDS:"
        " Lazy<Vec<String>> = Lazy::new(|| {"
        " vec!["
    )
    for kw in sorted(loaded_dialect.sets("reserved_keywords")):
        print(f'    "{kw}".to_string(),')
    print("]});")


def _as_rust_lexer_matcher(lexer_matcher: LexerType, dialect: str, is_subdivide=False):
    lexer_class = lexer_matcher.__class__.__name__
    segment_name = segment_to_token_name(lexer_matcher.segment_class.__name__)
    subdivider = (
        "Some(Box::new("
        f"{_as_rust_lexer_matcher(lexer_matcher.subdivider, dialect, True)}))"
        if lexer_matcher.subdivider
        else None
    )
    trim_post_subdivide = (
        "Some(Box::new("
        f"{_as_rust_lexer_matcher(lexer_matcher.trim_post_subdivide, dialect, True)}))"
        if lexer_matcher.trim_post_subdivide
        else None
    )

    fallback_function = {
        "block_comment": "Some(extract_nested_block_comment)",
    }

    is_match_valid_dict = {
        "block_comment": '|input| input.starts_with("/")',
        "dollar_quote": '|input| input.starts_with("$")',
        "single_quote": r"""|input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    }""",
        "double_quote": r"""|input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    }""",
        "numeric_literal": "|input| input.starts_with("
        "['x','X','.','0','1','2','3','4','5','6','7','8','9'])",
        "inline_comment": "|input| input.starts_with(['#','-','/'])",
        "escaped_single_quote": "|input| input.starts_with(['E', 'e'])",
        "meta_command": r"|input| input.starts_with(['\\'])",
        "meta_command_query_buffer": r"|input| input.starts_with(['\\'])",
        "prompt_command": """|input| input.starts_with("PROMPT")""",
    }

    trim_start: Optional[str] = lexer_matcher.segment_kwargs.get("trim_start")
    if trim_start:
        trim_start = (
            'Some(vec![String::from("' + '"), String::from("'.join(trim_start) + '")])'
        )
    trim_chars: Optional[str] = lexer_matcher.segment_kwargs.get("trim_chars")
    if trim_chars:
        trim_chars = (
            'Some(vec![String::from("' + '"), String::from("'.join(trim_chars) + '")])'
        )
    kwarg_type: Optional[str] = lexer_matcher.segment_kwargs.get("type")
    if kwarg_type:
        kwarg_type = f'Some(String::from("{kwarg_type}"))'

    quoted_value: Optional[Union[str, int]] = lexer_matcher.segment_kwargs.get(
        "quoted_value"
    )
    escape_replacements: Optional[list[tuple[str, str]]] = (
        lexer_matcher.segment_kwargs.get("escape_replacements")
    )
    casefold: Optional[Callable[[str], str]] = lexer_matcher.segment_kwargs.get(
        "casefold"
    )

    if lexer_class == "StringLexer":
        rust_fn = "string_lexer"
        template = f'"{lexer_matcher.template}"'
        fallback = ""
        is_match_valid = ""
    elif lexer_class == "RegexLexer":
        rust_fn = "regex_subdivider" if is_subdivide else "regex_lexer"
        template = f'r#"{lexer_matcher.template}"#'
        if template == r'r#"\[{2}([^[\\]|\\.)*\]{2}"#':
            template = r'r#"\[{2}([^\[\\]|\\.)*\]{2}"#'
        fallback = f"\n        {fallback_function.get(lexer_matcher.name, None)},"
        is_match_valid = (
            f"\n        {is_match_valid_dict.get(lexer_matcher.name, '|_| true')},"
        )
    else:
        raise ValueError

    if quoted_value:
        quoted_value = f'r#"{quoted_value[0]}"#', quoted_value[1]
        if quoted_value[0] == r'r#"\[{2}([^[\\]|\\.)*\]{2}"#':
            quoted_value = r'r#"\[{2}([^\[\\]|\\.)*\]{2}"#', quoted_value[1]
        if isinstance(quoted_value[1], int):
            quoted_value = (
                f"Some(({quoted_value[0]}.to_string(),"
                f" RegexModeGroup::Index({quoted_value[1]})))"
            )
        else:
            quoted_value = (
                f"Some(({quoted_value[0]}.to_string(),"
                f' RegexModeGroup::Name("{quoted_value[1]}".to_string())))'
            )

    if escape_replacements:
        escape_replacement = escape_replacements[0]
        escape_replacement = (
            f'r#"{escape_replacement[0]}"#',
            f'r#"{escape_replacement[1]}"#',
        )
        if escape_replacement[0] == r'r#"\[{2}([^[\\]|\\.)*\]{2}"#':
            escape_replacement = (
                r'r#"\[{2}([^\[\\]|\\.)*\]{2}"#',
                escape_replacement[1],
            )
        if escape_replacement[1] == r'r#"\[{2}([^[\\]|\\.)*\]{2}"#':
            escape_replacement = (
                escape_replacement[0],
                r'r#"\[{2}([^\[\\]|\\.)*\]{2}"#',
            )
        escape_replacement = (
            f"Some(({escape_replacement[0]}.to_string(),"
            f" {escape_replacement[1]}.to_string()))"
        )
    else:
        escape_replacement = None

    return f"""
    LexMatcher::{rust_fn}(
        Dialect::{dialect},
        "{lexer_matcher.name}",
        {template},
        Token::{segment_name},
        {subdivider},
        {trim_post_subdivide},
        {trim_start},
        {trim_chars},
        Uuid::new_v4().to_string(),
        {quoted_value},
        {escape_replacement},
        {casefold},{fallback}{is_match_valid}
        {kwarg_type},
    )"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build generated Rust output for a dialect."
    )
    parser.add_argument(
        "dialect",
    )
    args = parser.parse_args()
    print("/* This is a generated file! */")

    generate_use()
    print()
    generate_lexer(args.dialect)
    print()
    generate_reserved_keyword_list(args.dialect)
