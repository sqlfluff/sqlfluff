//! Parse frame types and state management for the iterative parser.
//!
//! This module contains the core types used by the iterative parser to track
//! parsing state without recursion. Instead of recursing into sub-grammars, the
//! engine pushes a [`super::table_driven::frame::TableParseFrame`] onto an
//! explicit stack; each frame carries a [`FrameState`] (where it is in its
//! lifecycle) and a [`FrameContext`] (its variant-specific working state).
//!
//! # Position-index glossary
//!
//! Several variants track positions into the token stream. The names recur with
//! consistent meaning across variants:
//!
//! - **`start_idx`** — the fixed token position where this grammar began
//!   matching. Never mutated after setup; used as the backtrack origin.
//! - **`matched_idx`** — the *committed* frontier: the position reached by
//!   everything matched and accepted so far. Advances only when a child match is
//!   folded into the result.
//! - **`working_idx`** — an *in-progress probe* position used while trying the
//!   next child/delimiter. May run ahead of `matched_idx` and be rolled back if
//!   the probe fails (e.g. a trailing delimiter with no following element).
//! - **`max_idx`** — the *ceiling*: the largest position this grammar is allowed
//!   to consume, derived from terminators and the parent's own ceiling
//!   (see [`crate::parser::helpers`]). Matching never crosses `max_idx`.
//!
//! See the glossary in `ENGINE.md` for the full list.

use hashbrown::HashMap;
use smallvec::SmallVec;
use std::sync::Arc;

use crate::parser::MetaSegment;

use super::match_result::MatchResult;
use sqlfluffrs_types::{GrammarId, ParseMode};

/// Where a frame is in its lifecycle. The iterative loop pops a frame, matches
/// on this state, and either pushes a child (and re-parks the parent in
/// [`FrameState::WaitingForChild`]) or finishes it.
///
/// Lifecycle: `Initial` → (`WaitingForChild`)\* → `Combining` → `Complete`.
#[derive(Debug, Clone)]
pub enum FrameState {
    /// Initial state - need to start parsing
    Initial,
    /// Parked while a child frame runs. `child_index` is the variant's resume
    /// cursor — its meaning is variant-specific (e.g. the element index for
    /// Sequence, the count of candidates tried for OneOf), so treat it as
    /// "which slot to resume into," not a literal child ordinal.
    WaitingForChild { child_index: usize },
    /// Processing results after all children complete
    Combining,
    /// Ready to return result
    Complete(Arc<MatchResult>),
}

/// Variant-specific working state carried by a frame across its lifecycle.
///
/// One variant per compound grammar, each holding its named `*State` struct.
/// The data lives here (not in the matcher) because frames are heterogeneous
/// values on a single `Vec` stack; the active variant is the discriminant the
/// `WaitingForChild`/`Combining` dispatch matches on. Accessors in
/// [`super::table_driven::contexts`] (`as_*_mut`) hand a matcher a typed
/// `&mut *State` for one variant.
///
/// Field-name conventions follow the position-index glossary in the module
/// docs (`start_idx` / `matched_idx` / `working_idx` / `max_idx`).
#[derive(Debug, Clone)]
pub enum FrameContext {
    None,
    OneOf(OneOfState),
    Sequence(SequenceState),
    Ref(RefState),
    Delimited(DelimitedState),
    Bracketed(BracketedState),
    AnyNumberOf(AnyNumberOfState),
}

