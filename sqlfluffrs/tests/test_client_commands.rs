//! Lexing scripts run through a command-line client, with the mysql rules.
//!
//! The same cases as `test/core/parser/client_commands_test.py`. Every case
//! was checked against the mysql 8.4 and 9.7 and mariadb 11.8 clients.

use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};

/// The (type, raw) of each token the lexer makes, but whitespace.
fn tokens(sql: &str, dialect: Dialect) -> Vec<(String, String)> {
    let (tokens, errors) =
        Lexer::for_dialect(dialect).lex(LexInput::String(sql.to_string()), false);
    assert!(errors.is_empty(), "Lexer errors: {errors:?}");
    tokens
        .iter()
        .filter(|token| !token.is_type(&["whitespace", "newline", "end_of_file"]))
        .map(|token| (token.instance_types[0].clone(), token.raw().to_string()))
        .collect()
}

fn assert_tokens(sql: &str, expected: &[(&str, &str)]) {
    let expected: Vec<(String, String)> = expected
        .iter()
        .map(|(kind, raw)| (kind.to_string(), raw.to_string()))
        .collect();
    assert_eq!(tokens(sql, Dialect::Mysql), expected, "lexing {sql:?}");
}

#[test]
fn test_delimiter_is_found_inside_words() {
    assert_tokens(
        "DELIMITER go\nSELECT good go\n",
        &[
            ("word", "DELIMITER"),
            ("delimiter_argument", "go"),
            ("word", "SELECT"),
            ("client_delimiter", "go"),
            ("word", "od"),
            ("client_delimiter", "go"),
        ],
    );
}

#[test]
fn test_backslash_escapes_in_unquoted_argument() {
    assert_tokens(
        "DELIMITER a\\ b\nSELECT 1 a b\n",
        &[
            ("word", "DELIMITER"),
            ("delimiter_argument", "a\\ b"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("client_delimiter", "a b"),
        ],
    );
}

#[test]
fn test_long_delimiter_is_cut_at_a_character_boundary() {
    assert_tokens(
        "DELIMITER ééééééééx\nSELECT 1 ééééééé\n",
        &[
            ("word", "DELIMITER"),
            ("delimiter_argument", "ééééééééx"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("client_delimiter", "ééééééé"),
        ],
    );
}

#[test]
fn test_shorthand_delimiter_skips_to_the_new_delimiter() {
    assert_tokens(
        "\\d $$ SELECT 1 $$\n",
        &[
            ("client_command_shorthand", "\\d"),
            ("delimiter_argument", "$$"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("client_delimiter", "$$"),
        ],
    );
}

#[test]
fn test_dash_dash_before_statement_end_is_a_comment() {
    assert_tokens(
        "SELECT 1 --\\g\n",
        &[
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("inline_comment", "--"),
            ("client_command_shorthand", "\\g"),
        ],
    );
}

#[test]
fn test_tokens_end_where_the_server_text_ends() {
    assert_tokens(
        "DELIMITER go\nSELECT 1.go\nSELECT .5go\n",
        &[
            ("word", "DELIMITER"),
            ("delimiter_argument", "go"),
            ("word", "SELECT"),
            ("numeric_literal", "1."),
            ("client_delimiter", "go"),
            ("word", "SELECT"),
            ("numeric_literal", ".5"),
            ("client_delimiter", "go"),
        ],
    );
}

#[test]
fn test_source_after_a_delimiter_runs_to_the_next() {
    assert_tokens(
        "SELECT 1; SOURCE b.sql;\n",
        &[
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("semicolon", ";"),
            ("word", "SOURCE"),
            ("source_file_name", "b.sql"),
            ("semicolon", ";"),
        ],
    );
}

#[test]
fn test_source_collected_as_a_statement_is_misread() {
    // `\g` sends `SOURCE a.sql` to the server, which ends the statement, so
    // the next line can be a command.
    assert_tokens(
        "SOURCE a.sql \\g\nDELIMITER $$\nSELECT 1 $$\n",
        &[
            ("word", "SOURCE"),
            ("client_command_misread", "a.sql"),
            ("client_command_shorthand", "\\g"),
            ("word", "DELIMITER"),
            ("delimiter_argument", "$$"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("client_delimiter", "$$"),
        ],
    );
}

#[test]
fn test_dash_dash_at_mariadb_statement_start() {
    let sql = "SELECT 1; --x\n";
    let mariadb = tokens(sql, Dialect::Mariadb);
    assert_eq!(
        mariadb.last(),
        Some(&("inline_comment".to_string(), "--x".to_string()))
    );
    let mysql = tokens(sql, Dialect::Mysql);
    let expected: Vec<(String, String)> = [("minus", "-"), ("minus", "-"), ("word", "x")]
        .iter()
        .map(|(kind, raw)| (kind.to_string(), raw.to_string()))
        .collect();
    assert_eq!(mysql[mysql.len() - 3..], expected[..]);
}

#[test]
fn test_shorthand_delimiter_with_no_argument_is_refused() {
    assert_tokens(
        "\\d\nSELECT 1;\n",
        &[
            ("client_command_shorthand", "\\d"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("semicolon", ";"),
        ],
    );
}

#[test]
fn test_unclosed_quoted_argument_runs_to_the_end_of_the_line() {
    assert_tokens(
        "DELIMITER 'ab\nSELECT 1 ab\n",
        &[
            ("word", "DELIMITER"),
            ("delimiter_argument", "'ab"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("client_delimiter", "ab"),
        ],
    );
}

#[test]
fn test_shorthand_right_after_source() {
    assert_tokens(
        "SOURCE \\g\n",
        &[("word", "SOURCE"), ("client_command_shorthand", "\\g")],
    );
}

#[test]
fn test_trailing_whitespace_is_not_part_of_a_file_name() {
    assert_tokens(
        "SOURCE a.sql \t \n",
        &[("word", "SOURCE"), ("source_file_name", "a.sql")],
    );
}

#[test]
fn test_unlexable_text() {
    let (tokens, errors) = Lexer::for_dialect(Dialect::Mysql)
        .lex(LexInput::String("SELECT 1 \u{1};\n".to_string()), false);
    let unlexable: Vec<&str> = tokens
        .iter()
        .filter(|token| token.is_type(&["unlexable"]))
        .map(|token| token.raw())
        .collect();
    assert_eq!(unlexable, ["\u{1}"]);
    assert!(!errors.is_empty());
}

#[test]
fn test_delimiter_inside_a_dollar_quote() {
    let sql = "DELIMITER ;;\nSELECT $js$ a ;; b $js$;;\n";
    let expected: Vec<(String, String)> = [
        ("word", "SELECT"),
        ("dollar_quote", "$js$ a ;; b $js$"),
        ("client_delimiter", ";;"),
    ]
    .iter()
    .map(|(kind, raw)| (kind.to_string(), raw.to_string()))
    .collect();
    assert_eq!(tokens(sql, Dialect::Mysql)[2..], expected[..]);

    // MariaDB has no dollar-quoted strings, so its client finds the delimiter.
    let expected: Vec<(String, String)> = [
        ("word", "SELECT"),
        ("word", "$js$"),
        ("word", "a"),
        ("client_delimiter", ";;"),
    ]
    .iter()
    .map(|(kind, raw)| (kind.to_string(), raw.to_string()))
    .collect();
    assert_eq!(tokens(sql, Dialect::Mariadb)[2..6], expected[..]);
}
