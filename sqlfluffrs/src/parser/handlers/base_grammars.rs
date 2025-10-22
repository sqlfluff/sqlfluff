use hashbrown::HashMap;
use crate::parser::Parser;
use crate::parser::{Node, ParseError, ParseFrame};
use crate::parser::iterative::NextStep;
use crate::parser::Grammar;

impl Parser<'_> {
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
                anything_tokens.push(Node::Token(
                    "anything".to_string(),
                    tok.raw().to_string(),
                    self.pos,
                ));
                self.bump();
            }
        }

        log::debug!("Anything matched tokens: {:?}", anything_tokens);
        results.insert(
            frame.frame_id,
            (Node::DelimitedList(anything_tokens), self.pos, None),
        );
        Ok(NextStep::Fallthrough)
    }
}