/// Working state for an `AnyNumberOf` frame (see [`FrameContext::AnyNumberOf`]).
///
/// AnyNumberOf repeatedly matches its elements, keeping the best candidate per
/// repetition and accumulating successful repetitions into `matched`.
#[derive(Debug, Clone)]
pub struct AnyNumberOfState {
    pub grammar_id: GrammarId,
    pub pruned_children: SmallVec<[GrammarId; 8]>,
    pub count: usize,
    pub matched_idx: usize,
    pub working_idx: usize,
    pub option_counter: HashMap<u64, usize>,
    pub max_idx: usize,
    pub last_child_frame_id: Option<usize>,
    pub matched: Arc<MatchResult>,
    /// Best candidate for the current repetition, as `(result, matched_grammar_id)`.
    /// AnyNumberOf compares candidates by absolute end position only
    /// (longest wins) and does NOT apply OneOf's clean-vs-unclean tiebreak —
    /// `parity::MatchQualityPolicy::LongestEnd`, applied in
    /// `contexts.rs::AnyNumberOfState::update_longest_match`.
    ///
    /// NOTE: deliberately different shape/semantics from
    /// `OneOfState::longest_match` (`LongestClean`). Both rules live in
    /// `parity::is_better_candidate`.
    pub longest_match: (Arc<MatchResult>, Option<GrammarId>),
    /// Number of elements tried for current repetition
    pub tried_elements: usize,
}

/// Working state for a `Delimited` frame (see [`FrameContext::Delimited`]).
///
/// Delimited alternates between matching list elements and delimiters (see
/// [`DelimitedPhase`]), holding each matched delimiter back until the next
/// element confirms it.
#[derive(Debug, Clone)]
pub struct DelimitedState {
    pub grammar_id: GrammarId,
    pub delimiter_count: usize,
    pub matched_idx: usize,
    pub working_idx: usize,
    pub max_idx: usize,
    pub phase: DelimitedPhase,
    pub last_child_frame_id: Option<usize>,
    /// A matched delimiter held back until the *next* element matches, so a
    /// trailing delimiter is not folded into the result unless something
    /// follows it (or `allow_trailing` permits it). `take()`n when consumed.
    pub delimiter_match: Option<Arc<MatchResult>>,
    /// Backtrack point captured before consuming a delimiter, so the
    /// delimiter can be un-consumed if it turns out to terminate the list.
    pub pos_before_delimiter: Option<usize>,
    /// Terminators to pass to child element frames (excludes local terminators)
    /// Python parity: local terminators (e.g., ObjectReferenceTerminatorGrammar)
    /// are checked at Delimited level, not passed to longest_match
    pub child_terminators: Vec<GrammarId>,
    pub working_match: Arc<MatchResult>,
}

/// Working state for a `Bracketed` frame (see [`FrameContext::Bracketed`]).
///
/// Bracketed matches an opening bracket, its content elements (an implicit
/// Sequence over `content_ids`), and a closing bracket (see [`BracketedPhase`]).
#[derive(Debug, Clone)]
pub struct BracketedState {
    pub grammar_id: GrammarId,
    pub phase: BracketedPhase,
    pub last_child_frame_id: Option<usize>,
    pub bracket_max_idx: Option<usize>,
    /// Multiple content elements treated as implicit Sequence.
    pub content_ids: Vec<GrammarId>,
    /// Current content element being parsed.
    pub content_idx: usize,
    /// When Some, override content grammar's parse_mode with this value
    /// Python parity: Bracketed inherits from Sequence, so content uses Bracketed's parse_mode
    pub parse_mode_override: Option<ParseMode>,
    /// Store child matches here until sequence is complete.
    pub child_matches: Vec<Arc<MatchResult>>,
}

