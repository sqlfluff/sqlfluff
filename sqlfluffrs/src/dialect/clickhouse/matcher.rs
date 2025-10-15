/* This is a generated file! */
use once_cell::sync::Lazy;
use crate::matcher::{LexMatcher, extract_nested_block_comment};
use crate::token::Token;
use crate::token::config::TokenConfig;
use crate::regex::RegexModeGroup;
use crate::dialect::Dialect;
use hashbrown::HashSet;

pub static CLICKHOUSE_KEYWORDS: Lazy<Vec<String>> = Lazy::new(|| { vec![
    "CASE".to_string(),
    "CROSS".to_string(),
    "FULL".to_string(),
    "IGNORE".to_string(),
    "INNER".to_string(),
    "INTERVAL".to_string(),
    "JOIN".to_string(),
    "LEFT".to_string(),
    "NATURAL".to_string(),
    "NOT".to_string(),
    "NULL".to_string(),
    "ON".to_string(),
    "ORDER".to_string(),
    "OUTER".to_string(),
    "PARTITION".to_string(),
    "RESPECT".to_string(),
    "RIGHT".to_string(),
    "ROWS".to_string(),
    "SELECT".to_string(),
    "SET".to_string(),
    "UNION".to_string(),
    "USING".to_string(),
]});

pub static CLICKHOUSE_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "whitespace",
        r#"[^\S\r\n]+"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::whitespace_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        |_| true,
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "inline_comment",
        r#"(--|#)[^\n]*"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::comment_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        None,
        None,
        None,
        None,
        |input| input.starts_with(['#','-','/']),
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::comment_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Clickhouse,
        "newline",
        r#"\r\n|\n"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::newline_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        |_| true,
        None,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Clickhouse,
        "whitespace",
        r#"[^\S\r\n]+"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::whitespace_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        |_| true,
        None,
    ))),
        None,
        None,
        None,
        None,
        None,
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "single_quote",
        r#"'([^'\\]|\\.|'')*'"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        Some((r#"'((?:[^'\\]|\\.|'')*)'"#.to_string(), RegexModeGroup::Index(1))),
        Some((r#"\\'|''"#.to_string(), r#"'"#.to_string())),
        None,
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "double_quote",
        r#""([^"\\]|""|\\.)*""#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        Some((r#""((?:[^"\\]|""|\\.)*)""#.to_string(), RegexModeGroup::Index(1))),
        Some((r#"(""|\\")"#.to_string(), r#"""#.to_string())),
        None,
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "back_quote",
        r#"`(?:[^`\\]|``|\\.)*`"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        Some((r#"`((?:[^`\\]|``|\\.)*)`"#.to_string(), RegexModeGroup::Index(1))),
        Some((r#"(``|\\`)"#.to_string(), r#"`"#.to_string())),
        None,
        None,
        |_| true,
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        Some((r#"\$(\w*)\$(.*?)\$\1\$"#.to_string(), RegexModeGroup::Index(2))),
        None,
        None,
        None,
        |input| input.starts_with("$"),
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::literal_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        |input| input.starts_with(['x','X','.','0','1','2','3','4','5','6','7','8','9']),
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "obevo_annotation",
        r#"////\s*(CHANGE|BODY|METADATA)[^\n]*"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::comment_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        |_| true,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "glob_operator",
        "~~~",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::comparison_operator_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "like_operator",
        r#"!?~~?\*?"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::comparison_operator_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        |_| true,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "lambda",
        "->",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::symbol_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "newline",
        r#"\r\n|\n"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::newline_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        |_| true,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "casting_operator",
        "::",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "equals",
        "=",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "greater_than",
        ">",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "less_than",
        "<",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "not",
        "!",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "dot",
        ".",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "comma",
        ",",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "plus",
        "+",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "minus",
        "-",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "divide",
        "/",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "percent",
        "%",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "question",
        "?",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "ampersand",
        "&",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "vertical_bar",
        "|",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "caret",
        "^",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "star",
        "*",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "start_bracket",
        "(",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "end_bracket",
        ")",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "start_square_bracket",
        "[",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "end_square_bracket",
        "]",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "start_curly_bracket",
        "{",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "end_curly_bracket",
        "}",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "colon",
        ":",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "semicolon",
        ";",
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::code_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::word_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        |_| true,
        None,
    ),
]});
