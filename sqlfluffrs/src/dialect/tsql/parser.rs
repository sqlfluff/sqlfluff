/* This is a generated file! */
use once_cell::sync::Lazy;
use crate::parser::{Grammar, ParseMode, types::SimpleHint};

pub fn get_tsql_segment_grammar(name: &str) -> Option<&'static Grammar> {
    match name {
            _ => None,
    }
}

pub fn get_tsql_segment_type(name: &str) -> Option<&'static str> {
    match name {
            _ => None,
    }
}

pub fn get_tsql_root_grammar() -> &'static Grammar {
    get_tsql_segment_grammar(
        "FileSegment"
    ).expect("Root grammar missing.")
}
