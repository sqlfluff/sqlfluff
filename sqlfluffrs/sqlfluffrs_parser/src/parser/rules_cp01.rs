//! Experimental Rust-native detection for rule CP01 (keyword capitalisation).
//!
//! Walks the parsed `Node` tree once, entirely in Rust, and returns the leaf
//! indices (aligned with Python's `raw_segments` order) that need a
//! capitalisation fix, paired with the corrected raw text. Keeping the whole
//! detection loop in Rust avoids the per-node FFI cost that makes a
//! Python-reads-the-tree approach slower than a native Python crawl.
//!
//! Mirrors `Rule_CP01` for the `consistent`/`upper`/`lower`/`capitalise`
//! policies (the only options `capitalisation_policy` accepts). Word-ignore and
//! templated-area handling are applied here so the `consistent` inference sees
//! exactly the segments stock CP01 would.

use std::collections::HashSet;

use sqlfluffrs_types::PositionMarker;

use crate::parser::types::Node;

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

fn node_class_types(node: &Node) -> &[String] {
    match node {
        Node::Raw { class_types, .. } | Node::Segment { class_types, .. } => class_types,
        _ => &[],
    }
}

/// Mirrors `BaseSegment.is_templated`: a non-empty source slice that is not
/// literal (i.e. produced by templating).
fn is_templated(pos_marker: &Option<PositionMarker>) -> bool {
    match pos_marker {
        Some(m) => m.source_slice.start != m.source_slice.stop && !m.is_literal(),
        None => false,
    }
}

fn is_excluded_parent(parent: Option<&Node>) -> bool {
    let Some(parent) = parent else {
        return false;
    };
    let parent_types = node_class_types(parent);
    if parent_types
        .iter()
        .any(|t| EXCLUDE_PARENT_TYPES.contains(&t.as_str()))
    {
        return true;
    }
    // Qualified function names (e.g. UDFs) are case-sensitive.
    if let Node::Segment {
        segment_type: Some(st),
        children,
        ..
    } = parent
    {
        if st == "function_name" && children.len() != 1 {
            return true;
        }
    }
    false
}

#[allow(clippy::too_many_arguments)]
fn walk<'a>(
    node: &'a Node,
    parent: Option<&'a Node>,
    policy: &str,
    ignore_words: &HashSet<String>,
    ignore_templated: bool,
    idx: &mut usize,
    refuted: &mut HashSet<&'static str>,
    latest_possible: &mut Option<&'static str>,
    out: &mut Vec<(usize, String)>,
) {
    match node {
        Node::Segment { children, .. } | Node::Unparsable { children, .. } => {
            for child in children {
                walk(
                    child,
                    Some(node),
                    policy,
                    ignore_words,
                    ignore_templated,
                    idx,
                    refuted,
                    latest_possible,
                    out,
                );
            }
        }
        Node::Raw {
            raw,
            class_types,
            pos_marker,
            ..
        } => {
            let leaf_idx = *idx;
            *idx += 1;

            // Target type? (keyword/binary_operator/date_part, not a literal)
            let is_target = class_types
                .iter()
                .any(|t| TARGET_TYPES.contains(&t.as_str()))
                && !class_types.iter().any(|t| t == "literal");
            if !is_target || is_excluded_parent(parent) {
                return;
            }

            // Skips that must NOT influence the consistent-policy inference.
            if raw.is_empty()
                || ignore_words.contains(&raw.to_lowercase())
                || (ignore_templated && is_templated(pos_marker))
            {
                return;
            }

            // Refute cases inconsistent with this segment (CP01 logic, limited
            // to the policy options keywords actually support).
            let first_lower = raw
                .chars()
                .find(|c| is_capitalizable(*c))
                .map(|c| c.to_string() != c.to_uppercase().to_string())
                .unwrap_or(false);
            if first_lower {
                refuted.insert("upper");
                refuted.insert("capitalise");
                if *raw != raw.to_lowercase() {
                    refuted.insert("lower");
                }
            } else {
                refuted.insert("lower");
                if *raw != raw.to_uppercase() {
                    refuted.insert("upper");
                }
                if *raw != to_capitalise(raw) {
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

            let fixed = apply_policy(raw, concrete);
            if fixed != *raw {
                out.push((leaf_idx, fixed));
            }
        }
        Node::Meta { .. } | Node::Empty => {
            *idx += 1;
        }
    }
}

/// Detect CP01 violations on a parsed node tree.
///
/// Returns `(leaf_index, fixed_raw)` for every keyword/operator leaf that needs
/// a capitalisation fix. `leaf_index` indexes the flattened leaf order, which
/// matches Python's `raw_segments`, so the caller can anchor a fix directly.
pub fn cp01_violations(
    root: &Node,
    policy: &str,
    ignore_words: &HashSet<String>,
    ignore_templated: bool,
) -> Vec<(usize, String)> {
    let mut out = Vec::new();
    let mut idx = 0usize;
    let mut refuted: HashSet<&'static str> = HashSet::new();
    let mut latest_possible: Option<&'static str> = None;
    walk(
        root,
        None,
        policy,
        ignore_words,
        ignore_templated,
        &mut idx,
        &mut refuted,
        &mut latest_possible,
        &mut out,
    );
    out
}
