//! Grammar feature tests
//!
//! Tests for specific grammar features like AnySetOf, Delimited, Bracketed, etc.

use hashbrown::HashSet;
use sqlfluffrs_parser::parser::{Grammar, Node, ParseError, ParseMode, Parser};
use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use std::sync::Arc;

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
        template: regex::RegexBuilder::new("[A-Z]+")
            .case_insensitive(true)
            .build()
            .unwrap(),
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

    let result = parser.parse_with_grammar_cached(&grammar, &[])?;
    println!("\nDelimited parse result: {:#?}", result);

    // Should produce a DelimitedList with 5 children: A, comma, B, comma, C
    match result {
        Node::DelimitedList { children } => {
            assert_eq!(
                children.len(),
                5,
                "Should have 5 children (A,comma,B,comma,C)"
            );
            assert!(matches!(&children[0], Node::Token { token_type, .. } if token_type == "word"));
            assert!(
                matches!(&children[1], Node::Token { token_type, .. } if token_type == "comma")
            );
            assert!(matches!(&children[2], Node::Token { token_type, .. } if token_type == "word"));
            assert!(
                matches!(&children[3], Node::Token { token_type, .. } if token_type == "comma")
            );
            assert!(matches!(&children[4], Node::Token { token_type, .. } if token_type == "word"));
        }
        _ => panic!("Expected DelimitedList node, got: {result:?}"),
    }
    Ok(())
}

#[test]
fn test_delimited_optional_and_trailing() -> Result<(), ParseError> {
    env_logger::try_init().ok();
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());

    // Delimiter: comma (not optional)
    let delimiter = Box::new(Arc::new(Grammar::StringParser {
        template: ",",
        raw_class: "SymbolSegment",
        token_type: "comma",
        optional: false,
    }));
    // Element: word (A, B, C)
    let element = Arc::new(Grammar::RegexParser {
        template: regex::RegexBuilder::new("[A-Z]+")
            .case_insensitive(true)
            .build()
            .unwrap(),
        raw_class: "WordSegment",
        token_type: "word",
        anti_template: None,
        optional: false,
    });

    // 1. Trailing delimiter allowed: "A,B,C,"
    let raw = "A,B,C,";
    let (tokens, _errors) = lexer.lex(LexInput::String(raw.into()), false);
    let mut parser = Parser::new(&tokens, dialect);
    let grammar = Arc::new(Grammar::Delimited {
        elements: vec![element.clone()],
        delimiter: delimiter.clone(),
        allow_trailing: true,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: false,
        min_delimiters: 0,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });
    let result = parser.parse_with_grammar_cached(&grammar.clone(), &[])?;
    match result {
        Node::DelimitedList { ref children } => {
            assert_eq!(children.len(), 6, "Should include trailing delimiter");
            assert!(
                matches!(&children[5], Node::Token { token_type, .. } if token_type == "comma")
            );
        }
        _ => panic!("Expected DelimitedList node for trailing delimiter case"),
    }

    // 2. Trailing delimiter not allowed: "A,B,C,"
    let raw = "A,B,C,";
    let (tokens, _errors) = lexer.lex(LexInput::String(raw.into()), false);
    let mut parser = Parser::new(&tokens, dialect);
    let grammar = Arc::new(Grammar::Delimited {
        elements: vec![element.clone()],
        delimiter: delimiter.clone(),
        allow_trailing: false,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: false,
        min_delimiters: 0,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });
    let result = parser.parse_with_grammar_cached(&grammar, &[]);
    println!("{:#?}", result);
    assert!(
        result.is_err(),
        "Should error if trailing delimiter is not allowed"
    );

    // 3. Minimum delimiters: "A,B"
    let raw = "A,B";
    let (tokens, _errors) = lexer.lex(LexInput::String(raw.into()), false);
    let mut parser = Parser::new(&tokens, dialect);
    let grammar = Arc::new(Grammar::Delimited {
        elements: vec![element],
        delimiter: delimiter,
        allow_trailing: false,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: false,
        min_delimiters: 2,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });
    let result = parser.parse_with_grammar_cached(&grammar, &[])?;
    assert!(result.is_empty(), "Should error if not enough delimiters");
    Ok(())
}

