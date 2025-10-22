use criterion::{criterion_group, criterion_main, Criterion};

use std::str::FromStr;

use sqlfluffrs::lexer::Lexer;
use sqlfluffrs::parser::{Grammar, Node, ParseMode, Parser};
use sqlfluffrs::Dialect;

fn bench_parse_simple_select(c: &mut Criterion) {
    let sql = "SELECT a, b FROM foo WHERE c = 1";
    use sqlfluffrs::lexer::{LexInput, Lexer};
    use sqlfluffrs::Dialect;
    let input = LexInput::String(sql.to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
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
    use sqlfluffrs::lexer::{LexInput, Lexer};
    use sqlfluffrs::Dialect;
    let input = LexInput::String(sql.to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
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
    use sqlfluffrs::lexer::{LexInput, Lexer};
    use sqlfluffrs::Dialect;
    let input = LexInput::String(sql.to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
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
    use sqlfluffrs::lexer::{LexInput, Lexer};
    use sqlfluffrs::Dialect;
    let input = LexInput::String(sql.to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
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
    use sqlfluffrs::lexer::{LexInput, Lexer};
    use sqlfluffrs::Dialect;
    let input = LexInput::String(sql.to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);
    c.bench_function("parse_complex_joins", |b| {
        b.iter(|| {
            let mut parser = Parser::new(&tokens, dialect);
            let _ast = parser.call_rule_as_root().expect("Parse failed");
        });
    });
}

// Add more benchmarks as needed for specific grammar constructs, dialects, or edge cases.

criterion_group!(
    parser_benches,
    bench_parse_simple_select,
    bench_parse_nested_functions,
    bench_parse_long_query,
    bench_parse_many_columns,
    bench_parse_complex_joins,
);

criterion_main!(parser_benches);
