"""For autogenerating rust parsers."""

import argparse
import re
from dataclasses import dataclass

from sqlfluff.core.dialects import dialect_selector
from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.parser.grammar.anyof import AnyNumberOf, OneOf, OptionallyBracketed
from sqlfluff.core.parser.grammar.base import Nothing, Ref
from sqlfluff.core.parser.grammar.delimited import Delimited
from sqlfluff.core.parser.grammar.sequence import Bracketed, Sequence
from sqlfluff.core.parser.parsers import (
    MultiStringParser,
    RegexParser,
    StringParser,
    TypedParser,
)
from sqlfluff.core.parser.segments.base import SegmentMetaclass
from sqlfluff.core.parser.segments.meta import Indent


@dataclass
class DummyParseContext:
    """Dummy context for parse context."""

    dialect: Dialect


def generate_use():
    """Generates the `use` statements."""
    print("use once_cell::sync::Lazy;")
    print("use crate::parser::Grammar;")


def matchable_to_const_name(s: str):
    """Convert a segment class name to a token name."""
    return re.sub(
        "_{2,}",
        "_",
        re.sub("([A-Z])", r"_\1", s).replace("-", "_").replace("$", "_").strip("_"),
    ).upper()


def generate_parser(dialect: str):
    """Generate the parser for a dialect."""
    loaded_dialect = dialect_selector(dialect)
    parse_context = DummyParseContext(loaded_dialect)
    segment_grammars = []

    for name, match_grammar in loaded_dialect._library.items():
        segment_grammars.append(f'"{name}" => Some(&{matchable_to_const_name(name)}),')
        print(f"// {name=}")
        print(
            f"pub static {matchable_to_const_name(name)}: Lazy<Grammar> = Lazy::new(|| "
        )
        _to_rust_parser_grammar(match_grammar, parse_context)
        print(");")
        print()
        # break
    segment_grammars.append("_ => None,")

    print(
        f"pub fn get_{dialect.lower()}_segment_grammar(name: &str) "
        "-> Option<&'static Grammar> {"
    )
    print("    match name {")
    for match_arm in segment_grammars:
        print(f"            {match_arm}")
    print("    }")
    print("}")