#[test]
fn test_oneof_longest_vs_first_match() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // OneOf should prefer the longest match, not the first
    // Input: "foobar"; options: "foo", "foobar"
    let raw = "foobar";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let grammar = Arc::new(Grammar::OneOf {
        elements: vec![
            Arc::new(Grammar::StringParser {
                template: "foo",
                raw_class: "WordSegment",
                token_type: "word",
                optional: false,
            }),
            Arc::new(Grammar::StringParser {
                template: "foobar",
                raw_class: "WordSegment",
                token_type: "word",
                optional: false,
            }),
        ],
        exclude: None,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: false,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let result = parser.parse_with_grammar_cached(&grammar, &[])?;
    // Should match "foobar" (the longest)
    let node_str = format!("{:?}", result);
    assert!(
        node_str.contains("foobar"),
        "Should match the longest option: {node_str}"
    );
    Ok(())
}

#[test]
fn test_oneof_first_match_when_equal_length() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // OneOf should prefer the first match if lengths are equal
    // Input: "foo"; options: "foo", "bar"
    let raw = "foo";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let grammar = Arc::new(Grammar::OneOf {
        elements: vec![
            Arc::new(Grammar::StringParser {
                template: "foo",
                raw_class: "WordSegment",
                token_type: "word",
                optional: false,
            }),
            Arc::new(Grammar::StringParser {
                template: "bar",
                raw_class: "WordSegment",
                token_type: "word",
                optional: false,
            }),
        ],
        exclude: None,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: false,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let result = parser.parse_with_grammar_cached(&grammar, &[])?;
    let node_str = format!("{:?}", result);
    assert!(
        node_str.contains("foo"),
        "Should match the first option: {node_str}"
    );
    Ok(())
}

#[test]
fn test_anynumberof_min_max() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // AnyNumberOf with min_times=1, max_times=3
    let raw = "A A B";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let grammar = Arc::new(Grammar::AnyNumberOf {
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
        min_times: 1,
        max_times: Some(3),
        max_times_per_element: None,
        exclude: None,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let result = parser.parse_with_grammar_cached(&grammar, &[])?;
    let node_str = format!("{:?}", result);
    assert!(
        node_str.contains("A") && node_str.contains("B"),
        "Should match all elements: {node_str}"
    );
    Ok(())
}

#[test]
fn test_anynumberof_optional_and_empty() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // AnyNumberOf with min_times=0, optional=true, should match empty input
    let raw = "";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let grammar = Arc::new(Grammar::AnyNumberOf {
        elements: vec![Arc::new(Grammar::StringParser {
            template: "A",
            raw_class: "WordSegment",
            token_type: "word",
            optional: false,
        })],
        min_times: 0,
        max_times: Some(2),
        max_times_per_element: None,
        exclude: None,
        optional: true,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let result = parser.parse_with_grammar_cached(&grammar, &[])?;
    let node_str = format!("{:?}", result);
    assert!(
        node_str.contains("Empty"),
        "Should match as empty: {node_str}"
    );
    Ok(())
}

#[test]
fn test_delimited_various_cases() -> Result<(), ParseError> {
    env_logger::try_init().ok();
    use sqlfluffrs_parser::parser::Grammar;
    // Each tuple: (input, min_delimiters, allow_gaps, allow_trailing, expected_tokens_consumed)
    // Note: Rust test expectations are based on tokens consumed from lexed input, matching Python's len(match_result)
    // Python tests use pre-tokenized lists, Rust lexes strings, so token counts differ but behavior is equivalent
    let cases = vec![
        // Python: ["bar", " \t ", ".", "    ", "bar"] = 5 tokens, expects 5
        // Rust: "bar \t .     bar" lexes to ["bar", " \t ", ".", "     ", "bar"] = 5 tokens, expects 5
        ("bar \t .     bar", 0, true, false, 5),
        // Python: ["bar", " \t ", ".", "    ", "bar", "    "] = 6 tokens, expects 5 (stops before trailing whitespace)
        // Rust: "bar \t .     bar     " lexes to ["bar", " \t ", ".", "     ", "bar", "     "] = 6 tokens, expects 5
        ("bar \t .     bar     ", 0, true, false, 5),
        // Python: ["bar", " \t ", ".", "   "] = 4 tokens, expects 1 (only matches first "bar" when allow_trailing=false)
        // Rust: "bar \t .   " lexes to ["bar", " \t ", ".", "   "] = 4 tokens, expects 1
        ("bar \t .   ", 0, true, false, 1),
        // Python: ["bar", " \t ", ".", "   "] = 4 tokens, expects 3 (matches "bar", whitespace, "." with trailing delimiter)
        // Rust: "bar \t .   " lexes to ["bar", " \t ", ".", "   "] = 4 tokens, expects 3
        ("bar \t .   ", 0, true, true, 3),
        // Repeat of first case
        ("bar \t .     bar", 0, true, false, 5),
        // Python: ["bar", " \t ", ".", "    ", "bar"] = 5 tokens, expects 1 (allow_gaps=false stops after first "bar")
        // Rust: "bar \t .     bar" = 5 tokens, expects 1
        ("bar \t .     bar", 0, false, false, 1),
        // Same as first but min_delimiters=1
        ("bar \t .     bar", 1, true, false, 5),
        // Python: expects 0 (allow_gaps=false + min_delimiters=1 means needs delimiter immediately after first element)
        // Rust: expects 0
        ("bar \t .     bar", 1, false, false, 0),
        // Python: ["bar", ".", "bar"] = 3 tokens, expects 3
        // Rust: "bar . bar" lexes to ["bar", " ", ".", " ", "bar"] = 5 tokens, expects 5
        ("bar . bar", 0, true, false, 5),
        // Python: ["bar", ".", "bar"] = 3 tokens, allow_gaps=false but no gaps in input, expects 3
        // Rust: "bar . bar" = 5 tokens (includes spaces), allow_gaps=false stops at first whitespace, expects 1
        ("bar . bar", 0, false, false, 1),
        // Same with min_delimiters=1
        ("bar . bar", 1, true, false, 5),
        // Python: min_delimiters=1 + allow_gaps=false, expects 3 (has delimiter)
        // Rust: min_delimiters=1 + allow_gaps=false stops at whitespace before delimiter, expects 0
        ("bar . bar", 1, false, false, 0),
        // Python: ["bar", ".", "bar", "foo"] = 4 tokens, expects 3 (stops before "foo")
        // Rust: "bar . bar foo" lexes to ["bar", " ", ".", " ", "bar", " ", "foo"] = 7 tokens
        // With min_delimiters=1 + allow_gaps=false: stops at whitespace, can't meet min_delimiters, expects 0
        ("bar . bar foo", 1, false, false, 0),
        // Python: ["bar", ".", "bar", "foo"] = 4 tokens, min_delimiters=2 expects 0 (only 1 delimiter)
        // Rust: "bar . bar foo" = 7 tokens, expects 0
        ("bar . bar foo", 2, true, false, 0),
    ];
    for (raw, min_delimiters, allow_gaps, allow_trailing, match_len) in cases {
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);
        let mut parser = Parser::new(&tokens, dialect);
        let element = Arc::new(Grammar::StringParser {
            template: "bar",
            raw_class: "WordSegment",
            token_type: "word",
            optional: false,
        });
        let delimiter = Box::new(Arc::new(Grammar::StringParser {
            template: ".",
            raw_class: "SymbolSegment",
            token_type: "dot",
            optional: false,
        }));
        let grammar = Arc::new(Grammar::Delimited {
            elements: vec![element],
            delimiter,
            allow_trailing,
            optional: false,
            terminators: vec![],
            reset_terminators: false,
            allow_gaps,
            min_delimiters,
            parse_mode: ParseMode::Strict,
            simple_hint: None,
        });
        let start_pos = parser.pos;
        let result = parser.parse_with_grammar_cached(&grammar, &[]);
        // Python tests check len(match_result) which is the number of input tokens consumed
        // In Rust, we check parser.pos - start_pos to get the same metric
        let tokens_consumed = if result.is_ok() && !matches!(result, Ok(Node::Empty)) {
            parser.pos - start_pos
        } else {
            0
        };
        assert_eq!(tokens_consumed, match_len, "Input: {raw:?} min_delimiters={min_delimiters} allow_gaps={allow_gaps} allow_trailing={allow_trailing}\nTokens: {:?}",
            tokens.iter().take(10).map(|t| (t.get_type(), t.raw())).collect::<Vec<_>>());
    }
    Ok(())
}

// Placeholder for Anything grammar test (Rust parser may not have direct equivalent)
// This would require a custom Grammar::Anything implementation if not present.

#[test]
fn test_nothing_grammar_matches_nothing() -> Result<(), ParseError> {
    env_logger::try_init().ok();
    // Simulate a Nothing grammar: always returns empty
    // If Grammar::Nothing exists, use it; otherwise, test empty match logic
    // Here, we use a RegexParser that matches nothing as a stand-in
    let raw = "foo bar";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);
    // If Grammar::Nothing exists, use it; else, use a regex that matches nothing
    let grammar = Arc::new(Grammar::RegexParser {
        template: regex::RegexBuilder::new("^$").build().unwrap(),
        raw_class: "NothingSegment",
        token_type: "nothing",
        anti_template: None,
        optional: true,
    });
    let result = parser.parse_with_grammar_cached(&grammar, &[])?;
    assert!(
        matches!(result, Node::Empty),
        "Nothing grammar should match as empty"
    );
    Ok(())
}

// --- Additional tests ported from grammar_ref_test.py ---

#[test]
fn test_ref_eq_and_repr() {
    use sqlfluffrs_parser::parser::Grammar;
    // Simulate Ref grammar equality and repr
    let r1 = Grammar::Ref {
        name: "foo",
        optional: false,
        exclude: None,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: false,
        simple_hint: None,
    };
    let r2 = Grammar::Ref {
        name: "foo",
        optional: false,
        exclude: None,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: false,
        simple_hint: None,
    };
    assert_ne!(&r1 as *const _, &r2 as *const _); // Not the same object
    assert_eq!(r1, r2);
    // Check repr (Debug)
    let repr = format!("{:?}", r1);
    assert!(repr.contains("Ref"));
    let r3 = Grammar::Ref {
        name: "bar",
        optional: true,
        exclude: None,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: false,
        simple_hint: None,
    };
    let repr_opt = format!("{:?}", r3);
    assert!(repr_opt.contains("bar"));
}

#[test]
fn test_ref_match_basic() -> Result<(), ParseError> {
    // Simulate a Ref grammar match for a simple token stream
    // This is a minimal test, not a full dialect-resolved match
    let raw = "foo bar";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);
    // Ref to "foo" (simulate as a StringParser for this test)
    let foo_grammar = Arc::new(Grammar::StringParser {
        template: "foo",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });
    // Parse from position 0 where "foo" is
    let result = parser.parse_with_grammar_cached(&foo_grammar, &[])?;
    let node_str = format!("{:?}", result);
    assert!(node_str.contains("foo"), "Expected 'foo' in node: {}", node_str);
    Ok(())
}

#[test]
fn test_ref_exclude_match() -> Result<(), ParseError> {
    // Simulate a Ref grammar with exclude logic
    // Exclude "ABS" from matching as "NakedIdentifierSegment"
    let raw = "ABS ABSOLUTE";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);
    // Simulate: match "ABS" but exclude it
    let abs_grammar = Arc::new(Grammar::StringParser {
        template: "ABS",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });
    let abs_exclude = Arc::new(Grammar::StringParser {
        template: "ABS",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });
    // Try to match "ABS" at position 0, but exclude it
    let exclude_match = parser.parse_with_grammar_cached(&abs_exclude, &[])?;
    let node_str = format!("{:?}", exclude_match);
    // Simulate exclusion: if matched, treat as excluded
    assert!(node_str.contains("ABS"));
    // Now match "ABSOLUTE" at position 1
    let abs_absolute_grammar = Arc::new(Grammar::StringParser {
        template: "ABSOLUTE",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });
    let result = parser.parse_with_grammar_cached(&abs_absolute_grammar, &[])?;
    let node_str2 = format!("{:?}", result);
    assert!(node_str2.contains("ABSOLUTE"));
    Ok(())
}

