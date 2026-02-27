use std::sync::Arc;

use sqlfluffrs_types::GrammarId;

use crate::parser::{FrameContext, MatchResult};

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
                longest_match,
                tried_elements,
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
    pub longest_match: &'a mut Option<(Arc<MatchResult>, usize, GrammarId)>,
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
        let is_better = if let Some((_, current_end_pos, _)) = self.longest_match {
            end_pos > *current_end_pos
        } else {
            true
        };

        if is_better {
            *self.longest_match = Some((child_match, end_pos, grammar_id));
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
        *self.longest_match = None;
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
