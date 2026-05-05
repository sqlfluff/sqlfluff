use smallvec::SmallVec;
use sqlfluffrs_types::{GrammarId, GrammarVariant, ParseMode};
use std::sync::Arc;

use crate::parser::{FrameContext, FrameState, MatchResult};

#[cfg(feature = "verbose-debug")]
use crate::vdebug;

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
    /// Results map: frame_id -> (Arc<MatchResult>, end_pos, element_key)
    /// Using Rc to avoid expensive clones of MatchResults
    pub results: hashbrown::HashMap<usize, (Arc<MatchResult>, usize, Option<u64>)>,
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

    pub fn push(&mut self, frame: TableParseFrame) {
        self.stack.push(frame);
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

    #[inline]
    pub(crate) fn insert_empty_result(&mut self, frame_id: usize, pos: usize) {
        self.results
            .insert(frame_id, (Arc::new(MatchResult::empty_at(pos)), pos, None));
    }

    #[inline]
    pub(crate) fn insert_result(
        &mut self,
        frame_id: usize,
        match_result: MatchResult,
        end_pos: usize,
    ) {
        self.results
            .insert(frame_id, (Arc::new(match_result), end_pos, None));
    }

    #[inline]
    pub(crate) fn insert_arc_result(
        &mut self,
        frame_id: usize,
        match_result: Arc<MatchResult>,
        end_pos: usize,
    ) {
        self.results.insert(frame_id, (match_result, end_pos, None));
    }

    #[inline]
    pub(crate) fn insert_arc_result_with_key(
        &mut self,
        frame_id: usize,
        match_result: Arc<MatchResult>,
        end_pos: usize,
        element_key: Option<u64>,
    ) {
        self.results
            .insert(frame_id, (match_result, end_pos, element_key));
    }

    /// Push child frame and update parent to wait for it
    #[inline]
    pub(crate) fn push_child_and_wait(
        &mut self,
        mut parent: TableParseFrame,
        child: TableParseFrame,
        child_index: usize,
    ) -> TableFrameResult {
        parent.state = FrameState::WaitingForChild { child_index };
        self.push(parent);
        self.push(child);
        self.increment_frame_id_counter();
        TableFrameResult::Done
    }

    #[inline]
    pub(crate) fn transition_to_combining(
        &mut self,
        mut frame: TableParseFrame,
        end_pos: Option<usize>,
    ) -> TableFrameResult {
        frame.transition_to_combining(end_pos);
        self.push(frame);
        TableFrameResult::Done
    }

    /// Complete a frame and insert into results map
    #[inline]
    pub(crate) fn complete_frame(
        &mut self,
        mut frame: TableParseFrame,
        result: Arc<MatchResult>,
    ) -> TableFrameResult {
        let pos = result.end();
        frame.end_pos = Some(pos);
        frame.state = FrameState::Complete(result);
        self.push(frame);
        // self.insert_result(frame.frame_id, result, pos);
        TableFrameResult::Done
    }

    /// Complete a frame with empty result
    #[inline]
    pub(crate) fn complete_frame_empty(&mut self, frame: &TableParseFrame) -> TableFrameResult {
        self.insert_empty_result(frame.frame_id, frame.pos);
        TableFrameResult::Done
    }

    /// Complete a frame with empty result
    #[inline]
    pub(crate) fn complete_frame_empty_at_pos(
        &mut self,
        frame: &TableParseFrame,
        pos: usize,
    ) -> TableFrameResult {
        self.insert_empty_result(frame.frame_id, pos);
        TableFrameResult::Done
    }

    /// Update the last_child_frame_id for the parent frame on the stack
    /// Returns true if the update succeeded, false if parent wasn't found or had wrong context type
    pub fn update_parent_last_child_id(
        &mut self,
        context_type: GrammarVariant,
        child_frame_id: usize,
    ) -> bool {
        if let Some(parent_frame) = self.last_mut() {
            match (&mut parent_frame.context, context_type) {
                (
                    FrameContext::SequenceTableDriven {
                        last_child_frame_id,
                        ..
                    },
                    GrammarVariant::Sequence,
                )
                | (
                    FrameContext::OneOfTableDriven {
                        last_child_frame_id,
                        ..
                    },
                    GrammarVariant::OneOf,
                )
                | (
                    FrameContext::BracketedTableDriven {
                        last_child_frame_id,
                        ..
                    },
                    GrammarVariant::Bracketed,
                )
                | (
                    FrameContext::DelimitedTableDriven {
                        last_child_frame_id,
                        ..
                    },
                    GrammarVariant::Delimited,
                )
                | (
                    FrameContext::RefTableDriven {
                        last_child_frame_id,
                        ..
                    },
                    GrammarVariant::Ref,
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
        &mut self,
        mut parent_frame: TableParseFrame,
        child_frame: TableParseFrame,
        parent_context_type: GrammarVariant,
    ) {
        let child_id = child_frame.frame_id;

        // Update parent's last_child_frame_id BEFORE pushing
        match (&mut parent_frame.context, parent_context_type) {
            (
                FrameContext::SequenceTableDriven {
                    last_child_frame_id,
                    ..
                },
                GrammarVariant::Sequence,
            )
            | (
                FrameContext::OneOfTableDriven {
                    last_child_frame_id,
                    ..
                },
                GrammarVariant::OneOf,
            )
            | (
                FrameContext::BracketedTableDriven {
                    last_child_frame_id,
                    ..
                },
                GrammarVariant::Bracketed,
            )
            | (
                FrameContext::DelimitedTableDriven {
                    last_child_frame_id,
                    ..
                },
                GrammarVariant::Delimited,
            )
            | (
                FrameContext::RefTableDriven {
                    last_child_frame_id,
                    ..
                },
                GrammarVariant::Ref,
            ) => {
                *last_child_frame_id = Some(child_id);
            }
            _ => {}
        }

        // Push parent and child
        self.push(parent_frame);
        self.increment_frame_id_counter();
        self.push(child_frame);
    }

    /// Specialized version for Sequence that also updates current_element_idx
    pub fn push_sequence_child_and_update_parent(
        &mut self,
        mut parent_frame: TableParseFrame,
        child_frame: TableParseFrame,
        next_element_idx: usize,
    ) {
        let child_id = child_frame.frame_id;

        // Update parent's last_child_frame_id AND current_element_idx BEFORE pushing
        #[cfg(feature = "verbose-debug")]
        let parent_id = parent_frame.frame_id;
        if let FrameContext::SequenceTableDriven {
            last_child_frame_id,
            current_element_idx,
            ..
        } = &mut parent_frame.context
        {
            vdebug!("DEBUG: push_sequence_child_and_update_parent (table) - parent {}, child {}, setting last_child_frame_id to {}",
                parent_id, child_id, child_id);
            *last_child_frame_id = Some(child_id);
            *current_element_idx = next_element_idx;
        }

        // Push parent and child
        self.push(parent_frame);
        self.increment_frame_id_counter();
        self.push(child_frame);
    }

    /// Update Sequence parent on stack and push child (for WaitingForChild state)
    /// Assumes parent is already on the stack
    pub fn update_sequence_parent_and_push_child(
        &mut self,
        child_frame: TableParseFrame,
        next_element_idx: usize,
    ) -> TableFrameResult {
        let child_id = child_frame.frame_id;

        // Update parent's last_child_frame_id, current_element_idx, AND state
        if let Some(parent_frame) = self.last_mut() {
            if let FrameContext::SequenceTableDriven {
                last_child_frame_id,
                current_element_idx,
                ..
            } = &mut parent_frame.context
            {
                *last_child_frame_id = Some(child_id);
                *current_element_idx = next_element_idx;
            }
            // CRITICAL: Set parent state to WaitingForChild so it knows to process child result
            parent_frame.state = FrameState::WaitingForChild {
                child_index: next_element_idx,
            };
        }

        // Increment counter and push child
        self.increment_frame_id_counter();
        self.push(child_frame);
        TableFrameResult::Done
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
    /// SmallVec avoids heap allocation for common case of 0-4 terminators
    pub table_terminators: SmallVec<[GrammarId; 4]>,
    /// Current state of this frame
    pub state: FrameState,
    /// Additional context depending on grammar type
    pub context: FrameContext,
    /// Parent's max_idx limit (simulates Python's segments[:max_idx] slicing)
    /// If Some(n), this frame cannot match beyond position n
    pub parent_max_idx: Option<usize>,
    /// Handler-calculated max_idx after considering terminators and parse mode
    /// Set by handlers (Sequence, OneOf, etc.) after they calculate their effective max_idx
    /// Used for cache key to ensure consistency between cache checks and stores
    pub calculated_max_idx: Option<usize>,
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
        table_terminators: &[GrammarId],
        parent_max_idx: Option<usize>,
    ) -> Self {
        TableParseFrame {
            frame_id,
            grammar_id,
            pos,
            table_terminators: SmallVec::from_slice(table_terminators),
            state: FrameState::Initial,
            context: FrameContext::None,
            parent_max_idx,
            calculated_max_idx: None,
            end_pos: None,
            transparent_positions: None,
            element_key: None,
            parse_mode_override: None,
        }
    }

    fn transition_to_combining(&mut self, end_pos: Option<usize>) {
        if let Some(pos) = end_pos {
            self.end_pos = Some(pos);
        }
        self.state = FrameState::Combining;
    }
}
