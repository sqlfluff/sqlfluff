//! Type mapping utilities for converting between token types and segment types.
//!
//! This module provides functions to map semantic token types (from the lexer)
//! to base segment types (for Python segment class lookup).

/// Map semantic token types to base segment types for Python class lookup.
///
/// The lexer provides semantic types like "naked_identifier" or "numeric_literal",
/// but Python segment classes use base types like "identifier" or "literal".
/// This function performs that mapping.
pub fn get_base_segment_type(token_type: &str) -> String {
    match token_type {
        // Identifiers
        "naked_identifier" | "quoted_identifier" => "identifier",

        // Literals
        "quoted_literal" | "single_quote" | "double_quote" => "literal",
        "numeric_literal" | "integer_literal" | "float_literal" => "literal",

        // Symbols
        "comma" | "dot" | "semicolon" | "colon" | "raw" => "symbol",
        "raw_comparison_operator" => "comparison_operator",

        // Operators
        "equals" | "not_equals" | "less_than" | "greater_than" => "comparison_operator",
        "less_than_or_equal" | "greater_than_or_equal" => "comparison_operator",

        // Already base types - return as-is
        "keyword"
        | "word"
        | "whitespace"
        | "newline"
        | "literal"
        | "symbol"
        | "comment"
        | "end_of_file"
        | "identifier"
        | "comparison_operator" => token_type,

        // Unknown - return as-is with warning
        _ => {
            log::trace!("Unknown token type for mapping: {}", token_type);
            token_type
        }
    }
    .to_string()
}

/// Determine if a name refers to a grammar (not a segment class).
///
/// Grammars typically end with "Grammar" and represent parsing rules
/// rather than actual segment classes.
pub fn is_grammar_name(name: &str) -> bool {
    name.ends_with("Grammar")
}

/// Get the segment class name for a Ref node.
///
/// Returns None if the name refers to a grammar (not a segment class),
/// otherwise returns the name itself.
pub fn get_segment_class_name(name: &str) -> Option<String> {
    if is_grammar_name(name) {
        None
    } else if name.ends_with("Segment") {
        Some(name.to_string())
    } else {
        // Ambiguous - could be grammar or segment
        // Default to treating it as a segment
        log::trace!("Ambiguous segment/grammar name: {}", name);
        Some(name.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_base_segment_type() {
        assert_eq!(get_base_segment_type("naked_identifier"), "identifier");
        assert_eq!(get_base_segment_type("quoted_identifier"), "identifier");
        assert_eq!(get_base_segment_type("numeric_literal"), "literal");
        assert_eq!(get_base_segment_type("keyword"), "keyword");
        assert_eq!(get_base_segment_type("comma"), "symbol");
    }

    #[test]
    fn test_is_grammar_name() {
        assert!(is_grammar_name("SelectableGrammar"));
        assert!(is_grammar_name("SingleIdentifierGrammar"));
        assert!(!is_grammar_name("SelectStatementSegment"));
        assert!(!is_grammar_name("KeywordSegment"));
    }

    #[test]
    fn test_get_segment_class_name() {
        assert_eq!(get_segment_class_name("SelectableGrammar"), None);
        assert_eq!(
            get_segment_class_name("SelectStatementSegment"),
            Some("SelectStatementSegment".to_string())
        );
        assert_eq!(
            get_segment_class_name("KeywordSegment"),
            Some("KeywordSegment".to_string())
        );
    }
}
