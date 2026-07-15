//! Rust-native lint rules, run over the parse arena's public read API.
//!
//! ## STATUS: early — the capitalisation bundle's CP01/CP03/CP04 are wired up
//! (CP02/CP05 still Python-only), gated by `core.use_rust_rules`
//!
//! Each rule's *detection* runs entirely in Rust over [`sqlfluffrs_parser::Arena`]
//! (read-only) and returns a compact result; *fix application* stays on the
//! Python side for now (the linter anchors a `LintFix` from the returned data).
//! Moving fixing into Rust waits on the arena's mutation milestone.
//!
//! Each rule's PyO3 binding lives next to its logic, gated behind the optional
//! `python` feature, and is registered on the module by [`python::register`].
//! Rule *detection* stays pure Rust (no feature needed) and unit-testable.

pub mod capitalisation;
pub mod cp01;
pub mod cp03;
pub mod cp04;

#[cfg(feature = "python")]
pub mod python;
