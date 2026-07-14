//! CP04 (boolean/null literal capitalisation) detection over the parse arena.
//!
//! Thin wrapper over [`crate::capitalisation::detect`] — see that module for
//! the shared walk/refute/apply logic. CP04 has no target/parent exclusions of
//! its own (`Rule_CP04` sets `_exclude_types`/`_exclude_parent_types` to empty
//! tuples) and, like CP01, reads the plain `capitalisation_policy` (not the
//! extended one) — confirmed via `default_config.cfg`, which gives CP04
//! `capitalisation_policy` rather than `extended_capitalisation_policy`.

use std::collections::HashSet;

use sqlfluffrs_parser::Arena;

use crate::capitalisation::detect;

const TARGET_TYPES: [&str; 2] = ["null_literal", "boolean_literal"];
const EXCLUDE_TYPES: [&str; 0] = [];
const EXCLUDE_PARENT_TYPES: [&str; 0] = [];

/// Detect CP04 violations on a parsed arena.
///
/// Returns `(leaf_index, fixed_raw)` for every null/boolean literal leaf that
/// needs a capitalisation fix. `leaf_index` is the position in the arena's
/// depth-first leaf order, which matches Python's `raw_segments`, so the
/// caller anchors via `raw_segments[leaf_index]`.
pub fn cp04_violations(
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
