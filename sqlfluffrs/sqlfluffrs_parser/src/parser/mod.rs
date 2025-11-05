//! Iterative parser implementation for SQLFluff
//!
//! This module contains an iterative (non-recursive) parser that uses an
//! explicit stack of frames to parse SQL grammar without stack overflow risks.

#[macro_use]
mod macros;
mod cache;
mod core;
mod frame;
pub(crate) mod types;
#[macro_use]
mod handlers;
mod helpers; // Utility methods for Parser
mod iterative;
mod utils;

// Re-export public types
pub use core::Parser;
pub use sqlfluffrs_types::{Grammar, ParseMode};
pub use types::{Node, ParseContext, ParseError, ParseErrorType, SegmentDef};

// Internal re-exports for submodules
pub(crate) use frame::{BracketedState, DelimitedState, FrameContext, FrameState, ParseFrame};
