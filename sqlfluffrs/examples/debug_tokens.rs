use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};

fn main() {
    let raw = "SELECT 1 + ~(~2 * 3) >= 4 + ~6+13 as val;";
    let dialect = Dialect::Ansi;
    let input = LexInput::String(raw.into());
    use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _) = lexer.lex(input, false);

    println!("Total tokens: {}", tokens.len());
    for (idx, token) in tokens.iter().enumerate() {
        println!(
            "{}: {:?} (type: {}) code={}",
            idx,
            token.raw(),
            token.get_type(),
            token.is_code()
        );
    }
}
