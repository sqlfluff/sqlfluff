//! Parse frame types and state management for the iterative parser.
//!
//! This module contains the core types used by the iterative parser to track
//! parsing state without recursion.

use super::types::{Grammar, Node, ParseMode};

/// A parse frame represents a single parsing task in the iterative parser.
///
/// Instead of using recursion, the parser maintains a stack of frames,
/// where each frame represents parsing a particular grammar element at a
/// specific position in the token stream.
#[derive(Debug, Clone)]
pub struct ParseFrame {
    /// Unique ID for this frame
    pub frame_id: usize,
    /// The grammar to parse
    pub grammar: Grammar,
    /// Position in token stream
    pub pos: usize,
    /// Terminators for this parse
    pub terminators: Vec<Grammar>,
    /// Current state of this frame
    pub state: FrameState,
    /// Accumulated results so far
    pub accumulated: Vec<Node>,
    /// Additional context depending on grammar type
    pub context: FrameContext,
    /// Parent's max_idx limit (simulates Python's segments[:max_idx] slicing)
    /// If Some(n), this frame cannot match beyond position n
    pub parent_max_idx: Option<usize>,
}

impl ParseFrame {
    /// Create a new child frame with common default settings
    pub fn new_child(
        frame_id: usize,
        grammar: Grammar,
        pos: usize,
        terminators: Vec<Grammar>,
        parent_max_idx: Option<usize>,
    ) -> Self {
        ParseFrame {
            frame_id,
            grammar,
            pos,
            terminators,
            state: FrameState::Initial,
            accumulated: vec![],
            context: FrameContext::None,
            parent_max_idx,
        }
    }

    /// Update the last_child_frame_id for the parent frame on the stack
    /// Returns true if the update succeeded, false if parent wasn't found or had wrong context type
    pub fn update_parent_last_child_id(
        stack: &mut Vec<ParseFrame>,
        context_type: &str,
        child_frame_id: usize,
    ) -> bool {
        if let Some(parent_frame) = stack.last_mut() {
            match (&mut parent_frame.context, context_type) {
                (
                    FrameContext::Sequence {
                        last_child_frame_id,
                        ..
                    },
                    "Sequence",
                ) => {
                    *last_child_frame_id = Some(child_frame_id);
                    true
                }
                (
                    FrameContext::AnyNumberOf {
                        last_child_frame_id,
                        ..
                    },
                    "AnyNumberOf",
                ) => {
                    *last_child_frame_id = Some(child_frame_id);
                    true
                }
                (
                    FrameContext::OneOf {
                        last_child_frame_id,
                        ..
                    },
                    "OneOf",
                ) => {
                    *last_child_frame_id = Some(child_frame_id);
                    true
                }
                (
                    FrameContext::Bracketed {
                        last_child_frame_id,
                        ..
                    },
                    "Bracketed",
                ) => {
                    *last_child_frame_id = Some(child_frame_id);
                    true
                }
                (
                    FrameContext::AnySetOf {
                        last_child_frame_id,
                        ..
                    },
                    "AnySetOf",
                ) => {
                    *last_child_frame_id = Some(child_frame_id);
                    true
                }
                (
                    FrameContext::Delimited {
                        last_child_frame_id,
                        ..
                    },
                    "Delimited",
                ) => {
                    *last_child_frame_id = Some(child_frame_id);
                    true
                }
                (
                    FrameContext::Ref {
                        last_child_frame_id,
                        ..
                    },
                    "Ref",
                ) => {
                    *last_child_frame_id = Some(child_frame_id);
                    true
                }
                _ => false,
            }
        } else {
            false
        }
    }

    /// Push a child frame onto the stack and update parent's last_child_frame_id
    /// Also pushes the parent frame back onto the stack first (for use in WaitingForChild handlers)
    /// Returns the new frame_id_counter value
    pub fn push_child_and_update_parent(
        stack: &mut Vec<ParseFrame>,
        parent_frame: ParseFrame,
        child_frame: ParseFrame,
        frame_id_counter: &mut usize,
        parent_context_type: &str,
    ) {
        let child_id = child_frame.frame_id;

        // Push parent back onto stack first
        stack.push(parent_frame);

        // Update parent's last_child_frame_id
        Self::update_parent_last_child_id(stack, parent_context_type, child_id);

        // Increment counter and push child
        *frame_id_counter += 1;
        stack.push(child_frame);
    }

