//! Grammar feature tests
//!
//! Tests for specific grammar features like AnySetOf, Delimited, Bracketed, etc.

use sqlfluffrs::parser::{Grammar, Node, ParseError, ParseMode, Parser};
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
fn test_anysetof_basic() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // Very simple test: create an AnySetOf grammar manually and test it
    // AnySetOf should match "A" and "B" in any order, each at most once
    let raw = "A B";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    // Create a simple AnySetOf grammar manually
    let grammar = Grammar::AnySetOf {
        elements: vec![
            Grammar::StringParser {
                template: "A",
                token_type: "word",
                optional: false,
            },
            Grammar::StringParser {
                template: "B",
                token_type: "word",
                optional: false,
            },
        ],
        min_times: 2,       // Must match at least 2 times total
        max_times: Some(2), // At most 2 times total (one for each element)
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
    };

    // Use the internal parse method directly
    parser.use_iterative_parser = true;
    let result = parser.parse_with_grammar_cached(&grammar, &[])?;

    println!("\nParsed successfully!");
    println!("Result: {:#?}", result);

    // Should have consumed "A" and "B" tokens (and whitespace)
    assert_eq!(parser.pos, 3, "Should consume A, whitespace, and B");

    Ok(())
}

#[test]
fn test_anysetof_order_independent() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // Test that AnySetOf matches elements in any order
    let test_cases = vec!["A B", "B A"];

    for (i, raw) in test_cases.iter().enumerate() {
        println!("\n=== Test case {}: '{}' ===", i + 1, raw);

        let input = LexInput::String((*raw).into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let grammar = Grammar::AnySetOf {
            elements: vec![
                Grammar::StringParser {
                    template: "A",
                    token_type: "word",
                    optional: false,
                },
                Grammar::StringParser {
                    template: "B",
                    token_type: "word",
                    optional: false,
                },
            ],
            min_times: 2,
            max_times: Some(2),
            optional: false,
            terminators: vec![],
            reset_terminators: false,
            allow_gaps: true,
            parse_mode: ParseMode::Strict,
        };

        parser.use_iterative_parser = true;
        let result = parser.parse_with_grammar_cached(&grammar, &[])?;

        println!("Result: {:#?}", result);

        // Should consume both tokens regardless of order
        assert_eq!(
            parser.pos,
            3,
            "Should consume both A and B for test case {}",
            i + 1
        );
    }

    Ok(())
}

#[test]
fn test_anysetof_foreign_key() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        // Test parsing a foreign key constraint with ON DELETE/UPDATE clauses
        // These can appear in any order
        let raw = "FOREIGN KEY (col1) REFERENCES other_table(other_col) ON DELETE CASCADE ON UPDATE RESTRICT";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("ForeignKeyConstraintSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    })
}

#[test]
fn test_anysetof_order_independence() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        // Test that foreign key actions can appear in any order
        let test_cases = vec![
            "FOREIGN KEY (col1) REFERENCES other_table(other_col) ON DELETE CASCADE ON UPDATE RESTRICT",
            "FOREIGN KEY (col1) REFERENCES other_table(other_col) ON UPDATE RESTRICT ON DELETE CASCADE",
        ];

        for raw in test_cases {
            println!("\nTesting: {}", raw);
            let input = LexInput::String(raw.into());
            let dialect = Dialect::Ansi;
            let lexer = Lexer::new(None, dialect);
            let (tokens, _errors) = lexer.lex(input, false);

            let mut parser = Parser::new(&tokens, dialect);

            let ast = parser.call_rule("ForeignKeyConstraintSegment", &[])?;
            println!("Parsed successfully!");
            println!("AST: {:#?}", ast);
        }

        Ok(())
    })
}

#[test]
fn test_create_table_simple() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "CREATE TABLE foo (id INT)";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("CreateTableStatementSegment", &[])?;
    println!("AST: {:#?}", ast);

    Ok(())
}

#[test]
fn test_create_table_two_columns() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "CREATE TABLE foo (id INT, name VARCHAR(100))";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("CreateTableStatementSegment", &[])?;
    println!("AST: {:#?}", ast);

    Ok(())
}

#[test]
fn test_format_tree() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "SELECT a, b FROM my_table";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("SelectStatementSegment", &[])?;

    // Verify we can format the tree
    let formatted = format!("{:#?}", ast);
    assert!(!formatted.is_empty());
    println!("Formatted AST:\n{}", formatted);

    Ok(())
}

#[test]
fn test_whitespace_in_ast() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "SELECT  a  ,  b  FROM  my_table";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("SelectStatementSegment", &[])?;
    println!("AST: {:#?}", ast);

    // Verify whitespace nodes are present
    let ast_str = format!("{:?}", ast);
    assert!(ast_str.contains("Whitespace"), "AST should contain whitespace nodes");

    Ok(())
}

#[test]
fn test_keyword_tagging() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "SELECT a FROM table";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("SelectStatementSegment", &[])?;

    // Verify keywords are properly tagged
    let ast_str = format!("{:?}", ast);
    assert!(ast_str.contains("Keyword"), "AST should contain Keyword nodes");
    println!("AST with keywords: {:#?}", ast);

    Ok(())
}

#[test]
fn test_no_duplicate_whitespace_tokens() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "SELECT   a   FROM   table";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("SelectStatementSegment", &[])?;

    // Collect all token positions in AST
    fn collect_positions(node: &Node, positions: &mut Vec<usize>) {
        match node {
            Node::Keyword(_, pos) | Node::Code(_, pos) |
            Node::Whitespace(_, pos) | Node::Newline(_, pos) |
            Node::Token(_, _, pos) | Node::EndOfFile(_, pos) => {
                positions.push(*pos);
            }
            Node::Sequence(children) | Node::DelimitedList(children) |
            Node::Unparsable(_, children) => {
                for child in children {
                    collect_positions(child, positions);
                }
            }
            Node::Ref { child, .. } => {
                collect_positions(child, positions);
            }
            Node::Empty | Node::Meta(_) => {}
        }
    }

    let mut positions = Vec::new();
    collect_positions(&ast, &mut positions);

    // Check for duplicates
    let mut seen = std::collections::HashSet::new();
    for pos in &positions {
        assert!(
            seen.insert(*pos),
            "Duplicate token position {} in AST",
            pos
        );
    }

    println!("All {} positions are unique", positions.len());

    Ok(())
}
