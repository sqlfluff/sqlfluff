use sqlfluffrs_types::{GrammarId, GrammarVariant, Token};

use crate::parser::{ParseError, Parser};

#[cfg(feature = "verbose-debug")]
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

/// The result of scanning forward for how an unresolved opening bracket at
/// `open_idx` is eventually accounted for.
enum BracketScanResult {
    /// A closer of the wrong type was found. `idx` is its position,
    /// `actual_close` its raw text, and `expected_open` the type of the
    /// innermost still-open bracket it should have closed instead.
    Mismatch {
        idx: usize,
        actual_close: String,
        expected_open: char,
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
fn find_mismatched_closing_bracket(
    tokens: &[Token],
    from_idx: usize,
    open_idx: usize,
) -> BracketScanResult {
    let mut idx = from_idx;
    let mut innermost_idx = open_idx;
    let mut open_char = tokens[open_idx]
        .raw()
        .chars()
        .next()
        .expect("bracket raw is non-empty");
    while idx < tokens.len() {
        let raw = tokens[idx].raw();
        match raw {
            "(" | "[" | "{" => match tokens[idx].matching_bracket_idx {
                Some(matching_idx) => idx = matching_idx + 1,
                None => {
                    innermost_idx = idx;
                    open_char = raw.chars().next().expect("bracket raw is non-empty");
                    idx += 1;
                }
            },
            ")" | "]" | "}" => {
                return BracketScanResult::Mismatch {
                    idx,
                    actual_close: raw.to_string(),
                    expected_open: open_char,
                };
            }
            _ => idx += 1,
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

        if start_idx >= tokens_len {
            return Ok((tokens_len, tokens_len));
        }

        // If a terminator matches immediately (at start_idx), return as-is.
        // Python allows keyword terminators at the very start ("first element" edge case).
        for &term_id in terminators {
            // Skip the NONCODE sentinel (not a real grammar id; handled by
            // `is_terminated`). Indexing the grammar tables with it would panic.
            if term_id == GrammarId::NONCODE {
                continue;
            }
            vdebug!(
                "[GREEDY_MATCH_TABLE] greedy_match: checking immediate terminator match for {:?} at {}",
                term_id, start_idx
            );
            if self.terminator_matches_at(term_id, start_idx, terminators) {
                vdebug!(
                    "[GREEDY_MATCH_TABLE] greedy_match: immediate terminator {:?} matched at {}",
                    term_id,
                    start_idx
                );
                return Ok((start_idx, start_idx));
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
                    match find_mismatched_closing_bracket(tokens, i + 1, i) {
                        BracketScanResult::Mismatch {
                            idx: mismatch_idx,
                            actual_close,
                            expected_open,
                        } => {
                            let expected_close = match expected_open {
                                '(' => ")",
                                '[' => "]",
                                '{' => "}",
                                _ => unreachable!("expected_open is always a bracket character"),
                            };
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
            if raw == ")" || raw == "]" || raw == "}" {
                vdebug!(
                    "[GREEDY_MATCH_TABLE] greedy_match: unexpected closing bracket at {} — aborting terminator search, claiming through {}",
                    i, max_idx
                );
                return Ok((start_idx, max_idx));
            }

            for &term_id in terminators {
                // Skip the NONCODE sentinel (see the immediate-match loop above).
                if term_id == GrammarId::NONCODE {
                    continue;
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
            i += 1;
        }
        vdebug!(
            "[GREEDY_MATCH_TABLE] greedy_match: returning max_idx={}",
            max_idx
        );
        Ok((start_idx, max_idx))
    }
}
