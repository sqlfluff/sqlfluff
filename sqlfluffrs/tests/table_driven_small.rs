use env_logger;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::Lexer;
use sqlfluffrs_parser::parser::{Node, Parser};
use sqlfluffrs_types::RootGrammar;

/// Parse `sql` using a specific segment grammar (table-driven) and return
/// true if a `Ref` node with `segment_type == expected` is present.
fn parse_and_find(sql: &str, grammar_name: &str, expected: &str) -> bool {
    let _ = env_logger::builder().is_test(true).try_init();

    // Prepare dialect and root grammar
    let dialect = Dialect::Ansi;
    let root = dialect.get_root_grammar();
    // Lookup the specific segment grammar by name. This helper is intended
    // to exercise table-driven grammars only and will error if the segment
    // grammar is Arc-based (the Arc-based path is tested elsewhere).
    let segment_grammar = dialect
        .get_segment_grammar(grammar_name)
        .unwrap_or_else(|| panic!("segment grammar '{}' not found", grammar_name));

    // Lex
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, _violations) =
        lexer.lex(sqlfluffrs_lexer::LexInput::String(sql.to_string()), true);

    // Print tokens for debugging
    for (i, t) in tokens.iter().enumerate() {
        eprintln!("TOK[{}]: '{}' ({})", i, t.raw(), t.get_type());
    }

    // Parse starting from the requested segment grammar and require it be
    // table-driven.
    let mut parser = Parser::new_with_root(&tokens, dialect, root);
    let node = match segment_grammar {
        RootGrammar::TableDriven { grammar_id, .. } => parser
            .parse_table_driven_iterative(grammar_id, &[])
            .expect("parse_table_driven_iterative should not error"),
        _ => panic!(
            "table_driven_small tests must be run against table-driven grammars; '{}' is Arc-based",
            grammar_name
        ),
    };

    println!("PARSE_RESULT for '{}': {:?}", sql, node);

    // Recursive search for a Ref with matching segment_type
    fn find(node: &Node, expected: &str) -> bool {
        match node {
            Node::Ref {
                segment_type,
                child,
                ..
            } => {
                if let Some(st) = segment_type {
                    if st == expected {
                        return true;
                    }
                }
                find(child, expected)
            }
            Node::Sequence { children } | Node::DelimitedList { children } => {
                children.iter().any(|c| find(c, expected))
            }
            Node::Bracketed { children, .. } => children.iter().any(|c| find(c, expected)),
            Node::Token { token_type, .. } => token_type == expected,
            Node::Empty | Node::Meta { .. } => false,
            // Fallback for any other node kinds
            _ => false,
        }
    }

    find(&node, expected)
}

#[test]
fn typed_parses() {
    assert!(
        parse_and_find("1", "NumericLiteralSegment", "numeric_literal"),
        "Expected numeric_literal in parse tree for '1'"
    );
}

#[test]
fn single_delimited_parses() {
    assert!(
        parse_and_find("abc", "ObjectReferenceSegment", "naked_identifier"),
        "Expected naked_identifier in parse tree for 'abc'"
    );
}

#[test]
fn string_parses() {
    assert!(
        parse_and_find("SELECT", "SelectKeywordSegment", "keyword"),
        "Expected keyword in parse tree for 'select'"
    );
}

#[test]
fn oneof_first_parses() {
    assert!(
        parse_and_find("DISTINCT", "SelectClauseModifierSegment", "keyword"),
        "Expected keyword in parse tree for 'DISTINCT'"
    );
}

#[test]
fn oneof_second_parses() {
    assert!(
        parse_and_find("ALL", "SelectClauseModifierSegment", "keyword"),
        "Expected keyword in parse tree for 'ALL'"
    );
}

#[test]
fn seq_no_allow_gaps_parses() {
    assert!(
        parse_and_find("||", "ConcatSegment", "PipeSegment"),
        "Expected PipeSegment in parse tree for '||'"
    );
}

#[test]
fn oneof_first_seq_parses() {
    assert!(
        parse_and_find("!=", "NotEqualToSegment", "RawNotSegment"),
        "Expected RawNotSegment in parse tree for '!='"
    );
}

#[test]
fn oneof_second_seq_parses() {
    assert!(
        parse_and_find("<>", "NotEqualToSegment", "RawLessThanSegment"),
        "Expected RawLessThanSegment in parse tree for '<>'"
    );
}

#[test]
fn bracketed_delimited_parses() {
    assert!(
        parse_and_find("(a)", "BracketedColumnReferenceListGrammar", "ColumnReferenceSegment"),
        "Expected ColumnReferenceSegment in parse tree for BracketedColumnReferenceListGrammar"
    );
}

#[test]
fn empty_bracketed_parses() {
    assert!(
        parse_and_find("()", "EmptyStructLiteralBracketsSegment", "end_bracket"),
        "Expected end_bracket in parse tree for EmptyStructLiteralBracketsSegment"
    );
}

#[test]
fn anynumberof_parses() {
    assert!(
        parse_and_find("[1][2]", "AccessorGrammar", "NumericLiteralSegment"),
        "Expected NumericLiteralSegment in parse tree for AccessorGrammar"
    );
}
