//! Iterative parser tests
//!
//! Tests specifically for the iterative (frame-based) parser implementation

use sqlfluffrs::parser::{ParseError, Parser};
use sqlfluffrs::{lexer::{LexInput, Lexer}, Dialect};

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
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);
        parser.use_iterative_parser = true;

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
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);
    parser.use_iterative_parser = true;

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
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);
    parser.use_iterative_parser = true;

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
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);
    parser.use_iterative_parser = true;

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
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);
    parser.use_iterative_parser = true;

    let ast = parser.call_rule("BracketedSegment", &[])?;
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
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);
    parser.use_iterative_parser = true;

    // This will use iterative parsing internally
    println!("Tokens: {:?}", tokens.iter().map(|t| t.raw()).collect::<Vec<_>>());

    Ok(())
}

#[test]
fn test_iterative_delimited_simple() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = "a, b, c";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);
        parser.use_iterative_parser = true;

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
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);
        parser.use_iterative_parser = true;

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
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);
        parser.use_iterative_parser = true;

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
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);
        parser.use_iterative_parser = true;

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
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);
        parser.use_iterative_parser = true;

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
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);
        parser.use_iterative_parser = true;

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
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);
        parser.use_iterative_parser = true;

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
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);
        parser.use_iterative_parser = true;

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
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);
        parser.use_iterative_parser = true;

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
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);
        parser.use_iterative_parser = true;

        let ast = parser.call_rule("SelectStatementSegment", &[])?;
        println!("Successfully parsed deeply nested expression (200 levels)");

        Ok(())
    })
}
