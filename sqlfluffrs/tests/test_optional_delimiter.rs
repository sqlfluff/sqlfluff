use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::{Node, ParseError, Parser};
use sqlfluffrs_types::{Grammar, ParseMode};
use std::sync::Arc;

/// Test OptionallyDelimited behavior - elements can be separated by delimiters OR not
#[test]
fn test_optionally_delimited_basic() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // Create a grammar that matches: A [,] A [,] A
    // Where the commas are optional
    let grammar = Arc::new(Grammar::Delimited {
        elements: vec![Arc::new(Grammar::StringParser {
            template: "A",
            token_type: "word",
            raw_class: "WordSegment",
            optional: false,
        })],
        delimiter: Box::new(Arc::new(Grammar::StringParser {
            template: ",",
            token_type: "comma",
            raw_class: "SymbolSegment",
            optional: false,
        })),
        allow_trailing: false,
        optional: false,
        optional_delimiter: true, // This is the key difference!
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        min_delimiters: 0,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    // Test case 1: With delimiters (traditional comma-separated)
    let sql1 = "A, A, A";
    let input1 = LexInput::String(sql1.into());
    let lexer1 = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens1, _errors1) = lexer1.lex(input1, false);
    let mut parser1 = Parser::new(&tokens1, Dialect::Ansi);
    let result1 = parser1.parse_with_grammar_cached(&grammar, &[])?;

    println!("\nTest 1 result: {:#?}", result1);
    match result1 {
        Node::DelimitedList { children } => {
            // Should have: A, whitespace, comma, whitespace, A, whitespace, comma, whitespace, A = 9 children
            // But whitespace might be included differently, so let's just check we have content
            assert!(
                children.len() >= 5,
                "Should have at least 5 children (3 A's + 2 commas), got {}",
                children.len()
            );
            println!(
                "Test 1 passed: matched {} children with delimiters",
                children.len()
            );
        }
        _ => panic!("Expected DelimitedList node, got: {result1:?}"),
    }

    // Test case 2: Without delimiters (space-separated)
    let sql2 = "A A A";
    let input2 = LexInput::String(sql2.into());
    let lexer2 = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens2, _errors2) = lexer2.lex(input2, false);
    let mut parser2 = Parser::new(&tokens2, Dialect::Ansi);
    let result2 = parser2.parse_with_grammar_cached(&grammar, &[])?;

    println!("\nTest 2 result: {:#?}", result2);
    match result2 {
        Node::DelimitedList { children } => {
            // Should have: A, whitespace, A, whitespace, A = 5 children
            assert!(
                children.len() >= 3,
                "Should have at least 3 children (3 A's), got {}",
                children.len()
            );
            println!(
                "Test 2 passed: matched {} children without delimiters",
                children.len()
            );
        }
        _ => panic!("Expected DelimitedList node, got: {result2:?}"),
    }

    // Test case 3: Mixed - some delimiters, some without
    let sql3 = "A, A A";
    let input3 = LexInput::String(sql3.into());
    let lexer3 = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens3, _errors3) = lexer3.lex(input3, false);
    let mut parser3 = Parser::new(&tokens3, Dialect::Ansi);
    let result3 = parser3.parse_with_grammar_cached(&grammar, &[])?;

    println!("\nTest 3 result: {:#?}", result3);
    match result3 {
        Node::DelimitedList { children } => {
            // Should have: A, whitespace, comma, whitespace, A, whitespace, A = at least 5 children
            assert!(
                children.len() >= 5,
                "Should have at least 5 children, got {}",
                children.len()
            );
            println!(
                "Test 3 passed: matched {} children with mixed delimiters",
                children.len()
            );
        }
        _ => panic!("Expected DelimitedList node, got: {result3:?}"),
    }

    Ok(())
}

/// Test that regular Delimited (optional_delimiter=false) still requires delimiters
#[test]
fn test_regular_delimited_requires_delimiters() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // Create a grammar that matches: A , A , A
    // Where the commas are REQUIRED
    let grammar = Arc::new(Grammar::Delimited {
        elements: vec![Arc::new(Grammar::StringParser {
            template: "A",
            token_type: "word",
            raw_class: "WordSegment",
            optional: false,
        })],
        delimiter: Box::new(Arc::new(Grammar::StringParser {
            template: ",",
            token_type: "comma",
            raw_class: "SymbolSegment",
            optional: false,
        })),
        allow_trailing: false,
        optional: false,
        optional_delimiter: false, // Delimiters are REQUIRED
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        min_delimiters: 0,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    // Test case 1: With delimiters - should match
    let sql1 = "A, A, A";
    let input1 = LexInput::String(sql1.into());
    let lexer1 = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens1, _errors1) = lexer1.lex(input1, false);
    let mut parser1 = Parser::new(&tokens1, Dialect::Ansi);
    let result1 = parser1.parse_with_grammar_cached(&grammar, &[])?;

    println!("\nTest regular delimited 1 result: {:#?}", result1);
    match result1 {
        Node::DelimitedList { children } => {
            assert!(
                children.len() >= 5,
                "Should match with delimiters, got {}",
                children.len()
            );
            println!("Regular delimited test 1 passed");
        }
        _ => panic!("Expected DelimitedList node, got: {result1:?}"),
    }

    // Test case 2: Without delimiters - should only match first element
    let sql2 = "A A A";
    let input2 = LexInput::String(sql2.into());
    let lexer2 = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens2, _errors2) = lexer2.lex(input2, false);
    let mut parser2 = Parser::new(&tokens2, Dialect::Ansi);
    let result2 = parser2.parse_with_grammar_cached(&grammar, &[])?;

    println!("\nTest regular delimited 2 result: {:#?}", result2);
    match result2 {
        Node::DelimitedList { children } => {
            // Should only match first "A" because no delimiter after it
            assert_eq!(
                children.len(),
                1,
                "Should only match first A (no delimiter), got {}",
                children.len()
            );
            println!("Regular delimited test 2 passed: only matched first element");
        }
        _ => panic!("Expected DelimitedList node, got: {result2:?}"),
    }

    Ok(())
}
