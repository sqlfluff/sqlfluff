//! Shared helpers for the TPC-H / TPC-DS lex and parse benchmarks.
//!
//! The query fixtures are not committed to the repository; they are downloaded
//! at build time by `build.rs` when the `fetch` feature is enabled and cached
//! under `OUT_DIR`. [`FIXTURES_DIR`] points at that cache.

use std::path::{Path, PathBuf};

/// Directory holding the downloaded TPC fixtures (`tpc-h/` and `tpc-ds/`),
/// populated by `build.rs` under `OUT_DIR` when built with `--features fetch`.
pub const FIXTURES_DIR: &str = env!("TPC_FIXTURES_DIR");

/// Number of TPC-H queries (Q1–Q22).
pub const TPCH_N: u32 = 22;
/// Number of TPC-DS queries (Q1–Q99).
pub const TPCDS_N: u32 = 99;

/// Path to a single TPC fixture, e.g. `tpc_fixture("tpc-h", 1)`.
///
/// Panics with actionable guidance if the fixtures have not been downloaded,
/// which happens when the crate is built without the `fetch` feature.
pub fn tpc_fixture(sub_dir: &str, n: u32) -> PathBuf {
    let path = Path::new(FIXTURES_DIR)
        .join(sub_dir)
        .join(format!("{n}.sql"));
    if !path.exists() {
        panic!(
            "TPC benchmark fixture not found: {}\n\n\
             These fixtures are downloaded at build time and are not committed.\n\
             Re-run with the `fetch` feature enabled, for example:\n  \
             cargo bench -p sqlfluffrs_benchmarks --features fetch\n  \
             cargo run -p sqlfluffrs_benchmarks --example time_tpc --features fetch",
            path.display()
        );
    }
    path
}
