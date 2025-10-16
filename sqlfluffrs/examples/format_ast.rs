/// Example demonstrating the format_tree() function to display AST in Python SQLFluff format
use sqlfluffrs::{
    dialect::Dialect,
    lexer::{LexInput, Lexer},
    parser::Parser,
};

fn main() {
    env_logger::init();

    let sql = "SELECT * FROM a\n";

    // Lex the SQL
    let input = LexInput::String(sql.into());
    let lexer = Lexer::new(None, Dialect::Ansi);
    let (tokens, _errors) = lexer.lex(input, false);

    // Debug: print tokens
    println!("=== Tokens ===");
    for (i, token) in tokens.iter().enumerate() {
        println!("Token {}: '{}' | {}", i, token.raw().replace('\n', "\\n"), token.get_type());
    }
    println!();

    // Parse the tokens
    let mut parser = Parser::new(&tokens, Dialect::Ansi);
    let ast = parser.call_rule("FileSegment", &[])
        .expect("Failed to parse");

    println!("=== AST ===");
    println!("{:#?}", ast);
    println!();

    // Debug: check parser position after parsing
    println!("Parser position after parsing: {} / {}", parser.pos, tokens.len());

    // Check if newline/end_of_file are in AST
    let ast_str = format!("{:?}", ast);
    println!("AST contains Newline: {}", ast_str.contains("Newline"));
    println!("AST contains EndOfFile: {}", ast_str.contains("EndOfFile"));
    println!();

    // Format and display the AST in Python SQLFluff style
    println!("=== Formatted AST ===");
    let formatted = ast.format_tree(&tokens);
    print!("{}", formatted);
    println!();
    println!("=== Last few lines should show newline and end_of_file ===");
}
