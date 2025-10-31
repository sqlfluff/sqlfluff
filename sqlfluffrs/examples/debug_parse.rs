use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

fn main() {
    env_logger::init();

    let raw = "SELECT id, name FROM users WHERE status = 'active'";
    let dialect = Dialect::Ansi;

    let input = LexInput::String(raw.into());
    use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    match parser.call_rule("SelectStatementSegment", &[]) {
        Ok(ast) => {
            println!("Parse succeeded!");
            println!("{:#?}", ast);
        }
        Err(e) => {
            log::debug!("Parse failed: {:?}", e);
        }
    }
}
