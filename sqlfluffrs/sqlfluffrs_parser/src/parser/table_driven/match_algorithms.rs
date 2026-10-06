use sqlfluffrs_types::{BracketPairSet, GrammarId, GrammarVariant, Token};

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
///   `FnMut(GrammarId, usize, &[GrammarId]) -> Result<usize, ParseError>`
///   which attempts to match the given grammar at the given position and
///   returns the end index on success. The closure is expected to perform any
///   necessary parser delegation (for example, calling the iterative engine).
fn try_match_grammar(
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
        "[TRY_MATCH_TABLE] try_match_grammar: grammar_id={:?}, pos={} -> end_pos={}, result={:?}",
        grammar_id,
        pos,
        end_pos,
        result
    );

    // Restore position regardless of match success
    parser.pos = saved_pos;

    // An empty match reports `pos` (no progress).
    let mr = result?;
    Ok(if end_pos > pos && !mr.is_empty() {
        end_pos
    } else {
        pos
    })
}

/// The result of scanning forward for how an unresolved opening bracket at
/// `open_idx` is eventually accounted for.
enum BracketScanResult {
    /// A closer of the wrong type was found. `idx` is its position,
    /// `actual_close` its raw text, and `expected_open` the raw text of the
    /// innermost still-open bracket it should have closed instead.
    Mismatch {
        idx: usize,
        actual_close: String,
        expected_open: String,
    },
    /// Nothing closed it before `tokens.len()`. `idx` is the innermost
    /// still-open bracket at that point, i.e. the one Python's recursive
    /// `resolve_bracket` would have been sitting in when it hit EOF.
    Unclosed { idx: usize },
}

/// Scan forward from `from_idx` for the first bracket-like token not already
/// resolved by lexing (i.e. one whose `matching_bracket_idx` is `None`),
/// skipping over any properly nested, already-resolved bracket pairs along
/// the way (same technique as `greedy_match`'s own bracket-skip).
///
/// `open_idx` is the position of the opener already known to be unresolved
/// (normally `from_idx - 1`). It, and the bracket type it opens with, track
/// the innermost bracket currently "active", updating to each further
/// unresolved opener found along the way, matching Python's
/// `resolve_bracket` recursing one level deeper for every bracket it opens
/// - so the position they end up at is always where Python's own
///   recursive call would raise from.
///
/// Used to distinguish Python's two distinct bracket-resolution failures
/// (`resolve_bracket`, match_algorithms.py): "Couldn't find closing bracket
/// for opening bracket" (genuinely unclosed) vs. "Found unexpected end
/// bracket!, was expecting X, but got Y" (closed by the wrong type).
///
/// `bracket_pairs` is the dialect's full bracket-pairs set (see
/// `Dialect::get_bracket_pairs`), so dialect-specific brackets are recognised
/// identically to round/square/curly, not just the universal ASCII trio.
fn find_mismatched_closing_bracket(
    tokens: &[Token],
    from_idx: usize,
    open_idx: usize,
    bracket_pairs: &BracketPairSet,
) -> BracketScanResult {
    let mut idx = from_idx;
    let mut innermost_idx = open_idx;
    let mut open_raw = tokens[open_idx].raw().to_string();
    while idx < tokens.len() {
        let raw = tokens[idx].raw();
        if bracket_pairs.is_open(raw) {
            match tokens[idx].matching_bracket_idx {
                Some(matching_idx) => idx = matching_idx + 1,
                None => {
                    innermost_idx = idx;
                    open_raw = raw.to_string();
                    idx += 1;
                }
            }
        } else if bracket_pairs.is_close(raw) {
            return BracketScanResult::Mismatch {
                idx,
                actual_close: raw.to_string(),
                expected_open: open_raw,
            };
        } else {
            idx += 1;
        }
    }
    BracketScanResult::Unclosed { idx: innermost_idx }
}

