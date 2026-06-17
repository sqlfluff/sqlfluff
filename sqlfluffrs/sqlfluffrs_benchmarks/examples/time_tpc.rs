/// time_tpc: timing and parser-stats harness for TPC-H and TPC-DS benchmarks.
///
/// Query fixtures are downloaded at build time (not committed); run with the
/// `fetch` feature so they are available:
///   cargo run -p sqlfluffrs_benchmarks --example time_tpc --features fetch
///
/// Lexing is done once outside the timed loop. Each timed run creates a fresh
/// Parser. One warm-up pass primes L3 cache and the branch predictor before
/// the five measured runs begin.
///
/// Prints a per-query table for TPC-H and TPC-DS, then full-suite summaries.
use std::fs;
use std::path::Path;
use std::time::{Duration, Instant};

use sqlfluffrs_benchmarks::{tpc_fixture, TPCDS_N, TPCH_N};
use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;
use sqlfluffrs_types::Token;

const N_WARMUP: usize = 1;
const N_TIMED: usize = 5;

struct RunStats {
    duration_secs: f64,
    cache_hits: usize,
    cache_misses: usize,
    cache_entries: usize,
    pruning_calls: usize,
    pruning_total: usize,
    pruning_kept: usize,
    match_attempts: usize,
    match_successes: usize,
    complete_match_early_exits: usize,
    terminator_checks: usize,
    terminator_hits: usize,
}

impl RunStats {
    fn capture(duration: Duration, parser: &Parser) -> Self {
        let (hits, misses, _) = parser.table_cache.stats();
        RunStats {
            duration_secs: duration.as_secs_f64(),
            cache_hits: hits,
            cache_misses: misses,
            cache_entries: parser.table_cache.len(),
            pruning_calls: parser.pruning_calls.get(),
            pruning_total: parser.pruning_total.get(),
            pruning_kept: parser.pruning_kept.get(),
            match_attempts: parser.match_attempts.get(),
            match_successes: parser.match_successes.get(),
            complete_match_early_exits: parser.complete_match_early_exits.get(),
            terminator_checks: parser.terminator_checks.get(),
            terminator_hits: parser.terminator_hits.get(),
        }
    }
}

struct Avg {
    mean: f64,
    min: f64,
    max: f64,
    stddev: f64,
    cache_hit_rate_pct: f64,
    cache_entries: f64,
    pruning_calls: f64,
    pruned_pct: f64,
    match_attempts: f64,
    match_success_pct: f64,
    early_exits: f64,
    term_checks: f64,
    term_hit_pct: f64,
}

fn avg(runs: &[RunStats]) -> Avg {
    let n = runs.len() as f64;
    let mean = runs.iter().map(|r| r.duration_secs).sum::<f64>() / n;
    let variance = runs
        .iter()
        .map(|r| (r.duration_secs - mean).powi(2))
        .sum::<f64>()
        / n;
    let stat = |f: fn(&RunStats) -> usize| runs.iter().map(|r| f(r)).sum::<usize>() as f64 / n;
    let hits = stat(|r| r.cache_hits);
    let misses = stat(|r| r.cache_misses);
    let kept = stat(|r| r.pruning_kept);
    let total_opts = stat(|r| r.pruning_total);
    let attempts = stat(|r| r.match_attempts);
    let successes = stat(|r| r.match_successes);
    let t_checks = stat(|r| r.terminator_checks);
    let t_hits = stat(|r| r.terminator_hits);
    Avg {
        mean,
        min: runs
            .iter()
            .map(|r| r.duration_secs)
            .fold(f64::INFINITY, f64::min),
        max: runs
            .iter()
            .map(|r| r.duration_secs)
            .fold(f64::NEG_INFINITY, f64::max),
        stddev: variance.sqrt(),
        cache_hit_rate_pct: hits / (hits + misses).max(1.0) * 100.0,
        cache_entries: stat(|r| r.cache_entries),
        pruning_calls: stat(|r| r.pruning_calls),
        pruned_pct: if total_opts > 0.0 {
            (1.0 - kept / total_opts) * 100.0
        } else {
            0.0
        },
        match_attempts: attempts,
        match_success_pct: successes / attempts.max(1.0) * 100.0,
        early_exits: stat(|r| r.complete_match_early_exits),
        term_checks: t_checks,
        term_hit_pct: if t_checks > 0.0 {
            t_hits / t_checks * 100.0
        } else {
            0.0
        },
    }
}

fn print_avg(label: &str, a: &Avg) {
    println!("  {label}");
    println!(
        "    Time          {:.1}ms  (min {:.1}  max {:.1}  stddev {:.1}ms)",
        a.mean * 1000.0,
        a.min * 1000.0,
        a.max * 1000.0,
        a.stddev * 1000.0,
    );
    println!(
        "    Cache         {:.1}% hit  ({:.0} entries)",
        a.cache_hit_rate_pct, a.cache_entries,
    );
    println!(
        "    Pruning       {:.0} calls  {:.1}% pruned",
        a.pruning_calls, a.pruned_pct,
    );
    println!(
        "    Matches       {:.0} attempts  {:.1}% success  {:.0} early-exits",
        a.match_attempts, a.match_success_pct, a.early_exits,
    );
    println!(
        "    Terminators   {:.0} checks  {:.1}% hit",
        a.term_checks, a.term_hit_pct,
    );
}

