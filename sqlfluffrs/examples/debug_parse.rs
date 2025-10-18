use sqlfluffrs::dialect::Dialect;
use sqlfluffrs::lexer::{LexInput, Lexer};
use sqlfluffrs::parser::Parser;

fn main() {
    env_logger::init();

    let raw = "SELECT id, name FROM users WHERE status = 'active'";
    let dialect = Dialect::Ansi;

    let input = LexInput::String(raw.into());
    let lexer = Lexer::new(None, dialect);
    let (tokens, _) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);
    parser.use_iterative_parser = true;

    match parser.call_rule("SelectStatementSegment", &[]) {
        Ok(ast) => {
            println!("Parse succeeded!");
            println!("{:#?}", ast);
        }
        Err(e) => {
            eprintln!("Parse failed: {:?}", e);
        }
    }
}
