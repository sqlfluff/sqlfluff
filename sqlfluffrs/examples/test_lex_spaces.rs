use sqlfluffrs_lexer::{Lexer, LexInput};
use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;

fn main() {
    let input1 = LexInput::String("bar . bar".into());
    let input2 = LexInput::String("bar \t .     bar".into());

    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());

    println!("=== Lexing 'bar . bar' ===");
    let (tokens1, _) = lexer.lex(input1, false);
    for (i, token) in tokens1.iter().enumerate() {
        println!("{}: type='{}', raw='{}', is_code={}", i, token.get_type(), token.raw(), token.is_code());
    }

    println!("\n=== Lexing 'bar \\t .     bar' ===");
    let (tokens2, _) = lexer.lex(input2, false);
    for (i, token) in tokens2.iter().enumerate() {
        println!("{}: type='{}', raw='{}', is_code={}", i, token.get_type(), token.raw(), token.is_code());
    }
}