    /// Specialized version for Sequence that also updates current_element_idx
    pub fn push_sequence_child_and_update_parent(
        stack: &mut Vec<ParseFrame>,
        parent_frame: ParseFrame,
        child_frame: ParseFrame,
        frame_id_counter: &mut usize,
        next_element_idx: usize,
    ) {
        let child_id = child_frame.frame_id;

        // Push parent back onto stack first
        let parent_id = parent_frame.frame_id;
        stack.push(parent_frame);

        // Update parent's last_child_frame_id AND current_element_idx
        if let Some(parent_frame) = stack.last_mut() {
            if let FrameContext::Sequence {
                last_child_frame_id,
                current_element_idx,
                ..
            } = &mut parent_frame.context
            {
                log::debug!("DEBUG: push_sequence_child_and_update_parent - parent {}, child {}, setting last_child_frame_id to {}",
                    parent_id, child_id, child_id);
                *last_child_frame_id = Some(child_id);
                *current_element_idx = next_element_idx;
            }
        }

        // Increment counter and push child
        *frame_id_counter += 1;
        stack.push(child_frame);
    }

    /// Update Sequence parent on stack and push child (for Initial state)
    /// Assumes parent is already on the stack
    pub fn update_sequence_parent_and_push_child(
        stack: &mut Vec<ParseFrame>,
        child_frame: ParseFrame,
        frame_id_counter: &mut usize,
        element_idx: usize,
    ) {
        let child_id = child_frame.frame_id;

        // Update parent's last_child_frame_id AND current_element_idx
        if let Some(parent_frame) = stack.last_mut() {
            if let FrameContext::Sequence {
                last_child_frame_id,
                current_element_idx,
                ..
            } = &mut parent_frame.context
            {
                *last_child_frame_id = Some(child_id);
                *current_element_idx = element_idx;
            }
        }

        // Increment counter and push child
        *frame_id_counter += 1;
        stack.push(child_frame);
    }
}

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
    Complete(Node),
}

/// Additional context data for specific grammar types
#[derive(Debug, Clone)]
pub enum FrameContext {
    None,
    Ref {
        name: String,
        optional: bool,
        allow_gaps: bool,
        segment_type: Option<String>,
        saved_pos: usize, // Position before skipping transparent tokens
        last_child_frame_id: Option<usize>, // Track which child frame we created
    },
    Sequence {
        elements: Vec<Grammar>,
        allow_gaps: bool,
        optional: bool,
        parse_mode: ParseMode,
        matched_idx: usize,
        tentatively_collected: Vec<usize>,
        max_idx: usize,
        original_max_idx: usize, // Max_idx before GREEDY_ONCE_STARTED trimming, used for creating children
        last_child_frame_id: Option<usize>,
        current_element_idx: usize, // Track which element we're currently processing
        first_match: bool,          // For GREEDY_ONCE_STARTED: trim max_idx after first match
    },
    OneOf {
        elements: Vec<Grammar>, // Available elements to try
        allow_gaps: bool,
        optional: bool,
        leading_ws: Vec<Node>,
        post_skip_pos: usize,
        longest_match: Option<(Node, usize, u64)>, // (node, consumed, element_key)
        tried_elements: usize,
        max_idx: usize, // Limit for greedy matching
        parse_mode: ParseMode,
        last_child_frame_id: Option<usize>, // Track child frame for WaitingForChild state
    },
    AnyNumberOf {
        min_times: usize,
        max_times: Option<usize>,
        max_times_per_element: Option<usize>,
        allow_gaps: bool,
        optional: bool,
        count: usize,
        matched_idx: usize,
        working_idx: usize,
        option_counter: std::collections::HashMap<u64, usize>,
        max_idx: usize,
        last_child_frame_id: Option<usize>,
        elements: Vec<Grammar>,
        parse_mode: ParseMode,
    },
    AnySetOf {
        min_times: usize,
        max_times: Option<usize>,
        allow_gaps: bool,
        optional: bool,
        count: usize,
        matched_idx: usize,
        working_idx: usize,
        matched_elements: std::collections::HashSet<u64>,
        max_idx: usize,
        last_child_frame_id: Option<usize>,
        elements: Vec<Grammar>,
        parse_mode: ParseMode,
    },
    Bracketed {
        bracket_pairs: (Box<Grammar>, Box<Grammar>),
        elements: Vec<Grammar>,
        allow_gaps: bool,
        optional: bool,
        parse_mode: ParseMode,
        state: BracketedState,
        last_child_frame_id: Option<usize>,
    },
    Delimited {
        elements: Vec<Grammar>,
        delimiter: Box<Grammar>,
        allow_trailing: bool,
        optional: bool,
        allow_gaps: bool,
        min_delimiters: usize,
        parse_mode: ParseMode,
        delimiter_count: usize,
        matched_idx: usize,
        working_idx: usize,
        max_idx: usize,
        state: DelimitedState,
        last_child_frame_id: Option<usize>,
    },
}

/// State for Bracketed parsing
#[derive(Debug, Clone)]
pub enum BracketedState {
    MatchingOpen,
    MatchingContent,
    MatchingClose,
}

/// State for Delimited parsing
#[derive(Debug, Clone)]
pub enum DelimitedState {
    MatchingElement,
    MatchingDelimiter,
}
