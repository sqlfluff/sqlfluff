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
//! | Which candidate match wins | `longest_match` best-candidate selection | [`is_better_candidate`] |

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

/// Match-quality policy: how a grammar decides whether a new candidate match
/// beats the best one seen so far. The two policies exist deliberately — see
/// the `longest_match` fields on `OneOfState` / `AnyNumberOfState`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) enum MatchQualityPolicy {
    /// Longest *clean* match wins (OneOf): candidates are compared by extent,
    /// but a clean (no-unparsable) candidate beats an unclean one of equal
    /// extent, and an unclean one must be strictly longer to displace a clean one.
    LongestClean,
    /// Longest match by extent only (AnyNumberOf): cleanliness is ignored.
    LongestEnd,
}

/// Whether a new candidate match beats the current best under `policy`.
///
/// `*_extent` is the policy's length metric — consumed token count for OneOf,
/// absolute end position for AnyNumberOf. Ties keep the current best, which
/// preserves "earliest tried wins" ordering. [`MatchQualityPolicy::LongestEnd`]
/// ignores the cleanliness flags.
///
/// MIRRORS: Python's `longest_match` (match_algorithms.py) — the best candidate
/// is the one consuming the most segments, ties going to the earliest listed
/// option; OneOf's clean-vs-unclean tiebreak mirrors how a shorter clean match
/// that leaves content unparsed loses to a longer match that covers everything.
#[inline]
pub(crate) fn is_better_candidate(
    policy: MatchQualityPolicy,
    new_extent: usize,
    new_is_clean: bool,
    current_extent: usize,
    current_is_clean: bool,
) -> bool {
    match policy {
        MatchQualityPolicy::LongestEnd => new_extent > current_extent,
        MatchQualityPolicy::LongestClean => {
            if new_is_clean && !current_is_clean {
                // Clean beats unclean only if it consumed at least as much.
                // A shorter clean match that leaves content unparsed is worse
                // than a longer unclean match that covers everything.
                new_extent >= current_extent
            } else {
                // Unclean only beats clean if strictly longer (same length:
                // prefer clean); clean-vs-clean and unclean-vs-unclean compare
                // by extent alone.
                new_extent > current_extent
            }
        }
    }
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
