// Temporary test file to check if iterative OneOf reduces stack usage
#[cfg(test)]
mod tests {
    use sqlfluffrs::{Dialect, Lexer, LexInput, Parser};

    #[test]
    fn test_parse_statements_iterative() {
        env_logger::try_init().ok();

        let raw = r#"
SELECT a, b, c
FROM foo
JOIN bar USING (a)
WHERE x > 100
"#;
        let dialect = Dialect::Ansi;

        let input = LexInput::String(raw.into());
        let lexer = Lexer::new(None, dialect);
        let (tokens, _) = lexer.lex(input, false);

        // Try with iterative OneOf (should use less stack)
        let mut parser = Parser::new(&tokens, dialect);
        parser.use_iterative_oneof = true;

        let result = parser.call_rule("StatementSegment", &[]);
        assert!(result.is_ok(), "Parse should succeed with iterative OneOf");

        println!("✓ Parse succeeded with iterative OneOf");
        parser.print_cache_stats();
    }
}