/// Working state for a `Sequence` frame (see [`FrameContext::Sequence`]).
///
/// A Sequence matches its elements in order, buffering meta (Indent/Dedent)
/// elements and folding each child match into the committed frontier.
#[derive(Debug, Clone)]
pub struct SequenceState {
    pub seq_grammar_id: GrammarId,
    pub start_idx: usize,
    pub matched_idx: usize,
    pub max_idx: usize,
    /// Max_idx before GREEDY_ONCE_STARTED trimming.
    pub original_max_idx: usize,
    pub last_child_frame_id: Option<usize>,
    /// Track which element we're currently processing.
    pub current_element_idx: usize,
    /// For GREEDY_ONCE_STARTED: trim max_idx after first match.
    pub first_match: bool,
    /// Buffer for meta elements to be flushed after matching content.
    pub meta_buffer: Vec<MetaSegment>,
    /// (position, segments) to insert.
    pub insert_segments: Vec<(usize, MetaSegment)>,
    /// Store child matches here until sequence is complete.
    pub child_matches: Vec<Arc<MatchResult>>,
    /// Terminators to pass to child element frames (excludes Sequence's own terminators).
    /// Python parity: Python's Sequence does NOT push its own terminators into
    /// parse_context.terminators. Children only see parent terminators, not the
    /// Sequence's local terminators. The Sequence uses the combined set (own + parent)
    /// only for its own trim_to_terminator / max_idx computation.
    pub child_terminators: Vec<GrammarId>,
}

/// Working state for a `OneOf` frame (see [`FrameContext::OneOf`]).
///
/// OneOf tries each (pruned) alternative from the same start position and
/// keeps the best candidate per its match-quality policy.
#[derive(Debug, Clone)]
pub struct OneOfState {
    pub grammar_id: GrammarId,
    /// Children after simple_hint pruning.
    pub pruned_children: SmallVec<[GrammarId; 8]>,
    pub post_skip_pos: usize,
    /// Best candidate seen so far, as `(result, consumed, child_grammar_id)`
    /// where `consumed = child_end_pos - post_skip_pos` (token count, NOT an
    /// absolute position). OneOf keeps the *longest clean* match: a clean
    /// (no-unparsable) candidate beats an unclean one of equal length
    /// (`parity::MatchQualityPolicy::LongestClean`).
    ///
    /// NOTE: deliberately different from `AnyNumberOfState::longest_match`,
    /// which compares absolute end position and ignores cleanliness
    /// (`LongestEnd`). Both rules live in `parity::is_better_candidate`.
    pub longest_match: Option<(Arc<MatchResult>, usize, GrammarId)>,
    pub tried_elements: usize,
    pub max_idx: usize,
    pub last_child_frame_id: Option<usize>,
    /// Child currently being tried.
    pub current_child_id: Option<GrammarId>,
}

/// Working state for a `Ref` frame (see [`FrameContext::Ref`]).
///
/// A Ref resolves a named rule to its underlying grammar and delegates the
/// match to it, then wraps the child result in a named segment.
#[derive(Debug, Clone)]
pub struct RefState {
    pub grammar_id: GrammarId,
    pub name: &'static str,
    pub segment_class_name: Option<&'static str>,
    pub segment_type: Option<&'static str>,
    /// Position the child was started at (after any leading-transparent skip);
    /// the position restored when the child comes back empty.
    pub saved_pos: usize,
    pub last_child_frame_id: Option<usize>,
    /// The actual grammar this Ref resolves to (for casefold lookup).
    pub child_grammar_id: GrammarId,
    pub match_result: Option<Arc<MatchResult>>,
}

/// Sub-state for Bracketed parsing. The `WaitingForChild` handler in
/// `bracketed.rs` branches on this to decide what the just-finished child was.
#[derive(Debug, Clone)]
pub enum BracketedPhase {
    /// Matching the opening bracket (start_bracket).
    MatchingOpen,
    /// Matching the content between the brackets (an implicit Sequence over
    /// `content_ids`).
    MatchingContent,
    /// Matching the closing bracket (end_bracket).
    MatchingClose,
    /// Successfully matched all parts: open + content + close.
    Complete,
}

/// Sub-state for Delimited parsing. The `WaitingForChild` handler in
/// `delimited.rs` alternates between these: an element, then a delimiter, then
/// the next element, until termination.
#[derive(Debug, Clone)]
pub enum DelimitedPhase {
    /// Matching a list element.
    MatchingElement,
    /// Matching the delimiter that separates two elements.
    MatchingDelimiter,
}
