//! Lexing scripts run through a command-line client, with the mysql rules.
//!
//! The same cases as `test/core/parser/client_commands_test.py`. Every case
//! was checked against the mysql 8.4 and 9.7 and mariadb 11.8 clients.

use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_types::{ClientCommandRules, Token};

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
        "DELIMITER \\$\\$\nSELECT 1 $$\n",
        &[
            ("word", "DELIMITER"),
            ("delimiter_argument", "\\$\\$"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("client_delimiter", "$$"),
        ],
    );
}

#[test]
fn test_delimiter_with_whitespace_inside_is_rejected() {
    assert_tokens(
        "DELIMITER a\\ b\nSELECT 1 a b;\n",
        &[
            ("word", "DELIMITER"),
            ("client_command_rejected", "a\\ b"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("word", "a"),
            ("word", "b"),
            ("semicolon", ";"),
        ],
    );
}

/// Whitespace past the 15th byte is cut off, so it doesn't count.
#[test]
fn test_whitespace_past_the_cut_is_accepted() {
    assert_tokens(
        "DELIMITER 'aaaaaaaaaaaaaaa b'\nSELECT 1 aaaaaaaaaaaaaaa\n",
        &[
            ("word", "DELIMITER"),
            ("delimiter_argument", "'aaaaaaaaaaaaaaa b'"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("client_delimiter", "aaaaaaaaaaaaaaa"),
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
fn test_short_delimiter_command_skips_to_the_new_delimiter() {
    assert_tokens(
        "\\d $$ SELECT 1 $$\n",
        &[
            ("client_short_command", "\\d"),
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
            ("client_short_command", "\\g"),
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
            ("client_short_command", "\\g"),
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
fn test_command_after_a_short_command() {
    assert_tokens(
        "\\d $$\nDELIMITER ;\n",
        &[
            ("client_short_command", "\\d"),
            ("delimiter_argument", "$$"),
            ("word", "DELIMITER"),
            ("delimiter_argument", ";"),
        ],
    );
}

#[test]
fn test_short_delimiter_command_goes_on_inside_a_long_argument() {
    assert_tokens(
        "\\d abcdefghijklmnopqrstuvwxyz\nSELECT 1 abcdefghijklmno\n",
        &[
            ("client_short_command", "\\d"),
            ("delimiter_argument", "abcdefghijklmno"),
            ("word", "pqrstuvwxyz"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("client_delimiter", "abcdefghijklmno"),
        ],
    );
}

#[test]
fn test_short_delimiter_command_discards_the_rest_of_its_line() {
    assert_tokens(
        "SELECT 8 \\d 'a\\' more\n;\n",
        &[
            ("word", "SELECT"),
            ("numeric_literal", "8"),
            ("client_short_command", "\\d"),
            ("client_command_rejected", "'a\\'"),
            ("client_command_ignored", "more"),
            ("semicolon", ";"),
        ],
    );
}

#[test]
fn test_short_delimiter_command_skips_to_its_escaped_delimiter() {
    assert_tokens(
        "SELECT 1 \\d \\$\\$ SELECT 2 $$\nSELECT 3 $$\n",
        &[
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("client_short_command", "\\d"),
            ("delimiter_argument", "\\$\\$"),
            ("client_command_ignored", "SELECT 2 $$"),
            ("word", "SELECT"),
            ("numeric_literal", "3"),
            ("client_delimiter", "$$"),
        ],
    );
}

#[test]
fn test_rejected_short_delimiter_keeps_the_delimiter() {
    // `\d xab\` is rejected for its backslash, so `ab` stays the delimiter.
    let (tokens, _) = Lexer::for_dialect(Dialect::Mysql).lex(
        LexInput::String("DELIMITER ab\n\\d xab\\\nSELECT 2 ab\n".to_string()),
        false,
    );
    let kinds: Vec<(String, String)> = tokens
        .iter()
        .filter_map(|token| {
            let kind = token.instance_types.first()?;
            Some((kind.clone(), token.raw().to_string()))
        })
        .collect();
    assert!(kinds.contains(&("client_command_rejected".to_string(), "xab".to_string())));
    assert_eq!(
        kinds[kinds.len() - 2..],
        [
            ("client_delimiter".to_string(), "ab".to_string()),
            ("newline".to_string(), "\n".to_string()),
        ]
    );
}

#[test]
fn test_delimiter_ending_with_whitespace_is_rejected() {
    assert_tokens(
        "DELIMITER '$$ '\nSELECT 1;\n",
        &[
            ("word", "DELIMITER"),
            ("client_command_rejected", "'$$ '"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("semicolon", ";"),
        ],
    );
}

#[test]
fn test_delimiter_starting_with_whitespace_is_rejected() {
    assert_tokens(
        "SELECT 1 \\d  \\ \nSELECT 2;\n",
        &[
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("client_short_command", "\\d"),
            ("client_command_rejected", "\\ "),
            ("word", "SELECT"),
            ("numeric_literal", "2"),
            ("semicolon", ";"),
        ],
    );
}

#[test]
fn test_delimiter_ending_with_whitespace_once_cut_is_rejected() {
    assert_tokens(
        "DELIMITER 'aaaaaaaaaaaaaa b'\nSELECT 1;\n",
        &[
            ("word", "DELIMITER"),
            ("client_command_rejected", "'aaaaaaaaaaaaaa b'"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("semicolon", ";"),
        ],
    );
}

/// The client looks for a backslash before it cuts, so one past the 15th
/// byte is still rejected.
#[test]
fn test_delimiter_with_backslash_past_the_cut_is_rejected() {
    assert_tokens(
        "DELIMITER `aaaaaaaaaaaaaaa\\`\nSELECT 1;\n",
        &[
            ("word", "DELIMITER"),
            ("client_command_rejected", "`aaaaaaaaaaaaaaa\\`"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("semicolon", ";"),
        ],
    );
}

#[test]
fn test_short_delimiter_command_with_no_argument_is_rejected() {
    assert_tokens(
        "\\d\nSELECT 1;\n",
        &[
            ("client_short_command", "\\d"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("semicolon", ";"),
        ],
    );
}

#[test]
fn test_unclosed_quoted_argument_is_rejected() {
    assert_tokens(
        "DELIMITER 'ab\nSELECT 1;\n",
        &[
            ("word", "DELIMITER"),
            ("client_command_rejected", "'ab"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("semicolon", ";"),
        ],
    );
}

#[test]
fn test_line_with_lower_case_g_is_collected() {
    assert_tokens(
        "DELIMITER // \\g\nSOURCE a.sql \\G\n",
        &[
            ("word", "DELIMITER"),
            ("client_command_misread", "//"),
            ("client_short_command", "\\g"),
            ("word", "SOURCE"),
            ("source_file_name", "a.sql \\G"),
        ],
    );
}

#[test]
fn test_mariadb_collected_command_after_a_comment() {
    let expected: Vec<(String, String)> = [
        ("block_comment", "/* c */"),
        ("word", "SOURCE"),
        ("source_file_name", "a.sql"),
        ("semicolon", ";"),
    ]
    .iter()
    .map(|(kind, raw)| (kind.to_string(), raw.to_string()))
    .collect();
    assert_eq!(
        tokens("/* c */ SOURCE a.sql;\n", Dialect::Mariadb),
        expected
    );
}

#[test]
fn test_short_command_right_after_source() {
    assert_tokens(
        "SOURCE \\g\n",
        &[("word", "SOURCE"), ("client_short_command", "\\g")],
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
fn test_no_delimiter_byte_limit() {
    let mysql = Dialect::Mysql
        .get_client_commands()
        .expect("mysql has client commands");
    let rules: &'static ClientCommandRules = Box::leak(Box::new(ClientCommandRules {
        max_delimiter_bytes: None,
        ..*mysql
    }));
    let delimiter = "abcdefghijklmnopqrstuvwxyz";
    let sql = format!("DELIMITER {delimiter}\nSELECT 1 {delimiter}\n");
    let (tokens, _) = Lexer::for_dialect(Dialect::Mysql)
        .with_client_commands(Some(rules))
        .lex(LexInput::String(sql), false);
    let delimiters: Vec<&str> = tokens
        .iter()
        .filter(|token| token.is_type(&["client_delimiter"]))
        .map(Token::raw)
        .collect();
    assert_eq!(delimiters, [delimiter]);
}

#[test]
fn test_unlexable_text() {
    let (tokens, errors) = Lexer::for_dialect(Dialect::Mysql)
        .lex(LexInput::String("SELECT 1 \u{1};\n".to_string()), false);
    let unlexable: Vec<&str> = tokens
        .iter()
        .filter(|token| token.is_type(&["unlexable"]))
        .map(Token::raw)
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

/// After a delimiter on its line, DELIMITER is collected, and runs at the old delimiter: the new one applies from just after it.
#[test]
fn test_collected_delimiter_runs_at_the_old_delimiter() {
    assert_tokens(
        "SELECT 1; DELIMITER // ;\nSELECT 2 //\n",
        &[
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("semicolon", ";"),
            ("word", "DELIMITER"),
            ("delimiter_argument", "//"),
            ("semicolon", ";"),
            ("word", "SELECT"),
            ("numeric_literal", "2"),
            ("client_delimiter", "//"),
        ],
    );
}

/// The old delimiter ends the collected argument, so this sets `//`, though `DELIMITER //;` on its own line sets `//;`.
#[test]
fn test_collected_delimiter_argument_ends_at_the_old_delimiter() {
    assert_tokens(
        "SELECT 1; DELIMITER //;\nSELECT 2 //\n",
        &[
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("semicolon", ";"),
            ("word", "DELIMITER"),
            ("delimiter_argument", "//"),
            ("semicolon", ";"),
            ("word", "SELECT"),
            ("numeric_literal", "2"),
            ("client_delimiter", "//"),
        ],
    );
}

/// Words after the argument are ignored, as on DELIMITER's own line.
#[test]
fn test_collected_delimiter_ignores_words_after_its_argument() {
    assert_tokens(
        "SELECT 1; DELIMITER // junk ;\nSELECT 2 //\n",
        &[
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("semicolon", ";"),
            ("word", "DELIMITER"),
            ("delimiter_argument", "//"),
            ("client_command_ignored", "junk"),
            ("semicolon", ";"),
            ("word", "SELECT"),
            ("numeric_literal", "2"),
            ("client_delimiter", "//"),
        ],
    );
}

/// With the old delimiter not on its line, the client collects the lines after it too, so it is misread.
#[test]
fn test_collected_delimiter_without_the_old_delimiter_is_misread() {
    assert_tokens(
        "SELECT 1; DELIMITER //\nSELECT 2 //\n",
        &[
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("semicolon", ";"),
            ("word", "DELIMITER"),
            ("client_command_misread", "//"),
            ("word", "SELECT"),
            ("numeric_literal", "2"),
            ("divide", "/"),
            ("divide", "/"),
        ],
    );
}

/// The old delimiter may be one set before.
#[test]
fn test_collected_delimiter_after_a_delimiter_set_before() {
    assert_tokens(
        "DELIMITER $$\nSELECT 1 $$ DELIMITER ; $$\nSELECT 2;\n",
        &[
            ("word", "DELIMITER"),
            ("delimiter_argument", "$$"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("client_delimiter", "$$"),
            ("word", "DELIMITER"),
            ("delimiter_argument", ";"),
            ("client_delimiter", "$$"),
            ("word", "SELECT"),
            ("numeric_literal", "2"),
            ("semicolon", ";"),
        ],
    );
}

/// A short command before the old delimiter sends it to the server as SQL.
#[test]
fn test_collected_delimiter_before_a_short_command_is_misread() {
    assert_tokens(
        "SELECT 1; DELIMITER // \\g\n",
        &[
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("semicolon", ";"),
            ("word", "DELIMITER"),
            ("client_command_misread", "//"),
            ("client_short_command", "\\g"),
        ],
    );
}

/// `\.` takes its whole line as the file name, backslashes and all, so a Windows path works.
#[test]
fn test_dot_command_takes_a_windows_path() {
    assert_tokens(
        "\\. C:\\My Files\\Golf\\golf.sql\n",
        &[
            ("client_short_command", "\\."),
            ("source_file_name", "C:\\My Files\\Golf\\golf.sql"),
        ],
    );
}

/// So does SOURCE, with no lower-case `\g` on its line.
#[test]
fn test_source_takes_a_windows_path() {
    assert_tokens(
        "SOURCE C:\\My Files\\Golf\\Golf.sql\n",
        &[
            ("word", "SOURCE"),
            ("source_file_name", "C:\\My Files\\Golf\\Golf.sql"),
        ],
    );
}

/// `\d` and `\n` in a SOURCE line's file name are part of it.
#[test]
fn test_source_path_with_other_short_command_letters() {
    assert_tokens(
        "SOURCE C:\\data\\new.sql\n",
        &[
            ("word", "SOURCE"),
            ("source_file_name", "C:\\data\\new.sql"),
        ],
    );
}

/// But the `\g` in `\golf` makes the client collect the line, so its backslashes run as commands, in all three clients.
#[test]
fn test_source_path_with_lower_case_g_is_collected() {
    assert_tokens(
        "SOURCE C:\\My Files\\Golf\\golf.sql\n",
        &[
            ("word", "SOURCE"),
            ("client_command_misread", "C:\\My Files"),
            ("client_short_command", "\\G"),
            ("word", "olf"),
            ("client_short_command", "\\g"),
            ("word", "olf"),
            ("dot", "."),
            ("word", "sql"),
        ],
    );
}

/// SOURCE needs a space before its file name, not a tab.
#[test]
fn test_source_with_a_tab_is_rejected() {
    assert_tokens(
        "SOURCE\tf.sql\n",
        &[("word", "SOURCE"), ("client_command_rejected", "f.sql")],
    );
}

/// `\s` matches a non-breaking space, so it is rejected too, though the
/// client treats it as an ordinary character.
#[test]
fn test_delimiter_with_a_non_breaking_space_is_rejected() {
    assert_tokens(
        "DELIMITER a\u{a0}b\nSELECT 1;\n",
        &[
            ("word", "DELIMITER"),
            ("client_command_rejected", "a\u{a0}b"),
            ("word", "SELECT"),
            ("numeric_literal", "1"),
            ("semicolon", ";"),
        ],
    );
}
