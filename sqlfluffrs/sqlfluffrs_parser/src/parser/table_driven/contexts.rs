use std::sync::Arc;

use sqlfluffrs_types::GrammarId;

use crate::parser::{table_driven::parity, FrameContext, MatchResult, MetaSegment};

impl FrameContext {
    /// The frame id of the child this frame is currently waiting on, if any.
    ///
    /// Every compound context (`OneOf`/`Sequence`/`Ref`/`Bracketed`/`Delimited`/
    /// `AnyNumberOf`) records the id of the child frame it pushed so its result can be
    /// reclaimed on resume. Returns `None` for `FrameContext::None` and the terminal
    /// variants, which never wait on a child.
    #[inline]
    pub(crate) fn last_child_frame_id(&self) -> Option<usize> {
        match self {
            FrameContext::AnyNumberOf(state) => state.last_child_frame_id,
            FrameContext::Bracketed(state) => state.last_child_frame_id,
            FrameContext::Delimited(state) => state.last_child_frame_id,
            FrameContext::Sequence(state) => state.last_child_frame_id,
            FrameContext::OneOf(state) => state.last_child_frame_id,
            FrameContext::Ref(state) => state.last_child_frame_id,
            FrameContext::None => None,
        }
    }

    /// Record the frame id of the child this frame just pushed.
    ///
    /// Every compound context stores `last_child_frame_id` so the child's result
    /// can be reclaimed from the results map on resume. This is the single writer
    /// for that field; `context_type` guards against a context/variant mismatch
    /// (a no-op for `None`/terminal variants). Returns whether the write landed.
    #[inline]
    pub(crate) fn set_last_child_id(
        &mut self,
        context_type: sqlfluffrs_types::GrammarVariant,
        child_frame_id: usize,
    ) -> bool {
        use sqlfluffrs_types::GrammarVariant;
        match (self, context_type) {
            (FrameContext::Bracketed(state), GrammarVariant::Bracketed) => {
                state.last_child_frame_id = Some(child_frame_id);
                true
            }
            (FrameContext::Delimited(state), GrammarVariant::Delimited) => {
                state.last_child_frame_id = Some(child_frame_id);
                true
            }
            (FrameContext::Sequence(state), GrammarVariant::Sequence) => {
                state.last_child_frame_id = Some(child_frame_id);
                true
            }
            (FrameContext::OneOf(state), GrammarVariant::OneOf) => {
                state.last_child_frame_id = Some(child_frame_id);
                true
            }
            (FrameContext::Ref(state), GrammarVariant::Ref) => {
                state.last_child_frame_id = Some(child_frame_id);
                true
            }
            _ => false,
        }
    }

    #[inline]
    pub(crate) fn as_anynumberof_mut(&mut self) -> Option<&mut crate::parser::AnyNumberOfState> {
        match self {
            FrameContext::AnyNumberOf(state) => Some(state),
            _ => None,
        }
    }

    #[inline]
    pub(crate) fn as_sequence_mut(&mut self) -> Option<&mut crate::parser::SequenceState> {
        match self {
            FrameContext::Sequence(state) => Some(state),
            _ => None,
        }
    }
}

impl crate::parser::AnyNumberOfState {
    /// Keep the candidate with the greatest end position (longest wins).
    ///
    /// This is AnyNumberOf's match-quality policy
    /// ([`parity::MatchQualityPolicy::LongestEnd`]): end-position only, with NO
    /// clean-vs-unclean tiebreak. OneOf uses `LongestClean` instead — both rules
    /// live in [`parity::is_better_candidate`].
    #[inline]
    pub(crate) fn update_longest_match(
        &mut self,
        child_match: Arc<MatchResult>,
        end_pos: usize,
        grammar_id: GrammarId,
    ) {
        // Cleanliness flags are not consulted by the LongestEnd policy.
        let is_better = parity::is_better_candidate(
            parity::MatchQualityPolicy::LongestEnd,
            end_pos,
            true,
            self.longest_match.0.end(),
            true,
        );

        if is_better {
            self.longest_match = (child_match, Some(grammar_id));
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
        self.pruned_children = new_pruned_children.to_vec();
        self.longest_match = (
            Arc::new(MatchResult::empty_at(self.longest_match.0.end())),
            None,
        );
        self.tried_elements = 0;
    }

    #[inline]
    pub(crate) fn has_more_candidates(&self) -> bool {
        self.tried_elements < self.pruned_children.len()
    }

    #[inline]
    pub(crate) fn next_candidate_idx(&self) -> usize {
        self.tried_elements
    }
}

impl crate::parser::SequenceState {
    #[inline]
    pub(crate) fn advance_element_idx(&mut self) {
        self.current_element_idx += 1;
    }

    #[inline]
    pub(crate) fn is_first_match(&self) -> bool {
        self.first_match
    }

    #[inline]
    pub(crate) fn mark_first_match_done(&mut self) {
        self.first_match = false;
    }

    #[inline]
    pub(crate) fn update_matched_idx(&mut self, new_idx: usize) {
        self.matched_idx = new_idx;
    }

    #[inline]
    pub(crate) fn trim_max_idx(&mut self, new_max_idx: usize) {
        self.max_idx = new_max_idx.min(self.original_max_idx);
    }

    #[inline]
    pub(crate) fn buffer_meta(&mut self, meta: MetaSegment) {
        self.meta_buffer.push(meta);
    }

    #[inline]
    pub(crate) fn take_meta_buffer(&mut self) -> Vec<MetaSegment> {
        std::mem::take(&mut self.meta_buffer)
    }

    #[inline]
    pub(crate) fn matched_idx_value(&self) -> usize {
        self.matched_idx
    }

    #[inline]
    pub(crate) fn max_idx_value(&self) -> usize {
        self.max_idx
    }
}
