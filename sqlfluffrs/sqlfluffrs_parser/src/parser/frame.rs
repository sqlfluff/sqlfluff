//! Parse frame types and state management for the iterative parser.
//!
//! This module contains the core types used by the iterative parser to track
//! parsing state without recursion.

use hashbrown::HashMap;

use super::match_result::MatchResult;
use super::types::Node;
use sqlfluffrs_types::GrammarId;

/// State machine for each frame
#[derive(Debug, Clone)]
pub enum FrameState {
    /// Initial state - need to start parsing
    Initial,
    /// Waiting for child results (for grammars with children)
    WaitingForChild {
        child_index: usize,
        total_children: usize,
    },
    /// Processing results after all children complete
    Combining,
    /// Ready to return result
    Complete(MatchResult),
}

/// Additional context data for specific grammar types
#[derive(Debug, Clone)]
pub enum FrameContext {
    None,
    // Table-driven variants (for gradual migration)
    OneOfTableDriven {
        grammar_id: GrammarId,
        pruned_children: Vec<GrammarId>, // Children after simple_hint pruning
        leading_ws: Vec<MatchResult>,
        post_skip_pos: usize,
        longest_match: Option<(MatchResult, usize, GrammarId)>, // (match_result, consumed, child_grammar_id)
        tried_elements: usize,
        max_idx: usize,
        last_child_frame_id: Option<usize>,
        current_child_id: Option<GrammarId>, // Child currently being tried
        initial_collected_positions: hashbrown::HashSet<usize>, // Snapshot for rollback between children
    },
    SequenceTableDriven {
        grammar_id: GrammarId,
        matched_idx: usize,
        max_idx: usize,
        original_max_idx: usize, // Max_idx before GREEDY_ONCE_STARTED trimming
        last_child_frame_id: Option<usize>,
        current_element_idx: usize, // Track which element we're currently processing
        first_match: bool,          // For GREEDY_ONCE_STARTED: trim max_idx after first match
        optional: bool,             // Sequence-level optional flag
        meta_buffer: Vec<GrammarId>, // Buffer for meta elements to be flushed after matching content
    },
    RefTableDriven {
        grammar_id: GrammarId,
        name: String,
        segment_type: Option<String>,
        saved_pos: usize, // Position before skipping transparent tokens
        last_child_frame_id: Option<usize>,
        leading_transparent: Vec<MatchResult>,
        child_grammar_id: GrammarId, // The actual grammar this Ref resolves to (for casefold lookup)
    },
    DelimitedTableDriven {
        grammar_id: GrammarId,
        delimiter_count: usize,
        matched_idx: usize,
        working_idx: usize,
        max_idx: usize,
        state: DelimitedState,
        last_child_frame_id: Option<usize>,
        delimiter_match: Option<MatchResult>,
        pos_before_delimiter: Option<usize>,
        element_children: Vec<GrammarId>,
        /// Terminators to pass to child element frames (excludes local terminators)
        /// Python parity: local terminators (e.g., ObjectReferenceTerminatorGrammar)
        /// are checked at Delimited level, not passed to longest_match
        child_terminators: Vec<GrammarId>,
    },
    BracketedTableDriven {
        grammar_id: GrammarId,
        state: BracketedState,
        last_child_frame_id: Option<usize>,
        bracket_max_idx: Option<usize>,
        content_ids: Vec<GrammarId>, // Multiple content elements treated as implicit Sequence
        content_idx: usize,          // Current content element being parsed
    },
    AnyNumberOfTableDriven {
        grammar_id: GrammarId,
        pruned_children: Vec<GrammarId>,
        count: usize,
        matched_idx: usize,
        working_idx: usize,
        option_counter: HashMap<u64, usize>,
        max_idx: usize,
        last_child_frame_id: Option<usize>,
        /// Track longest match among element candidates for current repetition
        /// (match_result, end_pos, matched_grammar_id)
        longest_match: Option<(MatchResult, usize, GrammarId)>,
        /// Number of elements tried for current repetition
        tried_elements: usize,
    },
}

/// State for Bracketed parsing
#[derive(Debug, Clone)]
pub enum BracketedState {
    MatchingOpen,
    MatchingContent,
    MatchingClose,
    Complete, // Successfully matched all parts: open + content + close
}

/// State for Delimited parsing
#[derive(Debug, Clone)]
pub enum DelimitedState {
    MatchingElement,
    MatchingDelimiter,
}
