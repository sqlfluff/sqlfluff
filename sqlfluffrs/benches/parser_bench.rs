use criterion::{criterion_group, criterion_main, Criterion};

use sqlfluffrs_parser::parser::Parser;
use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};

fn bench_parse_simple_select(c: &mut Criterion) {
    let sql = "SELECT a, b FROM foo WHERE c = 1";
    let input = LexInput::String(sql.to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    c.bench_function("parse_simple_select", |b| {
        b.iter(|| {
            let mut parser = Parser::new(&tokens, dialect);
            let _ast = parser.call_rule_as_root().expect("Parse failed");
        });
    });
}

fn bench_parse_nested_functions(c: &mut Criterion) {
    let sql = "SELECT CONCAT(UPPER(name), LOWER(SUBSTRING(description, 1, 10))) FROM users";
    let input = LexInput::String(sql.to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    c.bench_function("parse_nested_functions", |b| {
        b.iter(|| {
            let mut parser = Parser::new(&tokens, dialect);
            let _ast = parser.call_rule_as_root().expect("Parse failed");
        });
    });
}

fn bench_parse_long_query(c: &mut Criterion) {
    let sql = "SELECT * FROM foo WHERE bar IN (SELECT baz FROM qux WHERE quux > 10)";
    let input = LexInput::String(sql.to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    c.bench_function("parse_long_query", |b| {
        b.iter(|| {
            let mut parser = Parser::new(&tokens, dialect);
            let _ast = parser.call_rule_as_root().expect("Parse failed");
        });
    });
}

fn bench_parse_many_columns(c: &mut Criterion) {
    let sql = "SELECT col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 FROM big_table";
    let input = LexInput::String(sql.to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    c.bench_function("parse_many_columns", |b| {
        b.iter(|| {
            let mut parser = Parser::new(&tokens, dialect);
            let _ast = parser.call_rule_as_root().expect("Parse failed");
        });
    });
}

fn bench_parse_complex_joins(c: &mut Criterion) {
    let sql = "SELECT a FROM t1 JOIN t2 ON t1.id = t2.id LEFT JOIN t3 ON t2.ref = t3.ref";
    let input = LexInput::String(sql.to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    c.bench_function("parse_complex_joins", |b| {
        b.iter(|| {
            let mut parser = Parser::new(&tokens, dialect);
            let _ast = parser.call_rule_as_root().expect("Parse failed");
        });
    });
}

// Add more benchmarks as needed for specific grammar constructs, dialects, or edge cases.

use std::fs;
use std::path::Path;


// Helper to get fixture path relative to sqlfluffrs/ directory
fn fixture_path(filename: &str) -> std::path::PathBuf {
    let mut path = std::path::PathBuf::from("../test/fixtures/dialects/ansi/");
    path.push(filename);
    path
}

fn bench_expression_recursion(c: &mut Criterion) {
    let path = fixture_path("expression_recursion.sql");
    let sql = fs::read_to_string(&path).expect(&format!("Failed to read {}", path.display()));
    let input = LexInput::String(sql);
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    c.bench_function("parse_expression_recursion", |b| {
        b.iter(|| {
            let mut parser = Parser::new(&tokens, dialect);
            let _ast = parser.call_rule_as_root().expect("Parse failed");
        });
    });
}

fn bench_expression_recursion_2(c: &mut Criterion) {
    let path = fixture_path("expression_recursion_2.sql");
    let sql = fs::read_to_string(&path).expect(&format!("Failed to read {}", path.display()));
    let input = LexInput::String(sql);
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    c.bench_function("parse_expression_recursion_2", |b| {
        b.iter(|| {
            let mut parser = Parser::new(&tokens, dialect);
            let _ast = parser.call_rule_as_root().expect("Parse failed");
        });
    });
}

criterion_group!(
    parser_benches,
    bench_parse_simple_select,
    bench_parse_nested_functions,
    bench_parse_long_query,
    bench_parse_many_columns,
    bench_parse_complex_joins,
    bench_expression_recursion,
    bench_expression_recursion_2,
);

criterion_main!(parser_benches);
