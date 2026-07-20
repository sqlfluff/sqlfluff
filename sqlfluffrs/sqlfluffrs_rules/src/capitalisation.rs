//! Shared detection logic for the capitalisation rule bundle (CP01/CP03/CP04
//! today; CP02/CP05 have extra logic — ancestor-based policy applicability and
//! a container-scanning crawl shape, respectively — and are not yet ported).
//!
//! All three rules subclass `Rule_CP01` in Python and share its `_eval`/
//! `_handle_segment` state machine: refute capitalisation cases inconsistent
//! with what's been seen so far, resolve a concrete policy under `consistent`,
//! apply it, and compare. This module holds that state machine once; each
//! rule's arena walk differs only in which segment types it targets/excludes.

use std::collections::HashSet;

use sqlfluffrs_parser::{Arena, NodeId};

/// `capitalisation_policy`/`extended_capitalisation_policy` options minus
/// "consistent", in validation order. Only these three are ever inferred under
/// `consistent` — pascal/camel/snake are refuted unconditionally in the Python
/// rule (`refuted_cases.update(["camel", "pascal", "snake"])`) and so are only
/// reachable via an explicit (non-"consistent") policy.
const POLICY_OPTS: [&str; 3] = ["upper", "lower", "capitalise"];

fn is_capitalizable(c: char) -> bool {
    c.to_lowercase().to_string() != c.to_uppercase().to_string()
}

/// The four Unicode digraph letters (Dz, Dž, Lj, Nj) whose titlecase mapping
/// differs from their simple uppercase mapping — e.g. lowercase "dž" (U+01C6)
/// uppercases to "DŽ" (U+01C4) but title-cases to "Dž" (U+01C5). Python's
/// `str.capitalize()` uses the Unicode titlecase mapping for the first
/// character; Rust's `char::to_uppercase()` only exposes the uppercase one.
/// This table bridges that gap for exact parity on these (exceedingly rare in
/// practice) code points.
fn to_titlecase_char(c: char) -> String {
    let title = match c {
        '\u{01C4}' | '\u{01C6}' => '\u{01C5}',
        '\u{01C7}' | '\u{01C9}' => '\u{01C8}',
        '\u{01CA}' | '\u{01CC}' => '\u{01CB}',
        '\u{01F1}' | '\u{01F3}' => '\u{01F2}',
        _ => return c.to_uppercase().collect::<String>(),
    };
    title.to_string()
}

/// Python's `str.capitalize`: first char title-cased, the rest lower.
fn to_capitalise(raw: &str) -> String {
    let mut chars = raw.chars();
    match chars.next() {
        None => String::new(),
        Some(first) => to_titlecase_char(first) + &chars.as_str().to_lowercase(),
    }
}

/// Shared shape of Python's Pascal/Camel regexes: split on runs of non-alnum
/// (ASCII `[a-zA-Z0-9]`, matching the Python character class exactly) chars,
/// and transform only the first alnum char of each run — the rest of the run
/// is left untouched (so `PascalCase` isn't "corrected", and `under_score`
/// only gets its per-word first letters cased).
fn to_word_case(raw: &str, upper_first: bool) -> String {
    let mut out = String::with_capacity(raw.len());
    let mut prev_alnum = false;
    for c in raw.chars() {
        let is_alnum = c.is_ascii_alphanumeric();
        if is_alnum && !prev_alnum {
            if upper_first {
                out.extend(c.to_uppercase());
            } else {
                out.extend(c.to_lowercase());
            }
        } else {
            out.push(c);
        }
        prev_alnum = is_alnum;
    }
    out
}

/// Python's `str.isupper()`: true only if there's at least one cased char and
/// none of them are lowercase (so e.g. "123" is *not* upper).
fn python_isupper(raw: &str) -> bool {
    let mut has_cased = false;
    for c in raw.chars() {
        if c.is_lowercase() {
            return false;
        }
        if c.is_uppercase() {
            has_cased = true;
        }
    }
    has_cased
}

fn to_snake(raw: &str) -> String {
    if python_isupper(raw) {
        return raw.to_lowercase();
    }
    let chars: Vec<char> = raw.chars().collect();
    let mut out = String::with_capacity(raw.len() + 4);
    for (i, &c) in chars.iter().enumerate() {
        if i > 0 {
            let prev = chars[i - 1];
            let insert_underscore = (c.is_ascii_uppercase()
                && (prev.is_ascii_lowercase() || prev.is_ascii_digit()))
                || (c.is_ascii_digit() && prev.is_ascii_alphabetic())
                || (c.is_ascii_alphabetic() && prev.is_ascii_digit());
            if insert_underscore {
                out.push('_');
            }
        }
        out.push(c);
    }
    out.to_lowercase()
}

