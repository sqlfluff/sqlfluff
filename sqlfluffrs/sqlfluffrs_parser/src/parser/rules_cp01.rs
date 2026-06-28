//! Rust-native detection for rule CP01 (keyword capitalisation), over the arena.
//!
//! ## STATUS: experimental prototype — NOT wired into rule dispatch
//!
//! This proves out the "Rust-accelerated lint rule" approach end-to-end
//! (detect in Rust over the arena → return a compact result → Python anchors a
//! `LintFix`). It is exposed only via `RsTree.cp01_violations(...)` and is not
//! invoked by the linter; the stock Python `Rule_CP01` is still what runs.
//! Validated at parity with stock CP01 across the dialect fixtures × policies.
//!
//! Two things are deliberately left for design discussion before this becomes
//! production (see PR #7984):
//!   1. **Where this lives.** A *rule* in the *parser* crate is a layering
//!      smell; it sits here only because the arena read accessors are
//!      `pub(crate)`. Moving it to a `rules` module/crate needs the arena to
//!      expose a *public* navigation API — an arena-substrate decision.
//!   2. **Dispatch + gating.** How a Rust-accelerated rule is selected/gated
//!      (e.g. a `use_rust_rules` config) and falls back to Python is not
//!      decided here.
//!
//! Walks the parsed arena once, entirely in Rust, and returns the leaf indices
//! that need a capitalisation fix paired with the corrected raw text. Keeping
//! the whole detection loop in Rust (one FFI crossing for the result) avoids the
//! per-node boundary cost that makes a Python-reads-the-tree approach slower than
//! a native Python crawl.
//!
//! Mirrors `Rule_CP01` for the `consistent`/`upper`/`lower`/`capitalise`
//! policies (the only options `capitalisation_policy` accepts). Word-ignore and
//! templated-area handling are applied here so the `consistent` inference sees
//! exactly the segments stock CP01 would.
//!
//! Anchoring is by **leaf index**: the position of the node in the arena's
//! depth-first leaf order, which is 1:1 with Python's `raw_segments` (including
//! meta nodes). uuids are *not* shared between the arena and the Python
//! `BaseSegment` tree (they are built by independent constructions), so the
//! caller maps `leaf_index -> raw_segments[leaf_index]` to anchor the fix.

use std::collections::HashSet;

use crate::parser::arena::{Arena, NodeId};

const TARGET_TYPES: [&str; 3] = ["keyword", "binary_operator", "date_part"];
const EXCLUDE_PARENT_TYPES: [&str; 3] = ["data_type", "datetime_type_identifier", "primitive_type"];
// `capitalisation_policy` options minus "consistent", in validation order.
// `consistent` inference picks the first of these not yet refuted.
const POLICY_OPTS: [&str; 3] = ["upper", "lower", "capitalise"];

fn is_capitalizable(c: char) -> bool {
    c.to_lowercase().to_string() != c.to_uppercase().to_string()
}

/// Python's `str.capitalize`: first char upper, the rest lower.
fn to_capitalise(raw: &str) -> String {
    let mut chars = raw.chars();
    match chars.next() {
        None => String::new(),
        Some(first) => first.to_uppercase().collect::<String>() + &chars.as_str().to_lowercase(),
    }
}

fn apply_policy(raw: &str, policy: &str) -> String {
    match policy {
        "upper" => raw.to_uppercase(),
        "lower" => raw.to_lowercase(),
        "capitalise" => to_capitalise(raw),
        _ => raw.to_string(),
    }
}

/// Mirrors `Rule_CP01`'s parent-type exclusions.
fn is_excluded_parent(arena: &Arena, parent: Option<NodeId>) -> bool {
    let Some(parent) = parent else {
        return false;
    };
    // Membership checks via `is_type` (no allocation), not `class_types` (clones
    // a Vec per call).
    if EXCLUDE_PARENT_TYPES
        .iter()
        .any(|t| arena.is_type(parent, t))
    {
        return true;
    }
    // Qualified function names (e.g. UDFs) are case-sensitive.
    arena.get_type(parent) == "function_name" && arena.children(parent).len() != 1
}

