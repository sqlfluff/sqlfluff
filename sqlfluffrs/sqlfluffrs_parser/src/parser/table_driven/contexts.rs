use std::sync::Arc;

use sqlfluffrs_types::GrammarId;

use crate::parser::{FrameContext, MatchResult, MetaSegment};

impl FrameContext {
    #[inline]
    pub(crate) fn as_anynumberof_mut(&mut self) -> Option<AnyNumberOfContextMut<'_>> {
        match self {
            FrameContext::AnyNumberOfTableDriven {
                grammar_id,
                pruned_children,
                count,
                matched_idx,
                working_idx,
                option_counter,
                max_idx,
                last_child_frame_id,
                matched,
                longest_match,
                tried_elements,
            } => Some(AnyNumberOfContextMut {
                grammar_id,
                pruned_children,
                count,
                matched_idx,
                working_idx,
                option_counter,
                max_idx,
                last_child_frame_id,
                matched,
                longest_match,
                tried_elements,
            }),
            _ => None,
        }
    }

    #[inline]
    pub(crate) fn as_sequence_mut(&mut self) -> Option<SequenceContextMut<'_>> {
        match self {
            FrameContext::SequenceTableDriven {
                seq_grammar_id,
                start_idx,
                matched_idx,
                max_idx,
                original_max_idx,
                current_element_idx,
                first_match,
                meta_buffer,
                insert_segments,
                child_matches,
                ..
            } => Some(SequenceContextMut {
                seq_grammar_id,
                start_idx,
                matched_idx,
                max_idx,
                original_max_idx,
                current_element_idx,
                first_match,
                meta_buffer,
                insert_segments,
                child_matches,
            }),
            _ => None,
        }
    }
}

pub struct AnyNumberOfContextMut<'a> {
    pub grammar_id: &'a GrammarId,
    pub pruned_children: &'a mut Vec<GrammarId>,
    pub count: &'a mut usize,
    pub matched_idx: &'a mut usize,
    pub working_idx: &'a mut usize,
    pub option_counter: &'a mut hashbrown::HashMap<u64, usize>,
    pub max_idx: &'a mut usize,
    pub last_child_frame_id: &'a mut Option<usize>,
    pub matched: &'a mut Arc<MatchResult>,
    pub longest_match: &'a mut (Arc<MatchResult>, Option<GrammarId>),
    pub tried_elements: &'a mut usize,
}

impl<'a> AnyNumberOfContextMut<'a> {
    #[inline]
    pub(crate) fn update_longest_match(
        &mut self,
        child_match: Arc<MatchResult>,
        end_pos: usize,
        grammar_id: GrammarId,
    ) {
        let is_better = end_pos > self.longest_match.0.end();

        if is_better {
            *self.longest_match = (child_match, Some(grammar_id));
            vdebug!(
                "AnyNumberOf[table]: Updated longest_match: child_id={}, end_pos={}",
                grammar_id.0,
                end_pos
            );
        }
    }

    #[inline]
    pub(crate) fn increment_element_count(&mut self, element_key: u64) -> usize {
        let count_for_element = self.option_counter.entry(element_key).or_insert(0);
        *count_for_element += 1;
        *count_for_element
    }

    #[inline]
    pub(crate) fn reset_for_next_repetition(&mut self, new_pruned_children: &[GrammarId]) {
        *self.pruned_children = new_pruned_children.to_vec();
        *self.longest_match = (
            Arc::new(MatchResult::empty_at(self.longest_match.0.end())),
            None,
        );
        *self.tried_elements = 0;
    }

    #[inline]
    pub(crate) fn has_more_candidates(&self) -> bool {
        *self.tried_elements < self.pruned_children.len()
    }

    #[inline]
    pub(crate) fn next_candidate_idx(&self) -> usize {
        *self.tried_elements
    }
}

pub struct SequenceContextMut<'a> {
    pub seq_grammar_id: &'a GrammarId,
    pub start_idx: &'a usize, // This shouldn't change
    pub matched_idx: &'a mut usize,
    pub max_idx: &'a mut usize, // This may change due to GREEDY_ONCE_STARTED
    pub original_max_idx: &'a usize, // Max_idx before GREEDY_ONCE_STARTED trimming
    pub current_element_idx: &'a mut usize, // Track which element we're currently processing
    pub first_match: &'a mut bool, // For GREEDY_ONCE_STARTED: trim max_idx after first match
    pub meta_buffer: &'a mut Vec<MetaSegment>, // Buffer for meta elements to be flushed after matching content
    pub insert_segments: &'a mut Vec<(usize, MetaSegment)>, // (position, segments) to insert
    pub child_matches: &'a mut Vec<Arc<MatchResult>>, // Store child matches here until sequence is complete
}

impl<'a> SequenceContextMut<'a> {
    #[inline]
    pub(crate) fn advance_element_idx(&mut self) {
        *self.current_element_idx += 1;
    }

    #[inline]
    pub(crate) fn is_first_match(&self) -> bool {
        *self.first_match
    }

    #[inline]
    pub(crate) fn mark_first_match_done(&mut self) {
        *self.first_match = false;
    }

    #[inline]
    pub(crate) fn update_matched_idx(&mut self, new_idx: usize) {
        *self.matched_idx = new_idx;
    }

    #[inline]
    pub(crate) fn trim_max_idx(&mut self, new_max_idx: usize) {
        *self.max_idx = new_max_idx.min(*self.original_max_idx);
    }

    #[inline]
    pub(crate) fn buffer_meta(&mut self, meta: MetaSegment) {
        self.meta_buffer.push(meta);
    }

    #[inline]
    pub(crate) fn take_meta_buffer(&mut self) -> Vec<MetaSegment> {
        std::mem::take(self.meta_buffer)
    }

    #[inline]
    pub(crate) fn matched_idx_value(&self) -> usize {
        *self.matched_idx
    }

    #[inline]
    pub(crate) fn max_idx_value(&self) -> usize {
        *self.max_idx
    }
}
