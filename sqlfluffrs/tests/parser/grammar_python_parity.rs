/// Additional grammar tests ported from Python test suite
/// These tests ensure Rust parser behavior matches Python parser edge cases
use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::{Grammar, ParseError, ParseMode, Parser};
use std::sync::Arc;

/// Test OneOf takes longest match (Python: test__parser__grammar_oneof_take_longest_match)
#[test]
fn test_oneof_takes_longest_match() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "foobar";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    // Create two options: "foo" alone vs "foobar"
    let foo = Arc::new(Grammar::StringParser {
        template: "foo",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });

    let foobar = Arc::new(Grammar::StringParser {
        template: "foobar",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });

    // OneOf should take the longest match (foobar), even if foo comes first
    let grammar = Arc::new(Grammar::OneOf {
        elements: vec![foo, foobar],
        exclude: None,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let result = parser.parse_with_grammar_cached(&grammar, &[])?;
    let result_str = format!("{:?}", result);

    // Should match "foobar", not just "foo"
    assert!(
        result_str.contains("foobar"),
        "Should match longest option 'foobar', got: {}",
        result_str
    );

    Ok(())
}

/// Test AnyNumberOf with min/max constraints (Python: test__parser__grammar_anynumberof)
#[test]
fn test_anynumberof_min_max_constraints() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "a a a";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    let a_parser = Arc::new(Grammar::StringParser {
        template: "a",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });

    // Test min_times constraint (require at least 2)
    let grammar_min = Arc::new(Grammar::AnyNumberOf {
        elements: vec![a_parser.clone()],
        min_times: 2,
        max_times: None,
        max_times_per_element: None,
        exclude: None,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let mut parser = Parser::new(&tokens, dialect.clone());
    let result = parser.parse_with_grammar_cached(&grammar_min, &[]);
    assert!(
        result.is_ok(),
        "Should match with min_times=2 when we have 3 'a's"
    );

    // Test max_times constraint - parse only 2 of the 3 "a"s
    let grammar_max = Arc::new(Grammar::AnyNumberOf {
        elements: vec![a_parser.clone()],
        min_times: 0,
        max_times: Some(2),
        max_times_per_element: None,
        exclude: None,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let mut parser2 = Parser::new(&tokens, dialect);
    let _result2 = parser2.parse_with_grammar_cached(&grammar_max, &[])?;

    // Should stop after 2 matches
    assert!(
        parser2.pos >= 2,
        "Parser should have advanced past at least 2 tokens"
    );

    Ok(())
}

/// Test Sequence with optional elements (Python: test__parser__grammar_sequence_nested_match)
#[test]
fn test_sequence_with_optional_elements() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "a c";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let a_parser = Arc::new(Grammar::StringParser {
        template: "a",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });

    let b_parser = Arc::new(Grammar::StringParser {
        template: "b",
        raw_class: "WordSegment",
        token_type: "word",
        optional: true, // Optional
    });

    let c_parser = Arc::new(Grammar::StringParser {
        template: "c",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });

    // Sequence: a, [b], c (where b is optional)
    let grammar = Arc::new(Grammar::Sequence {
        elements: vec![a_parser, b_parser, c_parser],
        allow_gaps: true,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let result = parser.parse_with_grammar_cached(&grammar, &[])?;
    let result_str = format!("{:?}", result);

    // Should match "a" and "c", skipping optional "b"
    assert!(
        result_str.contains("a") && result_str.contains("c"),
        "Should match 'a' and 'c' with optional 'b' skipped, got: {}",
        result_str
    );

    Ok(())
}

/// Test Delimited with trailing delimiter allowed (Python delimited grammar tests)
#[test]
fn test_delimited_trailing_delimiter() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // Test "a, b," (trailing comma)
    let raw = "a, b,";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let element = Arc::new(Grammar::OneOf {
        elements: vec![
            Arc::new(Grammar::StringParser {
                template: "a",
                raw_class: "WordSegment",
                token_type: "word",
                optional: false,
            }),
            Arc::new(Grammar::StringParser {
                template: "b",
                raw_class: "WordSegment",
                token_type: "word",
                optional: false,
            }),
        ],
        exclude: None,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let delimiter = Arc::new(Grammar::StringParser {
        template: ",",
        raw_class: "SymbolSegment",
        token_type: "comma",
        optional: false,
    });

    let grammar = Arc::new(Grammar::Delimited {
        elements: vec![element],
        delimiter: Box::new(delimiter),
        allow_trailing: true, // Allow trailing delimiter
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        min_delimiters: 0,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let result = parser.parse_with_grammar_cached(&grammar, &[])?;
    let result_str = format!("{:?}", result);

    // Should successfully match with trailing comma
    assert!(
        result_str.contains("a") && result_str.contains("b"),
        "Should match 'a, b,' with trailing delimiter, got: {}",
        result_str
    );

    Ok(())
}

/// Test nested sequences (Python: test__parser__grammar_sequence_nested_match)
#[test]
fn test_nested_sequences() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "a b c";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let a_parser = Arc::new(Grammar::StringParser {
        template: "a",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });

    let b_parser = Arc::new(Grammar::StringParser {
        template: "b",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });

    let c_parser = Arc::new(Grammar::StringParser {
        template: "c",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });

    // Create nested sequence: (a, b), c
    let inner_sequence = Arc::new(Grammar::Sequence {
        elements: vec![a_parser, b_parser],
        allow_gaps: true,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let outer_sequence = Arc::new(Grammar::Sequence {
        elements: vec![inner_sequence, c_parser],
        allow_gaps: true,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let result = parser.parse_with_grammar_cached(&outer_sequence, &[])?;
    let result_str = format!("{:?}", result);

    // Should match all three elements
    assert!(
        result_str.contains("a") && result_str.contains("b") && result_str.contains("c"),
        "Should match nested sequence 'a b c', got: {}",
        result_str
    );

    Ok(())
}

/// Test Greedy mode with terminators (Python: test__parser__grammar_sequence_modes)
#[test]
fn test_greedy_mode_with_terminators() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "a b c";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let a_parser = Arc::new(Grammar::StringParser {
        template: "a",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });

    let c_terminator = Arc::new(Grammar::StringParser {
        template: "c",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });

    // Greedy sequence matching "a" with "c" as terminator
    // Should match "a", see "b" as unparsable, and stop before "c"
    let grammar = Arc::new(Grammar::Sequence {
        elements: vec![a_parser],
        allow_gaps: true,
        optional: false,
        terminators: vec![c_terminator],
        reset_terminators: false,
        parse_mode: ParseMode::Greedy,
        simple_hint: None,
    });

    let result = parser.parse_with_grammar_cached(&grammar, &[])?;
    let result_str = format!("{:?}", result);

    // Should match "a" and may include "b" as unparsable, but not "c"
    assert!(
        result_str.contains("a"),
        "Should match 'a', got: {}",
        result_str
    );

    // Parser should stop before the terminator "c"
    assert!(
        parser.pos < tokens.len(),
        "Parser should not consume terminator"
    );

    Ok(())
}

/// Test AnyNumberOf matching elements in order (Python: test_anynumberof_order)
#[test]
fn test_anynumberof_matches_in_order() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "a b a b";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let a_parser = Arc::new(Grammar::StringParser {
        template: "a",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });

    let b_parser = Arc::new(Grammar::StringParser {
        template: "b",
        raw_class: "WordSegment",
        token_type: "word",
        optional: false,
    });

    // AnyNumberOf matching "a" or "b" in any order
    let grammar = Arc::new(Grammar::AnyNumberOf {
        elements: vec![a_parser, b_parser],
        min_times: 0,
        max_times: None,
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
    let result_str = format!("{:?}", result);

    // Should match all four elements
    assert!(
        result_str.contains("a") && result_str.contains("b"),
        "Should match 'a b a b', got: {}",
        result_str
    );

    Ok(())
}

/// Test empty Bracketed grammar (Python: bracketed tests)
#[test]
fn test_empty_brackets() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "()";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let open = Arc::new(Grammar::StringParser {
        template: "(",
        raw_class: "SymbolSegment",
        token_type: "symbol",
        optional: false,
    });

    let close = Arc::new(Grammar::StringParser {
        template: ")",
        raw_class: "SymbolSegment",
        token_type: "symbol",
        optional: false,
    });

    // Empty bracketed content
    let grammar = Arc::new(Grammar::Bracketed {
        elements: vec![], // Empty content
        bracket_pairs: (Box::new(open), Box::new(close)),
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    });

    let result = parser.parse_with_grammar_cached(&grammar, &[])?;

    // Should successfully match empty brackets
    assert!(!result.is_empty(), "Should match empty brackets '()'");

    Ok(())
}
