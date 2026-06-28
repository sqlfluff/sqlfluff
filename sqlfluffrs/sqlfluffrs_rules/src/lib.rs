//! Rust-native lint rules, run over the parse arena's public read API.
//!
//! ## STATUS: early — one experimental rule (CP01), not wired into dispatch
//!
//! Each rule's *detection* runs entirely in Rust over [`sqlfluffrs_parser::Arena`]
//! (read-only) and returns a compact result; *fix application* stays on the
//! Python side for now (the linter anchors a `LintFix` from the returned data).
//! Moving fixing into Rust waits on the arena's mutation milestone.
//!
//! The PyO3 bindings are not here — they live in the root `sqlfluffrs` crate,
//! which depends on both this crate and `sqlfluffrs_parser`, so this crate stays
//! pure Rust and unit-testable.

pub mod cp01;
