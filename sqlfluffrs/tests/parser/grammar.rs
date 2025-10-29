//! Grammar feature tests
//!
//! Tests for specific grammar features like AnySetOf, Delimited, Bracketed, etc.

use std::sync::Arc;
use hashbrown::HashSet;
use sqlfluffrs::parser::{Grammar, Node, ParseError, ParseMode, Parser};
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
fn test_anysetof_basic() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // Very simple test: create an AnySetOf grammar manually and test it
    // AnySetOf should match "A" and "B" in any order, each at most once
    let raw = "A B";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    // Create a simple AnySetOf grammar manually
    let grammar = Arc::new(Grammar::AnySetOf {
        elements: vec![
            Arc::new(Grammar::StringParser {
                template: "A",
                raw_class: "WordSegment",
                token_type: "word",
                optional: false,
            }),
            Arc::new(Grammar::StringParser {
                template: "B",
                raw_class: "WordSegment",
                token_type: "word",
                optional: false,
            }),
        ],
        min_times: 2,       // Must match at least 2 times total
        max_times: Some(2), // At most 2 times total (one for each element)
        exclude: None,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    // Use the internal parse method directly
    let result = parser.parse_with_grammar_cached(grammar, &[])?;

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
    let test_cases = ["A B", "B A"];

    for (i, raw) in test_cases.iter().enumerate() {
        println!("\n=== Test case {}: '{}' ===", i + 1, raw);

        let input = LexInput::String((*raw).into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let grammar = Arc::new(Grammar::AnySetOf {
            elements: vec![
                Arc::new(Grammar::StringParser {
                    template: "A",
                    raw_class: "WordSegment",
                    token_type: "word",
                    optional: false,
                }),
                Arc::new(Grammar::StringParser {
                    template: "B",
                    raw_class: "WordSegment",
                    token_type: "word",
                    optional: false,
                }),
            ],
            min_times: 2,
            max_times: Some(2),
            exclude: None,
            optional: false,
            terminators: vec![],
            reset_terminators: false,
            allow_gaps: true,
            parse_mode: ParseMode::Strict,
            simple_hint: None,
        });

        let result = parser.parse_with_grammar_cached(grammar, &[])?;

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
        let raw = "REFERENCES other_table(other_col) ON DELETE CASCADE ON UPDATE RESTRICT";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("ReferenceDefinitionGrammar", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    })
}

#[test]
fn test_anysetof_order_independence() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // Test that foreign key actions can appear in any order
    let test_cases = vec![
        "REFERENCES other_table(other_col) ON DELETE CASCADE ON UPDATE RESTRICT",
        "REFERENCES other_table(other_col) ON UPDATE RESTRICT ON DELETE CASCADE",
    ];

    for raw in test_cases {
        println!("\nTesting: {}", raw);
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("ReferenceDefinitionGrammar", &[])?;
        println!("Parsed successfully!");
        println!("AST: {:#?}", ast);
    }

    Ok(())
}

#[test]
fn test_create_table_simple() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "CREATE TABLE foo (id INT)";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
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
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
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
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
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
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("SelectStatementSegment", &[])?;
    println!("AST: {:#?}", ast);

    // Verify whitespace nodes are present
    let ast_str = format!("{:?}", ast);
    assert!(
        ast_str.contains("Whitespace"),
        "AST should contain whitespace nodes"
    );

    Ok(())
}

#[test]
fn test_keyword_tagging() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "SELECT a FROM table";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("SelectStatementSegment", &[])?;

    // Verify keywords are properly tagged
    let ast_str = format!("{:?}", ast);
    assert!(
        ast_str.contains("Keyword"),
        "AST should contain Keyword nodes"
    );
    println!("AST with keywords: {:#?}", ast);

    Ok(())
}

#[test]
fn test_no_duplicate_whitespace_tokens() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "SELECT   a   FROM   table";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("SelectStatementSegment", &[])?;

    println!("AST: {:#?}", ast);

    // Collect all token positions in AST
    fn collect_positions(node: &Node, positions: &mut Vec<usize>) {
        match node {
            Node::Whitespace {
                raw: _,
                token_idx: pos,
            }
            | Node::Newline {
                raw: _,
                token_idx: pos,
            }
            | Node::Token {
                token_type: _,
                raw: _,
                token_idx: pos,
            }
            | Node::EndOfFile {
                raw: _,
                token_idx: pos,
            } => {
                positions.push(*pos);
            }
            Node::Sequence { children }
            | Node::DelimitedList { children }
            | Node::Unparsable {
                expected_message: _,
                children,
            }
            | Node::Bracketed { children } => {
                for child in children {
                    collect_positions(child, positions);
                }
            }
            Node::Ref { child, .. } => {
                collect_positions(child, positions);
            }
            Node::Empty | Node::Meta { .. } => {}
        }
    }

    let mut positions = Vec::new();
    collect_positions(&ast, &mut positions);

    // Check for duplicates
    let mut seen = HashSet::new();
    for pos in &positions {
        assert!(seen.insert(*pos), "Duplicate token position {} in AST", pos);
    }

    println!("All {} positions are unique", positions.len());

    Ok(())
}

#[test]
fn test_delimited_basic() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // Input: A,B,C
    let raw = "A,B,C";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    // Delimiter: comma
    let delimiter = Arc::new(Grammar::StringParser {
        template: ",",
        raw_class: "SymbolSegment",
        token_type: "comma",
        optional: false,
    });
    // Element: word (A, B, C)
    let element = Arc::new(Grammar::RegexParser {
        template: regex::RegexBuilder::new("[A-Z]+").case_insensitive(true).build().unwrap(),
        raw_class: "WordSegment",
        token_type: "word",
        anti_template: None,
        optional: false,
    });
    let grammar = Arc::new(Grammar::Delimited {
        elements: vec![element],
        delimiter: Box::new(delimiter),
        allow_trailing: false,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: false,
        min_delimiters: 0,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let result = parser.parse_with_grammar_cached(grammar, &[])?;
    println!("\nDelimited parse result: {:#?}", result);

    // Should produce a DelimitedList with 5 children: A, comma, B, comma, C
    match result {
        Node::DelimitedList { children } => {
            assert_eq!(children.len(), 5, "Should have 5 children (A,comma,B,comma,C)");
            assert!(matches!(&children[0], Node::Token { token_type, .. } if token_type == "word"));
            assert!(matches!(&children[1], Node::Token { token_type, .. } if token_type == "comma"));
            assert!(matches!(&children[2], Node::Token { token_type, .. } if token_type == "word"));
            assert!(matches!(&children[3], Node::Token { token_type, .. } if token_type == "comma"));
            assert!(matches!(&children[4], Node::Token { token_type, .. } if token_type == "word"));
        }
        _ => panic!("Expected DelimitedList node, got: {result:?}"),
    }
    Ok(())
}
