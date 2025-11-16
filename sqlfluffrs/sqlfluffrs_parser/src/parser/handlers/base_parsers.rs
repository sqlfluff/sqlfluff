use std::sync::Arc;

use crate::parser::{iterative::FrameResult, FrameState, Node, ParseError, ParseFrame};
use hashbrown::HashMap;
use sqlfluffrs_types::Grammar;

use crate::parser::core::Parser;

impl Parser<'_> {
    /// Handle StringParser grammar in iterative parser
    pub fn handle_string_parser_initial(
        &mut self,
        grammar: Arc<Grammar>,
        mut frame: ParseFrame, // Take ownership
        iteration_count: usize,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<FrameResult, ParseError> {
        log::debug!(
            "START StringParser: frame_id={}, pos={}, grammar={:?}",
            frame.frame_id,
            frame.pos,
            grammar
        );
        let (template, token_type) = match grammar.as_ref() {
            Grammar::StringParser {
                template,
                token_type,
                ..
            } => (template, token_type),
            _ => {
                return Err(ParseError::new(
                    "handle_string_parser_initial called with non-StringParser grammar".into(),
                ));
            }
        };
        self.pos = frame.pos;
        let tok_raw = self.peek().cloned();

        log::debug!(
            "START StringParser: frame_id={}, pos={}, template='{}', token_type='{}', peeked_token={:?}",
            frame.frame_id,
            self.pos,
            template,
            token_type,
            tok_raw.as_ref().map(|t| t.raw())
        );

        match tok_raw {
            Some(tok) if tok.raw().eq_ignore_ascii_case(template) => {
                let token_pos = self.pos;
                self.bump();
                log::debug!(
                    "MATCHED StringParser: frame_id={}, matched token: {}",
                    frame.frame_id,
                    tok.raw()
                );

                let node = Node::Token {
                    token_type: token_type.to_string(),
                    raw: tok.raw(),
                    token_idx: token_pos,
                };
                // Transition to Complete state
                frame.state = FrameState::Complete(node);
                frame.end_pos = Some(self.pos);
                log::debug!(
                    "🎯 StringParser set Complete state for frame {}",
                    frame.frame_id
                );
                Ok(FrameResult::Push(frame))
            }
            _ => {
                log::debug!(
                    "NOMATCH StringParser: frame_id={}, template='{}', peeked_token={:?}",
                    frame.frame_id,
                    template,
                    tok_raw.as_ref().map(|t| t.raw())
                );
                log::debug!(
                    "DEBUG [iter {}]: StringParser('{}') frame_id={} storing Empty result",
                    iteration_count,
                    template,
                    frame.frame_id
                );
                // Transition to Complete state with Empty
                frame.state = FrameState::Complete(Node::Empty);
                frame.end_pos = Some(self.pos);
                log::debug!(
                    "🎯 StringParser set Complete(Empty) for frame {}",
                    frame.frame_id
                );
                Ok(FrameResult::Push(frame))
            }
        }
    }

    /// Handle MultiStringParser grammar in iterative parser
    pub fn handle_multi_string_parser_initial(
        &mut self,
        grammar: Arc<Grammar>,
        mut frame: ParseFrame, // Take ownership
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<FrameResult, ParseError> {
        log::debug!(
            "START MultiStringParser: frame_id={}, pos={}, grammar={:?}",
            frame.frame_id,
            frame.pos,
            grammar
        );
        let (templates, token_type) = match grammar.as_ref() {
            Grammar::MultiStringParser {
                templates,
                token_type,
                ..
            } => (templates, token_type),
            _ => {
                return Err(ParseError::new(
                    "handle_multi_string_parser_initial called with non-MultiStringParser grammar"
                        .into(),
                ));
            }
        };
        self.pos = frame.pos;
        let token = self.peek().cloned();

        match token {
            Some(tok)
                if templates
                    .iter()
                    .any(|temp| tok.raw().eq_ignore_ascii_case(temp)) =>
            {
                let token_pos = self.pos;
                self.bump();
                log::debug!("MATCHED MultiString matched: {}", tok);

                let node = Node::Token {
                    token_type: token_type.to_string(),
                    raw: tok.raw(),
                    token_idx: token_pos,
                };
                frame.state = FrameState::Complete(node);
                frame.end_pos = Some(self.pos);
                Ok(FrameResult::Push(frame))
            }
            _ => {
                log::debug!("MultiString parser didn't match, returning Empty");
                frame.state = FrameState::Complete(Node::Empty);
                frame.end_pos = Some(self.pos);
                Ok(FrameResult::Push(frame))
            }
        }
    }

    /// Handle TypedParser grammar in iterative parser
    pub fn handle_typed_parser_initial(
        &mut self,
        grammar: Arc<Grammar>,
        mut frame: ParseFrame, // Take ownership
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<FrameResult, ParseError> {
        log::debug!(
            "START TypedParser: frame_id={}, pos={}, grammar={:?}",
            frame.frame_id,
            frame.pos,
            grammar
        );
        let (template, token_type) = match grammar.as_ref() {
            Grammar::TypedParser {
                template,
                token_type,
                ..
            } => (template, token_type),
            _ => {
                return Err(ParseError::new(
                    "handle_typed_parser_initial called with non-TypedParser grammar".into(),
                ));
            }
        };
        log::debug!(
            "START TypedParser: frame_id={}, pos={}, template='{}', token_type='{}', peeked_token={:?}",
            frame.frame_id,
            self.pos,
            template,
            token_type,
            self.peek().as_ref().map(|t| t.raw())
        );

        self.pos = frame.pos;

        if let Some(token) = self.peek() {
            let tok = token.clone();
            log::debug!(
                "DEBUG: TypedParser peeked token: type='{}', raw='{}', pos={}",
                tok.token_type,
                tok.raw(),
                self.pos
            );

            if tok.is_type(&[template]) {
                let raw = tok.raw().to_string();
                let token_pos = self.pos;
                self.bump();
                log::debug!(
                    "MATCHED TypedParser: frame_id={}, matched token: type={}, raw={}",
                    frame.frame_id,
                    tok.token_type,
                    raw
                );
                log::debug!(
                    "MATCHED Node::Token: type={}, raw={}, token_idx={}",
                    tok.token_type,
                    raw,
                    token_pos
                );
                let node = Node::Token {
                    token_type: token_type.to_string(),
                    raw,
                    token_idx: token_pos,
                };
                frame.state = FrameState::Complete(node);
                frame.end_pos = Some(self.pos);
                Ok(FrameResult::Push(frame))
            } else {
                log::debug!(
                    "NOMATCH TypedParser: frame_id={}, expected type '{}', found type '{}', raw '{}'",
                    frame.frame_id,
                    template,
                    tok.token_type,
                    tok.raw()
                );
                log::debug!(
                    "FAILED Node::Token: expected type '{}', found type '{}', raw '{}'",
                    template,
                    tok.token_type,
                    tok.raw()
                );
                frame.state = FrameState::Complete(Node::Empty);
                frame.end_pos = Some(frame.pos);
                Ok(FrameResult::Push(frame))
            }
        } else {
            log::debug!(
                "DEBUG: TypedParser at EOF! frame_id={}, pos={}",
                frame.frame_id,
                frame.pos
            );
            log::debug!("Typed parser at EOF");
            frame.state = FrameState::Complete(Node::Empty);
            frame.end_pos = Some(frame.pos);
            Ok(FrameResult::Push(frame))
        }
    }

    /// Handle RegexParser grammar in iterative parser
    /// Returns true if the caller should continue to the next frame (anti-template matched)
    pub fn handle_regex_parser_initial(
        &mut self,
        grammar: Arc<Grammar>,
        mut frame: ParseFrame, // Take ownership
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<FrameResult, ParseError> {
        log::debug!(
            "START RegexParser: frame_id={}, pos={}, grammar={:?}",
            frame.frame_id,
            frame.pos,
            grammar
        );
        let (template, anti_template, token_type) = match grammar.as_ref() {
            Grammar::RegexParser {
                template,
                anti_template,
                token_type,
                ..
            } => (template, anti_template, token_type),
            _ => {
                return Err(ParseError::new(
                    "handle_regex_parser_initial called with non-RegexParser grammar".into(),
                ));
            }
        };
        self.pos = frame.pos;
        let token = self.peek().cloned();

        match token {
            Some(tok) if template.is_match(&tok.raw()) => {
                log::debug!("Regex matched: {}", tok);

                // Check anti-template if present
                if let Some(anti) = anti_template {
                    if anti.is_match(&tok.raw()) {
                        log::debug!("Regex anti-matched: {}", tok);
                        log::debug!("RegexParser anti-match, returning Empty");
                        frame.state = FrameState::Complete(Node::Empty);
                        frame.end_pos = Some(self.pos);
                        return Ok(FrameResult::Push(frame));
                    }
                }

                log::debug!("MATCHED Regex matched and non anti-match: {}", tok);
                let token_pos = self.pos;
                self.bump();
                let node = Node::Token {
                    token_type: token_type.to_string(),
                    raw: tok.raw(),
                    token_idx: token_pos,
                };
                frame.state = FrameState::Complete(node);
                frame.end_pos = Some(self.pos);
                Ok(FrameResult::Push(frame))
            }
            _ => {
                log::debug!("RegexParser didn't match '{}', returning Empty", template);
                frame.state = FrameState::Complete(Node::Empty);
                frame.end_pos = Some(self.pos);
                Ok(FrameResult::Push(frame))
            }
        }
    }
}