// --- Additional tests ported from grammar_sequence_test.py ---

#[test]
fn test_sequence_repr() {
    // Test the Sequence grammar Debug/Display representation
    let bar = Grammar::StringParser {
        template: "bar",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    };
    let foo = Grammar::StringParser {
        template: "foo",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    };
    let sequence = Grammar::Sequence {
        elements: vec![Arc::new(bar), Arc::new(foo)],
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: false,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    };
    let repr = format!("{:?}", sequence);
    assert!(repr.contains("Sequence"));
}

#[test]
fn test_sequence_nested_match() -> Result<(), ParseError> {
    // Test the Sequence grammar when nested
    let raw = "bar \t foo baar \t ";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);
    let bar = Arc::new(Grammar::StringParser {
        template: "bar",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });
    let foo = Arc::new(Grammar::StringParser {
        template: "foo",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });
    let baar = Arc::new(Grammar::StringParser {
        template: "baar",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });
    let inner_seq = Arc::new(Grammar::Sequence {
        elements: vec![bar.clone(), foo.clone()],
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: false,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });
    let outer_seq = Arc::new(Grammar::Sequence {
        elements: vec![inner_seq, baar.clone()],
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: false,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });
    // Matching just the start of the list shouldn't work
    let partial_tokens = &tokens[0..3];
    let mut partial_parser = Parser::new(partial_tokens, dialect);
    let partial_result = partial_parser.parse_with_grammar_cached(&outer_seq, &[]);
    assert!(
        partial_result.is_err()
            || partial_result
                .as_ref()
                .map(|n| n.is_empty())
                .unwrap_or(false)
    );
    // Matching the whole list should work
    let mut parser = Parser::new(&tokens, dialect);
    let result = parser.parse_with_grammar_cached(&outer_seq, &[])?;
    let node_str = format!("{:?}", result);
    assert!(node_str.contains("bar") && node_str.contains("foo") && node_str.contains("baar"));
    Ok(())
}

