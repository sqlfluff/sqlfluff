use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

#[test]
fn test_simple_cast() {
    env_logger::try_init().ok();

    // Simplest possible cast query
    let sql = "SELECT amount :: FLOAT FROM bear;";

    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _lex_errors) = lexer.lex(input, false);

    println!("\n=== SQL: {} ===", sql);
    println!("\n=== Total tokens: {} ===", tokens.len());
    for (i, tok) in tokens.iter().enumerate() {
        println!(
            "{:3}: {:20} is_code={:5} {:?}",
            i,
            tok.token_type,
            tok.is_code(),
            tok.raw()
        );
    }

    let dialect = Dialect::Ansi;
    let mut parser = Parser::new(&tokens, dialect);
    let ast = parser.call_rule_as_root();

    match &ast {
        Ok(node) => {
            println!("\n=== AST ===");
            println!("{:#?}", node);

            println!(
                "\n=== Parser position: {} / {} ===",
                parser.pos,
                tokens.len()
            );

            if parser.pos < tokens.len() {
                println!("\n!!! WARNING: Parser did not consume all tokens !!!");
                println!("Stopped at token {}:", parser.pos);
                if parser.pos < tokens.len() {
                    println!(
                        "{:3}: {:20} {:?}",
                        parser.pos,
                        tokens[parser.pos].token_type,
                        tokens[parser.pos].raw()
                    );
                }
            }
        }
        Err(e) => {
            println!("\n=== PARSE ERROR ===");
            println!("{:?}", e);
        }
    }

    assert!(ast.is_ok(), "Parse error: {:?}", ast.err());
    assert!(
        parser.pos >= tokens.len() - 1,
        "Parser did not consume all tokens. Stopped at {} / {} tokens (last index: {})",
        parser.pos,
        tokens.len(),
        tokens.len() - 1
    );
}
