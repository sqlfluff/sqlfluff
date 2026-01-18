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
    // Lookup the specific segment grammar by name.
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

    // Parse starting from the requested segment grammar.
    let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
    let node = parser
        .parse_table_iterative(segment_grammar.grammar_id, &[])
        .expect("parse_table_driven_iterative should not error");

    println!("PARSE_RESULT for '{}': {:?}", sql, node);

    // Recursive search for a Ref with matching segment_type
    fn find(node: &Node, expected: &str) -> bool {
        match node {
            Node::Ref { name, child, .. } => {
                if name == expected {
                    return true;
                }
                find(child, expected)
            }
            Node::Sequence { children } | Node::DelimitedList { children } => {
                children.iter().any(|c| find(c, expected))
            }
            Node::Bracketed { children, .. } => children.iter().any(|c| find(c, expected)),
            Node::Raw { token_type, .. } => token_type == expected,
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
        parse_and_find(
            "(a)",
            "BracketedColumnReferenceListGrammar",
            "ColumnReferenceSegment"
        ),
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

// --- Targeted minimal tests for Delimited/AnyNumberOf element candidate issues ---

#[test]
fn delimited_multiple_elements() {
    // Should match either a naked_identifier or a numeric_literal inside brackets.
    assert!(
        parse_and_find(
            "(abc)",
            "BracketedColumnReferenceListGrammar",
            "naked_identifier"
        ),
        "Expected naked_identifier in parse tree for BracketedColumnReferenceListGrammar"
    );
}

#[test]
fn anynumberof_bracketed_element_and_delimiter() {
    // Should match bracketed-list element, not just delimiter.
    assert!(
        parse_and_find("[1,2,3]", "ArrayLiteralSegment", "numeric_literal"),
        "Expected numeric_literal in parse tree for ArrayLiteralSegment"
    );
}

// --- Minimal table-driven test for CreateSequenceOptionsSegment ---

#[test]
fn create_sequence_options_segment_variants() {
    // INCREMENT BY <num>
    assert!(
        parse_and_find(
            "INCREMENT BY 1",
            "CreateSequenceOptionsSegment",
            "numeric_literal"
        ),
        "Expected numeric_literal in parse tree for INCREMENT BY 1"
    );
    // START [WITH] <num>
    assert!(
        parse_and_find(
            "START WITH 10",
            "CreateSequenceOptionsSegment",
            "numeric_literal"
        ),
        "Expected numeric_literal in parse tree for START WITH 10"
    );
    assert!(
        parse_and_find(
            "START 20",
            "CreateSequenceOptionsSegment",
            "numeric_literal"
        ),
        "Expected numeric_literal in parse tree for START 20 (optional WITH)"
    );
    // CACHE <num>
    assert!(
        parse_and_find("CACHE 5", "CreateSequenceOptionsSegment", "numeric_literal"),
        "Expected numeric_literal in parse tree for CACHE 5"
    );
    // NOCACHE
    assert!(
        parse_and_find("NOCACHE", "CreateSequenceOptionsSegment", "keyword"),
        "Expected keyword in parse tree for NOCACHE"
    );
    // CYCLE
    assert!(
        parse_and_find("CYCLE", "CreateSequenceOptionsSegment", "keyword"),
        "Expected keyword in parse tree for CYCLE"
    );
    // NOCYCLE
    assert!(
        parse_and_find("NOCYCLE", "CreateSequenceOptionsSegment", "keyword"),
        "Expected keyword in parse tree for NOCYCLE"
    );
}

#[test]
fn create_sequence_statement_parses() {
    // A full CREATE SEQUENCE statement with multiple options should parse
    // and the table-driven AnyNumberOf of options should accept multiple
    // occurrences including optional elements.
    let sql = "CREATE SEQUENCE my_seq START WITH 20 INCREMENT BY 1 CACHE 5 CYCLE";
    assert!(
        parse_and_find(sql, "CreateSequenceStatementSegment", "numeric_literal"),
        "Expected numeric_literal in parse tree for full CREATE SEQUENCE"
    );

    // Ensure the sequence name reference is present
    assert!(
        parse_and_find(
            sql,
            "CreateSequenceStatementSegment",
            "SequenceReferenceSegment"
        ),
        "Expected SequenceReferenceSegment in parse tree for full CREATE SEQUENCE"
    );
}

// --- DatatypeSegment table-driven tests ---

#[test]
fn datatype_time_with_tz_parses() {
    // The table-driven parse produces a `TimeWithTZGrammar` ref for this branch.
    assert!(
        parse_and_find(
            "TIMESTAMP WITH TIME ZONE",
            "DatatypeSegment",
            "TimeWithTZGrammar"
        ),
        "Expected TimeWithTZGrammar in parse tree for TIMESTAMP WITH TIME ZONE"
    );
}

#[test]
fn datatype_double_precision_parses() {
    // The parse results in `DoubleKeywordSegment` + `PrecisionKeywordSegment`.
    assert!(
        parse_and_find(
            "DOUBLE PRECISION",
            "DatatypeSegment",
            "DoubleKeywordSegment"
        ),
        "Expected DoubleKeywordSegment in parse tree for DOUBLE PRECISION"
    );
}

#[test]
fn datatype_char_varying_parses() {
    // The bracketed argument contains a numeric literal (the length).
    assert!(
        parse_and_find(
            "CHARACTER VARYING(20)",
            "DatatypeSegment",
            "numeric_literal"
        ),
        "Expected numeric_literal in parse tree for CHARACTER VARYING(20)"
    );
}

#[test]
fn datatype_unsigned_parses() {
    // The UNSIGNED token is recognized as a `data_type_identifier` token.
    assert!(
        parse_and_find("INT UNSIGNED", "DatatypeSegment", "data_type_identifier"),
        "Expected data_type_identifier in parse tree for INT UNSIGNED"
    );
}

#[test]
fn datatype_array_type_parses() {
    // `ARRAY` currently parses as an identifier in this table-driven test; check for that.
    assert!(
        parse_and_find("ARRAY", "DatatypeSegment", "data_type_identifier"),
        "Expected data_type_identifier in parse tree for ARRAY"
    );
}
