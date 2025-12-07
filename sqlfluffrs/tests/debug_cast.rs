use sqlfluffrs_dialects::dialect::{self, ansi::matcher::ANSI_LEXERS};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

#[test]
fn test_cast_with_whitespaces_debug() {
    env_logger::try_init().ok();

    let sql = r#"-- ansi_cast_with_whitespaces.sql
/* Several valid queries where there is whitespace surrounding the ANSI
cast operator (::) */

-- query from https://github.com/sqlfluff/sqlfluff/issues/2720
SELECT amount_of_honey :: FLOAT
FROM bear_inventory;


-- should be able to support an arbitrary amount of whitespace
SELECT amount_of_honey        ::        FLOAT
FROM bear_inventory;"#;

    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, lex_errors) = lexer.lex(input, false);

    println!("\n=== Total tokens: {} ===", tokens.len());
    for (i, tok) in tokens.iter().enumerate() {
        if tok.is_code() {
            println!("{:3}: {:20} {:?}", i, tok.token_type, tok.raw);
        }
    }

    let dialect = Dialect::Ansi;
    let mut parser = Parser::new(&tokens, dialect);
    let ast = parser.call_rule_as_root();

    match &ast {
        Ok(node) => {
            println!("\n=== AST ===");
            println!("{:#?}", node);

            println!("\n=== YAML ===");
            let as_record = node.as_record(true, true, false);
            let yaml_str = serde_yaml_ng::to_string(&as_record).unwrap();
            println!("{}", yaml_str);

            println!(
                "\n=== Parser position: {} / {} ===",
                parser.pos,
                tokens.len()
            );

            if parser.pos < tokens.len() {
                println!("\n!!! WARNING: Parser did not consume all tokens !!!");
                println!("Remaining tokens:");
                for i in parser.pos..tokens.len().min(parser.pos + 10) {
                    println!("{:3}: {:20} {:?}", i, tokens[i].token_type, tokens[i].raw);
                }
            }
        }
        Err(e) => {
            println!("\n=== PARSE ERROR ===");
            println!("{:?}", e);
        }
    }

    assert!(ast.is_ok(), "Parse error: {:?}", ast.err());
    assert!(
        parser.pos >= tokens.len() - 1,
        "Parser did not consume all tokens. Stopped at {} / {} tokens (last index: {})",
        parser.pos,
        tokens.len(),
        tokens.len() - 1
    );
}

#[test]
fn test_select_from_debug() {
    env_logger::try_init().ok();

    let sql = r#"SELECT amount_of_honey FROM bear_inventory;"#;

    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, lex_errors) = lexer.lex(input, false);

    println!("\n=== Total tokens: {} ===", tokens.len());
    for (i, tok) in tokens.iter().enumerate() {
        if tok.is_code() {
            println!("{:3}: {:20} {:?}", i, tok.token_type, tok.raw);
        }
    }

    let dialect = Dialect::Ansi;
    let mut parser = Parser::new(&tokens, dialect);
    let ast = parser.call_rule_as_root();

    match &ast {
        Ok(node) => {
            println!("\n=== AST ===");
            println!("{:#?}", node);

            println!("\n=== YAML ===");
            let as_record = node.as_record(true, true, false);
            let yaml_str = serde_yaml_ng::to_string(&as_record).unwrap();
            println!("{}", yaml_str);

            println!(
                "\n=== Parser position: {} / {} ===",
                parser.pos,
                tokens.len()
            );

            if parser.pos < tokens.len() {
                println!("\n!!! WARNING: Parser did not consume all tokens !!!");
                println!("Remaining tokens:");
                for i in parser.pos..tokens.len().min(parser.pos + 10) {
                    println!("{:3}: {:20} {:?}", i, tokens[i].token_type, tokens[i].raw);
                }
            }
        }
        Err(e) => {
            println!("\n=== PARSE ERROR ===");
            println!("{:?}", e);
        }
    }

    assert!(ast.is_ok(), "Parse error: {:?}", ast.err());
    assert!(
        parser.pos >= tokens.len() - 1,
        "Parser did not consume all tokens. Stopped at {} / {} tokens (last index: {})",
        parser.pos,
        tokens.len(),
        tokens.len() - 1
    );
}

fn run_sql_debug(sql: &str, dialect: Dialect) {
    env_logger::try_init().ok();

    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, _lex_errors) = lexer.lex(input, false);

    println!("\n=== Total tokens: {} ===", tokens.len());
    for (i, tok) in tokens.iter().enumerate() {
        println!("{:3}: {:20} {:?}", i, tok.token_type, tok.raw);
    }

    let mut parser = Parser::new(&tokens, dialect);
    let ast = parser.call_rule_as_root();

    match &ast {
        Ok(node) => {
            println!("\n=== AST ===");
            println!("{:#?}", node);

            println!("\n=== YAML ===");
            let as_record = node.as_record(true, true, false);
            let yaml_str = serde_yaml_ng::to_string(&as_record).unwrap();
            println!("{}", yaml_str);

            println!(
                "\n=== Parser position: {} / {} ===",
                parser.pos,
                tokens.len()
            );

            if parser.pos < tokens.len() {
                println!("\n!!! WARNING: Parser did not consume all tokens !!!");
                println!("Remaining tokens:");
                for i in parser.pos..tokens.len().min(parser.pos + 10) {
                    println!("{:3}: {:20} {:?}", i, tokens[i].token_type, tokens[i].raw);
                }
            }
        }
        Err(e) => {
            println!("\n=== PARSE ERROR ===");
            println!("{:?}", e);
        }
    }

    assert!(ast.is_ok(), "Parse error: {:?}", ast.err());
    assert!(
        parser.pos >= tokens.len() - 1,
        "Parser did not consume all tokens. Stopped at {} / {} tokens (last index: {})",
        parser.pos,
        tokens.len(),
        tokens.len() - 1
    );
}

