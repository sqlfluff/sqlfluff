/* This is a generated file! */
use once_cell::sync::Lazy;
use crate::matcher::{LexMatcher, extract_nested_block_comment};
use crate::token::Token;
use crate::token::config::TokenConfig;
use crate::regex::RegexModeGroup;
use crate::dialect::Dialect;
use hashbrown::HashSet;

pub static MYSQL_KEYWORDS: Lazy<Vec<String>> = Lazy::new(|| { vec![
    "ACCESSIBLE".to_string(),
    "ADD".to_string(),
    "ALL".to_string(),
    "ALTER".to_string(),
    "ANALYZE".to_string(),
    "AND".to_string(),
    "AS".to_string(),
    "ASC".to_string(),
    "ASENSITIVE".to_string(),
    "BEFORE".to_string(),
    "BETWEEN".to_string(),
    "BIGINT".to_string(),
    "BINARY".to_string(),
    "BLOB".to_string(),
    "BOTH".to_string(),
    "BY".to_string(),
    "CALL".to_string(),
    "CASCADE".to_string(),
    "CASE".to_string(),
    "CHANGE".to_string(),
    "CHAR".to_string(),
    "CHARACTER".to_string(),
    "CHECK".to_string(),
    "COLLATE".to_string(),
    "COLUMN".to_string(),
    "CONDITION".to_string(),
    "CONSTRAINT".to_string(),
    "CONTINUE".to_string(),
    "CONVERT".to_string(),
    "CREATE".to_string(),
    "CROSS".to_string(),
    "CUME_DIST".to_string(),
    "CURRENT_DATE".to_string(),
    "CURRENT_TIME".to_string(),
    "CURRENT_TIMESTAMP".to_string(),
    "CURRENT_USER".to_string(),
    "CURSOR".to_string(),
    "DATABASE".to_string(),
    "DATABASES".to_string(),
    "DAY_HOUR".to_string(),
    "DAY_MICROSECOND".to_string(),
    "DAY_MINUTE".to_string(),
    "DAY_SECOND".to_string(),
    "DEC".to_string(),
    "DECIMAL".to_string(),
    "DECLARE".to_string(),
    "DEFAULT".to_string(),
    "DELAYED".to_string(),
    "DELETE".to_string(),
    "DENSE_RANK".to_string(),
    "DESC".to_string(),
    "DESCRIBE".to_string(),
    "DETERMINISTIC".to_string(),
    "DISTINCT".to_string(),
    "DISTINCTROW".to_string(),
    "DIV".to_string(),
    "DOUBLE".to_string(),
    "DROP".to_string(),
    "DUAL".to_string(),
    "EACH".to_string(),
    "ELSE".to_string(),
    "ELSEIF".to_string(),
    "EMPTY".to_string(),
    "ENCLOSED".to_string(),
    "ESCAPED".to_string(),
    "EXCEPT".to_string(),
    "EXISTS".to_string(),
    "EXIT".to_string(),
    "EXPLAIN".to_string(),
    "FALSE".to_string(),
    "FETCH".to_string(),
    "FIRST_VALUE".to_string(),
    "FLOAT".to_string(),
    "FLOAT4".to_string(),
    "FLOAT8".to_string(),
    "FOR".to_string(),
    "FORCE".to_string(),
    "FOREIGN".to_string(),
    "FROM".to_string(),
    "FULLTEXT".to_string(),
    "GENERATED".to_string(),
    "GET".to_string(),
    "GRANT".to_string(),
    "GROUP".to_string(),
    "GROUPING".to_string(),
    "GROUPS".to_string(),
    "HAVING".to_string(),
    "HIGH_PRIORITY".to_string(),
    "HOUR_MICROSECOND".to_string(),
    "HOUR_MINUTE".to_string(),
    "HOUR_SECOND".to_string(),
    "IF".to_string(),
    "IGNORE".to_string(),
    "IN".to_string(),
    "INDEX".to_string(),
    "INFILE".to_string(),
    "INNER".to_string(),
    "INOUT".to_string(),
    "INSENSITIVE".to_string(),
    "INSERT".to_string(),
    "INT".to_string(),
    "INT1".to_string(),
    "INT2".to_string(),
    "INT3".to_string(),
    "INT4".to_string(),
    "INT8".to_string(),
    "INTEGER".to_string(),
    "INTERSECT".to_string(),
    "INTERVAL".to_string(),
    "INTO".to_string(),
    "IO_AFTER_GTIDS".to_string(),
    "IO_BEFORE_GTIDS".to_string(),
    "IS".to_string(),
    "ITERATE".to_string(),
    "JOIN".to_string(),
    "JSON_TABLE".to_string(),
    "KEY".to_string(),
    "KEYS".to_string(),
    "KILL".to_string(),
    "LAG".to_string(),
    "LAST_VALUE".to_string(),
    "LATERAL".to_string(),
    "LEAD".to_string(),
    "LEADING".to_string(),
    "LEAVE".to_string(),
    "LEFT".to_string(),
    "LIKE".to_string(),
    "LIMIT".to_string(),
    "LINEAR".to_string(),
    "LINES".to_string(),
    "LOAD".to_string(),
    "LOCALTIME".to_string(),
    "LOCALTIMESTAMP".to_string(),
    "LOCK".to_string(),
    "LONG".to_string(),
    "LONGBLOB".to_string(),
    "LONGTEXT".to_string(),
    "LOOP".to_string(),
    "LOW_PRIORITY".to_string(),
    "MASTER_BIND".to_string(),
    "MASTER_SSL_VERIFY_SERVER_CERT".to_string(),
    "MATCH".to_string(),
    "MAXVALUE".to_string(),
    "MEDIUMBLOB".to_string(),
    "MEDIUMINT".to_string(),
    "MEDIUMTEXT".to_string(),
    "MIDDLEINT".to_string(),
    "MINUTE_MICROSECOND".to_string(),
    "MINUTE_SECOND".to_string(),
    "MOD".to_string(),
    "MODIFIES".to_string(),
    "NATURAL".to_string(),
    "NOT".to_string(),
    "NO_WRITE_TO_BINLOG".to_string(),
    "NTH_VALUE".to_string(),
    "NTILE".to_string(),
    "NULL".to_string(),
    "NUMERIC".to_string(),
    "OF".to_string(),
    "ON".to_string(),
    "OPTIMIZE".to_string(),
    "OPTIMIZER_COSTS".to_string(),
    "OPTION".to_string(),
    "OPTIONALLY".to_string(),
    "OR".to_string(),
    "ORDER".to_string(),
    "OUT".to_string(),
    "OUTER".to_string(),
    "OUTFILE".to_string(),
    "OVER".to_string(),
    "PARTITION".to_string(),
    "PERCENT_RANK".to_string(),
    "PRECISION".to_string(),
    "PRIMARY".to_string(),
    "PROCEDURE".to_string(),
    "PURGE".to_string(),
    "RANGE".to_string(),
    "RANK".to_string(),
    "READ".to_string(),
    "READS".to_string(),
    "READ_WRITE".to_string(),
    "REAL".to_string(),
    "RECURSIVE".to_string(),
    "REFERENCES".to_string(),
    "REGEXP".to_string(),
    "RELEASE".to_string(),
    "RENAME".to_string(),
    "REPEAT".to_string(),
    "REPLACE".to_string(),
    "REQUIRE".to_string(),
    "RESIGNAL".to_string(),
    "RESTRICT".to_string(),
    "RETURN".to_string(),
    "REVOKE".to_string(),
    "RIGHT".to_string(),
    "RLIKE".to_string(),
    "ROW_NUMBER".to_string(),
    "SCHEMA".to_string(),
    "SCHEMAS".to_string(),
    "SECOND_MICROSECOND".to_string(),
    "SELECT".to_string(),
    "SENSITIVE".to_string(),
    "SEPARATOR".to_string(),
    "SET".to_string(),
    "SHOW".to_string(),
    "SIGNAL".to_string(),
    "SMALLINT".to_string(),
    "SPATIAL".to_string(),
    "SPECIFIC".to_string(),
    "SQL".to_string(),
    "SQLEXCEPTION".to_string(),
    "SQLSTATE".to_string(),
    "SQLWARNING".to_string(),
    "SQL_BIG_RESULT".to_string(),
    "SQL_CALC_FOUND_ROWS".to_string(),
    "SQL_SMALL_RESULT".to_string(),
    "SSL".to_string(),
    "STARTING".to_string(),
    "STORED".to_string(),
    "STRAIGHT_JOIN".to_string(),
    "SYSTEM".to_string(),
    "TABLE".to_string(),
    "TERMINATED".to_string(),
    "THEN".to_string(),
    "TINYBLOB".to_string(),
    "TINYINT".to_string(),
    "TINYTEXT".to_string(),
    "TO".to_string(),
    "TRAILING".to_string(),
    "TRIGGER".to_string(),
    "TRUE".to_string(),
    "UNDO".to_string(),
    "UNION".to_string(),
    "UNIQUE".to_string(),
    "UNLOCK".to_string(),
    "UNSIGNED".to_string(),
    "UPDATE".to_string(),
    "USAGE".to_string(),
    "USE".to_string(),
    "USING".to_string(),
    "UTC_DATE".to_string(),
    "UTC_TIME".to_string(),
    "UTC_TIMESTAMP".to_string(),
    "VALUES".to_string(),
    "VARBINARY".to_string(),
    "VARCHAR".to_string(),
    "VARCHARACTER".to_string(),
    "VARYING".to_string(),
    "VIRTUAL".to_string(),
    "WHEN".to_string(),
    "WHERE".to_string(),
    "WHILE".to_string(),
    "WINDOW".to_string(),
    "WITH".to_string(),
    "WRITE".to_string(),
    "XOR".to_string(),
    "YEAR_MONTH".to_string(),
    "ZEROFILL".to_string(),
]});

