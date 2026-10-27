use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;
use std::str::FromStr;

#[test]
fn oracle_slash_comment_is_division_but_bare_slash_is_a_delimiter() {
    let dialect = Dialect::from_str("oracle").unwrap();
    let sql = "CREATE VIEW v AS\nSELECT 1\n/ -- division\n2 AS ratio\nFROM dual\n/\n";
    let (tokens, errors) = Lexer::for_dialect(dialect).lex(LexInput::String(sql.into()), false);
    assert!(errors.is_empty(), "{errors:?}");
    let mut parser =
        Parser::new_with_max_parse_depth(&tokens, dialect, hashbrown::HashMap::new(), 1024);
    let result = parser.call_rule_as_root().unwrap();
    assert!(!result.contains_unparsable(), "{}", result.stringify(0));
    let tree = result.stringify(0);
    assert!(tree.contains("binary_operator"), "{tree}");
    assert!(tree.contains("slash_buffer_executor"), "{tree}");
}
