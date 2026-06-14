/// TPC-H and TPC-DS lex and parse benchmarks.
///
/// Files live at test/fixtures/tpc/ under tpc-h/ and tpc-ds/.
/// For lex benchmarks, SQL strings are loaded once outside the timed loop and
/// lexed inside it. For parse benchmarks, tokens are produced once outside the
/// timed loop so only parse time is measured.
///
/// Run all TPC benchmarks:
///   cargo bench --bench tpc_bench --manifest-path sqlfluffrs/Cargo.toml
///
/// Run only TPC-H:
///   cargo bench --bench tpc_bench --manifest-path sqlfluffrs/Cargo.toml -- tpch
use criterion::{criterion_group, criterion_main, Criterion};

use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;
use sqlfluffrs_types::Token;
use std::fs;
use std::path::{Path, PathBuf};
use std::time::Duration;

const TPCH_N: u32 = 22;
const TPCDS_N: u32 = 99;

fn tpc_fixture(sub_dir: &str, n: u32) -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .expect("CARGO_MANIFEST_DIR has no parent")
        .join(format!("test/fixtures/tpc/{sub_dir}/{n}.sql"))
}

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

criterion_group!(tpch_benches, bench_tpch_lex, bench_tpch_parse);
criterion_group!(tpcds_benches, bench_tpcds_lex, bench_tpcds_parse);
criterion_main!(tpch_benches, tpcds_benches);
