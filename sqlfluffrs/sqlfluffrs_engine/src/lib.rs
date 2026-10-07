//! Pure-Rust orchestration primitives for SQLFluff's front-of-pipeline.
//!
//! These are shared by two consumers:
//! - the standalone `sqlfluff-rs` binary (`sqlfluffrs_cli`), which resolves
//!   config natively via [`config::ResolvedConfig`], and
//! - the Python-driven engine entrypoints in the `sqlfluffrs` extension module,
//!   which pass config in from the already-resolved Python `FluffConfig`.
//!
//! The leaf ops therefore take primitives (extension lists, ignore patterns,
//! dialect, indent flags) rather than a config object, so either caller can
//! drive them. There is deliberately **no pyo3** dependency here.

pub mod config;
pub mod discovery;
pub mod pipeline;
