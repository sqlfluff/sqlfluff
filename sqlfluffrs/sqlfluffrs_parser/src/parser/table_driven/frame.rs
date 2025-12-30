use sqlfluffrs_types::{GrammarId, ParseMode};

use crate::parser::{FrameContext, FrameState, MatchResult};

/// Result of frame processing - either finished or needs to push frame back
pub enum TableFrameResult {
    /// Frame processing is complete, don't push back
    Done,
    /// Frame needs to be pushed back with updated state
    Push(TableParseFrame),
}

/// Stack structure for managing ParseFrames and related state
pub struct TableParseFrameStack {
    stack: Vec<TableParseFrame>,
    /// Results map: frame_id -> (MatchResult, end_pos, element_key)
    /// MatchResult replaces Node for functional result composition
    pub results: hashbrown::HashMap<usize, (MatchResult, usize, Option<u64>)>,
    pub frame_id_counter: usize,
    // Add any additional state fields here as needed
}

impl Default for TableParseFrameStack {
    fn default() -> Self {
        Self::new()
    }
}

impl TableParseFrameStack {
    pub fn new() -> Self {
        TableParseFrameStack {
            stack: Vec::new(),
            results: hashbrown::HashMap::new(),
            frame_id_counter: 0,
        }
    }

    pub fn push(&mut self, frame: &mut TableParseFrame) {
        self.stack.push(frame.clone());
    }

    pub fn pop(&mut self) -> Option<TableParseFrame> {
        self.stack.pop()
    }

    pub fn len(&self) -> usize {
        self.stack.len()
    }

    pub fn is_empty(&self) -> bool {
        self.stack.is_empty()
    }

    pub fn last_mut(&mut self) -> Option<&mut TableParseFrame> {
        self.stack.last_mut()
    }

    pub fn iter(&'_ self) -> std::slice::Iter<'_, TableParseFrame> {
        self.stack.iter()
    }

    pub fn increment_frame_id_counter(&mut self) {
        self.frame_id_counter += 1;
    }

    // Add more helper methods as needed for dispatch or state management
}

/// A parse frame represents a single parsing task in the iterative parser.
///
/// Instead of using recursion, the parser maintains a stack of frames,
/// where each frame represents parsing a particular grammar element at a
/// specific position in the token stream.
#[derive(Debug, Clone)]
pub struct TableParseFrame {
    /// Unique ID for this frame
    pub frame_id: usize,
    /// Table-driven grammar ID (for gradual migration to table-based parsing)
    pub grammar_id: GrammarId,
    /// Position in token stream
    pub pos: usize,
    /// When Some, this frame uses table-driven parsing
    /// Table-driven terminators (parallel to terminators field)
    pub table_terminators: Vec<GrammarId>,
    /// Current state of this frame
    pub state: FrameState,
    /// Accumulated results (Python parity - stores MatchResult for lazy evaluation)
    pub accumulated: Vec<MatchResult>,
    /// Additional context depending on grammar type
    pub context: FrameContext,
    /// Parent's max_idx limit (simulates Python's segments[:max_idx] slicing)
    /// If Some(n), this frame cannot match beyond position n
    pub parent_max_idx: Option<usize>,
    /// End position for this parse (used when transitioning to Complete state)
    pub end_pos: Option<usize>,
    /// Transparent token positions collected during this parse
    pub transparent_positions: Option<Vec<usize>>,
    /// Element key for this match (used by AnyNumberOf to track per-element counts)
    /// Set by OneOf when storing its result, propagated to parent via results map
    pub element_key: Option<u64>,
    /// Parse mode override for this frame. When Some, this overrides the grammar's native parse_mode.
    /// Used by Bracketed to force content to use GREEDY mode when the Bracketed itself is GREEDY.
    /// This matches Python behavior where Bracketed(parse_mode=GREEDY) inherits from Sequence
    /// and passes its parse_mode to all content elements.
    pub parse_mode_override: Option<ParseMode>,
}

impl TableParseFrame {
    /// Create a new table-driven child frame
    pub fn new_child(
        frame_id: usize,
        grammar_id: GrammarId,
        pos: usize,
        table_terminators: Vec<GrammarId>,
        parent_max_idx: Option<usize>,
    ) -> Self {
        TableParseFrame {
            frame_id,
            grammar_id,
            pos,
            table_terminators,
            state: FrameState::Initial,
            accumulated: vec![],
            context: FrameContext::None,
            parent_max_idx,
            end_pos: None,
            transparent_positions: None,
            element_key: None,
            parse_mode_override: None,
        }
    }

