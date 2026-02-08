use sqlfluffrs_types::{GrammarId, Token};

use crate::parser::{ParseError, Parser};

use crate::vdebug;
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
///   `FnMut(GrammarId, usize, &[GrammarId]) -> Result<usize, ParseError>`
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

    let result = parser.parse_table_iterative(grammar_id, terminators);

    // Capture end_pos
    let end_pos = parser.pos;
    log::info!(
        "[TRY_MATCH_TABLE] try_match_grammar_table_driven: grammar_id={:?}, pos={} -> end_pos={}, result={:?}",
        grammar_id, pos, end_pos, result
    );

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

pub(crate) fn skip_stop_index_backward_to_code(
    tokens: &[Token],
    start_idx: usize,
    min_idx: usize,
) -> usize {
    let mut idx = start_idx;
    while idx > min_idx {
        idx -= 1;
        // Here we would check if the token at idx is a "code" token.
        // For this example, let's assume all tokens are code tokens.
        let is_code_token = tokens[idx].is_code();
        if is_code_token {
            return idx;
        }
    }
    min_idx
}

pub(crate) fn greedy_match_table_driven<F>(
    tokens: &[Token],
    start_idx: usize,
    terminators: &[GrammarId],
    max_idx: usize,
    try_match: &mut F,
) -> Result<(usize, usize), ParseError>
where
    F: FnMut(GrammarId, usize, &[GrammarId]) -> Result<usize, ParseError>,
{
    let tokens_len = tokens.len();
    // If no tokens left, return tokens_len
    if start_idx >= tokens_len {
        return Ok((tokens_len, tokens_len));
    }

    // If a terminator matches immediately, return start_idx and its end_pos
    for term_id in terminators {
        vdebug!(
            "[GREEDY_MATCH_TABLE] greedy_match_table_driven: checking immediate terminator match for {:?} at {}",
            term_id, start_idx
        );
        if let Ok(end_pos) = try_match(*term_id, start_idx, terminators) {
            if end_pos > start_idx {
                vdebug!(
                    "[GREEDY_MATCH_TABLE] greedy_match_table_driven: immediate terminator {:?} matched at {}",
                    term_id, start_idx
                );
                return Ok((start_idx, start_idx));
            }
        }
    }

    // Otherwise, scan forward until a terminator matches or we reach max_idx
    // CRITICAL: Skip over brackets to avoid finding terminators inside them
    let max_idx = std::cmp::min(max_idx, tokens_len);
    let mut i = start_idx;
    while i < max_idx {
        // Check if current token is an opening bracket - if so, skip to matching close
        let token = &tokens[i];
        let raw = token.raw();
        if raw == "(" || raw == "[" || raw == "{" {
            // Check if we have a pre-computed matching bracket index
            if let Some(matching_idx) = token.matching_bracket_idx {
                vdebug!(
                    "[GREEDY_MATCH_TABLE] greedy_match_table_driven: skipping bracket at {} to {}",
                    i,
                    matching_idx + 1
                );
                // Skip past the closing bracket
                i = matching_idx + 1;
                continue;
            } else {
                // PYTHON PARITY: No matching closing bracket found - raise parse error
                // This matches Python's resolve_bracket() behavior which raises
                // SQLParseError("Couldn't find closing bracket for opening bracket.")
                vdebug!(
                    "[GREEDY_MATCH_TABLE] greedy_match_table_driven: no matching closing bracket for opening bracket at {}",
                    i
                );
                return Err(ParseError::with_context(
                    "Couldn't find closing bracket for opening bracket.".to_string(),
                    Some(i),
                    None,
                ));
            }
        }

        // Check terminators at this position
        for &term_id in terminators {
            vdebug!(
                "[GREEDY_MATCH_TABLE] greedy_match_table_driven: checking terminator {:?} at {}",
                term_id,
                i
            );
            if let Ok(end_pos) = try_match(term_id, i, terminators) {
                if end_pos > i {
                    vdebug!(
                        "[GREEDY_MATCH_TABLE] greedy_match_table_driven: terminator {:?} matched at {}",
                        term_id, i
                    );
                    let last_code_idx = skip_stop_index_backward_to_code(tokens, i, start_idx);
                    // Return last_code_idx + 1 because max_idx is used as an EXCLUSIVE bound
                    // We want to include the token at last_code_idx in the match range
                    return Ok((i, last_code_idx + 1));
                }
            }
        }
        i += 1;
    }
    vdebug!(
        "[GREEDY_MATCH_TABLE] greedy_match_table_driven: returning max_idx={}",
        max_idx
    );
    Ok((start_idx, max_idx))
}

impl Parser<'_> {
    pub(crate) fn try_match_grammar_table_driven(
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
    ) -> Result<(usize, usize), ParseError> {
        let tokens = self.tokens;
        let mut try_match = |g: GrammarId, pos: usize, terms: &[GrammarId]| {
            self.try_match_grammar_table_driven(g, pos, terms)
        };
        greedy_match_table_driven(tokens, start_idx, terminators, max_idx, &mut try_match)
    }
}
