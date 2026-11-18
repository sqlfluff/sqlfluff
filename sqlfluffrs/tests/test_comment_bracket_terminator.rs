use std::str::FromStr;

use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

/// A block comment piece that is exactly `)` must not end the FROM search.
#[test]
fn test_bracket_in_comment_does_not_block_terminator() {
    let sql = "select a\n/*\n)\n*/\nfrom b\n";
    let dialect = Dialect::from_str("ansi").expect("Invalid dialect");
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, lex_errors) = lexer.lex(LexInput::String(sql.to_string()), false);
    assert!(lex_errors.is_empty(), "Lexer errors: {:?}", lex_errors);

    let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
    let result = parser.call_rule_as_root().expect("Parse error");
    assert!(!result.contains_unparsable());
}
