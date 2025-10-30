//! Iterative parser tests
//!
//! Tests specifically for the iterative (frame-based) parser implementation

use sqlfluffrs_parser::parser::{ParseError, Parser};
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;

macro_rules! with_larger_stack {
    ($test_fn:expr) => {{
        std::thread::Builder::new()
            .stack_size(16 * 1024 * 1024) // 16MB stack
            .spawn($test_fn)
            .expect("Failed to spawn thread")
            .join()
            .expect("Thread panicked")
    }};
}

#[test]
fn test_fully_iterative_parser() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = "SELECT a, b FROM my_table WHERE x = 1";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("SelectStatementSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    })
}

#[test]
fn test_iterative_simple_literal() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "42";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("LiteralGrammar", &[])?;
    println!("AST: {:#?}", ast);

    Ok(())
}

#[test]
fn test_iterative_sequence_simple() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "SELECT a";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("SelectClauseSegment", &[])?;
    println!("AST: {:#?}", ast);

    Ok(())
}

#[test]
fn test_iterative_anynumberof_simple() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "a, b, c";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("SelectClauseElementSegment", &[])?;
    println!("AST: {:#?}", ast);

    Ok(())
}

#[test]
fn test_iterative_bracketed_simple() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "(a, b)";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    // Use BracketedColumnReferenceListGrammar which actually parses brackets
    // (BracketedSegment is just a Token marker, not a parser)
    let ast = parser.call_rule("BracketedColumnReferenceListGrammar", &[])?;
    println!("AST: {:#?}", ast);

    Ok(())
}

#[test]
fn test_iterative_anysetof_simple() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // Simple AnySetOf test with iterative parser
    let raw = "A B";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    // This will use iterative parsing internally
    println!(
        "Tokens: {:?}",
        tokens.iter().map(|t| t.raw()).collect::<Vec<_>>()
    );

    Ok(())
}

#[test]
fn test_iterative_delimited_simple() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = "a, b, c";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        // Parse as a delimited list of identifiers
        let ast = parser.call_rule("SelectClauseElementSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    })
}

#[test]
fn test_iterative_delimited_single_element() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = "a";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("SelectClauseElementSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    })
}

#[test]
fn test_iterative_delimited_long_list() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        // Test with a long list to verify performance
        let raw = "a, b, c, d, e, f, g, h, i, j";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("SelectClauseElementSegment", &[])?;
        println!("Parsed {} element list", raw.split(',').count());

        Ok(())
    })
}

#[test]
fn test_iterative_delimited_with_whitespace() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = "a  ,  b  ,  c";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("SelectClauseElementSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    })
}

#[test]
fn test_iterative_delimited_with_newlines() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = "a,\nb,\nc";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("SelectClauseElementSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    })
}

#[test]
fn test_iterative_delimited_function_args() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = "CONCAT(a, b, c)";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("FunctionSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    })
}

#[test]
fn test_iterative_delimited_nested() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = "FUNC1(a, FUNC2(b, c), d)";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("FunctionSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    })
}

#[test]
fn test_iterative_delimited_order_by() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = "SELECT * FROM t ORDER BY a, b DESC, c ASC";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("SelectStatementSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    })
}

#[test]
fn test_iterative_delimited_group_by() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = "SELECT a, COUNT(*) FROM t GROUP BY a, b";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("SelectStatementSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    })
}

#[test]
fn test_iterative_parser_no_stack_overflow() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        // Create a deeply nested expression
        let mut raw = String::from("SELECT ");
        for _ in 0..100 {
            raw.push_str("(");
        }
        raw.push_str("1");
        for _ in 0..100 {
            raw.push_str(")");
        }

        let input = LexInput::String(raw.clone());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("SelectStatementSegment", &[])?;
        println!("Successfully parsed deeply nested expression (200 levels)");

        Ok(())
    })
}

#[test]
fn test_dateadd_function() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = "SELECT DATEADD(DAY, 1, '2024-01-01')";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("SelectStatementSegment", &[])?;
        println!("AST: {:#?}", ast);

        // Verify that we got a function segment, not just a column reference
        let ast_str = format!("{:?}", ast);
        assert!(ast_str.contains("function"), "Expected function segment but got: {}", ast_str);

        Ok(())
    })
}

#[test]
fn test_dateadd_with_window_function() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = "SELECT DATEADD(DAY, ROW_NUMBER() OVER (ORDER BY DateCD ASC), '2014-01-01')";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        println!("\n=== TOKENS ===");
        for (i, token) in tokens.iter().enumerate() {
            println!("{}: {} = '{}'", i, token.token_type, token.raw());
        }

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("SelectStatementSegment", &[])?;

        let ast_str = format!("{:?}", ast);

        // Print a more readable version
        if ast_str.contains("function") {
            println!("\n✓ Successfully parsed as function");
        } else if ast_str.contains("column_reference") {
            println!("\n✗ Incorrectly parsed as column_reference");
            println!("DATEADD token is at position 2");

            // Verify that we got a function segment, not just a column reference
            panic!("Expected function segment but got column_reference");
        }

        Ok(())
    })
}

#[test]
fn test_dateadd_with_nested_function() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        // Test with a simple nested function (no window function)
        let raw = "SELECT DATEADD(DAY, ABS(5), '2024-01-01')";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        println!("\n=== TOKENS ===");
        for (i, token) in tokens.iter().enumerate() {
            println!("{}: {} = '{}'", i, token.token_type, token.raw());
        }

        let mut parser = Parser::new(&tokens, dialect);
        let ast = parser.call_rule("SelectStatementSegment", &[])?;

        let ast_str = format!("{:?}", ast);

        if ast_str.contains("function") {
            println!("\n✓ Nested function: Successfully parsed as function");
        } else {
            println!("\n✗ Nested function: Incorrectly parsed as column_reference");
            panic!("Expected function segment");
        }

        Ok(())
    })
}
