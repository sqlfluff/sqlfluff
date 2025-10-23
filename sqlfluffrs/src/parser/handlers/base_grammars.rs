use crate::parser::iterative::NextStep;
use crate::parser::iterative::ParseFrameStack;
use crate::parser::FrameContext;
use crate::parser::FrameState;
use crate::parser::Grammar;
use crate::parser::Parser;
use crate::parser::{Node, ParseError, ParseFrame};
use hashbrown::HashMap;

impl Parser<'_> {
    /// Handle Empty grammar in iterative parser
    pub fn handle_empty_initial(
        &mut self,
        frame: &ParseFrame,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
        results.insert(frame.frame_id, (Node::Empty, frame.pos, None));
        Ok(NextStep::Fallthrough)
    }

    /// Handle Missing grammar in iterative parser
    pub fn handle_missing_initial(&mut self) -> Result<NextStep, ParseError> {
        log::debug!("Trying missing grammar");
        Err(ParseError::new("Encountered Missing grammar".into()))
    }

    /// Handle Meta grammar in iterative parser
    pub(crate) fn handle_meta_initial(
        &mut self,
        token_type: &'static str,
        frame: &ParseFrame,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
        log::debug!("Doing nothing with meta {}", token_type);
        results.insert(frame.frame_id, (Node::Meta { token_type, token_idx: None }, frame.pos, None));
        Ok(NextStep::Fallthrough)
    }

    /// Handle Anything grammar in iterative parser
    pub fn handle_anything_initial(
        &mut self,
        frame: &ParseFrame,
        parent_terminators: &[Grammar],
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
        self.pos = frame.pos;
        let mut anything_tokens = vec![];

        loop {
            if self.is_terminated(parent_terminators) || self.is_at_end() {
                break;
            }
            if let Some(tok) = self.peek() {
                anything_tokens.push(Node::Token { token_type: "anything".to_string(), raw: tok.raw().to_string(), token_idx: self.pos });
                self.bump();
            }
        }

        log::debug!("Anything matched tokens: {:?}", anything_tokens);
        results.insert(
            frame.frame_id,
            (Node::DelimitedList { children: anything_tokens }, self.pos, None),
        );
        Ok(NextStep::Fallthrough)
    }

    /// Handle Nothing grammar in iterative parser
    pub fn handle_nothing_initial(
        &mut self,
        frame: &ParseFrame,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
        log::debug!("Nothing grammar encountered, returning Empty");
        results.insert(frame.frame_id, (Node::Empty, frame.pos, None));
        Ok(NextStep::Fallthrough)
    }

    /// Handle Ref grammar Initial state in iterative parser
    pub(crate) fn handle_ref_initial(
        &mut self,
        name: &str,
        optional: bool,
        allow_gaps: bool,
        ref_terminators: &[Grammar],
        reset_terminators: bool,
        frame: &mut ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut ParseFrameStack,
        iteration_count: usize,
    ) -> Result<NextStep, ParseError> {
        log::debug!(
            "Iterative Ref to segment: {}, optional: {}, allow_gaps: {}",
            name,
            optional,
            allow_gaps
        );
        let saved = frame.pos;
        self.pos = frame.pos;
        self.skip_transparent(allow_gaps);

        // Combine parent and local terminators
        let all_terminators: Vec<Grammar> = if reset_terminators {
            ref_terminators.to_vec()
        } else {
            ref_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        // Look up the grammar for this segment
        let grammar_opt = self.get_segment_grammar(name);

        match grammar_opt {
            Some(child_grammar) => {
                // Get segment type for later wrapping
                let segment_type = self.dialect.get_segment_type(name).map(|s| s.to_string());

                // Create child frame to parse the target grammar
                let child_frame_id = stack.frame_id_counter;
                stack.increment_frame_id_counter();

                let mut child_frame = ParseFrame {
                    frame_id: child_frame_id,
                    grammar: child_grammar.clone(),
                    pos: self.pos,
                    terminators: all_terminators,
                    state: FrameState::Initial,
                    accumulated: vec![],
                    context: FrameContext::None,
                    parent_max_idx: frame.parent_max_idx, // CRITICAL: Propagate parent's limit
                };

                // Update current frame to wait for child and store Ref metadata
                frame.state = FrameState::WaitingForChild {
                    child_index: 0,
                    total_children: 1,
                };
                frame.context = FrameContext::Ref {
                    name: name.to_string(),
                    optional,
                    allow_gaps,
                    segment_type,
                    saved_pos: saved,
                    last_child_frame_id: Some(child_frame_id), // Track the child we just created
                };

                // Push parent back first, then child (LIFO - child will be processed next)
                stack.push(frame);

                log::debug!("DEBUG [iter {}]: Ref({}) frame_id={} creating child frame_id={}, child grammar type: {}",
                    iteration_count,
                    name,
                    stack.last_mut().unwrap().frame_id,
                    child_frame_id,
                    match &child_grammar {
                        Grammar::Ref { name, .. } => format!("Ref({})", name),
                        Grammar::Token { token_type } => format!("Token({})", token_type),
                        Grammar::Sequence { elements, .. } => format!("Sequence({} elements)", elements.len()),
                        Grammar::OneOf { elements, .. } => format!("OneOf({} elements)", elements.len()),
                        _ => format!("{:?}", child_grammar),
                    }
                );

                stack.push(&mut child_frame);
                log::debug!("DEBUG [iter {}]: ABOUT TO CONTINUE - Ref({}) pushed child {}, stack size now {}",
                    iteration_count, name, child_frame_id, stack.len());
                log::debug!(
                    "DEBUG [iter {}]: ==> CONTINUING 'MAIN_LOOP NOW! <==",
                    iteration_count
                );
                Ok(NextStep::Continue) // Signal caller to continue main loop
            }
            None => {
                self.pos = saved;
                if optional {
                    log::debug!("Iterative Ref optional (grammar not found), skipping");
                    stack
                        .results
                        .insert(frame.frame_id, (Node::Empty, saved, None));
                    Ok(NextStep::Fallthrough) // Don't continue, we stored a result
                } else {
                    log::debug!("Iterative Ref failed (grammar not found), returning error");
                    Err(ParseError::unknown_segment(name.to_string()))
                }
            }
        }
    }
}
