//! Type mapping utilities for segment class lookups.
//!
//! This module provides functions to determine segment class names from grammar references.

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
