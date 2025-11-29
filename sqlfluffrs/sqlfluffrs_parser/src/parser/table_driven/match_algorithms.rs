use sqlfluffrs_types::{GrammarContext, GrammarId};

use crate::parser::{ParseError, Parser};

/// Module-level implementations of the table-driven match algorithms.
///
/// These functions implement the matching helpers used by the table-driven
/// parser but take explicit parameters instead of borrowing the `Parser`.
/// The goals are:
/// - decouple matching logic from `&mut Parser` so it can be reused and
///   unit-tested more easily;
/// - keep thin `Parser` wrapper methods for backward compatibility.
///
/// Common calling conventions:
/// - `tokens_len`: the length of the token stream (usually `self.tokens.len()`).
/// - `start_idx` / `pos`: starting index in the token stream for a tentative
///   match attempt.
/// - `max_idx`: the maximum index to search up to (exclusive). Implementations
///   should clamp this against `tokens_len` before scanning.
/// - `grammar_ctx`: an `Option<&GrammarContext>`; when `None`, the function
///   should take the fast-path early-return behaviour (no table-driven matching
///   possible).
/// - `try_match`: a mutable closure of the shape
///     `FnMut(GrammarId, usize, &[GrammarId]) -> Result<usize, ParseError>`
///   which attempts to match the given grammar at the given position and
///   returns the end index on success. The closure is expected to perform any
///   necessary parser delegation (for example, calling the iterative engine).
fn try_match_grammar_table_driven(
    parser: &mut Parser<'_>,
    grammar_id: GrammarId,
    pos: usize,
    terminators: &[GrammarId],
) -> Result<usize, ParseError> {
    // Save current state
    let saved_pos = parser.pos;

    // Set position for tentative parse
    parser.pos = pos;

    let result = parser.parse_table_driven_iterative(grammar_id, terminators);

    // Capture end_pos
    let end_pos = parser.pos;

    // Restore position regardless of match success
    parser.pos = saved_pos;

    match result {
        Ok(node) => {
            if end_pos > pos && !node.is_empty() {
                Ok(end_pos)
            } else {
                Err(ParseError::with_context(
                    "trying but only an empty match found".to_string(),
                    Some(parser.pos),
                    None,
                ))
            }
        }
        Err(e) => Err(e),
    }
}

pub(crate) fn greedy_match_table_driven<F>(
    tokens_len: usize,
    start_idx: usize,
    terminators: &[GrammarId],
    max_idx: usize,
    grammar_ctx: Option<&GrammarContext>,
    try_match: &mut F,
) -> usize
where
    F: FnMut(GrammarId, usize, &[GrammarId]) -> Result<usize, ParseError>,
{
    // If no tokens left, return tokens_len
    if start_idx >= tokens_len {
        return tokens_len;
    }

    // If no grammar context, just return start_idx
    if grammar_ctx.is_none() {
        return start_idx;
    }

    // If a terminator matches immediately, return start_idx
    for term_id in terminators {
        if let Ok(end_pos) = try_match(*term_id, start_idx, terminators) {
            if end_pos > start_idx {
                return start_idx;
            }
        }
    }

    // Otherwise, scan forward until a terminator matches or we reach max_idx
    let mut idx = start_idx;
    let max_idx = std::cmp::min(max_idx, tokens_len);
    idx = (idx..max_idx)
        .find(|&i| {
            terminators.iter().any(|&term_id| {
                if let Ok(end_pos) = try_match(term_id, i, terminators) {
                    end_pos > i
                } else {
                    false
                }
            })
        })
        .unwrap_or(max_idx);
    idx
}

pub(crate) fn next_ex_bracket_match_table_driven<F>(
    tokens_len: usize,
    start_idx: usize,
    matchers: &[GrammarId],
    bracket_pairs: &[(GrammarId, GrammarId, bool)], // (start, end, persists)
    max_idx: usize,
    grammar_ctx: Option<&GrammarContext>,
    try_match: &mut F,
) -> (usize, Option<GrammarId>, Vec<(usize, usize)>)
where
    F: FnMut(GrammarId, usize, &[GrammarId]) -> Result<usize, ParseError>,
{
    let mut idx = start_idx;
    if grammar_ctx.is_none() {
        return (idx, None, Vec::new());
    }
    let mut bracket_stack: Vec<(GrammarId, usize)> = Vec::new();
    let mut bracket_matches: Vec<(usize, usize)> = Vec::new();
    let mut matched_terminator: Option<GrammarId> = None;
    let max_idx = std::cmp::min(max_idx, tokens_len);
    while idx < max_idx {
        // Check for bracket open/close
        let mut bracket_found = false;
        for (start_id, end_id, persists) in bracket_pairs {
            if let Ok(end_pos) = try_match(*start_id, idx, matchers) {
                if end_pos > idx {
                    bracket_stack.push((*start_id, idx));
                    bracket_found = true;
                    break;
                }
            }

            if let Ok(end_pos) = try_match(*end_id, idx, matchers) {
                if end_pos > idx {
                    if let Some((_open_id, open_idx)) = bracket_stack.pop() {
                        bracket_matches.push((open_idx, idx));
                        bracket_found = true;
                        if !persists {
                            break;
                        }
                    }
                }
            }
        }
        if bracket_found {
            idx += 1;
            continue;
        }
        // Check for matchers (terminators)
        for matcher_id in matchers {
            if let Ok(end_pos) = try_match(*matcher_id, idx, matchers) {
                if end_pos > idx {
                    matched_terminator = Some(*matcher_id);
                    return (idx, matched_terminator, bracket_matches);
                }
            }
        }
        idx += 1;
    }
    (idx, matched_terminator, bracket_matches)
}

