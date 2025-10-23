use crate::parser::{Node, ParseError, ParseFrame, ParseMode, Grammar};
use crate::parser::iterative::{NextStep, ParseFrameStack};
use crate::parser::{FrameState, FrameContext};
use crate::parser::DelimitedState;

impl crate::parser::Parser<'_> {
    /// Handle Delimited grammar Initial state in iterative parser
    /// Returns true if caller should continue main loop
    pub fn handle_delimited_initial(
        &mut self,
        elements: &[Grammar],
        delimiter: &Grammar,
        allow_trailing: bool,
        optional: bool,
        local_terminators: &[Grammar],
        reset_terminators: bool,
        allow_gaps: bool,
        min_delimiters: usize,
        parse_mode: ParseMode,
        frame: &mut ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut ParseFrameStack,
    ) -> Result<NextStep, ParseError> {
        let pos = frame.pos;
        log::debug!("[ITERATIVE] Delimited Initial state at pos {}", pos);

        // Combine terminators, filtering out delimiter from parent terminators
        // This is critical - delimiter shouldn't terminate the delimited list itself
        let filtered_parent: Vec<Grammar> = parent_terminators
            .iter()
            .filter(|t| *t != delimiter)
            .cloned()
            .collect();

        let all_terminators: Vec<Grammar> = if reset_terminators {
            local_terminators.to_vec()
        } else {
            local_terminators
                .iter()
                .cloned()
                .chain(filtered_parent)
                .collect()
        };

        // Calculate max_idx based on parse_mode and terminators
        self.pos = pos;
        let max_idx = if parse_mode == ParseMode::Greedy {
            // In GREEDY mode, actively look for terminators
            self.trim_to_terminator(pos, &all_terminators)
        } else {
            // In STRICT mode, still need to respect terminators if they exist
            // Check if there's a terminator anywhere ahead
            if all_terminators.is_empty() {
                self.tokens.len()
            } else {
                self.trim_to_terminator(pos, &all_terminators)
            }
        };

        // Apply parent's max_idx limit (simulates Python's segments[:max_idx])
        let max_idx = if let Some(parent_limit) = frame.parent_max_idx {
            max_idx.min(parent_limit)
        } else {
            max_idx
        };

        log::debug!(
            "[ITERATIVE] Delimited max_idx: {} (tokens.len: {}), parse_mode={:?}, terminators.len={}",
            max_idx,
            self.tokens.len(),
            parse_mode,
            all_terminators.len()
        );

        // Debug terminators for function-related Delimited
        if elements.iter().any(|e| {
            matches!(e, Grammar::Ref { name, .. } if name.contains("FunctionContents") || name.contains("DatetimeUnit"))
        }) {
            log::debug!("[DELIMITED-DEBUG] Active terminators (count={}):", all_terminators.len());
            for (i, term) in all_terminators.iter().enumerate() {
                match term {
                    Grammar::StringParser { template, .. } => {
                        log::debug!("  [{}] StringParser('{}')", i, template);
                    }
                    Grammar::Ref { name, .. } => {
                        log::debug!("  [{}] Ref({})", i, name);
                    }
                    _ => {
                        log::debug!("  [{}] {:?}", i, format!("{:?}", term).chars().take(80).collect::<String>());
                    }
                }
            }
        }

        // Check if optional and already terminated
        if optional && (self.is_at_end() || self.is_terminated(&all_terminators)) {
            log::debug!("[ITERATIVE] Delimited: empty optional");
            stack
                .results
                .insert(frame.frame_id, (Node::DelimitedList(vec![]), pos, None));
            return Ok(NextStep::Fallthrough); // Don't continue, we stored a result
        }

        // Create Delimited context
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: usize::MAX, // Unknown number of children
        };
        frame.context = FrameContext::Delimited {
            elements: elements.to_vec(),
            delimiter: Box::new(delimiter.clone()),
            allow_trailing,
            optional,
            allow_gaps,
            min_delimiters,
            parse_mode,
            delimiter_count: 0,
            matched_idx: pos,
            working_idx: pos,
            max_idx,
            state: DelimitedState::MatchingElement,
            last_child_frame_id: None,
        };
        frame.terminators = all_terminators.clone();

        // Extract max_idx before moving frame - this is the limit for children!
        // Children should be constrained by the Delimited's calculated max_idx
        let child_max_idx = max_idx;
        stack.push(frame);

        // Create first child to match element (try all elements via OneOf)
        let child_grammar = Grammar::OneOf {
            elements: elements.to_vec(),
            exclude: None,
            optional: true, // Elements in Delimited are implicitly optional
            terminators: vec![],
            reset_terminators: false,
            allow_gaps,
            parse_mode,
        };

        // Debug logging for specific grammars
        if elements.iter().any(|e| {
            matches!(e, Grammar::Ref { name, .. } if name.contains("FunctionContents") || name.contains("DatetimeUnit"))
        }) {
            log::debug!("[DELIMITED-DEBUG] Creating Delimited OneOf with {} elements at pos {}, max_idx={}", elements.len(), pos, child_max_idx);
            for (i, elem) in elements.iter().enumerate() {
                match elem {
                    Grammar::Ref { name, optional, .. } => {
                        log::debug!("  [{}] Ref({}) optional={}", i, name, optional);
                    }
                    _ => {
                        log::debug!("  [{}] {:?}", i, elem);
                    }
                }
            }
        }

        let mut child_frame = ParseFrame::new_child(
            stack.frame_id_counter,
            child_grammar,
            pos,
            all_terminators,
            Some(child_max_idx), // Use Delimited's max_idx!
        );

        // Update parent's last_child_frame_id and push child
        ParseFrame::update_parent_last_child_id(stack, "Delimited", stack.frame_id_counter);
        stack.increment_frame_id_counter();
        stack.push(&mut child_frame);
        Ok(NextStep::Continue) // Continue to process the child frame we just pushed
    }
}
