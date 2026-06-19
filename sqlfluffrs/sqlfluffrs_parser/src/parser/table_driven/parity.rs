//! Python-parity invariants — single source of truth.
//!
//! The iterative engine must produce the same parse trees as the Python parser
//! (`sqlfluff/core`). Historically the rules that enforce that were duplicated across
//! the per-variant handlers and held together by ~scattered "mirror Python" comments.
//! This module centralises the parity-sensitive *formulas* so each one is defined once;
//! every item names the Python concept it mirrors. Grep for `MIRRORS` to enumerate the
//! whole parity surface.
//!
//! See [`ENGINE.md`](../../../../ENGINE.md) §4 for the contract these helpers encode.
//!
//! | Invariant | Python concept | Owner |
//! |-----------|----------------|-------|
//! | Which grammars may be frame-cached | element-level memoization in `longest_match` | [`is_frame_cacheable`] |
//! | Effective parse mode (incl. Bracketed→child inheritance) | `ParseMode` resolution | [`effective_parse_mode`] |

use sqlfluffrs_types::{GrammarInst, GrammarVariant, ParseMode};

use crate::parser::table_driven::frame::TableParseFrame;

/// Whether a *complete* match for this grammar variant is safe to store in the frame
/// cache (`TableCacheKey { pos, grammar_id, max_idx }`).
///
/// MIRRORS: Python caches at the element level inside `longest_match`, not at the
/// complete-grammar level. Only these variants are deterministic enough that caching a
/// complete result is equivalent:
/// - `Ref`: deterministic indirection.
/// - `OneOf`: picks the single best alternative; no partial-match pollution.
/// - `Bracketed`: deterministic open/close.
/// - `Delimited`: deterministic delimiter pattern.
///
/// `Sequence` / `AnyNumberOf` / `AnySetOf` are intentionally excluded: a partial GREEDY
/// or N-vs-N+M match would pollute the cache.
///
/// This predicate MUST be identical at cache-store and cache-lookup time; both go through
/// this one function so they cannot drift (a mismatch would store under one key and look
/// up under another, silently corrupting results).
#[inline]
pub(crate) fn is_frame_cacheable(variant: GrammarVariant) -> bool {
    matches!(
        variant,
        GrammarVariant::Ref
            | GrammarVariant::OneOf
            | GrammarVariant::Delimited
            | GrammarVariant::Bracketed
    )
}

/// The parse mode a frame actually parses under.
///
/// MIRRORS: Python's parse-mode resolution, including the case where a parent (e.g.
/// `Bracketed`) imposes a mode on its child via `parse_mode_override`. When no override is
/// present the grammar's own declared `parse_mode` applies.
#[inline]
pub(crate) fn effective_parse_mode(frame: &TableParseFrame, inst: &GrammarInst) -> ParseMode {
    frame.parse_mode_override.unwrap_or(inst.parse_mode)
}