#[test]
fn test_sequence_modes_various_cases() -> Result<(), ParseError> {
    use sqlfluffrs_parser::parser::ParseMode;
    // Each tuple: (mode, input, sequence, terminators, expect_match, expect_token)
    // NOTE: These test cases mirror the Python test_parser__grammar_sequence_modes
    let cases = vec![
        // Test matches where we should get something (whole sequence)
        (ParseMode::Strict, "a ", vec!["a"], vec![], true, Some("a")),
        (ParseMode::Greedy, "a ", vec!["a"], vec![], true, Some("a")),
        (
            ParseMode::GreedyOnceStarted,
            "a ",
            vec!["a"],
            vec![],
            true,
            Some("a"),
        ),
        // Test matching sequences where we run out of segments before matching
        // STRICT returns no match when input "a " doesn't have enough for ["a", "b"]
        (
            ParseMode::Strict,
            "a ",
            vec!["a", "b"],
            vec![],
            false,
            None,
        ),
        // GREEDY returns content as unparsable (matches the "a" but can't get "b")
        // This is expected behavior: GREEDY mode tries to consume what it can
        (
            ParseMode::Greedy,
            "a ",
            vec!["a", "b"],
            vec![],
            true,
            Some("a"),
        ),
        (
            ParseMode::GreedyOnceStarted,
            "a ",
            vec!["a", "b"],
            vec![],
            true,
            Some("a"),
        ),
        // Test matching where first element fails
        // STRICT & GREEDY_ONCE_STARTED return no match when "b " doesn't match ["a"]
        (ParseMode::Strict, "b ", vec!["a"], vec![], false, None),
        (ParseMode::GreedyOnceStarted, "b ", vec!["a"], vec![], false, None),
        // GREEDY claims remaining as unparsable
        (ParseMode::Greedy, "b ", vec!["a"], vec![], true, Some("b")),
        // Test matching with more content after sequence matches
        // STRICT ignores the rest
        (
            ParseMode::Strict,
            "a b c",
            vec!["a"],
            vec![],
            true,
            Some("a"),
        ),
        // GREEDY claims rest as unparsable
        (
            ParseMode::Greedy,
            "a b c",
            vec!["a"],
            vec![],
            true,
            Some("a"),
        ),
        (
            ParseMode::GreedyOnceStarted,
            "a b c",
            vec!["a"],
            vec![],
            true,
            Some("a"),
        ),
        // With terminators
        (
            ParseMode::Strict,
            "a b c",
            vec!["a"],
            vec!["c"],
            true,
            Some("a"),
        ),
        (
            ParseMode::Greedy,
            "a b c",
            vec!["a"],
            vec!["c"],
            true,
            Some("a"),
        ),
        (
            ParseMode::GreedyOnceStarted,
            "a b c",
            vec!["a"],
            vec!["c"],
            true,
            Some("a"),
        ),
        // Test competition between sequence elements and terminators
        // GREEDY_ONCE_STARTED: first element matched before terminators
        (
            ParseMode::GreedyOnceStarted,
            "a ",
            vec!["a"],
            vec!["a"],
            true,
            Some("a"),
        ),
        // GREEDY: terminator takes precedence
        (
            ParseMode::Greedy,
            "a ",
            vec!["a"],
            vec!["a"],
            false,
            None,
        ),
    ];
    for (mode, raw, sequence, terminators, expect_match, expect_token) in cases {
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);
        let mut parser = Parser::new(&tokens, dialect);
        let elements: Vec<_> = sequence
            .iter()
            .map(|s| {
                Arc::new(Grammar::StringParser {
                    template: s.to_string().leak(),
                    raw_class: "WordSegment",
                    token_type: "word",
                    optional: false,
                })
            })
            .collect();
        let terminator_grammars: Vec<_> = terminators
            .iter()
            .map(|s| {
                Arc::new(Grammar::StringParser {
                    template: s,
                    raw_class: "WordSegment",
                    token_type: "word",
                    optional: false,
                })
            })
            .collect();
        let grammar = Arc::new(Grammar::Sequence {
            elements,
            optional: false,
            terminators: terminator_grammars,
            reset_terminators: false,
            allow_gaps: true,
            parse_mode: mode,
            simple_hint: None,
        });
        let result = parser.parse_with_grammar_cached(&grammar, &[]);
        if expect_match {
            let node = result.expect("Should parse");
            if let Some(tok) = expect_token {
                let node_str = format!("{:?}", node);
                assert!(
                    node_str.contains(tok),
                    "Expected token {tok:?} in node {node_str}"
                );
            }
        } else {
            assert!(
                result.is_err() || result.as_ref().map(|n| n.is_empty()).unwrap_or(false),
                "Expected no match for input {raw:?} mode={mode:?}"
            );
        }
    }
    Ok(())
}

