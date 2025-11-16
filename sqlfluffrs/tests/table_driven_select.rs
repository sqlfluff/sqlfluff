use env_logger;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::Lexer;
use sqlfluffrs_parser::parser::Parser;

#[test]
fn table_driven_select_parses() {
    let _ = env_logger::builder().is_test(true).try_init();

    // Prepare SQL and dialect
    let sql = "SELECT 1";
    let dialect = Dialect::Ansi;

    // Use the table-driven root grammar so parsing is started from the top-level
    // table-driven grammar (this exercises the table-driven parser path).
    let root = dialect.get_root_grammar();

    // Build a lexer for the dialect
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, _violations) =
        lexer.lex(sqlfluffrs_lexer::LexInput::String(sql.to_string()), true);

    // Print tokens for debugging
    for (i, t) in tokens.iter().enumerate() {
        eprintln!("TOK[{}]: '{}' ({})", i, t.raw(), t.get_type());
    }

    // Create parser using the RootGrammar
    let mut parser = Parser::new_with_root(&tokens, dialect, root);

    // Parse starting from the root
    let node = parser
        .call_rule_as_root()
        .expect("parse_root should not error");
    eprintln!("PARSE_RESULT: {:?}", node);

    assert!(!node.is_empty(), "Expected non-empty parse for 'SELECT 1'");

    // Ensure the numeric literal `1` was parsed as a token somewhere in the tree.
    // Define a small recursive helper to find a Token node with raw == "1".
    fn contains_numeric_one(n: &sqlfluffrs_parser::parser::Node) -> Option<(String, usize)> {
        use sqlfluffrs_parser::parser::Node;
        match n {
            Node::Token {
                token_type,
                raw,
                token_idx,
            } => {
                if raw == "1" {
                    return Some((token_type.clone(), *token_idx));
                }
                None
            }
            Node::Ref { child, .. } => contains_numeric_one(child),
            Node::Sequence { children } | Node::DelimitedList { children } => {
                for c in children {
                    if let Some(found) = contains_numeric_one(c) {
                        return Some(found);
                    }
                }
                None
            }
            Node::Bracketed { children, .. } => {
                for c in children {
                    if let Some(found) = contains_numeric_one(c) {
                        return Some(found);
                    }
                }
                None
            }
            _ => None,
        }
    }

    let found = contains_numeric_one(&node);
    assert!(
        found.is_some(),
        "Expected to find numeric literal '1' in parse tree"
    );
    if let Some((token_type, token_idx)) = found {
        eprintln!(
            "Found numeric literal '1' as token_type='{}' at idx={}",
            token_type, token_idx
        );
        // Optionally check the lexer token at that index matches raw '1'
        assert_eq!(tokens[token_idx].raw(), "1");
    }
}
