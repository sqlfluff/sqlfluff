/// Extract nested block comments from SQL input.
///
/// This function handles nested block comments (/* ... /* ... */ ... */)
/// for SQL dialects that support them.
///
/// # Arguments
/// * `input` - The input string starting with "/*"
/// * `dialect` - The SQL dialect name (used for dialect-specific behavior)
///
/// # Returns
/// * `Some(&str)` - The complete block comment if valid (borrowed from `input`)
/// * `None` - If the comment is invalid or improperly closed
pub fn extract_nested_block_comment<'a>(input: &'a str, dialect: &str) -> Option<&'a str> {
    let mut chars = input.chars().peekable();
    let mut comment = String::new();

    // Ensure the input starts with "/*"
    if chars.next() != Some('/') || chars.next() != Some('*') {
        return None;
    }

    comment.push_str("/*"); // Add the opening delimiter
    let mut depth = 1; // Track nesting level

    while let Some(c) = chars.next() {
        comment.push(c);

        if c == '/' && chars.peek() == Some(&'*') {
            chars.next(); // Consume '*'
            comment.push('*');
            depth += 1;
        } else if c == '*' && chars.peek() == Some(&'/') {
            chars.next(); // Consume '/'
            comment.push('/');
            depth -= 1;

            if depth == 0 {
                return Some(&input[..comment.len()]);
            }
        }
    }

    // If we reach here, the comment wasn't properly closed
    // SQLite allows unclosed comments, other dialects don't
    match dialect {
        "sqlite" => Some(&input[..comment.len()]),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_block_comment() {
        let input = "/* simple comment */";
        let result = extract_nested_block_comment(input, "ansi");
        assert_eq!(result, Some("/* simple comment */"));
    }

    #[test]
    fn test_nested_block_comment() {
        let input = "/* outer /* inner */ still outer */";
        let result = extract_nested_block_comment(input, "ansi");
        assert_eq!(result, Some("/* outer /* inner */ still outer */"));
    }

    #[test]
    fn test_unclosed_comment_sqlite() {
        let input = "/* unclosed comment";
        let result = extract_nested_block_comment(input, "sqlite");
        assert_eq!(result, Some("/* unclosed comment"));
    }

    #[test]
    fn test_unclosed_comment_other_dialect() {
        let input = "/* unclosed comment";
        let result = extract_nested_block_comment(input, "postgres");
        assert_eq!(result, None);
    }

    #[test]
    fn test_invalid_start() {
        let input = "not a comment";
        let result = extract_nested_block_comment(input, "ansi");
        assert_eq!(result, None);
    }
}
