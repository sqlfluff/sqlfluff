//! CP01 (keyword capitalisation) detection over the parse arena.
//!
//! Thin wrapper over the shared state machine in [`crate::capitalisation`];
//! this module only supplies CP01's target/exclude sets. See that module for
//! the walk/refute/apply logic shared with CP03 and CP04.
//!
//! Mirrors `Rule_CP01` for the `consistent`/`upper`/`lower`/`capitalise`
//! policies (the only options `capitalisation_policy` accepts). Word-ignore and
//! templated-area handling are applied in the shared walk so the `consistent`
//! inference sees exactly the segments stock CP01 would.
//!
//! Anchoring is by **leaf index**: the position of the node in the arena's
//! depth-first leaf order, which is 1:1 with Python's `raw_segments` (including
//! meta nodes). uuids are *not* shared between the arena and the Python
//! `BaseSegment` tree (they are built by independent constructions), so the
//! caller maps `leaf_index -> raw_segments[leaf_index]` to anchor the fix.

use std::collections::HashSet;

use sqlfluffrs_parser::Arena;

use crate::capitalisation::detect;

const TARGET_TYPES: [&str; 3] = ["keyword", "binary_operator", "date_part"];
// Literals are also keywords but have their own rule (CP04).
const EXCLUDE_TYPES: [&str; 1] = ["literal"];
const EXCLUDE_PARENT_TYPES: [&str; 3] = ["data_type", "datetime_type_identifier", "primitive_type"];

/// Detect CP01 violations on a parsed arena.
///
/// Returns `(leaf_index, fixed_raw)` for every keyword/operator leaf that needs
/// a capitalisation fix. `leaf_index` is the position in the arena's depth-first
/// leaf order, which matches Python's `raw_segments`, so the caller anchors via
/// `raw_segments[leaf_index]`.
pub fn cp01_violations(
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
