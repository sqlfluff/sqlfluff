use std::sync::Arc;

use crate::parser::Grammar;
use hashbrown::HashMap;
use crate::parser::{Node, ParseError, ParseFrame};
use crate::parser::iterative::NextStep;

use crate::parser::core::Parser;

impl<'a> Parser<'_> {
    /// Handle Token grammar in iterative parser
    pub(crate) fn handle_token_initial(
        &mut self,
        grammar: Arc<Grammar>,
        frame: &ParseFrame,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
        let token_type = match grammar.as_ref() {
            Grammar::Token { token_type } => token_type,
            _ => {
                return Err(ParseError::new("handle_token_initial called with non-Token grammar".into()));
            }
        };
        log::debug!("DEBUG: Token grammar frame_id={}, pos={}, parent_max_idx={:?}, token_type={:?}, available_tokens={}",
            frame.frame_id, frame.pos, frame.parent_max_idx, token_type, self.tokens.len());

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

                let node = Node::Token { token_type: token_type.to_string(), raw: tok.raw(), token_idx: token_pos };
                results.insert(frame.frame_id, (node, self.pos, None));
                Ok(NextStep::Fallthrough)
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
