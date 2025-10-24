/// Tests for the `exclude` grammar functionality
///
/// The `exclude` parameter allows grammars to specify patterns that should
/// prevent a match if they occur at the current position.

use sqlfluffrs::{
    lexer::{LexInput, Lexer},
    parser::{Grammar, Node, ParseError, ParseMode, Parser},
    Dialect,
};

#[test]
fn test_oneof_with_exclude() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // Test case: OneOf should match 'A' but NOT if 'AB' is present (exclude pattern)
    let input = LexInput::String("A".to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    // Create a OneOf grammar that matches "A" but excludes if "AB" is present
    let grammar = Grammar::OneOf {
        elements: vec![
            Grammar::StringParser {
                template: "A",
                raw_class: "WordSegment",
                token_type: "word",
                optional: false,
            },
        ],
        exclude: Some(Box::new(Grammar::Sequence {
            elements: vec![
                Grammar::StringParser {
                    template: "A",
                    raw_class: "WordSegment",
                    token_type: "word",
                    optional: false,
                },
                Grammar::StringParser {
                    template: "B",
                    raw_class: "WordSegment",
                    token_type: "word",
                    optional: false,
                },
            ],
            optional: false,
            terminators: vec![],
            reset_terminators: false,
            allow_gaps: true,
            parse_mode: ParseMode::Strict,
            simple_hint: None,
        })),
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    };

    // This should match since we only have "A", not "AB"
    let result = parser.parse_with_grammar_cached(&grammar, &[])?;

    println!("\nParsed successfully: {:#?}", result);

    // Should have consumed the "A" token (OneOf returns the single matched element directly)
    assert!(matches!(result, Node::Token { .. }), "Should match A: got {:?}", result);

    Ok(())
}

#[test]
fn test_oneof_exclude_blocks_match() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // Test case: OneOf should NOT match when exclude pattern is present
    let input = LexInput::String("AB".to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    // Create a OneOf grammar that matches "A" but excludes if "AB" is present
    let grammar = Grammar::OneOf {
        elements: vec![
            Grammar::StringParser {
                template: "A",
                raw_class: "WordSegment",
                token_type: "word",
                optional: false,
            },
        ],
        exclude: Some(Box::new(Grammar::Sequence {
            elements: vec![
                Grammar::StringParser {
                    template: "A",
                    raw_class: "WordSegment",
                    token_type: "word",
                    optional: false,
                },
                Grammar::StringParser {
                    template: "B",
                    raw_class: "WordSegment",
                    token_type: "word",
                    optional: false,
                },
            ],
            optional: false,
            terminators: vec![],
            reset_terminators: false,
            allow_gaps: true,
            parse_mode: ParseMode::Strict,
            simple_hint: None,
        })),
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    };

    // This should return Empty because "AB" matches the exclude pattern
    let result = parser.parse_with_grammar_cached(&grammar, &[])?;

    println!("\nExclude triggered, got: {:#?}", result);

    // Should be Empty due to exclude
    assert!(matches!(result, Node::Empty), "Should be empty due to exclude pattern");

    Ok(())
}

#[test]
fn test_anynumberof_with_exclude() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    // Test case: AnyNumberOf should match repeated "A" but not if "B" is present
    let input = LexInput::String("A A A".to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    // Create an AnyNumberOf grammar that matches "A" repeatedly but excludes if "B" is present
    let grammar = Grammar::AnyNumberOf {
        elements: vec![
            Grammar::StringParser {
                template: "A",
                raw_class: "WordSegment",
                token_type: "word",
                optional: false,
            },
        ],
        min_times: 1,
        max_times: None,
        max_times_per_element: None,
        exclude: Some(Box::new(Grammar::StringParser {
            template: "B",
            raw_class: "WordSegment",
            token_type: "word",
            optional: false,
        })),
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    };

    // This should match all three "A"s since there's no "B"
    let result = parser.parse_with_grammar_cached(&grammar, &[])?;

    println!("\nParsed successfully: {:#?}", result);

    // Should have matched multiple A's (AnyNumberOf returns DelimitedList)
    assert!(matches!(result, Node::DelimitedList { .. }), "Should match multiple A's: got {:?}", result);

    Ok(())
}
