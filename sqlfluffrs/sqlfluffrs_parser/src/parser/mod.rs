//! Iterative parser implementation for SQLFluff
//!
//! This module contains an iterative (non-recursive) parser that uses an
//! explicit stack of frames to parse SQL grammar without stack overflow risks.

mod cache;
mod core;
mod frame;
mod helpers; // Utility methods for Parser
mod table_driven;
pub(crate) mod type_mapping;
pub(crate) mod types;

#[cfg(feature = "python")]
pub mod python;

// Re-export public types
pub use core::Parser;
pub use sqlfluffrs_types::ParseMode;
pub use types::{Node, ParseError, ParseErrorType};

// Internal re-exports for submodules
pub(crate) use frame::{BracketedState, DelimitedState, FrameContext, FrameState};

// Re-export Python bindings when feature is enabled
#[cfg(feature = "python")]
pub use python::{PyNode, PyParseError, PyParser};
