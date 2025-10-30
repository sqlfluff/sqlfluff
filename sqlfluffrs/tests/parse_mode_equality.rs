/// Test to demonstrate that parse_mode affects Hash but not PartialEq
///
/// This test shows that:
/// 1. Two grammars with different parse_modes are still considered EQUAL (PartialEq)
/// 2. But they produce DIFFERENT hash values (Hash)
///
/// This matches Python's behavior where equality_kwargs doesn't include parse_mode,
/// but we still want different cache keys for different parse modes.
#[cfg(test)]
mod parse_mode_equality_tests {
    use sqlfluffrs_parser::parser::{Grammar, ParseMode};

    #[test]
    fn test_parse_mode_method() {
        let seq_strict = Grammar::Sequence {
            elements: vec![],
            optional: false,
            terminators: vec![],
            reset_terminators: false,
            allow_gaps: true,
            parse_mode: ParseMode::Strict,
            simple_hint: None,
        };

        assert_eq!(seq_strict.parse_mode(), ParseMode::Strict);

        // Test that non-mode grammars default to Strict
        let token = Grammar::Token {
            token_type: "keyword",
        };
        assert_eq!(token.parse_mode(), ParseMode::Strict);
    }
}
