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
    assert_tokens(
        "SOURCE a.sql \\g\n",
        &[("word", "SOURCE"), ("client_command_misread", "a.sql \\g")],
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
    let last_three: Vec<&str> = mysql[mysql.len() - 3..]
        .iter()
        .map(|(_, raw)| raw.as_str())
        .collect();
    assert_eq!(last_three, ["-", "-", "x"]);
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
    let mariadb = tokens(sql, Dialect::Mariadb);
    let raws: Vec<&str> = mariadb[2..6].iter().map(|(_, raw)| raw.as_str()).collect();
    assert_eq!(raws, ["SELECT", "$js$", "a", ";;"]);
}
