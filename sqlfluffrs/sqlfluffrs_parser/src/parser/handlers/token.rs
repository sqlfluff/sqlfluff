use std::sync::Arc;

use crate::parser::{FrameState, Node, ParseError, ParseFrame};
use hashbrown::HashMap;
use sqlfluffrs_types::Grammar;

use crate::parser::core::Parser;

impl<'a> Parser<'_> {
    /// Handle Token grammar in iterative parser
    pub(crate) fn handle_token_initial(
        &mut self,
        grammar: Arc<Grammar>,
        mut frame: ParseFrame, // Take ownership instead of &
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        let token_type = match grammar.as_ref() {
            Grammar::Token { token_type } => token_type,
            _ => {
                return Err(ParseError::new(
                    "handle_token_initial called with non-Token grammar".into(),
                ));
            }
        };
        log::debug!("DEBUG: Token grammar frame_id={}, pos={}, parent_max_idx={:?}, token_type={:?}, available_tokens={}",
            frame.frame_id, frame.pos, frame.parent_max_idx, token_type, self.tokens.len());

        // Python parity: In Python, segments are sliced to max_idx before matching.
        // segments[:max_idx] means positions 0..max_idx-1 are accessible, position max_idx is NOT.
        // So if pos >= parent_max_idx, we're beyond the slice boundary.
        // Return Empty node rather than Err so parent (e.g. OneOf) can try other options.
        if let Some(parent_max) = frame.parent_max_idx {
            if frame.pos >= parent_max {
                log::debug!(
                    "Token: pos {} >= parent_max_idx {}, returning Empty",
                    frame.pos,
                    parent_max
                );
                results.insert(frame.frame_id, (Node::Empty, frame.pos, None));
                return Ok(crate::parser::iterative::FrameResult::Done);
            }
        }

        self.pos = frame.pos;
        log::debug!("Trying token grammar, {}", token_type);

        if let Some(token) = self.peek() {
            let tok = token.clone();
            log::debug!("Current token: {:?}", tok.get_type());

            if tok.get_type().as_str() == *token_type {
                let token_pos = self.pos;
                self.bump();
                log::debug!("MATCHED Token matched: {:?}", tok);
                log::debug!(
                    "DEBUG: Token grammar frame_id={} matched, result end_pos={}",
                    frame.frame_id,
                    self.pos
                );

                let node = Node::Token {
                    token_type: token_type.to_string(),
                    raw: tok.raw(),
                    token_idx: token_pos,
                };

                // Transition to Complete state instead of direct insertion
                frame.state = FrameState::Complete(node);
                frame.end_pos = Some(self.pos);
                log::debug!(
                    "🎯 Token handler set Complete state for frame {}",
                    frame.frame_id
                );
                Ok(crate::parser::iterative::FrameResult::Push(frame))
            } else {
                log::debug!(
                    "DEBUG: Token grammar frame_id={} failed with error",
                    frame.frame_id
                );
                Err(ParseError::new(format!(
                    "Expected token type {}, found {}",
                    token_type,
                    tok.get_type()
                )))
            }
        } else {
            log::debug!(
                "DEBUG: Token grammar frame_id={} failed - at EOF",
                frame.frame_id
            );
            Err(ParseError::new("Expected token, found EOF".into()))
        }
    }
}