#[allow(clippy::too_many_arguments)]
fn walk(
    arena: &Arena,
    id: NodeId,
    parent: Option<NodeId>,
    policy: &str,
    ignore_words: &HashSet<String>,
    ignore_templated: bool,
    leaf_idx: &mut usize,
    refuted: &mut HashSet<&'static str>,
    latest_possible: &mut Option<&'static str>,
    out: &mut Vec<(usize, String)>,
) {
    // Containers (and unparsables): recurse into children. Targets are leaves.
    let children = arena.children(id).to_vec();
    if !children.is_empty() {
        for child in children {
            walk(
                arena,
                child,
                Some(id),
                policy,
                ignore_words,
                ignore_templated,
                leaf_idx,
                refuted,
                latest_possible,
                out,
            );
        }
        return;
    }

    // A childless node is one leaf in `raw_segments` order (raw/meta/empty).
    // Take the index *before* any early return so it stays aligned regardless
    // of whether this leaf is a target.
    let this_leaf = *leaf_idx;
    *leaf_idx += 1;

    // Target type? (keyword/binary_operator/date_part, not a literal). Use the
    // non-cloning `is_type` membership check — calling `class_types(id)` here
    // would clone a Vec<String> for every leaf in the file.
    let is_target =
        TARGET_TYPES.iter().any(|t| arena.is_type(id, t)) && !arena.is_type(id, "literal");
    if !is_target || is_excluded_parent(arena, parent) {
        return;
    }

    let raw = arena.raw(id);

    // Skips that must NOT influence the consistent-policy inference.
    let templated = ignore_templated
        && arena
            .pos_marker(id)
            .map(|m| m.source_slice.start != m.source_slice.stop && !m.is_literal())
            .unwrap_or(false);
    if raw.is_empty() || ignore_words.contains(&raw.to_lowercase()) || templated {
        return;
    }

    // Refute cases inconsistent with this segment (CP01 logic, limited to the
    // policy options keywords actually support).
    let first_lower = raw
        .chars()
        .find(|c| is_capitalizable(*c))
        .map(|c| c.to_string() != c.to_uppercase().to_string())
        .unwrap_or(false);
    if first_lower {
        refuted.insert("upper");
        refuted.insert("capitalise");
        if raw != raw.to_lowercase() {
            refuted.insert("lower");
        }
    } else {
        refuted.insert("lower");
        if raw != raw.to_uppercase() {
            refuted.insert("upper");
        }
        if raw != to_capitalise(&raw) {
            refuted.insert("capitalise");
        }
    }

    let concrete: &str = if policy == "consistent" {
        let possible: Vec<&'static str> = POLICY_OPTS
            .into_iter()
            .filter(|c| !refuted.contains(c))
            .collect();
        if let Some(first) = possible.first() {
            *latest_possible = Some(first);
            return; // still consistent so far
        }
        latest_possible.unwrap_or("upper")
    } else {
        if !refuted.contains(policy) {
            return; // already conforms
        }
        policy
    };

    let fixed = apply_policy(&raw, concrete);
    if fixed != raw {
        out.push((this_leaf, fixed));
    }
}

/// Detect CP01 violations on a parsed arena.
///
/// Returns `(leaf_index, fixed_raw)` for every keyword/operator leaf that needs
/// a capitalisation fix. `leaf_index` is the position in the arena's depth-first
/// leaf order, which matches Python's `raw_segments`, so the caller anchors via
/// `raw_segments[leaf_index]`.
pub(crate) fn cp01_violations(
    arena: &Arena,
    policy: &str,
    ignore_words: &HashSet<String>,
    ignore_templated: bool,
) -> Vec<(usize, String)> {
    let mut out = Vec::new();
    let mut leaf_idx = 0usize;
    let mut refuted: HashSet<&'static str> = HashSet::new();
    let mut latest_possible: Option<&'static str> = None;
    walk(
        arena,
        arena.root(),
        None,
        policy,
        ignore_words,
        ignore_templated,
        &mut leaf_idx,
        &mut refuted,
        &mut latest_possible,
        &mut out,
    );
    out
}