def _to_rust_parser_grammar(match_grammar, parse_context):
    # print(type(match_grammar), vars(match_grammar))
    if match_grammar.__class__ is Ref and isinstance(match_grammar, Ref):
        print("Grammar::Ref {")
        print(f'    name: "{match_grammar._ref}",')
        print(f"    optional: {str(match_grammar.optional).lower()},")
        print(f"    allow_gaps: {str(match_grammar.allow_gaps).lower()},")
        print("}")
    elif match_grammar.__class__ is StringParser:
        print("Grammar::StringParser()")
    elif match_grammar.__class__ is TypedParser:
        print("Grammar::TypedParser()")
    elif match_grammar.__class__ is MultiStringParser:
        print("Grammar::MultiStringParser()")
    elif match_grammar.__class__ is RegexParser:
        print("Grammar::RegexParser()")
    elif match_grammar.__class__ is OptionallyBracketed:
        print("Grammar::OptionallyBracketed()")
    elif match_grammar.__class__ is Nothing:
        print("Grammar::Nothing()")
    elif match_grammar.__class__ is Delimited and isinstance(match_grammar, Delimited):
        print("Grammar::Delimited {")
        print("    elements: vec![")
        for subgrammar in match_grammar._elements:
            _to_rust_parser_grammar(subgrammar, parse_context)
            print(",")
        print("    ],")
        print("    delimiter: Box::new(")
        _to_rust_parser_grammar(match_grammar.delimiter, parse_context)
        print("    ),")
        print(f"    allow_trailing: {str(match_grammar.allow_trailing).lower()},")
        print(f"    optional: {str(match_grammar.optional).lower()},")
        print("    terminators: vec![")
        for term_grammar in match_grammar.terminators:
            _to_rust_parser_grammar(term_grammar, parse_context)
            print(",")
        print("    ],")
        print(f"    allow_gaps: {str(match_grammar.allow_gaps).lower()},")
        print("}")
    elif match_grammar.__class__ is OneOf and isinstance(match_grammar, OneOf):
        print("Grammar::OneOf {")
        # print(f'    name: "{name}",')
        print("    elements: vec![")
        for subgrammar in match_grammar._elements:
            _to_rust_parser_grammar(subgrammar, parse_context)
            print(",")
        print("    ],")
        print(f"    optional: {str(match_grammar.optional).lower()},")
        print("    terminators: vec![")
        for term_grammar in match_grammar.terminators:
            _to_rust_parser_grammar(term_grammar, parse_context)
            print(",")
        print("    ],")
        print(f"    allow_gaps: {str(match_grammar.allow_gaps).lower()},")
        print("}")
    elif match_grammar.__class__ is Bracketed and isinstance(match_grammar, Bracketed):
        print("Grammar::Bracketed {")
        print("    elements: vec![")
        for subgrammar in match_grammar._elements:
            _to_rust_parser_grammar(subgrammar, parse_context)
            print(",")
        print("    ],")
        print("    bracket_pairs: (")
        print("        Box::new(")
        start_bracket, end_bracket, _ = match_grammar.get_bracket_from_dialect(
            parse_context
        )
        _to_rust_parser_grammar(
            match_grammar.start_bracket or start_bracket, parse_context
        )
        print("        ),")
        print("        Box::new(")
        _to_rust_parser_grammar(match_grammar.end_bracket or end_bracket, parse_context)
        print("        )")
        print("    ),")
        print(f"    optional: {str(match_grammar.optional).lower()},")
        print("    terminators: vec![")
        for term_grammar in match_grammar.terminators:
            _to_rust_parser_grammar(term_grammar, parse_context)
            print(",")
        print("    ],")
        print(f"    allow_gaps: {str(match_grammar.allow_gaps).lower()},")
        print("}")
    elif match_grammar.__class__ is Sequence and isinstance(match_grammar, Sequence):
        print("Grammar::Sequence {")
        print("    elements: vec![")
        for subgrammar in match_grammar._elements:
            _to_rust_parser_grammar(subgrammar, parse_context)
            print(",")
        print("    ],")
        print(f"    optional: {str(match_grammar.optional).lower()},")
        print("    terminators: vec![")
        for term_grammar in match_grammar.terminators:
            _to_rust_parser_grammar(term_grammar, parse_context)
            print(",")
        print("    ],")
        print(f"    allow_gaps: {str(match_grammar.allow_gaps).lower()},")
        print("}")
    elif match_grammar.__class__ is AnyNumberOf and isinstance(
        match_grammar, AnyNumberOf
    ):
        print("Grammar::AnyNumberOf {")
        print("    elements: vec![")
        for subgrammar in match_grammar._elements:
            _to_rust_parser_grammar(subgrammar, parse_context)
            print(",")
        print("    ],")
        print(f"    min_times: {match_grammar.min_times},")
        max_times = (
            f"Some({match_grammar.max_times})" if match_grammar.max_times else "None"
        )
        print(f"    max_times: {max_times},")
        print(f"    optional: {str(match_grammar.optional).lower()},")
        print("    terminators: vec![")
        for term_grammar in match_grammar.terminators:
            _to_rust_parser_grammar(term_grammar, parse_context)
            print(",")
        print("    ],")
        print(f"    allow_gaps: {str(match_grammar.allow_gaps).lower()},")
        print("}")
    elif isinstance(match_grammar, Indent):
        print("here")
    elif (
        match_grammar.__class__ is SegmentMetaclass
        and isinstance(match_grammar, SegmentMetaclass)
        and hasattr(match_grammar, "match_grammar")
    ):
        # print(match_grammar.match_grammar)
        _to_rust_parser_grammar(match_grammar.match_grammar, parse_context)
    else:
        print(f"// Missing elements {match_grammar=}, type:{match_grammar.__class__}")
        print("todo!()")


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
    generate_parser(args.dialect)
    print()
