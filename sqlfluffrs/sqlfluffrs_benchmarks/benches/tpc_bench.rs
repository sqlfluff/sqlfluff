/// TPC-H and TPC-DS lex and parse benchmarks.
///
/// Query fixtures are downloaded at build time (not committed); see this
/// crate's README. For lex benchmarks, SQL strings are loaded once outside the
/// timed loop and lexed inside it. For parse benchmarks, tokens are produced
/// once outside the timed loop so only parse time is measured. Two parse
/// paths are covered:
///   * `parse_*` — `call_rule_as_root()`, the hybrid path returning a
///     `MatchResult` (Python builds the AST downstream).
///   * `native_ast_*` — `root_parse()`, the native path that also
///     materialises the Rust `Node` AST.
///
/// Run all TPC benchmarks (the `fetch` feature downloads the fixtures):
///   cargo bench -p sqlfluffrs_benchmarks --features fetch
///
/// Run only TPC-H:
///   cargo bench -p sqlfluffrs_benchmarks --features fetch -- tpch
///
/// Run only the native AST path:
///   cargo bench -p sqlfluffrs_benchmarks --features fetch -- native_ast
use criterion::{criterion_group, criterion_main, Criterion};

use sqlfluffrs_benchmarks::{tpc_fixture, TPCDS_N, TPCH_N};
use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;
use sqlfluffrs_types::Token;
use std::fs;
use std::path::Path;
use std::time::Duration;

fn read_file(path: &Path) -> String {
    fs::read_to_string(path).unwrap_or_else(|e| panic!("Failed to read {}: {}", path.display(), e))
}

fn lex_sql(sql: &str) -> Vec<Token> {
    let (tokens, _) =
        Lexer::new(None, ANSI_LEXERS.to_vec()).lex(LexInput::String(sql.to_owned()), false);
    tokens
}

fn parse_tokens(tokens: &[Token]) {
    let mut parser = Parser::new(
        std::hint::black_box(tokens),
        Dialect::Ansi,
        hashbrown::HashMap::new(),
    );
    std::hint::black_box(parser.call_rule_as_root().expect("Parse failed"));
}

fn parse_native_ast(tokens: &[Token]) {
    let mut parser = Parser::new(
        std::hint::black_box(tokens),
        Dialect::Ansi,
        hashbrown::HashMap::new(),
    );
    std::hint::black_box(parser.root_parse().expect("Parse failed"));
}

fn bench_tpch_lex(c: &mut Criterion) {
    let sqls: Vec<String> = (1..=TPCH_N)
        .map(|n| read_file(&tpc_fixture("tpc-h", n)))
        .collect();

    let mut group = c.benchmark_group("tpch");
    group.sample_size(30).warm_up_time(Duration::from_secs(3));
    group.bench_function("lex_tpch_22", |b| {
        b.iter(|| {
            for sql in &sqls {
                std::hint::black_box(lex_sql(sql));
            }
        })
    });
    group.finish();
}

fn bench_tpch_parse(c: &mut Criterion) {
    let token_sets: Vec<Vec<Token>> = (1..=TPCH_N)
        .map(|n| lex_sql(&read_file(&tpc_fixture("tpc-h", n))))
        .collect();

    let mut group = c.benchmark_group("tpch");
    group.sample_size(30).warm_up_time(Duration::from_secs(3));
    group.bench_function("parse_tpch_22", |b| {
        b.iter(|| {
            for tokens in &token_sets {
                parse_tokens(tokens);
            }
        })
    });
    group.finish();
}

fn bench_tpch_native_ast(c: &mut Criterion) {
    let token_sets: Vec<Vec<Token>> = (1..=TPCH_N)
        .map(|n| lex_sql(&read_file(&tpc_fixture("tpc-h", n))))
        .collect();

    let mut group = c.benchmark_group("tpch");
    group.sample_size(30).warm_up_time(Duration::from_secs(3));
    group.bench_function("native_ast_tpch_22", |b| {
        b.iter(|| {
            for tokens in &token_sets {
                parse_native_ast(tokens);
            }
        })
    });
    group.finish();
}

fn bench_tpcds_lex(c: &mut Criterion) {
    let sqls: Vec<String> = (1..=TPCDS_N)
        .map(|n| read_file(&tpc_fixture("tpc-ds", n)))
        .collect();

    let mut group = c.benchmark_group("tpcds");
    group.sample_size(30).warm_up_time(Duration::from_secs(3));
    group.bench_function("lex_tpcds_99", |b| {
        b.iter(|| {
            for sql in &sqls {
                std::hint::black_box(lex_sql(sql));
            }
        })
    });
    group.finish();
}

fn bench_tpcds_parse(c: &mut Criterion) {
    let token_sets: Vec<Vec<Token>> = (1..=TPCDS_N)
        .map(|n| lex_sql(&read_file(&tpc_fixture("tpc-ds", n))))
        .collect();

    let mut group = c.benchmark_group("tpcds");
    group.sample_size(30).warm_up_time(Duration::from_secs(3));
    group.bench_function("parse_tpcds_99", |b| {
        b.iter(|| {
            for tokens in &token_sets {
                parse_tokens(tokens);
            }
        })
    });
    group.finish();
}

fn bench_tpcds_native_ast(c: &mut Criterion) {
    let token_sets: Vec<Vec<Token>> = (1..=TPCDS_N)
        .map(|n| lex_sql(&read_file(&tpc_fixture("tpc-ds", n))))
        .collect();

    let mut group = c.benchmark_group("tpcds");
    group.sample_size(30).warm_up_time(Duration::from_secs(3));
    group.bench_function("native_ast_tpcds_99", |b| {
        b.iter(|| {
            for tokens in &token_sets {
                parse_native_ast(tokens);
            }
        })
    });
    group.finish();
}

criterion_group!(
    tpch_benches,
    bench_tpch_lex,
    bench_tpch_parse,
    bench_tpch_native_ast
);
criterion_group!(
    tpcds_benches,
    bench_tpcds_lex,
    bench_tpcds_parse,
    bench_tpcds_native_ast
);
criterion_main!(tpch_benches, tpcds_benches);
