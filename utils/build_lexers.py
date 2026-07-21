"""For autogenerating rust lexers."""

import argparse
import re
import sys
from collections.abc import Callable
from typing import Optional, Union

from sqlfluff.core.dialects import dialect_selector
from sqlfluff.core.parser.lexer import LexerType


def generate_use():
    """Generates the `use` statements."""
    print("use once_cell::sync::Lazy;")
    print("use sqlfluffrs_types::{LexMatcher, LexMatcherConfig};")
    print("use sqlfluffrs_types::{Token, RegexModeGroup};")
    print("use sqlfluffrs_types::token::CaseFold;")


def segment_to_token_name(s: str):
    """Convert a segment class name to a token name."""
    base_name = (
        re.sub("([A-Z])", r"_\1", s).strip("_").lower().replace("segment", "token")
    )
    return base_name


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


def generate_bracket_pairs(dialect: str):
    """Generate the bracket pairs as (open, close, start, end, persists).

    Each tuple is (open raw text, close raw text, start-bracket segment type,
    end-bracket segment type, persists). Used by the Rust lexer/parser's
    bracket-matching (`matching_bracket_idx` pre-computation, the parser's
    stray-closing-bracket detection, and the Anything-grammar bracket recursion
    in core.rs), so dialect-specific brackets - e.g. snowflake's exclude bracket
    `{-`/`-}` (types start_exclude_bracket / end_exclude_bracket, persists=True),
    added to the same `bracket_pairs` set as round/square/curly - are recognised,
    typed and structurally preserved identically to the universal three rather
    than by a hardcoded ASCII trio. `persists` (round/exclude are True; square/
    curly are False) is whether the matched span is kept as a structured
    `bracketed` node vs flattened to raw siblings.
    """
    loaded_dialect = dialect_selector(dialect)
    print(
        f"pub static {dialect.upper()}_BRACKET_PAIRS:"
        " Lazy<Vec<(&'static str, &'static str, &'static str, &'static str, bool)>>"
        " = Lazy::new(|| { vec!["
    )
    for _bracket_type, start_ref, end_ref, persists in sorted(
        loaded_dialect.bracket_sets("bracket_pairs")
    ):
        start_seg = loaded_dialect.ref(start_ref)
        end_seg = loaded_dialect.ref(end_ref)
        start_template = start_seg.template
        end_template = end_seg.template
        # The segment type the parser assigns to the matched bracket, e.g.
        # "start_bracket" / "start_exclude_bracket" (matches Python's
        # StartBracketSegment / StartExcludeBracketSegment instance_types).
        start_type = (start_seg._instance_types or (start_seg.raw_class.type,))[0]
        end_type = (end_seg._instance_types or (end_seg.raw_class.type,))[0]
        print(
            f'    ("{start_template}", "{end_template}", '
            f'"{start_type}", "{end_type}", {str(bool(persists)).lower()}),'
        )
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
        "['x','X','.','0','1','2','3','4','5','6','7','8','9', "
        "'-', '+', '$', '¢', '£', '¤', '¥', '৲', '৳', '฿', '៛', "
        "'₠', '₡', '₢', '₣', '₤', '₥', '₦', '₧', '₨', '₩', '₪', "
        "'₫', '€', '₭', '₮', '₯', '₰', '₱', '﹩', '＄', "
        "'￠', '￡', '￥', '￦'])",
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

    # Convert Python casefold function to Rust CaseFold enum
    if casefold is None:
        casefold_rust = "CaseFold::None"
    elif casefold == str.upper:
        casefold_rust = "CaseFold::Upper"
    elif casefold == str.lower:
        casefold_rust = "CaseFold::Lower"
    else:
        # Unknown casefold function, default to None
        casefold_rust = "CaseFold::None"

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
        # Plural: emit every pair, not just the first - Python applies each
        # escape_replacements pair in order (RawSegment._get_normalized_value,
        # segments/raw.py), so dropping any but the first silently changes what
        # a token normalizes to on the Rust side.
        rust_pairs = []
        for pattern, replacement in escape_replacements:
            pattern, replacement = f'r#"{pattern}"#', f'r#"{replacement}"#'
            if pattern == r'r#"\[{2}([^[\\]|\\.)*\]{2}"#':
                pattern = r'r#"\[{2}([^\[\\]|\\.)*\]{2}"#'
            if replacement == r'r#"\[{2}([^[\\]|\\.)*\]{2}"#':
                replacement = r'r#"\[{2}([^\[\\]|\\.)*\]{2}"#'
            rust_pairs.append(f"({pattern}.to_string(), {replacement}.to_string())")
        escape_replacements_rust = (
            "Some(std::sync::Arc::new(vec![" + ", ".join(rust_pairs) + "]))"
        )
    else:
        escape_replacements_rust = None

    # TokenGenerator is `fn(String, PositionMarker, TokenConfig) -> Token`, which
    # every `Token::{kind}_token` constructor already matches directly.
    token_fn = f"Token::{segment_name}"

    config = f"""LexMatcherConfig {{
        subdivider: {subdivider},
        trim_post_subdivide: {trim_post_subdivide},
        trim_start: {trim_start},
        trim_chars: {trim_chars},
        quoted_value: {quoted_value},
        escape_replacements: {escape_replacements_rust},
        casefold: {casefold_rust},
        kwarg_type: {kwarg_type},
    }}"""

    return f"""
    LexMatcher::{rust_fn}(
        "{lexer_matcher.name}",
        {template},{token_fn},{fallback}{is_match_valid}
        {config},
    )"""


def generate_extract_nested_block_comments(dialect: str):
    """This function handles nested block comments.

    Since this function is now shared across all dialects, we just need
    to generate a wrapper that passes the dialect name to the shared implementation.
    """
    print(f"""
// Wrapper function that passes the dialect name to the shared implementation
fn extract_nested_block_comment(input: &str) -> Option<&str> {{
    crate::extract_nested_block_comment(input, "{dialect}")
}}""")


if __name__ == "__main__":
    sys.stdout.reconfigure(newline="\n", encoding="utf-8")  # Force LF line endings
    parser = argparse.ArgumentParser(
        description="Build generated Rust output for a dialect."
    )
    parser.add_argument(
        "dialect",
    )
    args = parser.parse_args()
    print("/* This is a generated file! */")
    print("/* Generated by `utils/build_lexers.py` via `utils/rustify.py` */")
    print("/* This process can be run via tox: `tox -e generate-rs` */")
    print("#![cfg_attr(rustfmt, rustfmt_skip)]")

    generate_use()
    print()
    generate_reserved_keyword_list(args.dialect)
    print()
    generate_lexer(args.dialect)
    print()
    generate_bracket_pairs(args.dialect)
    print()
    generate_extract_nested_block_comments(args.dialect)