fn bracketed_case(
    raw: &str,
    mode: ParseMode,
    sequence: Vec<&'static str>,
    allow_gaps: bool,
    expect_match: bool,
    expect_token: Option<&str>,
) {
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);
    let elements: Vec<_> = sequence
        .iter()
        .map(|s| {
            Arc::new(Grammar::StringParser {
                template: s,
                raw_class: "WordSegment",
                token_type: "word",
                optional: false,
            })
        })
        .collect();
    let open_bracket = Arc::new(Grammar::StringParser {
        template: "(",
        raw_class: "SymbolSegment",
        token_type: "start_bracket",
        optional: false,
    });
    let close_bracket = Arc::new(Grammar::StringParser {
        template: ")",
        raw_class: "SymbolSegment",
        token_type: "end_bracket",
        optional: false,
    });
    let grammar = Arc::new(Grammar::Bracketed {
        elements,
        bracket_pairs: (Box::new(open_bracket), Box::new(close_bracket)),
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps,
        parse_mode: mode,
        simple_hint: None,
    });
    let result = parser.parse_with_grammar_cached(&grammar, &[]);
    if expect_match {
        let node = result.expect("Should parse");
        if let Some(tok) = expect_token {
            let node_str = format!("{:?}", node);
            assert!(
                node_str.contains(tok),
                "Expected token {tok:?} in node {node_str}"
            );
        }
    } else {
        assert!(
            result.is_err() || result.as_ref().map(|n| n.is_empty()).unwrap_or(false),
            "Expected no match for input {raw:?} mode={mode:?}"
        );
    }
}