pub(crate) fn next_match_table_driven<F>(
    tokens_len: usize,
    start_idx: usize,
    matchers: &[GrammarId],
    max_idx: usize,
    grammar_ctx: Option<&GrammarContext>,
    try_match: &mut F,
) -> (usize, Option<GrammarId>)
where
    F: FnMut(GrammarId, usize, &[GrammarId]) -> Result<usize, ParseError>,
{
    // Quick bounds
    let max_idx = std::cmp::min(max_idx, tokens_len);
    if start_idx >= max_idx {
        return (start_idx, None);
    }

    if grammar_ctx.is_none() {
        return (start_idx, None);
    }

    // Use iterator combinators for more concise matching.
    if let Some((end_pos, matched_id)) = (start_idx..max_idx).find_map(|idx| {
        matchers.iter().find_map(|&m_id| {
            if let Ok(end_pos) = try_match(m_id, idx, &[]) {
                if end_pos > idx {
                    Some((end_pos, m_id))
                } else {
                    None
                }
            } else {
                None
            }
        })
    }) {
        return (end_pos, Some(matched_id));
    }

    (start_idx, None)
}

impl<'a> Parser<'_> {
    fn try_match_grammar_table_driven(
        &mut self,
        grammar_id: GrammarId,
        pos: usize,
        terminators: &[GrammarId],
    ) -> Result<usize, ParseError> {
        // Delegate to module-level implementation
        try_match_grammar_table_driven(self, grammar_id, pos, terminators)
    }

    pub(crate) fn greedy_match_table_driven(
        &mut self,
        start_idx: usize,
        terminators: &[GrammarId],
        max_idx: usize,
    ) -> usize {
        let tokens_len = self.tokens.len();
        let grammar_ctx = self.grammar_ctx; // copy the Option reference before borrowing self mutably
        let mut try_match = |g: GrammarId, pos: usize, terms: &[GrammarId]| {
            self.try_match_grammar_table_driven(g, pos, terms)
        };
        greedy_match_table_driven(
            tokens_len,
            start_idx,
            terminators,
            max_idx,
            grammar_ctx,
            &mut try_match,
        )
    }

    pub(crate) fn next_ex_bracket_match_table_driven(
        &mut self,
        start_idx: usize,
        matchers: &[GrammarId],
        bracket_pairs: &[(GrammarId, GrammarId, bool)],
        max_idx: usize,
    ) -> (usize, Option<GrammarId>, Vec<(usize, usize)>) {
        let tokens_len = self.tokens.len();
        let grammar_ctx = self.grammar_ctx; // copy option before closure
        let mut try_match = |g: GrammarId, pos: usize, terms: &[GrammarId]| {
            self.try_match_grammar_table_driven(g, pos, terms)
        };
        next_ex_bracket_match_table_driven(
            tokens_len,
            start_idx,
            matchers,
            bracket_pairs,
            max_idx,
            grammar_ctx,
            &mut try_match,
        )
    }

    pub(crate) fn next_match_table_driven(
        &mut self,
        start_idx: usize,
        matchers: &[GrammarId],
        max_idx: usize,
    ) -> (usize, Option<GrammarId>) {
        let tokens_len = self.tokens.len();
        let grammar_ctx = self.grammar_ctx; // copy option before closure
        let mut try_match = |g: GrammarId, pos: usize, terms: &[GrammarId]| {
            self.try_match_grammar_table_driven(g, pos, terms)
        };
        next_match_table_driven(
            tokens_len,
            start_idx,
            matchers,
            max_idx,
            grammar_ctx,
            &mut try_match,
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use sqlfluffrs_dialects::Dialect;
    use sqlfluffrs_lexer::{LexInput, Lexer};

    #[test]
    fn test_next_match_table_driven_no_grammar_context_returns_none() {
        // Build a small token stream using the lexer so we don't have to
        // construct Token objects manually.
        let sql = "";
        let input = LexInput::String(sql.to_string());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, Dialect::get_lexers(&dialect).clone());
        let (tokens, _errors) = lexer.lex(input, false);

        // Create a Parser without table-driven grammar context.
        let mut parser = Parser::new(&tokens, dialect);

        // With no GrammarContext, the function should return the start idx
        // and no matched GrammarId.
        let (end, gid) = parser.next_match_table_driven(0, &[], tokens.len());
        assert_eq!(end, 0);
        assert!(gid.is_none());
    }
}
