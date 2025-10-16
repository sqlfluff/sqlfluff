use sqlfluffrs::lexer::{Lexer, LexInput};
use sqlfluffrs::dialect::Dialect;

fn main() {
    let raw = "SELECT  \t*\n  FROM\n\ttable_name  ";
    let dialect = Dialect::Ansi;
    let input = LexInput::String(raw.into());
    let lexer = Lexer::new(None, dialect);
    let (tokens, _) = lexer.lex(input, false);

    println!("Total tokens: {}", tokens.len());
    for (idx, token) in tokens.iter().enumerate() {
        println!("{}: {:?} (type: {})", idx, token.raw(), token.get_type());
    }
}