impl Parser<'_> {
    pub(crate) fn try_match_grammar(
        &mut self,
        grammar_id: GrammarId,
        pos: usize,
        terminators: &[GrammarId],
    ) -> Result<usize, ParseError> {
        // Delegate to module-level implementation
        try_match_grammar(self, grammar_id, pos, terminators)
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

    pub(crate) fn greedy_match(
        &mut self,
        start_idx: usize,
        terminators: &[GrammarId],
        max_idx: usize,
    ) -> Result<(usize, usize), ParseError> {
        let tokens = self.tokens;
        let tokens_len = tokens.len();
        let bracket_pairs = self.dialect.get_bracket_pairs();

        if start_idx >= tokens_len {
            return Ok((tokens_len, tokens_len));
        }

        // Scan forward for a terminator, skipping over bracketed sections.
        let max_idx = std::cmp::min(max_idx, tokens_len);
        let mut i = start_idx;
        while i < max_idx {
            let token = &tokens[i];
            let raw = token.raw();
            // PYTHON PARITY: terminators are checked before brackets
            // (next_ex_bracket_match order), so a `(` terminator wins.
            for &term_id in terminators {
                // NONCODE is a sentinel handled by is_terminated; tables panic on it.
                if term_id == GrammarId::NONCODE {
                    continue;
                }
                // PYTHON PARITY: only probe where the simple hint fits this
                // token, as next_match does.
                let tables = self.grammar_ctx.tables();
                if let Some(hint) = tables.get_simple_hint_for_grammar(term_id) {
                    if !tables.hint_can_match(
                        hint,
                        token.raw_upper(),
                        &token.instance_types,
                        &token.class_types,
                    ) {
                        continue;
                    }
                }
                vdebug!(
                    "[GREEDY_MATCH_TABLE] greedy_match: checking terminator {:?} at {}",
                    term_id,
                    i
                );
                let cache_key = (i, term_id.0);
                let cached = self.terminator_match_cache.get(&cache_key).copied();
                let matched = if let Some(hit) = cached {
                    hit
                } else {
                    // Frame-free for terminal terminators (see
                    // terminator_matches_at); full sub-parse otherwise.
                    let result = self.terminator_matches_at(term_id, i, terminators);
                    self.terminator_match_cache.insert(cache_key, result);
                    result
                };
                if matched {
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
                                "[GREEDY_MATCH_TABLE] greedy_match: skipping {:?} at {} — all-alpha token not preceded by whitespace",
                                term_id, i
                            );
                            continue;
                        }
                    }
                    vdebug!(
                        "[GREEDY_MATCH_TABLE] greedy_match: terminator {:?} matched at {}",
                        term_id,
                        i
                    );
                    let stop_idx = self.skip_stop_index_backward_to_code(i, start_idx);
                    return Ok((i, stop_idx));
                }
            }
            // Block comments lex per line, so a comment piece can be `)`.
            let is_code = token.is_code();
            if is_code && bracket_pairs.is_open(raw) {
                if let Some(matching_idx) = token.matching_bracket_idx {
                    vdebug!(
                        "[GREEDY_MATCH_TABLE] greedy_match: skipping bracket at {} to {}",
                        i,
                        matching_idx + 1
                    );
                    i = matching_idx + 1;
                    continue;
                } else {
                    // PYTHON PARITY: mirror Python's resolve_bracket by raising
                    // its specific "wrong bracket type" error when the closer
                    // ahead is mismatched, keeping the generic "never closed"
                    // message for the true unclosed-to-EOF case. Either way,
                    // blame the innermost still-open bracket, matching
                    // resolve_bracket's own recursive call.
                    match find_mismatched_closing_bracket(tokens, i + 1, i, bracket_pairs) {
                        BracketScanResult::Mismatch {
                            idx: mismatch_idx,
                            actual_close,
                            expected_open,
                        } => {
                            // Lookup can't miss (expected_open is always a
                            // registered opener), but fall back to the opener
                            // text rather than panicking.
                            let expected_close = bracket_pairs
                                .find_by_open(&expected_open)
                                .map(|p| p.close)
                                .unwrap_or(expected_open.as_str());
                            vdebug!(
                                "[GREEDY_MATCH_TABLE] greedy_match: mismatched closing bracket '{}' at {} for opening bracket at {} (expected '{}')",
                                actual_close, mismatch_idx, i, expected_close
                            );
                            return Err(ParseError::with_context(
                                format!(
                                    "Found unexpected end bracket!, was expecting <StringParser: '{}'>, but got <StringParser: '{}'>",
                                    expected_close, actual_close
                                ),
                                Some(mismatch_idx),
                                None,
                            ));
                        }
                        BracketScanResult::Unclosed { idx: innermost_idx } => {
                            vdebug!(
                                "[GREEDY_MATCH_TABLE] greedy_match: no matching closing bracket for opening bracket at {}",
                                innermost_idx
                            );
                            return Err(ParseError::with_context(
                                "Couldn't find closing bracket for opening bracket.".to_string(),
                                Some(innermost_idx),
                                None,
                            ));
                        }
                    }
                }
            }

            // PYTHON PARITY: a closing bracket reached here is stray, not
            // nested inside anything we're currently scanning past (an
            // opening bracket's matching_bracket_idx skip would have
            // consumed it otherwise). Mirror Python's next_ex_bracket_match
            // (match_algorithms.py), which treats this as "unexpected end
            // bracket! Return no match": abort the terminator search and
            // claim everything through max_idx, rather than scan past the
            // stray bracket to a later terminator like `FROM` or `UNION`.
            if is_code && bracket_pairs.is_close(raw) {
                vdebug!(
                    "[GREEDY_MATCH_TABLE] greedy_match: unexpected closing bracket at {} — aborting terminator search, claiming through {}",
                    i, max_idx
                );
                return Ok((start_idx, max_idx));
            }

            i += 1;
        }
        vdebug!(
            "[GREEDY_MATCH_TABLE] greedy_match: returning max_idx={}",
            max_idx
        );
        Ok((start_idx, max_idx))
    }
}

#[cfg(test)]
mod tests {
    use sqlfluffrs_dialects::Dialect;
    use sqlfluffrs_lexer::{LexInput, Lexer};

    use crate::parser::Parser;

    /// Issue 8612: a `(` terminator must win over skipping the bracket pair.
    #[test]
    fn test_greedy_match_bracket_terminator_beats_bracket_skip() {
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
        let (tokens, _) = lexer.lex(LexInput::String("a = b (c) d".to_string()), false);
        let start_bracket = dialect
            .get_segment_grammar("StartBracketSegment")
            .expect("StartBracketSegment")
            .grammar_id;

        let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
        let (term_idx, stop_idx) = parser
            .greedy_match(0, &[start_bracket], tokens.len())
            .expect("greedy_match");

        assert_eq!(tokens[term_idx].raw(), "(");
        assert_eq!(tokens[stop_idx - 1].raw(), "b");
    }
}