    /// Update the last_child_frame_id for the parent frame on the stack
    /// Returns true if the update succeeded, false if parent wasn't found or had wrong context type
    pub fn update_parent_last_child_id(
        stack: &mut TableParseFrameStack,
        context_type: &str,
        child_frame_id: usize,
    ) -> bool {
        if let Some(parent_frame) = stack.last_mut() {
            match (&mut parent_frame.context, context_type) {
                (
                    FrameContext::SequenceTableDriven {
                        last_child_frame_id,
                        ..
                    },
                    "Sequence",
                ) => {
                    *last_child_frame_id = Some(child_frame_id);
                    true
                }
                (
                    FrameContext::OneOfTableDriven {
                        last_child_frame_id,
                        ..
                    },
                    "OneOf",
                ) => {
                    *last_child_frame_id = Some(child_frame_id);
                    true
                }
                (
                    FrameContext::BracketedTableDriven {
                        last_child_frame_id,
                        ..
                    },
                    "Bracketed",
                ) => {
                    *last_child_frame_id = Some(child_frame_id);
                    true
                }
                (
                    FrameContext::DelimitedTableDriven {
                        last_child_frame_id,
                        ..
                    },
                    "Delimited",
                ) => {
                    *last_child_frame_id = Some(child_frame_id);
                    true
                }
                (
                    FrameContext::RefTableDriven {
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
        stack: &mut TableParseFrameStack,
        parent_frame: &mut TableParseFrame,
        mut child_frame: TableParseFrame,
        parent_context_type: &str,
    ) {
        let child_id = child_frame.frame_id;

        // Push parent back onto stack first
        stack.push(parent_frame);

        // Update parent's last_child_frame_id
        Self::update_parent_last_child_id(stack, parent_context_type, child_id);

        // Increment counter and push child
        stack.increment_frame_id_counter();
        stack.push(&mut child_frame);
    }

    /// Specialized version for Sequence that also updates current_element_idx
    pub fn push_sequence_child_and_update_parent(
        stack: &mut TableParseFrameStack,
        parent_frame: &mut TableParseFrame,
        mut child_frame: TableParseFrame,
        next_element_idx: usize,
    ) {
        let child_id = child_frame.frame_id;

        // Push parent back onto stack first
        let parent_id = parent_frame.frame_id;
        stack.push(parent_frame);

        // Update parent's last_child_frame_id AND current_element_idx
        if let Some(parent_frame) = stack.last_mut() {
            match &mut parent_frame.context {
                FrameContext::SequenceTableDriven {
                    last_child_frame_id,
                    current_element_idx,
                    ..
                } => {
                    log::debug!("DEBUG: push_sequence_child_and_update_parent (table) - parent {}, child {}, setting last_child_frame_id to {}",
                        parent_id, child_id, child_id);
                    *last_child_frame_id = Some(child_id);
                    *current_element_idx = next_element_idx;
                }
                _ => {}
            }
        }

        // Increment counter and push child
        stack.increment_frame_id_counter();
        stack.push(&mut child_frame);
    }

    /// Update Sequence parent on stack and push child (for Initial state)
    /// Assumes parent is already on the stack
    pub fn update_sequence_parent_and_push_child(
        stack: &mut TableParseFrameStack,
        mut child_frame: TableParseFrame,
        element_idx: usize,
    ) {
        let child_id = child_frame.frame_id;

        // Update parent's last_child_frame_id AND current_element_idx
        if let Some(parent_frame) = stack.last_mut() {
            match &mut parent_frame.context {
                FrameContext::SequenceTableDriven {
                    last_child_frame_id,
                    current_element_idx,
                    ..
                } => {
                    *last_child_frame_id = Some(child_id);
                    *current_element_idx = element_idx;
                }
                _ => {}
            }
        }

        // Increment counter and push child
        stack.increment_frame_id_counter();
        stack.push(&mut child_frame);
    }
}