fn apply_policy(raw: &str, policy: &str) -> String {
    match policy {
        "upper" => raw.to_uppercase(),
        "lower" => raw.to_lowercase(),
        "capitalise" => to_capitalise(raw),
        "pascal" => to_word_case(raw, true),
        "camel" => to_word_case(raw, false),
        "snake" => to_snake(raw),
        _ => raw.to_string(),
    }
}

/// Refute cases inconsistent with `raw`, resolve a concrete policy, and apply
/// it. Returns `Some(fixed_raw)` when a fix is needed, `None` otherwise (mirrors
/// `Rule_CP01._handle_segment`'s per-segment control flow).
///
/// `camel`/`pascal`/`snake` bypass the refutation check entirely — in Python
/// they're always present in `refuted_cases` (added unconditionally), so
/// `cap_policy not in refuted_cases` is always false and the policy is always
/// applied; whether a fix is emitted depends only on whether the transform
/// changes the raw text.
fn evaluate(
    raw: &str,
    policy: &str,
    refuted: &mut HashSet<&'static str>,
    latest_possible: &mut Option<&'static str>,
) -> Option<String> {
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
        if raw != to_capitalise(raw) {
            refuted.insert("capitalise");
        }
    }

    let concrete: &str = match policy {
        "consistent" => {
            let possible: Vec<&'static str> = POLICY_OPTS
                .into_iter()
                .filter(|c| !refuted.contains(c))
                .collect();
            if let Some(first) = possible.first() {
                *latest_possible = Some(first);
                return None; // still consistent so far
            }
            latest_possible.unwrap_or("upper")
        }
        "camel" | "pascal" | "snake" => policy,
        _ => {
            if !refuted.contains(policy) {
                return None; // already conforms
            }
            policy
        }
    };

    let fixed = apply_policy(raw, concrete);
    if fixed != raw {
        Some(fixed)
    } else {
        None
    }
}

/// Mirrors `Rule_CP01._eval`'s parent-type exclusion plus the qualified
/// function-name check (used by CP03: multi-part function names are likely
/// case-sensitive UDFs) — the latter is hardcoded in the Python `_eval`, not
/// gated by `_exclude_parent_types`, so it applies unconditionally here too.
fn is_excluded_parent(
    arena: &Arena,
    parent: Option<NodeId>,
    exclude_parent_types: &[&str],
) -> bool {
    let Some(parent) = parent else {
        return false;
    };
    if exclude_parent_types
        .iter()
        .any(|t| arena.is_type(parent, t))
    {
        return true;
    }
    arena.get_type(parent) == "function_name" && arena.children(parent).len() != 1
}

#[allow(clippy::too_many_arguments)]
fn walk(
    arena: &Arena,
    id: NodeId,
    parent: Option<NodeId>,
    target_types: &[&str],
    exclude_types: &[&str],
    exclude_parent_types: &[&str],
    policy: &str,
    ignore_words: &HashSet<String>,
    ignore_templated: bool,
    leaf_idx: &mut usize,
    refuted: &mut HashSet<&'static str>,
    latest_possible: &mut Option<&'static str>,
    out: &mut Vec<(usize, String)>,
) {
    // Containers (and unparsables): recurse into children. Targets are leaves.
    let children = arena.children(id);
    if !children.is_empty() {
        for &child in children {
            walk(
                arena,
                child,
                Some(id),
                target_types,
                exclude_types,
                exclude_parent_types,
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

    // Non-cloning `is_type` membership checks — `class_types(id)` would clone
    // a Vec<String> per leaf, which dominates detection time on large files.
    let is_target = target_types.iter().any(|t| arena.is_type(id, t))
        && !exclude_types.iter().any(|t| arena.is_type(id, t));
    if !is_target || is_excluded_parent(arena, parent, exclude_parent_types) {
        return;
    }

    let raw = arena.raw(id);

    // Skips that must NOT influence the consistent-policy inference.
    if raw.is_empty()
        || ignore_words.contains(&raw.to_lowercase())
        || (ignore_templated && arena.is_templated(id))
    {
        return;
    }

    if let Some(fixed) = evaluate(&raw, policy, refuted, latest_possible) {
        out.push((this_leaf, fixed));
    }
}

/// Detect capitalisation violations on a parsed arena for a given target/
/// exclude configuration. `leaf_index` is the position in the arena's
/// depth-first leaf order, matching Python's `raw_segments`, so the caller
/// anchors via `raw_segments[leaf_index]`.
pub fn detect(
    arena: &Arena,
    target_types: &[&str],
    exclude_types: &[&str],
    exclude_parent_types: &[&str],
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
        target_types,
        exclude_types,
        exclude_parent_types,
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
