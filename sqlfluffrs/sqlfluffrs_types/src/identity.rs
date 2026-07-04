//! Process-global unique identifiers for tokens.
//!
//! Replaces per-token `Uuid::new_v4()`. A token's `uuid` is only ever used as
//! an opaque identity key (compared by equality and used as a map key in the
//! fix engine); it is never parsed back as an RFC-4122 UUID, so a monotonic
//! counter is sufficient -- and far cheaper than drawing 16 bytes of CSPRNG
//! entropy per token.
//!
//! The high bits carry a source tag so these ids stay disjoint from ids minted
//! on the Python side (which uses `PYTHON_TAG = 1 << 120`). `PyToken.uuid`
//! surfaces this `u128` to Python verbatim, where Python-created segments and
//! Rust-origin tokens share one id space inside the fix engine. Without the
//! tag, both counters would start at 1 and a Rust token would collide with an
//! unrelated Python segment.
//!
//! NOTE: this is the token *identity* uuid only. Templated `block_uuid`s remain
//! genuine `Uuid`s -- they are round-tripped through `Uuid::parse_str` at the
//! Python boundary and must keep RFC-4122 structure.

use std::sync::atomic::{AtomicU64, Ordering};

/// Source tag OR'd into the high bits of every Rust-minted id. Must stay
/// distinct from the Python tag (`1 << 120`). `2 << 120` sets bit 121, leaving
/// the low 120 bits for the counter; both fit within a `u128`.
const RUST_TAG: u128 = 2u128 << 120;

static COUNTER: AtomicU64 = AtomicU64::new(1);

/// Return a process-unique, source-tagged token identifier.
///
/// `fetch_add` with `Relaxed` ordering is correct here: we need atomic
/// uniqueness, not any happens-before relationship with other memory, so the
/// cheapest ordering suffices.
pub fn next_id() -> u128 {
    RUST_TAG | (COUNTER.fetch_add(1, Ordering::Relaxed) as u128)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Tag must match Python's convention and never overlap its space.
    const PYTHON_TAG: u128 = 1u128 << 120;

    #[test]
    fn ids_are_tagged_unique_and_disjoint_from_python() {
        let a = next_id();
        let b = next_id();
        assert_ne!(a, b, "ids must be unique");
        assert_eq!(a >> 120, 0b10, "rust tag (bit 121) must be set");
        // A Rust id can never equal a Python id: their tag bits differ.
        assert_ne!(a & !(RUST_TAG | PYTHON_TAG), a, "counter occupies low bits");
        assert_eq!(RUST_TAG & PYTHON_TAG, 0, "tag spaces must not overlap");
    }
}
