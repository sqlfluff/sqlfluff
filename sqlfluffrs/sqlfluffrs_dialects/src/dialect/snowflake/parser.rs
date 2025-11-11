/* This is a generated file! */
#![cfg_attr(rustfmt, rustfmt_skip)]
use std::sync::Arc;
use std::sync::OnceLock;
use sqlfluffrs_types::{Grammar, ParseMode, SimpleHint};
use sqlfluffrs_types::regex::RegexMode;

pub fn get_snowflake_segment_grammar(name: &str) -> Option<Arc<Grammar>> {
    match name {
            _ => None,
    }
}

pub fn get_snowflake_segment_type(name: &str) -> Option<&'static str> {
    match name {
            _ => None,
    }
}

pub fn get_snowflake_root_grammar() -> Arc<Grammar> {
    get_snowflake_segment_grammar(
        "FileSegment"
    ).expect("Root grammar missing.")
}