#[test]
fn test_select_b_context_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/ansi/select_b.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Ansi;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_bigquery_alter_table_add_column_context_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/bigquery/alter_table_add_column.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Bigquery;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_bigquery_assert_context_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/bigquery/assert.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Bigquery;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_ansi_functions_a_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/ansi/functions_a.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Ansi;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_ansi_select_j_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/ansi/select_j.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Ansi;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_bigquery_select_extract_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/bigquery/select_extract.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Bigquery;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_bigquery_dateparts_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/bigquery/dateparts.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Bigquery;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_ansi_create_trigger_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/ansi/create_trigger.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Ansi;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_ansi_select_except_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/ansi/select_except.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Ansi;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_ansi_trim_functions_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/ansi/trim_functions.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Ansi;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_ansi_trim_3stmts_debug() {
    let sql = r#"SELECT trim('a');

SELECT trim(BOTH FROM 'b');

SELECT trim(LEADING FROM 'c');
"#;
    let dialect = Dialect::Ansi;
    run_sql_debug(sql, dialect);
}

#[test]
fn test_ansi_select_many_join_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/ansi/select_many_join.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Ansi;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_ansi_merge_into_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/ansi/merge_into.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Ansi;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_bigquery_select_pivot_simple_debug() {
    let sql = r#"SELECT * FROM t PIVOT(SUM(a) FOR b IN ('x'))"#;
    let dialect = Dialect::Bigquery;
    run_sql_debug(sql, dialect);
}

#[test]
fn test_db2_create_index_simple_debug() {
    let sql = r#"CREATE UNIQUE INDEX SESSION.FOO_IDX ON SESSION.FOO(column1)
COMPRESS YES
ALLOW REVERSE SCANS;"#;
    let dialect = Dialect::Db2;
    run_sql_debug(sql, dialect);
}

#[test]
fn test_oracle_temporary_table_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/oracle/temporary_table.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Oracle;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_oracle_case_expressions_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/oracle/case_expressions.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Oracle;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_nested_case_simple_debug() {
    // Test 3: Searched CASE expression with nested CASE - the simplest nested case
    let sql = r#"SELECT
    CASE
        WHEN x = 5 THEN
            CASE
                WHEN y = 6 THEN 999
            END
    END AS hi
FROM abc;"#;
    let dialect = Dialect::Ansi;
    run_sql_debug(sql, dialect);
}

#[test]
fn test_three_statements_debug() {
    // Test multiple statements separated properly
    let sql = r#"-- Test 1
SELECT 1;

-- Test 2
SELECT 2;

-- Test 3
SELECT 3;
"#;
    let dialect = Dialect::Ansi;
    run_sql_debug(sql, dialect);
}

#[test]
fn test_oracle_three_case_debug() {
    // Test 1, 2, 3 from oracle case_expressions.sql
    let sql = r#"-- Test 1: Simple CASE expression (CASE WHEN)
SELECT
    CASE
        WHEN x = 5 THEN 1
        WHEN x = 10 THEN 2
        ELSE 0
    END AS result
FROM abc;

-- Test 2: Simple CASE expression without ELSE
SELECT
    CASE
        WHEN x = 5 THEN 1
        WHEN x = 10 THEN 2
    END AS result
FROM abc;

-- Test 3: Searched CASE expression with nested CASE
SELECT
    CASE
        WHEN x = 5 THEN
            CASE
                WHEN y = 6 THEN 999
            END
    END AS hi
FROM abc;
"#;
    let dialect = Dialect::Oracle;
    run_sql_debug(sql, dialect);
}

#[test]
fn test_oracle_nested_case_alone_debug() {
    // Test 3 alone with Oracle
    let sql = r#"SELECT
    CASE
        WHEN x = 5 THEN
            CASE
                WHEN y = 6 THEN 999
            END
    END AS hi
FROM abc;
"#;
    let dialect = Dialect::Oracle;
    run_sql_debug(sql, dialect);
}

#[test]
fn test_oracle_simple_case_debug() {
    // Simple Oracle CASE
    let sql = r#"SELECT CASE WHEN x = 5 THEN 1 END FROM abc;"#;
    let dialect = Dialect::Oracle;
    run_sql_debug(sql, dialect);
}

#[test]
fn test_oracle_nested_case_inline_debug() {
    // Nested Oracle CASE on one line
    let sql = r#"SELECT CASE WHEN x = 5 THEN CASE WHEN y = 6 THEN 999 END END AS hi FROM abc;"#;
    let dialect = Dialect::Oracle;
    run_sql_debug(sql, dialect);
}

#[test]
fn test_ansi_nested_case_inline_debug() {
    // Nested ANSI CASE on one line (should work)
    let sql = r#"SELECT CASE WHEN x = 5 THEN CASE WHEN y = 6 THEN 999 END END AS hi FROM abc;"#;
    let dialect = Dialect::Ansi;
    run_sql_debug(sql, dialect);
}

#[test]
fn test_postgres_alter_publication_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/postgres/alter_publication.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Postgres;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_postgres_drop_aggregate_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/postgres/drop_aggregate.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Postgres;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_mysql_insert_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/mysql/insert.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Mysql;
    run_sql_debug(&sql, dialect);
}

#[test]
fn test_bigquery_select_pivot_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/bigquery/select_pivot.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    println!("Running test for {}", path);
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    let dialect = Dialect::Bigquery;
    run_sql_debug(&sql, dialect);
}
