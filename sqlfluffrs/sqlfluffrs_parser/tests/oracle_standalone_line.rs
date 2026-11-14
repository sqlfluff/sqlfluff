use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;
use std::str::FromStr;

fn parse_oracle(sql: &str) -> String {
    let dialect = Dialect::from_str("oracle").unwrap();
    let (tokens, errors) = Lexer::for_dialect(dialect).lex(LexInput::String(sql.into()), false);
    assert!(errors.is_empty(), "{errors:?}");
    let mut parser =
        Parser::new_with_max_parse_depth(&tokens, dialect, hashbrown::HashMap::new(), 1024);
    let result = parser.call_rule_as_root().unwrap();
    assert!(!result.contains_unparsable(), "{}", result.stringify(0));
    result.stringify(0)
}

#[test]
fn oracle_slash_comment_is_division_but_bare_slash_is_a_delimiter() {
    let tree =
        parse_oracle("CREATE VIEW v AS\nSELECT 1\n/ -- division\n2 AS ratio\nFROM dual\n/\n");
    assert!(tree.contains("binary_operator"), "{tree}");
    assert!(tree.contains("slash_buffer_executor"), "{tree}");
}

#[test]
fn oracle_slash_comment_at_end_of_file_is_a_delimiter() {
    let tree = parse_oracle("CREATE VIEW v AS SELECT 1 FROM dual\n/ -- end\n");
    assert!(tree.contains("slash_buffer_executor"), "{tree}");
}

#[test]
fn oracle_slash_comment_between_statements_reaches_the_next_statement() {
    let tree = parse_oracle(
        "CREATE VIEW v AS SELECT 1 FROM dual\n/ -- end\nCREATE VIEW w AS SELECT 2 FROM dual\n",
    );
    assert_eq!(tree.matches("create_view_statement").count(), 2, "{tree}");
}

#[test]
fn oracle_slash_comment_before_a_non_statement_is_not_a_delimiter() {
    // `2` continues the expression, so the slash is a division and the batch
    // must not be cut at the comment.
    let tree =
        parse_oracle("CREATE VIEW v AS\nSELECT 1\n/ -- continues\n2 AS ratio\nFROM dual\n/\n");
    assert!(tree.contains("binary_operator"), "{tree}");
    assert!(tree.contains("slash_buffer_executor"), "{tree}");
}
