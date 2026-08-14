use super::Token;
use std::fmt::Display;

/// Render a string the way Python's `repr()` renders a `str`.
///
/// PYTHON PARITY: this surfaces verbatim in user-visible messages - token
/// Displays in UnparsableSegment "Expected: ... Found <...>" text
/// (`<{Class}: ({pos}) {raw!r}>`) and the `SQLLexError` "Unable to lex
/// characters: {!r}" description. Python's repr prefers single quotes,
/// switches to double quotes when the content contains a single quote (and no
/// double quote), escapes the backslash / the chosen quote / \n \r \t, and
/// hex/unicode-escapes control characters (C0, DEL and the C1 block) plus
/// non-space Unicode whitespace, choosing the `\xXX` / `\uXXXX` / `\U........`
/// width by codepoint - none of which matches Rust's `escape_debug`.
///
/// This is the single shared implementation used by both the parser (token
/// Display, above) and the lexer's unlexable-error rendering, so the two
/// never drift apart. (Format/private-use/unassigned codepoints are still
/// printed as-is - a documented, accepted limitation shared with the lexer.)
pub fn python_repr(s: &str) -> String {
    let has_single = s.contains('\'');
    let has_double = s.contains('"');
    let quote = if has_single && !has_double { '"' } else { '\'' };
    let mut out = String::with_capacity(s.len() + 2);
    out.push(quote);
    for c in s.chars() {
        match c {
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c == quote => {
                out.push('\\');
                out.push(c);
            }
            c if c.is_control() || (c.is_whitespace() && c != ' ') => {
                let cp = c as u32;
                if cp <= 0xff {
                    out.push_str(&format!("\\x{cp:02x}"));
                } else if cp <= 0xffff {
                    out.push_str(&format!("\\u{cp:04x}"));
                } else {
                    out.push_str(&format!("\\U{cp:08x}"));
                }
            }
            c => out.push(c),
        }
    }
    out.push(quote);
    out
}

impl Display for Token {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "<{}: ({}) {}>",
            self.class_name.clone(),
            self.pos_marker.clone().expect("PositionMarker unset"),
            python_repr(self.raw.as_str()),
        )
    }
}

#[cfg(test)]
mod tests {
    use super::python_repr;

    #[test]
    fn plain_ascii_uses_single_quotes() {
        assert_eq!(python_repr("abc"), "'abc'");
    }

    #[test]
    fn switches_to_double_quotes_for_single_quote_content() {
        assert_eq!(python_repr("it's"), "\"it's\"");
        // Both quote kinds present: stay single-quoted and escape the single.
        assert_eq!(python_repr("a'\"b"), "'a\\'\"b'");
    }

    #[test]
    fn escapes_c0_and_del() {
        assert_eq!(python_repr("\x00\x1f\x7f"), "'\\x00\\x1f\\x7f'");
        assert_eq!(python_repr("a\tb\nc"), "'a\\tb\\nc'");
    }

    #[test]
    fn escapes_c1_controls_and_non_space_whitespace() {
        // Matches CPython repr: NEL, NBSP -> \x85, \xa0; line separator ->  .
        assert_eq!(python_repr("a\u{85}b"), "'a\\x85b'");
        assert_eq!(python_repr("a\u{a0}b"), "'a\\xa0b'");
        assert_eq!(python_repr("a\u{2028}b"), "'a\\u2028b'");
    }

    #[test]
    fn leaves_printable_unicode_as_is() {
        assert_eq!(python_repr("straße"), "'straße'");
    }
}
