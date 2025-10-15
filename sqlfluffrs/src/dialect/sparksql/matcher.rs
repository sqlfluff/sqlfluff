/* This is a generated file! */
use once_cell::sync::Lazy;
use crate::matcher::{LexMatcher, extract_nested_block_comment};
use crate::token::Token;
use crate::token::config::TokenConfig;
use crate::regex::RegexModeGroup;
use crate::dialect::Dialect;
use hashbrown::HashSet;

pub static SPARKSQL_KEYWORDS: Lazy<Vec<String>> = Lazy::new(|| { vec![
    "ALL".to_string(),
    "AND".to_string(),
    "ANY".to_string(),
    "AS".to_string(),
    "AUTHORIZATION".to_string(),
    "BOTH".to_string(),
    "CASE".to_string(),
    "CAST".to_string(),
    "CHECK".to_string(),
    "COLLATE".to_string(),
    "COLUMN".to_string(),
    "CONSTRAINT".to_string(),
    "CREATE".to_string(),
    "CROSS".to_string(),
    "CURRENT_DATE".to_string(),
    "CURRENT_TIME".to_string(),
    "CURRENT_TIMESTAMP".to_string(),
    "CURRENT_USER".to_string(),
    "ELSE".to_string(),
    "END".to_string(),
    "ESCAPE".to_string(),
    "EXCEPT".to_string(),
    "FALSE".to_string(),
    "FETCH".to_string(),
    "FILTER".to_string(),
    "FOR".to_string(),
    "FOREIGN".to_string(),
    "FROM".to_string(),
    "FULL".to_string(),
    "GRANT".to_string(),
    "GROUP".to_string(),
    "HAVING".to_string(),
    "IGNORE".to_string(),
    "IN".to_string(),
    "INNER".to_string(),
    "INTERSECT".to_string(),
    "INTERVAL".to_string(),
    "INTO".to_string(),
    "IS".to_string(),
    "JOIN".to_string(),
    "LEADING".to_string(),
    "LEFT".to_string(),
    "NATURAL".to_string(),
    "NOT".to_string(),
    "NULL".to_string(),
    "ON".to_string(),
    "ONLY".to_string(),
    "OR".to_string(),
    "ORDER".to_string(),
    "OUTER".to_string(),
    "OVERLAPS".to_string(),
    "PARTITION".to_string(),
    "PRIMARY".to_string(),
    "REFERENCES".to_string(),
    "RESPECT".to_string(),
    "RIGHT".to_string(),
    "ROWS".to_string(),
    "SELECT".to_string(),
    "SESSION_USER".to_string(),
    "SET".to_string(),
    "SOME".to_string(),
    "TABLE".to_string(),
    "THEN".to_string(),
    "TO".to_string(),
    "TRAILING".to_string(),
    "UNION".to_string(),
    "UNIQUE".to_string(),
    "UNKNOWN".to_string(),
    "USER".to_string(),
    "USING".to_string(),
    "WHEN".to_string(),
    "WHERE".to_string(),
    "WITH".to_string(),
]});

pub static SPARKSQL_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
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
        Dialect::Sparksql,
        "inline_comment",
        r#"(--)[^\n]*"#,
        |raw, pos_marker, class_types, instance_types, trim_start, trim_chars,
         quoted_value, escape_replacement, casefold| {
            Token::comment_token(raw, pos_marker, TokenConfig {
                class_types, instance_types, trim_start, trim_chars,
                quoted_value, escape_replacement, casefold,
            })
        },
        None,
        None,
        Some(vec![String::from("-"), String::from("-")]),
        None,
        None,
        None,
        None,
        None,
        |input| input.starts_with(['#','-','/']),
        None,
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "start_hint",
        "/*+",
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
        "raw_single_quote",
        r#"[rR]'([^'\\]|\\.)*'"#,
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
        Dialect::Sparksql,
        "raw_double_quote",
        r#"[rR]"([^"\\]|\\.)*""#,
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
        Dialect::Sparksql,
        "bytes_single_quote",
        r#"X'([^'\\]|\\.)*'"#,
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
        Dialect::Sparksql,
        "bytes_double_quote",
        r#"X"([^"\\]|\\.)*""#,
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

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "end_hint",
        "*/",
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
        "back_quote",
        r#"`([^`]|``)*`"#,
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
        Some((r#"`((?:[^`]|``)*)`"#.to_string(), RegexModeGroup::Index(1))),
        Some((r#"``"#.to_string(), r#"`"#.to_string())),
        None,
        None,
        |_| true,
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
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
        Dialect::Sparksql,
        "numeric_literal",
        r#"(?>(?>\d+\.\d+|\d+\.|\.\d+)([eE][+-]?\d+)?([dDfF]|BD|bd)?|\d+[eE][+-]?\d+([dDfF]|BD|bd)?|\d+([dDfFlLsSyY]|BD|bd)?)((?<=\.)|(?=\b))"#,
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
        |input| input.starts_with(['x','X','.','0','1','2','3','4','5','6','7','8','9']),
        None,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "right_arrow",
        "->",
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
        "file_literal",
        r#"[a-zA-Z0-9]+:([a-zA-Z0-9\-_\.]*(\/|\\)){2,}((([a-zA-Z0-9\-_\.]*(:|\?|=|&)[a-zA-Z0-9\-_\.]*)+)|([a-zA-Z0-9\-_\.]*\.[a-z]+))"#,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "equals",
        r#"==|<=>|="#,
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

    LexMatcher::string_lexer(
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
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
        Dialect::Sparksql,
        "at_sign_literal",
        r#"@\w*"#,
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
        Dialect::Sparksql,
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
