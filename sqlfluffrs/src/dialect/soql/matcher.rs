/* This is a generated file! */
use once_cell::sync::Lazy;
use crate::matcher::{LexMatcher, extract_nested_block_comment};
use crate::token::Token;
use crate::token::config::TokenConfig;
use crate::regex::RegexModeGroup;
use crate::dialect::Dialect;
use hashbrown::HashSet;

pub static SOQL_KEYWORDS: Lazy<Vec<String>> = Lazy::new(|| { vec![
    "CASE".to_string(),
    "CROSS".to_string(),
    "FULL".to_string(),
    "IGNORE".to_string(),
    "INNER".to_string(),
    "INTERVAL".to_string(),
    "JOIN".to_string(),
    "LAST_90_DAYS".to_string(),
    "LAST_FISCAL_QUARTER".to_string(),
    "LAST_FISCAL_YEAR".to_string(),
    "LAST_MONTH".to_string(),
    "LAST_N_DAYS".to_string(),
    "LAST_N_FISCAL_QUARTERS".to_string(),
    "LAST_N_FISCAL_YEARS".to_string(),
    "LAST_N_MONTHS".to_string(),
    "LAST_N_QUARTERS".to_string(),
    "LAST_N_WEEKS".to_string(),
    "LAST_N_YEARS".to_string(),
    "LAST_QUARTER".to_string(),
    "LAST_WEEK".to_string(),
    "LAST_YEAR".to_string(),
    "LEFT".to_string(),
    "NATURAL".to_string(),
    "NEXT_90_DAYS".to_string(),
    "NEXT_FISCAL_QUARTER".to_string(),
    "NEXT_FISCAL_YEAR".to_string(),
    "NEXT_MONTH".to_string(),
    "NEXT_N_DAYS".to_string(),
    "NEXT_N_FISCAL_QUARTERS".to_string(),
    "NEXT_N_FISCAL_YEARS".to_string(),
    "NEXT_N_MONTHS".to_string(),
    "NEXT_N_QUARTERS".to_string(),
    "NEXT_N_WEEKS".to_string(),
    "NEXT_N_YEARS".to_string(),
    "NEXT_QUARTER".to_string(),
    "NEXT_WEEK".to_string(),
    "NEXT_YEAR".to_string(),
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
    "THIS_FISCAL_QUARTER".to_string(),
    "THIS_FISCAL_YEAR".to_string(),
    "THIS_MONTH".to_string(),
    "THIS_QUARTER".to_string(),
    "THIS_WEEK".to_string(),
    "THIS_YEAR".to_string(),
    "TODAY".to_string(),
    "TOMORROW".to_string(),
    "UNION".to_string(),
    "USING".to_string(),
    "YESTERDAY".to_string(),
]});

pub static SOQL_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
        "double_quote",
        r#""(""|[^"\\]|\\.)*""#,
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
        Some((r#""((?:[^"\\]|\\.)*)""#.to_string(), RegexModeGroup::Index(1))),
        Some((r#"\\"|"""#.to_string(), r#"""#.to_string())),
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
        Dialect::Soql,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
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
        Some((r#"`((?:[^`\\]|\\.)*)`"#.to_string(), RegexModeGroup::Index(1))),
        Some((r#"\\`"#.to_string(), r#"`"#.to_string())),
        None,
        None,
        |_| true,
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
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
        Dialect::Soql,
        "datetime_literal",
        r#"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z|(\+|\-)[0-9]{2}:[0-9]{2})"#,
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
        |_| true,
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "date_literal",
        r#"[0-9]{4}-[0-9]{2}-[0-9]{2}"#,
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
        |_| true,
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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

    LexMatcher::regex_lexer(
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
        Dialect::Soql,
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
