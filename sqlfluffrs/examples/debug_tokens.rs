use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};

fn main() {
    let raw = "SELECT  \t*\n  FROM\n\ttable_name  ";
    let dialect = Dialect::Ansi;
    let input = LexInput::String(raw.into());
    use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _) = lexer.lex(input, false);

    println!("Total tokens: {}", tokens.len());
    for (idx, token) in tokens.iter().enumerate() {
        println!("{}: {:?} (type: {})", idx, token.raw(), token.get_type());
    }
}
