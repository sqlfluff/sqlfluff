// Common helper functions for grammar construction
// These are used by all dialect parsers

use std::sync::Arc;
use hashbrown::HashSet;
use sqlfluffrs_types::{Grammar, ParseMode, SimpleHint};

/// Create a Ref grammar with default settings
#[inline(always)]
pub fn ref_(name: &'static str) -> Arc<Grammar> {
    Arc::new(Grammar::Ref {
        name,
        optional: false,
        allow_gaps: true,
        exclude: None,
        terminators: vec![],
        reset_terminators: false,
        simple_hint: None,
    })
}

/// Create an optional Ref grammar
#[inline(always)]
pub fn ref_opt(name: &'static str) -> Arc<Grammar> {
    Arc::new(Grammar::Ref {
        name,
        optional: true,
        allow_gaps: true,
        exclude: None,
        terminators: vec![],
        reset_terminators: false,
        simple_hint: None,
    })
}

/// Create a Ref grammar with a simple hint
#[inline(always)]
pub fn ref_hint(name: &'static str, hint: SimpleHint) -> Arc<Grammar> {
    Arc::new(Grammar::Ref {
        name,
        optional: false,
        allow_gaps: true,
        exclude: None,
        terminators: vec![],
        reset_terminators: false,
        simple_hint: Some(hint),
    })
}

/// Create a keyword (StringParser) grammar
#[inline(always)]
pub fn keyword(template: &'static str) -> Arc<Grammar> {
    Arc::new(Grammar::StringParser {
        template,
        token_type: "keyword",
        raw_class: "KeywordSegment",
        optional: false,
    })
}

/// Create a Sequence grammar
#[inline(always)]
pub fn seq(elements: Vec<Arc<Grammar>>) -> Arc<Grammar> {
    Arc::new(Grammar::Sequence {
        elements,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    })
}

/// Create a OneOf grammar
#[inline(always)]
pub fn oneof(elements: Vec<Arc<Grammar>>) -> Arc<Grammar> {
    Arc::new(Grammar::OneOf {
        elements,
        exclude: None,
        optional: false,
        terminators: vec![],
        reset_terminators: false,
        allow_gaps: true,
        parse_mode: ParseMode::Strict,
        simple_hint: None,
    })
}

/// Create a SimpleHint with a single keyword
#[inline(always)]
pub fn hint_single(keyword: &'static str) -> SimpleHint {
    SimpleHint {
        raw_values: HashSet::from_iter([keyword.to_string()]),
        token_types: HashSet::from_iter([]),
    }
}
