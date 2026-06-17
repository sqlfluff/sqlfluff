//! Build script for the TPC benchmark crate.
//!
//! The TPC-H / TPC-DS query fixtures are intentionally NOT committed to this
//! repository. Instead they are fetched at build time from the Apache Doris
//! project at a pinned commit and cached under `OUT_DIR/tpc`. The fixtures path
//! is exported to the crate as the `TPC_FIXTURES_DIR` env var (via
//! `cargo:rustc-env`), so benches and examples can locate them with
//! `env!("TPC_FIXTURES_DIR")`.
//!
//! Fetching only happens when the `fetch` feature is enabled. A normal
//! `cargo build --workspace` (and CI) leaves it off, so those builds never
//! touch the network; the bench/example then fail fast at runtime with a clear
//! message if the fixtures are absent.

use std::fs;
use std::path::{Path, PathBuf};

/// Apache Doris commit the fixtures are pinned to. See README.md for provenance.
const DORIS_SHA: &str = "3a2d9d55f1e8e2d74187179ef89c36c8562815fd";
const RAW_BASE: &str = "https://raw.githubusercontent.com/apache/doris";

const TPCH_N: u32 = 22;
const TPCDS_N: u32 = 99;

/// TPC-DS queries that the TPC-DS spec defines as two independent statements.
/// Doris stores them as `query{n}.sql` + `query{n}_1.sql`; we consolidate each
/// pair into a single `{n}.sql`, statements separated by a blank line.
const TPCDS_SPLIT: [u32; 4] = [14, 23, 24, 39];

fn main() {
    println!("cargo:rerun-if-changed=build.rs");

    let out_dir = PathBuf::from(std::env::var("OUT_DIR").expect("OUT_DIR not set"));
    let fixtures_dir = out_dir.join("tpc");

    // Always export the location so the crate compiles whether or not fixtures
    // have been fetched.
    println!(
        "cargo:rustc-env=TPC_FIXTURES_DIR={}",
        fixtures_dir.display()
    );

    // Only hit the network when explicitly asked to.
    if std::env::var_os("CARGO_FEATURE_FETCH").is_none() {
        return;
    }

    if let Err(e) = fetch_fixtures(&fixtures_dir) {
        panic!("Failed to download TPC benchmark fixtures: {e}");
    }
}

fn fetch_fixtures(fixtures_dir: &Path) -> Result<(), String> {
    // Skip if a previous run already populated the cache for this exact commit.
    let marker = fixtures_dir.join(".doris-sha");
    if fs::read_to_string(&marker)
        .map(|s| s.trim() == DORIS_SHA)
        .unwrap_or(false)
    {
        return Ok(());
    }

    let tpch_dir = fixtures_dir.join("tpc-h");
    let tpcds_dir = fixtures_dir.join("tpc-ds");
    fs::create_dir_all(&tpch_dir).map_err(|e| e.to_string())?;
    fs::create_dir_all(&tpcds_dir).map_err(|e| e.to_string())?;

    // TPC-H: tools/tpch-tools/queries/q{n}.sql
    for n in 1..=TPCH_N {
        let url = format!("{RAW_BASE}/{DORIS_SHA}/tools/tpch-tools/queries/q{n}.sql");
        let sql = normalize(&download(&url)?);
        write(&tpch_dir.join(format!("{n}.sql")), &sql)?;
    }

    // TPC-DS: tools/tpcds-tools/queries/sf1/query{n}.sql, consolidating split
    // queries into a single statement file.
    for n in 1..=TPCDS_N {
        let url = format!("{RAW_BASE}/{DORIS_SHA}/tools/tpcds-tools/queries/sf1/query{n}.sql");
        let mut sql = normalize(&download(&url)?);
        if TPCDS_SPLIT.contains(&n) {
            let url2 =
                format!("{RAW_BASE}/{DORIS_SHA}/tools/tpcds-tools/queries/sf1/query{n}_1.sql");
            let part2 = normalize(&download(&url2)?);
            sql = format!("{sql}\n{part2}");
        }
        write(&tpcds_dir.join(format!("{n}.sql")), &sql)?;
    }

    // Write the marker last so an interrupted fetch is retried next time.
    write(&marker, &format!("{DORIS_SHA}\n"))?;
    Ok(())
}

fn download(url: &str) -> Result<String, String> {
    ureq::get(url)
        .call()
        .map_err(|e| format!("GET {url}: {e}"))?
        .body_mut()
        .read_to_string()
        .map_err(|e| format!("reading {url}: {e}"))
}

/// Normalize to Unix line endings, strip per-line trailing whitespace, and end
/// with a single newline. Mirrors how the fixtures were prepared previously and
/// keeps lexer inputs stable across platforms.
fn normalize(raw: &str) -> String {
    let mut out = String::with_capacity(raw.len());
    for line in raw.replace("\r\n", "\n").replace('\r', "\n").lines() {
        out.push_str(line.trim_end());
        out.push('\n');
    }
    out
}

fn write(path: &Path, contents: &str) -> Result<(), String> {
    fs::write(path, contents).map_err(|e| format!("writing {}: {}", path.display(), e))
}
