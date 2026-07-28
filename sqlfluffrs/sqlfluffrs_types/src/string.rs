//! Small string helpers shared across the workspace.

/// Truncate `s` to `keep` codepoints and append `"..."` when it is longer than
/// `over` codepoints; otherwise return it unchanged.
///
/// This is the shared primitive behind two Python behaviours that differ only
/// in their thresholds, so each caller passes its own:
///
/// * `helpers/string.py`'s `curtail_string(s, n)` = `s[:n] + "..."` when
///   `len(s) > n` -> `ellipsize(s, n, n)`.
/// * `lexer.py`'s `raw[:10] + "..." if len(raw) > 9 else raw` -> `ellipsize(raw,
///   10, 9)` (note the deliberate 10-keep / 9-threshold asymmetry).
///
/// Counting and slicing by `char` matches Python's `len`/slicing on `str`, so
/// multi-byte characters truncate identically.
pub fn ellipsize(s: &str, keep: usize, over: usize) -> String {
    if s.chars().count() > over {
        let mut out: String = s.chars().take(keep).collect();
        out.push_str("...");
        out
    } else {
        s.to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::ellipsize;

    #[test]
    fn curtail_string_semantics() {
        // ellipsize(s, n, n): unchanged at length n, truncated past it.
        assert_eq!(ellipsize("abcd", 4, 4), "abcd");
        assert_eq!(ellipsize("abcde", 4, 4), "abcd...");
    }

    #[test]
    fn lexer_truncate_semantics() {
        // ellipsize(raw, 10, 9): the 10-keep / 9-threshold asymmetry means a
        // 10-char string keeps all ten and still gains the ellipsis.
        assert_eq!(ellipsize("123456789", 10, 9), "123456789");
        assert_eq!(ellipsize("1234567890", 10, 9), "1234567890...");
        assert_eq!(ellipsize("12345678901", 10, 9), "1234567890...");
    }

    #[test]
    fn counts_by_codepoint() {
        // Five 2-byte codepoints: length is 5 chars, not 10 bytes.
        assert_eq!(ellipsize("äääää", 3, 4), "äää...");
    }
}
