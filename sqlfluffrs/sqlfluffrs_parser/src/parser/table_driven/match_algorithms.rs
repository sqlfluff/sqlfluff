use sqlfluffrs_types::{GrammarId, GrammarVariant, Token};

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

    let result = parser.parse_table_iterative_match_result(grammar_id, terminators);

    // Capture end_pos
    let end_pos = parser.pos;
    vdebug!(
        "[TRY_MATCH_TABLE] try_match_grammar_table_driven: grammar_id={:?}, pos={} -> end_pos={}, result={:?}",
        grammar_id, pos, end_pos, result
    );

    // Restore position regardless of match success
    parser.pos = saved_pos;

    match result {
        Ok(mr) => {
            if end_pos > pos && !mr.is_empty() {
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

    /// Returns true if position `i` in the token stream is preceded (looking
    /// backwards past meta/transparent tokens) by a whitespace or newline token.
    ///
    /// PYTHON PARITY: In `greedy_match()`, Python checks `matcher.simple()` and
    /// if all returned strings are alphabetical with no token-type matches,
    /// requires that the matched segment is preceded by whitespace:
    ///
    /// ```python
    /// if all(_s.isalpha() for _s in _strings) and not _types:
    ///     # work backward looking for whitespace
    /// ```
    ///
    /// Edge case: if the terminator is at the very start of the search range
    /// (`_start_idx == working_idx`), Python allows it without whitespace.
    pub(crate) fn is_preceded_by_whitespace(
        &self,
        tokens: &[Token],
        i: usize,
        start_idx: usize,
    ) -> bool {
        if i == 0 || i <= start_idx {
            // At the very start — Python allows these (working_idx == start_idx case)
            return true;
        }
        let mut idx = i;
        while idx > start_idx {
            idx -= 1;
            let tok = &tokens[idx];
            if tok.is_meta {
                continue;
            }
            // Found a concrete token before position i
            return tok.is_whitespace()
                || tok.get_type() == "newline"
                || tok.get_type() == "whitespace";
        }
        // Went all the way back to start_idx — allow it (first element)
        true
    }

    pub(crate) fn greedy_match_table_driven(
        &mut self,
        start_idx: usize,
        terminators: &[GrammarId],
        max_idx: usize,
    ) -> Result<(usize, usize), ParseError> {
        let tokens = self.tokens;
        let tokens_len = tokens.len();

        if start_idx >= tokens_len {
            return Ok((tokens_len, tokens_len));
        }

        // If a terminator matches immediately (at start_idx), return as-is.
        // Python allows keyword terminators at the very start ("first element" edge case).
        for &term_id in terminators {
            vdebug!(
                "[GREEDY_MATCH_TABLE] greedy_match_table_driven: checking immediate terminator match for {:?} at {}",
                term_id, start_idx
            );
            if let Ok(end_pos) =
                self.try_match_grammar_table_driven(term_id, start_idx, terminators)
            {
                if end_pos > start_idx {
                    vdebug!(
                        "[GREEDY_MATCH_TABLE] greedy_match_table_driven: immediate terminator {:?} matched at {}",
                        term_id, start_idx
                    );
                    return Ok((start_idx, start_idx));
                }
            }
        }

        // Scan forward, looking for a terminator match.
        // CRITICAL: Skip over brackets to avoid finding terminators inside them.
        let max_idx = std::cmp::min(max_idx, tokens_len);
        let mut i = start_idx;
        while i < max_idx {
            let token = &tokens[i];
            let raw = token.raw();
            if raw == "(" || raw == "[" || raw == "{" {
                if let Some(matching_idx) = token.matching_bracket_idx {
                    vdebug!(
                        "[GREEDY_MATCH_TABLE] greedy_match_table_driven: skipping bracket at {} to {}",
                        i,
                        matching_idx + 1
                    );
                    i = matching_idx + 1;
                    continue;
                } else {
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

            for &term_id in terminators {
                vdebug!(
                    "[GREEDY_MATCH_TABLE] greedy_match_table_driven: checking terminator {:?} at {}",
                    term_id,
                    i
                );
                if let Ok(end_pos) = self.try_match_grammar_table_driven(term_id, i, terminators) {
                    if end_pos > i {
                        // If the matched terminator is a simple all-alphabetic token and the
                        // token is not preceded by whitespace, reject it. This prevents
                        // accidental matches of bare word tokens (e.g. identifiers) by
                        // string-based terminators when the string matcher does not enforce
                        // token-type constraints. Terminators implemented as TypedParser
                        // (which match by token type rather than raw text) are exempt.
                        let tok_is_alpha = tokens[i].is_code()
                            && !tokens[i].raw().is_empty()
                            && tokens[i].raw().chars().all(|c| c.is_ascii_alphabetic());
                        if tok_is_alpha && !self.is_preceded_by_whitespace(tokens, i, start_idx) {
                            let tables = self.grammar_ctx.tables();
                            let variant = tables.get_inst(term_id).variant;
                            if variant != GrammarVariant::TypedParser {
                                vdebug!(
                                    "[GREEDY_MATCH_TABLE] greedy_match_table_driven: skipping {:?} at {} — all-alpha token not preceded by whitespace",
                                    term_id, i
                                );
                                continue;
                            }
                        }
                        vdebug!(
                            "[GREEDY_MATCH_TABLE] greedy_match_table_driven: terminator {:?} matched at {}",
                            term_id, i
                        );
                        let last_code_idx = skip_stop_index_backward_to_code(tokens, i, start_idx);
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
}
