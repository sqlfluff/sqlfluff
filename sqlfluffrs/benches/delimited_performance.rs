/// Benchmark to measure performance impact of terminator timing in Delimited grammar
///
/// This benchmark compares parse times for queries with varying lengths of delimited lists
/// to quantify the actual performance impact of Rust's post-check terminator approach.
use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion};
use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;
use std::hint::black_box;

fn generate_select_with_n_columns(n: usize) -> String {
    let columns: Vec<String> = (1..=n).map(|i| format!("col{}", i)).collect();
    format!("SELECT {} FROM table", columns.join(", "))
}

fn parse_query(sql: &str) {
    let input = LexInput::String(sql.to_string());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);
    let _ = parser.call_rule_as_root();
}

fn bench_delimited_lists(c: &mut Criterion) {
    let mut group = c.benchmark_group("delimited_column_lists");

    // Benchmark with varying number of columns
    for n in [5, 10, 20, 50, 100, 200].iter() {
        let sql = generate_select_with_n_columns(*n);

        group.bench_with_input(BenchmarkId::from_parameter(n), &sql, |b, sql| {
            b.iter(|| parse_query(black_box(sql)));
        });
    }

    group.finish();
}

fn bench_complex_expressions(c: &mut Criterion) {
    let mut group = c.benchmark_group("delimited_with_expressions");

    // Simple identifiers
    let simple = "SELECT a, b, c, d, e FROM table";
    group.bench_function("simple_identifiers", |b| {
        b.iter(|| parse_query(black_box(simple)));
    });

    // Complex expressions
    let complex = "SELECT a + 1, b * 2, c / 3, d - 4, e % 5 FROM table";
    group.bench_function("arithmetic_expressions", |b| {
        b.iter(|| parse_query(black_box(complex)));
    });

    // Function calls
    let functions = "SELECT MAX(a), MIN(b), AVG(c), COUNT(d), SUM(e) FROM table";
    group.bench_function("function_calls", |b| {
        b.iter(|| parse_query(black_box(functions)));
    });

    // Nested expressions
    let nested = "SELECT (a + b) * c, (d - e) / f, (g * h) + i FROM table";
    group.bench_function("nested_expressions", |b| {
        b.iter(|| parse_query(black_box(nested)));
    });

    group.finish();
}

fn bench_long_where_clauses(c: &mut Criterion) {
    let mut group = c.benchmark_group("delimited_where_conditions");

    // Multiple conditions (AND is like a delimited list of conditions)
    let conditions_5 = "SELECT * FROM table WHERE a = 1 AND b = 2 AND c = 3 AND d = 4 AND e = 5";
    group.bench_function("5_conditions", |b| {
        b.iter(|| parse_query(black_box(conditions_5)));
    });

    let conditions_10 = "SELECT * FROM table WHERE a = 1 AND b = 2 AND c = 3 AND d = 4 AND e = 5 AND f = 6 AND g = 7 AND h = 8 AND i = 9 AND j = 10";
    group.bench_function("10_conditions", |b| {
        b.iter(|| parse_query(black_box(conditions_10)));
    });

    group.finish();
}

criterion_group!(
    benches,
    bench_delimited_lists,
    bench_complex_expressions,
    bench_long_where_clauses
);
criterion_main!(benches);