pub static MYSQL_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Mysql,
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
        Dialect::Mysql,
        "inline_comment",
        r#"(^--|-- |#)[^\n]*"#,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
        "single_quote",
        r#"(?s)('(?:\\'|''|\\\\|[^'])*'(?!'))"#,
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
        Some((r#"(?s)('((?:\\'|''|\\\\|[^'])*)'(?!'))"#.to_string(), RegexModeGroup::Index(2))),
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
        Dialect::Mysql,
        "double_quote",
        r#"(?s)("(?:\\"|""|\\\\|[^"])*"(?!"))"#,
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
        Some((r#"(?s)("((?:\\"|""|\\\\|[^"])*)"(?!"))"#.to_string(), RegexModeGroup::Index(2))),
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
        "hexadecimal_literal",
        r#"([xX]'([\da-fA-F][\da-fA-F])+'|0x[\da-fA-F]+)"#,
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
        |_| true,
        Some(String::from("numeric_literal")),
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "bit_value_literal",
        r#"([bB]'[01]+'|0b[01]+)"#,
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
        |_| true,
        Some(String::from("numeric_literal")),
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
        "walrus_operator",
        ":=",
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
        Dialect::Mysql,
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
        Dialect::Mysql,
        "inline_path_operator",
        "->>",
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

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "column_path_operator",
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

    LexMatcher::string_lexer(
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
        "double_ampersand",
        "&&",
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
        Dialect::Mysql,
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
        Dialect::Mysql,
        "double_vertical_bar",
        "||",
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
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
        Dialect::Mysql,
        "at_sign",
        r#"@@?[a-zA-Z0-9_$]*(\.[a-zA-Z0-9_$]+)?"#,
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
        Some(vec![String::from("@")]),
        None,
        None,
        None,
        None,
        |_| true,
        Some(String::from("at_sign_literal")),
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
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
