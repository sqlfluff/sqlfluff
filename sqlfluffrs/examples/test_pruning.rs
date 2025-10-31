use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

fn main() {
    env_logger::init();

    let sql =
        "SELECT DATEADD(DAY, ROW_NUMBER() OVER (ORDER BY DateCD ASC), '2014-01-01') AS dt FROM boo";
    let dialect = Dialect::Ansi;

    println!("Parsing: {}", sql);
    println!("==========================================\n");

    let input = LexInput::String(sql.into());
    use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _) = lexer.lex(input, false);

    println!("Token count: {}", tokens.len());
    for (i, token) in tokens.iter().enumerate() {
        if token.is_code() {
            println!("  [{}] {:?} = {:?}", i, token.get_type(), token.raw());
        }
    }
    println!("");

    let mut parser = Parser::new(&tokens, dialect);
    match parser.call_rule("FileSegment", &[]) {
        Ok(ast) => {
            println!("\n=== PARSE SUCCESS ===");
            println!("{:#?}", ast);
        }
        Err(e) => {
            println!("\n=== PARSE FAILED ===");
            println!("Error: {:?}", e);
        }
    }
}