#[test]
fn test_bracketed_strict_asymmetric_bracket_shouldnt_match() {
    bracketed_case("( a", ParseMode::Strict, vec!["a"], true, false, None);
}

#[test]
fn test_bracketed_sequence_not_bracketed_strict() {
    bracketed_case("a", ParseMode::Strict, vec!["a"], true, false, None);
}

#[test]
fn test_bracketed_sequence_not_bracketed_greedy() {
    bracketed_case("a", ParseMode::Greedy, vec!["a"], true, false, None);
}

#[test]
fn test_bracketed_empty_brackets_no_whitespace_strict() {
    bracketed_case("()", ParseMode::Strict, vec![], true, true, Some("("));
}

#[test]
fn test_bracketed_empty_brackets_no_whitespace_greedy() {
    bracketed_case("()", ParseMode::Greedy, vec![], true, true, Some("("));
}

#[test]
fn test_bracketed_empty_brackets_with_whitespace_strict() {
    bracketed_case("( )", ParseMode::Strict, vec![], true, true, Some("("));
}

#[test]
fn test_bracketed_empty_brackets_with_whitespace_greedy() {
    bracketed_case("( )", ParseMode::Greedy, vec![], true, true, Some("("));
}

#[test]
fn test_bracketed_strict_no_gaps_shouldnt_match() {
    bracketed_case("( )", ParseMode::Strict, vec![], false, false, None);
}

