//! CP03 (function-name capitalisation) detection over the parse arena.
//!
//! Thin wrapper over [`crate::capitalisation::detect`] — see that module for
//! the shared walk/refute/apply logic. CP03 has no target/parent exclusions of
//! its own (`Rule_CP03` sets `_exclude_types`/`_exclude_parent_types` to empty
//! tuples); the qualified-function-name skip (multi-part names are likely
//! case-sensitive UDFs) is still applied because it's unconditional in the
//! shared walk, matching `Rule_CP01._eval`.
//!
//! Unlike CP01, CP03 reads `extended_capitalisation_policy`, so `policy` may
//! additionally be `pascal`, `camel`, or `snake`.

use std::collections::HashSet;

use sqlfluffrs_parser::Arena;

use crate::capitalisation::detect;

const TARGET_TYPES: [&str; 2] = ["function_name_identifier", "bare_function"];
const EXCLUDE_TYPES: [&str; 0] = [];
const EXCLUDE_PARENT_TYPES: [&str; 0] = [];

/// Detect CP03 violations on a parsed arena.
///
/// Returns `(leaf_index, fixed_raw)` for every function-name leaf that needs a
/// capitalisation fix. `leaf_index` is the position in the arena's depth-first
/// leaf order, which matches Python's `raw_segments`, so the caller anchors via
/// `raw_segments[leaf_index]`.
pub fn cp03_violations(
    arena: &Arena,
    policy: &str,
    ignore_words: &HashSet<String>,
    ignore_templated: bool,
) -> Vec<(usize, String)> {
    detect(
        arena,
        &TARGET_TYPES,
        &EXCLUDE_TYPES,
        &EXCLUDE_PARENT_TYPES,
        policy,
        ignore_words,
        ignore_templated,
    )
}