fn lex(path: &Path) -> (Vec<Token>, usize) {
    let sql = fs::read_to_string(path)
        .unwrap_or_else(|e| panic!("Failed to read {}: {}", path.display(), e));
    let bytes = sql.len();
    let (tokens, _) = Lexer::new(None, ANSI_LEXERS.to_vec()).lex(LexInput::String(sql), false);
    (tokens, bytes)
}

fn timed_runs(tokens: &[Token]) -> Vec<RunStats> {
    for _ in 0..N_WARMUP {
        let mut p = Parser::new(tokens, Dialect::Ansi, hashbrown::HashMap::new());
        std::hint::black_box(p.call_rule_as_root().expect("Parse failed"));
    }
    (0..N_TIMED)
        .map(|_| {
            let t0 = Instant::now();
            let mut p = Parser::new(tokens, Dialect::Ansi, hashbrown::HashMap::new());
            p.call_rule_as_root().expect("Parse failed");
            RunStats::capture(t0.elapsed(), &p)
        })
        .collect()
}

fn timed_suite_runs(all_tokens: &[Vec<Token>]) -> Vec<RunStats> {
    for _ in 0..N_WARMUP {
        for tokens in all_tokens {
            let mut p = Parser::new(tokens, Dialect::Ansi, hashbrown::HashMap::new());
            std::hint::black_box(p.call_rule_as_root().expect("Parse failed"));
        }
    }
    (0..N_TIMED)
        .map(|_| {
            let t0 = Instant::now();
            let mut cache_hits = 0;
            let mut cache_misses = 0;
            let mut cache_entries = 0;
            let mut pruning_calls = 0;
            let mut pruning_total = 0;
            let mut pruning_kept = 0;
            let mut match_attempts = 0;
            let mut match_successes = 0;
            let mut early_exits = 0;
            let mut term_checks = 0;
            let mut term_hits = 0;
            for tokens in all_tokens {
                let mut p = Parser::new(tokens, Dialect::Ansi, hashbrown::HashMap::new());
                p.call_rule_as_root().expect("Parse failed");
                let (h, m, _) = p.table_cache.stats();
                cache_hits += h;
                cache_misses += m;
                cache_entries += p.table_cache.len();
                pruning_calls += p.pruning_calls.get();
                pruning_total += p.pruning_total.get();
                pruning_kept += p.pruning_kept.get();
                match_attempts += p.match_attempts.get();
                match_successes += p.match_successes.get();
                early_exits += p.complete_match_early_exits.get();
                term_checks += p.terminator_checks.get();
                term_hits += p.terminator_hits.get();
            }
            RunStats {
                duration_secs: t0.elapsed().as_secs_f64(),
                cache_hits,
                cache_misses,
                cache_entries,
                pruning_calls,
                pruning_total,
                pruning_kept,
                match_attempts,
                match_successes,
                complete_match_early_exits: early_exits,
                terminator_checks: term_checks,
                terminator_hits: term_hits,
            }
        })
        .collect()
}

fn print_query_table_header() {
    println!(
        "  {:<8} {:>8} {:>8} {:>10} {:>10} {:>10} {:>10}",
        "Query", "Bytes", "Tokens", "Mean(ms)", "Cache%", "Pruned%", "TermChk%"
    );
    println!("  {}", "-".repeat(72));
}

fn run_suite(name: &str, count: u32, sub_dir: &str) {
    println!("=== {name}: Per-Query ===");
    println!();
    print_query_table_header();

    let mut suite_tokens: Vec<Vec<Token>> = Vec::new();
    for n in 1..=count {
        let path = tpc_fixture(sub_dir, n);
        let (tokens, bytes) = lex(&path);
        let tok_count = tokens.len();
        let runs = timed_runs(&tokens);
        let a = avg(&runs);
        println!(
            "  Q{:<7} {:>8} {:>8} {:>10.2} {:>9.1}% {:>9.1}% {:>9.1}%",
            n,
            bytes,
            tok_count,
            a.mean * 1000.0,
            a.cache_hit_rate_pct,
            a.pruned_pct,
            a.term_hit_pct,
        );
        suite_tokens.push(tokens);
    }

    println!();
    println!("=== {name}: Full Suite ({count} queries) ===");
    let suite_avg = avg(&timed_suite_runs(&suite_tokens));
    print_avg("suite pass", &suite_avg);
}

fn main() {
    println!("TPC-H and TPC-DS Parser Baseline");
    println!("Warm-up runs: {N_WARMUP}  |  Timed runs: {N_TIMED}");
    println!("Dialect: ANSI");
    println!();

    run_suite("TPC-H", TPCH_N, "tpc-h");
    println!();
    run_suite("TPC-DS", TPCDS_N, "tpc-ds");
}
