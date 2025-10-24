use crate::parser::Grammar;
use crate::parser::iterative::NextStep;
use crate::parser::{Node, ParseError, ParseFrame};
use hashbrown::HashMap;

use crate::parser::core::Parser;

impl Parser<'_> {
    /// Handle StringParser grammar in iterative parser
    pub fn handle_string_parser_initial(
        &mut self,
        grammar: &Grammar,
        frame: &ParseFrame,
        iteration_count: usize,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
        let (template, token_type) = match grammar {
            Grammar::StringParser { template, token_type, .. } => (template, token_type),
            _ => {
                return Err(ParseError::new("handle_string_parser_initial called with non-StringParser grammar".into()));
            }
        };
        self.pos = frame.pos;
        self.skip_transparent(true);
        let tok_raw = self.peek().cloned();

        match tok_raw {
            Some(tok) if tok.raw().eq_ignore_ascii_case(template) => {
                let token_pos = self.pos;
                self.bump();
                log::debug!("MATCHED String matched: {}", tok);

                let node = Node::Token {
                    token_type: token_type.to_string(),
                    raw: tok.raw(),
                    token_idx: token_pos,
                };
                results.insert(frame.frame_id, (node, self.pos, None));
            }
            _ => {
                log::debug!("String parser didn't match '{}', returning Empty", template);
                log::debug!(
                    "DEBUG [iter {}]: StringParser('{}') frame_id={} storing Empty result",
                    iteration_count,
                    template,
                    frame.frame_id
                );
                results.insert(frame.frame_id, (Node::Empty, self.pos, None));
            }
        }
        Ok(NextStep::Fallthrough)
    }

    /// Handle MultiStringParser grammar in iterative parser
    pub fn handle_multi_string_parser_initial(
        &mut self,
        grammar: &Grammar,
        frame: &ParseFrame,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
        let (templates, token_type) = match grammar {
            Grammar::MultiStringParser { templates, token_type, .. } => (templates, token_type),
            _ => {
                return Err(ParseError::new("handle_multi_string_parser_initial called with non-MultiStringParser grammar".into()));
            }
        };
        self.pos = frame.pos;
        self.skip_transparent(true);
        let token = self.peek().cloned();

        match token {
            Some(tok)
                if templates
                    .iter()
                    .any(|&temp| tok.raw().eq_ignore_ascii_case(temp)) =>
            {
                let token_pos = self.pos;
                self.bump();
                log::debug!("MATCHED MultiString matched: {}", tok);

                let node = Node::Token {
                    token_type: token_type.to_string(),
                    raw: tok.raw(),
                    token_idx: token_pos,
                };
                results.insert(frame.frame_id, (node, self.pos, None));
            }
            _ => {
                log::debug!("MultiString parser didn't match, returning Empty");
                results.insert(frame.frame_id, (Node::Empty, self.pos, None));
            }
        }
        Ok(NextStep::Fallthrough)
    }

    /// Handle TypedParser grammar in iterative parser
    pub fn handle_typed_parser_initial(
        &mut self,
        grammar: &Grammar,
        frame: &ParseFrame,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
        let (template, token_type) = match grammar {
            Grammar::TypedParser { template, token_type, .. } => (template, token_type),
            _ => {
                return Err(ParseError::new("handle_typed_parser_initial called with non-TypedParser grammar".into()));
            }
        };
        log::debug!(
            "DEBUG: TypedParser frame_id={}, pos={}, parent_max_idx={:?}, template={:?}",
            frame.frame_id,
            frame.pos,
            frame.parent_max_idx,
            template
        );

        self.pos = frame.pos;
        self.skip_transparent(true);

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
                    "DEBUG: TypedParser MATCHED! frame_id={}, consumed token at pos={}",
                    frame.frame_id,
                    token_pos
                );
                log::debug!("MATCHED Typed matched: {}", tok.token_type);
                let node = Node::Token {
                    token_type: token_type.to_string(),
                    raw,
                    token_idx: token_pos,
                };
                results.insert(frame.frame_id, (node, self.pos, None));
            } else {
                log::debug!(
                    "DEBUG: TypedParser FAILED to match! frame_id={}, expected='{}', found='{}'",
                    frame.frame_id,
                    template,
                    tok.token_type
                );
                log::debug!(
                    "Typed parser failed: expected '{}', found '{}'",
                    template,
                    tok.token_type
                );
                results.insert(frame.frame_id, (Node::Empty, frame.pos, None));
            }
        } else {
            log::debug!(
                "DEBUG: TypedParser at EOF! frame_id={}, pos={}",
                frame.frame_id,
                frame.pos
            );
            log::debug!("Typed parser at EOF");
            results.insert(frame.frame_id, (Node::Empty, frame.pos, None));
        }
        Ok(NextStep::Fallthrough)
    }

    /// Handle RegexParser grammar in iterative parser
    /// Returns true if the caller should continue to the next frame (anti-template matched)
    pub fn handle_regex_parser_initial(
        &mut self,
        grammar: &Grammar,
        frame: &ParseFrame,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
        let (template, anti_template, token_type) = match grammar {
            Grammar::RegexParser { template, anti_template, token_type, .. } => (template, anti_template, token_type),
            _ => {
                return Err(ParseError::new("handle_regex_parser_initial called with non-RegexParser grammar".into()));
            }
        };
        self.pos = frame.pos;
        self.skip_transparent(true);
        let token = self.peek().cloned();

        match token {
            Some(tok) if template.is_match(&tok.raw()) => {
                log::debug!("Regex matched: {}", tok);

                // Check anti-template if present
                if let Some(anti) = anti_template {
                    if anti.is_match(&tok.raw()) {
                        log::debug!("Regex anti-matched: {}", tok);
                        log::debug!("RegexParser anti-match, returning Empty");
                        results.insert(frame.frame_id, (Node::Empty, self.pos, None));
                        return Ok(NextStep::Continue); // Signal caller to continue to next frame
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
                results.insert(frame.frame_id, (node, self.pos, None));
                Ok(NextStep::Fallthrough)
            }
            _ => {
                log::debug!("RegexParser didn't match '{}', returning Empty", template);
                results.insert(frame.frame_id, (Node::Empty, self.pos, None));
                Ok(NextStep::Fallthrough)
            }
        }
    }
}