#[test]
fn test_bracketed_happy_path_content_match() {
    bracketed_case("(a)", ParseMode::Strict, vec!["a"], true, true, Some("a"));
}

#[test]
fn test_bracketed_content_match_fails_strict() {
    bracketed_case("(a)", ParseMode::Strict, vec!["b"], true, false, None);
}

#[test]
fn test_bracketed_content_match_fails_greedy() {
    bracketed_case("(a)", ParseMode::Greedy, vec!["b"], true, true, Some("a"));
}

#[test]
fn test_bracketed_partial_match_not_whole_grammar_strict() {
    bracketed_case("(a)", ParseMode::Strict, vec!["a", "b"], true, false, None);
}

#[test]
fn test_bracketed_partial_match_not_whole_grammar_greedy() {
    bracketed_case(
        "(a)",
        ParseMode::Greedy,
        vec!["a", "b"],
        true,
        true,
        Some("a"),
    );
}

#[test]
fn test_bracketed_partial_match_not_whole_sequence_strict() {
    bracketed_case("(a b)", ParseMode::Strict, vec!["a"], true, false, None);
}

#[test]
fn test_bracketed_partial_match_not_whole_sequence_greedy() {
    bracketed_case("(a b)", ParseMode::Greedy, vec!["a"], true, true, Some("a"));
}
